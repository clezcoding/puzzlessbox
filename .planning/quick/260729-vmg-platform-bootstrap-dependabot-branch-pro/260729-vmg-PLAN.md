---
phase: quick
plan: 260729-vmg
type: execute
wave: 1
depends_on: []
files_modified:
  - .github/dependabot.yml
  - .github/kodiak.toml
  - .github/workflows/ci.yml
  - .github/workflows/codeql.yml
  - scripts/github-setup-branch-protection.sh
  - docs/platform-bootstrap.md
autonomous: true
requirements:
  - PLATFORM-01
  - PLATFORM-02
  - PLATFORM-03
must_haves:
  truths:
    - Dependabot opens PRs for github-actions updates on private repo
    - Kodiak auto-merges minor/patch dependabot PRs that pass CI
    - CI runs node --test brand/tests and actionlint on every PR
    - CodeQL scans javascript-typescript on push and PR
    - main branch requires PR, passing CI status checks, no force push
    - Coolify project "Puzzlessbox" exists with internal postgres:18-alpine database
  artifacts:
    - .github/dependabot.yml
    - .github/kodiak.toml
    - .github/workflows/ci.yml
    - .github/workflows/codeql.yml
    - scripts/github-setup-branch-protection.sh
    - docs/platform-bootstrap.md
  key_links:
    - Kodiak GitHub App installed on clezcoding/puzzlessbox (manual user setup)
    - Coolify context hostunlimited + server uuid ozwpdpj5bgxax8v6gfs5lolv
user_setup:
  - service: kodiak
    why: "Auto-merge dependabot PRs"
    dashboard_config:
      - task: "Install Kodiak GitHub App on clezcoding/puzzlessbox"
        location: "https://kodiakhq.com/install"
  - service: coolify
    why: "Host postgres database"
    env_vars:
      - name: COOLIFY_TOKEN
        source: "Coolify Profile -> API Tokens"
---

<objective>
Platform bootstrap for private repo clezcoding/puzzlessbox using free tools only: Dependabot + Kodiak automerge, targeted CI (node test + actionlint), CodeQL, branch protection via gh api, Coolify postgres database.

Purpose: Establish CI/CD and infra baseline without paid tools (no SuperLinter, no GHCR deploy, no webhooks).
Output: 6 files committed atomically across 3 tasks.
</objective>

<execution_context>
@$HOME/.cursor/gsd-core/workflows/execute-plan.md
@$HOME/.cursor/gsd-core/templates/summary.md
</execution_context>

<context>
Repo: clezcoding/puzzlessbox (private)
Branch: main
Coolify context: hostunlimited
Coolify server uuid: ozwpdpj5bgxax8v6gfs5lolv
</context>

<tasks>

<task type="auto">
  <name>Task 1: GitHub config files (dependabot, kodiak, ci, codeql)</name>
  <files>.github/dependabot.yml, .github/kodiak.toml, .github/workflows/ci.yml, .github/workflows/codeql.yml</files>
  <action>
Create four GitHub config files:

1. `.github/dependabot.yml` — version:2, ecosystem `github-actions`, directory `/`, schedule `weekly` (day: monday, time: "06:00", timezone: Europe/Berlin), open-pull-requests-limit:5, labels: ["dependencies"], groups: group actions (update-types: minor, patch).

2. `.github/kodiak.toml` — version:1, auto_approve_usernames: ["dependabot[bot]"] (per D-01), merge.method: squash, merge.require_automerge_checkpoint: true, update.always: true, update.automerge_title: true, automerge.title: "{{{title}}} (automerge)", plan.require_automerge: true. Restrict to dependabot minor/patch via `merge.automerge_label: "dependencies"` and `update.always: true` — Kodiak only triggers on PRs from dependabot[bot] (auto_approve_usernames gate).

3. `.github/workflows/ci.yml` — name: CI, on: [push, pull_request], permissions: contents: read. Jobs:
   - `test` (runs-on: ubuntu-latest): checkout@v4, setup-node@v4 (node-version: 20, cache: npm), run: `node --test brand/tests/` (fail if dir missing — brand/tests exists per repo layout).
   - `actionlint` (runs-on: ubuntu-latest): checkout@v4, run: `docker run --rm -v "$PWD:/repo" rhysd/actionlint:latest -color` (free, no install). Allow continue-on-error: false.

4. `.github/workflows/codeql.yml` — name: CodeQL, on: [push, pull_request], permissions: security-events: write, actions: read, contents: read. Jobs: `analyze` (runs-on: ubuntu-latest), init@v3 with languages: javascript-typescript, checkout@v4, autobuild, perform analysis@v3.

No SuperLinter (repo too small per scope). No GHCR deploy. No webhooks.
  </action>
  <verify>
    <automated>test -f .github/dependabot.yml && test -f .github/kodiak.toml && test -f .github/workflows/ci.yml && test -f .github/workflows/codeql.yml && node -e "require('js-yaml').load(require('fs').readFileSync('.github/dependabot.yml','utf8'))" 2>/dev/null || python3 -c "import yaml; yaml.safe_load(open('.github/dependabot.yml'))"</automated>
  </verify>
  <done>All four files exist, valid YAML, committed atomically.</done>
</task>

<task type="auto">
  <name>Task 2: Branch protection script + Kodiak docs</name>
  <files>scripts/github-setup-branch-protection.sh, docs/platform-bootstrap.md</files>
  <action>
Create `scripts/github-setup-branch-protection.sh` (executable, bash):
- Shebang `#!/usr/bin/env bash`, `set -euo pipefail`.
- Env check: `REPO="${REPO:-clezcoding/puzzlessbox}"`, `BRANCH="${BRANCH:-main}"`.
- Use `gh api -X PUT "repos/$REPO/branches/$BRANCH/protection"` with JSON body:
  - required_status_checks: strict: true, contexts: ["test", "actionlint", "Analyze (javascript-typescript)"] (matches CI + CodeQL job names from Task 1).
  - enforce_admins: true
  - required_pull_request_reviews: required_approving_review_count: 1, dismiss_stale_reviews: true, require_code_owner_reviews: false
  - restrictions: null
  - allow_force_pushes: false
  - allow_deletions: false
- Echo success. Exit non-zero on `gh api` failure.
- Document in script header: requires `gh auth login`, repo admin scope.

Create `docs/platform-bootstrap.md`:
- Section "Kodiak GitHub App" — install at https://kodiakhq.com/install on clezcoding/puzzlessbox (manual user setup, free). Without install, kodiak.toml is inert.
- Section "Branch Protection" — run `bash scripts/github-setup-branch-protection.sh`. Status check names must match CI job names exactly.
- Section "Coolify" — see Task 3.
- Section "Secrets Policy" — no secrets in git. Coolify token via env. Kodiak via app install.
  </action>
  <verify>
    <automated>test -x scripts/github-setup-branch-protection.sh && bash -n scripts/github-setup-branch-protection.sh && test -f docs/platform-bootstrap.md</automated>
  </verify>
  <done>Script executable, bash syntax valid, docs file exists, both committed atomically.</done>
</task>

<task type="auto">
  <name>Task 3: Coolify project + postgres database via MCP</name>
  <files>docs/platform-bootstrap.md</files>
  <action>
Use Coolify MCP tools with `--context hostunlimited` (server uuid `ozwpdpj5bgxax8v6gfs5lolv`):

1. `create_project` with name "Puzzlessbox" (per D-02). Capture returned project uuid.
2. `create_environment` within project, name "production". Capture environment uuid.
3. `create_database` with type `postgresql`, name `puzzlessbox-db`, image `postgres:18-alpine`, public: false (internal only), on server `ozwpdpj5bgxax8v6gfs5lolv`. Capture database uuid + connection string.

Append to `docs/platform-bootstrap.md` section "Coolify":
- Project: Puzzlessbox (uuid)
- Environment: production
- Database: puzzlessbox-db (postgres:18-alpine, internal, server uuid ozwpdpj5bgxax8v6gfs5lolv)
- Connection pattern: app services reference database via Coolily internal network env vars (e.g. `DATABASE_URL` injected at deploy). DO NOT commit connection strings — Coolify injects at runtime.
- Document the `--context hostunlimited` requirement and server uuid for reproducibility.

No app services created (out of scope). No webhooks (out of scope).
  </action>
  <verify>
    <automated>grep -q "Puzzlessbox" docs/platform-bootstrap.md && grep -q "ozwpdpj5bgxax8v6gfs5lolv" docs/platform-bootstrap.md && grep -q "puzzlessbox-db" docs/platform-bootstrap.md</automated>
  </verify>
  <done>Coolify project "Puzzlessbox" + environment "production" + internal postgres:18-alpine database `puzzlessbox-db` exist on server ozwpdpj5bgxax8v6gfs5lolv. Connection pattern documented. Docs committed atomically.</done>
</task>

</tasks>

<verification>
- All 6 files exist and committed atomically (one commit per task).
- CI workflow references real job names that branch protection enforces.
- Coolify database is internal (not public), on correct server.
- No secrets in git.
</verification>

<success_criteria>
- Dependabot config valid for github-actions ecosystem.
- Kodiak config auto-merges dependabot minor/patch PRs after CI passes.
- CI runs node --test brand/tests + actionlint.
- CodeQL analyzes javascript-typescript.
- Branch protection script runnable via `bash scripts/github-setup-branch-protection.sh`.
- Coolify project + database created and documented.
</success_criteria>

<output>
Create `.planning/quick/260729-vmg-platform-bootstrap-dependabot-branch-pro/260729-vmg-SUMMARY.md` when done.
</output>
