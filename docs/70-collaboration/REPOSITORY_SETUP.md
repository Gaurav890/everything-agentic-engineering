# GitHub repository setup

Apply these settings after creating the GitHub repository.

## 1. Default branch

Use:

```text
main
```

Keep `main` releasable and protected.

## 2. Recommended ruleset for `main`

Create a branch ruleset targeting `main` with:

- Restrict branch deletion.
- Block force pushes.
- Require changes through pull requests.
- Require at least one approval for team repositories.
- Dismiss stale approvals when new code changes materially affect the reviewed diff.
- Require review conversations to be resolved.
- Require status checks:
  - `CI / verify`
  - `PR policy / policy`
- Require code-owner review for repositories that configure real CODEOWNERS.
- Optionally require linear history when the repository uses only squash or rebase merges.

Do not configure administrators to bypass rules casually. Keep any bypass list extremely small and treat it as break-glass access.

## 3. Merge settings

Recommended:

- Enable squash merging.
- Disable merge commits unless the project has a real reason to preserve them.
- Rebase merging is optional; do not enable it merely to add another choice.
- Enable auto-merge when useful.
- Automatically delete head branches after merge.

## 4. Merge queue

Leave merge queue off for small teams by default.

Enable it when:

- Many approved PRs are ready simultaneously.
- `main` changes often enough that PRs repeatedly go stale.
- Required checks are expensive and frequently rerun because of merge races.

The provided CI workflow listens for `merge_group` events so it is compatible with a future merge queue.

## 5. CODEOWNERS

Edit `.github/CODEOWNERS` and replace the commented examples with actual GitHub usernames or organization teams.

Recommended ownership boundaries:

```text
/apps/web/               frontend owners
/apps/mobile/            mobile owners
/packages/api/           backend/API owners
/packages/database/      data/backend owners
/docs/30-engineering/    architecture owners
/.github/                repository maintainers
/.claude/                agent-harness maintainers
```

For a team repository, pair CODEOWNERS with a ruleset that requires code-owner review for owned paths.

## 6. Labels

Create a small, composable label system:

### Type

```text
type: bug
type: feature
type: task
type: security
type: docs
type: spike
```

### Area

```text
area: web
area: mobile
area: backend
area: data
area: design
area: infra
area: security
area: agent-harness
```

### State

```text
status: blocked
status: needs-review
status: needs-decision
```

### Priority

```text
priority: P0
priority: P1
priority: P2
priority: P3
```

Avoid dozens of overlapping labels that nobody uses consistently.

## 7. Issue forms

The starter includes:

```text
.github/ISSUE_TEMPLATE/bug.yml
.github/ISSUE_TEMPLATE/feature.yml
.github/ISSUE_TEMPLATE/task.yml
```

Customize fields for your product rather than deleting structure.

## 8. Pull request template

The starter includes:

```text
.github/PULL_REQUEST_TEMPLATE.md
```

Require meaningful verification evidence, not a checked box with no proof.

## 9. Actions permissions

Use least privilege for GitHub Actions.

The included workflows request only:

```yaml
permissions:
  contents: read
```

Add write permissions only to a specific job that truly needs them.

## 10. Secrets and environments

For deployment workflows:

- Store secrets in GitHub Actions secrets or approved external secret managers.
- Use protected GitHub environments for sensitive deployment targets.
- Require environment approval for production when human oversight is appropriate.
- Do not expose production credentials to pull requests from untrusted forks.

This starter intentionally does not auto-deploy to production.

## 11. Suggested repository settings checklist

```text
[ ] main is the default branch
[ ] main has an active ruleset
[ ] force push is blocked
[ ] deletion of main is blocked
[ ] PR required before merge
[ ] CI checks are required
[ ] PR policy check is required
[ ] review conversations must be resolved
[ ] one approval required for team repositories
[ ] code-owner review enabled where useful
[ ] squash merge enabled
[ ] auto-delete head branches enabled
[ ] issue forms visible
[ ] CODEOWNERS customized
[ ] Actions default permissions reviewed
```
