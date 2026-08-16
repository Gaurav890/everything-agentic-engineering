#!/usr/bin/env python3
"""Validate a materialized downstream project without external access."""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from project_generator import GenerationError, validate_generated_project  # noqa: E402


def main() -> int:
    try:
        report = validate_generated_project(ROOT)
    except GenerationError as error:
        print(f"Generated project verification failed: {error}", file=sys.stderr)
        return 1
    print(json.dumps(report, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
