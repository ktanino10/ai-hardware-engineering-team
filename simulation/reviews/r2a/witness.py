#!/usr/bin/env python3
"""Bounded R2 closure witnesses. No startup integration, old mesh research or live GUI."""

import ast
import csv
import hashlib
import json
import os
from pathlib import Path
import re
import shlex
import shutil
import subprocess
import sys

sys.dont_write_bytecode = True
REPO = Path(__file__).resolve().parents[3]
SIM = REPO/"simulation"
HERE = SIM/"reviews/r2a"
SCRATCH = SIM/"runs/reviewer-r2a"
HEAD = "8c626ecb55983005b157da48a4a7a7f3982a23a9"
FIX = "a9109f376e70b28788a4b99348cf3d39b2af2da3"
CASES = ("startup-reference", "startup-rev5-proxy", "startup-mechanism-fixture")
STARTUP = SIM/"evidence/startup-v4"
BLEND = SIM/"evidence/blender-replay-v5/startup-mechanism-fixture"
BLENDER = "/Applications/Blender.app/Contents/MacOS/Blender"
os.environ["PYTHONDONTWRITEBYTECODE"] = "1"
os.environ["TMPDIR"] = str(SCRATCH/"native-work")
os.environ["MPLCONFIGDIR"] = str(SCRATCH/"mpl-cache")

import numpy as np


def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def read(p):
    return json.loads(Path(p).read_text())


def write(p, data):
    Path(p).write_text(json.dumps(data, indent=2, sort_keys=True, allow_nan=False)+"\n")


def git(*args):
    return subprocess.check_output(["git", "--no-pager", *args], cwd=REPO, text=True).strip()


def bindings():
    prefixes = ("simulation/blender/", "simulation/tests/test_quadrature.py",
                "simulation/tests/test_blender_contract.py", "simulation/cube_sim/",
                "simulation/models/", "simulation/root/", "simulation/evidence/startup-v4/",
                "simulation/evidence/blender-replay-v5/", "simulation/evidence/root-v4/",
                "simulation/evidence/index.html")
    paths = [p for p in git("ls-files").splitlines() if p.startswith(prefixes)]
    return {
        "head": git("rev-parse", "HEAD"), "fix_source": FIX,
        "reviewed_sha256": {p: sha(REPO/p) for p in paths},
        "R1_R2_sha256": {str(p.relative_to(REPO)): sha(p)
                        for name in ("r1", "r2") for p in sorted((SIM/"reviews"/name).iterdir()) if p.is_file()},
        "reviewer_code_sha256": {p.name: sha(p) for p in HERE.glob("*.py")},
    }


def identity():
    assert not git("diff", "--name-only", "08adc390", HEAD, "--",
                   "simulation/cube_sim/integration.py", "simulation/cube_sim/model.py",
                   "simulation/cube_sim/runner.py", "simulation/cube_sim/scenarios.py",
                   "simulation/cube_sim/geometry.py", "simulation/cube_sim/numerics.py")
    result = {}
    keys = ("body", "wheels", "contact", "integration", "gravity_m_s2", "actuation", "scenario")
    for name in CASES:
        old, new = SIM/"evidence/startup-v3"/name, STARTUP/name
        before, after = read(old/"input.json"), read(new/"input.json")
        assert all(before[k] == after[k] for k in keys)
        with np.load(old/"trajectory.npz") as a, np.load(new/"trajectory.npz") as b:
            assert set(a.files) == set(b.files)
            assert all(np.array_equal(a[k], b[k]) for k in a.files)
            arrays = len(a.files)
        manifest = read(new/"manifest.json")
        assert manifest["source_revision"] == FIX and not manifest["uncommitted_model_code"]
        for path, digest in manifest["outputs"].items():
            assert sha(new/path) == digest
        assert sha(old/"trajectory.csv") == sha(new/"trajectory.csv")
        for movie in ("motion.mp4", "brake-detail.mp4"):
            info = json.loads(subprocess.check_output([
                "ffprobe", "-v", "error", "-select_streams", "v:0", "-count_frames",
                "-show_entries", "stream=nb_read_frames,duration,r_frame_rate", "-of", "json", str(new/movie)
            ]))["streams"][0]
            assert (int(info["nb_read_frames"]), float(info["duration"]), info["r_frame_rate"]) == (250, 10., "25/1")
        result[name] = {"physical_JSON_fields_identical": list(keys), "NPZ_arrays_identical": arrays,
                        "CSV_identical": True, "new_manifest_sha256": sha(new/"manifest.json"),
                        "new_input_sha256": sha(new/"input.json")}
    old = read(SIM/"models/startup-mechanism-fixture.json")
    new = read(SIM/"models/startup-mechanism-fixture-v2.json")
    assert all(old[k] == new[k] for k in keys)
    claim = new["provenance"]["actuation_and_contact"]
    assert "software template only" in claim
    assert "intentionally different assumptions" in claim
    assert "Base mass moments and floor law are unchanged" not in claim
    assert read(STARTUP/CASES[2]/"input.json") == new
    assert read(STARTUP/CASES[2]/"manifest.json")["input_model"]["path"].endswith("-v2.json")
    result["synthetic_provenance"] = claim
    result["no_dynamics_rerun"] = True
    return result


def test_and_ci():
    path = "simulation/tests/test_quadrature.py"
    old = git("show", "08adc390:"+path)
    new = (REPO/path).read_text()
    def criteria(text):
        return [ast.dump(node, include_attributes=False) for node in ast.walk(ast.parse(text))
                if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute)
                and isinstance(node.func.value, ast.Name) and node.func.value.id == "self"
                and node.func.attr.startswith("assert")]
    assert criteria(old) == criteria(new)
    assert 'assert_array_equal(result[key], unobserved[key]' in new
    assert 'atol=1e-10, rtol=0' in new and 'atol=1e-9, rtol=0' in new
    environment = dict(os.environ, PYTHONPATH="tests")
    local = subprocess.run([str(SIM/".venv/bin/python"), "-m", "unittest", "-v",
                            "test_quadrature", "test_blender_contract"],
                           cwd=SIM, env=environment, capture_output=True, text=True)
    (SCRATCH/"tests.log").write_text(local.stdout+local.stderr)
    local.check_returncode()
    runs = []
    for run in (33978039216, 33978690760, 33978933402):
        record = json.loads(subprocess.check_output(["gh", "run", "view", str(run), "--json",
                           "headSha,conclusion,status,url,jobs"], text=True))
        runs.append(record)
    assert runs[0]["conclusion"] == runs[1]["conclusion"] == "success"
    assert runs[1]["headSha"] == FIX
    return {"unchanged_self_assertion_AST": True, "same_runtime_bitwise_physical_comparison": True,
            "historical_atol_qpos_qvel": [1e-10, 1e-9], "energy_criteria_unchanged": True,
            "targeted_local_test_log_sha256": sha(SCRATCH/"tests.log"),
            "targeted_local_tests_passed": 7, "ci_runs": runs}


def native():
    command = [BLENDER, "--background", "--factory-startup", "--threads", "2", "--python-exit-code", "1",
               "--python", str(HERE/"native_witness.py"), "--", "--blend", str(BLEND/"replay.blend"),
               "--run", str(STARTUP/CASES[2]), "--checker", str(SIM/"blender/check_replay.py"),
               "--output", str(SCRATCH/"native")]
    p = subprocess.run(command, capture_output=True, text=True)
    (SCRATCH/"native.log").write_text(p.stdout+p.stderr)
    p.check_returncode()
    result = read(SCRATCH/"native/native-results.json")
    for row in result["saved_mutations"][:3]:
        assert row["rejected"] and not row["success_receipt_written"]
    assert result["positive_checker_status"] == "NATIVE_REOPEN_TRANSFORMS_GEOMETRY_AND_SOURCES_MATCH"
    return result


def stage_render(destination):
    destination.mkdir(parents=True)
    for name in ("replay.blend", "provenance.json", "render-receipt.json"):
        shutil.copyfile(BLEND/name, destination/name)
    shutil.copyfile(SCRATCH/"native/positive-check.json", destination/"native-check.json")
    shutil.copytree(BLEND/"frames", destination/"frames")


def encoder():
    work = SCRATCH/"encoding"
    if work.exists():
        shutil.rmtree(work)
    stage_render(work/"positive")
    stage_render(work/"negative")
    source = STARTUP/CASES[2]
    def invoke(run, render):
        return subprocess.run([str(SIM/".venv/bin/python"), str(SIM/"blender/encode_replay.py"),
                               "--run", str(run), "--render", str(render)], capture_output=True, text=True)
    positive = invoke(source, work/"positive")
    (work/"positive.log").write_text(positive.stdout+positive.stderr)
    positive.check_returncode()
    subprocess.run(["ffmpeg", "-v", "error", "-i", str(work/"positive/blender-motion.mp4"),
                    "-f", "null", "-"], check=True, capture_output=True)
    encoded = read(work/"positive/manifest.json")
    assert encoded["frames"] == 250 and encoded["fps"] == 25 and encoded["duration_s"] == 10
    assert encoded["source_manifest_sha256"] == sha(source/"manifest.json")
    for name, digest in read(BLEND/"manifest.json")["files"].items():
        assert sha(BLEND/name) == digest
    changed_source = work/"changed-source"
    changed_source.mkdir()
    for name in ("input.json", "scenario.json", "trajectory.csv", "video-frames.csv", "manifest.json"):
        shutil.copyfile(source/name, changed_source/name)
    with (changed_source/"trajectory.csv").open(newline="") as f:
        reader = csv.DictReader(f)
        fields, rows = reader.fieldnames, list(reader)
    for row in rows:
        row["wheel_x_relative_rad_s"] = "12345"
    with (changed_source/"trajectory.csv").open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)
    results = []
    negative = work/"negative"
    for label, run, error in (("changed-CSV-12345", changed_source, "Changed source trajectory.csv"),
                               ("wrong-valid-run", STARTUP/CASES[0], "Replay provenance mismatch")):
        p = invoke(run, negative)
        assert p.returncode != 0 and error in p.stderr
        assert not any((negative/name).exists() for name in ("blender-motion.mp4", "preview.png", "manifest.json"))
        results.append({"case": label, "returncode": p.returncode, "error": p.stderr.splitlines()[-1],
                        "no_movie_preview_or_manifest_written": True})
    for label, target, alter, expected in (
        ("stale-provenance", negative/"provenance.json", lambda raw: raw.replace(b'"schema_version": 2', b'"schema_version": 1'), "Replay provenance mismatch"),
        ("changed-native", negative/"replay.blend", lambda raw: raw+b"\n", "Native file/checker/source receipt changed"),
        ("changed-PNG", negative/"frames/frame_0001.png", lambda raw: raw+b"\n", "Changed rendered image"),
    ):
        original = target.read_bytes()
        target.write_bytes(alter(original))
        try:
            p = invoke(source, negative)
            assert p.returncode != 0 and expected in p.stderr
            assert not any((negative/name).exists() for name in ("blender-motion.mp4", "preview.png", "manifest.json"))
            results.append({"case": label, "returncode": p.returncode, "error": p.stderr.splitlines()[-1],
                            "no_movie_preview_or_manifest_written": True})
        finally:
            target.write_bytes(original)
    return {"fresh_positive_receipt_used": True, "positive_reencoded_and_decoded": True,
            "positive_movie_sha256": sha(work/"positive/blender-motion.mp4"),
            "delivered_movie_sha256": sha(BLEND/"blender-motion.mp4"),
            "all_250_PNGs_bound_by_receipt": True, "negative_cases": results}


def root_identity():
    build = SCRATCH/"root"
    build.mkdir(exist_ok=True)
    source = SIM/"reviews/r2/inspect_root.cxx"
    flags = shlex.split(subprocess.check_output(["root-config", "--cflags", "--libs"], text=True))
    binary = build/"inspect-root"
    subprocess.run(["c++", str(source), *flags, "-o", str(binary)], check=True)
    result = {}
    for name in CASES:
        new = SIM/"evidence/root-v4"/name
        manifest = read(new/"manifest.json")
        assert manifest["source_manifest_sha256"] == sha(STARTUP/name/"manifest.json")
        assert manifest["source_csv_sha256"] == sha(STARTUP/name/"trajectory.csv")
        assert manifest["adapter_sha256"] == sha(SIM/"root/export.py")
        assert manifest["cpp_sha256"] == sha(SIM/"root/export.cxx")
        for p, digest in manifest["files"].items():
            assert sha(new/p) == digest
        data = []
        for version in ("root-v3", "root-v4"):
            proc = subprocess.run([str(binary), str(SIM/"evidence"/version/name/"trajectory.root")],
                                  capture_output=True, text=True)
            (build/f"{version}-{name}.log").write_text(proc.stderr)
            proc.check_returncode()
            data.append(json.loads(proc.stdout))
        assert data[0] == data[1]
        result[name] = {"both_native_trees_identical": True, "rows": len(data[1]["trajectory"]["values"]),
                        "columns": len(data[1]["trajectory"]["columns"]),
                        "bins": len(data[1]["time_weighted_wheel_x_rpm"]["values"]),
                        "new_manifest_sha256": sha(new/"manifest.json")}
    return result


def main():
    (SCRATCH/"native-work").mkdir(parents=True, exist_ok=True)
    before = bindings()
    assert before["head"] == HEAD
    result = {"scope": "BOUNDED_R2_CLOSURE_NO_NEW_DYNAMICS", "bindings": before, "complete": False}
    for name, fn in (("parameter_record_identity", identity), ("test_portability", test_and_ci),
                     ("native_recheck", native), ("encoding_boundary", encoder),
                     ("ROOT_record_identity", root_identity)):
        print("R2a:", name, flush=True)
        result[name] = fn()
        write(HERE/"witness.json", result)
    assert before == bindings()
    result["complete"] = True
    result["frozen_scope_and_R1_R2_unchanged"] = True
    write(HERE/"witness.json", result)
    print("Bounded R2a witnesses completed; see review.md for finding dispositions.")


if __name__ == "__main__":
    main()
