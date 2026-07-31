---
schema_version: 1
open_count: 1
waived_count: 0
fixed_count: 0
total_count: 1
last_updated: 2026-07-31T03:09:45.682Z
---

# Broken Windows Ledger

> Cross-phase defect register. `/gsd-ship` blocks while `open_count > 0`.
> Waive with `gsd-tools windows waive <id> "<reason>"` (reason required).
> Mark fixed with `gsd-tools windows fixed <id>`.

| id | phase | kind | file | line | description | status | reason | recorded_at | resolved_at |
|----|-------|------|------|------|-------------|--------|--------|-------------|-------------|
| 1 | 02 | unmet-truth | mcp-server/app/server.py |  | POST /mcp with invalid Bearer returns 500 not 401 — fix before Hermes auth error handling | open |  | 2026-07-31T03:09:45.682Z |  |

````json
[
  {
    "id": 1,
    "kind": "unmet-truth",
    "phase": "02",
    "file": "mcp-server/app/server.py",
    "line": null,
    "description": "POST /mcp with invalid Bearer returns 500 not 401 — fix before Hermes auth error handling",
    "status": "open",
    "reason": "",
    "recorded_at": "2026-07-31T03:09:45.682Z",
    "resolved_at": null
  }
]
````
