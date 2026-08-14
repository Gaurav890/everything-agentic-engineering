#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

echo "== Agentic Product Starter bootstrap =="

for cmd in git node npx python3; do
  if ! command -v "$cmd" >/dev/null 2>&1; then
    echo "Missing required command: $cmd" >&2
    exit 1
  fi
done

chmod +x agentic .claude/hooks/*.sh scripts/*.sh

if [ ! -f .env ]; then
  cp .env.example .env
  echo "Created .env from .env.example. Add API keys before using research MCPs."
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

./scripts/codex-doctor.sh
./scripts/agent-plugin-doctor.sh

echo "Validating shell syntax..."
for f in .claude/hooks/*.sh scripts/*.sh; do
  bash -n "$f"
done

echo
echo "Bootstrap complete."
echo "Next:"
echo "  1. Add PERPLEXITY_API_KEY and FIRECRAWL_API_KEY to .env"
echo "  2. Export them into your shell"
echo "  3. Run ./agentic setup skills"
echo "  4. Review .agentic/project.json and run ./agentic profile doctor"
echo "  5. Run ./agentic doctor mcp"
echo "  6. If using Codex, review .codex/ and run ./agentic doctor codex"
echo "  7. Run ./agentic doctor plugin before testing portable plugin clients"
echo "  8. Open docs/ as an Obsidian vault"
echo "  9. Run ./agentic --help to discover all supported workflows"
