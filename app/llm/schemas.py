from typing import Any, Literal

from pydantic import Field, HttpUrl, model_validator

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
    missing_critical_information: bool = False
    question: str | None = None
    reference_product: ReferenceProduct | None = None
    suggestions: list[ProductSuggestion] = Field(default_factory=list, max_length=10)
    change_intent: ChangeIntent = ChangeIntent.RERANK

    @model_validator(mode="before")
    @classmethod
    def discard_incomplete_reference_products(cls, value: Any) -> Any:
        if not isinstance(value, dict):
            return value
        normalized = dict(value)
        if normalized.get("change_intent") is None:
            normalized["change_intent"] = ChangeIntent.RERANK
        reference = normalized.get("reference_product")
        if isinstance(reference, dict) and not (
            reference.get("brand") and reference.get("model")
        ):
            normalized["reference_product"] = None
        requirements = normalized.get("requirements")
        if isinstance(requirements, dict):
            normalized_requirements = dict(requirements)
            nested_reference = normalized_requirements.get("reference_product")
            if isinstance(nested_reference, dict) and not (
                nested_reference.get("brand") and nested_reference.get("model")
            ):
                normalized_requirements["reference_product"] = None
            normalized["requirements"] = normalized_requirements
        return normalized

    @model_validator(mode="after")
    def conversation_state_is_consistent(self) -> "ConversationOutput":
        if self.missing_critical_information:
            if not self.question or self.suggestions:
                raise ValueError("clarification requires one question and no suggestions")
        elif not 4 <= len(self.suggestions) <= 10:
            raise ValueError("ready conversation requires 4-10 candidates")
        return self


class ResearchParameter(DomainModel):
    name: str = Field(min_length=1, max_length=60)
    value: str = Field(min_length=1, max_length=200)


class ProductResearchOutput(DomainModel):
    summary: str
    key_parameters: list[ResearchParameter] = Field(default_factory=list, max_length=12)
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
