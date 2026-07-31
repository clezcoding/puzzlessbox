# Spike Conventions

Patterns established for Puzzlessbox spike sessions.

## Stack

- **Scripts:** Python 3.14 + stdlib; `httpx` for HTTP probes; optional `mcp` client for live tool calls.
- **UI demos:** Single-file HTML in spike folder (no build step).
- **Forensic logs:** JSON event arrays with ISO timestamps, written to `events.json` per run.

## Structure

```
.planning/spikes/
  MANIFEST.md
  CONVENTIONS.md
  NNN-descriptive-name/
    README.md          # frontmatter + results
    *.py / *.html      # runnable artifacts
    events.json        # gitignored output (optional)
```

## Patterns

- **Timing spikes:** Simulate scheduler resolution; cite Phase 1 integration tests as ground truth for API behavior.
- **MCP spikes:** Default to mock/in-process; `--live` requires `MCP_URL` + `MCP_BEARER` env (never commit secrets).
- **UX spikes:** Static HTML preview the user can open locally; brand voice from `brand/VOICE.md`.

## Tools & Libraries

- `httpx` — remote probes (already in api/mcp-server)
- Live MCP: `https://mcp.puzzlesstool.online` (production)
- Avoid Docker/Hermes VPS install in spikes — document integration contract instead
