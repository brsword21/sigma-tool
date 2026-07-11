from datetime import datetime
from typing import Protocol

from app.domain.models import NewPriceBenchmark, RawListing, SearchQuery


class ListingSource(Protocol):
    source_name: str

    async def search(self, query: SearchQuery) -> list[RawListing]: ...

    async def get_details(self, external_id: str) -> RawListing | None: ...


class NewPriceBenchmarkSource(Protocol):
    source_name: str

    async def get_benchmark(
        self, query: SearchQuery, retrieved_at: datetime
    ) -> NewPriceBenchmark | None: ...
