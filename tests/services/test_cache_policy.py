from datetime import UTC, datetime, timedelta

from app.services.cache_policy import CacheAction, decide_listing_cache, research_is_fresh

NOW = datetime(2026, 7, 11, 12, tzinfo=UTC)


def test_fresh_sufficient_cache_is_reranked() -> None:
    decision = decide_listing_cache(
        active_count=10, filtered_count=5, newest_seen_at=NOW - timedelta(hours=23), now=NOW
    )
    assert decision.action is CacheAction.RERANK


def test_hard_filters_below_five_force_refetch() -> None:
    decision = decide_listing_cache(active_count=20, filtered_count=4, newest_seen_at=NOW, now=NOW)
    assert decision.action is CacheAction.REFETCH


def test_research_ttl_is_thirty_days() -> None:
    assert research_is_fresh(NOW - timedelta(days=30), NOW)
    assert not research_is_fresh(NOW - timedelta(days=30, seconds=1), NOW)
