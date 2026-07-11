import pytest
from fastapi.testclient import TestClient

from app.config import Settings
from app.main import create_app
from tests.api.helpers import build_services


@pytest.mark.parametrize(
    "message,expects_reference",
    [
        ("Szukam słuchawek z ANC do 600 zł", False),
        ("coś jak AirPods Pro, ale taniej", True),
    ],
)
def test_both_entry_points_reach_three_ranked_offers(
    message: str, expects_reference: bool
) -> None:
    services = build_services()
    app = create_app(Settings(_env_file=None, environment="test"), services=services)
    with TestClient(app) as client:
        session_id = client.post("/sessions").json()["session_id"]
        discovery = client.post(
            f"/sessions/{session_id}/messages", json={"message": message}
        ).json()
        assert len(discovery["candidates"]) == 4
        assert discovery["is_final_ranking"] is False
        assert (discovery["reference_product"] is not None) is expects_reference
        assert "estimated_price" in discovery["candidates"][0]

        product_id = discovery["candidates"][0]["product_id"]
        selection = client.post(
            f"/sessions/{session_id}/products/{product_id}/select",
            json={"direction": "best_value"},
        )
        assert selection.status_code == 202
        run = client.get(f"/runs/{selection.json()['run_id']}").json()

    assert run["status"] == "completed"
    assert len(run["recommendations"]) == 3
    breakdown = run["recommendations"][0]["score_breakdown"]
    assert {"product_match", "offer_quality", "seller_trust"} <= breakdown.keys()
    listing = run["recommendations"][0]["listings"]
    assert listing["url"].startswith("https://example.com/offers/")
    assert listing["retrieved_at"] == "2026-07-11T12:00:00Z"
    assert "confidence" in listing
    assert "data_gaps" in listing
    assert run["recommendations"][0]["source_url"] == listing["url"]
    assert run["recommendations"][0]["retrieved_at"] == listing["retrieved_at"]


def test_direction_change_updates_session_without_reset() -> None:
    services = build_services()
    app = create_app(Settings(_env_file=None, environment="test"), services=services)
    with TestClient(app) as client:
        session_id = client.post("/sessions").json()["session_id"]
        discovery = client.post(
            f"/sessions/{session_id}/messages", json={"message": "ANC do 600 zł"}
        ).json()
        product_id = discovery["candidates"][0]["product_id"]
        client.post(
            f"/sessions/{session_id}/products/{product_id}/select",
            json={"direction": "lowest_price"},
        )

    session = services.sessions.rows[next(iter(services.sessions.rows))]
    assert session["requirements"]["search_direction"] == "lowest_price"
    assert session["selected_product_id"] == product_id
