"""Isolated negative regressions for complete native replay acceptance."""

import argparse
import json
from pathlib import Path
import runpy
import shutil
import sys

import bpy


def main():
    if not bpy.app.background:
        raise RuntimeError("Never mutate the user's live Blender scene for a test.")
    parser = argparse.ArgumentParser()
    parser.add_argument("--blend", type=Path, required=True)
    parser.add_argument("--run", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args(sys.argv[sys.argv.index("--") + 1:])
    args.blend, args.run, args.output = args.blend.resolve(), args.run.resolve(), args.output.resolve()
    args.output.mkdir(parents=True, exist_ok=False)
    results = []
    for name in ("wheel-centre-10mm", "wheel-scale", "mesh-axis"):
        bpy.ops.wm.open_mainfile(filepath=str(args.blend.resolve()))
        if name == "wheel-centre-10mm":
            bpy.data.objects["WHEEL_X_REPLAY"].location.x += .01
        elif name == "wheel-scale":
            bpy.data.objects["WHEEL_X_REPLAY"].scale.x = 1.1
        else:
            bpy.data.objects["Wheel_x"].rotation_quaternion = (1, 0, 0, 0)
        directory = args.output / name
        directory.mkdir()
        path = directory / "replay.blend"
        bpy.ops.wm.save_as_mainfile(filepath=str(path.resolve()), compress=True)
        shutil.copyfile(args.blend.parent / "provenance.json", directory / "provenance.json")
        bpy.ops.wm.open_mainfile(filepath=str(path.resolve()))
        sys.argv = ["blender", "--", "--run", str(args.run.resolve()), "--output", str((directory / "must-not-exist.json").resolve())]
        try:
            runpy.run_path(str(Path(__file__).with_name("check_replay.py")), run_name="__main__")
        except ValueError as error:
            results.append({"mutation": name, "rejected": True, "reason": str(error)})
        else:
            raise AssertionError(f"Native checker accepted {name}")
        if (directory / "must-not-exist.json").exists():
            raise AssertionError("Rejected native file received a success receipt")
    (args.output / "results.json").write_text(json.dumps(results, indent=2) + "\n")
    print("ALL_NATIVE_MUTATIONS_REJECTED")


if __name__ == "__main__":
    main()
