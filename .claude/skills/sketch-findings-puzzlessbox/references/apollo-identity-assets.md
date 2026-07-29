# Apollo Identity & Assets

## Design Decisions

Apollo is Puzzlessbox's sole brand hero, not a secondary mascot. Myth: Apollo is Hermes' companion, connecting identity to the Hermes capture channel.

Locked character DNA:

- Clever adult raccoon, upright, hands on hips, slight confident/mischievous smirk.
- Open box worn as backpack: capture and collection metaphor.
- Puzzle pieces and gears in or above box: organized chaos.
- Terracotta/burnt-orange bandana and warm cardboard box.
- Clean modern flat illustration, charcoal outlines, soft fills, bone-friendly palette.
- Adult indie tone; never babyish, Disney-like, or generic SaaS.

Canonical source:

`.planning/sketches/002-logo-mark-context/assets/brand-mascot-canonical.png`

Continuity rule: every generated or refined Apollo image must use canonical PNG as visual reference. Preserve species, facial mask, proportions, smirk, upright posture, box-backpack, puzzle/gear cargo, bandana color, outline weight, and flat rendering. Do not invent a parallel abstract logo system.

Voice:

- Clever, dry, resourceful.
- Short confirmations without corporate filler.
- “caught”, “stashed”, and “sorted” can support capture language, but not every line.
- No baby talk, meme spam, or purple AI-slop.

Asset usage map:

| Surface | Canonical asset |
|---|---|
| App launcher | `.planning/sketches/003-apollo-asset-pack/assets/apollo-icon-app.png` |
| Browser favicon | `.planning/sketches/003-apollo-asset-pack/assets/apollo-icon-favicon.png` |
| Wordmark lockup | `.planning/sketches/003-apollo-asset-pack/assets/apollo-wordmark.png` |
| Inbox empty state | `.planning/sketches/003-apollo-asset-pack/assets/apollo-empty-inbox.png` |
| Board empty state | `.planning/sketches/003-apollo-asset-pack/assets/apollo-empty-board.png` |
| Caught-up state | `.planning/sketches/003-apollo-asset-pack/assets/apollo-empty-caught.png` |
| Social / OG | `.planning/sketches/003-apollo-asset-pack/assets/apollo-og.png` |
| Splash | `.planning/sketches/003-apollo-asset-pack/assets/apollo-splash.png` |
| Loading | `.planning/sketches/003-apollo-asset-pack/assets/apollo-loading.png` |
| Error | `.planning/sketches/003-apollo-asset-pack/assets/apollo-error.png` |
| 404 | `.planning/sketches/003-apollo-asset-pack/assets/apollo-404.png` |
| Offline | `.planning/sketches/003-apollo-asset-pack/assets/apollo-offline.png` |
| Capture confirmation | `.planning/sketches/003-apollo-asset-pack/assets/apollo-capture.png` |
| Avatar / settings | `.planning/sketches/003-apollo-asset-pack/assets/apollo-avatar.png` |
| Notes empty state | `.planning/sketches/003-apollo-asset-pack/assets/apollo-empty-notes.png` |
| Links empty state | `.planning/sketches/003-apollo-asset-pack/assets/apollo-empty-links.png` |
| Tasks empty state | `.planning/sketches/003-apollo-asset-pack/assets/apollo-empty-tasks.png` |
| Calendar empty state | `.planning/sketches/003-apollo-asset-pack/assets/apollo-empty-cal.png` |
| Onboarding | `.planning/sketches/003-apollo-asset-pack/assets/apollo-onboard.png` |
| Thinking state | `.planning/sketches/003-apollo-asset-pack/assets/apollo-pose-think.png` |
| Pattern | `.planning/sketches/003-apollo-asset-pack/assets/apollo-pattern.png` |
| Email header | `.planning/sketches/003-apollo-asset-pack/assets/apollo-email-header.png` |

Generated assets are the 22 assets above. Three ready assets are local derivatives:

- Dark icon: `apollo-icon-dark.png` — favicon placed on charcoal.
- Stickers: `apollo-stickers.png` — six-up collage.
- Notification: `apollo-notify.png` — crop from capture.

Do not describe derivatives as newly generated poses. Two true generated poses remain pending: `pose-wave` and `pose-sleep`.

## CSS Patterns

Terracotta marks winner, must-have, or brand-significant states without flooding interface:

```css
.identity-card {
  background: #fff;
  border: 1px solid #eaeaea;
  border-radius: 10px;
  padding: 16px;
}

.identity-card[data-selected="true"] {
  border-color: #c45c3e;
  box-shadow: 0 0 0 2px rgba(196, 92, 62, 0.25);
}

.asset-tag {
  display: inline-block;
  padding: 2px 6px;
  border-radius: 3px;
  font-size: 10px;
  font-weight: 600;
}

.asset-tag--must { background: #c45c3e; color: #fff; }
.asset-tag--kept { background: #1a1a1a; color: #fff; }
.asset-tag--derived { background: #fce8e0; color: #c45c3e; }
.asset-card--derived { border-style: dashed; }
```

Keep mascot images on quiet bone or white fields with `object-fit: contain`; never crop canonical character anatomy unintentionally.

## HTML Structures

Identity choice:

```html
<figure class="identity-card" data-selected="true">
  <img
    src="/brand/apollo.png"
    alt="Apollo, Puzzlessbox raccoon mascot with box backpack"
  >
  <figcaption>
    <strong>Apollo</strong>
    Raccoon companion to Hermes
  </figcaption>
</figure>
```

Asset inventory entry:

```html
<figure class="asset-card">
  <span class="asset-tag asset-tag--must">must</span>
  <img src="/brand/apollo-capture.png" alt="Apollo confirming a captured item">
  <figcaption>
    <strong>Capture confirmation</strong>
  </figcaption>
</figure>
```

Use decorative empty-state art with empty `alt=""` when adjacent text already communicates state. Use descriptive alt text when Apollo conveys unique meaning or acts as content.

## What to Avoid

- Flat util lettermarks, seals, grids, capture slots, or abstract marks as primary identity.
- Soft-clay Box-Buddy as primary.
- Abstract P+box “cool SaaS” mark as primary.
- Baby proportions, toy gloss, Disney styling, random costume changes, missing backpack/cargo, or altered bandana hue.
- Treating every asset as separately generated; preserve derived/generated provenance.
- Claiming binary assets were copied into this skill. They remain canonical under `.planning/sketches/`.
- Using `.planning/sketches/002-logo-mark-context/index.html` for branding. It is stale pre-winner exploration. Use `sources/002-logo-mark-context/compare.html` and `.planning/sketches/BRAND.md`.

## Origin

Synthesized from sketches:
- 002-logo-mark-context, winner B → Apollo
- 003-apollo-asset-pack, keep-all

Source snapshots:
- `sources/002-logo-mark-context/compare.html`
- `sources/003-apollo-asset-pack/compare.html`

Canonical binary inventory remains in:
- `.planning/sketches/002-logo-mark-context/assets/`
- `.planning/sketches/003-apollo-asset-pack/assets/`
