# T-050 — Research-to-build journey evidence

Status: implementation and deterministic checks pass. Independent product,
design, security, integration, human task review, and newcomer measurement
remain separate.

## Observed gap

The repository contained strong engineering and design machinery, but its first
screen read like a toolbox. Perplexity was documented deep in the repository,
the research decision was not part of guided creation, and a newcomer could not
see how research, product definition, design, implementation, and evidence fit
together.

## Verified locally

- The public README leads with one outcome-first promise and the six-stage
  research → product → design → build → verify → review journey.
- Guided creation offers Perplexity-first current research or an explicit skip
  for relevant product profiles.
- Selecting research persists `research-enabled` and
  `research_enabled: true`, creates `docs/10-product/RESEARCH.md`, and routes the
  first continuation through `./agentic start` before design.
- The generated research contract distinguishes Perplexity discovery, official
  primary sources, authorized Firecrawl extraction, Playwright interaction, and
  a manual fallback.
- Selecting research does not collect an API key, install or activate a plugin
  or MCP server, run network research during generation, or add an MCP command;
  the fresh project's `.mcp.json` remained `{"mcpServers": {}}`.
- `./agentic journey` reports all six stages, status, and the exact next action
  in text and JSON without mutating project state.
- Sixty-five focused generator, handoff, next-action, journey, and command-router
  tests pass.
- A fresh research-enabled product generated successfully in a temporary
  directory and reported research as selected with `./agentic start` next.
- The complete ten-stage repository verification passes, including task,
  security-hook, token, documentation-link, generated-project, package, and
  evidence-bundle checks.

## UI evidence

Not applicable. This task changes CLI questions, generated Markdown/contracts,
routing, and public documentation. It does not change an application UI or an
approved visual baseline; reusing older screenshots would not prove this flow.

## Review boundary

Automated checks prove deterministic routing and safety constraints, not that
the promise is persuasive, the design outcome is world-class, the source
synthesis is insightful, or a newcomer succeeds unaided. Those claims require
independent product/design review and the consented P1–P5 newcomer pilot.

No external capability, credential, model, provider, plugin, MCP server,
network session, deployment, production service, approval, or merge authority
was installed, enabled, or exercised by this task.
