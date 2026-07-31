# Phase 2: MCP-Server - Pattern Map

**Mapped:** 2026-07-31
**Files analyzed:** 23 (17 new `mcp-server/`, 5 new/modified `api/`, 1 new deploy workflow)
**Analogs found:** 22 / 23 (1 greenfield: GHCR deploy workflow — kein Repo-Vorbild)

Greenfield-Kontext: `mcp-server/` neu; nächste Analoga leben unter `api/`. MCP ist dünner
Proxy — jede Item-Logik bleibt API. Analoga liefern Bootstrap-, Auth-, httpx-, Router-,
Dockerfile- und Test-Muster; **nicht** DB-Zugriff in MCP (D-06).

## File Classification

| New/Modified File | Role | Data Flow | Closest Analog | Match Quality |
|-------------------|------|-----------|----------------|---------------|
| `mcp-server/app/server.py` | config/bootstrap | request-response | `api/app/main.py` | role-match |
| `mcp-server/app/config.py` | config | — | `api/app/core/config.py` | exact |
| `mcp-server/app/auth.py` | middleware (TokenVerifier) | request-response | `api/app/auth/jwt.py` (`_resolve_service_owner`) | role-match |
| `mcp-server/app/api_client.py` | service (httpx client) | request-response | `api/app/services/scraper.py` + `api/app/routers/auth.py` (`_map_better_auth_error`) | role-match |
| `mcp-server/app/health.py` | route | request-response | `api/app/routers/health.py` | exact |
| `mcp-server/app/tools/items.py` | controller (tools) | CRUD | `api/app/routers/capture.py` | role-match |
| `mcp-server/app/tools/categories.py` | controller (tools) | CRUD | `api/app/routers/capture.py` | role-match |
| `mcp-server/app/tools/__init__.py` | config (register) | — | `api/app/routers/__init__.py` | role-match |
| `mcp-server/requirements.txt` | config | — | `api/requirements.txt` | exact |
| `mcp-server/Dockerfile` | config | — | `api/Dockerfile` | exact (ohne alembic) |
| `mcp-server/pytest.ini` | config (test) | — | `api/tests/conftest.py` (asyncio_mode) | partial |
| `mcp-server/tests/conftest.py` | test | — | `api/tests/conftest.py` | role-match |
| `mcp-server/tests/test_auth.py` | test | request-response | `api/tests/*/test_auth.py` + conftest | role-match |
| `mcp-server/tests/test_api_contract.py` | test | request-response | `api/tests/conftest.py` (`MockTransport`) | role-match |
| `mcp-server/tests/test_tools_schema.py` | test | — | `api/tests/unit/test_models.py`* | role-match |
| `mcp-server/tests/test_health.py` | test | request-response | `api/tests/unit/test_health.py`* | role-match |
| `api/app/routers/internal.py` (NEU) | controller | request-response | `api/app/auth/jwt.py` (`_resolve_service_owner`) + `api/app/routers/auth.py` | role-match |
| `api/app/routers/categories.py` (NEU) | controller | CRUD | `api/app/routers/capture.py` | exact |
| `api/app/routers/items.py` move (NEU) | controller | CRUD | `api/app/routers/capture.py` (`patch_draft`/`_apply_draft_patch`) | exact |
| `api/app/models/mcp_client.py` (NEU) | model | — | `api/app/models/service_principal.py` | exact |
| `api/alembic/versions/0004_mcp_clients.py` (NEU) | migration | — | `api/alembic/versions/0002_idempotency.py` + `0001` (RLS/GRANT) | role-match |
| `api/app/core/bootstrap.py` (MOD) | utility | — | `api/app/core/bootstrap.py` (`ensure_service_principal`) | exact |
| `.github/workflows/deploy-mcp.yml` (NEU) | config (CI/CD) | — | **KEIN Analog** (nur `ci.yml`-Skelett) | none |

\* Analog-Datei nicht gelesen (Standard-pytest-Struktur; Test-Muster aus `conftest.py` ableitbar).

Auch modifiziert (Router-Registrierung + Config): `api/app/main.py` (`include_router`),
`api/app/core/config.py` (neue MCP-Bootstrap-Vars). Muster trivial — siehe Shared Patterns.

## Pattern Assignments

### `mcp-server/app/server.py` (config/bootstrap, request-response)

**Analog:** `api/app/main.py`

App-Factory + Modul-Level-`app` Muster (lines 47-86). MCP-Äquivalent: `FastMCP(...)` statt
`FastAPI(...)`, `mcp.http_app(...)` statt `create_app()`. Health via `custom_route` (siehe
`health.py`), Tools via `register_tools(mcp)` (statt `include_router`).

**App-Factory + module-level app** (`api/app/main.py` lines 47-86):

```47:86:api/app/main.py
def create_app() -> FastAPI:
    settings = get_settings()
    docs_url = None if settings.is_prod else "/docs"
    redoc_url = None if settings.is_prod else "/redoc"

    application = FastAPI(
        title="Puzzlessbox API",
        lifespan=_lifespan,
        docs_url=docs_url,
        redoc_url=redoc_url,
    )
    application.add_middleware(AcceptVersionMiddleware)
    application.include_router(health.router)
    application.include_router(auth.router)
    application.include_router(capture.router)
    ...
    return application


app = create_app()
```

MCP-Ziel (aus RESEARCH Pattern 1): `mcp = FastMCP(name=..., auth=verifier)`;
`app = mcp.http_app(path="/mcp", stateless_http=True, allowed_hosts=["mcp.puzzlesstool.online"])`.
uvicorn-CMD spiegelt Dockerfile (`uvicorn app.server:app --host 0.0.0.0 --port 8000`).

**API_VERSION_ACCEPT-Konstante wiederverwenden** (line 16) — MCP-httpx-Client sendet exakt diesen String:

```16:16:api/app/main.py
API_VERSION_ACCEPT = "application/vnd.puzzlessbox.v1+json"
```

---

### `mcp-server/app/config.py` (config)

**Analog:** `api/app/core/config.py` (exact)

`pydantic_settings.BaseSettings` + `.env` + `@lru_cache get_settings()`. Kopiere Struktur,
tausche Felder. MCP braucht: `SERVICE_BEARER_TOKEN`, `MCP_API_BASE_URL`
(`http://puzzlessbox-api:8000`, D-15), `ENV`, optional `MCP_BOOTSTRAP_TOKEN`/`SERVICE_OWNER_ID`
(nur wenn MCP Bootstrap triggert — laut D-07 macht API/Alembic den Insert, MCP evtl. nur env-pass).

```1:43:api/app/core/config.py
from functools import lru_cache

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    DATABASE_URL: str = "postgresql+psycopg2://postgres:postgres@localhost:5432/puzzlessbox"
    ...
    SERVICE_BEARER_TOKEN: str = "change-me-service-bearer"
    ...
    ENV: str = "dev"
    ...

    @property
    def is_prod(self) -> bool:
        return self.ENV.lower() == "prod"


@lru_cache
def get_settings() -> Settings:
    return Settings()
```

MCP: **kein** `DATABASE_URL` (D-06, keine DB-Connection).

---

### `mcp-server/app/auth.py` (middleware / TokenVerifier, request-response)

**Analog:** `api/app/auth/jwt.py` — `_resolve_service_owner` (lines 67-87)

Kern-Übernahme: sha256-Hash des präsentierten Bearer + Owner-Lookup. **Unterschied:** MCP
öffnet keine DB — statt `SELECT ... FROM service_principals` ruft es `POST /internal/mcp-auth`
(D-06). `hmac.compare_digest` bleibt Muster falls ein lokaler Vergleich nötig; primär aber
Hash → interne API. RESEARCH Pattern 2 gibt `OwnerResolvingVerifier(TokenVerifier)`-Signatur.

**sha256 + owner-resolve + reject** (`api/app/auth/jwt.py` lines 67-87):

```67:87:api/app/auth/jwt.py
def _resolve_service_owner(service_bearer: str) -> str:
    settings = get_settings()
    if not hmac.compare_digest(service_bearer, settings.SERVICE_BEARER_TOKEN):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"code": "UNAUTHORIZED", "message": "Invalid service bearer token."},
        )

    bearer_hash = hashlib.sha256(service_bearer.encode()).hexdigest()
    with Session(get_engine()) as session:
        owner_id = session.execute(
            text("SELECT owner_id FROM service_principals WHERE bearer_hash = :hash LIMIT 1"),
            {"hash": bearer_hash},
        ).scalar_one_or_none()

    if not owner_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"code": "UNAUTHORIZED", "message": "Service principal not configured."},
        )
    return str(owner_id)
```

MCP-Verifier: `bearer_hash = hashlib.sha256(token.encode()).hexdigest()` →
`await api_client.resolve_owner(bearer_hash)` → `None` gibt FastMCP RFC-6750-401
(nicht `HTTPException` — TokenVerifier gibt `AccessToken | None`, siehe RESEARCH Pattern 2).
**Nie Plaintext-Token loggen** (D-07, Pitfall 1).

---

### `mcp-server/app/api_client.py` (service / httpx client, request-response)

**Analog:** `api/app/services/scraper.py` (httpx-Muster) + `api/app/routers/auth.py` (`_map_better_auth_error`)

httpx.AsyncClient-Instanziierung, Timeout, `httpx.HTTPError`-Handling: `scraper.py` lines
119-167. Fehler-Mapping API→Tool (D-13): `auth.py` `_map_better_auth_error` lines 41-66 ist
das nächste Analog (liest `resp.json()`, mappt code/message, kein Roh-Dump). RESEARCH
Pattern 4/5 gibt die MCP-Zielform (`call_api` + `_to_tool_error` → `ToolError`).

**httpx client + auth-header + error-swallow** (`api/app/services/scraper.py` lines 119-167):

```119:167:api/app/services/scraper.py
def _auth_headers(bearer: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {bearer}"}


class ScrapeService:
    def __init__(self, settings: Settings | None = None) -> None:
        self._settings = settings or get_settings()
    ...
    async def _scrape_firecrawl(self, url: str) -> dict[str, str | None] | None:
        base = self._settings.FIRECRAWL_URL.rstrip("/")
        ...
        try:
            async with httpx.AsyncClient(timeout=FIRECRAWL_TIMEOUT) as client:
                response = await client.post(
                    f"{base}/v1/scrape",
                    headers=_auth_headers(self._settings.FIRECRAWL_BEARER),
                    json={"url": url, "formats": ["html"]},
                )
                if response.status_code >= 400:
                    return None
                payload = response.json()
        except (httpx.HTTPError, ValueError):
            return None
```

**Fehler-Mapping API→Client** (`api/app/routers/auth.py` lines 41-66) — nächstes Analog für `_to_tool_error`:

```41:66:api/app/routers/auth.py
def _map_better_auth_error(resp: httpx.Response) -> HTTPException:
    try:
        body = resp.json()
    except ValueError:
        body = {}

    message = ""
    if isinstance(body, dict):
        message = str(body.get("message") or body.get("error") or "")
        if not message and isinstance(body.get("error"), dict):
            message = str(body["error"].get("message") or "")
    ...
    return HTTPException(
        status_code=resp.status_code,
        detail={
            "code": "AUTH_ERROR",
            "message": message or "Authentication request failed.",
            "details": body if body else None,
        },
    )
```

MCP-Ziel: `raise ToolError(f"{code}: {message}")` (kein `HTTPException`). Header immer
`Accept` (=`API_VERSION_ACCEPT`), `X-Service-Bearer`, `X-Owner-Id`; `Idempotency-Key` nur
`create_item` (D-16). Timeout `httpx.Timeout(15.0)` (D-17). Retry: **manuelle** Schleife
`range(2)` nur auf 502/503 (D-18; httpx-Transport-`retries` deckt das NICHT — RESEARCH
Anti-Pattern). API-Fehlershape verifiziert: `{"error":{"code","message","details?}}` (siehe
`api/app/core/errors.py` unten).

---

### `mcp-server/app/health.py` (route, request-response)

**Analog:** `api/app/routers/health.py` (exact)

`/health` = statisch 200. `/ready` = Dependency-Ping (hier API statt DB/scraper), 503 bei
down. MCP nutzt `@mcp.custom_route("/health", methods=["GET"])` → `JSONResponse` (RESEARCH
Pattern 1) statt `APIRouter`, aber Logik identisch.

```11:44:api/app/routers/health.py
@router.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@router.get("/ready")
async def ready() -> JSONResponse:
    if not check_db_connection():
        return JSONResponse(
            status_code=503,
            content={
                "error": {
                    "code": "SERVICE_UNAVAILABLE",
                    "message": "Database is not ready",
                }
            },
        )
    ...
    return JSONResponse(status_code=200, content={"status": "ready"})
```

MCP `/ready`: `await api_client` GET `/health` → 503 wenn API down (D-22). Beide Routes
unauth (FastMCP `custom_route` umgeht `RequireAuthMiddleware`).

---

### `mcp-server/app/tools/items.py` (controller/tools, CRUD)

**Analog:** `api/app/routers/capture.py`

Tools mappen 1:1 auf capture-Endpunkte. Owner **nie** aus Tool-Input — aus Token-Claim
(`get_access_token().claims["owner_id"]`, RESEARCH Pattern 3, Anti-Pattern Tenant-Leak).
Payload-Shapes verifiziert gegen `DraftCreate`/`DraftUpdate`.

**Endpunkte, die Tools aufrufen** (`api/app/routers/capture.py` lines 127-221):

```127:132:api/app/routers/capture.py
@router.post("/drafts", status_code=status.HTTP_201_CREATED)
async def create_draft(
    payload: DraftCreate,
    db: Session = Depends(get_db_for_owner),
    idempotency_key: str | None = Header(default=None, alias="Idempotency-Key"),
) -> dict[str, Any]:
```

```173:194:api/app/routers/capture.py
@router.patch("/drafts/{draft_id}")
async def patch_draft(
    draft_id: str,
    payload: DraftUpdate,
    db: Session = Depends(get_db_for_owner),
) -> dict[str, Any]:
    ...

@router.post("/drafts/{draft_id}/confirm")
async def confirm_draft(
    draft_id: str,
    db: Session = Depends(get_db_for_owner),
) -> dict[str, Any]:
```

Tool→API (verifiziert): `create_item`→`POST /drafts` (D-09, +`Idempotency-Key`);
`confirm_item`→ optional `PATCH /drafts/{id}` dann `POST /drafts/{id}/confirm` (D-10);
`update_item`→`PATCH /drafts/{id}` (D-12, `draft|auto_saved`); `move_item`→ **NEU**
`PATCH /items/{id}` `{category_id}`. Tool-Schemas via `Annotated[..., Field()]`, `type` als
`Literal["note","link","task","event"]` (RESEARCH Code Examples).

**Request-Shapes** (`api/app/models/note.py` lines 18-32):

```18:32:api/app/models/note.py
class DraftCreate(SQLModel):
    """Capture draft payload validation (CAP-01, D-02, D-30)."""

    title: str
    type: ItemType
    category_id: uuid.UUID
    summary: str = ""


class DraftUpdate(SQLModel):
    title: str | None = None
    summary: str | None = None
    category_id: uuid.UUID | None = None
```

---

### `mcp-server/app/tools/categories.py` (controller/tools, CRUD)

**Analog:** `api/app/routers/capture.py` (Tool-Struktur) + neuer `api/app/routers/categories.py`

`list_categories`→`GET /categories`, `create_category`→`POST /categories`. Beide Endpunkte
**neu API-seitig** (siehe unten). Tool-Muster identisch zu `items.py` (owner aus claim, httpx
via api_client).

---

### `api/app/routers/internal.py` (NEU — controller, request-response)

**Analog:** `api/app/auth/jwt.py` `_resolve_service_owner` (lines 67-87) + `api/app/routers/auth.py` router-struktur

`POST /internal/mcp-auth`: Body `{bearer_hash}` → validiert Service-Bearer-Header + lookup
`mcp_clients` (active|grace, expiry-Check, D-04) → `{owner_id}`. Kombiniert jwt.py Hash-Lookup
mit auth.py `/verify` Response-Shape (`{"owner_id": ...}`, line 133-135).

```133:135:api/app/routers/auth.py
@router.get("/verify")
async def verify(owner_id: str = Depends(get_current_owner)) -> dict[str, str]:
    return {"owner_id": owner_id}
```

Guard D-08: X-Owner-Id nur gültig wenn UUID-Format UND Better-Auth `user`-Row existiert →
Lookup gegen `user`-Tabelle (Better Auth owns it, kein FK — siehe migration 0001 header).
Muss in `get_current_owner`/service-path integriert werden (`api/app/auth/jwt.py`).

---

### `api/app/routers/categories.py` (NEU — controller, CRUD)

**Analog:** `api/app/routers/capture.py` (exact — Router-Struktur, `get_db_for_owner`, `current_owner_id`, RLS)

`GET /categories` spiegelt `list_board_items` (lines 224-239): `Depends(get_db_for_owner)`,
`text()`-Query gefiltert per owner (RLS erlaubt NULL owner_id = System-Defaults, siehe
category model + migration 0001 policy). `POST /categories` spiegelt `create_draft`-Insert.

```224:239:api/app/routers/capture.py
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

**Category-Shape** (`api/app/models/category.py`): `id`, `owner_id` (nullable=System-Default),
`name` (unique), `created_at`. Discretion: color/sort-Felder für spätere BOARD (D-11) — nur
name minimal reicht jetzt.

---

### `api/app/routers/items.py` move-Endpoint (NEU — controller, CRUD)

**Analog:** `api/app/routers/capture.py` `_apply_draft_patch` (lines 45-88) / `patch_draft`

`PATCH /items/{id}` `{category_id}` (RESEARCH move-Empfehlung). Spiegelt category-move-Zweig
von `_apply_draft_patch`. Confirmed-Items: nur category (D-12) — `status`-Filter im WHERE
anpassen (nicht auf `draft|auto_saved` beschränken für move).

```66:88:api/app/routers/capture.py
    if payload.category_id is not None:
        updates.append("category_id = :category_id")
        params["category_id"] = str(payload.category_id)

    updates.append("updated_at = NOW()")
    result = db.execute(
        text(
            f"""
            UPDATE {table}
            SET {", ".join(updates)}
            WHERE id = :draft_id
              AND owner_id = :owner_id
              AND status IN ('draft', 'auto_saved')
            RETURNING id
            """
        ),
        params,
    )
    if result.scalar_one_or_none() is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"code": "NOT_FOUND", "message": "Draft not found."},
        )
```

Item-Typ→Tabelle via `table_for_item_type` (`api/app/services/timeout.py`, referenziert
in capture.py line 22) — move muss Typ via `board_items`-VIEW auflösen (`_lookup_draft_type`
Muster lines 27-42).

---

### `api/app/models/mcp_client.py` (NEU — model)

**Analog:** `api/app/models/service_principal.py` (exact)

Kopiere Struktur, erweitere um Rotation-Felder (D-04): `status` (`active|grace`), `expires_at`.

```11:17:api/app/models/service_principal.py
class ServicePrincipal(SQLModel, table=True):
    __tablename__ = "service_principals"

    owner_id: uuid.UUID = Field(primary_key=True)
    name: str
    bearer_hash: str
    created_at: datetime | None = None
```

MCP-Client: `id` PK (mehrere Rows pro owner für dual-token grace, **nicht** owner_id PK),
`owner_id`, `bearer_hash` (unique/index für Lookup), `status`, `expires_at`, `created_at`.
Discretion: exakte Spaltennamen + grace-TTL (CONTEXT D-04). Registriere in
`api/app/models/__init__.py` (siehe conftest import line 27).

---

### `api/alembic/versions/0004_mcp_clients.py` (NEU — migration)

**Analog:** `api/alembic/versions/0002_idempotency.py` (create_table + GRANT) + `0001` (RLS/policy)

`0002` gibt die minimale Migration-Vorlage; `0001` das GRANT/RLS-Muster falls mcp_clients
tenant-isoliert sein soll (owner_id-basiert).

```9:26:api/alembic/versions/0002_idempotency.py
revision: str = "0002_idempotency"
down_revision: Union[str, None] = "0001_initial_schema"
...
def upgrade() -> None:
    op.create_table(
        "idempotency_keys",
        sa.Column("owner_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("key", sa.Text(), nullable=False),
        sa.Column("response", postgresql.JSONB(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=BERLIN_NOW, nullable=False),
        sa.PrimaryKeyConstraint("owner_id", "key", name="pk_idempotency_keys"),
    )
    op.execute("GRANT SELECT, INSERT, UPDATE, DELETE ON idempotency_keys TO puzzlessbox_app")
```

`down_revision` = `"0003_calendar_tokens"` (letzte Migration). `BERLIN_NOW`-Timestamp-Muster
übernehmen. GRANT an `puzzlessbox_app`. Owner-Lookup braucht Index auf `bearer_hash`.
Alembic läuft in **API**-Image (MCP-Dockerfile hat kein alembic, D-07/RESEARCH).

---

### `api/app/core/bootstrap.py` (MODIFY — utility)

**Analog:** dieselbe Datei — `ensure_service_principal` (exact)

Solo-Bootstrap D-07: neue `ensure_mcp_client(settings)` spiegelt `ensure_service_principal`
exakt — idempotenter hash-only INSERT wenn `MCP_BOOTSTRAP_TOKEN`+`SERVICE_OWNER_ID` gesetzt
und `mcp_clients` leer. Nie Plaintext loggen (Muster hält sich schon dran, line 37 loggt nur
owner_id).

```17:37:api/app/core/bootstrap.py
def ensure_service_principal(settings: Settings) -> None:
    owner_id = settings.SERVICE_OWNER_ID.strip()
    if not owner_id:
        return

    bearer_hash = hashlib.sha256(settings.SERVICE_BEARER_TOKEN.encode()).hexdigest()
    with Session(get_engine()) as session:
        session.execute(
            text(
                """
                INSERT INTO service_principals (owner_id, name, bearer_hash, created_at)
                VALUES (CAST(:owner_id AS uuid), 'mcp', :bearer_hash, timezone('Europe/Berlin', now()))
                ON CONFLICT (owner_id) DO UPDATE
                SET bearer_hash = EXCLUDED.bearer_hash,
                    name = EXCLUDED.name
                """
            ),
            {"owner_id": owner_id, "bearer_hash": bearer_hash},
        )
        session.commit()
    logger.info("service_principal bootstrap ok for owner_id=%s", owner_id)
```

D-07-Abweichung: "nur wenn leer" (nicht ON CONFLICT UPDATE) — Bootstrap-Insert einmalig,
env danach löschbar. Wird aus `_lifespan` (`api/app/main.py` lines 41-44) aufgerufen.

---

### `mcp-server/tests/conftest.py` + tests (test)

**Analog:** `api/tests/conftest.py`

`httpx.MockTransport`-Fixture-Muster (lines 151-162) = Vorlage für interne-API-Mock in
`test_api_contract.py` (Header/Idempotency/Retry/Error-Map). ASGITransport-Muster (lines
214-230) = Vorlage falls kein In-Memory `Client(mcp)` (RESEARCH A1-Fallback).

```151:162:api/tests/conftest.py
@pytest.fixture
def mock_jwks_client() -> Generator[httpx.Client, None, None]:
    def handler(request: httpx.Request) -> httpx.Response:
        if request.url.path.endswith("/jwks"):
            return httpx.Response(200, json=MOCK_JWKS)
        return httpx.Response(404)

    transport = httpx.MockTransport(handler)
    with httpx.Client(transport=transport, base_url="http://mock-auth.test") as client:
        yield client
```

```214:230:api/tests/conftest.py
@pytest.fixture
async def async_api_client(mock_jwks_keypair: dict[str, Any]) -> AsyncClient:
    ...
    with patch("app.auth.jwt.get_jwks_client", return_value=_TestPyJWKClient()):
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            yield client
```

`pytest.ini`: `asyncio_mode = auto` (RESEARCH Wave 0). Test-Map siehe RESEARCH Validation
Architecture (401/403, schema-reject, header/idempotency/retry/error, health).

---

### `.github/workflows/deploy-mcp.yml` (NEU — GHCR deploy) — **KEIN ANALOG**

**Analog:** keiner. `ci.yml` baut nur Brand-Tests (node), **kein** Docker/GHCR-Build im Repo.
RESEARCH bestätigt: greenfield, "nicht mirror existing workflow". Nur Skelett-Muster
übernehmbar (concurrency, pinned action-SHAs, permissions):

```1:19:.github/workflows/ci.yml
name: CI

on:
  push:
    paths:
      - "brand/**"
      - ".github/workflows/ci.yml"
  ...
concurrency:
  group: ci-${{ github.workflow }}-${{ github.ref }}
  cancel-in-progress: true

permissions:
  contents: read
```

Neu schreiben (D-20): `permissions: {contents: read, packages: write}`; `paths: mcp-server/**`;
`docker/build-push-action` → GHCR `:latest` + `:sha-<sha>`; dann Coolify-Webhook (curl).
SHA-pinned actions wie in ci.yml (V5 Supply-Chain). Planner: SHAs + Coolify-Webhook-URL
verifizieren (A3, MEDIUM confidence).

## Shared Patterns

### Unified error shape (D-13/D-33)
**Source:** `api/app/core/errors.py` (lines 8-16)
**Apply to:** `mcp-server/app/api_client.py` (`_to_tool_error` liest genau diese Struktur)

```8:16:api/app/core/errors.py
def _error_payload(
    code: str,
    message: str,
    details: dict | list | str | None = None,
) -> dict:
    payload: dict = {"code": code, "message": message}
    if details is not None:
        payload["details"] = details
    return {"error": payload}
```

API antwortet immer `{"error":{"code","message","details?}}`. MCP: `err = resp.json()["error"]`
→ `ToolError(f"{code}: {message}")`. Status-codes: 404 `NOT_FOUND`, 415
`UNSUPPORTED_MEDIA_TYPE`, 422 `VALIDATION_ERROR`, 500 `INTERNAL_ERROR`.

### Token-Hashing (V2/V6)
**Source:** `api/app/auth/jwt.py` (line 75) + `api/app/core/bootstrap.py` (line 22)
**Apply to:** `mcp-server/app/auth.py`, `api/app/routers/internal.py`, bootstrap

`bearer_hash = hashlib.sha256(token.encode()).hexdigest()`; Vergleich via
`hmac.compare_digest` (jwt.py line 69). Nie Plaintext speichern/loggen (D-07, Pitfall 1).

### Header-Contract MCP→API (D-16)
**Source:** `api/app/main.py` line 16 (`API_VERSION_ACCEPT`), capture.py line 131 (Idempotency-Key alias)
**Apply to:** `mcp-server/app/api_client.py` — jeder Request

`Accept: application/vnd.puzzlessbox.v1+json` (sonst 415 via `AcceptVersionMiddleware`),
`X-Service-Bearer`, `X-Owner-Id`; `Idempotency-Key` nur create_item. `/health`+`/ready`
skippen Accept-Check (main.py line 17).

### Router-Registrierung + Config-Vars (MODIFY, trivial)
**Source:** `api/app/main.py` lines 59-64, `api/app/core/config.py`
**Apply to:** `api/app/main.py` (`include_router(internal.router)`, `categories.router`,
`items.router`; `ensure_mcp_client` in `_lifespan`), `api/app/core/config.py`
(`MCP_BOOTSTRAP_TOKEN` neu falls API bootstrappt).

## No Analog Found

| File | Role | Data Flow | Reason |
|------|------|-----------|--------|
| `.github/workflows/deploy-mcp.yml` | CI/CD | — | Kein Docker/GHCR-Build-Workflow im Repo; `ci.yml`=nur Brand-Tests. Greenfield (RESEARCH A3, D-20). Nur Skelett (concurrency/SHA-pin/permissions) übernehmbar; Build+Coolify-Webhook neu. |

FastMCP-spezifisches (kein Python-Analog, nur RESEARCH-Code-Examples): `FastMCP()`-Init,
`http_app()`-Signatur, `TokenVerifier`-Subklasse, `@mcp.tool`/`Field`-Schemas,
`get_access_token()`, `@mcp.custom_route`, `stateless_http`/`allowed_hosts`. → RESEARCH
Patterns 1-5 + Code Examples nutzen.

## Metadata

**Analog search scope:** `api/app/{main,core,auth,routers,models,services}.py`,
`api/alembic/versions/`, `api/tests/conftest.py`, `api/Dockerfile`, `api/requirements.txt`,
`.github/workflows/`
**Files scanned:** 15 gelesen (45 Python-Files im api/-Tree total)
**Pattern extraction date:** 2026-07-31

## PATTERN MAPPING COMPLETE

**Phase:** 02 - mcp-server
**Files classified:** 23
**Analogs found:** 22 / 23

### Coverage
- Files with exact analog: 6
- Files with role-match analog: 16
- Files with no analog: 1 (`deploy-mcp.yml` — greenfield)

### Key Patterns Identified
- Auth: sha256-Hash + owner-resolve spiegelt `api/app/auth/jwt.py`, aber MCP ruft
  `POST /internal/mcp-auth` statt DB (D-06); `TokenVerifier`-Subklasse gibt `AccessToken|None`.
- httpx-Client: `api/app/services/scraper.py` (AsyncClient/timeout/HTTPError) + `auth.py`
  `_map_better_auth_error` (Fehler-Mapping) → MCP `call_api`+`_to_tool_error`→`ToolError`.
- Tools mappen 1:1 auf `api/app/routers/capture.py`-Endpunkte; owner aus Token-Claim nie
  Tool-Input; Payload-Shapes verifiziert gegen `DraftCreate`/`DraftUpdate`.
- API-Neu: categories/move-Router spiegeln capture.py (`get_db_for_owner`, `text()`, RLS);
  `mcp_clients`-Model spiegelt `service_principal.py`; migration spiegelt `0002`; bootstrap
  spiegelt `ensure_service_principal`.
- Deploy greenfield: kein GHCR-Workflow existiert — neu schreiben, nur ci.yml-Skelett spiegeln.

### File Created
`/Users/puzzless/Desktop/puzzlessbox/.planning/phases/02-mcp-server/02-PATTERNS.md`

### Ready for Planning
Pattern-Mapping vollständig. Planner kann Analog-Muster in PLAN.md referenzieren.
