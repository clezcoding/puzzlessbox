---
schema_version: 1
open_count: 0
waived_count: 0
fixed_count: 2
total_count: 2
last_updated: 2026-08-01T04:31:40.082Z
---

# Broken Windows Ledger

> Cross-phase defect register. `/gsd-ship` blocks while `open_count > 0`.
> Waive with `gsd-tools windows waive <id> "<reason>"` (reason required).
> Mark fixed with `gsd-tools windows fixed <id>`.

| id | phase | kind | file | line | description | status | reason | recorded_at | resolved_at |
|----|-------|------|------|------|-------------|--------|--------|-------------|-------------|
| 1 | 02 | unmet-truth | mcp-server/app/server.py |  | POST /mcp with invalid Bearer returns 500 not 401 — fix before Hermes auth error handling | fixed |  | 2026-07-31T03:09:45.682Z | 2026-07-31T03:26:04.769Z |
| 2 | 03 | deviation | hermes-plugin/tools.py |  | streamable_http_client import fix vs spike streamablehttp_client | fixed |  | 2026-08-01T03:12:31.512Z | 2026-08-01T04:31:40.082Z |

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
  }
]
````
