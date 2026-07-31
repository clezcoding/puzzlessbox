#!/usr/bin/env python3
"""Probe remote MCP from an external client (Hermes VPS analogue)."""

from __future__ import annotations

import json
import os
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

import httpx

DEFAULT_URL = "https://mcp.puzzlesstool.online"


def probe(base_url: str, bearer: str | None) -> dict:
    events: list[dict] = []
    base = base_url.rstrip("/")

    def record(name: str, status: int, elapsed_ms: float, detail: str) -> None:
        events.append(
            {
                "at": datetime.now(timezone.utc).isoformat(),
                "probe": name,
                "status": status,
                "elapsed_ms": round(elapsed_ms, 1),
                "detail": detail,
            }
        )

    with httpx.Client(timeout=15.0) as client:
        t0 = time.perf_counter()
        health = client.get(f"{base}/health")
        record("GET /health", health.status_code, (time.perf_counter() - t0) * 1000, health.text[:80])

        t0 = time.perf_counter()
        no_auth = client.post(f"{base}/mcp", json={})
        record(
            "POST /mcp no auth",
            no_auth.status_code,
            (time.perf_counter() - t0) * 1000,
            no_auth.text[:120],
        )

        t0 = time.perf_counter()
        bad = client.post(
            f"{base}/mcp",
            json={},
            headers={"Authorization": "Bearer invalid-spike-token"},
        )
        record(
            "POST /mcp bad bearer",
            bad.status_code,
            (time.perf_counter() - t0) * 1000,
            bad.text[:120],
        )

        auth_ok = None
        if bearer:
            t0 = time.perf_counter()
            auth = client.post(
                f"{base}/mcp",
                json={},
                headers={"Authorization": f"Bearer {bearer}"},
            )
            auth_ok = auth.status_code
            record(
                "POST /mcp valid bearer",
                auth.status_code,
                (time.perf_counter() - t0) * 1000,
                auth.text[:120],
            )

    verdict = {
        "health_ok": events[0]["status"] == 200,
        "no_auth_is_401": events[1]["status"] == 401,
        "bad_bearer_is_401": events[2]["status"] == 401,
        "valid_bearer_checked": bearer is not None,
        "valid_bearer_status": auth_ok,
        "latency_health_ms": events[0]["elapsed_ms"],
    }
    return {"events": events, "verdict": verdict}


def main() -> None:
    url = os.environ.get("MCP_URL", DEFAULT_URL)
    bearer = os.environ.get("MCP_BEARER")
    result = probe(url, bearer)
    out_path = Path(__file__).with_name("events.json")
    out_path.write_text(json.dumps(result, indent=2))
    print(json.dumps(result["verdict"], indent=2))
    if not bearer:
        print("\nNote: set MCP_BEARER to probe authenticated /mcp (optional).", file=sys.stderr)
    print(f"Wrote {out_path}")


if __name__ == "__main__":
    main()
