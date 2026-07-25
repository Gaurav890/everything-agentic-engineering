---
name: agentic-ux
description: Design understandable, controllable, and trustworthy human-agent experiences. Use for copilots, tool-calling agents, generated artifacts, background work, approvals, multi-agent systems, persistent memory, streaming, or long-running workflows.
---

# Agentic UX

Do not default to a chat box. Define:

- what the agent knows, plans, is doing, and has changed;
- idle, planning, queued, running, streaming, tool, approval, interrupted,
  partial, failed, retrying, complete, and handoff states;
- user control: edit plan, approve, deny, pause, interrupt, undo, retry, correct;
- trust: provenance, citations, confidence boundaries, permissions, previews,
  irreversible-action warnings, and memory visibility;
- artifacts, background work, notifications, collaboration, and recovery.

Minimize anthropomorphism that obscures system state. Show enough process for
users to predict consequences without dumping raw reasoning or logs. Test partial
success and loss-of-connection paths, not only the ideal completion.
