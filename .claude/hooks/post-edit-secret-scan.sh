#!/usr/bin/env bash
set -euo pipefail

# Claude Code PostToolUse hook.
# Scans the edited file for likely hard-coded secret patterns.
# It reports warnings but does not claim to be a complete secret scanner.

PAYLOAD="$(cat)"
python3 - "$PAYLOAD" <<'PY'
import json, re, sys
from pathlib import Path

try:
    data = json.loads(sys.argv[1])
except Exception:
    sys.exit(0)

tool_input = data.get("tool_input", {}) or {}
path_values = []

direct_path = (
    tool_input.get("file_path")
    or tool_input.get("path")
    or tool_input.get("filename")
)
if direct_path:
    path_values.append(str(direct_path))

# Codex reports apply_patch content in tool_input.command. Extract only the
# explicit file headers emitted by apply_patch; never interpret patch content
# as shell input.
if data.get("tool_name") == "apply_patch":
    command = str(tool_input.get("command", ""))
    path_values.extend(
        match.group(1).strip()
        for match in re.finditer(
            r"^\*\*\* (?:Add|Update) File: (.+)$",
            command,
            flags=re.MULTILINE,
        )
    )

if not path_values:
    sys.exit(0)

base = Path(str(data.get("cwd") or "."))
paths = []
for value in dict.fromkeys(path_values):
    path = Path(value)
    if not path.is_absolute():
        path = base / path
    if path.is_file() and path.stat().st_size <= 2_000_000:
        paths.append(path)

if not paths:
    sys.exit(0)

patterns = {
    "OpenAI-style key": r"\bsk-[A-Za-z0-9_-]{20,}\b",
    "AWS access key": r"\bAKIA[0-9A-Z]{16}\b",
    "GitHub token": r"\bgh[pousr]_[A-Za-z0-9_]{20,}\b",
    "Private key header": r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----",
    "Generic hard-coded secret": r"(?i)\b(?:api[_-]?key|secret|password|token)\s*[:=]\s*[\"'][^\"'\n]{12,}[\"']",
}

findings = []
for path in paths:
    try:
        text = path.read_text(errors="ignore")
    except Exception:
        continue
    hits = [name for name, pattern in patterns.items() if re.search(pattern, text)]
    if hits:
        findings.append(f"{path}: {', '.join(hits)}")

if findings:
    print(json.dumps({
        "systemMessage": (
            "Potential hard-coded secret pattern detected in "
            + "; ".join(findings)
            + ". Review immediately; do not commit real secrets."
        )
    }))

sys.exit(0)
PY
