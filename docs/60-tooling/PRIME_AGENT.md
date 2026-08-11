# Prime Agent optional runtime contract

Prime Agent is an **optional, disabled-by-default runtime**, not part of the
starter's core installation. It may be useful when an approved task genuinely
requires a long-running session, persistent goal, schedule, bounded subagents,
or continual harness work that cannot be handled inside one interactive coding
session.

The reviewed upstream source is
[PrimeIntellect-ai/prime-agent](https://github.com/PrimeIntellect-ai/prime-agent)
at commit `71ca6cfd1a2f7205ca0ec1baa65d10d0ed88f6e8` (MIT license, reviewed
2026-08-10). A source pin establishes provenance; it does not grant permission
to download, install, run, authenticate, update, or enable anything.

## Critical security boundary

Prime Agent executes model-generated Python and commands with the user's
permissions. Its workers and kernels are execution environments, **not a
security sandbox**. Use an independently reviewed external sandbox when the
work executes untrusted code or handles untrusted artifacts.

Installation does not authorize credentials, providers, models, MCPs, network,
sandbox changes, schedules, daemons, production, deployment, billing, external
writes, PR approval, or merge. Each authority expansion requires a separate,
scoped human decision.

## When to recommend it

Recommend this adapter only when durable task evidence shows that work must
survive a single interactive session, a schedule is explicitly authorized, or
bounded subagents materially reduce elapsed time. The goal must already have
measurable stop conditions, independent evaluation, exact worktree ownership,
and rollback. Do not recommend it for ordinary feature work or as a substitute
for a missing plan.

## Read-only doctor

```bash
python3 scripts/capability_adapters/prime_agent.py doctor
python3 scripts/capability_adapters/prime_agent.py doctor --json
```

The doctor only searches local `PATH`. It does not execute a detected binary,
probe a version, inspect configuration, connect to a service, or change the
repository. `FOUND` means only that a path exists—not that it is trusted,
compatible, configured, enabled, or approved.

## Plan-only output

```bash
python3 scripts/capability_adapters/prime_agent.py plan
python3 scripts/capability_adapters/prime_agent.py plan --json
```

The plan is inert data. It contains no executable installation command and
performs no download, install, login, service start, schedule creation,
provider/model selection, credential access, MCP registration, network/sandbox
change, production action, approval, or merge.

Before separately approved use, record one task branch and isolated worktree,
exclusive files, allowed and forbidden actions, execution budgets, a
human-owned kill switch, an independent evaluator, and exact rollback paths.
The default ceiling is 60 minutes, three attempts per failure, three parallel
subagents, three worktrees, one scheduled run before review, and ten idle
minutes. These are ceilings, not permission to consume them.

Rollback stops the dedicated process group and approved schedules, preserves
evidence, revokes only exact session credentials, and removes only
human-confirmed isolated paths. It never changes `main`, branch protections,
approvals, or production.

This repository intentionally provides recommendation, detection, and planning
only. Runtime installation and execution remain out of scope.
