---
name: sketch-findings-puzzlessbox
description: Validated design decisions, CSS patterns, and visual direction from Puzzlessbox sketches. Auto-loaded during UI implementation.
---

# Puzzlessbox Sketch Findings

<context>
## Project: puzzlessbox

Apollo is the brand hero on a Utilitarian Bone workbench scaffold. Apollo is the clever raccoon companion to Hermes: capture enters through Hermes, receives confirmation, auto-saves after inactivity, then appears on the categorized board. Treat this capture → confirm → auto-save → board flow as the product reference point.

Identity and interface have separate jobs: Apollo supplies face, terracotta accent, voice, and illustration continuity; Utilitarian Bone supplies workbench chrome, hierarchy, hairlines, and quiet behavior.

Sketch sessions wrapped: 2026-07-29
</context>

<design_direction>
## Overall Direction

- Palette: bone `#f7f6f3`, charcoal `#1a1a1a` / `#2f3437`, terracotta `#c45c3e`, white surfaces, soft category tints.
- Type: Instrument Serif for display and masthead; DM Sans for UI and body; JetBrains Mono only for rare timestamps, IDs, and compact system metadata.
- Spacing: 4/8px base rhythm. Prefer 4, 8, 12, 16, 24, 32, and 48px steps.
- Shape: small radii, hairline borders, minimal shadows. Structure comes from rules, columns, and spacing.
- Motion: quiet and brief. Use restrained entry, status, and capture feedback; always support reduced motion.
- Brand relationship: Apollo leads brand-facing moments. Utilitarian Bone stays the neutral scaffold. Terracotta is the brand signal; teal is informational only.
</design_direction>

<findings_index>
## Design Areas

| Area | Reference | Key Decision |
|------|-----------|--------------|
| UI Foundation | `references/ui-foundation.md` | Utilitarian Bone masthead, live capture rail, five-column semantic board, and restrained cards |
| Apollo Identity & Assets | `references/apollo-identity-assets.md` | Apollo is the sole identity system, with locked character DNA and continuity-controlled assets |

## Theme

The winning theme file is at `sources/themes/default.css`.

## Source Files

Winning HTML snapshots are preserved under `sources/`. No binary assets are copied into this skill; use canonical originals under `.planning/sketches/`.

Important: `.planning/sketches/002-logo-mark-context/index.html` is stale pre-winner exploration and must not guide branding. Use `sources/002-logo-mark-context/compare.html` and `.planning/sketches/BRAND.md`.
</findings_index>

<metadata>
## Processed Sketches

- 001-brand-mood-board
- 002-logo-mark-context
- 003-apollo-asset-pack
</metadata>
