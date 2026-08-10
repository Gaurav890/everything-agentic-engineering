---
name: design-engineering-quality
description: Route substantial design-critical web UI through the smallest relevant Emil Kowalski design-engineering capability. Use during implementation, live iteration, motion work, UI-library selection, and polish when the external suite is installed; preserve the approved project design system, tokens, accessibility, evidence, and independent evaluation.
---

# Design engineering quality

Use this contract after product intent, interaction logic, and an approved design
direction exist. It adds frontend craft; it does not invent product strategy or
visual identity.

## Authority

Read the approved design brief, directions, `DESIGN_SYSTEM.md`, token contract,
and task criteria first. The project contract wins every conflict. External
skills are perspectives, not authority, and their output still requires normal
review and verification.

## Route the smallest capability

Do not invoke the entire collection. Select one primary capability and at most
one focused specialist unless the human explicitly requests broader exploration.

| Need | Route when installed |
|---|---|
| Substantial design-critical UI implementation or refinement | `emil-design-eng` |
| Implement one justified animation | `animate` |
| Strictly review animation code or a motion-heavy diff | `review-animations` — explicit only |
| Audit existing animation quality and plan improvements | `improve-animations` |
| Find a few missing purposeful motion opportunities | `find-animation-opportunities` |
| Name or classify a motion pattern | `animation-vocabulary` |
| Approved tactile, gesture, spring, material, or Apple-platform direction | `apple-design` |
| Compare multiple live UI variants | `prototype` — explicit only; human chooses |
| Select a UI dependency | `pick-ui-library` — explicit only; inspect installed capabilities first |
| Sonner setup or troubleshooting | `ask-sonner` — only when Sonner is relevant |

If the external collection is unavailable, follow this repository's existing
design-system, interaction, frontend-quality, motion, and critique contracts.
Never block ordinary UI work merely because an optional skill is not installed.

## Anti-slop craft gate

For substantial design-critical web UI, use `emil-design-eng` when installed as
a craft pass during implementation or refinement. Require specific findings
about hierarchy, typography, spacing, density, composition, interaction,
content, restraint, motion, accessibility, and performance. Reject generic
approval such as “looks clean and modern.”

This pass does not replace discovery, user needs, UX strategy, design intake,
human direction approval, design tokens, responsive/accessibility audits,
Playwright evidence, or the independent final critic.

## Motion gate

Before adding motion, answer:

1. What user or system change needs explanation?
2. Does motion communicate causality, continuity, feedback, hierarchy, or state?
3. Is a cheaper CSS/native transition sufficient?
4. What happens when the interaction is interrupted or reversed?
5. What is the reduced-motion behavior?

If the answers are weak, do not animate. Motion is never required merely to make
an interface feel premium. Prefer transform and opacity, preserve input
responsiveness, and verify the running behavior rather than reading code alone.

## Completion

Return the capability selected, why it was the minimum sufficient route, the
specific changes or findings, running-product evidence, reduced-motion and
accessibility results when relevant, and remaining compromises. The builder may
not self-certify final quality.
