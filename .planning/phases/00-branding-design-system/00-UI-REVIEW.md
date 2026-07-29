# Phase 00 — UI Review

**Audited:** 2026-07-29
**Baseline:** `00-UI-SPEC.md` (approved 2026-07-29)
**Screenshots:** not captured (no dev server on ports 3000, 5173, 8080)

**Scope note:** Phase 00 ships a static `brand/` package (tokens, assets, docs) — no `src/` WebApp UI. Audit evaluates design-contract fidelity of tokens, voice docs, and state-asset inventory against UI-SPEC; visual pillar scored on asset coverage + documentation, not rendered components.

---

## Pillar Scores

| Pillar | Score | Key Finding |
|--------|-------|-------------|
| 1. Copywriting | 3/4 | VOICE.md aligns with contract table; Primary CTA not a locked example; empty-state body split incomplete |
| 2. Visuals | 2/4 | 25 state PNGs inventoried but no preview surface or screenshots to verify hierarchy/focal point |
| 3. Color | 3/4 | `tokens.css` hex matches UI-SPEC exactly; `BRAND.md` documents wrong `--color-muted` token name |
| 4. Typography | 2/4 | Font families tokenized; UI-SPEC size scale (14/16/20/28px) exists only in prose, not CSS/Tailwind |
| 5. Spacing | 4/4 | All seven spacing tokens match UI-SPEC scale; preset wired |
| 6. Experience Design | 3/4 | Seven UI-SPEC state categories covered by PNG assets; radius/motion tokens and long-text rules deferred |

**Overall: 17/24**

---

## Top 3 Priority Fixes

1. **Tokenize typography scale** — Phase 4 cannot compile `text-body`/`text-heading` from brand kit; risks size drift vs UI-SPEC — Add `--text-body: 16px`, `--text-label: 14px`, `--text-heading: 20px`, `--text-display: 28px` (with weights/line-heights) to `brand/tokens.css` and `fontSize` entries in `brand/tailwind.preset.ts`; extend `tokens.test.js` assertions.

2. **Lock Primary CTA as standalone microcopy example** — CTA copy only appears in alignment table (`brand/VOICE.md:130`), not in the 8 numbered examples; capture agents may miss it — Add `### 9. Primary CTA` (or renumber) with exact string `Eintrag sichern` and usage context (submit button, capture confirm).

3. **Split empty-state copy per Copywriting Contract** — UI-SPEC declares separate heading and body; example #1 merges them and omits stashen sentence — Update Inbox empty example to heading `Hier ist gähnende Leere.` + body `Apollo hat noch nichts gefangen. Sende eine Nachricht, um den ersten Eintrag zu stashen.` matching `00-UI-SPEC.md:87-88`.

---

## Detailed Findings

### Pillar 1: Copywriting (3/4)

**WARNING — Primary CTA not in numbered examples**
- UI-SPEC Copywriting Contract: `Eintrag sichern` (`00-UI-SPEC.md:86`)
- `brand/VOICE.md:130` lists it only in the alignment table; no dedicated `###` example with context
- Capture success example (`VOICE.md:47`) uses related phrasing `Eintrag gesichert` but is a toast, not the CTA label

**WARNING — Empty state heading/body split inconsistent**
- UI-SPEC: heading `Hier ist gähnende Leere.` + body with stashen CTA (`00-UI-SPEC.md:87-88`)
- `brand/VOICE.md:31` combines heading + first body sentence on one line; second body sentence appears only in placeholder example #8 (`VOICE.md:87`) and alignment table (`VOICE.md:132`)

**PASS — Contract strings present and on-brand**
- Error, destructive, offline, onboarding copy match UI-SPEC verbatim (`VOICE.md:55, 63, 71, 79`)
- Anti-patterns block generic SaaS/meme/AI-slop (`VOICE.md:108-118`)
- All product copy in German per project brief

**PASS — No off-brand generic labels in brand package**

### Pillar 2: Visuals (2/4)

**WARNING — No visual verification surface**
- No dev server; screenshots not captured
- `brand/` contains no preview HTML — mood-board sketch lives under `.planning/sketches/001-brand-mood-board/` only
- UI-SPEC checker already FLAGged missing focal-point section for brand-kit phase (`00-UI-SPEC.md:128`)

**PASS — State illustration inventory matches UI Considerations**
- Empty: `apollo-empty-inbox.png`, `apollo-empty-notes.png`, `apollo-empty-links.png`, `apollo-empty-tasks.png`, `apollo-empty-cal.png`, `apollo-empty-board.png`, `apollo-empty-caught.png`
- Loading: `apollo-loading.png`
- Error: `apollo-error.png`
- Offline: `apollo-offline.png`
- Splash: `apollo-splash.png`
- 404: `apollo-404.png`
- Dark: `apollo-icon-dark.png` + `@theme dark` tokens

**needs_human_review: true** — Bandana terracotta `#c45c3e`, bone surfaces, and illustration consistency across 25 PNGs require human eye on assets; not verifiable from code audit alone.

### Pillar 3: Color (3/4)

**PASS — Core palette matches UI-SPEC byte-for-byte**

| Role | UI-SPEC | `brand/tokens.css` | Match |
|------|---------|-------------------|-------|
| Dominant | `#f7f6f3` | `--color-bg: #f7f6f3` (L4) | ✓ |
| Secondary | `#ffffff` | `--color-surface: #ffffff` (L6) | ✓ |
| Accent | `#c45c3e` | `--color-brand: #c45c3e` (L14) | ✓ |
| Destructive | `#d9383a` | `--color-destructive: #d9383a` (L21) | ✓ |

**PASS — All five category pastel pairs locked** (`tokens.css:25-34`, dark L74-83)

**PASS — 60/30/10 documented** in `brand/BRAND.md:78-82` with terracotta reserved for brand signal

**WARNING — Documentation token name drift**
- `brand/BRAND.md:85` references `--color-muted` but shipped token is `--color-text-muted` (`tokens.css:11`)
- Downstream agents reading BRAND.md may grep wrong variable name

**PASS — Teal demoted to info-only** (`--color-info: #1f6c9f`, `BRAND.md:48, 88`)

### Pillar 4: Typography (2/4)

**PASS — Font families match UI-SPEC Design System**
- Instrument Serif display (`tokens.css:37-38`)
- DM Sans UI (`tokens.css:39`)
- JetBrains Mono mono (`tokens.css:40`)
- Wired in `tailwind.preset.ts:47-51`

**WARNING — Font size scale not tokenized**
- UI-SPEC declares Body 16px/400/1.5, Label 14px/600/1.4, Heading 20px/600/1.2, Display 28px/400/1.2 (`00-UI-SPEC.md:48-53`)
- `brand/tokens.css` has zero `--text-*` or `--font-size-*` variables
- `brand/tailwind.preset.ts` has no `fontSize` extend block
- Sizes exist only in `brand/BRAND.md:116-121` prose — not machine-consumable by Phase 4 Tailwind

**WARNING — Weight/line-height not exportable**
- UI-SPEC pairs sizes with weights; preset cannot emit `font-semibold` + `text-label` combo from brand kit alone

### Pillar 5: Spacing (4/4)

**PASS — Full UI-SPEC scale in tokens**

| Token | UI-SPEC | `tokens.css` |
|-------|---------|--------------|
| xs | 4px | `--spacing-xs: 4px` (L43) |
| sm | 8px | `--spacing-sm: 8px` (L44) |
| md | 16px | `--spacing-md: 16px` (L45) |
| lg | 24px | `--spacing-lg: 24px` (L46) |
| xl | 32px | `--spacing-xl: 32px` (L47) |
| 2xl | 48px | `--spacing-2xl: 48px` (L48) |
| 3xl | 64px | `--spacing-3xl: 64px` (L49) |

**PASS — Preset maps all spacing** (`tailwind.preset.ts:53-60`)

**PASS — No arbitrary spacing values in brand package**

**PASS — UI-SPEC "Exceptions: none" honored** — no rogue 12px step in shipped tokens (sketch theme `--space-3: 12px` not promoted)

### Pillar 6: Experience Design (3/4)

**PASS — UI-SPEC state coverage via assets** (7 covered per `00-UI-SPEC.md:104-112`)
- All listed PNG filenames present; `assets.test.js` validates 25/25 non-empty

**PASS — Dark mode token parity** (`@theme dark` L52-84); category accents unchanged per D-08

**PASS — Automated validation gate** — `node --test brand/tests/*.test.js` passes (2/2)

**WARNING — long-text overflow backstop deferred**
- UI-SPEC marks long-text as 🧪 backstop for Phase 4 (`00-UI-SPEC.md:113`)
- Acceptable for Phase 0; document in Phase 4 UI-SPEC

**WARNING — Shape/motion tokens not exported**
- BRAND.md specifies small radii, hairline borders, `prefers-reduced-motion` (`BRAND.md:143-151`)
- No `--radius-*` or `--dur-*` tokens in `brand/tokens.css` (sketch `default.css` has them; not promoted)
- Phase 4 must re-derive or duplicate sketch motion values

**Minor — node:test module warning**
- Tests emit `MODULE_TYPELESS_PACKAGE_JSON` warning (no root `package.json` `"type": "module"`) — cosmetic, tests pass

---

## Files Audited

- `.planning/phases/00-branding-design-system/00-UI-SPEC.md`
- `.planning/phases/00-branding-design-system/00-CONTEXT.md`
- `.planning/phases/00-branding-design-system/00-01-SUMMARY.md`
- `.planning/phases/00-branding-design-system/00-02-SUMMARY.md`
- `.planning/phases/00-branding-design-system/00-01-PLAN.md`
- `.planning/phases/00-branding-design-system/00-02-PLAN.md`
- `brand/tokens.css`
- `brand/tailwind.preset.ts`
- `brand/BRAND.md`
- `brand/VOICE.md`
- `brand/README.md`
- `brand/tests/assets.test.js`
- `brand/tests/tokens.test.js`
- `brand/assets/` (25 PNG inventory via test + glob)
- `.planning/sketches/003-apollo-asset-pack/KIT.md` (canonical asset cross-check)
- `.planning/sketches/themes/default.css` (sketch vs shipped token diff)
- `.planning/sketches/001-brand-mood-board/index.html` (sketch-only visual reference)
