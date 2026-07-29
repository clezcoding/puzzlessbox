# Phase 0: Branding & Design System - Context

**Gathered:** 2026-07-29
**Status:** Ready for planning

<domain>
## Phase Boundary

Deliver a shippable Hallmark brand kit and design tokens for Puzzlessbox (BRAND-01, BRAND-02): Apollo-led identity, Util Bone UI scaffold, exported CSS/Tailwind tokens, versioned asset library under `brand/`, and voice documentation — ready to feed `/gsd-ui-phase 4`. No WebApp UI build in this phase.

</domain>

<decisions>
## Implementation Decisions

### Brand identity (pre-locked via sketches — carry forward)
- **D-01:** Brand hero is **Apollo** (raccoon mascot; myth companion of Hermes). Entire brand-facing identity derives from Apollo — no parallel abstract primary logo. — **Reversibility:** costly — all assets and voice assume Apollo
- **D-02:** UI scaffold DNA is Sketch **001-C Utilitarian Bone** (warm bone board, charcoal CTA, Instrument Serif + DM Sans, hairline columns, quiet motion). Brand accent = terracotta `#c45c3e` (bandana); util teal demoted to info-only.
- **D-03:** Sketch 003 Apollo asset pack is **keep-all** (~25 PNGs). Canonical character ref: `.planning/sketches/002-logo-mark-context/assets/brand-mascot-canonical.png`. Bible: `.planning/sketches/BRAND.md`.

### Asset promotion
- **D-04:** Sketches stay exploration source. Ship copy into repo root `brand/` (tokens, assets, BRAND.md, VOICE.md). Next.js consumes from `brand/`, not from `.planning/sketches/`. — **Reversibility:** reversible

### Logo / vector formats
- **D-05:** Phase 0 ships the **PNG kit** as the versioned asset library. Full SVG vectorization deferred — Higgsfield Recraft credits unavailable (~0.89). After credit top-up: vectorize brand marks first (favicon, app icon, wordmark, avatar, dark icon) — pragmatic A1 path. Empty/OG/scene illustrations remain PNG unless later needed as SVG. — **Reversibility:** reversible — SVGs can be added without invalidating PNGs

### Token delivery
- **D-06:** Deliver both `brand/tokens.css` (CSS custom properties) and `brand/tailwind.preset.ts` (Tailwind preset importing those tokens) for Next.js 16 consumption. — **Reversibility:** reversible

### Category pastels (locked hex)
- **D-07:** Lock five soft category pastels in tokens now (must not compete with terracotta brand signal):

| Category | Soft bg | Accent |
|---|---|---|
| Inbox | `#f0eeea` | `#787774` |
| Notizen | `#f5f0e6` | `#b8956a` |
| Links | `#e8f0f5` | `#5a7a8f` |
| Tasks | `#eaf3ec` | `#5f7d64` |
| Termine | `#f5ebe8` | `#c45c3e` |

— **Reversibility:** reversible — hex tweaks local to tokens

### Dark mode
- **D-08:** Full dark-theme **token parity** in Phase 0 via CSS (`[data-theme=dark]` or equivalent) covering all semantic surfaces/text/borders/brand/category tokens. Include existing `apollo-icon-dark`. Do **not** regenerate Apollo scene illustrations for dark (no HF credits) — place existing PNGs on dark surfaces. No Dark UI screens built here. — **Reversibility:** reversible

### Voice / tone documentation
- **D-09:** Keep voice card in brand bible; add `brand/VOICE.md` with ~8 microcopy examples covering empty, error, confirm, and capture moments. Tone: clever, dry, resourceful; capture verbs light (“caught”, “stashed”, “sorted”); no baby talk / meme spam / AI-slop. — **Reversibility:** reversible

### Claude's Discretion
- Exact `brand/` subdirectory layout (`assets/`, `tokens.css` placement) — choose boring convention for Next.js greenfield
- Dark token inversion mapping (bone↔charcoal) — keep readability WCAG-minded without new illustrations
- Exact eight VOICE.md sample lines — stay on-brand, German or bilingual OK if product UI language TBD; prefer German product UI copy samples unless PROJECT says otherwise (product brief is German)

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Requirements & roadmap
- `.planning/REQUIREMENTS.md` — BRAND-01, BRAND-02
- `.planning/ROADMAP.md` — Phase 0 goal + success criteria
- `.planning/PROJECT.md` — Hallmark branding before WebApp; Higgsfield for assets
- `PUZZLESSBOX_PROJECT_BRIEF.md` — product brief

### Brand / sketches (locked DNA)
- `.planning/sketches/BRAND.md` — Apollo identity, palette, typography, voice, rejects
- `.planning/sketches/MANIFEST.md` — sketch winners 001-C / 002-B / 003 keep-all
- `.planning/sketches/themes/default.css` — Util theme + Critter brand accent tokens
- `.planning/sketches/001-brand-mood-board/README.md` — Util winner lock
- `.planning/sketches/002-logo-mark-context/README.md` — Apollo/Critter winner
- `.planning/sketches/002-logo-mark-context/assets/brand-mascot-canonical.png` — character reference
- `.planning/sketches/003-apollo-asset-pack/KIT.md` — full asset inventory
- `.planning/sketches/003-apollo-asset-pack/README.md` — keep-all + pack notes
- `.planning/sketches/003-apollo-asset-pack/assets/` — ship source PNGs to promote

### Phase discuss artifacts
- `.planning/phases/00-branding-design-system/00-CONTEXT.md` — this file

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- Sketch theme CSS (`.planning/sketches/themes/default.css`) — seed for `brand/tokens.css` light + dark
- Apollo PNG pack under `003-apollo-asset-pack/assets/` — promote into `brand/assets/`
- `BRAND.md` — promote/adapt into `brand/BRAND.md`

### Established Patterns
- Greenfield repo — almost no app code yet; Phase 0 creates the first consumable `brand/` package surface for later Next.js
- Hallmark + Higgsfield already used for DNA/assets; planner should not re-open rejected marks (lettermark/seal/grid/box-buddy/cool-P)

### Integration Points
- Future Next.js app imports `brand/tailwind.preset.ts` and/or `brand/tokens.css`
- `/gsd-ui-phase 4` must consume these tokens — Phase 0 success = tokens + assets exist and are documented

</code_context>

<specifics>
## Specific Ideas

- Apollo naming locked by user: companion of Hermes (messaging/capture channel myth thread)
- User explicitly: entire brand identity on the raccoon — “ALLES”
- SVG full-set (A2) desired in principle but deferred until Higgsfield credits restored
- Category Termine accent deliberately reuses brand terracotta as capture-signal

</specifics>

<deferred>
## Deferred Ideas

- Recraft SVG vectorization of brand marks (favicon, app icon, wordmark, avatar, dark icon) — after HF credit top-up
- Optional later: SVG or dark-specific regenerations of empty/OG scenes — not required for Phase 0
- `pose-wave` / `pose-sleep` HF gens — still credit-blocked from asset pack
- `/gsd-sketch --wrap-up` to package sketch findings as a skill — optional hygiene

</deferred>

---

*Phase: 0-Branding & Design System*
*Context gathered: 2026-07-29*
