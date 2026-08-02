---
phase: 05-coolify-deployment-ci-cd-h-rtung
reviewed: 2026-08-02T21:18:00Z
depth: standard
files_reviewed: 7
files_reviewed_list:
  - webapp/Dockerfile
  - webapp/app/api/health/route.ts
  - webapp/app/api/health/route.test.ts
  - webapp/next.config.ts
  - .github/workflows/deploy-web.yml
  - .github/workflows/deploy-api.yml
  - webapp/.dockerignore
findings:
  critical: 0
  warning: 4
  info: 2
  total: 6
status: issues
---

# Phase 05: Code Review Report

**Reviewed:** 2026-08-02T21:18:00Z  
**Depth:** standard  
**Files Reviewed:** 7  
**Status:** issues

## Summary

Phase-05-Infra (Coolify CI/CD, WebApp-Dockerfile, Health-Route, Deploy-Workflows) reviewed. Core-Pipeline solid: multi-stage non-root image, SHA-pinned Actions, GET-webhook with status assert, lightweight `/api/health`. No production-blocking defects in the GHA path.

Four warnings: root `.dockerignore` missing so `webapp/.dockerignore` is ineffective at repo-root build context; health auth test bypasses middleware; deploy workflows verify webhook only, not live health; broad `images.remotePatterns` widen image-proxy abuse surface.

## Warnings

### WR-01: Root `.dockerignore` missing — `webapp/.dockerignore` never applied

**File:** `webapp/Dockerfile:14`, `.github/workflows/deploy-web.yml:42-43`, `webapp/.dockerignore:1-6`  
**Issue:** `deploy-web.yml` sets `context: .` (repo root). Docker reads `.dockerignore` only from the context root, not beside `webapp/Dockerfile`. The `webapp/.dockerignore` added in 05-04 is ignored. `COPY webapp/ .` copies every file under `webapp/`, including `.env*` if present on the build host. GHA checkout omits gitignored env files, but local `docker build` can bake secrets into image layers. Entire monorepo is also sent as build context (planning docs, `api/`, etc.).  
**Fix:** Add a repo-root `.dockerignore` (or relocate patterns from `webapp/.dockerignore`):

```dockerignore
# repo-root .dockerignore (for webapp monorepo build)
**
!webapp/**
!brand/**
webapp/node_modules
webapp/.next
webapp/.env*
.git
**/*.md
```

Alternatively narrow `context` to `./webapp` and adjust Dockerfile `COPY` paths for `brand/`.

### WR-02: Health auth test does not exercise middleware

**File:** `webapp/app/api/health/route.test.ts:12-16`  
**Issue:** Test `"does not require auth"` imports and calls `GET()` directly, bypassing `middleware.ts`. It only asserts absence of `www-authenticate`; middleware redirects unauthenticated users (302), it does not set that header. A future matcher change (e.g. `/api/:path*`) would not be caught by this test while the route handler still returns 200 in isolation.  
**Fix:** Add an integration test via `next/server` test harness or `fetch` against a running app, asserting `GET /api/health` returns 200 without session cookie and without redirect:

```typescript
it("is reachable through middleware without auth", async () => {
  const res = await fetch("http://localhost:3000/api/health", { redirect: "manual" });
  expect(res.status).toBe(200);
});
```

Or document that middleware exclusion is enforced only by `config.matcher` and add a matcher regression test.

### WR-03: Deploy workflows stop at webhook — no post-deploy health gate

**File:** `.github/workflows/deploy-web.yml:48-55`, `.github/workflows/deploy-api.yml:46-53`  
**Issue:** CI succeeds when Coolify webhook returns 200/202. It does not verify the new image is running or that `/api/health` / `/health` responds. A broken image (failed pull, crash loop) can pass CI while production stays unhealthy until manual discovery.  
**Fix:** After webhook, poll the public health URL with bounded retries:

```yaml
- name: Verify deployment health
  run: |
    for i in $(seq 1 30); do
      CODE=$(curl -s -o /dev/null -w "%{http_code}" https://pbox.puzzlesstool.online/api/health)
      [ "$CODE" = "200" ] && exit 0
      sleep 10
    done
    echo "Health check failed after deploy"
    exit 1
```

Mirror for API with `https://api.puzzlesstool.online/health`.

### WR-04: Overly broad `images.remotePatterns` in Next config

**File:** `webapp/next.config.ts:6-16`  
**Issue:** Wildcard hostnames (`**.amazonaws.com`, `**.cloudfront.net`, `**.githubusercontent.com`, etc.) allow Next.js image optimization to fetch from any matching host. If user-controlled image URLs reach `next/image`, this expands SSRF / open-proxy abuse surface beyond project-owned assets.  
**Fix:** Replace wildcards with explicit hostnames used by the app (e.g. your CDN bucket, known avatar providers). Remove unused patterns.

## Info

### IN-01: `cancel-in-progress: true` can abort in-flight deploy workflows

**File:** `.github/workflows/deploy-web.yml:12-14`, `.github/workflows/deploy-api.yml:11-13`  
**Issue:** Rapid pushes cancel the prior workflow. If the cancelled run already pushed an image but not yet triggered webhook, registry and Coolify state can diverge briefly. Low probability on `main`, worth knowing for incident response.  
**Fix:** Accept trade-off or set `cancel-in-progress: false` if serial deploy ordering matters more than queue latency.

### IN-02: Health route lacks explicit cache-control

**File:** `webapp/app/api/health/route.ts:3-5`  
**Issue:** No `Cache-Control: no-store` on the response. Unlikely to break Coolify/Traefik today, but a future CDN in front could cache a stale 200.  
**Fix:**

```typescript
return NextResponse.json(
  { status: "ok" },
  { headers: { "Cache-Control": "no-store" } },
);
```

---

_Reviewed: 2026-08-02T21:18:00Z_  
_Reviewer: Claude (gsd-code-reviewer)_  
_Depth: standard_
