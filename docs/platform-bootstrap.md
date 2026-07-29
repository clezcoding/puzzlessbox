# Platform Bootstrap

Baseline CI/CD and infrastructure for `clezcoding/puzzlessbox` using free tools only.

## Kodiak GitHub App

Kodiak auto-merges Dependabot PRs that pass CI. Config lives at `.kodiak.toml` (repo root, per [Kodiak docs](https://kodiakhq.com/docs/config)).

**Pricing (verified 2026-07-29):** Per [Kodiak billing](https://kodiakhq.com/docs/billing), Kodiak is **free for personal use and public repositories**. A paid subscription ($4.99/active user/month) is required only for **private GitHub Organization** repositories — not for personal-account private repos like `clezcoding/puzzlessbox`.

1. Install the Kodiak GitHub App: https://kodiakhq.com/install
2. Grant access to `clezcoding/puzzlessbox`
3. Without the app install, `.kodiak.toml` has no effect

Kodiak auto-approves PRs from `dependabot` (username, not `dependabot[bot]`).

## Labels

Dependabot applies the `dependencies` label (configured in `.github/dependabot.yml`). Create it once:

```bash
gh label create dependencies --color 0E8A16 --description "Dependency updates (Dependabot)"
```

## Branch Protection

Requires `gh` CLI authenticated with repo admin scope.

```bash
bash scripts/github-setup-branch-protection.sh
```

> **GitHub Free + private repo:** Classic branch protection and rulesets return **403** — [protected branches require GitHub Pro](https://docs.github.com/en/get-started/learning-about-github/githubs-products#github-pro) for personal private repositories. **Cannot be enabled via API or script on the current plan.** Upgrade to GitHub Pro (~$4/mo) or enforce PR discipline manually until then.

When Pro is available, enforced status checks (must match workflow job names):

| Check | Workflow | Job |
|-------|----------|-----|
| `test` | `.github/workflows/ci.yml` | `test` |
| `actionlint` | `.github/workflows/ci.yml` | `actionlint` |
| `analyze` | `.github/workflows/codeql.yml` | `analyze` |

> **CodeQL on GitHub Free private:** Code scanning SARIF upload requires enabling Code Scanning in repo settings (typically **GitHub Pro** or Advanced Security). The workflow runs analysis with `continue-on-error` on upload until upgraded.

Also enforced (when Pro available): PR required, no force push, no branch deletion, admins included.

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
- **Internal only:** `is_public: false` (no public port)
- **DB name / user:** `puzzlessbox` (credentials managed by Coolify — not in git)

### Connection pattern

App services reference the database via Coolify internal network env vars injected at deploy time (e.g. `DATABASE_URL`). Do not commit connection strings; retrieve from Coolify dashboard or `coolify database get <uuid> -s` locally.

### Provision commands (reproducibility)

```bash
coolify --context hostunlimited project create \
  --name "Puzzlessbox" \
  --description "Capture inbox - Hermes + WebApp"

coolify --context hostunlimited database create postgresql \
  --server-uuid ozwpdpj5bgxax8v6gfs5lolv \
  --project-uuid nlm9h0u5lh2rnf2fg10vuf16 \
  --environment-name production \
  --name puzzlessbox-db \
  --image postgres:18-alpine \
  --postgres-db puzzlessbox \
  --postgres-user puzzlessbox \
  --instant-deploy
```

## Secrets Policy

- No secrets, passwords, or connection strings in git
- Coolify API token via `COOLIFY_TOKEN` env var (Coolify Profile → API Tokens)
- Kodiak authenticates via GitHub App install — no token in repo
- Database credentials injected by Coolify at deploy time via internal network env vars (e.g. `DATABASE_URL`)
