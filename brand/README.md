# Puzzlessbox Brand Kit

Production brand package for Puzzlessbox — Apollo mascot assets, CSS design tokens, and a Tailwind v4 preset. Sketches under `.planning/sketches/` stay exploration-only; Next.js and other apps consume from `brand/`.

## Layout

```
brand/
├── assets/           # Canonical Apollo PNG illustrations (25 files)
├── tokens.css        # Light + dark @theme CSS custom properties
├── tailwind.preset.ts # Tailwind Config preset referencing CSS vars
├── tests/            # node:test validation (assets + tokens)
└── README.md
```

## Next.js consumption

**1. Import tokens in `globals.css`:**

```css
@import "tailwindcss";
@import "../brand/tokens.css";
```

**2. Extend Tailwind config with the preset** (when `webapp/` exists):

```typescript
import type { Config } from 'tailwindcss';
import brandPreset from '../brand/tailwind.preset';

export default {
  presets: [brandPreset],
} satisfies Config;
```

Utilities like `bg-brand`, `text-text`, `font-display`, and category pastels (`bg-inbox-bg`) compile from the CSS variables in `tokens.css`.

## SVG vectorization

Full SVG vectorization is deferred per D-05 (Higgsfield Recraft credits). Phase 0 ships the PNG kit only; SVGs can be added later without invalidating PNGs.

## Verification

```bash
node --test brand/tests/*.test.js
```
