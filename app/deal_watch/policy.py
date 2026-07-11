from datetime import datetime

from app.deal_watch.costs import calculate_landed_cost
from app.deal_watch.models import DealAction, DealDecision, DealMandate, MarketEvent
from app.domain.models import ListingCondition

CONDITION_RANK = {
    ListingCondition.UNKNOWN: 0,
    ListingCondition.FAIR: 1,
    ListingCondition.GOOD: 2,
    ListingCondition.VERY_GOOD: 3,
    ListingCondition.LIKE_NEW: 4,
    ListingCondition.NEW: 5,
}


def _normalized(value: str) -> str:
    return " ".join(value.casefold().split())


def evaluate_event(
    mandate: DealMandate, event: MarketEvent, evaluated_at: datetime
) -> DealDecision:
    landed_cost = calculate_landed_cost(event)
    hard_failures: list[str] = []
    uncertainties: list[str] = []

    if _normalized(event.exact_variant) != _normalized(mandate.exact_variant):
        hard_failures.append("variant_mismatch")
    if event.currency is not mandate.currency:
        hard_failures.append("currency_mismatch")
    if not event.in_stock:
        hard_failures.append("out_of_stock")
    if landed_cost.total > mandate.max_landed_cost:
        hard_failures.append("budget_exceeded")
    if CONDITION_RANK[event.condition] < CONDITION_RANK[mandate.min_condition]:
        hard_failures.append("condition_below_minimum")
    if mandate.min_seller_rating is not None:
        if event.seller_rating is None:
            uncertainties.append("seller_rating_unknown")
        elif event.seller_rating < mandate.min_seller_rating:
            hard_failures.append("seller_rating_below_minimum")
    if (
        event.claimed_original_price is not None
        and event.claimed_original_price <= event.item_price
    ):
        hard_failures.append("fake_discount")

    if hard_failures:
        action = DealAction.IGNORE
        reasons = hard_failures.copy()
    elif uncertainties:
        action = DealAction.HOLD
        reasons = uncertainties.copy()
    else:
        action = DealAction.ALERT
        reasons = [
            "exact_variant",
            "in_stock",
            "within_budget",
            "condition_accepted",
            "seller_accepted",
        ]

    return DealDecision(
        mandate_id=mandate.id,
        event_id=event.event_id,
        action=action,
        landed_cost=landed_cost,
        reasons=reasons,
        hard_failures=hard_failures,
        uncertainties=uncertainties,
        source_url=event.source_url,
        observed_at=event.observed_at,
        evaluated_at=evaluated_at,
    )

