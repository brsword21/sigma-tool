from typing import Any, Literal

from pydantic import Field, HttpUrl

from app.domain.models import ChangeIntent, DomainModel, Requirements


class ProductSuggestion(DomainModel):
    brand: str
    model: str
    estimated_used_price_pln: int = Field(gt=0)
    key_features: list[str] = Field(min_length=1, max_length=4)
    why_it_fits: str
    tradeoff: str
    image_url: HttpUrl | None = None


class ConversationOutput(DomainModel):
    requirements: Requirements
    missing_critical_information: bool
    question: str | None = None
    suggestions: list[ProductSuggestion] = Field(default_factory=list, max_length=6)
    change_intent: ChangeIntent = ChangeIntent.RERANK


class ProductResearchOutput(DomainModel):
    summary: str
    key_parameters: dict[str, Any]
    second_hand_checks: list[str] = Field(min_length=1, max_length=8)
    known_risks: list[str] = Field(max_length=8)
    sources: list[HttpUrl] = Field(min_length=1, max_length=10)
    research_version: Literal["v1"] = "v1"
