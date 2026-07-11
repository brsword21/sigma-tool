from typing import Any
from uuid import uuid4

from app.domain.models import RunStatus
from app.repositories.supabase import SupabaseSearchRunRepository


class Result:
    data: list[dict[str, Any]] = []


class Query:
    def __init__(self) -> None:
        self.updated: dict[str, Any] | None = None

    def update(self, payload: dict[str, Any]) -> "Query":
        self.updated = payload
        return self

    def eq(self, key: str, value: str) -> "Query":
        del key, value
        return self

    def execute(self) -> Result:
        return Result()


class Client:
    def __init__(self) -> None:
        self.query = Query()

    def table(self, name: str) -> Query:
        assert name == "search_runs"
        return self.query


async def test_final_status_persists_new_price_benchmark() -> None:
    client = Client()
    repository = SupabaseSearchRunRepository(client)
    benchmark = {
        "product_name": "Sony WH-1000XM4",
        "price": "899.00",
        "currency": "PLN",
        "url": "https://www.ceneo.pl/123456",
        "source": "ceneo_firecrawl",
        "retrieved_at": "2026-07-11T12:00:00Z",
    }

    await repository.set_status(
        uuid4(),
        RunStatus.COMPLETED,
        sources_succeeded=["olx_firecrawl", "ceneo_firecrawl"],
        error_summary={},
        new_price_benchmark=benchmark,
    )

    assert client.query.updated is not None
    assert client.query.updated["new_price_benchmark"] == benchmark


async def test_final_status_clears_a_benchmark_when_refresh_did_not_find_one() -> None:
    client = Client()
    repository = SupabaseSearchRunRepository(client)

    await repository.set_status(
        uuid4(),
        RunStatus.PARTIAL,
        error_summary={"ceneo_firecrawl": "benchmark unavailable"},
    )

    assert client.query.updated is not None
    assert "new_price_benchmark" in client.query.updated
    assert client.query.updated["new_price_benchmark"] is None
