---
status: local-complete
phase: 04-webapp
source: [04-VERIFICATION.md]
started: 2026-08-02T18:18:00Z
updated: 2026-08-02T18:32:00Z
environment: local (OrbStack docker-compose :5433 + webapp pnpm dev @ localhost:3000)
tester: gsd-browser (session puzzless-uat-4)
uat_login: uat@puzzless.local (see webapp/.env.local UAT_EMAIL / UAT_PASSWORD)
account_reset: true
---

## Current Test

[testing complete — local suite]

## Tests

### 1. Browser-Refresh Session-Persistenz
expected: Nach F5 bleibt Board sichtbar; kein Redirect zu /login
result: pass
tested_by: gsd-browser
notes: |
  Nach Login auf /board → navigate reload /board → URL bleibt /board, 5 Kategorien, offline=false.

### 2. Brand-Hero Login-Page visuell (D-24)
expected: Apollo-splash + Instrument Serif Wortmarke; Form auf surface card; Tabs Anmelden|Registrieren; Registrieren immer sichtbar (D-25)
result: pass
tested_by: gsd-browser
notes: |
  evaluate: hasApollo=true, hasWordmark=true, tabs=[Anmelden, Registrieren], cardSurface=true.

### 3. Board-Layout responsiv
expected: Desktop ~5 Spalten ohne H-Scroll; Mobile <768px Single-Column + Tabs; long-press Sheet öffnet Category-Picker
result: pass
tested_by: gsd-browser
notes: |
  Desktop (834×1194 iPad Pro 11, mq=false): 5 regions Inbox→Termine, hScroll=false, no tablist.
  Mobile (iPhone 15, 393×852): mq=true; 5 tabs; 1 visible region.
  Long-press: touchstart 650ms on board-card-325405ee… → Sheet data-testid=mobile-category-sheet, title "Kategorie wählen", cats Inbox/Notizen/Links/Tasks/Termine (gsd-browser eval CLI).

### 4. Item-Modal zentriert + dimmed + close-flush (D-09, D-15)
expected: Modal max-width 560px zentriert; Board dimmed; Close nur X+Escape; Overlay-Click schließt nicht; Autosave flushed vor Close
result: pass
tested_by: gsd-browser
notes: |
  Card "UAT flushed" → dialog "Eintrag bearbeiten", w=512 ≤560, centerX=960=vw/2.
  Overlay corner click → dialog bleibt offen.
  Title edit → Escape → closed; board zeigt "UAT flushed" (autosave flush).

### 5. Google Calendar OAuth Roundtrip
expected: Step 1 → Google Consent → Step 2 Kalender-Liste → Step 3 Done; Disconnect löscht Token, lokale Termine bleiben
result: blocked
blocked_by: third-party
reason: deferred to Coolify (needs real redirect URIs + GOOGLE_CLIENT_ID/SECRET)

### 6. DnD cross-category + in-column reorder visuell (D-16..D-23)
expected: Drag via Handle (Desktop); Body-Click öffnet Modal; Classic floating ghost; optimistic + revert toast
result: pass
tested_by: gsd-browser
notes: |
  Body-click title → dialog "Eintrag bearbeiten" (CLI click section[aria-label=Notizen] button.min-w-0.flex-1).
  Body-drag ohne Handle (coords 200,255→450,334) → flushed bleibt in Notizen.
  Handle drag flushed (78d7d153…) Notizen→Inbox → inboxFlushed=true + toast "Eintrag verschoben".
  In-column reorder: DnD Note B über Reorder A in Notizen → order ["UAT DnD Note B","UAT Reorder A"] + toast.
  Mock PATCH **/localhost:8000/items/* → 500 → drag flushed Inbox→Notizen revert; toast "Verschieben fehlgeschlagen. Eintrag ist zurück."; flushed bleibt Inbox.

### 7. Poll-Verhalten mit echtem Hermes-Capture (CAP-05)
expected: Poll alle ~10s; neuer Item via Hermes → Toast + terracotta pulse; Offline → Banner + Erneut versuchen
result: blocked
blocked_by: third-party
reason: deferred to Coolify / Hermes end-to-end

### 8. Theme toggle visuell
expected: System/Light/Dark wechselt live; persistiert; respects prefers-color-scheme bei System
result: pass
tested_by: gsd-browser
notes: |
  Header "Darstellung umschalten": dark→light live (html.dark false, pb.theme=light).
  Reload /board → theme light persisted.
  Settings zeigt System/Hell/Dunkel; Settings-Button-Klick per evaluate ohne Effekt (Header-Toggle + Persistenz verifiziert).

### 9. First-Login Welcome → Board (D-31)
expected: Erster Login → /welcome → Los geht's → /board; pb.welcome.seen=true; zweiter Login → /board; ?next= wins
result: pass
tested_by: gsd-browser
notes: |
  Fresh account (DB reset + register uat@puzzless.local).
  First login → /welcome → "Los geht's" → /board, pb.welcome.seen=true.
  Second login → /board (skip welcome).
  login?next=/settings → /settings after login.

## Summary

total: 9
passed: 7
issues: 0
pending: 0
skipped: 0
blocked: 2
blocked_tests: [5, 7]
blocked_reason: Coolify / real Google OAuth + Hermes capture

## Gaps

[none — fresh account, clean local run]

## Account Reset Log

- Deleted prior user fe86d6d8-… + owned notes/sessions/categories.
- Registered fresh uat@puzzless.local (user f57a7d32-958e-4f80-b1b5-5a748714ddce).
- Seeded UAT items via API /drafts for modal + DnD tests.
