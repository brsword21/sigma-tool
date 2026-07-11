import asyncio
from uuid import UUID

from app.deal_watch.models import DealDecision, DealMandate


class InMemoryDealWatchRepository:
    def __init__(self) -> None:
        self._mandates: dict[UUID, DealMandate] = {}
        self._decisions: dict[UUID, list[DealDecision]] = {}
        self._lock = asyncio.Lock()

    async def save_mandate(self, mandate: DealMandate) -> None:
        async with self._lock:
            self._mandates[mandate.id] = mandate.model_copy(deep=True)
            self._decisions.setdefault(mandate.id, [])

    async def get_mandate(self, mandate_id: UUID) -> DealMandate | None:
        async with self._lock:
            mandate = self._mandates.get(mandate_id)
            return mandate.model_copy(deep=True) if mandate else None

    async def save_decisions_once(
        self, mandate_id: UUID, decisions: list[DealDecision]
    ) -> list[DealDecision]:
        async with self._lock:
            history = self._decisions.setdefault(mandate_id, [])
            by_event_id = {decision.event_id: decision for decision in history}
            persisted: list[DealDecision] = []
            for decision in decisions:
                stored = by_event_id.get(decision.event_id)
                if stored is None:
                    stored = decision.model_copy(deep=True)
                    history.append(stored)
                    by_event_id[stored.event_id] = stored
                persisted.append(stored.model_copy(deep=True))
            return persisted

    async def get_decisions(self, mandate_id: UUID) -> list[DealDecision]:
        async with self._lock:
            return [
                decision.model_copy(deep=True)
                for decision in self._decisions.get(mandate_id, [])
            ]
