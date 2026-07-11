from datetime import UTC, datetime
from decimal import Decimal
from enum import StrEnum
from uuid import UUID, uuid4

from pydantic import BaseModel, ConfigDict, Field, HttpUrl, model_validator

from app.domain.models import Currency, ListingCondition


class DealWatchModel(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)


class MandateMode(StrEnum):
    ALERT_ONLY = "alert_only"


class DealAction(StrEnum):
    IGNORE = "ignore"
    HOLD = "hold"
    ALERT = "alert"


class CreateMandateRequest(DealWatchModel):
    product_model: str = Field(min_length=1, max_length=120)
    exact_variant: str = Field(min_length=1, max_length=120)
    max_landed_cost: Decimal = Field(gt=0, max_digits=12, decimal_places=2)
    currency: Currency = Currency.PLN
    min_condition: ListingCondition = ListingCondition.GOOD
    min_seller_rating: Decimal | None = Field(
        default=None, ge=0, le=5, max_digits=2, decimal_places=1
    )
    mode: MandateMode = MandateMode.ALERT_ONLY


class DealMandate(CreateMandateRequest):
    id: UUID = Field(default_factory=uuid4)
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))


class MarketEvent(DealWatchModel):
    event_id: str = Field(min_length=1, max_length=80)
    source: str = Field(min_length=1, max_length=80)
    source_url: HttpUrl
    exact_variant: str = Field(min_length=1, max_length=120)
    condition: ListingCondition
    item_price: Decimal = Field(ge=0, max_digits=12, decimal_places=4)
    currency: Currency = Currency.PLN
    shipping: Decimal = Field(default=Decimal("0"), ge=0, max_digits=12, decimal_places=4)
    duties_tax: Decimal = Field(
        default=Decimal("0"), ge=0, max_digits=12, decimal_places=4
    )
    fx_cost: Decimal = Field(default=Decimal("0"), ge=0, max_digits=12, decimal_places=4)
    coupon_discount: Decimal = Field(
        default=Decimal("0"), ge=0, max_digits=12, decimal_places=4
    )
    coupon_valid: bool = False
    in_stock: bool
    seller_rating: Decimal | None = Field(
        default=None, ge=0, le=5, max_digits=2, decimal_places=1
    )
    claimed_original_price: Decimal | None = Field(
        default=None, ge=0, max_digits=12, decimal_places=4
    )
    observed_at: datetime = Field(default_factory=lambda: datetime.now(UTC))


class EventBatch(DealWatchModel):
    events: list[MarketEvent] = Field(min_length=1, max_length=10)

    @model_validator(mode="after")
    def event_ids_are_unique(self) -> "EventBatch":
        event_ids = [event.event_id for event in self.events]
        if len(event_ids) != len(set(event_ids)):
            raise ValueError("event_id values must be unique within a batch")
        return self


class CostBreakdown(DealWatchModel):
    currency: Currency
    item_price: Decimal
    shipping: Decimal
    duties_tax: Decimal
    fx_cost: Decimal
    coupon_offered: Decimal
    coupon_applied: Decimal
    total: Decimal


class DealDecision(DealWatchModel):
    id: UUID = Field(default_factory=uuid4)
    mandate_id: UUID
    event_id: str
    action: DealAction
    landed_cost: CostBreakdown
    reasons: list[str] = Field(default_factory=list, max_length=12)
    hard_failures: list[str] = Field(default_factory=list, max_length=10)
    uncertainties: list[str] = Field(default_factory=list, max_length=10)
    source_url: HttpUrl
    observed_at: datetime
    evaluated_at: datetime


class DecisionSummary(DealWatchModel):
    alert: int = Field(ge=0)
    hold: int = Field(ge=0)
    ignore: int = Field(ge=0)


class DecisionBatchResponse(DealWatchModel):
    mandate_id: UUID
    decisions: list[DealDecision]
    summary: DecisionSummary

