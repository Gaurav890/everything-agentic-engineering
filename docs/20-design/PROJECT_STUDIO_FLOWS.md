# Project Studio flows

Status: Clickable contract prototype for T-055

Open [`prototypes/product-to-proof-studio.html`](prototypes/product-to-proof-studio.html)
in a browser. The prototype is intentionally static: it validates hierarchy,
language, activity transitions, disclosure, and human gates without creating a
second implementation or suggesting that workers already run.

## Navigation model

```text
Start
  └─ Shape ── product gate
       └─ Design ── direction + token gates
            └─ Build ── wave + integration gates
                 └─ Prove ── evidence + release gates
```

People may inspect any scenario. CSS `:target` state routing keeps the prototype
functional without JavaScript, and only the current rendered state exposes a
primary action. A blocked or unknown prerequisite routes to its owning
decision; stages never manufacture completion to keep the journey moving.

## Flow A — New product

```text
Describe outcome
→ confirm audience and first journey
→ decide whether current research matters
→ compare live product-specific directions
→ approve or reject all
→ compile reviewed semantics
→ plan bounded tasks
→ review exact run boundary
→ execute one supervised wave
→ inspect integration evidence
→ continue or pause
→ accept independent proof
→ human release and merge decision
```

## Flow B — Resume after interruption

```text
Open Studio
→ reconcile journal with Git/worktrees/processes/checks/PRs
→ show observed versus recorded state
→ stale running becomes uncertain
→ choose safe recovery, cancel, or human diagnosis
→ append decision
→ resume only from a reconciled checkpoint
```

## Flow C — Missing dependency

```text
Start
→ detect missing frontend dependency
→ show one exact installation command
→ retain the same project state
→ offer terminal continuation
→ never install automatically
```

## Interaction rules

- Scenario and state navigation uses ordinary links and works without JavaScript.
- Keyboard focus remains visible.
- The page begins with a skip link and every state has a labelled region.
- Status is communicated in text, not color alone.
- Details use native disclosure elements.
- No motion is required to understand state.
- The future implementation announces event-stream updates without moving
  focus or continuously reordering the page.
- Destructive or authority-expanding actions are never the default button.

T-054 verification covers tab order, visible focus in light/dark themes, target
state/action consistency, reflow at 200% zoom, and narrow/wide viewport
screenshots. These validate the contract prototype, not the future Studio.

## T-055 handoff

T-055 converts these flows into the loopback control plane with strict origin
and session protection, validated project roots, and an allow-listed action
registry. The static prototype itself must not grow a shell endpoint.
