from datetime import UTC, datetime
from uuid import uuid4

from app.llm.schemas import ProductResearchOutput, ResearchParameter
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


class CapturingRepository:
    def __init__(self) -> None:
        self.saved: dict[str, object] | None = None

    async def get_fresh(self, product_id: object, fresh_since: datetime) -> None:
        return None

    async def save(self, product_id: object, research: dict[str, object]) -> object:
        self.saved = research
        return uuid4()


class ResearchLLM:
    async def structured_response(self, **kwargs: object) -> ProductResearchOutput:
        return ProductResearchOutput(
            summary="Sprawdź ANC i baterię",
            key_parameters=[
                ResearchParameter(name="ANC", value="tak"),
                ResearchParameter(name="kodek", value="LDAC"),
            ],
            second_hand_checks=["Sprawdź baterię"],
            known_risks=[],
            sources=[],
        )


async def test_structured_parameter_pairs_are_persisted_as_existing_mapping() -> None:
    repository = CapturingRepository()

    result = await ProductResearchService(repository, ResearchLLM(), Clock()).get_or_create(
        uuid4(), {"model": "Sony XM4", "specifications": {}}
    )

    assert result["key_parameters"] == {"ANC": "tak", "kodek": "LDAC"}
    assert repository.saved == result
