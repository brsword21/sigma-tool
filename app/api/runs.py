from typing import Annotated, Any
from uuid import UUID

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, status

from app.api.dependencies import ApplicationServices, get_services
from app.domain.models import Requirements, RunStatus

router = APIRouter(prefix="/runs", tags=["runs"])
Services = Annotated[ApplicationServices, Depends(get_services)]


@router.get("/{run_id}")
async def get_run(run_id: UUID, services: Services) -> dict[str, Any]:
    run = await services.runs.get(run_id)
    if run is None:
        raise HTTPException(status_code=404, detail={"code": "run_not_found"})
    recommendations = await services.recommendations.get_for_run(run_id)
    return {
        **run,
        "id": str(run_id),
        "recommendations": [_present_recommendation(item) for item in recommendations],
    }


@router.post("/{run_id}/refresh", status_code=status.HTTP_202_ACCEPTED)
async def refresh_run(
    run_id: UUID,
    background_tasks: BackgroundTasks,
    services: Services,
) -> dict[str, Any]:
    run = await services.runs.get(run_id)
    if run is None:
        raise HTTPException(status_code=404, detail={"code": "run_not_found"})
    product_id = UUID(str(run["product_id"]))
    session_id = UUID(str(run["session_id"]))
    product = await services.products.get(product_id)
    if product is None:
        raise HTTPException(status_code=404, detail={"code": "product_not_found"})
    requirements = Requirements.model_validate((run.get("query") or {}).get("requirements") or {})
    await services.runs.set_status(run_id, RunStatus.PENDING)
    background_tasks.add_task(
        services.orchestrator.run,
        run_id,
        session_id,
        product_id,
        product,
        requirements,
    )
    return {"run_id": str(run_id), "status": RunStatus.PENDING.value}


def _present_recommendation(recommendation: dict[str, Any]) -> dict[str, Any]:
    listing = recommendation.get("listings") or recommendation.get("listing") or {}
    attributes = listing.get("attributes") or {}
    breakdown = recommendation.get("score_breakdown") or {}
    return {
        **recommendation,
        "source_url": listing.get("url"),
        "retrieved_at": listing.get("retrieved_at") or listing.get("last_seen_at"),
        "confidence": listing.get("confidence", attributes.get("confidence", 0.5)),
        "data_gaps": listing.get(
            "data_gaps", attributes.get("data_gaps", breakdown.get("data_gaps", []))
        ),
    }
