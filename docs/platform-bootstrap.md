# Platform Bootstrap

Baseline CI/CD and infrastructure for `clezcoding/puzzlessbox` using free tools only.

## Kodiak GitHub App

Kodiak auto-merges Dependabot PRs that pass CI. Config lives at `.kodiak.toml` (repo root, per [Kodiak docs](https://kodiakhq.com/docs/config)).

1. Install the Kodiak GitHub App: https://kodiakhq.com/install
2. Grant access to `clezcoding/puzzlessbox`
3. Without the app install, `.kodiak.toml` has no effect

Kodiak auto-approves PRs from `dependabot` (username, not `dependabot[bot]`). Branch protection uses `required_approving_review_count: 0` so Kodiak's approval satisfies the review requirement.

## Branch Protection

Requires `gh` CLI authenticated with repo admin scope.

```bash
bash scripts/github-setup-branch-protection.sh
```

Enforced status checks (must match workflow job names):

| Check | Workflow | Job |
|-------|----------|-----|
| `test` | `.github/workflows/ci.yml` | `test` |
| `actionlint` | `.github/workflows/ci.yml` | `actionlint` |
| `analyze` | `.github/workflows/codeql.yml` | `analyze` |

> **Note:** After the first CodeQL workflow run, confirm the check context name in a PR's "Checks" tab matches `analyze`. GitHub sometimes prefixes with workflow name; update the script's `contexts` array if it differs.

Also enforced: PR required, no force push, no branch deletion, admins included.

## Coolify

See Coolify section below (populated after provisioning).

## Secrets Policy

- No secrets, passwords, or connection strings in git
- Coolify API token via `COOLIFY_TOKEN` env var (Coolify Profile → API Tokens)
- Kodiak authenticates via GitHub App install — no token in repo
- Database credentials injected by Coolify at deploy time via internal network env vars (e.g. `DATABASE_URL`)
