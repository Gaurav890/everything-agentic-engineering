# 60-second demo

This script demonstrates the system without pretending the starter implements
or ships a product autonomously.

## Recording setup

- Start from a clean terminal at 1440×900 or larger.
- Use a readable 18–20 px monospace font.
- Hide secrets, notifications, unrelated tabs, and local usernames.
- Record at normal speed; trim waiting time rather than accelerating text.
- End on Signalroom or the generated task plan, not on a wall of source code.

## Sequence

### 0–08 seconds — The problem

On screen:

```text
Stop giving coding agents prompts.
Give them an engineering system.
```

Narration:

> Coding is only one part of shipping. Agents also need product context,
> ownership, safety, verification, and a real collaboration workflow.

### 08–20 seconds — Configure only what matters

```bash
./scripts/init-project.sh --name signalroom --preset web-supabase
```

Show the preview of active profiles, inactive profiles, retained capabilities,
and external setup. Confirm the selection.

Narration:

> The guided initializer activates only the capabilities this project needs.
> Nothing is silently installed or deleted.

### 20–31 seconds — Validate the environment

```bash
./scripts/profile-doctor.sh
```

Narration:

> The doctor checks whether the selected agents, skills, tools, and environment
> are actually available.

### 31–45 seconds — Plan real work

```bash
./scripts/task-plan.sh T-101
```

Show dependency, file ownership, specialist routing, workspace, and
verification sections.

Narration:

> A durable task becomes a reviewed execution plan with dependencies, exclusive
> file ownership, specialist routing, and evidence gates.

### 45–53 seconds — Start safely

```bash
./scripts/task-start.sh T-101
```

Stop at the confirmation prompt.

Narration:

> Starting work is explicit. The system prepares a short-lived branch or
> isolated worktree; it does not implement, merge, or deploy by itself.

### 53–60 seconds — Show the result

```bash
pnpm install
pnpm dev:showcase
```

Cut to Signalroom showing an active run, approval, and durable artifact.

Narration:

> Product intent becomes coordinated work, running-product evidence, review,
> and durable memory—from idea to merge.

## Capture checklist

- [ ] Commands match the current README.
- [ ] No API keys, emails, usernames, or private paths are visible.
- [ ] Inactive capability behavior is visible.
- [ ] The confirmation gate is visible.
- [ ] Signalroom desktop and mobile frames are included.
- [ ] Captions are readable without audio.
- [ ] The final frame contains the repository name and URL.

The recording may be embedded in the README after it has been captured and
reviewed. Until then, `docs/assets/quickstart-flow.svg` is the canonical visual.
