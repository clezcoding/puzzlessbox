# API Coverage — Google Calendar

> Full coverage by default. Opt-outs are explicit, reasoned decisions.
> Phase 4 wires Calendar OAuth + select flow in the WebApp Settings wizard (CAL-01).
> Core Calendar token/event endpoints landed in Phase 1; this matrix covers the
> Google Calendar surface the WebApp exercises.

| capability | decision | reason |
|---|---|---|
| OAuth connect (`/auth/google/connect`) | INTEGRATE | |
| OAuth callback + token persist | INTEGRATE | |
| Connection status (`/auth/google/status`) | INTEGRATE | |
| Disconnect (`/auth/google/disconnect`) | INTEGRATE | |
| List calendars (`/calendars`) | INTEGRATE | |
| Select primary calendar (`/calendars/{id}/select`) | INTEGRATE | |
| Create/update calendar events (capture→Termine) | INTEGRATE | Phase 1 API; WebApp shows event items on board |
| FreeBusy query | OPT-OUT | not needed yet — no availability UI in v1 |
| Recurring event expansion | OPT-OUT | not needed yet — store/display single instances only |
| Calendar ACL / sharing management | OPT-OUT | explicitly out of scope — single-owner v1 |
| Push notifications / watch channels | OPT-OUT | not needed yet — board uses poll, not Google push |
| Secondary Google account linking | OPT-OUT | explicitly out of scope — one Google account per user |
