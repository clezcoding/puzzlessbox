---
phase: 03-hermes-plugin-timeout-spike
plan: 04
subsystem: infra
tags: [hermes, setup, d-12, cap-04, channel-neutral, pytest, bash]

requires:
  - phase: 03-hermes-plugin-timeout-spike
    provides: handle_user_message + format_confirmation (Plans 02–03)
provides:
  - interactive setup.sh for MCP_URL/MCP_BEARER on Hermes VPS (D-12)
  - deploy README with D-11 git pull/rsync + security notes
  - CAP-04 channel-neutral verification via mock adapters
affects: [04-webapp, 05-coolify]

tech-stack:
  added: []
  patterns:
    - setup.sh read -rs bearer prompt, chmod 600 .env, gitignore guard
    - channel tests share capture_patches contextmanager across mock adapters

key-files:
  created:
    - hermes-plugin/setup.sh
    - hermes-plugin/README.md
    - hermes-plugin/tests/test_channels.py
  modified: []

key-decisions:
  - "setup.sh validates MCP_URL https:// prefix and MCP_BEARER min 20 chars"
  - "Channel mock adapters reuse MockSession — no render logic in plugin tests"

patterns-established:
  - "First-run secrets via setup.sh only — never hardcoded bearer in repo"

requirements-completed: [CAP-04, MCP-03]

coverage:
  - id: D1
    description: "setup.sh schreibt MCP_URL/MCP_BEARER sicher in .env (D-12)"
    requirement: MCP-03
    verification:
      - kind: unit
        ref: "bash -n hermes-plugin/setup.sh && grep read -rs hermes-plugin/setup.sh"
        status: pass
    human_judgment: false
  - id: D2
    description: "Kanalneutrale Plain-Text-Payload über Telegram/WhatsApp/Discord"
    requirement: CAP-04
    verification:
      - kind: unit
        ref: "hermes-plugin/tests/test_channels.py#test_all_channels_identical_payload"
        status: pass
    human_judgment: false
  - id: D3
    description: "Kein Markdown/HTML in Bestätigungs-Reply (CAP-04)"
    requirement: CAP-04
    verification:
      - kind: unit
        ref: "hermes-plugin/tests/test_channels.py#test_all_channels_no_markdown"
        status: pass
    human_judgment: false
  - id: D4
    description: "Identischer silent ACK nach Edit über alle Adapter"
    requirement: CAP-04
    verification:
      - kind: unit
        ref: "hermes-plugin/tests/test_channels.py#test_all_channels_same_edit_ack"
        status: pass
    human_judgment: false
  - id: D5
    description: "Keine kanalspezifischen Tokens in dialog.py/formatters.py"
    requirement: CAP-04
    verification:
      - kind: unit
        ref: "hermes-plugin/tests/test_channels.py#test_channel_specific_buttons_only_in_adapter"
        status: pass
    human_judgment: false
  - id: D6
    description: "README Deploy-Anleitung + Sicherheitshinweise"
    requirement: CAP-04
    verification:
      - kind: other
        ref: "hermes-plugin/README.md Deploy + Sicherheit sections"
        status: pass
    human_judgment: false

duration: 6min
completed: 2026-08-01
status: complete
---

# Phase 03 Plan 04: Setup & Channel Neutrality Summary

**Interaktives setup.sh für MCP-Secrets (D-12) und CAP-04-Nachweis identischer Plain-Text-Payload über drei Mock-Adapter**

## Performance

- **Duration:** 6 min
- **Started:** 2026-08-01T03:18:00Z
- **Completed:** 2026-08-01T03:24:00Z
- **Tasks:** 2
- **Files modified:** 3

## Accomplishments

- `setup.sh`: interaktive MCP_URL/MCP_BEARER-Eingabe, HTTPS-Validierung, `read -rs`, chmod 600, `.gitignore`-Guard
- `README.md`: D-11 Deploy (git pull/rsync), Abhängigkeiten, Sicherheit, Spike-Referenz
- `test_channels.py`: 7 Tests — identische Capture-Payload, Plain-Text-Guard, Edit-ACK, kein Channel-Token in Plugin-Layer

## Task Commits

1. **Task 1: setup.sh + README** - `870c8ac` (feat)
2. **Task 2: channel tests** - `5807485` (test)

**Plan metadata:** `9feb78b` (docs)

## Files Created/Modified

- `hermes-plugin/setup.sh` — First-Run MCP env configuration
- `hermes-plugin/README.md` — Deploy and security documentation
- `hermes-plugin/tests/test_channels.py` — CAP-04 mock-adapter verification

## Decisions Made

- setup.sh enforces https:// prefix and bearer min 20 characters
- Mock adapters are thin MockSession wrappers without channel render logic

## Deviations from Plan

None - plan executed exactly as written.

## Issues Encountered

None.

## User Setup Required

Hermes-VPS operator runs `bash setup.sh` once per deploy environment to set `MCP_URL` and `MCP_BEARER` (see README).

## Next Phase Readiness

- Phase 3 all 4 plans complete — ready for phase verifier and Phase 4 WebApp
- `format_confirmation` Plain-Text contract validated for board UI reference

## Self-Check: PASSED

- hermes-plugin/setup.sh — FOUND
- hermes-plugin/README.md — FOUND
- hermes-plugin/tests/test_channels.py — FOUND
- Commits 870c8ac, 5807485 — FOUND

---
*Phase: 03-hermes-plugin-timeout-spike*
*Completed: 2026-08-01*
