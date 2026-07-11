import json
from time import perf_counter

from fastapi.testclient import TestClient

from app.config import Settings
from app.main import create_app


def run_demo() -> dict[str, object]:
    settings = Settings()
    if not settings.external_services_configured:
        return {"ok": False, "error": "external_services_not_configured"}
    started = perf_counter()
    report: dict[str, object] = {"ok": False, "checks": {}}
    try:
        with TestClient(create_app(settings)) as client:
            session_response = client.post("/sessions")
            session_response.raise_for_status()
            session_id = session_response.json()["session_id"]
            discovery = client.post(
                f"/sessions/{session_id}/messages",
                json={
                    "message": (
                        "Coś jak AirPods Pro, ale taniej: do 500 zł, dobre ANC, do iPhone'a."
                    )
                },
            ).json()
            for answer in ("Budżet to 500 zł.", "Najważniejsze są ANC i wygoda."):
                if discovery.get("candidates"):
                    break
                discovery = client.post(
                    f"/sessions/{session_id}/messages", json={"message": answer}
                ).json()
            candidates = discovery.get("candidates") or []
            report["checks"] = {
                "candidate_count": len(candidates),
                "reference_detected": discovery.get("reference_product") is not None,
            }
            if not candidates:
                raise RuntimeError("conversation_returned_no_candidates")
            product_id = candidates[0]["product_id"]
            selected = client.post(
                f"/sessions/{session_id}/products/{product_id}/select",
                json={"direction": "best_value"},
            )
            selected.raise_for_status()
            run = client.get(f"/runs/{selected.json()['run_id']}").json()
            follow_up = client.post(
                f"/sessions/{session_id}/messages",
                json={"message": "Ważniejsza jest gwarancja niż najniższa cena."},
            ).json()
            reranked = (
                client.get(f"/runs/{follow_up['run_id']}").json()
                if follow_up.get("run_id")
                else {}
            )
            recommendations = run.get("recommendations") or []
            report["checks"].update(
                {
                    "initial_run_status": run.get("status"),
                    "offer_count": len(recommendations),
                    "offers_have_links": all(item.get("source_url") for item in recommendations),
                    "offers_have_variant": all(
                        (item.get("listings") or {}).get("exact_variant")
                        for item in recommendations
                    ),
                    "scores_are_separate": all(
                        {"product_match", "offer_quality", "seller_trust"}
                        <= set(item.get("score_breakdown") or {})
                        for item in recommendations
                    ),
                    "rerank_status": reranked.get("status"),
                    "rerank_offer_count": len(reranked.get("recommendations") or []),
                }
            )
            report["ok"] = (
                4 <= len(candidates) <= 6
                and len(recommendations) >= 3
                and run.get("status") in {"completed", "partial"}
                and reranked.get("status") in {"completed", "partial"}
            )
    except Exception as exc:
        report["error"] = f"{type(exc).__name__}: {exc}"[:300]
    duration = perf_counter() - started
    report["duration_seconds"] = round(duration, 2)
    report["under_three_minutes"] = duration < settings.demo_timeout_seconds
    return report


if __name__ == "__main__":
    print(json.dumps(run_demo(), ensure_ascii=False, indent=2))
