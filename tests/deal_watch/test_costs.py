from decimal import Decimal

import pytest
from pydantic import ValidationError

from app.deal_watch.costs import calculate_landed_cost
from app.deal_watch.models import MarketEvent
from app.domain.models import ListingCondition


def make_event(**changes: object) -> MarketEvent:
    values = {
        "event_id": "event-1",
        "source": "demo_merchant",
        "source_url": "https://example.com/offers/1",
        "exact_variant": "AirPods Pro 2 USB-C",
        "condition": ListingCondition.VERY_GOOD,
        "item_price": Decimal("399.99"),
        "shipping": Decimal("15.00"),
        "duties_tax": Decimal("10.00"),
        "fx_cost": Decimal("5.00"),
        "coupon_discount": Decimal("20.00"),
        "coupon_valid": True,
        "in_stock": True,
        "seller_rating": Decimal("4.8"),
    }
    values.update(changes)
    return MarketEvent.model_validate(values)


def test_calculates_auditable_landed_cost_with_valid_coupon() -> None:
    result = calculate_landed_cost(make_event())

    assert result.item_price == Decimal("399.99")
    assert result.shipping == Decimal("15.00")
    assert result.duties_tax == Decimal("10.00")
    assert result.fx_cost == Decimal("5.00")
    assert result.coupon_applied == Decimal("20.00")
    assert result.total == Decimal("409.99")


def test_invalid_coupon_is_visible_but_not_applied() -> None:
    result = calculate_landed_cost(make_event(coupon_valid=False))

    assert result.coupon_offered == Decimal("20.00")
    assert result.coupon_applied == Decimal("0.00")
    assert result.total == Decimal("429.99")


def test_total_cannot_fall_below_zero() -> None:
    result = calculate_landed_cost(
        make_event(
            item_price=Decimal("10.00"),
            shipping=Decimal("0"),
            duties_tax=Decimal("0"),
            fx_cost=Decimal("0"),
            coupon_discount=Decimal("50.00"),
        )
    )

    assert result.total == Decimal("0.00")


def test_negative_money_is_rejected() -> None:
    with pytest.raises(ValidationError):
        make_event(shipping=Decimal("-0.01"))

