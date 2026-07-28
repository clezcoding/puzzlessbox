# Feature Research

**Domain:** Personal Capture Inbox / Second-Brain / Voice-to-Structured-Note
**Researched:** July 28, 2026
**Confidence:** MEDIUM

## Feature Landscape

### Table Stakes (Users Expect These)

Features users assume exist. Missing these = product feels incomplete.

| Feature | Why Expected | Complexity | Notes |
|---------|--------------|------------|-------|
| **High-Accuracy Voice Transcription** | Spoken notes must be converted to text with high fidelity and multilingual support. | LOW | Leverages Hermes' built-in voice mode (Whisper/Groq/OpenAI), avoiding custom pipeline overhead. |
| **Automated Structured Formatting** | Raw transcripts are messy. AI must format them into clean markdown, summarize, and extract action items. | MEDIUM | Uses FastAPI backend with structured JSON output from LLM (instructor/Pydantic) to parse text. |
| **Multi-Channel Ingestion** | Capture must happen where the user is (Telegram, WhatsApp, Discord, Slack, Signal, Email, Web, Voice). | LOW | Leverages Hermes' existing multi-channel gateway; Puzzlessbox only needs to expose an MCP endpoint. |
| **Categorization & Board UI** | Visual interface to organize captured items into default categories (Inbox, Notes, Links, Tasks, Calendar). | MEDIUM | Implemented in Next.js 16 using a drag-and-drop board (`@hello-pangea/dnd` or `@dnd-kit`). |
| **Secure WebApp Authentication** | Standard secure login/signup for the solo operator. | LOW | Uses Better Auth with PostgreSQL adapter, email/password credentials provider. |

### Differentiators (Competitive Advantage)

Features that set the product apart. Not required, but valuable.

| Feature | Value Proposition | Complexity | Notes |
|---------|-------------------|------------|-------|
| **Capture Confirmation UX & Auto-save** | Interactive confirmation flow where Hermes presents a draft (Title, Type, Category, Summary) and waits for user feedback. If no response within 30s, it auto-saves. | HIGH | Requires a stateful plugin on the Hermes side, cron/hooks for the 30s timer, and custom MCP tools. |
| **Link Bookmarking with Rich Previews** | Automatically scraping links sent via chat to extract metadata (title, preview image, description) and auto-categorizing them. | MEDIUM | FastAPI backend uses a scraper (e.g., BeautifulSoup/Playwright) to extract Open Graph tags and stores them in JSONB. |
| **Google Calendar Sync** | Deep integration to read and write events directly into Google Calendar via OAuth in Settings. | HIGH | Uses a separate Google OAuth flow (not Better Auth Social) to obtain refresh tokens, stored securely in Postgres. |
| **Better Auth First-User Lock** | Dynamic signup closure after the first user registers to secure private single-user deployment while remaining SaaS-ready. | MEDIUM | Implements a Better Auth `before` hook to block `/sign-up/email` dynamically if any user exists in the database. |
| **MCP Tool Surface** | Exposing a FastMCP server with tools (`create_item`, `list_categories`, `move_item`, `confirm_item`, `update_item`) for programmatic interaction. | MEDIUM | Exposes FastAPI backend actions as MCP tools using FastMCP 3.4.4, secured with Bearer Token. |

### Anti-Features (Commonly Requested, Often Problematic)

Features that seem good but create problems.

| Feature | Why Requested | Why Problematic | Alternative |
|---------|---------------|-----------------|-------------|
| **Multi-User / Team UI in v1** | Collaboration and sharing notes with others. | Massive scope creep, complex UI, and security isolation overhead for a solo-operator tool. | Tenant-ready data model (`owner_id` on every table) from day 1, but UI is strictly single-user. |
| **Custom STT/TTS Pipeline** | Complete control over transcription and voice synthesis. | High infrastructure costs, maintenance overhead, and latency. | Reuse Hermes' built-in voice capabilities. |
| **Google Tasks API in v1** | Synchronizing tasks with Google Tasks. | Adds OAuth scope complexity and API maintenance for a secondary feature. | Keep tasks local to the categories board. |
| **OAuth 2.1 for MCP in v1** | Industry-standard security for remote MCP clients. | Overengineered for a single-client (Hermes) use case. | Static Bearer Token auth with proxy-level IP allowlisting. |

## Feature Dependencies

```
[Capture Confirmation UX]
    └──requires──> [MCP Tool Surface]
                       └──requires──> [Automated Structured Formatting]

[Google Calendar Sync] ──enhances──> [Automated Structured Formatting]

[Drag-and-Drop Board] ──requires──> [Categorization & Board UI]

[Link Bookmarking] ──enhances──> [Automated Structured Formatting]
```

### Dependency Notes

- **Capture Confirmation UX requires MCP Tool Surface:** Hermes needs tools to create, confirm, and update items during the interactive confirmation flow.
- **MCP Tool Surface requires Automated Structured Formatting:** The MCP tools rely on the backend API to parse and structure raw text before creating items.
- **Google Calendar Sync enhances Automated Structured Formatting:** Extracted calendar events can be pushed directly to Google Calendar once the OAuth connection is established.
- **Link Bookmarking enhances Automated Structured Formatting:** When a URL is detected in the captured text, the system triggers the metadata scraping pipeline.

## MVP Definition

### Launch With (v1)

Minimum viable product — what's needed to validate the concept.

- [ ] **Capture Confirmation UX & Auto-save (30s)** — The core frictionless capture loop.
- [ ] **Categorization Board** — Visual board with default categories (Inbox, Notes, Links, Tasks, Calendar).
- [ ] **Better Auth First-User Lock** — Secure single-user deployment.
- [ ] **MCP Tool Surface** — FastMCP server for Hermes integration.
- [ ] **Link Bookmarking with Previews** — Automatic link metadata extraction.

### Add After Validation (v1.x)

Features to add once core is working.

- [ ] **Google Calendar Sync** — Connect Google Calendar in Settings to read/write events.
- [ ] **Custom Categories** — Allow users to create, edit, and delete custom categories and colors.

### Future Consideration (v2+)

Features to defer until product-market fit is established.

- [ ] **Multi-User SaaS UI** — Tenant isolation, billing, and team collaboration.
- [ ] **"Ask AI" Knowledge Retrieval** — Semantic search and chat with historical notes.

## Feature Prioritization Matrix

| Feature | User Value | Implementation Cost | Priority |
|---------|------------|---------------------|----------|
| **Capture Confirmation UX & Auto-save** | HIGH | HIGH | P1 |
| **Categorization Board** | HIGH | MEDIUM | P1 |
| **Better Auth First-User Lock** | HIGH | LOW | P1 |
| **MCP Tool Surface** | HIGH | MEDIUM | P1 |
| **Link Bookmarking with Previews** | MEDIUM | MEDIUM | P1 |
| **Google Calendar Sync** | HIGH | HIGH | P2 |
| **Custom Categories** | MEDIUM | LOW | P2 |
| **"Ask AI" Knowledge Retrieval** | HIGH | HIGH | P3 |

**Priority key:**
- P1: Must have for launch
- P2: Should have, add when possible
- P3: Nice to have, future consideration

## Competitor Feature Analysis

| Feature | PLAUD.ai | Voicenotes.com | Our Approach |
|---------|----------|----------------|--------------|
| **Capture Confirmation** | No confirmation; direct save. | Direct save; manual edit later. | **Interactive confirmation** with 30s auto-save timeout via Hermes chat. |
| **Ingestion Channels** | Dedicated hardware device / app. | Web app / mobile app. | **Multi-channel messaging** (Telegram, WhatsApp, etc.) via Hermes. |
| **Authentication** | Standard SaaS login. | Standard SaaS login. | **Better Auth with First-User Lock** (self-host secure, SaaS-ready). |
| **Extensibility** | Closed ecosystem. | Closed ecosystem. | **Open MCP Tool Surface** for agentic extensibility. |

## Sources

- [PLAUD.ai Feature Documentation (2026)](https://www.plaud.ai/blogs/articles/best-ai-voice-recorder-and-note-taker)
- [SpeakNotes Blog (2026)](https://speaknotes.io/blog/voice-to-notes-app-android)
- [Voicenotes.com Review](https://nerdymomocat.github.io/posts/voicenotes-hitting-half-of-the-right-notes/)
- [Better Auth Configuration Reference](https://github.com/better-auth/better-auth/blob/main/packages/core/src/types/init-options.ts)
- [Voice UI Design Best Practices (2026)](https://thefinch.design/voice-user-interface-design-best-practices-2026/)

---
*Feature research for: Personal Capture / Second Brain*
*Researched: July 28, 2026*