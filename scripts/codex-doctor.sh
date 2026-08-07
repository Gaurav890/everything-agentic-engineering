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
  .claude/skills/codex-adapter/SKILL.md
)

for path in "${required_files[@]}"; do
  if [ -f "$path" ]; then
    pass "$path exists"
  else
    fail "$path is missing"
  fi
done

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

if [ -x .claude/hooks/pre-tool-security.sh ] && \
   [ -x .claude/hooks/post-edit-secret-scan.sh ]; then
  pass "shared safety hooks are executable"
else
  fail "shared safety hooks must be executable"
fi

if command -v codex >/dev/null 2>&1; then
  version_output="$(codex --version 2>/dev/null || true)"
  version="$(printf '%s\n' "$version_output" | sed -nE 's/.* ([0-9]+\.[0-9]+\.[0-9]+).*/\1/p' | head -1)"
  if [ -z "$version" ]; then
    warn "Codex is installed but its version could not be parsed: $version_output"
  elif python3 - "$version" <<'PY'
import sys
actual = tuple(int(part) for part in sys.argv[1].split("."))
raise SystemExit(0 if actual >= (0, 147, 0) else 1)
PY
  then
    pass "Codex runtime $version meets the plugin baseline"
  elif [ "$STRICT_RUNTIME" = true ]; then
    fail "Codex runtime $version is below the 0.147.0 plugin baseline"
  else
    warn "Codex runtime $version is below 0.147.0; repository contracts still validate, but plugin workflows require an approved upgrade"
  fi
else
  if [ "$STRICT_RUNTIME" = true ]; then
    fail "Codex is not installed"
  else
    warn "Codex is not installed; runtime checks were skipped"
  fi
fi

if [ "$failures" -gt 0 ]; then
  printf '\nCodex adapter failed with %s error(s) and %s warning(s).\n' "$failures" "$warnings" >&2
  exit 1
fi

printf '\nCodex adapter valid with %s warning(s).\n' "$warnings"
