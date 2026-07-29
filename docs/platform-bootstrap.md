# Platform Bootstrap

Baseline CI/CD and infrastructure for `clezcoding/puzzlessbox`.

## GitHub Free (private personal repo)

This setup targets **GitHub Free on a personal private repository** — no paid features, no workarounds.

| Feature | Free private | This repo |
|---------|--------------|-----------|
| GitHub Actions CI | Yes | `ci.yml`, `codeql.yml` |
| Renovate (github-actions) | Yes | `renovate.json` |
| Kodiak auto-merge | Yes (personal private) | `.kodiak.toml` + app install |
| Branch protection (required checks) | **No** | Not enforced — upgrade to Pro or stay manual |
| Code Scanning (SARIF UI) | **No** | CodeQL runs with `upload: false` |
| GHCR + deploy workflows | Yes | Phase 5 (OPS-02) |

**Repo settings (recommended, applied via `gh`):**

- `delete_branch_on_merge: true`
- Merge method: **squash only** (matches Kodiak)
- `squash_merge_allowed: true`, `merge_commit_allowed: false`, `rebase_merge_allowed: false`

## Renovate GitHub App

Renovate opens dependency update PRs (github-actions today; extend when lockfiles land). Config at `renovate.json` (repo root).

1. Install: https://github.com/apps/renovate
2. Grant access to `clezcoding/puzzlessbox`
3. Without the app, `renovate.json` has no effect

Renovate does **not** automerge — Kodiak handles squash merge after CI passes.

## Kodiak GitHub App

Kodiak auto-merges Renovate PRs that pass CI. Config at `.kodiak.toml` (repo root).

1. Install: https://kodiakhq.com/install
2. Grant access to `clezcoding/puzzlessbox`
3. Without the app, `.kodiak.toml` has no effect

Kodiak auto-approves PRs from username `renovate` (not `renovate[bot]`).

## Labels

| Label | Purpose |
|-------|---------|
| `dependencies` | Renovate PRs (auto-applied) |
| `ci` | GitHub Actions / workflow changes |
| `infra` | Coolify, deploy, ops |
| `security` | Security fixes and hardening |
| `phase-0` … `phase-5` | GSD phase tracking |

Create missing labels:

```bash
bash scripts/github-setup-labels.sh
```

## Branch Protection

**Requires GitHub Pro** on a personal private repo. The script below will return **403** on Free — that is expected, not a bug.

```bash
bash scripts/github-setup-branch-protection.sh
```

When Pro is available, enforced status checks (job names):

| Check | Workflow | Job |
|-------|----------|-----|
| `test` | `.github/workflows/ci.yml` | `test` |
| `actionlint` | `.github/workflows/ci.yml` | `actionlint` |
| `analyze` | `.github/workflows/codeql.yml` | `analyze` |

Also enforced (Pro): PR required, no force push, no branch deletion, admins included.

## CI Workflows

### `ci.yml`

- **Node 24 LTS** (project pin — not Node 20/26)
- Path filters: `brand/**`, workflow file itself
- Concurrency: cancel stale runs on same branch
- Jobs: `node --test brand/tests/` + `actionlint`

### `codeql.yml`

- JavaScript/TypeScript analysis (brand tests today; extend when apps land)
- `upload: false` — analysis only, no SARIF upload (Pro feature on private)
- Weekly schedule: Monday 06:00 UTC
- Same path filters as CI

## Coolify

All commands use context `hostunlimited`:

```bash
/usr/local/bin/coolify --context hostunlimited <command>
```

### Resources

| Resource | Name | UUID |
|----------|------|------|
| Server | hostunlimited | `ozwpdpj5bgxax8v6gfs5lolv` |
| Project | Puzzlessbox | `nlm9h0u5lh2rnf2fg10vuf16` |
| Environment | production | `e14kngyecvqrv2dt73iu7eg3` |
| Database | puzzlessbox-db | `pfqgb5pcvgi9oh64bpe3shtn` |

- **Image:** `postgres:18-alpine`
- **Internal only:** `is_public: false`
- **DB name / user:** `puzzlessbox` (credentials in Coolify — not in git)

### Connection pattern

App services get `DATABASE_URL` via Coolify internal network at deploy time. Do not commit connection strings.

## Secrets Policy

- No secrets, passwords, or connection strings in git
- `COOLIFY_TOKEN` via env (Coolify Profile → API Tokens)
- Kodiak via GitHub App install — no token in repo
- Phase 5 deploy secrets: `COOLIFY_WEBHOOK_*` via `gh secret set` (not in git)

## Phase 5 (not yet)

OPS-02 will add separate deploy workflows (not merged into `ci.yml`):

- Docker build → GHCR (`:latest` + `:sha-<short>`)
- Coolify webhook trigger on `main` only
- Reusable workflow recommended for api / mcp / webapp
