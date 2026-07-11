from fastapi.testclient import TestClient

from app.config import Settings
from app.main import create_app
from tests.api.helpers import build_services


def test_source_failure_keeps_cached_recommendations_and_marks_run_partial() -> None:
    services = build_services(source_fails=True)
    app = create_app(Settings(_env_file=None, environment="test"), services=services)
    with TestClient(app) as client:
        session_id = client.post("/sessions").json()["session_id"]
        discovery = client.post(
            f"/sessions/{session_id}/messages",
            json={"message": "coś jak AirPods Pro, ale taniej"},
        ).json()
        product_id = discovery["candidates"][0]["product_id"]
        run_id = client.post(
            f"/sessions/{session_id}/products/{product_id}/select",
            json={"direction": "best_value"},
        ).json()["run_id"]
        run = client.get(f"/runs/{run_id}").json()

    assert run["status"] == "partial"
    assert "fixture_source" in run["error_summary"]
    assert len(run["recommendations"]) == 3
    assert run["recommendations"][0]["listings"]["source"] == "cache"
