#!/usr/bin/env python3
"""MCP confirm flow orchestration spike (mock + optional live)."""

from __future__ import annotations

import argparse
import asyncio
import json
import os
import sys
import uuid
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[3]
MCP_ROOT = REPO_ROOT / "mcp-server"

TEST_OWNER = "11111111-1111-4111-8111-111111111111"
TEST_CATEGORY = "33333333-3333-4333-8333-333333333333"
TEST_DRAFT = "22222222-2222-4222-8222-222222222222"


@dataclass
class StepResult:
    step: str
    ok: bool
    detail: str
    payload: dict[str, Any] | None = None


def _mock_transport(state: dict[str, Any]):
    import httpx

    def handler(request: httpx.Request) -> httpx.Response:
        entry = {
            "method": request.method,
            "path": request.url.path,
            "json": json.loads(request.content) if request.content else None,
        }
        state["api_calls"].append(entry)
        if request.url.path == "/drafts" and request.method == "POST":
            state["drafts_calls"].append(entry)
            return httpx.Response(201, json={"id": TEST_DRAFT, "status": "draft"})
        if request.url.path.startswith("/drafts/") and request.method == "PATCH":
            return httpx.Response(200, json={"id": TEST_DRAFT, "status": "draft"})
        if request.url.path.endswith("/confirm") and request.method == "POST":
            return httpx.Response(200, json={"id": TEST_DRAFT, "status": "confirmed"})
        return httpx.Response(404)

    return httpx.MockTransport(handler)


async def run_mock() -> list[StepResult]:
    sys.path.insert(0, str(MCP_ROOT))
    from unittest.mock import patch

    from app.factory import build_mcp_stack
    from app.tools.items import confirm_item, create_item, update_item
    from fastmcp.server.auth import AccessToken

    access = AccessToken(
        token="spike",
        client_id=TEST_OWNER,
        scopes=[],
        claims={"owner_id": TEST_OWNER, "sub": TEST_OWNER},
    )

    state: dict[str, Any] = {"api_calls": [], "drafts_calls": []}
    _http_app, _mcp, client = build_mcp_stack(api_transport=_mock_transport(state))
    results: list[StepResult] = []

    try:
        with patch("app.tools.items.get_access_token", return_value=access):
            created = await create_item(
                title="Spike note",
                type="note",
                category_id=TEST_CATEGORY,
                summary="Test",
            )
            results.append(StepResult("create_item", True, "draft created", {"result": created}))

            updated = await update_item(
                item_id=TEST_DRAFT,
                summary="Edited summary",
            )
            results.append(StepResult("update_item", True, "draft patched", {"result": updated}))

            confirmed = await confirm_item(item_id=TEST_DRAFT)
            results.append(StepResult("confirm_item", True, "draft confirmed", {"result": confirmed}))

        paths = [c["path"] for c in state["api_calls"]]
        methods_paths = [(c["method"], c["path"]) for c in state["api_calls"]]
        wiring_ok = (
            state["drafts_calls"]
            and ("POST", f"/drafts/{TEST_DRAFT}/confirm") in methods_paths
            and any(m == "PATCH" and p.startswith("/drafts/") for m, p in methods_paths)
        )
        results.append(
            StepResult(
                "wiring",
                wiring_ok,
                f"api_calls={paths}",
            )
        )
    finally:
        await client.aclose()

    return results


async def run_live() -> list[StepResult]:
    bearer = os.environ.get("MCP_BEARER")
    if not bearer:
        raise SystemExit("MCP_BEARER required for --live")
    try:
        from mcp import ClientSession
        from mcp.client.streamable_http import streamablehttp_client
    except ImportError as exc:
        raise SystemExit("pip install mcp for --live mode") from exc

    url = os.environ.get("MCP_URL", "https://mcp.puzzlesstool.online/mcp")
    headers = {"Authorization": f"Bearer {bearer}"}
    results: list[StepResult] = []

    async with streamablehttp_client(url, headers=headers) as (read, write, _):
        async with ClientSession(read, write) as session:
            await session.initialize()
            tools = await session.list_tools()
            names = {t.name for t in tools.tools}
            if not {"create_item", "confirm_item"}.issubset(names):
                return [StepResult("list_tools", False, f"missing tools: {sorted(names)}")]

            category_id = os.environ.get("MCP_CATEGORY_ID", "")
            if not category_id:
                return [
                    StepResult("create_item", False, "set MCP_CATEGORY_ID for live create"),
                ]

            created = await session.call_tool(
                "create_item",
                {
                    "title": "Spike live note",
                    "type": "note",
                    "category_id": category_id,
                    "summary": "live spike",
                },
            )
            results.append(
                StepResult(
                    "create_item",
                    not created.isError,
                    str(created.content)[:300],
                )
            )
            results.append(
                StepResult(
                    "confirm_item",
                    False,
                    "PARTIAL: complete live confirm in Hermes with draft_id from create response",
                )
            )
    return results


async def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--live", action="store_true", help="Hit production MCP (needs MCP_BEARER)")
    args = parser.parse_args()

    results = await (run_live() if args.live else run_mock())
    verdict = (
        "PARTIAL"
        if args.live
        else ("VALIDATED" if all(r.ok for r in results) else "INVALIDATED")
    )
    out = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "mode": "live" if args.live else "mock",
        "steps": [asdict(r) for r in results],
        "verdict": verdict,
    }
    path = Path(__file__).with_name("events.json")
    path.write_text(json.dumps(out, indent=2))
    print(json.dumps(out, indent=2))


if __name__ == "__main__":
    asyncio.run(main())
