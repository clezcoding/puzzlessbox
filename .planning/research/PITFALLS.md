# Pitfalls Research

**Domain:** Personal Capture, Remote MCP, and Agentic Concurrency
**Researched:** 2026-07-28
**Confidence:** HIGH

## Critical Pitfalls

### Pitfall 1: Hermes Cron/dispatch_tool 30s Timeout Incompatibility

**What goes wrong:**
Attempting to use Hermes' native Cron scheduler to trigger the 30-second auto-save timeout fails. The auto-save fires at highly irregular intervals (either prematurely in under 5 seconds, or delayed by up to a minute), leading to a chaotic user experience where drafts are saved before the user can edit them, or are lost entirely.

**Why it happens:**
The Hermes gateway daemon only ticks the scheduler every 60 seconds (standard cron resolution). It is architecturally incapable of handling sub-minute real-time scheduling.

**How to avoid:**
Do not use Hermes' native Cron scheduler for the 30-second real-time timeout. Instead, centralize the timeout state machine on the FastAPI Backend-API:
1. When a capture is initiated, save the item with status `pending_confirmation` and an `expires_at` timestamp.
2. Run a non-blocking background task on the FastAPI server (using FastAPI's `BackgroundTasks` or an `asyncio` task) that transitions the item to `auto_saved` after 30 seconds of inactivity.
3. If the user edits or confirms the item, cancel or ignore the background task.
4. If the user does not respond, the server automatically saves the item and can optionally send a webhook back to Hermes to notify the user.

**Warning signs:**
- Auto-saves triggering in less than 5 seconds or taking over a minute.
- Inconsistent timing logs in Hermes.
- User complaints of premature saves or lost drafts.

**Phase to address:**
Phase 3 (Hermes-Plugin / 30s-Timeout) and Phase 1 (Backend-API).

---

### Pitfall 2: Google Calendar Dual-Write Race Condition

**What goes wrong:**
The agent and the user edit the same calendar event simultaneously or in close succession. The agent's automated update overwrites the user's manual changes, causing silent data loss and destroying user trust.

**Why it happens:**
The tool layer treats `update_event` as an unconditional write, dropping ETags/version tokens returned by the Google Calendar API during reads, and failing to pass `If-Match` headers in PATCH/DELETE requests.

**How to avoid:**
Implement a three-layer optimistic concurrency control pattern:
1. **Read-with-version:** The read tool returns the event along with its ETag (e.g., `{event: {...}, version: "abcd1234"}`).
2. **Write-with-precondition:** The write tool accepts the ETag and forwards it as an `If-Match` header. If no token is provided, the tool fails loudly.
3. **Conflict-as-outcome:** If Google Calendar returns `412 Precondition Failed`, the tool returns a structured conflict result to the agent instead of retrying, allowing the agent to re-plan or ask the user.

**Warning signs:**
- Calendar events reverting to old times.
- User edits disappearing.
- Database and calendar states drifting.

**Phase to address:**
Phase 1 (Backend-API) and Phase 2 (MCP-Server).

---

### Pitfall 3: First-User Signup Lockout with Better Auth

**What goes wrong:**
Setting `disableSignUp: true` statically in Better Auth's configuration blocks *all* registrations, preventing the solo operator (the owner) from signing up. Leaving it `false` leaves the registration open to the public, creating a security risk where unauthorized users can register.

**Why it happens:**
Statically configuring the `disableSignUp` option without a dynamic check of the database state.

**How to avoid:**
Use Better Auth's `databaseHooks` to dynamically check the user count:
```typescript
export const auth = betterAuth({
  databaseHooks: {
    user: {
      create: {
        before: async (user, ctx) => {
          const userCount = await ctx.adapter.count('user');
          if (userCount > 0) {
            // Abort the operation by returning false
            return false;
          }
        }
      }
    }
  }
});
```
This allows the first user to register and automatically locks all subsequent signups.

**Warning signs:**
- Admin unable to register on first deploy.
- Unauthorized users registering on the platform.
- Registration endpoints returning 500 instead of a clean "Signups disabled" error.

**Phase to address:**
Phase 1 (Backend-API / Better Auth integration).

---

### Pitfall 4: MCP Bearer Token Exposure over Remote HTTP

**What goes wrong:**
The static Bearer token used to authenticate Hermes' remote connection to the FastMCP server is leaked or intercepted, allowing unauthorized access to the MCP tools (which can read, write, and delete user data).

**Why it happens:**
Sending the token over unencrypted HTTP (no SSL/TLS), hardcoding the token in configuration files committed to Git, or printing the `Authorization` header in verbose FastAPI/FastMCP logs.

**How to avoid:**
1. Enforce HTTPS/TLS on Coolify for the MCP subdomain (`mcp.puzzlessbox.<domain>`).
2. Load the token via environment variables in Hermes instead of hardcoding it in config files.
3. Configure FastAPI logging middleware to redact the `Authorization` header.
4. Configure Traefik on Coolify to restrict access to the MCP endpoint to the specific IP address of the Hermes VPS (IP-allowlisting).

**Warning signs:**
- Bearer token visible in plain text in GitHub repositories.
- Unencrypted HTTP requests in network logs.
- Unauthorized tool executions in application logs.

**Phase to address:**
Phase 2 (MCP-Server) and Phase 5 (Coolify-Deployment & Härtung).

---

### Pitfall 5: Multi-Tenant owner_id Leakage

**What goes wrong:**
Data leaks between tenants (e.g., one user sees or modifies another user's captured items or calendar events) when the application transitions from single-user to multi-tenant.

**Why it happens:**
Developers forget to include `WHERE owner_id = :owner_id` in SQL queries, particularly in complex joins, subqueries, search indexes, or MCP tool queries.

**How to avoid:**
1. Enforce `owner_id` filtering at the database/ORM layer using global query filters or middleware.
2. In FastAPI, use a dependency to extract the `owner_id` from the authenticated session/token and pass it to all repository methods.
3. Write integration tests that explicitly attempt to access data using a different `owner_id` and assert that empty or 404 results are returned.

**Warning signs:**
- Captured items belonging to one user appearing on another user's board.
- Updates to items succeeding without verifying the requester's ownership.

**Phase to address:**
Phase 1 (Backend-API / Datenmodell).

---

## Technical Debt Patterns

Shortcuts that seem reasonable but create long-term problems.

| Shortcut | Immediate Benefit | Long-term Cost | When Acceptable |
|----------|-------------------|----------------|-----------------|
| Hardcoding `owner_id = 1` in SQL queries | Faster development in v1. | Massive refactoring required for SaaS transition. | Never (Multi-tenancy is a day-1 requirement). |
| In-memory timer for 30s auto-save in Hermes plugin | Simple plugin implementation. | Timers lost on restart, leading to orphaned confirmation windows. | Only during Phase 3 spike/prototype, never in production. |
| Storing Google OAuth tokens in unencrypted DB columns | Simple DB schema and queries. | Security vulnerability; compromised DB exposes calendar access. | Never. |

## Integration Gotchas

Common mistakes when connecting to external services.

| Integration | Common Mistake | Correct Approach |
|-------------|----------------|------------------|
| Google Calendar API | Ignoring rate limits and quota errors during sync. | Implement exponential backoff and handle `403 User Rate Limit Exceeded` gracefully. |
| Hermes Agent | Blocking Hermes' main thread with synchronous network calls or sleeps. | Use asynchronous HTTP calls (`httpx.AsyncClient`) and non-blocking background tasks. |
| Coolify Webhooks | Hardcoding webhook URLs in CI/CD scripts. | Store webhook URLs as GitHub Secrets and inject them dynamically. |

## Performance Traps

Patterns that work at small scale but fail as usage grows.

| Trap | Symptoms | Prevention | When It Breaks |
|------|----------|------------|----------------|
| N+1 queries when fetching items with their categories | Slow board loading times as the number of items grows. | Use eager loading (e.g., `joinedload` in SQLAlchemy) to fetch items and categories in a single query. | At ~500 items. |
| Full-table scans on `owner_id` or `category_id` | Database CPU spikes and slow query performance. | Add composite indexes on `(owner_id, category_id)` and `(owner_id, status)`. | At ~10,000 items. |

## Security Mistakes

Domain-specific security issues beyond general web security.

| Mistake | Risk | Prevention |
|---------|------|------------|
| Exposing the FastAPI `/docs` (Swagger) endpoint publicly without authentication | Attackers can discover API schemas and exploit vulnerabilities. | Disable `/docs` in production or protect it behind basic auth. |
| Storing raw static Bearer tokens in the database | Database leak compromises all MCP server access. | Store cryptographic hashes of the Bearer tokens (like bcrypt or SHA-256) and verify them dynamically. |

## UX Pitfalls

Common user experience mistakes in this domain.

| Pitfall | User Impact | Better Approach |
|---------|-------------|-----------------|
| Premature auto-save while the user is still typing/recording | Frustration as unfinished drafts are saved and the confirmation window closes. | Reset the 30-second timer on every user interaction (keystroke, voice input, edit command). |
| Lack of feedback during slow voice transcriptions | User thinks the system is hung and sends the message again, causing duplicate captures. | Send an immediate "Processing..." or "Transcribing..." message to the user. |

## "Looks Done But Isn't" Checklist

Things that appear complete but are missing critical pieces.

- [ ] **Google Calendar Sync:** Often missing token refresh logic — verify that the system automatically refreshes the Google OAuth access token using the refresh token before it expires.
- [ ] **30s Auto-Save:** Often missing timer reset on edit — verify that the 30-second timer is reset if the user sends an update or edit command within the window.
- [ ] **Multi-Tenant owner_id:** Often missing in subqueries — verify that all subqueries and joins explicitly filter by `owner_id`.
- [ ] **Coolify Deployment:** Often missing health check endpoints — verify that `/health` endpoints are configured and active in Coolify.

## Recovery Strategies

When pitfalls occur despite prevention, how to recover.

| Pitfall | Recovery Cost | Recovery Steps |
|---------|---------------|----------------|
| Leaked Bearer Token | LOW | Rotate the token in Coolify secrets, update the Hermes client configuration, and restart the services. |
| Database Corruption / Data Loss | HIGH | Restore the database from the latest local Coolify backup, verify data integrity, and re-sync calendar events from Google Calendar. |
| Stale/Orphaned Confirmation Windows | MEDIUM | Run a database migration/script to transition all `pending_confirmation` items older than 5 minutes to `auto_saved` status. |

## Pitfall-to-Phase Mapping

How roadmap phases should address these pitfalls.

| Pitfall | Prevention Phase | Verification |
|---------|------------------|--------------|
| Hermes Cron 30s Timeout Incompatibility | Phase 3 (Hermes-Plugin) & Phase 1 (Backend) | Verify that the 30s timeout is handled on the FastAPI server and is accurate to within 1 second. |
| Google Calendar Dual-Write Race | Phase 1 (Backend-API) & Phase 2 (MCP-Server) | Verify that write tools accept ETags and fail with `412 Precondition Failed` if the event has been modified. |
| First-User Signup Lockout | Phase 1 (Backend-API) | Verify that after the first user registers, all subsequent signup attempts return a 400 or 403 error. |
| MCP Bearer Token Exposure | Phase 2 (MCP-Server) & Phase 5 (Coolify) | Verify that MCP traffic is strictly HTTPS and Traefik restricts access to the Hermes VPS IP. |
| Multi-Tenant owner_id Leakage | Phase 1 (Backend-API) | Verify that all database queries and repository methods filter by `owner_id` using automated integration tests. |

## Sources

- [Nous Research Hermes Agent Documentation](https://hermes-agent.nousresearch.com/docs/user-guide/features/cron)
- [The Dual-Writer Race: When Your Agent and Your User Edit the Same Calendar Event](https://tianpan.co/blog/2026-04-26-dual-writer-race-agents-shared-state-concurrency)
- [Better Auth Hooks and Database Concepts](https://better-auth.com/docs/concepts/database)
- [FastMCP Authentication and Token Verification](https://fastmcp.wiki/en/servers/auth/token-verification)

---
*Pitfalls research for: Puzzlessbox*
*Researched: 2026-07-28*
