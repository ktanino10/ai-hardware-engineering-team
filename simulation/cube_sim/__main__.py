import argparse
import json
from pathlib import Path
import platform
import shutil

import mujoco

from .model import ROOT, build, load_config
from .runner import run
from .scenarios import scenarios
from .visualize import plot, read_run, render, replay


def main():
    parser = argparse.ArgumentParser(description="WIP cube dynamics; no hardware/device access.")
    sub = parser.add_subparsers(dest="action", required=True)
    sub.add_parser("preflight")
    runner = sub.add_parser("run")
    runner.add_argument("--config", type=Path, default=ROOT / "models/reference.json")
    runner.add_argument("--scenario", choices=scenarios(), default="three-wheel")
    runner.add_argument("--output", type=Path, required=True)
    runner.add_argument("--video", action="store_true")
    for action in ("plot", "render", "replay", "verify"):
        command = sub.add_parser(action)
        command.add_argument("directory", type=Path)
        if action == "replay":
            command.add_argument("--seconds", type=float)
    args = parser.parse_args()
    if args.action == "preflight":
        model, data, _ = build(load_config())
        with mujoco.Renderer(model, height=240, width=320) as renderer:
            renderer.update_scene(data)
            image = renderer.render()
        print(json.dumps({"mujoco": mujoco.__version__, "python": platform.python_version(),
                          "offscreen_rgb_shape": image.shape, "ffmpeg": shutil.which("ffmpeg"),
                          "native_viewer": "NOT_EXERCISED by preflight",
                          "macos_replay_command": ".venv/bin/mjpython -m cube_sim replay RUN_DIR"}, indent=2))
    elif args.action == "run":
        run(load_config(args.config), scenarios()[args.scenario], args.output)
        plot(args.output)
        if args.video:
            render(args.output)
        print(args.output.resolve())
    elif args.action == "plot":
        plot(args.directory)
    elif args.action == "render":
        render(args.directory)
    elif args.action == "replay":
        replay(args.directory, args.seconds)
    elif args.action == "verify":
        manifest, values = read_run(args.directory)
        print(f"Bound outputs match: {len(values['time'])} states, {manifest['rendering']['status']}")


if __name__ == "__main__":
    main()
