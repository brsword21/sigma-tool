from typing import Any, Protocol
from uuid import UUID

from anyio import to_thread

from app.auth.models import AuthenticatedUser


class AuthVerifier(Protocol):
    async def verify(self, access_token: str) -> AuthenticatedUser | None: ...


class SupabaseAuthVerifier:
    def __init__(self, client: Any) -> None:
        self._client = client

    async def verify(self, access_token: str) -> AuthenticatedUser | None:
        try:
            response = await to_thread.run_sync(self._client.auth.get_user, access_token)
            user = getattr(response, "user", None)
            if user is None:
                return None
            user_id = getattr(user, "id", None)
            if not user_id:
                return None
            return AuthenticatedUser(
                id=UUID(str(user_id)),
                email=getattr(user, "email", None),
            )
        except Exception:
            return None
