from datetime import datetime
from decimal import Decimal
from typing import Protocol, TypeVar

from pydantic import BaseModel

ResponseT = TypeVar("ResponseT", bound=BaseModel)


class MarketPriceProbe(Protocol):
    async def probe_used_prices(self, model: str, limit: int = 12) -> list[Decimal]: ...


class LLMClient(Protocol):
    async def structured_response(
        self,
        *,
        system_prompt: str,
        user_prompt: str,
        response_model: type[ResponseT],
    ) -> ResponseT: ...


class Clock(Protocol):
    def now(self) -> datetime: ...
