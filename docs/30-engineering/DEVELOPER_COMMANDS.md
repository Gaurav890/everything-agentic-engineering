# Developer commands

The starter's supported workflow interface is `./agentic`:

```bash
./agentic --help
./agentic commands
./agentic verify full
```

The registry lives at `.agentic/commands.json`. Direct shell-script entry
points remain compatible, but new contributor documentation should use the
unified interface.

## Web projects

From the generated project root, use `pnpm install --frozen-lockfile`, then
`./agentic next`. The generated development command is `pnpm dev`; in the
starter checkout the equivalent is `pnpm dev:web`.

| Command | Scope |
|---|---|
| `./agentic verify quick` or `full` | Repository checks and available package lint/type/unit checks; no build/browser/visual execution |
| `./agentic verify web` | Requires local dependencies and Chromium, then runs repository checks, build, interaction, and automated accessibility tests |
| `./agentic verify visual` | Builds and compares existing platform-specific screenshots; never creates or updates baselines |

The explicit browser download is `pnpm --dir apps/web install:browsers`.
Neither verification mode downloads tools. The browser suite owns local port
3012; a conflicting server must be stopped separately.

Add new acceptance tests as features change. Follow the
[first-project guide](../60-tooling/FIRST_PROJECT.md) for visual candidates,
independent evaluation, human approval, and post-merge continuation. Native
device tests and production integration checks require their own implementation.
