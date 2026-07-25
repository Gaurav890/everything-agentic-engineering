#!/usr/bin/env bash
set -euo pipefail

MODE="${1:-quick}"
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

echo "== Verification: $MODE =="

echo "[1/6] Validate JSON"
python3 -m json.tool .mcp.json >/dev/null
python3 -m json.tool .claude/settings.json >/dev/null
for f in packages/design-tokens/tokens/*/*.json; do
  python3 -m json.tool "$f" >/dev/null
done
python3 - <<'PY'
import json
import re
from pathlib import Path

token_paths = set()
aliases = []

def walk(node, path=()):
    if isinstance(node, dict):
        if "$value" in node:
            token_paths.add(".".join(path))
            value = node["$value"]
            if isinstance(value, str):
                match = re.fullmatch(r"\{([^}]+)\}", value)
                if match:
                    aliases.append((".".join(path), match.group(1)))
        for key, value in node.items():
            if not key.startswith("$"):
                walk(value, path + (key,))
    elif isinstance(node, list):
        for value in node:
            walk(value, path)

for path in Path("packages/design-tokens/tokens").glob("*/*.json"):
    walk(json.loads(path.read_text()))

missing = [(source, target) for source, target in aliases if target not in token_paths]
if missing:
    raise SystemExit(f"Missing design-token aliases: {missing}")
print(f"Validated {len(token_paths)} design tokens and {len(aliases)} aliases")
PY

echo "[2/6] Validate JSONL"
python3 - <<'PY'
import json
from pathlib import Path
path = Path("docs/40-execution/TASKS.jsonl")
for i, line in enumerate(path.read_text().splitlines(), 1):
    if line.strip():
        json.loads(line)
print("TASKS.jsonl valid")
PY

echo "[3/6] Validate GitHub YAML"
python3 - <<'PY'
from pathlib import Path
try:
    import yaml
except ImportError:
    print("PyYAML not installed; skipping YAML parse validation")
else:
    files = list(Path(".github/workflows").glob("*.yml")) + list(Path(".github/ISSUE_TEMPLATE").glob("*.yml"))
    for path in files:
        with path.open() as f:
            yaml.safe_load(f)
    print(f"Validated {len(files)} GitHub YAML files")
PY

echo "[4/6] Validate shell scripts"
for f in .claude/hooks/*.sh scripts/*.sh; do
  bash -n "$f"
done

echo "[5/6] Validate collaboration policy scripts"
./scripts/check-branch-name.sh feat/T-014-password-reset >/dev/null
./scripts/check-branch-name.sh agent/T-014-password-reset >/dev/null
./scripts/check-pr-title.sh 'feat(T-014): add password reset confirmation' >/dev/null

for required in \
  CONTRIBUTING.md \
  docs/70-collaboration/GITHUB_WORKFLOW.md \
  docs/70-collaboration/REPOSITORY_SETUP.md \
  docs/70-collaboration/CODE_REVIEW.md \
  docs/70-collaboration/TEAM_COLLABORATION.md \
  .github/PULL_REQUEST_TEMPLATE.md \
  .github/CODEOWNERS; do
  test -f "$required" || { echo "Missing required file: $required" >&2; exit 1; }
done

for skill in .claude/skills/*/SKILL.md; do
  python3 - "$skill" <<'PY'
from pathlib import Path
import re
import sys

path = Path(sys.argv[1])
text = path.read_text()
match = re.match(r"^---\n(.*?)\n---\n", text, re.S)
if not match:
    raise SystemExit(f"Invalid skill frontmatter: {path}")
frontmatter = match.group(1)
for field in ("name", "description"):
    if not re.search(rf"^{field}:\s*.+$", frontmatter, re.M):
        raise SystemExit(f"Missing {field} in {path}")
PY
done

echo "[6/6] Run project-defined checks when available"

if [ -f package.json ]; then
  if command -v pnpm >/dev/null 2>&1; then
    for script in lint typecheck test; do
      if node -e "const p=require('./package.json'); process.exit(p.scripts&&p.scripts['$script']?0:1)"; then
        pnpm "$script"
      fi
    done
  else
    echo "pnpm not found; skipping package scripts"
  fi
fi

if [ "$MODE" = "full" ]; then
  echo "Full mode: add profile-specific E2E, visual, accessibility, and security commands as the implementation grows."
fi

echo "Verification complete."
