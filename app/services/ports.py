from datetime import datetime
from typing import Protocol, TypeVar

from pydantic import BaseModel

ResponseT = TypeVar("ResponseT", bound=BaseModel)


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
