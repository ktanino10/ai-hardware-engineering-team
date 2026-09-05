"""Deterministic forward integration; no pose writes after initialization."""

from collections import deque
import csv
import hashlib
import importlib.metadata
import json
from pathlib import Path
import platform
import subprocess

import mujoco
import numpy as np

from .model import ROOT, build
from .scenarios import command, error_vector, initialize, rotation

REPO = ROOT.parent
SAMPLE_PERIOD = 0.01


def sha256(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def write_json(path, value):
    Path(path).write_text(json.dumps(value, indent=2, sort_keys=True, allow_nan=False) + "\n",
                          encoding="utf-8")


def integer_steps(period, timestep):
    steps = round(period / timestep)
    if steps < 0 or not np.isclose(steps * timestep, period, rtol=0, atol=1e-10):
        raise ValueError(f"{period} s must be an integer multiple of timestep {timestep} s.")
    return steps


def contacts(model, data):
    normal = 0.0
    active = 0
    minimum = 0.0
    for i in range(data.ncon):
        contact = data.contact[i]
        minimum = min(minimum, float(contact.dist))
        if contact.efc_address >= 0:
            wrench = np.zeros(6)
            mujoco.mj_contactForce(model, data, i, wrench)
            normal += wrench[0]
            active += int(wrench[0] > 1e-8)
    return active, normal, minimum


def simulate(config, scenario):
    model, data, xml = build(config, contact=scenario.contact, gravity=scenario.gravity)
    initialize(model, data, config, scenario)
    dt = model.opt.timestep
    count = integer_steps(scenario.duration_s, dt)
    stride = integer_steps(SAMPLE_PERIOD, dt)
    if stride < 1 or count % stride:
        raise ValueError("Duration and timestep must support the 100 Hz evidence grid.")
    delay = integer_steps(scenario.command_delay_s, dt)
    queue = deque([np.zeros(3) for _ in range(delay)])
    torque_limit = np.asarray(config["actuation"]["torque_limit_nm"])
    speed_limit = np.asarray(config["actuation"]["speed_cutoff_rad_s"])
    total_mass = float(sum(model.body_mass))
    arrays = {k: [] for k in ("time", "qpos", "qvel", "command", "delayed", "applied",
                              "saturated", "speed_cutoff", "angular_momentum", "linear_momentum",
                              "energy", "work", "contact", "omega_world", "attitude_error")}
    work = np.zeros(3)

    def powers():
        return np.array([data.actuator_force @ data.qvel[6:],
                         data.qfrc_passive @ data.qvel, data.qfrc_constraint @ data.qvel])

    for step in range(count + 1):
        requested = command(data, scenario)
        queue.append(requested.copy())
        delayed = queue.popleft()
        applied = np.clip(delayed, -torque_limit, torque_limit)
        cutoff = (np.abs(data.qvel[6:]) >= speed_limit) & (applied * data.qvel[6:] > 0)
        applied[cutoff] = 0
        data.ctrl[:] = applied
        mujoco.mj_forward(model, data)
        if not np.all(np.isfinite(np.r_[data.qpos, data.qvel, data.qacc, data.energy])):
            raise FloatingPointError(f"Non-finite dynamics at step {step}.")
        if any(warning.number for warning in data.warning):
            raise RuntimeError(f"MuJoCo numerical/capacity warning at step {step}: {data.warning}")
        if abs(data.time - step * dt) > 1e-9:
            raise RuntimeError("Unexpected time/reset; refusing a success-shaped trajectory.")
        if step % stride == 0:
            values = {
                "time": float(data.time), "qpos": data.qpos.copy(), "qvel": data.qvel.copy(),
                "command": requested, "delayed": delayed, "applied": data.actuator_force.copy(),
                "saturated": np.abs(delayed) > torque_limit, "speed_cutoff": cutoff,
                "angular_momentum": data.sensor("angular_momentum_world").data.copy(),
                "linear_momentum": total_mass * data.sensor("com_velocity_world").data.copy(),
                "energy": data.energy.copy(), "work": work.copy(), "contact": contacts(model, data),
                "omega_world": rotation(data.qpos[3:7]) @ data.qvel[3:6],
                "attitude_error": error_vector(data.qpos[3:7], scenario.target),
            }
            for key, value in values.items():
                arrays[key].append(value)
        if step < count:
            before = powers()
            mujoco.mj_step(model, data)
            mujoco.mj_forward(model, data)
            work += .5 * dt * (before + powers())
    return {key: np.asarray(value) for key, value in arrays.items()}, xml


def write_csv(path, values):
    fields = {"time": ["time_s"], "qpos": ["x_m", "y_m", "z_m", "qw", "qx", "qy", "qz",
                                                  "wheel_x_rad", "wheel_y_rad", "wheel_z_rad"],
              "qvel": ["vx_world_m_s", "vy_world_m_s", "vz_world_m_s",
                       "wx_body_rad_s", "wy_body_rad_s", "wz_body_rad_s",
                       "wheel_x_relative_rad_s", "wheel_y_relative_rad_s", "wheel_z_relative_rad_s"],
              "contact": ["active_contacts", "normal_force_n", "minimum_contact_distance_m"],
              "energy": ["potential_j", "kinetic_j"], "work": ["motor_work_j", "passive_work_j", "constraint_work_j"]}
    for key, unit in (("command", "nm"), ("delayed", "nm"), ("applied", "nm"),
                      ("saturated", "bool"), ("speed_cutoff", "bool"),
                      ("angular_momentum", "world_nms"), ("linear_momentum", "world_kg_m_s"),
                      ("omega_world", "rad_s"), ("attitude_error", "body_rad")):
        fields[key] = [f"{key}_{axis}_{unit}" for axis in "xyz"]
    matrix = np.column_stack([values[key] for key in fields])
    with Path(path).open("w", newline="", encoding="utf-8") as stream:
        writer = csv.writer(stream)
        writer.writerow([name for names in fields.values() for name in names])
        writer.writerows(matrix)


def summary(values, scenario, config):
    angle = np.rad2deg(np.linalg.norm(values["attitude_error"], axis=1))
    return {
        "classification": config["classification"], "hardware_approval": False,
        "scenario": scenario.record(), "samples": len(values["time"]),
        "final_attitude_error_deg": float(angle[-1]), "max_attitude_error_deg": float(max(angle)),
        "trial_band_deg": 5,
        "outcome": ("DEPARTED_TARGET" if np.any(angle > 5) else "WITHIN_TRIAL_BAND")
        if scenario.controller == "pd" else "NO_CONTROL_GOAL",
        "max_wheel_relative_rad_s": np.max(np.abs(values["qvel"][:, 6:]), axis=0).tolist(),
        "torque_saturated_samples": np.sum(values["saturated"], axis=0).tolist(),
        "speed_cutoff_samples": np.sum(values["speed_cutoff"], axis=0).tolist(),
        "min_height_m": float(np.min(values["qpos"][:, 2])),
        "max_penetration_m": float(-np.min(values["contact"][:, 2])),
        "delta_angular_momentum_world_nms": (values["angular_momentum"][-1] - values["angular_momentum"][0]).tolist(),
        "rigid_energy_minus_logged_work_j": float(np.sum(values["energy"][-1] - values["energy"][0]) -
                                                  np.sum(values["work"][-1])),
        "interpretation": "5 deg is a reporting band, not qualification. Pre-positioned balance is not a transition.",
    }


def finalize_manifest(directory, manifest):
    manifest["outputs"] = {p.name: sha256(p) for p in sorted(directory.iterdir())
                           if p.is_file() and p.name != "manifest.json"}
    write_json(directory / "manifest.json", manifest)


def run(config, scenario, directory):
    directory = Path(directory)
    directory.mkdir(parents=True, exist_ok=False)
    values, xml = simulate(config, scenario)
    write_json(directory / "input.json", config)
    write_json(directory / "scenario.json", scenario.record())
    (directory / "model.xml").write_text(xml, encoding="utf-8")
    np.savez_compressed(directory / "trajectory.npz", **values)
    write_csv(directory / "trajectory.csv", values)
    write_json(directory / "summary.json", summary(values, scenario, config))
    revision = subprocess.run(["git", "rev-parse", "HEAD"], cwd=REPO, check=True,
                              capture_output=True, text=True).stdout.strip()
    dirty = subprocess.run(["git", "status", "--porcelain", "--", "simulation/cube_sim",
                            "simulation/models", "simulation/requirements.txt"], cwd=REPO,
                           check=True, capture_output=True, text=True).stdout.strip()
    manifest = {
        "schema_version": 1, "state": "WIP_SIMULATION_NOT_HARDWARE_OR_ASSEMBLY_APPROVAL",
        "classification": config["classification"], "source_revision": revision,
        "uncommitted_model_code": bool(dirty),
        "code": {str(p.relative_to(REPO)): sha256(p) for p in sorted((ROOT / "cube_sim").glob("*.py"))},
        "environment": {"python": platform.python_version(), "platform": platform.platform(),
                        **{pkg: importlib.metadata.version(pkg) for pkg in ("mujoco", "numpy", "matplotlib", "pillow")}},
        "sample_period_s": SAMPLE_PERIOD, "rendering": {"status": "NOT_RUN"},
        "source_snapshot": config["provenance"]["source_snapshot"],
        "omissions": config["omissions"],
    }
    finalize_manifest(directory, manifest)
    return values, manifest
