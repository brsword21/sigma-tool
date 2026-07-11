from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Request, status

from app.deal_watch.models import (
    CreateMandateRequest,
    DealAction,
    DealDecision,
    DealMandate,
    DecisionBatchResponse,
    DecisionSummary,
    EventBatch,
)
from app.deal_watch.scenarios import demo_market_events
from app.deal_watch.service import DealWatchService, MandateNotFoundError

router = APIRouter(prefix="/deal-watch", tags=["deal-watch"])


def get_deal_watch(request: Request) -> DealWatchService:
    return request.app.state.deal_watch


DealWatch = Annotated[DealWatchService, Depends(get_deal_watch)]


def _response(mandate_id: UUID, decisions: list[DealDecision]) -> DecisionBatchResponse:
    return DecisionBatchResponse(
        mandate_id=mandate_id,
        decisions=decisions,
        summary=DecisionSummary(
            alert=sum(item.action is DealAction.ALERT for item in decisions),
            hold=sum(item.action is DealAction.HOLD for item in decisions),
            ignore=sum(item.action is DealAction.IGNORE for item in decisions),
        ),
    )


def _not_found() -> HTTPException:
    return HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail={"code": "mandate_not_found"},
    )


@router.post("/mandates", response_model=DealMandate, status_code=status.HTTP_201_CREATED)
async def create_mandate(
    payload: CreateMandateRequest, service: DealWatch
) -> DealMandate:
    return await service.create_mandate(payload)


@router.post("/mandates/{mandate_id}/events", response_model=DecisionBatchResponse)
async def evaluate_events(
    mandate_id: UUID, payload: EventBatch, service: DealWatch
) -> DecisionBatchResponse:
    try:
        decisions = await service.evaluate(mandate_id, payload.events)
    except MandateNotFoundError as exc:
        raise _not_found() from exc
    return _response(mandate_id, decisions)


@router.post("/mandates/{mandate_id}/simulate", response_model=DecisionBatchResponse)
async def simulate(mandate_id: UUID, service: DealWatch) -> DecisionBatchResponse:
    try:
        decisions = await service.evaluate(mandate_id, demo_market_events())
    except MandateNotFoundError as exc:
        raise _not_found() from exc
    return _response(mandate_id, decisions)


@router.get("/mandates/{mandate_id}/decisions", response_model=DecisionBatchResponse)
async def get_decisions(mandate_id: UUID, service: DealWatch) -> DecisionBatchResponse:
    try:
        decisions = await service.history(mandate_id)
    except MandateNotFoundError as exc:
        raise _not_found() from exc
    return _response(mandate_id, decisions)

