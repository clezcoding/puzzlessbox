# Phase 4: WebApp - Pattern Map

**Mapped:** 2026-08-02
**Files analyzed:** 10 new/modified files
**Analogs found:** 5 / 10

## File Classification

| New/Modified File | Role | Data Flow | Closest Analog | Match Quality |
|-------------------|------|-----------|----------------|---------------|
| `webapp/app/globals.css` | config / style | static | `brand/tokens.css` | exact |
| `webapp/app/layout.tsx` | provider / layout | request-response | None (greenfield) | n/a |
| `webapp/app/page.tsx` | controller / route | request-response | None (greenfield) | n/a |
| `webapp/app/board/page.tsx` | controller / route / component | CRUD / polling | None (greenfield) | n/a |
| `webapp/app/login/page.tsx` | controller / route / component | request-response (auth) | None (greenfield) | n/a |
| `webapp/app/settings/page.tsx` | controller / route / component | request-response / form | None (greenfield) | n/a |
| `webapp/components/board/board-column.tsx` | component | CRUD / drag-and-drop | None (greenfield) | n/a |
| `webapp/components/board/board-card.tsx` | component | CRUD / drag-and-drop | None (greenfield) | n/a |
| `webapp/components/settings/calendar-wizard.tsx` | component | form / wizard state machine | None (greenfield) | n/a |
| `webapp/lib/api-client.ts` | service / utility | request-response | `api/app/auth/jwt.py` | partial |

## Pattern Assignments

### `webapp/app/globals.css` (config / style, static)

**Analog:** `brand/tokens.css`

**CSS Theme Pattern** (lines 1-17):
```css
/* Puzzlessbox brand tokens — Utilitarian Bone + Apollo terracotta accent */

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
  --color-brand: #c45c3e;
  --color-brand-soft: #fce8e0;
  --color-accent: #c45c3e;
  --color-accent-soft: #fce8e0;
```

**Tailwind Integration Pattern** (from `brand/tailwind.preset.ts` lines 1-15):
```typescript
import type { Config } from 'tailwindcss';

export default {
  theme: {
    extend: {
      colors: {
        bg: 'var(--color-bg)',
        'bg-wash': 'var(--color-bg-wash)',
        surface: 'var(--color-surface)',
        'surface-soft': 'var(--color-surface-soft)',
        border: 'var(--color-border)',
        'border-strong': 'var(--color-border-strong)',
        text: 'var(--color-text)',
        'text-muted': 'var(--color-text-muted)',
        primary: 'var(--color-primary)',
```

---

### `webapp/lib/api-client.ts` (service / utility, request-response)

**Analog:** `api/app/auth/jwt.py`

**Auth Cookie Pattern** (lines 20, 60-66):
```python
SESSION_COOKIE = "puzzlessbox_session"
...
def _extract_bearer_token(
    request: Request,
    credentials: HTTPAuthorizationCredentials | None,
) -> str | None:
    if credentials and credentials.credentials:
        return credentials.credentials
    return request.cookies.get(SESSION_COOKIE)
```

**Client API Request Pattern** (to match FastAPI backend expectations):
```typescript
// Proposed implementation for webapp/lib/api-client.ts
export async function apiFetch<T>(endpoint: string, options: RequestInit = {}): Promise<T> {
  const baseUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
  const headers = new Headers(options.headers);
  
  // Credentials 'include' ensures browser forwards the session cookie automatically
  const response = await fetch(`${baseUrl}${endpoint}`, {
    ...options,
    credentials: 'include',
    headers,
  });
  
  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}));
    throw new Error(errorData?.detail?.message || 'API request failed');
  }
  
  return response.json() as Promise<T>;
}
```

---

### `webapp/app/board/page.tsx` (controller / route / component, CRUD / polling)

**Analog:** `api/app/routers/capture.py` & `api/app/routers/items.py`

**Board Items Fetch Pattern** (from `api/app/routers/capture.py` lines 294-309):
```python
@router.get("/board-items")
def list_board_items(db: Session = Depends(get_db_for_owner)) -> list[BoardItem]:
    owner_id = current_owner_id.get()
    rows = db.execute(
        text(
            """
            SELECT id, owner_id, category_id, status, title, summary, type,
                   created_at, updated_at, deleted_at
            FROM board_items
            WHERE owner_id = :owner_id
            ORDER BY created_at DESC
            """
        ),
        {"owner_id": owner_id},
    ).mappings()
    return [BoardItem.model_validate(dict(row)) for row in rows]
```

**Item Move Pattern** (from `api/app/routers/items.py` lines 41-71):
```python
@router.patch("/items/{item_id}")
def move_item(
    item_id: str,
    payload: ItemMove,
    db: Session = Depends(get_db_for_owner),
) -> dict[str, str]:
...
```

**Draft Patch Pattern** (from `api/app/routers/capture.py` lines 173-187):
```python
@router.patch("/drafts/{draft_id}")
async def patch_draft(
    draft_id: str,
    payload: DraftUpdate,
    db: Session = Depends(get_db_for_owner),
) -> dict[str, Any]:
...
```

**Proposed Client Polling & Optimistic Move Pattern** (from `04-RESEARCH.md` Pattern 1):
```typescript
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
  newCards.splice(destination.index, 0, updatedCard);
  setCards(newCards);

  // 2. Background API persistence
  try {
    await apiFetch(`/items/${draggableId}`, {
      method: 'PATCH',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ category_id: destination.droppableId }),
    });
    toast.success('Eintrag verschoben.');
  } catch (err) {
    // 3. Revert on API Failure
    setCards(previousCards);
    toast.error('Verschieben fehlgeschlagen. Eintrag ist zurück.');
  }
};
```

---

### `webapp/app/login/page.tsx` (controller / route / component, request-response)

**Analog:** `webapp/lib/auth.config.ts` & `api/app/routers/auth.py`

**Better Auth Server signup lock hook** (from `webapp/lib/auth.config.ts` lines 16-32):
```typescript
  databaseHooks: {
    user: {
      create: {
        before: async () => {
          const result = await pool.query<{ count: string }>(
            'SELECT count(*)::text AS count FROM "user"',
          );
          const count = Number.parseInt(result.rows[0]?.count ?? "0", 10);
          if (count > 0) {
            throw new APIError("CONFLICT", {
              message: "SIGNUP_LOCKED",
            });
          }
        },
      },
    },
  },
```

**Better Auth Client Hook Pattern** (from `04-RESEARCH.md` Code Examples):
```typescript
import { createAuthClient } from "better-auth/react";

export const authClient = createAuthClient({
    baseURL: process.env.NEXT_PUBLIC_APP_URL
});
```

---

## Shared Patterns

### Authentication
**Source:** `webapp/lib/auth.ts` & `webapp/lib/auth.config.ts`
**Apply to:** All client-side pages and API client requests.
Use `better-auth/react` client hooks for session tracking, and forward session cookies automatically using `credentials: 'include'` on fetch requests.

### Error Handling
**Source:** `api/app/core/errors.py` (FastAPI error shape)
**Apply to:** All API requests in `webapp/lib/api-client.ts`.
All API error responses from the backend follow the shape `{ error: { code, message, details? } }`. The frontend must parse this and display friendly German microcopy from `brand/VOICE.md` via `sonner` toasts.

### Styling & Tokens
**Source:** `brand/tokens.css` & `brand/tailwind.preset.ts`
**Apply to:** All components and pages.
Always use CSS variables from `brand/tokens.css` via Tailwind classes (e.g., `bg-bg`, `text-text`, `border-border`, `bg-brand`, `text-brand`). Do not hardcode hex colors.

## No Analog Found

Files with no close match in the codebase (planner should use RESEARCH.md and UI-SPEC.md patterns instead):

| File | Role | Data Flow | Reason |
|------|------|-----------|--------|
| `webapp/app/settings/page.tsx` | controller / route / component | request-response / form | No settings page or wizard components exist yet |
| `webapp/components/settings/calendar-wizard.tsx` | component | form / wizard state machine | No multi-step wizards exist yet |
| `webapp/app/layout.tsx` | provider / layout | request-response | Greenfield app layout |

## Metadata

**Analog search scope:** `webapp/`, `brand/`, `api/app/routers/`
**Files scanned:** 15 files
**Pattern extraction date:** 2026-08-02
