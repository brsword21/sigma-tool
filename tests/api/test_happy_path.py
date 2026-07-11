import json
import logging

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


def test_full_fetch_is_logged_only_after_product_selection(
    caplog: pytest.LogCaptureFixture,
) -> None:
    services = build_services()
    app = create_app(Settings(_env_file=None, environment="test"), services=services)
    caplog.set_level(logging.INFO, logger="sigma.shopping_agent")
    with TestClient(app) as client:
        session_id = client.post("/sessions").json()["session_id"]
        discovery = client.post(
            f"/sessions/{session_id}/messages", json={"message": "ANC do 600 zł"}
        ).json()
        assert not caplog.records
        product_id = discovery["candidates"][0]["product_id"]
        client.post(
            f"/sessions/{session_id}/products/{product_id}/select",
            json={"direction": "best_value"},
        )

    events = [json.loads(record.message)["event"] for record in caplog.records]
    assert events.index("search_run_started") < events.index("listing_fetch_started")
    assert "source_finished" in events
    assert events[-1] == "search_run_finished"


def test_follow_up_priority_change_reranks_cache_without_refetch() -> None:
    services = build_services()
    source = services.orchestrator._sources[0]
    app = create_app(Settings(_env_file=None, environment="test"), services=services)
    with TestClient(app) as client:
        session_id = client.post("/sessions").json()["session_id"]
        discovery = client.post(
            f"/sessions/{session_id}/messages",
            json={"message": "coś jak AirPods Pro, ale taniej"},
        ).json()
        product_id = discovery["candidates"][0]["product_id"]
        client.post(
            f"/sessions/{session_id}/products/{product_id}/select",
            json={"direction": "best_value"},
        )
        assert source.calls == 1

        follow_up = client.post(
            f"/sessions/{session_id}/messages",
            json={"message": "ważniejsza jest gwarancja"},
        ).json()
        reranked = client.get(f"/runs/{follow_up['run_id']}").json()

    assert source.calls == 1
    assert reranked["status"] == "completed"
    assert len(reranked["recommendations"]) == 3
    session = services.sessions.rows[next(iter(services.sessions.rows))]
    assert session["selected_product_id"] == product_id
