# Skills strategy

For exact source URLs, invocation notes, timing, rationale, and the original
assessments, read [`PRODUCT_DESIGN_RESOURCES.md`](PRODUCT_DESIGN_RESOURCES.md).

## Principle

Use a small phase-based system, not a pile of overlapping aesthetic prompts.
Local skills own routing, contracts, durable outputs, and fallbacks. Third-party
skills remain externally installed and are invoked only for the phase they serve.

`product-design-router` selects the minimum phases required by evidence:

```text
DISCOVERY
→ USER NEEDS
→ BENCHMARK
→ UX STRATEGY
→ INTERACTION DESIGN
→ DESIGN INTAKE
→ DESIGN DIRECTIONS
→ HUMAN APPROVAL
→ DESIGN SYSTEM
→ DESIGN TOKENS
→ COMPONENT / FIGMA TRANSLATION
→ IMPLEMENTATION
→ LIVE ITERATION
→ RESPONSIVE / ACCESSIBILITY / SYSTEM / TOKEN AUDITS
→ PERFORMANCE
→ INDEPENDENT CRITIQUE
→ POLISH
→ DESIGN OPS
→ SHIP
```

Do not rerun phases whose outputs exist, remain valid, and match the current task.

## Product-design routing

| Phase | Local contract | External capability when installed |
|---|---|---|
| Discovery | `discover` | Owl Listener discover; Impeccable Shape |
| User needs | `user-needs` | Layers user-needs |
| Competitive landscape | `benchmark` | Owl Listener UX strategy |
| UX strategy | `strategize` | Owl Listener strategize |
| Interaction | `interaction-design`, `agentic-ux` | cuellarfr interaction-design |
| Design intake | `design-intake` | Existing brand/Figma inputs and user constraints |
| Design directions | `design-system` | UI UX Pro Max; Refero; real products; optional Anthropic frontend-design |
| System documentation | `design-system` | Impeccable Document; extract-design-system for existing products |
| Tokens | `design-tokens` | tailwind-design-system when Tailwind is active |
| Components | project design system | shadcn registry/MCP; 21st.dev; Aceternity |
| Design-to-code | project design system | Figma MCP Implement Design; Code Connect |
| Live iteration | frontend agent | Impeccable Live |
| Audits | `responsive-audit`, `accessibility-audit`, `design-system-audit`, `token-audit` | relevant specialist audit skills |
| Engineering | framework rules | Vercel React/Next.js or React Native guidance |
| Performance | `performance-ux` | Impeccable Optimize |
| Critique | `design-critic` | Impeccable Critique; Taste Skill |
| Polish | `polish` | Impeccable Polish |
| Delivery | `design-ops` | cuellarfr design-ops |
| Evidence | repo verification contract | Playwright |

## Authority rules

- The product context and approved brief define intent.
- `DESIGN_DIRECTIONS.md` records the human-approved direction.
- `docs/20-design/DESIGN_SYSTEM.md` defines the product experience.
- `packages/design-tokens/tokens/` encodes approved reusable values.
- References are ingredients, not templates.
- Imported components are structural donors.
- Anthropic `frontend-design` is optional supplementary design intelligence. It
  is never the default aesthetic and may be skipped.
- Vercel engineering and audit guidance improves implementation quality; it does
  not define visual identity.
- The project design system wins every conflict.

## Existing-product routing

For an inherited or mature product, inspect the running implementation before
proposing a new system. Use external extraction/documentation skills when
installed, then audit drift and plan migration. Do not overwrite a coherent
existing language with starter defaults.

## Install and trust policy

Install an external skill only when its phase is active, its source is trusted,
and it does not conflict with an already selected specialist. Review third-party
shell hooks and code before enabling them.

Avoid:

- bulk skill dumps;
- several taste skills loaded simultaneously;
- copying external skill implementations into this repository without need;
- using a component registry as art direction;
- treating automated accessibility or performance output as complete evidence.

## Core engineering skills

The non-design local skills remain:

- `create-prd`
- `decompose-prd`
- `context-handoff`
- `research-ledger`
- `parallel-plan`
- `loop-engineering`
- `security-gate`
- `self-improvement-loop`

Superpowers and Expo tooling remain optional external workflow/platform layers.
