#!/usr/bin/env bash
set -euo pipefail

TITLE="${1:-}"
TASKS_PATH="${TASKS_PATH:-docs/40-execution/TASKS.jsonl}"

if [ -z "$TITLE" ]; then
  echo "Usage: $0 '<type>(T-014): summary'" >&2
  exit 1
fi

PATTERN='\((T-[0-9]{3,})\)'
if [[ ! "$TITLE" =~ $PATTERN ]]; then
  echo "Could not extract a task ID from PR title: $TITLE" >&2
  exit 1
fi

TASK_ID="${BASH_REMATCH[1]}"

python3 - "$TASK_ID" "$TASKS_PATH" <<'PY'
import json
import sys
from pathlib import Path

task_id = sys.argv[1]
path = Path(sys.argv[2])

if not path.is_file():
    raise SystemExit(f"Task ledger not found: {path}")

task = None
for line_number, line in enumerate(path.read_text().splitlines(), 1):
    if not line.strip():
        continue
    try:
        candidate = json.loads(line)
    except json.JSONDecodeError as error:
        raise SystemExit(f"Invalid JSONL at {path}:{line_number}: {error}") from error
    if candidate.get("id") == task_id:
        task = candidate
        break

if task is None:
    raise SystemExit(
        f"PR references {task_id}, but that task does not exist in {path}."
    )

status = task.get("status")
if status != "done":
    raise SystemExit(
        f"PR references {task_id}, but its status is {status!r}, not 'done'.\n"
        f"Run finish-task.sh and prepare-merge.sh for {task_id}, commit the "
        "durable-state update, then request final review again."
    )

print(f"PR task state accepted: {task_id} is done")
PY
