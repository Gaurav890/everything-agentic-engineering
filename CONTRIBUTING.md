# Contributing

Use the repository's GitHub workflow for all committed changes.

## Start here

Read:

1. `CLAUDE.md`
2. `docs/70-collaboration/GITHUB_WORKFLOW.md`
3. `docs/70-collaboration/CODE_REVIEW.md`
4. The relevant product, design, engineering, and task artifacts.

## Normal contribution flow

```text
issue/task → branch → implementation → verification → PR → review → merge → delete branch → mark task done
```

Create a branch:

```bash
./agentic workspace branch feat T-014 password-reset
```

Before human review:

```bash
./agentic pr ready T-014
./agentic task finish T-014
# commit and push the review-state update; keep the PR draft
```

After the reviewer directly says `T-014 approved`:

```bash
./agentic pr finalize T-014 --dry-run
./agentic pr finalize T-014 --yes
```

The bounded finalizer prepares and pushes the task-state update, marks a draft
ready, and waits for checks. Do not manually edit `TASKS.jsonl`. The finalizer
never approves or merges; a human squash-merges after checks are green. `main`
becomes the durable source of truth only when the PR is actually merged.

## Rules

- Do not push directly to protected `main`.
- Do not commit secrets.
- Keep one coherent change per branch/PR.
- Link task IDs and issues.
- Include evidence.
- Update durable state when project truth changes.
- Use squash merge by default.
- Delete merged branches.

## Command discovery

Run `./agentic --help` for the supported command groups or
`./agentic commands --json` for a machine-readable list. Existing
`./scripts/*.sh` paths remain compatible during the migration, but new
documentation and contributor workflows should use `./agentic`.

See `docs/70-collaboration/GITHUB_WORKFLOW.md` for the complete operating model.
