# Backend rules

- Validate at every trust boundary.
- Authenticate and authorize server-side.
- Do not expose service-role credentials to clients.
- Prefer idempotent writes for retryable workflows.
- Define timeouts, retries, and terminal failure states explicitly.
- Log critical workflow transitions without leaking secrets.
- Document migrations, rollback strategy, and compatibility impact.
- Production writes and destructive migrations require human approval.
- For enterprise workflows, enforce tenant and role policy server-side, deny
  self-approval and invalid transitions, require evidence/rationale, and persist
  the transition and audit event atomically.
- Browser actor switching and in-memory persistence are local demonstrations,
  not production identity, authorization, storage, or audit guarantees.
