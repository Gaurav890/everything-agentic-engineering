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
path_value = (
    tool_input.get("file_path")
    or tool_input.get("path")
    or tool_input.get("filename")
)

if not path_value:
    sys.exit(0)

path = Path(path_value)
if not path.is_file() or path.stat().st_size > 2_000_000:
    sys.exit(0)

try:
    text = path.read_text(errors="ignore")
except Exception:
    sys.exit(0)

patterns = {
    "OpenAI-style key": r"\bsk-[A-Za-z0-9_-]{20,}\b",
    "AWS access key": r"\bAKIA[0-9A-Z]{16}\b",
    "GitHub token": r"\bgh[pousr]_[A-Za-z0-9_]{20,}\b",
    "Private key header": r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----",
    "Generic hard-coded secret": r"(?i)\b(?:api[_-]?key|secret|password|token)\s*[:=]\s*[\"'][^\"'\n]{12,}[\"']",
}

hits = [name for name, pattern in patterns.items() if re.search(pattern, text)]

if hits:
    print(json.dumps({
        "systemMessage": (
            "Potential hard-coded secret pattern detected in "
            f"{path}: {', '.join(hits)}. Review immediately; do not commit real secrets."
        )
    }))

sys.exit(0)
PY
