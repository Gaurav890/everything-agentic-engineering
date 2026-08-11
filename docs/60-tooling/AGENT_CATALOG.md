# Reviewed specialist catalog

The canonical machine-readable catalog is
`.agentic/external-agents.json`. This page makes its scope understandable to
contributors; `./agentic agents list` is the live discovery command.

- Source: [Agency Agents](https://github.com/msitarzewski/agency-agents)
- Reviewed revision: `ebe9c99acb5c96f9468de368d8bead775387d1a7`
- License: [MIT](https://github.com/msitarzewski/agency-agents/blob/ebe9c99acb5c96f9468de368d8bead775387d1a7/LICENSE)
- Complete upstream roster: [The Agency roster](https://github.com/msitarzewski/agency-agents#the-agency-roster)

The external repository is untrusted input. Nothing from it is vendored,
installed, or executed by the broker.

| Contract | Route when evidence shows | Default project role | Required on match |
|---|---|---|---|
| [`codebase-onboarding`](https://github.com/msitarzewski/agency-agents/blob/ebe9c99acb5c96f9468de368d8bead775387d1a7/engineering/engineering-codebase-onboarding-engineer.md) | unfamiliar repository or execution path | architect / researcher | No |
| [`minimal-change`](https://github.com/msitarzewski/agency-agents/blob/ebe9c99acb5c96f9468de368d8bead775387d1a7/engineering/engineering-minimal-change-engineer.md) | surgical fix or regression containment | implementation owner | No |
| [`multi-agent-systems`](https://github.com/msitarzewski/agency-agents/blob/ebe9c99acb5c96f9468de368d8bead775387d1a7/engineering/engineering-multi-agent-systems-architect.md) | orchestration, handoffs, agent topology | orchestrator / architect | Yes |
| [`identity-access`](https://github.com/msitarzewski/agency-agents/blob/ebe9c99acb5c96f9468de368d8bead775387d1a7/engineering/engineering-identity-access-engineer.md) | authentication, authorization, SSO, sessions | backend / security | Yes |
| [`payments-billing`](https://github.com/msitarzewski/agency-agents/blob/ebe9c99acb5c96f9468de368d8bead775387d1a7/engineering/engineering-payments-billing-engineer.md) | payments, billing, refunds, subscriptions | backend / security | Yes |
| [`privacy-engineering`](https://github.com/msitarzewski/agency-agents/blob/ebe9c99acb5c96f9468de368d8bead775387d1a7/engineering/engineering-privacy-engineer.md) | PII, retention, consent, privacy rights | architect / security | Yes |
| [`site-reliability`](https://github.com/msitarzewski/agency-agents/blob/ebe9c99acb5c96f9468de368d8bead775387d1a7/engineering/engineering-sre.md) | SLOs, capacity, observability, resilience | architect / backend | No |
| [`incident-response`](https://github.com/msitarzewski/agency-agents/blob/ebe9c99acb5c96f9468de368d8bead775387d1a7/engineering/engineering-incident-response-commander.md) | production incident or postmortem | orchestrator / security | Yes |
| [`internationalization`](https://github.com/msitarzewski/agency-agents/blob/ebe9c99acb5c96f9468de368d8bead775387d1a7/engineering/engineering-i18n-engineer.md) | locale, translation, RTL, ICU/CLDR | frontend or mobile | No |
| [`ui-finish-gate`](https://github.com/msitarzewski/agency-agents/blob/ebe9c99acb5c96f9468de368d8bead775387d1a7/design/design-ui-finish-gate-reviewer.md) | substantial design-critical interface | frontend / design critic | Yes |
| [`persona-walkthrough`](https://github.com/msitarzewski/agency-agents/blob/ebe9c99acb5c96f9468de368d8bead775387d1a7/design/design-persona-walkthrough.md) | journey friction, anxiety, trust, conversion | product / design critic | No |
| [`evidence-collector`](https://github.com/msitarzewski/agency-agents/blob/ebe9c99acb5c96f9468de368d8bead775387d1a7/testing/testing-evidence-collector.md) | browser, screenshot, or visual evidence | QA evaluator | No |
| [`accessibility-auditor`](https://github.com/msitarzewski/agency-agents/blob/ebe9c99acb5c96f9468de368d8bead775387d1a7/testing/testing-accessibility-auditor.md) | WCAG, keyboard, screen reader, contrast | QA / design critic | Yes |
| [`agentic-identity-trust`](https://github.com/msitarzewski/agency-agents/blob/ebe9c99acb5c96f9468de368d8bead775387d1a7/specialized/agentic-identity-trust.md) | cross-agent identity, delegation, audit trail | architect / security | Yes |

Use `./agentic agents show <id>` for the exact pinned source file, authority,
deliverables, evaluator, profiles, and non-use rule. The larger upstream roster
is deliberately visible but does not become active until a capability proves a
real gap and passes the local review contract.
