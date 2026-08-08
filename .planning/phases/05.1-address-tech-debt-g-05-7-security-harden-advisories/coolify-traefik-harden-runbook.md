# Coolify / Traefik HSTS + Banner-Strip Runbook

**Phase:** 05.1 — Security harden advisories (D-06, D-07, D-08)  
**Created:** 2026-08-08 (Plan 05.1-03)

---

## 1. Goal

Apply **HSTS** and **Server / X-Powered-By banner stripping** at the Traefik ingress layer for the three public **leaf** FQDNs:

| Host | Coolify app | UUID |
|------|-------------|------|
| `pbox.puzzlesstool.online` | `puzzlessbox-web` | `qxpgv6p1rp3vupue9al8hbzz` |
| `api.puzzlesstool.online` | `puzzlessbox-api-ghcr` | `pasmduuzitoh21qipyq3ay1l` |
| `mcp.puzzlesstool.online` | `puzzlessbox-mcp` | `n5frtiupale5c2zjm9fyk1qc` |

**Excluded (D-07):** Do **not** add HSTS with `includeSubDomains` on apex `puzzlesstool.online`. Leaf-only HSTS avoids forcing HTTPS on unrelated sibling subdomains.

**No preload** in v1 (D-06).

Defense in depth: Next.js `poweredByHeader: false` (Plan 05.1-03 Task 1) disables app-layer `X-Powered-By`; Traefik strips any remaining banners at the gateway.

---

## 2. Traefik middleware labels (per app)

Add these Docker labels on **each** of the three Coolify applications. Replace `<app>` with `pbox`, `api`, or `mcp`. Replace `<router>` with the HTTPS router name for that app (see table below).

### 2.1 HSTS middleware

```
traefik.http.middlewares.hsts-<app>.headers.stsSeconds=31536000
traefik.http.middlewares.hsts-<app>.headers.stsIncludeSubdomains=true
traefik.http.middlewares.hsts-<app>.headers.forceSTSHeader=true
```

### 2.2 Banner-strip middleware (empty value = strip per Pitfall 2)

```
traefik.http.middlewares.strip-headers-<app>.headers.customResponseHeaders.Server=
traefik.http.middlewares.strip-headers-<app>.headers.customResponseHeaders.X-Powered-By=
```

### 2.3 Wire middlewares into existing HTTPS router

**Append** to the existing `traefik.http.routers.<router>.middlewares` value — do **not** replace existing middlewares (each app currently has `gzip`).

| App | HTTPS router name | Current middlewares | New middlewares value |
|-----|-------------------|---------------------|------------------------|
| pbox | `https-0-qxpgv6p1rp3vupue9al8hbzz` | `gzip` | `gzip,hsts-pbox,strip-headers-pbox` |
| api | `https-0-pasmduuzitoh21qipyq3ay1l` | `gzip` | `gzip,hsts-api,strip-headers-api` |
| mcp | `https-0-n5frtiupale5c2zjm9fyk1qc` | `gzip` | `gzip,hsts-mcp,strip-headers-mcp` |

Label to **edit** (not add) per app:

```
traefik.http.routers.<router>.middlewares=gzip,hsts-<app>,strip-headers-<app>
```

### 2.4 Full label block — pbox (web)

```
traefik.http.middlewares.hsts-pbox.headers.stsSeconds=31536000
traefik.http.middlewares.hsts-pbox.headers.stsIncludeSubdomains=true
traefik.http.middlewares.hsts-pbox.headers.forceSTSHeader=true
traefik.http.middlewares.strip-headers-pbox.headers.customResponseHeaders.Server=
traefik.http.middlewares.strip-headers-pbox.headers.customResponseHeaders.X-Powered-By=
traefik.http.routers.https-0-qxpgv6p1rp3vupue9al8hbzz.middlewares=gzip,hsts-pbox,strip-headers-pbox
```

### 2.5 Full label block — api

```
traefik.http.middlewares.hsts-api.headers.stsSeconds=31536000
traefik.http.middlewares.hsts-api.headers.stsIncludeSubdomains=true
traefik.http.middlewares.hsts-api.headers.forceSTSHeader=true
traefik.http.middlewares.strip-headers-api.headers.customResponseHeaders.Server=
traefik.http.middlewares.strip-headers-api.headers.customResponseHeaders.X-Powered-By=
traefik.http.routers.https-0-pasmduuzitoh21qipyq3ay1l.middlewares=gzip,hsts-api,strip-headers-api
```

### 2.6 Full label block — mcp

```
traefik.http.middlewares.hsts-mcp.headers.stsSeconds=31536000
traefik.http.middlewares.hsts-mcp.headers.stsIncludeSubdomains=true
traefik.http.middlewares.hsts-mcp.headers.forceSTSHeader=true
traefik.http.middlewares.strip-headers-mcp.headers.customResponseHeaders.Server=
traefik.http.middlewares.strip-headers-mcp.headers.customResponseHeaders.X-Powered-By=
traefik.http.routers.https-0-n5frtiupale5c2zjm9fyk1qc.middlewares=gzip,hsts-mcp,strip-headers-mcp
```

---

## 3. Coolify application steps

### 3.1 Coolify MCP attempt (2026-08-08)

| Step | Result |
|------|--------|
| `get_application` for `qxpgv6p1rp3vupue9al8hbzz` (web) | **OK** — `running:healthy`, `custom_labels` present (base64 Traefik labels) |
| `get_application` for `pasmduuzitoh21qipyq3ay1l` (api) | **OK** — `running:healthy` |
| `get_application` for `n5frtiupale5c2zjm9fyk1qc` (mcp) | **OK** — `running:healthy` |
| `update_application` via MCP | **NOT SUPPORTED** — schema accepts only `uuid`, `name`, `description`; no `custom_labels` / docker-label field |

**Primary path:** Coolify UI (D-19 manual-steps convention per Phase 5).

### 3.2 UI steps (per app)

1. Open Coolify → **Projects** → select environment → open application (web / api / mcp).
2. Go to **Configuration** → **Docker Labels** (or **Advanced** → **Custom Docker Options / Labels** depending on Coolify version).
3. Add the six labels from §2.4 / §2.5 / §2.6 (or add five new + **edit** the existing `middlewares` line).
4. **Save** configuration.
5. **Redeploy** (or Restart) the application so Traefik reloads container labels.
6. Repeat for all three apps.

**Order:** api → mcp → web (or any order); verify each host after redeploy.

---

## 4. Verification commands

Run after labels applied and all three apps redeployed:

### 4.1 HSTS on leaf FQDNs (D-06)

```bash
curl -sI https://pbox.puzzlesstool.online | grep -i strict-transport-security
curl -sI https://api.puzzlesstool.online | grep -i strict-transport-security
curl -sI https://mcp.puzzlesstool.online | grep -i strict-transport-security
```

**Expected (each):** `Strict-Transport-Security: max-age=31536000; includeSubDomains` (no `preload`).

### 4.2 Banners stripped (D-08, D-09)

```bash
curl -sI https://pbox.puzzlesstool.online | grep -iE 'server:|x-powered-by:'
curl -sI https://api.puzzlesstool.online | grep -iE 'server:|x-powered-by:'
curl -sI https://mcp.puzzlesstool.online | grep -iE 'server:|x-powered-by:'
```

**Expected:** no output (headers absent).

### 4.3 Apex negative check (D-07)

```bash
curl -sI https://puzzlesstool.online | grep -i strict-transport-security
```

**Expected:** no output, **or** a `Strict-Transport-Security` line **without** `includeSubDomains`.  
**Unacceptable:** `max-age=...; includeSubDomains` on apex.

### 4.4 WebApp health (post next.config change)

```bash
curl -s https://pbox.puzzlesstool.online/api/health
```

**Expected:** `200` with body `{"status":"ok"}`.

### 4.5 Optional — MCP well-known stub (Plan 05.1-02)

```bash
curl -s https://mcp.puzzlesstool.online/.well-known/oauth-protected-resource/mcp | jq
```

**Expected:** `200` with `resource` + `bearer_methods_supported`; no `authorization_servers`.

---

## 5. Rollback

1. Remove the six HSTS/strip labels added in §2 from each Coolify app.
2. Restore each router's `middlewares` label to `gzip` only.
3. Save and redeploy each app.
4. New responses stop sending HSTS immediately; browsers may retain HSTS until `max-age` expires (~1 year for clients that already cached it).

---

## References

- [MDN: Strict-Transport-Security](https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/Strict-Transport-Security)
- [Traefik Headers middleware](https://doc.traefik.io/traefik/v2.9/middlewares/headers/)
- `.planning/phases/05.1-address-tech-debt-g-05-7-security-harden-advisories/05.1-RESEARCH.md` — Pitfall 2 (empty-value strip syntax)
- `.planning/phases/05-coolify-deployment-ci-cd-h-rtung/05-UAT.md` — prod URLs and app UUIDs
