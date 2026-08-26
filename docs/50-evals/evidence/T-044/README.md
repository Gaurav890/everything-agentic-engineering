# T-044 enterprise golden-path evidence

Status: Builder verification complete; independent and human review pending.

## Product contract

- One public command starts guided creation.
- Enterprise selection adds only business object, tenancy, approval model, and
  data-sensitivity questions.
- The output contains one working request-decision journey and one next action.
- Local demonstration adapters are visible and `production_ready` is false.

## Running-product evidence

- Requester/admin creation is role-scoped and repository-backed.
- Cross-tenant actors receive no request data before action handling.
- Auditor, reviewer, requester, administrator, self-approval, evidence,
  rationale, and state policies fail closed at the domain boundary.
- The UI covers queue loading, empty, invalid input, refresh failure, recovery,
  incomplete evidence, disabled action, success, and append-only audit outcomes.
- Editorial Signal, Kinetic Index, and Quiet Material remain visibly distinct on
  desktop and mobile without changing the workflow contract.

## Verification recorded before commit

```text
python3 -m unittest tests.test_project_generator tests.test_next_action
PASS — 27 tests

domain / API / web model tests
PASS — 4 + 2 + 5 tests

source production build
PASS

source Playwright interaction/accessibility suite
PASS — 23 passed, 1 intentional skip

source visual comparison
PASS — 24 cases

fresh generated enterprise project
./agentic verify full — PASS
pnpm test:e2e — PASS, 17 passed and 7 intentionally irrelevant skips
```

## Review still required

- independent product-design and adversarial QA evaluation;
- independent security and authority evaluation;
- Linux visual candidate generation and human inspection;
- full repository verification and release smoke at the exact committed head;
- human task approval and pull-request merge decision.

Builder verification does not grant approval, production authority, or merge
authority.
