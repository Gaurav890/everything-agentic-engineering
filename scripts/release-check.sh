#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

PACKAGE_VERSION="$(
  node -e "const p=require('./package.json'); process.stdout.write(p.version)"
)"
PORTABLE_PLUGIN_VERSION="$(
  node -e "const p=require('./plugin.json'); process.stdout.write(p.version)"
)"
CODEX_PLUGIN_VERSION="$(
  node -e "const p=require('./.codex-plugin/plugin.json'); process.stdout.write(p.version)"
)"
if [ "$PORTABLE_PLUGIN_VERSION" != "$PACKAGE_VERSION" ] || \
   [ "$CODEX_PLUGIN_VERSION" != "$PACKAGE_VERSION" ]; then
  echo "Package, portable plugin, and Codex-native plugin versions must match." >&2
  exit 1
fi
EXPECTED_TAG="v${PACKAGE_VERSION}"
REQUESTED_TAG="${1:-$EXPECTED_TAG}"

if [[ ! "$REQUESTED_TAG" =~ ^v[0-9]+\.[0-9]+\.[0-9]+([.-][0-9A-Za-z.-]+)?$ ]]; then
  echo "Invalid semantic release tag: $REQUESTED_TAG" >&2
  exit 1
fi

if [ "$REQUESTED_TAG" != "$EXPECTED_TAG" ]; then
  echo "Release tag $REQUESTED_TAG does not match package version $PACKAGE_VERSION." >&2
  exit 1
fi

NOTES="docs/releases/${REQUESTED_TAG}.md"
test -f "$NOTES" || {
  echo "Missing release notes: $NOTES" >&2
  exit 1
}

grep -Fq "## [${PACKAGE_VERSION}]" CHANGELOG.md || {
  echo "CHANGELOG.md has no ${PACKAGE_VERSION} release section." >&2
  exit 1
}

grep -Fq "$REQUESTED_TAG" README.md || {
  echo "README.md does not identify $REQUESTED_TAG." >&2
  exit 1
}

grep -Fq "$REQUESTED_TAG" docs/60-tooling/COMPATIBILITY.md || {
  echo "Compatibility documentation does not identify $REQUESTED_TAG." >&2
  exit 1
}

echo "Release contract valid for $REQUESTED_TAG."
