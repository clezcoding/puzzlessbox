#!/usr/bin/env bash
# Configure branch ruleset for clezcoding/puzzlessbox (public).
# Classic branch-protection API returns 404 here — use repository rulesets.
# Docs: https://docs.github.com/en/rest/repos/rules
# CodeQL default setup check names: Analyze (actions|javascript-typescript|python)
set -euo pipefail

REPO="${REPO:-clezcoding/puzzlessbox}"
RULESET_NAME="${RULESET_NAME:-main}"

PAYLOAD=$(cat <<'EOF'
{
  "name": "main",
  "target": "branch",
  "enforcement": "active",
  "conditions": {
    "ref_name": {
      "include": ["~DEFAULT_BRANCH"],
      "exclude": []
    }
  },
  "bypass_actors": [
    {
      "actor_id": 5,
      "actor_type": "RepositoryRole",
      "bypass_mode": "pull_request"
    }
  ],
  "rules": [
    { "type": "deletion" },
    { "type": "non_fast_forward" },
    { "type": "required_linear_history" },
    {
      "type": "pull_request",
      "parameters": {
        "required_approving_review_count": 0,
        "dismiss_stale_reviews_on_push": true,
        "require_code_owner_review": false,
        "require_last_push_approval": false,
        "required_review_thread_resolution": true,
        "allowed_merge_methods": ["squash"]
      }
    },
    {
      "type": "required_status_checks",
      "parameters": {
        "strict_required_status_checks_policy": true,
        "do_not_enforce_on_create": false,
        "required_status_checks": [
          { "context": "test" },
          { "context": "actionlint" },
          { "context": "api-test" },
          { "context": "mcp-test" },
          { "context": "webapp-build" },
          { "context": "Analyze (actions)" },
          { "context": "Analyze (javascript-typescript)" },
          { "context": "Analyze (python)" }
        ]
      }
    }
  ]
}
EOF
)

EXISTING_ID=$(gh api "repos/${REPO}/rulesets" --jq ".[] | select(.name==\"${RULESET_NAME}\") | .id" | head -1)

if [[ -n "${EXISTING_ID}" ]]; then
  gh api -X PUT "repos/${REPO}/rulesets/${EXISTING_ID}" --input - <<<"${PAYLOAD}"
  echo "Updated ruleset ${RULESET_NAME} (id=${EXISTING_ID}) on ${REPO}"
else
  gh api -X POST "repos/${REPO}/rulesets" --input - <<<"${PAYLOAD}"
  echo "Created ruleset ${RULESET_NAME} on ${REPO}"
fi
