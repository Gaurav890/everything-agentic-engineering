---
name: context-handoff
description: Preserve project continuity before ending a substantial task or session by updating current truth, verified progress, decisions, risks, blockers, and exact next actions without dumping noisy transcripts.
---

# Context handoff

Use before ending substantial work, after major merges, before compaction, or whenever another agent/session may continue.

## Update CURRENT_STATE.md

Record only present-tense factual truth:
- what exists,
- what is deployed,
- what is verified,
- what remains incomplete.

## Append PROGRESS.md

For each verified accomplishment:
- timestamp/date,
- task ID,
- requirement/acceptance IDs,
- change summary,
- evidence,
- commit/PR if available.

Never rewrite prior entries to make history look cleaner.

## Rewrite HANDOFF.md

Keep it concise:
- current goal,
- completed,
- in progress,
- blockers,
- unresolved decisions,
- exact next action,
- verification status,
- relevant files.

## Decisions

If an architectural choice is durable, create/update an ADR.
If a visual choice is durable, update DESIGN_DECISIONS.md.

## Anti-pattern

Do not paste chat transcripts, chain-of-thought, or full test logs into memory.
Distill facts, decisions, and evidence.
