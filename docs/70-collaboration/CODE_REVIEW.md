# Code review standard

Code review exists to reduce risk, improve clarity, transfer context, and verify that a change actually solves the intended problem.

## Review order

Review in this order:

1. **Intent** — does the PR solve the linked requirement or issue?
2. **Scope** — is unrelated work mixed in?
3. **Correctness** — does behavior match acceptance criteria?
4. **Security and data** — are trust boundaries, auth, secrets, PII, and migrations safe?
5. **Failure behavior** — what happens on timeout, bad input, retries, partial failure, or dependency outage?
6. **Tests and evidence** — is proof strong enough for the risk?
7. **Maintainability** — is the design understandable and consistent with architecture?
8. **Polish** — naming, readability, comments, and minor cleanup.

Do not spend ten minutes debating formatting while a security boundary or missing error path remains unreviewed.

## Review comment vocabulary

Use:

```text
BLOCKING: must change before merge
QUESTION: clarification needed before deciding
SUGGESTION: recommended but not required
NIT: minor polish; never a merge blocker
```

A blocking comment should explain the concrete risk or violated requirement.

## Author responsibilities

Before requesting review:

- Keep the PR description current.
- Self-review the entire diff.
- Remove accidental debug code and unrelated changes.
- Run `./scripts/pr-ready.sh <TASK-ID>`.
- Attach visual evidence for UI work.
- Call out migrations, auth, security, data, API, or deployment impact.
- Link the issue and task.
- Mark unresolved uncertainty explicitly.

## Reviewer responsibilities

- Read the PR intent before the diff.
- Check the acceptance criteria.
- Pull or run the code when risk justifies it.
- Prefer concrete, actionable feedback.
- Distinguish personal preference from a correctness issue.
- Re-request changes only for real blockers.
- Re-review meaningful changes after the author updates the branch.

## Sensitive changes

Require specialist or code-owner review when applicable for:

- Authentication or authorization.
- Permissions or role logic.
- Payment or billing.
- PII or sensitive data.
- Secret management.
- Production data mutation.
- Destructive migrations.
- Cryptography.
- Infrastructure or deployment controls.
- Security policy or protective hooks.

## AI-generated changes

AI-generated code is reviewed by the same standard as human-authored code.

Never treat "the agent said tests passed" as evidence. Reviewers should rely on actual checks, logs, screenshots, test results, and inspected behavior.
