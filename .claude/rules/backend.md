# Backend rules

- Validate at every trust boundary.
- Authenticate and authorize server-side.
- Do not expose service-role credentials to clients.
- Prefer idempotent writes for retryable workflows.
- Define timeouts, retries, and terminal failure states explicitly.
- Log critical workflow transitions without leaking secrets.
- Document migrations, rollback strategy, and compatibility impact.
- Production writes and destructive migrations require human approval.
