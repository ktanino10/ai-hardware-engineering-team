"""Render/replay recorded states, never prescribe an apparently successful motion."""

import csv
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import time

import mujoco
import numpy as np
from PIL import Image, ImageDraw, ImageFont

from .model import ROOT
from .runner import finalize_manifest, sha256
from .braking import PHASES

FPS = 25


def read_run(directory):
    directory = Path(directory)
    manifest = json.loads((directory / "manifest.json").read_text(encoding="utf-8"))
    for name, expected in manifest["outputs"].items():
        if Path(name).name != name:
            raise ValueError("Run output references must be plain filenames.")
        if sha256(directory / name) != expected:
            raise ValueError(f"Changed/missing evidence: {name}; regenerate as a new run.")
    with np.load(directory / "trajectory.npz", allow_pickle=False) as archive:
        values = {key: archive[key].copy() for key in archive.files}
    return manifest, values


def verify_current(directory):
    manifest, values = read_run(directory)
    for name, expected in manifest["code"].items():
        path = (ROOT.parent / name).resolve()
        if not path.is_relative_to(ROOT / "cube_sim") or sha256(path) != expected:
            raise ValueError(f"Simulation code changed: {name}. Historical output is not current evidence.")
    snapshot = manifest["source_snapshot"]
    if snapshot is not None:
        path = (ROOT.parent / snapshot["path"]).resolve()
        if not path.is_relative_to(ROOT / "intake") or sha256(path) != snapshot["sha256"]:
            raise ValueError("Frozen intake changed; derive a new proxy and regenerate affected runs.")
    source = manifest["input_model"]
    if source["kind"] == "repository_file":
        path = (ROOT.parent / source["path"]).resolve()
        if not path.is_relative_to(ROOT / "models") or sha256(path) != source["sha256"]:
            raise ValueError("Model input changed; archived conclusion is not current evidence.")
    if sha256(ROOT / "requirements-lock.txt") != manifest["dependency_lock_sha256"]:
        raise ValueError("Dependency lock changed; archived run is not current numerical evidence.")
    for key, folder in (("mechanism_source", "intake"), ("base_model", "models")):
        item = manifest.get(key)
        if item:
            path = (ROOT.parent / item["path"]).resolve()
            if not path.is_relative_to(ROOT / folder) or sha256(path) != item["sha256"]:
                raise ValueError(f"{key} changed; derive new inputs and regenerate evidence.")
    return manifest, values


def source_label(manifest):
    code = manifest["source_revision"][:12] + ("+dirty" if manifest["uncommitted_model_code"] else "")
    snapshot = manifest["source_snapshot"]
    label = f"code {code} | " + (f"WIP intake {snapshot['upstream_revision'][:12]}" if snapshot else "synthetic input")
    mechanism = manifest.get("mechanism_source")
    return label + (f" | study {mechanism['revision'][:8]}" if mechanism else "")


def plot(directory):
    os.environ.setdefault("MPLCONFIGDIR", str(ROOT / ".mpl-cache"))
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    directory = Path(directory)
    manifest, values = verify_current(directory)
    times = values["time"]
    fig, axes = plt.subplots(4, 2, figsize=(13, 12), sharex=True, layout="constrained")
    colors = ("#d64735", "#209756", "#357bcc")
    for i, axis in enumerate("XYZ"):
        axes[0, 0].plot(times, np.rad2deg(values["attitude_error"][:, i]), label=axis, color=colors[i])
        axes[0, 1].plot(times, values["qvel"][:, i + 3], label=axis, color=colors[i])
        axes[1, 0].plot(times, values["qvel"][:, i + 6], label=axis, color=colors[i])
        axes[1, 1].plot(times, values["command"][:, i], "--", color=colors[i], alpha=.55)
        axes[1, 1].plot(times, values["applied"][:, i], color=colors[i], label=axis)
        axes[3, 0].plot(times, values["angular_momentum"][:, i], color=colors[i], label=axis)
    axes[2, 0].plot(times, values["qpos"][:, 2], label="body centre z")
    axes[2, 0].set_ylabel("height [m]")
    axes[2, 0].fill_between(times, 0, 1, where=values["contact"][:, 0] > 0, color="green",
                            alpha=.08, transform=axes[2, 0].get_xaxis_transform(), label="loaded contact")
    load_axis = axes[2, 0].twinx()
    load_axis.plot(times, values["contact"][:, 1], color="#995400", label="normal force")
    load_axis.set_ylabel("normal force [N]", color="#995400")
    load_axis.legend(fontsize=8, loc="upper right")
    energy_change = np.sum(values["energy"] - values["energy"][0], axis=1)
    axes[2, 1].plot(times, energy_change, label="delta (potential + kinetic)")
    for i, label in enumerate(("motor work", "passive work", "constraint work")):
        axes[2, 1].plot(times, values["work"][:, i], label=label)
    if np.any(values.get("brake_limit", 0)):
        axes[2, 1].plot(times, values["brake_work"], "--", label="brake work (constraint subset)")
    axes[3, 1].plot(times, energy_change - np.sum(values["work"], axis=1), label="energy-work residual")
    titles = ("Attitude error vector, current body frame [deg]", "Body angular rate, body frame [rad/s]",
              "Relative wheel speed [rad/s] (not rated RPM)", "Command dashed / applied solid [N m]",
              "Height / contact load (shading = loaded contact)", "Rigid energy change and work [J]",
              "Total angular momentum about COM, world [N m s]", "Numerical energy/work balance [J]")
    for axis, title in zip(axes.flat, titles):
        axis.set_title(title, fontsize=10)
        axis.grid(alpha=.25)
        axis.legend(fontsize=8, loc="best")
    for axis in axes[-1]:
        axis.set_xlabel("Recorded simulation time [s]")
    config = json.loads((directory / "input.json").read_text(encoding="utf-8"))
    scenario = json.loads((directory / "scenario.json").read_text(encoding="utf-8"))
    limit = np.asarray(config["actuation"]["speed_cutoff_rad_s"])
    for i, cutoff in enumerate(limit):
        axes[1, 0].axhline(cutoff, color=colors[i], ls=":", alpha=.5)
        axes[1, 0].axhline(-cutoff, color=colors[i], ls=":", alpha=.5)
    fig.suptitle(f"WIP / {manifest['classification']} / {config['case_id']}\n"
                 f"{source_label(manifest)} | MuJoCo {manifest['environment']['mujoco']}\n"
                 "Ideal actuator + uncalibrated rigid contact. NOT hardware approval or Fusion animation.", fontsize=12)
    fig.savefig(directory / "plots.png", dpi=120, metadata={"Software": "cube_sim"})
    plt.close(fig)
    finalize_manifest(directory, manifest)


def video_samples(values):
    times = values["time"]
    # Exclude the terminal endpoint: N frames represent [0, duration) at 25 fps.
    count = round(times[-1] * FPS)
    wanted = np.arange(count) / FPS
    indices = np.searchsorted(times + 1e-9, wanted)
    if np.any(indices >= len(times)) or not np.allclose(times[indices], wanted, atol=1e-8, rtol=0):
        raise ValueError("Video timestamps must exist exactly on the recorded trajectory grid.")
    return indices


def detail_samples(values, program):
    start = program["brake_command_s"] + program["engagement_delay_s"] - .04
    # 0.1 simulated seconds / 0.0004 s per frame / 25 fps = 10 s, explicitly 100x slow.
    wanted = start + np.arange(250) * .0004
    indices = np.searchsorted(values["time"] + 1e-9, wanted)
    if np.any(indices >= len(values["time"])) or not np.allclose(values["time"][indices], wanted, atol=1e-8, rtol=0):
        raise ValueError("The detailed brake movie requires exact recorded dense-grid timestamps.")
    return indices


def camera(data):
    cam = mujoco.MjvCamera()
    cam.type = mujoco.mjtCamera.mjCAMERA_FREE
    cam.lookat[:] = data.qpos[:3]
    cam.distance, cam.azimuth, cam.elevation = .85, 135, -24
    return cam


def restore(model, data, values, index):
    data.qpos[:] = values["qpos"][index]
    data.qvel[:] = values["qvel"][index]
    data.ctrl[:] = values["applied"][index]
    data.time = values["time"][index]
    if "brake_limit" in values:
        model.dof_frictionloss[6:] = values["brake_limit"][index]
    mujoco.mj_forward(model, data)


def render(directory, *, detail=False):
    directory = Path(directory)
    manifest, values = verify_current(directory)
    ffmpeg = shutil.which("ffmpeg")
    if ffmpeg is None:
        raise RuntimeError("ffmpeg is missing. Install it locally or use the native replay viewer; no video was made.")
    scenario = json.loads((directory / "scenario.json").read_text(encoding="utf-8"))
    if detail and not scenario.get("startup"):
        raise ValueError("A brake detail movie requires a declared startup program.")
    indices = detail_samples(values, scenario["startup"]) if detail else video_samples(values)
    if len(indices) / FPS < 10:
        raise ValueError("Published video must contain at least ten seconds. Integrate a longer run; do not pad or loop it.")
    model = mujoco.MjModel.from_xml_path(str(directory / "model.xml"))
    data = mujoco.MjData(model)
    config = json.loads((directory / "input.json").read_text())
    case_label = f"{config['case_id']} | {config['body']['side_m']*1000:g} mm | modeled total {sum(model.body_mass):.3f} kg"
    summary = json.loads((directory / "summary.json").read_text(encoding="utf-8"))
    font = ImageFont.load_default(size=18)
    small = ImageFont.load_default(size=15)
    stem = "brake-detail" if detail else "motion"
    output = directory / f"{stem}.mp4"
    command = [ffmpeg, "-v", "error", "-n", "-f", "rawvideo", "-pix_fmt", "rgb24",
               "-s", "960x720", "-r", str(FPS), "-i", "-", "-an", "-c:v", "libx264",
               "-crf", "22", "-pix_fmt", "yuv420p", "-movflags", "+faststart", str(output)]
    frame_map = []
    poster_frame = int(np.argmax(values["qpos"][indices, 2])) if scenario.get("startup") else len(indices) // 2
    with mujoco.Renderer(model, height=520, width=960) as renderer, \
            subprocess.Popen(command, stdin=subprocess.PIPE, stderr=subprocess.PIPE) as encoder:
        for frame_index, sample_index in enumerate(indices):
            restore(model, data, values, sample_index)
            view = camera(data)
            if scenario.get("startup"):
                view.distance = max(.4, config["body"]["side_m"] * 3.5)
                view.lookat[2] = values["qpos"][0, 2]
            renderer.update_scene(data, camera=view)
            image = Image.new("RGB", (960, 720), (18, 24, 34))
            image.paste(Image.fromarray(renderer.render()), (0, 100))
            draw = ImageDraw.Draw(image)
            draw.text((20, 10), f"WIP | {manifest['classification']} | {scenario['name']}", fill="#ffd479", font=font)
            draw.text((20, 36), ("100x SLOW: 0.1 simulated seconds shown in 10 seconds. " if detail else "")
                      + (f"{config['body']['side_m']*1000:g} mm / {sum(model.body_mass):.3f} kg model" if detail else case_label),
                      fill="white", font=small)
            draw.text((20, 58), f"MuJoCo {manifest['environment']['mujoco']} | {source_label(manifest)}"
                      , fill="#bfcedf", font=small)
            draw.text((20, 78), "NOT hardware feasibility/safety approval. NOT Fusion assembly animation.",
                      fill="#ffb1a1", font=small)
            angle = np.rad2deg(np.linalg.norm(values["attitude_error"][sample_index]))
            active = int(values["contact"][sample_index, 0])
            support = "airborne" if active == 0 else f"{active} loaded contact point(s)"
            phase = PHASES[int(values["phase"][sample_index])] if "phase" in values else "ordinary trial"
            draw.text((20, 625), f"t={data.time:.4f} s | {phase} | {support} | error={angle:.1f} deg"
                      f" | trial: {summary['outcome']}", fill="white", font=small)
            speeds = " / ".join(f"{v:+.1f}" for v in data.qvel[6:])
            draw.text((20, 648), f"X red / Y green / Z blue: relative wheel rad/s = {speeds}"
                      " (markers may alias)", fill="#bfcedf", font=small)
            limited = bool(np.any(values["saturated"][sample_index] | values["speed_cutoff"][sample_index]))
            exceeded = bool(np.any(values["speed_exceeded"][sample_index]))
            draw.text((20, 671), f"Limited={limited}; speed exceeded={exceeded} | slip={values['contact'][sample_index, 3]:.3f} m/s"
                      f" | xy=({data.qpos[0]:+.3f},{data.qpos[1]:+.3f}) m", fill="#ffd479" if limited or exceeded else "#bfcedf", font=small)
            draw.text((20, 693), ("100x SLOW REPLAY; clock shows simulation seconds. " if detail else "REAL TIME. ")
                      + "Computed states only; no hidden support or pose correction.",
                      fill="#bfcedf", font=small)
            if frame_index == poster_frame:
                image.save(directory / ("brake-detail-preview.png" if detail else "preview.png"))
            encoder.stdin.write(image.tobytes())
            frame_map.append((frame_index, int(sample_index), float(data.time),
                              hashlib.sha256(data.qpos.astype("<f8").tobytes()).hexdigest()))
        encoder.stdin.close()
        error = encoder.stderr.read().decode("utf-8")
        if encoder.wait() != 0:
            raise RuntimeError(f"ffmpeg failed, video not accepted: {error}")
    map_name = "brake-detail-frames.csv" if detail else "video-frames.csv"
    with (directory / map_name).open("w", newline="", encoding="utf-8") as stream:
        writer = csv.writer(stream)
        writer.writerow(["video_frame", "sample_index", "time_s", "qpos_float64_le_sha256"])
        writer.writerows(frame_map)
    subprocess.run([ffmpeg, "-v", "error", "-i", str(output), "-f", "null", "-"], check=True,
                   stdout=subprocess.DEVNULL)
    rendering = {"status": "OFFSCREEN_RENDERED_AND_DECODED", "fps": FPS,
                             "frames": len(indices), "duration_s": len(indices) / FPS,
                             "producer": "MuJoCo Renderer + Pillow labels + ffmpeg/libx264",
                             "camera": ("XY tracking with fixed initial height, size-aware distance" if scenario.get("startup")
                                        else "body-centre tracking, distance 0.85 m"),
                             "state_source": f"trajectory.npz; exact rows in {map_name}",
                             "playback_rate": .01 if detail else 1,
                             "poster_sample_index": int(indices[poster_frame]),
                             "ffmpeg": subprocess.run([ffmpeg, "-version"], check=True, capture_output=True,
                                                      text=True).stdout.splitlines()[0]}
    if detail:
        manifest["brake_detail_rendering"] = rendering
    else:
        manifest["rendering"] = rendering
    finalize_manifest(directory, manifest)


def plot_startup(directory):
    os.environ.setdefault("MPLCONFIGDIR", str(ROOT / ".mpl-cache"))
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    directory = Path(directory)
    manifest, values = verify_current(directory)
    scenario = json.loads((directory / "scenario.json").read_text())
    program = scenario["startup"]
    config = json.loads((directory / "input.json").read_text())
    time_values = values["time"]
    fig, axes = plt.subplots(3, 2, figsize=(13, 10), layout="constrained")
    for i, axis in enumerate("XYZ"):
        axes[0, 0].plot(time_values, values["qvel"][:, 6+i] * 60 / (2*np.pi), label=axis)
        axes[0, 1].plot(time_values, values["brake_torque"][:, i], label=axis)
        axes[1, 0].plot(time_values, values["ground_force"][:, i], label=axis)
        axes[1, 1].plot(time_values, values["angular_momentum"][:, i], label=f"H {axis}")
        axes[1, 1].plot(time_values, values["ground_angular_impulse"][:, i], "--", label=f"floor impulse {axis}")
    axes[2, 0].plot(time_values, values["qpos"][:, 2], label="body centre")
    axes[2, 0].plot(time_values, values["minimum_corner_height"], label="lowest cube corner")
    axes[2, 1].plot(time_values, -values["brake_work"], label="modeled brake dissipation")
    axes[2, 1].plot(time_values, values["energy_residual"], label="rigid energy/work residual")
    for ax, title in zip(axes.flat, ("Relative wheel speed [rpm; not a rating]", "Internal brake torque [N m]",
                                     "Computed floor force XYZ [N]; NOT imposed lift", "COM H / external angular impulse [N m s]",
                                     "Heights [m]; rotation vs actual clearance", "Modeled mechanical energy [J]; NOT heat qualification")):
        ax.set_title(title, fontsize=10)
        ax.set_xlabel("Simulation time [s]")
        ax.grid(alpha=.25)
        ax.legend(fontsize=8)
    axes[0, 1].set_xlim(program["dense_start_s"], program["dense_end_s"])
    axes[1, 0].set_xlim(program["brake_command_s"] - .05, program["brake_command_s"] + .6)
    fig.suptitle(f"WIP / {manifest['classification']} / {config['case_id']}\nSPIN FROM REST -> FINITE BRAKE / {source_label(manifest)}")
    fig.savefig(directory / "startup-plots.png", dpi=120, metadata={"Software": "cube_sim"})
    plt.close(fig)
    finalize_manifest(directory, manifest)


def replay(directory, seconds=None):
    import mujoco.viewer

    directory = Path(directory)
    manifest, values = read_run(directory)
    model = mujoco.MjModel.from_xml_path(str(directory / "model.xml"))
    data = mujoco.MjData(model)
    if seconds is not None and (not np.isfinite(seconds) or seconds <= 0):
        raise ValueError("Replay duration must be finite and positive.")
    with mujoco.viewer.launch_passive(model, data, show_left_ui=False, show_right_ui=False) as viewer:
        print("Native passive replay opened; recorded states only, not live control.", flush=True)
        start = time.monotonic()
        while viewer.is_running():
            elapsed = time.monotonic() - start
            if seconds is not None and elapsed >= seconds:
                break
            phase = elapsed % values["time"][-1]
            index = min(np.searchsorted(values["time"], phase), len(values["time"]) - 1)
            with viewer.lock():
                restore(model, data, values, index)
                viewer.cam.lookat[:] = data.qpos[:3]
                viewer.cam.distance, viewer.cam.azimuth, viewer.cam.elevation = .85, 135, -24
            viewer.set_texts((None, None, f"WIP {manifest['classification']}\n{source_label(manifest)}\n"
                             "Recorded replay; ideal torque / uncalibrated contact\n"
                             "NOT hardware approval; NOT Fusion assembly animation\n"
                             f"t = {data.time:.2f} s; wheel markers may alias", None))
            viewer.sync()
            time.sleep(.01)
