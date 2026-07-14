#!/usr/bin/env bash
set -euo pipefail

TASK_ID="${1:-}"
if [ -z "$TASK_ID" ]; then
  echo "Usage: $0 T-014" >&2
  exit 1
fi

BRANCH="$(git branch --show-current)"

if [ "$BRANCH" = "main" ] || [ "$BRANCH" = "master" ]; then
  echo "Refusing PR readiness check on protected integration branch: $BRANCH" >&2
  exit 1
fi

./scripts/check-branch-name.sh "$BRANCH"
./scripts/verify.sh full

python3 - "$TASK_ID" <<'PY'
import json, sys
from pathlib import Path

task_id = sys.argv[1]
path = Path("docs/40-execution/TASKS.jsonl")
found = None
for line in path.read_text().splitlines():
    if not line.strip():
        continue
    task = json.loads(line)
    if task.get("id") == task_id:
        found = task
        break

if found is None:
    raise SystemExit(f"Task not found: {task_id}")

if found.get("status") not in {"in_progress", "review"}:
    raise SystemExit(
        f"Task {task_id} must be in_progress or review before final PR readiness; "
        f"current status: {found.get('status')}"
    )

print(f"Task found: {task_id} ({found.get('status')})")
print("Requirements:", ", ".join(found.get("requirement_ids", [])) or "none")
print("Acceptance criteria:", ", ".join(found.get("acceptance_ids", [])) or "none")
PY

echo
cat <<EOF2
PR readiness checks passed for $TASK_ID on $BRANCH.

Before requesting final review, confirm the PR includes:
  - linked issue and task ID
  - requirements / acceptance criteria
  - verification evidence
  - UI evidence when applicable
  - security/data/auth/migration impact
  - durable context updates
EOF2
