# 02-DEPLOY-SPEC — MCP GHCR + Coolify Deploy (Plan 02-04)

**Status:** Executor-ready (spec only — kein Dockerfile/Workflow im Repo bis Execute)  
**Plan:** `02-04-PLAN.md`  
**Erstellt:** 2026-07-31  
**Pinning-Konvention:** wie `.github/workflows/ci.yml` — voller Commit-SHA + `# vX.Y.Z`-Kommentar

---

## D-23 Checkpoint (pre-confirmed)

| Feld | Wert |
|------|------|
| **Entscheidung** | `separate-image` |
| **Status** | **pre-confirmed** |
| **Quelle** | User-Anfrage: volle Phase-2-Vorbereitung vor Execute |
| **Kontext** | `.planning/phases/02-mcp-server/02-CONTEXT.md` **D-23** — top-level `mcp-server/` mit eigenem Image, nicht FastMCP in `api/` gemountet; one-way Deploy-Topologie (eigenes Image, Domain, GHCR-Package, CI-Workflow) |
| **Option** | Separate `mcp-server/`-Image + eigene Coolify-App unter `mcp.puzzlesstool.online` |
| **Verworfen** | `mounted` — widerspricht D-23 + MCP-02; STACK.md-Notiz überholt |

Executor: Checkpoint in 02-04 als erledigt behandeln; kein erneutes Gate nötig.

---

## 1. Secrets Checklist

| Secret | Wo | Zweck | Setup |
|--------|-----|-------|-------|
| `GITHUB_TOKEN` | GitHub Actions (automatisch) | GHCR push | Workflow braucht `permissions: packages: write` — Token wird von Actions injiziert |
| `COOLIFY_MCP_WEBHOOK` | GitHub → Settings → Secrets and variables → Actions | Coolify Deploy nach erfolgreichem Push | Coolify App → Webhooks → URL kopieren, als Repo-Secret anlegen |

**Nicht im Workflow/Repo:** Bearer-Tokens, Webhook-URLs im Klartext, `SERVICE_BEARER_TOKEN` (nur Coolify App Env).

---

## 2. GHCR Image

| Feld | Wert |
|------|------|
| **Registry** | `ghcr.io` |
| **Image** | `ghcr.io/${{ github.repository_owner }}/puzzlessbox-mcp` |
| **Tags** | `latest` + `sha-<short>` (via `docker/metadata-action`, `type=sha,prefix=sha-`) |
| **Visibility** | Public oder org-policy — Package nach erstem Push in GHCR prüfen |

Coolify zieht typischerweise `:latest`; Rollback via `:sha-<commit>`.

---

## 3. Pinned GitHub Actions (verifiziert 2026-07-31)

| Action | SHA | Version |
|--------|-----|---------|
| `actions/checkout` | `3d3c42e5aac5ba805825da76410c181273ba90b1` | v7 (wie `ci.yml`) |
| `docker/login-action` | `dbcb813823bdd20940b903addbd779551569679f` | v4.6.0 |
| `docker/metadata-action` | `dc802804100637a589fabce1cb79ff13a1411302` | v6.2.0 |
| `docker/build-push-action` | `53b7df96c91f9c12dcc8a07bcb9ccacbed38856a` | v7.3.0 |

Vor Execute: Tags erneut gegen `git ls-remote` prüfen falls Releases neuer.

---

## 4. Workflow — `.github/workflows/deploy-mcp.yml`

Copy-paste für Executor (entspricht 02-04-PLAN Task 1 action block):

```yaml
name: Deploy MCP

on:
  push:
    branches: [main]
    paths:
      - "mcp-server/**"
      - ".github/workflows/deploy-mcp.yml"

concurrency:
  group: deploy-mcp-${{ github.ref }}
  cancel-in-progress: true

permissions:
  contents: read
  packages: write

jobs:
  build-push:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@3d3c42e5aac5ba805825da76410c181273ba90b1 # v7

      - uses: docker/login-action@dbcb813823bdd20940b903addbd779551569679f # v4.6.0
        with:
          registry: ghcr.io
          username: ${{ github.actor }}
          password: ${{ secrets.GITHUB_TOKEN }}

      - id: meta
        uses: docker/metadata-action@dc802804100637a589fabce1cb79ff13a1411302 # v6.2.0
        with:
          images: ghcr.io/${{ github.repository_owner }}/puzzlessbox-mcp
          tags: |
            type=raw,value=latest
            type=sha,prefix=sha-

      - uses: docker/build-push-action@53b7df96c91f9c12dcc8a07bcb9ccacbed38856a # v7.3.0
        with:
          context: ./mcp-server
          push: true
          tags: ${{ steps.meta.outputs.tags }}
          labels: ${{ steps.meta.outputs.labels }}

      - name: Trigger Coolify deploy
        if: success()
        run: curl -fsSL -X POST "${{ secrets.COOLIFY_MCP_WEBHOOK }}"
```

**Acceptance (automatisiert):**

```bash
docker build -t puzzlessbox-mcp:test mcp-server
python -c "import yaml; d=yaml.safe_load(open('.github/workflows/deploy-mcp.yml')); assert 'mcp-server/**' in str(d); assert 'packages' in str(d); print('workflow ok')"
grep -E "uses: .*@v[0-9]" .github/workflows/deploy-mcp.yml  # keine Treffer
grep -c "secrets.COOLIFY_MCP_WEBHOOK\|secrets.GITHUB_TOKEN" .github/workflows/deploy-mcp.yml  # >= 2
```

---

## 5. Coolify user_setup (aus 02-04-PLAN)

**Warum:** MCP als separate Docker-Image-App unter `mcp.puzzlesstool.online` (D-20/D-23, OPS-01/04-Slice).

### Dashboard

| Task | Ort |
|------|-----|
| Docker-Image-App anlegen (`ghcr.io/<owner>/puzzlessbox-mcp:latest`), Domain `mcp.puzzlesstool.online`, Traefik/Let's-Encrypt TLS | Coolify → Projekt → New Resource → Docker Image |
| Health-Check-Pfad `/health` (D-22) | Coolify → App → Health Checks |
| Deploy-Webhook-URL + Token → GitHub Secret `COOLIFY_MCP_WEBHOOK` | Coolify → App → Webhooks |

### App Env Vars

| Name | Source |
|------|--------|
| `SERVICE_BEARER_TOKEN` | Gleicher Wert wie API (`X-Service-Bearer` Gateway-Auth, D-01) |
| `MCP_API_BASE_URL` | Interne Docker-Netz-URL der API, z.B. `http://puzzlessbox-api:8000` (D-15) |
| `ENV` | `prod` |

**Precondition:** Coolify-App + Webhook-Secret vor erstem Workflow-Run — sonst schlägt Webhook-Step fehl.

---

## 6. Verification Commands (human-check, end-of-phase)

Nach Coolify-Deploy gegen Live-URL:

```bash
# 1. Health + TLS
curl -sS https://mcp.puzzlesstool.online/health
# Erwartung: 200 {"status":"ok","service":"mcp-server"}

# 2. MCP ohne Auth → 401
curl -sS -o /dev/null -w "%{http_code}" -X POST https://mcp.puzzlesstool.online/mcp
# Erwartung: 401

# 3. Falscher Bearer → 401
curl -sS -o /dev/null -w "%{http_code}" -X POST https://mcp.puzzlesstool.online/mcp \
  -H "Authorization: Bearer WRONG"
# Erwartung: 401

# 4. Coolify UI: App healthy, Health-Check `/health` konfiguriert
```

Resume-Signal: `approved` oder Abweichungen benennen.

---

## 7. Executor Notes

- **Dockerfile:** `mcp-server/Dockerfile` — spiegelt `api/Dockerfile` **ohne** alembic (D-06); `python:3.14-slim`, `uvicorn app.server:app :8000`
- **allowed_hosts:** `mcp.puzzlesstool.online` in `mcp-server/app/server.py` (02-01) — verify only
- **Greenfield:** kein bestehender GHCR-Workflow; `ci.yml` liefert nur Skelett (concurrency, SHA-pins)
- **Threat model:** T-02-14..16 in 02-04-PLAN — keine Klartext-Secrets, SHA-pins, TLS-only prod
