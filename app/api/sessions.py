from typing import Annotated, Any
from uuid import UUID

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, status
from pydantic import BaseModel, Field

from app.api.dependencies import ApplicationServices, get_services
from app.domain.models import ConversationStage, Requirements, RunStatus, SearchDirection

router = APIRouter(prefix="/sessions", tags=["sessions"])
Services = Annotated[ApplicationServices, Depends(get_services)]


class MessageRequest(BaseModel):
    message: str = Field(min_length=1, max_length=2000)


class SelectProductRequest(BaseModel):
    direction: SearchDirection = SearchDirection.BEST_VALUE


@router.post("", status_code=status.HTTP_201_CREATED)
async def create_session(services: Services) -> dict[str, Any]:
    session_id = await services.sessions.create()
    return {"session_id": str(session_id), "stage": ConversationStage.DISCOVERY.value}


@router.post("/{session_id}/messages")
async def add_message(
    session_id: UUID, payload: MessageRequest, services: Services
) -> dict[str, Any]:
    session = await services.sessions.get(session_id)
    if session is None:
        raise HTTPException(status_code=404, detail={"code": "session_not_found"})
    current = Requirements.model_validate(session.get("requirements") or {})
    result = await services.conversation.handle_message(payload.message, current)
    stage = (
        ConversationStage.DISCOVERY
        if result.question
        else ConversationStage.PRODUCT_SELECTION
    )
    candidates: list[dict[str, Any]] = []
    for suggestion in result.suggestions:
        product_id = await services.products.upsert(
            {
                "category": result.requirements.category,
                "brand": suggestion.brand,
                "model": suggestion.model,
                "canonical_name": f"{suggestion.brand} {suggestion.model}",
                "specifications": {"key_features": suggestion.key_features},
            }
        )
        candidate = suggestion.model_dump(mode="json")
        candidate["product_id"] = str(product_id)
        candidate["estimated_price"] = suggestion.estimated_price
        candidates.append(candidate)
    await services.sessions.update(
        session_id,
        {
            "stage": stage.value,
            "requirements": result.requirements.model_dump(mode="json"),
            "message_summary": payload.message,
        },
    )
    return {
        "session_id": str(session_id),
        "stage": stage.value,
        "question": result.question,
        "reference_product": (
            result.reference_product.model_dump(mode="json")
            if result.reference_product
            else None
        ),
        "candidates": candidates,
        "is_final_ranking": False,
    }


@router.post("/{session_id}/products/{product_id}/select", status_code=status.HTTP_202_ACCEPTED)
async def select_product(
    session_id: UUID,
    product_id: UUID,
    payload: SelectProductRequest,
    background_tasks: BackgroundTasks,
    services: Services,
) -> dict[str, Any]:
    session = await services.sessions.get(session_id)
    product = await services.products.get(product_id)
    if session is None:
        raise HTTPException(status_code=404, detail={"code": "session_not_found"})
    if product is None:
        raise HTTPException(status_code=404, detail={"code": "product_not_found"})
    requirements = Requirements.model_validate(session.get("requirements") or {}).model_copy(
        update={"search_direction": payload.direction}
    )
    query = {
        "requirements": requirements.model_dump(mode="json"),
        "direction": payload.direction.value,
        "sources_requested": services.orchestrator.source_names,
    }
    run_id = await services.runs.create(session_id, product_id, query)
    await services.sessions.update(
        session_id,
        {
            "stage": ConversationStage.SEARCHING.value,
            "requirements": requirements.model_dump(mode="json"),
            "selected_product_id": str(product_id),
        },
    )
    background_tasks.add_task(
        services.orchestrator.run,
        run_id,
        session_id,
        product_id,
        product,
        requirements,
    )
    return {"run_id": str(run_id), "status": RunStatus.PENDING.value}
