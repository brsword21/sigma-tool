from datetime import UTC, datetime
from decimal import Decimal
from uuid import uuid4

import pytest

from app.deal_watch.models import CreateMandateRequest, DealAction
from app.deal_watch.repository import InMemoryDealWatchRepository
from app.deal_watch.scenarios import demo_market_events
from app.deal_watch.service import DealWatchService, MandateNotFoundError
from app.domain.models import ListingCondition

NOW = datetime(2026, 7, 11, 12, 0, tzinfo=UTC)


def request() -> CreateMandateRequest:
    return CreateMandateRequest(
        product_model="Apple AirPods Pro",
        exact_variant="AirPods Pro 2 USB-C",
        max_landed_cost=Decimal("500"),
        min_condition=ListingCondition.GOOD,
        min_seller_rating=Decimal("4.5"),
    )


@pytest.mark.asyncio
async def test_evaluates_demo_and_keeps_auditable_history() -> None:
    service = DealWatchService(InMemoryDealWatchRepository(), now=lambda: NOW)
    mandate = await service.create_mandate(request())

    decisions = await service.evaluate(mandate.id, demo_market_events())
    history = await service.history(mandate.id)

    assert len(decisions) == 6
    assert history == decisions
    assert [item.action for item in decisions].count(DealAction.ALERT) == 1
    assert [item.action for item in decisions].count(DealAction.HOLD) == 1
    assert [item.action for item in decisions].count(DealAction.IGNORE) == 4
    assert all(item.evaluated_at == NOW for item in decisions)


@pytest.mark.asyncio
async def test_unknown_mandate_is_a_controlled_domain_error() -> None:
    service = DealWatchService(InMemoryDealWatchRepository(), now=lambda: NOW)

    with pytest.raises(MandateNotFoundError):
        await service.evaluate(uuid4(), demo_market_events())


@pytest.mark.asyncio
async def test_repeated_market_event_does_not_emit_a_second_alert() -> None:
    service = DealWatchService(InMemoryDealWatchRepository(), now=lambda: NOW)
    mandate = await service.create_mandate(request())
    event = demo_market_events()[0]

    first = await service.evaluate(mandate.id, [event])
    repeated = await service.evaluate(mandate.id, [event])

    assert repeated == first
    assert await service.history(mandate.id) == first
