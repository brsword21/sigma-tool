from app.api.deal_watch import router as deal_watch_router
from app.api.health import router as health_router
from app.api.products import router as products_router
from app.api.runs import router as runs_router
from app.api.sessions import router as sessions_router

__all__ = [
    "deal_watch_router",
    "health_router",
    "products_router",
    "runs_router",
    "sessions_router",
]
