#!/usr/bin/env bash
# Create recommended GitHub labels for clezcoding/puzzlessbox (incl. Kodiak).
# Idempotent: skips labels that already exist.
set -euo pipefail

REPO="${REPO:-clezcoding/puzzlessbox}"

create_label() {
  local name="$1"
  local color="$2"
  local description="$3"
  if gh label list --repo "$REPO" --json name --jq ".[].name" | grep -Fxq "$name"; then
    echo "exists: $name"
  else
    gh label create "$name" --repo "$REPO" --color "$color" --description "$description"
    echo "created: $name"
  fi
}

# Project / bots
create_label "dependencies" "0E8A16" "Dependency updates (Renovate/Dependabot)"
create_label "ci" "1D76DB" "CI/CD and GitHub Actions"
create_label "infra" "FBCA04" "Infrastructure, Coolify, deployment"
create_label "security" "D93F0B" "Security fixes and hardening"

# Kodiak (https://kodiakhq.com/docs/config-reference)
create_label "automerge" "35CE17" "Kodiak: merge when checks pass"
create_label "wip" "FBCA04" "Kodiak blocking: work in progress"
create_label "do-not-merge" "B60205" "Kodiak blocking: do not merge"
create_label "kodiak: merge.method = 'squash'" "0E8A16" "Kodiak override: squash merge"
create_label "kodiak: merge.method = 'merge'" "0E8A16" "Kodiak override: merge commit"
create_label "kodiak: merge.method = 'rebase'" "0E8A16" "Kodiak override: rebase merge"

# GSD phases
create_label "phase-0" "C5DEF5" "Phase 0: Branding and design tokens"
create_label "phase-1" "BFD4F2" "Phase 1: Datenmodell and Backend API"
create_label "phase-2" "D4C5F9" "Phase 2: MCP server"
create_label "phase-3" "F9D0C4" "Phase 3: Hermes plugin and timeout spike"
create_label "phase-4" "C2E0C6" "Phase 4: WebApp UI"
create_label "phase-5" "E99695" "Phase 5: Coolify deploy and CI/CD hardening"

echo "Done. Labels on ${REPO}"
