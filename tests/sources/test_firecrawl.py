import httpx

from app.domain.models import SearchQuery
from app.sources.firecrawl import OlxFirecrawlSource


async def test_firecrawl_adapter_maps_valid_documents_and_skips_noise() -> None:
    async def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(
            200,
            json={
                "data": {
                    "documents": [
                        {
                            "url": "https://www.olx.pl/d/oferta/sony-wh-1000xm4-ID123.html",
                            "title": "Sony XM4",
                            "price": "450 zł",
                            "markdown": "opis",
                        },
                        {"url": "https://example.com/not-olx", "title": "noise", "price": "1 zł"},
                    ]
                }
            },
        )

    client = httpx.AsyncClient(transport=httpx.MockTransport(handler))
    source = OlxFirecrawlSource("test", client=client)
    results = await source.search(SearchQuery(model="Sony XM4"))
    await client.aclose()
    assert len(results) == 1
    assert results[0].source == "olx_firecrawl"
    assert results[0].price_text == "450 zł"


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
