#!/usr/bin/env bash
set -euo pipefail

BRANCH="${1:-$(git branch --show-current 2>/dev/null || true)}"

if [ -z "$BRANCH" ]; then
  echo "Could not determine branch name." >&2
  exit 1
fi

case "$BRANCH" in
  main|master|dependabot/*|renovate/*|release/v*)
    echo "Branch accepted: $BRANCH"
    exit 0
    ;;
esac

PATTERN='^(feat|fix|docs|refactor|test|chore|spike|security|hotfix|agent)/T-[0-9]{3,}-[a-z0-9]+(-[a-z0-9]+)*$'

if [[ "$BRANCH" =~ $PATTERN ]]; then
  echo "Branch accepted: $BRANCH"
else
  cat >&2 <<EOF2
Invalid branch name: $BRANCH

Expected:
  <type>/<TASK-ID>-<short-kebab-case-description>

Examples:
  feat/T-014-password-reset
  fix/T-028-token-expiry
  agent/T-014-password-reset

Allowed types:
  feat fix docs refactor test chore spike security hotfix agent
EOF2
  exit 1
fi
