import asyncio
import time
from datetime import datetime
from typing import Any
from uuid import UUID, uuid4

import pytest
from httpx import ASGITransport, AsyncClient

from app.api.dependencies import ApplicationServices
from app.config import Settings
from app.conversation.service import ConversationService
from app.domain.models import NormalizedListing, Requirements
from app.main import create_app
from app.orchestration.search import SearchOrchestrator
from app.repositories.supabase import SupabaseListingRepository
from tests.api.helpers import (
    Auth,
    BenchmarkSource,
    ConversationLLM,
    FixedClock,
    Messages,
    Products,
    Recommendations,
    Research,
    ResearchService,
    Runs,
    Sessions,
    Source,
)


class Result:
    def __init__(self, data: list[dict[str, object]]) -> None:
        self.data = data


class SlowBlockingQuery:
    def __init__(self, db: "SlowBlockingClient", table: str) -> None:
        self.db = db
        self.table = table
        self.payload: dict[str, object] | list[dict[str, object]] | None = None

    def upsert(
        self, payload: dict[str, object] | list[dict[str, object]], **kwargs: object
    ) -> "SlowBlockingQuery":
        self.payload = payload
        return self

    def select(self, *args: object) -> "SlowBlockingQuery":
        return self

    def eq(self, field: str, value: object) -> "SlowBlockingQuery":
        return self

    def lte(self, field: str, value: object) -> "SlowBlockingQuery":
        return self

    def gte(self, field: str, value: object) -> "SlowBlockingQuery":
        return self

    def ilike(self, field: str, value: object) -> "SlowBlockingQuery":
        return self

    def order(self, *args: object, **kwargs: object) -> "SlowBlockingQuery":
        return self

    def execute(self) -> Result:
        time.sleep(0.25)
        if self.table == "listing_snapshots":
            payloads = self.payload if isinstance(self.payload, list) else [self.payload or {}]
            return Result(payloads)
        if self.table == "listings" and self.payload is not None:
            payloads = self.payload if isinstance(self.payload, list) else [self.payload]
            results: list[dict[str, object]] = []
            for payload in payloads:
                key = (str(payload["source"]), str(payload["external_id"]))
                existing = self.db.rows.get(
                    key, {"id": str(uuid4()), "first_seen_at": payload["last_seen_at"]}
                )
                existing.update(payload)
                self.db.rows[key] = existing
                results.append(existing)
            return Result(results)
        return Result([])


class SlowBlockingClient:
    def __init__(self) -> None:
        self.rows: dict[tuple[str, str], dict[str, object]] = {}

    def table(self, name: str) -> SlowBlockingQuery:
        return SlowBlockingQuery(self, name)


class BlockingListings:
    def __init__(self) -> None:
        self._repo = SupabaseListingRepository(SlowBlockingClient())
        self.rows: list[NormalizedListing] = []

    async def upsert_many(
        self, product_id: UUID, listings: list[NormalizedListing], observed_at: datetime
    ) -> list[NormalizedListing]:
        saved = await self._repo.upsert_many(product_id, listings, observed_at)
        self.rows.extend(saved)
        return saved

    async def find_active(
        self,
        product_id: UUID,
        requirements: Requirements,
        fresh_since: datetime | None = None,
    ) -> list[NormalizedListing]:
        return await self._repo.find_active(product_id, requirements, fresh_since)


def build_services_with_blocking_listings() -> ApplicationServices:
    clock = FixedClock()
    sessions = Sessions()
    products = Products()
    runs = Runs()
    listings = BlockingListings()
    recommendations = Recommendations(listings)
    research_repository = Research()
    orchestrator = SearchOrchestrator(
        runs=runs,
        listings=listings,
        recommendations=recommendations,
        research=ResearchService(research_repository, clock),  # type: ignore[arg-type]
        sources=[Source()],
        benchmark_source=BenchmarkSource(),
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
        messages=Messages(),
        auth=Auth(),
    )


@pytest.mark.asyncio
async def test_run_polling_stays_responsive_during_blocking_listing_io() -> None:
    services = build_services_with_blocking_listings()
    app = create_app(Settings(_env_file=None, environment="test"), services=services)
    transport = ASGITransport(app=app)

    async with AsyncClient(transport=transport, base_url="http://test") as client:
        session_id = (await client.post("/sessions")).json()["session_id"]
        discovery = (
            await client.post(
                f"/sessions/{session_id}/messages",
                json={"message": "ANC do 600 zł"},
            )
        ).json()
        product_id = discovery["candidates"][0]["product_id"]
        run_id = (
            await client.post(
                f"/sessions/{session_id}/products/{product_id}/select",
                json={"direction": "best_value"},
            )
        ).json()["run_id"]

        started = time.monotonic()
        responses = await asyncio.gather(
            client.get(f"/runs/{run_id}"),
            client.get(f"/runs/{run_id}"),
            client.get(f"/runs/{run_id}"),
        )
        elapsed = time.monotonic() - started

        assert all(response.status_code == 200 for response in responses)
        assert elapsed < 2.0
        statuses = [response.json()["status"] for response in responses]
        assert any(status in {"running", "completed", "partial", "failed"} for status in statuses)
