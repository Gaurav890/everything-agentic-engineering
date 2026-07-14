---
name: design-system
description: Establish and maintain a product-specific design contract covering visual thesis, tokens, typography, spacing, interaction, motion, accessibility, responsive behavior, and required UI states before substantial frontend work.
---

# Design system

## First principle

A UI needs a point of view. Do not begin with a component library and call that the design.

Define:
- product personality,
- audience,
- visual thesis,
- density,
- tone,
- information hierarchy,
- signature interaction.

## Required contract

Update `docs/20-design/DESIGN_SYSTEM.md` with:

1. Visual thesis
2. Design principles
3. Color tokens and semantic roles
4. Typography scale and usage
5. Spacing and layout grid
6. Radius, border, elevation
7. Iconography
8. Motion and reduced-motion behavior
9. Component behavior
10. Content/copy conventions
11. Responsive strategy
12. Accessibility
13. Required states:
   - loading
   - empty
   - sparse
   - dense
   - error
   - disabled
   - success
14. Anti-patterns

## Build and critique

Creation:
- use Anthropic `frontend-design` when installed.

Engineering:
- use Vercel `react-best-practices` for React/Next.js.

Audit:
- use Vercel `web-design-guidelines`.

Evidence:
- inspect the running app with Playwright.
- use a separate evaluator from the builder.
