#!/usr/bin/env bash
set -euo pipefail

MODE="${1:-quick}"
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"
export PYTHONPYCACHEPREFIX="$ROOT/.cache/python"

echo "== Verification: $MODE =="

if [ -f .agentic/generated-project.json ]; then
  echo "Generated downstream project detected."
  python3 scripts/verify_generated_project.py
  for f in .claude/hooks/*.sh scripts/*.sh; do
    bash -n "$f"
  done
  python3 -m compileall -q scripts
  ./agentic --help >/dev/null
  ./agentic profile resolve >/dev/null
  ./agentic agents doctor >/dev/null
  python3 scripts/mcp_compatibility.py --allow-disabled >/dev/null
  if [ -f package.json ] && [ -d node_modules ] && command -v pnpm >/dev/null 2>&1; then
    for script in lint typecheck test; do
      if node -e "const p=require('./package.json'); process.exit(p.scripts&&p.scripts['$script']?0:1)"; then
        pnpm "$script"
      fi
    done
  elif [ -f package.json ] && command -v pnpm >/dev/null 2>&1; then
    echo "Dependencies are not installed; package checks are available after pnpm install."
  fi
  echo "Generated project verification complete."
  exit 0
fi

echo "[1/10] Validate JSON"
python3 -m json.tool .mcp.json >/dev/null
python3 -m json.tool .claude/settings.json >/dev/null
python3 -m json.tool .codex/hooks.json >/dev/null
python3 -m json.tool .codex-plugin/plugin.json >/dev/null
python3 -m json.tool plugin.json >/dev/null
python3 -m json.tool .agentic/project.json >/dev/null
python3 -m json.tool .agentic/resources.json >/dev/null
python3 -m json.tool .agentic/external-skills.json >/dev/null
python3 -m json.tool .agentic/external-agents.json >/dev/null
python3 -m json.tool .agentic/runtime-baselines.json >/dev/null
python3 -m json.tool .agentic/mcp-compatibility.json >/dev/null
python3 -m json.tool .agentic/commands.json >/dev/null
python3 -m json.tool .agentic/generator.json >/dev/null
python3 -m json.tool .agentic/evolution/policy.json >/dev/null
python3 -m json.tool .agentic/evolution/incumbent.json >/dev/null
for f in .agentic/evolution/schemas/*.json; do
  python3 -m json.tool "$f" >/dev/null
done
for f in .agentic/capabilities/*.json; do
  python3 -m json.tool "$f" >/dev/null
done
for f in .agentic/profiles/*.json; do
  python3 -m json.tool "$f" >/dev/null
done
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

echo "[2/10] Validate JSONL"
python3 - <<'PY'
import json
from pathlib import Path
path = Path("docs/40-execution/TASKS.jsonl")
for i, line in enumerate(path.read_text().splitlines(), 1):
    if line.strip():
        json.loads(line)
print("TASKS.jsonl valid")
PY
./scripts/task-sync.sh validate-ledger
./scripts/task-closeout.sh --validate-handoff
python3 - <<'PY'
import json
from pathlib import Path
path = Path(".agentic/evolution/eval-sets/harness-regression.jsonl")
for i, line in enumerate(path.read_text().splitlines(), 1):
    if line.strip():
        json.loads(line)
print("Evolution eval JSONL valid")
PY

echo "[3/10] Validate GitHub YAML"
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

echo "[4/10] Validate shell and Python scripts"
for f in .claude/hooks/*.sh scripts/*.sh; do
  bash -n "$f"
done
python3 -m compileall -q scripts tests

echo "[5/10] Run profile and initializer tests"
python3 -m unittest discover -s tests -p 'test_profile_engine.py'
python3 -m unittest discover -s tests -p 'test_external_design_skills.py'
python3 -m unittest discover -s tests -p 'test_initializer.py'
python3 -m unittest discover -s tests -p 'test_task_engine.py'
python3 -m unittest discover -s tests -p 'test_agent_broker.py'
python3 -m unittest discover -s tests -p 'test_github_task_sync.py'
python3 -m unittest discover -s tests -p 'test_post_merge_closeout.py'
python3 -m unittest discover -s tests -p 'test_pr_finalization.py'
python3 -m unittest discover -s tests -p 'test_agentic_cli.py'
python3 -m unittest discover -s tests -p 'test_capability_engine.py'
python3 -m unittest discover -s tests -p 'test_project_generator.py'
python3 -m unittest discover -s tests -p 'test_evolution_engine.py'
./scripts/check-branch-name.sh feat/T-014-password-reset >/dev/null
./scripts/check-branch-name.sh agent/T-014-password-reset >/dev/null
./scripts/check-pr-title.sh 'feat(T-014): add password reset confirmation' >/dev/null
TASKS_PATH=tests/fixtures/pr-task-states.jsonl \
  ./scripts/check-pr-task-state.sh 'feat(T-900): completed fixture' >/dev/null
if TASKS_PATH=tests/fixtures/pr-task-states.jsonl \
  ./scripts/check-pr-task-state.sh 'feat(T-901): unfinished fixture' >/dev/null 2>&1; then
  echo "Unfinished PR task state unexpectedly passed" >&2
  exit 1
fi
if TASKS_PATH=tests/fixtures/pr-task-states.jsonl \
  ./scripts/check-pr-task-state.sh 'feat(T-999): unknown task' >/dev/null 2>&1; then
  echo "Unknown PR task state unexpectedly passed" >&2
  exit 1
fi
./scripts/profile-resolve.sh >/dev/null
./scripts/profile-doctor.sh >/dev/null
./scripts/profile-preview.sh web-next,design-critical,research-enabled >/dev/null
./agentic --help >/dev/null
./agentic commands --json | python3 -m json.tool >/dev/null
./agentic agents doctor >/dev/null
./agentic capabilities doctor >/dev/null
./agentic evolve validate >/dev/null

if ./scripts/profile-preview.sh backend-supabase,backend-convex >/dev/null 2>&1; then
  echo "Profile conflict check unexpectedly passed" >&2
  exit 1
fi

echo "[6/10] Build and test design tokens"
./scripts/build-design-tokens.sh
./scripts/build-design-tokens.sh --check
python3 -m unittest discover -s tests -p 'test_design_tokens.py'
python3 -m unittest discover -s tests -p 'test_design_engine.py'
./agentic design check

echo "[7/10] Test deterministic security hooks"
python3 -m unittest discover -s tests -p 'test_security_hooks.py'
python3 -m unittest discover -s tests -p 'test_codex_adapter.py'
python3 -m unittest discover -s tests -p 'test_agent_plugin.py'
python3 -m unittest discover -s tests -p 'test_mcp_compatibility.py'
python3 -m unittest discover -s tests -p 'test_runtime_compatibility.py'
./scripts/runtime-doctor.sh
./scripts/codex-doctor.sh
./scripts/agent-plugin-doctor.sh
./scripts/mcp-doctor.sh --json | python3 -m json.tool >/dev/null

echo "[8/10] Validate collaboration and community contracts"
for required in \
  LICENSE \
  SECURITY.md \
  CODE_OF_CONDUCT.md \
  CHANGELOG.md \
  CONTRIBUTING.md \
  docs/70-collaboration/GITHUB_WORKFLOW.md \
  docs/70-collaboration/REPOSITORY_SETUP.md \
  docs/70-collaboration/CODE_REVIEW.md \
  docs/70-collaboration/TEAM_COLLABORATION.md \
  .github/PULL_REQUEST_TEMPLATE.md \
  .github/CODEOWNERS; do
  test -f "$required" || { echo "Missing required file: $required" >&2; exit 1; }
done
./scripts/release-check.sh

echo "[9/10] Validate local documentation links and evidence bundles"
python3 - <<'PY'
import re
from pathlib import Path

root = Path.cwd()
missing = []
pattern = re.compile(r"\[[^\]]+\]\(([^)]+)\)")
for source in root.rglob("*.md"):
    if any(part in {".git", "node_modules"} for part in source.parts):
        continue
    for target in pattern.findall(source.read_text(errors="ignore")):
        target = target.strip().split("#", 1)[0]
        if not target or "://" in target or target.startswith(("mailto:", "#")):
            continue
        destination = (source.parent / target).resolve()
        if not destination.exists():
            missing.append(f"{source.relative_to(root)} -> {target}")
if missing:
    raise SystemExit("Broken local documentation links:\n" + "\n".join(missing))
print("Local documentation links valid")
PY

evidence_bundles=()
if [ -d docs/50-evals/evidence ]; then
  while IFS= read -r bundle; do
    evidence_bundles+=("$bundle")
  done < <(find docs/50-evals/evidence -mindepth 1 -maxdepth 1 -type d | sort)
fi
if [ "${#evidence_bundles[@]}" -gt 0 ]; then
  python3 scripts/validate_evidence.py "${evidence_bundles[@]}"
else
  echo "No committed evidence bundles yet"
fi

echo "[10/10] Run project-defined checks when available"
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
  echo "Full mode complete. Product profiles may add application-specific E2E, visual, accessibility, and security commands."
fi

echo "Verification complete."
