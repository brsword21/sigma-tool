from typing import Any
from uuid import uuid4

from fastapi.testclient import TestClient


def mandate_payload() -> dict[str, Any]:
    return {
        "product_model": "Apple AirPods Pro",
        "exact_variant": "AirPods Pro 2 USB-C",
        "max_landed_cost": "500.00",
        "currency": "PLN",
        "min_condition": "good",
        "min_seller_rating": "4.5",
        "mode": "alert_only",
    }


def event_payload(index: int) -> dict[str, Any]:
    return {
        "event_id": f"custom-{index}",
        "source": "manual_demo",
        "source_url": f"https://example.com/custom/{index}",
        "exact_variant": "AirPods Pro 2 USB-C",
        "condition": "very_good",
        "item_price": "400.00",
        "shipping": "10.00",
        "in_stock": True,
        "seller_rating": "4.8",
    }


def test_complete_simulation_flow_works_without_external_services(client: TestClient) -> None:
    created = client.post("/deal-watch/mandates", json=mandate_payload())
    assert created.status_code == 201
    mandate_id = created.json()["id"]

    simulated = client.post(f"/deal-watch/mandates/{mandate_id}/simulate")
    assert simulated.status_code == 200
    assert simulated.json()["summary"] == {"alert": 1, "hold": 1, "ignore": 4}
    assert len(simulated.json()["decisions"]) == 6

    history = client.get(f"/deal-watch/mandates/{mandate_id}/decisions")
    assert history.status_code == 200
    assert history.json()["decisions"] == simulated.json()["decisions"]


def test_accepts_a_valid_custom_event_batch(client: TestClient) -> None:
    mandate_id = client.post("/deal-watch/mandates", json=mandate_payload()).json()["id"]

    response = client.post(
        f"/deal-watch/mandates/{mandate_id}/events",
        json={"events": [event_payload(1)]},
    )

    assert response.status_code == 200
    assert response.json()["summary"] == {"alert": 1, "hold": 0, "ignore": 0}


def test_unknown_mandate_returns_safe_404(client: TestClient) -> None:
    response = client.post(f"/deal-watch/mandates/{uuid4()}/simulate")

    assert response.status_code == 404
    assert response.json() == {"detail": {"code": "mandate_not_found"}}


def test_rejects_extra_fields_and_oversized_batches(client: TestClient) -> None:
    invalid_mandate = {**mandate_payload(), "payment_token": "must-not-be-accepted"}
    assert client.post("/deal-watch/mandates", json=invalid_mandate).status_code == 422

    mandate_id = client.post("/deal-watch/mandates", json=mandate_payload()).json()["id"]
    response = client.post(
        f"/deal-watch/mandates/{mandate_id}/events",
        json={"events": [event_payload(index) for index in range(11)]},
    )
    assert response.status_code == 422


def test_rejects_empty_and_duplicate_event_batches(client: TestClient) -> None:
    mandate_id = client.post("/deal-watch/mandates", json=mandate_payload()).json()["id"]
    endpoint = f"/deal-watch/mandates/{mandate_id}/events"

    assert client.post(endpoint, json={"events": []}).status_code == 422
    duplicate = event_payload(1)
    assert client.post(endpoint, json={"events": [duplicate, duplicate]}).status_code == 422

