from decimal import ROUND_HALF_UP, Decimal

from app.deal_watch.models import CostBreakdown, MarketEvent

CENT = Decimal("0.01")


def _money(value: Decimal) -> Decimal:
    return value.quantize(CENT, rounding=ROUND_HALF_UP)


def calculate_landed_cost(event: MarketEvent) -> CostBreakdown:
    coupon_applied = event.coupon_discount if event.coupon_valid else Decimal("0")
    raw_total = (
        event.item_price
        + event.shipping
        + event.duties_tax
        + event.fx_cost
        - coupon_applied
    )
    return CostBreakdown(
        currency=event.currency,
        item_price=_money(event.item_price),
        shipping=_money(event.shipping),
        duties_tax=_money(event.duties_tax),
        fx_cost=_money(event.fx_cost),
        coupon_offered=_money(event.coupon_discount),
        coupon_applied=_money(coupon_applied),
        total=_money(max(Decimal("0"), raw_total)),
    )

