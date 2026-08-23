# Harness evolution policy

The evolution kernel is built into the core profile because every downstream
project benefits from a safe improvement contract. It is inactive until a user
provides sanitized evidence and an explicit candidate-results file.

## Shortest path

```bash
./agentic evolve status
./agentic evolve signal validate path/to/sanitized-signal.json
./agentic evolve compare --candidate path/to/candidate-results.json
```

`status` and `validate` prove that policy, schemas, protected cases, and the
incumbent agree. `signal validate` accepts only aggregate, redacted records.
`compare` evaluates a supplied candidate; it does not produce or apply one.

## Authority

The machine-readable policy allows proposal and comparison. It denies candidate
writes, eval modification, promotion, deployment, approval, and merge.

These denials are product behavior, not documentation decoration. Validation
fails if they are weakened.

## Change surfaces

| Surface | Risk | Required review |
|---|---|---|
| Few-shot examples | Low | QA evaluator |
| Instructions | Medium | QA evaluator and security |
| Memory curation | Medium | QA evaluator and security |
| Routing | Medium | Architecture, QA, and security |

Anything outside these reviewed paths is rejected. Protected patterns take
precedence over allowed patterns.

The comparator checks the paths declared in candidate evidence and reports the
reviews required by every selected surface. Before accepting that report, the
reviewer must reconcile the declaration with the actual pull-request diff;
normal code-owner and branch protections remain authoritative. Candidate
evidence is not trusted to certify its own file coverage.

## Data handling

The starter stores no production trace database. Do not commit raw signals.
Commit only synthetic fixtures, aggregate reports that pass the privacy
contract, and review evidence without customer content.

Before adding real signal adapters, define purpose limitation, consent,
retention, deletion, encryption, tenant isolation, regional boundaries, access
control, breach response, and whether signals may ever enter training data.

## Rollback

The last-known-good harness remains the incumbent until a reviewed PR lands.
Rejecting a candidate changes nothing. If a later accepted harness regresses,
revert its normal repository commit and restore the prior evaluated incumbent
through a separately reviewed PR.

No scheduled loop may rewrite this policy, its evals, or its incumbent.
