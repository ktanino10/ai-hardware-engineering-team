"""Independent, background-only native pose/geometry/framing witness."""

import argparse
import csv
import hashlib
import itertools
import json
import math
from pathlib import Path
import runpy
import sys

import bpy
from bpy_extras.object_utils import world_to_camera_view
from mathutils import Matrix, Quaternion, Vector


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def distance(a, b):
    return max(abs(x-y) for x, y in zip(a, b))


def main():
    assert bpy.app.background, "Never use the user's live Blender scene"
    parser = argparse.ArgumentParser()
    parser.add_argument("--blend", type=Path, required=True)
    parser.add_argument("--run", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--author-checker", type=Path, required=True)
    parser.add_argument("--all-frames", action="store_true")
    args = parser.parse_args(sys.argv[sys.argv.index("--")+1:])
    args.output.mkdir(parents=True, exist_ok=True)
    (args.output/"frames").mkdir(exist_ok=True)
    before = sha(args.blend)
    bpy.ops.wm.open_mainfile(filepath=str(args.blend.resolve()))
    scene = bpy.data.scenes["CubePhysicsReplay"]
    bpy.context.window.scene = scene
    assert scene.rigidbody_world is None
    config = json.loads((args.run/"input.json").read_text())
    provenance = json.loads(bpy.data.texts["PROVENANCE.json"].as_string())
    assert provenance == json.loads((args.blend.parent/"provenance.json").read_text())
    assert provenance["source_manifest_sha256"] == sha(args.run/"manifest.json")
    assert provenance["trajectory_csv_sha256"] == sha(args.run/"trajectory.csv")
    with (args.run/"trajectory.csv").open(newline="") as f:
        rows = list(csv.DictReader(f))
    with (args.run/"video-frames.csv").open(newline="") as f:
        mapping = list(csv.DictReader(f))
    assert mapping == provenance["frame_mapping"]
    assert len(mapping) == 250 and scene.frame_start == 1 and scene.frame_end == 250
    assert scene.render.fps == 25
    root = bpy.data.objects["CUBE_BODY_REPLAY"]
    half = config["body"]["side_m"]/2
    corners = [Vector(p) for p in itertools.product((-half, half), repeat=3)]
    worst = {"body_position_m": 0., "body_rotation_matrix": 0., "wheel_center_m": 0.,
             "annulus_world_vertex_m": 0., "camera_position_m": 0.}
    framing = [1., 1., 1., 1.]
    transforms = (Quaternion((0, 1, 0), math.pi/2), Quaternion((1, 0, 0), -math.pi/2),
                  Quaternion((1, 0, 0), 0))
    observations = []
    selected = set(range(250)) if args.all_frames else {0, 87, 88, 89, 90, 100, 249}
    for index, entry in enumerate(mapping):
        row = rows[int(entry["sample_index"])]
        assert int(entry["video_frame"]) == index
        assert abs(float(entry["time_s"])-index/25) < 1e-8
        assert abs(float(row["time_s"])-index/25) < 1e-8
        scene.frame_set(index+1)
        scene.view_layers[0].update()
        position = Vector([float(row[f"{axis}_m"]) for axis in "xyz"])
        q = Quaternion([float(row[k]) for k in ("qw", "qx", "qy", "qz")])
        R = q.to_matrix()
        worst["body_position_m"] = max(worst["body_position_m"],
                                      (root.matrix_world.translation-position).length)
        worst["body_rotation_matrix"] = max(worst["body_rotation_matrix"],
            max(distance(a, b) for a, b in zip(root.matrix_world.to_3x3(), R)))
        for axis, wheel in enumerate(config["wheels"]):
            pivot = bpy.data.objects["WHEEL_"+wheel["name"].upper()+"_REPLAY"]
            mesh = bpy.data.objects["Wheel_"+wheel["name"]]
            assert pivot.parent == root and mesh.parent == pivot
            assert mesh.rigid_body is None
            assert max(abs(s-1) for s in (*mesh.scale, *pivot.scale, *root.scale)) < 1e-7
            center = position + R @ Vector(wheel["center_m"])
            worst["wheel_center_m"] = max(worst["wheel_center_m"],
                                         (pivot.matrix_world.translation-center).length)
            angle = float(row[f"wheel_{wheel['name']}_rad"])
            spin = Quaternion(Vector(wheel["axis"]), angle)
            assert len(mesh.data.vertices) == 192
            for k, vertex in enumerate(mesh.data.vertices):
                theta = 2*math.pi*(k//4)/48
                radius = wheel["radius_m"] if k % 4 < 2 else wheel["inner_radius_m"]
                z = (-1 if k % 2 == 0 else 1)*wheel["thickness_m"]/2
                local = Vector((radius*math.cos(theta), radius*math.sin(theta), z))
                expected = center + R @ (spin @ (transforms[axis] @ local))
                actual = mesh.matrix_world @ vertex.co
                worst["annulus_world_vertex_m"] = max(worst["annulus_world_vertex_m"],
                                                     (actual-expected).length)
        viewpoint = Vector((position.x, position.y, float(rows[0]["z_m"])))
        expected_camera = viewpoint + Vector((.53, -.72, .43))*(config["body"]["side_m"]/.24)*1.4
        worst["camera_position_m"] = max(worst["camera_position_m"],
                                        (scene.camera.matrix_world.translation-expected_camera).length)
        projections = [world_to_camera_view(scene, scene.camera, position+R@corner) for corner in corners]
        framing[0] = min(framing[0], *(p.x for p in projections))
        framing[1] = min(framing[1], *(1-p.x for p in projections))
        framing[2] = min(framing[2], *(p.y for p in projections))
        framing[3] = min(framing[3], *(1-p.y for p in projections))
        assert all(p.z > 0 for p in projections)
        if index in selected:
            file = args.output/"frames"/f"frame_{index+1:04}.png"
            scene.render.filepath = str(file.resolve())
            bpy.ops.render.render(write_still=True)
            observations.append({"video_frame": index, "time_s": float(row["time_s"]),
                                 "raw_frame": file.name, "sha256": sha(file)})
    assert max(worst.values()) < 1e-6, worst
    assert min(framing) > 0, framing
    result = {"status": "INDEPENDENT_NATIVE_REOPEN_AND_GEOMETRY_CHECK_COMPLETE",
              "blender": bpy.app.version_string, "blend_sha256": before, "frames_checked": 250,
              "maximum_errors": worst, "minimum_screen_margins_left_right_bottom_top": framing,
              "raw_rendered_frames": observations, "integer_frames_only": True,
              "native_blender_dynamics": False, "live_scene_accessed": False}

    # Negative test: a wrong rotor center must not pass a "matching poses" check.
    pivot = bpy.data.objects["WHEEL_X_REPLAY"]
    pivot.location.x += .01
    mutated = args.output/"wrong-wheel-center.blend"
    bpy.ops.wm.save_as_mainfile(filepath=str(mutated.resolve()), compress=True)
    old_argv = sys.argv
    try:
        sys.argv = ["blender", "--", "--run", str(args.run),
                    "--output", str(args.output/"author-check-wrong-center.json")]
        runpy.run_path(str(args.author_checker), run_name="__main__")
        result["negative_wrong_wheel_center"] = {
            "injected_center_shift_m": .01, "author_checker_accepted": True,
            "checker_output_sha256": sha(args.output/"author-check-wrong-center.json"),
        }
    except (AssertionError, ValueError, RuntimeError) as error:
        result["negative_wrong_wheel_center"] = {
            "injected_center_shift_m": .01, "author_checker_accepted": False,
            "error": str(error),
        }
    finally:
        sys.argv = old_argv
    assert sha(args.blend) == before
    (args.output/"native-witness.json").write_text(json.dumps(result, indent=2)+"\n")
    print("R2_NATIVE_WITNESS_COMPLETE")


if __name__ == "__main__":
    main()
