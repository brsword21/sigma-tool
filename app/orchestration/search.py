import asyncio
from dataclasses import dataclass
from datetime import timedelta
from typing import Any
from uuid import UUID

from app.domain.models import (
    NormalizedListing,
    Requirements,
    RunStatus,
    SearchDirection,
    SearchQuery,
)
from app.listings.normalizer import normalize_listing
from app.product_research.service import ProductResearchService
from app.ranking.engine import rank_listings
from app.repositories.protocols import (
    ListingRepository,
    RecommendationRepository,
    SearchRunRepository,
)
from app.services.ports import Clock
from app.sources.base import ListingSource


@dataclass(frozen=True)
class ListingCollection:
    listings: list[NormalizedListing]
    sources_succeeded: list[str]
    errors: dict[str, str]


class SearchOrchestrator:
    def __init__(
        self,
        *,
        runs: SearchRunRepository,
        listings: ListingRepository,
        recommendations: RecommendationRepository,
        research: ProductResearchService,
        sources: list[ListingSource],
        clock: Clock,
    ) -> None:
        self._runs = runs
        self._listings = listings
        self._recommendations = recommendations
        self._research = research
        self._sources = sources
        self._clock = clock

    @property
    def source_names(self) -> list[str]:
        return [source.source_name for source in self._sources]

    async def run(
        self,
        run_id: UUID,
        session_id: UUID,
        product_id: UUID,
        product: dict[str, Any],
        requirements: Requirements,
    ) -> None:
        del session_id
        await self._runs.set_status(run_id, RunStatus.RUNNING)
        brief_result, listing_result = await asyncio.gather(
            self._research.get_or_create(product_id, product),
            self._collect_listings(product_id, product, requirements),
            return_exceptions=True,
        )
        errors: dict[str, str] = {}
        if isinstance(brief_result, BaseException):
            errors["product_research"] = _safe_error(brief_result)
        collection = (
            listing_result
            if isinstance(listing_result, ListingCollection)
            else ListingCollection([], [], {"listings": _safe_error(listing_result)})
        )
        errors.update(collection.errors)
        ranked = _order_for_direction(
            rank_listings(collection.listings, requirements), requirements.search_direction
        )[:10]
        if ranked:
            persisted = [
                {
                    "search_run_id": str(run_id),
                    "listing_id": str(item.listing.id),
                    "rank": index,
                    "score": item.score,
                    "score_breakdown": {
                        **item.score_breakdown.model_dump(mode="json"),
                        "product_match": item.product_match_score,
                        "offer_quality": item.offer_quality_score,
                        "seller_trust": item.seller_trust_score,
                        "confidence": item.confidence,
                        "data_gaps": item.data_gaps,
                    },
                    "explanation": item.explanation
                    or "; ".join(
                        item.strengths
                        + ([item.risk_or_tradeoff] if item.risk_or_tradeoff else [])
                    ),
                }
                for index, item in enumerate(ranked, start=1)
                if item.listing.id is not None
            ]
            await self._recommendations.replace_for_run(run_id, persisted)
        status = (
            RunStatus.PARTIAL
            if ranked and errors
            else RunStatus.COMPLETED
            if ranked
            else RunStatus.FAILED
        )
        await self._runs.set_status(
            run_id,
            status,
            sources_succeeded=collection.sources_succeeded,
            error_summary=errors,
        )

    async def _collect_listings(
        self, product_id: UUID, product: dict[str, Any], requirements: Requirements
    ) -> ListingCollection:
        fresh_since = self._clock.now() - timedelta(hours=24)
        fresh = await self._listings.find_active(product_id, requirements, fresh_since)
        if len(fresh) >= 10:
            return ListingCollection(fresh, ["cache"], {})

        query = SearchQuery(
            product_id=product_id,
            model=str(product["model"]),
            budget_max=requirements.budget_max,
            currency=requirements.currency,
            variants=requirements.required_variants,
            location=requirements.location,
            limit=20,
        )
        results = await asyncio.gather(
            *(source.search(query) for source in self._sources), return_exceptions=True
        )
        observed_at = self._clock.now()
        succeeded: list[str] = []
        errors: dict[str, str] = {}
        fetched: list[NormalizedListing] = []
        for source, result in zip(self._sources, results, strict=True):
            if isinstance(result, BaseException):
                errors[source.source_name] = _safe_error(result)
                continue
            succeeded.append(source.source_name)
            for raw in result:
                try:
                    fetched.append(
                        normalize_listing(raw).model_copy(
                            update={"product_id": product_id, "retrieved_at": observed_at}
                        )
                    )
                except ValueError:
                    continue
        saved = (
            await self._listings.upsert_many(product_id, fetched, observed_at) if fetched else []
        )
        available = _merge_listings(fresh, saved)
        if errors or len(available) < 5:
            stale = await self._listings.find_active(product_id, requirements)
            available = _merge_listings(available, stale)
        return ListingCollection(available, succeeded, errors)


def _merge_listings(
    first: list[NormalizedListing], second: list[NormalizedListing]
) -> list[NormalizedListing]:
    merged = {(item.source, item.external_id): item for item in first}
    merged.update({(item.source, item.external_id): item for item in second})
    return list(merged.values())


def _order_for_direction(items: list[Any], direction: SearchDirection) -> list[Any]:
    if direction is SearchDirection.LOWEST_PRICE:
        return sorted(items, key=lambda item: (item.listing.price, -item.score))
    if direction is SearchDirection.MOST_SIMILAR:
        return sorted(items, key=lambda item: (-item.product_match_score, -item.score))
    if direction is SearchDirection.BEST_QUALITY:
        return sorted(items, key=lambda item: (-item.offer_quality_score, -item.score))
    return items


def _safe_error(error: BaseException) -> str:
    return f"{type(error).__name__}: {error}"[:300]
