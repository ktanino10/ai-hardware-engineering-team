"""Synthetic unit fixtures only; native trials require the explicit experiment CLI."""
from __future__ import annotations

import contextlib
import copy
import io
import json
import os
from pathlib import Path
import shutil
import signal
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import Mock, patch

import engineering_harness as harness
from engineering_harness_adapters import kicad


FIXTURES = Path(__file__).parent / "fixtures" / "engineering_harness"
TOOL = kicad.ToolIdentity("a" * 64, "10.0.1")


@contextlib.contextmanager
def interrupt_owned_wait(use_sigint=True):
    real_popen = subprocess.Popen
    owned = []

    def start(*args, **kwargs):
        child = real_popen(*args, **kwargs)
        if args[0][0] == sys.executable and not owned:
            owned.append(child)
            real_wait = child.wait

            def interrupt(timeout=None):
                child.wait = real_wait
                if use_sigint:
                    os.kill(os.getpid(), signal.SIGINT)
                raise KeyboardInterrupt
            child.wait = interrupt
        return child

    try:
        with patch.object(kicad.subprocess, "Popen", side_effect=start):
            yield owned
    finally:
        # Test cleanup is not credited to the transport if an assertion fails.
        for child in owned:
            if child.poll() is None:
                os.killpg(child.pid, signal.SIGKILL)
                child.wait(timeout=5)


def synthetic_report(operation="drc", source="clean.kicad_pcb", violations=None):
    report = {
        "$schema": f"https://schemas.kicad.org/{operation}.v1.json",
        "coordinate_units": "mm", "date": "SYNTHETIC_ONLY",
        "kicad_version": TOOL.version, "source": source,
        "included_severities": ["error", "warning", "exclusion"],
        "ignored_checks": [{"key": key, "description": "Native default, explicitly frozen"}
                           for key in sorted(kicad.IGNORED_CHECKS[operation])],
    }
    rows = violations or []
    if operation == "erc":
        report["sheets"] = [{"path": "/", "uuid_path": "/fixture", "violations": rows}]
    else:
        report |= {"violations": rows, "unconnected_items": [], "schematic_parity": []}
    return harness.json_bytes(report)


def violation(kind="tracks_crossing", severity="error"):
    return {
        "type": kind, "description": "SYNTHETIC_ONLY known violation",
        "severity": severity, "items": [{"uuid": "test-only-item", "description": "test"}],
    }


def observation(report=None, exit_code=0, error=None):
    return kicad.Invocation(
        ["SYNTHETIC_ONLY"], exit_code, 0.0, False, True,
        kicad.bytes_hash(b""), kicad.bytes_hash(b""),
        synthetic_report() if report is None else report, error,
        source="SYNTHETIC_FAULT_INJECTION",
    )


class HarnessTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name).resolve()
        self.fixture_root = self.root / harness.FIXTURE_PREFIX
        shutil.copytree(FIXTURES, self.fixture_root, ignore=shutil.ignore_patterns("__pycache__"))
        (self.root / "configuration.txt").write_text("Synthetic frozen policy\n")
        self.git("init", "-q")
        self.git("add", ".")
        self.git("-c", "user.name=Fixture", "-c", "user.email=fixture@example.invalid",
                 "commit", "-qm", "Synthetic inputs")
        self.revision = self.git("rev-parse", "HEAD")
        self.names = [harness.FIXTURE_PREFIX + name for name in
                      ("clean.kicad_pcb", "clean.kicad_pro", "manifest.json", "dependency.json")]
        self.binding = harness.bind_inputs(
            self.root, self.revision, self.revision,
            self.names, ["configuration.txt"], TOOL,
        )

    def git(self, *args):
        return subprocess.check_output(["git", *args], cwd=self.root, text=True).strip()

    def outputs(self, name="trial", initial=None):
        return harness.OwnedOutputs(self.root / name, ("report.json",), initial)

    def finish(self, outputs=None, obs=None, mode="CURRENT"):
        outputs = outputs or self.outputs()
        record = harness.finish_observation(
            harness.Operation("test-task", "test-run", "drc"),
            obs or observation(), self.binding, self.root, outputs, TOOL,
            "clean.kicad_pcb", mode,
        )
        return record, outputs

    def test_clean_report_allows_only_test_output(self):
        record, outputs = self.finish()
        self.assertEqual(record.validation_verdict, harness.Verdict.PASS)
        self.assertEqual(record.evidence_freshness, harness.Freshness.CURRENT)
        self.assertEqual(record.gate_decision, harness.Gate.ALLOW_TEST_OUTPUT)
        self.assertEqual(record.scope, "SYNTHETIC_ONLY")
        decision = harness.recheck_decision(record, self.root, self.binding, outputs, TOOL)
        self.assertEqual(decision["gate_decision"], "ALLOW_TEST_OUTPUT")

    def test_failure_with_successful_restore_stays_failed(self):
        before = b"Old test output"
        outputs = self.outputs(initial={"report.json": before})
        outputs.write("report.json", b"Partial test output")
        obs = observation(synthetic_report(violations=[violation()]), 5)
        record, _ = self.finish(outputs, obs)
        self.assertEqual(record.operation_lifecycle, harness.Lifecycle.FAILED)
        self.assertEqual(record.validation_verdict, harness.Verdict.FAIL)
        self.assertEqual(record.gate_decision, harness.Gate.BLOCKED)
        self.assertEqual(record.recovery_outcome, harness.Recovery.ROLLBACK_OK)
        self.assertEqual((outputs.output / "report.json").read_bytes(), before)
        self.assertEqual((outputs.journal / "original-report.json").read_bytes(), obs.report)

    def test_conflicting_write_is_never_overwritten(self):
        outputs = self.outputs(initial={"report.json": b"old"})
        outputs.write("report.json", b"partial")
        (outputs.output / "report.json").write_bytes(b"other cooperative writer")
        record, _ = self.finish(outputs, observation(b"bad", 1))
        self.assertEqual(record.recovery_outcome, harness.Recovery.ROLLBACK_FAILED)
        self.assertEqual((outputs.output / "report.json").read_bytes(), b"other cooperative writer")
        self.assertIn("RECOVERY_RECONCILIATION_REQUIRED", record.gate_reasons)

    def test_sentinel_outside_operation_outputs_is_untouched(self):
        sentinel = self.root / "test-owned-sentinel.txt"
        sentinel.write_bytes(b"sentinel")
        self.finish(obs=observation(b"corrupt", 1))
        self.assertEqual(sentinel.read_bytes(), b"sentinel")

    def test_direct_source_and_configuration_drift_block_reuse(self):
        for index, name in enumerate((self.names[0], "configuration.txt", self.names[-1])):
            record, outputs = self.finish(self.outputs("drift-" + str(index)))
            path = self.root / name
            before = path.read_bytes()
            path.write_bytes(before + b" ")
            decision = harness.recheck_decision(record, self.root, self.binding, outputs, TOOL)
            self.assertEqual(decision["evidence_freshness"], "STALE")
            self.assertEqual(decision["gate_decision"], "BLOCKED")
            path.write_bytes(before)

    def test_missing_direct_input_is_unknown_not_pass(self):
        record, outputs = self.finish()
        (self.root / self.names[-1]).unlink()
        decision = harness.recheck_decision(record, self.root, self.binding, outputs, TOOL)
        self.assertEqual(decision["evidence_freshness"], "UNKNOWN")
        self.assertEqual(decision["gate_decision"], "BLOCKED")

    def test_historical_only_is_unknown_not_stale(self):
        record, outputs = self.finish(mode="HISTORICAL")
        self.assertEqual(record.validation_verdict, "PASS")
        self.assertEqual(record.evidence_freshness, "UNKNOWN")
        self.assertEqual(record.gate_decision, "BLOCKED")
        self.assertIn("CURRENT_FRESHNESS_NOT_CHECKED", record.gate_reasons)
        self.assertTrue((outputs.journal / "original-report.json").is_file())

    def test_missing_evidence_and_restored_positive_control(self):
        record, outputs = self.finish()
        path = outputs.journal / "stdout.txt"
        data = path.read_bytes()
        path.unlink()
        self.assertEqual(harness.recheck_decision(
            record, self.root, self.binding, outputs, TOOL)["gate_decision"], "BLOCKED")
        path.write_bytes(data)
        self.assertEqual(harness.recheck_decision(
            record, self.root, self.binding, outputs, TOOL)["gate_decision"], "ALLOW_TEST_OUTPUT")

    def test_corrupt_report_or_retained_records_block_reuse(self):
        for index, target in enumerate(("original-report.json", "invocation.json", "operation.json")):
            record, outputs = self.finish(self.outputs("corrupt-" + str(index)))
            (outputs.journal / target).write_bytes(b"{")
            self.assertEqual(harness.recheck_decision(
                record, self.root, self.binding, outputs, TOOL)["gate_decision"], "BLOCKED")

    def test_published_output_tamper_blocks_decision(self):
        record, outputs = self.finish()
        (outputs.output / "report.json").write_bytes(b"corrupt")
        self.assertEqual(harness.recheck_decision(
            record, self.root, self.binding, outputs, TOOL)["gate_decision"], "BLOCKED")

    def test_tool_or_policy_change_is_stale(self):
        current, _ = harness.freshness(self.root, self.binding, kicad.ToolIdentity("b" * 64, "10.0.1"))
        self.assertEqual(current, "STALE")
        with patch.dict(harness.POLICY, {"reported_violations_allowed": 1}):
            self.assertEqual(harness.freshness(self.root, self.binding, TOOL)[0], "STALE")

    def test_record_cannot_be_rebound_to_new_inputs(self):
        record, outputs = self.finish()
        record.binding["source_revision"] = "b" * 40
        self.assertEqual(harness.recheck_decision(
            record, self.root, self.binding, outputs, TOOL)["gate_decision"], "BLOCKED")

    def test_unsafe_cleanup_preserves_outputs_and_blocks_recovery(self):
        outputs = self.outputs(initial={"report.json": b"old"})
        outputs.write("report.json", b"partial")
        obs = observation(b"partial", 1, "CLEANUP_UNVERIFIED")
        obs.cleanup_verified = False
        record, _ = self.finish(outputs, obs)
        self.assertEqual(record.recovery_outcome, "NOT_ATTEMPTED")
        self.assertEqual((outputs.output / "report.json").read_bytes(), b"partial")
        self.assertEqual(record.gate_decision, "BLOCKED")

    def test_timeout_never_retries_or_allows_output(self):
        obs = observation(b"partial", -15, "TIMEOUT")
        obs.timed_out = True
        record, _ = self.finish(obs=obs)
        self.assertEqual(record.gate_decision, "BLOCKED")
        self.assertEqual(record.retries, 0)
        self.assertEqual(record.retry_reason, "NO_AUTOMATIC_RETRY")

    def test_missing_and_unsupported_capability_are_not_validation_success(self):
        for index, error in enumerate(("EXECUTABLE_UNAVAILABLE", "UNSUPPORTED_COMMAND")):
            obs = observation(error=error)
            obs.exit_code, obs.report = None, None
            record, _ = self.finish(self.outputs("cap-" + str(index)), obs)
            self.assertEqual(record.operation_lifecycle, "BLOCKED")
            self.assertEqual(record.validation_verdict, "NOT_RUN")
            self.assertEqual(record.gate_decision, "BLOCKED")

    def test_false_log_hash_blocks_operation(self):
        obs = observation()
        obs.stdout = b"not the hashed log"
        record, _ = self.finish(obs=obs)
        self.assertEqual(record.gate_decision, "BLOCKED")
        self.assertIn("MISSING_OR_MISMATCHED_LOG", record.gate_reasons)

    def test_forbidden_actions_never_reach_adapter_even_with_approval(self):
        for action in ("manufacturing-export", "fabricate", "purchase", "power", "flash", "save-board",
                       "refill-zones", "rm -rf ignored-test"):
            with self.subTest(action=action):
                request = self.root / "request.json"
                request.write_bytes(harness.json_bytes({
                    "scope": "SYNTHETIC_ONLY", "operation": action,
                    "task_id": "test-task", "run_id": "test-run",
                    "approval": {"actor": "synthetic", "usable_for_real_action": False},
                }))
                with patch.object(harness, "KiCad") as adapter, contextlib.redirect_stdout(io.StringIO()) as out:
                    status = harness.main([str(request), "--workspace", ".agent-work/test"])
                self.assertEqual(status, 2)
                adapter.assert_not_called()
                self.assertEqual(json.loads(out.getvalue())["gate_decision"], "HUMAN_REQUIRED")

    def test_traversal_symlinks_hardlinks_and_unowned_paths_rejected(self):
        outputs = self.outputs()
        for name in ("../sentinel", "/tmp/outside", ".git/config", "unknown.json"):
            with self.subTest(name=name), self.assertRaises((harness.HarnessError, harness.WorkflowError)):
                outputs.write(name, b"bad")
        sentinel = self.root / "sentinel"
        sentinel.write_bytes(b"keep")
        target = outputs.output / "report.json"
        target.symlink_to(sentinel)
        self.assertEqual(outputs.restore(), "ROLLBACK_FAILED")
        self.assertEqual(sentinel.read_bytes(), b"keep")
        target.unlink()
        os.link(sentinel, target)
        self.assertEqual(outputs.restore(), "ROLLBACK_FAILED")
        self.assertEqual(sentinel.read_bytes(), b"keep")

    def test_replaced_output_root_or_owner_marker_is_refused(self):
        outputs = self.outputs()
        (outputs.root / "owner.json").write_text("{}")
        self.assertEqual(outputs.restore(), "ROLLBACK_FAILED")

    def test_frozen_dirty_inputs_and_noncommits_are_rejected(self):
        (self.root / self.names[0]).write_text("dirty")
        with self.assertRaisesRegex(harness.HarnessError, "FROZEN_INPUT_MISMATCH"):
            harness.bind_inputs(self.root, self.revision, self.revision, self.names, ["configuration.txt"], TOOL)
        with self.assertRaisesRegex(harness.HarnessError, "IMMUTABLE_REVISIONS"):
            harness.bind_inputs(self.root, "main", self.revision, self.names, ["configuration.txt"], TOOL)

    def test_native_path_uses_exact_fixture_input_set(self):
        adapter = Mock(expected=TOOL)
        adapter.execute.return_value = observation()
        outputs = self.outputs()
        record = harness.run_native(
            self.root, "drc", self.names[0], self.names[:2], self.binding,
            outputs, adapter, "test-task", "test-run",
        )
        self.assertEqual(record.validation_verdict, "PASS")
        self.assertEqual(adapter.execute.call_args.args[0], "drc")
        with self.assertRaisesRegex(harness.HarnessError, "UNDECLARED_FIXTURE_INPUT_SET"):
            harness.run_native(self.root, "drc", self.names[0], self.names[:1], self.binding,
                               self.outputs("incomplete"), adapter, "test-task", "test-run")

    def test_native_production_path_cannot_be_smuggled_by_hash_binding(self):
        self.binding.files["hardware/production.kicad_pcb"] = "0" * 64
        adapter = Mock(expected=TOOL)
        record = harness.run_native(
            self.root, "drc", "hardware/production.kicad_pcb", ["hardware/production.kicad_pcb"],
            self.binding, self.outputs(), adapter, "test-task", "test-run",
        )
        self.assertEqual(record.gate_decision, "BLOCKED")
        adapter.execute.assert_not_called()

    def test_inconsistent_allow_cannot_serialize(self):
        record = harness.Operation("task", "run", "drc", gate_decision=harness.Gate.ALLOW_TEST_OUTPUT)
        with self.assertRaisesRegex(harness.HarnessError, "INCONSISTENT_ALLOW"):
            record.facts()

    def test_cli_end_to_end_uses_frozen_inputs_and_no_extra_flags(self):
        request = {
            "scope": "SYNTHETIC_ONLY", "operation": "drc",
            "task_id": "unit-task", "run_id": "unit-run",
            "source_revision": self.revision, "config_revision": self.revision,
            "inputs": self.names, "configuration": ["configuration.txt"],
            "native_inputs": self.names[:2], "input_name": self.names[0],
            "tool": {"sha256": TOOL.sha256, "version": TOOL.version}, "timeout": 20,
        }
        path = self.root / "request.json"
        path.write_bytes(harness.json_bytes(request))
        adapter = Mock(expected=TOOL)
        adapter.execute.return_value = observation()
        arguments = [str(path), "--root", str(self.root), "--workspace", ".agent-work/cli",
                     "--kicad-cli", "/nonexistent/kicad-cli"]
        with patch.object(harness, "KiCad", return_value=adapter), contextlib.redirect_stdout(io.StringIO()) as stdout:
            self.assertEqual(harness.main(arguments), 0)
        self.assertEqual(json.loads(stdout.getvalue())["decision"]["gate_decision"], "ALLOW_TEST_OUTPUT")
        request["extra_args"] = ["--save-board"]
        path.write_bytes(harness.json_bytes(request))
        with patch.object(harness, "KiCad") as blocked, contextlib.redirect_stderr(io.StringIO()) as stderr:
            self.assertEqual(harness.main(arguments), 2)
        blocked.assert_not_called()
        self.assertIn("INVALID_REQUEST_FIELDS", stderr.getvalue())

    def test_cli_honors_preflight_cancellation_and_retains_receipt(self):
        request = {
            "scope": "SYNTHETIC_ONLY", "operation": "drc", "task_id": "unit-task", "run_id": "unit-run",
            "source_revision": self.revision, "config_revision": self.revision,
            "inputs": self.names, "configuration": ["configuration.txt"],
            "native_inputs": self.names[:2], "input_name": self.names[0],
            "tool": {"sha256": TOOL.sha256, "version": TOOL.version}, "timeout": 20,
        }
        path = self.root / "request.json"
        path.write_bytes(harness.json_bytes(request))
        adapter = Mock(expected=TOOL)
        adapter.preflight.side_effect = kicad.ProcessInterrupted({"cleanup_verified": False})
        with patch.object(harness, "KiCad", return_value=adapter), contextlib.redirect_stderr(io.StringIO()) as stderr:
            status = harness.main([str(path), "--root", str(self.root),
                                   "--workspace", ".agent-work/cancel",
                                   "--kicad-cli", "/nonexistent/kicad-cli"])
        self.assertEqual(status, 130)
        adapter.execute.assert_not_called()
        result = json.loads(stderr.getvalue())
        self.assertEqual(result["gate_reasons"], ["OPERATOR_CANCELLED"])
        self.assertFalse(result["owned_process_cleanup_verified"])
        self.assertTrue((self.root / ".agent-work/cancel/journal/cancelled.json").is_file())


class ReportTests(unittest.TestCase):
    def parse(self, data, operation="drc", exit_code=0, source="clean.kicad_pcb"):
        return kicad.parse_report(data, operation, exit_code, TOOL.version, source)

    def test_real_schema_shapes_and_failure_classes(self):
        self.assertEqual(self.parse(synthetic_report())["verdict"], "PASS")
        result = self.parse(synthetic_report("erc", "test.kicad_sch", [violation("pin_not_connected")]),
                            "erc", 5, "test.kicad_sch")
        self.assertEqual(result["violation_types"], ["pin_not_connected"])

    def test_exit_zero_does_not_hide_semantic_failure(self):
        with self.assertRaisesRegex(kicad.AdapterError, "EXIT_REPORT_DISAGREEMENT"):
            self.parse(synthetic_report(violations=[violation()]))

    def test_parse_errors_are_not_intended_domain_failures(self):
        for data in (b"{}", b"{", b"", b"[]", None):
            with self.subTest(data=data), self.assertRaises(kicad.AdapterError):
                self.parse(data, exit_code=3)

    def test_missing_collections_duplicate_keys_threshold_and_version_rejected(self):
        original = json.loads(synthetic_report())
        for field in ("violations", "unconnected_items", "schematic_parity", "ignored_checks",
                      "included_severities", "source", "kicad_version", "$schema"):
            data = copy.deepcopy(original)
            del data[field]
            with self.subTest(field=field), self.assertRaises(kicad.AdapterError):
                self.parse(harness.json_bytes(data))
        with self.assertRaisesRegex(kicad.AdapterError, "CORRUPT_REPORT"):
            self.parse(b'{"kicad_version":"10.0.1","kicad_version":"10.0.1"}')

    def test_nonzero_command_error_with_clean_report_is_error(self):
        for exit_code in (None, 1, 3, 5, -15):
            with self.subTest(exit_code=exit_code), self.assertRaises(kicad.AdapterError):
                self.parse(synthetic_report(), exit_code=exit_code)

    def test_request_json_duplicate_keys_and_nonfinite_numbers_are_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "request.json"
            for value in ('{"x":1,"x":2}', '{"x":NaN}', "[]"):
                path.write_text(value)
                with self.subTest(value=value), self.assertRaises(ValueError):
                    harness.read_json(path)

    def test_domain_commands_are_allowlisted(self):
        adapter = object.__new__(kicad.KiCad)
        for operation in ("export", "pcb drc --save-board", "refill-zones", "shell"):
            with self.subTest(operation=operation), self.assertRaisesRegex(kicad.AdapterError, "OUT_OF_MVP_SCOPE"):
                adapter.execute(operation, "board.kicad_pcb", {}, Path("unused"))

    def test_transport_timeout_reaps_known_test_process(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory).resolve()
            receipt = kicad.run_process(
                [sys.executable, "-c", "import time; time.sleep(10)"],
                root, {"PATH": "/usr/bin:/bin"}, root, 0.1,
            )
            self.assertTrue(receipt["timed_out"])
            self.assertTrue(receipt["cleanup_verified"])
            self.assertEqual(receipt["remaining_owned_pids"], [])

    def test_keyboard_interrupt_and_sigint_reap_owned_child_and_preserve_receipts(self):
        for use_sigint in (False, True):
            with self.subTest(sigint=use_sigint), tempfile.TemporaryDirectory() as directory:
                root = Path(directory).resolve()
                with interrupt_owned_wait(use_sigint) as children:
                    with self.assertRaises(kicad.ProcessInterrupted) as stopped:
                        kicad.run_process([sys.executable, "-c", "import time; time.sleep(3)"],
                                          root, {"PATH": "/usr/bin:/bin"}, root, 10)
                    self.assertIsNotNone(children[0].poll())
                    self.assertTrue(stopped.exception.receipt["cleanup_verified"])
                    self.assertTrue(stopped.exception.receipt["interrupted"])
                    self.assertEqual(stopped.exception.receipt["remaining_owned_pids"], [])
                    receipt = json.loads((root / "process.json").read_text())
                    self.assertEqual(receipt["error"], "OPERATOR_CANCELLED")
                    self.assertTrue((root / "stdout.txt").is_file())
                    self.assertTrue((root / "stderr.txt").is_file())

    def test_interrupted_cleanup_uncertainty_is_not_reported_as_zero_processes(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory).resolve()
            with interrupt_owned_wait() as children, patch.object(kicad, "process_group", side_effect=OSError("fixture")):
                with self.assertRaises(kicad.ProcessInterrupted) as stopped:
                    kicad.run_process([sys.executable, "-c", "import time; time.sleep(3)"],
                                      root, {"PATH": "/usr/bin:/bin"}, root, 10)
                self.assertIsNotNone(children[0].poll())
            self.assertFalse(stopped.exception.receipt["cleanup_verified"])
            self.assertIsNone(stopped.exception.receipt["remaining_owned_pids"])
            self.assertTrue((root / "process.json").is_file())

    def test_adapter_cancellation_keeps_partial_runtime_and_propagates(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory).resolve()
            adapter = object.__new__(kicad.KiCad)
            adapter.executable = Path(sys.executable)
            adapter.verify_identity = Mock()
            with interrupt_owned_wait() as children:
                with self.assertRaises(kicad.ProcessInterrupted):
                    adapter._invoke(["-c", "import time; time.sleep(3)"], root / "native", {}, 10)
                self.assertIsNotNone(children[0].poll())
            receipt = json.loads((root / "native/runtime.json").read_text())
            self.assertTrue(receipt["retained_for_interruption"])
            self.assertFalse(receipt["temporary_environment_removed"])
            self.assertTrue(Path(receipt["runtime"]).exists())


if __name__ == "__main__":
    unittest.main()
