#!/usr/bin/env python3
"""Verify run polling stays responsive while orchestrator performs blocking Supabase I/O."""

from __future__ import annotations

import asyncio
import sys
import time

import httpx


async def main() -> int:
    base_url = "http://localhost:8000"
    async with httpx.AsyncClient(base_url=base_url, timeout=60.0) as client:
        health = await client.get("/health")
        if health.status_code != 200:
            print(f"Backend unhealthy: {health.status_code}")
            return 1

        session_id = (await client.post("/sessions")).json()["session_id"]
        discovery = (
            await client.post(
                f"/sessions/{session_id}/messages",
                json={"message": "Samsung S21 w dobrym stanie do 2200 zł"},
            )
        ).json()
        candidates = discovery.get("candidates") or []
        if not candidates:
            print("No candidates returned; cannot verify select flow")
            return 1

        product_id = candidates[0]["product_id"]
        run_id = (
            await client.post(
                f"/sessions/{session_id}/products/{product_id}/select",
                json={"direction": "best_value"},
            )
        ).json()["run_id"]

        poll_latencies: list[float] = []
        statuses: list[str] = []
        deadline = time.monotonic() + 50

        while time.monotonic() < deadline:
            started = time.monotonic()
            response = await client.get(f"/runs/{run_id}")
            latency = time.monotonic() - started
            poll_latencies.append(latency)
            if response.status_code != 200:
                print(f"Poll failed: HTTP {response.status_code} {response.text[:200]}")
                return 1
            status = response.json()["status"]
            statuses.append(status)
            if status in {"completed", "partial", "failed"}:
                break
            await asyncio.sleep(1.5)

        print(f"Poll count: {len(poll_latencies)}")
        print(f"Statuses: {statuses}")
        print(f"Max poll latency: {max(poll_latencies):.3f}s")
        print(f"Final status: {statuses[-1]}")

        if len(poll_latencies) < 3:
            print("FAIL: expected at least 3 successful polls during run")
            return 1
        if max(poll_latencies) >= 8.0:
            print("FAIL: poll latency exceeded frontend timeout threshold (8s)")
            return 1
        if statuses[-1] not in {"completed", "partial"}:
            print("FAIL: run did not finish with usable results")
            return 1
        if "running" not in statuses and statuses[0] == statuses[-1]:
            print("WARN: status never transitioned through running")

        print("PASS: polling remained responsive and run completed")
        return 0


if __name__ == "__main__":
    raise SystemExit(asyncio.run(main()))
