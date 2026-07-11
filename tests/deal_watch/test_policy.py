from datetime import UTC, datetime
from decimal import Decimal

from app.deal_watch.models import DealAction, DealMandate, MarketEvent
from app.deal_watch.policy import evaluate_event
from app.domain.models import ListingCondition


def make_mandate(**changes: object) -> DealMandate:
    values = {
        "product_model": "Apple AirPods Pro",
        "exact_variant": "AirPods Pro 2 USB-C",
        "max_landed_cost": Decimal("500.00"),
        "min_condition": ListingCondition.GOOD,
        "min_seller_rating": Decimal("4.5"),
    }
    values.update(changes)
    return DealMandate.model_validate(values)


def make_event(**changes: object) -> MarketEvent:
    values = {
        "event_id": "event-1",
        "source": "demo_merchant",
        "source_url": "https://example.com/offers/1",
        "exact_variant": "AirPods Pro 2 USB-C",
        "condition": ListingCondition.VERY_GOOD,
        "item_price": Decimal("430.00"),
        "shipping": Decimal("10.00"),
        "in_stock": True,
        "seller_rating": Decimal("4.8"),
    }
    values.update(changes)
    return MarketEvent.model_validate(values)


NOW = datetime(2026, 7, 11, 12, 0, tzinfo=UTC)


def test_alerts_only_when_all_hard_conditions_are_satisfied() -> None:
    decision = evaluate_event(make_mandate(), make_event(), NOW)

    assert decision.action is DealAction.ALERT
    assert decision.hard_failures == []
    assert decision.uncertainties == []
    assert decision.landed_cost.total == Decimal("440.00")


def test_ignores_every_explicit_hard_failure() -> None:
    cases = [
        (make_event(exact_variant="AirPods Pro 1"), "variant_mismatch"),
        (make_event(in_stock=False), "out_of_stock"),
        (make_event(item_price=Decimal("510")), "budget_exceeded"),
        (make_event(condition=ListingCondition.FAIR), "condition_below_minimum"),
        (make_event(seller_rating=Decimal("4.2")), "seller_rating_below_minimum"),
        (
            make_event(claimed_original_price=Decimal("400")),
            "fake_discount",
        ),
    ]

    for event, expected_failure in cases:
        decision = evaluate_event(make_mandate(), event, NOW)
        assert decision.action is DealAction.IGNORE
        assert expected_failure in decision.hard_failures


def test_holds_when_required_seller_rating_is_unknown() -> None:
    decision = evaluate_event(make_mandate(), make_event(seller_rating=None), NOW)

    assert decision.action is DealAction.HOLD
    assert decision.hard_failures == []
    assert decision.uncertainties == ["seller_rating_unknown"]


def test_currency_mismatch_is_not_an_alert() -> None:
    decision = evaluate_event(make_mandate(), make_event(currency="EUR"), NOW)

    assert decision.action is DealAction.IGNORE
    assert "currency_mismatch" in decision.hard_failures

