# Skills strategy

## Core project-local skills

Already included:

- `create-prd`
- `decompose-prd`
- `context-handoff`
- `design-system`
- `research-ledger`
- `parallel-plan`
- `loop-engineering`
- `security-gate`

These encode project behavior and should remain version-controlled.

## External skills: final core recommendation

### Frontend creation

**Anthropic `frontend-design`**

Purpose:
- distinctive production-grade frontend creation,
- design intent,
- critique loop.

### React/Next.js engineering

**Vercel `react-best-practices`**

Purpose:
- React/Next.js performance and engineering guidance.

### UI/UX audit

**Vercel `web-design-guidelines`**

Purpose:
- accessibility,
- focus,
- forms,
- animation,
- typography,
- performance,
- navigation/state,
- theming,
- touch,
- i18n.

### Mobile

**Vercel `react-native-guidelines`**
and, when mobile is enabled,
**official Expo skills/plugin**.

## Workflow plugin

**Superpowers** is recommended as an optional workflow layer for brainstorming, planning, worktrees, TDD, debugging, and subagent-driven development.

Do not let Superpowers replace this repository's durable product truth, acceptance criteria, security gates, or handoff system.

## Install philosophy

Do not install every popular skill.

Install a skill when:
- the domain is active,
- the instructions are narrow and high quality,
- the source is trusted,
- the skill does not conflict heavily with another loaded skill.

Avoid:
- 100-skill dumps,
- overlapping frontend taste skills all loaded together,
- stale stack-specific instructions,
- unknown skills with shell hooks you have not reviewed.

## Creative frontend companions

Optional, choose at most one initially:
- `taste-skill`
- `ui-ux-pro-max`

The starter does not auto-install either. First see whether Anthropic frontend-design + the project's own design-system skill + Vercel audit is enough.

## Mobile plugin

For Expo projects, install the official Expo plugin in Claude Code:

```text
/plugin install expo@claude-plugins-official
```

## Superpowers plugin

In Claude Code:

```text
/plugin install superpowers@claude-plugins-official
```
