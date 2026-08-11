---
schema_version: 1
open_count: 1
waived_count: 0
fixed_count: 2
total_count: 3
last_updated: 2026-08-09T13:02:43.686Z
---

# Broken Windows Ledger

> Cross-phase defect register. With `workflow.windows_enforce` enabled, `/gsd-ship` blocks while `open_count > 0`.
> Waive with `gsd-tools windows waive <id> "<reason>"` (reason required).
> Mark fixed with `gsd-tools windows fixed <id>`.

| id | phase | kind | file | line | description | status | reason | recorded_at | resolved_at |
|----|-------|------|------|------|-------------|--------|--------|-------------|-------------|
| 1 | 02 | unmet-truth | mcp-server/app/server.py |  | POST /mcp with invalid Bearer returns 500 not 401 — fix before Hermes auth error handling | fixed |  | 2026-07-31T03:09:45.682Z | 2026-07-31T03:26:04.769Z |
| 2 | 03 | deviation | hermes-plugin/tools.py |  | streamable_http_client import fix vs spike streamablehttp_client | fixed |  | 2026-08-01T03:12:31.512Z | 2026-08-01T04:31:40.082Z |
| 3 | 05.4 | deviation | .planning/phases/05.4-address-residual-v1-0-audit-polish-cal-title-only-sync-stale/05.4-02-SUMMARY.md |  | Task 1 commit included pre-staged 05.4 planning artifacts | open |  | 2026-08-09T13:02:43.686Z |  |

````json
[
  {
    "id": 1,
    "kind": "unmet-truth",
    "phase": "02",
    "file": "mcp-server/app/server.py",
    "line": null,
    "description": "POST /mcp with invalid Bearer returns 500 not 401 — fix before Hermes auth error handling",
    "status": "fixed",
    "reason": "",
    "recorded_at": "2026-07-31T03:09:45.682Z",
    "resolved_at": "2026-07-31T03:26:04.769Z"
  },
  {
    "id": 2,
    "kind": "deviation",
    "phase": "03",
    "file": "hermes-plugin/tools.py",
    "line": null,
    "description": "streamable_http_client import fix vs spike streamablehttp_client",
    "status": "fixed",
    "reason": "",
    "recorded_at": "2026-08-01T03:12:31.512Z",
    "resolved_at": "2026-08-01T04:31:40.082Z"
  },
  {
    "id": 3,
    "kind": "deviation",
    "phase": "05.4",
    "file": ".planning/phases/05.4-address-residual-v1-0-audit-polish-cal-title-only-sync-stale/05.4-02-SUMMARY.md",
    "line": null,
    "description": "Task 1 commit included pre-staged 05.4 planning artifacts",
    "status": "open",
    "reason": "",
    "recorded_at": "2026-08-09T13:02:43.686Z",
    "resolved_at": null
  }
]
````
