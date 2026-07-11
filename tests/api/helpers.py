from datetime import UTC, datetime
from decimal import Decimal
from typing import Any
from uuid import UUID, uuid4

from app.api.dependencies import ApplicationServices
from app.conversation.service import ConversationService
from app.domain.models import (
    ListingCondition,
    NormalizedListing,
    RawListing,
    ReferenceProduct,
    Requirements,
    RunStatus,
)
from app.llm.schemas import ConversationOutput, ProductSuggestion
from app.orchestration.search import SearchOrchestrator


class FixedClock:
    def now(self) -> datetime:
        return datetime(2026, 7, 11, 12, tzinfo=UTC)


class ConversationLLM:
    async def structured_response(self, **kwargs: object) -> ConversationOutput:
        prompt = str(kwargs["user_prompt"])
        has_reference = "AirPods Pro" in prompt
        reference = (
            ReferenceProduct(brand="Apple", model="AirPods Pro", confidence=0.95)
            if has_reference
            else None
        )
        return ConversationOutput(
            requirements=Requirements(
                budget_max=Decimal("600"),
                required_features=["ANC"],
                reference_product=reference,
            ),
            missing_critical_information=False,
            reference_product=reference,
            suggestions=[
                ProductSuggestion(
                    brand="Sony",
                    model=f"WF-XM{index}",
                    estimated_used_price_pln=350 + index * 10,
                    key_features=["ANC"],
                    similarity_reasons=["ANC", "dokanalowe"],
                    differences=["inny ekosystem"],
                    why_it_fits="Dobre ANC w niższej cenie",
                    tradeoff="Brak funkcji Apple",
                    source_url="https://example.com/products",
                    confidence=0.8,
                )
                for index in range(4)
            ],
        )


class Sessions:
    def __init__(self) -> None:
        self.rows: dict[UUID, dict[str, Any]] = {}

    async def create(self) -> UUID:
        session_id = uuid4()
        self.rows[session_id] = {"id": str(session_id), "requirements": {}}
        return session_id

    async def get(self, session_id: UUID) -> dict[str, Any] | None:
        return self.rows.get(session_id)

    async def update(self, session_id: UUID, changes: dict[str, Any]) -> None:
        self.rows[session_id].update(changes)


class Products:
    def __init__(self) -> None:
        self.rows: dict[UUID, dict[str, Any]] = {}

    async def get(self, product_id: UUID) -> dict[str, Any] | None:
        return self.rows.get(product_id)

    async def upsert(self, product: dict[str, Any]) -> UUID:
        existing = next(
            (
                product_id
                for product_id, row in self.rows.items()
                if (row["brand"], row["model"]) == (product["brand"], product["model"])
            ),
            None,
        )
        product_id = existing or uuid4()
        self.rows[product_id] = {"id": str(product_id), **product}
        return product_id


class Runs:
    def __init__(self) -> None:
        self.rows: dict[UUID, dict[str, Any]] = {}

    async def create(self, session_id: UUID, product_id: UUID, query: dict[str, Any]) -> UUID:
        run_id = uuid4()
        self.rows[run_id] = {
            "id": str(run_id),
            "session_id": str(session_id),
            "product_id": str(product_id),
            "query": query,
            "status": RunStatus.PENDING.value,
            "sources_succeeded": [],
            "error_summary": {},
        }
        return run_id

    async def set_status(
        self,
        run_id: UUID,
        status: RunStatus,
        *,
        sources_succeeded: list[str] | None = None,
        error_summary: dict[str, str] | None = None,
    ) -> None:
        self.rows[run_id]["status"] = status.value
        if sources_succeeded is not None:
            self.rows[run_id]["sources_succeeded"] = sources_succeeded
        if error_summary is not None:
            self.rows[run_id]["error_summary"] = error_summary

    async def get(self, run_id: UUID) -> dict[str, Any] | None:
        return self.rows.get(run_id)


class Listings:
    def __init__(self, cached: list[NormalizedListing] | None = None) -> None:
        self.rows = cached or []

    async def upsert_many(
        self, product_id: UUID, listings: list[NormalizedListing], observed_at: datetime
    ) -> list[NormalizedListing]:
        saved = [
            listing.model_copy(
                update={
                    "id": listing.id or uuid4(),
                    "product_id": product_id,
                    "last_seen_at": observed_at,
                    "retrieved_at": observed_at,
                }
            )
            for listing in listings
        ]
        self.rows.extend(saved)
        return saved

    async def find_active(
        self,
        product_id: UUID,
        requirements: Requirements,
        fresh_since: datetime | None = None,
    ) -> list[NormalizedListing]:
        del product_id, requirements
        if fresh_since is None:
            return list(self.rows)
        return [
            item for item in self.rows if item.last_seen_at and item.last_seen_at >= fresh_since
        ]


class Recommendations:
    def __init__(self, listings: Listings) -> None:
        self.listings = listings
        self.rows: dict[UUID, list[dict[str, Any]]] = {}

    async def replace_for_run(
        self, run_id: UUID, recommendations: list[dict[str, Any]]
    ) -> None:
        listing_by_id = {str(item.id): item for item in self.listings.rows}
        self.rows[run_id] = [
            {
                **recommendation,
                "listings": listing_by_id[recommendation["listing_id"]].model_dump(mode="json"),
            }
            for recommendation in recommendations
        ]

    async def get_for_run(self, run_id: UUID) -> list[dict[str, Any]]:
        return self.rows.get(run_id, [])


class Research:
    def __init__(self) -> None:
        self.rows: dict[UUID, dict[str, Any]] = {}

    async def get_fresh(self, product_id: UUID, fresh_since: datetime) -> dict[str, Any] | None:
        del fresh_since
        return self.rows.get(product_id)

    async def save(self, product_id: UUID, research: dict[str, Any]) -> UUID:
        self.rows[product_id] = research
        return uuid4()


class ResearchService:
    def __init__(self, repository: Research, clock: FixedClock) -> None:
        self.repository = repository
        self.clock = clock

    async def get_or_create(self, product_id: UUID, product: dict[str, Any]) -> dict[str, Any]:
        del product
        result = {
            "summary": "Sprawdź baterię, ANC i dowód zakupu",
            "sources": ["https://example.com/research"],
            "retrieved_at": self.clock.now().isoformat(),
            "confidence": 0.8,
            "data_gaps": [],
        }
        self.repository.rows[product_id] = result
        return result


class Source:
    source_name = "fixture_source"

    def __init__(self, *, fails: bool = False) -> None:
        self.fails = fails
        self.calls = 0

    async def search(self, query: object) -> list[RawListing]:
        del query
        self.calls += 1
        if self.fails:
            raise RuntimeError("source unavailable")
        return [
            RawListing(
                source=self.source_name,
                external_id=f"offer-{index}",
                url=f"https://example.com/offers/{index}",
                title=f"Sony WF-XM0 ANC oferta {index}",
                price_text=f"{350 + index * 20} zł",
                description="Kompletne sprawne słuchawki z ANC, etui i dowodem zakupu. " * 2,
                attributes={
                    "variant": "WF-XM0",
                    "warranty": "6 miesięcy",
                    "returns": "14 dni",
                    "seller_rating": "4.8",
                },
                image_urls=[f"https://example.com/images/{index}.jpg"],
            )
            for index in range(3)
        ]

    async def get_details(self, external_id: str) -> RawListing | None:
        del external_id
        return None


def cached_listings() -> list[NormalizedListing]:
    return [
        NormalizedListing(
            id=uuid4(),
            source="cache",
            external_id=f"cached-{index}",
            url=f"https://example.com/cached/{index}",
            title=f"Sony WF-XM0 ANC cached {index}",
            price=Decimal(390 + index * 10),
            condition=ListingCondition.VERY_GOOD,
            description="Pełny opis słuchawek z ANC i etui, oferta sprawdzona wcześniej. " * 2,
            attributes={"variant": "WF-XM0", "feature": "ANC"},
            image_urls=[f"https://example.com/cached/{index}.jpg"],
            confidence=0.6,
            data_gaps=["warranty", "returns", "seller_signals"],
            last_seen_at=datetime(2026, 7, 9, tzinfo=UTC),
            retrieved_at=datetime(2026, 7, 9, tzinfo=UTC),
        )
        for index in range(3)
    ]


def build_services(*, source_fails: bool = False) -> ApplicationServices:
    clock = FixedClock()
    sessions = Sessions()
    products = Products()
    runs = Runs()
    listings = Listings(cached_listings() if source_fails else None)
    recommendations = Recommendations(listings)
    research_repository = Research()
    orchestrator = SearchOrchestrator(
        runs=runs,
        listings=listings,
        recommendations=recommendations,
        research=ResearchService(research_repository, clock),  # type: ignore[arg-type]
        sources=[Source(fails=source_fails)],
        clock=clock,
    )
    return ApplicationServices(
        conversation=ConversationService(ConversationLLM()),
        sessions=sessions,
        products=products,
        runs=runs,
        recommendations=recommendations,
        product_research=research_repository,
        orchestrator=orchestrator,
        clock=clock,
    )
