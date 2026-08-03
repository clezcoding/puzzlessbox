---
phase: quick-260803-4nq
plan: 01
subsystem: infra
tags: [mcp, pr, ci, coolify, uat, www-authenticate, deploy-mcp]

requires:
  - phase: quick-260803-4ji
    provides: MCP_PUBLIC_BASE_URL code fix + test
provides:
  - G-05-5 shipped to prod via PR #49
  - Live UAT curl verified prod FQDN in WWW-Authenticate
  - 05-UAT.md G-05-5 resolved on main (PR #50)
affects: [05-coolify-deployment-ci-cd-h-rtung]

tech-stack:
  added: []
  patterns: [MCP_PUBLIC_BASE_URL env → OwnerResolvingVerifier.base_url for RFC 9728]

key-files:
  created: []
  modified:
    - .planning/phases/05-coolify-deployment-ci-cd-h-rtung/05-UAT.md

key-decisions:
  - "Squash merge PR #49 after resolving planning-doc conflicts with main"
  - "UAT doc update via PR #50 (main branch protection blocks direct push)"

patterns-established:
  - "G-05-5 only resolved after live curl proves mcp.puzzlesstool.online in WWW-Authenticate"

requirements-completed: [OPS-02, MCP-02]

duration: 10min
completed: 2026-08-03
status: complete
---

# Quick 260803-4nq: G-05-5 PR Ship + UAT Summary

**G-05-5 MCP WWW-Authenticate localhost leak closed in prod — live curl 401 with `mcp.puzzlesstool.online` resource_metadata.**

## Performance

- **Duration:** ~10 min
- **Started:** 2026-08-03T01:22:00Z
- **Completed:** 2026-08-03T01:31:00Z
- **Tasks:** 3/3 (checkpoint auto-approved per user override)
- **Files modified:** 1

## Accomplishments

- PR #49 merged: G-05-5 code fix + UAT gap fixes on main
- deploy-mcp.yml run **30776842021** success (headSha `df4e488`)
- Coolify MCP `n5frtiupale5c2zjm9fyk1qc` **running:healthy**
- Live UAT curl pass — 401, no localhost in WWW-Authenticate
- 05-UAT.md G-05-5 resolved — 16/16 passed, issues 0 (PR #50)

## Evidence

| Item | Value |
|------|-------|
| PR (code) | https://github.com/clezcoding/puzzlessbox/pull/49 |
| PR (UAT doc) | https://github.com/clezcoding/puzzlessbox/pull/50 |
| Merge commit (code) | `df4e488` |
| Merge commit (UAT) | `76f548e` |
| deploy-mcp run | https://github.com/clezcoding/puzzlessbox/actions/runs/30776842021 |
| Coolify MCP status | `running:healthy` (uuid n5frtiupale5c2zjm9fyk1qc) |

### Live curl (G-05-5 acceptance)

```
HTTP/2 401
www-authenticate: Bearer resource_metadata="https://mcp.puzzlesstool.online/.well-known/oauth-protected-resource/mcp"
```

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 3 - Blocking] PR #49 merge conflicts in planning docs**
- **Found during:** Task 2
- **Issue:** `mergeStateStatus=DIRTY` — conflicts in STATE.md and 05-UAT.md vs stale main UAT
- **Fix:** Merged main into branch, kept deep-prod UAT state; commit `e18444b`
- **Commit:** included in squash `df4e488`

**2. [Rule 3 - Blocking] Main branch protection blocked direct UAT doc push**
- **Found during:** Task 3
- **Issue:** `GH013: Changes must be made through a pull request`
- **Fix:** Branch `quick/260803-4nq-uat-g05-5-resolved` → PR #50 → squash merge `76f548e`
- **Commit:** `76f548e`

## Self-Check: PASSED

- FOUND: `.planning/phases/05-coolify-deployment-ci-cd-h-rtung/05-UAT.md` on origin/main (G-05-5 resolved)
- FOUND: merge commit `df4e488`
- FOUND: merge commit `76f548e`
- FOUND: deploy run 30776842021 success
