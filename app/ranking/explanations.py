import json

from app.domain.models import RankedListing
from app.llm.schemas import RecommendationExplanationsOutput
from app.services.ports import LLMClient

EXPLANATION_PROMPT_V1 = """Formułuj krótkie polskie wyjaśnienia rankingu ofert używanej
elektroniki. Odnoś się do rodzaju urządzenia wynikającego z danych, bez zakładania kategorii.
Używaj wyłącznie faktów obecnych w przekazanych danych. Nie zmieniaj punktacji ani kolejności.
Dla każdej oferty zwróć maksymalnie trzy zalety i jedno ryzyko. Brak danych nazwij wprost."""


class RecommendationExplanationService:
    def __init__(self, llm: LLMClient) -> None:
        self._llm = llm

    async def explain(self, ranked: list[RankedListing]) -> dict[str, str]:
        if not ranked:
            return {}
        payload = [
            {
                "external_id": item.listing.external_id,
                "title": item.listing.title,
                "price": str(item.listing.price),
                "condition": item.listing.condition.value,
                "score_breakdown": item.score_breakdown.model_dump(mode="json"),
                "strengths": item.strengths,
                "risk": item.risk_or_tradeoff,
                "data_gaps": item.data_gaps,
            }
            for item in ranked
        ]
        output = await self._llm.structured_response(
            system_prompt=EXPLANATION_PROMPT_V1,
            user_prompt=json.dumps(payload, ensure_ascii=False),
            response_model=RecommendationExplanationsOutput,
        )
        allowed = {item.listing.external_id for item in ranked}
        return {
            item.external_id: item.explanation
            for item in output.items
            if item.external_id in allowed
        }
