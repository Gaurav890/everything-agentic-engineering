# UX strategy

## Experience principles

1. **Attention before activity.** One pending decision outranks dozens of active
   tool calls.
2. **State is a contract.** “Working” is insufficient; show planning, running,
   waiting, approval, recovery, and completion distinctly.
3. **Evidence near consequence.** Put sources, affected scope, and rollback next
   to approval—not in a separate audit screen.
4. **Progressive operational detail.** Start with task purpose and current step;
   reveal granular events on demand.
5. **Human control without micromanagement.** Pause, redirect, approve, deny,
   and retry are available at meaningful boundaries.
6. **Artifacts over chatter.** Durable outputs are first-class; conversational
   narration is secondary.

## Information architecture

```text
Workspace
├── Attention queue
├── Runs
│   ├── Plan and progress
│   ├── Agent workstreams
│   ├── Evidence/activity
│   └── Controls
└── Artifacts
```

## Differentiation thesis

Most agent consoles optimize for traces or chat. Signalroom optimizes for
supervision: an editorial operations surface where consequential decisions,
execution state, and durable work products remain continuously legible.
