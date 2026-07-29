---
phase: 00
slug: branding-design-system
status: verified
threats_open: 0
asvs_level: 1
created: 2026-07-29
---

# Phase 00 — Security

> Per-phase security contract: threat register, accepted risks, and audit trail.

---

## Trust Boundaries

| Boundary | Description | Data Crossing |
|----------|-------------|---------------|
| brand/ → Next.js build | Tokens + assets cross from static package into Next.js compile; no runtime user input | CSS custom properties, PNG binaries |
| PNG asset provenance | Assets sourced from `.planning/sketches/003-apollo-asset-pack/` (Higgsfield-generated, keep-all per D-03) | Internal sketch assets → `brand/assets/` |
| brand/*.md → downstream agents | Documentation read by `/gsd-ui-phase 4` and LLM capture agents; no runtime user input | Brand identity + voice guidelines |

---

## Threat Register

| Threat ID | Category | Component | Severity | Disposition | Mitigation | Status |
|-----------|----------|-----------|----------|-------------|------------|--------|
| T-00-01 | Tampering | PNG asset integrity during copy | low | accept | Assets copied from trusted internal sketch folder; no untrusted upload path in this phase | closed |
| T-00-02 | Information Disclosure | SVG script injection (deferred) | low | accept | D-05 ships PNG kit only; no SVGs in Phase 0 — verified 0 SVG files under `brand/` | closed |
| T-00-SC | Tampering | npm installs (tailwindcss/postcss) | low | accept | `brand/` is pure static package — no `package.json`, no `node_modules`; consumers install Tailwind themselves | closed |
| T-00-03 | Information Disclosure | Voice docs leak internal codenames or unreleased features | low | accept | Brand docs are internal-canonical; repo is private (AGPL-3.0 + Commercial); no secrets in voice examples | closed |

*Status: open · closed · open — below high threshold (non-blocking)*
*Severity: critical > high > medium > low — only open threats at or above workflow.security_block_on count toward threats_open*
*Disposition: mitigate (implementation required) · accept (documented risk) · transfer (third-party)*

---

## Accepted Risks Log

| Risk ID | Threat Ref | Rationale | Accepted By | Date |
|---------|------------|-----------|-------------|------|
| AR-00-01 | T-00-01 | Assets promoted from trusted internal sketch folder only; no external upload surface in Phase 0 | gsd-secure-phase | 2026-07-29 |
| AR-00-02 | T-00-02 | PNG-only kit per D-05; SVG vectorization deferred post-credit-topup; 0 SVG files verified | gsd-secure-phase | 2026-07-29 |
| AR-00-03 | T-00-SC | Zero-runtime-deps static package; Tailwind installed by downstream consumers, not brand/ | gsd-secure-phase | 2026-07-29 |
| AR-00-04 | T-00-03 | Private repo; voice examples contain no secrets or unreleased feature codenames | gsd-secure-phase | 2026-07-29 |

---

## Security Audit Trail

| Audit Date | Threats Total | Closed | Open | Run By |
|------------|---------------|--------|------|--------|
| 2026-07-29 | 4 | 4 | 0 | gsd-secure-phase (L1 grep, ASVS-1 short-circuit) |

**L1 evidence (2026-07-29):**
- `ls brand/assets/*.png | wc -l` → 25
- `find brand -name '*.svg' | wc -l` → 0
- `brand/package.json` → absent
- `brand/node_modules` → absent
- `node --test brand/tests/*.test.js` → 0 failures
- `grep` brand/*.md for secrets/credentials → no matches

---

## Sign-Off

- [x] All threats have a disposition (mitigate / accept / transfer)
- [x] Accepted risks documented in Accepted Risks Log
- [x] `threats_open: 0` confirmed
- [x] `status: verified` set in frontmatter

**Approval:** verified 2026-07-29
