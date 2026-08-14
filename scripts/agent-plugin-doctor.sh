#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

python3 scripts/validate_agent_plugin.py . "$@"

if [ "${1:-}" != "--json" ]; then
  if [ ! -f mcp.json ]; then
    echo "INFO  Portable MCP is intentionally not packaged; .mcp.json remains project-local."
  fi

  echo "PASS  Codex-native compatibility remains separately defined in .codex-plugin/plugin.json."
fi
