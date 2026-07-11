import os
from datetime import UTC, datetime
from decimal import Decimal
from uuid import uuid4

import pytest

from app.config import Settings
from app.conversation.service import ConversationService
from app.domain.models import ListingCondition, NormalizedListing, Requirements, SearchQuery
from app.listings.normalizer import normalize_listing
from app.llm.client import OpenAIStructuredClient
from app.product_research.service import ProductResearchService
from app.ranking.engine import rank_listings
from app.ranking.explanations import RecommendationExplanationService
from app.sources.firecrawl import OlxFirecrawlSource
from supabase import create_client

pytestmark = pytest.mark.skipif(
    os.getenv("RUN_LIVE_TESTS") != "1", reason="set RUN_LIVE_TESTS=1 to use external services"
)


class Clock:
    def now(self) -> datetime:
        return datetime.now(UTC)


class ResearchRepository:
    async def get_fresh(self, product_id: object, fresh_since: datetime) -> None:
        return None

    async def save(self, product_id: object, research: dict[str, object]) -> object:
        return uuid4()


def test_supabase_schema_is_accessible() -> None:
    settings = Settings()
    assert settings.supabase_url and settings.supabase_service_role_key
    database = create_client(settings.supabase_url, settings.supabase_service_role_key)
    for table in (
        "products",
        "product_research",
        "listings",
        "listing_snapshots",
        "sessions",
        "search_runs",
        "recommendations",
    ):
        database.table(table).select("*", count="exact").limit(1).execute()


async def test_firecrawl_returns_a_normalizable_real_olx_payload() -> None:
    settings = Settings()
    assert settings.firecrawl_api_key
    source = OlxFirecrawlSource(
        settings.firecrawl_api_key, timeout_seconds=settings.firecrawl_timeout_seconds
    )
    raw = await source.search(SearchQuery(model="Sony WF-1000XM4", limit=5))
    normalized = []
    for item in raw:
        try:
            normalized.append(normalize_listing(item))
        except ValueError:
            continue
    assert raw, "Firecrawl returned no OLX records"
    assert normalized, "Firecrawl returned OLX records but none had a usable price"


async def test_openai_validates_conversation_research_and_explanations() -> None:
    settings = Settings()
    assert settings.openai_api_key
    llm = OpenAIStructuredClient(
        settings.openai_api_key,
        settings.openai_model,
        timeout_seconds=settings.openai_timeout_seconds,
    )
    conversation = await ConversationService(llm).handle_message(
        "Coś jak AirPods Pro, ale do 500 zł, z dobrym ANC do iPhone'a.", Requirements()
    )
    assert conversation.question or 4 <= len(conversation.suggestions) <= 6

    research = await ProductResearchService(ResearchRepository(), llm, Clock()).get_or_create(
        uuid4(), {"brand": "Sony", "model": "WF-1000XM4", "specifications": {}}
    )
    assert "unverified_product_research" in research["data_gaps"]
    assert research["sources"] == []

    listing = NormalizedListing(
        source="live-smoke",
        external_id="live-offer",
        url="https://example.com/live-offer",
        title="Sony WF-1000XM4",
        price=Decimal("400"),
        condition=ListingCondition.VERY_GOOD,
        data_gaps=["battery", "authenticity"],
    )
    ranked = rank_listings([listing], Requirements())
    explanations = await RecommendationExplanationService(llm).explain(ranked)
    assert explanations.get("live-offer")
