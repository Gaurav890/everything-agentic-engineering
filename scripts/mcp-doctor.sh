#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

echo "== MCP doctor =="

python3 -m json.tool .mcp.json >/dev/null
echo "✓ .mcp.json is valid JSON"

if [ -z "${PERPLEXITY_API_KEY:-}" ]; then
  echo "⚠ PERPLEXITY_API_KEY is not exported in this shell"
else
  echo "✓ PERPLEXITY_API_KEY is present (value hidden)"
fi

if [ -z "${FIRECRAWL_API_KEY:-}" ]; then
  echo "⚠ FIRECRAWL_API_KEY is not exported in this shell"
else
  echo "✓ FIRECRAWL_API_KEY is present (value hidden)"
fi

if command -v claude >/dev/null 2>&1; then
  echo
  echo "Claude MCP status:"
  claude mcp list || true
else
  echo "⚠ claude CLI not found; cannot inspect server status"
fi

cat <<'EOF'

Expected core servers:
  - perplexity
  - firecrawl
  - playwright

Inside Claude Code, use /mcp to review status and project approvals.

Security notes:
  - Do not print API keys.
  - Keep Playwright isolated unless persistence is intentional.
  - Never commit browser storage state or auth profiles.
EOF
