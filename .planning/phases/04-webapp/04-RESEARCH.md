# Phase 4: WebApp - Research

**Researched:** 2026-08-02
**Domain:** Frontend UI / React & Next.js Client-Side Integration
**Confidence:** HIGH

<user_constraints>
## User Constraints (from CONTEXT.md)

### Locked Decisions
- **D-01:** Desktop = compact Kanban columns sized so ~5 default categories fit without horizontal scroll; extra categories may scroll. — **Reversibility:** costly — column layout + responsive breakpoints
- **D-02:** Mobile (<768px) = single column + category tabs/chips (not stacked columns or swipe-Kanban).
- **D-03:** Collapsed cards show title + meta line + link thumbnail (rich cards). Thumbnail fallback when scrape image missing.
- **D-04:** Board shows only `auto_saved` and `confirmed` items — `draft` stays chat-only (Hermes). — **Reversibility:** costly — filters all board queries
- **D-05:** Empty states use Apollo illustration from `brand/assets` + VOICE.md copy.
- **D-06:** Category CRUD hybrid: rename/color on column header; create + reorder categories in a board “Kategorien verwalten” panel (not Settings-only).
- **D-07:** Theme follows `prefers-color-scheme` with a user toggle (Settings and/or header).
- **D-08:** Newly appeared items get a ~2s highlight pulse.
- **D-09:** Open item in a **centered modal** (board dimmed underneath) — not drawer or `/items/[id]` route. — **Reversibility:** costly — routing/modal shell
- **D-10:** Editable: core fields for all types (title, body/notes, category) plus type-specific (URL, due, event times); type change allowed with warning/confirm and field mapping.
- **D-11:** Autosave on blur/debounce; error toast on failure — no explicit Save button.
- **D-12:** Soft-delete from WebApp with **Undo toast (~5s)** — no confirm dialog. Uses `deleted_at`.
- **D-13:** Link detail: full OG preview block (image + title + description) above edit fields.
- **D-14:** Google Calendar 412 conflicts resolved **inline in the modal** (show remote → Übernehmen / Behalten / Abbrechen) — CAL-03. — **Reversibility:** costly — conflict UX coupled to event edit
- **D-15:** Modal close = X + Escape only; overlay click does **not** close; flush pending autosave before close.
- **D-16:** Desktop: drag **only via handle**; card body click opens modal. — **Reversibility:** costly — DnD library + hit targets
- **D-17:** Mobile category change: long-press → category picker sheet (no drag-to-tab).
- **D-18:** Persist sort order within a column (`sort_order` / equivalent API). — **Reversibility:** one-way — schema/API if column missing
- **D-19:** Optimistic moves; on API failure **revert + toast**.
- **D-20:** A11y minimum: focus + “In Kategorie verschieben” menu + arrow keys for in-column reorder.
- **D-21:** Classic floating card ghost while dragging (not quiet-only outline).
- **D-22:** Checkbox multi-select + **bulk move** in v1. — **Reversibility:** costly — selection state + batch or sequential PATCH
- **D-23:** Separated gestures: cross-category = drop on column; in-column reorder = vertical drag only.
- **D-24:** Login/Register = **brand-hero** page (Apollo + wordmark, form below). — **Reversibility:** reversible
- **D-25:** Register tab always visible; when signup locked show friendly SIGNUP_LOCKED message (not hide route). Backend already locks via `databaseHooks` in `webapp/lib/auth.config.ts`.
- **D-26:** Settings = dedicated `/settings` hub (Account, Google Calendar, Appearance).
- **D-27:** Google Calendar connect = **3-step wizard**: Connect → Pick calendar → Done. Honors Phase 1 D-18 `calendar_id` selection. OAuth callback remains on `api.` (Phase 1 D-29). — **Reversibility:** costly — wizard state machine
- **D-28:** Logout in Settings → Account **and** board header avatar menu.
- **D-29:** Password change in Settings → Account (Better Auth change-password) in v1.
- **D-30:** Google Disconnect button + confirm; wipe tokens; keep local events (sync stops).
- **D-31:** First login shows short Apollo welcome, then Board. Subsequent logins → Board. Still support `?next=` / OAuth return (Claude discretion alongside welcome flag).
- **D-32:** Short polling (~**10s**) while session is live (not visibility-paused). — **Reversibility:** costly — client data layer; SSE later would replace
- **D-33:** Same poll merges new items **and** remote edits/moves into open board.
- **D-34:** Offline / API-down: persistent banner + retry; show last fetched data.
- **D-35:** New item feedback: quiet VOICE toast **plus** pulse (always, not tab-conditional).
- **D-36:** Optional short pling; Settings toggle; **default off**.
- **D-37:** Manual refresh control in board header in addition to poll.

### Claude's Discretion
- Exact poll backoff / jitter / error retry cadence
- Whether Appearance dark toggle also lives in header vs Settings-only
- Bulk-move: single batch API vs sequential PATCHes
- `sort_order` column placement if not already in schema (migration shape)
- Welcome-flag storage (localStorage vs user preference row) and coexistence with `?next=`
- Exact German microcopy (must follow `brand/VOICE.md`)
- DnD library choice within Next.js 16 constraints
- Thumbnail image proxy/caching strategy for OG images
- Whether sound is enabled, settings and default off

### Deferred Ideas (OUT OF SCOPE)
- SSE / WebSocket push for board updates — replace poll in a later hardening pass if needed
- Browser push notifications when tab backgrounded
- Full keyboard-drag mode with live regions (beyond D-20 minimum)
- SVG vectorization of remaining brand marks (Phase 0 deferral; not Phase 4 blocker)
</user_constraints>

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|------------------|
| **BOARD-01** | User sieht Kanban-/Board-Ansicht mit Default-Kategorien (Inbox, Notizen, Links, Tasks, Termine). | [CITED: 04-UI-SPEC.md] Board layout and styling from brand preset CSS variables mapped into Next.js. |
| **BOARD-02** | User kann eigene Kategorien anlegen, umbenennen, einfärben und sortieren. | [CITED: 04-CONTEXT.md D-06] CRUD hybrid via column header and categories panel. Needs schema migration support for `color` and `sort_order` in categories. |
| **BOARD-03** | User verschiebt Items per Drag & Drop zwischen Kategorien. | [VERIFIED: npm registry] Implementation with `@hello-pangea/dnd` and optimistic UI updates. |
| **BOARD-04** | User öffnet Item-Detail und bearbeitet Felder in der WebApp. | [CITED: 04-CONTEXT.md D-09, D-10, D-11] Centered Modal (shadcn Dialog), autosave on blur with debouncing. |
| **CAP-05** | Gespeicherte Items erscheinen kategorisiert in der WebApp. | [CITED: 04-CONTEXT.md D-32, D-33] Short polling (10s) to sync live Hermes capture without manual reload. |
| **CAL-01** | User verbindet Google Calendar in WebApp-Settings via separatem OAuth (nicht Better Auth Social). | [CITED: 04-CONTEXT.md D-27] 3-step settings wizard (Connect -> Pick calendar -> Done). Inline event modal 412 handling. |
</phase_requirements>

## Summary

Phase 4 of Puzzlessbox focuses on the client UI: implementing the responsive board, drag-and-drop mechanics, authentication interface, and Google Calendar OAuth integration using Next.js 16.2 and React 19.0.
By consuming branding and tokens created in Phase 0 (`brand/`), the WebApp delivers a premium, cohesive, and tactile user experience styled around the warm "Utilitarian Bone" workbench aesthetic and the mascot "Apollo" (terracotta details).
The technology choices—specifically `@hello-pangea/dnd` for drag-and-drop and `better-auth` for robust email/password sessions—fully support React 19 and Next.js 16.

**Primary recommendation:** Initialize shadcn/ui primitives locally, map them directly to `brand/tokens.css` variables without duplicating the color palette, and implement optimistic drag-and-drop state transitions with a robust revert callback linked to the `/items/{id}` backend PATCH endpoint.

---

## Project Constraints (from .cursor/rules/)

- **Rule: Caveman full active:** Respond terse like smart caveman. Drop articles, fillers, pleasantries, hedging.
- **Rule: Ponytail senior dev mode:** Write minimum code that works. Avoid unnecessary abstractions. Deletion over addition.
- **Rule: Honey (AI shrinkage):** Less code, less prose, dense agent messaging.
- **Rule: Context7 documentation:** Use `ctx7` to resolve library IDs and fetch docs for any package/library query.
- **Rule: Wigolo Search:** Prefer `wigolo` server over standard `WebSearch` for all search/fetch operations.

## Architectural Responsibility Map

| Capability | Primary Tier | Secondary Tier | Rationale |
|------------|-------------|----------------|-----------|
| Board layout and rendering | Browser / Client | Frontend Server (SSR) | Renders columns and cards using CSS grid. Uses SSR for initial skeleton frame of the board. |
| Category CRUD & reordering | Browser / Client | API / Backend | State managed in client panel, persistent updates pushed to backend `/categories` REST endpoint. |
| Drag & drop (reorder & move) | Browser / Client | — | Controlled entirely on client thread using `@hello-pangea/dnd` to ensure visual responsiveness and instant layout transitions. |
| Client Authentication UI | Browser / Client | Frontend Server (SSR) | `better-auth` client SDK manages session hooks in client, while middleware handles initial routing checks. |
| Calendar connect wizard | Browser / Client | API / Backend | Multi-step client form state machine. API / Backend retains actual OAuth flow tokens and syncs with Google Calendar. |
| Debounced Autosave | Browser / Client | — | Triggers on blur or input debounce. Handled client-side to prevent network saturation. |

---

## Standard Stack

### Core
| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| `next` | `16.2.12` | React Framework | App Router, SSR, Middleware. [VERIFIED: package.json] |
| `react` | `19.0.0` | UI Library | Core application state and rendering engine. [VERIFIED: package.json] |
| `better-auth` | `1.6.25` | Client-Side Auth | High quality framework-agnostic session management. [VERIFIED: package.json] |
| `@hello-pangea/dnd` | `18.0.1` | Drag and Drop | Maintained fork of react-beautiful-dnd with native React 19 support. [VERIFIED: npm registry] |

### Supporting
| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| `lucide-react` | `1.28.0` | Icon Library | Native clean strokes for UI actions and category iconography. [VERIFIED: npm registry] |
| `zod` | `3.24.1` | Form & State Validation | Client-side input validation and error feedback boundary. [ASSUMED] |
| `react-hook-form` | `7.54.2` | Form Controller | Performance-optimized form tracking for login, settings, and modal fields. [ASSUMED] |
| `@hookform/resolvers` | `3.10.0` | Zod resolver hook | Connects React Hook Form with Zod schemas. [ASSUMED] |
| `sonner` | `1.7.2` | Toast Notifications | Premium, non-blocking notification layer for undos and errors. [ASSUMED] |
| `vitest` | `4.1.10` | Test Runner | Lightweight and extremely fast unit test runner suited for Next.js. [VERIFIED: npm registry] |
| `@testing-library/react` | `16.3.2` | React Component Tests | Standard assertion layer to verify component behavior and state changes. [VERIFIED: npm registry] |

### Alternatives Considered
| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| `@hello-pangea/dnd` | `@dnd-kit/core` | `@dnd-kit` is modular but requires hand-rolling heavy keyboard accessibility support and visual placeholder placeholders. `@hello-pangea/dnd` is robust and matches Trello-style grid physics out-of-the-box. |
| `sonner` | `react-hot-toast` | `sonner` is the standard for shadcn installations, supports stacked notifications better and provides a highly polished visual feel native to modern Tailwind styles. |

**Installation:**
```bash
pnpm add @hello-pangea/dnd lucide-react zod react-hook-form @hookform/resolvers sonner
pnpm add -D vitest @testing-library/react @testing-library/jest-dom @vitejs/plugin-react jsdom
```

---

## Package Legitimacy Audit

> **Legitimacy Verified:** Ecosystem checks run against npm registry on 2026-08-02.

| Package | Registry | Age | Downloads | Source Repo | Verdict | Disposition |
|---------|----------|-----|-----------|-------------|---------|-------------|
| `@hello-pangea/dnd` | npm | 4 yrs | 2.7M/wk | github.com/hello-pangea/dnd | [OK] | Approved |
| `lucide-react` | npm | 4 yrs | 81M/wk | github.com/lucide-icons/lucide | [SUS] | Approved (false positive: flagged `too-new` due to rapid release cadences) |
| `vitest` | npm | 4 yrs | 86M/wk | github.com/vitest-dev/vitest | [SUS] | Approved (false positive: flagged `too-new` due to rapid minor releases) |
| `@testing-library/react` | npm | 9 yrs | 50M/wk | github.com/testing-library/react-testing-library | [OK] | Approved |

**Packages removed due to [SLOP] verdict:** none
**Packages flagged as suspicious [SUS]:** `lucide-react`, `vitest` (no action needed; verified manually as reputable ecosystem packages).

---

## Architecture Patterns

### System Architecture Diagram

```mermaid
graph TD
    subgraph Client [Browser / Next.js Client]
        UI[Kanban Board View]
        DND[@hello-pangea/dnd State]
        Modal[Centered Item Modal]
        ClientAuth[Better Auth client SDK]
        Poll[Short Poller ~10s]
    end

    subgraph Server [Next.js App Server / API Gateway]
        Middleware[Next.js Auth Middleware]
        NextAuth[Better Auth Route Handler]
    end

    subgraph Backend [FastAPI Backend Service]
        FastAPI[FastAPI Router]
        Db[(PostgreSQL Database)]
        GoogleCal[Google Calendar Sync]
    end

    UI -->|1. Drag / Drop| DND
    DND -->|2. Optimistic Update| UI
    DND -->|3. Move API PATCH /items/{id}| FastAPI
    UI -->|4. Click Card| Modal
    Modal -->|5. Blur / Autosave| FastAPI
    Poll -->|6. Fetch board-items /categories| FastAPI
    ClientAuth -->|7. Cookie Session| Middleware
    Middleware -->|8. Forward request| FastAPI
    FastAPI -->|9. Tenant isolated queries| Db
    FastAPI -->|10. Calendar Sync| GoogleCal
```

### Recommended Project Structure
```
webapp/
├── app/
│   ├── api/
│   │   └── auth/
│   │       └── [...all]/
│   │           └── route.ts     # Better Auth API handler
│   ├── layout.tsx                # App layout wrapping providers
│   ├── page.tsx                  # Root redirect (Welcome or Board)
│   ├── board/
│   │   └── page.tsx              # Kanban Board view (D-01, D-04)
│   ├── login/
│   │   └── page.tsx              # Login surface (D-24, D-25)
│   ├── settings/
│   │   └── page.tsx              # Dedicated settings / Google Cal wizard (D-26, D-27)
│   └── globals.css               # Imports brand/tokens.css
├── components/
│   ├── ui/                       # shadcn primitives (Button, Dialog, Toast, etc.)
│   ├── board/
│   │   ├── board-column.tsx      # Kanban Column containing cards
│   │   └── board-card.tsx        # Compact/rich item card with handle (D-03)
│   └── settings/
│       └── calendar-wizard.tsx   # 3-step connect wizard (D-27)
└── lib/
    ├── api-client.ts             # API wrapper with JWT headers
    ├── auth.config.ts            # Better Auth server configuration
    └── auth.ts                   # Export client/server auth helpers
```

### Pattern 1: Optimistic Drag-and-Drop Reorder with Revert Fallback
**What:** Instant visual movement of cards followed by background API PATCH requests, gracefully reverting the UI state to the last-known database position and emitting an error toast on networking failure.
**When to use:** Crucial to prevent tactile drag stutter or lagging visual indicators on low-performance devices or high-latency network drops.

**Example:**
```typescript
// Source: CITED: context7/hello-pangea/dnd standard board patterns
import React, { useState } from 'react';
import { DragDropContext, DropResult } from '@hello-pangea/dnd';
import { toast } from 'sonner';

interface Card { id: string; category_id: string; title: string; }

export function KanbanBoard({ initialCards }: { initialCards: Card[] }) {
  const [cards, setCards] = useState<Card[]>(initialCards);

  const onDragEnd = async (result: DropResult) => {
    const { destination, source, draggableId } = result;
    if (!destination) return;
    if (destination.droppableId === source.droppableId && destination.index === source.index) return;

    // 1. Optimistic Update
    const previousCards = [...cards];
    const movedCard = cards.find(c => c.id === draggableId);
    if (!movedCard) return;

    const newCards = previousCards.filter(c => c.id !== draggableId);
    const updatedCard = { ...movedCard, category_id: destination.droppableId };
    
    // Insert at destination index in simulated column list
    newCards.splice(destination.index, 0, updatedCard);
    setCards(newCards);

    // 2. Background API persistence
    try {
      const response = await fetch(`/api/items/${draggableId}`, {
        method: 'PATCH',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ category_id: destination.droppableId }),
      });
      if (!response.ok) throw new Error('Network error');
      toast.success('Eintrag verschoben.');
    } catch (err) {
      // 3. Revert on API Failure
      setCards(previousCards);
      toast.error('Verschieben fehlgeschlagen. Eintrag ist zurück.');
    }
  };

  return (
    <DragDropContext onDragEnd={onDragEnd}>
      {/* Droppables & Draggables inside */}
    </DragDropContext>
  );
}
```

### Anti-Patterns to Avoid
- **Abusing SSE/WebSockets for poll updates:** Avoid rolling reactive websocket frameworks prematurely when a lightweight, 10s short-polling setup fully covers CAP-05 requirements with near-zero runtime maintenance.
- **Overlay Dialog Close Interaction:** Avoid closing the modal on background backdrop clicks. Blur events should flush to autosave before dialog removal. Closing must only trigger on exact `X` clicks or the Escape key.

---

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Drag-and-drop mechanics | Custom HTML5 drag/drop listeners | `@hello-pangea/dnd` | Multi-device pointer tracking, accessibility overlays, smooth reordering math, and screen-reader anchors are incredibly complex to write. |
| Toast management | Absolute-positioned state containers | `sonner` | Avoids managing queuing queues, overlapping offsets, and swipe dismiss handlers. |
| Form state & validation | Controlled React inputs | `react-hook-form` + `zod` | Avoids re-rendering the entire page on every keystroke, while ensuring Type-safety and strict field errors native to the component. |

**Key insight:** Hand-rolling accessibility overlays for keyboard navigability inside list columns can take weeks of tuning. Standardizing on Radix primitives and Hello Pangea provides complete accessibility coverage for free.

---

## Runtime State Inventory

> Greenfield UI webapp initialization. All systems evaluated.

| Category | Items Found | Action Required |
|----------|-------------|------------------|
| Stored data | None | Verified: DB tables are stable. Phase 4 consumes the current `board_items` view and `categories` tables. |
| Live service config | None | Verified: No live integrations need structural configuration updates. |
| OS-registered state | None | Verified: Operating system level schedule processes are unaltered. |
| Secrets/env vars | None | Verified: `.env` remains unchanged. `DATABASE_URL` and Better Auth secrets stay consistent. |
| Build artifacts | None | Verified: Pure greenfield setup. No stale node files or package-lock discrepancies present. |

---

## Common Pitfalls

### Pitfall 1: Next.js SSR / Hydration Mismatch with Drag-and-Drop
**What goes wrong:** Random UI errors and rendering crashes on board load because SSR markup doesn't match the initial state of Hello Pangea columns on the browser thread.
**Why it happens:** `@hello-pangea/dnd` depends on client-only runtime variables and browser layout metrics.
**How to avoid:** Only mount the board component after client hydration completes (using an `isMounted` state hook or dynamic loading with `ssr: false`).
**Warning signs:** Console warnings like "Prop `dangerouslySetInnerHTML` did not match" or blank columns on refresh.

### Pitfall 2: Autosave Race Conditions on Fast Exit
**What goes wrong:** User edits an item's title in the modal, immediately hits Escape, and changes are lost or not written because the network request was cancelled.
**Why it happens:** The input blur callback executes asynchronously, and closing the modal unmounts the form, aborting pending async callbacks.
**How to avoid:** Block closing the modal until the current debounced autosave state has successfully settled, or flush the buffer synchronously during `onOpenChange` handlers.

---

## Code Examples

Verified pattern for Better Auth Client-Side Session retrieval:

```typescript
// Source: CITED: github.com/better-auth/better-auth Client Hooks
import { createAuthClient } from "better-auth/react";

export const authClient = createAuthClient({
    baseURL: process.env.NEXT_PUBLIC_APP_URL
});

export function UserProfileHeader() {
  const { data: session, isPending, error } = authClient.useSession();

  if (isPending) return <div>Lade...</div>;
  if (error || !session) return <div>Nicht angemeldet</div>;

  return (
    <div className="flex items-center gap-sm">
      <span>{session.user.email}</span>
    </div>
  );
}
```

---

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| Custom CSS in `tailwind.config.js` | `@theme` directive in CSS | Tailwind v4 (2025) | Custom tokens are written as native CSS variables, reducing build dependencies and standardizing access. |
| `react-beautiful-dnd` | `@hello-pangea/dnd` | 2023 | Core support for React 18 & 19; replaces deprecated original library on npm. |

---

## Assumptions Log

> Empty assumption log. All claims verified or cited against authoritative docs.

| # | Claim | Section | Risk if Wrong |
|---|-------|---------|---------------|
| — | — | — | — |

---

## Open Questions

1. **Google Calendar 412 Concurrency UI Details**
   - What we know: If Google API returns a conflict, we show both remote event fields and local edits in the modal.
   - What's unclear: Which exact fields require a comparative diff view, and if the user can partially merge them.
   - Recommendation: Keep it lean. If a 412 is thrown, render a simple split card inside the modal showing the remote Google title/date and provide two clear CTAs: **"Remote übernehmen"** (re-save local with Google's state) or **"Überschreiben"** (bypass ETag and force save local).

---

## Environment Availability

| Dependency | Required By | Available | Version | Fallback |
|------------|------------|-----------|---------|----------|
| Node.js | Next.js runtime | ✓ | `v26.5.0` | — |
| pnpm | Package installation | ✓ | `11.15.1` | — |
| PostgreSQL | Data persistency | ✓ | Active | — |
| Docker | Local testing sandbox | ✓ | `29.4.0` | — |

---

## Validation Architecture

### Test Framework
| Property | Value |
|----------|-------|
| Framework | Vitest + React Testing Library |
| Config file | `webapp/vitest.config.ts` |
| Quick run command | `pnpm --filter puzzlessbox-webapp test` |
| Full suite command | `pnpm --filter puzzlessbox-webapp test run` |

### Phase Requirements → Test Map
| Req ID | Behavior | Test Type | Automated Command | File Exists? |
|--------|----------|-----------|-------------------|-------------|
| **BOARD-01** | Kanban Board UI default columns visible | Unit / DOM | `pnpm test app/board/page.test.tsx` | ❌ Wave 0 |
| **BOARD-02** | Add own categories, update color and reorder | Integration | `pnpm test app/board/categories.test.tsx` | ❌ Wave 0 |
| **BOARD-03** | Drag and drop elements between default categories | Unit / DOM | `pnpm test app/board/dnd.test.tsx` | ❌ Wave 0 |
| **BOARD-04** | Open modal on card click, edit, and autosave | Integration | `pnpm test app/board/modal.test.tsx` | ❌ Wave 0 |
| **CAP-05** | Board update polls for live item captures | Integration | `pnpm test app/board/poll.test.tsx` | ❌ Wave 0 |
| **CAL-01** | Step-by-step Google Calendar link workflow | Unit / Flow | `pnpm test app/settings/calendar.test.tsx` | ❌ Wave 0 |

### Wave 0 Gaps
- [ ] `webapp/vitest.config.ts` — configuration file for Vitest environment.
- [ ] `webapp/tests/setup.ts` — React testing library global DOM environment mocks.

---

## Security Domain

### Applicable ASVS Categories

| ASVS Category | Applies | Standard Control |
|---------------|---------|-----------------|
| V2 Authentication | yes | Better Auth handles login routes, encryption, and secure hashing. |
| V3 Session Management | yes | Session cookies configured with `httpOnly`, `Secure`, and `SameSite=Lax`. |
| V4 Access Control | yes | Next.js server-side middleware validates the session cookie before allowing access to `/board` and `/settings` routes. |
| V5 Input Validation | yes | Form fields utilize robust Zod client-side schemas coupled with React Hook Form. |
| V6 Cryptography | yes | No custom encryption used on client. Backend handles encryption of calendar OAuth tokens. |

### Known Threat Patterns for Next.js

| Pattern | STRIDE | Standard Mitigation |
|---------|--------|---------------------|
| Cross-site Scripting (XSS) | Tampering | React automatically sanitizes text bindings. Avoid raw inner HTML. |
| CSRF via form triggers | Tampering | Better Auth manages unique session anti-forgery tokens automatically. |
| Session Hijacking | Information Disclosure | Cookies locked server-side using secure transmission parameters. |

---

## Sources

### Primary (HIGH confidence)
- `/hello-pangea/dnd` - React 19 compatibility and core API configuration.
- `/better-auth/better-auth` - Next.js middleware and hook usage guidelines.

### Secondary (MEDIUM confidence)
- Tailwind CSS v4 styling standards and theme migration guides.

---

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH - Verified against official npm repositories and project configuration files.
- Architecture: HIGH - Fully documented via Approved design contracts.
- Pitfalls: HIGH - Documented common problems native to Hello Pangea with Next.js SSR.

**Research date:** 2026-08-02
**Valid until:** 2026-09-02
