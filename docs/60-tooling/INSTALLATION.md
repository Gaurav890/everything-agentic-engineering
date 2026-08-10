# Installation

Use `./agentic --help` as the command index. The implementation scripts remain
available for compatibility, but the unified interface is the supported path
for new contributors and agents.

## Requirements

- Git
- Node.js 18+
- Claude Code and/or Codex
- Python 3 for included guardrail hooks
- pnpm recommended for app profiles

Claude Code 2.1.225+ and Codex 0.147.0+ are the recommended runtime baselines.
The repository doctor reports an older or missing runtime without upgrading it
or enabling optional capabilities.

## 1. Clone/copy

```bash
git clone <your-repo>
cd <your-repo>
```

## 2. Secrets

```bash
cp .env.example .env
```

Add:
- `PERPLEXITY_API_KEY`
- `FIRECRAWL_API_KEY`

Export them only into the shell that launches an approved MCP-enabled runtime.

Example:

```bash
set -a
source .env
set +a
```

## 3. Bootstrap

```bash
./agentic setup bootstrap
```

## 4. Install selected skills

```bash
./agentic setup skills
```

The project-local skills require no Codex copy step. Codex discovers the same
catalog through `.agents/skills`.

## 5. Check MCPs

```bash
./agentic doctor mcp
```

Inside Claude Code, also use:

```text
/mcp
```

Project-scoped MCPs may require workspace trust/approval.

The Codex adapter intentionally does not translate `.mcp.json` into executable
project configuration. Read `CODEX.md` and configure only the MCP capabilities
required by the selected profile after reviewing their code, credentials, and
permissions.

## 6. Check the selected coding-agent runtime

For either adapter:

```bash
./agentic doctor runtime
```

Use `--strict` for a managed developer image or release validation and `--json`
for inventory tooling. The doctor is read-only.

For Codex:

```bash
./agentic doctor codex
```

Review project hooks with `/hooks` before trusting them.

## 7. Open Obsidian

Open the `docs/` folder as a vault.

## 8. Choose profile

Read `PROFILES.md` and record the decision in:
- `ARCHITECTURE.md`
- an ADR when the choice is significant.

## 9. Build the PRD before large implementation

Use:
- `create-prd`
- `decompose-prd`
- `parallel-plan`
- `loop-engineering`
