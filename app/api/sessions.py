import asyncio
from decimal import Decimal
from typing import Annotated, Any
from uuid import UUID

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, status
from pydantic import BaseModel, Field

from app.api.dependencies import (
    ApplicationServices,
    get_current_user,
    get_optional_user,
    get_services,
)
from app.auth.models import AuthenticatedUser
from app.conversation.service import infer_direct_product_search
from app.domain.models import ConversationStage, Requirements, RunStatus, SearchDirection

router = APIRouter(prefix="/sessions", tags=["sessions"])
Services = Annotated[ApplicationServices, Depends(get_services)]
OptionalUser = Annotated[AuthenticatedUser | None, Depends(get_optional_user)]
CurrentUser = Annotated[AuthenticatedUser, Depends(get_current_user)]


class MessageRequest(BaseModel):
    message: str = Field(min_length=1, max_length=2000)


class SelectProductRequest(BaseModel):
    direction: SearchDirection = SearchDirection.BEST_VALUE


@router.post("", status_code=status.HTTP_201_CREATED)
async def create_session(services: Services, user: OptionalUser) -> dict[str, Any]:
    session_id = await services.sessions.create(user.id if user else None)
    return {"session_id": str(session_id), "stage": ConversationStage.DISCOVERY.value}


@router.get("/history")
async def list_history(services: Services, user: CurrentUser) -> dict[str, Any]:
    sessions = await services.sessions.list_for_user(user.id)
    return {"sessions": sessions}


@router.get("/{session_id}/history")
async def get_history(
    session_id: UUID,
    services: Services,
    user: CurrentUser,
) -> dict[str, Any]:
    session = await services.sessions.get(session_id)
    _assert_session_access(session, user, require_owner=True)
    messages = (
        await services.messages.list_for_session(session_id) if services.messages else []
    )
    return {"session": session, "messages": messages}


@router.post("/{session_id}/messages")
async def add_message(
    session_id: UUID,
    payload: MessageRequest,
    background_tasks: BackgroundTasks,
    services: Services,
    user: OptionalUser,
) -> dict[str, Any]:
    session = await services.sessions.get(session_id)
    _assert_session_access(session, user)
    if services.messages and session.get("user_id"):
        await services.messages.add(session_id, "user", payload.message)
    current = Requirements.model_validate(session.get("requirements") or {})
    direct_search = infer_direct_product_search(payload.message)
    if direct_search is not None:
        product = direct_search.product
        updates: dict[str, Any] = {"reference_product": product}
        if direct_search.budget_max is not None:
            updates["budget_max"] = direct_search.budget_max
        requirements = current.model_copy(update=updates)
        product_payload = {
            "category": requirements.category,
            "brand": product.brand,
            "model": product.model,
            "canonical_name": f"{product.brand} {product.model}",
            "specifications": {
                "exact_variant": product.model,
                "confidence": product.confidence,
                "data_gaps": [],
            },
        }
        product_id = await services.products.upsert(product_payload)
        query = {
            "requirements": requirements.model_dump(mode="json"),
            "direction": requirements.search_direction.value,
            "sources_requested": services.orchestrator.source_names,
            "direct_search": True,
        }
        run_id = await services.runs.create(session_id, product_id, query)
        await services.sessions.update(
            session_id,
            {
                "stage": ConversationStage.SEARCHING.value,
                "requirements": requirements.model_dump(mode="json"),
                "selected_product_id": str(product_id),
                "message_summary": session.get("message_summary") or payload.message,
            },
        )
        background_tasks.add_task(
            services.orchestrator.run,
            run_id,
            session_id,
            product_id,
            product_payload,
            requirements,
        )
        response = {
            "session_id": str(session_id),
            "stage": ConversationStage.SEARCHING.value,
            "run_id": str(run_id),
            "status": RunStatus.PENDING.value,
            "candidates": [],
            "is_final_ranking": True,
            "direct_search": True,
        }
        await _save_assistant_message(
            services,
            session_id,
            f"Szukam konkretnych ofert dla {product.brand} {product.model}.",
            session,
        )
        return response
    result = await services.conversation.handle_message(payload.message, current)
    selected_product_id = session.get("selected_product_id")
    if selected_product_id and result.change_intent.value == "rerank" and not result.question:
        product_id = UUID(str(selected_product_id))
        product = await services.products.get(product_id)
        if product is None:
            raise HTTPException(status_code=404, detail={"code": "product_not_found"})
        query = {
            "requirements": result.requirements.model_dump(mode="json"),
            "direction": result.requirements.search_direction.value,
            "sources_requested": [],
            "cache_only": True,
        }
        run_id = await services.runs.create(session_id, product_id, query)
        changes = {
            "stage": ConversationStage.SEARCHING.value,
            "requirements": result.requirements.model_dump(mode="json"),
        }
        if not session.get("message_summary"):
            changes["message_summary"] = payload.message
        await services.sessions.update(session_id, changes)
        background_tasks.add_task(
            services.orchestrator.run,
            run_id,
            session_id,
            product_id,
            product,
            result.requirements,
            False,
        )
        response = {
            "session_id": str(session_id),
            "stage": ConversationStage.SEARCHING.value,
            "run_id": str(run_id),
            "status": RunStatus.PENDING.value,
            "candidates": [],
            "is_final_ranking": True,
        }
        await _save_assistant_message(services, session_id, "Aktualizuję ranking ofert.", session)
        return response
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
                "specifications": {
                    "key_features": suggestion.key_features,
                    "exact_variant": suggestion.exact_variant or suggestion.model,
                    "source_url": str(suggestion.source_url) if suggestion.source_url else None,
                    "confidence": suggestion.confidence,
                    "data_gaps": suggestion.data_gaps,
                },
            }
        )
        candidate = suggestion.model_dump(mode="json")
        candidate["product_id"] = str(product_id)
        candidate["estimated_price"] = suggestion.estimated_price
        candidates.append(candidate)
    if not result.question:
        candidates = await _with_market_prices(
            services, candidates, result.requirements.budget_max
        )
    changes = {
        "stage": stage.value,
        "requirements": result.requirements.model_dump(mode="json"),
    }
    if not session.get("message_summary"):
        changes["message_summary"] = payload.message
    await services.sessions.update(session_id, changes)
    response = {
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
    assistant_text = result.question or f"Mam {len(candidates)} dopasowane propozycje."
    await _save_assistant_message(services, session_id, assistant_text, session)
    return response


@router.post("/{session_id}/products/{product_id}/select", status_code=status.HTTP_202_ACCEPTED)
async def select_product(
    session_id: UUID,
    product_id: UUID,
    payload: SelectProductRequest,
    background_tasks: BackgroundTasks,
    services: Services,
    user: OptionalUser,
) -> dict[str, Any]:
    session = await services.sessions.get(session_id)
    product = await services.products.get(product_id)
    _assert_session_access(session, user)
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


MARKET_PROBE_TIMEOUT_SECONDS = 12
MIN_CANDIDATES = 4


async def _with_market_prices(
    services: ApplicationServices,
    candidates: list[dict[str, Any]],
    budget_max: Decimal | None,
) -> list[dict[str, Any]]:
    """Ground LLM suggestions in real second-hand prices before showing them.

    Each candidate gets a quick OLX probe; its estimated price becomes the
    observed median. Candidates whose cheapest real offer exceeds the budget
    are dropped, unless that would leave fewer than the UI's minimum of 4.
    """
    probe = services.market_probe
    if probe is None or not candidates:
        return candidates

    async def probe_one(candidate: dict[str, Any]) -> list[Decimal] | None:
        try:
            return await asyncio.wait_for(
                probe.probe_used_prices(f"{candidate['brand']} {candidate['model']}"),
                timeout=MARKET_PROBE_TIMEOUT_SECONDS,
            )
        except Exception:
            return None

    results = await asyncio.gather(*(probe_one(candidate) for candidate in candidates))
    enriched: list[dict[str, Any]] = []
    for candidate, prices in zip(candidates, results, strict=True):
        if prices:
            ordered = sorted(prices)
            candidate = {
                **candidate,
                "estimated_price": int(ordered[len(ordered) // 2]),
                "market_price_from": int(ordered[0]),
                "market_offer_count": len(ordered),
            }
        enriched.append(candidate)
    if budget_max is not None:
        affordable = [
            candidate
            for candidate in enriched
            if Decimal(candidate["estimated_price"]) <= budget_max
        ]
        if len(affordable) >= MIN_CANDIDATES:
            return affordable
        over_budget = sorted(
            (candidate for candidate in enriched if candidate not in affordable),
            key=lambda candidate: candidate["estimated_price"],
        )
        return affordable + over_budget[: MIN_CANDIDATES - len(affordable)]
    return enriched


def _assert_session_access(
    session: dict[str, Any] | None,
    user: AuthenticatedUser | None,
    *,
    require_owner: bool = False,
) -> None:
    if session is None:
        raise HTTPException(status_code=404, detail={"code": "session_not_found"})
    owner_id = session.get("user_id")
    if require_owner and owner_id is None:
        raise HTTPException(status_code=404, detail={"code": "session_not_found"})
    if owner_id is not None and (user is None or str(user.id) != str(owner_id)):
        raise HTTPException(status_code=404, detail={"code": "session_not_found"})


async def _save_assistant_message(
    services: ApplicationServices,
    session_id: UUID,
    content: str,
    session: dict[str, Any],
) -> None:
    if services.messages and session.get("user_id") and content:
        await services.messages.add(session_id, "assistant", content)
