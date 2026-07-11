import json
from datetime import timedelta
from typing import Any
from uuid import UUID

from app.llm.schemas import ProductResearchOutput
from app.repositories.protocols import ProductResearchRepository
from app.services.ports import Clock, LLMClient

PRODUCT_RESEARCH_PROMPT_V1 = """Przygotuj zwięzły brief zakupu używanych słuchawek.
Podawaj wyłącznie fakty poparte faktycznymi URL-ami w sources. Uwzględnij parametry,
kontrole przed zakupem i znane ryzyka. Nie oceniaj ogłoszeń i nie ustalaj rankingu."""


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
        result = await self._llm.structured_response(
            system_prompt=PRODUCT_RESEARCH_PROMPT_V1,
            user_prompt=json.dumps(product, ensure_ascii=False, default=str),
            response_model=ProductResearchOutput,
        )
        payload = result.model_dump(mode="json")
        payload["refreshed_at"] = self._clock.now().isoformat()
        await self._repository.save(product_id, payload)
        return payload
