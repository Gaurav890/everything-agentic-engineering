# Signalroom

Signalroom is the reference product for Everything Agentic Engineering: a
human-first operations console for supervising long-running AI-agent work.

It demonstrates:

- phase-routed discovery, strategy, interaction, and visual design;
- product-specific design rather than a framework or vendor aesthetic;
- agent planning, execution, approval, interruption, recovery, and artifacts;
- repository-generated design tokens;
- desktop and mobile layouts;
- normal, loading, empty, and error states;
- interaction and accessibility tests;
- machine-checkable evidence.

## Run

From the repository root:

```bash
pnpm install
pnpm dev:showcase
```

## Verify

```bash
pnpm build
pnpm test
cd apps/showcase
pnpm install:browsers
pnpm test:e2e
```

The product brief, benchmark, user needs, strategy, and interaction model live
under `docs/80-showcase/`. The design contract is `DESIGN.md`.
