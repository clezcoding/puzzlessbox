#!/usr/bin/env bash
# Configure branch protection for clezcoding/puzzlessbox (public Free OK).
# Requires: gh auth login with repo admin scope.
# CodeQL default setup check names: Analyze (actions|javascript-typescript|python)
set -euo pipefail

REPO="${REPO:-clezcoding/puzzlessbox}"
BRANCH="${BRANCH:-main}"

gh api -X PUT "repos/${REPO}/branches/${BRANCH}/protection" \
  --input - <<'EOF'
{
  "required_status_checks": {
    "strict": true,
    "contexts": [
      "test",
      "actionlint",
      "api-test",
      "mcp-test",
      "webapp-build",
      "Analyze (actions)",
      "Analyze (javascript-typescript)",
      "Analyze (python)"
    ]
  },
  "enforce_admins": true,
  "required_pull_request_reviews": {
    "required_approving_review_count": 1,
    "dismiss_stale_reviews": true,
    "require_code_owner_reviews": false,
    "require_last_push_approval": false
  },
  "restrictions": null,
  "required_linear_history": true,
  "allow_force_pushes": false,
  "allow_deletions": false,
  "block_creations": false,
  "required_conversation_resolution": true
}
EOF

echo "Branch protection applied to ${REPO}:${BRANCH}"
