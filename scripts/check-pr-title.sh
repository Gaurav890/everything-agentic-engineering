#!/usr/bin/env bash
set -euo pipefail

TITLE="${1:-}"
if [ -z "$TITLE" ]; then
  echo "Usage: $0 'feat(T-014): add password reset'" >&2
  exit 1
fi

PATTERN='^(feat|fix|docs|refactor|test|chore|spike|security|hotfix|ci|perf)\(T-[0-9]{3,}\): .+'

if [[ "$TITLE" =~ $PATTERN ]]; then
  echo "PR title accepted: $TITLE"
else
  cat >&2 <<EOF2
Invalid PR title:
  $TITLE

Expected:
  <type>(<TASK-ID>): <imperative summary>

Examples:
  feat(T-014): add password reset confirmation
  fix(T-028): prevent expired refresh token reuse
  security(T-060): enforce request rate limiting
EOF2
  exit 1
fi
