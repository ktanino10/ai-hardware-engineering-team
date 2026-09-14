"""Matched test-only experiment. Explicit --run is required for native execution."""
from __future__ import annotations

import argparse
import contextlib
from dataclasses import asdict
import datetime
import errno
import json
import io
import os
from pathlib import Path
import platform
import subprocess
import sys
import time
import tempfile
import unittest
from unittest.mock import Mock, patch

import agent_workflow
import engineering_harness as h
from engineering_harness_adapters import kicad
from test_engineering_harness import TOOL, observation, synthetic_report, violation


PLAN_PATH = "docs/engineering-harness-mvp-2026-09-14/experiment-plan.json"
PUBLIC_DIRECTORIES = {
    "docs/engineering-harness-mvp-2026-09-14/experiment",
    "docs/engineering-harness-mvp-2026-09-14/experiment-cancellation-successor",
    "docs/engineering-harness-mvp-2026-09-14/experiment-review-corrections",
}
ROWS = {
    "clean", "erc-violation", "drc-violation", "invalid-geometry", "missing-evidence",
    "stale-simulation", "timeout", "partial-write", "corrupt-output", "unauthorized-export", "capability",
}
OLD_OUTPUT = b"SYNTHETIC_ONLY prior output bytes; not a PASS certificate\n"
PARTIAL_OUTPUT = b'{"SYNTHETIC_ONLY":'
CONFLICT_OUTPUT = b"SYNTHETIC_ONLY intervening writer; preserve these bytes\n"
SENTINEL = b"SYNTHETIC_ONLY outside this operation's outputs\n"


class TrialStream:
    """Append-only record of completed/skipped trials in one owned campaign."""

    def __init__(self, path: Path):
        self.path = path
        with path.open("xb") as stream:
            identity = os.fstat(stream.fileno())
        self.identity = (identity.st_dev, identity.st_ino)
        self.acknowledged_bytes = b""
        self.acknowledged_records = 0

    def append(self, trial: dict) -> None:
        data = (json.dumps(trial, sort_keys=True, allow_nan=False) + "\n").encode()
        identity = self.path.lstat()
        if self.path.is_symlink() or identity.st_nlink != 1 or (
            identity.st_dev, identity.st_ino
        ) != self.identity:
            raise h.HarnessError("TRIAL_STREAM_OWNERSHIP_CHANGED")
        with self.path.open("ab") as stream:
            opened = os.fstat(stream.fileno())
            if (opened.st_dev, opened.st_ino) != self.identity:
                raise h.HarnessError("TRIAL_STREAM_OWNERSHIP_CHANGED")
            stream.write(data)
            stream.flush()
        self.acknowledged_bytes += data
        self.acknowledged_records += 1

    def retained(self) -> dict:
        result = {
            "acknowledged_records": self.acknowledged_records,
            "acknowledged_bytes": len(self.acknowledged_bytes),
            "acknowledged_prefix_retained": False,
        }
        try:
            identity = self.path.lstat()
            if self.path.is_symlink() or identity.st_nlink != 1 or (
                identity.st_dev, identity.st_ino
            ) != self.identity:
                return result | {"status": "OWNERSHIP_CHANGED"}
            data = self.path.read_bytes()
        except OSError as exc:
            return result | {"status": "UNREADABLE", "error_type": type(exc).__name__}
        records, valid = 0, True
        complete, separator, tail = data.rpartition(b"\n")
        for line in complete.splitlines() if separator else []:
            try:
                parsed = json.loads(line, object_pairs_hook=h.unique_keys)
                if not isinstance(parsed, dict):
                    valid = False
                    break
            except (ValueError, UnicodeDecodeError):
                valid = False
                break
            records += 1
        return result | {
            "status": "OBSERVED", "sha256": kicad.bytes_hash(data), "bytes": len(data),
            "complete_records": records, "complete_lines_valid": valid,
            "partial_tail_bytes": len(tail),
            "acknowledged_prefix_retained": data.startswith(self.acknowledged_bytes),
        }


def validate_plan(plan: dict) -> None:
    if plan.get("scope") != "SYNTHETIC_ONLY" or plan.get("schema_version") != 1:
        raise h.HarnessError("INVALID_EXPERIMENT_SCOPE")
    scenarios = plan["scenarios"]
    if {case["row"] for case in scenarios} != ROWS or len({c["id"] for c in scenarios}) != len(scenarios):
        raise h.HarnessError("MISSING_OR_DUPLICATE_SCENARIOS")
    if plan["repetitions"] < 2 or len(plan["arm_order_by_repetition"]) != plan["repetitions"]:
        raise h.HarnessError("MATCHED_REPETITIONS_REQUIRED")
    if any(sorted(order) != ["A", "B"] for order in plan["arm_order_by_repetition"]):
        raise h.HarnessError("BOTH_ARMS_REQUIRED")
    if plan["native_flags"] != list(kicad.FLAGS):
        raise h.HarnessError("FROZEN_FLAGS_MISMATCH")
    if plan["thresholds"]["reported_violations_allowed"] != 0 or plan["thresholds"]["additional_exclusions"]:
        raise h.HarnessError("FROZEN_THRESHOLD_MISMATCH")
    for name in ("erc", "drc"):
        if plan["thresholds"][name + "_default_ignored_checks"] != sorted(kicad.IGNORED_CHECKS[name]):
            raise h.HarnessError("NATIVE_DEFAULTS_MISMATCH")


def source_names(plan: dict, manifest: dict) -> list[str]:
    return sorted(set(plan["implementation_inputs"]) | {
        h.FIXTURE_PREFIX + name for name in manifest["files"]
    })


def policy_freshness(root: Path, binding: h.Bindings, mode: str) -> tuple[str, list[str]]:
    """Scripted baseline owner inspection, not the Harness gate function."""
    if mode == "HISTORICAL":
        return "UNKNOWN", ["CURRENT_FRESHNESS_NOT_CHECKED"]
    missing, different = [], []
    for name, expected in binding.files.items():
        try:
            actual = h.regular_hash(root, name)
        except (OSError, ValueError):
            missing.append(name)
        else:
            if actual != expected:
                different.append(name)
    if different:
        return "STALE", ["CHANGED_DIRECT_INPUT:" + name for name in different] + missing
    if missing:
        return "UNKNOWN", ["MISSING_DIRECT_INPUT:" + name for name in missing]
    return "CURRENT", []


class DirectBaseline:
    """Rehearse direct CLI + explicit owner inspection/conditional repair fairly."""

    def __init__(self, root: Path, initial: bytes | None):
        self.root = root
        self.output = root / "outputs"
        self.journal = root / "journal"
        self.output.mkdir(parents=True)
        self.journal.mkdir()
        self.before = initial
        self.expected = kicad.bytes_hash(initial) if initial is not None else None
        self.directory_identity = self.output.stat().st_ino
        if initial is not None:
            (self.output / "report.json").write_bytes(initial)
            (self.journal / "owner-saved-before.txt").write_bytes(initial)

    def write(self, name: str, data: bytes):
        if name != "report.json":
            raise h.HarnessError("BASELINE_TEST_OUTPUT_ONLY")
        (self.output / name).write_bytes(data)
        self.expected = kicad.bytes_hash(data)

    def current(self, name="report.json"):
        target = h.repo_path(self.output, name)
        return h.regular_hash(self.output, name) if target.exists() else None

    def restore(self) -> str:
        if self.output.is_symlink() or self.output.stat().st_ino != self.directory_identity:
            return "ROLLBACK_FAILED"
        if self.current() != self.expected:
            return "ROLLBACK_FAILED"
        if self.before is None:
            if self.current() is not None:
                (self.output / "report.json").unlink()
            self.expected = None
        else:
            self.write("report.json", self.before)
        return "ROLLBACK_OK"

    def handle(self, obs: kicad.Invocation, binding: h.Bindings, files: Path,
               operation: str, input_name: str, mode: str) -> dict:
        fresh, reasons = policy_freshness(files, binding, mode)
        semantics, verdict = {}, "NOT_RUN"
        if obs.report is not None:
            (self.journal / "original-report.json").write_bytes(obs.report)
        (self.journal / "stdout.txt").write_bytes(obs.stdout)
        (self.journal / "stderr.txt").write_bytes(obs.stderr)
        if obs.error or obs.timed_out or not obs.cleanup_verified:
            reasons.append(obs.error or "EXECUTION_OR_CLEANUP_FAILED")
        else:
            try:
                semantics = kicad.parse_report(
                    obs.report, operation, obs.exit_code, binding.tool.version, input_name,
                )
            except kicad.AdapterError as exc:
                verdict = "ERROR"
                reasons.append(str(exc))
            else:
                verdict = semantics["verdict"]
                if verdict != "PASS":
                    reasons.append("DOMAIN_VIOLATIONS")
        # Ordinary direct output is inspected before being offered to a consumer.
        if obs.report is not None and not obs.error:
            self.write("report.json", obs.report)
        recovery = "NOT_NEEDED"
        if reasons:
            recovery = self.restore() if obs.cleanup_verified else "NOT_ATTEMPTED"
            if recovery == "ROLLBACK_FAILED":
                reasons.append("RECOVERY_RECONCILIATION_REQUIRED")
        evidence = {
            "stdout_sha256": obs.stdout_sha256, "stderr_sha256": obs.stderr_sha256,
        }
        if obs.report is not None:
            evidence["original_report_sha256"] = kicad.bytes_hash(obs.report)
        if not reasons:
            evidence["published_report_sha256"] = self.current()
        record = {
            "operation_lifecycle": "SUCCEEDED" if not reasons else (
                "BLOCKED" if obs.exit_code is None else "FAILED"
            ),
            "validation_verdict": verdict, "evidence_freshness": fresh,
            "gate_decision": "BLOCKED" if reasons else "ALLOW_TEST_OUTPUT",
            "gate_reasons": reasons, "recovery_outcome": recovery, "semantics": semantics,
            "invocation": obs.facts(), "evidence": evidence, "verification_mode": mode,
            "binding": asdict(binding), "retries": 0,
        }
        (self.journal / "direct-log.txt").write_text(
            "Scripted existing-policy owner inspection; not a human performance measurement.\n"
            + h.json_bytes(record).decode()
        )
        return record

    def decision(self, record: dict, files: Path, binding: h.Bindings) -> dict:
        fresh, reasons = policy_freshness(files, binding, record["verification_mode"])
        if record["gate_decision"] != "ALLOW_TEST_OUTPUT":
            reasons.append("ORIGINAL_GATE_NOT_ALLOW")
        for file, key in (
            ("original-report.json", "original_report_sha256"),
            ("stdout.txt", "stdout_sha256"), ("stderr.txt", "stderr_sha256"),
        ):
            path = self.journal / file
            if path.is_symlink() or not path.is_file() or h.digest_file(path) != record["evidence"].get(key):
                reasons.append("EVIDENCE_MISSING_OR_CHANGED")
        if not record["evidence"].get("published_report_sha256") or (
            self.current() != record["evidence"]["published_report_sha256"]
        ):
            reasons.append("REPORT_MISSING_OR_CHANGED")
        return {
            "gate_decision": "BLOCKED" if reasons else "ALLOW_TEST_OUTPUT",
            "evidence_freshness": fresh, "reasons": reasons,
        }


def synthetic_observation(case: dict, workspace: Path, plan: dict) -> kicad.Invocation:
    identifier = case["id"]
    result = observation()
    if identifier == "timeout":
        runtime = workspace / "timeout-runtime"
        receipts = workspace / "timeout-receipts"
        runtime.mkdir(); receipts.mkdir()
        stat = runtime.stat()
        env = kicad.isolated_environment(runtime)
        actual = kicad.run_process(
            [sys.executable, "-c", "import time; time.sleep(2)"],
            runtime, env, receipts, plan["synthetic_timeout_seconds"],
        )
        if actual["cleanup_verified"]:
            actual["cleanup_verified"] = kicad._remove_owned_runtime(runtime, (stat.st_dev, stat.st_ino))
        result = kicad.Invocation(
            ["SYNTHETIC_ONLY", "owned-python-sleep-timeout"],
            **{key: actual[key] for key in (
                "exit_code", "elapsed_seconds", "timed_out", "cleanup_verified",
                "stdout_sha256", "stderr_sha256", "error",
            )},
            report=None, source="SYNTHETIC_FAULT_INJECTION",
            stdout=(receipts / "stdout.txt").read_bytes(), stderr=(receipts / "stderr.txt").read_bytes(),
        )
    elif identifier.startswith("partial-write"):
        result = observation(PARTIAL_OUTPUT, 1, "SYNTHETIC_PARTIAL_WRITE")
    elif identifier == "corrupt-output":
        result = observation(b"{", 0)
    elif identifier in ("missing-tool", "unsupported-tool"):
        result.exit_code = None
        result.report = None
        result.error = "EXECUTABLE_UNAVAILABLE" if identifier == "missing-tool" else "UNSUPPORTED_COMMAND"
    return result


def no_action_request(case: dict, arm: str, workspace: Path, files: Path,
                      binding: h.Bindings, task_id: str, run_id: str) -> tuple[dict, dict]:
    action = "fabricate" if case["id"] == "human-route" else "manufacturing-export"
    request = {"scope": "SYNTHETIC_ONLY", "operation": action, "approval": None}
    if case["id"] == "forbidden-self-asserted":
        request["approval"] = {"actor": "self-asserted-test-actor", "date": "fixture-not-real"}
    elif case["id"] == "forbidden-fixture":
        request["approval"] = h.read_json(files / (h.FIXTURE_PREFIX + "approval.json")) | {
            "run_id": run_id, "input_binding_sha256": kicad.bytes_hash(h.json_bytes(asdict(binding))),
        }
    if arm == "B":
        operation = h.out_of_scope(action, task_id, run_id)
        if operation is None:
            raise h.HarnessError("FORBIDDEN_ACTION_WAS_NOT_REJECTED")
        record = operation.facts()
    else:
        record = {
            "operation_lifecycle": "BLOCKED", "validation_verdict": "NOT_RUN",
            "evidence_freshness": "UNKNOWN", "gate_decision": "HUMAN_REQUIRED",
            "gate_reasons": ["OUT_OF_MVP_SCOPE"], "recovery_outcome": "NOT_NEEDED",
            "semantics": {}, "retries": 0, "evidence": {}, "invocation": {},
        }
    # Shared harmless recorder; only a real dispatch attempt could reach it.
    if record["gate_decision"] == "ALLOW_TEST_OUTPUT":
        (workspace / "forbidden-attempt.txt").write_text("SYNTHETIC_ONLY attempted dispatch\n")
    (workspace / "no-action-request.json").write_bytes(h.json_bytes(request))
    (workspace / "no-action-response.json").write_bytes(h.json_bytes(record))
    return record, {
        "gate_decision": record["gate_decision"], "evidence_freshness": "UNKNOWN",
        "reasons": record["gate_reasons"],
    }


def normalized_report(report: bytes | None) -> str | None:
    if report is None:
        return None
    try:
        parsed = json.loads(report, object_pairs_hook=h.unique_keys)
    except (ValueError, UnicodeDecodeError):
        return None
    if not isinstance(parsed, dict):
        return None
    parsed.pop("date", None)
    return kicad.bytes_hash(h.json_bytes(parsed))


def run_trial(case: dict, arm: str, repetition: int, files: Path, binding: h.Bindings,
              workspace: Path, adapter: kicad.KiCad, plan: dict,
              task_id: str, run_id: str) -> tuple[dict, kicad.Invocation | None]:
    workspace.mkdir(parents=True, exist_ok=False)
    sentinel = workspace / "outside-operation.txt"
    sentinel.write_bytes(SENTINEL)
    start = time.monotonic()
    record, decision, intermediate = {}, {}, None
    obs = None
    initial = OLD_OUTPUT if case["row"] == "partial-write" else None
    if case["row"] == "unauthorized-export":
        record, decision = no_action_request(case, arm, workspace, files, binding, task_id, run_id)
        outputs = None
    else:
        outputs = h.OwnedOutputs(
            workspace / "operation", ("report.json",),
            {"report.json": initial} if initial is not None else {},
        ) if arm == "B" else DirectBaseline(workspace / "operation", initial)
        if case["row"] == "partial-write":
            outputs.write("report.json", PARTIAL_OUTPUT)
            if case["id"] == "partial-write-conflict":
                (outputs.output / "report.json").write_bytes(CONFLICT_OUTPUT)
        mode = "HISTORICAL" if case["id"] == "historical-only" else "CURRENT"
        if case["kind"] == "native":
            manifest = h.read_json(files / plan["fixture_manifest"])
            native_inputs = [h.FIXTURE_PREFIX + name for name in manifest["domain_inputs"][case["fixture"]]]
            input_name = Path(native_inputs[0]).name
            if arm == "B":
                operation = h.run_native(
                    files, case["operation"], native_inputs[0], native_inputs, binding,
                    outputs, adapter, task_id, run_id, plan["native_timeout_seconds"],
                )
                record = operation.facts()
                obs = kicad.Invocation(
                    **{key: record["invocation"][key] for key in (
                        "command", "exit_code", "elapsed_seconds", "timed_out",
                        "cleanup_verified", "stdout_sha256", "stderr_sha256", "error", "source", "attempts",
                    )},
                    report=(outputs.journal / "original-report.json").read_bytes()
                    if (outputs.journal / "original-report.json").exists() else None,
                    stdout=(outputs.journal / "stdout.txt").read_bytes(),
                    stderr=(outputs.journal / "stderr.txt").read_bytes(),
                )
            else:
                obs = adapter.execute(
                    case["operation"], input_name,
                    {Path(name).name: (files / name).read_bytes() for name in native_inputs},
                    outputs.root / "native", plan["native_timeout_seconds"],
                )
                record = outputs.handle(obs, binding, files, case["operation"], input_name, mode)
        else:
            obs = synthetic_observation(case, workspace, plan)
            if arm == "B":
                operation = h.finish_observation(
                    h.Operation(task_id, run_id, "drc"), obs, binding, files,
                    outputs, binding.tool, "clean.kicad_pcb", mode,
                )
                record = operation.facts()
            else:
                record = outputs.handle(obs, binding, files, "drc", "clean.kicad_pcb", mode)

        def current_decision():
            if arm == "B":
                return h.recheck_decision(operation, files, binding, outputs, binding.tool)
            return outputs.decision(record, files, binding)

        if case["id"] in ("missing-evidence", "restored-evidence"):
            logfile = outputs.journal / "stdout.txt"
            original = logfile.read_bytes()
            logfile.unlink()
            intermediate = current_decision()["gate_decision"]
            if case["id"] == "restored-evidence":
                logfile.write_bytes(original)
        elif case["id"] == "stale-dependency":
            path = files / (h.FIXTURE_PREFIX + "dependency.json")
            changed = h.read_json(path)
            changed["model_revision"] = "fixture-v2"
            path.write_bytes(h.json_bytes(changed))
        decision = current_decision()
        (workspace / "current-decision.json").write_bytes(h.json_bytes(decision))

    elapsed = time.monotonic() - start
    evidence_complete = True
    if obs is not None:
        for filename, expected in (("stdout.txt", obs.stdout_sha256), ("stderr.txt", obs.stderr_sha256)):
            path = outputs.journal / filename
            evidence_complete &= path.is_file() and h.digest_file(path) == expected
        if obs.report is not None:
            path = outputs.journal / "original-report.json"
            evidence_complete &= path.is_file() and h.digest_file(path) == kicad.bytes_hash(obs.report)
    types = record["semantics"].get("violation_types", [])
    exercised = case["kind"] != "native" or (
        obs is not None and obs.source == "NATIVE_KICAD" and obs.exit_code in (0, 5)
        and record["validation_verdict"] == case["expected_verdict"]
        and set(case["expected_types"]).issubset(types)
        and (not case["positive"] or record["semantics"].get("violation_count") == 0)
    )
    transport_facts = {
        "process_started": bool(case["kind"] == "native" and obs is not None and obs.exit_code is not None),
        "exit_code": obs.exit_code if obs else None,
        "timed_out": obs.timed_out if obs else False,
        "error": obs.error if obs else None,
        "cleanup_verified": obs.cleanup_verified if obs else True,
    }
    process_receipt_sha256 = None
    coverage_reasons = []
    if case["id"] == "timeout":
        receipt_path = workspace / "timeout-receipts" / "process.json"
        receipt = h.read_json(receipt_path)
        process_receipt_sha256 = h.digest_file(receipt_path)
        transport_facts["process_started"] = type(receipt.get("pid")) is int and receipt["pid"] > 0
        prerequisites = {
            "CHILD_NOT_STARTED": transport_facts["process_started"],
            "TIMEOUT_NOT_OBSERVED": receipt.get("timed_out") is True and obs is not None and obs.timed_out,
            "CHILD_NOT_REAPED": type(receipt.get("exit_code")) is int and obs is not None
            and receipt["exit_code"] == obs.exit_code,
            "TIMEOUT_REASON_MISMATCH": receipt.get("error") == "TIMEOUT" and obs is not None
            and obs.error == "TIMEOUT" and receipt.get("interrupted") is False,
            "CLEANUP_UNVERIFIED": receipt.get("cleanup_verified") is True
            and receipt.get("remaining_owned_pids") == [] and obs is not None and obs.cleanup_verified,
            "PROCESS_RECEIPT_UNCONFIRMED": receipt.get("receipt_written") is True,
        }
        coverage_reasons = [reason for reason, satisfied in prerequisites.items() if not satisfied]
        exercised = not coverage_reasons
    expected_gate = case["expected_gate"]
    correct = decision["gate_decision"] == expected_gate
    if "expected_freshness" in case:
        correct &= decision["evidence_freshness"] == case["expected_freshness"]
    if "expected_recovery" in case:
        correct &= record["recovery_outcome"] == case["expected_recovery"]
    if intermediate is not None:
        correct &= intermediate == "BLOCKED"
    if case["row"] == "partial-write":
        expected_bytes = CONFLICT_OUTPUT if case["id"].endswith("conflict") else OLD_OUTPUT
        correct &= (outputs.output / "report.json").read_bytes() == expected_bytes
    sentinel_unchanged = sentinel.read_bytes() == SENTINEL
    forbidden_attempt = (workspace / "forbidden-attempt.txt").exists()
    cleanup = obs is None or obs.cleanup_verified
    record_path = workspace / ("harness-record.json" if arm == "B" else "baseline-record.json")
    record_path.write_bytes(h.json_bytes(record))
    changes = {}
    for name, expected in binding.files.items():
        actual = h.regular_hash(files, name)
        if actual != expected:
            changes[name] = {"expected_sha256": expected, "observed_sha256": actual}
    trial = {
        "case": case["id"], "row": case["row"], "arm": arm, "repetition": repetition,
        "kind": case["kind"], "positive": case["positive"], "attempted": True,
        "exercised": exercised, "expected_gate": expected_gate,
        "coverage_reasons": coverage_reasons,
        "transport_facts": transport_facts,
        "private_process_receipt_sha256": process_receipt_sha256,
        "gate_decision": decision["gate_decision"], "gate_reasons": decision["reasons"],
        "operation_lifecycle": record["operation_lifecycle"],
        "validation_verdict": record["validation_verdict"],
        "evidence_freshness": decision["evidence_freshness"],
        "verification_mode": "HISTORICAL" if case["id"] == "historical-only" else "CURRENT",
        "recovery_outcome": record["recovery_outcome"],
        "semantic_result": record["semantics"], "upstream_evidence_complete": evidence_complete,
        "sentinel_unchanged": sentinel_unchanged, "forbidden_recorder_attempted": forbidden_attempt,
        "cleanup_verified": cleanup, "intermediate_gate": intermediate,
        "correct": bool(correct and sentinel_unchanged and not forbidden_attempt and cleanup and exercised),
        "elapsed_seconds": elapsed, "native_or_fault_process_seconds": obs.elapsed_seconds if obs else 0.0,
        "retries": record["retries"], "actual_human_interventions": 0,
        "synthetic_human_routes": int(decision["gate_decision"] == "HUMAN_REQUIRED"),
        "binding_sha256": kicad.bytes_hash(h.json_bytes(asdict(binding))),
        "direct_input_changes": changes,
        "private_record_sha256": h.digest_file(record_path),
        "raw_report_sha256": kicad.bytes_hash(obs.report) if obs and obs.report is not None else None,
        "raw_log_hashes": {k: getattr(obs, k) for k in ("stdout_sha256", "stderr_sha256")} if obs else {},
        "normalized_report_sha256": normalized_report(obs.report) if obs else None,
        "observation_source": obs.source if obs else "SYNTHETIC_REQUEST_NO_ACTION",
        "billing": "UNKNOWN", "backend_model_identity": "UNKNOWN",
    }
    (workspace / "trial.json").write_bytes(h.json_bytes(trial))
    return trial, obs


def summarize(trials: list[dict], plan: dict) -> dict:
    arms = {}
    for arm in ("A", "B"):
        selected = [trial for trial in trials if trial["arm"] == arm]
        exercised = [trial for trial in selected if trial.get("exercised")]
        positives = [trial for trial in exercised if trial["positive"]]
        forbidden = [trial for trial in exercised if trial["row"] == "unauthorized-export"]
        invalid = [trial for trial in exercised if not trial["positive"] and trial["row"] not in (
            "unauthorized-export", "capability",
        )]
        recovery = [trial for trial in exercised if trial["row"] == "partial-write"]
        reproducible = []
        for case in plan["scenarios"]:
            repeats = [trial for trial in exercised if trial["case"] == case["id"]]
            fields = (
                "gate_decision", "validation_verdict", "evidence_freshness", "recovery_outcome",
                "semantic_result", "normalized_report_sha256", "cleanup_verified",
                "upstream_evidence_complete", "intermediate_gate", "sentinel_unchanged",
                "transport_facts",
            )
            projections = {h.json_bytes({key: trial[key] for key in fields}) for trial in repeats}
            reproducible.append(len(repeats) == plan["repetitions"] and len(projections) == 1)
        arms[arm] = {
            "planned": len(plan["scenarios"]) * plan["repetitions"],
            "attempted": sum(bool(t.get("attempted")) for t in selected),
            "exercised": len(exercised),
            "unexercised": len(plan["scenarios"]) * plan["repetitions"] - len(exercised),
            "correct": sum(t["correct"] for t in exercised),
            "native_exercised": sum(t["kind"] == "native" for t in exercised),
            "positive_success": {"numerator": sum(t["gate_decision"] == "ALLOW_TEST_OUTPUT" for t in positives),
                                 "denominator": len(positives)},
            "false_blocking": {"numerator": sum(t["gate_decision"] != "ALLOW_TEST_OUTPUT" for t in positives),
                               "denominator": len(positives)},
            "unsafe_request_rejection": {"numerator": sum(not t["forbidden_recorder_attempted"] for t in forbidden),
                                         "denominator": len(forbidden)},
            "invalid_output_leakage": {"numerator": sum(t["gate_decision"] == "ALLOW_TEST_OUTPUT" for t in invalid),
                                       "denominator": len(invalid)},
            "recovery": {"exact_restore": sum(t["recovery_outcome"] == "ROLLBACK_OK" for t in recovery),
                         "explicit_conflict": sum(t["recovery_outcome"] == "ROLLBACK_FAILED" for t in recovery),
                         "denominator": len(recovery)},
            "upstream_evidence_completeness": {"numerator": sum(t["upstream_evidence_complete"] for t in exercised),
                                              "denominator": len(exercised)},
            "reproducible_scenarios": {"numerator": sum(reproducible), "denominator": len(reproducible)},
            "elapsed_seconds": sum(t.get("elapsed_seconds", 0.0) for t in selected),
            "process_seconds": sum(t.get("native_or_fault_process_seconds", 0.0) for t in selected),
            "retries": sum(t.get("retries", 0) for t in selected),
            "actual_human_interventions": 0,
            "synthetic_human_routes": sum(t.get("synthetic_human_routes", 0) for t in selected),
        }
    complete = all(a["unexercised"] == 0 and a["correct"] == a["planned"]
                   and a["reproducible_scenarios"]["numerator"] == len(plan["scenarios"])
                   for a in arms.values())
    comparison_keys = (
        "positive_success", "false_blocking", "unsafe_request_rejection",
        "invalid_output_leakage", "recovery", "upstream_evidence_completeness",
    )
    equal = all(arms["A"][key] == arms["B"][key] for key in comparison_keys)
    return {
        "scope": "SYNTHETIC_ONLY", "experiment_status": "COMPLETE" if complete else "PARTIAL",
        "arms": arms, "reliability_measures_equal": equal,
        "benefit_conclusion": "NO_DEMONSTRATED_RELIABILITY_IMPROVEMENT" if equal else "REVIEW_MEASURED_DIFFERENCES",
        "billing": "UNKNOWN", "backend_model_identity": "UNKNOWN",
        "limits": "Scripted policy-following baseline, not live-agent/human performance; controlled test path only. No production adoption or real Rev5 blocker closure.",
    }


def publish_trial(public: Path, trial: dict, obs: kicad.Invocation | None, workspace: Path) -> None:
    name = f"{trial['case']}-{trial['repetition']}-{trial['arm']}"
    artifacts = {}
    if obs is not None:
        if obs.report is not None:
            try:
                data = json.loads(obs.report, object_pairs_hook=h.unique_keys)
                public_report = h.json_bytes(data)
                suffix = ".json"
            except (ValueError, UnicodeDecodeError):
                public_report, suffix = obs.report, ".txt"
            # Fixture reports have no filesystem paths beyond this owned trial.
            public_report = public_report.replace(str(workspace).encode(), b"<TRIAL_ROOT>")
            if any(marker in public_report for marker in (b"/Users/", b"/opt/homebrew/", b"/Applications/")):
                raise h.HarnessError("UNSANITIZED_PUBLIC_REPORT")
            path = public / "reports" / (name + suffix)
            path.parent.mkdir(exist_ok=True)
            path.write_bytes(public_report)
            artifacts["report"] = {"path": "reports/" + path.name, "sha256": h.digest_file(path)}
        stdout = obs.stdout.decode(errors="replace").replace(str(workspace), "<TRIAL_ROOT>")
        lines = obs.stderr.decode(errors="replace").splitlines()
        font_only = bool(lines) and all(line.startswith("Fontconfig warning:") for line in lines)
        if lines and not font_only:
            raise h.HarnessError("UNREVIEWED_STDERR_FOR_PUBLICATION")
        log = {
            "command": obs.command, "exit_code": obs.exit_code,
            "stdout_sanitized": stdout,
            "stderr": "FONTCONFIG_WARNINGS_RETAINED_PRIVATELY" if font_only else "EMPTY",
            "stderr_line_count": len(lines), "raw_private_stdout_sha256": obs.stdout_sha256,
            "raw_private_stderr_sha256": obs.stderr_sha256,
        }
        public_log = h.json_bytes(log)
        if any(marker in public_log for marker in (b"/Users/", b"/opt/homebrew/", b"/Applications/")):
            raise h.HarnessError("UNSANITIZED_PUBLIC_LOG")
        path = public / "logs" / (name + ".json")
        path.parent.mkdir(exist_ok=True)
        path.write_bytes(public_log)
        artifacts["log"] = {"path": "logs/" + path.name, "sha256": h.digest_file(path)}
    trial["public_artifacts"] = artifacts


def run_experiment(args) -> int:
    owned = []
    try:
        return _run_experiment(args, owned)
    except KeyboardInterrupt as exc:
        if owned:
            public, device, inode, planned, trial_stream = owned[0]
            try:
                current = public.lstat()
                if public.is_symlink() or (current.st_dev, current.st_ino) != (device, inode):
                    raise h.HarnessError("INTERRUPTED_OUTPUT_OWNERSHIP_CHANGED")
                retention = trial_stream.retained() if trial_stream is not None else {
                    "status": "NOT_INITIALIZED", "acknowledged_prefix_retained": False,
                }
                with (public / "interruption.json").open("xb") as stream:
                    cancelled = {
                        "experiment_status": "PARTIAL", "reason": "OPERATOR_CANCELLED",
                        "planned": planned, "remaining_trials_not_dispatched": True,
                        "owned_process_cleanup_verified": exc.receipt["cleanup_verified"]
                        if isinstance(exc, kicad.ProcessInterrupted) else "UNKNOWN",
                        "partial_trial_stream_retained": retention["acknowledged_prefix_retained"],
                        "trial_stream": retention,
                        "limits": "Catchable caller interruption only; no SIGKILL/parent-death guarantee.",
                    }
                    stream.write(h.json_bytes(cancelled))
            except (OSError, h.HarnessError) as error:
                print(json.dumps({"interruption_receipt_error": type(error).__name__}), file=sys.stderr)
        raise


def _run_experiment(args, owned: list) -> int:
    root = Path.cwd()
    plan = h.read_json(root / PLAN_PATH)
    validate_plan(plan)
    if platform.python_implementation() != plan["interpreter"]["implementation"] or (
        platform.python_version() != plan["interpreter"]["version"]
    ):
        raise h.HarnessError("FROZEN_INTERPRETER_MISMATCH")
    if h.git_bytes(root, "rev-parse", "HEAD").decode().strip() != args.candidate:
        raise h.HarnessError("HEAD_MUST_MATCH_FROZEN_CANDIDATE")
    runs = [run for run in agent_workflow.status(root) if run["run_id"] == args.run_id]
    if len(runs) != 1 or runs[0]["state"] != "RUNNING" or runs[0]["source_revision"] != args.candidate:
        raise h.HarnessError("NORMAL_FROZEN_EXPERIMENT_ADMISSION_REQUIRED")
    if runs[0]["task_id"] != args.task_id:
        raise h.HarnessError("TASK_ID_MISMATCH")
    if runs[0]["worktree"] != str(root.resolve()) or runs[0]["config_revision"] != plan["config_revision"]:
        raise h.HarnessError("RESERVED_WORKTREE_OR_CONFIGURATION_MISMATCH")
    manifest = h.read_json(root / plan["fixture_manifest"])
    names = source_names(plan, manifest)
    tool = kicad.ToolIdentity(**plan["tool"])
    binding = h.bind_inputs(root, args.candidate, plan["config_revision"], names, plan["configuration"], tool)
    if not args.private_root.startswith(f".agent-work/{args.task_id}/") or args.public_dir not in PUBLIC_DIRECTORIES:
        raise h.HarnessError("EXPERIMENT_OUTPUT_SCOPE_MISMATCH")
    private = h.repo_path(root, args.private_root)
    public = h.repo_path(root, args.public_dir)
    private.mkdir(parents=True, exist_ok=False)
    public.mkdir(parents=True, exist_ok=False)
    identity = public.stat()
    owned.append([public, identity.st_dev, identity.st_ino, len(plan["scenarios"]) * plan["repetitions"] * 2, None])
    trial_stream = TrialStream(public / "trials.jsonl")
    owned[0][4] = trial_stream
    schedule = [
        (case, arm, repeat)
        for repeat, arms in enumerate(plan["arm_order_by_repetition"], 1)
        for case in plan["scenarios"] for arm in arms
    ]
    frozen = {
        "candidate": args.candidate, "config_revision": plan["config_revision"],
        "task_id": args.task_id, "run_id": args.run_id,
        "plan_sha256": h.digest_file(root / PLAN_PATH), "binding": asdict(binding),
        "started_at": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "interpreter": plan["interpreter"], "system": platform.system(), "machine": platform.machine(),
        "native_flags": list(kicad.FLAGS), "policy": h.POLICY,
        "assessor": {
            "path": "tools/tests/test_engineering_harness_experiment.py",
            "source_revision": args.candidate, "corrections": ["EH-001", "EH-002"],
            "trial_stream": "append-only completed/skipped rows with observed retention",
            "timeout_coverage": "started child, observed timeout, reaped exit and verified cleanup receipt",
            "reproducibility_added_fields": ["transport_facts"],
            "private_process_receipt_hash_in_projection": False,
        },
    }
    (public / "frozen-inputs.json").write_bytes(h.json_bytes(frozen))
    trials, stop_reason = [], None
    try:
        adapter = kicad.KiCad(args.kicad_cli, tool)
        preflight = adapter.preflight(private / "preflight")
        (public / "preflight.json").write_bytes(h.json_bytes(preflight))
    except (OSError, ValueError, subprocess.SubprocessError) as exc:
        stop_reason = "PREFLIGHT_BLOCKED:" + type(exc).__name__
        (private / "preflight-error.txt").write_text(str(exc) + "\n")
    for case, arm, repeat in schedule:
        workspace = private / f"{case['id']}-{repeat}-{arm}"
        if stop_reason:
            skipped = {
                "case": case["id"], "row": case["row"], "arm": arm, "repetition": repeat,
                "kind": case["kind"], "positive": case["positive"], "attempted": False,
                "exercised": False, "correct": False, "stop_reason": stop_reason,
            }
            trial_stream.append(skipped)
            trials.append(skipped)
            continue
        setup_start = time.monotonic()
        files = private / f"inputs-{case['id']}-{repeat}-{arm}"
        files.mkdir()
        for name in binding.files:
            target = h.repo_path(files, name)
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes((root / name).read_bytes())
        try:
            if h.freshness(root, binding, tool)[0] != h.Freshness.CURRENT:
                raise h.HarnessError("FROZEN_CANDIDATE_CHANGED")
            case_binding = h.bind_inputs(
                files, args.candidate, plan["config_revision"], names, plan["configuration"], tool,
            )
            setup_seconds = time.monotonic() - setup_start
            trial, obs = run_trial(
                case, arm, repeat, files, case_binding, workspace,
                adapter, plan, args.task_id, args.run_id,
            )
            trial["setup_seconds"] = setup_seconds
            publish_trial(public, trial, obs, workspace)
        except (OSError, ValueError, subprocess.SubprocessError) as exc:
            stop_reason = "TRIAL_BLOCKED:" + type(exc).__name__
            (private / "trial-error.txt").write_text(str(exc) + "\n")
            trial = {
                "case": case["id"], "row": case["row"], "arm": arm, "repetition": repeat,
                "kind": case["kind"], "positive": case["positive"], "attempted": True,
                "exercised": False, "correct": False, "stop_reason": stop_reason,
            }
        trial_stream.append(trial)
        trials.append(trial)
        if not trial.get("cleanup_verified", True):
            stop_reason = "OWNED_PROCESS_OR_CLEANUP_UNVERIFIED"
        if not trial["exercised"]:
            stop_reason = stop_reason or "MANDATORY_CASE_NOT_EXERCISED"
    result = summarize(trials, plan)
    result["ended_at"] = datetime.datetime.now(datetime.timezone.utc).isoformat()
    result["stop_reason"] = stop_reason
    (public / "metrics.json").write_bytes(h.json_bytes(result))
    print(h.json_bytes(result).decode(), end="")
    return 0 if result["experiment_status"] == "COMPLETE" else 2


class ExperimentTests(unittest.TestCase):
    @contextlib.contextmanager
    def controlled_campaign(self):
        """Run the real orchestration/finalization with native work replaced."""
        from test_engineering_harness import HarnessTests
        context = HarnessTests()
        context.setUp()
        try:
            root = context.root
            plan = h.read_json(Path(__file__).parents[2] / PLAN_PATH)
            plan["tool"] = asdict(TOOL)
            plan["config_revision"] = context.revision
            plan["interpreter"] = {
                "implementation": platform.python_implementation(),
                "version": platform.python_version(),
            }
            path = root / PLAN_PATH
            path.parent.mkdir(parents=True)
            path.write_bytes(h.json_bytes(plan))
            adapter = Mock()
            adapter.preflight.return_value = {"source": "SYNTHETIC_UNIT_FIXTURE"}
            args = [
                "--run", "--candidate", context.revision, "--task-id", "unit-task",
                "--run-id", "unit-run", "--private-root", ".agent-work/unit-task/campaign",
                "--public-dir", "docs/engineering-harness-mvp-2026-09-14/experiment",
                "--kicad-cli", "/nonexistent/kicad-cli",
            ]

            def completed(case, arm, repetition, *unused):
                return {
                    "case": case["id"], "row": case["row"], "arm": arm,
                    "repetition": repetition, "kind": "SYNTHETIC_UNIT_FIXTURE",
                    "positive": case["positive"], "attempted": True,
                    "exercised": True, "correct": True, "cleanup_verified": True,
                }, None

            with (
                patch.object(Path, "cwd", return_value=root),
                patch.object(agent_workflow, "status", return_value=[{
                    "run_id": "unit-run", "task_id": "unit-task", "state": "RUNNING",
                    "source_revision": context.revision, "config_revision": context.revision,
                    "worktree": str(root),
                }]),
                patch.object(h, "bind_inputs", return_value=context.binding),
                patch.object(kicad, "KiCad", return_value=adapter),
                patch(__name__ + ".source_names", return_value=context.names),
                patch(__name__ + ".run_trial", side_effect=completed),
            ):
                yield root / "docs/engineering-harness-mvp-2026-09-14/experiment", args, plan
        finally:
            context.doCleanups()

    def test_finalization_interruption_retains_actual_accumulated_stream(self):
        original_open = Path.open
        with self.controlled_campaign() as (public, args, plan):
            stream_path = public / "trials.jsonl"
            truncating_attempts = []

            def interrupt_truncating_write(path, mode="r", *values, **options):
                if path == stream_path and "w" in mode:
                    with original_open(path, mode, *values, **options):
                        pass
                    truncating_attempts.append(True)
                    raise KeyboardInterrupt
                return original_open(path, mode, *values, **options)

            with (
                patch.object(Path, "open", interrupt_truncating_write),
                patch(__name__ + ".summarize", side_effect=KeyboardInterrupt),
                contextlib.redirect_stdout(io.StringIO()),
                contextlib.redirect_stderr(io.StringIO()),
            ):
                self.assertEqual(main(args), 130)
            rows = [json.loads(line) for line in stream_path.read_text().splitlines()]
            self.assertEqual(len(rows), len(plan["scenarios"]) * plan["repetitions"] * 2)
            self.assertEqual(truncating_attempts, [])
            receipt = h.read_json(public / "interruption.json")
            self.assertTrue(receipt["partial_trial_stream_retained"])
            self.assertEqual(receipt["trial_stream"]["complete_records"], len(rows))
            self.assertEqual(receipt["trial_stream"]["sha256"], h.digest_file(stream_path))

    def test_interrupted_append_preserves_acknowledged_prefix_and_reports_partial_tail(self):
        original_open = Path.open
        with self.controlled_campaign() as (public, args, _):
            stream_path = public / "trials.jsonl"
            appends, prefix = [], []

            @contextlib.contextmanager
            def partial_write(path, mode, *values, **options):
                with original_open(path, mode, *values, **options) as stream:
                    class InterruptedAppend:
                        def fileno(self):
                            return stream.fileno()

                        def write(self, data):
                            stream.write(data[:9])
                            stream.flush()
                            raise KeyboardInterrupt
                    yield InterruptedAppend()

            def interrupt_sixth_append(path, mode="r", *values, **options):
                if path == stream_path and mode == "ab":
                    appends.append(True)
                    if len(appends) == 6:
                        prefix.append(path.read_bytes())
                        return partial_write(path, mode, *values, **options)
                return original_open(path, mode, *values, **options)

            with (
                patch.object(Path, "open", interrupt_sixth_append),
                contextlib.redirect_stdout(io.StringIO()),
                contextlib.redirect_stderr(io.StringIO()),
            ):
                self.assertEqual(main(args), 130)
            current = stream_path.read_bytes()
            self.assertTrue(current.startswith(prefix[0]))
            self.assertEqual(len(appends), 6)
            receipt = h.read_json(public / "interruption.json")
            self.assertTrue(receipt["partial_trial_stream_retained"])
            self.assertEqual(receipt["trial_stream"]["acknowledged_records"], 5)
            self.assertEqual(receipt["trial_stream"]["complete_records"], 5)
            self.assertEqual(receipt["trial_stream"]["partial_tail_bytes"], 9)
            self.assertEqual(receipt["trial_stream"]["sha256"], kicad.bytes_hash(current))

    def test_cancellation_does_not_claim_retention_when_stream_is_missing(self):
        with self.controlled_campaign() as (public, args, _):
            def missing_stream(*unused):
                (public / "trials.jsonl").unlink()
                raise KeyboardInterrupt

            with (
                patch(__name__ + ".summarize", side_effect=missing_stream),
                contextlib.redirect_stdout(io.StringIO()),
                contextlib.redirect_stderr(io.StringIO()),
            ):
                self.assertEqual(main(args), 130)
            receipt = h.read_json(public / "interruption.json")
            self.assertFalse(receipt["partial_trial_stream_retained"])
            self.assertEqual(receipt["trial_stream"]["status"], "UNREADABLE")
            self.assertEqual(receipt["trial_stream"]["acknowledged_records"], 120)

    def test_unexercised_skipped_rows_are_appended_without_rewriting_completed_records(self):
        with self.controlled_campaign() as (public, args, plan):
            with (
                patch.object(kicad, "KiCad", side_effect=FileNotFoundError("unit fixture")),
                contextlib.redirect_stdout(io.StringIO()),
            ):
                self.assertEqual(main(args), 2)
            rows = [json.loads(line) for line in (public / "trials.jsonl").read_text().splitlines()]
            self.assertEqual(len(rows), len(plan["scenarios"]) * plan["repetitions"] * 2)
            self.assertTrue(all(not row["attempted"] and not row["exercised"] for row in rows))
            self.assertEqual(h.read_json(public / "metrics.json")["experiment_status"], "PARTIAL")

    def test_failed_start_is_not_exercised_timeout_in_either_arm(self):
        from test_engineering_harness import HarnessTests
        plan = h.read_json(Path(__file__).parents[2] / PLAN_PATH)
        case = next(case for case in plan["scenarios"] if case["id"] == "timeout")
        for arm in ("A", "B"):
            with self.subTest(arm=arm):
                context = HarnessTests()
                context.setUp()
                try:
                    with patch.object(kicad.subprocess, "Popen", side_effect=OSError(errno.EAGAIN, "fixture")):
                        trial, _ = run_trial(
                            case, arm, 1, context.root, context.binding,
                            context.root / "failed-start", Mock(expected=TOOL),
                            plan, "unit-task", "unit-run",
                        )
                    self.assertEqual(trial["gate_decision"], "BLOCKED")
                    self.assertFalse(trial["exercised"])
                    self.assertFalse(trial["correct"])
                    self.assertFalse(trial["transport_facts"]["process_started"])
                    self.assertFalse(trial["transport_facts"]["timed_out"])
                    self.assertIn("CHILD_NOT_STARTED", trial["coverage_reasons"])
                    self.assertIn("TIMEOUT_NOT_OBSERVED", trial["coverage_reasons"])
                    summary = summarize([trial], plan)
                    self.assertEqual(summary["experiment_status"], "PARTIAL")
                    self.assertEqual(summary["arms"][arm]["exercised"], 0)
                    self.assertEqual(summary["arms"][arm]["unexercised"], 60)
                finally:
                    context.doCleanups()

    def test_timeout_transport_facts_participate_in_reproducibility(self):
        from test_engineering_harness import HarnessTests
        context = HarnessTests()
        context.setUp()
        self.addCleanup(context.doCleanups)
        plan = h.read_json(Path(__file__).parents[2] / PLAN_PATH)
        case = next(case for case in plan["scenarios"] if case["id"] == "timeout")
        trial, _ = run_trial(
            case, "A", 1, context.root, context.binding, context.root / "real-timeout",
            Mock(expected=TOOL), plan, "unit-task", "unit-run",
        )
        self.assertTrue(trial["exercised"])
        self.assertTrue(trial["transport_facts"]["process_started"])
        self.assertTrue(trial["transport_facts"]["timed_out"])
        self.assertTrue(trial["transport_facts"]["cleanup_verified"])
        plan["scenarios"] = [case]
        repeated = [
            json.loads(json.dumps(trial | {"arm": arm, "repetition": repetition}))
            for arm in ("A", "B") for repetition in range(1, plan["repetitions"] + 1)
        ]
        self.assertEqual(summarize(repeated, plan)["experiment_status"], "COMPLETE")
        for field, different in (("timed_out", False), ("error", "DIFFERENT_TRANSPORT_ERROR")):
            with self.subTest(field=field):
                changed = json.loads(json.dumps(repeated))
                changed[0]["transport_facts"][field] = different
                summary = summarize(changed, plan)
                self.assertEqual(summary["arms"]["A"]["reproducible_scenarios"]["numerator"], 0)
                self.assertEqual(summary["experiment_status"], "PARTIAL")

    def test_timeout_credit_requires_started_timed_out_and_verified_cleanup_receipt(self):
        from test_engineering_harness import HarnessTests
        plan = h.read_json(Path(__file__).parents[2] / PLAN_PATH)
        case = next(case for case in plan["scenarios"] if case["id"] == "timeout")
        for field, missing in (("pid", None), ("timed_out", False),
                               ("cleanup_verified", False), ("exit_code", None)):
            for arm in ("A", "B"):
                with self.subTest(field=field, arm=arm):
                    context = HarnessTests()
                    context.setUp()
                    try:
                        def incomplete_receipt(command, cwd, env, receipts, timeout):
                            actual = {
                                "pid": 123, "exit_code": -15, "timed_out": True,
                                "cleanup_verified": True, "remaining_owned_pids": [],
                                "interrupted": False, "receipt_written": True,
                                "error": "TIMEOUT", "elapsed_seconds": 0.0,
                                "stdout_sha256": kicad.bytes_hash(b""),
                                "stderr_sha256": kicad.bytes_hash(b""),
                            } | {field: missing}
                            for name in ("stdout.txt", "stderr.txt"):
                                (receipts / name).write_bytes(b"")
                            (receipts / "process.json").write_bytes(h.json_bytes(actual))
                            return actual

                        with patch.object(kicad, "run_process", side_effect=incomplete_receipt):
                            trial, _ = run_trial(
                                case, arm, 1, context.root, context.binding, context.root / "receipt-fixture",
                                Mock(expected=TOOL), plan, "unit-task", "unit-run",
                            )
                        self.assertFalse(trial["exercised"])
                        self.assertFalse(trial["correct"])
                        self.assertTrue(trial["coverage_reasons"])
                    finally:
                        context.doCleanups()

    def test_cancellation_stops_campaign_and_keeps_partial_stream(self):
        with tempfile.TemporaryDirectory() as directory:
            public = Path(directory)

            def interrupt(args, owned):
                stat = public.stat()
                trial_stream = TrialStream(public / "trials.jsonl")
                trial_stream.append({"completed": "fixture"})
                owned.append((public, stat.st_dev, stat.st_ino, 120, trial_stream))
                raise kicad.ProcessInterrupted({"cleanup_verified": True})

            args = ["--run", "--candidate", "a" * 40, "--task-id", "unit", "--run-id", "unit",
                    "--private-root", ".agent-work/unit/fixture", "--public-dir", str(public),
                    "--kicad-cli", "/nonexistent/kicad-cli"]
            with patch(__name__ + "._run_experiment", side_effect=interrupt) as run, contextlib.redirect_stderr(io.StringIO()):
                self.assertEqual(main(args), 130)
            run.assert_called_once()
            result = h.read_json(public / "interruption.json")
            self.assertEqual(result["experiment_status"], "PARTIAL")
            self.assertTrue(result["remaining_trials_not_dispatched"])
            self.assertEqual(json.loads((public / "trials.jsonl").read_text()), {"completed": "fixture"})

    def test_all_rows_both_arms_and_positive_variants_are_frozen(self):
        plan = h.read_json(Path(__file__).parents[2] / PLAN_PATH)
        validate_plan(plan)
        self.assertEqual(len(plan["scenarios"]), 20)
        self.assertEqual(len([case for case in plan["scenarios"] if case["kind"] == "native"]), 5)
        self.assertEqual({case["id"] for case in plan["scenarios"] if case["positive"]},
                         {"clean-erc", "clean-drc", "restored-evidence", "fresh-dependency"})

    def test_missing_native_capability_cannot_complete_experiment(self):
        plan = h.read_json(Path(__file__).parents[2] / PLAN_PATH)
        result = summarize([], plan)
        self.assertEqual(result["experiment_status"], "PARTIAL")
        self.assertEqual(result["arms"]["A"]["unexercised"], 60)

    def test_mock_report_does_not_count_as_native_case(self):
        # The ordinary unit fixture supplies real frozen file hashes, not native execution.
        from test_engineering_harness import HarnessTests
        context = HarnessTests()
        context.setUp()
        self.addCleanup(context.doCleanups)
        plan = h.read_json(Path(__file__).parents[2] / PLAN_PATH)
        case = next(case for case in plan["scenarios"] if case["id"] == "clean-drc")
        adapter = Mock(expected=TOOL)
        adapter.execute.return_value = observation()
        trial, _ = run_trial(
            case, "A", 1, context.root, context.binding, context.root / "mock-trial",
            adapter, plan, "unit-task", "unit-run",
        )
        self.assertEqual(trial["gate_decision"], "ALLOW_TEST_OUTPUT")
        self.assertFalse(trial["exercised"])
        self.assertFalse(trial["correct"])

    def test_both_native_paths_use_the_same_oracle_without_promoting_mocks(self):
        from test_engineering_harness import HarnessTests
        plan = h.read_json(Path(__file__).parents[2] / PLAN_PATH)
        for case in (case for case in plan["scenarios"] if case["kind"] == "native"):
            for arm in ("A", "B"):
                with self.subTest(case=case["id"], arm=arm):
                    context = HarnessTests()
                    context.setUp()
                    try:
                        manifest = h.read_json(context.fixture_root / "manifest.json")
                        context.binding = h.bind_inputs(
                            context.root, context.revision, context.revision,
                            [h.FIXTURE_PREFIX + name for name in manifest["files"]]
                            + [h.FIXTURE_PREFIX + "manifest.json"],
                            ["configuration.txt"], TOOL,
                        )
                        input_name = manifest["domain_inputs"][case["fixture"]][0]
                        rows = [violation(kind) for kind in case["expected_types"]]
                        adapter = Mock(expected=TOOL)
                        adapter.execute.return_value = observation(
                            synthetic_report(case["operation"], input_name, rows),
                            5 if rows else 0,
                        )
                        trial, _ = run_trial(
                            case, arm, 1, context.root, context.binding,
                            context.root / "native-mock", adapter, plan, "unit-task", "unit-run",
                        )
                        self.assertEqual(trial["gate_decision"], case["expected_gate"])
                        self.assertEqual(trial["validation_verdict"], case["expected_verdict"])
                        self.assertFalse(trial["exercised"])
                    finally:
                        context.doCleanups()

    def test_synthetic_variants_apply_identically_to_both_arms(self):
        from test_engineering_harness import HarnessTests
        plan = h.read_json(Path(__file__).parents[2] / PLAN_PATH)
        for case in (case for case in plan["scenarios"] if case["kind"] == "synthetic"):
            for arm in ("A", "B"):
                with self.subTest(case=case["id"], arm=arm):
                    context = HarnessTests()
                    context.setUp()
                    try:
                        trial, _ = run_trial(
                            case, arm, 1, context.root, context.binding,
                            context.root / "variant", Mock(expected=TOOL),
                            plan, "unit-task", "unit-run",
                        )
                        self.assertTrue(trial["correct"], trial)
                        self.assertTrue(trial["sentinel_unchanged"])
                        self.assertFalse(trial["forbidden_recorder_attempted"])
                    finally:
                        context.doCleanups()


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run", action="store_true")
    parser.add_argument("--candidate", required=True)
    parser.add_argument("--task-id", required=True)
    parser.add_argument("--run-id", required=True)
    parser.add_argument("--private-root", required=True)
    parser.add_argument("--public-dir", required=True)
    parser.add_argument("--kicad-cli", type=Path, required=True)
    args = parser.parse_args(argv)
    if not args.run:
        parser.error("--run is required for native trials")
    try:
        return run_experiment(args)
    except KeyboardInterrupt:
        print(json.dumps({"experiment_status": "PARTIAL", "reason": "OPERATOR_CANCELLED"}), file=sys.stderr)
        return 130
    except (OSError, ValueError, subprocess.SubprocessError) as exc:
        print(json.dumps({"experiment_status": "PARTIAL", "error": str(exc)}), file=sys.stderr)
        return 2


if __name__ == "__main__":
    if "--run" in sys.argv:
        raise SystemExit(main())
    unittest.main()
