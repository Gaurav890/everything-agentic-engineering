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

chmod +x .claude/hooks/*.sh scripts/*.sh

if [ ! -f .env ]; then
  cp .env.example .env
  echo "Created .env from .env.example. Add API keys before using research MCPs."
fi

echo "Validating JSON..."
python3 -m json.tool .mcp.json >/dev/null
python3 -m json.tool .claude/settings.json >/dev/null
python3 -m json.tool .codex/hooks.json >/dev/null
python3 -m json.tool .codex-plugin/plugin.json >/dev/null
python3 -m json.tool .agentic/project.json >/dev/null
python3 -m json.tool .agentic/resources.json >/dev/null
for f in .agentic/profiles/*.json; do
  python3 -m json.tool "$f" >/dev/null
done

./scripts/codex-doctor.sh

echo "Validating shell syntax..."
for f in .claude/hooks/*.sh scripts/*.sh; do
  bash -n "$f"
done

echo
echo "Bootstrap complete."
echo "Next:"
echo "  1. Add PERPLEXITY_API_KEY and FIRECRAWL_API_KEY to .env"
echo "  2. Export them into your shell"
echo "  3. Run ./scripts/install-skills.sh"
echo "  4. Review .agentic/project.json and run ./scripts/profile-doctor.sh"
echo "  5. Run ./scripts/mcp-doctor.sh"
echo "  6. If using Codex, review .codex/ and run ./scripts/codex-doctor.sh"
echo "  7. Open docs/ as an Obsidian vault"
