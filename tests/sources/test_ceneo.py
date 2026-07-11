from datetime import UTC, datetime
from decimal import Decimal

import httpx

from app.domain.models import SearchQuery
from app.sources.ceneo import CeneoFirecrawlSource


async def test_ceneo_returns_cheapest_equally_matching_product_page() -> None:
    async def handler(request: httpx.Request) -> httpx.Response:
        assert request.url.path == "/v1/search"
        payload = __import__("json").loads(request.content)
        assert payload["query"].startswith('site:ceneo.pl "Sony WH-1000XM4"')
        return httpx.Response(
            200,
            json={
                "data": {
                    "documents": [
                        {
                            "url": "https://www.ceneo.pl/123456",
                            "title": "Sony WH-1000XM4 czarne",
                            "metadata": {"product:price:amount": "999.99"},
                        },
                        {
                            "url": "https://www.ceneo.pl/987654",
                            "title": "Sony WH-1000XM4 srebrne",
                            "markdown": "Najniższa cena: 899,00 zł",
                        },
                    ]
                }
            },
        )

    client = httpx.AsyncClient(transport=httpx.MockTransport(handler))
    source = CeneoFirecrawlSource("test", client=client)
    result = await source.get_benchmark(
        SearchQuery(model="Sony WH-1000XM4"), datetime(2026, 7, 11, 12, tzinfo=UTC)
    )
    await client.aclose()

    assert result is not None
    assert result.price == Decimal("899.00")
    assert str(result.url) == "https://www.ceneo.pl/987654"
    assert result.source == "ceneo_firecrawl"
    assert result.retrieved_at == datetime(2026, 7, 11, 12, tzinfo=UTC)


async def test_ceneo_rejects_noise_mismatched_products_and_missing_prices() -> None:
    async def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(
            200,
            json={
                "data": [
                    {
                        "url": "https://example.com/cheap",
                        "title": "Sony WH-1000XM4",
                        "price": "1 zł",
                    },
                    {
                        "url": "https://www.ceneo.pl/111",
                        "title": "Sony WH-1000XM5",
                        "price": "10 zł",
                    },
                    {
                        "url": "https://www.ceneo.pl/222",
                        "title": "Sony WH-1000XM4",
                        "markdown": "Produkt chwilowo niedostępny",
                    },
                ]
            },
        )

    client = httpx.AsyncClient(transport=httpx.MockTransport(handler))
    source = CeneoFirecrawlSource("test", client=client)
    result = await source.get_benchmark(SearchQuery(model="Sony WH-1000XM4"), datetime.now(UTC))
    await client.aclose()

    assert result is None
