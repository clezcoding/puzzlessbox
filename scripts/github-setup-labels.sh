#!/usr/bin/env bash
# Create recommended GitHub labels for clezcoding/puzzlessbox.
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

create_label "dependencies" "0366D6" "Renovate dependency update PRs"
create_label "ci" "1D76DB" "CI/CD and GitHub Actions"
create_label "infra" "FBCA04" "Infrastructure, Coolify, deployment"
create_label "security" "D93F0B" "Security fixes and hardening"
create_label "phase-0" "C5DEF5" "Phase 0: Branding and design tokens"
create_label "phase-1" "BFD4F2" "Phase 1: Datenmodell and Backend API"
create_label "phase-2" "D4C5F9" "Phase 2: MCP server"
create_label "phase-3" "F9D0C4" "Phase 3: Hermes plugin and timeout spike"
create_label "phase-4" "C2E0C6" "Phase 4: WebApp UI"
create_label "phase-5" "E99695" "Phase 5: Coolify deploy and CI/CD hardening"

echo "Done. Labels on ${REPO}"
