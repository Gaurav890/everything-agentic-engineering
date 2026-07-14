#!/usr/bin/env bash
set -euo pipefail

TASK_ID="${1:-}"
SLUG="${2:-}"
TYPE="${3:-agent}"
BASE="${4:-main}"

if [ -z "$TASK_ID" ] || [ -z "$SLUG" ]; then
  echo "Usage: $0 T-001 short-description [type] [base-branch]" >&2
  echo "Example: $0 T-014 password-reset agent main" >&2
  exit 1
fi

case "$TYPE" in
  feat|fix|docs|refactor|test|chore|spike|security|hotfix|agent) ;;
  *) echo "Unsupported type: $TYPE" >&2; exit 1 ;;
esac

if [[ ! "$TASK_ID" =~ ^T-[0-9]{3,}$ ]]; then
  echo "Invalid task ID: $TASK_ID" >&2
  exit 1
fi

if [[ ! "$SLUG" =~ ^[a-z0-9]+(-[a-z0-9]+)*$ ]]; then
  echo "Invalid slug: $SLUG (use lowercase kebab-case)" >&2
  exit 1
fi

BRANCH="$TYPE/$TASK_ID-$SLUG"
DIR=".claude/worktrees/${TASK_ID,,}-$SLUG"

mkdir -p .claude/worktrees

if git show-ref --verify --quiet "refs/heads/$BRANCH"; then
  echo "Branch already exists: $BRANCH" >&2
  exit 1
fi

if ! git show-ref --verify --quiet "refs/heads/$BASE"; then
  echo "Base branch does not exist locally: $BASE" >&2
  exit 1
fi

git worktree add -b "$BRANCH" "$DIR" "$BASE"

echo "Created worktree:"
echo "  branch: $BRANCH"
echo "  path:   $DIR"
echo "  base:   $BASE"
echo
echo "Assign exclusive file ownership before parallel writes."
