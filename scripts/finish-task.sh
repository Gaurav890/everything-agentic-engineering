#!/usr/bin/env bash
set -euo pipefail

TASK_ID="${1:-}"
if [ -z "$TASK_ID" ]; then
  echo "Usage: $0 T-001" >&2
  exit 1
fi

./scripts/verify.sh full

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
        task["status"] = "review"
        found = True
    tasks.append(task)

if not found:
    raise SystemExit(f"Task not found: {task_id}")

path.write_text("\n".join(json.dumps(t, sort_keys=False) for t in tasks) + "\n")
print(f"Marked {task_id} ready for review after full verification.")
print("Next: commit the review-state change, complete review, then run prepare-merge.sh before the final merge cycle.")
PY
