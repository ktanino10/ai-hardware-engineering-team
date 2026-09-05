"""Run with isolated Blender --background --factory-startup --python.

This is a renderer of MuJoCo records, NOT a second physics implementation.
Blender API: https://docs.blender.org/api/5.1/bpy.ops.render.html
"""

import argparse
import csv
import hashlib
import json
from pathlib import Path
import sys

import bpy
from mathutils import Quaternion, Vector
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from cube_sim.geometry import annulus_mesh


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def material(name, color, metallic=0):
    mat = bpy.data.materials.new(name)
    mat.diffuse_color = (*color, 1)
    mat.use_nodes = True
    shader = mat.node_tree.nodes.get("Principled BSDF")
    shader.inputs["Base Color"].default_value = (*color, 1)
    shader.inputs["Metallic"].default_value = metallic
    shader.inputs["Roughness"].default_value = .32
    return mat


def cylinder(name, radius, depth, parent, location, quat, mat):
    bpy.ops.mesh.primitive_cylinder_add(vertices=48, radius=radius, depth=depth)
    obj = bpy.context.object
    obj.name, obj.parent = name, parent
    obj.location = location
    obj.rotation_mode = "QUATERNION"
    obj.rotation_quaternion = quat
    obj.data.materials.append(mat)
    return obj


def empty(name, scene, parent=None, location=(0, 0, 0)):
    obj = bpy.data.objects.new(name, None)
    scene.collection.objects.link(obj)
    obj.parent, obj.location = parent, location
    obj.rotation_mode = "QUATERNION"
    return obj


def linearize(obj):
    # Reuse the repository's Blender 5 layered-action convention.
    for layer in obj.animation_data.action.layers:
        for strip in layer.strips:
            for bag in strip.channelbags:
                for curve in bag.fcurves:
                    for point in curve.keyframe_points:
                        point.interpolation = "LINEAR"


def main():
    if not bpy.app.background:
        raise RuntimeError("Use an isolated background Blender process; never reset the user's open scene.")
    parser = argparse.ArgumentParser()
    parser.add_argument("--run", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--animation", action="store_true")
    parser.add_argument("--engine", choices=("cycles", "workbench"), default="cycles")
    args = parser.parse_args(sys.argv[sys.argv.index("--") + 1:])
    source, output = args.run.resolve(), args.output.resolve()
    output.mkdir(parents=True, exist_ok=False)
    manifest = json.loads((source / "manifest.json").read_text())
    for name in ("input.json", "scenario.json", "trajectory.csv", "video-frames.csv"):
        if sha(source / name) != manifest["outputs"][name]:
            raise ValueError(f"Changed input: {name}")
    config = json.loads((source / "input.json").read_text())
    with (source / "trajectory.csv").open(newline="") as stream:
        rows = list(csv.DictReader(stream))
    with (source / "video-frames.csv").open(newline="") as stream:
        mapping = list(csv.DictReader(stream))

    bpy.ops.wm.read_factory_settings(use_empty=True)
    scene = bpy.context.scene
    scene.name = "CubePhysicsReplay"
    scene["scope"] = "WIP: MuJoCo trajectory replay, NOT Blender dynamics or Fusion assembly."
    scene["model_case_id"] = config["case_id"]
    scene["source_manifest_sha256"] = sha(source / "manifest.json")
    scene.unit_settings.system = "METRIC"
    scene.unit_settings.scale_length = 1
    scene.render.engine = "CYCLES" if args.engine == "cycles" else "BLENDER_WORKBENCH"
    scene.cycles.device, scene.cycles.samples = "CPU", 16
    scene.cycles.use_denoising = True
    scene.view_settings.exposure = -1
    scene.render.resolution_x, scene.render.resolution_y = 960, 520
    scene.render.resolution_percentage = 100
    scene.render.fps = manifest["rendering"]["fps"]
    if len(mapping) / scene.render.fps < 10:
        raise ValueError("Use a source trajectory/video map with at least ten seconds; no loops or padding.")
    scene.display.shading.color_type = "MATERIAL"
    scene.display.shading.show_shadows = True
    scene.display.shading.show_cavity = True
    scene.render.image_settings.file_format = "PNG"
    scene.world = bpy.data.worlds.new("Local studio")
    scene.world.use_nodes = True
    scene.world.node_tree.nodes["Background"].inputs[0].default_value = (.2, .27, .35, 1)
    scene.world.node_tree.nodes["Background"].inputs[1].default_value = .3

    root = empty("CUBE_BODY_REPLAY", scene)
    frame_mat = material("Visual frame only - not structural CAD", (.08, .3, .48), .35)
    colors = ((.8, .12, .06), (.08, .58, .27), (.09, .29, .83))
    marker_mat = material("Sampled rotation witness", (.96, .96, .88))
    half = config["body"]["side_m"] / 2
    for axis in range(3):
        others = [i for i in range(3) if i != axis]
        direction = Vector([int(i == axis) for i in range(3)])
        quat = Vector((0, 0, 1)).rotation_difference(direction)
        for a in (-half, half):
            for b in (-half, half):
                position = [0, 0, 0]
                position[others[0]], position[others[1]] = a, b
                cylinder("Visual_cube_edge", .002, 2 * half, root, position, quat, frame_mat)
    wheels = []
    for i, item in enumerate(config["wheels"]):
        pivot = empty("WHEEL_" + item["name"].upper() + "_REPLAY", scene, root, item["center_m"])
        wheels.append(pivot)
        axis = Vector(item["axis"])
        quat = Vector((0, 0, 1)).rotation_difference(axis)
        mat = material("Axis " + item["name"], colors[i], .45)
        if "inner_radius_m" in item:
            vertices, faces = annulus_mesh(item["radius_m"], item["inner_radius_m"], item["thickness_m"])
            mesh = bpy.data.meshes.new("Annulus_" + item["name"])
            mesh.from_pydata(vertices, [], faces)
            mesh.update()
            obj = bpy.data.objects.new("Wheel_" + item["name"], mesh)
            scene.collection.objects.link(obj)
            obj.parent, obj.rotation_mode, obj.rotation_quaternion = pivot, "QUATERNION", quat
            obj.data.materials.append(mat)
        else:
            cylinder("Wheel_" + item["name"], item["radius_m"], item["thickness_m"],
                     pivot, (0, 0, 0), quat, mat)
        point = Vector([0, 0, 0])
        point[(i + 1) % 3] = ((item["radius_m"] + item["inner_radius_m"]) / 2
                               if "inner_radius_m" in item else item["radius_m"] * .8)
        point += axis * item["thickness_m"] / 2
        bpy.ops.mesh.primitive_uv_sphere_add(segments=16, ring_count=8, radius=.0035)
        marker = bpy.context.object
        marker.name, marker.parent, marker.location = "Physical_angle_sample_marker", pivot, point
        marker.data.materials.append(marker_mat)

    bpy.ops.mesh.primitive_plane_add(size=6)
    floor = bpy.context.object
    floor.name = "Visual_floor_NOT_a_Blender_rigid_body"
    floor_mat = material("Floor grid", (.14, .19, .24))
    checker = floor_mat.node_tree.nodes.new("ShaderNodeTexChecker")
    checker.inputs["Color1"].default_value = (.16, .23, .28, 1)
    checker.inputs["Color2"].default_value = (.22, .3, .35, 1)
    checker.inputs["Scale"].default_value = 24
    floor_mat.node_tree.links.new(checker.outputs["Color"], floor_mat.node_tree.nodes["Principled BSDF"].inputs["Base Color"])
    floor.data.materials.append(floor_mat)
    for name, position, energy, size in (("Key", (1, -2, 3), 80, 3),
                                         ("Fill", (-2, 1, 2), 40, 2)):
        light = bpy.data.lights.new(name, "AREA")
        light.energy, light.shape, light.size = energy, "DISK", size
        obj = bpy.data.objects.new(name, light)
        scene.collection.objects.link(obj)
        obj.location = position
        obj.rotation_euler = (-obj.location).to_track_quat("-Z", "Y").to_euler()
    camera_data = bpy.data.cameras.new("Replay camera")
    cam = bpy.data.objects.new("Replay camera", camera_data)
    scene.collection.objects.link(cam)
    scene.camera = cam
    cam.rotation_mode, camera_data.lens = "QUATERNION", 48
    label_curve = bpy.data.curves.new("WIP_scope_label", "FONT")
    label_curve.body = f"WIP | {config['case_id']}\nMuJoCo replay; NOT hardware / Blender dynamics / Fusion"
    label_curve.size = .011
    label = bpy.data.objects.new("WIP_scope_label", label_curve)
    scene.collection.objects.link(label)
    label.parent, label.location = cam, (-.32, .14, -1)
    label.data.materials.append(marker_mat)
    for index, entry in enumerate(mapping, start=1):
        row = rows[int(entry["sample_index"])]
        root.location = [float(row[f"{axis}_m"]) for axis in "xyz"]
        root.rotation_quaternion = [float(row[key]) for key in ("qw", "qx", "qy", "qz")]
        root.keyframe_insert(data_path="location", frame=index)
        root.keyframe_insert(data_path="rotation_quaternion", frame=index)
        for wheel, item in zip(wheels, config["wheels"]):
            wheel.rotation_quaternion = Quaternion(Vector(item["axis"]), float(row[f"wheel_{item['name']}_rad"]))
            wheel.keyframe_insert(data_path="rotation_quaternion", frame=index)
        view_point = root.location.copy()
        if "scenario" in config and config["scenario"].get("startup"):
            view_point.z = float(rows[0]["z_m"])
        offset = Vector((.53, -.72, .43)) * (config["body"]["side_m"] / .24)
        cam.location = view_point + offset
        cam.rotation_quaternion = (view_point - cam.location).to_track_quat("-Z", "Y")
        cam.keyframe_insert(data_path="location", frame=index)
        cam.keyframe_insert(data_path="rotation_quaternion", frame=index)
    for obj in (root, *wheels, cam):
        linearize(obj)
    scene.frame_start, scene.frame_end = 1, len(mapping)
    scene.frame_set(1)
    provenance = {
        "status": "WIP_MUJOCO_STATE_REPLAY_NOT_BLENDER_PHYSICS",
        "blender": bpy.app.version_string, "engine": "Cycles CPU, 16 samples" if args.engine == "cycles" else "Blender Workbench",
        "source_manifest_sha256": sha(source / "manifest.json"),
        "trajectory_csv_sha256": sha(source / "trajectory.csv"),
        "source_code_revision": manifest["source_revision"],
        "source_code_dirty": manifest["uncommitted_model_code"],
        "source_code_sha256": manifest["code"],
        "input_classification": manifest["classification"],
        "model_case_id": config["case_id"], "side_m": config["body"]["side_m"],
        "total_modeled_mass_kg": config["body"]["mass_kg"] + sum(w["mass_kg"] for w in config["wheels"]),
        "renderer_script_sha256": sha(__file__), "frame_mapping": mapping,
        "geometry_script_sha256": sha(Path(__file__).resolve().parents[1] / "cube_sim/geometry.py"),
        "poster_sample_index": manifest["rendering"]["poster_sample_index"],
        "camera": "size-aware XY following, fixed initial Z for startup; body following otherwise",
        "frames": len(mapping), "fps": scene.render.fps,
        "scope": "Display-only cube edges/cylinders, not canonical CAD. Integer-frame poses copied from computed records. Between-frame interpolation is not physics evidence.",
    }
    bpy.data.texts.new("PROVENANCE.json").write(json.dumps(provenance, indent=2))
    (output / "provenance.json").write_text(json.dumps(provenance, indent=2) + "\n")
    (output / "frames").mkdir()
    scene.render.filepath = "//frames/frame_"
    bpy.ops.wm.save_as_mainfile(filepath=str(output / "replay.blend"), compress=True)
    if args.animation:
        bpy.ops.render.render(animation=True)
    else:
        scene.frame_set(len(mapping) // 2 + 1)
        scene.render.filepath = str(output / "preview-raw.png")
        bpy.ops.render.render(write_still=True)
    print("BLENDER_REPLAY_COMPLETE", json.dumps({key: value for key, value in provenance.items()
                                                if key != "frame_mapping"}))


if __name__ == "__main__":
    main()
