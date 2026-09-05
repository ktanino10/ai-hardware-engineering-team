import argparse
import json
from pathlib import Path
import platform
import shutil

import mujoco

from .model import ROOT, build, load_config
from .intake import write_proxy
from .gallery import suite
from .numerics import write_witnesses
from .runner import run
from .scenarios import scenarios
from .visualize import plot, read_run, render, replay, verify_current


def main():
    parser = argparse.ArgumentParser(description="WIP cube dynamics; no hardware/device access.")
    sub = parser.add_subparsers(dest="action", required=True)
    sub.add_parser("preflight")
    derive = sub.add_parser("derive-proxy")
    derive.add_argument("--output", type=Path, default=ROOT / "models/rev5-proxy.json")
    witnesses = sub.add_parser("witnesses")
    witnesses.add_argument("--output", type=Path, required=True)
    batch = sub.add_parser("suite", help="Both labeled model cases, seven scenarios each, plots/video/numerical witnesses.")
    batch.add_argument("--output", type=Path, required=True)
    batch.add_argument("--allow-proxy", action="store_true")
    runner = sub.add_parser("run")
    runner.add_argument("--config", type=Path, default=ROOT / "models/reference.json")
    runner.add_argument("--scenario", choices=scenarios(), default="three-wheel")
    runner.add_argument("--output", type=Path, required=True)
    runner.add_argument("--video", action="store_true")
    runner.add_argument("--allow-proxy", action="store_true", help="Acknowledge incomplete solid-CAD mass and assumed actuator/contact.")
    for action in ("plot", "render", "replay", "verify"):
        command = sub.add_parser(action)
        command.add_argument("directory", type=Path)
        if action == "replay":
            command.add_argument("--seconds", type=float)
        if action == "verify":
            command.add_argument("--historical", action="store_true", help="Check archived output hashes only, not current code/intake.")
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
    elif args.action == "derive-proxy":
        write_proxy(args.output)
    elif args.action == "witnesses":
        write_witnesses(args.output)
    elif args.action == "suite":
        if not args.allow_proxy:
            parser.error("The suite includes an incomplete WIP design proxy; use --allow-proxy to acknowledge its assumptions.")
        suite(args.output)
    elif args.action == "run":
        config = load_config(args.config)
        if config["classification"] == "WIP_DESIGN_PROXY" and not args.allow_proxy:
            parser.error("WIP proxy is incomplete; --allow-proxy acknowledges assumed actuator/contact, NOT actual-driver feasibility.")
        run(config, scenarios()[args.scenario], args.output, config_path=args.config)
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
        manifest, values = read_run(args.directory) if args.historical else verify_current(args.directory)
        print(f"Bound outputs match: {len(values['time'])} states, {manifest['rendering']['status']}")


if __name__ == "__main__":
    main()
