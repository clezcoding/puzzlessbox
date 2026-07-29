# Puzzlessbox — Brand Bible

**Version:** 1.0  
**Date:** 2026-07-29  
**Status:** locked

---

## North Star

Everything brand-facing derives from **Apollo** — the raccoon mascot and sole brand hero. Logo, favicon, app icon, empty states, loading, OG/social, marketing, onboarding, error humor, and microcopy tone all flow from this character. No parallel abstract mark system. Apollo *is* the brand.

**Myth thread:** Apollo ↔ Hermes (messenger) — brand personality rides with the capture channel.

**Reversibility (D-01):** Costly. All assets and voice assume Apollo. Reverting to an abstract mark would invalidate the entire asset library and voice system.

---

## Identity — Apollo (D-01)

| Trait | Spec |
|---|---|
| Name | **Apollo** (user-facing). Myth: companion of Hermes — fits Hermes capture channel |
| Species | Raccoon (Waschbär) |
| Pose | Upright, hands on hips, confident / mischievous |
| Prop | Open box worn as backpack — Capture-Flow metaphor |
| Cargo | Puzzle pieces + gears (organize chaos) |
| Accent prop | Terracotta / burnt-orange bandana (`#c45c3e`) |
| Style | Clean modern flat illustration · charcoal outlines · soft fills |
| Age vibe | Adult indie — clever, not cute-baby |

Apollo leads all brand-facing moments: face, terracotta accent, voice, illustration continuity. The entire product identity rests on this character — "ALLES auf den Waschbär."

---

## UI Scaffold DNA (D-02)

**Utilitarian Bone** workbench — warm bone board, charcoal CTA, hairline columns, quiet motion.

| Element | Spec |
|---|---|
| Background | Warm bone paper (`#f7f6f3`) |
| CTA | Charcoal (`#1a1a1a`) — primary actions |
| Typography | Instrument Serif (display) + DM Sans (UI/body) |
| Layout | Hairline columns, structure from rules/spacing — not heavy chrome |
| Motion | Quiet and brief — restrained entry, status, capture feedback |
| Brand accent | Terracotta `#c45c3e` (bandana) — **the** brand signal |
| Info accent | Teal `#1f6c9f` demoted to informational links only |

Utilitarian Bone stays the neutral scaffold. Terracotta = brand signal; teal = informational only. Category pastels must not compete with terracotta.

---

## Asset Policy (D-03, D-05)

**Keep-all Apollo asset pack** — ~25 transparent PNGs under `brand/assets/`.

| Policy | Detail |
|---|---|
| Canonical character ref | `brand/assets/apollo-avatar.png` |
| Phase 0 format | PNG kit only — no SVG vectorization |
| SVG deferral | Higgsfield Recraft credits unavailable (~0.89). After top-up: vectorize brand marks first (favicon, app icon, wordmark, avatar, dark icon) — pragmatic A1 path |
| Scene illustrations | Empty/OG/scene illustrations remain PNG unless later needed as SVG |
| Pending gens | `pose-wave`, `pose-sleep` blocked on HF credits |

Downstream agents generate or refine assets only with Apollo as reference. Tool bias: Nano Banana family for character continuity; Recraft only for simplified flat icon derivatives after pose lock.

---

## Palette

Locked hex values — must match `brand/tokens.css` exactly.

### Core Colors

| Token | Hex | Role |
|---|---|---|
| `--color-bg` | `#f7f6f3` | Bone paper — dominant (60%) |
| `--color-surface` | `#ffffff` | Cards / panels — secondary (30%) |
| `--color-text` | `#2f3437` | Body ink |
| `--color-primary` | `#1a1a1a` | CTA / raccoon charcoal |
| `--color-brand` | `#c45c3e` | Bandana terracotta — **brand accent** (10%) |
| `--color-brand-soft` | `#fce8e0` | Soft brand wash |
| `--color-cardboard` | `#c9a07a` | Box / warm secondary |
| `--color-muted` | `#787774` | Secondary text |
| `--color-border` | `#eaeaea` | Hairlines |
| `--color-destructive` | `#d9383a` | Destructive actions, delete buttons |
| `--color-info` | `#1f6c9f` | Informational links only (not brand) |

### Category Pastels (D-07)

Soft util tints — must not compete with terracotta brand signal.

| Category | Soft bg | Accent |
|---|---|---|
| Inbox | `#f0eeea` | `#787774` |
| Notizen | `#f5f0e6` | `#b8956a` |
| Links | `#e8f0f5` | `#5a7a8f` |
| Tasks | `#eaf3ec` | `#5f7d64` |
| Termine | `#f5ebe8` | `#c45c3e` |

**Note:** Termine accent deliberately reuses brand terracotta as capture-signal. Category pastels provide wayfinding only — terracotta remains the sole brand accent.

---

## Typography

| Role | Family | Usage |
|---|---|---|
| Display / masthead | Instrument Serif | Headlines, hero text, brand moments |
| UI / body | DM Sans | All interface copy, labels, buttons |
| Mono (rare) | JetBrains Mono | Timestamps, IDs, compact system metadata |

**Rationale:** Serif warmth + sans clarity + mono precision. Type pairing locked — do not substitute.

| Role | Size | Weight | Line Height |
|---|---|---|---|
| Body | 16px | 400 | 1.5 |
| Label | 14px | 600 | 1.4 |
| Heading | 20px | 600 | 1.2 |
| Display | 28px | 400 | 1.2 |

---

## Spacing

4/8px base rhythm — all values multiples of 4:

| Token | Value | Usage |
|---|---|---|
| xs | 4px | Icon gaps, inline padding |
| sm | 8px | Compact element spacing |
| md | 16px | Default element spacing |
| lg | 24px | Section padding |
| xl | 32px | Layout gaps |
| 2xl | 48px | Major section breaks |
| 3xl | 64px | Page-level spacing |

Structure from rules, columns, spacing — not from heavy chrome.

---

## Shape + Motion

| Property | Spec |
|---|---|
| Border radius | Small radii — subtle, not pill-shaped |
| Borders | Hairline (`#eaeaea` light / `#2d2d2d` dark) |
| Shadows | Minimal — prefer borders and spacing for depth |
| Motion | Quiet and brief — restrained entry, status, capture feedback |
| Reduced motion | Always support `prefers-reduced-motion` — disable or shorten animations |

---

## Brand Relationship

| Layer | Role |
|---|---|
| Apollo (identity) | Face, terracotta accent, voice, illustration continuity |
| Utilitarian Bone (scaffold) | Neutral layout DNA — bone board, hairline columns, charcoal CTA |
| Terracotta `#c45c3e` | Brand signal — bandana, primary CTA, capture confirmation, active highlights |
| Teal `#1f6c9f` | Informational only — never brand accent |
| Category pastels | Wayfinding — must not compete with terracotta |

---

## Rejected Marks (Do Not Regenerate)

| Direction | Rejection Reason |
|---|---|
| Lettermark | Flat util lettermarks compete with Apollo as sole identity |
| Seal | Seal/badge marks create parallel abstract logo system |
| Grid | Grid-based marks feel corporate, not indie-clever |
| Box-Buddy | Soft-clay Box-Buddy too cute-baby — conflicts with adult indie tone |
| Cool-P | Cool abstract P+box SaaS mark is generic startup — no character DNA |

Also rejected as default UI: neon glass, phosphor terminal, carnival warm.

---

## Icon / Illustration Style

| Property | Spec |
|---|---|
| Format (Phase 0) | Transparent PNG only — no flat vector icon set |
| Character DNA | Bandana terracotta `#c45c3e`, warm bone surfaces, charcoal outlines, soft fills |
| Asset inventory | `apollo-empty-*`, `apollo-error`, `apollo-splash`, `apollo-404`, `apollo-offline`, `apollo-loading`, `apollo-capture`, `apollo-onboard`, `apollo-og`, etc. |
| Consistency rule | All poses share Apollo character DNA — upright raccoon, box backpack, puzzle/gear cargo |
| Dark mode scenes | Do **not** regenerate scene illustrations for dark (D-08). Place existing light PNGs on dark surfaces with clean bounding boxes/borders via CSS |
| Future icons (Phase 4) | Must match this style without look-drift — read this bible before generating |

---

## Voice / Tone (D-09)

Apollo spricht clever, trocken, einfallsreich — wie das verschmitzte Waschbär-Grinsen.

| Principle | Rule |
|---|---|
| Tone | Clever, dry, resourceful |
| Capture verbs | Light — gefangen, gestasht, sortiert, stibitzt |
| Length | Short confirms, no corporate fluff |
| Never | Baby talk, meme spam, AI-slop |

Full microcopy examples with 8 locked German strings: see [`brand/VOICE.md`](./VOICE.md).

---

## Dark Mode (D-08)

| Property | Spec |
|---|---|
| Token parity | Full dark-theme via `[data-theme=dark]` / `@theme dark` in `brand/tokens.css` |
| Dark icon | `brand/assets/apollo-icon-dark.png` included in asset pack |
| Scene illustrations | **Not** regenerated for dark — place existing light PNGs on dark surfaces |
| Category dark | Background tokens shift; accent hex values unchanged |
| Bone↔charcoal | Light bone `#f7f6f3` inverts to charcoal `#1a1a1a` — WCAG-minded readability |

No dark UI screens built in Phase 0 — token parity only.

---

## Downstream Consumption

| Consumer | Integration |
|---|---|
| Next.js 16 | `@import "../brand/tokens.css"` + `brand/tailwind.preset.ts` |
| `/gsd-ui-phase 4` | Read this bible before generating any new UI asset |
| LLM capture agents | Read `brand/VOICE.md` before writing user-facing strings |
| Asset generation | Apollo as sole reference — no rejected marks, no look-drift |

---

*Puzzlessbox Brand Bible v1.0 — locked 2026-07-29*
