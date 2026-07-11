from datetime import datetime
from decimal import Decimal
from typing import Any
from uuid import UUID

from app.domain.models import Currency, ListingCondition, NormalizedListing, Requirements


def _execute(query: Any) -> list[dict[str, Any]]:
    result = query.execute()
    return list(result.data or [])


class SupabaseListingRepository:
    """Supabase adapter; all database details stay behind ListingRepository."""

    def __init__(self, client: Any) -> None:
        self._client = client

    async def upsert_many(
        self, product_id: UUID, listings: list[NormalizedListing], observed_at: datetime
    ) -> list[NormalizedListing]:
        saved: list[NormalizedListing] = []
        for listing in listings:
            payload = {
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
                "attributes": listing.attributes,
                "image_urls": [str(url) for url in listing.image_urls],
                "raw_payload": listing.raw_payload,
                "last_seen_at": observed_at.isoformat(),
                "active": listing.active,
            }
            rows = _execute(
                self._client.table("listings").upsert(payload, on_conflict="source,external_id")
            )
            if not rows:
                continue
            row = rows[0]
            _execute(
                self._client.table("listing_snapshots").upsert(
                    {
                        "listing_id": row["id"],
                        "price": str(listing.price),
                        "active": listing.active,
                        "observed_at": observed_at.isoformat(),
                    },
                    on_conflict="listing_id,observed_at",
                )
            )
            saved.append(_listing_from_row(row))
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
        rows = _execute(query.order("last_seen_at", desc=True))
        listings = [_listing_from_row(row) for row in rows]
        if requirements.required_variants:
            wanted = {item.casefold() for item in requirements.required_variants}
            listings = [item for item in listings if wanted <= _listing_terms(item)]
        return listings


def _listing_terms(listing: NormalizedListing) -> set[str]:
    values = [listing.title, listing.description or "", *map(str, listing.attributes.values())]
    return {token.casefold() for value in values for token in value.replace(",", " ").split()}


def _listing_from_row(row: dict[str, Any]) -> NormalizedListing:
    return NormalizedListing(
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
        attributes=row.get("attributes") or {},
        image_urls=row.get("image_urls") or [],
        raw_payload=row.get("raw_payload") or {},
        first_seen_at=row.get("first_seen_at"),
        last_seen_at=row.get("last_seen_at"),
        active=row.get("active", True),
    )
