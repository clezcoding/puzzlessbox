---
phase: 3
slug: hermes-plugin-timeout-spike
# status lifecycle: draft (seeded by plan-phase) → validated (set by validate-phase §6)
# audit-milestone §5.5 distinguishes NOT-VALIDATED (draft) from PARTIAL (validated + nyquist_compliant: false) (#2117)
status: draft
nyquist_compliant: false
wave_0_complete: false
created: 2026-08-01
---

# Phase 3 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | pytest 8.x |
| **Config file** | `api/tests/conftest.py`, `mcp-server/tests/conftest.py`, Wave 0: `hermes-plugin/tests/` |
| **Quick run command** | `pytest api/tests/unit/ -x` |
| **Full suite command** | `pytest api/tests/ mcp-server/tests/ hermes-plugin/tests/` |
| **Estimated runtime** | ~60 seconds |

---

## Sampling Rate

- **After every task commit:** Run `pytest api/tests/unit/ -x`
- **After every plan wave:** Run `pytest api/tests/ mcp-server/tests/ hermes-plugin/tests/`
- **Before `/gsd-verify-work`:** Full suite must be green
- **Max feedback latency:** 60 seconds

---

## Per-Task Verification Map

| Task ID | Plan | Wave | Requirement | Threat Ref | Secure Behavior | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|------------|-----------------|-----------|-------------------|-------------|--------|
| 03-W0 | 01 | 0 | CAP-02 | — | N/A | unit | `pytest hermes-plugin/tests/test_formatter.py -x` | ❌ W0 | ⬜ pending |
| 03-CAP02 | 01 | 1 | CAP-02 | — | N/A | unit | `pytest hermes-plugin/tests/test_formatter.py -x` | ❌ W0 | ⬜ pending |
| 03-CAP04 | 02 | 1 | CAP-04 | — | N/A | integration | `pytest hermes-plugin/tests/test_channels.py -x` | ❌ W0 | ⬜ pending |
| 03-MCP03 | 02 | 2 | MCP-03 | T-03-01 | Bearer only via env; no DB from VPS | integration | `pytest hermes-plugin/tests/test_orchestration.py -x` | ❌ W0 | ⬜ pending |
| 03-MCP04 | 03 | 1 | MCP-04 | — | N/A | integration | `pytest api/tests/integration/test_capture.py::test_autosave -x` | ✅ | ⬜ pending |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

---

## Wave 0 Requirements

- [ ] `hermes-plugin/tests/test_formatter.py` — stubs for CAP-02 template generation
- [ ] `hermes-plugin/tests/test_orchestration.py` — stubs for MCP-03 tool call chains
- [ ] `hermes-plugin/tests/test_channels.py` — stubs for CAP-04 channel-agnostic flow
- [ ] `hermes-plugin/tests/conftest.py` — shared fixtures / MCP client mocks

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| Live E2E on Hermes VPS with real category_id | MCP-03 / CAP-04 | External VPS + live messaging adapters | Send message via Telegram → confirm card → edit → autosave ping; spike 002 still PARTIAL |

---

## Validation Sign-Off

- [ ] All tasks have `<automated>` verify or Wave 0 dependencies
- [ ] Sampling continuity: no 3 consecutive tasks without automated verify
- [ ] Wave 0 covers all MISSING references
- [ ] No watch-mode flags
- [ ] Feedback latency < 60s
- [ ] `nyquist_compliant: true` set in frontmatter

**Approval:** pending
