# Phase 3: Hermes-Plugin & Timeout-Spike - Context

**Gathered:** 2026-08-01
**Status:** Ready for planning

<domain>
## Phase Boundary

Hermes orchestrates the capture confirmation flow across all Hermes-supported messaging channels and drives MCP tools only (`create_item` → optional `update_item` → `confirm_item` / `discard_item`). The 30s autosave remains owned by the API `DraftTimeoutManager` (MCP-04 VALIDATED — Hermes cron is not the timer). Phase 3 ships `hermes-plugin/` (monorepo), German CAP-02 confirmation UX, post-autosave chat notify via poll, single-active-draft concurrency, and a new MCP `discard_item` soft-delete tool. No WebApp UI (Phase 4). No Coolify/CI for remaining apps (Phase 5).

</domain>

<decisions>
## Implementation Decisions

### Edit flow (CAP-02)
- **D-01:** After the confirmation card, the next free-text / natural-language message is treated as an edit — no separate „Bearbeiten“ hop. Explicit confirm remains „Eintrag sichern“ / confirm affordance. — **Reversibility:** costly — Hermes plugin dialog state machine
- **D-02:** Hermes LLM maps edit text to draft fields and calls `update_item` with only changed keys. — **Reversibility:** costly — coupling to LLM field extraction
- **D-03:** After a successful edit: silent ACK only — do **not** re-send a full Stash-Check card. Timer reset still happens via API PATCH from `update_item` (Phase 1 D-06). — **Reversibility:** reversible

### Discard / soft-delete
- **D-04:** Phase 3 adds MCP tool `discard_item(item_id)` that soft-deletes via API (`deleted_at`). German copy „Verworfen“ (Apollo voice). Expands tool surface beyond Phase-2 MCP-01 list. — **Reversibility:** costly — new MCP tool + API path + Hermes action mapping; Spike 004 had deferred delete

### Post-autosave notify
- **D-05:** Always send a chat ping after status becomes `auto_saved` (e.g. gestasht / lands on board — Apollo voice per `brand/VOICE.md`). — **Reversibility:** reversible
- **D-06:** Detect `auto_saved` by polling item status ~30–35s after create — **no** API→Hermes webhook and **not** using 60s Hermes cron as the deadline driver. — **Reversibility:** costly — poll loop in plugin; webhook later would be a different design

### Parallel captures
- **D-07:** At most one active pending draft per chat/session. A new capture while a draft is open asks the user: confirm old / discard old / wait. — **Reversibility:** costly — concurrency policy in plugin
- **D-08:** If user confirms after status is already `auto_saved`: idempotent success or friendly ACK („war schon gestasht“) — never punish late confirm. Planner must verify/extend API `confirm` on `auto_saved`. — **Reversibility:** costly — API confirm semantics

### Type / category suggestion
- **D-09:** On first `create_item`, Hermes LLM chooses `type` + `category` after `list_categories`, with heuristic hints (URL→link, datetime→event/Termin). — **Reversibility:** costly — capture quality depends on this path
- **D-10:** When category confidence is low: fall back to **Inbox** and show Inbox honestly on the card — do not block on a pre-create clarification question. — **Reversibility:** reversible

### Plugin packaging & config
- **D-11:** Ship plugin as top-level `hermes-plugin/` in the monorepo. Deploy to Hermes VPS via git pull or rsync + Hermes reload — no npm/pip publish, no Coolify app for the plugin. — **Reversibility:** reversible
- **D-12:** First-run interactive setup script collects MCP URL + bearer and writes them to Hermes env/secrets (`MCP_URL`, `MCP_BEARER`). Never commit secrets; never hardcode in plugin source. — **Reversibility:** reversible

### Carried forward (spikes / prior phases — do not re-litigate)
- API owns 30s `DraftTimeoutManager`; Hermes cron must not drive the deadline (MCP-04 VALIDATED)
- Hermes → MCP HTTPS Bearer only; no direct DB from Hermes VPS (MCP-03)
- Confirmation formatter: German plain-text CAP-02 template from spike 004 / `format_confirmation` — port into `hermes-plugin/`; channel-specific buttons only in adapter layer
- Primary CTA: „Eintrag sichern“ (`brand/VOICE.md`); tool schemas stay English (Phase 2 D-14)
- Phase 2 tool/client contracts D-09…D-19 remain unless this phase’s `discard_item` / confirm-on-`auto_saved` explicitly extends them

### Claude's Discretion
- Exact German microcopy strings for silent edit ACK, autosave ping, discard, and dual-draft prompt (must follow `brand/VOICE.md`)
- Poll implementation details (sleep vs Hermes timer helper; one-shot vs short retry)
- Exact API route/shape for soft-delete if not already exposed; MCP error `code` mapping for discard
- Setup-script UX (prompts, validation, where Hermes stores env)
- Whether confirm buttons map per-channel inside Hermes adapters vs text-only v1

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Requirements & roadmap
- `.planning/REQUIREMENTS.md` — CAP-02, CAP-04, MCP-03, MCP-04 (phase scope)
- `.planning/ROADMAP.md` — Phase 3 goal + success criteria
- `.planning/PROJECT.md` — Hermes external VPS, remote MCP, all channels, monorepo `hermes-plugin/`
- `PUZZLESSBOX_PROJECT_BRIEF.md` — capture flow + Hermes plugin intent

### Spike findings (mandatory)
- `.claude/skills/spike-findings-puzzlessbox/SKILL.md` — Phase 3 spike index
- `.claude/skills/spike-findings-puzzlessbox/references/draft-timeout.md` — API timer VALIDATED; Hermes cron INVALIDATED as timer
- `.claude/skills/spike-findings-puzzlessbox/references/mcp-remote-integration.md` — MCP-only orchestration; remote HTTPS+bearer
- `.claude/skills/spike-findings-puzzlessbox/references/capture-confirmation-ux.md` — CAP-02 template + action mapping
- `.planning/spikes/WRAP-UP-SUMMARY.md` — verdict table; open live E2E note
- `.planning/spikes/MANIFEST.md` — spike requirements

### Prior phase contracts
- `.planning/phases/02-mcp-server/02-CONTEXT.md` — D-01…D-23 auth, tools, deploy
- `.planning/phases/01-datenmodell-backend-api/01-CONTEXT.md` — D-05…D-08 draft timer; soft-delete `deleted_at`; status lifecycle
- `mcp-server/app/tools/items.py` — existing `create_item` / `confirm_item` / `update_item`
- `api/app/routers/capture.py` — drafts create/patch/confirm + timer
- `brand/VOICE.md` — German microcopy + capture verbs

### Resume / constraints
- `.planning/.continue-here.md` — blocking: no Hermes-cron-as-timer; no direct DB from Hermes

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- MCP tools in `mcp-server/app/tools/items.py` — extend with `discard_item`; reuse confirm/update patterns + schema tests
- Spike confirmation formatter — port from spike findings / `sources/004-confirmation-payload` into `hermes-plugin/`
- API draft lifecycle + `DraftTimeoutManager` — plugin must not duplicate timer; poll/read status only
- Soft-delete column `deleted_at` (Phase 1) — wire API endpoint if missing, then MCP tool

### Established Patterns
- Hermes → public MCP Bearer; MCP → internal API service bearer + `X-Owner-Id` (Phase 2)
- Tool errors: short text + `code` + `details` (Phase 2 D-13)
- German user-facing copy only in plugin layer; English tool schemas

### Integration Points
- New greenfield `hermes-plugin/` consumed on external Hermes v0.19.0 VPS
- MCP prod `https://mcp.puzzlesstool.online/mcp`
- Optional live E2E confirm on VPS still open from spike 002 PARTIAL

</code_context>

<specifics>
## Specific Ideas

- User accepted setup-script UX with the clarification that the script **writes** `MCP_URL` / `MCP_BEARER` into Hermes env/secrets (not git, not source hardcode)
- User overrode spike „no delete in v1“ — soft-delete ships in Phase 3 as first-class confirm-flow action
- User preferred silent edit ACK over re-sending the Stash-Check card (less chat noise; board shows final state in Phase 4)
- Autosave notify is mandatory chat ping, not optional silence

</specifics>

<deferred>
## Deferred Ideas

- API→Hermes webhook for autosave notify (rejected for v1 — poll instead)
- Parallel multi-draft queue in one chat (rejected — single active draft)
- Publishing hermes-plugin as npm/pip package or Coolify app (rejected — monorepo + rsync/pull)
- Live Hermes VPS E2E confirm still recommended as validation during execute (spike 002 PARTIAL) — not a separate product feature
- WebApp board surfacing of discarded/auto_saved items — Phase 4

None further — discussion stayed within phase scope aside from intentional `discard_item` tool-surface pull.

</deferred>

---

*Phase: 3-Hermes-Plugin & Timeout-Spike*
*Context gathered: 2026-08-01*
