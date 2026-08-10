#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

DRY_RUN=false
case "${1:-}" in
  "") ;;
  --dry-run) DRY_RUN=true ;;
  *)
    echo "Usage: $0 [--dry-run]" >&2
    exit 2
    ;;
esac

run_install() {
  if [ "$DRY_RUN" = true ]; then
    printf 'Would run:'
    printf ' %q' "$@"
    printf '\n'
  else
    "$@"
  fi
}

profile_active() {
  python3 - "$1" <<'PY'
import json
import sys
from pathlib import Path

root = Path.cwd()
target = sys.argv[1]
selected = json.loads((root / ".agentic/project.json").read_text())["profiles"]
profiles = {
    path.stem: json.loads(path.read_text())
    for path in (root / ".agentic/profiles").glob("*.json")
}
resolved = set()

def visit(profile_id):
    if profile_id in resolved:
        return
    for dependency in profiles[profile_id].get("requires", []):
        visit(dependency)
    resolved.add(profile_id)

for profile_id in selected:
    visit(profile_id)
raise SystemExit(0 if target in resolved else 1)
PY
}

echo "Installing reviewed external skills for the active project profiles..."
echo "Targets: Claude Code and Codex (global user scope)"
echo

vercel_skills=()
if profile_active web-next; then
  vercel_skills+=(--skill react-best-practices --skill web-design-guidelines)
fi
if profile_active mobile-expo; then
  vercel_skills+=(--skill react-native-guidelines)
fi

if [ "${#vercel_skills[@]}" -gt 0 ]; then
  run_install npx skills@latest add vercel-labs/agent-skills \
    "${vercel_skills[@]}" \
    --global \
    --agent claude-code \
    --agent codex \
    --yes
fi

if profile_active design-critical; then
  run_install npx skills@latest add \
    https://github.com/emilkowalski/skills/tree/78761e1b57f97dce65b983d640c70a68f39e8163 \
    --skill '*' \
    --global \
    --agent claude-code \
    --agent codex \
    --yes
fi

if [ "$DRY_RUN" = true ]; then
  echo
  echo "Dry run complete. No external skills were installed."
fi

cat <<'EOF'

Selected external skill plan completed for active profiles.

The Emil Kowalski collection is installed only when `design-critical` is active.
Installation makes capabilities available; `product-design-router` and
`design-engineering-quality` still invoke only the smallest relevant skill.

Anthropic frontend-design is supplementary and is not installed by default.
Install it separately only when you explicitly want another direction perspective:

  npx skills@latest add anthropics/skills --skill frontend-design \
    --global --agent claude-code --agent codex --yes

Optional workflow plugin in Claude Code:
  /plugin install superpowers@claude-plugins-official

Optional Expo plugin when mobile/Expo is active:
  /plugin install expo@claude-plugins-official

Review third-party skills before enabling their hooks or shell behavior.
EOF
