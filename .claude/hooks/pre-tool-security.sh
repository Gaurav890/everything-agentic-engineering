#!/usr/bin/env bash
set -euo pipefail

# Claude Code PreToolUse hook.
# Reads JSON on stdin and denies obviously destructive Bash commands.
# This is a guardrail, not a security boundary.

PAYLOAD="$(cat)"
python3 - "$PAYLOAD" <<'PY'
import json, re, sys

try:
    data = json.loads(sys.argv[1])
except Exception:
    sys.exit(0)

if data.get("tool_name") != "Bash":
    sys.exit(0)

command = str(data.get("tool_input", {}).get("command", ""))

patterns = [
    (r'(^|[;&|]\s*)rm\s+-rf\s+/(?:\s|$|\*)', "Refusing recursive deletion from filesystem root."),
    (r'\bgit\s+push\b.*\s--force(?:-with-lease)?\b', "Force-push requires explicit human approval."),
    (r'\bgit\s+reset\s+--hard\b', "Hard reset requires explicit human approval."),
    (r'\b(?:npm|pnpm|yarn)\s+publish\b', "Package publishing requires explicit human approval."),
    (r'\b(?:vercel|netlify|fly|railway)\b.*\b(?:deploy|--prod|production)\b', "Production deployment requires explicit human approval."),
    (r'\b(?:terraform|tofu)\s+destroy\b', "Infrastructure destruction requires explicit human approval."),
    (r'\bkubectl\s+delete\b', "Kubernetes deletion requires explicit human approval."),
    (r'\bDROP\s+(?:DATABASE|SCHEMA|TABLE)\b', "Destructive database operation requires explicit human approval."),
]

for pattern, reason in patterns:
    if re.search(pattern, command, flags=re.I):
        print(json.dumps({
            "hookSpecificOutput": {
                "hookEventName": "PreToolUse",
                "permissionDecision": "deny",
                "permissionDecisionReason": reason
            }
        }))
        sys.exit(0)

sys.exit(0)
PY
