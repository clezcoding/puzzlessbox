# Phase 5: Coolify-Deployment, CI/CD & Härtung - Pattern Map

**Mapped:** 2026-08-02
**Files analyzed:** 5
**Analogs found:** 5 / 5

## File Classification

| New/Modified File | Role | Data Flow | Closest Analog | Match Quality |
|-------------------|------|-----------|----------------|---------------|
| `.github/workflows/deploy-api.yml` | CI/CD workflow | request-response | `.github/workflows/deploy-mcp.yml` | exact |
| `.github/workflows/deploy-web.yml` | CI/CD workflow | request-response | `.github/workflows/deploy-mcp.yml` | exact |
| `webapp/Dockerfile` | Dockerfile | file-I/O | `mcp-server/Dockerfile` | role-match |
| `webapp/app/api/health/route.ts` | route | request-response | `api/app/routers/health.py` | role-match |
| `webapp/next.config.ts` | config | transform | `webapp/next.config.ts` | exact |

---

## Pattern Assignments

### `.github/workflows/deploy-api.yml` (CI/CD workflow, request-response)

**Analog:** `.github/workflows/deploy-mcp.yml`

**Imports/Triggers pattern** (lines 1-13):
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
```

**Build and Push pattern** (lines 18-44):
```yaml
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
```

**Trigger Coolify Deploy (GET with Status Assert) pattern** (lines 45-50 adapted for D-06):
```yaml
      - name: Trigger Coolify deploy
        if: success()
        run: |
          STATUS=$(curl -s -o /dev/null -w "%{http_code}" -X GET "${{ secrets.COOLIFY_API_WEBHOOK }}" -H "Authorization: Bearer ${{ secrets.COOLIFY_TOKEN }}")
          if [ "$STATUS" -ne 200 ] && [ "$STATUS" -ne 202 ]; then
            echo "Webhook failed with status $STATUS"
            exit 1
          fi
```

---

### `.github/workflows/deploy-web.yml` (CI/CD workflow, request-response)

**Analog:** `.github/workflows/deploy-mcp.yml`

**Imports/Triggers pattern** (lines 1-13):
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
```

**Build and Push pattern** (lines 18-44):
```yaml
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
```

**Trigger Coolify Deploy (GET with Status Assert) pattern** (lines 45-50 adapted for D-06):
```yaml
      - name: Trigger Coolify deploy
        if: success()
        run: |
          STATUS=$(curl -s -o /dev/null -w "%{http_code}" -X GET "${{ secrets.COOLIFY_WEB_WEBHOOK }}" -H "Authorization: Bearer ${{ secrets.COOLIFY_TOKEN }}")
          if [ "$STATUS" -ne 200 ] && [ "$STATUS" -ne 202 ]; then
            echo "Webhook failed with status $STATUS"
            exit 1
          fi
```

---

### `webapp/Dockerfile` (Dockerfile, file-I/O)

**Analog:** `mcp-server/Dockerfile` (multi-stage structure) + Next.js Standalone with pnpm

**Imports/Base pattern** (lines 1-3):
```dockerfile
FROM node:24-alpine AS base
```

**Core Build/Install pattern** (adapted from `mcp-server/Dockerfile` lines 5-10 for Node/pnpm):
```dockerfile
FROM base AS deps
RUN apk add --no-cache libc6-compat
WORKDIR /app
COPY package.json pnpm-lock.yaml* ./
RUN corepack enable pnpm && pnpm i --frozen-lockfile

FROM base AS builder
WORKDIR /app
COPY --from=deps /app/node_modules ./node_modules
COPY . .
RUN corepack enable pnpm && pnpm run build
```

**Runner stage pattern** (adapted from `mcp-server/Dockerfile` lines 12-14 for Next.js standalone):
```dockerfile
FROM base AS runner
WORKDIR /app
ENV NODE_ENV=production
ENV PORT=3000
ENV HOSTNAME="0.0.0.0"

RUN addgroup --system --gid 1001 nodejs
RUN adduser --system --uid 1001 nextjs

COPY --from=builder /app/public ./public
COPY --from=builder --chown=nextjs:nodejs /app/.next/standalone ./
COPY --from=builder --chown=nextjs:nodejs /app/.next/static ./.next/static

USER nextjs
EXPOSE 3000
CMD ["node", "server.js"]
```

---

### `webapp/app/api/health/route.ts` (route, request-response)

**Analog:** `api/app/routers/health.py` (logic) + `webapp/app/api/auth/[...all]/route.ts` (Next.js route syntax)

**Imports pattern** (lines 1-2):
```typescript
import { NextResponse } from "next/server";
```

**Core Pattern** (adapted from `api/app/routers/health.py` lines 11-14):
```typescript
export async function GET() {
  return NextResponse.json({ status: "ok" });
}
```

---

### `webapp/next.config.ts` (config, transform)

**Analog:** `webapp/next.config.ts` (itself)

**Core Configuration pattern** (lines 1-20):
```typescript
import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  output: "standalone",
  images: {
    remotePatterns: [
      { protocol: "https", hostname: "**.googleusercontent.com" },
      { protocol: "https", hostname: "**.ggpht.com" },
      { protocol: "https", hostname: "**.ytimg.com" },
      { protocol: "https", hostname: "**.githubusercontent.com" },
      { protocol: "https", hostname: "**.cloudfront.net" },
      { protocol: "https", hostname: "**.amazonaws.com" },
      { protocol: "https", hostname: "**.opengraph.xyz" },
      { protocol: "https", hostname: "**.notion.so" },
      { protocol: "https", hostname: "**.notion-static.com" },
    ],
  },
};

export default nextConfig;
```

---

## Shared Patterns

### Action Pinning
**Source:** `.github/workflows/ci.yml`
**Apply to:** All GitHub Actions workflows
```yaml
- uses: actions/checkout@3d3c42e5aac5ba805825da76410c181273ba90b1 # v7
- uses: docker/login-action@dbcb813823bdd20940b903addbd779551569679f # v4.6.0
- uses: docker/metadata-action@dc802804100637a589fabce1cb79ff13a1411302 # v6.2.0
- uses: docker/build-push-action@53b7df96c91f9c12dcc8a07bcb9ccacbed38856a # v7.3.0
```

### Health Check Path
**Source:** `api/app/routers/health.py`
**Apply to:** All service routers and Coolify configurations
```
Path: /health (for API/MCP)
Path: /api/health (for WebApp)
```

---

## No Analog Found

All files had strong analogs in the codebase.

---

## Metadata

**Analog search scope:** `.github/workflows/`, `api/`, `mcp-server/`, `webapp/`
**Files scanned:** 12
**Pattern extraction date:** 2026-08-02
