#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

if [ "$#" -gt 1 ] || { [ "$#" -eq 1 ] && [ "${1:-}" != "--json" ]; }; then
  echo "Usage: ./agentic doctor mcp [--json]" >&2
  exit 2
fi

python3 scripts/mcp_compatibility.py "$@"

if [ "${1:-}" = "--json" ]; then
  exit 0
fi

echo
echo "Local readiness (values hidden):"
for variable in PERPLEXITY_API_KEY FIRECRAWL_API_KEY; do
  if printenv "$variable" >/dev/null 2>&1; then
    printf '✓ %s is present\n' "$variable"
  else
    printf '⚠ %s is not exported in this shell\n' "$variable"
  fi
done

if command -v claude >/dev/null 2>&1; then
  echo "✓ claude CLI is available (not invoked)"
else
  echo "⚠ claude CLI is not available"
fi

cat <<'EOF'

Security notes:
  - Do not print API keys.
  - This doctor validates configuration only; it does not connect to servers.
  - Review and approve project servers inside the client before first use.
  - Keep Playwright isolated unless persistence is intentional.
  - Never commit browser storage state or auth profiles.
EOF
