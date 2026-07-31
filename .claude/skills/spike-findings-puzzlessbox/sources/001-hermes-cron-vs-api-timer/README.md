---
spike: 001
name: hermes-cron-vs-api-timer
type: standard
validates: "Given 30s confirmation window, when user is idle, then API autosaves — Hermes 60s cron cannot substitute"
verdict: VALIDATED
related: [002, 003]
tags: [hermes, timeout, mcp-04, cap-03]
---

# Spike 001: Hermes Cron vs API 30s Timer

## What This Validates

**Given** a capture draft with 30s confirmation window (CAP-03),  
**When** the user does not confirm,  
**Then** the API must transition `draft` → `auto_saved` at ~30s — and Hermes native cron (60s tick) cannot be the timer.

## Research

| Approach | Tool | Pros | Cons | Status |
|----------|------|------|------|--------|
| Hermes cron / dispatch_tool | Hermes scheduler | Simple if it worked | 60s tick; PITFALLS.md reports chaotic timing | **INVALIDATED** |
| API asyncio timer | `DraftTimeoutManager` | Sub-second precision; cancel on confirm | In-process (Phase 1 accepted) | **VALIDATED** |
| Hybrid expires_at + cron poll | API column + Hermes | Decoupled | Still needs API authority on transition | Deferred notify-only |

**Chosen approach:** API-only timer (Phase 1 D-05). Hermes optional nudge after `auto_saved`.

Sources: `.planning/research/PITFALLS.md` Pitfall 1, `api/app/services/timeout.py`, `01-02-SUMMARY.md`.

## How to Run

```bash
python3 .planning/spikes/001-hermes-cron-vs-api-timer/timing_simulation.py
```

Phase 1 ground truth (requires Postgres):

```bash
cd api && DRAFT_TIMEOUT_SECONDS=1 pytest tests/integration/test_capture.py::test_autosave -q
```

## What to Expect

- Simulation prints `hermes_cron_meets_30s: false`, `api_timer_meets_30s: true`.
- `events.json` shows API autosave at T+30s and first Hermes cron tick at T+60s.
- Integration test proves real autosave with compressed timeout.

## Investigation Trail

1. Read PITFALLS + Phase 1 research — cron 60s documented.
2. Ran simulation — 30s gap before first cron tick.
3. Cross-checked `test_autosave` — API timer validated in CI with Postgres service.

## Results

**Verdict: VALIDATED** (split):

| Component | Verdict | Evidence |
|-----------|---------|----------|
| API 30s timer | ✓ VALIDATED | `test_autosave`, `DraftTimeoutManager` |
| Hermes cron as timer | ✗ INVALIDATED | 60s tick simulation + PITFALLS HIGH |
| Hermes cron as post-save notifier | ⚠ PARTIAL | Not built; contract documented in MANIFEST requirements |

**Impact:** Phase 3 plugin must call `create_item` then rely on API for timeout; use webhooks/poll only to inform user after `auto_saved`.
