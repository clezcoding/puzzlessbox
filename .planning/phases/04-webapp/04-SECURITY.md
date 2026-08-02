---
phase: 04
slug: webapp
status: verified
threats_open: 0
asvs_level: 1
created: 2026-08-02
---

# Phase 04 — Security

> Per-phase security contract: threat register, accepted risks, and audit trail.

---

## Trust Boundaries

| Boundary | Description | Data Crossing |
|----------|-------------|---------------|
| Browser → Next.js (App Router) | Unauthenticated access; middleware checks session cookie | Session cookie, page requests |
| Next.js Client → FastAPI | API calls with session cookie (`credentials: include`); API validates `owner_id` | JWT, board/item/category payloads |
| Next.js → npm registry | shadcn + pnpm installs; official shadcn registry only | Package manifests |
| Browser → Next.js Client (DnD) | Client-side drag state; server validates on PATCH | Item/category IDs, sort order |
| Browser → Next.js (poll) | Authenticated poll via session cookie | Board items, categories |
| Next.js → api.* (OAuth start) | Redirect to Google consent; callback on api.* (Phase 1) | OAuth state, tokens |
| api.* → app.* (OAuth return) | Redirect back to wizard step 2 with code/state | OAuth code, state |
| FastAPI → Postgres | RLS per tenant; explicit `WHERE owner_id` additionally | All tenant data |

---

## Threat Register

| Threat ID | Category | Component | Severity | Disposition | Mitigation | Status |
|-----------|----------|-----------|----------|-------------|------------|--------|
| T-04-01 | Spoofing | login endpoint | high | mitigate | Better Auth email/password; httpOnly+Secure+SameSite=Lax cookie | closed |
| T-04-02 | Information Disclosure | session cookie | high | mitigate | httpOnly prevents JS access; Secure over HTTPS; SameSite=Lax | closed |
| T-04-03 | Tampering | JWT in cookie | medium | mitigate | API validates JWT via JWKS (D-21); client never trusts unverified token state | closed |
| T-04-04 | Information Disclosure | `?next=` redirect | medium | mitigate | `getSafeNextPath` rejects absolute URLs and foreign hosts | closed |
| T-04-05 | Tampering | npm/pnpm installs | high | mitigate | Official shadcn registry only; package legitimacy audit (04-RESEARCH) | closed |
| T-04-06 | Tampering | OG image proxy | medium | mitigate | `next/image` with `remotePatterns` allowlist; broken-image fallback | closed |
| T-04-07 | Tampering / IDOR | PATCH /categories/{id} | high | mitigate | `owner_id` WHERE + RLS; 404 on foreign category | closed |
| T-04-08 | Tampering / XSS | categories.color | high | mitigate | SQLModel regex `^#[0-9a-fA-F]{6}$`; 422 on invalid | closed |
| T-04-09 | Information Disclosure | GET /board-items | high | mitigate | `WHERE owner_id` + `deleted_at IS NULL` + status filter; RLS | closed |
| T-04-10 | Tampering / IDOR | PATCH /items/{id} | high | mitigate | `_lookup_item_type` checks `owner_id`; 404 on foreign | closed |
| T-04-11 | Repudiation | DELETE /items/{id} | medium | mitigate | `deleted_at` timestamp + `owner_id`; restore owner-only | closed |
| T-04-12 | Denial of Service | POST /categories/reorder | medium | mitigate | `MAX_REORDER_ITEMS=100`; per-entry `owner_id` validation | closed |
| T-04-12b | Tampering / IDOR | POST /items/reorder | high | mitigate | `owner_id` check per item; 404 foreign; atomic UPDATE | closed |
| T-04-13 | Tampering | optimistic move bypass | high | mitigate | API validates `owner_id` + RLS; UI revert on 401/403/500 | closed |
| T-04-14 | Information Disclosure | item modal cross-tenant | high | mitigate | API 404 on foreign `item_id`; modal uses local board reference only | closed |
| T-04-15 | Tampering | bulk move sequential PATCH | medium | mitigate | `owner_id` check per PATCH; loop breaks on 403/404 | closed |
| T-04-16 | Denial of Service | DnD rapid drag spam | low | accept | Debounce on API call; optimistic UI buffers | closed |
| T-04-17 | Tampering / XSS | category name in panel | medium | mitigate | React text binding; `maxLength=40`; no `dangerouslySetInnerHTML` | closed |
| T-04-18 | Tampering | 412 conflict force-PATCH | medium | mitigate | Server-side ETag-bypass validation + audit log for overrides | open — below high threshold (non-blocking) |
| T-04-19 | Information Disclosure | poll cross-tenant leak | high | mitigate | API filters `owner_id` + RLS; poll uses session cookie | closed |
| T-04-20 | Spoofing / CSRF | calendar OAuth callback | high | mitigate | HMAC-signed OAuth state (Phase 1) + session check; redirect whitelist | closed |
| T-04-21 | Information Disclosure | calendar list leak | medium | mitigate | `GET /calendar/list` owner-scoped; `GET /auth/google/status` owner-scoped | closed |
| T-04-22 | Tampering | theme/sound localStorage | low | accept | Client-side only; no security impact | closed |
| T-04-23 | Denial of Service | poll interval flooding | low | mitigate | 10s base + exponential backoff; no concurrent polls; debounced refresh | closed |

*Status: open · closed · open — below high threshold (non-blocking)*
*Severity: critical > high > medium > low — only open threats at or above `workflow.security_block_on` count toward `threats_open`*
*Disposition: mitigate (implementation required) · accept (documented risk) · transfer (third-party)*

---

## Accepted Risks Log

| Risk ID | Threat Ref | Rationale | Accepted By | Date |
|---------|------------|-----------|-------------|------|
| AR-04-01 | T-04-16 | DnD rapid drag spam mitigated client-side via debounce + optimistic UI; normal user behavior cannot overload server | gsd-security-auditor | 2026-08-02 |
| AR-04-02 | T-04-22 | Theme/sound preferences in localStorage are client-side UX only; no auth or tenant data stored | gsd-security-auditor | 2026-08-02 |

---

## Security Audit Trail

| Audit Date | Threats Total | Closed | Open | Run By |
|------------|---------------|--------|------|--------|
| 2026-08-02 | 24 | 23 | 1 | gsd-security-auditor |

### Security Audit 2026-08-02

| Metric | Count |
|--------|-------|
| Threats found | 24 |
| Closed | 23 |
| Open (blocking) | 0 |
| Open (non-blocking) | 1 |

**Notes:**
- T-04-18: Item modal sends `If-None-Match: *` on 412 "Behalten" force-PATCH, but `api/app/routers/items.py` `update_item` does not validate ETag or honor bypass header; no audit log for overrides. Calendar ETag validation exists in `api/app/services/calendar.py` only. Non-blocking (medium < high `block_on` threshold).
- Unregistered flag `GET /auth/google/status` maps to T-04-21; endpoint is owner-scoped via `Depends(get_current_owner)`.

---

## Sign-Off

- [x] All threats have a disposition (mitigate / accept / transfer)
- [x] Accepted risks documented in Accepted Risks Log
- [x] `threats_open: 0` confirmed
- [x] `status: verified` set in frontmatter

**Approval:** verified 2026-08-02
