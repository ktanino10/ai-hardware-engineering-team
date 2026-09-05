#!/usr/bin/env python3
"""Tiny SIM-R2A-001 closure: real native good/bad files and receipt bindings only."""

import hashlib
import json
import os
from pathlib import Path
import runpy
import shutil
import subprocess
import sys

sys.dont_write_bytecode = True
REPO = Path(__file__).resolve().parents[3]
SIM = REPO/"simulation"
HERE = SIM/"reviews/r2b"
SCRATCH = SIM/"runs/reviewer-r2b"
HEAD = "7512042dcdf773935a0a528ee9d4617787317da3"
CURRENT = SIM/"evidence/blender-replay-v6/startup-mechanism-fixture"
PREVIOUS = SIM/"evidence/blender-replay-v5/startup-mechanism-fixture"
SOURCE = SIM/"evidence/startup-v4/startup-mechanism-fixture"
CHECKER = SIM/"blender/check_replay.py"


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def read(path):
    return json.loads(Path(path).read_text())


def write(path, value):
    Path(path).write_text(json.dumps(value, indent=2, sort_keys=True)+"\n")


def checker(output):
    previous_argv = sys.argv
    try:
        sys.argv = ["blender", "--", "--run", str(SOURCE), "--output", str(output)]
        runpy.run_path(str(CHECKER), run_name="__main__")
    finally:
        sys.argv = previous_argv


def native():
    import bpy
    if not bpy.app.background:
        raise RuntimeError("Only isolated background Blender is allowed")
    bpy.ops.wm.open_mainfile(filepath=str(CURRENT/"replay.blend"))
    checker(SCRATCH/"positive-check.json")
    positive = read(SCRATCH/"positive-check.json")
    if positive != read(CURRENT/"native-check.json"):
        raise AssertionError("Fresh native receipt differs from delivered receipt")
    root = bpy.data.objects["CUBE_BODY_REPLAY"]
    edge = next(obj for obj in root.children if obj.name.startswith("Visual_cube_edge"))
    edge_name = edge.name
    inverse = edge.matrix_parent_inverse.copy()
    inverse.translation.x += .01
    edge.matrix_parent_inverse = inverse
    bad = SCRATCH/"negative"
    bad.mkdir(exist_ok=True)
    bpy.ops.wm.save_as_mainfile(filepath=str(bad/"replay.blend"), compress=True)
    shutil.copyfile(CURRENT/"provenance.json", bad/"provenance.json")
    bpy.ops.wm.open_mainfile(filepath=str(bad/"replay.blend"))
    scene = bpy.data.scenes["CubePhysicsReplay"]
    scene.frame_set(1)
    scene.view_layers[0].update()
    root, edge = bpy.data.objects["CUBE_BODY_REPLAY"], bpy.data.objects[edge_name]
    displacement = (edge.matrix_world.translation-root.matrix_world@edge.location).length
    output = bad/"must-not-exist.json"
    if output.exists():
        output.unlink()
    try:
        checker(output)
        raise AssertionError("Existing saved-file parent-inverse counterexample was accepted")
    except ValueError as error:
        reason = str(error)
        if "unsupported parent inverse" not in reason:
            raise AssertionError("Unexpected rejection cause: "+reason)
    if output.exists():
        raise AssertionError("Rejected file received a success receipt")
    write(SCRATCH/"native-result.json", {
        "blender": bpy.app.version_string, "good_native_status": positive["status"],
        "positive_frames": len(positive["frames"]), "fresh_receipt_matches_delivered": True,
        "counterexample": {"object": edge_name, "world_displacement_m": displacement,
                           "saved_mutation_sha256": sha(bad/"replay.blend"),
                           "rejected": True, "reason": reason, "success_receipt_written": False},
        "live_scene_accessed": False,
    })


def main():
    (SCRATCH/"native-work").mkdir(parents=True, exist_ok=True)
    os.environ.update(PYTHONDONTWRITEBYTECODE="1", TMPDIR=str(SCRATCH/"native-work"))
    actual_head = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=REPO, text=True).strip()
    if actual_head != HEAD:
        raise AssertionError("Different revision; do not reuse this closure silently")
    protected = {str(p.relative_to(REPO)): sha(p) for name in ("r1", "r2", "r2a")
                 for p in (SIM/"reviews"/name).iterdir() if p.is_file()}
    unchanged = {}
    for name in ("replay.blend", "provenance.json", "render-receipt.json", "blender-motion.mp4", "preview.png"):
        if sha(CURRENT/name) != sha(PREVIOUS/name):
            raise AssertionError("Unexpected geometry/render change: "+name)
        unchanged[name] = sha(CURRENT/name)
    manifest = read(CURRENT/"manifest.json")
    for name, digest in manifest["files"].items():
        if sha(CURRENT/name) != digest:
            raise AssertionError("Output hash mismatch: "+name)
    sys.path.insert(0, str(SIM/"blender"))
    from blender_contract import load_source, validate_encoding
    source = load_source(SOURCE)
    _, receipt = validate_encoding(CURRENT, source)
    for name, digest in receipt["frame_sha256"].items():
        if sha(PREVIOUS/"frames"/name) != digest:
            raise AssertionError("Raw frame changed between v5/v6")
    try:
        validate_encoding(PREVIOUS, source)
        raise AssertionError("Previous checker receipt was accepted as current")
    except ValueError as error:
        stale_reason = str(error)
    command = ["/Applications/Blender.app/Contents/MacOS/Blender", "--background", "--factory-startup",
               "--threads", "2", "--python-exit-code", "1", "--python", str(Path(__file__).resolve()),
               "--", "--native"]
    proc = subprocess.run(command, capture_output=True, text=True)
    (SCRATCH/"native.log").write_text(proc.stdout+proc.stderr)
    proc.check_returncode()
    info = json.loads(subprocess.check_output([
        "ffprobe", "-v", "error", "-select_streams", "v:0", "-count_frames",
        "-show_entries", "stream=duration,nb_read_frames,r_frame_rate", "-of", "json",
        str(CURRENT/"blender-motion.mp4")
    ]))["streams"][0]
    if (float(info["duration"]), int(info["nb_read_frames"]), info["r_frame_rate"]) != (10., 250, "25/1"):
        raise AssertionError("Unexpected movie timing")
    for path, digest in protected.items():
        if sha(REPO/path) != digest:
            raise AssertionError("Prior review changed: "+path)
    for name, digest in manifest["files"].items():
        if sha(CURRENT/name) != digest:
            raise AssertionError("Delivered evidence changed during recheck")
    ci = json.loads(subprocess.check_output(["gh", "run", "view", "33979993468", "--json",
                                            "headSha,status,conclusion,url"], text=True))
    if ci["headSha"] != HEAD:
        raise AssertionError("Wrong CI revision")
    write(HERE/"witness.json", {
        "scope": "SIM-R2A-001_ONLY_NO_DYNAMICS_RERUN", "head": HEAD,
        "checker_fix_commit": subprocess.check_output(["git", "rev-parse", "1e87163"], cwd=REPO, text=True).strip(),
        "checker_sha256": sha(CHECKER), "witness_sha256": sha(__file__),
        "native": read(SCRATCH/"native-result.json"), "byte_identical_v5_v6": unchanged,
        "raw_frames_unchanged_and_bound": len(receipt["frame_sha256"]),
        "v6_manifest_sha256": sha(CURRENT/"manifest.json"),
        "v6_native_check_sha256": sha(CURRENT/"native-check.json"),
        "source_manifest_sha256": source["manifest_sha256"],
        "previous_receipt_rejected_as_current": stale_reason, "movie": info, "CI": ci,
        "prior_reviews_unchanged_sha256": protected, "evidence_unchanged": True,
        "finding_disposition": "SIM-R2A-001_RESOLVED",
    })
    print("SIM-R2A-001 closure witnesses passed; prior reviews/evidence unchanged.")


if __name__ == "__main__":
    native() if "--native" in sys.argv else main()
