---
name: design-system
description: Establish or revise a product-specific design contract after discovery, strategy, interaction design, and design-direction selection. Use for substantial new UI, redesigns, or system changes that need a coherent visual thesis, reference synthesis, component language, motion, accessibility, responsive behavior, and required states.
---

# Design system

## Establish the direction

Start from approved product intent, user needs, UX strategy, interaction model,
`DESIGN_BRIEF.md`, and an explicitly approved direction. If those inputs are missing, return to
`product-design-router`; do not hide upstream ambiguity with styling.

Synthesize 3–7 appropriate references when the scope warrants research.
Record what each reference contributes and explicitly reject wholesale copying.

Define:

- audience, product personality, visual thesis, and differentiation;
- hierarchy, information density, composition, typography, color, geometry;
- content voice, interaction principles, signature behaviors, and motion;
- responsive, accessibility, platform, and agentic-experience rules;
- required normal, edge, failure, recovery, and trust states.

Avoid empty adjectives such as “clean, modern, minimal.” Make decisions specific
enough that another designer or agent could distinguish this product from a
framework demo.

## Resource roles

- Refero, real category-leading products, and brand material: visual research.
- UI UX Pro Max or equivalent: broad exploration and alternative generation.
- 21st.dev, Aceternity, shadcn registries: component/interaction discovery.
- Taste Skill or Impeccable: anti-slop critique and refinement.
- Emil Kowalski `emil-design-eng`: high-craft implementation/refinement when
  installed; specialist motion, prototyping, library, and Sonner skills route
  only when their exact trigger is active.
- Motion references: interaction inspiration when motion serves comprehension.
- Anthropic `frontend-design`: optional supplementary design intelligence only.
- Vercel engineering/audit skills: implementation quality, not visual identity.

The project brief and `docs/20-design/DESIGN_SYSTEM.md` always win.
Emil's suite does not choose the product aesthetic, authorize a dependency, or
make motion mandatory. Use `design-engineering-quality` to select the minimum
capability and preserve explicit-only gates.

## Structural-donor rule

External components may donate interaction structure, accessibility behavior,
layout ideas, or implementation techniques. Replace their copy, tokens, fonts,
colors, geometry, effects, and branding with the product’s approved system.

## Tokenization boundary

Complete the visual direction before invoking `design-tokens`. Tokens encode
approved reusable decisions; they do not choose those decisions.

For color, define semantic roles and foreground/background relationships across
every required mode. A palette is not approved merely because its swatches look
attractive. Record contrast evidence and how brand colors behave in actions,
surfaces, focus, feedback, data visualization, and agent states.

## Required output

Update `docs/20-design/DESIGN_SYSTEM.md` with the reference ledger, synthesis,
visual thesis, system contract, interaction/agentic states, anti-patterns, and
decision provenance. Do not approve implementation from source alone; preserve
Playwright evidence and independent critique as later phases.
