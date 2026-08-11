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
requires confirmation before writing.

It also makes non-selection explicit. If a project does not use mobile,
`mobile-expo`, the mobile agent, and React Native guidance remain inactive:
agents do not route work to them and they are not project requirements. Their
template files remain in the starter so profile changes stay reversible.
Removing cataloged files is a separate, explicit cleanup decision—never an
initializer side effect.

Start from a preset when the shape is familiar:

```bash
./scripts/init-project.sh --list-presets
./scripts/init-project.sh --name my-saas --preset web-supabase --dry-run
```

Or select capabilities directly:

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

Every preview shows:

- active profiles and why they are active;
- inactive profiles;
- active capabilities;
- inactive capabilities retained in the starter;
- external skills, MCPs, and backends that require separate review.

Presets and manual selectors cannot be mixed. This prevents a convenient
starting point from silently accumulating contradictory choices.

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

## Specialist contracts

The core profile includes the local specialist broker, not every upstream
agent. `./agentic task plan` routes contracts whose triggers and profile gates
match the task. A web-only project never receives mobile-only routing; an app
without design-critical work does not receive the design finish gate.

```bash
./agentic agents list
./agentic agents recommend T-009
./agentic agents doctor
```

Optional `activate` and `deactivate` operations update only the `specialists`
array in `.agentic/project.json`. They do not change profiles, install external
code, or grant tools and permissions.

## Available profiles

Choose only what the product genuinely needs.

## Presets

| Preset | Intended starting point |
|---|---|
| `core` | Harness and durable context only |
| `web` | Next.js plus design-critical workflow |
| `web-research` | Web plus current research/crawling |
| `web-supabase` | Web plus design workflow and Supabase |
| `mobile` | Expo plus design-critical workflow |
| `mobile-research` | Mobile plus current research/crawling |
| `full-stack` | Web, mobile, design, research, and Supabase |
| `research` | Research/crawling harness without an app surface |

## Web + Supabase composition

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
- when `design-critical` is active, `./agentic setup skills` installs Emil
  Kowalski's reviewed collection for Claude Code and Codex; route it through
  `design-engineering-quality`, never as one bundle
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
