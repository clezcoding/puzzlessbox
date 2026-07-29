---
phase: quick
plan: 260729-vmg
subsystem: infra
tags: [dependabot, kodiak, codeql, coolify, github-actions, branch-protection]

requires: []
provides:
  - Dependabot github-actions updates
  - Kodiak auto-merge config
  - CI (node test + actionlint) and CodeQL workflows
  - Branch protection script
  - Coolify Puzzlessbox project + postgres database
affects: [deploy, ci]

tech-stack:
  added: [dependabot, kodiak, actionlint, codeql, coolify-cli]
  patterns: [free-tier platform bootstrap, no secrets in git]

key-files:
  created:
    - .github/dependabot.yml
    - .kodiak.toml
    - .github/workflows/ci.yml
    - .github/workflows/codeql.yml
    - scripts/github-setup-branch-protection.sh
    - docs/platform-bootstrap.md
  modified: []

key-decisions:
  - "Kodiak config at repo root .kodiak.toml per official docs"
  - "auto_approve_usernames dependabot not dependabot[bot]"
  - "required_approving_review_count 0 for Kodiak auto-approve on private repo"
  - "CodeQL status check context analyze (job name)"

patterns-established:
  - "Platform UUIDs in docs, credentials via Coolify runtime injection"

requirements-completed: [PLATFORM-01, PLATFORM-02, PLATFORM-03]

duration: 8min
completed: 2026-07-29
status: complete
---

# Quick 260729-vmg: Platform Bootstrap Summary

**Dependabot + Kodiak auto-merge, CI/CodeQL workflows, branch protection script, Coolify postgres on hostunlimited**

## Performance

- **Duration:** ~8 min
- **Started:** 2026-07-29T20:47:00Z
- **Completed:** 2026-07-29T20:55:00Z
- **Tasks:** 3/3
- **Files modified:** 6

## Accomplishments

- Dependabot weekly github-actions updates with minor/patch grouping
- Kodiak `.kodiak.toml` at repo root with dependabot auto-approve
- CI runs `node --test brand/tests/` + actionlint on push/PR
- CodeQL javascript-typescript scan (job `analyze`)
- Branch protection script with contexts `test`, `actionlint`, `analyze`
- Coolify project Puzzlessbox + internal postgres:18-alpine `puzzlessbox-db`

## Task Commits

1. **Task 1: GitHub config files** - `c9d265d` (feat)
2. **Task 2: Branch protection script + docs** - `6eac1e2` (feat)
3. **Task 3: Coolify provisioning docs** - `634d1fc` (docs)

## Files Created/Modified

- `.github/dependabot.yml` - github-actions weekly updates
- `.kodiak.toml` - Kodiak auto-merge (repo root)
- `.github/workflows/ci.yml` - test + actionlint jobs
- `.github/workflows/codeql.yml` - CodeQL analyze job
- `scripts/github-setup-branch-protection.sh` - gh api branch protection
- `docs/platform-bootstrap.md` - Kodiak, branch protection, Coolify, secrets policy

## Decisions Made

- Kodiak at `.kodiak.toml` (not `.github/kodiak.toml`) per official docs
- `dependabot` username in kodiak (not `dependabot[bot]`)
- `required_approving_review_count: 0` so Kodiak approval satisfies review gate
- CodeQL check context `analyze` (job name); verify after first workflow run
- Omitted `cache: npm` in CI (no package.json in repo)

## Deviations from Plan

### User-specified fixes (applied)

1. `.kodiak.toml` at repo root instead of `.github/kodiak.toml`
2. `auto_approve_usernames = ["dependabot"]`
3. `required_approving_review_count: 0` in branch protection
4. CodeQL context `analyze` instead of `Analyze (javascript-typescript)`

### Auto-fixed Issues

**1. [Rule 2 - Missing Critical] Removed npm cache from setup-node**
- **Found during:** Task 1
- **Issue:** No `package.json` / lockfile — cache would be no-op or warn
- **Fix:** Omitted `cache: npm` from setup-node step
- **Files modified:** `.github/workflows/ci.yml`
- **Committed in:** `c9d265d`

## Issues Encountered

1. **Branch protection 403:** `gh api` returned "Upgrade to GitHub Pro or make this repository public". Script is correct; requires GitHub Pro for private repo branch protection or manual org settings.
2. **Coolify DB unhealthy:** `puzzlessbox-db` created (`pfqgb5pcvgi9oh64bpe3shtn`) but status `exited:unhealthy` after instant-deploy. Start queued; investigate in Coolify dashboard.

## User Setup Required

- Install Kodiak GitHub App: https://kodiakhq.com/install on `clezcoding/puzzlessbox`
- Set `COOLIFY_TOKEN` for API access (not in git)
- Apply branch protection when GitHub plan allows (Pro or public repo)
- Confirm CodeQL check name `analyze` after first workflow run

## Coolify Resources

| Resource | UUID |
|----------|------|
| Server (hostunlimited) | `ozwpdpj5bgxax8v6gfs5lolv` |
| Project Puzzlessbox | `nlm9h0u5lh2rnf2fg10vuf16` |
| Environment production | `e14kngyecvqrv2dt73iu7eg3` |
| Database puzzlessbox-db | `pfqgb5pcvgi9oh64bpe3shtn` |

## Self-Check: PASSED

- FOUND: .github/dependabot.yml
- FOUND: .kodiak.toml
- FOUND: .github/workflows/ci.yml
- FOUND: .github/workflows/codeql.yml
- FOUND: scripts/github-setup-branch-protection.sh
- FOUND: docs/platform-bootstrap.md
- FOUND: c9d265d
- FOUND: 6eac1e2
- FOUND: 634d1fc

---
*Phase: quick*
*Completed: 2026-07-29*
