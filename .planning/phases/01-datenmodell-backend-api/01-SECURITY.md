---
phase: 1
slug: datenmodell-backend-api
status: verified
threats_open: 0
asvs_level: 1
created: 2026-07-31
---

# Phase 1 — Security

> Per-phase security contract: threat register, accepted risks, and audit trail.

---

## Trust Boundaries

| Boundary | Description | Data Crossing |
|----------|-------------|---------------|
| Public HTTPS → FastAPI | Internet clients hit api.puzzlesstool.online | JWT/cookie/session, draft/link/calendar payloads |
| FastAPI → Postgres | App DB role + RLS | owner_id scoped rows, encrypted calendar tokens |
| FastAPI → Scraper stack | Internal Docker network only | Firecrawl/Camoufox bearer, scrape URLs |
| FastAPI → Google OAuth | Separate Calendar OAuth client | Authorization codes, refresh/access tokens |
| FastAPI → Better Auth JWKS | Webapp JWKS endpoint | Public keys for JWT verify |

---

## Threat Register

| Threat ID | Category | Component | Severity | Disposition | Mitigation | Status |
|-----------|----------|-----------|----------|-------------|------------|--------|
| T-01-docs | Information Disclosure | /docs /redoc | medium | mitigate | Disabled when ENV=prod | closed |
| T-01-versioning | Tampering | Accept middleware | medium | mitigate | Missing Accept → 415 | closed |
| T-01-SC (01-01) | Tampering | pip deps | high | mitigate | Pinned requirements.txt | closed |
| T-01-timer-race | Tampering | timeout manager | medium | mitigate | Cancel-then-spawn on asyncio loop | closed |
| T-01-orphan-save | Tampering | autosave | high | mitigate | UPDATE WHERE status='draft'; cancel on confirm | closed |
| T-01-cross-owner | Information Disclosure | draft CRUD | high | mitigate | RLS + owner_id filters | closed |
| T-01-ssrf | Tampering / Info Disclosure | scraper | high | mitigate | Scheme/length + private IP reject | closed |
| T-01-scraper-bearer | Spoofing | Firecrawl/Camoufox | high | mitigate | Internal network expose-only + bearer | closed |
| T-01-scrape-timeout | DoS | scraper | medium | mitigate | 8s+4s httpx timeouts | closed |
| T-01-SC (01-03) | Tampering | scrape deps | low | accept | No new scrape packages; stdlib/regex OG | closed |
| T-01-oauth-csrf | Tampering | Google OAuth state | high | mitigate | Signed state verify on callback | closed |
| T-01-token-exposure | Information Disclosure | calendar_tokens | high | mitigate | AES-256-GCM at rest | closed |
| T-01-silent-overwrite | Tampering | calendar PATCH | high | mitigate | If-Match + 412 conflict | closed |
| T-01-oauth-scope | Elevation of Privilege | Calendar OAuth | medium | mitigate | Separate Google client/scopes | closed |
| T-01-SC (01-04) | Tampering | Google API pkgs | high | mitigate | Pinned google-* packages | closed |
| T-01-tenant | Information Disclosure | core tables | high | mitigate | RLS FORCE + app.owner_id | closed |
| T-01-auth | Spoofing | JWKS JWT | high | mitigate | PyJWKClient RS256 + exp + sub | closed |
| T-01-signup | Tampering | signup lock | high | mitigate | databaseHooks count → 409 | closed |
| T-01-cookie | Spoofing | session cookie | medium | mitigate | httponly, samesite=lax, secure prod | closed |
| T-01-service-bearer | Spoofing | X-Service-Bearer | high | mitigate | hmac.compare_digest + bearer_hash | closed |
| T-01-idempotency | Tampering | Idempotency-Key | low | mitigate | Store/replay per owner_id | closed |

---

## Accepted Risks Log

| Risk ID | Threat Ref | Rationale | Accepted By | Date |
|---------|------------|-----------|-------------|------|
| AR-01-03-SC | T-01-SC (01-03) | Plan accepted: no new scrape packages; regex/stdlib OG parse avoids BeautifulSoup | orchestrator / gsd-secure-phase | 2026-07-31 |

---

## Security Audit Trail

| Audit Date | Threats Total | Closed | Open | Run By |
|------------|---------------|--------|------|--------|
| 2026-07-31 | 21 | 21 | 0 | gsd-security-auditor |

---

## Sign-Off

- [x] All threats have a disposition (mitigate / accept / transfer)
- [x] Accepted risks documented in Accepted Risks Log
- [x] `threats_open: 0` confirmed
- [x] `status: verified` set in frontmatter

**Approval:** verified 2026-07-31
