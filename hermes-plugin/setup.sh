#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ENV_FILE="${SCRIPT_DIR}/.env"
GITIGNORE_FILE="${SCRIPT_DIR}/.gitignore"
DEFAULT_MCP_URL="https://mcp.puzzlesstool.online/mcp"

if [[ -f "$ENV_FILE" ]]; then
  echo "Warnung: $ENV_FILE existiert bereits."
  read -r -p "Überschreiben? [y/N] " overwrite
  if [[ ! "$overwrite" =~ ^[Yy]$ ]]; then
    echo "Abgebrochen."
    exit 0
  fi
fi

read -r -p "MCP_URL [${DEFAULT_MCP_URL}]: " mcp_url
mcp_url="${mcp_url:-$DEFAULT_MCP_URL}"
if [[ "$mcp_url" != https://* ]]; then
  echo "Fehler: MCP_URL muss mit https:// beginnen." >&2
  exit 1
fi

read -rs -p "MCP_BEARER (min. 20 Zeichen, kein Echo): " mcp_bearer
echo
if [[ ${#mcp_bearer} -lt 20 ]]; then
  echo "Fehler: MCP_BEARER muss mindestens 20 Zeichen haben." >&2
  exit 1
fi

umask 077
printf 'MCP_URL=%s\nMCP_BEARER=%s\n' "$mcp_url" "$mcp_bearer" >"$ENV_FILE"
chmod 600 "$ENV_FILE"

if [[ ! -f "$GITIGNORE_FILE" ]] || ! grep -qxF '.env' "$GITIGNORE_FILE"; then
  echo '.env' >>"$GITIGNORE_FILE"
  echo "Hinweis: .env zu .gitignore hinzugefügt."
fi

if git -C "$SCRIPT_DIR" rev-parse --git-dir >/dev/null 2>&1; then
  if ! git -C "$SCRIPT_DIR" check-ignore -q "$ENV_FILE"; then
    echo "Warnung: .env wird von git nicht ignoriert — prüfe .gitignore." >&2
    exit 1
  fi
fi

echo "Konfiguration geschrieben nach hermes-plugin/.env. Bitte Hermes neu laden."
