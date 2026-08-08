# Coolify Labels — fertig zum Einfügen (HSTS + Banner-Strip)

**Stand:** 2026-08-08 · Phase 05.1-03  
**Quelle:** eure aktuellen Labels + HSTS/Strip aus dem Runbook

## So geht’s (pro App)

1. Coolify → App öffnen → **Labels**
2. **Readonly labels** abhaken
3. Gesamten Inhalt im Textfeld **ersetzen** durch den Block unten (Copy-Paste)
4. **Save** → **Redeploy**
5. Nächste App

Danach Verify:

```bash
curl -sI https://pbox.puzzlesstool.online | grep -iE 'strict-transport|server:|x-powered-by:'
curl -sI https://api.puzzlesstool.online | grep -iE 'strict-transport|server:|x-powered-by:'
curl -sI https://mcp.puzzlesstool.online | grep -iE 'strict-transport|server:|x-powered-by:'
curl -sI https://puzzlesstool.online | grep -i strict-transport-security
```

Erwartung: auf pbox/api/mcp → `Strict-Transport-Security: max-age=31536000; includeSubDomains`, kein `Server:` / `X-Powered-By:`. Apex → kein `includeSubDomains`.

---

## Was geändert wurde (Diff-Logik)

| Änderung | Wo |
|----------|-----|
| **NEU** 3× HSTS-Middleware-Zeilen | nach `gzip.compress=true` |
| **NEU** 2× Strip-Middleware-Zeilen (`Server=` / `X-Powered-By=` leer = löschen) | direkt danach |
| **EDIT** HTTPS-Router `middlewares=` | von `gzip` → `gzip,hsts-<app>,strip-headers-<app>` |
| Rest | unverändert (Domain, TLS, Ports, Caddy) |

---

## 1) API — `puzzlessbox-api-ghcr` · `api.puzzlesstool.online`

UUID: `pasmduuzitoh21qipyq3ay1l` · Port: `8000`

```
traefik.enable=true
traefik.http.middlewares.gzip.compress=true
traefik.http.middlewares.hsts-api.headers.stsSeconds=31536000
traefik.http.middlewares.hsts-api.headers.stsIncludeSubdomains=true
traefik.http.middlewares.hsts-api.headers.forceSTSHeader=true
traefik.http.middlewares.strip-headers-api.headers.customResponseHeaders.Server=
traefik.http.middlewares.strip-headers-api.headers.customResponseHeaders.X-Powered-By=
traefik.http.middlewares.redirect-to-https.redirectscheme.scheme=https
traefik.http.routers.http-0-pasmduuzitoh21qipyq3ay1l.entryPoints=http
traefik.http.routers.http-0-pasmduuzitoh21qipyq3ay1l.middlewares=redirect-to-https
traefik.http.routers.http-0-pasmduuzitoh21qipyq3ay1l.rule=Host(`api.puzzlesstool.online`) && PathPrefix(`/`)
traefik.http.routers.http-0-pasmduuzitoh21qipyq3ay1l.service=http-0-pasmduuzitoh21qipyq3ay1l
traefik.http.routers.https-0-pasmduuzitoh21qipyq3ay1l.entryPoints=https
traefik.http.routers.https-0-pasmduuzitoh21qipyq3ay1l.middlewares=gzip,hsts-api,strip-headers-api
traefik.http.routers.https-0-pasmduuzitoh21qipyq3ay1l.rule=Host(`api.puzzlesstool.online`) && PathPrefix(`/`)
traefik.http.routers.https-0-pasmduuzitoh21qipyq3ay1l.service=https-0-pasmduuzitoh21qipyq3ay1l
traefik.http.routers.https-0-pasmduuzitoh21qipyq3ay1l.tls.certresolver=letsencrypt
traefik.http.routers.https-0-pasmduuzitoh21qipyq3ay1l.tls=true
traefik.http.services.http-0-pasmduuzitoh21qipyq3ay1l.loadbalancer.server.port=8000
traefik.http.services.https-0-pasmduuzitoh21qipyq3ay1l.loadbalancer.server.port=8000
caddy_0.encode=zstd gzip
caddy_0.handle_path.0_reverse_proxy={{upstreams 8000}}
caddy_0.handle_path=/*
caddy_0.header=-Server
caddy_0.try_files={path} /index.html /index.php
caddy_0=https://api.puzzlesstool.online
caddy_ingress_network=coolify
```

**Einzige inhaltliche Edit-Zeile vs. vorher:**  
`…https-0-….middlewares=gzip` → `…middlewares=gzip,hsts-api,strip-headers-api`

---

## 2) WEB — `puzzlessbox-web` · `pbox.puzzlesstool.online`

UUID: `qxpgv6p1rp3vupue9al8hbzz` · Port: `3000`

```
traefik.enable=true
traefik.http.middlewares.gzip.compress=true
traefik.http.middlewares.hsts-pbox.headers.stsSeconds=31536000
traefik.http.middlewares.hsts-pbox.headers.stsIncludeSubdomains=true
traefik.http.middlewares.hsts-pbox.headers.forceSTSHeader=true
traefik.http.middlewares.strip-headers-pbox.headers.customResponseHeaders.Server=
traefik.http.middlewares.strip-headers-pbox.headers.customResponseHeaders.X-Powered-By=
traefik.http.middlewares.redirect-to-https.redirectscheme.scheme=https
traefik.http.routers.http-0-qxpgv6p1rp3vupue9al8hbzz.entryPoints=http
traefik.http.routers.http-0-qxpgv6p1rp3vupue9al8hbzz.middlewares=redirect-to-https
traefik.http.routers.http-0-qxpgv6p1rp3vupue9al8hbzz.rule=Host(`pbox.puzzlesstool.online`) && PathPrefix(`/`)
traefik.http.routers.http-0-qxpgv6p1rp3vupue9al8hbzz.service=http-0-qxpgv6p1rp3vupue9al8hbzz
traefik.http.routers.https-0-qxpgv6p1rp3vupue9al8hbzz.entryPoints=https
traefik.http.routers.https-0-qxpgv6p1rp3vupue9al8hbzz.middlewares=gzip,hsts-pbox,strip-headers-pbox
traefik.http.routers.https-0-qxpgv6p1rp3vupue9al8hbzz.rule=Host(`pbox.puzzlesstool.online`) && PathPrefix(`/`)
traefik.http.routers.https-0-qxpgv6p1rp3vupue9al8hbzz.service=https-0-qxpgv6p1rp3vupue9al8hbzz
traefik.http.routers.https-0-qxpgv6p1rp3vupue9al8hbzz.tls.certresolver=letsencrypt
traefik.http.routers.https-0-qxpgv6p1rp3vupue9al8hbzz.tls=true
traefik.http.services.http-0-qxpgv6p1rp3vupue9al8hbzz.loadbalancer.server.port=3000
traefik.http.services.https-0-qxpgv6p1rp3vupue9al8hbzz.loadbalancer.server.port=3000
caddy_0.encode=zstd gzip
caddy_0.handle_path.0_reverse_proxy={{upstreams 3000}}
caddy_0.handle_path=/*
caddy_0.header=-Server
caddy_0.try_files={path} /index.html /index.php
caddy_0=https://pbox.puzzlesstool.online
caddy_ingress_network=coolify
```

**Edit-Zeile:** `…middlewares=gzip` → `…middlewares=gzip,hsts-pbox,strip-headers-pbox`

---

## 3) MCP — `puzzlessbox-mcp` · `mcp.puzzlesstool.online`

UUID: `n5frtiupale5c2zjm9fyk1qc` · Port: `8000`

```
traefik.enable=true
traefik.http.middlewares.gzip.compress=true
traefik.http.middlewares.hsts-mcp.headers.stsSeconds=31536000
traefik.http.middlewares.hsts-mcp.headers.stsIncludeSubdomains=true
traefik.http.middlewares.hsts-mcp.headers.forceSTSHeader=true
traefik.http.middlewares.strip-headers-mcp.headers.customResponseHeaders.Server=
traefik.http.middlewares.strip-headers-mcp.headers.customResponseHeaders.X-Powered-By=
traefik.http.middlewares.redirect-to-https.redirectscheme.scheme=https
traefik.http.routers.http-0-n5frtiupale5c2zjm9fyk1qc.entryPoints=http
traefik.http.routers.http-0-n5frtiupale5c2zjm9fyk1qc.middlewares=redirect-to-https
traefik.http.routers.http-0-n5frtiupale5c2zjm9fyk1qc.rule=Host(`mcp.puzzlesstool.online`) && PathPrefix(`/`)
traefik.http.routers.http-0-n5frtiupale5c2zjm9fyk1qc.service=http-0-n5frtiupale5c2zjm9fyk1qc
traefik.http.routers.https-0-n5frtiupale5c2zjm9fyk1qc.entryPoints=https
traefik.http.routers.https-0-n5frtiupale5c2zjm9fyk1qc.middlewares=gzip,hsts-mcp,strip-headers-mcp
traefik.http.routers.https-0-n5frtiupale5c2zjm9fyk1qc.rule=Host(`mcp.puzzlesstool.online`) && PathPrefix(`/`)
traefik.http.routers.https-0-n5frtiupale5c2zjm9fyk1qc.service=https-0-n5frtiupale5c2zjm9fyk1qc
traefik.http.routers.https-0-n5frtiupale5c2zjm9fyk1qc.tls.certresolver=letsencrypt
traefik.http.routers.https-0-n5frtiupale5c2zjm9fyk1qc.tls=true
traefik.http.services.http-0-n5frtiupale5c2zjm9fyk1qc.loadbalancer.server.port=8000
traefik.http.services.https-0-n5frtiupale5c2zjm9fyk1qc.loadbalancer.server.port=8000
caddy_0.encode=zstd gzip
caddy_0.handle_path.0_reverse_proxy={{upstreams 8000}}
caddy_0.handle_path=/*
caddy_0.header=-Server
caddy_0.try_files={path} /index.html /index.php
caddy_0=https://mcp.puzzlesstool.online
caddy_ingress_network=coolify
```

**Edit-Zeile:** `…middlewares=gzip` → `…middlewares=gzip,hsts-mcp,strip-headers-mcp`

---

## Checkliste

- [ ] API: Paste → Save → Redeploy
- [ ] WEB: Paste → Save → Redeploy
- [ ] MCP: Paste → Save → Redeploy
- [ ] curl-Verify (oben) grün
- [ ] Checkpoint: `approved` im Chat

## Rollback

**Reset Labels to Defaults** in Coolify → Readonly wieder an → Redeploy.  
Oder: HSTS/Strip-Zeilen löschen und `middlewares=` wieder nur auf `gzip` setzen.
