from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import StrEnum


class CacheAction(StrEnum):
    RERANK = "rerank"
    REFETCH = "refetch"


@dataclass(frozen=True)
class CacheDecision:
    action: CacheAction
    reason: str


def decide_listing_cache(
    *,
    active_count: int,
    filtered_count: int,
    newest_seen_at: datetime | None,
    now: datetime,
    ttl: timedelta = timedelta(hours=24),
    sufficient_count: int = 10,
    refetch_below: int = 5,
) -> CacheDecision:
    if newest_seen_at is None or now - newest_seen_at > ttl:
        return CacheDecision(CacheAction.REFETCH, "missing_or_stale")
    if filtered_count < refetch_below:
        return CacheDecision(CacheAction.REFETCH, "too_few_after_hard_filters")
    if active_count < sufficient_count:
        return CacheDecision(CacheAction.REFETCH, "insufficient_active_listings")
    return CacheDecision(CacheAction.RERANK, "fresh_cache_sufficient")


def research_is_fresh(refreshed_at: datetime | None, now: datetime) -> bool:
    return refreshed_at is not None and now - refreshed_at <= timedelta(days=30)
