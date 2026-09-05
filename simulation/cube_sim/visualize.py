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
    return manifest, values


def source_label(manifest):
    code = manifest["source_revision"][:12] + ("+dirty" if manifest["uncommitted_model_code"] else "")
    snapshot = manifest["source_snapshot"]
    return f"code {code} | " + (f"WIP intake {snapshot['upstream_revision'][:12]}" if snapshot else "synthetic input")


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
    axes[1, 0].axhline(max(limit), color="gray", ls=":", label="outward torque cutoff")
    axes[1, 0].axhline(-max(limit), color="gray", ls=":")
    fig.suptitle(f"WIP / {manifest['classification']} / {scenario['name']}\n"
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
    mujoco.mj_forward(model, data)


def render(directory):
    directory = Path(directory)
    manifest, values = verify_current(directory)
    ffmpeg = shutil.which("ffmpeg")
    if ffmpeg is None:
        raise RuntimeError("ffmpeg is missing. Install it locally or use the native replay viewer; no video was made.")
    indices = video_samples(values)
    model = mujoco.MjModel.from_xml_path(str(directory / "model.xml"))
    data = mujoco.MjData(model)
    scenario = json.loads((directory / "scenario.json").read_text(encoding="utf-8"))
    summary = json.loads((directory / "summary.json").read_text(encoding="utf-8"))
    font = ImageFont.load_default(size=18)
    small = ImageFont.load_default(size=15)
    output = directory / "motion.mp4"
    command = [ffmpeg, "-v", "error", "-n", "-f", "rawvideo", "-pix_fmt", "rgb24",
               "-s", "960x720", "-r", str(FPS), "-i", "-", "-an", "-c:v", "libx264",
               "-crf", "22", "-pix_fmt", "yuv420p", "-movflags", "+faststart", str(output)]
    frame_map = []
    with mujoco.Renderer(model, height=520, width=960) as renderer, \
            subprocess.Popen(command, stdin=subprocess.PIPE, stderr=subprocess.PIPE) as encoder:
        for frame_index, sample_index in enumerate(indices):
            restore(model, data, values, sample_index)
            renderer.update_scene(data, camera=camera(data))
            image = Image.new("RGB", (960, 720), (18, 24, 34))
            image.paste(Image.fromarray(renderer.render()), (0, 100))
            draw = ImageDraw.Draw(image)
            draw.text((20, 10), f"WIP | {manifest['classification']} | {scenario['name']}", fill="#ffd479", font=font)
            draw.text((20, 36), scenario["description"], fill="white", font=small)
            draw.text((20, 58), f"MuJoCo {manifest['environment']['mujoco']} | {source_label(manifest)}"
                      " | assumed torque/contact", fill="#bfcedf", font=small)
            draw.text((20, 78), "NOT hardware feasibility/safety approval. NOT Fusion assembly animation.",
                      fill="#ffb1a1", font=small)
            angle = np.rad2deg(np.linalg.norm(values["attitude_error"][sample_index]))
            active = int(values["contact"][sample_index, 0])
            support = "airborne" if active == 0 else f"{active} loaded contact point(s)"
            draw.text((20, 625), f"t={data.time:.2f} s | {support} | attitude error={angle:.1f} deg"
                      f" | trial: {summary['outcome']}", fill="white", font=small)
            speeds = " / ".join(f"{v:+.1f}" for v in data.qvel[6:])
            draw.text((20, 648), f"X red / Y green / Z blue: relative wheel rad/s = {speeds}"
                      " (markers may alias)", fill="#bfcedf", font=small)
            limited = bool(np.any(values["saturated"][sample_index] | values["speed_cutoff"][sample_index]))
            exceeded = bool(np.any(values["speed_exceeded"][sample_index]))
            draw.text((20, 671), f"Limited={limited}; speed exceeded={exceeded} | slip={values['contact'][sample_index, 3]:.3f} m/s"
                      f" | xy=({data.qpos[0]:+.3f},{data.qpos[1]:+.3f}) m", fill="#ffd479" if limited or exceeded else "#bfcedf", font=small)
            draw.text((20, 693), "Camera follows body; computed states only. No keyframes, time scaling, hidden support or pose correction.",
                      fill="#bfcedf", font=small)
            if frame_index == len(indices) // 2:
                image.save(directory / "preview.png")
            encoder.stdin.write(image.tobytes())
            frame_map.append((frame_index, int(sample_index), float(data.time),
                              hashlib.sha256(data.qpos.astype("<f8").tobytes()).hexdigest()))
        encoder.stdin.close()
        error = encoder.stderr.read().decode("utf-8")
        if encoder.wait() != 0:
            raise RuntimeError(f"ffmpeg failed, video not accepted: {error}")
    with (directory / "video-frames.csv").open("w", newline="", encoding="utf-8") as stream:
        writer = csv.writer(stream)
        writer.writerow(["video_frame", "sample_index", "time_s", "qpos_float64_le_sha256"])
        writer.writerows(frame_map)
    subprocess.run([ffmpeg, "-v", "error", "-i", str(output), "-f", "null", "-"], check=True,
                   stdout=subprocess.DEVNULL)
    manifest["rendering"] = {"status": "OFFSCREEN_RENDERED_AND_DECODED", "fps": FPS,
                             "frames": len(indices), "duration_s": len(indices) / FPS,
                             "producer": "MuJoCo Renderer + Pillow labels + ffmpeg/libx264",
                             "camera": "body-centre tracking, azimuth 135 deg, elevation -24 deg",
                             "state_source": "trajectory.npz; exact rows in video-frames.csv",
                             "ffmpeg": subprocess.run([ffmpeg, "-version"], check=True, capture_output=True,
                                                      text=True).stdout.splitlines()[0]}
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
