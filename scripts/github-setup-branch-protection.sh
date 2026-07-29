#!/usr/bin/env bash
# Configure branch protection for clezcoding/puzzlessbox.
# Requires: gh auth login with repo admin scope.
set -euo pipefail

REPO="${REPO:-clezcoding/puzzlessbox}"
BRANCH="${BRANCH:-main}"

# Status check contexts must match CI/CodeQL job names exactly.
# CodeQL job name is "analyze" — verify in GitHub PR checks after first workflow run.
gh api -X PUT "repos/${REPO}/branches/${BRANCH}/protection" \
  --input - <<'EOF'
{
  "required_status_checks": {
    "strict": true,
    "contexts": ["test", "actionlint", "analyze"]
  },
  "enforce_admins": true,
  "required_pull_request_reviews": {
    "required_approving_review_count": 0,
    "dismiss_stale_reviews": true,
    "require_code_owner_reviews": false
  },
  "restrictions": null,
  "allow_force_pushes": false,
  "allow_deletions": false
}
EOF

echo "Branch protection applied to ${REPO}:${BRANCH}"
