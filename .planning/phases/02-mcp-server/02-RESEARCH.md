# Phase 2: MCP-Server - Research

**Researched:** 2026-07-31
**Domain:** Remote FastMCP 3.4.4 Streamable-HTTP Server, Bearer-Auth, interner httpx-API-Client, Coolify/GHCR Deploy
**Confidence:** HIGH (FastMCP-API via Context7 `/prefecthq/fastmcp` verifiziert; Deploy-Pfad MEDIUM — kein bestehender Image-Workflow zum Spiegeln)

<user_constraints>
## User Constraints (from CONTEXT.md)

### Locked Decisions
- **D-01:** Zwei Secrets — Hermes-Bearer nur am MCP validiert; MCP→API nutzt bestehendes `SERVICE_BEARER_TOKEN` via `X-Service-Bearer` (Phase-1 D-23).
- **D-02:** Owner-Auflösung via Postgres `mcp_clients` (bearer_hash → owner_id), SaaS-ready; kein env-only Owner.
- **D-03:** Nach Lookup sendet MCP `X-Owner-Id` an API; Service-Bearer bleibt Gateway-Auth. API vertraut `X-Owner-Id` nur bei gültigem Service-Bearer.
- **D-04:** Token-Rotation = dual-token grace pro `mcp_clients`-Row (`active|grace` + expiry), nicht env PRIMARY/PREVIOUS.
- **D-05:** Hermes-Bearer im FastMCP/app validiert (401/403 testbar); Traefik nur TLS (keine IP-Allowlist).
- **D-06:** MCP öffnet `mcp_clients` **nicht** selbst — API besitzt Tabelle; MCP ruft internes `POST /internal/mcp-auth` (Service-Bearer) → `{owner_id}` (reject bei invalid/expired).
- **D-07:** Solo-Bootstrap: bei `MCP_BOOTSTRAP_TOKEN` + `SERVICE_OWNER_ID` und leerer `mcp_clients` → hash-only Row; nie Plaintext loggen; env danach löschbar.
- **D-08:** API `X-Owner-Id`-Guard: UUID-Format **und** Better-Auth `user`-Row muss existieren; sonst 403.
- **D-09:** `create_item` → immer `POST /drafts` (startet 30s-Timer); `type` required `note|link|task|event`.
- **D-10:** `confirm_item` = optionaler Field-Patch, dann `POST /drafts/{id}/confirm`.
- **D-11:** Phase 2 liefert API-Endpunkte für Tools: `GET/POST /categories`, Item-Category-Move (`PATCH` category_id / dedizierter Move).
- **D-12:** `update_item`: title, summary, category (+ typ-spezifische Felder wo API es kann); editierbar bei Status `draft|auto_saved`; `confirmed` → nur Category-Move.
- **D-13:** Tool-Fehler zu Hermes: kurzer MCP-Text + `code`; reichere Payload in `details` (kein Roh-API-Dump, kein opakes "failed").
- **D-14:** Tool-Descriptions/Schemas in **English**; deutsche Confirm-Copy erst Phase 3.
- **D-15:** MCP→API Base-URL = internes Docker-Netz (`http://puzzlessbox-api:8000`). Hermes→MCP bleibt public `https://mcp.puzzlesstool.online`.
- **D-16:** MCP sendet immer: `Accept: application/vnd.puzzlessbox.v1+json`, `X-Service-Bearer`, `X-Owner-Id`; bei `create_item` zusätzlich `Idempotency-Key`.
- **D-17:** HTTP-Timeout MCP→API = **15s**.
- **D-18:** Retries: **1×** nur auf 502/503 (keine blanket write-retries).
- **D-19:** `Idempotency-Key`: Hermes liefert wenn möglich; fehlt er, generiert MCP einmalig eine UUID und leitet sie weiter.
- **D-20:** Phase 2 inkludiert vollen MCP-Deploy: `mcp-server/` + Dockerfile + Coolify docker-image app + `mcp.puzzlesstool.online` + GitHub Actions → GHCR (`:latest` + `:sha-<sha>`) → Coolify-Webhook.
- **D-21:** Transport: Streamable HTTP (exakter FastMCP-Pfad research/planner-Sache; nicht SSE legacy, nicht stdio).
- **D-22:** MCP `/health` + `/ready` (ready darf API pingen) **und** Coolify Health-Check in Phase 2.
- **D-23:** Repo-Layout: top-level `mcp-server/` mit eigenem Image (NICHT FastMCP in `api/` gemountet).

### Claude's Discretion
- Exakter FastMCP Streamable-HTTP Mount-Path / Version-Pin innerhalb 3.4.x
- `mcp_clients`-Spaltennamen und grace-Default-TTL
- Interne Route-Benennung (`/internal/mcp-auth` vs Äquivalent)
- Categories-Create-Felder (color/sort) über name hinaus, falls API es für BOARD braucht
- GHCR-Image-Name / Workflow-Layout (API-Muster spiegeln)

### Deferred Ideas (OUT OF SCOPE)
- Hermes-Plugin, Confirm-Chat-UX, Channel-Orchestrierung — Phase 3 (MCP-03, CAP-02, CAP-04)
- Hermes Cron/dispatch_tool Spike — Phase 3 (MCP-04)
- WebApp-Board-UI die Categories konsumiert — Phase 4 (BOARD-*)
- Phase 5 OPS für API/WebApp/Backups (MCP-Slice bereits in Phase 2)
- MCP OAuth 2.1 / IP-Allowlist — v2 (MCP-05, MCP-06)
</user_constraints>

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|------------------|
| MCP-01 | Remote-MCP-Server (FastMCP) exponiert Tools `create_item`, `list_categories`, `create_category`, `move_item`, `confirm_item`, `update_item` | Tool-Definition mit `@mcp.tool` + `Annotated[..., Field()]` Pydantic-Schemas (Standard Stack + Code Examples); Mapping zu Phase-1-API in "Tool → API Mapping" |
| MCP-02 | MCP nur mit Bearer-Token über HTTPS erreichbar (separate Coolify-App) | Custom `TokenVerifier` → 401/403 (Auth-Sektion); eigenes `mcp-server/` Image + Coolify docker-image (Deploy-Sektion); Traefik TLS |
</phase_requirements>

## Summary

Phase 2 baut einen **eigenständigen** FastMCP-3.4.4-Server in `mcp-server/` (NICHT in `api/` gemountet — D-23 überschreibt die veraltete STACK.md-Notiz "mounted as ASGI sub-app"). Der Server ist ein dünner, zustandsloser Proxy: Er authentifiziert Hermes per rotierbarem Bearer, löst über die interne API (`POST /internal/mcp-auth`) den `owner_id` auf und ruft dann die Phase-1-FastAPI als interner httpx-Client (`X-Service-Bearer` + `X-Owner-Id`) auf. Sechs Tools mappen 1:1 auf REST-Endpunkte; die Kern-Item-Endpunkte existieren bereits (`POST /drafts`, `POST /drafts/{id}/confirm`, `PATCH /drafts/{id}`), Categories- und Move-Endpunkte sind **neu und Teil dieser Phase auf der API-Seite**.

Auth ist der kritische Pfad: FastMCP liefert `StaticTokenVerifier` (in-memory, plaintext, docs sagen explizit "never use in production") — das ist für die DB-gestützte dual-token-grace-Rotation (D-04) **ungeeignet**. Empfehlung: eine schlanke Subklasse von `TokenVerifier`, deren `verify_token()` den präsentierten Bearer sha256-hasht, `/internal/mcp-auth` aufruft und bei Erfolg ein `AccessToken` mit `claims={"owner_id": ...}` zurückgibt; `None`/Exception → FastMCPs `RequireAuthMiddleware` antwortet RFC-6750-konform mit 401. Tools lesen den Owner via `get_access_token().claims["owner_id"]`.

Deploy spiegelt das `api/`-Dockerfile-Muster (python:3.14-slim + uvicorn), **ohne Alembic** (MCP besitzt keine Tabelle). Wichtig: es existiert **noch kein** Image-Build-Workflow im Repo (`ci.yml` baut nur Brand-Tests) — der GHCR-Push + Coolify-Webhook ist greenfield und muss neu geschrieben werden.

**Primary recommendation:** Standalone `FastMCP(name=..., auth=CustomTokenVerifier(...))`, exponiert via `mcp.http_app(path="/mcp", stateless_http=True, allowed_hosts=["mcp.puzzlesstool.online"])`, uvicorn-served; httpx `AsyncClient` mit `timeout=15s` + manueller 1×-Retry-Schleife auf 502/503; jedes Tool ein `@mcp.tool` mit Pydantic-`Field`-Validierung; Fehler → `ToolError(f"{code}: {message}")`.

## Architectural Responsibility Map

| Capability | Primary Tier | Secondary Tier | Rationale |
|------------|-------------|----------------|-----------|
| Hermes-Bearer-Validierung | MCP-Server (FastMCP auth) | — | D-05: 401/403 muss am MCP testbar sein; API kennt Hermes-Bearer nicht |
| Owner-Auflösung (bearer→owner_id) | API (`/internal/mcp-auth`) | MCP ruft auf | D-06: API besitzt `mcp_clients`; MCP hält keine DB-Connection |
| Tool-Schema-Validierung | MCP-Server (Pydantic) | — | Fehler vor Netzwerk-Hop abfangen; V5 Input-Validation |
| Business-Logik / Persistenz | API | — | MCP ist reiner Proxy; keine Item-Logik dupliziert |
| Idempotency / Retry-Steuerung | MCP-Server (httpx) | API (Idempotency-Store) | D-16..D-19: MCP formt Header, API dedupliziert |
| TLS-Terminierung | Coolify Traefik | — | D-05: Traefik nur TLS, keine Auth-Logik |
| Categories/Move-Persistenz | API (neue Endpunkte) | MCP konsumiert | D-11: Board-API-Surface, WebApp später |

## Standard Stack

### Core
| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| `fastmcp` | `==3.4.4` | Remote MCP-Server-Framework | Gelockt (D-21, PROJECT.md); stabil, nicht 4.0-alpha. `http_app()` liefert Starlette-ASGI-App, `custom_route` für Health, `auth=TokenVerifier` für Bearer. [VERIFIED: PyPI — 3.4.4 vorhanden, 3.4.5 latest] |
| `uvicorn` | `==0.34.0` | ASGI-Server | Spiegelt `api/requirements.txt`; served `mcp.http_app()`. [VERIFIED: api/requirements.txt] |
| `httpx` | `==0.28.1` | Async HTTP-Client → interne API | Bereits Projekt-Standard; `AsyncClient`, `Timeout`, `MockTransport` für Tests. [VERIFIED: api/requirements.txt + PyPI] |
| `pydantic` | (via fastmcp) | Tool-Argument-Schemas | FastMCP generiert JSON-Schema aus `Annotated[..., Field()]`. [CITED: docs/servers/tools.mdx] |

### Supporting
| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| `pydantic-settings` | `==2.7.1` | Env-Config (`Settings`) | Spiegelt `api/app/core/config.py`; MCP-Env-Vars laden. [VERIFIED: api/requirements.txt] |
| `pytest` + `pytest-asyncio` | (Projekt-Standard) | Async-Tests, In-Memory-Client | Auth-/Tool-/Contract-Tests (Validation Architecture). [VERIFIED: api/requirements.txt] |

### Alternatives Considered
| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| Custom `TokenVerifier` | `StaticTokenVerifier` (built-in) | In-memory dict, Plaintext-Tokens, kein DB-grace, docs: "never use in production" → nur Dev. Ungeeignet für D-02/D-04. |
| Custom `TokenVerifier` | ASGI-Middleware vor http_app | Umgeht FastMCPs RFC-6750-401-Logik; muss Owner-Context selbst durch Tool-Kontext reichen. Mehr Boilerplate. |
| `mcp.http_app()` + uvicorn | `mcp.run(transport="http", ...)` | `run()` ist ok für Single-Process; `http_app()` gibt Kontrolle über `path`/`allowed_hosts`/`stateless_http` und spiegelt api/ CMD-Muster. |
| Manuelle Retry-Schleife | `httpx.HTTPTransport(retries=1)` | httpx-Transport-`retries` deckt NUR Connect-Fehler ab, NICHT 502/503-Statuscodes. D-18 verlangt Status-basierten Retry → manuell. |

**Installation:**
```bash
pip install "fastmcp==3.4.4" "uvicorn==0.34.0" "httpx==0.28.1" "pydantic-settings==2.7.1"
```

**Version verification:** `python3 -m pip index versions fastmcp` → `3.4.4` vorhanden (latest `3.4.5`), gelockt auf `3.4.4`. `httpx 0.28.1` = latest. [VERIFIED: PyPI 2026-07-31]

## Package Legitimacy Audit

| Package | Registry | Age | Downloads | Source Repo | Verdict | Disposition |
|---------|----------|-----|-----------|-------------|---------|-------------|
| `fastmcp` | PyPI | reif (v2→v3, Prefect-maintained) | hoch | github.com/prefecthq/fastmcp | OK | Approved (pin `==3.4.4`) |
| `uvicorn` | PyPI | reif | sehr hoch | github.com/encode/uvicorn | OK | Approved |
| `httpx` | PyPI | reif | sehr hoch | github.com/encode/httpx | OK | Approved (bereits in api/) |
| `pydantic-settings` | PyPI | reif | sehr hoch | github.com/pydantic/pydantic-settings | OK | Approved (bereits in api/) |

**Packages removed due to [SLOP] verdict:** none
**Packages flagged as suspicious [SUS]:** none

*Alle Packages via Context7 (`/prefecthq/fastmcp`) bzw. bestehende `api/requirements.txt` bestätigt — keine WebSearch-only-Discovery, keine `[ASSUMED]` Package-Namen.*

## Architecture Patterns

### System Architecture Diagram

```
                         (public HTTPS)
   Hermes VPS  ──Authorization: Bearer <hermes-token>──►  Coolify Traefik (TLS)
                                                                │
                                                                ▼
                                             ┌──────────── mcp-server (FastMCP) ────────────┐
                                             │  http_app(path="/mcp", stateless_http=True)   │
                                             │                                               │
                                             │  RequireAuthMiddleware ──► CustomTokenVerifier │
                                             │       │ (missing/invalid → 401)                │
                                             │       ▼ verify_token(token)                    │
                                             │   sha256(token) ──POST /internal/mcp-auth──────┼──┐
                                             │       ◄── {owner_id}                            │  │ (internal
                                             │   AccessToken(claims={owner_id})                │  │  Docker net,
                                             │       │                                         │  │  X-Service-Bearer)
                                             │       ▼ @mcp.tool (Pydantic-validiert)          │  │
                                             │   httpx.AsyncClient (timeout 15s, 1× retry 502/3)┼──┤
                                             │   Accept: vnd.v1+json, X-Service-Bearer,        │  │
                                             │   X-Owner-Id, [Idempotency-Key]                 │  ▼
                                             │  custom_route /health (unauth)                  │  puzzlessbox-api:8000
                                             │  custom_route /ready  (pingt API /health)       │  POST /drafts, /confirm,
                                             └─────────────────────────────────────────────────┘  GET/POST /categories,
                                                                                                    PATCH move, /internal/mcp-auth
```

Primärer Use-Case (`create_item`): Hermes → Traefik → RequireAuthMiddleware → CustomTokenVerifier (→ /internal/mcp-auth → owner_id) → `create_item`-Tool (Pydantic-Validierung) → httpx `POST /drafts` mit allen Headern + Idempotency-Key → API-Antwort → Tool-Result an Hermes.

### Recommended Project Structure
```
mcp-server/
├── Dockerfile                 # python:3.14-slim + uvicorn (KEIN alembic)
├── requirements.txt           # fastmcp==3.4.4, uvicorn, httpx, pydantic-settings
├── app/
│   ├── __init__.py
│   ├── server.py              # FastMCP(...), http_app; `app = mcp.http_app(...)`
│   ├── config.py              # Settings (spiegelt api/app/core/config.py)
│   ├── auth.py                # CustomTokenVerifier(TokenVerifier)
│   ├── api_client.py          # httpx.AsyncClient factory + retry helper + error map
│   ├── health.py              # custom_route /health + /ready
│   └── tools/
│       ├── __init__.py        # register_tools(mcp)
│       ├── items.py           # create_item, confirm_item, update_item, move_item
│       └── categories.py      # list_categories, create_category
└── tests/
    ├── conftest.py            # in-memory Client fixture + httpx.MockTransport fixture
    ├── test_auth.py           # 401/403 seams
    ├── test_tools_schema.py   # Pydantic reject
    ├── test_api_contract.py   # Header + Idempotency + Retry
    └── test_health.py
```

### Pattern 1: Standalone Streamable-HTTP Server + Health
**What:** FastMCP-Server als eigene ASGI-App, Health-Routes via `custom_route`.
**When to use:** Immer (D-22, D-23).
**Example:**
```python
# Source: Context7 /prefecthq/fastmcp docs/deployment/http.mdx
from fastmcp import FastMCP
from starlette.responses import JSONResponse

mcp = FastMCP(name="Puzzlessbox MCP", auth=verifier)

@mcp.custom_route("/health", methods=["GET"])
async def health_check(request):
    return JSONResponse({"status": "ok", "service": "mcp-server"})

# http_app() signatur (verifiziert):
# http_app(path, middleware, json_response, stateless_http,
#          transport="http"|"streamable-http"|"sse", ..., allowed_hosts, allowed_origins)
app = mcp.http_app(path="/mcp", stateless_http=True,
                   allowed_hosts=["mcp.puzzlesstool.online"])
# uvicorn app.server:app --host 0.0.0.0 --port 8000
```
Hinweis: `transport="http"` == moderner Streamable-HTTP (Default). `"sse"` = legacy (verboten, D-21).

### Pattern 2: Custom Bearer-Auth via TokenVerifier
**What:** Subklasse von `TokenVerifier`; `verify_token` löst Owner via interne API auf.
**When to use:** MCP-01/02 Auth — DB-grace-Rotation (D-02/D-04/D-06).
**Example:**
```python
# Source: Context7 /prefecthq/fastmcp tests/server/auth/... + docs/servers/authorization.mdx
import hashlib, time
from fastmcp.server.auth import AccessToken, TokenVerifier  # öffentliches Re-Export; StaticTokenVerifier NICHT nutzen

class OwnerResolvingVerifier(TokenVerifier):
    def __init__(self, api_client): self._api = api_client
    async def verify_token(self, token: str) -> AccessToken | None:
        bearer_hash = hashlib.sha256(token.encode()).hexdigest()
        owner_id = await self._api.resolve_owner(bearer_hash)  # POST /internal/mcp-auth
        if owner_id is None:
            return None  # → RequireAuthMiddleware sendet 401 (RFC 6750)
        return AccessToken(token=token, client_id=owner_id,
                           scopes=[], expires_at=None,
                           claims={"owner_id": owner_id, "sub": owner_id})

mcp = FastMCP(name="Puzzlessbox MCP", auth=OwnerResolvingVerifier(api_client))
```
401-Verhalten (verifiziert aus `fastmcp/server/auth/middleware.py`): fehlender `Authorization`-Header → 401 + `WWW-Authenticate: Bearer`, leerer Body; vorhandener aber ungültiger Token → 401 + JSON `{"error":"invalid_token","error_description":...}`.

### Pattern 3: Owner im Tool lesen
```python
# Source: Context7 /prefecthq/fastmcp docs/servers/dependency-injection.mdx
from fastmcp.server.dependencies import get_access_token, TokenClaim

@mcp.tool
async def list_categories() -> list[dict]:
    """List all categories for the authenticated owner."""
    owner_id = get_access_token().claims["owner_id"]
    return await api_client.get_categories(owner_id)

# Alternative: owner_id: str = TokenClaim("owner_id") als Tool-Parameter (raises wenn fehlend)
```

### Pattern 4: Interner httpx-Client mit Timeout + 1×-Retry (502/503)
```python
import uuid, httpx
from fastmcp.exceptions import ToolError

BASE = "http://puzzlessbox-api:8000"
ACCEPT = "application/vnd.puzzlessbox.v1+json"

def make_client(service_bearer: str) -> httpx.AsyncClient:
    return httpx.AsyncClient(
        base_url=BASE,
        timeout=httpx.Timeout(15.0),  # D-17
        headers={"Accept": ACCEPT, "X-Service-Bearer": service_bearer},
    )

async def call_api(client, method, path, owner_id, *, json=None, idempotency_key=None):
    headers = {"X-Owner-Id": owner_id}  # D-03/D-16
    if idempotency_key:
        headers["Idempotency-Key"] = idempotency_key
    for attempt in range(2):  # 1 initial + 1 retry (D-18)
        resp = await client.request(method, path, json=json, headers=headers)
        if resp.status_code in (502, 503) and attempt == 0:
            continue  # nur EIN retry, nur 502/503
        break
    if resp.status_code >= 400:
        raise _to_tool_error(resp)  # siehe Pattern 5
    return resp.json()
```
Idempotency-Key (D-19): `idempotency_key = provided or str(uuid.uuid4())` — einmal generieren, dann forwarden (nur `create_item`).

### Pattern 5: Fehler-Mapping API → MCP (D-13)
```python
def _to_tool_error(resp: httpx.Response) -> ToolError:
    try:
        err = resp.json().get("error", {})
    except Exception:
        err = {}
    code = err.get("code", "API_ERROR")
    message = err.get("message", "Request failed")
    # kurzer Text + code für Hermes; details strukturiert, KEIN Roh-Dump
    return ToolError(f"{code}: {message}")
```
API-Fehlershape (verifiziert `api/app/core/errors.py`): `{"error":{"code","message","details?}}`. Status-Beispiele: 404 `NOT_FOUND`, 415 `UNSUPPORTED_MEDIA_TYPE`, 422 `VALIDATION_ERROR`, 500 `INTERNAL_ERROR`.

### Anti-Patterns to Avoid
- **`StaticTokenVerifier` in Prod:** In-memory Plaintext-Tokens, kein DB-grace — docs verbieten es explizit. Nur Dev/Test.
- **FastMCP in `api/` mounten:** Widerspricht D-23 (separate Coolify-App). STACK.md-Notiz "mounted as ASGI sub-app" ist überholt.
- **`httpx` Transport-`retries` für 502/503:** Deckt nur Connect-Fehler; verpasst Status-Retry (D-18).
- **`allowed_hosts` weglassen:** FastMCP hat DNS-Rebinding-Schutz (`host_origin_protection`/`allowed_hosts`) — hinter Traefik ist Host `mcp.puzzlesstool.online`; ohne Eintrag drohen blockierte Requests.
- **Owner_id als Tool-Argument von Hermes akzeptieren:** Owner MUSS aus dem verifizierten Token stammen (Tenancy-Leak-Risiko), nie aus Tool-Input.

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| MCP-Protokoll / Streamable-HTTP | Eigener JSON-RPC/SSE-Handler | `fastmcp` `http_app()` | Session-Mgmt, Schema-Gen, Protokoll-Versionierung gelöst |
| Tool-Argument-JSON-Schema | Manuelles JSON-Schema | `Annotated[..., Field()]` | FastMCP generiert + validiert automatisch |
| 401-Body/WWW-Authenticate | Eigene 401-Responses | `TokenVerifier` + `RequireAuthMiddleware` | RFC-6750-konform (missing vs invalid) out of the box |
| Bearer→Owner Persistenz | Eigene DB-Connection im MCP | `POST /internal/mcp-auth` | D-06: API besitzt Tabelle; MCP bleibt DB-frei |
| HTTP-Timeout/Connect-Handling | `requests` + eigene Loops | `httpx.AsyncClient(timeout=)` | Async, Projekt-Standard |
| Token-Hashing | Eigenes Krypto | `hashlib.sha256` + `hmac.compare_digest` | Spiegelt `api/app/auth/jwt.py` / `bootstrap.py` |

**Key insight:** MCP-Server ist ein **dünner Proxy** — jede Item-Logik gehört in die API. MCP validiert Input, resolved Owner, formt Header, mappt Fehler. Sonst nichts.

## Runtime State Inventory

Nicht anwendbar — Phase 2 ist **greenfield** (`mcp-server/` existiert nicht, `git status` zeigt nur `.planning/`-Files). Kein Rename/Refactor/Migration bestehender Runtime-State.
- **Stored data:** None — neue `mcp_clients`-Tabelle wird via Alembic in der API (nicht MCP) angelegt; keine bestehenden Records umzuschreiben.
- **Live service config:** None — neue Coolify-App, keine bestehende MCP-Config.
- **OS-registered state:** None.
- **Secrets/env vars:** Neu (`MCP_HERMES_*` n/a — Bearer in `mcp_clients`; `SERVICE_BEARER_TOKEN`/`SERVICE_OWNER_ID` bestehen bereits, `MCP_BOOTSTRAP_TOKEN` neu). Keine Umbenennung.
- **Build artifacts:** None — neues Image.

## Common Pitfalls

### Pitfall 1: Bearer-Token-Exposure (Logs/Git/HTTP)
**What goes wrong:** Static-Bearer leakt via verbose Logs, committetes Config oder unverschlüsseltes HTTP → voller Tool-Zugriff.
**Why it happens:** `Authorization`-Header in Logs; Plaintext-Token in DB/Git; kein TLS.
**How to avoid:** Nur sha256-Hash in `mcp_clients` speichern (D-02); nie Plaintext loggen (D-07); Traefik-TLS erzwingen (D-05); Bootstrap-Token nach Insert env-löschbar.
**Warning signs:** Bearer im Klartext in Logs/Repo; HTTP-Requests in Netzwerk-Logs.

### Pitfall 2: Streamable-HTTP Session-State bei Container-Restart
**What goes wrong:** Stateful Streamable-HTTP hält Session-IDs (`Mcp-Session-Id`) in-memory; Coolify-Redeploy/Restart droppt sie → Client-Reconnect nötig.
**Why it happens:** Default ist stateful.
**How to avoid:** `stateless_http=True` in `http_app()` — Tools sind zustandslose REST-Proxies, keine Session-Affinität nötig. Vereinfacht auch spätere horizontale Skalierung.
**Warning signs:** Sporadische Session-not-found-Fehler nach Deploys.

### Pitfall 3: DNS-Rebinding-Schutz blockt Traefik-Host
**What goes wrong:** Requests hinter Traefik werden mit Host-Header-Fehler abgewiesen.
**Why it happens:** FastMCP `host_origin_protection`/`allowed_hosts` Default kennt `mcp.puzzlesstool.online` nicht.
**How to avoid:** `allowed_hosts=["mcp.puzzlesstool.online"]` (und ggf. interner Health-Host) explizit setzen.
**Warning signs:** 400/403 nur in Prod hinter Proxy, lokal grün.

### Pitfall 4: Retry verdoppelt Nicht-idempotente Writes
**What goes wrong:** Blanket-Retry auf alle 5xx wiederholt `create_item` → Duplikate.
**Why it happens:** Zu breite Retry-Bedingung; kein Idempotency-Key.
**How to avoid:** Retry NUR auf 502/503, genau 1× (D-18); `Idempotency-Key` immer auf `create_item` (D-16/D-19) — API dedupliziert (verifiziert `capture.py` `idempotency_keys`-Tabelle).
**Warning signs:** Doppelte Drafts bei API-Flapping.

### Pitfall 5: `X-Owner-Id` ohne gültige User-Row → 403 (D-08)
**What goes wrong:** API weist `X-Owner-Id` ab, wenn keine Better-Auth `user`-Row existiert → Tools scheitern trotz gültigem Bearer.
**Why it happens:** Bootstrap-Owner (`SERVICE_OWNER_ID`) hat evtl. keine `user`-Row.
**How to avoid:** Sicherstellen, dass Bootstrap-`owner_id` einer existierenden Better-Auth-User-UUID entspricht; API-Guard prüft UUID-Format UND User-Existenz.
**Warning signs:** 403 bei allen Tools trotz erfolgreicher Auth am MCP.

### Pitfall 6: Version-Drift innerhalb 3.4.x
**What goes wrong:** Ungepinntes `fastmcp` zieht 3.4.5+ → subtile API-Änderungen.
**How to avoid:** `fastmcp==3.4.4` exakt pinnen (D-21); Renovate/Dependabot-Bumps bewusst reviewen.

## Code Examples

### Tool: create_item (D-09, D-16, D-19)
```python
from typing import Annotated, Literal
from pydantic import Field
from fastmcp.server.dependencies import get_access_token

@mcp.tool
async def create_item(
    title: Annotated[str, Field(description="Item title", min_length=1)],
    type: Annotated[Literal["note", "link", "task", "event"],
                    Field(description="Item type")],
    category_id: Annotated[str, Field(description="Target category UUID")],
    summary: Annotated[str, Field(description="Short summary")] = "",
    idempotency_key: Annotated[str | None,
                    Field(description="Optional client idempotency key")] = None,
) -> dict:
    """Create a capture draft (starts the 30s confirmation timer)."""
    owner_id = get_access_token().claims["owner_id"]
    body = {"title": title, "type": type, "category_id": category_id, "summary": summary}
    return await call_api(client, "POST", "/drafts", owner_id,
                          json=body, idempotency_key=idempotency_key or str(uuid.uuid4()))
```
Mapping zu `DraftCreate` (verifiziert `api/app/models/note.py`): `title:str`, `type:ItemType`, `category_id:uuid.UUID`, `summary:str=""`.

### Tool: confirm_item (D-10)
```python
@mcp.tool
async def confirm_item(
    item_id: Annotated[str, Field(description="Draft UUID")],
    title: Annotated[str | None, Field(description="Optional title patch")] = None,
    summary: Annotated[str | None, Field(description="Optional summary patch")] = None,
    category_id: Annotated[str | None, Field(description="Optional category patch")] = None,
) -> dict:
    """Optionally patch fields, then confirm the draft."""
    owner_id = get_access_token().claims["owner_id"]
    patch = {k: v for k, v in
             {"title": title, "summary": summary, "category_id": category_id}.items()
             if v is not None}
    if patch:
        await call_api(client, "PATCH", f"/drafts/{item_id}", owner_id, json=patch)
    return await call_api(client, "POST", f"/drafts/{item_id}/confirm", owner_id)
```
Verifiziert: `PATCH /drafts/{id}` (DraftUpdate: title/summary/category_id optional) + `POST /drafts/{id}/confirm` existieren (`api/app/routers/capture.py`).

### Tool → API Mapping (vollständig)
| Tool | HTTP | Path | Status Endpoint |
|------|------|------|-----------------|
| `create_item` | POST | `/drafts` | ✅ existiert (`capture.py`) |
| `confirm_item` | PATCH→POST | `/drafts/{id}` → `/drafts/{id}/confirm` | ✅ existiert |
| `update_item` | PATCH | `/drafts/{id}` (draft/auto_saved); confirmed → nur category | ✅ PATCH existiert; ⚠️ confirmed-move braucht neuen Endpunkt |
| `list_categories` | GET | `/categories` | ❌ **NEU** (Phase 2 API-Seite) |
| `create_category` | POST | `/categories` | ❌ **NEU** |
| `move_item` | PATCH | `/items/{id}` category_id / `/items/{id}/move` | ❌ **NEU** |

### Internal auth resolve helper
```python
async def resolve_owner(self, bearer_hash: str) -> str | None:
    resp = await self._client.post("/internal/mcp-auth", json={"bearer_hash": bearer_hash})
    if resp.status_code == 200:
        return resp.json()["owner_id"]
    return None  # 401/403/404 → unauth
```

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| SSE-Transport | Streamable HTTP (`transport="http"`) | MCP-Spec 2025+ | D-21: SSE legacy, verboten |
| FastMCP in FastAPI gemountet (STACK.md) | Standalone `mcp-server/` Image | D-23 (Discuss) | Separate Coolify-App, entkoppelt |
| env PRIMARY/PREVIOUS Token | DB dual-token grace (`mcp_clients`) | D-04 | SaaS-ready Rotation |

**Deprecated/outdated:**
- STACK.md-Notiz "Mounted as an ASGI sub-app inside FastAPI to run on a single port" → **überholt** durch D-23.
- SUMMARY.md nummeriert MCP als "Phase 3" → aktuelle Roadmap: **Phase 2**.

## Assumptions Log

> A1, A4, A5 **pre-execute verifiziert** (2026-07-31) — siehe [Resolved at Pre-Execute](#resolved-at-pre-execute-2026-07-31). Verbleibende Annahmen:
| # | Claim | Section | Risk if Wrong |
|---|-------|---------|---------------|
| A1 | ~~In-Memory `Client(mcp)` Transport für Tests verfügbar in 3.4.4~~ **VERIFIED** — `from fastmcp import Client`; `async with Client(mcp)`; Auth/HTTP-Stack via `fastmcp.utilities.tests.asgi_client` | Validation Architecture | — |
| A2 | `stateless_http=True` kompatibel mit gewähltem Auth-Flow | Architecture Patterns | LOW — Auth ist per-Request-Token, kein Session-State nötig |
| A3 | Coolify docker-image App + Webhook-Deploy-Muster (kein bestehender Workflow zum Spiegeln) | Deploy | MEDIUM — GHCR/Actions greenfield; Deploy-Spec in `02-DEPLOY-SPEC.md` (Sibling-Agent) |
| A4 | ~~Exakter Import-Pfad `fastmcp.server.auth.auth.TokenVerifier`~~ **VERIFIED** — öffentlich: `from fastmcp.server.auth import TokenVerifier, AccessToken` | Auth | — |
| A5 | ~~`AccessToken` akzeptiert freies `claims`-dict~~ **VERIFIED** — `claims: dict[str, Any]` dokumentiert; optional `token`, `client_id`, `scopes`, `expires_at` | Auth | — |

## Open Questions

Alle vorherigen Offenen Punkte sind **(RESOLVED)** — Details in [Resolved at Pre-Execute (2026-07-31)](#resolved-at-pre-execute-2026-07-31).

1. **In-Memory-Test-Client-API in 3.4.4 (RESOLVED)**
   - **Import:** `from fastmcp import FastMCP, Client` [CITED: docs/clients/transports.mdx]
   - **Unit/Tool-Tests (ohne HTTP-Stack):** Server-Instanz direkt an Client übergeben — kein Port, kein Subprocess:
     ```python
     from fastmcp import FastMCP, Client

     async def test_tool_in_memory(mcp: FastMCP):
         async with Client(mcp) as client:
             result = await client.call_tool("greet", {"name": "World"})
             assert result.data == "Hello, World!"
     ```
   - **Auth/Middleware/HTTP-Stack-Tests (MCP-02):** `asgi_client` aus `fastmcp.utilities.tests` — fährt vollen HTTP-Stack in-process (RequireAuthMiddleware, Bearer-Header):
     ```python
     from fastmcp.utilities.tests import asgi_client

     async def test_auth_over_http(mcp: FastMCP):
         async with asgi_client(mcp, path="/mcp") as client:
             # client sendet Authorization: Bearer … über echten ASGI-Stack
             ...
     ```
     Signatur: `asgi_client(server, transport="http", path=None, **client_kwargs) -> AsyncGenerator[Client, None]` [CITED: docs/python-sdk/fastmcp-utilities-tests.mdx]
   - **Fallback (wenn `asgi_client`/`Client` in Pin-Version fehlt):** `httpx.AsyncClient(transport=httpx.ASGITransport(app=mcp.http_app(path="/mcp")), base_url="http://test")` — manuelle MCP-HTTP-Requests inkl. `Authorization`-Header.
   - **Lokal nicht installiert:** `fastmcp` fehlt im Workspace-venv; Verifikation via Context7 `/prefecthq/fastmcp` (nicht lokaler Import).

2. **`AccessToken`-Konstruktor-Felder (3.4.4) (RESOLVED)**
   - **Import:** `from fastmcp.server.auth import AccessToken` (öffentliches Re-Export; kein Deep-Import `fastmcp.server.auth.auth`) [CITED: docs/servers/authorization.mdx, tests/server/auth/test_oauth_consent_flow.py]
   - **Felder** (alle optional außer `token` in der Praxis; kein `resource`-Feld):
     | Feld | Typ | Pflicht | Default / Hinweis |
     |------|-----|---------|-------------------|
     | `token` | `str` | ja (praktisch) | Raw Bearer-String |
     | `client_id` | `str \| None` | nein | OAuth-Client-ID; hier `owner_id` nutzbar |
     | `scopes` | `list[str]` | nein | `[]` wenn leer |
     | `expires_at` | `datetime \| int \| None` | nein | `None` für nicht ablaufende Service-Bearer |
     | `claims` | `dict[str, Any]` | nein | Custom Claims, z. B. `{"owner_id": ..., "sub": ...}` |
   - **Beispiel (OwnerResolvingVerifier):**
     ```python
     from fastmcp.server.auth import AccessToken, TokenVerifier

     return AccessToken(
         token=token,
         client_id=owner_id,
         scopes=[],
         expires_at=None,
         claims={"owner_id": owner_id, "sub": owner_id},
     )
     ```
   - **TokenVerifier-Import:** `from fastmcp.server.auth import TokenVerifier` — Subklasse implementiert `async def verify_token(self, token: str) -> AccessToken | None` [CITED: fastmcp_slim/fastmcp/server/auth/auth.py]

3. **move_item API-Shape (RESOLVED — LOCKED)**
   - **Entscheidung:** `PATCH /items/{id}` mit Body `{"category_id": "<uuid>"}` — **kein** dedizierter `/items/{id}/move`.
   - **Evidenz:** D-11/D-12 (CONTEXT), `02-02-PLAN.md` Task 2, `02-03-PLAN.md` move_item-Mapping, `02-PATTERNS.md` Zeile 316–317.
   - **Codebase-Stand:** `api/app/routers/capture.py` hat nur `PATCH /drafts/{id}` mit `status IN ('draft','auto_saved')` — confirmed-Move braucht neuen Router `api/app/routers/items.py` (02-02), **ohne** Status-Filter (D-12).
   - **MCP-Tool:** `move_item(item_id, category_id)` → `PATCH /items/{item_id}` `json={"category_id": category_id}`.

## Environment Availability

| Dependency | Required By | Available | Version | Fallback |
|------------|------------|-----------|---------|----------|
| Python 3.14 | MCP-Runtime | ✓ (Docker base `python:3.14-slim`, wie api/) | 3.14 | — |
| `fastmcp==3.4.4` | MCP-Server | ✓ PyPI | 3.4.4 | — |
| `httpx`, `uvicorn`, `pydantic-settings` | Client/Server/Config | ✓ (in api/) | pinned | — |
| Interne API `puzzlessbox-api:8000` | MCP→API Hop | ✓ (Phase 1 merged) | v1 | `/ready` degradiert wenn down |
| GHCR (ghcr.io) | Image-Registry | ✓ (GITHUB_TOKEN) | — | — |
| Coolify docker-image App + Webhook | Deploy | ✓ Plattform (v4.1.2) | — | manueller Pull |
| **Bestehender Image-Build-Workflow** | Spiegel-Vorlage | ✗ (`ci.yml` = nur Brand-Tests) | — | **neu schreiben** — Spec: `02-DEPLOY-SPEC.md` |

**Missing dependencies with no fallback:** keine blockierenden — aber:
**Missing with fallback / Achtung:**
- Es gibt **keinen** bestehenden GHCR-Docker-Build-Workflow im Repo. D-20 "GitHub Actions → GHCR" ist greenfield; `api/`-Muster existiert nur als Dockerfile, nicht als Workflow. **Deploy-Workflow-Spec** wird vom Sibling-Agent in `02-DEPLOY-SPEC.md` geliefert (nicht in diesem RESEARCH-Dokument duplizieren).

## Validation Architecture

### Test Framework
| Property | Value |
|----------|-------|
| Framework | `pytest` + `pytest-asyncio` (Projekt-Standard, spiegelt api/) |
| Config file | none in `mcp-server/` — **Wave 0** anlegen (`pytest.ini` oder `[tool.pytest.ini_options]`) |
| Quick run command | `pytest mcp-server/tests -x -q` |
| Full suite command | `pytest mcp-server/tests` |

### Phase Requirements → Test Map
| Req ID | Behavior | Test Type | Automated Command | File Exists? |
|--------|----------|-----------|-------------------|-------------|
| MCP-02 | Fehlender Bearer → 401 | integration (ASGI/in-mem) | `pytest mcp-server/tests/test_auth.py::test_missing_bearer_401 -x` | ❌ Wave 0 |
| MCP-02 | Ungültiger Bearer → 401 (invalid_token) | integration | `pytest mcp-server/tests/test_auth.py::test_invalid_bearer_401 -x` | ❌ Wave 0 |
| MCP-02 | Gültiger Bearer, aber /internal/mcp-auth reject → 401/403 | integration | `pytest mcp-server/tests/test_auth.py::test_owner_reject -x` | ❌ Wave 0 |
| MCP-01 | `create_item` ohne `type` / invalid enum → Schema-Reject (kein Crash) | unit | `pytest mcp-server/tests/test_tools_schema.py -x` | ❌ Wave 0 |
| MCP-01 | MCP→API sendet Accept vnd + X-Service-Bearer + X-Owner-Id | contract (MockTransport) | `pytest mcp-server/tests/test_api_contract.py::test_headers -x` | ❌ Wave 0 |
| MCP-01 | `create_item` setzt Idempotency-Key (provided verbatim / generiert wenn fehlend) | contract | `pytest mcp-server/tests/test_api_contract.py::test_idempotency -x` | ❌ Wave 0 |
| MCP-01 | Retry: 502→200 = 1 retry; 500 = 0 retry; 503,503 = fail | contract | `pytest mcp-server/tests/test_api_contract.py::test_retry -x` | ❌ Wave 0 |
| MCP-01 | API-Fehler `{error:{code,message}}` → `ToolError` mit code | unit | `pytest mcp-server/tests/test_api_contract.py::test_error_map -x` | ❌ Wave 0 |
| MCP-01 | Tool→API Mapping (create/confirm/update/list/create_cat/move) | contract | `pytest mcp-server/tests/test_api_contract.py::test_mapping -x` | ❌ Wave 0 |
| MCP-02 | `/health` 200 (unauth), `/ready` pingt API | integration | `pytest mcp-server/tests/test_health.py -x` | ❌ Wave 0 |

### Sampling Rate
- **Per task commit:** `pytest mcp-server/tests -x -q`
- **Per wave merge:** `pytest mcp-server/tests`
- **Phase gate:** volle Suite grün vor `/gsd-verify-work`

### Wave 0 Gaps
- [ ] `mcp-server/tests/conftest.py` — `Client(mcp)` für Tool-Unit-Tests; `asgi_client(mcp, path="/mcp")` für Auth-Integration; Fallback `httpx.ASGITransport(app=mcp.http_app())`; `httpx.MockTransport` für interne API
- [ ] `mcp-server/tests/test_auth.py` — 401/403-Seams (MCP-02)
- [ ] `mcp-server/tests/test_tools_schema.py` — Pydantic-Reject (MCP-01)
- [ ] `mcp-server/tests/test_api_contract.py` — Header/Idempotency/Retry/Error/Mapping (MCP-01)
- [ ] `mcp-server/tests/test_health.py` — /health, /ready
- [ ] `mcp-server/pytest.ini` (`asyncio_mode = auto`)
- [ ] Framework install: `pip install pytest pytest-asyncio` (in `mcp-server/requirements.txt` dev-Sektion)

## Security Domain

`security_enforcement: true`, `security_asvs_level: 1`, `security_block_on: high`.

### Applicable ASVS Categories

| ASVS Category | Applies | Standard Control |
|---------------|---------|-----------------|
| V2 Authentication | yes | Static rotatable Bearer, sha256-Hash in `mcp_clients`, `hmac.compare_digest` (spiegelt `api/app/auth/jwt.py`) |
| V3 Session Management | yes | `stateless_http=True` — keine serverseitige Session; per-Request-Token-Validierung |
| V4 Access Control | yes | Owner nur aus verifiziertem Token-Claim; `X-Owner-Id` an API; API-Guard D-08 (UUID + user-row) |
| V5 Input Validation | yes | Pydantic `Field`-Constraints auf allen Tool-Args; Enum für `type`; UUID-Format für IDs |
| V6 Cryptography | yes | `hashlib.sha256` für Token-Hash; **kein** Custom-Krypto; Plaintext nie speichern/loggen (D-07) |
| V7 Logging | yes | `Authorization`/Bearer aus Logs redacten; keine Token in Exceptions |
| V9 Communication | yes | HTTPS/TLS via Traefik (D-05); interner Hop im privaten Docker-Netz |

### Known Threat Patterns for FastMCP-Remote-Server

| Pattern | STRIDE | Standard Mitigation |
|---------|--------|---------------------|
| Bearer-Token-Leak (Logs/Git/HTTP) | Information Disclosure | TLS + Hash-only-Storage + Log-Redaction + Bootstrap-env-clear |
| DNS-Rebinding / Host-Header-Spoof | Spoofing | `allowed_hosts`/`host_origin_protection` explizit setzen |
| Tenant-Leak (owner_id aus Tool-Input) | Elevation of Privilege | Owner ausschließlich aus Token-Claim, nie aus Tool-Argument |
| Replay / Duplicate-Write | Tampering | `Idempotency-Key` auf `create_item`; Retry nur 502/503 ×1 |
| Token nach Rotation weiter gültig | Spoofing | dual-token grace mit `expiry` (D-04); grace-Token nach TTL invalid |
| Verbose-Fehler leaken interne API-Details | Information Disclosure | `ToolError` nur code+message; kein Roh-API-Dump (D-13) |

## Sources

### Primary (HIGH confidence)
- Context7 `/prefecthq/fastmcp` — `http_app()` Signatur, `custom_route` Health, `StaticTokenVerifier`, `TokenVerifier`/`AccessToken`, `get_access_token`/`TokenClaim`, `RequireAuthMiddleware` 401-Logik, Tool-`Field`-Schemas
- `api/app/auth/jwt.py`, `bootstrap.py`, `routers/capture.py`, `core/errors.py`, `core/config.py`, `main.py`, `models/note.py` — verifizierte Phase-1-Contracts
- PyPI (`pip index versions`) — `fastmcp 3.4.4`, `httpx 0.28.1` bestätigt

### Secondary (MEDIUM confidence)
- `.planning/research/STACK.md`, `SUMMARY.md`, `PITFALLS.md` — Projekt-Kontext (mit korrigierten Überholungen, s. State of the Art)
- Coolify docker-image + GHCR-Deploy-Muster (greenfield, kein Repo-Workflow zum Spiegeln)

### Tertiary (LOW confidence)
- none (A1/A4/A5 pre-execute verifiziert)

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH — Context7 + PyPI verifiziert, Versionen gepinnt
- Architecture: HIGH — FastMCP-API verifiziert, Phase-1-Contracts gelesen
- Auth: HIGH — `TokenVerifier`/401-Middleware aus Source verifiziert
- Deploy: MEDIUM — kein bestehender Image-Workflow; GHCR/Coolify greenfield
- Pitfalls: HIGH — aus FastMCP-Source + Projekt-PITFALLS.md

**Research date:** 2026-07-31
**Valid until:** 2026-08-30 (FastMCP 3.4.x stabil; bei 4.0-Migration neu prüfen)

## Resolved at Pre-Execute (2026-07-31)

| # | Frage | Ergebnis | Evidenz |
|---|-------|----------|---------|
| 1 | In-Memory-Test-Client 3.4.4 | `from fastmcp import Client`; `Client(mcp)` für Tools; `asgi_client(mcp)` für Auth/HTTP; Fallback `httpx.ASGITransport(app=mcp.http_app())` | [CITED: docs/clients/transports.mdx, docs/development/tests.mdx] |
| 2 | `AccessToken`-Felder | `token` + optional `client_id`, `scopes`, `expires_at`, `claims`; Import `from fastmcp.server.auth import AccessToken, TokenVerifier` | [CITED: docs/servers/authorization.mdx, test_oauth_consent_flow.py] |
| 3 | `move_item` API-Shape | **LOCKED:** `PATCH /items/{id}` `{"category_id"}` — kein `/move`-Suffix | D-11/D-12, `02-02-PLAN.md`, `capture.py` (drafts ≠ confirmed-move) |

**Assumptions aktualisiert:** A1, A4, A5 → VERIFIED. A3 Deploy-Detail → `02-DEPLOY-SPEC.md`.

## RESEARCH COMPLETE

**Phase:** 02 - MCP-Server
**Confidence:** HIGH

### Key Findings
- Standalone FastMCP 3.4.4 (`mcp-server/` eigenes Image, NICHT in api/ gemountet — D-23 überschreibt STACK.md); `mcp.http_app(path="/mcp", stateless_http=True, allowed_hosts=[...])` + uvicorn; Health via `@mcp.custom_route`.
- Auth: **Custom `TokenVerifier`-Subklasse** (nicht `StaticTokenVerifier` — prod-verboten), `verify_token` → sha256 → `POST /internal/mcp-auth` → `AccessToken(claims={owner_id})`; `None` → RFC-6750-401 via `RequireAuthMiddleware`. Owner in Tools via `get_access_token().claims["owner_id"]`.
- httpx `AsyncClient` timeout 15s + **manuelle** 1×-Retry-Schleife auf 502/503 (Transport-`retries` deckt nur Connect-Fehler); Idempotency-Key `provided or uuid4()` auf create_item.
- 6 Tools mit `Annotated[..., Field()]`-Schemas; create/confirm/update mappen auf bestehende `/drafts`-Endpunkte; `/categories` + Move sind **neue API-Endpunkte in Phase 2**.
- Landmine: **kein bestehender GHCR-Build-Workflow** im Repo — D-20 greenfield, nicht "mirror".

### File Created
`.planning/phases/02-mcp-server/02-RESEARCH.md`

### Confidence Assessment
| Area | Level | Reason |
|------|-------|--------|
| Standard Stack | HIGH | Context7 + PyPI verifiziert |
| Architecture | HIGH | FastMCP-API + Phase-1-Contracts verifiziert |
| Pitfalls | HIGH | FastMCP-Source + PITFALLS.md |
| Deploy | MEDIUM | GHCR/Coolify greenfield, kein Workflow-Vorbild |

### Ready for Planning
Research vollständig (alle Open Questions RESOLVED 2026-07-31). Planner kann PLAN.md ausführen.
