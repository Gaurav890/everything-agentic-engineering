# Evidence bundles

Important tasks store proof under `docs/50-evals/evidence/<TASK-ID>/`.

An `evidence.json` manifest makes completion claims machine-checkable:

```json
{
  "task_id": "T-014",
  "acceptance_ids": ["AC-041", "AC-042"],
  "ui_change": true,
  "builder": "frontend",
  "evaluator": "qa-evaluator",
  "commands": ["pnpm test", "pnpm test:e2e"],
  "states": ["normal", "loading", "empty", "error"],
  "viewports": ["mobile", "desktop"],
  "artifacts": [
    "desktop.png",
    "mobile.png",
    "critic.md",
    "accessibility.json"
  ],
  "verdict": "PASS"
}
```

Paths in `artifacts` are relative to the bundle. UI changes require normal,
loading, empty, and error evidence; mobile and desktop evidence; and an
evaluator distinct from the builder. Every bundle, including non-UI evidence,
requires non-empty and distinct builder and evaluator identities. Artifact
paths must resolve to regular, non-symlinked files inside the bundle; absolute
paths and traversal are invalid.

Verdicts use one exact status, optionally followed by ` — ` and a concise
explanation: `PASS`, `PASS_WITH_RISKS`, `PASS_WITH_REVIEW_PENDING`,
`PASS_WITH_PORTABLE_PACKAGING_BLOCKED`, `FAIL`, `BLOCKED`, `NEEDS_HUMAN`, or
`INSUFFICIENT_EVIDENCE`. Only `PASS` evidence can advance the project journey;
qualified or non-passing evidence remains visible without certifying completion.

Validate one or more bundles with:

```bash
python3 scripts/validate_evidence.py docs/50-evals/evidence/T-014
```

The repository verification suite validates every committed bundle
automatically.
