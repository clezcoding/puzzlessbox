FROM node:24-alpine AS base

FROM base AS deps
RUN apk add --no-cache libc6-compat
WORKDIR /app/webapp
COPY webapp/package.json webapp/pnpm-lock.yaml webapp/pnpm-workspace.yaml ./
RUN corepack enable pnpm && pnpm i --frozen-lockfile

FROM base AS builder
WORKDIR /app
ENV CI=true
ARG NEXT_PUBLIC_API_URL=https://api.puzzlesstool.online
ARG NEXT_PUBLIC_APP_URL=https://pbox.puzzlesstool.online
ENV NEXT_PUBLIC_API_URL=$NEXT_PUBLIC_API_URL
ENV NEXT_PUBLIC_APP_URL=$NEXT_PUBLIC_APP_URL
# Keep brand/ + webapp/ as siblings so next.config outputFileTracingRoot
# (repo root) nests standalone at webapp/server.js — not /app/app/server.js.
COPY --from=deps /app/webapp/node_modules ./webapp/node_modules
COPY brand ./brand
COPY webapp ./webapp
WORKDIR /app/webapp
RUN corepack enable pnpm && pnpm run build

FROM base AS runner
WORKDIR /app
ENV NODE_ENV=production
ENV PORT=3000
ENV HOSTNAME="0.0.0.0"

RUN apk add --no-cache curl

RUN addgroup --system --gid 1001 nodejs
RUN adduser --system --uid 1001 nextjs

COPY --from=builder --chown=nextjs:nodejs /app/webapp/.next/standalone ./
COPY --from=builder --chown=nextjs:nodejs /app/webapp/.next/static ./webapp/.next/static
COPY --from=builder --chown=nextjs:nodejs /app/webapp/public ./webapp/public

# Fail the image build if tracing-root nesting drifts again.
RUN test -f webapp/server.js

USER nextjs
EXPOSE 3000
# Better Auth schema is applied at process start via instrumentation.ts
# (official getMigrations) when AUTH_MIGRATE_ON_START != false.
CMD ["node", "webapp/server.js"]
