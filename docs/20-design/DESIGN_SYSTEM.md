# Design system

Status: Draft

## Source-of-truth contract

This document explains why the product looks and behaves as it does.
`packages/design-tokens/tokens/` encodes approved reusable values.
Components consume semantic or component tokens; screens compose components.

```text
PRODUCT INTENT
→ RESEARCH + REFERENCES
→ VISUAL THESIS
→ DESIGN SYSTEM
→ DESIGN TOKENS
→ COMPONENTS
→ SCREENS
```

References are ingredients, not templates. Components are structural donors,
not visual identity. Tokens encode approved decisions; they do not create the
direction. If external guidance conflicts with this contract, this contract wins.

## Product and audience

Define the primary users, jobs, context of use, frequency, constraints, and
experience outcomes.

## Reference board and synthesis

For each approved reference, record:

| Reference | Relevant quality | Borrow | Do not borrow |
|---|---|---|---|
| | | interaction/layout principle | brand, assets, or wholesale aesthetic |

Document the synthesis: how the selected principles become an original,
product-specific direction.

## Visual thesis

What should this product feel like, and why is that appropriate for the user and task?

Define product personality, differentiation, density, composition, and at least
one signature interaction or experience where appropriate.

## Design principles

1. Replace with product-specific principles.
2. Avoid generic slogans.

## Token contract

Canonical tokens use DTCG-compatible JSON under `packages/design-tokens/tokens/`.

- Primitive tokens hold raw values.
- Semantic tokens express intent.
- Component tokens exist only for stable component contracts.
- Theme files map semantics for light and dark modes.
- Product code normally consumes semantic or component tokens, not primitives.
- Repeated raw visual values require a token or a documented `TOKEN_EXCEPTION`.
- Foundational decisions should include rationale or a design-decision ID.

## Color and themes

Define canvas, surfaces, text, borders, actions, feedback, data visualization,
focus, selection, and agent-state semantics for light/dark modes.

## Typography

Define display, heading, body, label, caption, numeric, and mono roles with
family, size, weight, line height, tracking, wrapping, and responsive behavior.

## Spacing, density, and layout

Define spacing rhythm, compact/default/comfortable density, content widths,
grids, gutters, navigation dimensions, and breakpoint behavior.

## Radius, border, elevation

## Iconography

## Motion

Respect `prefers-reduced-motion`.

## Interaction

Define flows, feedback, validation, selection, interruption, undo, recovery, and
progressive disclosure before specifying decorative states.

## Agentic UX

When applicable, define planning, thinking, streaming, tool-running, queued,
approval, interrupted, partial, failed, retry, complete, provenance, memory,
handoff, and background-work behavior. Users must understand status, control,
consequences, and recovery.

## Responsive strategy

## Accessibility

## Required states

Every important flow must define:
- loading,
- empty,
- sparse,
- dense,
- invalid,
- error,
- disabled,
- success.

## Anti-patterns

List product-specific patterns to avoid.

Examples:
- gratuitous gradients,
- excessive glassmorphism,
- dashboard cards with no information hierarchy,
- meaningless animation,
- tiny low-contrast text,
- icon-only controls without accessible labels.

## Verification

Important UI must be inspected in the running application with Playwright or
equivalent evidence at meaningful breakpoints and states. Responsive,
accessibility, token, system, and performance audits run before an independent
critic. Record material decisions in `DESIGN_DECISIONS.md`.
