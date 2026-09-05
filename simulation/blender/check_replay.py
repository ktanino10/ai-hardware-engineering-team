"""Reopen a saved .blend in isolated Blender and compare every rendered pose."""

import argparse
import hashlib
import json
import itertools
import math
from pathlib import Path
import sys

import bpy
from mathutils import Quaternion, Vector
sys.path.insert(0, str(Path(__file__).resolve().parent))
from blender_contract import load_source, sha, validate_provenance


def require(condition, message):
    if not condition:
        raise ValueError(message)


def vector_error(actual, expected, label):
    error = (Vector(actual) - Vector(expected)).length
    require(math.isfinite(error) and error < 1e-6, f"{label} differs from the model: {error}")
    return error


def quaternion_error(actual, expected, label):
    error = min(sum((a-b)**2 for a, b in zip(actual, expected))**.5,
                sum((a+b)**2 for a, b in zip(actual, expected))**.5)
    require(math.isfinite(error) and error < 1e-6, f"{label} orientation mismatch: {error}")
    return error


def world_transform(obj, position, quaternion):
    expected = quaternion.to_matrix().to_4x4()
    expected.translation = position
    error = max(abs(obj.matrix_world[i][j] - expected[i][j]) for i in range(4) for j in range(4))
    require(math.isfinite(error) and error < 1e-6, f"{obj.name} full world transform mismatch: {error}")


def parent_inverse_identity(obj):
    error = max(abs(obj.matrix_parent_inverse[i][j] - (1 if i == j else 0))
                for i in range(4) for j in range(4))
    require(math.isfinite(error) and error < 1e-12, f"{obj.name} unsupported parent inverse")


def cylinder_bounds(obj, radius, depth, inner=None):
    parent_inverse_identity(obj)
    require(not obj.modifiers and not obj.constraints and obj.data.shape_keys is None,
            f"{obj.name} has an unsupported geometry modifier/constraint")
    require(obj.animation_data is None, f"{obj.name} must have a fixed local geometry transform")
    vertices = [v.co for v in obj.data.vertices]
    require(bool(vertices), f"{obj.name} has no mesh")
    radii = [math.hypot(v.x, v.y) for v in vertices]
    expected_min = radius if inner is None else inner
    require(abs(max(radii) - radius) < 1e-6 and abs(min(radii) - expected_min) < 1e-6,
            f"{obj.name} radial geometry mismatch")
    require(abs(min(v.z for v in vertices) + depth / 2) < 1e-6
            and abs(max(v.z for v in vertices) - depth / 2) < 1e-6,
            f"{obj.name} axial geometry mismatch")


def main():
    if not bpy.app.background:
        raise RuntimeError("Native verification must not replace the user's open Blender file.")
    parser = argparse.ArgumentParser()
    parser.add_argument("--run", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args(sys.argv[sys.argv.index("--") + 1:])
    source = load_source(args.run)
    rows, config = source["rows"], source["config"]
    provenance = json.loads(bpy.data.texts["PROVENANCE.json"].as_string())
    validate_provenance(source, provenance)
    sidecar = Path(bpy.data.filepath).parent / "provenance.json"
    require(json.loads(sidecar.read_text()) == provenance, "Native/sidecar provenance mismatch")
    scene = bpy.data.scenes["CubePhysicsReplay"]
    bpy.context.window.scene = scene
    require(scene.rigidbody_world is None, "This file must not impersonate Blender dynamics.")
    require(scene.frame_start == 1 and scene.frame_end == provenance["frames"]
            and scene.render.fps == provenance["fps"], "Native frame range/FPS mismatch")
    root = bpy.data.objects["CUBE_BODY_REPLAY"]
    require(root.parent is None, "Unexpected parent of the recorded body root")
    require(not root.constraints, "Unexpected body constraint")
    vector_error(root.scale, (1, 1, 1), "body scale")
    half = config["body"]["side_m"] / 2
    expected_edges = []
    for axis in range(3):
        for a, b in itertools.product((-half, half), repeat=2):
            location = [0, 0, 0]
            others = [i for i in range(3) if i != axis]
            location[others[0]], location[others[1]] = a, b
            expected_edges.append((Vector(location), Vector([int(i == axis) for i in range(3)])))
    edges = [obj for obj in root.children if obj.name.startswith("Visual_cube_edge")]
    require(len(edges) == 12, "Expected all twelve display edges")
    edge_transforms = []
    for obj in edges:
        index = min(range(len(expected_edges)), key=lambda i: (obj.location - expected_edges[i][0]).length)
        location, axis = expected_edges.pop(index)
        vector_error(obj.location, location, "body edge centre")
        vector_error(obj.scale, (1, 1, 1), "body edge scale")
        alignment = Vector((0, 0, 1)).rotation_difference(axis)
        quaternion_error(obj.rotation_quaternion, alignment, "body edge")
        cylinder_bounds(obj, .002, 2 * half)
        edge_transforms.append((obj, location, alignment))
    for i, item in enumerate(config["wheels"]):
        pivot = bpy.data.objects["WHEEL_" + item["name"].upper() + "_REPLAY"]
        mesh = bpy.data.objects["Wheel_" + item["name"]]
        require(pivot.parent == root and mesh.parent == pivot, "Rotor parenting mismatch")
        parent_inverse_identity(pivot)
        require(not pivot.constraints, "Unexpected rotor constraint")
        vector_error(pivot.location, item["center_m"], "rotor local centre")
        vector_error(pivot.scale, (1, 1, 1), "rotor scale")
        vector_error(mesh.location, (0, 0, 0), "rotor mesh centre")
        vector_error(mesh.scale, (1, 1, 1), "rotor mesh scale")
        alignment = Vector((0, 0, 1)).rotation_difference(Vector(item["axis"]))
        quaternion_error(mesh.rotation_quaternion, alignment, "fixed rotor mesh axis")
        cylinder_bounds(mesh, item["radius_m"], item["thickness_m"], item.get("inner_radius_m"))
        markers = [obj for obj in pivot.children if obj.name.startswith("Physical_angle_sample_marker")]
        require(len(markers) == 1, "Expected one source-angle marker per rotor")
        parent_inverse_identity(markers[0])
        require(markers[0].animation_data is None and not markers[0].constraints and not markers[0].modifiers,
                "Unexpected animated/modified rotation marker")
        marker = Vector(item["axis"]) * item["thickness_m"] / 2
        marker[(i+1) % 3] += ((item["radius_m"] + item["inner_radius_m"]) / 2
                              if "inner_radius_m" in item else item["radius_m"] * .8)
        vector_error(markers[0].location, marker, "rotation marker")
    errors = []
    for frame, entry in enumerate(source["mapping"], start=1):
        scene.frame_set(frame)
        scene.view_layers[0].update()
        row = rows[int(entry["sample_index"])]
        position = Vector([float(row[f"{axis}_m"]) for axis in "xyz"])
        position_error = vector_error(root.matrix_world.translation, position, "body world position")
        expected = Quaternion([float(row[key]) for key in ("qw", "qx", "qy", "qz")])
        actual = root.matrix_world.to_quaternion()
        body_error = quaternion_error(actual, expected, "body world")
        world_transform(root, position, expected)
        for obj, location, alignment in edge_transforms:
            world_transform(obj, position + expected @ location, expected @ alignment)
        wheel_errors = []
        centre_errors = []
        for item in config["wheels"]:
            wheel_q = Quaternion(Vector(item["axis"]), float(row[f"wheel_{item['name']}_rad"]))
            pivot = bpy.data.objects["WHEEL_" + item["name"].upper() + "_REPLAY"]
            mesh = bpy.data.objects["Wheel_" + item["name"]]
            centre = position + expected @ Vector(item["center_m"])
            centre_errors.append(vector_error(pivot.matrix_world.translation, centre, "rotor world centre"))
            vector_error(mesh.matrix_world.translation, centre, "rotor mesh world centre")
            wheel_errors.append(quaternion_error(pivot.matrix_world.to_quaternion(), expected @ wheel_q, "rotor world"))
            world_transform(pivot, centre, expected @ wheel_q)
            alignment = Vector((0, 0, 1)).rotation_difference(Vector(item["axis"]))
            quaternion_error(mesh.matrix_world.to_quaternion(), expected @ wheel_q @ alignment, "rotor mesh world")
            world_transform(mesh, centre, expected @ wheel_q @ alignment)
        errors.append({"frame": frame, "time_s": float(entry["time_s"]), "position_error_m": position_error,
                       "quaternion_l2_error": body_error, "wheel_quaternion_l2_errors": wheel_errors,
                       "wheel_world_centre_errors_m": centre_errors})
    record = {"status": "NATIVE_REOPEN_TRANSFORMS_GEOMETRY_AND_SOURCES_MATCH", "blender": bpy.app.version_string,
              "blend_sha256": hashlib.sha256(Path(bpy.data.filepath).read_bytes()).hexdigest(),
              "checker_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
              "contract_sha256": sha(Path(__file__).with_name("blender_contract.py")),
              "source_manifest_sha256": source["manifest_sha256"],
              "provenance_sha256": sha(sidecar),
              "tolerance": "1e-6 m / quaternion-component L2, Blender float32 render precision only; not physics qualification.",
              "frames": errors, "blender_dynamics": False}
    args.output.write_text(json.dumps(record, indent=2) + "\n")
    print(record["status"], len(errors))


if __name__ == "__main__":
    main()
