# Codex adapter

Codex is a first-class repository surface. `AGENTS.md` carries the universal
engineering contract; `.codex/` provides narrow Codex runtime wiring; the
canonical skills and safety scripts remain shared with the Claude adapter.

## Start safely

From a trusted checkout:

```bash
./scripts/runtime-doctor.sh
./scripts/codex-doctor.sh
codex
```

The doctor validates repository configuration even when Codex is unavailable,
which keeps CI framework-independent. Maintainers validating plugin behavior
on a developer machine can require the runtime floor:

```bash
./scripts/codex-doctor.sh --strict-runtime
```

Codex 0.147.0 or newer is the recommended baseline for plugin workflows. An
older runtime does not authorize an automatic upgrade; review and approve
runtime changes separately.

The shared runtime doctor reads `.agentic/runtime-baselines.json`, supports
advisory, strict, and JSON reports, and performs no mutation. The Codex doctor
reuses that baseline so version policy cannot drift between scripts.

## Source-of-truth map

| Surface | Purpose |
|---|---|
| `AGENTS.md` | Cross-runtime engineering, review, and safety contract |
| `.codex/config.toml` | Safe project-scoped Codex context and concurrency defaults |
| `.codex/agents/*.toml` | Read-only project-scoped Codex specialist roles |
| `.codex/hooks.json` | Codex lifecycle wiring for reviewed safety scripts |
| `.agents/skills` | Codex repository skill discovery |
| `.claude/skills` | Canonical local skill content shared by both adapters |
| `plugin.json` | Agent Plugins 1.0 portable manifest |
| `skills` | Portable fixed-location link to the canonical skill catalog |
| `.codex-plugin/plugin.json` | Separate Codex-native compatibility and interface metadata |

Codex officially supports symlinked repository skills. Both links are checked
by the doctor and CI so Claude, Codex, and the plugin cannot silently diverge.

## Configuration boundary

The committed `.codex/config.toml` intentionally sets only:

- the project-instruction byte budget;
- bounded spawned-agent concurrency;
- lifecycle-hook discovery.

It does **not** choose a model/provider, define credentials, register MCP
execution, enable network access, expand writable paths, select a sandbox, or
bypass approval. User and managed enterprise policy remain authoritative.
Codex ignores project `.codex/` layers until the repository is trusted.

## Hooks

Project hooks reuse:

```text
.claude/hooks/pre-tool-security.sh
.claude/hooks/post-edit-secret-scan.sh
```

The destructive-command hook can deny supported Bash calls. The secret scanner
warns after Claude edit/write calls and Codex `apply_patch` calls. Hooks are a
guardrail, not a security boundary.

Review the exact project hook definitions with `/hooks` before trusting them.
Changed hooks require renewed trust in Codex.

## Parallel work

Use Codex-managed worktrees in the desktop app or the repository task launcher
from separate terminals. In both cases:

- one task owns one branch/worktree;
- one writer owns each file or tightly coupled module;
- shared contracts merge before dependent implementations;
- workers verify their own scope;
- an independent evaluator verifies the integrated claim.

Read [Parallel terminals](../70-collaboration/PARALLEL_TERMINALS.md) for the
full operating pattern.

## Specialist subagents

Codex automatically discovers the custom agents under `.codex/agents/` after
the project is trusted. The starter includes bounded roles for product
planning, architecture, research, design critique, security review,
adversarial QA, and final integration review.

All committed roles:

- use `sandbox_mode = "read-only"`;
- inherit the parent session's approved capabilities without adding new ones;
- avoid repository-level model and reasoning choices;
- do not register MCP servers, credentials, network access, or approval rules;
- return findings to the parent rather than modifying or approving the change.

Example:

```text
Review this branch against main. Use architect to map contract changes,
security_reviewer to identify trust-boundary risks, and qa_evaluator to find
acceptance or regression gaps. Wait for all three, then consolidate only
evidence-backed findings with file references. Do not modify code.
```

Use Codex's built-in `explorer` for ordinary code mapping. For multiple agents
that must change code, create separate task branches and worktrees instead of
making the in-session specialist roles writable.

## Skills and plugin packaging

Codex discovers the project skills directly through `.agents/skills`. The
Agent Plugins 1.0 portable core exposes the same catalog through the fixed
`skills/` location. The existing `.codex-plugin/plugin.json` remains a separate
Codex-native compatibility surface during the additive migration. Neither
package bundles MCP servers, apps, credentials, or lifecycle hooks.

Validate the portable package with:

```bash
./agentic doctor plugin
```

Validate the Codex-native compatibility package with the installed
plugin-creator skill when maintaining that surface:

```bash
python3 /path/to/plugin-creator/scripts/validate_plugin.py .
```

The root `plugin.json` is the portable package source. Read
[Agent Plugins packaging](AGENT_PLUGINS.md) for the compatibility boundary.
Publishing to a marketplace, changing installation policy, or enabling
external capabilities remains a separate reviewed release action.

## MCP and external services

`.mcp.json` remains the Claude project configuration. The Codex adapter does
not silently translate or start those servers because doing so could execute
third-party packages or request external credentials.

Configure approved Codex MCP servers in user, team, or separately reviewed
project configuration only when the active profile requires them. Preserve the
routing in `docs/60-tooling/MCP_STACK.md` and run the relevant doctor before
use.

## Known boundaries

- The Codex roles intentionally translate only safe read-heavy specialist
  responsibilities; Claude write-capable agent definitions are not copied
  mechanically.
- The adapter supports parallel workspaces but does not start concurrent
  feature branches without reviewed tasks and ownership.
- Plugin marketplace publication is not automatic.
- Portable plugin installation, portable MCP packaging, MCP 2026-07-28 opt-in, and
  `--approve-for-me` remain disabled by default and require separate human
  approval; runtime compatibility alone does not authorize them.
- Enterprise administrators may constrain plugins, hooks, concurrency,
  permissions, models, network access, or MCP sources beyond repository
  defaults.

## Primary references

- [Codex project instructions](https://learn.chatgpt.com/docs/agent-configuration/agents-md)
- [Codex worktrees](https://learn.chatgpt.com/docs/environments/git-worktrees)
- [Codex project configuration](https://learn.chatgpt.com/docs/config-file/config-advanced)
- [Codex subagents and custom agents](https://learn.chatgpt.com/docs/agent-configuration/subagents)
- [Codex skills](https://learn.chatgpt.com/docs/build-skills)
- [Codex hooks](https://learn.chatgpt.com/docs/hooks)
- [Codex plugins](https://developers.openai.com/plugins/build/plugins)
