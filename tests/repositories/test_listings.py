from datetime import UTC, datetime
from decimal import Decimal
from uuid import uuid4

from app.domain.models import NormalizedListing
from app.repositories.supabase import SupabaseListingRepository


class Result:
    def __init__(self, data: list[dict[str, object]]) -> None:
        self.data = data


class Query:
    def __init__(self, db: "FakeClient", table: str) -> None:
        self.db, self.table = db, table
        self.payload = None

    def upsert(self, payload: dict[str, object], **kwargs: object) -> "Query":
        self.payload = payload
        return self

    def execute(self) -> Result:
        if self.table == "listing_snapshots":
            return Result([self.payload or {}])
        key = (str(self.payload["source"]), str(self.payload["external_id"]))
        existing = self.db.rows.get(
            key, {"id": str(uuid4()), "first_seen_at": self.payload["last_seen_at"]}
        )
        existing.update(self.payload or {})
        self.db.rows[key] = existing
        return Result([existing])


class FakeClient:
    def __init__(self) -> None:
        self.rows: dict[tuple[str, str], dict[str, object]] = {}

    def table(self, name: str) -> Query:
        return Query(self, name)


async def test_repeated_source_external_id_is_idempotent() -> None:
    client = FakeClient()
    repository = SupabaseListingRepository(client)
    product_id = uuid4()
    item = NormalizedListing(
        source="olx",
        external_id="same",
        url="https://example.com/1",
        title="Sony",
        price=Decimal("400"),
    )
    await repository.upsert_many(product_id, [item], datetime(2026, 7, 11, tzinfo=UTC))
    await repository.upsert_many(product_id, [item], datetime(2026, 7, 12, tzinfo=UTC))
    assert len(client.rows) == 1
    assert next(iter(client.rows.values()))["last_seen_at"] == "2026-07-12T00:00:00+00:00"
