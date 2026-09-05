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

from .model import ROOT, build, inertia_matrix, load_config
from .braking import PHASES
from .integration import advance, quadrature_method
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
    slip_speed = 0.0
    omega = rotation(data.qpos[3:7]) @ data.qvel[3:6]
    for i in range(data.ncon):
        contact = data.contact[i]
        minimum = min(minimum, float(contact.dist))
        if contact.efc_address >= 0:
            wrench = np.zeros(6)
            mujoco.mj_contactForce(model, data, i, wrench)
            normal += wrench[0]
            active += int(wrench[0] > 1e-8)
            if wrench[0] > 1e-8:
                velocity = data.qvel[:3] + np.cross(omega, contact.pos - data.qpos[:3])
                slip_speed = max(slip_speed, float(np.linalg.norm(velocity[:2])))
    return active, normal, minimum, slip_speed


def simulate(config, scenario):
    if mujoco.get_mjcb_control() is not None:
        raise RuntimeError("Simulation owns its control loop; an existing native control callback would alter it.")
    model, data, xml = build(config, contact=scenario.contact, gravity=scenario.gravity)
    initialize(model, data, config, scenario)
    probe = mujoco.MjData(model)
    initial_energy = float(data.energy.sum())
    peak_energy_residual = 0.0
    dt = model.opt.timestep
    count = integer_steps(scenario.duration_s, dt)
    stride = integer_steps(SAMPLE_PERIOD, dt)
    if stride < 1 or count % stride:
        raise ValueError("Duration and timestep must support the 100 Hz evidence grid.")
    delay = integer_steps(scenario.command_delay_s, dt)
    queue = deque([np.zeros(3) for _ in range(delay)])
    torque_limit = np.asarray(config["actuation"]["torque_limit_nm"])
    speed_limit = np.asarray(config["actuation"]["speed_cutoff_rad_s"])
    brake = config["actuation"].get("independent_brake")
    program = scenario.startup
    if program and (brake is None or not np.any(np.asarray(brake["capacity_nm"]) > 0)):
        raise ValueError("Startup requires declared independent finite hinge brakes.")
    dense_stride = integer_steps(program.dense_period_s, dt) if program else 0
    if program and (dense_stride < 1 or dt > program.ramp_s / 10 + 1e-12):
        raise ValueError("Resolve the brake ramp with at least ten steps and the declared dense output grid.")
    if program and np.any(np.abs(program.target_rad_s) > speed_limit + 1e-12):
        raise ValueError("Startup target exceeds this case's explicit simulation cutoff.")
    total_mass = float(sum(model.body_mass))
    cube_id = model.body("cube").id
    initial_momentum = data.sensor("angular_momentum_world").data.copy()
    axial_inertia = np.array([inertia_matrix(w["inertia_kg_m2"])[i, i] for i, w in enumerate(config["wheels"])])
    arrays = {k: [] for k in ("time", "qpos", "qvel", "command", "delayed", "applied",
                              "saturated", "speed_cutoff", "speed_exceeded", "angular_momentum", "linear_momentum",
                              "energy", "work", "energy_residual", "peak_energy_residual",
                              "contact", "omega_world", "wheel_absolute_axial", "attitude_error",
                              "brake_limit", "brake_torque", "brake_work", "phase",
                              "ground_angular_impulse", "momentum_residual", "wheel_relative_axial_momentum",
                              "peak_positive_brake_power", "ground_force", "minimum_corner_height", "geometric_contacts")}
    integrals = np.zeros(7)
    peak_positive_brake_power = 0.0

    def powers(state):
        nonlocal peak_positive_brake_power
        brake_power = float(state.qfrc_constraint[6:] @ state.qvel[6:]) if brake else 0.0
        peak_positive_brake_power = max(peak_positive_brake_power, brake_power)
        # Only the floor contributes to the free-root constraint wrench.
        # Hinge-brake generalized forces have zero free-root entries.
        ground_moment = (rotation(state.qpos[3:7]) @ state.qfrc_constraint[3:6]
                         - np.cross(state.subtree_com[cube_id] - state.qpos[:3], state.qfrc_constraint[:3]))
        return np.r_[state.actuator_force @ state.qvel[6:], state.qfrc_passive @ state.qvel,
                     state.qfrc_constraint @ state.qvel, brake_power, ground_moment]

    for step in range(count + 1):
        timestamp = step * dt
        brake_limit = (np.asarray(brake["capacity_nm"]) * program.brake_fraction(timestamp)
                       if program else np.zeros(3))
        model.dof_frictionloss[6:] = brake_limit
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
        dense = program and program.dense_start_s - 1e-12 <= timestamp <= program.dense_end_s + 1e-12
        if step % stride == 0 or dense and step % dense_stride == 0:
            values = {
                "time": float(data.time), "qpos": data.qpos.copy(), "qvel": data.qvel.copy(),
                "command": requested, "delayed": delayed, "applied": data.actuator_force.copy(),
                "saturated": np.abs(delayed) > torque_limit, "speed_cutoff": cutoff,
                "speed_exceeded": np.abs(data.qvel[6:]) > speed_limit,
                "angular_momentum": data.sensor("angular_momentum_world").data.copy(),
                "linear_momentum": total_mass * data.sensor("com_velocity_world").data.copy(),
                "energy": data.energy.copy(), "work": integrals[:3].copy(), "contact": contacts(model, data),
                "energy_residual": float(data.energy.sum() - initial_energy - integrals[:3].sum()),
                "peak_energy_residual": peak_energy_residual,
                "omega_world": rotation(data.qpos[3:7]) @ data.qvel[3:6],
                "wheel_absolute_axial": data.qvel[6:].copy() + data.qvel[3:6],
                "attitude_error": error_vector(data.qpos[3:7], scenario.target),
                "brake_limit": brake_limit, "brake_torque": data.qfrc_constraint[6:].copy(),
                "brake_work": float(integrals[3]),
                "phase": program.phase(timestamp, data.qvel[6:]) if program else 0,
                "ground_angular_impulse": integrals[4:].copy(),
                "momentum_residual": data.sensor("angular_momentum_world").data - initial_momentum - integrals[4:],
                "wheel_relative_axial_momentum": axial_inertia * data.qvel[6:],
                "peak_positive_brake_power": peak_positive_brake_power,
                "ground_force": data.qfrc_constraint[:3].copy(),
                "minimum_corner_height": float(data.qpos[2] - config["body"]["side_m"] / 2
                                               * np.abs(rotation(data.qpos[3:7])[2]).sum()),
                "geometric_contacts": int(data.ncon),
            }
            for key, value in values.items():
                arrays[key].append(value)
        if step < count:
            integrals += advance(model, data, probe, powers)
            peak_energy_residual = max(peak_energy_residual,
                                       abs(float(data.energy.sum() - initial_energy - integrals[:3].sum())))
    return {key: np.asarray(value) for key, value in arrays.items()}, xml


def write_csv(path, values):
    fields = {"time": ["time_s"], "qpos": ["x_m", "y_m", "z_m", "qw", "qx", "qy", "qz",
                                                  "wheel_x_rad", "wheel_y_rad", "wheel_z_rad"],
              "qvel": ["vx_world_m_s", "vy_world_m_s", "vz_world_m_s",
                       "wx_body_rad_s", "wy_body_rad_s", "wz_body_rad_s",
                       "wheel_x_relative_rad_s", "wheel_y_relative_rad_s", "wheel_z_relative_rad_s"],
              "contact": ["active_contacts", "normal_force_n", "minimum_contact_distance_m", "max_loaded_point_slip_m_s"],
              "energy_residual": ["energy_work_residual_j"],
              "peak_energy_residual": ["max_abs_energy_work_residual_all_steps_j"],
              "brake_work": ["brake_work_j_subset_of_constraint_work"],
              "peak_positive_brake_power": ["max_positive_brake_power_stage_w"],
              "phase": ["phase_code"],
              "minimum_corner_height": ["minimum_cube_corner_height_m"],
              "geometric_contacts": ["geometric_contact_count"],
              "energy": ["potential_j", "kinetic_j"], "work": ["motor_work_j", "passive_work_j", "constraint_work_j"]}
    for key, unit in (("command", "nm"), ("delayed", "nm"), ("applied", "nm"),
                      ("saturated", "bool"), ("speed_cutoff", "bool"), ("speed_exceeded", "bool"),
                      ("angular_momentum", "world_nms"), ("linear_momentum", "world_kg_m_s"),
                      ("omega_world", "rad_s"), ("wheel_absolute_axial", "rad_s"), ("attitude_error", "body_rad")):
        fields[key] = [f"{key}_{axis}_{unit}" for axis in "xyz"]
    for key, unit in (("brake_limit", "nm"), ("brake_torque", "nm"),
                      ("ground_angular_impulse", "world_nms"), ("momentum_residual", "world_nms"),
                      ("ground_force", "world_n"),
                      ("wheel_relative_axial_momentum", "body_axis_nms")):
        fields[key] = [f"{key}_{axis}_{unit}" for axis in "xyz"]
    matrix = np.column_stack([values[key] for key in fields])
    with Path(path).open("w", newline="", encoding="utf-8") as stream:
        writer = csv.writer(stream)
        writer.writerow([name for names in fields.values() for name in names])
        writer.writerows(matrix)


def summary(values, scenario, config):
    angle = np.rad2deg(np.linalg.norm(values["attitude_error"], axis=1))
    outcome = "NO_CONTROL_GOAL"
    if scenario.controller == "pd":
        if scenario.initial_quat is not None:
            outcome = "TARGET_ATTITUDE_REACHED_ONLY" if angle[-1] <= 5 else "TARGET_NOT_REACHED"
        else:
            outcome = "DEPARTED_TARGET" if np.any(angle > 5) else "WITHIN_TRIAL_BAND"
    if scenario.startup:
        outcome = "TARGET_ATTITUDE_VISITED_NO_CAPTURE" if np.any(angle <= 5) else "TARGET_NOT_REACHED"
    report = {
        "classification": config["classification"], "hardware_approval": False,
        "scenario": scenario.record(), "samples": len(values["time"]),
        "final_attitude_error_deg": float(angle[-1]), "max_attitude_error_deg": float(max(angle)),
        "trial_band_deg": 5,
        "outcome": outcome,
        "max_wheel_relative_rad_s": np.max(np.abs(values["qvel"][:, 6:]), axis=0).tolist(),
        "torque_saturated_samples": np.sum(values["saturated"], axis=0).tolist(),
        "speed_cutoff_samples": np.sum(values["speed_cutoff"], axis=0).tolist(),
        "speed_exceeded_samples": np.sum(values["speed_exceeded"], axis=0).tolist(),
        "min_height_m": float(np.min(values["qpos"][:, 2])),
        "max_penetration_m": float(max(0, -np.min(values["contact"][:, 2]))),
        "max_loaded_point_slip_m_s": float(np.max(values["contact"][:, 3])),
        "max_angular_momentum_balance_residual_nms": float(np.max(np.linalg.norm(values["momentum_residual"], axis=1))),
        "delta_angular_momentum_world_nms": (values["angular_momentum"][-1] - values["angular_momentum"][0]).tolist(),
        "rigid_energy_minus_logged_work_j": float(np.sum(values["energy"][-1] - values["energy"][0]) -
                                                  np.sum(values["work"][-1])),
        "energy_accounting": {
            "method": quadrature_method(config["integration"]["integrator"]),
            "max_abs_residual_all_steps_j": float(values["peak_energy_residual"][-1]),
            "max_abs_residual_recorded_grid_j": float(np.max(np.abs(values["energy_residual"]))),
            "final_residual_j": float(values["energy_residual"][-1]),
            "contact_energy_status": ("UNCALIBRATED_CONTACT_NUMERICAL_RESIDUAL_REPORTED"
                                      if scenario.contact else "FREE_SPACE_NUMERICAL_DIAGNOSTIC"),
            "physical_energy_heat_impact_qualified": False,
            "limits": "Stage-consistent quadrature does not remove integrator/solver error or qualify real contact, heat or impact."
        },
        "interpretation": "Metrics are sampled at 100 Hz, not guaranteed continuous maxima. 5 deg is a reporting band, not qualification. Pre-positioned balance is not a transition; a geometric target is not necessarily the COM-balanced pose of an asymmetric proxy.",
    }
    if scenario.startup:
        program = scenario.startup
        before = int(np.searchsorted(values["time"], program.brake_on_s + 1e-9, side="right") - 1)
        active = np.asarray(program.target_rad_s) != 0
        stopped = np.flatnonzero((values["time"] >= program.brake_on_s)
                                 & np.all(np.abs(values["qvel"][:, 6:][:, active]) < program.stop_relative_rad_s, axis=1))
        initial_quat = values["qpos"][0, 3:7]
        maximum_rotation = max(np.linalg.norm(error_vector(q, initial_quat)) for q in values["qpos"][:, 3:7])
        candidates = np.flatnonzero((values["geometric_contacts"] == 0)
                                     & (values["contact"][:, 1] <= 1e-8)
                                     & (values["minimum_corner_height"] > .0001))
        intervals = []
        if len(candidates):
            for group in np.split(candidates, np.flatnonzero(np.diff(candidates) > 1) + 1):
                start, end = float(values["time"][group[0]]), float(values["time"][group[-1]])
                intervals.append({"first_observed_s": start, "last_observed_s": end,
                                  "observed_span_s": end - start, "consecutive_samples": len(group)})
        report["startup"] = {
            "initial_condition": "All bodies and wheels start at rest; no pre-spun state or velocity reset.",
            "target_only_rpm_xyz": (np.asarray(program.target_rad_s) * 60 / (2 * np.pi)).tolist(),
            "pre_brake_relative_rpm_xyz": (values["qvel"][before, 6:] * 60 / (2 * np.pi)).tolist(),
            "pre_brake_relative_wheel_momentum_nms_xyz": values["wheel_relative_axial_momentum"][before].tolist(),
            "brake_command_s": program.brake_command_s, "brake_ramp_start_s": program.brake_on_s,
            "observed_stop_delay_from_ramp_start_s": float(values["time"][stopped[0]] - program.brake_on_s) if len(stopped) else None,
            "stop_criterion_relative_rad_s": program.stop_relative_rad_s,
            "brake_peak_sampled_torque_nm_xyz": np.max(np.abs(values["brake_torque"]), axis=0).tolist(),
            "modeled_brake_dissipation_j": float(-values["brake_work"][-1]),
            "floor_contact_work_on_assembly_j": float(values["work"][-1, 2] - values["brake_work"][-1]),
            "max_positive_brake_power_stage_w": float(values["peak_positive_brake_power"][-1]),
            "max_body_rotation_from_initial_deg": float(np.rad2deg(maximum_rotation)),
            "max_body_centre_height_m": float(np.max(values["qpos"][:, 2])),
            "max_minimum_corner_height_m": float(np.max(values["minimum_corner_height"])),
            "contact_gap_candidate_observed": bool(len(candidates)),
            "flight_assessment": {
                "status": "NUMERICALLY_UNRESOLVED_CONTACT_ENVELOPE" if len(candidates) else "NO_GAP_CANDIDATE_ABOVE_THRESHOLD",
                "criterion": "No geometric contacts; total normal force <=1e-8 N; every cube corner >0.1 mm above plane.",
                "observed_intervals": intervals,
                "intervals_are_continuous_clearance_proof": False,
                "actual_contact_envelope_uncertainty_m": None,
                "visual_edge_radius_m": .002,
                "max_recorded_contact_penetration_m": float(max(0, -values["contact"][:, 2].min())),
                "interpretation": "A tiny box-proxy gap is not resolved physical flight. Compare step/solver/contact-envelope sensitivity; display edges themselves are approximate. Edge crossing/tumbling is separate from capture."
            },
            "dense_period_s": program.dense_period_s,
            "capture_and_second_jump": "NOT_IMPLEMENTED_OR_CLAIMED; first face-to-edge kick only.",
            "hardware_speed_or_brake_qualified": False,
        }
        report["interpretation"] = (
            "Real simulated spin-up from rest, not a pre-spun initialization. Motor and independent finite brake are assumptions. "
            "Dense brake-window rows resolve stopping; they are not continuous physical bounds. Brake work is a SUBSET of constraint work, not an additional energy term."
        )
    return report


def finalize_manifest(directory, manifest):
    manifest["outputs"] = {p.name: sha256(p) for p in sorted(directory.iterdir())
                           if p.is_file() and p.name != "manifest.json"}
    write_json(directory / "manifest.json", manifest)


def run(config, scenario, directory, *, config_path=None):
    if config_path is not None and load_config(config_path) != config:
        raise ValueError("Selected model file differs from the supplied model; do not misattribute its provenance.")
    code_before = {str(p.relative_to(REPO)): sha256(p) for p in sorted((ROOT / "cube_sim").glob("*.py"))}
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
                            "simulation/models", "simulation/intake", "simulation/requirements.txt",
                            "simulation/requirements-lock.txt"], cwd=REPO,
                           check=True, capture_output=True, text=True).stdout.strip()
    source = {"kind": "inline_snapshot", "sha256": sha256(directory / "input.json")}
    if config_path is not None:
        path = Path(config_path).resolve()
        if path.is_relative_to(ROOT / "models"):
            source = {"kind": "repository_file", "path": str(path.relative_to(REPO)), "sha256": sha256(path)}
    manifest = {
        "schema_version": 1, "state": "WIP_SIMULATION_NOT_HARDWARE_OR_ASSEMBLY_APPROVAL",
        "classification": config["classification"], "source_revision": revision,
        "uncommitted_model_code": bool(dirty),
        "code": code_before,
        "dependency_lock_sha256": sha256(ROOT / "requirements-lock.txt"),
        "input_model": source,
        "environment": {"python": platform.python_version(), "platform": platform.platform(),
                        **{pkg: importlib.metadata.version(pkg) for pkg in ("mujoco", "numpy", "matplotlib", "pillow")}},
        "sample_period_s": SAMPLE_PERIOD, "stochasticity": "NONE", "rendering": {"status": "NOT_RUN"},
        "diagnostic_quadrature": quadrature_method(config["integration"]["integrator"]),
        "source_snapshot": config["provenance"]["source_snapshot"],
        "mechanism_source": config["provenance"].get("mechanism_source"),
        "base_model": config["provenance"].get("base_model"),
        "phase_codes": dict(enumerate(PHASES)),
        "dense_sampling": ({"start_s": scenario.startup.dense_start_s, "end_s": scenario.startup.dense_end_s,
                            "period_s": scenario.startup.dense_period_s} if scenario.startup else None),
        "omissions": config["omissions"],
    }
    if code_before != {str(p.relative_to(REPO)): sha256(p) for p in sorted((ROOT / "cube_sim").glob("*.py"))}:
        raise RuntimeError("Code changed during integration; discard this partial run and regenerate from a frozen revision.")
    if config_path is not None and load_config(config_path) != config:
        raise RuntimeError("Model file changed during integration; this partial run is not accepted.")
    finalize_manifest(directory, manifest)
    return values, manifest
