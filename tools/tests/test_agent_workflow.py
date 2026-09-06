"""Synthetic Git repositories only; never dispatch a real agent."""
import copy
import concurrent.futures
import contextlib
import io
import json
import pathlib
import re
import subprocess
import tempfile
import threading
import unittest

import agent_workflow as workflow


class AgentWorkflowTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = pathlib.Path(self.temp.name)
        self.git("init", "-q")
        self.file(".github/copilot-instructions.md", "Synthetic instructions\n")
        self.file("docs/work-execution.md", "Synthetic execution contract\n")
        self.file("tools/agent_workflow.py", "# Synthetic adopted guard\n")
        for role in ("hardware-lead", "circuit-engineer", "hardware-reviewer"):
            self.file(f".github/agents/{role}.agent.md", "Synthetic role\n")
        self.file("requirements/input.txt", "Synthetic input A\n")
        self.sha = self.commit()
        self.contract = {
            "schema_version": 1,
            "id": "example-interface",
            "owner": "circuit-engineer",
            "objective": "Resolve the synthetic interface",
            "source_revision": self.sha,
            "config_revision": self.sha,
            "inputs": ["requirements/input.txt"],
            "writes": ["output"],
            "deliverables": ["output/handoff.txt"],
            "done_when": "Record the interface decision and its limitations",
            "stop_when": "A required source or human decision is unavailable",
            "depends_on": [],
        }

    def git(self, *args):
        return subprocess.run(
            ["git", *args], cwd=self.root, check=True, capture_output=True, text=True
        ).stdout.strip()

    def file(self, name, contents):
        path = self.root / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(contents, encoding="utf-8")
        return path

    def commit(self):
        self.git("add", ".")
        self.git("-c", "user.name=Fixture", "-c", "user.email=fixture@example.invalid",
                 "commit", "-qm", "Synthetic snapshot")
        return self.git("rev-parse", "HEAD")

    def test_snapshot_uses_relevant_content_not_whole_commit(self):
        first = workflow.validate_contract(self.root, self.contract)
        self.file("unrelated.txt", "Unrelated change\n")
        self.contract["source_revision"] = self.commit()
        self.assertEqual(first, workflow.validate_contract(self.root, self.contract))

    def test_input_drift_is_rejected(self):
        self.file("requirements/input.txt", "Uncommitted drift\n")
        with self.assertRaisesRegex(workflow.WorkflowError, "input differs"):
            workflow.validate_contract(self.root, self.contract)

    def test_configuration_drift_is_rejected(self):
        self.file(".github/copilot-instructions.md", "Changed instructions\n")
        with self.assertRaisesRegex(workflow.WorkflowError, "configuration differs"):
            workflow.validate_contract(self.root, self.contract)

    def test_root_agent_guide_is_part_of_pinned_configuration(self):
        self.file("AGENTS.md", "Synthetic contributor entry point\n")
        self.contract["config_revision"] = self.contract["source_revision"] = self.commit()
        self.file("AGENTS.md", "Changed contributor instructions\n")
        with self.assertRaisesRegex(workflow.WorkflowError, "configuration differs"):
            workflow.validate_contract(self.root, self.contract)

    def test_legacy_checkout_without_execution_contract_cannot_be_reserved(self):
        self.git("rm", "-q", "docs/work-execution.md", "tools/agent_workflow.py")
        self.contract["config_revision"] = self.contract["source_revision"] = self.commit()
        with self.assertRaisesRegex(workflow.WorkflowError, "missing adopted configuration"):
            workflow.start(self.root, self.contract, "parent-session")

    def test_contract_rejects_missing_fields_and_unsafe_paths(self):
        for key in ("done_when", "stop_when", "config_revision"):
            with self.subTest(key=key):
                data = copy.deepcopy(self.contract)
                del data[key]
                with self.assertRaises(workflow.WorkflowError):
                    workflow.validate_contract(self.root, data)
        for name in ("../outside", "/tmp/outside", ".git/config", "output/*"):
            with self.subTest(path=name):
                data = copy.deepcopy(self.contract)
                data["writes"] = [name]
                with self.assertRaises(workflow.WorkflowError):
                    workflow.validate_contract(self.root, data)

    def test_shared_ledgers_require_the_serial_publisher(self):
        self.contract["writes"] = ["validation"]
        self.contract["deliverables"] = ["validation/open-issues.md"]
        with self.assertRaisesRegex(workflow.WorkflowError, "shared ledger"):
            workflow.validate_contract(self.root, self.contract)

    def test_running_task_cannot_be_dispatched_twice(self):
        run = workflow.start(self.root, self.contract, "parent-session")
        self.assertEqual(run["state"], "RUNNING")
        with self.assertRaisesRegex(workflow.WorkflowError, "already RUNNING"):
            workflow.start(self.root, self.contract, "another-session")

    def test_write_scopes_cannot_overlap_even_for_different_tasks(self):
        workflow.start(self.root, self.contract, "parent-session")
        other = copy.deepcopy(self.contract)
        other["id"] = "another-interface"
        other["writes"] = ["output/child"]
        other["deliverables"] = ["output/child/result.txt"]
        with self.assertRaisesRegex(workflow.WorkflowError, "write conflict"):
            workflow.start(self.root, other, "another-session")
        other["writes"] = ["separate"]
        other["deliverables"] = ["separate/result.txt"]
        self.assertEqual(workflow.start(self.root, other, "another-session")["state"],
                         "RUNNING")

    def test_other_worktree_shares_the_same_dispatch_guard(self):
        workflow.start(self.root, self.contract, "parent-session")
        other = self.root / "linked-worktree"
        self.git("worktree", "add", "--detach", str(other), self.sha)
        self.assertEqual(workflow.state_path(self.root), workflow.state_path(other))
        with self.assertRaisesRegex(workflow.WorkflowError, "already RUNNING"):
            workflow.start(other, self.contract, "other-app-session")

    def close(self, run, state="BLOCKED"):
        return workflow.finish(self.root, run["run_id"], "parent-session", state,
                               "Synthetic outcome", "Wait for changed source")

    def test_blocked_task_rejects_unchanged_inputs_and_unrelated_commits(self):
        self.close(workflow.start(self.root, self.contract, "parent-session"))
        for unrelated_commit in (False, True):
            with self.subTest(unrelated_commit=unrelated_commit):
                if unrelated_commit:
                    self.file("unrelated.txt", "Unrelated update\n")
                    self.contract["source_revision"] = self.commit()
                with self.assertRaisesRegex(workflow.WorkflowError, "unchanged inputs"):
                    workflow.start(self.root, self.contract, "parent-session")
        self.file("requirements/input.txt", "Relevant new decision B\n")
        self.contract["source_revision"] = self.commit()
        self.assertEqual(workflow.start(self.root, self.contract, "parent-session")["state"],
                         "RUNNING")

    def test_done_requires_saved_deliverables_and_also_prevents_redispatch(self):
        run = workflow.start(self.root, self.contract, "parent-session")
        with self.assertRaisesRegex(workflow.WorkflowError, "missing deliverable"):
            self.close(run, "DONE")
        self.file("output/handoff.txt", "Saved bounded result, not design approval\n")
        result = self.close(run, "DONE")
        self.assertEqual(result["state"], "DONE")
        self.assertEqual(len(result["artifacts"]), 1)
        with self.assertRaisesRegex(workflow.WorkflowError, "unchanged inputs"):
            workflow.start(self.root, self.contract, "new-parent-session")

    def test_only_the_recorded_session_can_close_a_running_attempt(self):
        run = workflow.start(self.root, self.contract, "parent-session")
        with self.assertRaisesRegex(workflow.WorkflowError, "session"):
            workflow.finish(self.root, run["run_id"], "another-session", "BLOCKED",
                            "Do not close another owner", "Wait")
        self.close(run)
        with self.assertRaisesRegex(workflow.WorkflowError, "not RUNNING"):
            self.close(run)

    def test_done_dependency_requires_unchanged_saved_artifacts(self):
        parent = workflow.start(self.root, self.contract, "parent-session")
        downstream = copy.deepcopy(self.contract)
        downstream.update(id="downstream-review", owner="hardware-reviewer",
                          writes=["review"], deliverables=["review/handoff.txt"],
                          depends_on=[self.contract["id"]])
        with self.assertRaisesRegex(workflow.WorkflowError, "dependency not DONE"):
            workflow.start(self.root, downstream, "review-session")
        self.file("output/handoff.txt", "Saved result\n")
        self.close(parent, "DONE")
        self.file("output/handoff.txt", "Changed result without a new handoff\n")
        with self.assertRaisesRegex(workflow.WorkflowError, "dependency artifacts changed"):
            workflow.start(self.root, downstream, "review-session")
        self.file("output/handoff.txt", "Saved result\n")
        self.assertEqual(workflow.start(self.root, downstream, "review-session")["state"],
                         "RUNNING")

    def test_work_status_cannot_be_used_as_physical_approval(self):
        run = workflow.start(self.root, self.contract, "parent-session")
        for state in ("APPROVED", "DESIGN_COMPLETE", "ACCEPTED-RISK"):
            with self.subTest(state=state):
                with self.assertRaises(workflow.WorkflowError):
                    workflow.finish(self.root, run["run_id"], "parent-session", state,
                                    "Not a safety decision", "Keep holds")

    def cli(self, *args):
        output, errors = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(output), contextlib.redirect_stderr(errors):
            code = workflow.main(["--repo", str(self.root), *args])
        return code, output.getvalue(), errors.getvalue()

    def test_cli_records_progress_and_finishes_without_launching_an_agent(self):
        path = self.file("contract.json", json.dumps(self.contract))
        code, output, errors = self.cli("start", str(path), "--session", "parent-session")
        self.assertEqual((code, errors), (0, ""))
        run = json.loads(output)["result"]["run_id"]
        code, _, errors = self.cli(
            "progress", run, "--session", "parent-session",
            "--summary", "Worker returned one result",
            "--next-action", "Save the bounded handoff; completion estimate unknown",
        )
        self.assertEqual((code, errors), (0, ""))
        _, output, _ = self.cli("status")
        self.assertIn("Worker returned one result", output)
        code, _, errors = self.cli(
            "finish", run, "--session", "parent-session", "--state", "BLOCKED",
            "--summary", "Awaiting source decision", "--next-action", "Wait; do not redispatch",
        )
        self.assertEqual((code, errors), (0, ""))
        code, _, errors = self.cli("start", str(path), "--session", "parent-session")
        self.assertEqual(code, 2)
        self.assertIn("unchanged inputs", errors)

    def test_status_read_does_not_create_a_database(self):
        self.assertEqual(workflow.status(self.root), [])
        self.assertFalse(workflow.state_path(self.root).exists())

    def test_unknown_dependency_and_untracked_configuration_fail_closed(self):
        self.contract["depends_on"] = ["missing-task"]
        with self.assertRaisesRegex(workflow.WorkflowError, "dependency not DONE"):
            workflow.start(self.root, self.contract, "parent-session")
        self.contract["depends_on"] = []
        self.file(".github/agents/uncommitted.agent.md", "Uncommitted configuration\n")
        with self.assertRaisesRegex(workflow.WorkflowError, "configuration differs"):
            workflow.start(self.root, self.contract, "parent-session")
        self.assertEqual(workflow.status(self.root), [])

    def test_cli_reports_invalid_json_instead_of_claiming_success(self):
        path = self.file("invalid.json", "{")
        code, output, errors = self.cli("start", str(path), "--session", "parent-session")
        self.assertEqual((code, output), (2, ""))
        self.assertIn("Workflow refused:", errors)

    def test_simultaneous_claims_admit_only_one_worker(self):
        barrier = threading.Barrier(2)

        def claim():
            barrier.wait(timeout=5)
            try:
                workflow.start(self.root, self.contract, "parent-session")
                return "reserved"
            except workflow.WorkflowError as exc:
                return str(exc)

        with concurrent.futures.ThreadPoolExecutor(max_workers=2) as workers:
            results = list(workers.map(lambda _: claim(), range(2)))
        self.assertEqual(results.count("reserved"), 1)
        self.assertEqual(len(workflow.status(self.root)), 1)
        self.assertTrue(any("already RUNNING" in value for value in results))

    def test_history_prevents_replaying_an_older_blocked_input(self):
        self.close(workflow.start(self.root, self.contract, "parent-session"))
        original = copy.deepcopy(self.contract)
        self.file("requirements/input.txt", "Relevant B\n")
        self.contract["source_revision"] = self.commit()
        self.close(workflow.start(self.root, self.contract, "parent-session"))
        self.file("requirements/input.txt", "Synthetic input A\n")
        with self.assertRaisesRegex(workflow.WorkflowError, "unchanged inputs"):
            workflow.start(self.root, original, "new-session")
        self.assertEqual(len(workflow.status(self.root)), 1)
        self.assertEqual(len(workflow.status(self.root, history=True)), 2)

    def test_shared_publication_is_serial_even_for_different_ledgers(self):
        self.contract.update(owner="hardware-lead", writes=["validation/open-issues.md"],
                             deliverables=["validation/open-issues.md"])
        workflow.start(self.root, self.contract, "parent-session")
        other = copy.deepcopy(self.contract)
        other.update(id="publish-evidence", writes=["datasheets/evidence-log.md"],
                     deliverables=["datasheets/evidence-log.md"])
        with self.assertRaisesRegex(workflow.WorkflowError, "shared ledger publisher"):
            workflow.start(self.root, other, "another-lead-session")

    def test_active_input_cannot_be_changed_by_another_reserved_writer(self):
        workflow.start(self.root, self.contract, "parent-session")
        other = copy.deepcopy(self.contract)
        other.update(id="input-edit", writes=["requirements/input.txt"],
                     deliverables=["requirements/input.txt"])
        with self.assertRaisesRegex(workflow.WorkflowError, "input/write conflict"):
            workflow.start(self.root, other, "another-session")

    def test_reader_in_another_frozen_worktree_can_continue(self):
        workflow.start(self.root, self.contract, "parent-session")
        other_root = self.root / "frozen-worktree"
        self.git("worktree", "add", "--detach", str(other_root), self.sha)
        other = copy.deepcopy(self.contract)
        other.update(id="input-edit", writes=["requirements/input.txt"],
                     deliverables=["requirements/input.txt"])
        self.assertEqual(workflow.start(other_root, other, "another-session")["state"],
                         "RUNNING")

    def test_corrupt_state_is_reported_not_reset(self):
        path = workflow.state_path(self.root)
        path.parent.mkdir(parents=True)
        path.write_bytes(b"not a sqlite database")
        code, output, errors = self.cli("status")
        self.assertEqual((code, output), (2, ""))
        self.assertIn("Workflow refused:", errors)
        self.assertEqual(path.read_bytes(), b"not a sqlite database")

    def test_case_aliases_do_not_bypass_write_scope_conflicts(self):
        workflow.start(self.root, self.contract, "parent-session")
        other = copy.deepcopy(self.contract)
        other.update(id="case-alias", writes=["OUTPUT"], deliverables=["OUTPUT/other.txt"])
        with self.assertRaisesRegex(workflow.WorkflowError, "write conflict"):
            workflow.start(self.root, other, "another-session")

    def test_symlinked_scope_cannot_alias_another_owner_path(self):
        (self.root / "output").mkdir()
        (self.root / "alias").symlink_to(self.root / "output", target_is_directory=True)
        self.contract.update(writes=["alias"], deliverables=["alias/handoff.txt"])
        with self.assertRaisesRegex(workflow.WorkflowError, "symlink"):
            workflow.start(self.root, self.contract, "parent-session")

    def test_documented_contract_is_usable_with_real_snapshot_ids(self):
        doc = pathlib.Path(__file__).resolve().parents[2] / "docs/work-execution.md"
        block = re.search(r"```json\n(.*?)\n```", doc.read_text(encoding="utf-8"), re.DOTALL)
        self.assertIsNotNone(block)
        data = json.loads(block.group(1))
        self.file("requirements/requirements.md", "Synthetic scoped requirements\n")
        data["source_revision"] = data["config_revision"] = self.commit()
        self.assertEqual(workflow.start(self.root, data, "example-session")["state"], "RUNNING")


if __name__ == "__main__":
    unittest.main()
