from datetime import timedelta
from typing import Annotated, Any
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException

from app.api.dependencies import ApplicationServices, get_services

router = APIRouter(prefix="/products", tags=["products"])
Services = Annotated[ApplicationServices, Depends(get_services)]


@router.get("/{product_id}/brief")
async def get_product_brief(product_id: UUID, services: Services) -> dict[str, Any]:
    product = await services.products.get(product_id)
    if product is None:
        raise HTTPException(status_code=404, detail={"code": "product_not_found"})
    brief = await services.product_research.get_fresh(
        product_id, services.clock.now() - timedelta(days=30)
    )
    if brief is None:
        raise HTTPException(status_code=404, detail={"code": "brief_not_found"})
    return brief
