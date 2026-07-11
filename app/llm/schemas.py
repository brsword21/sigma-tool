from typing import Any, Literal

from pydantic import Field, HttpUrl

from app.domain.models import ChangeIntent, DomainModel, ReferenceProduct, Requirements


class ProductSuggestion(DomainModel):
    brand: str
    model: str
    estimated_used_price_pln: int = Field(gt=0)
    key_features: list[str] = Field(min_length=1, max_length=4)
    similarity_reasons: list[str] = Field(default_factory=list, max_length=4)
    differences: list[str] = Field(default_factory=list, max_length=4)
    why_it_fits: str
    tradeoff: str
    image_url: HttpUrl | None = None
    source_url: HttpUrl | None = None
    confidence: float = Field(default=0.5, ge=0, le=1)
    data_gaps: list[str] = Field(default_factory=list)
    exact_variant: str | None = None

    @property
    def estimated_price(self) -> int:
        return self.estimated_used_price_pln


class ConversationOutput(DomainModel):
    requirements: Requirements
    missing_critical_information: bool
    question: str | None = None
    reference_product: ReferenceProduct | None = None
    suggestions: list[ProductSuggestion] = Field(default_factory=list, max_length=10)
    change_intent: ChangeIntent = ChangeIntent.RERANK


class ProductResearchOutput(DomainModel):
    summary: str
    key_parameters: dict[str, Any]
    second_hand_checks: list[str] = Field(min_length=1, max_length=8)
    known_risks: list[str] = Field(max_length=8)
    sources: list[HttpUrl] = Field(default_factory=list, max_length=10)
    confidence: float = Field(default=0.5, ge=0, le=1)
    data_gaps: list[str] = Field(default_factory=list)
    research_version: Literal["v1"] = "v1"


class RecommendationExplanation(DomainModel):
    external_id: str
    strengths: list[str] = Field(default_factory=list, max_length=3)
    risk_or_tradeoff: str | None = None
    explanation: str


class RecommendationExplanationsOutput(DomainModel):
    items: list[RecommendationExplanation] = Field(max_length=10)
