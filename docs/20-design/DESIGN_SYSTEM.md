# Design system

Status: Draft

## Source-of-truth contract

This document explains why the product looks and behaves as it does.
`packages/design-tokens/tokens/` encodes approved reusable values.
Components consume semantic or component tokens; screens compose components.
`DESIGN_BRIEF.md` records constraints and `DESIGN_DIRECTIONS.md` records the
explicitly approved direction that authorizes this contract.

```text
PRODUCT INTENT
→ RESEARCH + REFERENCES
→ DESIGN INTAKE
→ COMPARED DIRECTIONS + HUMAN APPROVAL
→ VISUAL THESIS
→ DESIGN SYSTEM
→ DESIGN TOKENS
→ COMPONENTS
→ SCREENS
```

References are ingredients, not templates. Components are structural donors,
not visual identity. Tokens encode approved decisions; they do not create the
direction. If external guidance conflicts with this contract, this contract wins.

## Experience architecture contract

`.agentic/experience.json` owns the product name, selected archetype, audience,
promise, starting visual character, and whether the checkout is the multi-
archetype reference lab. The three archetypes are different information and
interaction systems—not themes:

- `portfolio`: identity, selected work, evidence, and working philosophy;
- `product`: promise, outcome surface, proof, and operating rhythm;
- `agentic-product`: objective, execution evidence, human decision gate,
  consequence, recovery, and control.

Changing color or tokens never changes this architecture. Query-string
archetype previews are allowed only in the starter's explicit reference lab.
Generated products expose and test only their selected archetype.

Do not replace `Status: Draft` until the direction decision includes an
approver, date, evidence reviewed, and design-decision ID.

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

The three candidate packs live in `.agentic/design-directions.json`. They use
DTCG `$type`/`$value` objects but remain non-canonical exploration until
`.agentic/design.json` records human approval. `./agentic tokens build` then
compiles only the approved direction into `generated/direction.css`. Resetting a
direction removes the override; it never guesses a replacement.

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

Record required brand colors, forbidden hues, neutral temperature, expression
level, and foreground/background relationships. Theme modes keep the same
semantic names and types while values may change. Component tokens reference
mode-independent semantic roles, never a specific light/dark namespace.

Every approved color direction must include realistic previews and contrast
evidence for primary/secondary text, interactive controls, and focus indicators.

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

Motion must explain causality, continuity, feedback, hierarchy, or state. Record
its purpose, property choice, duration/easing, interruption/reversal behavior,
performance constraints, and reduced-motion result. Prefer the least expensive
implementation that communicates the change. “Do not animate” is an approved
outcome when motion would be decorative or distracting.

When Emil Kowalski's external design-engineering suite is installed, use the
local `design-engineering-quality` contract to route one relevant craft or
motion capability. The suite does not define this product's visual identity,
tokens, or interaction model.

## Interaction

Define flows, feedback, validation, selection, interruption, undo, recovery, and
progressive disclosure before specifying decorative states.

## Agentic UX

When applicable, define planning, thinking, streaming, tool-running, queued,
approval, interrupted, partial, failed, retry, complete, provenance, memory,
handoff, and background-work behavior. Users must understand status, control,
consequences, and recovery.

Do not label a mock as “live,” “verified,” or “human controlled.” Demonstrations
must identify themselves. Review gates disclose evidence completeness, lock
approval while required proof is missing, explain the consequence, and provide
working approve, reject, cancel, and retry paths.

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
- animation added only to make the interface feel “premium”.
- copied motion or component-library aesthetics that bypass project tokens.

## Verification

Require token schema/alias validation, light-dark semantic parity, contrast
checks, generated web/native output, the generated token specimen, running UI
screenshots, and independent evaluation.

## Redesign and migration

For a visual redesign, capture baseline evidence before changing tokens. Update
the smallest correct layer: primitives for raw scales, semantics for system-wide
meaning, and component tokens only for stable component contracts. Deprecate and
document public token renames. Token changes do not silently redefine product
flows, information architecture, content, or interaction behavior.

Important UI must be inspected in the running application with Playwright or
equivalent evidence at meaningful breakpoints and states. Responsive,
accessibility, token, system, and performance audits run before an independent
critic. Record material decisions in `DESIGN_DECISIONS.md`.
