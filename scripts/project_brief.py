"""Project-owned onboarding context and copy-only document templates."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

BRIEF_PATH = Path(".agentic/project-brief.json")
CLIENTS = ("choose", "claude", "codex", "manual")
DESIGN_MODES = ("custom", "existing-brand", "reference")


class BriefError(ValueError):
    pass


def validate(brief: dict[str, Any]) -> None:
    if brief.get("schema_version") != 1:
        raise BriefError("Unsupported project brief schema")
    for field in ("name", "audience", "promise"):
        if not isinstance(brief.get(field), str) or not brief[field].strip():
            raise BriefError(f"Project brief requires {field}")
    for field in ("first_outcome", "design_preferences"):
        if brief.get(field) is not None and not isinstance(brief[field], str):
            raise BriefError(f"Project brief {field} must be text or null")
    if brief.get("assistant") not in CLIENTS or brief.get("design_mode") not in DESIGN_MODES:
        raise BriefError("Unknown assistant choice or design mode")
    if brief.get("status") not in ("captured", "ready"):
        raise BriefError("Project brief status must be captured or ready")
    if not isinstance(brief.get("open_questions"), list) or not all(
        isinstance(question, str) and question.strip() for question in brief["open_questions"]
    ):
        raise BriefError("Project brief open questions must be a text list")
    if brief["status"] == "ready" and not (
        isinstance(brief.get("first_outcome"), str) and brief["first_outcome"].strip()
        and isinstance(brief.get("confirmed_by"), str)
        and brief["confirmed_by"].strip()
    ):
        raise BriefError("A ready brief needs a first outcome and recorded human confirmation")


def load(root: Path) -> dict[str, Any]:
    if (root / ".agentic").is_symlink() or (root / BRIEF_PATH).is_symlink():
        raise BriefError("Project brief cannot follow symlinks")
    try:
        brief = json.loads((root / BRIEF_PATH).read_text())
    except (OSError, ValueError) as error:
        raise BriefError(f"Cannot read the project brief: {error}") from error
    if not isinstance(brief, dict):
        raise BriefError("Project brief must be an object")
    validate(brief)
    return brief


def create(plan: Any) -> dict[str, Any]:
    return {
        "schema_version": 1,
        "name": plan.project_name,
        "audience": plan.audience or "To be discussed with the product owner",
        "promise": plan.promise or "To be discussed with the product owner",
        "first_outcome": plan.first_outcome,
        "design_mode": plan.design_mode,
        "design_preferences": plan.design_preferences,
        "assistant": plan.assistant,
        "status": "captured",
        "confirmed_by": None,
        "open_questions": [
            "Confirm the first useful journey and its failure/recovery states.",
            "Clarify product facts, constraints, content, and success criteria.",
            "Resolve brand, palette, typography, motion, and accessibility intent.",
        ],
    }


def documents(brief: dict[str, Any], *, web: bool) -> dict[Path, str]:
    """Used only at creation. Later revisions belong to the user and their reviewer."""
    validate(brief)
    name, audience, promise = (brief[key] for key in ("name", "audience", "promise"))
    outcome = brief["first_outcome"] or "Not chosen yet. Agree one useful outcome before implementation."
    heading = f"Project: {name}\n\nStatus: Draft — product-owner review required.\n"
    context = f"\n## Known intent\n\nAudience: {audience}\n\nPromise: {promise}\n\nFirst outcome: {outcome}\n"
    boundary = "\nThese are captured inputs, not evidence that a feature exists. Unknown facts remain open; do not substitute the starter's requirements.\n"
    result = {
        "docs/00-vision/NORTH_STAR.md": f"# {name} — North star\n\n{heading}{context}{boundary}\n## Open decisions\n\nSuccess measures, non-goals, and immutable constraints need confirmation.\n",
        "docs/00-vision/PRODUCT_CONTEXT.md": f"# Product context\n\n{heading}{context}{boundary}",
        "docs/00-vision/PERSONAS.md": f"# Audience\n\n{heading}\n{audience}\n\nNeeds and constraints have not been validated through user research.\n",
        "docs/00-vision/GLOSSARY.md": f"# {name} glossary\n\nDefine domain terms as decisions are made. No starter domain is assumed.\n",
        "docs/10-product/PRD.md": f"# {name} — Product requirements\n\n{heading}{context}{boundary}\n## FR-001 — First useful outcome (draft)\n\n{outcome}\n\nConfirm the user, trigger, result, alternatives, and recovery before creating an implementation task.\n\n## Open questions\n\nData ownership, domain rules, sensitive information, integrations, and launch criteria are unresolved.\n",
        "docs/10-product/ACCEPTANCE_CRITERIA.md": f"# {name} — Acceptance criteria\n\n{heading}\n## AC-001 — First useful outcome (draft)\n\nLinked requirement: FR-001.\n\nIntended outcome: {outcome}\n\nAgree observable Given/When/Then examples with the product owner, including failure and recovery. No passing product evidence exists yet.\n",
        "docs/10-product/USER_JOURNEYS.md": f"# {name} — User journeys\n\n{heading}{context}\nDocument the trigger, normal path, intermediate states, failure, recovery, and exit after scope review.\n",
        "docs/10-product/ROADMAP.md": f"# {name} — Roadmap\n\n1. Confirm the brief and first useful outcome.\n2. Review a product-specific working design.\n3. Implement and verify the agreed slice.\n4. Review production requirements separately.\n\nNo inherited starter milestones or completion claims apply.\n",
        "docs/10-product/NON_GOALS.md": f"# {name} — Non-goals\n\nConfirm product exclusions with the owner. Generation itself does not connect services, enable permissions, deploy, or implement the product.\n",
        "docs/10-product/OPEN_QUESTIONS.md": f"# {name} — Open questions\n\n" + "\n".join(f"- {q}" for q in brief["open_questions"]) + "\n",
        "docs/20-design/COPY.md": f"# {name} — Product copy\n\n{heading}{context}\nAll interface copy remains draft. Do not invent customers, testimonials, metrics, credentials, or portfolio projects.\n",
        "docs/20-design/DESIGN_DECISIONS.md": f"# {name} — Design decisions\n\nNo product-specific design has been approved. Record rationale, alternatives, evidence, and direct approval here.\n",
        "docs/20-design/DESIGN_DIRECTIONS.md": f"# {name} — Design directions\n\nStatus: Needs approval\n\nMode: {brief['design_mode']}\n\nPreferences: {brief['design_preferences'] or 'Discuss or delegate recommendations; no palette is assumed.'}\n\nCreate product-specific alternatives with real local preview routes. The bundled examples are optional references, not the available design space. Register candidates with `./agentic design propose`, inspect them, and record reviewed evidence before approval.\n",
        "docs/40-execution/INITIAL_TASK_GRAPH.md": f"# {name} — Initial task graph\n\nNo implementation scope has been approved. After brief review, decompose FR-001 and AC-001 into bounded tasks with ownership and verification.\n",
    }
    for filename, title in (
        ("ARCHITECTURE", "Architecture"), ("API_CONTRACTS", "API contracts"),
        ("DATA_MODEL", "Data model"), ("ROLE_MATRIX", "Roles and access"),
        ("AUDIT_EVENTS", "Audit events"),
    ):
        result[f"docs/30-engineering/{filename}.md"] = f"# {name} — {title}\n\n{heading}{context}\nNo production contract is established. Inspect the selected scaffold, then document this product's actual boundaries; do not present reference adapters as production services.\n"
    result["docs/30-engineering/SECURITY_MODEL.md"] = f"# {name} — Security model\n\n{heading}\nNo production security review has been completed. Identify data sensitivity, trust boundaries, authorization, retention, and abuse cases for the agreed product.\n\nKeep secrets out of source and browser bundles. Existing permission, review, and verification safeguards remain in force. Development-assistant credentials never become application credentials.\n"
    result["docs/60-tooling/ASSISTANT_HANDOFF.md"] = f"""# Continue building {name}

Run `./agentic start`. It shows the project folder, saved brief, and exact next
instruction, and can launch an installed interactive client after confirmation.
No keys are collected, no client is installed, and no permissions are changed.
If you already use a desktop app or editor, open this project there and paste:

```text
Use the project-onboarding skill. Read .agentic/project-brief.json and the
project instructions. Resume from the current brief, tasks, and evidence;
do not repeat settled questions or assume a preset is the final design.
```

Native sign-in belongs to the client. Its subscription or API billing is separate
from any future AI feature inside this product. Never paste keys or session tokens
into this file. For unsupported clients choose the manual handoff.

{'The included web reference is not your finished product.' if web else 'This profile is a planning scaffold; no runnable application is promised.'}
"""
    return {Path(path): content for path, content in result.items()}


def digest(value: Any) -> str:
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
