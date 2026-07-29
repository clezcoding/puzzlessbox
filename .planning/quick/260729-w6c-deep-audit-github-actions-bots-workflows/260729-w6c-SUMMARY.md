---
phase: quick
plan: 260729-w6c
status: complete
completed: 2026-07-29
---

# Quick 260729-w6c: GitHub Platform Audit

Deep audit + hardening for Free-tier private repo (no workarounds).

## User decisions

- GitHub Free — only features that work properly without hacks
- Full platform scope: CI + repo settings + labels + templates + docs
- Kodiak installed

## Changes (local, uncommitted)

### Workflows

- **ci.yml:** Node 24, concurrency, path filters, explicit test glob
- **codeql.yml:** `upload: false` (replaces `continue-on-error`), schedule, path filters, dropped security-events write perm

### GitHub metadata

- PR template, bug + feature issue templates
- Labels: ci, infra, security, phase-0..5 (applied via API)
- Repo settings: deleteBranchOnMerge, squash-only merge

### Docs / scripts

- `docs/platform-bootstrap.md` — honest Free-tier matrix
- `scripts/github-setup-labels.sh` — idempotent label bootstrap
- `scripts/github-setup-branch-protection.sh` — Pro requirement noted

## Still unavailable on Free private (documented, not faked)

- Branch protection / required status checks
- Code Scanning SARIF UI
- Secret scanning push protection

## Renovate migration (post-audit)

- Replaced Dependabot with Mend Renovate (`renovate.json` at repo root)
- Deleted `.github/dependabot.yml`
- Kodiak usernames switched `dependabot` → `renovate` (minor/patch automerge unchanged)
- Install Renovate: https://github.com/apps/renovate

## Deferred to Phase 5

- GHCR deploy workflows (OPS-02)
- Renovate npm/pip managers when lockfiles exist
- Reusable docker-build workflow

## Research

See `260729-w6c-RESEARCH.md` for full audit findings.
