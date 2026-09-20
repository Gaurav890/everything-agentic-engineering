# Signalroom cross-platform journey

Status: Product contract; implementation is split across T-057 and T-058

## Promise

Signalroom helps an operations team make consequential decisions without
losing evidence, responsibility, or recovery context.

## One shared journey

1. A requester creates a tenant-scoped decision request.
2. Evidence requirements become visible before submission.
3. The policy layer identifies an eligible reviewer and prevents self-approval.
4. A reviewer inspects evidence, consequences, conflicts, and audit history.
5. The reviewer approves, rejects, requests changes, or interrupts the action.
6. Concurrency and authorization failures preserve context and a safe recovery.
7. The final decision appends an attributable audit event and exposes the proof
   required for release review.

## Web product

The web surface is an operational decision environment, not a generic admin
dashboard. It must show:

- evidence and consequence in the same decision context;
- ownership, freshness, conflicts, and blocked states before action;
- interruption and resumption without losing the decision trail;
- purposeful animation that explains state change, plus reduced motion;
- responsive compositions that preserve hierarchy instead of merely stacking;
- three genuinely different product directions before one becomes canonical.

## Enterprise contract

The reference slice proves locally:

- tenant isolation and verified role enforcement;
- dual control for consequential decisions;
- policy-gated evidence and rationale;
- append-only audit vocabulary;
- safe authorization failures and concurrency conflicts;
- explicit local-demo versus production-adapter boundaries.

Production identity, transactional persistence, immutable audit storage,
notifications, retention, observability, migration, and deployment remain
separate adapter decisions.

## Native mobile companion

The mobile product is for consequential moments away from the operations desk:

- triage a decision and see what changed;
- review the minimum sufficient evidence with native navigation;
- acknowledge consequence before responding;
- approve, reject, request changes, or defer when policy allows;
- recover after interruption, offline state, conflict, or expired authority;
- confirm the resulting audit event.

Offline mode is read/draft-only. It may show explicitly labeled cached evidence,
save a local response draft, or defer the decision. It may not finalize or
queue an approval, rejection, or change request as authoritative. Submission
requires connectivity and fresh revalidation of identity, tenant, role,
dual-control eligibility, evidence version, policy, request version, and
concurrency before the service appends an audit event.

It must use native interaction, focus, haptics, typography, text scaling,
screen-reader labels, reduced motion, safe areas, and device layouts. It is not
the web layout compressed into a phone.

The initial tested target for T-058 is Expo SDK 57, React Native 0.86, React
19.2.3, Expo Router, and Node 22.13 or newer. The final pin is revalidated when
T-058 begins. EAS remains optional and is never configured automatically.

Sources: [Expo SDK compatibility table](https://docs.expo.dev/versions/latest/)
and [Expo end-to-end testing guidance](https://docs.expo.dev/tutorial/eas/maestro/).

## What platforms share

- domain and API contracts;
- workflow, authorization, audit, and recovery vocabulary;
- semantic design tokens and platform mappings;
- evidence identifiers and decision status.

Web components are not imported into native UI. Shared semantics do not imply
shared layout, gestures, navigation, or rendering primitives.

## Required states

Normal, loading, empty, sparse, dense, invalid, disabled, unauthorized,
offline, interrupted, conflict, error, recovery, and success states must have
platform-appropriate evidence.

## Release proof

Web needs behavior, keyboard, responsive, contrast, reduced-motion,
performance, and visual-regression evidence. Mobile needs Jest/React Native
Testing Library plus explicit Maestro journeys on Android and iOS simulators,
small and large devices, light and dark themes, text scaling, screen-reader
labels, reduced motion, interruption, offline/error, and recovery.

Builder and release-blocking evaluator identities must differ.
