#!/usr/bin/env bash
# Apply repo-level GitHub settings for public puzzlessbox (Kodiak + security).
# Requires: gh auth with admin:repo / security_events as needed.
set -euo pipefail

REPO="${REPO:-clezcoding/puzzlessbox}"

echo "==> Merge / PR settings"
gh api -X PATCH "repos/${REPO}" \
  -f allow_auto_merge=true \
  -f allow_squash_merge=true \
  -f allow_merge_commit=false \
  -f allow_rebase_merge=false \
  -f delete_branch_on_merge=true \
  -f squash_merge_commit_title=PR_TITLE \
  -f squash_merge_commit_message=COMMIT_MESSAGES

echo "==> Secret scanning + push protection"
gh api -X PATCH "repos/${REPO}" \
  --input - <<'EOF'
{
  "security_and_analysis": {
    "secret_scanning": { "status": "enabled" },
    "secret_scanning_push_protection": { "status": "enabled" }
  }
}
EOF

echo "==> Vulnerability alerts (Dependabot)"
gh api -X PUT "repos/${REPO}/vulnerability-alerts" || true
gh api -X PUT "repos/${REPO}/automated-security-fixes" || true

echo "Repo settings applied to ${REPO}"
