# UI Foundation

## Design Decisions

- Use Sketch 001-C, Utilitarian Bone, as interface scaffold: warm bone page, white working surfaces, charcoal controls, hairline divisions, small radii, minimal shadow.
- Keep hierarchy editorial but practical: Instrument Serif masthead over DM Sans interface text. Reserve JetBrains Mono for timestamps, IDs, counts, and system state.
- Follow a 4/8px spacing rhythm. Core steps are 4, 8, 12, 16, 24, 32, and 48px.
- Show capture state above the board in a live rail. Product sequence is capture → confirm → auto-save → categorized board.
- Use five semantic columns: Inbox, Notizen, Links, Tasks, Termine. Keep category colors soft so terracotta remains the brand signal.
- Use restrained motion for entry, status, and capture landing. Hairlines and spacing carry structure; shadows do not.

## CSS Patterns

Use the Utilitarian Bone variables from the winning theme:

```css
[data-theme="util"] {
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
  --color-info: #1f6c9f;
  --font-display: 'Instrument Serif', Georgia, serif;
  --font-sans: 'DM Sans', system-ui, sans-serif;
  --radius-sm: 4px;
  --radius-md: 8px;
  --radius-lg: 10px;
  --shadow-sm: 0 0 0 transparent;
  --shadow-md: 0 2px 8px rgba(0, 0, 0, 0.04);
  --shadow-lg: 0 4px 16px rgba(0, 0, 0, 0.05);
}
```

Build masthead with one hairline and flexible controls:

```css
.masthead {
  margin-bottom: 28px;
  padding-bottom: 20px;
  border-bottom: 1px solid var(--color-border);
}

.masthead h1 {
  margin: 0;
  max-width: 16ch;
  font: 400 clamp(2rem, 4vw, 2.75rem)/1.1 var(--font-display);
  letter-spacing: -0.03em;
}

.masthead .bar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  flex-wrap: wrap;
  margin-top: 20px;
}
```

Preserve continuous five-column workbench:

```css
.board {
  display: grid;
  grid-template-columns: repeat(5, minmax(200px, 1fr));
  gap: 0;
  overflow-x: auto;
  border: 1px solid var(--color-border);
  border-radius: 10px;
}

.col {
  min-height: 480px;
  padding: 10px;
  background: var(--color-surface);
  border-right: 1px solid var(--color-border);
}

.col:last-child {
  border-right: 0;
}

@media (max-width: 980px) {
  .board { grid-template-columns: repeat(5, 230px); }
}
```

Keep cards quiet and information-dense:

```css
.card {
  overflow: hidden;
  background: #fff;
  border: 1px solid color-mix(in srgb, var(--card-accent, #eaeaea) 28%, #eaeaea);
  border-radius: 8px;
  box-shadow: none;
}

.card-accent {
  height: 2px;
  opacity: 0.7;
  background: linear-gradient(90deg, var(--card-accent), transparent 90%);
}

@media (hover: hover) and (pointer: fine) {
  .card:hover {
    transform: translateY(-1px);
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04);
  }
}

@media (prefers-reduced-motion: reduce) {
  *, *::before, *::after {
    animation-duration: 0.01ms !important;
    animation-iteration-count: 1 !important;
    transition-duration: 0.01ms !important;
  }
}
```

Responsive rule: retain semantic columns and allow horizontal board scrolling below desktop width. Let masthead controls wrap. Never squeeze five columns into unreadable slivers.

## HTML Structures

Masthead and live capture rail:

```html
<header class="masthead">
  <p class="kicker">Workbench · Capture Board</p>
  <h1>Puzzlessbox</h1>
  <div class="rule" aria-hidden="true"></div>
  <p class="deck">Nachrichten landen kategorisiert.</p>
  <div class="bar">
    <div class="meta-row" aria-label="Capture status"></div>
    <div class="actions"></div>
  </div>
</header>

<section class="util-rail" aria-label="Live capture">
  <h2>Live · zuletzt erfasst</h2>
  <div class="feed" aria-live="polite"></div>
</section>
```

Semantic board and cards:

```html
<main>
  <div class="board" aria-label="Categorized capture board">
    <section class="col" data-col="inbox">
      <header class="col-h">
        <h2>Inbox</h2>
        <span data-count>0</span>
      </header>
      <div class="cards">
        <article class="card">
          <div class="card-accent" aria-hidden="true"></div>
          <div class="card-body">
            <header class="card-top"></header>
            <h3>Capture title</h3>
            <p>Capture detail</p>
            <div class="meta"></div>
          </div>
        </article>
      </div>
    </section>
    <!-- Repeat for Notizen, Links, Tasks, Termine. -->
  </div>
</main>
```

Use real buttons for actions, semantic headings, visible focus states, and `aria-live="polite"` only for meaningful status updates.

## What to Avoid

- Phosphor terminal, neon glass, and high-contrast hacker chrome as default UI.
- Soft Dock mesh washes, rose signal color, oversized rounding, and floating bottom dock as core scaffold.
- Carnival warmth, heavy gradients, thick borders, large shadows, or motion that competes with captured content.
- Teal as brand accent. It is optional informational color; terracotta owns brand signaling.
- Mono typography across entire interface, decorative emoji replacing accessible icons, or five columns compressed below readable width.

## Origin

Synthesized from sketch: 001-brand-mood-board, winner C.

Source files:
- `sources/001-brand-mood-board/index.html`
- `sources/themes/default.css`

Canonical originals:
- `.planning/sketches/001-brand-mood-board/index.html`
- `.planning/sketches/themes/default.css`
