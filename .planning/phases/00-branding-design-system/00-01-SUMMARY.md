---
phase: 00-branding-design-system
plan: 01
subsystem: ui
tags: [brand, tailwind, css-tokens, apollo, node-test]

requires: []
provides:
  - 25-PNG Apollo asset library under brand/assets/
  - Light + dark CSS tokens in brand/tokens.css
  - Tailwind v4 preset in brand/tailwind.preset.ts
  - node:test validation for assets and tokens
affects: [00-02-branding-design-system, phase-4-webapp]

tech-stack:
  added: []
  patterns:
    - Tailwind v4 CSS-first @theme tokens with @theme dark parity
    - Pure static brand/ package (no runtime deps)
    - node:test asset and token validation

key-files:
  created:
    - brand/tokens.css
    - brand/tailwind.preset.ts
    - brand/assets/ (25 PNGs)
    - brand/tests/assets.test.js
    - brand/tests/tokens.test.js
    - brand/README.md
  modified: []

key-decisions:
  - "PNG kit only per D-05 — no SVG vectorization in Phase 0"
  - "Category dark mode shifts bg tokens only; accents unchanged per D-08"

patterns-established:
  - "Downstream Next.js imports brand/tokens.css and brand/tailwind.preset.ts"
  - "Canonical assets promoted from .planning/sketches/003-apollo-asset-pack/"

requirements-completed: [BRAND-01, BRAND-02]

coverage:
  - id: D1
    description: 25 canonical Apollo PNG assets versioned under brand/assets/
    requirement: BRAND-01
    verification:
      - kind: unit
        ref: "brand/tests/assets.test.js#all 25 canonical Apollo PNG assets exist and are non-empty"
        status: pass
    human_judgment: false
  - id: D2
    description: Full light + dark design tokens with category pastels and spacing scale
    requirement: BRAND-02
    verification:
      - kind: unit
        ref: "brand/tests/tokens.test.js#tokens.css defines full light + dark token set"
        status: pass
    human_judgment: false
  - id: D3
    description: Tailwind v4 preset referencing CSS custom properties for Next.js consumption
    requirement: BRAND-02
    verification:
      - kind: unit
        ref: "grep var(--color-inbox-bg) brand/tailwind.preset.ts"
        status: pass
    human_judgment: false

duration: 2min
completed: 2026-07-29
status: complete
---

# Phase 00 Plan 01: Brand Kit Package Summary

**25-PNG Apollo asset library with light/dark CSS tokens and Tailwind v4 preset validated by node:test**

## Performance

- **Duration:** 2 min
- **Started:** 2026-07-29T03:22:55Z
- **Completed:** 2026-07-29T03:24:35Z
- **Tasks:** 2
- **Files modified:** 34

## Accomplishments

- Shipped production `brand/` package at repo root with 25 canonical Apollo PNG assets
- Defined full Utilitarian Bone light + dark `@theme` tokens including D-07 category pastels and spacing scale
- Exported Tailwind v4-compatible preset mapping semantic colors, nested category objects, fonts, and spacing to CSS vars
- Added `node:test` suites validating asset inventory and required token variables

## Task Commits

Each task was committed atomically:

1. **Task 1: Tracer — brand/ skeleton** - `37cbb72` (feat)
2. **Task 2: Full 25-PNG kit + tokens + preset** - `1fe51aa` (feat)

**Plan metadata:** pending (docs commit)

## Files Created/Modified

- `brand/tokens.css` — Light `@theme` + `@theme dark` semantic, category, font, spacing tokens
- `brand/tailwind.preset.ts` — Full Tailwind Config preset referencing CSS variables
- `brand/assets/*.png` — 25 promoted Apollo illustrations (icons, empty states, OG, scenes)
- `brand/tests/assets.test.js` — Asserts all 25 PNGs exist and are non-empty
- `brand/tests/tokens.test.js` — Asserts required light/dark CSS variables present
- `brand/README.md` — Package layout and Next.js consumption pattern

## Decisions Made

- PNG kit only per D-05 — SVG vectorization deferred until Higgsfield credits restored
- Dark category tokens shift background hues only; accent hex values unchanged per D-08

## Deviations from Plan

None - plan executed exactly as written.

## Issues Encountered

None

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness

- Plan 00-02 can promote `BRAND.md` and `VOICE.md` into `brand/`
- Phase 4 WebApp can `@import "../brand/tokens.css"` and consume `tailwind.preset.ts`
- `node --test brand/tests/*.test.js` green for CI gate

## Self-Check: PASSED

- FOUND: brand/tokens.css
- FOUND: brand/tailwind.preset.ts
- FOUND: brand/tests/assets.test.js
- FOUND: commit 37cbb72
- FOUND: commit 1fe51aa

---
*Phase: 00-branding-design-system*
*Completed: 2026-07-29*
