#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

echo "== Everything Agentic Engineering =="

for cmd in git node npx python3; do
  if ! command -v "$cmd" >/dev/null 2>&1; then
    echo "Missing required command: $cmd" >&2
    exit 1
  fi
done

chmod +x agentic .claude/hooks/*.sh scripts/*.sh

if [ ! -f .env ]; then
  cp .env.example .env
  echo "Created local .env from the profile-specific example."
fi

echo "Validating JSON..."
python3 -m json.tool .mcp.json >/dev/null
python3 -m json.tool .claude/settings.json >/dev/null
python3 -m json.tool .codex/hooks.json >/dev/null
python3 -m json.tool .codex-plugin/plugin.json >/dev/null
python3 -m json.tool plugin.json >/dev/null
python3 -m json.tool .agentic/project.json >/dev/null
python3 -m json.tool .agentic/resources.json >/dev/null
python3 -m json.tool .agentic/commands.json >/dev/null
for f in .agentic/profiles/*.json; do
  python3 -m json.tool "$f" >/dev/null
done

echo "Validating shell syntax..."
for f in .claude/hooks/*.sh scripts/*.sh; do
  bash -n "$f"
done

echo
echo "Bootstrap complete."
./agentic next
