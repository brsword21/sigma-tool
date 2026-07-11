from decimal import Decimal

from app.domain.models import ListingCondition, NormalizedListing, Requirements
from app.ranking.engine import rank_listings


def listing(
    external_id: str, price: str, condition: ListingCondition, description: str, images: int = 2
) -> NormalizedListing:
    return NormalizedListing(
        source="fixture",
        external_id=external_id,
        url=f"https://example.com/{external_id}",
        title="Sony WH-1000XM4 blue ANC",
        price=Decimal(price),
        condition=condition,
        color="blue",
        delivery=True,
        description=description,
        attributes={"variant": "wireless", "feature": "ANC"},
        image_urls=[f"https://example.com/{external_id}-{index}.jpg" for index in range(images)],
    )


def test_three_listings_get_stable_order_and_exact_breakdown() -> None:
    description = (
        "Kompletne sprawne słuchawki z etui, ładowarką i możliwością wysyłki, bez widocznych wad."
    )
    results = rank_listings(
        [
            listing("cheap-risk", "150", ListingCondition.UNKNOWN, "Krótki opis", 0),
            listing("best", "420", ListingCondition.VERY_GOOD, description, 4),
            listing("expensive", "500", ListingCondition.GOOD, description),
        ],
        Requirements(
            budget_max=Decimal("500"),
            required_features=["ANC"],
            preferred_colors=["blue"],
            delivery_required=True,
        ),
    )
    assert [item.listing.external_id for item in results] == ["best", "expensive", "cheap-risk"]
    assert results[0].score == results[0].score_breakdown.total
    assert len(results[0].strengths) == 3
    assert results[-1].score_breakdown.risk_penalty > 0


def test_hard_budget_filter_runs_before_scoring() -> None:
    results = rank_listings(
        [listing("over", "501", ListingCondition.NEW, "x" * 100)],
        Requirements(budget_max=Decimal("500")),
    )
    assert results == []
