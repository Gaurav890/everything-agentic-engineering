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

./agentic setup bootstrap
test -f .env || {
  echo "Bootstrap did not create .env from the example." >&2
  exit 1
}

./agentic setup init --list-presets >/dev/null
./agentic setup init \
  --name release-smoke \
  --preset web-supabase \
  --dry-run >/dev/null
./agentic profile resolve >/dev/null
./agentic profile doctor >/dev/null

WEB_PROJECT="$TEMP_ROOT/smoke-web"
MOBILE_PROJECT="$TEMP_ROOT/smoke-mobile"
CORE_PROJECT="$TEMP_ROOT/smoke-core"
GUIDED_PROJECT="$TEMP_ROOT/smoke-guided"
ENTERPRISE_PROJECT="$TEMP_ROOT/smoke-enterprise"

printf '%s\n' \
  "Guided Signal" \
  "$GUIDED_PROJECT" \
  "2" \
  "" \
  "" \
  "" \
  "y" | ./agentic setup create >/dev/null
test -f "$GUIDED_PROJECT/.agentic/experience.json"
GUIDED_NEXT="$("$GUIDED_PROJECT/agentic" next)"
[[ "$GUIDED_NEXT" == *"pnpm install"* ]] || {
  echo "Guided web project did not expose the expected single next action." >&2
  exit 1
}

./agentic setup create \
  --name "Smoke Signal" \
  --destination "$WEB_PROJECT" \
  --preset web \
  --archetype agentic-product \
  --audience "operators supervising consequential automation" \
  --promise "Make every automated decision visible and reversible." \
  --visual-character bold \
  --yes >/dev/null
"$WEB_PROJECT/agentic" verify full >/dev/null
WEB_NEXT="$("$WEB_PROJECT/agentic" next)"
[[ "$WEB_NEXT" == *"pnpm install"* ]]
test "$(python3 -c 'import json,sys; print(json.load(open(sys.argv[1]))["archetype"])' "$WEB_PROJECT/.agentic/experience.json")" = "agentic-product"
test ! -e "$WEB_PROJECT/apps/mobile"

./agentic setup create \
  --name "Smoke Decision Desk" \
  --destination "$ENTERPRISE_PROJECT" \
  --preset web \
  --archetype enterprise-workflow \
  --audience "security teams reviewing sensitive access" \
  --promise "Move every request from evidence to accountable decision." \
  --visual-character precise \
  --business-object "access request" \
  --tenant-model multi-tenant \
  --approval-model dual-control \
  --data-sensitivity confidential \
  --yes >/dev/null
"$ENTERPRISE_PROJECT/agentic" verify full >/dev/null
test "$(python3 -c 'import json,sys; print(json.load(open(sys.argv[1]))["enabled"])' "$ENTERPRISE_PROJECT/.agentic/enterprise.json")" = "True"
test -f "$ENTERPRISE_PROJECT/docs/30-engineering/ROLE_MATRIX.md"
test -f "$ENTERPRISE_PROJECT/packages/domain/tests/workflow.test.mjs"
ENTERPRISE_NEXT="$("$ENTERPRISE_PROJECT/agentic" next)"
[[ "$ENTERPRISE_NEXT" == *"pnpm install"* ]]

./agentic setup create \
  --name "Smoke Mobile" \
  --destination "$MOBILE_PROJECT" \
  --preset mobile \
  --yes >/dev/null
"$MOBILE_PROJECT/agentic" verify full >/dev/null
MOBILE_NEXT="$("$MOBILE_PROJECT/agentic" next)"
[[ "$MOBILE_NEXT" == *"Open docs/00-vision/NORTH_STAR.md"* ]]
test ! -e "$MOBILE_PROJECT/.agentic/experience.json"
test ! -e "$MOBILE_PROJECT/apps/web"

./agentic setup create \
  --name "Smoke Core" \
  --destination "$CORE_PROJECT" \
  --preset core \
  --yes >/dev/null
"$CORE_PROJECT/agentic" verify full >/dev/null
CORE_NEXT="$("$CORE_PROJECT/agentic" next)"
[[ "$CORE_NEXT" == *"Open docs/00-vision/NORTH_STAR.md"* ]]
test ! -e "$CORE_PROJECT/apps"

./agentic release check

git diff --exit-code -- . ':!.env' >/dev/null || {
  echo "Onboarding changed tracked files in a clean checkout." >&2
  exit 1
}

echo "Clean-checkout onboarding smoke test passed."
