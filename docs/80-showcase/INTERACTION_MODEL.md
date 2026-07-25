# Interaction model

## Run lifecycle

```text
queued → planning → running → waiting_for_approval
                              ├── approve → running → complete
                              ├── deny → redirected → running
                              └── pause → paused → resume

running → partial_failure → retry / redirect / stop
```

## Approval gate

An approval shows:

- requested action;
- why it is needed;
- affected scope;
- evidence reviewed;
- reversibility;
- approve and deny actions.

Approval never auto-advances. Choosing an action creates visible feedback and
updates the run state.

## Interruption

Pause is always available for active work. Pausing preserves completed steps and
the next safe continuation point. Resume continues from that boundary.

## Selection

Selecting a run changes the central plan, execution lane, evidence, artifacts,
and controls without losing workspace context.

## Responsive behavior

- Desktop: task rail, execution canvas, and attention inspector appear together.
- Tablet: inspector becomes an inline panel below the run header.
- Mobile: a compact run switcher precedes the execution timeline; details stack
  in decision-first order.

## Required demonstrable states

- normal: active research brief with a pending approval;
- loading: initial workspace skeleton;
- empty: no runs in the chosen filter;
- error: source retrieval partially failed with recovery affordance.
