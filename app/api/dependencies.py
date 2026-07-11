from dataclasses import dataclass

from fastapi import HTTPException, Request, status

from app.conversation.service import ConversationService
from app.orchestration.search import SearchOrchestrator
from app.repositories.protocols import (
    ProductRepository,
    ProductResearchRepository,
    RecommendationRepository,
    SearchRunRepository,
    SessionRepository,
)
from app.services.ports import Clock


@dataclass(frozen=True)
class ApplicationServices:
    conversation: ConversationService
    sessions: SessionRepository
    products: ProductRepository
    runs: SearchRunRepository
    recommendations: RecommendationRepository
    product_research: ProductResearchRepository
    orchestrator: SearchOrchestrator
    clock: Clock


def get_services(request: Request) -> ApplicationServices:
    services = getattr(request.app.state, "services", None)
    if services is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail={
                "code": "services_not_configured",
                "message": "External services are unavailable",
            },
        )
    return services
