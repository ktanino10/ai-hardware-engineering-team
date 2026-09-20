#!/usr/bin/env python3
"""Compile the hash-selected Bosch source; no Git, old campaign, SDK or device dependency."""
import argparse
import datetime as dt
import hashlib
import json
import os
from pathlib import Path
import platform
import shutil
import signal
import subprocess
import sys
import time

PACKAGE = Path(__file__).resolve().parent
ROOT = PACKAGE.parents[3]


def sha(data):
    return hashlib.sha256(data).hexdigest()


def artifact(path):
    data = path.read_bytes()
    return {"path": str(path), "bytes": len(data), "sha256": sha(data)}


def checked(path, binding):
    if any(p.is_symlink() for p in (path, *path.parents)) or not path.is_file():
        raise ValueError("Missing or symlinked input: " + str(path))
    data = path.read_bytes()
    if len(data) != binding["bytes"] or sha(data) != binding["sha256"]:
        raise ValueError("Bound input differs: " + str(path))
    return data


def save(path, value):
    with path.open("x", encoding="ascii") as handle:
        json.dump(value, handle, indent=2)
        handle.write("\n")


def parse_cases(data, expected):
    rows = [json.loads(line) for line in data.decode("ascii").splitlines()]
    if len(rows) != expected + 1 or rows[-1].get("cases") != expected:
        raise ValueError("Missing cases or completion summary")
    return rows[:-1], rows[-1]


def paired(left, right):
    if len(left) != len(right):
        raise ValueError("Executed cases and declared oracles have different lengths")
    return zip(left, right)


def run(args):
    binding = json.loads((PACKAGE / "candidate.json").read_bytes())
    source = Path(args.bmi2).absolute() if args.bmi2 else PACKAGE / "bmi2.c"
    expected_sha = args.expected_sha256 if args.bmi2 else binding["derivative"]["sha256"]
    if bool(args.bmi2) != bool(args.expected_sha256):
        raise ValueError("--bmi2 and --expected-sha256 must be supplied together")
    if expected_sha != binding["derivative"]["sha256"]:
        raise ValueError("Expected hash is not this selected candidate's final source")
    checked(source, binding["derivative"])
    vendor = Path(args.vendor_dir).absolute() if args.vendor_dir else ROOT / binding["vendor_directory"]
    inputs = [source, PACKAGE / "candidate.json"]
    for row in binding["unchanged_vendor_files"]:
        path = vendor / Path(row["path"]).name
        checked(path, row)
        inputs.append(path)
    fixture = ROOT / binding["reused_fixture"]["path"]
    legacy = ROOT / binding["legacy_binding"]["path"]
    for path, row in [(fixture, binding["reused_fixture"]), (legacy, binding["legacy_binding"])]:
        checked(path, row)
        inputs.append(path)
    for row in binding["test_files"]:
        path = PACKAGE / row["path"]
        checked(path, row)
        inputs.append(path)
    matrix = json.loads((PACKAGE / "case-matrix.json").read_bytes())
    suites = list(dict.fromkeys(args.suite or list(matrix["suites"])))
    selected = {
        name: [row for row in matrix["suites"][name]
               if not args.series or row["series"] in args.series]
        for name in suites
    }
    if any(not rows for rows in selected.values()):
        raise ValueError("Every requested suite must select at least one declared case")
    if args.series and "legacy" in selected:
        raise ValueError("The immutable legacy binding runs only its complete 25/36/12 groups")
    known_series = {row["series"] for name in suites for row in matrix["suites"][name]}
    if set(args.series or []) - known_series:
        raise ValueError("Unknown series requested")
    output, output_root = Path(args.output).absolute(), Path(args.output_root).absolute()
    if (output == output_root or not output.is_relative_to(output_root) or
            ".." in output.parts or ".." in output_root.parts or not output_root.is_dir()):
        raise ValueError("Output must be a fresh strict child of the existing explicit output root")
    if any(p.is_symlink() for p in (output, *output.parents)):
        raise ValueError("Symlink in output path")
    if output.exists() or not output.parent.is_dir():
        raise ValueError("Output must not exist and its parent must exist")
    if any(p == output or p.is_relative_to(output) for p in inputs):
        raise ValueError("Output overlaps source inputs")
    compiler = shutil.which(args.cc)
    if compiler is None:
        raise RuntimeError("Installed clang is required; nothing will be installed")
    snapshots = {str(p): artifact(p) for p in inputs}
    output.mkdir()
    for name in ("home", "tmp", "cache"):
        (output / name).mkdir()
    env = {
        "PATH": os.pathsep.join((str(Path(compiler).parent), "/usr/bin", "/bin", "/usr/sbin", "/sbin")),
        "HOME": str(output / "home"), "TMPDIR": str(output / "tmp"),
        "XDG_CACHE_HOME": str(output / "cache"), "PYTHONDONTWRITEBYTECODE": "1",
        "LANG": "C", "LC_ALL": "C",
        "ASAN_OPTIONS": "detect_stack_use_after_return=1:abort_on_error=0:exitcode=91",
        "UBSAN_OPTIONS": "halt_on_error=1:print_stacktrace=1:exitcode=92",
    }
    report = {
        "classification": "SELECTED_SOURCE_AUTHOR_HOST_ONLY_NOT_INDEPENDENT_ACCEPTANCE",
        "status": "RUNNING", "started_at": dt.datetime.now(dt.timezone.utc).isoformat(),
        "selected_source": snapshots[str(source)], "inputs": list(snapshots.values()),
        "matrix_sha256": sha((PACKAGE / "case-matrix.json").read_bytes()),
        "planned_counts": {name: len(rows) for name, rows in selected.items()},
        "commands": [], "results": {}, "executed_cases": 0, "unique_scenarios": 0,
        "python": sys.version, "platform": platform.platform(),
        "old_campaigns_executed": False, "SDK_or_device_access": False,
        "C3": "OPEN_MEDIUM_UNSELECTED_NOT_QUALIFIED_BY_IMMEDIATE_READY_MODEL",
    }
    completed_scenarios = set()

    def command(label, argv, timeout):
        started = time.monotonic()
        with (output / (label + ".stdout")).open("xb") as stdout, \
                (output / (label + ".stderr")).open("xb") as stderr:
            process = subprocess.Popen(argv, cwd=ROOT, env=env, stdin=subprocess.DEVNULL,
                                       stdout=stdout, stderr=stderr, start_new_session=True)
            timed_out = interrupted = False
            try:
                code = process.wait(timeout=timeout)
            except (subprocess.TimeoutExpired, KeyboardInterrupt) as exc:
                timed_out = isinstance(exc, subprocess.TimeoutExpired)
                interrupted = isinstance(exc, KeyboardInterrupt)
                os.killpg(process.pid, signal.SIGKILL)
                code = process.wait(timeout=10)
        stdout = (output / (label + ".stdout")).read_bytes()
        stderr = (output / (label + ".stderr")).read_bytes()
        row = {
            "label": label, "argv": argv, "actual_exit": code, "reaped": True,
            "timed_out": timed_out, "interrupted": interrupted,
            "timeout_seconds": timeout, "elapsed_seconds": time.monotonic() - started,
            "stdout_sha256": sha(stdout), "stderr_sha256": sha(stderr),
            "stderr_bytes": len(stderr),
        }
        report["commands"].append(row)
        save(output / (label + ".command.json"), row)
        if code or timed_out or interrupted:
            report["failed_command"] = label
            # Completed JSON rows survive even if the next assertion/sanitizer fails.
            report["failed_command_stdout"] = stdout.decode("ascii", errors="backslashreplace")
            raise RuntimeError(label + " failed; logs retained, subsequent cases NOT_RUN")
        if stderr:
            raise RuntimeError(label + " emitted diagnostics; retained, not suppressed")
        return stdout

    def record(name, rows, plan):
        report["results"][name] = rows
        report["executed_cases"] += len(rows)
        completed_scenarios.update(row["scenario"] for row in plan)
        report["unique_scenarios"] = len(completed_scenarios)

    try:
        report["compiler_version"] = command("compiler-version", [compiler, "--version"], 30).decode().strip()
        if "clang" not in report["compiler_version"].lower():
            raise ValueError("This suite requires the installed clang sanitizer toolchain")
        flags = [
            compiler, "-std=c11", "-O1", "-g", "-Wall", "-Wextra", "-Werror",
            "-fsanitize=address,undefined", "-fno-omit-frame-pointer", "-DEXPECT_FIXED=1",
            "-I" + str(vendor), "-I" + str(fixture.parent),
        ]
        driver = [str(source), str(vendor / "bmi270.c")]
        report["compiler_source_paths"] = driver
        if "legacy" in selected:
            executable = output / "legacy-host"
            command("compile-legacy", flags + [str(legacy)] + driver + ["-o", str(executable)], 120)
            expected = json.loads((PACKAGE / "legacy-oracles.json").read_bytes())
            for mode, series, count in [("bounds", "legacy-bounds", 25),
                                        ("controls", "legacy-state", 36),
                                        ("early-errors", "legacy-initial-error", 12)]:
                data = command("legacy-" + mode, [str(executable), "--" + mode], 60)
                rows, summary = parse_cases(data, count)
                if mode == "bounds":
                    if (summary.get("summary") != "PASS_BOUNDED_SOFTWARE_ONLY" or
                            sha(data) != expected["bounds_stdout_sha256"]):
                        raise ValueError("Historical 25-case output changed")
                elif mode == "controls":
                    if summary.get("summary") != "COMPLETE_NEW_SOURCE_AUTHOR_HOST_ONLY":
                        raise ValueError("Legacy control summary changed")
                    for row, prior in paired(rows, expected["nonerror_controls"]):
                        compact = {k: v for k, v in row.items() if k != "trace"}
                        oracle = {k: v for k, v in prior.items() if k not in ("case_id", "trace_sha256")}
                        digest = sha(json.dumps(row["trace"], separators=(",", ":")).encode())
                        if compact != oracle or digest != prior["trace_sha256"]:
                            raise ValueError("Historical control values/full trace changed")
                else:
                    if summary.get("summary") != "COMPLETE_NEW_SOURCE_AUTHOR_HOST_ONLY":
                        raise ValueError("Legacy initial-error summary changed")
                    for row, prior in paired(rows, expected["early_error_cases"]):
                        if any(row.get(k) != v for k, v in prior.items() if k != "id"):
                            raise ValueError("Historical initial-error oracle changed")
                        if not row["error_preserved"] or row["budget_hits"]:
                            raise ValueError("Initial error not retained")
                plan = [row for row in selected["legacy"] if row["series"] == series]
                compact = [{**{k: v for k, v in row.items() if k not in ("trace", "spans")},
                            "id": planned["id"]} for row, planned in paired(rows, plan)]
                record("legacy-" + mode, compact, plan)
        for group, names, fixture_name in [
            ("crt", ["crt"], "crt_selected.c"),
            ("aux", ["aux-write", "aux-read"], "aux_selected.c"),
        ]:
            active = [name for name in names if name in selected]
            if not active:
                continue
            executable = output / (group + "-host")
            command("compile-" + group, flags + [str(PACKAGE / fixture_name)] + driver +
                    ["-o", str(executable)], 120)
            for name in active:
                plan = selected[name]
                fields = matrix["crt_fields" if group == "crt" else "aux_fields"]
                case_file = output / (name + ".cases")
                with case_file.open("x", encoding="ascii") as handle:
                    for row in plan:
                        handle.write(row["id"] + " " + " ".join(str(row["input"][f]) for f in fields) + "\n")
                data = command(name, [str(executable), str(case_file)], 60)
                rows, summary = parse_cases(data, len(plan))
                if summary.get("summary") != "COMPLETE_SELECTED_AUTHOR_HOST_ONLY":
                    raise ValueError("New suite lacks completion summary")
                if [r.get("id") for r in rows] != [r["id"] for r in plan]:
                    raise ValueError("Executed cases differ from the predeclared ordered matrix")
                if any(not r.get("passed") or r["callbacks_after_fault"] for r in rows):
                    raise ValueError("Failed case or post-error callback")
                record(name, rows, plan)
        for path, row in snapshots.items():
            checked(Path(path), row)
        report.update(status="COMPLETE_SELECTED_AUTHOR_HOST_ONLY", inputs_unchanged=True,
                      compiler_runtime_diagnostics=0, owned_jobs=0)
    except (OSError, ValueError, KeyError, RuntimeError, subprocess.SubprocessError) as exc:
        report.update(status="FAILED", error=type(exc).__name__ + ": " + str(exc))
    finally:
        report["finished_at"] = dt.datetime.now(dt.timezone.utc).isoformat()
        save(output / "report.json", report)
    print(json.dumps({k: report[k] for k in ("status", "executed_cases", "unique_scenarios")} |
                     {"error": report.get("error")}))
    return 0 if report["status"] == "COMPLETE_SELECTED_AUTHOR_HOST_ONLY" else 1


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-root", required=True, help="Existing dedicated output parent; never a source input")
    parser.add_argument("--output", required=True, help="Fresh strict descendant of --output-root")
    parser.add_argument("--bmi2", help="Exact selected source, e.g. the promoted public measurement/vendor/bosch/bmi2.c")
    parser.add_argument("--expected-sha256", help="Required with --bmi2; must match this selected candidate")
    parser.add_argument("--vendor-dir", help="Unchanged Bosch headers, bmi270.c and LICENSE")
    parser.add_argument("--cc", default="clang")
    parser.add_argument("--suite", action="append", choices=["legacy", "crt", "aux-write", "aux-read"])
    parser.add_argument("--series", action="append", help="Run a coherent predeclared slice of a new suite")
    try:
        return run(parser.parse_args())
    except (OSError, ValueError, KeyError, RuntimeError) as exc:
        print(json.dumps({"status": "FAILED_BEFORE_RUN", "error": str(exc)}), file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
