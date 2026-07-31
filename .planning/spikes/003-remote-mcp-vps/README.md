---
spike: 003
name: remote-mcp-vps
type: standard
validates: "Given Hermes VPS path, when HTTPS+bearer to mcp.puzzlesstool.online, then health OK and auth errors are 401"
verdict: VALIDATED
related: [002]
tags: [mcp, remote, auth, mcp-02]
---

# Spike 003: Remote MCP from External Client

## What This Validates

**Given** Hermes on a separate VPS,  
**When** it calls public `https://mcp.puzzlesstool.online`,  
**Then** `/health` is reachable without auth and `/mcp` rejects missing/invalid bearer with **401** (not 500).

## How to Run

```bash
# From repo root (uses httpx from api venv or pip install httpx)
python3 .planning/spikes/003-remote-mcp-vps/probe_remote_mcp.py

# Optional authenticated probe
MCP_BEARER='your-hermes-token' python3 .planning/spikes/003-remote-mcp-vps/probe_remote_mcp.py
```

## What to Expect

- `health_ok: true`, latency typically &lt;500ms from EU.
- `no_auth_is_401: true`, `bad_bearer_is_401: true`.
- `events.json` forensic log.

## Results

**Verdict: VALIDATED**

Live probe 2026-07-31: `/health` 200 ~180ms; unauthenticated and invalid bearer `POST /mcp` return 401 with `invalid_token` semantics (Phase 2 verification + broken window #1 fixed).

**Impact:** Hermes plugin can rely on 401 for auth failures; use `MCP_URL` + rotatable bearer in Coolify/Hermes env.
