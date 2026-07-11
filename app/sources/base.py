from typing import Protocol

from app.domain.models import RawListing, SearchQuery


class ListingSource(Protocol):
    source_name: str

    async def search(self, query: SearchQuery) -> list[RawListing]: ...

    async def get_details(self, external_id: str) -> RawListing | None: ...
