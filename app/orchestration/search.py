import asyncio
from dataclasses import dataclass
from datetime import datetime, timedelta
from time import perf_counter
from typing import Any
from uuid import UUID

from app.domain.models import (
    NewPriceBenchmark,
    NormalizedListing,
    Requirements,
    RunStatus,
    SearchDirection,
    SearchQuery,
)
from app.listings.normalizer import normalize_listing
from app.observability import log_event
from app.product_matching import is_direct_olx_listing_url
from app.product_research.service import ProductResearchService
from app.ranking.engine import matches_exact_product, rank_listings
from app.ranking.explanations import RecommendationExplanationService
from app.repositories.protocols import (
    ListingRepository,
    RecommendationRepository,
    SearchRunRepository,
)
from app.services.ports import Clock
from app.sources.base import ListingSource, NewPriceBenchmarkSource

TOP_RESULTS = 5
TOTAL_RESULTS = 20
PRODUCT_RESEARCH_TIMEOUT_SECONDS = 15
SOURCE_TIMEOUT_SECONDS = 25
RUN_TIMEOUT_SECONDS = 40


@dataclass(frozen=True)
class ListingCollection:
    listings: list[NormalizedListing]
    sources_succeeded: list[str]
    errors: dict[str, str]
    source_timings_ms: dict[str, int]
    stale_count: int = 0


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
        explanations: RecommendationExplanationService | None = None,
        benchmark_source: NewPriceBenchmarkSource | None = None,
    ) -> None:
        self._runs = runs
        self._listings = listings
        self._recommendations = recommendations
        self._research = research
        self._sources = sources
        self._clock = clock
        self._explanations = explanations
        self._benchmark_source = benchmark_source

    @property
    def source_names(self) -> list[str]:
        names = [source.source_name for source in self._sources]
        if self._benchmark_source is not None:
            names.append(self._benchmark_source.source_name)
        return names

    async def run(
        self,
        run_id: UUID,
        session_id: UUID,
        product_id: UUID,
        product: dict[str, Any],
        requirements: Requirements,
        allow_fetch: bool = True,
    ) -> None:
        try:
            await asyncio.wait_for(
                self._run(
                    run_id,
                    session_id,
                    product_id,
                    product,
                    requirements,
                    allow_fetch,
                ),
                timeout=RUN_TIMEOUT_SECONDS,
            )
        except Exception as exc:
            error = _safe_error(exc)
            try:
                await self._runs.set_status(
                    run_id,
                    RunStatus.FAILED,
                    error_summary={"orchestrator": error},
                )
            except Exception as persistence_error:
                log_event(
                    "search_run_failure_unpersisted",
                    run_id=run_id,
                    error=error,
                    persistence_error=_safe_error(persistence_error),
                )
                return
            log_event("search_run_failed", run_id=run_id, error=error)

    async def _run(
        self,
        run_id: UUID,
        session_id: UUID,
        product_id: UUID,
        product: dict[str, Any],
        requirements: Requirements,
        allow_fetch: bool = True,
    ) -> None:
        del session_id
        started = perf_counter()
        log_event(
            "search_run_started",
            run_id=run_id,
            product_id=product_id,
            direction=requirements.search_direction.value,
        )
        await self._runs.set_status(run_id, RunStatus.RUNNING)
        benchmark_query = SearchQuery(
            product_id=product_id,
            model=str(
                product.get("canonical_name")
                or f"{product.get('brand', '')} {product['model']}".strip()
            ),
            variants=requirements.required_variants,
            limit=10,
        )
        brief_result, listing_result, benchmark_result = await asyncio.gather(
            asyncio.wait_for(
                self._research.get_or_create(product_id, product),
                timeout=PRODUCT_RESEARCH_TIMEOUT_SECONDS,
            ),
            self._collect_listings(product_id, product, requirements, allow_fetch=allow_fetch),
            _timed_benchmark(self._benchmark_source, benchmark_query, self._clock.now()),
            return_exceptions=True,
        )
        errors: dict[str, str] = {}
        brief = brief_result if isinstance(brief_result, dict) else None
        if isinstance(brief_result, BaseException):
            errors["product_research"] = _safe_error(brief_result)
        collection = (
            listing_result
            if isinstance(listing_result, ListingCollection)
            else ListingCollection([], [], {"listings": _safe_error(listing_result)}, {})
        )
        errors.update(collection.errors)
        benchmark: NewPriceBenchmark | None = None
        benchmark_timing_ms = 0
        if isinstance(benchmark_result, tuple):
            benchmark, benchmark_error, benchmark_timing_ms = benchmark_result
            if benchmark_error is not None and self._benchmark_source is not None:
                errors[self._benchmark_source.source_name] = _safe_error(benchmark_error)
            elif benchmark is None and self._benchmark_source is not None:
                errors[self._benchmark_source.source_name] = "No matching Ceneo product with price"
        elif isinstance(benchmark_result, BaseException) and self._benchmark_source is not None:
            errors[self._benchmark_source.source_name] = _safe_error(benchmark_result)
        expected_variant = str(
            (product.get("specifications") or {}).get("exact_variant")
            or product.get("model")
            or ""
        )
        verified: list[NormalizedListing] = []
        rejected_variants = 0
        for listing in collection.listings:
            if not matches_exact_product(listing, product):
                rejected_variants += 1
                continue
            verified.append(
                listing
                if listing.exact_variant
                else listing.model_copy(update={"exact_variant": expected_variant})
            )
        ranked = _order_for_direction(
            rank_listings(verified, requirements, brief), requirements.search_direction
        )[:TOTAL_RESULTS]
        explanations: dict[str, str] = {}
        if ranked and self._explanations is not None:
            try:
                explanations = await self._explanations.explain(ranked)
            except Exception as exc:
                errors["explanations"] = _safe_error(exc)
        if ranked:
            persisted = [
                {
                    "search_run_id": str(run_id),
                    "listing_id": str(item.listing.id),
                    "rank": index,
                    "tier": "top" if index <= TOP_RESULTS else "secondary",
                    "recommended": index == 1,
                    "score": item.score,
                    "score_breakdown": {
                        **item.score_breakdown.model_dump(mode="json"),
                        "product_match": item.product_match_score,
                        "offer_quality": item.offer_quality_score,
                        "seller_trust": item.seller_trust_score,
                        "confidence": item.confidence,
                        "data_gaps": item.data_gaps,
                    },
                    "explanation": explanations.get(item.listing.external_id)
                    or item.explanation
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
        sources_succeeded = list(collection.sources_succeeded)
        if benchmark is not None and self._benchmark_source is not None:
            sources_succeeded.append(self._benchmark_source.source_name)
        await self._runs.set_status(
            run_id,
            status,
            sources_succeeded=sources_succeeded,
            error_summary=errors,
            new_price_benchmark=(benchmark.model_dump(mode="json") if benchmark else None),
        )
        log_event(
            "search_run_finished",
            run_id=run_id,
            status=status.value,
            duration_ms=round((perf_counter() - started) * 1000),
            source_timings_ms=collection.source_timings_ms,
            benchmark_timing_ms=benchmark_timing_ms,
            stale_cache_count=collection.stale_count,
            rejected_variant_count=rejected_variants,
            recommendation_count=len(ranked),
        )

    async def _collect_listings(
        self,
        product_id: UUID,
        product: dict[str, Any],
        requirements: Requirements,
        *,
        allow_fetch: bool = True,
    ) -> ListingCollection:
        fresh_since = self._clock.now() - timedelta(hours=24)
        fresh = _usable_listings(
            await self._listings.find_active(product_id, requirements, fresh_since)
        )
        if not allow_fetch:
            cached = _usable_listings(await self._listings.find_active(product_id, requirements))
            stale_count = 0
            marked: list[NormalizedListing] = []
            for listing in cached:
                if listing.last_seen_at is not None and listing.last_seen_at < fresh_since:
                    marked.append(
                        listing.model_copy(
                            update={
                                "confidence": min(listing.confidence, 0.4),
                                "data_gaps": sorted({*listing.data_gaps, "stale_cache"}),
                            }
                        )
                    )
                    stale_count += 1
                else:
                    marked.append(listing)
            log_event(
                "listing_cache_used",
                product_id=product_id,
                count=len(marked),
                stale=stale_count > 0,
                reason="rerank",
            )
            return ListingCollection(marked, ["cache"], {}, {}, stale_count)
        if len(fresh) >= 10:
            log_event("listing_cache_used", product_id=product_id, count=len(fresh), stale=False)
            return ListingCollection(fresh, ["cache"], {}, {})

        query = SearchQuery(
            product_id=product_id,
            model=str(
                product.get("canonical_name")
                or f"{product.get('brand', '')} {product['model']}".strip()
            ),
            budget_max=requirements.budget_max,
            currency=requirements.currency,
            variants=requirements.required_variants,
            location=requirements.location,
            limit=20,
        )
        log_event(
            "listing_fetch_started",
            product_id=product_id,
            source_names=self.source_names,
            cached_fresh_count=len(fresh),
        )
        results = await asyncio.gather(*(_timed_search(source, query) for source in self._sources))
        observed_at = self._clock.now()
        succeeded: list[str] = []
        errors: dict[str, str] = {}
        fetched: list[NormalizedListing] = []
        source_timings_ms: dict[str, int] = {}
        for source, (result, source_error, duration_ms) in zip(
            self._sources, results, strict=True
        ):
            source_timings_ms[source.source_name] = duration_ms
            log_event(
                "source_finished",
                source=source.source_name,
                duration_ms=duration_ms,
                success=source_error is None,
                result_count=len(result),
            )
            if source_error is not None:
                errors[source.source_name] = _safe_error(source_error)
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
        stale_count = 0
        if errors or len(available) < 5:
            stale = _usable_listings(await self._listings.find_active(product_id, requirements))
            marked_stale: list[NormalizedListing] = []
            for listing in stale:
                if listing.last_seen_at is not None and listing.last_seen_at < fresh_since:
                    marked_stale.append(
                        listing.model_copy(
                            update={
                                "confidence": min(listing.confidence, 0.4),
                                "data_gaps": sorted({*listing.data_gaps, "stale_cache"}),
                            }
                        )
                    )
                    stale_count += 1
                else:
                    marked_stale.append(listing)
            available = _merge_listings(available, marked_stale)
        return ListingCollection(available, succeeded, errors, source_timings_ms, stale_count)


async def _timed_search(
    source: ListingSource, query: SearchQuery
) -> tuple[list[Any], BaseException | None, int]:
    started = perf_counter()
    try:
        return (
            await asyncio.wait_for(source.search(query), timeout=SOURCE_TIMEOUT_SECONDS),
            None,
            round((perf_counter() - started) * 1000),
        )
    except BaseException as exc:
        return [], exc, round((perf_counter() - started) * 1000)


async def _timed_benchmark(
    source: NewPriceBenchmarkSource | None,
    query: SearchQuery,
    retrieved_at: datetime,
) -> tuple[NewPriceBenchmark | None, BaseException | None, int]:
    if source is None:
        return None, None, 0
    started = perf_counter()
    try:
        benchmark = await asyncio.wait_for(
            source.get_benchmark(query, retrieved_at), timeout=SOURCE_TIMEOUT_SECONDS
        )
        return benchmark, None, round((perf_counter() - started) * 1000)
    except BaseException as exc:
        return None, exc, round((perf_counter() - started) * 1000)


def _merge_listings(
    first: list[NormalizedListing], second: list[NormalizedListing]
) -> list[NormalizedListing]:
    merged = {(item.source, item.external_id): item for item in first}
    merged.update({(item.source, item.external_id): item for item in second})
    return list(merged.values())


def _usable_listings(listings: list[NormalizedListing]) -> list[NormalizedListing]:
    return [
        listing
        for listing in listings
        if listing.source != "olx_firecrawl" or is_direct_olx_listing_url(str(listing.url))
    ]


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
