#!/usr/bin/env bash
set -euo pipefail

TASK_ID="${1:-}"
if [ -z "$TASK_ID" ]; then
  echo "Usage: $0 T-014" >&2
  exit 1
fi

BRANCH="$(git branch --show-current)"
if [ "$BRANCH" = "main" ] || [ "$BRANCH" = "master" ]; then
  echo "Run prepare-merge on the task branch, not on $BRANCH." >&2
  exit 1
fi

./scripts/check-branch-name.sh "$BRANCH"
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
        prior = task.get("status")
        if prior != "review":
            raise SystemExit(
                f"Task {task_id} must be in review before prepare-merge; current status: {prior}"
            )
        task["status"] = "done"
        found = True
    tasks.append(task)

if not found:
    raise SystemExit(f"Task not found: {task_id}")

path.write_text("\n".join(json.dumps(t, sort_keys=False) for t in tasks) + "\n")
print(f"Prepared {task_id} for merge by writing status=done on this task branch.")
print("The repository source of truth does not consider the task done until this change is merged into main.")
print("Commit this bookkeeping change before the final merge.")
PY
