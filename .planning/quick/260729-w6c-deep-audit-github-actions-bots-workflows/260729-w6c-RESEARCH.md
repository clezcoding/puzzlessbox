# Quick 260729-w6c: GitHub Platform Audit — Research

**Date:** 2026-07-29  
**Repo:** `clezcoding/puzzlessbox` (private, ADMIN access)  
**Scope:** Actions, bots, CI/CD, labels, PR templates, dependency versions (July 2026)

---

## Current State Inventory

### Workflows (2 active)

| File | Triggers | Jobs | Last run |
|------|----------|------|----------|
| `.github/workflows/ci.yml` | push, pull_request | `test`, `actionlint` | success (2026-07-29) |
| `.github/workflows/codeql.yml` | push, pull_request | `analyze` | success (2026-07-29) |

### Bots / Automation

| Tool | Config | Status |
|------|--------|--------|
| Dependabot | `.github/dependabot.yml` (github-actions only) | Active, 0 open alerts |
| Kodiak | `.kodiak.toml` (repo root) | **App install unverified** |
| CodeQL | workflow | Runs; SARIF upload masked via `continue-on-error` |

### Repo Settings (live API)

| Setting | Value | Assessment |
|---------|-------|------------|
| Private | yes | Branch protection + Code Scanning need Pro |
| deleteBranchOnMerge | **false** | Should be true |
| squashMergeAllowed | true | Aligns with Kodiak |
| mergeCommitAllowed | **true** | Redundant with Kodiak squash-only |
| rebaseMergeAllowed | **true** | Redundant |
| Branch protection | **403** (Free private) | Script exists, not applied |
| Actions permissions | all actions, **no SHA pinning** | Security gap vs 2026 roadmap |
| Secrets | none | Expected pre-Phase-5 |
| PR templates | none | Gap |
| Issue templates | none | Gap |
| Labels | 9 default + `dependencies` | Minimal |

### Dependency Versions

| Area | Current | Target (PROJECT.md / Brief) |
|------|---------|----------------------------|
| CI Node | **20** | **24 LTS** (Krypton, v24.18.1) |
| Node Current | v26.5.0 | Explicitly NOT target (Current until Oct 2026) |
| PostgreSQL (Coolify) | 18-alpine | ✓ |
| Deploy workflows | missing | Phase 5 / OPS-02 |

---

## Findings by Category

### 1. Correctness / Version Drift

**HIGH — Node 20 in CI contradicts project pin**

`ci.yml` uses `node-version: 20`. Brief and PROJECT.md pin **Node 24 LTS**. Tests pass on 20 today but will diverge when Next.js 16 lands (requires >=20.9.0; 24 LTS is the chosen runtime).

**MEDIUM — No path filters**

Every push runs full CI + CodeQL even for `.planning/` or sketch assets. Wastes ~4 min wall time per push.

**LOW — actionlint as separate job**

Two `ubuntu-latest` runners spin up (~30s overhead each). Could merge into one job for cost; keep parallel for wall-clock. Not wrong either way.

### 2. Security

**HIGH — `continue-on-error: true` on CodeQL analyze**

Masks real failures. Acceptable workaround for Free-tier SARIF upload limit, but should be conditional (`if: github.event.repository.visibility == 'public'` or Pro check) not blanket.

**HIGH — Branch protection not enforceable (Free private)**

Documented. Manual discipline only. `required_approving_review_count: 0` in script is intentional for Kodiak but means zero human review on dependency PRs.

**MEDIUM — Actions allow all third-party actions, no SHA pinning**

GitHub 2026 security roadmap pushes workflow-level dependency locking and SHA pinning. Dependabot updates majors via tags today (`@v4`) — acceptable but not hardened.

**MEDIUM — No `pull_request` vs `pull_request_target` audit**

Clean — no `pull_request_target` workflows (good).

**LOW — No SECURITY.md / security policy**

Recommended for private repo preparing dual-license public release.

### 3. Performance / Cost

| Issue | Impact | Fix |
|-------|--------|-----|
| No `concurrency: cancel-in-progress` | Stale runs on rapid pushes | Add group per workflow |
| No path filters | ~4 min on non-code pushes | `paths` / `paths-ignore` |
| CodeQL on every PR | ~3 min | Add `paths` + weekly `schedule` |
| Duplicate checkout in 2 CI jobs | ~20s | Optional: single job |

### 4. Duplication / Architecture

**No harmful duplication today** — bootstrap is intentionally minimal.

**Future risk:** Phase 5 will add 3 Docker build workflows (api, mcp, webapp). Without a **reusable workflow** (`workflow_call`), copy-paste across services is likely.

**Dependabot scope gap:** Only `github-actions`. When `package.json` / `pyproject.toml` appear, need separate ecosystems or Renovate for unified grouping.

### 5. Missing but Sensible (Private Solo Repo)

| Item | Priority | Notes |
|------|----------|-------|
| PR template | High | GSD ship flow + manual PRs |
| Issue templates (bug, feature) | Medium | hasIssuesEnabled=true |
| Labels: `infra`, `ci`, `security`, `phase/*` | Medium | Filter + automation |
| CODEOWNERS | Low (solo) | Useful when public/SaaS |
| `deleteBranchOnMerge: true` | High | One-click repo setting |
| Merge method: squash-only | Medium | Match Kodiak |
| Kodiak app install verification | High | Config inert without it |
| GitHub Pro | Decision | Unlocks protection + Code Scanning |
| Deploy workflow (GHCR + Coolify) | Phase 5 | OPS-02, not bootstrap |

### 6. Kodiak + Dependabot Interaction

Config is **correct per Kodiak docs**:
- `.kodiak.toml` at repo root ✓
- `auto_approve_usernames = ["dependabot"]` ✓
- minor/patch automerge for dependabot ✓
- `update.always = true` keeps PRs current ✓

**Open question:** Is Kodiak GitHub App installed? No PRs merged via Kodiak yet (no dependabot PRs observed).

### 7. CI/CD Roadmap Alignment

Bootstrap (260729-vmg) scope was intentionally **no GHCR, no deploy webhooks**. That matches Phase 0 state.

Phase 5 (OPS-02) requires:
- Matrix or reusable workflow for api/mcp/webapp
- GHCR push (`:latest` + `:sha-<short>`)
- Coolify webhook trigger (secrets)
- Deploy only on `main` merge (not PR)
- OIDC or `GITHUB_TOKEN` with `packages: write`

**Recommendation:** Extend CI now; add CD in Phase 5 as separate workflow file(s), not bolted onto `ci.yml`.

---

## Recommended Target Architecture (July 2026)

```
.github/
  dependabot.yml          # github-actions now; +npm +pip when apps exist
  kodiak.toml             # unchanged
  CODEOWNERS              # optional until contributors
  PULL_REQUEST_TEMPLATE.md
  ISSUE_TEMPLATE/
    bug_report.yml
    feature_request.yml
  workflows/
    ci.yml                # test + lint, path-filtered, concurrency, Node 24
    codeql.yml            # path-filtered + weekly schedule
    deploy.yml            # Phase 5: reusable caller or matrix (main only)
    reusable/
      docker-build.yml    # Phase 5: workflow_call
```

---

## Version Pin Reference (July 2026)

| Component | Stable choice | Notes |
|-----------|---------------|-------|
| Node.js | 24 LTS (24.18.x) | Active LTS "Krypton" |
| Python | 3.14.x | Per brief |
| PostgreSQL | 18.x | Coolify already on 18-alpine |
| actions/checkout | v4 (pin SHA via Dependabot) | Current |
| actions/setup-node | v4, `node-version: 24` | Fix from 20 |
| github/codeql-action | v3 | Current |
| rhysd/actionlint | v1.7.7 | Pinned ✓ |

---

## Open Decisions for User

1. **GitHub Pro (~$4/mo)?** Unlocks branch protection + Code Scanning on private repo.
2. **Kodiak installed?** Verify at https://kodiakhq.com/install
3. **Implement audit fixes now vs Phase 5 bundle?** CI hardening can be now; deploy waits for apps.
4. **Renovate vs Dependabot** when monorepo grows? Dependabot sufficient for solo + Kodiak today.
5. **Label taxonomy** — minimal (5 custom) vs full GSD phase labels?

---

## Sources

- Live repo API (2026-07-29)
- `.planning/PROJECT.md`, `PUZZLESSBOX_PROJECT_BRIEF.md`, OPS-02
- Quick task 260729-vmg SUMMARY
- nodejs.org/dist/index.json — Node 24.18.1 LTS Krypton
- GitHub Actions 2026 security roadmap (github.blog)
