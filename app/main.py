from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api import health_router, products_router, runs_router, sessions_router
from app.api.dependencies import ApplicationServices
from app.bootstrap import build_application_services
from app.config import Settings, get_settings


def create_app(
    settings: Settings | None = None, *, services: ApplicationServices | None = None
) -> FastAPI:
    resolved_settings = settings or get_settings()
    resolved_services = services
    if resolved_services is None and resolved_settings.external_services_configured:
        resolved_services = build_application_services(resolved_settings)
    app = FastAPI(title=resolved_settings.app_name, version="0.1.0")
    app.state.settings = resolved_settings
    app.state.services = resolved_services
    app.add_middleware(
        CORSMiddleware,
        allow_origins=resolved_settings.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(health_router)
    app.include_router(sessions_router)
    app.include_router(runs_router)
    app.include_router(products_router)

    return app


app = create_app()
