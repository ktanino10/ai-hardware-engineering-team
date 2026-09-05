"""Reopen a saved .blend in isolated Blender and compare every rendered pose."""

import argparse
import csv
import hashlib
import json
from pathlib import Path
import sys

import bpy
from mathutils import Quaternion, Vector


def main():
    if not bpy.app.background:
        raise RuntimeError("Native verification must not replace the user's open Blender file.")
    parser = argparse.ArgumentParser()
    parser.add_argument("--run", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args(sys.argv[sys.argv.index("--") + 1:])
    provenance = json.loads(bpy.data.texts["PROVENANCE.json"].as_string())
    with (args.run / "trajectory.csv").open(newline="") as stream:
        rows = list(csv.DictReader(stream))
    config = json.loads((args.run / "input.json").read_text())
    scene = bpy.data.scenes["CubePhysicsReplay"]
    bpy.context.window.scene = scene
    assert scene.rigidbody_world is None, "This file must not impersonate Blender dynamics."
    errors = []
    for frame, entry in enumerate(provenance["frame_mapping"], start=1):
        scene.frame_set(frame)
        scene.view_layers[0].update()
        row = rows[int(entry["sample_index"])]
        root = bpy.data.objects["CUBE_BODY_REPLAY"]
        position = Vector([float(row[f"{axis}_m"]) for axis in "xyz"])
        position_error = (root.matrix_world.translation - position).length
        expected = Quaternion([float(row[key]) for key in ("qw", "qx", "qy", "qz")])
        actual = root.matrix_world.to_quaternion()
        quaternion_error = min(sum((a-b)**2 for a, b in zip(actual, expected))**.5,
                               sum((a+b)**2 for a, b in zip(actual, expected))**.5)
        wheel_errors = []
        for item in config["wheels"]:
            expected = Quaternion(Vector(item["axis"]), float(row[f"wheel_{item['name']}_rad"]))
            actual = bpy.data.objects["WHEEL_" + item["name"].upper() + "_REPLAY"].rotation_quaternion
            wheel_errors.append(min(sum((a-b)**2 for a, b in zip(actual, expected))**.5,
                                    sum((a+b)**2 for a, b in zip(actual, expected))**.5))
        assert max(position_error, quaternion_error, *wheel_errors) < 1e-6, (frame, position_error, quaternion_error, wheel_errors)
        errors.append({"frame": frame, "time_s": float(entry["time_s"]), "position_error_m": position_error,
                       "quaternion_l2_error": quaternion_error, "wheel_quaternion_l2_errors": wheel_errors})
    record = {"status": "NATIVE_REOPEN_POSES_MATCH_COMPUTED_RECORDS", "blender": bpy.app.version_string,
              "blend_sha256": hashlib.sha256(Path(bpy.data.filepath).read_bytes()).hexdigest(),
              "checker_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
              "tolerance": "1e-6 m / quaternion-component L2, Blender float32 render precision only; not physics qualification.",
              "frames": errors, "blender_dynamics": False}
    args.output.write_text(json.dumps(record, indent=2) + "\n")
    print(record["status"], len(errors))


if __name__ == "__main__":
    main()
