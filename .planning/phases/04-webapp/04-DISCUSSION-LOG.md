# Phase 4: WebApp - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in CONTEXT.md — this log preserves the alternatives considered.

**Date:** 2026-08-01
**Phase:** 4-WebApp
**Areas discussed:** Board-Layout & Karten, Item-Detail & Bearbeitung, Drag & Drop Verhalten, Auth-UI & Calendar-Settings, Board-Aktualisierung (CAP-05)

---

## Board-Layout & Karten

| Question | Options | Selected |
|----------|---------|----------|
| Desktop layout | Klassisches Kanban / Kompakte Spalten / Liste | ✓ Kompakte Spalten |
| Mobile | Tabs / Gestapelt / Swipe | ✓ Tabs |
| Card content | Titel+Badge / Titel+Meta / Titel+Meta+Thumb | ✓ Titel+Meta+Thumb |
| Drafts on board | Nur saved / Ghost drafts / Alle+Badge | ✓ Nur auto_saved+confirmed |
| Empty state | Text / Apollo+Text / Minimal | ✓ Apollo+Text |
| Category CRUD | Inline only / Settings / Hybrid | ✓ Hybrid |
| Dark default | System+Toggle / Light / Dark | ✓ System+Toggle |
| New item highlight | Pulse / Badge Neu / Keine | ✓ Pulse ~2s |

**Notes:** User chose rich thumbnails over recommended meta-only cards.

---

## Item-Detail & Bearbeitung

| Question | Options | Selected |
|----------|---------|----------|
| Open UI | Drawer / Modal / Route | ✓ Centered Modal |
| Editable fields | Kern+typ / Nur Kern / Alles Raw | ✓ Kern+typ |
| Save | Explicit / Autosave / Hybrid | ✓ Autosave |
| Delete | Confirm soft / Kein Delete / Undo toast | ✓ Undo toast 5s |
| Link preview | Full OG / Compact / Kein Block | ✓ Full OG |
| Calendar 412 | Inline modal / Toast / Block edit | ✓ Inline modal |
| Type change | Warn / Silent / Locked | ✓ Warn |
| Close | Esc+overlay+X / X+Esc / X only | ✓ X+Esc |

**Notes:** Modal and Undo-toast overrode drawer/confirm recommendations.

---

## Drag & Drop Verhalten

| Question | Options | Selected |
|----------|---------|----------|
| Desktop drag | Whole card / Handle / Kein DnD | ✓ Handle |
| Mobile move | Long-press picker / Drag-to-tab / Beides | ✓ Long-press picker |
| In-column reorder | Persist / Nein v1 / Session only | ✓ Persist sort_order |
| API fail | Revert+Toast / Sync badge / Blocking | ✓ Revert+Toast |
| A11y | Menü+Pfeile / Voll / Mouse only | ✓ Menü+Pfeile |
| Ghost | Quiet / Classic / Minimal | ✓ Classic ghost |
| Multi | Single / Checkbox bulk / Shift-range | ✓ Checkbox bulk |
| Gestures | Unified / Separated / Reorder keyboard | ✓ Separated |

**Notes:** Persist reorder + multi bulk + classic ghost overrode lean recommendations.

---

## Auth-UI & Calendar-Settings

| Question | Options | Selected |
|----------|---------|----------|
| Login look | Brand-hero / Compact / Minimal | ✓ Brand-hero |
| Register locked | Hide route / Tab+message / CLI only | ✓ Tab+message |
| Settings shell | /settings / Modal / Calendar-only | ✓ /settings |
| Calendar connect | Button+dropdown / Wizard 3 / Auto primary | ✓ Wizard 3 |
| Logout | Settings+Header / Settings / Header | ✓ Settings+Header |
| Password change | Yes Settings / No v1 / Forgot only | ✓ Yes Settings |
| Google disconnect | Confirm / No confirm / None | ✓ Confirm |
| Post-login | Board / Board+next / Welcome first | ✓ Welcome first |

**Notes:** Always-visible Register + calendar wizard + first-login welcome overrode lean options. `?next=` still Claude discretion for OAuth return.

---

## Board-Aktualisierung (CAP-05)

| Question | Options | Selected |
|----------|---------|----------|
| Transport | Poll / SSE / Manual+focus | ✓ Poll |
| When active | Visibility / Always session / Time window | ✓ Always session |
| Merge edits | Poll merged / New only / ETag conflict | ✓ Poll merged |
| Offline | Banner / Silent / Full-page | ✓ Banner |
| Interval | 5s / 10s / 15–20s | ✓ ~10s |
| Toast | Toast+Pulse / Pulse only / Toast other-tab | ✓ Toast+Pulse |
| Sound | None / Optional pling / Browser notif | ✓ Optional pling default off |
| Manual refresh | Header / Poll only / Pull mobile | ✓ Header refresh |

**Notes:** Always-on poll + always toast + optional sound overrode quieter defaults.

---

## Claude's Discretion

- Poll backoff/jitter; dark toggle placement; bulk API shape; sort_order migration; welcome-flag storage + `?next=`; VOICE microcopy; DnD library; OG image caching

## Deferred Ideas

- SSE/WebSocket later; browser push notifications; full keyboard-drag a11y mode; brand SVG vectorization (Phase 0)
