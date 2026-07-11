from datetime import UTC, datetime
from uuid import uuid4

from app.product_research.service import ProductResearchService


class Clock:
    def now(self) -> datetime:
        return datetime(2026, 7, 11, tzinfo=UTC)


class Repository:
    def __init__(self, cached: dict[str, object] | None) -> None:
        self.cached = cached
        self.fresh_since: datetime | None = None

    async def get_fresh(
        self, product_id: object, fresh_since: datetime
    ) -> dict[str, object] | None:
        self.fresh_since = fresh_since
        return self.cached

    async def save(self, product_id: object, research: dict[str, object]) -> object:
        raise AssertionError("fresh research must not be overwritten")


class LLM:
    async def structured_response(self, **kwargs: object) -> object:
        raise AssertionError("LLM must not run when research cache is fresh")


async def test_fresh_research_is_returned_without_llm_call() -> None:
    cached = {"summary": "cached"}
    repository = Repository(cached)
    result = await ProductResearchService(repository, LLM(), Clock()).get_or_create(
        uuid4(), {"model": "Sony XM4"}
    )
    assert result is cached
    assert repository.fresh_since == datetime(2026, 6, 11, tzinfo=UTC)
