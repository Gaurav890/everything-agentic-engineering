from __future__ import annotations

import copy
import hashlib
import json
import sys
import tempfile
import unittest
from html.parser import HTMLParser
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
AGENTIC = ROOT / ".agentic"
sys.path.insert(0, str(ROOT / "scripts"))

import product_to_proof_contract as contract  # noqa: E402

try:
    from jsonschema import Draft202012Validator
    from referencing import Registry, Resource
except ImportError:  # pragma: no cover - the semantic validator remains mandatory
    Draft202012Validator = None
    Registry = None
    Resource = None


SHA = "a" * 64
COMMIT = "b" * 40


def load_json(path: Path) -> dict:
    return json.loads(path.read_text())


ACTION_REGISTRY = load_json(AGENTIC / "run-actions.json")
ACTION_INDEX = {action["id"]: action for action in ACTION_REGISTRY["actions"]}


def project_identity(root: Path) -> dict:
    resolved = root.resolve(strict=True)
    stat = resolved.stat()
    return {
        "display_path": str(root),
        "canonical_path": str(resolved),
        "device": stat.st_dev,
        "inode": stat.st_ino,
    }


def task(task_id: str, path: str, dependencies: list[str], provider: str = "manual") -> dict:
    return {
        "task_id": task_id,
        "title": task_id,
        "depends_on": dependencies,
        "writable_paths": [path],
        "check_action_ids": ["verify.quick"],
        "provider": provider,
        "provider_version": "manual-1",
        "capability_tier": "standard",
        "capability_ids": ["manual_packet", "workspace_write", "network_disabled", "mcp_disabled", "checkpoint_resume"],
        "model": "user-selected",
        "model_source": "user",
        "invocation_sha256": SHA,
        "allowed_action_ids": [],
        "retry_budget": 2,
        "timeout_seconds": 900,
        "branch": f"feature/{task_id}",
        "worktree": f"/tmp/{task_id}",
    }


def valid_plan(root: Path) -> dict:
    worktree_parent = root / "worktrees"
    worktree_parent.mkdir(exist_ok=True)
    tasks = [task("T-100", "src/alpha/**", []), task("T-101", "src/beta/**", ["T-100"])]
    for item in tasks:
        item["worktree"] = str(worktree_parent / item["task_id"])
    return {
        "schema_version": "1.0.0",
        "run_id": "run_contract01",
        "created_at": "2026-09-20T00:00:00Z",
        "project_root": project_identity(root),
        "worktree_parent": project_identity(worktree_parent),
        "task_ledger_sha256": SHA,
        "default_branch": {"name": "main", "ref": "refs/heads/main", "commit": COMMIT},
        "base_ref": "main",
        "base_commit": COMMIT,
        "concurrency": 3,
        "gate_mode": "pause_after_wave",
        "tasks": tasks,
        "waves": [
            {"wave": 1, "task_ids": ["T-100"], "requires_human_continue": True},
            {"wave": 2, "task_ids": ["T-101"], "requires_human_continue": True},
        ],
        "runtime_policy": {
            "allowed_providers": ["manual"],
            "network": {"mode": "disabled", "allowlist": [], "policy_sha256": SHA, "reviewed_decision_id": None},
            "mcp": {"mode": "disabled", "server_ids": [], "tool_ids": [], "config_sha256": SHA, "reviewed_decision_id": None},
            "permissions": {"workspace_write": True, "sandbox_bypass": False, "direct_main_write": False, "policy_sha256": SHA},
            "environment_sha256": SHA,
            "action_registry_sha256": contract.digest(ACTION_REGISTRY),
            "stop_conditions": ["wave_complete", "permission_denied", "same_failure_third_attempt"],
        },
        "authority": {"may_deploy": False, "may_approve": False, "may_merge": False},
    }


def valid_state() -> dict:
    state = {
        "schema_version": "1.0.0",
        "reducer_version": "1.0.0",
        "run_id": "run_contract01",
        "plan_sha256": SHA,
        "journal_head_sha256": SHA,
        "journal_head_event_id": "evt_contract01",
        "last_sequence": 3,
        "status": "completed",
        "updated_at": "2026-09-20T00:10:00Z",
        "current_wave": 1,
        "workers": [{"worker_id": "worker_1", "task_id": "T-100", "provider": "manual", "session_id": None, "process_id": None, "resume_token_sha256": None, "status": "passed", "branch": "feature/T-100", "worktree": "/tmp/T-100", "attempts": 1}],
        "evidence": {"required": ["evd_contract01"], "collected": ["evd_contract01"], "complete": True},
        "decisions": ["dec_contract01"],
        "human_gate": {"required": False, "kind": "none", "decision_event_id": None},
        "reconciliation": {"checked_at": "2026-09-20T00:10:00Z", "git": "consistent", "worktrees": "consistent", "processes": "consistent", "checks": "consistent", "pull_requests": "consistent", "stale_running_count": 0},
        "reconciliation_sha256": None,
    }
    state["reconciliation_sha256"] = contract.digest(state["reconciliation"])
    return state


def valid_benchmark() -> dict:
    scores = {"correctness": 4, "design_specificity": 4, "interaction_quality": 4, "accessibility": 4, "recovery": 4}
    measurement = {"value": 10, "unknown_reason": None}
    return {
        "schema_version": "1.0.0",
        "benchmark_id": "bench_contract01",
        "protocol_sha256": SHA,
        "brief_id": "signalroom",
        "brief_sha256": SHA,
        "acceptance_sha256": SHA,
        "repetition": 1,
        "blind_arm_id": "arm_contract01",
        "workflow_label": "revealed-after-seal",
        "reidentified_at": "2026-09-20T02:00:00Z",
        "arm_position": 1,
        "operator_id": "operator-1",
        "builder_ids": ["builder-1"],
        "operator_protocol_sha256": SHA,
        "pinned_setup": {"repository_commit": COMMIT, "workflow_version": "1", "provider": "manual", "provider_version": "1", "model": "user-selected", "machine": "fixture", "dependency_state": "locked", "cache_state": "cold", "network_policy_sha256": SHA, "permission_policy_sha256": SHA},
        "reviewers": [
            {"id": "reviewer-1", "blind": True, "independent_from_builder": True, "sealed_at": "2026-09-20T01:00:00Z", "scores": scores},
            {"id": "reviewer-2", "blind": True, "independent_from_builder": True, "sealed_at": "2026-09-20T01:10:00Z", "scores": scores},
        ],
        "aggregate_scores": scores,
        "measurements": {"active_minutes": measurement, "wall_minutes": measurement, "human_intervention_minutes": measurement, "cost": {"value": 1, "currency": "USD", "estimated": True, "unknown_reason": None}},
        "counts": {"tasks": 2, "waves": 2, "retries": 0, "failure_fingerprints": 0, "checks": 2, "evidence_items": 1, "human_decisions": 2},
        "violations": [],
        "failures": [],
        "exclusions": [],
        "artifacts": [{"kind": "review", "path": "review.json", "sha256": SHA}],
        "failures_published": True,
        "verdict": "pass",
    }


def completed_run(root: Path) -> tuple[dict, list[dict], dict]:
    artifact = root / "proof.txt"
    artifact.write_text("verified")
    artifact_sha = hashlib.sha256(artifact.read_bytes()).hexdigest()
    plan = valid_plan(root)
    plan["tasks"] = [plan["tasks"][0]]
    plan["waves"] = [{"wave": 1, "task_ids": ["T-100"], "requires_human_continue": True}]
    plan_sha = contract.digest(plan)
    events: list[dict] = []

    def append(event_type: str, actor: dict, payload: dict, **fields: object) -> dict:
        event = {
            "schema_version": "1.0.0",
            "sequence": len(events) + 1,
            "event_id": f"evt_contract{len(events) + 1:02d}",
            "run_id": plan["run_id"],
            "plan_sha256": plan_sha,
            "occurred_at": f"2026-09-20T00:{len(events):02d}:00Z",
            "type": event_type,
            "actor": actor,
            "previous_event_sha256": contract.digest(events[-1]) if events else None,
            "payload": payload,
            **fields,
        }
        events.append(event)
        return event

    append("run.planned", {"kind": "system", "id": "planner"}, {"plan_sha256": plan_sha})
    start_head = contract.digest(events[-1])
    start_decision = {
        "schema_version": "1.0.0",
        "decision_id": "dec_start0001",
        "run_id": plan["run_id"],
        "plan_sha256": plan_sha,
        "journal_head_sha256": start_head,
        "gate_kind": "run_start",
        "subject": {"kind": "run", "id": plan["run_id"], "sha256": plan_sha},
        "actor": {"kind": "human", "id": "owner", "session_id": "session-1", "authenticated_at": "2026-09-20T00:01:00Z"},
        "disposition": "continue",
        "rationale": "Reviewed the immutable plan and runtime boundary.",
        "evidence_ids": [],
        "occurred_at": "2026-09-20T00:01:00Z",
    }
    append("decision.recorded", {"kind": "human", "id": "owner"}, start_decision)
    append("run.started", {"kind": "human", "id": "owner"}, {"decision_id": "dec_start0001"})
    append("wave.started", {"kind": "system", "id": "scheduler"}, {"task_ids": ["T-100"]}, wave=1)
    worker_base = {
        "provider": "manual",
        "branch": plan["tasks"][0]["branch"],
        "worktree": plan["tasks"][0]["worktree"],
        "session_id": None,
        "process_id": None,
        "resume_token_sha256": None,
        "result_sha256": None,
        "event_ids": [],
        "evidence_ids": [],
    }
    append("worker.prepared", {"kind": "system", "id": "scheduler"}, {**worker_base, "status": "prepared"}, task_id="T-100", worker_id="worker-1", wave=1, attempt=1)
    append("worker.launched", {"kind": "worker", "id": "worker-1"}, {**worker_base, "status": "running"}, task_id="T-100", worker_id="worker-1", wave=1, attempt=1)
    append("worker.completed", {"kind": "worker", "id": "worker-1"}, {**worker_base, "status": "passed", "result_sha256": SHA}, task_id="T-100", worker_id="worker-1", wave=1, attempt=1)
    quick_action_sha = contract.digest(ACTION_INDEX["verify.quick"])
    append("check.completed", {"kind": "check", "id": "check-1"}, {"check_id": "check-1", "action_id": "verify.quick", "action_sha256": quick_action_sha, "commit": COMMIT, "status": "passed", "exit_code": 0, "result_sha256": SHA, "evidence_ids": []}, task_id="T-100")
    evidence_head = contract.digest(events[-1])
    evidence = {
        "schema_version": "1.0.0",
        "evidence_id": "evd_contract01",
        "run_id": plan["run_id"],
        "plan_sha256": plan_sha,
        "journal_head_sha256": evidence_head,
        "task_id": "T-100",
        "kind": "test",
        "collected_at": "2026-09-20T00:08:00Z",
        "producer": {"kind": "check", "id": "check-1", "session_id": None, "commit": COMMIT},
        "builder_id": "builder",
        "evaluator_id": "reviewer",
        "artifacts": [{"path": "proof.txt", "sha256": artifact_sha, "media_type": "text/plain"}],
        "check": {"name": "verify.quick", "command_sha256": quick_action_sha, "exit_code": 0, "started_at": "2026-09-20T00:07:00Z", "finished_at": "2026-09-20T00:08:00Z"},
        "verdict": "pass",
    }
    append("evidence.collected", {"kind": "check", "id": "check-1"}, evidence)
    append("wave.paused", {"kind": "system", "id": "scheduler"}, {"completed_task_ids": ["T-100"], "failed_task_ids": [], "evidence_ids": ["evd_contract01"], "gate_kind": "wave_continue"}, wave=1)
    decision_head = contract.digest(events[-1])
    wave_decision = {
        "schema_version": "1.0.0",
        "decision_id": "dec_contract01",
        "run_id": plan["run_id"],
        "plan_sha256": plan_sha,
        "journal_head_sha256": decision_head,
        "gate_kind": "wave_continue",
        "subject": {"kind": "wave", "id": "1", "sha256": contract.digest(events[-1])},
        "actor": {"kind": "human", "id": "owner", "session_id": "session-1", "authenticated_at": "2026-09-20T00:10:00Z"},
        "disposition": "continue",
        "rationale": "Reviewed checks and evidence.",
        "evidence_ids": ["evd_contract01"],
        "occurred_at": "2026-09-20T00:10:00Z",
    }
    append("decision.recorded", {"kind": "human", "id": "owner"}, wave_decision)
    reconciliation = {"checked_at": "2026-09-20T00:11:00Z", "git": "consistent", "worktrees": "consistent", "processes": "consistent", "checks": "consistent", "pull_requests": "consistent", "stale_running_count": 0}
    append("run.completed", {"kind": "system", "id": "reducer"}, {"status": "passed", "final_wave": 1, "worker_ids": ["worker-1"], "check_ids": ["check-1"], "evidence_ids": ["evd_contract01"], "decision_ids": ["dec_start0001", "dec_contract01"], "reconciliation_sha256": contract.digest(reconciliation)})
    return plan, events, reconciliation


class PrototypeParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.ids: set[str] = set()
        self.links: list[str] = []
        self.primary_by_section: dict[str, list[str]] = {}
        self.current_section: str | None = None
        self.scripts = 0

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        values = dict(attrs)
        if values.get("id"):
            self.ids.add(str(values["id"]))
        if tag == "section":
            self.current_section = values.get("id")
        if tag == "a" and values.get("href"):
            href = str(values["href"])
            self.links.append(href)
            if "primary" in set(str(values.get("class", "")).split()) and self.current_section:
                self.primary_by_section.setdefault(self.current_section, []).append(href)
        if tag == "script":
            self.scripts += 1

    def handle_endtag(self, tag: str) -> None:
        if tag == "section":
            self.current_section = None


class ProductToProofContractTests(unittest.TestCase):
    def setUp(self) -> None:
        self.contract = load_json(AGENTIC / "product-to-proof.json")
        self.schemas = {
            path.name: load_json(path)
            for path in sorted((AGENTIC / "schemas").glob("*.schema.json"))
        }

    def test_contract_is_versioned_and_all_references_exist(self) -> None:
        self.assertEqual(self.contract["schema_version"], "1.0.0")
        self.assertEqual(len(self.contract["contracts"]), 8)
        for relative_path in self.contract["contracts"].values():
            self.assertTrue((ROOT / relative_path).is_file(), relative_path)
        for schema in self.schemas.values():
            self.assertEqual(schema["$schema"], "https://json-schema.org/draft/2020-12/schema")
            self.assertTrue(schema["$id"].startswith("urn:everything-agentic-engineering:"))
            self.assertEqual(schema["type"], "object")
            self.assertFalse(schema["additionalProperties"])

    @unittest.skipUnless(Draft202012Validator, "jsonschema is not installed")
    def test_every_schema_is_valid_draft_2020_12(self) -> None:
        for name, schema in self.schemas.items():
            with self.subTest(name=name):
                Draft202012Validator.check_schema(schema)

    def test_studio_and_provider_contract_are_closed(self) -> None:
        self.assertEqual([stage["id"] for stage in self.contract["studio"]["stages"]], ["shape", "design", "build", "prove"])
        self.assertEqual(self.contract["studio"]["primary_action_policy"]["maximum_visible_primary_actions"], 1)
        self.assertEqual(self.contract["provider_contract"]["operations"], ["doctor", "prepare", "launch", "stream", "interrupt", "resume", "reconcile", "collect"])
        self.assertFalse(self.contract["provider_contract"]["silent_provider_switching"])
        self.assertTrue({"sandbox_bypass", "direct_main_write", "deployment", "self_approval", "merge"} <= set(self.contract["authority"]["forbidden_automatic_actions"]))

    def test_valid_plan_and_adversarial_dag_failures(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            contract.validate_record("plan", valid_plan(root), project_root=root, action_registry=ACTION_REGISTRY)

            duplicate = valid_plan(root)
            duplicate["tasks"][1]["task_id"] = "T-100"
            with self.assertRaisesRegex(contract.ContractError, "unique"):
                contract.validate_plan(duplicate, root, ACTION_REGISTRY)

            missing = valid_plan(root)
            missing["tasks"][1]["depends_on"] = ["T-999"]
            with self.assertRaisesRegex(contract.ContractError, "missing dependency"):
                contract.validate_plan(missing, root, ACTION_REGISTRY)

            cycle = valid_plan(root)
            cycle["tasks"][0]["depends_on"] = ["T-101"]
            with self.assertRaisesRegex(contract.ContractError, "cycle"):
                contract.validate_plan(cycle, root, ACTION_REGISTRY)

            overlap = valid_plan(root)
            overlap["tasks"][1]["writable_paths"] = ["src/alpha/file.ts"]
            with self.assertRaisesRegex(contract.ContractError, "collision"):
                contract.validate_plan(overlap, root, ACTION_REGISTRY)

            duplicate_wave = valid_plan(root)
            duplicate_wave["waves"][1]["task_ids"] = ["T-100", "T-101"]
            with self.assertRaisesRegex(contract.ContractError, "more than one wave"):
                contract.validate_plan(duplicate_wave, root, ACTION_REGISTRY)

            nonmaximal = valid_plan(root)
            nonmaximal["tasks"][1]["depends_on"] = []
            with self.assertRaisesRegex(contract.ContractError, "maximally filled"):
                contract.validate_plan(nonmaximal, root, ACTION_REGISTRY)

    def test_plan_rejects_root_mismatch_provider_drift_and_symlink_escape(self) -> None:
        with tempfile.TemporaryDirectory() as directory, tempfile.TemporaryDirectory() as outside:
            root = Path(directory)
            wrong_root = valid_plan(root)
            wrong_root["project_root"] = project_identity(Path(outside))
            with self.assertRaisesRegex(contract.ContractError, "unexpected project root"):
                contract.validate_plan(wrong_root, root, ACTION_REGISTRY)

            provider = valid_plan(root)
            provider["tasks"][0]["provider"] = "codex"
            with self.assertRaisesRegex(contract.ContractError, "provider not allowed"):
                contract.validate_plan(provider, root, ACTION_REGISTRY)

            default_alias = valid_plan(root)
            default_alias["tasks"][0]["branch"] = "refs/heads/main"
            with self.assertRaisesRegex(contract.ContractError, "default branch"):
                contract.validate_plan(default_alias, root, ACTION_REGISTRY)

            duplicate_worktree = valid_plan(root)
            duplicate_worktree["tasks"][1]["worktree"] = duplicate_worktree["tasks"][0]["worktree"]
            with self.assertRaisesRegex(contract.ContractError, "worktrees must be unique"):
                contract.validate_plan(duplicate_worktree, root, ACTION_REGISTRY)

            arbitrary_worktree = valid_plan(root)
            arbitrary_worktree["tasks"][0]["worktree"] = "/etc"
            with self.assertRaisesRegex(contract.ContractError, "reviewed parent"):
                contract.validate_plan(arbitrary_worktree, root, ACTION_REGISTRY)

            shell_check = valid_plan(root)
            shell_check["tasks"][0]["check_action_ids"] = ["sh -c deploy"]
            with self.assertRaisesRegex(contract.ContractError, "schema violation"):
                contract.validate_record("plan", shell_check, project_root=root, action_registry=ACTION_REGISTRY)

            (root / "escape").symlink_to(Path(outside), target_is_directory=True)
            escape = valid_plan(root)
            escape["tasks"][0]["writable_paths"] = ["escape/**"]
            with self.assertRaisesRegex(contract.ContractError, "outside|escapes"):
                contract.validate_plan(escape, root, ACTION_REGISTRY)

    def test_journal_chain_detects_unlinked_reordered_and_worker_authored_decision(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            plan, events, _ = completed_run(root)
            first, second = events[0], events[1]
            contract.validate_journal(events[:2], plan, ACTION_REGISTRY, project_root=root)
            contract.validate_journal(events[:2], plan, ACTION_REGISTRY, expected_head_sha256=contract.digest(second), expected_last_sequence=2, project_root=root)

            unlinked = copy.deepcopy(second)
            unlinked["previous_event_sha256"] = "c" * 64
            with self.assertRaisesRegex(contract.ContractError, "hash chain"):
                contract.validate_journal([first, unlinked], plan, ACTION_REGISTRY, project_root=root)

            with self.assertRaisesRegex(contract.ContractError, "first event|sequence"):
                contract.validate_journal([second, first], plan, ACTION_REGISTRY, project_root=root)

            with self.assertRaisesRegex(contract.ContractError, "truncated"):
                contract.validate_journal([first], plan, ACTION_REGISTRY, expected_head_sha256=contract.digest(second), expected_last_sequence=2, project_root=root)

            worker_decision = copy.deepcopy(second)
            worker_decision["actor"] = {"kind": "worker", "id": "worker-1"}
            with self.assertRaisesRegex(contract.ContractError, "actor must be human"):
                contract.validate_journal([first, worker_decision], plan, ACTION_REGISTRY, project_root=root)

            started_without_decision = copy.deepcopy(events[2])
            started_without_decision["sequence"] = 2
            started_without_decision["previous_event_sha256"] = contract.digest(first)
            with self.assertRaisesRegex(contract.ContractError, "missing human decision"):
                contract.validate_journal([first, started_without_decision], plan, ACTION_REGISTRY, project_root=root)

    def test_journal_binds_evidence_decision_and_replays_completed_state(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            plan, events, reconciliation = completed_run(root)

            with self.assertRaisesRegex(contract.ContractError, "canonical project root"):
                contract.validate_record("journal", events, plan=plan, action_registry=ACTION_REGISTRY)
            projection = contract.validate_record("journal", events, plan=plan, action_registry=ACTION_REGISTRY, project_root=root)
            state = {**projection, "schema_version": "1.0.0", "reducer_version": "1.0.0", "updated_at": "2026-09-20T00:11:00Z", "reconciliation": reconciliation}
            contract.validate_record("state", state, journal_projection=projection)

            Path(plan["tasks"][0]["worktree"]).mkdir()
            replay_with_live_worktree = contract.validate_record("journal", events, plan=plan, action_registry=ACTION_REGISTRY, project_root=root)
            self.assertEqual(replay_with_live_worktree, projection)

            foreign = copy.deepcopy(events)
            foreign[8]["payload"]["run_id"] = "run_foreign001"
            foreign[9]["previous_event_sha256"] = contract.digest(foreign[8])
            with self.assertRaisesRegex(contract.ContractError, "another run"):
                contract.validate_journal(foreign, plan, ACTION_REGISTRY, project_root=root)

            stale = copy.deepcopy(events)
            stale[10]["payload"]["journal_head_sha256"] = SHA
            stale[11]["previous_event_sha256"] = contract.digest(stale[10])
            with self.assertRaisesRegex(contract.ContractError, "stale journal head"):
                contract.validate_journal(stale, plan, ACTION_REGISTRY, project_root=root)

            missing = copy.deepcopy(events)
            missing[10]["payload"]["evidence_ids"] = ["evd_missing001"]
            missing[11]["previous_event_sha256"] = contract.digest(missing[10])
            with self.assertRaisesRegex(contract.ContractError, "missing evidence"):
                contract.validate_journal(missing, plan, ACTION_REGISTRY, project_root=root)

            (root / "proof.txt").write_text("tampered")
            with self.assertRaisesRegex(contract.ContractError, "digest mismatch"):
                contract.validate_journal(events, plan, ACTION_REGISTRY, project_root=root)

    def test_forged_completion_and_unregistered_actions_fail_closed(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            plan, events, _ = completed_run(root)

            forged_task = copy.deepcopy(events)
            forged_task[3]["payload"]["task_ids"] = ["T-999"]
            with self.assertRaisesRegex(contract.ContractError, "immutable plan"):
                contract.validate_record("journal", forged_task, plan=plan, action_registry=ACTION_REGISTRY, project_root=root)

            failed_check = copy.deepcopy(events)
            failed_check[7]["payload"]["status"] = "failed"
            failed_check[7]["payload"]["exit_code"] = 1
            failed_check[8]["payload"]["journal_head_sha256"] = contract.digest(failed_check[7])
            for index in range(8, len(failed_check)):
                failed_check[index]["previous_event_sha256"] = contract.digest(failed_check[index - 1])
            with self.assertRaisesRegex(contract.ContractError, "passing checks|only passing checks|evidence exit code"):
                contract.validate_record("journal", failed_check, plan=plan, action_registry=ACTION_REGISTRY, project_root=root)

            failed_evidence = copy.deepcopy(events)
            failed_evidence[8]["payload"]["verdict"] = "fail"
            for index in range(9, len(failed_evidence)):
                failed_evidence[index]["previous_event_sha256"] = contract.digest(failed_evidence[index - 1])
            with self.assertRaisesRegex(contract.ContractError, "passing evidence|only passing evidence"):
                contract.validate_record("journal", failed_evidence, plan=plan, action_registry=ACTION_REGISTRY, project_root=root)

            mismatched_evidence = copy.deepcopy(events)
            mismatched_evidence[8]["payload"]["check"]["name"] = "some-unrelated-command"
            mismatched_evidence[8]["payload"]["check"]["command_sha256"] = SHA
            for index in range(9, len(mismatched_evidence)):
                mismatched_evidence[index]["previous_event_sha256"] = contract.digest(mismatched_evidence[index - 1])
            with self.assertRaisesRegex(contract.ContractError, "another check action|command digest"):
                contract.validate_record("journal", mismatched_evidence, plan=plan, action_registry=ACTION_REGISTRY, project_root=root)

            unknown_action = valid_plan(root)
            unknown_action["tasks"][0]["allowed_action_ids"] = ["deploy.production", "git.push.main"]
            with self.assertRaisesRegex(contract.ContractError, "unknown action ids"):
                contract.validate_record("plan", unknown_action, project_root=root, action_registry=ACTION_REGISTRY)

    def test_generic_human_gate_decision_must_match_exact_subject(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            plan, completed_events, _ = completed_run(root)
            for gate_kind, event_type, subject_kind, disposition in (
                ("integration", "run.paused", "integration", "approve"),
                ("diagnosis", "run.needs_human", "failure", "acknowledge"),
            ):
                with self.subTest(gate_kind=gate_kind):
                    events = copy.deepcopy(completed_events[:3])
                    checkpoint = {
                        "schema_version": "1.0.0",
                        "sequence": 4,
                        "event_id": f"evt_{gate_kind}01",
                        "run_id": plan["run_id"],
                        "plan_sha256": contract.digest(plan),
                        "occurred_at": "2026-09-20T00:03:00Z",
                        "type": event_type,
                        "actor": {"kind": "system", "id": "reducer"},
                        "previous_event_sha256": contract.digest(events[-1]),
                        "payload": {"reason": "review required", "gate_kind": gate_kind},
                    }
                    events.append(checkpoint)
                    decision = {
                        "schema_version": "1.0.0",
                        "decision_id": f"dec_{gate_kind}01",
                        "run_id": plan["run_id"],
                        "plan_sha256": contract.digest(plan),
                        "journal_head_sha256": contract.digest(checkpoint),
                        "gate_kind": gate_kind,
                        "subject": {"kind": subject_kind, "id": "completely-unrelated", "sha256": SHA},
                        "actor": {"kind": "human", "id": "owner", "session_id": "session-1", "authenticated_at": "2026-09-20T00:04:00Z"},
                        "disposition": disposition,
                        "rationale": "Reviewed the checkpoint.",
                        "evidence_ids": [],
                        "occurred_at": "2026-09-20T00:04:00Z",
                    }
                    events.append({"schema_version": "1.0.0", "sequence": 5, "event_id": f"evt_{gate_kind}02", "run_id": plan["run_id"], "plan_sha256": contract.digest(plan), "occurred_at": "2026-09-20T00:04:00Z", "type": "decision.recorded", "actor": {"kind": "human", "id": "owner"}, "previous_event_sha256": contract.digest(checkpoint), "payload": decision})
                    with self.assertRaisesRegex(contract.ContractError, "another gate subject"):
                        contract.validate_record("journal", events, plan=plan, action_registry=ACTION_REGISTRY, project_root=root)

    def test_authoritative_entry_point_schema_checks_before_semantics(self) -> None:
        incomplete_decision = {"schema_version": "1.0.0", "actor": {"kind": "human", "id": "owner", "session_id": "session", "authenticated_at": "2026-09-20T00:00:00Z"}, "rationale": "reviewed"}
        with self.assertRaisesRegex(contract.ContractError, "schema violation"):
            contract.validate_record("decision", incomplete_decision)

        unsafe_evidence = {"schema_version": "1.0.0", "evidence_id": "evd_contract01", "run_id": "run_contract01", "plan_sha256": SHA, "journal_head_sha256": SHA, "kind": "test", "collected_at": "2026-09-20T00:00:00Z", "producer": {"kind": "check", "id": "check-1", "session_id": None, "commit": COMMIT}, "builder_id": "builder", "evaluator_id": "reviewer", "artifacts": [{"path": "/etc/passwd", "sha256": SHA, "media_type": "text/plain"}], "check": {"name": "unit", "command_sha256": SHA, "exit_code": 0, "started_at": "2026-09-20T00:00:00Z", "finished_at": "2026-09-20T00:01:00Z"}, "verdict": "pass"}
        with self.assertRaisesRegex(contract.ContractError, "schema violation"):
            contract.validate_record("evidence", unsafe_evidence)

    @unittest.skipUnless(Draft202012Validator, "jsonschema is not installed")
    def test_adapter_resume_requires_exact_target_and_action_registry(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            plan = valid_plan(root)
            task_record = plan["tasks"][0]
            operation = {
                "schema_version": "1.0.0",
                "operation_id": "op_contract01",
                "run_id": plan["run_id"],
                "task_id": task_record["task_id"],
                "worker_id": "worker-1",
                "operation": "resume",
                "request": {"provider": task_record["provider"], "provider_version": task_record["provider_version"], "capabilities": task_record["capability_ids"], "plan_sha256": contract.digest(plan), "worktree": task_record["worktree"], "branch": task_record["branch"], "writable_paths": task_record["writable_paths"], "action_ids": ["verify.quick"], "action_registry_sha256": contract.digest(ACTION_REGISTRY), "permission_policy_sha256": plan["runtime_policy"]["permissions"]["policy_sha256"], "invocation_sha256": task_record["invocation_sha256"], "timeout_seconds": task_record["timeout_seconds"], "target": {"session_id": None, "process_id": None, "checkpoint_event_id": None, "journal_head_sha256": None, "resume_token_sha256": None}},
                "outcome": {"status": "unsupported", "session_id": None, "process_id": None, "resume_token_sha256": None, "events": [], "evidence_ids": [], "error": {"code": "protocol", "message": "No checkpoint", "retryable": False}},
            }
            with self.assertRaises(contract.ContractError):
                contract.validate_record("adapter", operation, action_registry=ACTION_REGISTRY, plan=plan, project_root=root)

            unsafe_capability = copy.deepcopy(operation)
            unsafe_capability["operation"] = "launch"
            unsafe_capability["request"]["capabilities"] = ["sandbox_bypass", "network:any", "mcp:*"]
            with self.assertRaisesRegex(contract.ContractError, "schema violation|capabilities differ"):
                contract.validate_record("adapter", unsafe_capability, action_registry=ACTION_REGISTRY, plan=plan, project_root=root)

            operation["operation"] = "launch"
            operation["request"]["action_ids"] = ["git.push.main"]
            with self.assertRaisesRegex(contract.ContractError, "exceed|unknown action ids"):
                contract.validate_record("adapter", operation, action_registry=ACTION_REGISTRY, plan=plan, project_root=root)

            forged = copy.deepcopy(operation)
            forged["task_id"] = "T-999"
            forged["request"].update({"action_ids": [], "plan_sha256": SHA, "branch": "main", "worktree": "/tmp/unreviewed", "writable_paths": ["**"]})
            with self.assertRaisesRegex(contract.ContractError, "another plan|absent from the immutable plan"):
                contract.validate_record("adapter", forged, action_registry=ACTION_REGISTRY, plan=plan, project_root=root)

            resume_plan = valid_plan(root)
            resume_task = resume_plan["tasks"][0]
            resume_task["provider"] = "claude-code"
            resume_task["provider_version"] = "2.1.278"
            resume_task["capability_ids"] = ["structured_stream", "session_resume", "process_interrupt", "checkpoint_resume", "workspace_write", "network_disabled", "mcp_disabled"]
            resume_plan["runtime_policy"]["allowed_providers"] = ["manual", "claude-code"]
            resume_operation = copy.deepcopy(operation)
            resume_operation["operation"] = "resume"
            resume_operation["request"].update({"provider": "claude-code", "provider_version": "2.1.278", "capabilities": resume_task["capability_ids"], "plan_sha256": contract.digest(resume_plan), "action_ids": ["verify.quick"], "target": {"session_id": "session-forged", "process_id": None, "checkpoint_event_id": None, "journal_head_sha256": None, "resume_token_sha256": "d" * 64}})
            projection = {"run_id": resume_plan["run_id"], "plan_sha256": contract.digest(resume_plan), "journal_head_sha256": "e" * 64, "journal_head_event_id": "evt_checkpoint01", "workers": [{"worker_id": "worker-1", "task_id": "T-100", "session_id": "session-recorded", "process_id": 1234, "resume_token_sha256": "c" * 64}]}
            with self.assertRaisesRegex(contract.ContractError, "session target|resume token"):
                contract.validate_record("adapter", resume_operation, action_registry=ACTION_REGISTRY, plan=resume_plan, project_root=root, journal_projection=projection)

    def test_unsafe_completed_state_and_self_evaluated_evidence_fail(self) -> None:
        contract.validate_state(valid_state())
        unsafe = valid_state()
        unsafe["evidence"]["complete"] = False
        unsafe["reconciliation"]["git"] = "drifted"
        unsafe["reconciliation"]["stale_running_count"] = 2
        unsafe["human_gate"] = {"required": True, "kind": "merge", "decision_event_id": None}
        with self.assertRaises(contract.ContractError):
            contract.validate_state(unsafe)

        evidence = {"schema_version": "1.0.0", "builder_id": "same", "evaluator_id": "same", "artifacts": [{"path": "proof.txt"}], "check": {"exit_code": 0}, "verdict": "pass"}
        with self.assertRaisesRegex(contract.ContractError, "must differ"):
            contract.validate_evidence(evidence)

    def test_passing_benchmark_cannot_hide_violations_or_unknown_measurements(self) -> None:
        benchmark = valid_benchmark()
        contract.validate_record("benchmark", benchmark)
        violated = copy.deepcopy(benchmark)
        violated["violations"] = [{"code": "direct-main-write", "summary": "unsafe", "blocking": True, "artifact_sha256": None}]
        with self.assertRaisesRegex(contract.ContractError, "violations"):
            contract.validate_benchmark(violated)
        ambiguous = copy.deepcopy(benchmark)
        ambiguous["measurements"]["active_minutes"] = {"value": None, "unknown_reason": None}
        with self.assertRaisesRegex(contract.ContractError, "value or an unknown reason"):
            contract.validate_benchmark(ambiguous)
        unknown = copy.deepcopy(benchmark)
        unknown["measurements"]["active_minutes"] = {"value": None, "unknown_reason": "clock unavailable"}
        with self.assertRaisesRegex(contract.ContractError, "unknown active_minutes"):
            contract.validate_benchmark(unknown)

    @unittest.skipUnless(Draft202012Validator, "jsonschema is not installed")
    def test_schema_conditionals_reject_unsafe_completed_and_passing_violation(self) -> None:
        state_schema = self.schemas["run-state.schema.json"]
        benchmark_schema = self.schemas["benchmark-result.schema.json"]
        Draft202012Validator(state_schema).validate(valid_state())
        Draft202012Validator(benchmark_schema).validate(valid_benchmark())

        unsafe = valid_state()
        unsafe["reconciliation"]["git"] = "unknown"
        self.assertFalse(Draft202012Validator(state_schema).is_valid(unsafe))
        violated = valid_benchmark()
        violated["violations"] = [{"code": "credential-exposure", "summary": "secret", "blocking": True, "artifact_sha256": None}]
        self.assertFalse(Draft202012Validator(benchmark_schema).is_valid(violated))
        unknown_time = valid_benchmark()
        unknown_time["measurements"]["wall_minutes"] = {"value": None, "unknown_reason": "clock unavailable"}
        self.assertFalse(Draft202012Validator(benchmark_schema).is_valid(unknown_time))

    @unittest.skipUnless(Draft202012Validator and Registry and Resource, "schema registry support is not installed")
    def test_external_event_references_resolve_and_enforce_human_actor(self) -> None:
        registry = Registry().with_resources(
            (schema["$id"], Resource.from_contents(schema))
            for schema in self.schemas.values()
        )
        validator = Draft202012Validator(self.schemas["run-event.schema.json"], registry=registry)
        decision = {
            "schema_version": "1.0.0",
            "decision_id": "dec_contract01",
            "run_id": "run_contract01",
            "plan_sha256": SHA,
            "journal_head_sha256": SHA,
            "gate_kind": "wave_continue",
            "subject": {"kind": "wave", "id": "1", "sha256": SHA},
            "actor": {"kind": "human", "id": "reviewer-1", "session_id": "session-1", "authenticated_at": "2026-09-20T00:00:00Z"},
            "disposition": "continue",
            "rationale": "Reviewed the wave boundary and evidence.",
            "evidence_ids": ["evd_contract01"],
            "occurred_at": "2026-09-20T00:00:00Z",
        }
        event = {
            "schema_version": "1.0.0",
            "sequence": 2,
            "event_id": "evt_contract01",
            "run_id": "run_contract01",
            "plan_sha256": SHA,
            "occurred_at": "2026-09-20T00:00:00Z",
            "type": "decision.recorded",
            "actor": {"kind": "human", "id": "reviewer-1"},
            "previous_event_sha256": SHA,
            "payload": decision,
        }
        validator.validate(event)
        event["actor"] = {"kind": "worker", "id": "worker-1"}
        self.assertFalse(validator.is_valid(event))

    def test_static_prototype_models_all_flows_and_routes_blockers_to_owner(self) -> None:
        path = ROOT / "docs/20-design/prototypes/product-to-proof-studio.html"
        parser = PrototypeParser()
        contents = path.read_text()
        parser.feed(contents)
        expected_states = {"shape", "design-blocked", "design-ready", "build-boundary", "wave-paused", "recovery", "dependency", "prove"}
        self.assertEqual(parser.scripts, 0)
        self.assertTrue(expected_states <= parser.ids)
        self.assertTrue(all(len(parser.primary_by_section.get(state, [])) == 1 for state in expected_states))
        for href in [link for link in parser.links if link.startswith("#")]:
            self.assertIn(href[1:], parser.ids)
        self.assertEqual(parser.primary_by_section["design-blocked"], ["#shape"])
        self.assertEqual(parser.primary_by_section["design-ready"], ["#build-boundary"])
        self.assertEqual(parser.primary_by_section["build-boundary"], ["#wave-paused"])
        self.assertIn("#shape:not(:target)", contents)
        self.assertIn("class=\"skip\"", contents)
        self.assertIn(":focus-visible", contents)

    def test_docs_do_not_claim_unimplemented_control_plane_or_results(self) -> None:
        product = (ROOT / "docs/10-product/PRODUCT_TO_PROOF_STUDIO.md").read_text()
        benchmark = (ROOT / "docs/50-evals/PRODUCT_TO_PROOF_BENCHMARK.md").read_text()
        mobile = (ROOT / "docs/10-product/SIGNALROOM_CROSS_PLATFORM_JOURNEY.md").read_text()
        self.assertIn("does not claim", product)
        self.assertIn("no comparative results have been run or claimed", benchmark)
        self.assertIn("may not finalize or\nqueue an approval", mobile)

    def test_task_traceability_is_present(self) -> None:
        rows = [json.loads(line) for line in (ROOT / "docs/40-execution/TASKS.jsonl").read_text().splitlines() if line]
        task_record = next(row for row in rows if row["id"] == "T-054")
        self.assertEqual(task_record["tracking"], {"mode": "required", "issues": ["#87"]})
        self.assertEqual(task_record["depends_on"], ["T-053"])
        self.assertIn("FR-009", task_record["requirement_ids"])
        self.assertIn("AC-009", task_record["acceptance_ids"])


if __name__ == "__main__":
    unittest.main()
