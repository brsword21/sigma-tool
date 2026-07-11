from datetime import datetime
from decimal import Decimal
from enum import StrEnum
from typing import Any
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, HttpUrl, model_validator


class DomainModel(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)


class Currency(StrEnum):
    PLN = "PLN"
    EUR = "EUR"
    USD = "USD"


class ListingCondition(StrEnum):
    NEW = "new"
    LIKE_NEW = "like_new"
    VERY_GOOD = "very_good"
    GOOD = "good"
    FAIR = "fair"
    UNKNOWN = "unknown"


class RunStatus(StrEnum):
    PENDING = "pending"
    RUNNING = "running"
    PARTIAL = "partial"
    COMPLETED = "completed"
    FAILED = "failed"


class ConversationStage(StrEnum):
    DISCOVERY = "discovery"
    PRODUCT_SELECTION = "product_selection"
    SEARCHING = "searching"
    RESULTS = "results"


class ChangeIntent(StrEnum):
    RERANK = "rerank"
    REFETCH = "refetch"
    NEW_PRODUCT_RESEARCH = "new_product_research"


class SearchDirection(StrEnum):
    MOST_SIMILAR = "most_similar"
    BEST_QUALITY = "best_quality"
    LOWEST_PRICE = "lowest_price"
    BEST_VALUE = "best_value"


class ReferenceProduct(DomainModel):
    brand: str = Field(min_length=1)
    model: str = Field(min_length=1)
    exact_variant: str | None = None
    source_url: HttpUrl | None = None
    retrieved_at: datetime | None = None
    confidence: float = Field(default=1.0, ge=0, le=1)
    data_gaps: list[str] = Field(default_factory=list)


class Requirements(DomainModel):
    category: str = "headphones"
    budget_max: Decimal | None = Field(default=None, gt=0)
    currency: Currency = Currency.PLN
    required_variants: list[str] = Field(default_factory=list)
    required_features: list[str] = Field(default_factory=list)
    preferred_features: list[str] = Field(default_factory=list)
    preferred_colors: list[str] = Field(default_factory=list)
    location: str | None = None
    delivery_required: bool | None = None
    reference_product: ReferenceProduct | None = None
    search_direction: SearchDirection = SearchDirection.BEST_VALUE
    question_count: int = Field(default=0, ge=0, le=3)


class SearchQuery(DomainModel):
    product_id: UUID | None = None
    model: str = Field(min_length=1)
    budget_max: Decimal | None = Field(default=None, gt=0)
    currency: Currency = Currency.PLN
    variants: list[str] = Field(default_factory=list)
    location: str | None = None
    limit: int = Field(default=20, ge=1, le=100)


class RawListing(DomainModel):
    source: str = Field(min_length=1)
    external_id: str = Field(min_length=1)
    url: HttpUrl
    title: str = Field(min_length=1)
    price_text: str | None = None
    description: str | None = None
    attributes: dict[str, Any] = Field(default_factory=dict)
    image_urls: list[HttpUrl] = Field(default_factory=list)
    raw_payload: dict[str, Any] = Field(default_factory=dict)


class NewPriceBenchmark(DomainModel):
    product_name: str = Field(min_length=1)
    price: Decimal = Field(gt=0)
    currency: Currency = Currency.PLN
    url: HttpUrl
    source: str = "ceneo_firecrawl"
    retrieved_at: datetime


class NormalizedListing(DomainModel):
    id: UUID | None = None
    product_id: UUID | None = None
    source: str = Field(min_length=1)
    external_id: str = Field(min_length=1)
    url: HttpUrl
    title: str = Field(min_length=1)
    price: Decimal = Field(ge=0)
    currency: Currency = Currency.PLN
    condition: ListingCondition = ListingCondition.UNKNOWN
    color: str | None = None
    location: str | None = None
    delivery: bool | None = None
    exact_variant: str | None = None
    warranty: str | None = None
    returns: str | None = None
    seller_signals: dict[str, Any] = Field(default_factory=dict)
    description: str | None = None
    attributes: dict[str, Any] = Field(default_factory=dict)
    image_urls: list[HttpUrl] = Field(default_factory=list)
    raw_payload: dict[str, Any] = Field(default_factory=dict)
    first_seen_at: datetime | None = None
    last_seen_at: datetime | None = None
    retrieved_at: datetime | None = None
    confidence: float = Field(default=0.5, ge=0, le=1)
    data_gaps: list[str] = Field(default_factory=list)
    active: bool = True


class ScoreBreakdown(DomainModel):
    price: float = Field(ge=0, le=30)
    requirements: float = Field(ge=0, le=25)
    condition: float = Field(ge=0, le=20)
    completeness: float = Field(ge=0, le=10)
    logistics: float = Field(ge=0, le=10)
    preferences: float = Field(ge=0, le=5)
    risk_penalty: float = Field(ge=0, le=30)

    @property
    def total(self) -> float:
        positive = (
            self.price
            + self.requirements
            + self.condition
            + self.completeness
            + self.logistics
            + self.preferences
        )
        return round(max(0.0, min(100.0, positive - self.risk_penalty)), 2)


class RankedListing(DomainModel):
    listing: NormalizedListing
    score: float = Field(ge=0, le=100)
    score_breakdown: ScoreBreakdown
    strengths: list[str] = Field(default_factory=list, max_length=3)
    risk_or_tradeoff: str | None = None
    explanation: str | None = None
    product_match_score: float = Field(default=0, ge=0, le=100)
    offer_quality_score: float = Field(default=0, ge=0, le=100)
    seller_trust_score: float = Field(default=0, ge=0, le=100)
    confidence: float = Field(default=0.5, ge=0, le=1)
    data_gaps: list[str] = Field(default_factory=list)

    @model_validator(mode="after")
    def score_matches_breakdown(self) -> "RankedListing":
        if abs(self.score - self.score_breakdown.total) > 0.01:
            raise ValueError("score must equal score_breakdown.total")
        return self


class ApiError(DomainModel):
    code: str = Field(min_length=1)
    message: str = Field(min_length=1)
    details: dict[str, Any] = Field(default_factory=dict)
    request_id: str | None = None


class ErrorResponse(DomainModel):
    error: ApiError
