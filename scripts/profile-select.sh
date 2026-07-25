#!/usr/bin/env bash
set -euo pipefail

if [ "$#" -lt 1 ] || [ "$#" -gt 2 ]; then
  echo "Usage: $0 <comma-separated-profiles> [--yes]" >&2
  exit 2
fi

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
if [ "${2:-}" = "--yes" ]; then
  exec python3 "$ROOT/scripts/profile_engine.py" select --profiles "$1" --yes
fi
exec python3 "$ROOT/scripts/profile_engine.py" select --profiles "$1"
