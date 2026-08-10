---
name: product-design-router
description: Select the minimum valid product-design phases for substantial UI/UX work. Use for new products, ambiguous features, redesigns, inherited interfaces, agentic experiences, or frontend changes where discovery, strategy, system, implementation, audit, or critique readiness is uncertain.
---

# Product design router

Inspect durable artifacts and the running product before routing.

## Phase order

`discover → user-needs → benchmark → strategize → interaction-design → design-intake → design directions → human approval → design-system → design-tokens → component/Figma translation → implementation → live iteration → responsive/accessibility/system/token audits → performance-ux → design-critic → polish → design-ops → ship`

## Route by evidence

- Ambiguous 0→1 work: start with `discover`.
- Solution-focused requirements: add `user-needs`.
- Unfamiliar or strategically crowded category: add `benchmark`.
- Missing experience principles or differentiation: add `strategize`.
- Missing flows, states, feedback, failure, or recovery: add `interaction-design`.
- Agent/coprocessor behavior: add `agentic-ux`.
- Unclear brand, palette, type, density, geometry, motion, platform, or
  accessibility constraints: add `design-intake` before directions.
- Missing product-specific aesthetic: create comparable directions, obtain
  explicit human approval, then invoke `design-system`.
- Approved direction without reusable encoding: add `design-tokens`.
- Existing mature UI: inspect first; use extraction/documentation externally when available.
- Approved Figma: translate through Figma MCP/Code Connect when installed.
- Substantial design-critical implementation or refinement: add
  `design-engineering-quality`; when Emil Kowalski's suite is installed, route
  `emil-design-eng` as a craft pass and only the smallest relevant specialist.
- Existing implementation refinement: skip upstream phases that remain valid;
  iterate live.
- Motion work: route the exact motion capability only after purpose,
  interruption, performance, and reduced-motion behavior are clear. “Do not
  animate” is a valid result.
- Before release: route applicable audits, `performance-ux`, independent `design-critic`, `polish`, and `design-ops`.

Never rerun a phase merely because a skill exists. State:

1. task type;
2. evidence inspected;
3. phases skipped and why;
4. phases required and expected outputs;
5. approval/evaluation gates.

Do not route canonical design-system or token changes while
`DESIGN_DIRECTIONS.md` remains `Needs approval`.

The project design system is authoritative. Anthropic `frontend-design` is one
optional input during design-direction exploration, never the default aesthetic.
Emil Kowalski's external collection is an optional design-engineering craft
layer, not a replacement for discovery, strategy, approved directions, tokens,
accessibility, Playwright evidence, or the independent evaluator. `prototype`,
`pick-ui-library`, and `review-animations` require explicit human invocation.
