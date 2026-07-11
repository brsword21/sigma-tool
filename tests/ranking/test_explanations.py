from decimal import Decimal

from app.domain.models import ListingCondition, NormalizedListing, Requirements
from app.llm.schemas import (
    RecommendationExplanation,
    RecommendationExplanationsOutput,
)
from app.ranking.engine import rank_listings
from app.ranking.explanations import RecommendationExplanationService


class ExplanationLLM:
    async def structured_response(self, **kwargs: object) -> RecommendationExplanationsOutput:
        return RecommendationExplanationsOutput(
            items=[
                RecommendationExplanation(
                    external_id="offer-1",
                    strengths=["cena"],
                    risk_or_tradeoff="brak danych o baterii",
                    explanation="Korzystna cena; brak danych o baterii.",
                )
            ]
        )


async def test_batch_explanation_is_mapped_by_external_id() -> None:
    listing = NormalizedListing(
        source="fixture",
        external_id="offer-1",
        url="https://example.com/offer-1",
        title="Sony WF-XM0",
        price=Decimal("400"),
        condition=ListingCondition.VERY_GOOD,
    )
    ranked = rank_listings([listing], Requirements())
    explanations = await RecommendationExplanationService(ExplanationLLM()).explain(ranked)
    assert explanations == {"offer-1": "Korzystna cena; brak danych o baterii."}
