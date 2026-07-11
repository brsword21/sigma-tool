import json
from statistics import median

from app.domain.models import RankedListing
from app.llm.schemas import RecommendationExplanationsOutput
from app.services.ports import LLMClient

EXPLANATION_PROMPT_V2 = """Piszesz po polsku krótkie wyjaśnienia rankingu ofert używanej
elektroniki. Odnoś się do rodzaju urządzenia wynikającego z danych, bez zakładania kategorii.
Zasady:
- Każde wyjaśnienie opiera się na faktach z TEJ konkretnej oferty: cena na tle median_price,
  kondycja baterii, pojemność/wariant, stan, gwarancja, zwroty, lokalizacja, szczegóły z tytułu
  i opisu.
- Wyjaśnienia różnych ofert nie mogą brzmieć tak samo — podkreśl, czym oferta różni się od
  pozostałych z listy (np. najtańsza, najlepsza bateria, jedyna z gwarancją).
- Zakaz ogólników typu "zgodność z preferencjami", "spełnia wymagania", "dobra oferta".
- Maksymalnie dwa zdania zalet oraz jedno konkretne ryzyko lub brak danych, oddzielone ";".
- Używaj wyłącznie faktów obecnych w przekazanych danych. Brak danych nazwij wprost.
- Nie zmieniaj punktacji ani kolejności."""


class RecommendationExplanationService:
    def __init__(self, llm: LLMClient) -> None:
        self._llm = llm

    async def explain(self, ranked: list[RankedListing]) -> dict[str, str]:
        if not ranked:
            return {}
        median_price = float(median(float(item.listing.price) for item in ranked))
        payload = [
            {
                "external_id": item.listing.external_id,
                "title": item.listing.title,
                "description": (item.listing.description or "")[:400],
                "attributes": item.listing.attributes,
                "price": str(item.listing.price),
                "median_price": median_price,
                "condition": item.listing.condition.value,
                "warranty": item.listing.warranty,
                "returns": item.listing.returns,
                "location": item.listing.location,
                "delivery": item.listing.delivery,
                "risk": item.risk_or_tradeoff,
                "data_gaps": item.data_gaps,
            }
            for item in ranked
        ]
        output = await self._llm.structured_response(
            system_prompt=EXPLANATION_PROMPT_V2,
            user_prompt=json.dumps(payload, ensure_ascii=False),
            response_model=RecommendationExplanationsOutput,
        )
        allowed = {item.listing.external_id for item in ranked}
        return {
            item.external_id: item.explanation
            for item in output.items
            if item.external_id in allowed
        }
