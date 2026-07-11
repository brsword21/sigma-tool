from collections.abc import Callable
from datetime import UTC, datetime
from uuid import UUID

from app.deal_watch.models import (
    CreateMandateRequest,
    DealDecision,
    DealMandate,
    MarketEvent,
)
from app.deal_watch.policy import evaluate_event
from app.deal_watch.repository import InMemoryDealWatchRepository


class MandateNotFoundError(LookupError):
    pass


class DealWatchService:
    def __init__(
        self,
        repository: InMemoryDealWatchRepository,
        *,
        now: Callable[[], datetime] | None = None,
    ) -> None:
        self._repository = repository
        self._now = now or (lambda: datetime.now(UTC))

    async def create_mandate(self, request: CreateMandateRequest) -> DealMandate:
        mandate = DealMandate(
            **request.model_dump(),
            created_at=self._now(),
        )
        await self._repository.save_mandate(mandate)
        return mandate

    async def evaluate(
        self, mandate_id: UUID, events: list[MarketEvent]
    ) -> list[DealDecision]:
        mandate = await self._repository.get_mandate(mandate_id)
        if mandate is None:
            raise MandateNotFoundError
        evaluated_at = self._now()
        decisions = [
            evaluate_event(mandate, event, evaluated_at)
            for event in events
        ]
        return await self._repository.save_decisions_once(mandate_id, decisions)

    async def history(self, mandate_id: UUID) -> list[DealDecision]:
        if await self._repository.get_mandate(mandate_id) is None:
            raise MandateNotFoundError
        return await self._repository.get_decisions(mandate_id)
