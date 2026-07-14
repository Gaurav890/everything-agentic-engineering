# Verification rules

Agent confidence is not evidence.

Use the smallest relevant verification set:
- formatting/lint,
- typecheck,
- unit tests,
- integration tests,
- end-to-end tests,
- visual inspection,
- accessibility checks,
- security review,
- observability evidence.

For UI, inspect the running product.
For backend, verify success and failure paths.
For migrations, test forward and rollback behavior when possible.
For external integrations, distinguish mocked evidence from live-system evidence.
