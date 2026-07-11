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
    data_gaps = breakdown.get("data_gaps") or listing.get("data_gaps") or attributes.get(
        "data_gaps", []
    )
    seller_signals = listing.get("seller_signals") or attributes.get("seller_signals") or {}
    return {
        **recommendation,
        "source_url": listing.get("url"),
        "retrieved_at": listing.get("retrieved_at") or listing.get("last_seen_at"),
        "confidence": breakdown.get(
            "confidence", listing.get("confidence", attributes.get("confidence", 0.5))
        ),
        "data_gaps": data_gaps,
        "is_stale": "stale_cache" in data_gaps,
        "field_availability": {
            "seller_reviews": seller_signals.get("seller_reviews", "unknown"),
            "seller_rating": seller_signals.get("seller_rating", "unknown"),
            "warranty": listing.get("warranty") or attributes.get("warranty") or "unknown",
            "returns": listing.get("returns") or attributes.get("returns") or "unknown",
            "authenticity": attributes.get("authenticity", "unknown"),
            "battery": attributes.get("battery")
            or attributes.get("battery_health")
            or "unknown",
        },
    }
