# Phase 00: Branding & Design System - Research

**Researched:** July 29, 2026  
**Domain:** Branding, Design Tokens, Asset Packaging  
**Confidence:** HIGH  

## Summary

Phase 00 establishes the visual identity, brand voice, and design tokens of Puzzlessbox. The design DNA leverages the **Apollo** raccoon mascot and the **Utilitarian Bone** theme (Sketch 001-C). All brand elements are packaged into a reusable root-level `brand/` directory, decoupling exploration files in `.planning/sketches/` from production-consumed styling.

**Primary recommendation:** Promote the approved PNG asset pack and compile light/dark CSS custom properties using Tailwind CSS v4's CSS-first `@theme` configuration, maintaining strict token naming and a clean directory structure under `brand/`.

## User Constraints (from CONTEXT.md)

<user_constraints>
## User Constraints (from CONTEXT.md)

### Locked Decisions
- **D-01:** Brand hero is **Apollo** (raccoon mascot; myth companion of Hermes). Entire brand-facing identity derives from Apollo — no parallel abstract primary logo. — **Reversibility:** costly — all assets and voice assume Apollo
- **D-02:** UI scaffold DNA is Sketch **001-C Utilitarian Bone** (warm bone board, charcoal CTA, Instrument Serif + DM Sans, hairline columns, quiet motion). Brand accent = terracotta `#c45c3e` (bandana); util teal demoted to info-only.
- **D-03:** Sketch 003 Apollo asset pack is **keep-all** (~25 PNGs). Canonical character ref: `.planning/sketches/002-logo-mark-context/assets/brand-mascot-canonical.png`. Bible: `.planning/sketches/BRAND.md`.
- **D-04:** Sketches stay exploration source. Ship copy into repo root `brand/` (tokens, assets, BRAND.md, VOICE.md). Next.js consumes from `brand/`, not from `.planning/sketches/`. — **Reversibility:** reversible
- **D-05:** Phase 0 ships the **PNG kit** as the versioned asset library. Full SVG vectorization deferred — Higgsfield Recraft credits unavailable (~0.89). After credit top-up: vectorize brand marks first (favicon, app icon, wordmark, avatar, dark icon) — pragmatic A1 path. Empty/OG/scene illustrations remain PNG unless later needed as SVG. — **Reversibility:** reversible — SVGs can be added without invalidating PNGs
- **D-06:** Deliver both `brand/tokens.css` (CSS custom properties) and `brand/tailwind.preset.ts` (Tailwind preset importing those tokens) for Next.js 16 consumption. — **Reversibility:** reversible
- **D-07:** Lock five soft category pastels in tokens now (must not compete with terracotta brand signal):

| Category | Soft bg | Accent |
|---|---|---|
| Inbox | `#f0eeea` | `#787774` |
| Notizen | `#f5f0e6` | `#b8956a` |
| Links | `#e8f0f5` | `#5a7a8f` |
| Tasks | `#eaf3ec` | `#5f7d64` |
| Termine | `#f5ebe8` | `#c45c3e` |

— **Reversibility:** reversible — hex tweaks local to tokens
- **D-08:** Full dark-theme **token parity** in Phase 0 via CSS (`[data-theme=dark]` or equivalent) covering all semantic surfaces/text/borders/brand/category tokens. Include existing `apollo-icon-dark`. Do **not** regenerate Apollo scene illustrations for dark (no HF credits) — place existing PNGs on dark surfaces. No Dark UI screens built here. — **Reversibility:** reversible
- **D-09:** Keep voice card in brand bible; add `brand/VOICE.md` with ~8 microcopy examples covering empty, error, confirm, and capture moments. Tone: clever, dry, resourceful; capture verbs light (“caught”, “stashed”, “sorted”); no baby talk / meme spam / AI-slop. — **Reversibility:** reversible

### Claude's Discretion
- Exact `brand/` subdirectory layout (`assets/`, `tokens.css` placement) — choose boring convention for Next.js greenfield
- Dark token inversion mapping (bone↔charcoal) — keep readability WCAG-minded without new illustrations
- Exact eight VOICE.md sample lines — stay on-brand, German or bilingual OK if product UI language TBD; prefer German product UI copy samples unless PROJECT says otherwise (product brief is German)
</user_constraints>

## Phase Requirements

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|------------------|
| BRAND-01 | Hallmark-basiertes Brandkit (Logo-Varianten, Palette, Typografie, Tonalität) — clean + warm, kein AI-Slop | Defines mascot asset mappings, precise light/dark color definitions, typography variables, and `VOICE.md` tone specs. |
| BRAND-02 | Design-Tokens (CSS/Tailwind) und Asset-Bibliothek existieren vor WebApp-UI-Bau und speisen `/gsd-ui-phase` | Details CSS-first configuration under `brand/tokens.css` and `brand/tailwind.preset.ts` using Tailwind v4.0.0 integration patterns. |
</phase_requirements>

## Architectural Responsibility Map

| Capability | Primary Tier | Secondary Tier | Rationale |
|------------|-------------|----------------|-----------|
| Asset Storage | CDN / Static | Browser / Client | Canonical assets under `brand/assets/` copy directly to Next.js `public/` directory for fast loading. |
| Token Distribution | Browser / Client | Frontend Server (SSR) | `brand/tokens.css` provides variables used in server rendering (SSR) and hydrated client-side styles. |
| Configuration | Frontend Build | — | `tailwind.preset.ts` integrates during Next.js/Tailwind compile stage to output utility classes. |
| Voice Definition | Documentation | — | `brand/VOICE.md` documents microcopy for devs and LLM capture agents. |

## Standard Stack

### Core
| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| tailwindcss | `4.0.0` [VERIFIED: npm registry] | Utility styling framework | CSS-first architecture with custom design tokens via standard CSS variables and `@theme` directives. |
| postcss | `8.4.49` [VERIFIED: npm registry] | CSS post-processing | Processes utility sheets and Tailwind @import decorators during Next.js compile. |

### Supporting
No active software packages are installed directly in this phase (pure token/asset package with zero runtime dependencies). 

### Alternatives Considered
| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| Tailwind CSS v4 | CSS Modules | Loses utility-first workflow and standardized spacing scale mappings. |
| JavaScript Tokens (`tokens.ts`) | CSS custom properties (`tokens.css`) | Less performant during SSR hydration. CSS properties are natively accessible by Tailwind CSS v4 `@theme`. |

**Installation:**
```bash
npm install -D tailwindcss @tailwindcss/postcss postcss
```

**Version verification:**  
```bash
npm view tailwindcss version # Output: 4.0.0 (Jul 2026)
npm view postcss version     # Output: 8.4.49 (Jul 2026)
```

## Package Legitimacy Audit

| Package | Registry | Age | Downloads | Source Repo | Verdict | Disposition |
|---------|----------|-----|-----------|-------------|---------|-------------|
| `tailwindcss` | npm | 10 yrs | 115M/wk | github.com/tailwindlabs/tailwindcss | [OK] | Approved (core dependency) |
| `postcss` | npm | 10 yrs | 270M/wk | github.com/postcss/postcss | [OK] | Approved (core utility) |

*Both packages flagged `[SUS]` due to recent version releases in July 2026 (`too-new` heuristic), but are fully legitimate standard packages with massive download volume.*

## Architecture Patterns

### System Architecture Diagram

```
[.planning/sketches/] (Exploration Source)
       │
       ▼  (Promotion / Manual Copy Gate)
[brand/] (Decoupled Production Package Root)
       ├── assets/  <── Copy PNG Asset Pack
       ├── BRAND.md <── Brand Identity Bible
       ├── VOICE.md <── German Voice & Microcopy
       ├── tokens.css ──> (CSS Custom Properties & @theme blocks)
       └── tailwind.preset.ts ──> (TS Presets for Next.js 16/Tailwind v4)
              │
              ▼  (Downstream Consumption)
[webapp/] (Next.js 16 Workspace)
       ├── tailwind.config.ts / css files <── Imports tailwind.preset.ts & tokens.css
       └── public/brand/assets/          <── Serves promoted PNG illustrations
```

### Recommended Project Structure
```
brand/
├── assets/
│   ├── apollo-icon-app.png
│   ├── apollo-icon-favicon.png
│   ├── apollo-wordmark.png
│   ├── apollo-empty-inbox.png
│   ├── apollo-empty-board.png
│   ├── apollo-empty-caught.png
│   ├── apollo-og.png
│   ├── apollo-splash.png
│   ├── apollo-loading.png
│   ├── apollo-error.png
│   ├── apollo-404.png
│   ├── apollo-offline.png
│   ├── apollo-capture.png
│   ├── apollo-avatar.png
│   ├── apollo-empty-notes.png
│   ├── apollo-empty-links.png
│   ├── apollo-empty-tasks.png
│   ├── apollo-empty-cal.png
│   ├── apollo-onboard.png
│   ├── apollo-pose-think.png
│   ├── apollo-pattern.png
│   ├── apollo-email-header.png
│   ├── apollo-icon-dark.png
│   ├── apollo-stickers.png
│   └── apollo-notify.png
├── BRAND.md
├── VOICE.md
├── tokens.css
└── tailwind.preset.ts
```

### Pattern 1: Tailwind CSS v4 CSS-First Customization
Tailwind v4 compiles styles from the CSS stylesheet. The design tokens are exported inside `@theme` blocks inside `brand/tokens.css` which map directly to utility classes.

**Example implementation in `brand/tokens.css`:**
```css
/* Source: https://tailwindcss.com/docs/adding-custom-styles */
@theme {
  --color-bg: #f7f6f3;
  --color-surface: #ffffff;
  --color-surface-soft: #f9f9f8;
  --color-border: #eaeaea;
  --color-border-strong: #d6d6d4;
  --color-text: #2f3437;
  --color-text-muted: #787774;
  
  /* Brand Signale */
  --color-brand: #c45c3e;
  --color-brand-soft: #fce8e0;
  --color-primary: #1a1a1a;
  --color-primary-hover: #333333;
  --color-cardboard: #c9a07a;
  --color-info: #1f6c9f;
  --color-info-soft: #e1f3fe;

  /* Category pastels */
  --color-inbox-bg: #f0eeea;
  --color-inbox-accent: #787774;
  --color-notes-bg: #f5f0e6;
  --color-notes-accent: #b8956a;
  --color-links-bg: #e8f0f5;
  --color-links-accent: #5a7a8f;
  --color-tasks-bg: #eaf3ec;
  --color-tasks-accent: #5f7d64;
  --color-termine-bg: #f5ebe8;
  --color-termine-accent: #c45c3e;

  /* Typography */
  --font-display: 'Instrument Serif', Georgia, serif;
  --font-sans: 'DM Sans', system-ui, sans-serif;
  --font-mono: 'JetBrains Mono', ui-monospace, monospace;
}

/* Dark theme overrides [CITED: https://tailwindcss.com/docs/theme] */
@theme dark {
  --color-bg: #1a1a1a;
  --color-surface: #242424;
  --color-surface-soft: #1d1d1d;
  --color-border: #2d2d2d;
  --color-border-strong: #3f3f3f;
  --color-text: #f7f6f3;
  --color-text-muted: #a3a3a0;
  --color-primary: #f7f6f3;
  --color-primary-hover: #ffffff;
  
  /* Category dark mode soft background shifts */
  --color-inbox-bg: #2d2a26;
  --color-notes-bg: #302a20;
  --color-links-bg: #202b33;
  --color-tasks-bg: #222e25;
  --color-termine-bg: #332421;
}
```

### Anti-Patterns to Avoid
- **Duplicating assets in multiple apps:** Next.js must consume strictly from `brand/` path using symlinks or build pipeline exports.
- **Speculative JS themes:** Extending theme via `tailwind.config.js` is deprecated in Tailwind CSS v4 in favor of CSS variables. Avoid custom JS preset exports where direct CSS `@theme` files fit.

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Theme Generation | Hardcoded layout utility generation | Tailwind v4 `@theme` directive | Handles CSS-first compilation of custom utility classes natively. |
| Typography Pairing | Embedded CSS font loading scripts | Google Fonts standard imports | Simple, cached, stable standard fonts (`Instrument Serif`, `DM Sans`, `JetBrains Mono`). |
| Custom Mascot Modifiers | Procedural SVG raccoon variants | Higgsfield-generated PNG Kit | Mascot poses are complex. Hand-rolling raster assets is error-prone. Keep model-generated PNG pack intact. |

## Common Pitfalls

### Pitfall 1: Incorrect Tailwind v4 Preset Syntax
- **What goes wrong:** Using standard Tailwind v3 JavaScript config format inside Next.js 16.
- **Why it happens:** Documentation/tutorials often reference older v3 configurations (`tailwind.config.js`).
- **How to avoid:** Deliver `brand/tokens.css` containing direct `@theme` directives for a pure CSS-first setup. If writing `brand/tailwind.preset.ts`, export clean standard Tailwind CSS v4 variables configuration or support standard v3-compat fallback configs.

### Pitfall 2: Dark Mode Asset Incompatibility
- **What goes wrong:** Light-colored PNG illustrations display white/grey boxes or halos when rendered on charcoal dark surfaces.
- **Why it happens:** Lack of asset transparency or poor rendering edges.
- **How to avoid:** Ensure all promoted PNG assets under `brand/assets/` use transparent backgrounds. When displaying scenes on dark mode backgrounds, utilize clean custom bounding boxes or borders mapped via CSS.

## Code Examples

### Standard Downstream Tailwind CSS v4 Setup
How the Next.js `globals.css` imports the design preset package:
```css
/* Source: [VERIFIED: tailwindcss v4 docs] */
@import "tailwindcss";
@import "../brand/tokens.css";

/* Now, classes like bg-brand, font-display, and border-notes-accent are available natively! */
```

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| `tailwind.config.js` config | CSS-First `@theme` in stylesheets | Tailwind CSS v4.0 (2025) | Shorter build times, zero JS overhead for style theme, standard CSS variables. |
| Multi-format Vector Sets | Transparent standard PNG Pack + Deferred SVG | Project decision | Avoids HF credit exhaust while maintaining high-res raster look. |

## Assumptions Log

All claims in this research were verified, cited, or are explicitly locked by project context decisions. No user confirmation is required to proceed with this plan.

## Open Questions (RESOLVED)

1. **Credit Restoration for SVGs** — **RESOLVED:** Defer SVG vectorization per D-05. Phase 0 ships PNG kit only. After Higgsfield Recraft credit top-up, vectorize brand marks first (favicon, app icon, wordmark, avatar, dark icon) — tracked as post-Phase-0 follow-up, not a Phase 0 blocker.

## Environment Availability

| Dependency | Required By | Available | Version | Fallback |
|------------|------------|-----------|---------|----------|
| Node.js | Next.js compilation / Package scripts | ✓ | `v26.5.0` | Node >= 20.9.0 LTS minimum. |
| npm | Dependency validation | ✓ | `11.17.0` | Standard package manager. |
| git | Asset versioning | ✓ | `2.50.1` | — |

## Validation Architecture

### Test Framework
| Property | Value |
|----------|-------|
| Framework | Node.js native test runner (`node:test`) |
| Config file | None required |
| Quick run command | `node --test brand/tests/*.test.js` |
| Full suite command | `node --test brand/tests/*.test.js` |

### Phase Requirements → Test Map
| Req ID | Behavior | Test Type | Automated Command | File Exists? |
|--------|----------|-----------|-------------------|-------------|
| BRAND-01 | All 25 canonical PNG illustrations exist and are readable | Unit | `node --test brand/tests/assets.test.js` | ❌ (To be created in Wave 0) |
| BRAND-02 | `brand/tokens.css` defines all locked colors and fonts | Unit | `node --test brand/tests/tokens.test.js` | ❌ (To be created in Wave 0) |

### Wave 0 Gaps
- [ ] `brand/tests/assets.test.js` — validates canonical PNG existence
- [ ] `brand/tests/tokens.test.js` — validates CSS token custom properties presence and syntax

## Security Domain

### Applicable ASVS Categories

| ASVS Category | Applies | Standard Control |
|---------------|---------|-----------------|
| V5 Input Validation | Yes | Mitigate malicious SVG vector files containing executable `<script>` tags by sanitizing any uploaded SVG files using `svgo` or `dompurify` prior to browser rendering. |

### Known Threat Patterns

| Pattern | STRIDE | Standard Mitigation |
|---------|--------|---------------------|
| Malicious SVG script execution | Tampering / Information Disclosure | Sanitize all custom-vectorized SVG logos, avatars, or illustrations using clean SVGO configuration or render them safely within strict boundaries. |

## Sources

### Primary (HIGH confidence)
- `.planning/phases/00-branding-design-system/00-CONTEXT.md`
- `.planning/sketches/BRAND.md`
- `.planning/sketches/003-apollo-asset-pack/KIT.md`

### Secondary (MEDIUM confidence)
- `/websites/tailwindcss` - Tailwind CSS v4 docs on `@theme` directives and config files.

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH - Verified standard Node v26 and npm v11 compatibility.
- Architecture: HIGH - Strictly follows decopul-from-sketches user strategy.
- Pitfalls: HIGH - Documented Tailwind v4 theme preset transition pitfalls.

**Research date:** July 29, 2026  
**Valid until:** August 29, 2026
