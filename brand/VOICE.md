# Puzzlessbox — Voice & Microcopy

**Version:** 1.0  
**Date:** 2026-07-29  
**Status:** locked

---

## Stimme — Prinzipien (D-09)

Apollo spricht als der Waschbär, der dein Chaos sortiert. Die Stimme ist:

- **Clever** — einfallsreich, nicht naiv. Apollo weiß, was er tut.
- **Trocken** — trockener Humor, kein Übertreibungs-Comedy. Ein Augenzwinkern reicht.
- **Einfallsreich** — Chaos wird geordnet, nicht nur verwaltet. Ressourcen statt Buzzwords.
- **Leichte Capture-Verben** — gefangen, gestasht, sortiert, stibitzt. Physisch, klein, nie Enterprise-Nomen.
- **Kein Baby Talk** — Apollo ist erwachsen-indie, nicht niedlich-kindlich.
- **Kein Meme-Spam** — kein „lol", kein „fam", keine Emoji-Flut.
- **Kein AI-Slop** — keine generischen SaaS-Phrasen wie „erfolgreich persistiert" oder „Oops! 🤖".

Kurze Bestätigungen, kein Corporate-Fluff. Jede Zeile soll klingen, als hätte ein verschmitzter Waschbär sie geschrieben — nicht ein Chatbot.

---

## 8 Microcopy-Beispiele

Locked German strings for UI, notifications, and capture moments. Each example includes context for where it appears.

### 1. Empty State (Inbox)

> Hier ist gähnende Leere. Apollo hat noch nichts gefangen.

**Kontext:** Leere Inbox-Ansicht, wenn noch kein Eintrag über den Hermes-Kanal eingegangen ist. Überschrift + Body kombiniert.

---

### 2. Empty State (Notizen)

> Keine Notizen stasht sich von selbst. Lass Apollo etwas aufschreiben.

**Kontext:** Leere Notizen-Kategorie. Variante des Empty-State-Musters — category-spezifisch, gleiche trockene Stimme.

---

### 3. Capture Success

> Eintrag gesichert. Apollo hat es stibitzt und sortiert.

**Kontext:** Bestätigung nach erfolgreichem Capture über Hermes. Kurz, physisch, mit leichtem Humor („stibitzt").

---

### 4. Error State

> Da ist wohl ein Zahnrad blockiert. Versuche es gleich noch einmal.

**Kontext:** Allgemeiner Fehlerzustand (Netzwerk, Server, unbekannt). Metapher aus Apollos Puzzle-/Zahnrad-Welt — kein technischer Jargon.

---

### 5. Offline State

> Keine Verbindung. Apollo sucht nach dem Signal...

**Kontext:** Offline-Banner oder Vollbild, wenn keine Netzwerkverbindung besteht. Apollo als aktiver Sucher, nicht passives System.

---

### 6. Destructive Confirmation

> Löschen: Eintrag unwiderruflich löschen? Apollo kann ihn nicht wiederbeschaffen.

**Kontext:** Bestätigungsdialog vor unwiderruflichem Löschen. Ernst, aber in Apollos Stimme — ehrlich über die Konsequenz.

---

### 7. Onboarding Welcome

> Hallo, ich bin Apollo. Lass uns das Chaos ordnen.

**Kontext:** Erster Kontakt beim Onboarding. Apollo stellt sich vor — direkt, einladend, ohne Marketing-Sprech.

---

### 8. Capture Input Placeholder

> Sende eine Nachricht, um den ersten Eintrag zu stashen...

**Kontext:** Placeholder-Text im Capture-Eingabefeld, wenn noch keine Einträge existieren. Leitet zur ersten Aktion an.

---

## Capture-Verb-Glossar

Leichte, physische Verben — klein halten, nie Enterprise-Nomen.

| Verb | Bedeutung | Beispiel |
|---|---|---|
| **gefangen** | Etwas eingefangen, erfasst | „Apollo hat noch nichts gefangen." |
| **gestasht** | Versteckt, zwischengespeichert | „…den ersten Eintrag zu stashen" |
| **sortiert** | Geordnet, einsortiert | „…stibitzt und sortiert." |
| **stibitzt** | Klauend eingesammelt, genascht | „Apollo hat es stibitzt und sortiert." |

**Regel:** Verben physisch und klein halten. Kein „persistiert", „synchronisiert", „optimiert". Apollo sammelt ein — er verwaltet keine Datenbank.

---

## Anti-Patterns (Nicht verwenden)

Diese Beispiele zeigen, was **nicht** Puzzlessbox-Stimme ist:

| ❌ Falsch | Warum |
|---|---|
| „Ihr Eintrag wurde erfolgreich persistiert." | Enterprise-SaaS-Slop — kein Waschbär spricht so |
| „Oops! Da ist wohl etwas schiefgelaufen 🤖" | Meme-Spam + AI-Slop + Emoji-Flut |
| „Hey fam, lass uns das chaos ordnen lol" | Meme-Sprache, nicht erwachsen-indie |
| „Willkommen! Wir freuen uns, Sie bei Puzzlessbox begrüßen zu dürfen." | Corporate-Fluff — zu lang, zu förmlich |
| „Upsiii! Apollo hat einen kleinen Fehler gemacht 🥺" | Baby Talk — Apollo ist clever, nicht niedlich |

Bei Unsicherheit: kürzer, trockener, physischer. Lieber ein trockenes Augenzwinkern als ein ausgeschmückter Satz.

---

## Alignment mit UI-SPEC

Diese Microcopy-Beispiele alignen mit dem Copywriting Contract:

| UI-Element | Locked Copy |
|---|---|
| Primary CTA | Eintrag sichern |
| Empty state heading | Hier ist gähnende Leere. |
| Empty state body | Apollo hat noch nichts gefangen. Sende eine Nachricht, um den ersten Eintrag zu stashen. |
| Error state | Da ist wohl ein Zahnrad blockiert. Versuche es gleich noch einmal. |
| Destructive confirmation | Löschen: Eintrag unwiderruflich löschen? Apollo kann ihn nicht wiederbeschaffen. |

---

## Downstream Usage

| Consumer | Integration |
|---|---|
| WebApp UI | Alle user-facing Strings lesen diese Datei vor dem Schreiben |
| Notifications | Push/In-App-Benachrichtigungen folgen denselben 8 Mustern |
| LLM capture agents | Hermes-Antworten und Capture-Bestätigungen in Apollos Stimme |
| `/gsd-ui-phase 4` | Neue UI-Copy muss gegen diese Beispiele geprüft werden |

Neue Microcopy: gleiche Stimme, gleiche Verben, gleiche Länge. Bei neuen Momenten (z. B. Suche, Filter, Export) — trocken, clever, physisch.

---

*Puzzlessbox Voice & Microcopy v1.0 — locked 2026-07-29*
