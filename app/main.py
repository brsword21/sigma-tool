from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import logging

from app.api import (
    deal_watch_router,
    health_router,
    products_router,
    runs_router,
    sessions_router,
)
from app.api.dependencies import ApplicationServices
from app.bootstrap import build_application_services
from app.config import Settings, get_settings
from app.deal_watch.repository import InMemoryDealWatchRepository
from app.deal_watch.service import DealWatchService


def _configure_observability_logging() -> None:
    logger = logging.getLogger("picky.shopping_agent")
    if any(isinstance(handler, logging.StreamHandler) for handler in logger.handlers):
        return
    handler = logging.StreamHandler()
    handler.setFormatter(logging.Formatter("%(message)s"))
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)


def create_app(
    settings: Settings | None = None, *, services: ApplicationServices | None = None
) -> FastAPI:
    _configure_observability_logging()
    resolved_settings = settings or get_settings()
    resolved_services = services
    if resolved_services is None and resolved_settings.external_services_configured:
        resolved_services = build_application_services(resolved_settings)
    app = FastAPI(title=resolved_settings.app_name, version="0.1.0")
    app.state.settings = resolved_settings
    app.state.services = resolved_services
    app.state.deal_watch = DealWatchService(InMemoryDealWatchRepository())
    app.add_middleware(
        CORSMiddleware,
        allow_origins=resolved_settings.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(health_router)
    app.include_router(deal_watch_router)
    app.include_router(sessions_router)
    app.include_router(runs_router)
    app.include_router(products_router)

    return app


app = create_app()
