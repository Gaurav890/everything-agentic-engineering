# Harness evolution evaluations

## Protected cases

The starter ships five synthetic contract cases under
`.agentic/evolution/eval-sets/harness-regression.jsonl`. Each case has a stable
id, category, positive weight, protected status, and minimum quality.

All committed starter cases are protected. Downstream teams should add
domain-specific cases through a separate human-owned evaluation change, not in
the same PR as a harness candidate.

## Evaluation result

Incumbent and candidate results use the same closed shape:

```json
{
  "schema_version": 1,
  "harness_id": "candidate-v2",
  "policy_sha256": "<current policy sha256>",
  "eval_set_sha256": "<current eval-set sha256>",
  "builder_role": "orchestrator",
  "evaluator_role": "qa-evaluator",
  "changed_paths": ["CLAUDE.md"],
  "cases": [
    {
      "case_id": "traceability",
      "quality_score": 0.9,
      "safety_pass": true,
      "cost_units": 10,
      "latency_ms": 900
    }
  ]
}
```

The real file must contain every protected case exactly once. Builder and
evaluator roles must differ.

## Commands

```bash
./agentic evolve status
./agentic evolve validate --json
./agentic evolve signal validate sanitized-signal.json --json
./agentic evolve compare --candidate candidate-results.json --json
```

All commands are offline and read-only. Comparison exits `0` for an eligible
candidate, `1` for a valid candidate that fails one or more gates, and `2` for
invalid or insufficient evidence.

## Gate semantics

The comparator calculates weighted quality, total cost ratio, and nearest-rank
p95 latency ratio. It reports the exact protected regressions, safety failures,
and every Boolean gate.

Do not interpret a synthetic score as a user outcome. In a downstream product:

- ground explicit outcomes first;
- treat edits, retries, and escalations as noisy signals;
- calibrate any learned judge against human labels;
- retain a hidden human-owned slice to detect eval overfitting;
- choose sample and confidence requirements for the domain;
- compare candidate and incumbent under the same environment.

The starter intentionally does not encode a universal production sample-size
claim.

## Review checklist

- Were signals sanitized before validation?
- Did candidate and incumbent use the exact policy and eval fingerprints?
- Are all protected cases present exactly once?
- Did any case regress even if the mean improved?
- Did safety remain perfect?
- Did cost or p95 latency exceed the budget?
- Are declared paths complete and allowed?
- Do the declared paths exactly match the actual pull-request diff?
- Did every review reported for the selected surfaces occur?
- Is the evaluator independent?
- Were the exam and candidate changed in separate reviews?
- Is promotion still a separate human decision?
