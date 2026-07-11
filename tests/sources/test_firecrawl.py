import json

import httpx
import pytest

from app.domain.models import SearchQuery
from app.sources.firecrawl import OlxFirecrawlSource, SourceError


async def test_firecrawl_adapter_maps_valid_documents_and_skips_noise() -> None:
    async def handler(request: httpx.Request) -> httpx.Response:
        assert request.url.path == "/v2/search"
        payload = json.loads(request.content)
        assert payload["includeDomains"] == ["olx.pl"]
        assert payload["country"] == "PL"
        assert payload["sources"] == ["web"]
        assert payload["query"] == "site:olx.pl/d/oferta Sony XM4"
        assert "450" not in payload["query"]
        return httpx.Response(
            200,
            json={
                "data": {
                    "web": [
                        {
                            "url": "https://www.olx.pl/d/oferta/sony-wh-1000xm4-ID123.html?srsltid=first",
                            "title": "Sony XM4",
                            "price": "450 zł",
                            "markdown": "opis",
                        },
                        {
                            "url": "https://www.olx.pl/d/oferta/sony-wh-1000xm4-ID123.html?srsltid=duplicate",
                            "title": "Sony XM4",
                            "price": "450 zł",
                        },
                        {
                            "url": "https://www.olx.pl/elektronika/q-sony-xm4/",
                            "title": "Sony XM4 - wyniki wyszukiwania",
                            "price": "20 zł",
                        },
                        {"url": "https://example.com/not-olx", "title": "noise", "price": "1 zł"},
                    ]
                }
            },
        )

    client = httpx.AsyncClient(transport=httpx.MockTransport(handler))
    source = OlxFirecrawlSource("test", client=client)
    results = await source.search(SearchQuery(model="Sony XM4", budget_max="450"))
    await client.aclose()
    assert len(results) == 1
    assert results[0].source == "olx_firecrawl"
    assert results[0].price_text == "450 zł"
    assert results[0].external_id == "ID123.html"


async def test_firecrawl_extracts_price_from_realistic_search_description() -> None:
    async def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(
            200,
            json={
                "data": [
                    {
                        "url": "https://www.olx.pl/d/oferta/sony-wf-1000xm4-IDABC.html",
                        "title": "Sony WF-1000XM4 używane",
                        "description": "Cena 399 zł. Stan bardzo dobry, wysyłka OLX.",
                    }
                ]
            },
        )

    client = httpx.AsyncClient(transport=httpx.MockTransport(handler))
    source = OlxFirecrawlSource("test", client=client)
    results = await source.search(SearchQuery(model="Sony WF-1000XM4"))
    await client.aclose()

    assert results[0].price_text == "399 zł"


async def test_firecrawl_reports_successful_but_irrelevant_results_as_source_error() -> None:
    async def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(
            200,
            json={
                "data": {
                    "web": [
                        {
                            "url": "https://www.olx.pl/d/oferta/iphone-17-IDNOISE.html",
                            "title": "iPhone 17 Air 256 GB",
                            "description": "Cena 3499 zł",
                        }
                    ]
                }
            },
        )

    client = httpx.AsyncClient(transport=httpx.MockTransport(handler))
    source = OlxFirecrawlSource("test", client=client)

    with pytest.raises(SourceError, match="no matching priced offers"):
        await source.search(SearchQuery(model="Samsung Galaxy S25"))

    await client.aclose()
