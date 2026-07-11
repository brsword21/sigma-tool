from dataclasses import dataclass
from typing import Annotated

from fastapi import Depends, HTTPException, Request, status

from app.auth.models import AuthenticatedUser
from app.auth.service import AuthVerifier
from app.conversation.service import ConversationService
from app.orchestration.search import SearchOrchestrator
from app.repositories.protocols import (
    MessageRepository,
    ProductRepository,
    ProductResearchRepository,
    RecommendationRepository,
    SearchRunRepository,
    SessionRepository,
)
from app.services.ports import Clock, MarketPriceProbe


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
    messages: MessageRepository | None = None
    auth: AuthVerifier | None = None
    market_probe: MarketPriceProbe | None = None


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


async def get_optional_user(
    request: Request,
    services: Annotated[ApplicationServices, Depends(get_services)],
) -> AuthenticatedUser | None:
    authorization = request.headers.get("authorization")
    if authorization is None:
        return None
    scheme, separator, token = authorization.partition(" ")
    if not separator or scheme.casefold() != "bearer" or not token.strip():
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"code": "invalid_authorization"},
            headers={"WWW-Authenticate": "Bearer"},
        )
    if services.auth is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail={"code": "authentication_unavailable"},
        )
    user = await services.auth.verify(token.strip())
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"code": "invalid_access_token"},
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user


async def get_current_user(
    user: Annotated[AuthenticatedUser | None, Depends(get_optional_user)],
) -> AuthenticatedUser:
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"code": "authentication_required"},
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user
