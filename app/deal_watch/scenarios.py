from datetime import UTC, datetime
from decimal import Decimal

from app.deal_watch.models import MarketEvent
from app.domain.models import ListingCondition

OBSERVED_AT = datetime(2026, 7, 11, 10, 0, tzinfo=UTC)


def demo_market_events() -> list[MarketEvent]:
    common = {
        "source": "phase5_demo",
        "exact_variant": "AirPods Pro 2 USB-C",
        "condition": ListingCondition.VERY_GOOD,
        "currency": "PLN",
        "shipping": Decimal("15.00"),
        "in_stock": True,
        "seller_rating": Decimal("4.8"),
        "observed_at": OBSERVED_AT,
    }
    def event(**values: object) -> MarketEvent:
        return MarketEvent.model_validate({**common, **values})

    return [
        event(
            event_id="real-deal",
            source_url="https://example.com/phase5/real-deal",
            item_price=Decimal("399.00"),
            claimed_original_price=Decimal("599.00"),
        ),
        event(
            event_id="wrong-variant",
            source_url="https://example.com/phase5/wrong-variant",
            exact_variant="AirPods Pro 1 Lightning",
            item_price=Decimal("250.00"),
        ),
        event(
            event_id="shipping-trap",
            source_url="https://example.com/phase5/shipping-trap",
            item_price=Decimal("450.00"),
            shipping=Decimal("80.00"),
        ),
        event(
            event_id="out-of-stock",
            source_url="https://example.com/phase5/out-of-stock",
            item_price=Decimal("380.00"),
            in_stock=False,
        ),
        event(
            event_id="seller-unknown",
            source_url="https://example.com/phase5/seller-unknown",
            item_price=Decimal("390.00"),
            seller_rating=None,
        ),
        event(
            event_id="fake-discount",
            source_url="https://example.com/phase5/fake-discount",
            item_price=Decimal("430.00"),
            claimed_original_price=Decimal("400.00"),
        ),
    ]
