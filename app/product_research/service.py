import json
from datetime import timedelta
from typing import Any
from uuid import UUID

from app.llm.schemas import ProductResearchOutput
from app.repositories.protocols import ProductResearchRepository
from app.services.ports import Clock, LLMClient

PRODUCT_RESEARCH_PROMPT_V1 = """Przygotuj zwięzły brief zakupu używanych słuchawek.
Podawaj jako potwierdzone wyłącznie fakty poparte URL-ami z pola allowed_sources wejścia.
Nie twórz nowych URL-i. Gdy źródeł brakuje, zwróć sources=[], obniż confidence i wpisz
unverified_product_research do data_gaps. Możesz podać ogólne kontrole przed zakupem,
ale oznacz niepotwierdzone ryzyka jako braki danych. Parametry zwróć jako listę par
name/value. Nie oceniaj ogłoszeń ani rankingu."""


class ProductResearchService:
    def __init__(self, repository: ProductResearchRepository, llm: LLMClient, clock: Clock) -> None:
        self._repository = repository
        self._llm = llm
        self._clock = clock

    async def get_or_create(self, product_id: UUID, product: dict[str, Any]) -> dict[str, Any]:
        fresh_since = self._clock.now() - timedelta(days=30)
        cached = await self._repository.get_fresh(product_id, fresh_since)
        if cached is not None:
            return cached
        allowed_sources = _allowed_sources(product)
        result = await self._llm.structured_response(
            system_prompt=PRODUCT_RESEARCH_PROMPT_V1,
            user_prompt=json.dumps(
                {"product": product, "allowed_sources": allowed_sources},
                ensure_ascii=False,
                default=str,
            ),
            response_model=ProductResearchOutput,
        )
        payload = result.model_dump(mode="json")
        payload["key_parameters"] = {
            parameter.name: parameter.value for parameter in result.key_parameters
        }
        payload["sources"] = [
            str(source) for source in result.sources if str(source) in allowed_sources
        ]
        if not payload["sources"]:
            payload["confidence"] = min(float(payload.get("confidence", 0.5)), 0.4)
            payload["data_gaps"] = sorted(
                {*payload.get("data_gaps", []), "unverified_product_research"}
            )
        payload["refreshed_at"] = self._clock.now().isoformat()
        await self._repository.save(product_id, payload)
        return payload


def _allowed_sources(product: dict[str, Any]) -> list[str]:
    specifications = product.get("specifications") or {}
    candidates = [product.get("source_url"), specifications.get("source_url")]
    candidates.extend(specifications.get("sources") or [])
    return [str(value) for value in candidates if value]
