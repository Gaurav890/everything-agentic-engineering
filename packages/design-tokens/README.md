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

Component tokens reference stable semantic roles such as
`color.action.primary.default`; they never reference a light or dark namespace.
The build resolves semantic and component values independently for each mode.

## Generate platform outputs

```bash
./scripts/build-design-tokens.sh
```

This validates aliases and writes:

```text
generated/
├── direction.css
├── tokens.css
├── tokens.ts
├── tokens.native.ts
└── tokens.preview.html
```

`direction.css` is empty until `.agentic/design.json` records an explicitly
approved direction. It then contains only the selected DTCG-compatible semantic
overrides from `.agentic/design-directions.json`; candidate directions do not
silently become canonical.

Generated files are build artifacts and are not edited or committed. CI
regenerates and tests them from the canonical DTCG sources.

Validation fails on theme key/type drift, theme-specific component aliases, or
required WCAG contrast failures. Open `generated/tokens.preview.html` to review
light/dark semantic roles and contrast evidence before evaluating real screens.
