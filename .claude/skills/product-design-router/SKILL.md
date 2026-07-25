---
name: product-design-router
description: Select the minimum valid product-design phases for substantial UI/UX work. Use for new products, ambiguous features, redesigns, inherited interfaces, agentic experiences, or frontend changes where discovery, strategy, system, implementation, audit, or critique readiness is uncertain.
---

# Product design router

Inspect durable artifacts and the running product before routing.

## Phase order

`discover → user-needs → benchmark → strategize → interaction-design → design directions → design-system → design-tokens → component/Figma translation → implementation → live iteration → responsive/accessibility/system/token audits → performance-ux → design-critic → polish → design-ops → ship`

## Route by evidence

- Ambiguous 0→1 work: start with `discover`.
- Solution-focused requirements: add `user-needs`.
- Unfamiliar or strategically crowded category: add `benchmark`.
- Missing experience principles or differentiation: add `strategize`.
- Missing flows, states, feedback, failure, or recovery: add `interaction-design`.
- Agent/coprocessor behavior: add `agentic-ux`.
- Missing product-specific aesthetic: explore directions, then `design-system`.
- Approved direction without reusable encoding: add `design-tokens`.
- Existing mature UI: inspect first; use extraction/documentation externally when available.
- Approved Figma: translate through Figma MCP/Code Connect when installed.
- Existing implementation refinement: skip upstream phases that remain valid; iterate live.
- Before release: route applicable audits, `performance-ux`, independent `design-critic`, `polish`, and `design-ops`.

Never rerun a phase merely because a skill exists. State:

1. task type;
2. evidence inspected;
3. phases skipped and why;
4. phases required and expected outputs;
5. approval/evaluation gates.

The project design system is authoritative. Anthropic `frontend-design` is one
optional input during design-direction exploration, never the default aesthetic.
