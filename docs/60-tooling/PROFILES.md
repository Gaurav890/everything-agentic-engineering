# Project profiles

Profiles make capability selection deterministic. The catalog can describe web,
mobile, backend, research, and design tooling without activating all of it.

The source of truth is `.agentic/project.json`.

```bash
./scripts/init-project.sh
./scripts/profile-resolve.sh
./scripts/profile-doctor.sh
./scripts/profile-preview.sh web-next,design-critical,research-enabled
./scripts/profile-select.sh web-next,design-critical,research-enabled --yes
```

Selection changes only the manifest. It never installs packages, enables MCPs,
or removes files. The doctor reports missing/external resources and
present-but-inactive resources for review.

The guided initializer asks plain-language questions about web, mobile, backend,
design importance, research, and agentic UX. It previews the exact manifest and
requires confirmation before writing. In non-interactive environments:

```bash
./scripts/init-project.sh \
  --name my-product \
  --web \
  --design \
  --research \
  --backend supabase \
  --dry-run
```

Replace `--dry-run` with `--yes` only after reviewing the proposal.

```text
PROJECT MANIFEST
→ PROFILE DEPENDENCIES
→ REQUIRED RESOURCE UNION
→ CONFLICT CHECK
→ DETECTION / DRIFT REPORT
→ CHANGE PREVIEW
→ EXPLICIT MANIFEST UPDATE
```

Resources shared by several profiles remain required until no selected profile
references them. Optional template surfaces may remain cataloged without being
active.

## Available profiles

Choose only what the product genuinely needs.

## web-next-supabase

Recommended default for many full-stack web products.

Suggested:
- Next.js
- TypeScript
- Tailwind
- shadcn/ui if useful
- Supabase
- Playwright
- Vercel

External skills:
- route product-design phases through `product-design-router`
- install discovery, strategy, taste, component, or Figma specialists only when routed
- use react-best-practices for engineering
- use web-design-guidelines as one audit input
- use frontend-design only as optional supplementary direction intelligence

## mobile-expo

Suggested:
- Expo
- React Native
- TypeScript
- Expo Router
- official Expo skills/plugin
- react-native-guidelines

Share domain types and API contracts with web when helpful. Do not force UI sharing where native experience would suffer.

## realtime-convex

Suggested when real-time state and fast reactive product iteration are central.

Choose Convex as the default data backend for that project rather than mixing it with Supabase without an ADR.

## research-heavy

Core:
- Perplexity MCP
- Firecrawl MCP
- Playwright MCP
- research-ledger skill

Use source ledgers and keep raw crawl output out of the main context.

## full-stack

Combine:
- web or mobile frontend,
- one primary backend,
- research stack,
- security gate,
- evaluator loop.

Keep agent count proportional to independent workstreams.

`full-stack` is a composition concept, not a profile id. Select the specific
web/mobile/backend/design/research profiles instead.

## Safety

- Unknown profiles fail closed.
- Conflicting backends fail validation.
- Profile selection changes only `.agentic/project.json`.
- External skills and MCPs remain separately permissioned.
- Cleanup is advisory in this version; no automatic deletion exists.
- User-owned files are never classified as safe to remove by inference alone.
