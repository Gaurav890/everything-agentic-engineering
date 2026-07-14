#!/usr/bin/env bash
set -euo pipefail

TYPE="${1:-}"
TASK_ID="${2:-}"
SLUG="${3:-}"
BASE="${4:-main}"

if [ -z "$TYPE" ] || [ -z "$TASK_ID" ] || [ -z "$SLUG" ]; then
  echo "Usage: $0 <type> <TASK-ID> <short-kebab-slug> [base-branch]" >&2
  echo "Example: $0 feat T-014 password-reset main" >&2
  exit 1
fi

case "$TYPE" in
  feat|fix|docs|refactor|test|chore|spike|security|hotfix|agent) ;;
  *) echo "Unsupported type: $TYPE" >&2; exit 1 ;;
esac

if [[ ! "$TASK_ID" =~ ^T-[0-9]{3,}$ ]]; then
  echo "Invalid task ID: $TASK_ID (expected T-014 or similar)" >&2
  exit 1
fi

if [[ ! "$SLUG" =~ ^[a-z0-9]+(-[a-z0-9]+)*$ ]]; then
  echo "Invalid slug: $SLUG (use lowercase kebab-case)" >&2
  exit 1
fi

if [ -n "$(git status --porcelain)" ]; then
  echo "Working tree is not clean. Commit, stash, or discard changes before creating a branch." >&2
  exit 1
fi

BRANCH="$TYPE/$TASK_ID-$SLUG"

if git show-ref --verify --quiet "refs/heads/$BRANCH"; then
  echo "Local branch already exists: $BRANCH" >&2
  exit 1
fi

if git remote get-url origin >/dev/null 2>&1; then
  git fetch origin "$BASE" --prune
fi

git switch "$BASE"

if git show-ref --verify --quiet "refs/remotes/origin/$BASE"; then
  git merge --ff-only "origin/$BASE"
fi

git switch -c "$BRANCH"
./scripts/start-task.sh "$TASK_ID"

echo
printf 'Created branch: %s\n' "$BRANCH"
printf 'Task started:   %s\n' "$TASK_ID"
