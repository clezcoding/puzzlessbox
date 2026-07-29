# Phase 00: Branding & Design System - Pattern Map

**Mapped:** 2026-07-29  
**Files analyzed:** 7  
**Analogs found:** 4 / 7  

## File Classification

| New/Modified File | Role | Data Flow | Closest Analog | Match Quality |
|-------------------|------|-----------|----------------|---------------|
| `brand/assets/` | asset | file-I/O | `.planning/sketches/003-apollo-asset-pack/assets/` | exact |
| `brand/BRAND.md` | documentation | static | `.planning/sketches/BRAND.md` | exact |
| `brand/VOICE.md` | documentation | static | `.planning/sketches/BRAND.md` (Voice section) | partial |
| `brand/tokens.css` | config | static | `.planning/sketches/themes/default.css` | exact |
| `brand/tailwind.preset.ts` | config | transform | none (greenfield) | none |
| `brand/tests/assets.test.js` | test | batch | none (greenfield) | none |
| `brand/tests/tokens.test.js` | test | batch | none (greenfield) | none |

---

## Pattern Assignments

### `brand/assets/` (asset, file-I/O)

**Analog:** `.planning/sketches/003-apollo-asset-pack/assets/`

**Promotion pattern:** Copy all 25 canonical transparent PNG assets from sketch folder directly to production asset folder.

**Asset list to promote:**
```
apollo-icon-app.png
apollo-icon-favicon.png
apollo-wordmark.png
apollo-empty-inbox.png
apollo-empty-board.png
apollo-empty-caught.png
apollo-og.png
apollo-splash.png
apollo-loading.png
apollo-error.png
apollo-404.png
apollo-offline.png
apollo-capture.png
apollo-avatar.png
apollo-empty-notes.png
apollo-empty-links.png
apollo-empty-tasks.png
apollo-empty-cal.png
apollo-onboard.png
apollo-pose-think.png
apollo-pattern.png
apollo-email-header.png
apollo-icon-dark.png
apollo-stickers.png
apollo-notify.png
```

---

### `brand/BRAND.md` (documentation, static)

**Analog:** `.planning/sketches/BRAND.md`

**Promotion pattern:** Promote the brand identity bible. Retain character definitions, color palette, typography, and UI relationship rules.

---

### `brand/VOICE.md` (documentation, static)

**Analog:** `.planning/sketches/BRAND.md` (lines 53-59) & `.planning/phases/00-branding-design-system/00-UI-SPEC.md` (lines 82-92)

**Voice pattern:** German voice guidelines with 8 concrete microcopy examples. Tone: clever, dry, resourceful. No baby talk or meme spam.

**Microcopy Examples:**
1. **Empty State (Inbox):** "Hier ist gähnende Leere. Apollo hat noch nichts gefangen."
2. **Empty State (Notizen):** "Keine Notizen stasht sich von selbst. Lass Apollo etwas aufschreiben."
3. **Capture Success:** "Eintrag gesichert. Apollo hat es stibitzt und sortiert."
4. **Error State:** "Da ist wohl ein Zahnrad blockiert. Versuche es gleich noch einmal."
5. **Offline State:** "Keine Verbindung. Apollo sucht nach dem Signal..."
6. **Destructive Confirmation:** "Löschen: Eintrag unwiderruflich löschen? Apollo kann ihn nicht wiederbeschaffen."
7. **Onboarding Welcome:** "Hallo, ich bin Apollo. Lass uns das Chaos ordnen."
8. **Capture Input Placeholder:** "Sende eine Nachricht, um den ersten Eintrag zu stashen..."

---

### `brand/tokens.css` (config, static)

**Analog:** `.planning/sketches/themes/default.css` (lines 112-147)

**Tailwind v4 CSS-First Customization pattern:** Map custom properties inside `@theme` blocks.

**Light mode variables** (adapted from `default.css` `[data-theme="util"]`):
```css
@theme {
  --color-bg: #f7f6f3;
  --color-bg-wash: #fbfbfa;
  --color-surface: #ffffff;
  --color-surface-soft: #f9f9f8;
  --color-border: #eaeaea;
  --color-border-strong: #d6d6d4;
  --color-text: #2f3437;
  --color-text-muted: #787774;
  --color-primary: #1a1a1a;
  --color-primary-hover: #333333;
  --color-signal: #c45c3e;
  --color-brand: #c45c3e;
  --color-brand-soft: #fce8e0;
  --color-cardboard: #c9a07a;
  --color-accent: #c45c3e;
  --color-accent-soft: #fce8e0;
  --color-info: #1f6c9f;
  --color-info-soft: #e1f3fe;
  --color-ink-bar: #1a1a1a;

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
  --font-serif: 'Instrument Serif', Georgia, serif;
  --font-sans: 'DM Sans', system-ui, sans-serif;
  --font-mono: 'JetBrains Mono', ui-monospace, monospace;
}
```

**Dark mode overrides** (WCAG bone↔charcoal inversion):
```css
@theme dark {
  --color-bg: #1a1a1a;
  --color-bg-wash: #121212;
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

---

### `brand/tailwind.preset.ts` (config, transform)

**Analog:** none (greenfield)

**Preset pattern:** Tailwind v4 is CSS-first. This file provides a simple TypeScript export of the theme or compatibility config for Next.js build integration.

```typescript
import type { Config } from 'tailwindcss';

export default {
  theme: {
    extend: {
      colors: {
        bg: 'var(--color-bg)',
        surface: 'var(--color-surface)',
        brand: 'var(--color-brand)',
        inbox: {
          bg: 'var(--color-inbox-bg)',
          accent: 'var(--color-inbox-accent)',
        },
        notes: {
          bg: 'var(--color-notes-bg)',
          accent: 'var(--color-notes-accent)',
        },
        links: {
          bg: 'var(--color-links-bg)',
          accent: 'var(--color-links-accent)',
        },
        tasks: {
          bg: 'var(--color-tasks-bg)',
          accent: 'var(--color-tasks-accent)',
        },
        termine: {
          bg: 'var(--color-termine-bg)',
          accent: 'var(--color-termine-accent)',
        },
      },
      fontFamily: {
        display: ['var(--font-display)', 'serif'],
        sans: ['var(--font-sans)', 'sans-serif'],
        mono: ['var(--font-mono)', 'monospace'],
      },
    },
  },
} satisfies Config;
```

---

### `brand/tests/assets.test.js` (test, batch)

**Analog:** none (greenfield)

**Node.js native test runner pattern:** Validate existence and readability of promoted PNG assets.

```javascript
import test from 'node:test';
import assert from 'node:assert';
import fs from 'node:fs';
import path from 'node:path';

const assetsDir = path.resolve('brand/assets');
const expectedAssets = [
  'apollo-icon-app.png',
  'apollo-icon-favicon.png',
  'apollo-wordmark.png',
  'apollo-empty-inbox.png',
  'apollo-empty-board.png',
  'apollo-empty-caught.png',
  'apollo-og.png',
  'apollo-splash.png',
  'apollo-loading.png',
  'apollo-error.png',
  'apollo-404.png',
  'apollo-offline.png',
  'apollo-capture.png',
  'apollo-avatar.png',
  'apollo-empty-notes.png',
  'apollo-empty-links.png',
  'apollo-empty-tasks.png',
  'apollo-empty-cal.png',
  'apollo-onboard.png',
  'apollo-pose-think.png',
  'apollo-pattern.png',
  'apollo-email-header.png',
  'apollo-icon-dark.png',
  'apollo-stickers.png',
  'apollo-notify.png'
];

test('validate canonical PNG illustrations exist', () => {
  for (const asset of expectedAssets) {
    const filePath = path.join(assetsDir, asset);
    assert.ok(fs.existsSync(filePath), `Asset missing: ${asset}`);
    const stats = fs.statSync(filePath);
    assert.ok(stats.size > 0, `Asset is empty: ${asset}`);
  }
});
```

---

### `brand/tests/tokens.test.js` (test, batch)

**Analog:** none (greenfield)

**Node.js native test runner pattern:** Parse `brand/tokens.css` and assert the presence of required CSS variables.

```javascript
import test from 'node:test';
import assert from 'node:assert';
import fs from 'node:fs';
import path from 'node:path';

const tokensPath = path.resolve('brand/tokens.css');

test('validate CSS tokens file exists and contains required variables', () => {
  assert.ok(fs.existsSync(tokensPath), 'tokens.css file missing');
  const content = fs.readFileSync(tokensPath, 'utf8');

  const requiredVariables = [
    '--color-bg',
    '--color-surface',
    '--color-brand',
    '--color-inbox-bg',
    '--color-notes-bg',
    '--color-links-bg',
    '--color-tasks-bg',
    '--color-termine-bg',
    '--font-display',
    '--font-sans'
  ];

  for (const variable of requiredVariables) {
    assert.ok(content.includes(variable), `CSS variable missing: ${variable}`);
  }
});
```

---

## Shared Patterns

### CSS custom properties & theme injection
**Source:** `brand/tokens.css`  
**Apply to:** Future WebApp global stylesheet.
```css
@import "tailwindcss";
@import "../brand/tokens.css";
```

### German voice guidelines
**Source:** `brand/VOICE.md`  
**Apply to:** Future WebApp UI copy, notifications, and LLM capture agent responses.

---

## Metadata

**Analog search scope:** `.planning/sketches/`  
**Files scanned:** 5  
**Pattern extraction date:** 2026-07-29  
