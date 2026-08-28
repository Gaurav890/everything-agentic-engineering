---
name: design-intake
description: Collect the minimum product-specific visual constraints, generate comparable design directions, and obtain explicit approval before design-system or token changes. Use for design-critical greenfield products, major redesigns, inherited brands, theme creation, or substantial UI work where palette, typography, density, geometry, motion, accessibility, platform, or brand authority is unclear.
---

# Design intake

Do not ask the user to design the token system. Gather intent and constraints,
then translate them into reviewable directions.

## Route the intake

- Existing brand: inventory exact assets, licensed fonts, colors, Figma sources,
  restrictions, and the authority that may approve changes. Preserve exact brand
  inputs; do not approximate them from screenshots.
- Greenfield design-critical product: collect preferences, research references,
  and produce comparable materially different directions. Two or three per
  round is a starting point, not a catalog limit.
- Redesign: inspect the running product and current tokens first. Separate what
  must remain compatible from what may change, and capture baseline evidence.
- Design is not a competitive advantage: use one restrained accessible baseline;
  skip expressive questions and unnecessary alternatives.

Read `.agentic/project.json` and ask only about active platforms. Do not ask
mobile questions for a web-only product or require a Figma workflow when Figma
is not part of the project.

## Interview adaptively

Ask one to three short groups at a time. Do not make every question mandatory.
Resolve, in this order:

1. **Authority and mode** — existing brand, greenfield, or redesign; approver;
   fixed assets and non-negotiable constraints.
2. **Experience intent** — audience, task, context, desired feelings, density,
   and qualities the product must avoid.
3. **Color constraints** — exact existing colors or preferred/forbidden hue
   families, neutral temperature, restrained/expressive use, data visualization,
   and required light/dark/high-contrast modes.
4. **Type and composition** — licensed fonts, reading/data needs, typography
   personality, spacing density, geometry, elevation, and content width.
5. **Interaction and motion** — input methods, motion intensity, reduced motion,
   signature behavior, and agentic states when applicable.
6. **Accessibility and platform** — WCAG target, localization, color-vision,
   touch/keyboard, and active web/native surfaces.
7. **References** — examples the user values and the exact quality to learn from;
   record what must not be copied.

If the user has no exact color preference, do not force a hex choice. Generate
coherent proposals from product intent and show them in context.

## Create durable intake

Write facts, constraints, preferences, assumptions, open questions, and approval
authority to `docs/20-design/DESIGN_BRIEF.md`. Never present an assumption as an
approved decision.

## Generate comparable directions

For design-critical work, create a reviewable set of coherent directions in
`docs/20-design/DESIGN_DIRECTIONS.md`. Each direction must include:

- a name and product-specific thesis;
- palette roles for all requested modes, not swatches alone;
- typography, density, geometry, elevation, icon, and motion choices;
- representative normal, loading, empty, error, focus, and agent states;
- realistic rendered previews at relevant breakpoints;
- WCAG contrast evidence for required text and UI pairs;
- reference provenance, tradeoffs, risks, and implementation cost.

Alternatives must differ in meaningful system decisions, not only accent color.
References are inputs to synthesis; do not clone a product or library aesthetic.

Generated projects use `project-onboarding` and an open-ended candidate catalog.
Register actual local preview routes through `./agentic design propose`; do not
force the bundled reference styles on custom or existing-brand projects. List
preview code and its shared appearance-affecting dependencies/assets so approval
fingerprints detect drift. Record complete intake and reviewed screenshot paths
before approval; see `docs/60-tooling/PROJECT_ONBOARDING.md`.

## Approval gate

Before invoking `design-system` or editing canonical tokens, record:

- selected direction or explicitly approved synthesis;
- approver and date;
- accepted compromises;
- decisions still open;
- evidence reviewed.

Status must remain `Draft` or `Needs approval` until a human approves the
direction. Silence, an agent recommendation, or an attractive screenshot is not
approval. After approval, invoke `design-system`, then `design-tokens`.

## Redesign contract

For redesigns, preserve baseline screenshots and audit existing token usage.
Classify each proposed change as primitive, semantic, component, or structural.
Token changes may retheme an interface; they do not substitute for changes to
information architecture, interaction, content, or component behavior.

Do not overwrite a coherent existing system with starter defaults. Use token
deprecation and a migration plan when consumers cannot change atomically.
