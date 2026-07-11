from uuid import uuid4

from fastapi.testclient import TestClient

from app.auth.models import AuthenticatedUser
from app.config import Settings
from app.main import create_app
from tests.api.helpers import build_services


def test_missing_authorization_keeps_guest_mode() -> None:
    app = create_app(Settings(_env_file=None, environment="test"), services=build_services())

    with TestClient(app) as client:
        response = client.post("/sessions")

    assert response.status_code == 201


def test_valid_bearer_token_assigns_session_owner() -> None:
    user = AuthenticatedUser(id=uuid4(), email="ania@example.com")
    services = build_services(users_by_token={"valid-token": user})
    app = create_app(Settings(_env_file=None, environment="test"), services=services)

    with TestClient(app) as client:
        response = client.post(
            "/sessions", headers={"Authorization": "Bearer valid-token"}
        )

    assert response.status_code == 201
    session = next(iter(services.sessions.rows.values()))
    assert session["user_id"] == str(user.id)


def test_malformed_authorization_is_rejected() -> None:
    app = create_app(Settings(_env_file=None, environment="test"), services=build_services())

    with TestClient(app) as client:
        response = client.post("/sessions", headers={"Authorization": "Token nope"})

    assert response.status_code == 401
    assert response.json()["detail"]["code"] == "invalid_authorization"


def test_invalid_bearer_token_is_rejected() -> None:
    app = create_app(Settings(_env_file=None, environment="test"), services=build_services())

    with TestClient(app) as client:
        response = client.post("/sessions", headers={"Authorization": "Bearer expired"})

    assert response.status_code == 401
    assert response.json()["detail"]["code"] == "invalid_access_token"
