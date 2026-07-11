import asyncio
import re
from collections.abc import Mapping
from decimal import Decimal, InvalidOperation
from typing import Any
from urllib.parse import urlparse

import httpx
from pydantic import TypeAdapter, ValidationError

from app.domain.models import RawListing, SearchQuery
from app.product_matching import (
    product_words,
    is_direct_olx_listing_url,
    matches_product_title,
)


class SourceError(RuntimeError):
    pass


class OlxFirecrawlSource:
    source_name = "olx_firecrawl"

    def __init__(
        self, api_key: str, *, timeout_seconds: float = 20, client: httpx.AsyncClient | None = None
    ) -> None:
        if not api_key:
            raise ValueError("Firecrawl API key is required")
        self._api_key = api_key
        self._timeout = timeout_seconds
        self._client = client

    async def search(self, query: SearchQuery) -> list[RawListing]:
        # Model stays unquoted so "Samsung S25" also matches "Samsung Galaxy S25"
        # titles; only variants are exact phrases. Over-fetch because category
        # pages and accessories get filtered out below.
        payload = {
            "query": " ".join(
                ["site:olx.pl/d/oferta", query.model, *(f'"{term}"' for term in query.variants)]
            ),
            "limit": min(50, max(query.limit * 2, 20)),
            "sources": ["web"],
            "includeDomains": ["olx.pl"],
            "country": "PL",
            "location": "Poland",
            "ignoreInvalidURLs": True,
        }
        # Web search surfaces mostly category pages, so the OLX results page is
        # scraped in parallel — it lists dozens of direct offers per query.
        results_url = f"https://www.olx.pl/oferty/q-{'-'.join(product_words(query.model))}/"
        search_result, scrape_result = await asyncio.gather(
            self._post("https://api.firecrawl.dev/v2/search", payload),
            self._post(
                "https://api.firecrawl.dev/v2/scrape",
                {"url": results_url, "formats": ["markdown"], "onlyMainContent": True},
            ),
            return_exceptions=True,
        )
        if isinstance(search_result, BaseException) and isinstance(scrape_result, BaseException):
            raise SourceError(f"Firecrawl search and scrape failed: {search_result}")
        records: list[Mapping[str, Any]] = []
        if not isinstance(scrape_result, BaseException):
            records.extend(_offers_from_results_page(scrape_result))
        if not isinstance(search_result, BaseException):
            records.extend(_records(search_result))
        listings: list[RawListing] = []
        external_ids: set[str] = set()
        for record in records:
            if len(listings) >= query.limit:
                break
            try:
                listing = _raw_listing(record)
                if (
                    listing.price_text
                    and matches_product_title(listing.title, query.model)
                    and listing.external_id not in external_ids
                ):
                    listings.append(listing)
                    external_ids.add(listing.external_id)
            except (KeyError, TypeError, ValidationError, ValueError):
                continue
        if not listings:
            raise SourceError("Firecrawl returned no matching priced offers")
        return listings

    async def probe_used_prices(self, model: str, limit: int = 12) -> list[Decimal]:
        """Quick market probe: one results-page scrape, matching offers' prices only."""
        results_url = f"https://www.olx.pl/oferty/q-{'-'.join(product_words(model))}/"
        data = await self._post(
            "https://api.firecrawl.dev/v2/scrape",
            {"url": results_url, "formats": ["markdown"], "onlyMainContent": True},
        )
        prices: list[Decimal] = []
        for offer in _offers_from_results_page(data):
            if len(prices) >= limit:
                break
            if not offer.get("price") or not matches_product_title(str(offer["title"]), model):
                continue
            price = _decimal_from_price_text(str(offer["price"]))
            if price is not None and price > 0:
                prices.append(price)
        return prices

    async def get_details(self, external_id: str) -> RawListing | None:
        url = (
            external_id
            if external_id.startswith("http")
            else f"https://www.olx.pl/d/oferta/{external_id}"
        )
        data = await self._post(
            "https://api.firecrawl.dev/v1/scrape", {"url": url, "formats": ["markdown"]}
        )
        records = _records(data)
        return _raw_listing(records[0]) if records else None

    async def _post(self, url: str, payload: dict[str, Any]) -> dict[str, Any]:
        headers = {"Authorization": f"Bearer {self._api_key}"}
        try:
            if self._client is not None:
                response = await asyncio.wait_for(
                    self._client.post(url, json=payload, headers=headers), self._timeout
                )
            else:
                async with httpx.AsyncClient(timeout=self._timeout) as client:
                    response = await client.post(url, json=payload, headers=headers)
            response.raise_for_status()
            result = response.json()
            if not isinstance(result, dict):
                raise SourceError("Firecrawl returned a non-object response")
            return result
        except httpx.HTTPStatusError as exc:
            raise SourceError(
                f"Firecrawl request failed with HTTP {exc.response.status_code}"
            ) from exc
        except (TimeoutError, httpx.HTTPError, ValueError) as exc:
            raise SourceError(f"Firecrawl request failed: {type(exc).__name__}") from exc


_RESULTS_PAGE_OFFER = re.compile(
    r"\[\*\*(?P<title>[^\]]{5,160})\*\*\]\((?P<url>https://www\.olx\.pl/d/oferta/[^)\s]+)\)"
)


def _offers_from_results_page(payload: Mapping[str, Any]) -> list[Mapping[str, Any]]:
    data = payload.get("data")
    markdown = str(data.get("markdown") or "") if isinstance(data, Mapping) else ""
    offers: list[Mapping[str, Any]] = []
    for match in _RESULTS_PAGE_OFFER.finditer(markdown):
        title = re.sub(r"\\(.)", r"\1", match.group("title")).strip()
        # Price sits right after the link; stop at the next markdown link so a
        # price-less offer ("Zamienię") doesn't steal the neighbour's price.
        window = markdown[match.end() : match.end() + 160].split("[")[0]
        offers.append({"url": match.group("url"), "title": title, "price": _price_from_text(window)})
    return offers


def _records(payload: Mapping[str, Any]) -> list[Mapping[str, Any]]:
    data: Any = payload.get("data", payload)
    if isinstance(data, Mapping):
        data = data.get("web") or data.get("data") or data.get("documents") or [data]
    return [item for item in data if isinstance(item, Mapping)] if isinstance(data, list) else []


def _raw_listing(record: Mapping[str, Any]) -> RawListing:
    metadata = record.get("metadata") if isinstance(record.get("metadata"), Mapping) else {}
    url = str(record.get("url") or metadata.get("sourceURL") or metadata.get("url"))
    if not is_direct_olx_listing_url(url):
        raise ValueError("not a direct OLX listing")
    external_id = (
        str(record.get("external_id") or metadata.get("og:url") or urlparse(url).path)
        .rstrip("/")
        .split("-")[-1]
    )
    title = str(record.get("title") or metadata.get("title") or metadata.get("og:title") or "")
    attributes = dict(record.get("attributes") or {})
    price = record.get("price") or metadata.get("product:price:amount") or attributes.get("price")
    content = str(record.get("markdown") or record.get("description") or "")
    if price is None:
        price = _price_from_text(f"{title} {content}")
    images = record.get("image_urls") or metadata.get("og:image") or []
    if isinstance(images, str):
        images = [images]
    return RawListing(
        source="olx_firecrawl",
        external_id=external_id,
        url=url,
        title=title,
        price_text=str(price) if price is not None else None,
        description=content or None,
        attributes=attributes,
        image_urls=TypeAdapter(list[str]).validate_python(images),
        raw_payload=dict(record),
    )


def _decimal_from_price_text(value: str) -> Decimal | None:
    match = re.search(
        r"(?<!\d)(\d{1,3}(?:[ . ]\d{3})*|\d+)(?:[,.](\d{1,2}))?\s*(?:zł|PLN)",
        value,
        re.IGNORECASE,
    )
    if match is None:
        return None
    whole = match.group(1).replace(" ", "").replace(".", "").replace(" ", "")
    try:
        return Decimal(f"{whole}.{match.group(2) or '00'}")
    except InvalidOperation:
        return None


def _price_from_text(value: str) -> str | None:
    match = re.search(
        r"(?<!\d)(\d{1,3}(?:[ .]\d{3})*|\d+)(?:[,.]\d{1,2})?\s*(?:zł|PLN)",
        value,
        re.IGNORECASE,
    )
    return match.group(0) if match else None
