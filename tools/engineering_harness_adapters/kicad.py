"""KiCad ERC/DRC transport for owned synthetic fixtures, not a sandbox."""
from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
import signal
import subprocess
import tempfile
import time
from dataclasses import asdict, dataclass

from agent_workflow import repo_path
from check_assembly_evidence import EvidenceError, digest_file, unique_keys


MAX_REPORT_BYTES = 2 * 1024 * 1024
COMMANDS = {"erc": ("sch", "erc"), "drc": ("pcb", "drc")}
FLAGS = ("--format", "json", "--severity-all", "--exit-code-violations")
IGNORED_CHECKS = {
    "erc": {"single_global_label", "four_way_junction", "simulation_model_issue", "footprint_filter"},
    "drc": {"missing_courtyard", "track_not_centered_on_via", "tuning_profile_track_geometries",
            "footprint_filters_mismatch", "footprint_type_mismatch"},
}


class AdapterError(ValueError):
    """A capability, input or result cannot be established."""


class ProcessInterrupted(KeyboardInterrupt):
    """Operator cancellation with the best available owned-process receipt."""

    def __init__(self, receipt: dict):
        super().__init__("OPERATOR_CANCELLED")
        self.receipt = receipt


@dataclass(frozen=True)
class ToolIdentity:
    sha256: str
    version: str


@dataclass
class Invocation:
    command: list[str]
    exit_code: int | None
    elapsed_seconds: float
    timed_out: bool
    cleanup_verified: bool
    stdout_sha256: str
    stderr_sha256: str
    report: bytes | None
    error: str | None = None
    source: str = "NATIVE_KICAD"
    attempts: int = 1
    stdout: bytes = b""
    stderr: bytes = b""

    def facts(self) -> dict:
        return {
            key: value for key, value in asdict(self).items()
            if key not in {"report", "stdout", "stderr"}
        } | {"raw_report_sha256": bytes_hash(self.report) if self.report is not None else None}


def bytes_hash(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def process_group(pgid: int) -> list[int]:
    result = subprocess.run(
        ["ps", "-axo", "pid=,pgid="], check=True, capture_output=True,
        text=True, timeout=10,
    )
    return [
        int(pid) for line in result.stdout.splitlines()
        for pid, group in [line.split()] if int(group) == pgid
    ]


def isolated_environment(root: Path) -> dict[str, str]:
    for name in ("home", "config", "cache", "data", "tmp"):
        (root / name).mkdir()
    return {
        "PATH": "/usr/bin:/bin:/usr/sbin:/sbin", "LANG": "C", "LC_ALL": "C",
        "HOME": str(root / "home"), "KICAD_CONFIG_HOME": str(root / "config"),
        "XDG_CONFIG_HOME": str(root / "config"), "XDG_CACHE_HOME": str(root / "cache"),
        "XDG_DATA_HOME": str(root / "data"), "TMPDIR": str(root / "tmp"),
    }


def run_process(command: list[str], cwd: Path, env: dict[str, str],
                receipts: Path, timeout: float) -> dict:
    """Shared test/native transport; the adapter alone builds native commands."""
    if not 0 < timeout <= 300:
        raise AdapterError("INVALID_TIMEOUT")
    started = time.monotonic()
    stdout_path, stderr_path = receipts / "stdout.txt", receipts / "stderr.txt"
    process = None
    interrupted, timed_out = False, False
    remaining = None
    error = None
    cleanup_error = None
    with stdout_path.open("xb") as stdout, stderr_path.open("xb") as stderr:
        try:
            process = subprocess.Popen(
                command, cwd=cwd, env=env, stdin=subprocess.DEVNULL,
                stdout=stdout, stderr=stderr, start_new_session=True,
            )
            try:
                process.wait(timeout=timeout)
            except subprocess.TimeoutExpired:
                timed_out = True
                error = "TIMEOUT"
        except KeyboardInterrupt:
            interrupted = True
            error = "OPERATOR_CANCELLED"
        except OSError as exc:
            error = f"PROCESS_ERRNO_{exc.errno}"
        finally:
            if process is not None:
                try:
                    if timed_out or interrupted or process.poll() is None:
                        _stop_owned_process(process)
                    remaining = process_group(process.pid)
                except KeyboardInterrupt:
                    interrupted = True
                    error = "OPERATOR_CANCELLED"
                    cleanup_error = "CLEANUP_INTERRUPTED"
                except (OSError, subprocess.SubprocessError) as exc:
                    cleanup_error = "CLEANUP_UNVERIFIED:" + type(exc).__name__
            elif not interrupted:
                remaining = []
    clean = remaining == [] and cleanup_error is None and (
        process is None or process.returncode is not None
    )
    result = {
        "pid": process.pid if process is not None else None,
        "exit_code": process.returncode if process is not None else None,
        "timed_out": timed_out, "interrupted": interrupted,
        "cleanup_verified": clean, "remaining_owned_pids": remaining,
        "cleanup_error": cleanup_error,
        "error": error or (None if clean else "CLEANUP_UNVERIFIED"),
        "elapsed_seconds": time.monotonic() - started,
        "stdout_sha256": digest_file(stdout_path), "stderr_sha256": digest_file(stderr_path),
        "receipt_written": True,
    }
    try:
        (receipts / "process.json").write_text(json.dumps(result, indent=2) + "\n")
    except OSError as exc:
        if not interrupted:
            raise
        result["receipt_written"] = False
        result["receipt_error"] = f"ERRNO_{exc.errno}"
        raise ProcessInterrupted(result) from exc
    if interrupted:
        raise ProcessInterrupted(result)
    return result


def _stop_owned_process(process: subprocess.Popen) -> None:
    # Only the process group created by this Popen belongs to this operation.
    try:
        os.killpg(process.pid, signal.SIGTERM)
    except ProcessLookupError:
        pass
    try:
        process.wait(timeout=5)
    except subprocess.TimeoutExpired:
        try:
            os.killpg(process.pid, signal.SIGKILL)
        except ProcessLookupError:
            pass
        process.wait(timeout=5)
    remaining = process_group(process.pid)
    if remaining:
        try:
            os.killpg(process.pid, signal.SIGKILL)
        except ProcessLookupError:
            pass
        deadline = time.monotonic() + 2
        while remaining and time.monotonic() < deadline:
            time.sleep(0.05)
            remaining = process_group(process.pid)


def _remove_owned_runtime(path: Path, identity: tuple[int, int]) -> bool:
    if path.is_symlink():
        return False
    current = path.stat()
    if (current.st_dev, current.st_ino) != identity:
        return False
    # Do not follow links even in the disposable, uniquely created runtime.
    for child in path.iterdir():
        if child.is_symlink() or child.is_file():
            child.unlink()
        elif child.is_dir():
            info = child.stat()
            if not _remove_owned_runtime(child, (info.st_dev, info.st_ino)):
                return False
        else:
            return False
    path.rmdir()
    return not path.exists()


class KiCad:
    def __init__(self, executable: Path, expected: ToolIdentity):
        if executable.name != "kicad-cli":
            raise AdapterError("NOT_KICAD_CLI")
        self.executable = executable.resolve(strict=True)
        if not self.executable.is_file() or not os.access(self.executable, os.X_OK):
            raise AdapterError("EXECUTABLE_UNAVAILABLE")
        self.expected = expected
        self.verify_identity()

    def verify_identity(self) -> None:
        if digest_file(self.executable) != self.expected.sha256:
            raise AdapterError("TOOL_IDENTITY_MISMATCH")

    def _invoke(self, arguments: list[str], receipts: Path, sources: dict[str, bytes],
                timeout: float) -> tuple[Invocation, bytes]:
        self.verify_identity()
        receipts = receipts.absolute()
        if any(path.is_symlink() for path in (receipts, *receipts.parents)):
            raise AdapterError("RECEIPT_PATH_SYMLINK")
        receipts.mkdir(parents=True, exist_ok=False)
        runtime = Path(tempfile.mkdtemp(prefix="runtime-", dir=receipts))
        info = runtime.stat()
        identity = (info.st_dev, info.st_ino)
        env = isolated_environment(runtime)
        inputs = runtime / "inputs"
        inputs.mkdir()
        for name, data in sources.items():
            target = repo_path(inputs, name)
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(data)
        command = [
            str(self.executable),
            *(str(inputs / item[8:]) if item.startswith("@source/") else
              str(runtime / "report.json") if item == "@report" else item
              for item in arguments),
        ]
        (receipts / "private-command.json").write_text(json.dumps(command) + "\n")
        try:
            observed = run_process(command, inputs, env, receipts, timeout)
        except ProcessInterrupted as exc:
            # Keep the partial runtime and streams, never publish or resume it.
            try:
                (receipts / "runtime.json").write_text(json.dumps({
                    "runtime": str(runtime), "temporary_environment_removed": False,
                    "retained_for_interruption": True,
                    "owned_process_cleanup_verified": exc.receipt["cleanup_verified"],
                }, indent=2) + "\n")
            except OSError as error:
                exc.receipt["runtime_receipt_error"] = f"ERRNO_{error.errno}"
            raise
        report_path = runtime / "report.json"
        report = None
        if report_path.is_symlink():
            observed["error"] = "REPORT_SYMLINK"
        elif report_path.exists():
            if not report_path.is_file() or report_path.stat().st_size > MAX_REPORT_BYTES:
                observed["error"] = "INVALID_REPORT_SIZE_OR_TYPE"
            else:
                report = report_path.read_bytes()
                (receipts / "raw-report.json").write_bytes(report)
        unchanged = all(
            not repo_path(inputs, name).is_symlink()
            and repo_path(inputs, name).is_file()
            and repo_path(inputs, name).read_bytes() == data
            for name, data in sources.items()
        )
        if not unchanged:
            observed["error"] = "TOOL_MUTATED_INPUT_COPY"
        self.verify_identity()
        clean = observed["cleanup_verified"]
        if clean:
            clean = _remove_owned_runtime(runtime, identity)
        observed["cleanup_verified"] = clean
        if not clean:
            observed["error"] = "CLEANUP_UNVERIFIED"
        (receipts / "runtime.json").write_text(json.dumps({
            "runtime": str(runtime), "temporary_environment_removed": clean,
            "input_copies_unchanged": unchanged,
        }, indent=2) + "\n")
        invocation = Invocation(
            command=["kicad-cli", *arguments],
            **{key: observed[key] for key in (
                "exit_code", "elapsed_seconds", "timed_out", "cleanup_verified",
                "stdout_sha256", "stderr_sha256", "error",
            )},
            report=report,
            stdout=(receipts / "stdout.txt").read_bytes(),
            stderr=(receipts / "stderr.txt").read_bytes(),
        )
        return invocation, (receipts / "stdout.txt").read_bytes()

    def preflight(self, receipts: Path) -> dict:
        facts = {}
        for name, arguments in (
            ("version", ["--version"]), ("erc", ["sch", "erc", "--help"]),
            ("drc", ["pcb", "drc", "--help"]),
        ):
            observed, output = self._invoke(arguments, receipts / name, {}, 20)
            if observed.exit_code != 0 or observed.error or not observed.cleanup_verified:
                raise AdapterError(f"PREFLIGHT_{name.upper()}_FAILED")
            if name == "version" and output.decode().strip() != self.expected.version:
                raise AdapterError("VERSION_MISMATCH")
            if name != "version" and not all(
                text in output for text in (b"--format", b"json", b"--exit-code-violations")
            ):
                raise AdapterError("REQUIRED_COMMAND_FLAGS_UNAVAILABLE")
            facts[name] = observed.facts()
        return {"identity": asdict(self.expected), "help": facts, "domain_acceptance": "NOT_RUN"}

    def execute(self, operation: str, input_name: str, sources: dict[str, bytes],
                receipts: Path, timeout: float = 20) -> Invocation:
        if operation not in COMMANDS:
            raise AdapterError("OUT_OF_MVP_SCOPE")
        suffix = ".kicad_sch" if operation == "erc" else ".kicad_pcb"
        if input_name not in sources or not input_name.endswith(suffix):
            raise AdapterError("INVALID_DOMAIN_INPUT")
        arguments = [*COMMANDS[operation], *FLAGS, "--output", "@report", f"@source/{input_name}"]
        return self._invoke(arguments, receipts, sources, timeout)[0]


def parse_report(data: bytes | None, operation: str, exit_code: int | None,
                 expected_version: str, expected_source: str) -> dict:
    if data is None:
        raise AdapterError("MISSING_REPORT")
    if len(data) > MAX_REPORT_BYTES:
        raise AdapterError("REPORT_TOO_LARGE")
    try:
        report = json.loads(data, object_pairs_hook=unique_keys)
    except (json.JSONDecodeError, UnicodeDecodeError, EvidenceError) as exc:
        raise AdapterError("CORRUPT_REPORT") from exc
    if not isinstance(report, dict) or report.get("kicad_version") != expected_version:
        raise AdapterError("REPORT_VERSION_MISMATCH")
    if report.get("$schema") != f"https://schemas.kicad.org/{operation}.v1.json":
        raise AdapterError("REPORT_SCHEMA_MISMATCH")
    if report.get("source") != expected_source:
        raise AdapterError("REPORT_SOURCE_MISMATCH")
    if report.get("coordinate_units") != "mm" or report.get("included_severities") != [
        "error", "warning", "exclusion"
    ]:
        raise AdapterError("REPORT_THRESHOLD_MISMATCH")
    ignored = report.get("ignored_checks")
    if not isinstance(ignored, list) or not all(
        isinstance(item, dict) and isinstance(item.get("key"), str) for item in ignored
    ) or {item["key"] for item in ignored} != IGNORED_CHECKS.get(operation):
        raise AdapterError("REPORT_IGNORED_CHECKS_MISMATCH")
    if operation == "erc":
        sheets = report.get("sheets")
        if not isinstance(sheets, list) or not sheets:
            raise AdapterError("MISSING_ERC_SHEETS")
        collections = []
        for sheet in sheets:
            if not isinstance(sheet, dict) or not isinstance(sheet.get("violations"), list):
                raise AdapterError("INVALID_ERC_SHEET")
            collections.append(sheet["violations"])
    elif operation == "drc":
        collections = []
        for key in ("violations", "unconnected_items", "schematic_parity"):
            value = report.get(key)
            if not isinstance(value, list):
                raise AdapterError(f"MISSING_DRC_{key.upper()}")
            collections.append(value)
    else:
        raise AdapterError("OUT_OF_MVP_SCOPE")
    violations = []
    for collection in collections:
        for violation in collection:
            if not isinstance(violation, dict) or not all(
                isinstance(violation.get(key), str) and violation[key]
                for key in ("type", "severity", "description")
            ) or violation["severity"] not in ("error", "warning", "exclusion") or not (
                isinstance(violation.get("items"), list) and violation["items"]
            ):
                raise AdapterError("INVALID_VIOLATION")
            violations.append(violation)
    if exit_code not in (0, 5):
        raise AdapterError("DOMAIN_COMMAND_FAILED")
    if (bool(violations) and exit_code != 5) or (not violations and exit_code != 0):
        raise AdapterError("EXIT_REPORT_DISAGREEMENT")
    return {
        "verdict": "FAIL" if violations else "PASS",
        "violation_count": len(violations),
        "violation_types": sorted({v["type"] for v in violations}),
        "severities": sorted({v["severity"] for v in violations}),
        "kicad_version": report["kicad_version"],
    }
