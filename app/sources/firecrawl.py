import asyncio
from collections.abc import Mapping
from typing import Any
from urllib.parse import urlparse

import httpx
from pydantic import TypeAdapter, ValidationError

from app.domain.models import RawListing, SearchQuery


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
        search_terms = [f'site:olx.pl/d/oferta "{query.model}"']
        if query.variants:
            search_terms.extend(query.variants)
        if query.budget_max is not None:
            search_terms.append(f"do {query.budget_max} {query.currency.value}")
        payload = {
            "query": " ".join(search_terms),
            "limit": query.limit,
            "scrapeOptions": {"formats": ["markdown", "links"]},
        }
        data = await self._post("https://api.firecrawl.dev/v1/search", payload)
        records = _records(data)
        listings: list[RawListing] = []
        for record in records[: query.limit]:
            try:
                listings.append(_raw_listing(record))
            except (KeyError, TypeError, ValidationError, ValueError):
                continue
        return listings

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
        except (TimeoutError, httpx.HTTPError, ValueError) as exc:
            raise SourceError(f"Firecrawl request failed: {type(exc).__name__}") from exc


def _records(payload: Mapping[str, Any]) -> list[Mapping[str, Any]]:
    data: Any = payload.get("data", payload)
    if isinstance(data, Mapping):
        data = data.get("data") or data.get("documents") or [data]
    return [item for item in data if isinstance(item, Mapping)] if isinstance(data, list) else []


def _raw_listing(record: Mapping[str, Any]) -> RawListing:
    metadata = record.get("metadata") if isinstance(record.get("metadata"), Mapping) else {}
    url = str(record.get("url") or metadata.get("sourceURL") or metadata.get("url"))
    if "olx.pl" not in urlparse(url).netloc:
        raise ValueError("not an OLX listing")
    external_id = (
        str(record.get("external_id") or metadata.get("og:url") or url).rstrip("/").split("-")[-1]
    )
    title = str(record.get("title") or metadata.get("title") or metadata.get("og:title") or "")
    attributes = dict(record.get("attributes") or {})
    price = record.get("price") or metadata.get("product:price:amount") or attributes.get("price")
    images = record.get("image_urls") or metadata.get("og:image") or []
    if isinstance(images, str):
        images = [images]
    return RawListing(
        source="olx_firecrawl",
        external_id=external_id,
        url=url,
        title=title,
        price_text=str(price) if price is not None else None,
        description=str(record.get("markdown") or record.get("description") or "") or None,
        attributes=attributes,
        image_urls=TypeAdapter(list[str]).validate_python(images),
        raw_payload=dict(record),
    )
