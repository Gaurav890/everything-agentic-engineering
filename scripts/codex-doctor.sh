#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
STRICT_RUNTIME=false

if [ "${1:-}" = "--strict-runtime" ]; then
  STRICT_RUNTIME=true
elif [ -n "${1:-}" ]; then
  echo "Usage: $0 [--strict-runtime]" >&2
  exit 2
fi

cd "$ROOT"

failures=0
warnings=0

pass() {
  printf 'PASS  %s\n' "$1"
}

warn() {
  printf 'WARN  %s\n' "$1"
  warnings=$((warnings + 1))
}

fail() {
  printf 'FAIL  %s\n' "$1" >&2
  failures=$((failures + 1))
}

required_files=(
  AGENTS.md
  .codex/config.toml
  .codex/hooks.json
  .codex-plugin/plugin.json
  plugin.json
  .claude/skills/codex-adapter/SKILL.md
)

for path in "${required_files[@]}"; do
  if [ -f "$path" ]; then
    pass "$path exists"
  else
    fail "$path is missing"
  fi
done

if ./scripts/agent-plugin-doctor.sh >/dev/null; then
  pass "Agent Plugins 1.0 portable core is valid"
else
  fail "Agent Plugins 1.0 portable core is invalid"
fi

for path in .agents/skills skills; do
  if [ -L "$path" ] && [ -d "$path" ]; then
    pass "$path resolves to the shared skill catalog"
  else
    fail "$path must be a valid symbolic link to .claude/skills"
  fi
done

python3 - <<'PY' || failures=$((failures + 1))
import json
import re
from pathlib import Path

root = Path.cwd()

config_text = (root / ".codex/config.toml").read_text()
forbidden = {
    "approval_policy",
    "default_permissions",
    "model",
    "model_provider",
    "model_providers",
    "mcp_servers",
    "openai_base_url",
    "permissions",
    "sandbox_mode",
    "sandbox_workspace_write",
}
present = sorted(
    key
    for key in forbidden
    if re.search(rf"(?m)^\s*(?:\[{re.escape(key)}(?:\.|\])|{re.escape(key)}\s*=)", config_text)
)
if present:
    raise SystemExit(
        "FAIL  public project config contains authority-sensitive keys: "
        + ", ".join(present)
    )

instruction_budget = re.search(
    r"(?m)^project_doc_max_bytes\s*=\s*(\d+)\s*$", config_text
)
if not instruction_budget or int(instruction_budget.group(1)) < 32768:
    raise SystemExit("FAIL  project_doc_max_bytes is below the Codex default")

agents_section = re.search(
    r"(?ms)^\[agents\]\s*$\n(.*?)(?=^\[|\Z)", config_text
)
if not agents_section or not re.search(
    r"(?m)^max_concurrent_threads_per_session\s*=\s*4\s*$",
    agents_section.group(1),
):
    raise SystemExit("FAIL  bounded Codex concurrency must remain 4")

features_section = re.search(
    r"(?ms)^\[features\]\s*$\n(.*?)(?=^\[|\Z)", config_text
)
if not features_section or not re.search(
    r"(?m)^hooks\s*=\s*true\s*$", features_section.group(1)
):
    raise SystemExit("FAIL  Codex hook discovery is not enabled")

hooks = json.loads((root / ".codex/hooks.json").read_text())
events = hooks.get("hooks", {})
if not events.get("PreToolUse") or not events.get("PostToolUse"):
    raise SystemExit("FAIL  required Codex hook events are missing")
serialized_hooks = json.dumps(hooks)
for script in ("pre-tool-security.sh", "post-edit-secret-scan.sh"):
    if script not in serialized_hooks:
        raise SystemExit(f"FAIL  Codex hooks do not invoke {script}")

plugin = json.loads((root / ".codex-plugin/plugin.json").read_text())
if plugin.get("name") != "everything-agentic-engineering":
    raise SystemExit("FAIL  plugin name drift")
if plugin.get("skills") != "./skills/":
    raise SystemExit("FAIL  plugin must use the shared root skills catalog")
if not re.fullmatch(r"\d+\.\d+\.\d+", str(plugin.get("version", ""))):
    raise SystemExit("FAIL  plugin version is not strict semver")
if any(key in plugin for key in ("hooks", "mcpServers", "apps")):
    raise SystemExit("FAIL  plugin declares an unreviewed external capability")

canonical = sorted((root / ".claude/skills").glob("*/SKILL.md"))
codex = sorted((root / ".agents/skills").glob("*/SKILL.md"))
packaged = sorted((root / "skills").glob("*/SKILL.md"))
canonical_names = [path.parent.name for path in canonical]
if canonical_names != [path.parent.name for path in codex]:
    raise SystemExit("FAIL  Codex repository skill catalog drift")
if canonical_names != [path.parent.name for path in packaged]:
    raise SystemExit("FAIL  plugin skill catalog drift")

print(f"PASS  validated {len(canonical_names)} shared skills")
print("PASS  Codex configuration does not grant additional authority")
print("PASS  Codex hook and plugin contracts are valid")
PY

if python3 scripts/validate_codex_agents.py; then
  :
else
  failures=$((failures + 1))
fi

if [ -x .claude/hooks/pre-tool-security.sh ] && \
   [ -x .claude/hooks/post-edit-secret-scan.sh ]; then
  pass "shared safety hooks are executable"
else
  fail "shared safety hooks must be executable"
fi

runtime_args=(--runtime codex --json)
if [ "$STRICT_RUNTIME" = true ]; then
  runtime_args+=(--strict)
fi
if runtime_report="$(./scripts/runtime-doctor.sh "${runtime_args[@]}")"; then
  runtime_command_passed=true
else
  runtime_command_passed=false
fi
runtime_status="$(printf '%s' "$runtime_report" | python3 -c 'import json, sys; print(json.load(sys.stdin)["runtimes"][0]["status"])')"
runtime_message="$(printf '%s' "$runtime_report" | python3 -c 'import json, sys; print(json.load(sys.stdin)["runtimes"][0]["message"])')"
case "$runtime_status" in
  pass)
    pass "$runtime_message"
    ;;
  warn)
    warn "$runtime_message"
    ;;
  fail)
    fail "$runtime_message"
    ;;
  *)
    fail "shared Codex runtime policy returned unknown status: $runtime_status"
    ;;
esac
if [ "$runtime_command_passed" = false ] && [ "$runtime_status" != fail ]; then
  fail "shared Codex runtime policy command failed unexpectedly"
fi

if [ "$failures" -gt 0 ]; then
  printf '\nCodex adapter failed with %s error(s) and %s warning(s).\n' "$failures" "$warnings" >&2
  exit 1
fi

printf '\nCodex adapter valid with %s warning(s).\n' "$warnings"
