from datetime import datetime
from typing import Any, Protocol
from uuid import UUID

from app.domain.models import NormalizedListing, Requirements, RunStatus


class ProductRepository(Protocol):
    async def get(self, product_id: UUID) -> dict[str, Any] | None: ...

    async def upsert(self, product: dict[str, Any]) -> UUID: ...


class ListingRepository(Protocol):
    async def upsert_many(
        self, product_id: UUID, listings: list[NormalizedListing], observed_at: datetime
    ) -> list[NormalizedListing]: ...

    async def find_active(
        self, product_id: UUID, requirements: Requirements, fresh_since: datetime | None = None
    ) -> list[NormalizedListing]: ...


class SessionRepository(Protocol):
    async def create(self, user_id: UUID | None = None) -> UUID: ...

    async def get(self, session_id: UUID) -> dict[str, Any] | None: ...

    async def update(self, session_id: UUID, changes: dict[str, Any]) -> None: ...

    async def list_for_user(self, user_id: UUID) -> list[dict[str, Any]]: ...


class MessageRepository(Protocol):
    async def add(self, session_id: UUID, role: str, content: str) -> UUID: ...

    async def list_for_session(self, session_id: UUID) -> list[dict[str, Any]]: ...


class SearchRunRepository(Protocol):
    async def create(self, session_id: UUID, product_id: UUID, query: dict[str, Any]) -> UUID: ...

    async def set_status(
        self,
        run_id: UUID,
        status: RunStatus,
        *,
        sources_succeeded: list[str] | None = None,
        error_summary: dict[str, str] | None = None,
        new_price_benchmark: dict[str, Any] | None = None,
    ) -> None: ...

    async def get(self, run_id: UUID) -> dict[str, Any] | None: ...


class ProductResearchRepository(Protocol):
    async def get_fresh(self, product_id: UUID, fresh_since: datetime) -> dict[str, Any] | None: ...

    async def save(self, product_id: UUID, research: dict[str, Any]) -> UUID: ...


class RecommendationRepository(Protocol):
    async def replace_for_run(
        self, run_id: UUID, recommendations: list[dict[str, Any]]
    ) -> None: ...

    async def get_for_run(self, run_id: UUID) -> list[dict[str, Any]]: ...
