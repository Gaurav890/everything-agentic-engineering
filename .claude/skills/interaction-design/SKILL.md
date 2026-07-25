---
name: interaction-design
description: Define flows, states, transitions, feedback, failure, recovery, and control before screen styling. Use for new workflows, complex forms, multi-step tasks, destructive operations, asynchronous work, or interfaces whose UX logic is not yet explicit.
---

# Interaction design

Model each critical journey as:

`goal → trigger → system response → intermediate states → feedback → completion`

Also define cancellation, undo, validation, empty/loading, timeout, partial
failure, permission denial, recovery, and exit. Specify state ownership,
persistence, keyboard/touch behavior, and accessibility consequences.

For AI or automation, invoke `agentic-ux`. Validate the model against acceptance
criteria before visual design. UI polish cannot repair broken interaction logic.
