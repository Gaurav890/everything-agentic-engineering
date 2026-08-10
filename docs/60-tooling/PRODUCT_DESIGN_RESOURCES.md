# Product-design resource catalog

This catalog preserves the product-design resources supplied for this starter.
It is a source and routing ledger—not an instruction to install everything.

Use `SKILLS.md` for concise phase routing. Use this file to understand the
original resource, invocation, timing, rationale, and assessment.

## Status vocabulary

- **Local contract** — this repository contains a local routing/quality skill.
- **External** — install or connect separately after source/security review.
- **Reference** — use for research or inspiration; do not install.
- **Conditional** — use only when the relevant stack or workflow is active.

## Phase 1: discovery, needs, and strategy

### `/benchmark`

- **Source:** [Owl Listener designer-skills — UX strategy](https://github.com/Owl-Listener/designer-skills/tree/main/ux-strategy)
- **What:** Structured competitive analysis of UX patterns, features, strengths, constraints, and gaps.
- **When:** Entering an unfamiliar problem space or competitive landscape.
- **Why:** Competitors reveal category expectations, constraints, and openings.
- **Assessment:** Good starting point; benchmarking informs synthesis, not copying.
- **Repository route:** Local `benchmark` contract; external source remains optional.

### `/strategize`

- **Source:** [Owl Listener designer-skills — UX strategy](https://github.com/Owl-Listener/designer-skills/tree/main/ux-strategy)
- **What:** Develops a complete UX strategy for a product or feature area.
- **When:** Before committing to information architecture, interaction, or visual direction.
- **Why:** Many visible design failures originate in upstream assumptions and tradeoffs.
- **Assessment:** Valuable when it surfaces non-obvious assumptions; push further if everything appears obvious.
- **Repository route:** Local `strategize` contract.

### `/layers-user-needs`

- **Source:** [Layers — User Needs](https://layers.jamiemill.com/skills/user-needs)
- **What:** Separates functional, emotional, social, and underlying user needs.
- **When:** After discovery or when a problem statement is solution-focused.
- **Why:** Prevents teams from jumping directly from observations to features.
- **Assessment:** Shifts “what should we build?” toward “what need are we serving?” and exposes assumptions.
- **Repository route:** Local `user-needs` contract.

### `/design-research:discover`

- **Source:** [Owl Listener designer-skills — Design research](https://github.com/Owl-Listener/designer-skills/tree/main/design-research)
- **What:** Runs structured discovery and opportunity mapping.
- **When:** At the start of ambiguous or 0→1 projects.
- **Why:** Discovery is often rushed and inconsistent.
- **Assessment:** Excellent landscape tool; not a replacement for judgment.
- **Repository route:** Local `discover` contract.

### `/impeccable shape`

- **Source:** [Impeccable Shape](https://impeccable.style/docs/shape)
- **What:** Interviews for purpose, users, content, constraints, and intent, then produces a design brief before code.
- **When:** Before vague or disputed feature work begins.
- **Why:** Most generic UI originates in skipped thinking rather than weak code.
- **Assessment:** A short interview prevents hours of rewriting; the brief is a compass, not a screen specification.
- **Repository route:** External; local `discover` and `user-needs` provide the fallback contract.

## Phase 2: interaction and agentic experience

### `/interaction-design`

- **Source:** [cuellarfr/design-skills](https://github.com/cuellarfr/design-skills)
- **What:** Defines flows, states, transitions, feedback, failure, and recovery.
- **When:** Before designing screens.
- **Why:** Most UX failures are interaction failures; polish cannot repair broken logic.
- **Assessment:** Validate the behavior here before spending time on visual treatment.
- **Repository route:** Local `interaction-design` contract.

### Agentic UX

- **Source:** Repository-owned synthesis in [`agentic-ux`](../../.claude/skills/agentic-ux/SKILL.md).
- **What:** Designs planning, streaming, tools, approvals, interruption, recovery, provenance, memory, and handoff.
- **When:** Any product includes agents, copilots, background work, generated artifacts, or automation.
- **Why:** AI-native UX requires visibility, control, trust calibration, and reversibility—not merely a chat box.
- **Repository route:** Local `agentic-ux` contract.

## Phase 3: design direction and reference research

### Anthropic `/frontend-design`

- **Source:** [anthropics/skills — frontend-design](https://github.com/anthropics/skills/tree/main/skills/frontend-design)
- **What:** Encourages an explicit aesthetic direction and avoids common generic AI output.
- **When:** Rapid prototyping without an established design system, or as one perspective during direction exploration.
- **Why:** Useful creative pressure against homogenized interfaces.
- **Assessment:** Popular and useful, but not the art director. It must not make every product look Anthropic.
- **Repository route:** Optional supplementary intelligence only.

### UI UX Pro Max

- **Source:** [nextlevelbuilder/ui-ux-pro-max-skill](https://github.com/nextlevelbuilder/ui-ux-pro-max-skill)
- **What:** Broad design intelligence for product types, palettes, typography, UX patterns, charts, web, and mobile stacks.
- **When:** Exploring several viable directions or generating category-specific system options.
- **Why:** Expands the solution space beyond one model’s default aesthetic.
- **Assessment:** Generate and compare alternatives; never accept the first recommendation blindly.
- **Repository route:** External and optional.

### Taste Skill

- **Source:** [Leonxlnx/taste-skill](https://github.com/Leonxlnx/taste-skill)
- **What:** Anti-slop critique focused on composition, hierarchy, typography, spacing, variance, motion, and density.
- **When:** Redesign, critique, or final taste pass.
- **Why:** Explicitly targets generic AI visual fingerprints.
- **Assessment:** A strong critic perspective, not a universal design system.
- **Repository route:** External and optional; pair with an independent evaluator.

### Emil Kowalski design-engineering skills

- **Source:** [emilkowalski/skills](https://github.com/emilkowalski/skills) · [skills directory](https://github.com/emilkowalski/skills/tree/main/skills) · [MIT license](https://github.com/emilkowalski/skills/blob/main/LICENSE)
- **Reviewed revision:** `78761e1b57f97dce65b983d640c70a68f39e8163` on 2026-08-10.
- **Install:** Upstream documents `npx skills@latest add emilkowalski/skills` for current main. The profile-aware `./agentic setup skills` command installs the reviewed revision recorded in `.agentic/external-skills.json` instead of silently advancing it.
- **What:** A ten-skill design-engineering collection covering high-craft UI implementation, purposeful motion, motion review/audit, vocabulary, Apple-style interaction, live variants, UI-library selection, and Sonner.
- **When:** The `design-critical` profile is active and implementation or refinement needs a precise craft capability.
- **Why:** It adds unusually concrete design-engineering and motion judgment that can reduce generic, mechanically polished AI output.
- **Assessment:** High-value craft layer, not art direction. It cannot replace discovery, user needs, UX strategy, human-approved direction, design tokens, accessibility, running-product evidence, or the independent evaluator.
- **Repository route:** Local `design-engineering-quality` contract selects the minimum installed capability. The external source is not copied into this repository.

| Upstream skill | Exact route |
|---|---|
| [`emil-design-eng`](https://github.com/emilkowalski/skills/tree/main/skills/emil-design-eng) | Broad design-critical implementation/refinement craft pass |
| [`animate`](https://github.com/emilkowalski/skills/tree/main/skills/animate) | Implement one justified animation |
| [`review-animations`](https://github.com/emilkowalski/skills/tree/main/skills/review-animations) | Explicit-only strict review of animation code or a motion-heavy diff |
| [`improve-animations`](https://github.com/emilkowalski/skills/tree/main/skills/improve-animations) | Read-only codebase animation audit and improvement plan |
| [`find-animation-opportunities`](https://github.com/emilkowalski/skills/tree/main/skills/find-animation-opportunities) | Find a few missing purposeful motion opportunities; reject decorative candidates |
| [`animation-vocabulary`](https://github.com/emilkowalski/skills/tree/main/skills/animation-vocabulary) | Name or classify an effect for shared design/engineering language |
| [`apple-design`](https://github.com/emilkowalski/skills/tree/main/skills/apple-design) | Approved gesture, spring, fluid-material, or Apple-platform direction only |
| [`prototype`](https://github.com/emilkowalski/skills/tree/main/skills/prototype) | Explicit-only live variants; a human chooses before production changes |
| [`pick-ui-library`](https://github.com/emilkowalski/skills/tree/main/skills/pick-ui-library) | Explicit-only dependency choice after inspecting installed capabilities |
| [`ask-sonner`](https://github.com/emilkowalski/skills/tree/main/skills/ask-sonner) | Sonner-specific setup or troubleshooting only |

The suite must not be invoked wholesale. For motion, establish purpose,
interruption/reversal behavior, performance, and reduced-motion handling before
implementation. “Do not animate” is a valid outcome.

### Impeccable

- **Source:** [Impeccable documentation](https://impeccable.style/docs)
- **What:** Design workflow spanning shaping, live iteration, critique, documentation, optimization, and polish.
- **When:** Use the relevant command at its corresponding phase.
- **Why:** Keeps product thinking, implementation, and refinement connected to the running interface.
- **Assessment:** One of the strongest “designing in code” workflows; still subordinate to the project design system.
- **Repository route:** External and optional.

### Refero Styles

- **Source:** [Refero Styles](https://styles.refero.design)
- **What:** Complete visual directions, typography, spacing, layout, and system inspiration.
- **When:** Building a reference board before choosing a visual thesis.
- **Why:** Gives the design process real examples instead of relying only on model taste.
- **Assessment:** Study several directions and synthesize; never clone one wholesale.
- **Repository route:** Reference only.

### 21st.dev

- **Source:** [21st.dev](https://21st.dev)
- **What:** Multi-author React/Tailwind components and interaction patterns.
- **When:** Component, layout, AI-interface, hero, dashboard, or interaction discovery.
- **Why:** Provides diverse structural ideas rather than one monolithic aesthetic.
- **Assessment:** Treat every component as a structural donor and restyle it through project tokens.
- **Repository route:** External component/reference source.

### Aceternity UI

- **Source:** [Aceternity UI](https://ui.aceternity.com)
- **What:** High-impact animated components and marketing interactions.
- **When:** The product genuinely needs expressive presentation or sophisticated interaction.
- **Why:** Accelerates complex visual techniques.
- **Assessment:** Use selectively; interaction structure may be borrowed, visual identity may not.
- **Repository route:** External component/reference source.

### MotionSites

- **Source:** Canonical source was not included in the supplied material and remains unverified.
- **What:** Motion, hero, and animated-experience inspiration.
- **When:** Motion is part of the approved product thesis.
- **Why:** Helps define choreography and interaction references before implementation.
- **Assessment:** Do not invent a link or add motion merely because a reference is impressive.
- **Repository route:** Reference pending canonical-source confirmation.

## Phase 4: systems, tokens, and components

### `/impeccable document`

- **Source:** [Impeccable Document](https://impeccable.style/docs/document)
- **What:** Scans a codebase and generates structured `DESIGN.md` documentation.
- **When:** Once the visual language has started stabilizing.
- **Why:** Design documentation usually drifts behind implementation.
- **Assessment:** Practical for documenting the system that actually exists.
- **Repository route:** External; local `design-system` owns the durable contract.

### `/tailwind-design-system`

- **Source:** [Tailwind Design System skill](https://claudemarketplaces.com/skills/wshobson/agents/tailwind-design-system)
- **What:** Evaluates tokens, theming, dark mode, and component variants in Tailwind systems.
- **When:** The active frontend is tightly coupled to Tailwind.
- **Why:** Modern design systems increasingly live in code.
- **Assessment:** Particularly useful for designer–engineer collaboration; conditional on the stack.
- **Repository route:** External and conditional.

### `/design-systems:audit-system`

- **Source:** [Owl Listener designer-skills](https://github.com/Owl-Listener/designer-skills)
- **What:** Audits consistency, completeness, accessibility, and token usage across a design system.
- **When:** Before scaling or redesigning.
- **Why:** Systems drift across tokens, components, documentation, and screens.
- **Assessment:** Often confirms suspected debt and helps prioritize migration.
- **Repository route:** Local `design-system-audit` contract.

### `/extract-design-system`

- **Source:** [Extract Design System skill](https://claudemarketplaces.com/skills/arvindrk/extract-design-system/extract-design-system)
- **What:** Extracts tokens, components, naming, and visual foundations from an existing codebase.
- **When:** Inheriting or auditing a mature product.
- **Why:** Teams often do not know the system they actually have.
- **Assessment:** A fast way to expose design debt before proposing a replacement.
- **Repository route:** External; inspect and document before redesigning.

### shadcn

- **Sources:** [shadcn/ui repository](https://github.com/shadcn-ui/ui) · [shadcn create](https://ui.shadcn.com/create)
- **What:** Accessible Radix/Tailwind components copied into the project so the team owns the code.
- **When:** Prototyping infrastructure or product logic where custom component invention is not yet valuable.
- **Why:** Removes low-value setup friction without package-level visual lock-in.
- **Assessment:** “Copy, own, modify” is the right tradeoff; default shadcn styling is not a finished design.
- **Repository route:** Conditional structural donor.

### Design intake and token-system foundations

- **Sources:** [DTCG 2025.10 format](https://www.designtokens.org/tr/2025.10/format/) · [DTCG color module](https://www.designtokens.org/tr/2025.10/color/) · [Figma variables and modes](https://help.figma.com/hc/en-us/articles/14506821864087-Overview-of-variables-collections-and-modes) · [Carbon color tokens](https://preview.carbondesignsystem.com/building-blocks/foundations/color/overview) · [Fluent design tokens](https://fluent2.microsoft.design/design-tokens) · [Material Color Utilities](https://github.com/material-foundation/material-color-utilities) · [WCAG text contrast](https://www.w3.org/WAI/WCAG22/Understanding/contrast-minimum.html) · [WCAG non-text contrast](https://www.w3.org/WAI/WCAG22/Understanding/non-text-contrast)
- **What:** Platform-neutral token format with types, values, aliases, groups, and extensions.
- **When:** Encoding an approved design direction for multiple platforms or tools.
- **Why:** Keeps design decisions interoperable rather than trapped in CSS or one design tool.
- **Assessment:** Gather constraints, compare realistic directions, and obtain
  human approval first. Stable semantic roles should keep their names across
  modes while values change. Tokens encode decisions; they do not create them.
- **Repository route:** Local `design-intake` and `design-tokens` contracts plus
  the `packages/design-tokens/` scaffold and generated specimen.

## Phase 5: Figma and implementation

### Figma Implement Design

- **Source:** [Figma MCP Server Guide](https://github.com/figma/mcp-server-guide)
- **What:** Supplies Figma design context to coding agents for implementation.
- **When:** After design decisions and target frames are approved.
- **Why:** Reduces friction and interpretation in design-to-code translation.
- **Assessment:** A compelling translation workflow; it does not replace product or design decisions.
- **Invocation:** Natural language after the Figma MCP/plugin is connected.
- **Repository route:** External and conditional.

### Figma Code Connect

- **Sources:** [Figma Code Connect](https://github.com/figma/code-connect) · [Figma MCP Server Guide](https://github.com/figma/mcp-server-guide)
- **What:** Maps Figma design-system components to production components.
- **When:** During system implementation and handoff.
- **Why:** Reduces divergence between design assets and real code.
- **Assessment:** Less flashy than generation and often more operationally useful.
- **Invocation:** Natural language after Figma tooling is connected.
- **Repository route:** External and conditional.

### Vercel React and web-design guidance

- **Source:** [vercel-labs/agent-skills](https://github.com/vercel-labs/agent-skills)
- **What:** React/Next.js engineering guidance and web-design/accessibility auditing.
- **When:** During implementation and focused audits.
- **Why:** Performance, semantics, state, and accessibility are part of UX quality.
- **Assessment:** Engineering and audit intelligence—not aesthetic authority.
- **Repository route:** External and stack-conditional.

## Phase 6: live iteration, audits, and release

### `/impeccable live`

- **Source:** [Impeccable Live](https://impeccable.style/tutorials/iterate-live)
- **What:** Iterates on running UI and writes variants back into code.
- **When:** Refining an existing interface.
- **Why:** Collapses the gap between visual exploration and implementation.
- **Assessment:** One of the closest workflows to natural designing in code.
- **Repository route:** External; preserve Playwright evidence and normal review.

### `/responsive-audit`

- **Source:** [Owl Listener designer-skills](https://github.com/Owl-Listener/designer-skills)
- **What:** Evaluates layouts and behavior across breakpoints.
- **When:** Before release and after layout/navigation changes.
- **Why:** Many interfaces work at only one viewport.
- **Assessment:** Quickly reveals whether a composition is robust.
- **Repository route:** Local `responsive-audit` contract.

### `/impeccable critique`

- **Source:** [Impeccable Critique](https://impeccable.style/docs/critique/)
- **What:** Performs a scored design review with rationale.
- **When:** An honest independent opinion is required.
- **Why:** Generic or polite feedback does not produce strong iteration.
- **Assessment:** Valuable because it can identify mediocrity specifically.
- **Repository route:** External; local `design-critic` enforces evaluator independence.

### `/impeccable polish`

- **Source:** [Impeccable Polish](https://impeccable.style/docs/polish)
- **What:** Finds visual and interaction details before launch.
- **When:** After functionality, system integrity, and critique pass.
- **Why:** Small details drive perceived quality.
- **Assessment:** The final gap between “done” and “delightful”; never use it to hide broken UX.
- **Repository route:** External; local `polish` contract.

### `/accessibility-audit`

- **Source:** [cuellarfr/design-skills](https://github.com/cuellarfr/design-skills)
- **What:** Checks designs and implemented flows against accessibility standards.
- **When:** Throughout implementation and before release.
- **Why:** Accessibility otherwise becomes late cleanup.
- **Assessment:** Compliance and an accessible experience are not identical; manual testing still matters.
- **Repository route:** Local `accessibility-audit` contract.

### `/optimize`

- **Source:** [Impeccable Optimize](https://impeccable.style/docs/optimize)
- **What:** Analyzes LCP, bundle size, rendering, and performance bottlenecks.
- **When:** Before major launches or after performance-sensitive changes.
- **Why:** A visually strong interface that responds slowly is poor UX.
- **Assessment:** Design and engineering quality converge here.
- **Repository route:** External; local `performance-ux` contract.

### `/design-ops`

- **Source:** [cuellarfr/design-skills](https://github.com/cuellarfr/design-skills)
- **What:** Produces implementation-ready documentation and delivery artifacts.
- **When:** Before engineering handoff, review, or cross-team transfer.
- **Why:** Ambiguity creates product delays and implementation drift.
- **Assessment:** The purpose is reduced interpretation, not documentation volume.
- **Repository route:** Local `design-ops` contract.

## Original curated collection

- **Source:** [Claude Code Skills for Product Designers Who Want to Build](https://floraghnassia.notion.site/Claude-Code-Skills-for-Product-Designers-who-want-to-build-3742aec4753680bf89f9c8bd51b318d8)
- **Use:** Inspiration for organizing specialist capabilities by design phase rather than building one giant design skill.
- **Note:** The linked page is an external curated collection; each dependency should still be verified at its original source before installation.

## Discovery helpers mentioned in the collection

- **Find Skills:** Use a trusted skill-discovery mechanism to locate candidates; discovery is not approval.
- **Skill Creator:** Use the platform’s built-in skill-creation guidance to encode repeatable local workflows.
- **Rule:** The best system is a small set that reflects the actual workflow, not the largest possible collection.
