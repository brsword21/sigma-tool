from datetime import UTC, datetime
from decimal import Decimal
from typing import Any
from uuid import UUID

from anyio import to_thread

from app.domain.models import Currency, ListingCondition, NormalizedListing, Requirements, RunStatus


async def _execute(query: Any) -> list[dict[str, Any]]:
    result = await to_thread.run_sync(query.execute)
    return list(result.data or [])


class SupabaseProductRepository:
    def __init__(self, client: Any) -> None:
        self._client = client

    async def get(self, product_id: UUID) -> dict[str, Any] | None:
        rows = await _execute(self._client.table("products").select("*").eq("id", str(product_id)))
        return rows[0] if rows else None

    async def upsert(self, product: dict[str, Any]) -> UUID:
        payload = {
            "category": product.get("category", "electronics"),
            "brand": product["brand"],
            "model": product["model"],
            "canonical_name": product.get("canonical_name")
            or f"{product['brand']} {product['model']}",
            "specifications": product.get("specifications") or {},
        }
        rows = await _execute(
            self._client.table("products").upsert(payload, on_conflict="brand,model")
        )
        if not rows:
            raise RuntimeError("Supabase did not return the upserted product")
        return UUID(str(rows[0]["id"]))


class SupabaseSessionRepository:
    def __init__(self, client: Any) -> None:
        self._client = client

    async def create(self, user_id: UUID | None = None) -> UUID:
        payload = {"user_id": str(user_id)} if user_id else {}
        rows = await _execute(self._client.table("sessions").insert(payload))
        if not rows:
            raise RuntimeError("Supabase did not return the created session")
        return UUID(str(rows[0]["id"]))

    async def get(self, session_id: UUID) -> dict[str, Any] | None:
        rows = await _execute(self._client.table("sessions").select("*").eq("id", str(session_id)))
        return rows[0] if rows else None

    async def update(self, session_id: UUID, changes: dict[str, Any]) -> None:
        payload = {**changes, "updated_at": datetime.now(UTC).isoformat()}
        await _execute(self._client.table("sessions").update(payload).eq("id", str(session_id)))

    async def list_for_user(self, user_id: UUID) -> list[dict[str, Any]]:
        return await _execute(
            self._client.table("sessions")
            .select("*")
            .eq("user_id", str(user_id))
            .order("updated_at", desc=True)
        )


class SupabaseMessageRepository:
    def __init__(self, client: Any) -> None:
        self._client = client

    async def add(self, session_id: UUID, role: str, content: str) -> UUID:
        rows = await _execute(
            self._client.table("messages").insert(
                {"session_id": str(session_id), "role": role, "content": content}
            )
        )
        if not rows:
            raise RuntimeError("Supabase did not return the created message")
        return UUID(str(rows[0]["id"]))

    async def list_for_session(self, session_id: UUID) -> list[dict[str, Any]]:
        return await _execute(
            self._client.table("messages")
            .select("id,session_id,role,content,created_at")
            .eq("session_id", str(session_id))
            .order("created_at")
        )


class SupabaseSearchRunRepository:
    def __init__(self, client: Any) -> None:
        self._client = client

    async def create(self, session_id: UUID, product_id: UUID, query: dict[str, Any]) -> UUID:
        payload = {
            "session_id": str(session_id),
            "product_id": str(product_id),
            "query": query,
            "sources_requested": query.get("sources_requested", []),
            "status": RunStatus.PENDING.value,
        }
        rows = await _execute(self._client.table("search_runs").insert(payload))
        if not rows:
            raise RuntimeError("Supabase did not return the created search run")
        return UUID(str(rows[0]["id"]))

    async def set_status(
        self,
        run_id: UUID,
        status: RunStatus,
        *,
        sources_succeeded: list[str] | None = None,
        error_summary: dict[str, str] | None = None,
        new_price_benchmark: dict[str, Any] | None = None,
    ) -> None:
        now = datetime.now(UTC).isoformat()
        payload: dict[str, Any] = {"status": status.value}
        if status is RunStatus.RUNNING:
            payload["started_at"] = now
        if status in {RunStatus.PARTIAL, RunStatus.COMPLETED, RunStatus.FAILED}:
            payload["finished_at"] = now
        if sources_succeeded is not None:
            payload["sources_succeeded"] = sources_succeeded
        if error_summary is not None:
            payload["error_summary"] = error_summary
        if status in {RunStatus.PARTIAL, RunStatus.COMPLETED, RunStatus.FAILED}:
            payload["new_price_benchmark"] = new_price_benchmark
        await _execute(self._client.table("search_runs").update(payload).eq("id", str(run_id)))

    async def get(self, run_id: UUID) -> dict[str, Any] | None:
        rows = await _execute(self._client.table("search_runs").select("*").eq("id", str(run_id)))
        return rows[0] if rows else None


class SupabaseProductResearchRepository:
    def __init__(self, client: Any) -> None:
        self._client = client

    async def get_fresh(self, product_id: UUID, fresh_since: datetime) -> dict[str, Any] | None:
        rows = await _execute(
            self._client.table("product_research")
            .select("*")
            .eq("product_id", str(product_id))
            .gte("refreshed_at", fresh_since.isoformat())
            .order("refreshed_at", desc=True)
            .limit(1)
        )
        return rows[0] if rows else None

    async def save(self, product_id: UUID, research: dict[str, Any]) -> UUID:
        rows = await _execute(
            self._client.table("product_research").insert(
                {"product_id": str(product_id), **research}
            )
        )
        if not rows:
            raise RuntimeError("Supabase did not return the saved product research")
        return UUID(str(rows[0]["id"]))


class SupabaseRecommendationRepository:
    def __init__(self, client: Any) -> None:
        self._client = client

    async def replace_for_run(
        self, run_id: UUID, recommendations: list[dict[str, Any]]
    ) -> None:
        await _execute(
            self._client.table("recommendations").delete().eq("search_run_id", str(run_id))
        )
        if recommendations:
            await _execute(self._client.table("recommendations").insert(recommendations))

    async def get_for_run(self, run_id: UUID) -> list[dict[str, Any]]:
        return await _execute(
            self._client.table("recommendations")
            .select("*,listings(*)")
            .eq("search_run_id", str(run_id))
            .order("rank")
        )


class SupabaseListingRepository:
    """Supabase adapter; all database details stay behind ListingRepository."""

    def __init__(self, client: Any) -> None:
        self._client = client

    async def upsert_many(
        self, product_id: UUID, listings: list[NormalizedListing], observed_at: datetime
    ) -> list[NormalizedListing]:
        if not listings:
            return []

        payloads = [
            {
                "product_id": str(product_id),
                "source": listing.source,
                "external_id": listing.external_id,
                "url": str(listing.url),
                "title": listing.title,
                "price": str(listing.price),
                "currency": listing.currency.value,
                "condition": listing.condition.value,
                "color": listing.color,
                "location": listing.location,
                "delivery": listing.delivery,
                "description": listing.description,
                "attributes": {
                    **listing.attributes,
                    "exact_variant": listing.exact_variant,
                    "warranty": listing.warranty,
                    "returns": listing.returns,
                    "seller_signals": listing.seller_signals,
                    "confidence": listing.confidence,
                    "data_gaps": listing.data_gaps,
                },
                "image_urls": [str(url) for url in listing.image_urls],
                "raw_payload": listing.raw_payload,
                "last_seen_at": observed_at.isoformat(),
                "active": listing.active,
            }
            for listing in listings
        ]
        rows = await _execute(
            self._client.table("listings").upsert(payloads, on_conflict="source,external_id")
        )
        if not rows:
            return []

        rows_by_external_id = {str(row["external_id"]): row for row in rows}
        snapshot_payloads: list[dict[str, Any]] = []
        saved: list[NormalizedListing] = []
        for listing in listings:
            row = rows_by_external_id.get(listing.external_id)
            if row is None:
                continue
            snapshot_payloads.append(
                {
                    "listing_id": row["id"],
                    "price": str(listing.price),
                    "active": listing.active,
                    "observed_at": observed_at.isoformat(),
                }
            )
            saved.append(_listing_from_row(row))

        if snapshot_payloads:
            await _execute(
                self._client.table("listing_snapshots").upsert(
                    snapshot_payloads,
                    on_conflict="listing_id,observed_at",
                )
            )
        return saved

    async def find_active(
        self, product_id: UUID, requirements: Requirements, fresh_since: datetime | None = None
    ) -> list[NormalizedListing]:
        query = (
            self._client.table("listings")
            .select("*")
            .eq("product_id", str(product_id))
            .eq("active", True)
        )
        if requirements.budget_max is not None:
            query = query.lte("price", str(requirements.budget_max))
        if requirements.delivery_required:
            query = query.eq("delivery", True)
        if requirements.location:
            query = query.ilike("location", f"%{requirements.location}%")
        if fresh_since:
            query = query.gte("last_seen_at", fresh_since.isoformat())
        rows = await _execute(query.order("last_seen_at", desc=True))
        listings = [_listing_from_row(row) for row in rows]
        if requirements.required_variants:
            wanted = {item.casefold() for item in requirements.required_variants}
            listings = [item for item in listings if wanted <= _listing_terms(item)]
        return listings


def _listing_terms(listing: NormalizedListing) -> set[str]:
    values = [listing.title, listing.description or "", *map(str, listing.attributes.values())]
    return {token.casefold() for value in values for token in value.replace(",", " ").split()}


def _listing_from_row(row: dict[str, Any]) -> NormalizedListing:
    attributes = row.get("attributes") or {}
    return NormalizedListing(
        id=row.get("id"),
        product_id=row.get("product_id"),
        source=row["source"],
        external_id=row["external_id"],
        url=row["url"],
        title=row["title"],
        price=Decimal(str(row["price"])),
        currency=Currency(row.get("currency", "PLN")),
        condition=ListingCondition(row.get("condition", "unknown")),
        color=row.get("color"),
        location=row.get("location"),
        delivery=row.get("delivery"),
        description=row.get("description"),
        exact_variant=attributes.get("exact_variant"),
        warranty=attributes.get("warranty"),
        returns=attributes.get("returns"),
        seller_signals=attributes.get("seller_signals") or {},
        attributes=attributes,
        image_urls=row.get("image_urls") or [],
        raw_payload=row.get("raw_payload") or {},
        first_seen_at=row.get("first_seen_at"),
        last_seen_at=row.get("last_seen_at"),
        retrieved_at=row.get("last_seen_at"),
        confidence=attributes.get("confidence", 0.5),
        data_gaps=attributes.get("data_gaps") or [],
        active=row.get("active", True),
    )
