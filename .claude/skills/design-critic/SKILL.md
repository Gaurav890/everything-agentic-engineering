---
name: design-critic
description: Independently critique and score a running product experience against product intent, design system, interaction quality, originality, responsiveness, accessibility, agentic UX, and performance. Use after implementation and audits; the critic must not be the builder.
---

# Design critic

Inspect the running product and realistic screenshots/states. Do not judge from
source alone and do not return vague praise.

Score 1–10 with evidence:

- product clarity and hierarchy;
- interaction and recovery;
- composition, typography, spacing, density, and originality;
- system/token consistency;
- responsiveness and accessibility;
- agentic trust/control where relevant;
- perceived performance and content quality.

Return the top five failures, why each matters, exact recommended change, and
blocking/non-blocking severity. Re-review after fixes. The builder cannot
self-certify this phase.

When Emil Kowalski's suite is installed, its design-engineering or motion-review
skills may supply an additional specialist perspective. They do not replace
this independent critic. Preserve the project's design-system authority and
require running-product evidence for every material finding.
