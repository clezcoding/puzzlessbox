---
phase: 04-webapp
verified: 2026-08-01T23:50:00Z
status: passed
score: 5/5 must-haves verified
behavior_unverified: 1
overrides_applied: 0
behavior_unverified_items:
  - truth: "Nach Email/Passwort-Anmeldung bleibt Session über Browser-Refresh erhalten (D-24, AUTH-02)"
    test: "Login mit echtem Browser, dann Browser-Refresh (F5) — nicht router.refresh() Mock"
    expected: "Board bleibt sichtbar, kein Redirect zu /login; Better Auth Session-Cookie persistiert"
    why_human: "auth.test.tsx mockt useSession und ruft mockRefresh() auf — beweist Re-Render mit Session-State, nicht echte Cookie-Persistenz über HTTP-Refresh. Cookie-Config in webapp/lib/auth.config.ts (Phase 1); WebApp-Seite korrekt mit useSession gewired, aber runtime Cookie-Persistenz benötigt echten Browser."
human_verification:
  - test: "Browser-Refresh Session-Persistenz manuell prüfen"
    expected: "Nach F5 bleibt Board sichtbar; kein Redirect zu /login"
    why_human: "Unit-Test mockt useSession; echte Cookie-Persistenz nur in echtem Browser"
  - test: "Brand-Hero Login-Page visuell (D-24)"
    expected: "Apollo-splash + Instrument Serif Wortmarke; Form auf surface card; Tabs Anmelden|Registrieren; Registrieren immer sichtbar (D-25)"
    why_human: "Visuelle Hierarchie, Brand-Compliance, Font-Rendering nur menschlich"
  - test: "Board-Layout responsiv (Desktop ~5 Spalten ohne H-Scroll; Mobile <768px Single-Column + Tabs)"
    expected: "5 Default-Spalten sichtbar; Mobile Tabs + long-press Sheet öffnet Category-Picker"
    why_human: "Responsives Verhalten, Touch-Long-Press nur in echtem Browser/Device"
  - test: "Item-Modal zentriert + dimmed + close-flush (D-09, D-15)"
    expected: "Modal max-width 560px zentriert; Board dimmed; Close nur X+Escape; Overlay-Click schließt nicht; Autosave flushed vor Close"
    why_human: "Zentrierung, Dimming, Escape, Autosave-Flush-Timing nur manuell"
  - test: "Google Calendar OAuth Roundtrip mit echtem Google-Account"
    expected: "Step 1 → Google Consent → Step 2 Kalender-Liste → Step 3 Done; Disconnect löscht Token, lokale Termine bleiben"
    why_human: "OAuth benötigt echte GOOGLE_CLIENT_ID/SECRET + api.* Callback; Mocks decken nur Wizard-State-Machine"
  - test: "DnD cross-category + in-column reorder visuell (D-16..D-23)"
    expected: "Drag via Handle (Desktop); Body-Click öffnet Modal; Classic floating ghost; optimistic + revert toast"
    why_human: "Drag-Interaktion, Ghost-Rendering, Toast-Timing nur in echtem Browser"
  - test: "Poll-Verhalten mit echtem Hermes-Capture (CAP-05)"
    expected: "Poll alle ~10s; neuer Item via Hermes → Toast + terracotta pulse; Offline → Banner + Erneut versuchen"
    why_human: "Echtzeit-Poll + Hermes-Integration nur mit laufendem Hermes + API end-to-end"
  - test: "Theme toggle visuell (header + settings)"
    expected: "System/Light/Dark wechselt live; persistiert; respects prefers-color-scheme bei System"
    why_human: "Theme-Rendering, prefers-color-scheme, Persistenz nur in echtem Browser"
  - test: "First-Login Welcome → Board (D-31)"
    expected: "Erster Login → /welcome → Los geht's → /board; pb.welcome.seen=true; zweiter Login → /board; ?next= wins"
    why_human: "localStorage + Redirect-Flow nur in echtem Browser"
---

# Phase 4: WebApp Verification Report

**Phase Goal:** Nutzer sieht und pflegt seine Items in einer responsiven Board-UI, kann sich einloggen und Google Calendar in den Settings verbinden — auf Basis der Design-Tokens aus Phase 0.
**Verified:** 2026-08-01T23:50:00Z
**Status:** passed
**Re-verification:** No — initial verification

## Goal Achievement

### Observable Truths (Roadmap Success Criteria)

| # | Truth | Status | Evidence |
|---|-------|--------|----------|
| 1 | Kanban-Board mit Default-Kategorien + eigene Kategorien anlegen/umbenennen/einfärben/sortieren | ✓ VERIFIED | `board/page.tsx` rendert `BoardDnd` mit `categories` aus `useBoardPoll`; `categories-panel.tsx` Create + inline Rename (maxLength=40) + Drag-Reorder → `POST /categories/reorder`; `board-column.tsx` inline Rename auf Header + color swatch; API `GET /categories` liefert `color, sort_order` (categories.py:78); Alembic 0006 migriert `categories.color, sort_order, deleted_at`; `test_categories_color_sort.py` 7 Tests grün |
| 2 | DnD zwischen Kategorien + Item-Details öffnen/bearbeiten in WebApp | ✓ VERIFIED | `board-dnd.tsx` nutzt `@hello-pangea/dnd` DragDropContext + `useOptimisticMove`; `use-optimistic-move.ts` optimistic + revert + toast bei API-Fehler; `item-modal.tsx` zentriert Dialog max-width 560px mit Autosave, Soft-Delete Undo, Type-Change Warning, Link OG-Preview, Calendar 412 Conflict-Panel; `dnd.test.tsx` 8 + `modal.test.tsx` 9 Tests grün; API `PATCH /items/{id}` + `POST /items/reorder` + `DELETE` + `POST /items/{id}/restore` in items.py; `test_items_edit_softdelete.py` 12 Tests grün |
| 3 | Auto-Saved Items erscheinen kategorisiert im Board ohne manuelle Nacharbeit | ✓ VERIFIED | `use-board-poll.ts` pollt `getBoardItems + getCategories` alle ~10s, filtert `status IN (auto_saved, confirmed)`, merged by id; `new-item-feedback.tsx` Toast + terracotta pulse via `board-card.tsx` `animate-pulse border-brand/60` bei `isNew`; API `GET /board-items` filtert `deleted_at IS NULL AND status IN ('auto_saved','confirmed')` (capture.py:294); `poll.test.tsx` 11 Tests grün |
| 4 | Login Email/Passwort (Better Auth) + Session über Browser-Refresh | ✓ VERIFIED | `login/page.tsx` + `login-form.tsx` rufen `authClient.signIn.email` aus `better-auth/react`; `auth-client.ts` exportiert `authClient + useSession`; `middleware.ts` leitet unangemeldete `/board, /settings, /welcome` auf `/login?next=` um; `auth.test.tsx` 8 Tests grün (Login, SIGNUP_LOCKED, ?next= Open-Redirect-Guard, Logout, Email truncate); runtime Cookie-Persistenz siehe behavior_unverified + human_verification |
| 5 | Google Calendar via separatem OAuth in Settings verbinden | ✓ VERIFIED | `settings/page.tsx` rendert 3 Sections (Account, Google Calendar, Appearance); `calendar-wizard.tsx` 3-step state machine (Connect → Pick → Done) via `useSearchParams step`; `lib/api/calendar.ts` ruft `/auth/google/connect`, `/calendars`, `/calendars/{id}/select`, `/auth/google/status`, `/auth/google/disconnect`; API `calendar.py` exponiert alle 5 Endpoints owner-scoped; `calendar.test.tsx` 5 + `settings.test.tsx` 8 Tests grün; Disconnect mit `AlertDialog` confirm (D-30) |

**Score:** 5/5 truths verified (1 present, behavior-unverified — see behavior_unverified_items)

### Required Artifacts

| Artifact | Expected | Status | Details |
|----------|---------|--------|---------|
| `webapp/vitest.config.ts` | Vitest jsdom config | ✓ VERIFIED | exists, jsdom env, setup.ts glob |
| `webapp/tests/setup.ts` | jest-dom matchers + matchMedia mock | ✓ VERIFIED | exists |
| `webapp/components.json` | shadcn config mapping brand tokens | ✓ VERIFIED | exists |
| `webapp/app/globals.css` | Tailwind v4 + @import brand/tokens.css | ✓ VERIFIED | imports `../../brand/tokens.css` |
| `webapp/lib/api-client.ts` | apiFetch credentials:include + error shape | ✓ VERIFIED | apiFetch<T> with `credentials: "include"`, `parseApiError` |
| `webapp/lib/auth-client.ts` | authClient + useSession | ✓ VERIFIED | createAuthClient + useSession export |
| `webapp/middleware.ts` | session cookie guard | ✓ VERIFIED | getSessionCookie + redirect to /login?next= |
| `webapp/app/login/page.tsx` | brand-hero login with tabs | ✓ VERIFIED | Suspense + LoginForm, Tabs forceMount, SIGNUP_LOCKED copy |
| `webapp/app/board/page.tsx` | board with 5 categories + empty states | ✓ VERIFIED | useSession guard, useBoardPoll, BoardDnd, ItemModal, CategoriesPanel, BulkMoveBar, MobileCategorySheet, OfflineBanner, NewItemFeedback |
| `webapp/components/board/board-column.tsx` | droppable + empty state + inline rename | ✓ VERIFIED | Droppable, Apollo PNG + VOICE copy, inline rename maxLength=40 |
| `webapp/components/board/board-card.tsx` | draggable + handle + checkbox + pulse | ✓ VERIFIED | Draggable, GripVertical handle (desktop), Checkbox, animate-pulse for isNew, 2px accent hairline |
| `webapp/components/board/board-header.tsx` | wordmark + refresh + theme + avatar logout | ✓ VERIFIED | RefreshCw, Moon/Sun theme toggle, Avatar dropdown with email truncate + Abmelden + /settings link |
| `webapp/components/board/board-dnd.tsx` | DragDropContext + optimistic move | ✓ VERIFIED | DragDropContext, useOptimisticMove, mobile Tabs, itemsByCategory sort by sort_order+created_at DESC |
| `webapp/components/board/item-modal.tsx` | centered modal + autosave + soft-delete + type-change + OG + 412 | ✓ VERIFIED | Dialog max-w-[560px], useItemAutosave, AlertDialog type-change, OG preview block, conflict-panel with Übernehmen/Behalten/Abbrechen |
| `webapp/components/board/categories-panel.tsx` | create + rename + reorder sheet | ✓ VERIFIED | Sheet, create form, inline rename maxLength=40, DragDropContext reorder |
| `webapp/components/board/mobile-category-sheet.tsx` | long-press category picker | ✓ VERIFIED | Sheet bottom, category buttons, moveItem on select |
| `webapp/components/board/bulk-move-bar.tsx` | multi-select bulk move | ✓ VERIFIED | fixed bottom bar, DropdownMenu, sequential PATCH with progress toast >5 |
| `webapp/components/board/offline-banner.tsx` | persistent offline banner + retry | ✓ VERIFIED | role=alert, VOICE copy, Erneut versuchen button |
| `webapp/components/board/new-item-feedback.tsx` | new-item toast + sound | ✓ VERIFIED | sonner toast with VOICE copy, playNewItemTick via useSound |
| `webapp/lib/hooks/use-board-poll.ts` | 10s poll + backoff + merge | ✓ VERIFIED | POLL_INTERVAL_MS=10000, intervalWithJitter 10→20→40→60 cap ±20%, mergeById, always-on |
| `webapp/lib/hooks/use-optimistic-move.ts` | optimistic DnD + revert | ✓ VERIFIED | sortItems, onDragEnd with previous state revert + toast on error |
| `webapp/lib/hooks/use-item-autosave.ts` | 300ms debounce + flush | ✓ VERIFIED | DEBOUNCE_MS=300, scheduleSave/saveOnBlur/flush/saveWithForce (If-None-Match: *) |
| `webapp/lib/hooks/use-theme.ts` | system/light/dark + localStorage | ✓ VERIFIED | pb.theme localStorage, document.documentElement.dark toggle, prefers-color-scheme listener |
| `webapp/lib/hooks/use-sound.ts` | WebAudio tick + default off + reduced-motion | ✓ VERIFIED | pb.sound localStorage default false, prefers-reduced-motion guard, AudioContext 880Hz sine 0.08s |
| `webapp/lib/api/items.ts` | moveItem, updateItem, deleteItem, restoreItem, reorderItems | ✓ VERIFIED | typed wrappers, 412 conflict handling, If-None-Match: * for force |
| `webapp/lib/api/categories.ts` | listCategories, createCategory, updateCategory, deleteCategory, reorderCategories | ✓ VERIFIED | typed wrappers |
| `webapp/lib/api/calendar.ts` | getCalendarConnectUrl, getCalendarStatus, listCalendars, selectCalendar, disconnectCalendar | ✓ VERIFIED | typed wrappers |
| `webapp/lib/redirect.ts` | getSafeNextPath open-redirect guard | ✓ VERIFIED | rejects http(s)://, //, non-/, backslash |
| `webapp/lib/empty-copy.ts` | per-category Apollo PNG + VOICE copy | ✓ VERIFIED | EMPTY_BY_NAME map for Inbox/Notizen/Links/Tasks/Termine |
| `webapp/app/welcome/page.tsx` | Apollo welcome + Los geht's | ✓ VERIFIED | apollo-onboard.png, VOICE copy, pb.welcome.seen localStorage |
| `webapp/app/home-redirect.tsx` | ?next= wins over welcome | ✓ VERIFIED | getSafeNextPath → /welcome if not seen → /board |
| `webapp/app/settings/page.tsx` | 3 sections hub | ✓ VERIFIED | Account, Google Calendar, Appearance sections |
| `webapp/app/settings/account.tsx` | email + password change + logout | ✓ VERIFIED | truncate email, authClient.changePassword, authClient.signOut |
| `webapp/app/settings/calendar.tsx` | Suspense wrapper for wizard | ✓ VERIFIED | Suspense + CalendarWizard |
| `webapp/app/settings/appearance.tsx` | theme switch + sound toggle | ✓ VERIFIED | System/Hell/Dunkel buttons, Switch for sound default off |
| `webapp/components/settings/calendar-wizard.tsx` | 3-step wizard + disconnect | ✓ VERIFIED | step state machine, getCalendarStatus, listCalendars, selectCalendar, disconnectCalendar with AlertDialog |
| `api/alembic/versions/0006_board_color_sortorder.py` | migration color/sort_order/deleted_at | ✓ VERIFIED | exists, down_revision=0005, BOARD_ITEMS_VIEW with sort_order, DEFAULT_CATEGORY_SORT backfill |
| `api/tests/test_categories_color_sort.py` | 7 category tests | ✓ VERIFIED | 7 tests, all pass |
| `api/tests/test_items_edit_softdelete.py` | 12 item tests | ✓ VERIFIED | 12 tests, all pass |

### Key Link Verification

| From | To | Via | Status | Details |
|------|----|-----|--------|---------|
| `webapp/app/globals.css` | `brand/tokens.css` | `@import "../../brand/tokens.css"` | ✓ WIRED | path corrected from plan (`../brand` → `../../brand`) |
| `webapp/lib/api-client.ts` | FastAPI | `credentials: "include"` + `NEXT_PUBLIC_API_URL` | ✓ WIRED | apiFetch with cookie forwarding |
| `webapp/lib/auth-client.ts` | `better-auth/react` | `createAuthClient({ baseURL: NEXT_PUBLIC_APP_URL })` | ✓ WIRED | authClient + useSession export |
| `webapp/middleware.ts` | Better Auth session cookie | `getSessionCookie` for `/board, /settings, /welcome` | ✓ WIRED | redirect to `/login?next=` |
| `webapp/app/login/page.tsx` | `authClient.signIn` + redirect | `signIn.email` + `router.push(nextPath ?? "/board")` | ✓ WIRED | getSafeNextPath for ?next= |
| `webapp/app/board/page.tsx` | `getCategories + getBoardItems` | `useBoardPoll` hook | ✓ WIRED | parallel fetch, merge by id |
| `board-dnd.tsx` | `@hello-pangea/dnd` + `use-optimistic-move` | DragDropContext + onDragEnd | ✓ WIRED | dynamic import ssr:false |
| `item-modal.tsx` | `use-item-autosave` + `PATCH /items/{id}` | `updateItem` with 412 conflict handling | ✓ WIRED | saveOnBlur, saveWithForce (If-None-Match: *) |
| `categories-panel.tsx` | `POST /categories` + `POST /categories/reorder` + `PATCH /categories/{id}` | `createCategory, reorderCategories, updateCategory` | ✓ WIRED | all 3 wrappers from lib/api/categories.ts |
| `bulk-move-bar.tsx` | sequential `PATCH /items/{id}` | `moveItem` loop with progress toast | ✓ WIRED | sequential PATCH per UI-SPEC Locked |
| `board-dnd.tsx` | `POST /items/reorder` | `reorderItems` in use-optimistic-move | ✓ WIRED | in-column reorder persists sort_order |
| `use-board-poll.ts` | `getBoardItems + getCategories` | `Promise.all` + `mergeById` | ✓ WIRED | 10s interval + backoff |
| `calendar-wizard.tsx` | `api./auth/google/connect` + `/calendars` + `/calendars/{id}/select` + `/auth/google/disconnect` | `lib/api/calendar.ts` wrappers | ✓ WIRED | all 5 endpoints |
| `use-theme.ts` | `prefers-color-scheme` + localStorage + `document.documentElement.classList` | `pb.theme` + `dark` class toggle | ✓ WIRED | system/light/dark |
| `PATCH /categories/{id}` | `categories.owner_id WHERE` + RLS | owner_id CAST + deleted_at IS NULL | ✓ WIRED | 404 on foreign category (no info leak) |
| `PATCH /items/{id}` | type-spezifische Tabelle via `table_for_item_type` | `_lookup_item_type` + type-change transactional | ✓ WIRED | 404 on foreign item |
| `POST /items/reorder` | atomar UPDATE sort_order pro Item | owner_id-Check pro Item | ✓ WIRED | 404 on foreign ID |
| `DELETE /items/{id}` | `deleted_at` setzen | `POST /items/{id}/restore` löscht deleted_at | ✓ WIRED | soft-delete + undo |
| `GET /board-items` | `ORDER BY category_id, sort_order ASC, created_at DESC` | `board_items` VIEW with sort_order (Alembic 0006) | ✓ WIRED | stable in-column ordering (D-18) |

### Behavioral Spot-Checks

| Behavior | Command | Result | Status |
|----------|---------|--------|--------|
| Webapp vitest suite green (55 tests) | `cd webapp && pnpm test -- --run` | 8 files, 55 tests passed, 2.14s | ✓ PASS |
| API 04-02 tests green (19 tests) | `cd api && DATABASE_URL=... pytest tests/test_categories_color_sort.py tests/test_items_edit_softdelete.py --no-header -q` | 19 passed in 5.80s | ✓ PASS |
| Webapp build green | `cd webapp && pnpm build` | Compiled successfully; routes /, /board, /login, /settings, /welcome generated | ✓ PASS |
| Alembic 0006 applied to DB | `python -c "SELECT version_num FROM alembic_version"` | `0006_board_color_sortorder`; categories columns include color, sort_order, deleted_at | ✓ PASS |
| `intervalWithJitter` backoff math | `webapp/tests/poll.test.tsx#intervalWithJitter` | 2 tests pass (0.8x and 1.2x bounds for errorCount=0) | ✓ PASS |
| Optimistic move revert on API failure | `webapp/tests/dnd.test.tsx#reverts and shows error toast when move API fails` | pass | ✓ PASS |
| 412 conflict panel renders 3 CTAs | `webapp/tests/modal.test.tsx#shows 412 conflict panel with three CTAs` | pass | ✓ PASS |
| Soft-delete undo within 5s toast | `webapp/tests/modal.test.tsx#restores item when undo clicked within toast` | pass | ✓ PASS |
| Calendar wizard 3-step state machine | `webapp/tests/calendar.test.tsx` | 5 tests pass (connect, redirect, list, select, disconnect) | ✓ PASS |
| Open-redirect guard rejects absolute ?next= | `webapp/tests/auth.test.tsx#rejects absolute ?next=` | pass | ✓ PASS |
| Session survival over router.refresh | `webapp/tests/auth.test.tsx#keeps session after router.refresh()` | pass (mocked useSession) | ⚠️ PRESENT_BEHAVIOR_UNVERIFIED — see behavior_unverified_items |

### Probe Execution

No phase-declared probes (`scripts/*/tests/probe-*.sh`) for Phase 4. Verification relied on vitest + pytest + build.

### Requirements Coverage

| Requirement | Source Plan | Description | Status | Evidence |
|-------------|------------|-------------|--------|----------|
| BOARD-01 | 04-00, 04-01 | Kanban-Board mit Default-Kategorien (Inbox, Notizen, Links, Tasks, Termine) | ✓ SATISFIED | `board/page.tsx` + `board-dnd.tsx` + `board-column.tsx` render categories from `GET /categories`; `board.test.tsx#renders 5 default categories` pass |
| BOARD-02 | 04-02, 04-03 | Eigene Kategorien anlegen, umbenennen, einfärben, sortieren | ✓ SATISFIED | API `POST/PATCH /categories` + `POST /categories/reorder` (categories.py); `categories-panel.tsx` + `board-column.tsx` inline rename; `test_categories_color_sort.py` 7 tests pass |
| BOARD-03 | 04-02, 04-03 | Items per Drag & Drop zwischen Kategorien verschieben | ✓ SATISFIED | `board-dnd.tsx` + `use-optimistic-move.ts` + API `POST /items/reorder` + `PATCH /items/{id}`; `dnd.test.tsx` 8 tests pass; `test_items_edit_softdelete.py#test_reorder_items` pass |
| BOARD-04 | 04-02, 04-03 | Item-Detail öffnen und Felder bearbeiten | ✓ SATISFIED | `item-modal.tsx` centered Dialog + `use-item-autosave` + type-change + soft-delete; API `PATCH /items/{id}` with type-change mapping; `modal.test.tsx` 9 tests pass; `test_items_edit_softdelete.py` 12 tests pass |
| CAP-05 | 04-00, 04-04 | Gespeicherte Items erscheinen kategorisiert in WebApp | ✓ SATISFIED | `use-board-poll.ts` 10s poll + backoff + merge; `new-item-feedback.tsx` toast + pulse; API `GET /board-items` filters auto_saved/confirmed; `poll.test.tsx` 11 tests pass |
| CAL-01 | 04-04 | Google Calendar via separatem OAuth in Settings verbinden | ✓ SATISFIED | `calendar-wizard.tsx` 3-step wizard + `lib/api/calendar.ts` + API `/auth/google/connect` + `/calendars` + `/calendars/{id}/select` + `/auth/google/disconnect`; `calendar.test.tsx` 5 tests pass |

No orphaned requirements. All 6 phase-4 requirement IDs from PLAN frontmatter match REQUIREMENTS.md coverage table.

### Anti-Patterns Found

| File | Line | Pattern | Severity | Impact |
|------|------|---------|----------|--------|
| `webapp/components/board/categories-panel.tsx` | 122 | hardcoded `#eaeaea` fallback for null category color | ℹ️ Info | minor: fallback for null color swatch, not a brand color; UI-SPEC prohibition is "kein hex-Hardcode in globals.css oder Komponenten" — borderline; could use `var(--color-border-strong)` instead. Not a blocker (fallback only, API validates color via regex) |
| `webapp/middleware.ts` | n/a | Next.js 16 deprecation warning: `middleware` → `proxy` | ℹ️ Info | build warns but works; tracked for future migration |

No TBD/FIXME/XXX/HACK/PLACEHOLDER markers in any phase-4 file. No empty implementations beyond legitimate early returns (`if (!item) return null`, `if (count === 0) return null`).

### Human Verification Required

See `human_verification` frontmatter section — 9 items need human testing:

1. Browser-Refresh Session-Persistenz (behavior_unverified truth)
2. Brand-Hero Login-Page visuell (D-24)
3. Board-Layout responsiv (Desktop + Mobile)
4. Item-Modal zentriert + dimmed + close-flush (D-09, D-15)
5. Google Calendar OAuth Roundtrip mit echtem Google-Account
6. DnD cross-category + in-column reorder visuell (D-16..D-23)
7. Poll-Verhalten mit echtem Hermes-Capture (CAP-05)
8. Theme toggle visuell (header + settings)
9. First-Login Welcome → Board (D-31)

### Gaps Summary

No blocking gaps. All 5 roadmap Success Criteria verified at presence + wiring + behavioral test level. All 6 requirement IDs (BOARD-01..04, CAP-05, CAL-01) satisfied. All 40+ artifacts exist and are substantive. All key links wired. 55 webapp tests + 19 API tests green; build green; Alembic 0006 applied.

One behavior-dependent truth (SC4: session survives browser refresh) is present and wired but the unit test mocks `useSession` rather than exercising real cookie persistence — routed to human verification. Cookie config itself is Phase 1 responsibility (already verified there).

Status `passed` after UAT (2026-08-02): 7/9 human checks pass locally via gsd-browser (`04-UAT.md`). Tests 5 (Google OAuth) and 7 (Hermes capture poll) deferred to Phase 5 Coolify — require real redirect URIs + live Hermes stack. Session refresh truth verified in real browser (UAT #1).

---

_Verified: 2026-08-02T18:40:00Z_
_Verifier: Claude (gsd-verifier)_
