---
phase: quick-260803-4ji
plan: 01
subsystem: auth
tags: [mcp, oauth, www-authenticate, rfc-9728, coolify]

requires: []
provides:
  - MCP_PUBLIC_BASE_URL env drives OwnerResolvingVerifier.base_url for RFC 9728 resource_metadata
affects: [coolify-deployment, mcp-server]

tech-stack:
  added: []
  patterns: [public base URL resolved once in OwnerResolvingVerifier, not per-caller]

key-files:
  created: []
  modified:
    - mcp-server/app/config.py
    - mcp-server/app/auth.py
    - mcp-server/app/factory.py
    - mcp-server/tests/test_auth.py

key-decisions:
  - "Root fix in OwnerResolvingVerifier base_url resolution — factory passes settings.mcp_public_base_url explicitly"
  - "FastMCP TokenVerifier normalizes base_url with trailing slash; functional check uses host substring not exact URL"

patterns-established:
  - "MCP_PUBLIC_BASE_URL for client-visible OAuth metadata; MCP_API_BASE_URL for internal API calls"

requirements-completed: [OPS-01, MCP-02]

coverage:
  - id: D1
    description: "MCP_PUBLIC_BASE_URL wires into OwnerResolvingVerifier.base_url with localhost fallback"
    requirement: MCP-02
    verification:
      - kind: unit
        ref: "mcp-server/.venv/bin/python -c OwnerResolvingVerifier base_url assertions"
        status: pass
    human_judgment: false
  - id: D2
    description: "401 WWW-Authenticate uses prod FQDN when MCP_PUBLIC_BASE_URL set; no localhost leak"
    requirement: MCP-02
    verification:
      - kind: unit
        ref: "cd mcp-server && .venv/bin/python -m pytest tests/test_auth.py -x -q"
        status: pass
    human_judgment: false

duration: 5min
completed: 2026-08-03
status: complete
---

# Quick 260803-4ji: Fix G-05-5 MCP 401 WWW-Authenticate Summary

**MCP_PUBLIC_BASE_URL env drives OAuth resource_metadata host; regression test blocks localhost leak in prod-like config.**

## Performance

- **Duration:** ~5 min
- **Tasks:** 2/2
- **Files modified:** 4

## Accomplishments

- Added `MCP_PUBLIC_BASE_URL` to `Settings` with `mcp_public_base_url` property
- `OwnerResolvingVerifier` resolves `base_url` from settings (localhost fallback when unset)
- `build_mcp_stack` passes `settings.mcp_public_base_url` into verifier
- New test `test_www_authenticate_uses_public_base_url_in_prod_like_config` — 5/5 auth tests pass

## Coolify Operator Action (Required)

Set on **MCP app** in Coolify:

```env
MCP_PUBLIC_BASE_URL=https://mcp.puzzlesstool.online
```

Post-deploy verify:

```bash
curl -i -X POST https://mcp.puzzlesstool.online/mcp
```

Expect `401` with `www-authenticate` containing `mcp.puzzlesstool.online` and **no** `localhost`.

## Deviations from Plan

None — plan executed as written. Note: FastMCP `TokenVerifier.base_url` stores trailing slash (`https://mcp.puzzlesstool.online/`); plan's inline verify used exact string without slash — functional behavior and tests use host substring checks.

## Self-Check: PASSED

- FOUND: mcp-server/app/config.py
- FOUND: mcp-server/app/auth.py
- FOUND: mcp-server/app/factory.py
- FOUND: mcp-server/tests/test_auth.py
- FOUND: commit e5f8871
- FOUND: commit 754c102
