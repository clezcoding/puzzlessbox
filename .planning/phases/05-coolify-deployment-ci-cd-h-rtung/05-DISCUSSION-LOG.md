# Phase 5: Coolify-Deployment, CI/CD & Härtung - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in CONTEXT.md — this log preserves the alternatives considered.

**Date:** 2026-08-02
**Phase:** 5-Coolify-Deployment, CI/CD & Härtung
**Areas discussed:** App-Topologie & Subdomains, CI/CD Workflow-Layout, Backup-Policy, Health-Check-Strategie, Secrets & Cutover-Reihenfolge
**Mode:** `--batch` · response_language `de` · recommendations marked per question

---

## App-Topologie & Subdomains

| Option | Description | Selected |
|--------|-------------|----------|
| `app.puzzlesstool.online` | Recommended default matching api./mcp. | |
| Apex `puzzlesstool.online` | Root domain | |
| `web.puzzlesstool.online` | Alternate subdomain | |
| `pbox.puzzlesstool.online` | User custom | ✓ |

**User's choice:** `pbox.puzzlesstool.online`
**Notes:** Overrides recommended `app.`

| Option | Description | Selected |
|--------|-------------|----------|
| UI switch same UUID | Change build_pack in place | |
| New dockerimage app + domain swap | Recreate because switch unsupported | ✓ |
| Keep dockerfile | Defer image deploy | |

**User's choice:** New app cutover — cannot switch build_pack via UI/CLI/MCP

| Option | Description | Selected |
|--------|-------------|----------|
| Create Coolify app first | Instant deploy false | |
| Workflow + GHCR push then app | Avoid empty image | ✓ |
| Nixpacks in Coolify | Rejected (locked) | |

**User's choice:** Push then create app

| Option | Description | Selected |
|--------|-------------|----------|
| Leave scraper as-is | OPS scope only | ✓ |
| Harden scraper in Phase 5 | Health/images/network | |
| Full compose rebuild | Out of scope | |

**User's choice:** (a) after clarifying Firecrawl/Camoufox meaning; deferred harden to later phase

---

## CI/CD Workflow-Layout

| Option | Description | Selected |
|--------|-------------|----------|
| Separate deploy-*.yml | Path-filter per service | ✓ |
| Matrix one file | Shared job matrix | |
| Monolith always-all | One job builds all | |

**User's choice:** Separate files

| Option | Description | Selected |
|--------|-------------|----------|
| App webhook + Bearer | Match MCP; GET for new | ✓ |
| Deploy API ?uuid= | reloop pattern | |
| Registry poll only | No instant deploy | |

**User's choice:** Webhook + Bearer after review of live MCP POST + Coolify docs (GET preferred for new)

| Option | Description | Selected |
|--------|-------------|----------|
| latest + sha-short | MCP parity | ✓ |
| sha only | No latest | |
| SemVer git tags | Release process | |

**User's choice:** latest + sha-

| Option | Description | Selected |
|--------|-------------|----------|
| Fail hard non-2xx | curl -f | ✓ |
| best-effort \|\| true | Hide deploy fail | |
| Retry 3× then fail | Soften | |

**User's choice:** Fail hard

---

## Backup-Policy

| Option | Description | Selected |
|--------|-------------|----------|
| Daily 03:00 UTC | `0 3 * * *` | ✓ |
| Every 6h | Higher disk | |
| Weekly | Up to 7d RPO | |

**User's choice:** Daily

| Option | Description | Selected |
|--------|-------------|----------|
| 7 days | Tight | |
| 14 days | Balance | ✓ |
| 30 days | Disk heavy | |

**User's choice:** 14

| Option | Description | Selected |
|--------|-------------|----------|
| Trigger immediately | Baseline before cutover | ✓ |
| Schedule only | Wait for night | |
| Manual only | No auto trigger | |

**User's choice:** Trigger now; also noted S3 upgrade intent for later milestone (OPS-06)

---

## Health-Check-Strategie

| Option | Description | Selected |
|--------|-------------|----------|
| /health only for Coolify | Liveness | |
| /ready for Coolify | Includes deps | |
| /health Coolify + /ready monitor | Split | ✓ |

**User's choice:** Split

| Option | Description | Selected |
|--------|-------------|----------|
| Dedicated /api/health | Unauthenticated 200 | ✓ |
| Probe /login | Like clared-web | |
| Docker HEALTHCHECK only | No app route | |

**User's choice:** Dedicated route

| Option | Description | Selected |
|--------|-------------|----------|
| MCP-style 5s | Aggressive | |
| 10s / 15s start | Web cold start | ✓ |
| 3s aggressive | Noise | |

**User's choice:** 10s interval, 15s start

---

## Secrets & Cutover-Reihenfolge

| Option | Description | Selected |
|--------|-------------|----------|
| Parallel API+Web | Fast | |
| Sequential backup→API→Web | Ordered | ✓ |
| Web first | Login without API | |

**User's choice:** Sequential

| Option | Description | Selected |
|--------|-------------|----------|
| Shared token + per-app webhooks | MCP pattern | ✓ |
| One project webhook | Couples deploys | |
| Token per app | Secret spam | |

**User's choice:** Shared token + per-app webhooks

| Option | Description | Selected |
|--------|-------------|----------|
| Private GHCR + Coolify login | Secure default if private repo | |
| Public GHCR packages | Fits public repo | ✓ |
| Decide later | Kick can | |

**User's choice:** Public packages — user clarified repo is public (not private)

| Option | Description | Selected |
|--------|-------------|----------|
| Temp FQDN then swap | Safer smoke | |
| Immediate domain on new, stop old | Faster | ✓ |
| Dual same domain | Traefik conflict | |

**User's choice:** Immediate swap

---

## Claude's Discretion

- Exact WebApp health path string
- GHCR image naming for api/web
- Whether to retune MCP health intervals to match D-14
- Env copy checklist old→new API app
- Optional HTTP 200/202 assert beyond curl -f

## Deferred Ideas

- Scraper-Stack harden post-prod
- Optional deploy-mcp.yml POST→GET align
- OPS-05 GlitchTip (v2)
- OPS-06 S3 offsite backups (later milestone — user confirmed intent)
