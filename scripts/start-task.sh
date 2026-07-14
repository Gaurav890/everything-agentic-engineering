#!/usr/bin/env bash
set -euo pipefail

TASK_ID="${1:-}"
if [ -z "$TASK_ID" ]; then
  echo "Usage: $0 T-001" >&2
  exit 1
fi

python3 - "$TASK_ID" <<'PY'
import json, sys
from pathlib import Path

task_id = sys.argv[1]
path = Path("docs/40-execution/TASKS.jsonl")
tasks = []
found = False

for line in path.read_text().splitlines():
    if not line.strip():
        continue
    task = json.loads(line)
    if task.get("id") == task_id:
        if task.get("status") not in {"backlog", "ready", "blocked"}:
            print(f"Task {task_id} current status: {task.get('status')}")
        task["status"] = "in_progress"
        found = True
    tasks.append(task)

if not found:
    raise SystemExit(f"Task not found: {task_id}")

path.write_text("\n".join(json.dumps(t, sort_keys=False) for t in tasks) + "\n")
print(f"Started {task_id}")
PY
