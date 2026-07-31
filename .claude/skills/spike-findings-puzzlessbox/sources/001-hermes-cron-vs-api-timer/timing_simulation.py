#!/usr/bin/env python3
"""Simulate Hermes 60s cron vs 30s confirmation deadline (MCP-04 spike)."""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path

CRON_TICK_SECONDS = 60
CONFIRMATION_DEADLINE_SECONDS = 30
SIMULATION_SECONDS = 120


@dataclass
class Event:
    ts: float
    source: str
    kind: str
    detail: str


def simulate() -> list[Event]:
    events: list[Event] = []
    api_autosave_at = CONFIRMATION_DEADLINE_SECONDS
    cron_ticks = list(range(0, SIMULATION_SECONDS + 1, CRON_TICK_SECONDS))

    events.append(
        Event(0, "user", "message", "Capture draft created; API timer starts")
    )
    events.append(
        Event(
            api_autosave_at,
            "api",
            "auto_saved",
            f"DraftTimeoutManager fires at T+{api_autosave_at}s (exact)",
        )
    )

    for tick in cron_ticks:
        if tick == 0:
            continue
        if tick < api_autosave_at:
            events.append(
                Event(
                    tick,
                    "hermes_cron",
                    "tick_skipped",
                    f"Cron tick T+{tick}s — too late to meet 30s deadline",
                )
            )
        elif tick == api_autosave_at:
            events.append(
                Event(
                    tick,
                    "hermes_cron",
                    "missed_deadline",
                    "First cron tick at 60s — 30s already passed",
                )
            )
        else:
            events.append(
                Event(tick, "hermes_cron", "tick", f"Scheduler tick T+{tick}s")
            )

    return events


def main() -> None:
    events = simulate()
    earliest_cron_action = min(
        (e.ts for e in events if e.source == "hermes_cron"), default=None
    )
    verdict = {
        "api_timer_meets_30s": True,
        "hermes_cron_meets_30s": False,
        "earliest_hermes_cron_tick": earliest_cron_action,
        "gap_seconds": (earliest_cron_action or 0) - CONFIRMATION_DEADLINE_SECONDS,
        "recommendation": (
            "API DraftTimeoutManager owns the 30s transition. "
            "Hermes cron may only send post-autosave nudges (webhook/poll), "
            "never dispatch_tool as a timer."
        ),
        "phase1_evidence": "api/tests/integration/test_capture.py::test_autosave (DRAFT_TIMEOUT_SECONDS=1)",
    }
    out = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "events": [asdict(e) for e in events],
        "verdict": verdict,
    }
    path = Path(__file__).with_name("events.json")
    path.write_text(json.dumps(out, indent=2))
    print(json.dumps(verdict, indent=2))
    print(f"\nWrote {path}")


if __name__ == "__main__":
    main()
