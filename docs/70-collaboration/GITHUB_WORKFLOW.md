# GitHub workflow

This repository uses a lightweight trunk-based workflow built around a protected `main` branch, short-lived task branches, pull requests, automated checks, and durable project context.

The default path is:

```text
ISSUE / TASK
    ↓
SYNC MAIN
    ↓
CREATE SHORT-LIVED BRANCH
    ↓
IMPLEMENT + VERIFY
    ↓
DRAFT PR EARLY WHEN COLLABORATION HELPS
    ↓
REVIEW + CI + SECURITY / CODE OWNER GATES
    ↓
SQUASH MERGE TO MAIN
    ↓
DELETE BRANCH
    ↓
MARK TASK DONE + RECORD DURABLE STATE
```

## 1. The branch model

`main` is always the integration branch and should remain releasable.

Do not work directly on `main` except for an explicitly approved break-glass emergency. Normal work happens on short-lived branches created from an up-to-date `main`.

Use these branch prefixes:

| Type | Use for | Example |
|---|---|---|
| `feat/` | New product capability | `feat/T-014-password-reset` |
| `fix/` | Bug fix | `fix/T-028-token-expiry` |
| `docs/` | Documentation-only change | `docs/T-031-auth-guide` |
| `refactor/` | Internal change with no intended product behavior change | `refactor/T-033-billing-service` |
| `test/` | Test-only work | `test/T-040-checkout-e2e` |
| `chore/` | Maintenance, tooling, dependencies | `chore/T-045-dependencies` |
| `spike/` | Time-boxed research or prototype | `spike/T-052-queue-benchmark` |
| `security/` | Security hardening or remediation | `security/T-060-rate-limit` |
| `hotfix/` | Urgent production fix | `hotfix/T-071-checkout-crash` |
| `agent/` | Isolated autonomous-agent worktree | `agent/T-014-password-reset` |

Canonical format:

```text
<type>/<TASK-ID>-<short-kebab-case-description>
```

Use:

```bash
./scripts/new-branch.sh feat T-014 password-reset
```

For parallel agent coding, use a worktree:

```bash
./scripts/create-worktree.sh T-014 password-reset agent main
```

### When not to create a branch

Only skip a branch for a local experiment that will never be committed. Any committed change that may reach `main` should go through a task branch and pull request.

## 2. When to raise a GitHub issue

Create an issue when any of these are true:

- A bug has user, customer, security, reliability, or data impact.
- A feature needs product discussion, acceptance criteria, or prioritization.
- Work spans multiple pull requests or contributors.
- The change needs a decision from another team or colleague.
- There is an unresolved blocker, risk, or dependency.
- The work should be discoverable later from GitHub history.

A separate issue is optional for:

- A typo or extremely small documentation cleanup.
- A tiny internal maintenance change already represented by a task ID and fully explained in the pull request.
- An emergency hotfix, provided a follow-up issue is created for any deferred cleanup or root-cause work.

### Security exception

Do not put active vulnerability details, exploitable secrets, or sensitive incident information in a public issue. Use the repository's private security reporting path or a restricted internal channel.

## 3. Relationship between GitHub issues and `TASKS.jsonl`

Use both when the work matters enough to require collaboration or durable tracking:

```text
GitHub issue  = human discussion, ownership, priority, external collaboration
TASKS.jsonl   = agent-executable unit, dependencies, file ownership, verification
```

One GitHub issue may decompose into multiple task IDs.

Example:

```text
Issue #128: Add password recovery
  ├── T-014 backend token flow
  ├── T-015 email delivery
  ├── T-016 web UI
  └── T-017 end-to-end verification
```

Reference both in the pull request:

```text
Closes #128
Task: T-016
```

## 4. Starting work

Before coding:

1. Read the relevant requirement and acceptance criteria.
2. Confirm or create the task in `TASKS.jsonl`.
3. Identify any GitHub issue that owns the work.
4. Pull the latest `main`.
5. Create a short-lived branch or isolated worktree.
6. Mark the task `in_progress`.
7. For parallel work, record file ownership and merge order in `PARALLELIZATION.md`.

Recommended commands:

```bash
git switch main
git pull --ff-only origin main
./scripts/new-branch.sh feat T-014 password-reset
```

Or, for an agent worktree:

```bash
./scripts/create-worktree.sh T-014 password-reset agent main
```

## 5. Commit discipline

Make small, meaningful commits that represent coherent checkpoints.

Recommended commit format:

```text
feat(T-014): add password-reset confirmation state
fix(T-028): reject expired refresh tokens
security(T-060): enforce request rate limits
```

Do not:

- Commit secrets.
- Mix unrelated fixes into one branch.
- Use commits as a substitute for updating durable project state.
- Rewrite shared branch history after a colleague has based work on it unless everyone involved explicitly agrees.

## 6. When to open a pull request

Open a pull request as soon as review or visibility becomes useful.

Use a **draft pull request** when:

- The work is still in progress but a colleague should see direction early.
- The change spans multiple days.
- It changes an API, schema, auth boundary, design system, or architecture.
- Another contributor depends on the branch.
- You want early feedback before completing implementation.

Use a normal ready-for-review pull request when the implementation is complete enough for someone to make a merge decision.

Do not wait until a giant feature is finished before creating the first PR. Prefer vertical, independently verifiable slices.

## 7. Pull request requirements

Every meaningful PR should state:

- What changed.
- Why it changed.
- Linked issue and task ID.
- Requirements and acceptance criteria affected.
- Files or systems with meaningful risk.
- Verification evidence.
- Screenshots or video for substantial UI changes.
- Security, auth, data, migration, or deployment impact.
- Durable context files updated.

The repository includes `.github/PULL_REQUEST_TEMPLATE.md` so this structure appears automatically.

## 8. PR title format

Use:

```text
<type>(<TASK-ID>): <imperative summary>
```

Examples:

```text
feat(T-014): add password reset confirmation
fix(T-028): prevent expired refresh token reuse
security(T-060): enforce request rate limiting
```

The PR policy workflow validates this format.

## 9. Collaboration with colleagues

The default team behavior is:

### Before implementation

- Agree on the issue or requirement being solved.
- Assign one accountable owner.
- Identify affected systems and reviewers.
- For parallel work, assign exclusive file/module ownership.
- Surface API, schema, auth, design-system, and architecture changes before they become expensive to unwind.

### During implementation

- Push working checkpoints regularly.
- Use a draft PR as the shared collaboration surface.
- Keep the PR description current as scope changes.
- Resolve disagreements in the owning source-of-truth artifact, not only in chat.
- Do not let two contributors independently modify the same tightly coupled files without explicit coordination.

### Review language

Use clear review intent:

```text
BLOCKING: must change before merge
QUESTION: clarification needed before deciding
SUGGESTION: recommended but not required
NIT: minor polish, never a merge blocker
```

Review the code against the stated acceptance criteria and risks, not personal style preferences.

## 10. Who should review

Minimum recommendation:

- Solo repository: self-review is acceptable, but automated checks and evidence are still required.
- Team repository: at least one approval for normal changes.
- Sensitive change: require the relevant domain owner when auth, permissions, payment, PII, secrets, security controls, production data, destructive migration, or deployment infrastructure is affected.

Use `.github/CODEOWNERS` after replacing the commented examples with real GitHub users or teams.

## 11. Merge readiness gate

A pull request is ready to merge only when all applicable items are true:

- Scope matches the issue/task and no unrelated work is hidden inside.
- Acceptance criteria are satisfied.
- Required CI checks pass.
- Required approvals are present.
- Review conversations are resolved.
- Security-sensitive changes have the right review.
- UI has been visually verified when applicable.
- Schema, API, architecture, or design decisions are documented.
- `CURRENT_STATE.md`, `PROGRESS.md`, `HANDOFF.md`, and task state are updated when the project truth changed.
- The branch is not knowingly stale in a way that invalidates verification.

Run before requesting final review:

```bash
./scripts/pr-ready.sh T-014
./scripts/finish-task.sh T-014
# commit the review-state update
```

When the implementation is final and the PR is ready for its last review/check cycle:

```bash
./scripts/prepare-merge.sh T-014
# commit this final task-state update; then complete final review/checks and merge
```

## 12. Merge strategy

### Default: squash merge

Use squash merge for normal feature, fix, documentation, and maintenance PRs. The result is one coherent commit on `main` per merged PR, while the PR still preserves discussion, review, and intermediate branch history.

Recommended squash commit title:

```text
feat(T-014): add password reset confirmation (#128)
```

### Use a merge commit only when history structure matters

Examples:

- Preserving a deliberately curated multi-commit change series.
- Integrating a long-lived release or vendor branch.
- A repository policy explicitly requires it.

This starter does not recommend long-lived feature branches by default.

### Merge queue

Enable a merge queue only when repository traffic is high enough that many approved PRs compete to merge into `main` and frequently invalidate one another's checks.

## 13. After merge

After the PR lands:

1. Delete the task branch automatically or manually.
2. Confirm `main` now contains the task status and durable-state changes from the PR.
3. Record the PR link or merge evidence in `PROGRESS.md` when useful.
4. Pull the latest `main` before starting dependent work.
5. The owning issue should close automatically when the PR uses a closing keyword such as `Closes #128`; otherwise close or update it manually.
6. Re-evaluate any tasks that depended on the merged change.

## 14. Hotfix workflow

For an urgent production incident:

1. Create `hotfix/<TASK-ID>-<slug>` directly from current `main`.
2. Keep scope as small as possible.
3. Do not bundle cleanup or unrelated refactoring.
4. Run the normal required checks unless the break-glass procedure explicitly authorizes an exception.
5. Obtain at least one reviewer when available.
6. Merge, deploy through the approved deployment path, and verify production behavior.
7. Create follow-up work for root cause, tests, observability, and deferred cleanup.

Do not normalize bypassing protections just because a change is urgent.

## 15. Task lifecycle

Recommended statuses:

```text
backlog
  ↓
ready
  ↓
in_progress
  ↓
review
  ↓
done
```

Side states:

```text
blocked
needs_human
failed_safe
```

`finish-task.sh` moves a task to `review` after verification. Before final merge, `prepare-merge.sh` writes `done` on the task branch; because `main` is the source of truth, the task becomes durably done only when that PR lands in `main`.

## 16. The default answer to common workflow questions

| Question | Default answer |
|---|---|
| Direct push to `main`? | No. |
| Branch for every committed change? | Yes, except explicit break-glass emergency handling. |
| Issue for every typo? | No. |
| Issue for bugs/features/cross-team work? | Yes. |
| Draft PR before code is finished? | Yes, when early visibility or feedback helps. |
| One branch per developer forever? | No. One short-lived branch per task or coherent slice. |
| Multiple agents editing same file in parallel? | No. |
| Merge with failing checks? | No. |
| Default merge method? | Squash merge. |
| Delete merged branches? | Yes. |
| Mark task done before merge? | No. |
