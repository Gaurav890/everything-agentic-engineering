---
name: design-tokens
description: Encode approved visual and interaction decisions as DTCG-compatible primitive, semantic, component, theme, layout, density, motion, and agentic-state tokens. Use after a visual thesis exists or when evolving an established token system across web and mobile.
---

# Design tokens

Tokens encode decisions; they do not create the design direction.

Use `packages/design-tokens/tokens/` as canonical source:

1. primitives: raw color, dimension, typography, radius, border, shadow, motion;
2. semantic: intent such as surface, text, action, feedback, focus, layout,
   density, and agent status;
3. component: only stable component-specific contracts;
4. themes: light/dark semantic overrides.

Use DTCG `$type`, `$value`, `$description`, aliases, and `$extensions` for
rationale/decision provenance. Product components normally consume semantic or
component tokens, never raw primitives.

Before adding a token ask whether it is reusable, semantically meaningful, and
different from an existing token. Before changing one assess cross-platform and
theme impact. Document legitimate one-offs as `TOKEN_EXCEPTION` with rationale.
Run `token-audit` after implementation.
