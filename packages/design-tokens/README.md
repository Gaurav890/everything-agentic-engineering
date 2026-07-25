# Design tokens

Canonical, platform-neutral design decisions live under `tokens/` in a
DTCG-compatible shape. The example values are an intentionally neutral scaffold,
not a product aesthetic.

```text
tokens/
├── primitives/   raw reusable values
├── semantic/     intent-based aliases
├── component/    stable component contracts only
└── themes/       light/dark semantic mappings
```

Use this order:

```text
approved visual thesis
→ primitive palette/scales
→ semantic intent
→ selective component contracts
→ generated platform outputs
```

Applications should consume semantic or component tokens. Replace scaffold
values only after the project design direction is approved. Keep rationale and
design-decision IDs in `$extensions.com.everything-agentic`.

## Generate platform outputs

```bash
./scripts/build-design-tokens.sh
```

This validates aliases and writes:

```text
generated/
├── tokens.css
├── tokens.ts
└── tokens.native.ts
```

Generated files are build artifacts and are not edited or committed. CI
regenerates and tests them from the canonical DTCG sources.
