# Phase 4: WebApp - Context

**Gathered:** 2026-08-01
**Status:** Ready for planning

<domain>
## Phase Boundary

Ship the Next.js WebApp UI: responsive Kanban board (default + custom categories, DnD, item detail edit), Better Auth login/register UI, and Google Calendar Connect in Settings — consuming Phase 0 `brand/` tokens. Requirements: BOARD-01..04, CAP-05, CAL-01. No Coolify/CI/deploy (Phase 5). No Hermes/MCP changes except consuming existing APIs.

</domain>

<decisions>
## Implementation Decisions

### Board layout & cards
- **D-01:** Desktop = compact Kanban columns sized so ~5 default categories fit without horizontal scroll; extra categories may scroll. — **Reversibility:** costly — column layout + responsive breakpoints
- **D-02:** Mobile (<768px) = single column + category tabs/chips (not stacked columns or swipe-Kanban).
- **D-03:** Collapsed cards show title + meta line + link thumbnail (rich cards). Thumbnail fallback when scrape image missing.
- **D-04:** Board shows only `auto_saved` and `confirmed` items — `draft` stays chat-only (Hermes). — **Reversibility:** costly — filters all board queries
- **D-05:** Empty states use Apollo illustration from `brand/assets` + VOICE.md copy.
- **D-06:** Category CRUD hybrid: rename/color on column header; create + reorder categories in a board “Kategorien verwalten” panel (not Settings-only).
- **D-07:** Theme follows `prefers-color-scheme` with a user toggle (Settings and/or header).
- **D-08:** Newly appeared items get a ~2s highlight pulse.

### Item detail & edit
- **D-09:** Open item in a **centered modal** (board dimmed underneath) — not drawer or `/items/[id]` route. — **Reversibility:** costly — routing/modal shell
- **D-10:** Editable: core fields for all types (title, body/notes, category) plus type-specific (URL, due, event times); type change allowed with warning/confirm and field mapping.
- **D-11:** Autosave on blur/debounce; error toast on failure — no explicit Save button.
- **D-12:** Soft-delete from WebApp with **Undo toast (~5s)** — no confirm dialog. Uses `deleted_at`.
- **D-13:** Link detail: full OG preview block (image + title + description) above edit fields.
- **D-14:** Google Calendar 412 conflicts resolved **inline in the modal** (show remote → Übernehmen / Behalten / Abbrechen) — CAL-03. — **Reversibility:** costly — conflict UX coupled to event edit
- **D-15:** Modal close = X + Escape only; overlay click does **not** close; flush pending autosave before close.

### Drag & drop
- **D-16:** Desktop: drag **only via handle**; card body click opens modal. — **Reversibility:** costly — DnD library + hit targets
- **D-17:** Mobile category change: long-press → category picker sheet (no drag-to-tab).
- **D-18:** Persist sort order within a column (`sort_order` / equivalent API). — **Reversibility:** one-way — schema/API if column missing
- **D-19:** Optimistic moves; on API failure **revert + toast**.
- **D-20:** A11y minimum: focus + “In Kategorie verschieben” menu + arrow keys for in-column reorder.
- **D-21:** Classic floating card ghost while dragging (not quiet-only outline).
- **D-22:** Checkbox multi-select + **bulk move** in v1. — **Reversibility:** costly — selection state + batch or sequential PATCH
- **D-23:** Separated gestures: cross-category = drop on column; in-column reorder = vertical drag only.

### Auth UI & Calendar settings
- **D-24:** Login/Register = **brand-hero** page (Apollo + wordmark, form below). — **Reversibility:** reversible
- **D-25:** Register tab always visible; when signup locked show friendly SIGNUP_LOCKED message (not hide route). Backend already locks via `databaseHooks` in `webapp/lib/auth.config.ts`.
- **D-26:** Settings = dedicated `/settings` hub (Account, Google Calendar, Appearance).
- **D-27:** Google Calendar connect = **3-step wizard**: Connect → Pick calendar → Done. Honors Phase 1 D-18 `calendar_id` selection. OAuth callback remains on `api.` (Phase 1 D-29). — **Reversibility:** costly — wizard state machine
- **D-28:** Logout in Settings → Account **and** board header avatar menu.
- **D-29:** Password change in Settings → Account (Better Auth change-password) in v1.
- **D-30:** Google Disconnect button + confirm; wipe tokens; keep local events (sync stops).
- **D-31:** First login shows short Apollo welcome, then Board. Subsequent logins → Board. Still support `?next=` / OAuth return (Claude discretion alongside welcome flag).

### Board live update (CAP-05)
- **D-32:** Short polling (~**10s**) while session is live (not visibility-paused). — **Reversibility:** costly — client data layer; SSE later would replace
- **D-33:** Same poll merges new items **and** remote edits/moves into open board.
- **D-34:** Offline / API-down: persistent banner + retry; show last fetched data.
- **D-35:** New item feedback: quiet VOICE toast **plus** pulse (always, not tab-conditional).
- **D-36:** Optional short pling; Settings toggle; **default off**.
- **D-37:** Manual refresh control in board header in addition to poll.

### Carried forward (do not re-litigate)
- Better Auth Email/Password in Next.js; FastAPI JWKS (Phase 1 D-21..D-24)
- Signup lock after first user (AUTH-03) — already wired in `auth.config.ts`
- Google Calendar = separate OAuth in Settings, not Better Auth Social (CAL-01 / PROJECT)
- Util Bone + Apollo + category pastels + dark token parity (Phase 0)
- Default categories Inbox · Notizen · Links · Tasks · Termine; `board_items` VIEW; soft-delete `deleted_at` (Phase 1)
- Product UI copy German / Apollo voice (`brand/VOICE.md`)

### Claude's Discretion
- Exact poll backoff / jitter / error retry cadence
- Whether Appearance dark toggle also lives in header vs Settings-only
- Bulk-move: single batch API vs sequential PATCHes
- `sort_order` column placement if not already in schema (migration shape)
- Welcome-flag storage (localStorage vs user preference row) and coexistence with `?next=`
- Exact German microcopy (must follow `brand/VOICE.md`)
- DnD library choice within Next.js 16 constraints
- Thumbnail image proxy/caching strategy for OG images

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Requirements & roadmap
- `.planning/REQUIREMENTS.md` — BOARD-01..04, CAP-05, CAL-01
- `.planning/ROADMAP.md` — Phase 4 goal + success criteria
- `.planning/PROJECT.md` — Better Auth, Calendar OAuth, stack pins, brand consumption
- `PUZZLESSBOX_PROJECT_BRIEF.md` — capture → board core value

### Brand (Phase 0)
- `brand/tokens.css` — CSS variables light/dark + category pastels
- `brand/tailwind.preset.ts` — Next.js Tailwind preset
- `brand/BRAND.md` — Apollo / Util Bone DNA
- `brand/VOICE.md` — German microcopy (empty, error, stash, confirm)
- `brand/assets/` — Apollo PNGs for empty/welcome/login hero
- `.planning/phases/00-branding-design-system/00-CONTEXT.md` — D-01..D-09 brand locks

### Prior phase contracts
- `.planning/phases/01-datenmodell-backend-api/01-CONTEXT.md` — auth bridge, calendar OAuth, `board_items`, status lifecycle, D-18 calendar_id
- `.planning/phases/02-mcp-server/02-CONTEXT.md` — item/category API shapes Hermes already uses
- `.planning/phases/03-hermes-plugin-timeout-spike/03-CONTEXT.md` — draft stays in chat; board sees post-autosave

### Existing WebApp code
- `webapp/lib/auth.config.ts` — Better Auth + JWT plugin + signup lock hook
- `webapp/lib/auth.ts` — auth export
- `webapp/app/api/auth/[...all]/route.ts` — Better Auth Next handler

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- `brand/tokens.css` + `brand/tailwind.preset.ts` — wire into Next.js 16 theme first
- Better Auth already mounted at `webapp/app/api/auth/[...all]` with signup lock
- Apollo asset pack under `brand/assets/` — login hero, empty states, first-login welcome
- API board/items/categories/calendar endpoints from Phase 1 (consume; extend only for `sort_order` / bulk if missing)

### Established Patterns
- Cross-service auth: Next.js session cookie / JWT → FastAPI JWKS (Phase 1)
- Status filter for board: exclude `draft`
- Unified API error shape `{ error: { code, message, details? } }`
- Soft-delete via `deleted_at` (Undo = clear `deleted_at` within toast window)

### Integration Points
- Greenfield UI under `webapp/app/` (board, settings, login/register, welcome)
- Google OAuth start from `app.` Settings wizard; callback on `api.` then return to wizard Done step
- CAP-05 poll against board list/items endpoints (~10s)

</code_context>

<specifics>
## Specific Ideas

- User overrode sparse cards → **rich cards with link thumbnails**
- User overrode drawer → **centered modal**
- User overrode confirm-delete → **Undo toast**
- User overrode no-reorder → **persist in-column sort_order**
- User overrode single-select → **checkbox multi + bulk move**
- User overrode quiet ghost → **classic floating card ghost**
- User overrode hide-register-route → **always show Register tab + locked message**
- User overrode single-screen calendar connect → **3-step wizard**
- User overrode visibility-paused poll → **always-on poll for live session**
- User overrode no-sound → **optional pling, default off**
- User wants **first-login Apollo welcome** before Board

</specifics>

<deferred>
## Deferred Ideas

- SSE / WebSocket push for board updates — replace poll in a later hardening pass if needed
- Browser push notifications when tab backgrounded
- Full keyboard-drag mode with live regions (beyond D-20 minimum)
- SVG vectorization of remaining brand marks (Phase 0 deferral; not Phase 4 blocker)

None of the above block Phase 4 success criteria.

</deferred>

---

*Phase: 4-WebApp*
*Context gathered: 2026-08-01*
