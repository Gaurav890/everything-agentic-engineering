# Installation

## Requirements

- Git
- Node.js 18+
- Claude Code
- Python 3 for included guardrail hooks
- pnpm recommended for app profiles

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

Export them into the shell that launches Claude Code.

Example:

```bash
set -a
source .env
set +a
```

## 3. Bootstrap

```bash
./scripts/bootstrap.sh
```

## 4. Install selected skills

```bash
./scripts/install-skills.sh
```

## 5. Check MCPs

```bash
./scripts/mcp-doctor.sh
```

Inside Claude Code, also use:

```text
/mcp
```

Project-scoped MCPs may require workspace trust/approval.

## 6. Open Obsidian

Open the `docs/` folder as a vault.

## 7. Choose profile

Read `PROFILES.md` and record the decision in:
- `ARCHITECTURE.md`
- an ADR when the choice is significant.

## 8. Build the PRD before large implementation

Use:
- `create-prd`
- `decompose-prd`
- `parallel-plan`
- `loop-engineering`
