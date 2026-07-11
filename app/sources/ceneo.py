import asyncio
import re
import unicodedata
from collections.abc import Mapping
from datetime import datetime
from decimal import Decimal, InvalidOperation
from typing import Any
from urllib.parse import urlparse

import httpx

from app.domain.models import NewPriceBenchmark, SearchQuery
from app.product_matching import is_accessory_title
from app.sources.firecrawl import SourceError, _records

_PRICE_WITH_CURRENCY_RE = re.compile(
    r"(?<!\d)(\d{1,3}(?:[ .\u00a0]\d{3})*|\d+)(?:[,.](\d{1,2}))?\s*(?:zł|PLN)",
    re.IGNORECASE,
)
_PRODUCT_PATH_RE = re.compile(r"^/\d+(?:[/?#-]|$)")


class CeneoFirecrawlSource:
    source_name = "ceneo_firecrawl"

    def __init__(
        self, api_key: str, *, timeout_seconds: float = 20, client: httpx.AsyncClient | None = None
    ) -> None:
        if not api_key:
            raise ValueError("Firecrawl API key is required")
        self._api_key = api_key
        self._timeout = timeout_seconds
        self._client = client

    async def get_benchmark(
        self, query: SearchQuery, retrieved_at: datetime
    ) -> NewPriceBenchmark | None:
        payload = {
            "query": f'site:ceneo.pl "{query.model}" najniższa cena',
            "limit": min(query.limit, 10),
            "scrapeOptions": {"formats": ["markdown"]},
        }
        records = _records(await self._post("https://api.firecrawl.dev/v1/search", payload))
        candidates = [
            candidate
            for record in records
            if (candidate := _benchmark(record, query.model, retrieved_at)) is not None
        ]
        return min(candidates, key=lambda item: item.price) if candidates else None

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


def _benchmark(
    record: Mapping[str, Any], model: str, retrieved_at: datetime
) -> NewPriceBenchmark | None:
    metadata = record.get("metadata") if isinstance(record.get("metadata"), Mapping) else {}
    url = str(record.get("url") or metadata.get("sourceURL") or metadata.get("url") or "")
    title = str(record.get("title") or metadata.get("title") or metadata.get("og:title") or "")
    if (
        not _is_product_url(url)
        or not title
        or is_accessory_title(title)
        or not _matches_model(title, model)
    ):
        return None
    price = _record_price(record, metadata)
    if price is None or price <= 0:
        return None
    return NewPriceBenchmark(
        product_name=title,
        price=price,
        url=url,
        retrieved_at=retrieved_at,
    )


def _is_product_url(url: str) -> bool:
    parsed = urlparse(url)
    host = parsed.hostname or ""
    return (host == "ceneo.pl" or host.endswith(".ceneo.pl")) and bool(
        _PRODUCT_PATH_RE.match(parsed.path)
    )


def _matches_model(title: str, model: str) -> bool:
    normalized_title = _normalized(title)
    terms = [term for term in _normalized(model).split() if len(term) > 1]
    if not terms:
        return False
    distinctive = [term for term in terms if any(character.isdigit() for character in term)]
    if distinctive and not all(term in normalized_title for term in distinctive):
        return False
    return sum(term in normalized_title for term in terms) / len(terms) >= 0.6


def _normalized(value: str) -> str:
    ascii_value = "".join(
        character
        for character in unicodedata.normalize("NFKD", value)
        if not unicodedata.combining(character)
    )
    return " ".join(re.findall(r"[a-z0-9]+", ascii_value.casefold()))


def _record_price(record: Mapping[str, Any], metadata: Mapping[str, Any]) -> Decimal | None:
    structured = (
        record.get("price")
        or metadata.get("product:price:amount")
        or metadata.get("og:price:amount")
        or metadata.get("lowPrice")
    )
    if structured is not None:
        parsed = _decimal_price(str(structured), currency_required=False)
        if parsed is not None:
            return parsed
    content = " ".join(
        str(value)
        for value in (
            record.get("description"),
            record.get("markdown"),
            metadata.get("description"),
        )
        if value
    )
    return _decimal_price(content, currency_required=True)


def _decimal_price(value: str, *, currency_required: bool) -> Decimal | None:
    if currency_required:
        match = _PRICE_WITH_CURRENCY_RE.search(value)
        if not match:
            return None
        whole, fraction = match.groups()
        normalized = whole.replace(" ", "").replace(".", "").replace("\u00a0", "")
        number = f"{normalized}.{fraction or '00'}"
    else:
        match = re.search(r"\d[\d .\u00a0]*(?:[,.]\d{1,2})?", value)
        if not match:
            return None
        number = match.group(0).replace(" ", "").replace("\u00a0", "")
        if "," in number and "." in number:
            number = number.replace(".", "").replace(",", ".")
        elif "," in number:
            number = number.replace(",", ".")
    try:
        return Decimal(number).quantize(Decimal("0.01"))
    except InvalidOperation:
        return None
