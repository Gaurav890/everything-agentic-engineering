"""Small local evidence fixtures for approval-contract tests; not product evidence."""

import base64
import json
from pathlib import Path
import design_engine


def write(root, relative, payload):
    target = root / relative
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(payload))


def prepare(root: Path, *, approved=True):
    catalog = design_engine.load_catalog()
    direction = catalog["editorial-signal"].copy()
    write(root, ".agentic/design-directions.json", {"schema_version": 1, "directions": list(catalog.values())})
    write(root, ".agentic/design-intake.json", {
        "schema_version": 1, "status": "complete",
        "answers": {key: default for key, _, default in design_engine.INTAKE_FIELDS},
    })
    evidence = "docs/50-evals/fixture.png"
    target = root / evidence
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_bytes(base64.b64decode("iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mP8/x8AAusB9Wl6V1sAAAAASUVORK5CYII="))
    brief = root / ".agentic/project-brief.json"
    if brief.exists():
        data = json.loads(brief.read_text())
        data.update(status="ready", first_outcome="A test outcome", confirmed_by="Test reviewer", design_mode="reference")
        write(root, ".agentic/project-brief.json", data)
    state = {"schema_version": 1, "status": "approved" if approved else "needs_approval",
             "approved_direction": "editorial-signal" if approved else None,
             "approved_by": "Test reviewer", "approved_at": "2026-08-27T00:00:00Z"}
    if approved:
        state.update(evidence=[evidence], fingerprint=design_engine.approval_fingerprint(root, direction, [evidence]))
    write(root, ".agentic/design.json", state)
    return state
