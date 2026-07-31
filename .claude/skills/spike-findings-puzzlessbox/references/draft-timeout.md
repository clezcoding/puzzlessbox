# Draft Timeout (30s Auto-Save)

## Requirements

- 30s auto-save precision **MUST** live in FastAPI `DraftTimeoutManager`, not Hermes cron (MCP-04).
- Optional Hermes cron **MAY** notify user after API `auto_saved` — never drive the timer itself.
- Hermes plugin calls `create_item` → API starts timer; confirm cancels it via existing API endpoints.

## How to Build It

1. **Do not add Hermes `dispatch_tool` or cron jobs for the 30s deadline.** Hermes scheduler ticks every 60s — first actionable tick is too late (spike simulation: gap = 30s).

2. **Rely on Phase 1 `DraftTimeoutManager`** (`api/app/services/timeout.py`):
   - `POST /drafts` (via MCP `create_item`) calls `schedule_timeout(draft_id, owner_id, type)`.
   - `confirm` / `PATCH` on draft cancels or resets timer per existing capture router logic.
   - Env `DRAFT_TIMEOUT_SECONDS` for tests (default `30.0`).

3. **Hermes plugin responsibility after `create_item`:**
   - Show CAP-02 confirmation card (see `capture-confirmation-ux.md`).
   - On user confirm → `confirm_item` MCP tool.
   - On user edit → `update_item` then re-show card.
   - On silence → **do nothing**; API autosaves at 30s.
   - Optional: poll `GET /board-items` or API webhook (future) to send „Eintrag gesichert“ after `auto_saved`.

4. **Verify timing** before shipping Phase 3:
   ```bash
   python3 .planning/spikes/001-hermes-cron-vs-api-timer/timing_simulation.py
   cd api && DRAFT_TIMEOUT_SECONDS=1 pytest tests/integration/test_capture.py::test_autosave -q
   ```

## What to Avoid

- **Hermes cron as timer** — INVALIDATED (60s resolution, chaotic early/late saves per PITFALLS.md).
- **In-memory timer on Hermes VPS** — connection drops lose state; API already owns state machine.
- **Hybrid where cron writes `auto_saved`** — API is sole authority on status transitions.

## Constraints

- `DraftTimeoutManager` is in-process asyncio — acceptable for v1 (Phase 1 decision D-05).
- Hermes cannot guarantee sub-minute scheduling natively.

## Origin

Synthesized from spikes: 001  
Source files: `sources/001-hermes-cron-vs-api-timer/`
