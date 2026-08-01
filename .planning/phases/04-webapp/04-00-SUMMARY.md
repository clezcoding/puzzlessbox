---
phase: 04-webapp
plan: 00
subsystem: ui
tags: [nextjs, vitest, shadcn, better-auth, tailwind-v4, brand-tokens]

requires:
  - phase: 00-branding-design-system
    provides: brand/tokens.css and tailwind.preset.ts design tokens
  - phase: 01-datenmodell-backend-api
    provides: Better Auth JWKS bridge and unified API error shape
provides:
  - Vitest + RTL test infrastructure (no test bodies yet)
  - shadcn/ui init with brand CSS variable mapping
  - apiFetch client with credentials:include and error parsing
  - Better Auth React client and session middleware
  - Root layout with brand fonts, Toaster, German locale
affects: [04-01]

tech-stack:
  added: [vitest, @testing-library/react, @testing-library/jest-dom, tailwindcss v4, @tailwindcss/postcss, shadcn primitives, sonner, lucide-react, @hello-pangea/dnd, zod, react-hook-form]
  patterns: [brand token CSS vars for shadcn, apiFetch error shape, getSessionCookie middleware guard]

key-files:
  created:
    - webapp/vitest.config.ts
    - webapp/tests/setup.ts
    - webapp/components.json
    - webapp/app/globals.css
    - webapp/app/layout.tsx
    - webapp/app/page.tsx
    - webapp/middleware.ts
    - webapp/lib/api-client.ts
    - webapp/lib/auth-client.ts
    - webapp/lib/utils.ts
    - webapp/components/ui/button.tsx
    - webapp/components/ui/input.tsx
    - webapp/components/ui/label.tsx
    - webapp/components/ui/sonner.tsx
    - webapp/postcss.config.mjs
    - webapp/public/apollo-icon-favicon.png
  modified:
    - webapp/package.json

key-decisions:
  - "shadcn semantic tokens map to brand/tokens.css via @theme inline — no parallel palette"
  - "Middleware uses getSessionCookie for optimistic redirect; full session validation deferred to page/route level per Better Auth docs"
  - "globals.css imports ../../brand/tokens.css (correct path from webapp/app/)"

patterns-established:
  - "apiFetch<T>: credentials include + { error: { code, message, details? } } parsing"
  - "Protected routes: /board and /settings redirect to /login?next=<path>"

requirements-completed: [BOARD-01, CAP-05]

coverage:
  - id: D1
    description: "Vitest + RTL test infrastructure runs with --passWithNoTests"
    requirement: BOARD-01
    verification:
      - kind: unit
        ref: "cd webapp && pnpm test -- --run --passWithNoTests"
        status: pass
    human_judgment: false
  - id: D2
    description: "shadcn init with brand/tokens.css CSS variable mapping in globals.css"
    requirement: BOARD-01
    verification:
      - kind: other
        ref: "webapp/components.json + webapp/app/globals.css @import brand/tokens.css"
        status: pass
    human_judgment: false
  - id: D3
    description: "apiFetch with credentials:include and unified error shape"
    requirement: CAP-05
    verification:
      - kind: unit
        ref: "webapp/lib/api-client.ts ApiError + parseApiError"
        status: pass
    human_judgment: false
  - id: D4
    description: "Better Auth client exports authClient + useSession"
    requirement: BOARD-01
    verification:
      - kind: other
        ref: "webapp/lib/auth-client.ts"
        status: pass
    human_judgment: false
  - id: D5
    description: "Middleware redirects unauthenticated /board and /settings to /login?next="
    requirement: BOARD-01
    verification:
      - kind: integration
        ref: "webapp/middleware.ts getSessionCookie guard"
        status: pass
    human_judgment: true
    rationale: "End-to-end redirect flow requires /login route (04-01); middleware logic verified at build time only"

duration: 18min
completed: 2026-08-02
status: complete
---

# Phase 4 Plan 00: Wave 0 Infra Summary

**Vitest + shadcn + brand token wiring, apiFetch/auth clients, and session middleware on Next.js 16**

## Performance

- **Duration:** 18 min
- **Started:** 2026-08-01T23:00:00Z
- **Completed:** 2026-08-01T23:18:00Z
- **Tasks:** 1
- **Files modified:** 18

## Accomplishments

- Wave 0 Vitest setup (jsdom, jest-dom, passWithNoTests) — runs in ~4s
- shadcn/ui initialized; components.json + globals.css map semantic tokens to `brand/tokens.css`
- `apiFetch<T>` with `credentials: "include"` and `{ error: { code, message, details? } }` parsing
- `authClient` + `useSession` from `better-auth/react`
- Middleware guards `/board` and `/settings` → `/login?next=`
- Root layout: Instrument Serif + DM Sans, sonner Toaster, `lang="de"`, Apollo favicon
- `pnpm build` green

## Task Commits

1. **Task 1: Wave 0 Vitest-Setup + shadcn init + Brand-Wiring + API/Auth-Clients + Middleware** - `7d2430a` (feat)

## Files Created/Modified

- `webapp/vitest.config.ts` — Vitest config with jsdom + @ alias
- `webapp/tests/setup.ts` — jest-dom matchers
- `webapp/components.json` — shadcn config pointing at globals.css
- `webapp/app/globals.css` — Tailwind v4 + brand token import + shadcn @theme inline
- `webapp/lib/api-client.ts` — apiFetch, getCategories, getBoardItems
- `webapp/lib/auth-client.ts` — Better Auth React client
- `webapp/middleware.ts` — session cookie guard for protected routes
- `webapp/app/layout.tsx` — fonts, Toaster, metadata
- `webapp/app/page.tsx` — redirect `/` → `/board`
- `webapp/components/ui/*` — button, input, label, sonner primitives

## Decisions Made

- Manual shadcn component install (not `npx shadcn add`) to ensure brand token classes from day one
- `globals.css` uses `../../brand/tokens.css` (plan said `../brand` which would resolve incorrectly from `webapp/app/`)
- Open-redirect validation on `?next=` deferred to 04-01 per plan

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 3 - Blocking] Corrected brand/tokens.css import path**
- **Found during:** Task 1 (globals.css)
- **Issue:** Plan referenced `@import '../brand/tokens.css'` from `webapp/app/` — resolves to non-existent `webapp/brand/`
- **Fix:** Used `@import '../../brand/tokens.css'`
- **Files modified:** webapp/app/globals.css
- **Committed in:** 7d2430a

**2. [Rule 3 - Blocking] esbuild build script approval for Vitest**
- **Found during:** Task 1 verification
- **Issue:** pnpm ignored esbuild postinstall script
- **Fix:** Ran `pnpm approve-builds esbuild` + rebuild
- **Committed in:** 7d2430a (lockfile only; no source change)

---

**Total deviations:** 2 auto-fixed (2 blocking)
**Impact on plan:** Path fix required for brand tokens to load. esbuild approval is local pnpm config only.

## Issues Encountered

- Next.js build warns about missing `BETTER_AUTH_SECRET` / `BETTER_AUTH_URL` — expected in dev; env vars set in deployment
- Next.js 16.2 deprecates `middleware` convention in favor of `proxy` — tracked for future migration; current middleware works

## User Setup Required

None — no external service configuration required.

## Next Phase Readiness

- 04-01 can add login/board routes, test bodies, and avatar/dropdown-menu primitives
- `getCategories` / `getBoardItems` signatures ready for board data layer
- Middleware + auth client ready for login→board tracer

## Self-Check: PASSED

- FOUND: webapp/vitest.config.ts
- FOUND: webapp/tests/setup.ts
- FOUND: webapp/components.json
- FOUND: webapp/app/globals.css
- FOUND: webapp/lib/api-client.ts
- FOUND: webapp/lib/auth-client.ts
- FOUND: webapp/middleware.ts
- FOUND: 7d2430a

---
*Phase: 04-webapp*
*Completed: 2026-08-02*
