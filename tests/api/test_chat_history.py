from uuid import uuid4

from fastapi.testclient import TestClient

from app.auth.models import AuthenticatedUser
from app.config import Settings
from app.main import create_app
from tests.api.helpers import build_services


def test_authenticated_conversation_is_saved_and_returned() -> None:
    user = AuthenticatedUser(id=uuid4(), email="ania@example.com")
    services = build_services(users_by_token={"user-token": user})
    app = create_app(Settings(_env_file=None, environment="test"), services=services)
    headers = {"Authorization": "Bearer user-token"}

    with TestClient(app) as client:
        session_id = client.post("/sessions", headers=headers).json()["session_id"]
        message = client.post(
            f"/sessions/{session_id}/messages",
            headers=headers,
            json={"message": "Szukam słuchawek z ANC"},
        )
        history = client.get(f"/sessions/{session_id}/history", headers=headers)

    assert message.status_code == 200
    assert history.status_code == 200
    assert [item["role"] for item in history.json()["messages"]] == [
        "user",
        "assistant",
    ]
    assert history.json()["messages"][0]["content"] == "Szukam słuchawek z ANC"


def test_guest_conversation_is_not_added_to_account_history() -> None:
    user = AuthenticatedUser(id=uuid4(), email="ania@example.com")
    services = build_services(users_by_token={"user-token": user})
    app = create_app(Settings(_env_file=None, environment="test"), services=services)

    with TestClient(app) as client:
        guest_session = client.post("/sessions").json()["session_id"]
        client.post(
            f"/sessions/{guest_session}/messages",
            json={"message": "Rozmowa gościa"},
        )
        history = client.get(
            "/sessions/history", headers={"Authorization": "Bearer user-token"}
        )

    assert history.status_code == 200
    assert history.json()["sessions"] == []


def test_other_user_cannot_read_or_continue_owned_session() -> None:
    owner = AuthenticatedUser(id=uuid4(), email="owner@example.com")
    intruder = AuthenticatedUser(id=uuid4(), email="intruder@example.com")
    services = build_services(users_by_token={"owner": owner, "intruder": intruder})
    app = create_app(Settings(_env_file=None, environment="test"), services=services)

    with TestClient(app) as client:
        session_id = client.post(
            "/sessions", headers={"Authorization": "Bearer owner"}
        ).json()["session_id"]
        history = client.get(
            f"/sessions/{session_id}/history",
            headers={"Authorization": "Bearer intruder"},
        )
        message = client.post(
            f"/sessions/{session_id}/messages",
            headers={"Authorization": "Bearer intruder"},
            json={"message": "Próba dostępu"},
        )

    assert history.status_code == 404
    assert message.status_code == 404


def test_history_endpoint_requires_login() -> None:
    app = create_app(Settings(_env_file=None, environment="test"), services=build_services())

    with TestClient(app) as client:
        response = client.get("/sessions/history")

    assert response.status_code == 401
