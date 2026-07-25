#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SOURCE_SHA="$(git -C "$ROOT" rev-parse HEAD)"
TEMP_ROOT="$(mktemp -d "${TMPDIR:-/tmp}/eae-release-smoke.XXXXXX")"
CHECKOUT="$TEMP_ROOT/everything-agentic-engineering"

cleanup() {
  rm -rf "$TEMP_ROOT"
}
trap cleanup EXIT

echo "== Clean-checkout onboarding smoke test =="
git clone --quiet --no-local "$ROOT" "$CHECKOUT"
git -C "$CHECKOUT" checkout --quiet "$SOURCE_SHA"
cd "$CHECKOUT"

test ! -e .env || {
  echo "A clean checkout unexpectedly contains .env." >&2
  exit 1
}

./scripts/bootstrap.sh
test -f .env || {
  echo "Bootstrap did not create .env from the example." >&2
  exit 1
}

./scripts/init-project.sh --list-presets >/dev/null
./scripts/init-project.sh \
  --name release-smoke \
  --preset web-supabase \
  --dry-run >/dev/null
./scripts/profile-resolve.sh >/dev/null
./scripts/profile-doctor.sh >/dev/null
./scripts/release-check.sh

git diff --exit-code -- . ':!.env' >/dev/null || {
  echo "Onboarding changed tracked files in a clean checkout." >&2
  exit 1
}

echo "Clean-checkout onboarding smoke test passed."
