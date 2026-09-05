"""Reviewer-owned saved-file closure probes; background Blender only."""

import argparse
import csv
import hashlib
import json
from pathlib import Path
import runpy
import shutil
import sys

import bpy
from mathutils import Quaternion, Vector


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def check(checker, run, output):
    original = sys.argv
    try:
        sys.argv = ["blender", "--", "--run", str(run), "--output", str(output)]
        runpy.run_path(str(checker), run_name="__main__")
    finally:
        sys.argv = original


def main():
    if not bpy.app.background:
        raise RuntimeError("No live scene access is permitted")
    parser = argparse.ArgumentParser()
    for name in ("blend", "run", "checker", "output"):
        parser.add_argument("--"+name, type=Path, required=True)
    args = parser.parse_args(sys.argv[sys.argv.index("--")+1:])
    args.blend, args.run, args.checker, args.output = (
        p.resolve() for p in (args.blend, args.run, args.checker, args.output))
    args.output.mkdir(parents=True, exist_ok=True)
    original_hash = digest(args.blend)
    bpy.ops.wm.open_mainfile(filepath=str(args.blend))
    check(args.checker, args.run, args.output/"positive-check.json")
    config = json.loads((args.run/"input.json").read_text())
    with (args.run/"trajectory.csv").open(newline="") as stream:
        rows = list(csv.DictReader(stream))
    with (args.run/"video-frames.csv").open(newline="") as stream:
        mapping = list(csv.DictReader(stream))
    scene = bpy.data.scenes["CubePhysicsReplay"]
    bpy.context.window.scene = scene
    maximum = 0.
    for frame, entry in enumerate(mapping, start=1):
        scene.frame_set(frame)
        scene.view_layers[0].update()
        row = rows[int(entry["sample_index"])]
        position = Vector([float(row[f"{a}_m"]) for a in "xyz"])
        body_q = Quaternion([float(row[k]) for k in ("qw", "qx", "qy", "qz")])
        expected_objects = [("CUBE_BODY_REPLAY", position, body_q)]
        for wheel in config["wheels"]:
            centre = position+body_q@Vector(wheel["center_m"])
            q = body_q@Quaternion(Vector(wheel["axis"]), float(row[f"wheel_{wheel['name']}_rad"]))
            expected_objects.extend([
                ("WHEEL_"+wheel["name"].upper()+"_REPLAY", centre, q),
                ("Wheel_"+wheel["name"], centre, q@Vector((0, 0, 1)).rotation_difference(Vector(wheel["axis"]))),
            ])
        for name, centre, quaternion in expected_objects:
            expected = quaternion.to_matrix().to_4x4()
            expected.translation = centre
            actual = bpy.data.objects[name].matrix_world
            maximum = max(maximum, *(abs(actual[i][j]-expected[i][j]) for i in range(4) for j in range(4)))
    if maximum >= 1e-6:
        raise AssertionError(f"Independent full world-transform error: {maximum}")
    results = []
    for mutation in ("rotor-centre-10mm", "rotor-scale", "fixed-mesh-axis", "display-edge-parent-inverse"):
        bpy.ops.wm.open_mainfile(filepath=str(args.blend))
        edge = None
        if mutation == "rotor-centre-10mm":
            bpy.data.objects["WHEEL_X_REPLAY"].location.x += .01
        elif mutation == "rotor-scale":
            bpy.data.objects["WHEEL_X_REPLAY"].scale.y = 1.1
        elif mutation == "fixed-mesh-axis":
            bpy.data.objects["Wheel_x"].rotation_quaternion = (1, 0, 0, 0)
        else:
            edge = next(obj for obj in bpy.data.objects["CUBE_BODY_REPLAY"].children
                        if obj.name.startswith("Visual_cube_edge"))
            inverse = edge.matrix_parent_inverse.copy()
            inverse.translation.x += .01
            edge.matrix_parent_inverse = inverse
        directory = args.output/mutation
        directory.mkdir(exist_ok=True)
        native = directory/"replay.blend"
        bpy.ops.wm.save_as_mainfile(filepath=str(native), compress=True)
        shutil.copyfile(args.blend.parent/"provenance.json", directory/"provenance.json")
        bpy.ops.wm.open_mainfile(filepath=str(native))
        record = {"mutation": mutation, "saved_blend_sha256": digest(native)}
        if edge is not None:
            scene = bpy.data.scenes["CubePhysicsReplay"]
            scene.frame_set(1)
            scene.view_layers[0].update()
            root = bpy.data.objects["CUBE_BODY_REPLAY"]
            moved = next(obj for obj in root.children if obj.name.startswith("Visual_cube_edge")
                         and obj.matrix_parent_inverse.translation.length > .005)
            record["world_edge_displacement_m"] = (
                moved.matrix_world.translation-(root.matrix_world@moved.location)).length
            record["object"] = moved.name
        receipt = directory/"must-not-exist.json"
        if receipt.exists():
            receipt.unlink()
        try:
            check(args.checker, args.run, receipt)
            record.update(rejected=False, success_receipt_written=receipt.exists())
        except (ValueError, RuntimeError, AssertionError) as error:
            record.update(rejected=True, reason=str(error), success_receipt_written=receipt.exists())
        results.append(record)
    if digest(args.blend) != original_hash:
        raise AssertionError("Source native file changed")
    result = {"source_blend_sha256": original_hash, "blender": bpy.app.version_string,
              "positive_checker_status": json.loads((args.output/"positive-check.json").read_text())["status"],
              "independently_checked_frames": len(mapping), "max_world_matrix_error": maximum,
              "saved_mutations": results, "live_scene_accessed": False}
    (args.output/"native-results.json").write_text(json.dumps(result, indent=2)+"\n")
    print(json.dumps({k: v for k, v in result.items() if k != "source_blend_sha256"}, indent=2))


if __name__ == "__main__":
    main()
