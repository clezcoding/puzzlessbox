# Phase 01: Datenmodell & Backend-API - Pattern Map

**Mapped:** 2026-07-30  
**Files analyzed:** 26  
**Analogs found:** 3 / 26 (Greenfield codebase, referenced from `01-RESEARCH.md` design patterns)

## File Classification

| New/Modified File | Role | Data Flow | Closest Analog | Match Quality |
|-------------------|------|-----------|----------------|---------------|
| `api/app/main.py` | entrypoint | request-response | none (greenfield) | none |
| `api/app/core/config.py` | config | static | none (greenfield) | none |
| `api/app/core/database.py` | config | CRUD | none (greenfield) | none |
| `api/app/core/security.py` | utility | transform | none (greenfield) | none |
| `api/app/auth/jwt.py` | middleware | request-response | `01-RESEARCH.md` (lines 225-251) | exact |
| `api/app/models/category.py` | model | CRUD | none (greenfield) | none |
| `api/app/models/note.py` | model | CRUD | none (greenfield) | none |
| `api/app/models/link.py` | model | CRUD | none (greenfield) | none |
| `api/app/models/task.py` | model | CRUD | none (greenfield) | none |
| `api/app/models/event.py` | model | CRUD | none (greenfield) | none |
| `api/app/models/board.py` | model | CRUD | none (greenfield) | none |
| `api/app/routers/capture.py` | controller | CRUD | none (greenfield) | none |
| `api/app/routers/notes.py` | controller | CRUD | none (greenfield) | none |
| `api/app/routers/links.py` | controller | CRUD | none (greenfield) | none |
| `api/app/routers/tasks.py` | controller | CRUD | none (greenfield) | none |
| `api/app/routers/events.py` | controller | CRUD | none (greenfield) | none |
| `api/app/routers/health.py` | controller | request-response | none (greenfield) | none |
| `api/app/services/timeout.py` | service | event-driven | `01-RESEARCH.md` (lines 287-322) | exact |
| `api/app/services/scraper.py` | service | transform | none (greenfield) | none |
| `api/app/services/calendar.py` | service | event-driven | `01-RESEARCH.md` (lines 325-352) | exact |
| `api/requirements.txt` | config | static | none (greenfield) | none |
| `api/Dockerfile` | config | static | none (greenfield) | none |
| `api/alembic.ini` | config | static | none (greenfield) | none |
| `api/tests/conftest.py` | test | setup | none (greenfield) | none |
| `api/tests/integration/` | test | batch | none (greenfield) | none |
| `api/tests/unit/` | test | batch | none (greenfield) | none |

---

## Pattern Assignments

### `api/app/auth/jwt.py` (middleware, request-response)

**Analog:** `01-RESEARCH.md` (lines 225-251)

**Imports & Initialization pattern** (lines 231-233 in `01-RESEARCH.md`):
```python
import jwt
from fastapi import Depends, HTTPException, Security, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

security = HTTPBearer(auto_error=True)
jwks_url = "http://webapp:3000/api/auth/jwks"  # Internal Next.js Better Auth path
jwks_client = jwt.PyJWKClient(jwks_url, cache_jwk_set=True, lifespan=300)
```

**Token verification & Owner Extraction pattern** (lines 235-251 in `01-RESEARCH.md`):
```python
async def get_current_owner(credentials: HTTPAuthorizationCredentials = Security(security)) -> str:
    token = credentials.credentials
    try:
        signing_key = jwks_client.get_signing_key_from_jwt(token)
        payload = jwt.decode(
            token,
            signing_key.key,
            algorithms=["RS256"],
            options={"verify_exp": True}
        )
        owner_id = payload.get("sub")
        if not owner_id:
            raise HTTPException(status_code=401, detail="Invalid token: missing subject.")
        return owner_id
    except jwt.PyJWTError as e:
        raise HTTPException(status_code=401, detail=f"Authentication failed: {str(e)}")
```

---

### `api/app/services/timeout.py` (service, event-driven)

**Analog:** `01-RESEARCH.md` (lines 287-322)

**In-Memory asyncio.Task timer pattern** (lines 292-322 in `01-RESEARCH.md`):
```python
import asyncio
from typing import Dict

class DraftTimeoutManager:
    def __init__(self):
        self._active_tasks: Dict[str, asyncio.Task] = {}

    def schedule_timeout(self, draft_id: str, owner_id: str, delay_seconds: float = 30.0):
        self.cancel_timeout(draft_id)
        
        # Spawn non-blocking background task
        task = asyncio.create_task(self._wait_and_autosave(draft_id, owner_id, delay_seconds))
        self._active_tasks[draft_id] = task

    def cancel_timeout(self, draft_id: str):
        task = self._active_tasks.pop(draft_id, None)
        if task and not task.done():
            task.cancel()

    async def _wait_and_autosave(self, draft_id: str, owner_id: str, delay_seconds: float):
        try:
            await asyncio.sleep(delay_seconds)
            await self._execute_autosave(draft_id, owner_id)
        except asyncio.CancelledError:
            pass  # Expected when draft is confirmed or edited
        finally:
            self._active_tasks.pop(draft_id, None)

    async def _execute_autosave(self, draft_id: str, owner_id: str):
        # Database transaction goes here: update status from 'draft' to 'auto_saved'
        pass

draft_timeout_manager = DraftTimeoutManager()
```

---

### `api/app/services/calendar.py` (service, event-driven)

**Analog:** `01-RESEARCH.md` (lines 325-352)

**Google Calendar optimistic concurrency update pattern** (lines 331-352 in `01-RESEARCH.md`):
```python
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from fastapi import HTTPException

def update_calendar_event(service, calendar_id: str, event_id: str, etag: str, event_body: dict):
    try:
        request = service.events().update(
            calendarId=calendar_id,
            eventId=event_id,
            body=event_body
        )
        # Inject If-Match header with current version etag
        request.headers["If-Match"] = etag
        return request.execute()
    except HttpError as e:
        if e.resp.status == 412:
            raise HTTPException(
                status_code=412,
                detail={
                    "error": {
                        "code": "CONCURRENCY_CONFLICT",
                        "message": "The calendar event has been modified externally.",
                        "details": {"etag": etag}
                    }
                }
            )
        raise e
```

---

## Shared Patterns

### Authentication & Tenant Isolation
**Source:** `01-RESEARCH.md` (lines 235-251) & `01-CONTEXT.md` (line 51)  
**Apply to:** All database CRUD endpoints & Routers  
All routes requiring multi-tenant safety must resolve the `owner_id` via `get_current_owner` dependency injection, passing it down to filter SQLModel database queries or leveraging active PostgreSQL Row-Level Security policies.
```python
@router.get("/items")
async def read_items(
    db: Session = Depends(get_db), 
    owner_id: str = Depends(get_current_owner)
):
    # App-level owner filter as defense-in-depth along with database-level RLS
    items = db.exec(select(BoardItem).where(BoardItem.owner_id == owner_id)).all()
    return {"data": items}
```

### Unified Error Handling
**Source:** `01-CONTEXT.md` (line 59)  
**Apply to:** Centralized exception handlers inside `api/app/main.py` and routers  
All errors must strictly follow the standard schema: `{ "error": { "code", "message", "details?" } }`.
```python
from fastapi import Request
from fastapi.responses import JSONResponse

@app.exception_handler(HTTPException)
async def custom_http_exception_handler(request: Request, exc: HTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": {
                "code": exc.detail.get("code", "API_ERROR") if isinstance(exc.detail, dict) else "API_ERROR",
                "message": exc.detail.get("message", exc.detail) if isinstance(exc.detail, dict) else exc.detail,
                "details": exc.detail.get("details") if isinstance(exc.detail, dict) else None
            }
        }
    )
```

### Encryption of Third-Party Credentials at Rest
**Source:** `01-CONTEXT.md` (line 39) & `01-RESEARCH.md` (lines 111-112)  
**Apply to:** Google OAuth refresh and access tokens storage in Postgres  
```python
import os
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

# encryption_key is loaded from environment variables (Coolify secret)
ENCRYPTION_KEY = os.environ["ENCRYPTION_KEY"]

def encrypt_token(plain_text: str) -> str:
    aesgcm = AESGCM(ENCRYPTION_KEY.encode())
    nonce = os.urandom(12)
    ct = aesgcm.encrypt(nonce, plain_text.encode(), None)
    return (nonce + ct).hex()

def decrypt_token(cipher_text_hex: str) -> str:
    data = bytes.fromhex(cipher_text_hex)
    nonce = data[:12]
    ct = data[12:]
    aesgcm = AESGCM(ENCRYPTION_KEY.encode())
    return aesgcm.decrypt(nonce, ct, None).decode()
```

---

## No Analog Found

Since the codebase currently has **no Python files**, there are no local pre-existing analogs for the following essential components. The planner and implementer should follow standard clean-architecture patterns and use the design specs in `01-RESEARCH.md` and `01-CONTEXT.md`.

| File | Role | Data Flow | Reason / Guideline |
|------|------|-----------|--------------------|
| `api/app/services/scraper.py` | service | transform | Web scraper using self-hosted Firecrawl (8s timeout) and Camoufox sidecar fallback (4s timeout). |
| `api/app/models/board.py` | model | CRUD | Union database VIEW (`board_items`) for `notes`, `links`, `tasks`, and `events`. |
| `api/app/core/database.py` | config | CRUD | Configures SQLModel PostgreSQL engines and defines DB session generators. |
| `api/tests/conftest.py` | test | setup | Pytest config establishing transactional test database sessions and auth mocks. |

---

## Metadata

**Analog search scope:** `.planning/phases/01-datenmodell-backend-api/`, `brand/`  
**Files scanned:** 2  
**Pattern extraction date:** 2026-07-30  
