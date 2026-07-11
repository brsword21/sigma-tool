from datetime import UTC, datetime

from app.api.dependencies import ApplicationServices
from app.auth.service import SupabaseAuthVerifier
from app.config import Settings
from app.conversation.service import ConversationService
from app.llm.client import OpenAIStructuredClient
from app.orchestration.search import SearchOrchestrator
from app.product_research.service import ProductResearchService
from app.ranking.explanations import RecommendationExplanationService
from app.repositories.supabase import (
    SupabaseListingRepository,
    SupabaseMessageRepository,
    SupabaseProductRepository,
    SupabaseProductResearchRepository,
    SupabaseRecommendationRepository,
    SupabaseSearchRunRepository,
    SupabaseSessionRepository,
)
from app.sources.ceneo import CeneoFirecrawlSource
from app.sources.firecrawl import OlxFirecrawlSource
from supabase import create_client


class SystemClock:
    def now(self) -> datetime:
        return datetime.now(UTC)


def build_application_services(settings: Settings) -> ApplicationServices:
    missing = [
        name
        for name, value in (
            ("OPENAI_API_KEY", settings.openai_api_key),
            ("SUPABASE_URL", settings.supabase_url),
            ("SUPABASE_SERVICE_ROLE_KEY", settings.supabase_service_role_key),
            ("FIRECRAWL_API_KEY", settings.firecrawl_api_key),
        )
        if not settings.is_real_service_value(value)
    ]
    if missing:
        raise ValueError(f"Missing external service settings: {', '.join(missing)}")

    database = create_client(settings.supabase_url, settings.supabase_service_role_key)
    llm = OpenAIStructuredClient(
        settings.openai_api_key,
        settings.openai_model,
        timeout_seconds=settings.openai_timeout_seconds,
    )
    clock = SystemClock()
    sessions = SupabaseSessionRepository(database)
    messages = SupabaseMessageRepository(database)
    products = SupabaseProductRepository(database)
    runs = SupabaseSearchRunRepository(database)
    listings = SupabaseListingRepository(database)
    recommendations = SupabaseRecommendationRepository(database)
    research_repository = SupabaseProductResearchRepository(database)
    research = ProductResearchService(research_repository, llm, clock)
    olx_source = OlxFirecrawlSource(
        settings.firecrawl_api_key,
        timeout_seconds=settings.firecrawl_timeout_seconds,
    )
    orchestrator = SearchOrchestrator(
        runs=runs,
        listings=listings,
        recommendations=recommendations,
        research=research,
        sources=[olx_source],
        clock=clock,
        explanations=RecommendationExplanationService(llm),
        benchmark_source=CeneoFirecrawlSource(
            settings.firecrawl_api_key,
            timeout_seconds=settings.firecrawl_timeout_seconds,
        ),
    )
    return ApplicationServices(
        conversation=ConversationService(llm),
        sessions=sessions,
        products=products,
        runs=runs,
        recommendations=recommendations,
        product_research=research_repository,
        orchestrator=orchestrator,
        clock=clock,
        messages=messages,
        auth=SupabaseAuthVerifier(database),
        market_probe=olx_source,
    )
