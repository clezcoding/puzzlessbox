---
status: diagnosed
trigger: "G-05.2-2 — Prod Google Calendar connect from Settings redirects browser to API /auth/google/connect and returns UNSUPPORTED_MEDIA_TYPE because Accept header must include application/vnd.puzzlessbox.v1+json"
created: 2026-08-09T05:27:00Z
updated: 2026-08-09T05:30:00Z
symptoms_prefilled: true
goal: find_root_cause_only
---

## Current Focus

hypothesis: "AcceptVersionMiddleware rejects browser top-level GETs to /auth/google/connect (and callback) because skip list omits OAuth paths; Settings uses window.location so Accept cannot be set"
test: prod curl with browser Accept vs vnd Accept; code read of middleware + wizard
expecting: browser Accept → 415; vnd Accept → past middleware (401 without auth)
next_action: return ROOT CAUSE FOUND (diagnose-only)
bug_class: Bohrbug
known_pattern_candidate: none (no knowledge-base.md)

reasoning_checkpoint:
  hypothesis: "AcceptVersionMiddleware 415-blocks browser navigations to /auth/google/connect because _VERSION_SKIP_PREFIXES omits OAuth routes AND Settings uses window.location.href which cannot send Accept: application/vnd.puzzlessbox.v1+json"
  confirming_evidence:
    - "prod curl Accept: text/html… → 415 UNSUPPORTED_MEDIA_TYPE on /auth/google/connect and /auth/google/callback"
    - "prod curl Accept: vnd → 401 Missing authentication (middleware passed)"
    - "main.py skip list is only /health,/ready,/docs,/redoc,/openapi.json"
    - "calendar-wizard.tsx handleConnect sets window.location.href = getCalendarConnectUrl()"
  falsification_test: "If middleware already skipped /auth/google/* OR wizard used fetch with Accept header, browser Accept curl would not return 415"
  fix_rationale: "N/A diagnose-only — fix must either exempt browser OAuth paths from Accept enforcement and/or start connect via authenticated apiFetch then redirect"
  blind_spots: "After Accept fix, connect may still 401: window.location cannot attach Authorization Bearer that apiFetch uses; Better Auth cookie is webapp-host; API SESSION_COOKIE only set via API /auth/login. Callback JSON return vs webapp redirect also unverified end-to-end."
  candidate_causes:
    - "code: AcceptVersionMiddleware _VERSION_SKIP_PREFIXES omits /auth/google/connect and /auth/google/callback"
    - "code: webapp Settings uses top-level navigation instead of apiFetch (which sets Accept+Bearer)"
    - "config: SESSION_COOKIE_DOMAIN may not share JWT cookie to api host (secondary after Accept)"
  and_gate: "yes — 415 requires both middleware enforcement AND a client that cannot set Accept (browser navigation). Either exempt OAuth or change connect client to send Accept."

## Symptoms

expected: Confirm event with Google Connected; edit conflicting remote → conflict panel; scrape retry CTA. First step: Settings → Connect Google Calendar starts OAuth and returns connected.
actual: User reported: Wenn ich mich auf der prod/coolify url anmelde und in den settings den google calender verbinden möchte werde ich auf diese error seite geleitet — https://api.puzzlestool.online/auth/google/connect → {"error":{"code":"UNSUPPORTED_MEDIA_TYPE","message":"Accept header must include application/vnd.puzzlessbox.v1+json"}}
errors: UNSUPPORTED_MEDIA_TYPE — Accept header must include application/vnd.puzzlessbox.v1+json
reproduction: Test 2 in UAT — login on prod Coolify URL (pbox), open Settings, click connect Google Calendar
started: Discovered during UAT on prod after PR #61 deploy

## Eliminated

- hypothesis: "Prod API down / wrong host only"
  evidence: "https://api.puzzlesstool.online responds; with correct Accept returns 401 not connection error"
  timestamp: 2026-08-09T05:29:00Z

- hypothesis: "Only callback broken; connect itself fine"
  evidence: "Both /auth/google/connect and /auth/google/callback return 415 with browser Accept"
  timestamp: 2026-08-09T05:29:00Z

## Evidence

- timestamp: 2026-08-09T05:27:30Z
  checked: api/app/main.py AcceptVersionMiddleware
  found: "_VERSION_SKIP_PREFIXES = (/health, /ready, /docs, /redoc, /openapi.json); no /auth/google; missing Accept → 415 UNSUPPORTED_MEDIA_TYPE"
  implication: "Browser navigations to OAuth routes always 415"

- timestamp: 2026-08-09T05:27:45Z
  checked: webapp/components/settings/calendar-wizard.tsx + webapp/lib/api/calendar.ts
  found: "handleConnect: window.location.href = getCalendarConnectUrl() → `${API}/auth/google/connect`; no Accept/Authorization headers"
  implication: "Connect is top-level navigation; cannot set vnd Accept or Bearer JWT"

- timestamp: 2026-08-09T05:28:00Z
  checked: webapp/lib/api-client.ts
  found: "apiFetch sets Accept vnd + Authorization Bearer via getApiJwt(); comment notes cookie domain won't reach API"
  implication: "JSON API calls work; OAuth connect bypasses this path"

- timestamp: 2026-08-09T05:28:30Z
  checked: prod curl https://api.puzzlesstool.online
  found: "browser Accept → 415 on connect+callback; Accept vnd → 401 Missing authentication on connect"
  implication: "Root cause of reported error is Accept gate; auth is next layer after Accept"

- timestamp: 2026-08-09T05:28:45Z
  checked: api/app/routers/calendar.py
  found: "GET /auth/google/connect → RedirectResponse 302 (needs get_current_owner); GET /auth/google/callback has no JWT but still behind Accept middleware"
  implication: "Callback also blocked by Accept; Google redirect cannot send vnd header"

- timestamp: 2026-08-09T05:29:00Z
  checked: knowledge-base.md
  found: "file absent"
  implication: "No prior KB match"

- timestamp: 2026-08-09T05:29:15Z
  checked: common bug patterns + taxonomy
  found: "matches Data Shape/API Contract + Environment/client mismatch; bug_class=Bohrbug (deterministic 415)"
  implication: "Route: deterministic reproduction confirmed"

## Resolution

root_cause: "AcceptVersionMiddleware requires Accept: application/vnd.puzzlessbox.v1+json on all non-skip paths; Settings starts Google OAuth via browser top-level navigation to /auth/google/connect which cannot send that header, so API returns 415 before OAuth begins. Same gate also blocks Google redirect to /auth/google/callback. (AND-gate: middleware skip-list omission + window.location connect client.)"
fix:
verification:
files_changed: []
oracle_type: specified
