#!/usr/bin/env python3
"""Test-only EDA evidence gating on a cooperative, explicitly controlled path."""
from __future__ import annotations

import argparse
import base64
import json
import os
from pathlib import Path
import re
import sys
import uuid
from dataclasses import asdict, dataclass, field
from enum import StrEnum

from agent_workflow import WorkflowError, repo_path
from check_assembly_evidence import EvidenceError, digest_file, git_bytes, unique_keys
from engineering_harness_adapters.kicad import (
    AdapterError, IGNORED_CHECKS, Invocation, KiCad, ProcessInterrupted, ToolIdentity,
    bytes_hash, parse_report,
)


class HarnessError(ValueError):
    pass


class Lifecycle(StrEnum):
    PLANNED = "PLANNED"
    SNAPSHOTTED = "SNAPSHOTTED"
    EXECUTING = "EXECUTING"
    VALIDATING = "VALIDATING"
    SUCCEEDED = "SUCCEEDED"
    FAILED = "FAILED"
    BLOCKED = "BLOCKED"


class Verdict(StrEnum):
    NOT_RUN = "NOT_RUN"
    PASS = "PASS"
    FAIL = "FAIL"
    ERROR = "ERROR"


class Freshness(StrEnum):
    UNKNOWN = "UNKNOWN"
    CURRENT = "CURRENT"
    STALE = "STALE"


class Gate(StrEnum):
    NOT_EVALUATED = "NOT_EVALUATED"
    ALLOW_TEST_OUTPUT = "ALLOW_TEST_OUTPUT"
    BLOCKED = "BLOCKED"
    HUMAN_REQUIRED = "HUMAN_REQUIRED"


class Recovery(StrEnum):
    NOT_NEEDED = "NOT_NEEDED"
    NOT_ATTEMPTED = "NOT_ATTEMPTED"
    ROLLBACK_OK = "ROLLBACK_OK"
    ROLLBACK_FAILED = "ROLLBACK_FAILED"


POLICY = {
    "scope": "SYNTHETIC_ONLY",
    "purpose": "TEST_ONLY_REVIEW_READINESS",
    "reported_violations_allowed": 0,
    "severity": "all",
    "exclusions": [],
    "retry_limit": 0,
    "irreversible_actions": "OUT_OF_MVP_SCOPE",
    "native_default_ignored_checks": {name: sorted(keys) for name, keys in IGNORED_CHECKS.items()},
}
FIXTURE_PREFIX = "tools/tests/fixtures/engineering_harness/"
HASH = re.compile(r"[0-9a-f]{64}")
COMMIT = re.compile(r"[0-9a-f]{40}|[0-9a-f]{64}")


def json_bytes(value: object) -> bytes:
    return (json.dumps(value, sort_keys=True, indent=2, allow_nan=False) + "\n").encode()


def read_json(path: Path) -> dict:
    def invalid_constant(value: str):
        raise HarnessError(f"NONFINITE_JSON_{value}")
    with path.open() as stream:
        data = json.load(stream, object_pairs_hook=unique_keys, parse_constant=invalid_constant)
    if not isinstance(data, dict):
        raise HarnessError("JSON_OBJECT_REQUIRED")
    return data


def regular_hash(root: Path, name: str) -> str:
    path = repo_path(root, name)
    if not path.is_file() or path.stat().st_nlink != 1:
        raise HarnessError(f"MISSING_OR_NONEXCLUSIVE_FILE:{name}")
    return digest_file(path)


@dataclass(frozen=True)
class Bindings:
    source_revision: str
    config_revision: str
    files: dict[str, str]
    tool: ToolIdentity
    policy_sha256: str


def bind_inputs(root: Path, source_revision: str, config_revision: str,
                inputs: list[str], configuration: list[str], tool: ToolIdentity) -> Bindings:
    if not COMMIT.fullmatch(source_revision) or not COMMIT.fullmatch(config_revision):
        raise HarnessError("IMMUTABLE_REVISIONS_REQUIRED")
    if not inputs or not configuration or len(set(inputs + configuration)) != len(inputs + configuration):
        raise HarnessError("NONEMPTY_DISTINCT_INPUTS_AND_CONFIG_REQUIRED")
    hashes = {}
    for revision, names in ((source_revision, inputs), (config_revision, configuration)):
        if git_bytes(root, "cat-file", "-t", revision).strip() != b"commit":
            raise HarnessError("REVISION_IS_NOT_COMMIT")
        for name in names:
            digest = regular_hash(root, name)
            if bytes_hash(git_bytes(root, "show", f"{revision}:{name}")) != digest:
                raise HarnessError(f"FROZEN_INPUT_MISMATCH:{name}")
            hashes[name] = digest
    return Bindings(source_revision, config_revision, hashes, tool, bytes_hash(json_bytes(POLICY)))


def freshness(root: Path, binding: Bindings, tool: ToolIdentity,
              mode: str = "CURRENT") -> tuple[Freshness, list[str]]:
    if mode == "HISTORICAL":
        return Freshness.UNKNOWN, ["CURRENT_FRESHNESS_NOT_CHECKED"]
    if mode != "CURRENT" or not binding.files:
        return Freshness.UNKNOWN, ["INVALID_VERIFICATION_MODE_OR_BINDINGS"]
    missing, changed = [], []
    for name, expected in binding.files.items():
        try:
            actual = regular_hash(root, name)
        except (OSError, HarnessError, WorkflowError):
            missing.append(name)
        else:
            if actual != expected:
                changed.append(name)
    if tool != binding.tool or binding.policy_sha256 != bytes_hash(json_bytes(POLICY)):
        changed.append("tool-or-policy")
    if changed:
        return Freshness.STALE, ["CHANGED_DIRECT_INPUT:" + name for name in changed] + [
            "MISSING_DIRECT_INPUT:" + name for name in missing
        ]
    if missing:
        return Freshness.UNKNOWN, ["MISSING_DIRECT_INPUT:" + name for name in missing]
    return Freshness.CURRENT, []


class OwnedOutputs:
    """Durable small snapshots and cooperative revision fences, not OS isolation."""

    def __init__(self, root: Path, names: tuple[str, ...], initial: dict[str, bytes] | None = None):
        if not names or len({name.casefold() for name in names}) != len(names):
            raise HarnessError("INVALID_OWNED_OUTPUTS")
        self.root = root.absolute()
        if any(path.is_symlink() for path in (self.root, *self.root.parents)):
            raise HarnessError("OUTPUT_ROOT_SYMLINK")
        self.root.mkdir(parents=True, exist_ok=False)
        self.output = self.root / "outputs"
        self.output.mkdir()
        self.journal = self.root / "journal"
        self.journal.mkdir()
        self.token = str(uuid.uuid4())
        self.names = names
        self.marker = json_bytes({"token": self.token, "owned_outputs": names, "scope": "SYNTHETIC_ONLY"})
        (self.root / "owner.json").write_bytes(self.marker)
        stat = self.output.stat()
        self.identity = (stat.st_dev, stat.st_ino)
        stat = self.journal.stat()
        self.journal_identity = (stat.st_dev, stat.st_ino)
        self.before: dict[str, bytes | None] = {}
        self.expected: dict[str, str | None] = {}
        seeds = initial or {}
        if not set(seeds).issubset(names):
            raise HarnessError("UNOWNED_SEED")
        for name in names:
            path = repo_path(self.output, name)
            path.parent.mkdir(parents=True, exist_ok=True)
            if name in seeds:
                path.write_bytes(seeds[name])
            self.before[name] = seeds.get(name)
            self.expected[name] = bytes_hash(seeds[name]) if name in seeds else None
        self._save("snapshot.json", {
            name: base64.b64encode(data).decode() if data is not None else None
            for name, data in self.before.items()
        })
        self._save("initial-hashes.json", self.expected)

    def _save(self, name: str, data: object) -> None:
        self._check_root()
        with (self.journal / name).open("xb") as stream:
            stream.write(json_bytes(data))

    def _check_root(self) -> None:
        if any(path.is_symlink() for path in (self.output, self.journal, self.root, *self.root.parents)):
            raise HarnessError("OWNERSHIP_CHANGED")
        stat = self.output.stat()
        if (stat.st_dev, stat.st_ino) != self.identity:
            raise HarnessError("OWNERSHIP_CHANGED")
        stat = self.journal.stat()
        if (stat.st_dev, stat.st_ino) != self.journal_identity:
            raise HarnessError("JOURNAL_OWNERSHIP_CHANGED")
        marker = self.root / "owner.json"
        if marker.is_symlink() or not marker.is_file() or marker.read_bytes() != self.marker:
            raise HarnessError("OWNERSHIP_CHANGED")

    def current(self, name: str) -> str | None:
        self._check_root()
        if name not in self.names:
            raise HarnessError("OUTPUT_NOT_OWNED")
        path = repo_path(self.output, name)
        if not path.exists():
            return None
        return regular_hash(self.output, name)

    def write(self, name: str, data: bytes) -> None:
        if name not in self.names or self.current(name) != self.expected[name]:
            raise HarnessError("OUTPUT_REVISION_CONFLICT")
        target = repo_path(self.output, name)
        temporary = target.with_name(target.name + "." + str(uuid.uuid4()) + ".pending")
        with temporary.open("xb") as stream:
            stream.write(data)
        if self.current(name) != self.expected[name]:
            raise HarnessError("OUTPUT_REVISION_CONFLICT")
        os.replace(temporary, target)
        self.expected[name] = bytes_hash(data)
        self._save(f"write-{uuid.uuid4()}.json", {"path": name, "sha256": self.expected[name]})

    def restore(self) -> Recovery:
        try:
            # Precheck the complete owned set before restoring any member.
            for name in self.names:
                if self.current(name) != self.expected[name]:
                    raise HarnessError("OUTPUT_REVISION_CONFLICT")
            for name, data in self.before.items():
                if data is None:
                    if self.current(name) is not None:
                        repo_path(self.output, name).unlink()
                    self.expected[name] = None
                else:
                    self.write(name, data)
            if any(self.current(name) != (bytes_hash(data) if data is not None else None)
                   for name, data in self.before.items()):
                raise HarnessError("RESTORE_HASH_MISMATCH")
        except (OSError, WorkflowError, HarnessError) as exc:
            # If the journal itself changed, return failure without writing into it.
            try:
                self._check_root()
            except (OSError, HarnessError):
                return Recovery.ROLLBACK_FAILED
            self._save(f"recovery-{uuid.uuid4()}.json", {
                "outcome": "ROLLBACK_FAILED", "error_type": type(exc).__name__,
            })
            return Recovery.ROLLBACK_FAILED
        self._save(f"recovery-{uuid.uuid4()}.json", {"outcome": "ROLLBACK_OK"})
        return Recovery.ROLLBACK_OK


@dataclass
class Operation:
    task_id: str
    run_id: str
    operation: str
    operation_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    operation_lifecycle: Lifecycle = Lifecycle.PLANNED
    validation_verdict: Verdict = Verdict.NOT_RUN
    evidence_freshness: Freshness = Freshness.UNKNOWN
    gate_decision: Gate = Gate.NOT_EVALUATED
    recovery_outcome: Recovery = Recovery.NOT_NEEDED
    gate_reasons: list[str] = field(default_factory=list)
    verification_mode: str = "CURRENT"
    binding: dict = field(default_factory=dict)
    invocation: dict = field(default_factory=dict)
    semantics: dict = field(default_factory=dict)
    evidence: dict[str, str] = field(default_factory=dict)
    retries: int = 0
    retry_reason: str = "NO_AUTOMATIC_RETRY"
    model_identity: str = "UNKNOWN"
    cost: str = "UNKNOWN"
    scope: str = "SYNTHETIC_ONLY"
    purpose: str = "TEST_ONLY_REVIEW_READINESS"

    def facts(self) -> dict:
        if self.gate_decision == Gate.ALLOW_TEST_OUTPUT and not (
            self.operation_lifecycle == Lifecycle.SUCCEEDED
            and self.validation_verdict == Verdict.PASS
            and self.evidence_freshness == Freshness.CURRENT
            and self.recovery_outcome == Recovery.NOT_NEEDED
            and self.evidence and not self.gate_reasons
        ):
            raise HarnessError("INCONSISTENT_ALLOW")
        return asdict(self)


def out_of_scope(operation: str, task_id: str, run_id: str) -> Operation | None:
    if operation in ("erc", "drc"):
        return None
    return Operation(
        task_id, run_id, operation, operation_lifecycle=Lifecycle.BLOCKED,
        gate_decision=Gate.HUMAN_REQUIRED, gate_reasons=["OUT_OF_MVP_SCOPE"],
    )


def finish_observation(record: Operation, observation: Invocation, binding: Bindings,
                       root: Path, outputs: OwnedOutputs, tool: ToolIdentity,
                       input_name: str, mode: str = "CURRENT") -> Operation:
    record.binding = asdict(binding)
    record.invocation = observation.facts()
    record.verification_mode = mode
    record.operation_lifecycle = Lifecycle.VALIDATING
    record.evidence_freshness, record.gate_reasons = freshness(root, binding, tool, mode)
    # Keep the original failure/report separate from restored publication outputs.
    outputs._save("invocation.json", observation.facts())
    if observation.report is not None:
        with (outputs.journal / "original-report.json").open("xb") as stream:
            stream.write(observation.report)
        record.evidence["original_report_sha256"] = bytes_hash(observation.report)
    for key in ("stdout_sha256", "stderr_sha256"):
        value = getattr(observation, key)
        data = getattr(observation, key.removesuffix("_sha256"))
        if not HASH.fullmatch(value) or bytes_hash(data) != value:
            record.gate_reasons.append("MISSING_OR_MISMATCHED_LOG")
        else:
            record.evidence[key] = value
            with (outputs.journal / (key.removesuffix("_sha256") + ".txt")).open("xb") as stream:
                stream.write(data)
    if observation.error or observation.timed_out or not observation.cleanup_verified:
        record.gate_reasons.append(observation.error or "EXECUTION_OR_CLEANUP_FAILED")
        record.validation_verdict = Verdict.NOT_RUN
    else:
        try:
            record.semantics = parse_report(
                observation.report, record.operation, observation.exit_code,
                tool.version, input_name,
            )
        except AdapterError as exc:
            record.validation_verdict = Verdict.ERROR
            record.gate_reasons.append(str(exc))
        else:
            record.validation_verdict = Verdict(record.semantics["verdict"])
            if record.validation_verdict != Verdict.PASS:
                record.gate_reasons.append("DOMAIN_VIOLATIONS")
    if not record.gate_reasons:
        try:
            if observation.report is None:
                raise HarnessError("MISSING_REPORT")
            outputs.write("report.json", observation.report)
            if outputs.current("report.json") != record.evidence["original_report_sha256"]:
                raise HarnessError("PUBLISHED_REPORT_MISMATCH")
        except (OSError, WorkflowError, HarnessError) as exc:
            record.gate_reasons.append(f"PUBLICATION_FAILED:{type(exc).__name__}")
    if record.gate_reasons:
        record.operation_lifecycle = Lifecycle.BLOCKED if observation.exit_code is None else Lifecycle.FAILED
        record.gate_decision = Gate.BLOCKED
        record.recovery_outcome = outputs.restore() if observation.cleanup_verified else Recovery.NOT_ATTEMPTED
        if not observation.cleanup_verified:
            record.gate_reasons.append("RECOVERY_UNSAFE_CLEANUP_UNKNOWN")
        if record.recovery_outcome == Recovery.ROLLBACK_FAILED:
            record.gate_reasons.append("RECOVERY_RECONCILIATION_REQUIRED")
    else:
        record.operation_lifecycle = Lifecycle.SUCCEEDED
        record.gate_decision = Gate.ALLOW_TEST_OUTPUT
        published_hash = outputs.current("report.json")
        if published_hash is None:
            raise HarnessError("PUBLICATION_DISAPPEARED")
        record.evidence["published_report_sha256"] = published_hash
    outputs._save("operation.json", record.facts())
    return record


def recheck_decision(record: Operation, root: Path, binding: Bindings,
                     outputs: OwnedOutputs, tool: ToolIdentity) -> dict:
    current, reasons = freshness(root, binding, tool, record.verification_mode)
    if record.binding != asdict(binding):
        reasons.append("OPERATION_BINDING_CHANGED")
    if record.validation_verdict != Verdict.PASS or record.operation_lifecycle != Lifecycle.SUCCEEDED:
        reasons.append("OPERATION_NOT_SUCCESSFUL")
    if record.gate_decision != Gate.ALLOW_TEST_OUTPUT:
        reasons.append("ORIGINAL_GATE_NOT_ALLOW")
    for name, key in (("report.json", "published_report_sha256"),):
        expected = record.evidence.get(key)
        try:
            actual = outputs.current(name)
        except (OSError, WorkflowError, HarnessError):
            actual = None
        if not expected or actual != expected:
            reasons.append("REPORT_MISSING_OR_CHANGED")
    for filename, key in (
        ("original-report.json", "original_report_sha256"),
        ("invocation.json", None),
        ("stdout.txt", "stdout_sha256"),
        ("stderr.txt", "stderr_sha256"),
        ("operation.json", None),
    ):
        path = outputs.journal / filename
        if path.is_symlink() or not path.is_file():
            reasons.append("EVIDENCE_MISSING_OR_CHANGED")
        elif key and digest_file(path) != record.evidence.get(key):
            reasons.append("EVIDENCE_MISSING_OR_CHANGED")
        elif filename in ("invocation.json", "operation.json"):
            try:
                expected_record = record.invocation if filename == "invocation.json" else record.facts()
                unchanged = read_json(path) == expected_record
            except (OSError, ValueError):
                unchanged = False
            if not unchanged:
                reasons.append("RETAINED_RECORD_CHANGED")
    return {
        "purpose": "TEST_ONLY_REVIEW_READINESS",
        "gate_decision": "BLOCKED" if reasons else "ALLOW_TEST_OUTPUT",
        "evidence_freshness": current, "reasons": reasons,
        "binding_sha256": bytes_hash(json_bytes(asdict(binding))),
        "operation_id": record.operation_id,
    }


def run_native(root: Path, operation: str, input_name: str, native_inputs: list[str],
               binding: Bindings, outputs: OwnedOutputs, adapter: KiCad,
               task_id: str, run_id: str, timeout: float = 20) -> Operation:
    rejected = out_of_scope(operation, task_id, run_id)
    if rejected is not None:
        return rejected
    state, reasons = freshness(root, binding, adapter.expected)
    if state != Freshness.CURRENT:
        return Operation(
            task_id, run_id, operation, operation_lifecycle=Lifecycle.BLOCKED,
            gate_decision=Gate.BLOCKED, evidence_freshness=state, gate_reasons=reasons,
        )
    if input_name not in native_inputs or not set(native_inputs).issubset(binding.files):
        raise HarnessError("NATIVE_INPUTS_NOT_BOUND")
    manifest_path = FIXTURE_PREFIX + "manifest.json"
    if manifest_path not in binding.files or not all(name.startswith(FIXTURE_PREFIX) for name in native_inputs):
        raise HarnessError("ONLY_DECLARED_SYNTHETIC_FIXTURES")
    manifest = read_json(repo_path(root, manifest_path))
    expected_names = [name.removeprefix(FIXTURE_PREFIX) for name in native_inputs]
    if manifest.get("scope") != "SYNTHETIC_ONLY" or expected_names not in manifest["domain_inputs"].values():
        raise HarnessError("UNDECLARED_FIXTURE_INPUT_SET")
    for name in expected_names:
        if manifest["files"].get(name) != binding.files[FIXTURE_PREFIX + name]:
            raise HarnessError("FIXTURE_MANIFEST_MISMATCH")
    if len({Path(name).name for name in native_inputs}) != len(native_inputs):
        raise HarnessError("AMBIGUOUS_NATIVE_INPUT_NAMES")
    sources = {Path(name).name: repo_path(root, name).read_bytes() for name in native_inputs}
    record = Operation(task_id, run_id, operation, operation_lifecycle=Lifecycle.EXECUTING)
    observation = adapter.execute(
        operation, Path(input_name).name, sources, outputs.root / "native", timeout,
    )
    return finish_observation(
        record, observation, binding, root, outputs, adapter.expected, Path(input_name).name,
    )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("request", type=Path)
    parser.add_argument("--root", type=Path, default=Path.cwd())
    parser.add_argument("--workspace", required=True, help="New owned repository-relative directory")
    parser.add_argument("--kicad-cli", type=Path)
    args = parser.parse_args(argv)
    outputs = None
    try:
        request = read_json(args.request)
        if request.get("scope") != "SYNTHETIC_ONLY":
            raise HarnessError("TEST_ONLY_REQUEST_REQUIRED")
        operation = request["operation"]
        rejected = out_of_scope(operation, request["task_id"], request["run_id"])
        if rejected:
            print(json_bytes(rejected.facts()).decode(), end="")
            return 2
        allowed = {
            "scope", "operation", "task_id", "run_id", "source_revision", "config_revision",
            "inputs", "configuration", "native_inputs", "input_name", "tool", "timeout",
        }
        if set(request) != allowed or args.kicad_cli is None:
            raise HarnessError("INVALID_REQUEST_FIELDS_OR_TOOL")
        expected = ToolIdentity(**request["tool"])
        binding = bind_inputs(
            args.root, request["source_revision"], request["config_revision"],
            request["inputs"], request["configuration"], expected,
        )
        adapter = KiCad(args.kicad_cli, expected)
        if not args.workspace.startswith(".agent-work/"):
            raise HarnessError("WORKSPACE_MUST_BE_IGNORED_TASK_SCRATCH")
        outputs = OwnedOutputs(repo_path(args.root, args.workspace), ("report.json",))
        adapter.preflight(outputs.root / "preflight")
        record = run_native(
            args.root, operation, request["input_name"], request["native_inputs"],
            binding, outputs, adapter, request["task_id"], request["run_id"], request["timeout"],
        )
        decision = recheck_decision(record, args.root, binding, outputs, expected)
        outputs._save("decision.json", decision)
        print(json_bytes({"operation": record.facts(), "decision": decision}).decode(), end="")
        return 0 if decision["gate_decision"] == "ALLOW_TEST_OUTPUT" else 2
    except KeyboardInterrupt as exc:
        cancelled = {
            "operation_lifecycle": "FAILED", "validation_verdict": "NOT_RUN",
            "evidence_freshness": "UNKNOWN", "gate_decision": "BLOCKED",
            "gate_reasons": ["OPERATOR_CANCELLED"], "recovery_outcome": "NOT_ATTEMPTED",
            "owned_process_cleanup_verified": exc.receipt["cleanup_verified"]
            if isinstance(exc, ProcessInterrupted) else "UNKNOWN",
            "partial_state_retained": outputs is not None,
        }
        if isinstance(exc, ProcessInterrupted):
            cancelled["transport_receipt_status"] = {
                key: exc.receipt.get(key, "UNKNOWN")
                for key in ("receipt_written", "receipt_error", "runtime_receipt_error")
            }
        if outputs is not None:
            try:
                outputs._save("cancelled.json", cancelled)
            except (OSError, HarnessError) as error:
                cancelled["receipt_error"] = type(error).__name__
        print(json.dumps(cancelled), file=sys.stderr)
        return 130
    except (OSError, KeyError, TypeError, ValueError, EvidenceError, WorkflowError) as exc:
        print(json.dumps({"state": "BLOCKED", "error_type": type(exc).__name__,
                          "error": str(exc)}), file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
