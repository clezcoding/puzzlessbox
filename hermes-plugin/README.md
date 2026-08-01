# Hermes Plugin — Puzzlessbox Capture

Hermes-Plugin für den Capture-Flow: Nachricht rein → Stash-Check → Bestätigung → Auto-Save.
Alle Daten laufen über Remote-MCP — kein direkter DB-Zugriff vom Hermes-VPS.

## Kanalneutralität (CAP-04)

Bestätigungs-Payload ist Plain-Text, identisch für Telegram, WhatsApp und Discord.
Kanalspezifische Buttons/Markdown liegen in Hermes-Adaptern, nicht in diesem Plugin.

## Deploy (D-11)

Plugin läuft auf separatem Hermes-VPS. Monorepo-Deploy per `git pull` oder `rsync`:

```bash
# Auf Hermes-VPS im Repo-Root
git pull origin main
# oder: rsync -av --exclude .venv hermes-plugin/ /path/to/hermes/plugins/puzzlessbox/

cd hermes-plugin
pip install -e .   # oder: uv sync && uv pip install -e .
bash setup.sh      # First-Run: MCP_URL + MCP_BEARER
# Hermes reload (Coolify restart oder hermes CLI reload)
```

## Erstkonfiguration (D-12)

`setup.sh` fragt interaktiv ab:

| Variable | Beschreibung |
|----------|--------------|
| `MCP_URL` | MCP-Endpoint (Default: `https://mcp.puzzlesstool.online/mcp`) |
| `MCP_BEARER` | Bearer-Token vom MCP-Service (Coolify Secret) |

- Bearer-Eingabe via `read -rs` (kein Echo)
- Schreibt `hermes-plugin/.env` mit `chmod 600`
- Prüft `.gitignore` und `git check-ignore .env`

**Niemals** `MCP_BEARER` committen oder im Quellcode hardcoden.

## Abhängigkeiten

- Python 3.12+
- `pip install -e .` (siehe `pyproject.toml`)
- MCP SDK (`mcp`), Pydantic Settings

## Sicherheit

- Plugin ruft **nur** MCP-Tools auf — keine DB-Credentials, keine DB-Libs
- Secrets nur via `setup.sh` → `.env` (git-ignored)
- MCP-Traffic über HTTPS mit Bearer-Auth

## Spike-Referenz (MCP-04)

Ergebnisse der Timeout- und Kanalneutralitäts-Spikes:
`.claude/skills/spike-findings-puzzlessbox/SKILL.md`

## Tests

```bash
cd hermes-plugin
pytest tests/ -x
```
