---
name: token-audit
description: Audit implementation and token sources for raw visual values, arbitrary utilities, duplicate semantics, invalid aliases, missing theme coverage, unused tokens, and undocumented exceptions. Use after tokenized UI changes or before system-scale release.
---

# Token audit

Inspect token JSON and product code for:

- raw colors, spacing, radii, shadows, borders, z-index, and durations;
- direct primitive consumption where semantic intent exists;
- duplicate or ambiguous semantics;
- invalid aliases and missing light/dark mappings;
- component tokens that should be semantic—or needless one-off tokens;
- unused/dead tokens and inconsistent naming;
- undocumented `TOKEN_EXCEPTION` values.

Classify findings as defect, migration, system decision, or valid exception.
Do not force geometric/canvas values into reusable tokens when they are truly
one-off. Report file, value, recommended token/action, and risk.
