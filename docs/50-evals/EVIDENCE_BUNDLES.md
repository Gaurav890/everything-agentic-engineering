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
evaluator distinct from the builder.

Validate one or more bundles with:

```bash
python3 scripts/validate_evidence.py docs/50-evals/evidence/T-014
```

The repository verification suite validates every committed bundle
automatically.
