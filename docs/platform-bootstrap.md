# Platform Bootstrap

Baseline CI/CD and infrastructure for **public** repo `clezcoding/puzzlessbox`.

## GitHub Free (public personal repo)

Public repos unlock branch protection + secret scanning on Free.

| Feature | Status |
|---------|--------|
| GitHub Actions CI | `ci.yml` (always-on for required checks) |
| CodeQL | **Default setup** (actions, javascript-typescript, python) — no custom workflow |
| Renovate | `renovate.json` — labels `dependencies` + `automerge` (non-major) |
| Dependabot | `.github/dependabot.yml` — same labels |
| Kodiak auto-merge | `.kodiak.toml` + [app install](https://kodiakhq.com/install) |
| Branch protection | `scripts/github-setup-branch-protection.sh` |
| Secret scanning + push protection | Enabled via repo settings API |
| GHCR + deploy | `deploy-mcp.yml` (Phase 2); Phase 5 expands |

**Repo merge settings (applied via `gh`):**

- `delete_branch_on_merge: true`
- `allow_auto_merge: true` (needed for Kodiak)
- Squash only (`allow_squash_merge: true`, merge/rebase off)
- Linear history required

## Kodiak

Config: `.kodiak.toml` ([reference](https://kodiakhq.com/docs/config-reference)).

**Requires branch protection** on the target branch — without it Kodiak stays NEUTRAL.

| Mechanism | Behavior |
|-----------|----------|
| Label `automerge` | Merge when checks + 1 approval pass |
| `merge.automerge_dependencies` | Auto-merge Renovate/Dependabot **minor/patch** (title-parsed) without label |
| pinDigest / major | Need explicit `automerge` label (Renovate adds for pin/digest) |
| Labels `wip` / `do-not-merge` | Block merge |
| `[approve]` | Auto-approve PRs from `renovate` / `dependabot` |

```bash
bash scripts/github-setup-labels.sh
bash scripts/github-setup-branch-protection.sh
bash scripts/github-setup-repo-settings.sh
```

## Labels

| Label | Purpose |
|-------|---------|
| `automerge` | Kodiak merge gate |
| `wip` / `do-not-merge` | Kodiak blocking |
| `kodiak: merge.method = '…'` | Per-PR method override |
| `dependencies` | Bot PRs |
| `ci` / `infra` / `security` | Triage |
| `phase-0` … `phase-5` | GSD phase tracking |

## Branch protection (`main`)

Required status checks (job / CodeQL default names):

| Check | Source |
|-------|--------|
| `test` | CI — brand node tests |
| `actionlint` | CI |
| `api-test` | CI — api + camoufox-sidecar SSRF |
| `mcp-test` | CI |
| `webapp-build` | CI |
| `Analyze (actions)` | CodeQL default setup |
| `Analyze (javascript-typescript)` | CodeQL default setup |
| `Analyze (python)` | CodeQL default setup |

Also: PR required, 1 approving review (Kodiak satisfies for bots), dismiss stale, no force-push, no deletions, conversation resolution, linear history, `enforce_admins`.

## CI Workflow (`ci.yml`)

- Runs on **all** PRs and pushes to `main` (no path filters — required checks must not skip)
- Node 24 LTS, Python 3.14
- Postgres service pinned by digest
- Concurrency: cancel stale runs

Inspired by [actomatic](https://github.com/MuhammadTahaNasir/actomatic) CI/lint split — deploy templates (Vercel/Railway/Heroku) intentionally **not** copied; Coolify + GHCR is the stack.

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
| Application | puzzlessbox-api | `dxoflgio67786lc4yilhce43` |
| Application | puzzlessbox-mcp | `n5frtiupale5c2zjm9fyk1qc` |

- **Image:** `postgres:18-alpine`
- **Internal only:** `is_public: false`
- App services get `DATABASE_URL` via Coolify — never commit connection strings.

## Secrets Policy

- No secrets in git
- `COOLIFY_TOKEN` via env
- Kodiak via GitHub App — no token in repo
- Deploy secrets via `gh secret set`

## Security docs

- `SECURITY.md` — private vulnerability reporting
- `.github/CODEOWNERS` — `@clezcoding`
