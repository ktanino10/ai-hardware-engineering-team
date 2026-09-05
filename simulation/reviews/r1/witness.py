#!/usr/bin/env python3
"""Independent R1 witnesses; no implementation or archived-evidence writes.

From the repository root:
  PYTHONDONTWRITEBYTECODE=1 simulation/.venv/bin/python \
    simulation/reviews/r1/witness.py

Outputs are this directory's witness.json and disposable, repository-local
simulation/runs/reviewer-r1/ experiments. The frozen intake is read, never
imported or executed. Formulas below are reviewer-authored, not imports of
the author's inertia, quaternion, energy, momentum, or CSV helpers.
"""

import argparse
import copy
import csv
from datetime import datetime, timezone
import hashlib
import importlib.metadata
import itertools
import json
import math
import os
from pathlib import Path
import platform
import shutil
import struct
import subprocess
import sys
from unittest.mock import patch
import xml.etree.ElementTree as ET

sys.dont_write_bytecode = True
REPO = Path(__file__).resolve().parents[3]
SIM = REPO / "simulation"
HERE = SIM / "reviews/r1"
SCRATCH = SIM / "runs/reviewer-r1"
EVIDENCE = SIM / "evidence/initial-v1"
BUNDLE = Path(
    "/Users/kyosuketanino/.copilot/session-state/"
    "cc8c11df-9cc9-4b20-9f05-5680d77250ab/files/rev5-simulation-intake-v1"
)
BASE = "dd7e4b4"
HEAD = "848005a0a63ebc2d9931bea60251e98d40c0296d"
IMPLEMENTATION = "6636b95b78bb14b94acda53a413d39f6baa8688a"
PRIMARY_SOURCES = {
    "https://raw.githubusercontent.com/google-deepmind/mujoco/3.12.0/doc/XMLreference.rst":
        "2652a8b2567a673b14e51a72713465af02be30a972c63c5eaf77253edf6861d2",
    "https://raw.githubusercontent.com/google-deepmind/mujoco/3.12.0/doc/computation/index.rst":
        "0c184816976bae1ce7d598263d1422bf5f489dbd3f46b8395618a59173797656",
    "https://raw.githubusercontent.com/google-deepmind/mujoco/3.12.0/doc/python.rst":
        "9a1ed229cab8f85d9aec0ace16d9b7fa9b48970d26383caa1b00c77cdac3d4c2",
    "https://raw.githubusercontent.com/google-deepmind/mujoco/3.12.0/src/engine/engine_forward.c":
        "c81f57dfa0249b07bfd92ac14ac145e43581a1695be607c5ae80fab2417c6d52",
}

os.environ.setdefault("MPLCONFIGDIR", str(SCRATCH / "mpl-cache"))
sys.path.insert(0, str(SIM))

import mujoco
import numpy as np
from PIL import Image, ImageDraw

from cube_sim import runner, visualize
from cube_sim.model import load_config
from cube_sim.scenarios import Scenario, scenarios


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def jread(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def output_json(path, value):
    Path(path).write_text(
        json.dumps(value, indent=2, sort_keys=True, allow_nan=False) + "\n",
        encoding="utf-8",
    )


def git(*args):
    return subprocess.check_output(
        ["git", "--no-pager", *args], cwd=REPO, text=True
    ).strip()


def maxerr(a, b):
    return float(np.max(np.abs(np.asarray(a) - np.asarray(b))))


def rotation(q):
    w, x, y, z = q
    return np.array([
        [1 - 2 * (y*y + z*z), 2 * (x*y - w*z), 2 * (x*z + w*y)],
        [2 * (x*y + w*z), 1 - 2 * (x*x + z*z), 2 * (y*z - w*x)],
        [2 * (x*z - w*y), 2 * (y*z + w*x), 1 - 2 * (x*x + y*y)],
    ])


def quat_product(a, b):
    return np.r_[a[0]*b[0] - a[1:] @ b[1:],
                 a[0]*b[1:] + b[0]*a[1:] + np.cross(a[1:], b[1:])]


def axis_quat(axis, angle):
    axis = np.asarray(axis, dtype=float)
    return np.r_[math.cos(angle/2), axis / np.linalg.norm(axis) * math.sin(angle/2)]


def independent_error(q, target):
    e = quat_product(q * [1, -1, -1, -1], np.asarray(target))
    if e[0] < 0:
        e = -e
    length = np.linalg.norm(e[1:])
    return 2*e[1:] if length < 1e-14 else e[1:] * 2*math.atan2(length, e[0])/length


def tensor(value):
    a = np.asarray(value, dtype=float)
    return np.diag(a) if a.ndim == 1 else a


def shift(r):
    r = np.asarray(r, dtype=float)
    return np.eye(3) * (r @ r) - r[:, None]*r[None, :]


def parts(config):
    return [(config["body"]["mass_kg"], np.array(config["body"]["com_m"]),
             tensor(config["body"]["inertia_kg_m2"]))] + [
        (w["mass_kg"], np.array(w["center_m"]), tensor(w["inertia_kg_m2"]))
        for w in config["wheels"]
    ]


def aggregate(items):
    mass = math.fsum(p[0] for p in items)
    center = sum((m*r for m, r, _ in items), np.zeros(3)) / mass
    inertia = sum((j + m*shift(r-center) for m, r, j in items), np.zeros((3, 3)))
    return mass, center, inertia


def quantities(config, q, v, gravity):
    """Newton/Euler sums for the specific axisymmetric rotors under review."""
    R = rotation(q[3:7])
    items = parts(config)
    mass, c, _ = aggregate(items)
    center = q[:3] + R @ c
    P = np.zeros(3)
    H = np.zeros(3)
    potential = kinetic = 0.0
    for k, (m, r, j) in enumerate(items):
        off = R @ r
        velocity = v[:3] + R @ np.cross(v[3:6], r)
        omega = v[3:6].copy()
        if k:
            omega[k-1] += v[k+5]
        P += m*velocity
        H += R @ (j @ omega) + np.cross(q[:3]+off-center, m*velocity)
        potential -= m * np.dot(gravity, q[:3]+off)
        kinetic += .5*m*np.dot(velocity, velocity) + .5*omega @ j @ omega
    return P, H, np.array([potential, kinetic]), center


def energy_rate(config, q, v, a, gravity):
    R = rotation(q[3:7])
    result = 0.0
    for k, (m, r, j) in enumerate(parts(config)):
        velocity = v[:3] + R @ np.cross(v[3:6], r)
        acceleration = a[:3] + R @ (
            np.cross(a[3:6], r) + np.cross(v[3:6], np.cross(v[3:6], r))
        )
        omega, alpha = v[3:6].copy(), a[3:6].copy()
        if k:
            omega[k-1] += v[k+5]
            alpha[k-1] += a[k+5]
        result += m*np.dot(velocity, acceleration-gravity) + omega @ j @ alpha
    return float(result)


def mesh_moments(path, density):
    """Signed tetrahedron volume/first/second integrals, mm -> m exactly once."""
    data = Path(path).read_bytes()
    if len(data) >= 84 and len(data) == 84 + 50*struct.unpack("<I", data[80:84])[0]:
        count = struct.unpack("<I", data[80:84])[0]
        triangles = np.array([
            struct.unpack("<12fH", data[84+50*i:134+50*i])[3:12]
            for i in range(count)
        ]).reshape(-1, 3, 3)
    else:
        vertices = [
            [float(x) for x in line.split()[1:4]]
            for line in data.decode("ascii").splitlines()
            if line.lstrip().startswith("vertex ")
        ]
        triangles = np.asarray(vertices).reshape(-1, 3, 3)
    triangles *= .001
    signed = np.einsum(
        "ij,ij->i", triangles[:, 0], np.cross(triangles[:, 1], triangles[:, 2])
    ) / 6
    volume = math.fsum(signed)
    sums = triangles.sum(axis=1)
    first = np.einsum("i,ij->j", signed, sums)/4
    second = (
        np.einsum("n,nij,nik->jk", signed, triangles, triangles)
        + np.einsum("i,ij,ik->jk", signed, sums, sums)
    ) / 20
    center = first/volume
    origin = density * (np.eye(3)*np.trace(second) - second)
    return density*volume, center, origin-density*volume*shift(center), len(triangles)


def frozen_intake(bundle):
    expected = {
        "INTAKE.txt": "bef4cfd724089d818b6083070dd2853c40b23100bdac6826157f3742a47233a2",
        "manifest.json": "1f94e5fdf89d8e1df234e9dec4db7ea32568e30671ba9a841293cf9d79d55999",
        "baseline/results.json": "a181bc328b61ecdad52a0b8acdcc6e7cc5c0e5c4748b680ec8fcad0aa5e44c36",
        "baseline/screen.py": "fc8b4dd6e013afc834b37649414e6230b5689e5c28a9b67a0ec2b6fec7d3bd88",
    }
    checked = {}
    for name, digest in expected.items():
        actual = sha(bundle/name)
        assert actual == digest, name
        checked[name] = actual
    intake = jread(SIM/"intake/rev5-v1.json")
    base = jread(bundle/"baseline/results.json")
    original = base["scenarios"][0]
    assert original["name"] == "solid_CAD_partial"
    assert original["M_kg"] == intake["locked_partial"]["mass_kg"]
    assert original["CG_m"] == intake["locked_partial"]["com_m"]
    assert original["Ic_kg_m2"] == intake["locked_partial"]["inertia_kg_m2"]
    manifest = jread(bundle/"manifest.json")
    bound = {row["path"]: row for row in manifest["files"]}
    for source in intake["upstream_sources"]:
        relative = "source/"+source["path"]
        actual = sha(bundle/relative)
        assert actual == source["sha256"] == bound[relative]["sha256"]
        assert (bundle/relative).stat().st_size == bound[relative]["bytes"]
        checked[relative] = actual
    mesh = bundle/"baseline/assembly.stl"
    assert sha(mesh) == intake["printed_aggregate"]["mesh_sha256"]
    checked["baseline/assembly.stl"] = sha(mesh)
    mass, center, j, triangles = mesh_moments(
        mesh, intake["printed_aggregate"]["density_kg_m3_assumption"]
    )
    prints = intake["printed_aggregate"]
    errors = [abs(mass-prints["mass_kg"]), maxerr(center, prints["com_m"]),
              maxerr(j, prints["inertia_kg_m2"])]
    assert max(errors) < 1e-11, errors
    independent = [(mass, center, j)]
    motor = intake["motor_surrogate"]
    for axis in range(3):
        m, r, h = [motor[k] for k in ("mass_kg", "radius_m", "thickness_m")]
        vals = np.full(3, m*(3*r*r+h*h)/12)
        vals[axis] = m*r*r/2
        independent.append((m, np.eye(3)[axis]*motor["axial_center_m"], np.diag(vals)))
    board = intake["bare_laminate"]
    dims = np.array(board["dimensions_m"])
    independent.append((
        board["mass_kg"], np.array(board["com_m"]),
        np.diag(board["mass_kg"]*(sum(dims*dims)-dims*dims)/12),
    ))
    bm, bc, bj = aggregate(independent)
    config = load_config(SIM/"models/rev5-proxy.json")
    body = config["body"]
    assert abs(bm-body["mass_kg"]) < 1e-11
    assert maxerr(bc, body["com_m"]) < 1e-12
    assert maxerr(bj, body["inertia_kg_m2"]) < 1e-12
    wm, wc, wj = aggregate(parts(config))
    lock = intake["locked_partial"]
    assert abs(wm-lock["mass_kg"]) < 1e-13
    assert maxerr(wc, lock["com_m"]) < 1e-14
    assert maxerr(wj, lock["inertia_kg_m2"]) < 1e-14
    return {
        "bundle_path": str(bundle), "verified_files": checked,
        "unadopted_candidate_L_read_or_executed": False,
        "old_script_imported_or_executed": False,
        "source_owner_revision": intake["source_revision"],
        "source_is_main_or_release": intake["source_is_main_or_release"],
        "mesh_tetrahedral_integral": {
            "triangles": triangles, "mass_kg": mass, "com_m": center.tolist(),
            "centroidal_inertia_kg_m2": j.tolist(),
            "absolute_errors_vs_frozen_mass_com_inertia": errors,
        },
        "independent_mesh_plus_motors_plus_laminate": {
            "mass_kg": bm, "com_m": bc.tolist(), "inertia_kg_m2": bj.tolist(),
            "inertia_error_vs_proxy_kg_m2": maxerr(bj, body["inertia_kg_m2"]),
        },
        "recomposed_locked": {
            "mass_kg": wm, "com_m": wc.tolist(), "inertia_kg_m2": wj.tolist(),
            "inertia_error_kg_m2": maxerr(wj, lock["inertia_kg_m2"]),
        },
    }


def mechanics():
    rows = {}
    tau = np.array([.009, -.007, .011])
    for name in ("reference", "rev5-proxy"):
        config = load_config(SIM/"models"/f"{name}.json")
        path = EVIDENCE/name/"three-wheel"
        model = mujoco.MjModel.from_xml_path(str(path/"model.xml"))
        element = ET.parse(path/"model.xml").getroot()
        assert element.find("compiler").get("inertiafromgeom") == "false"
        assert element.find("equality") is None
        assert (model.nq, model.nv, model.nu, model.neq) == (10, 9, 3, 0)
        assert np.array_equal(model.actuator_trnid[:, 0], [1, 2, 3])
        assert np.array_equal(model.actuator_gear[:, 0], [1, 1, 1])
        mass, com, locked = aggregate(parts(config))
        axial = np.array([tensor(w["inertia_kg_m2"])[i, i]
                          for i, w in enumerate(config["wheels"])])
        alpha = np.linalg.solve(locked - np.diag(axial), -tau)
        wheel_accel = tau/axial - alpha
        eigs = [np.linalg.eigvalsh(j) for _, _, j in parts(config)]
        assert all(min(e) > 0 and 2*max(e) <= sum(e)+1e-14 for e in eigs)
        compiled = rotation(model.body_iquat[1])
        compiled_error = maxerr(
            compiled @ np.diag(model.body_inertia[1]) @ compiled.T,
            config["body"]["inertia_kg_m2"] if name == "rev5-proxy"
            else np.diag(config["body"]["inertia_kg_m2"]),
        )
        assert compiled_error < 1e-12
        trials = []
        for q in (np.array([1., 0, 0, 0]), axis_quat([0, 0, 1], math.pi/2),
                  axis_quat([1, 2, -1], .73)):
            data = mujoco.MjData(model)
            data.qpos[:3] = [.1, -.2, .5]
            data.qpos[3:7] = q
            data.qpos[7:] = [.4, -.7, 1.1]
            data.ctrl[:] = tau
            mujoco.mj_forward(model, data)
            predicted_origin = -rotation(q) @ np.cross(alpha, com)
            assert maxerr(data.qacc[3:6], alpha) < 1e-10
            assert maxerr(data.qacc[6:], wheel_accel) < 1e-10
            assert maxerr(data.qacc[:3], predicted_origin) < 1e-12
            assert np.array_equal(data.qfrc_actuator[:6], np.zeros(6))
            assert not np.any(data.xfrc_applied) and not np.any(data.qfrc_applied)
            trials.append({
                "q_wxyz": q.tolist(), "predicted_origin_acceleration_world_m_s2": predicted_origin.tolist(),
                "origin_acceleration_error_m_s2": maxerr(data.qacc[:3], predicted_origin),
                "angular_acceleration_error_rad_s2": maxerr(data.qacc[3:6], alpha),
                "wheel_relative_acceleration_error_rad_s2": maxerr(data.qacc[6:], wheel_accel),
                "angular_acceleration_world_rad_s2": (rotation(q) @ data.qacc[3:6]).tolist(),
            })
        rows[name] = {
            "mass_kg": mass, "whole_com_body_m": com.tolist(),
            "locked_tensor_about_whole_com_kg_m2": locked.tolist(),
            "principal_moments_each_part_kg_m2": [e.tolist() for e in eigs],
            "compiled_chassis_tensor_error_kg_m2": compiled_error,
            "axial_rotor_inertias_kg_m2": axial.tolist(),
            "joint_effort_nm": tau.tolist(), "predicted_body_alpha_rad_s2": alpha.tolist(),
            "predicted_rotor_relative_alpha_rad_s2": wheel_accel.tolist(),
            "rotation_trials": trials,
        }
    return rows


def free_space():
    result = {}
    for name in ("reference", "rev5-proxy"):
        config = load_config(SIM/"models"/f"{name}.json")
        model = mujoco.MjModel.from_xml_path(str(EVIDENCE/name/"three-wheel/model.xml"))
        data = mujoco.MjData(model)
        data.qpos[:3] = [.1, -.2, .6]
        data.qpos[3:7] = axis_quat([1, 2, -1], .73)
        data.qpos[7:] = [.3, -.7, 1.1]
        mujoco.mj_forward(model, data)
        initial = data.qpos.copy()
        for _ in range(50):
            mujoco.mj_step(model, data)
        assert np.array_equal(initial, data.qpos) and not np.any(data.qvel)
        data.time = 0
        data.qvel[:] = [.17, -.12, .26, .31, -.27, .19, 17, -11, 23]
        initial_velocity = data.qvel.copy()
        mujoco.mj_forward(model, data)
        P0, H0, E0, c0 = quantities(config, data.qpos, data.qvel, model.opt.gravity)
        maximum = np.zeros(8)
        work = 0.
        for step in range(301):
            P, H, E, c = quantities(config, data.qpos, data.qvel, model.opt.gravity)
            deviations = [
                np.linalg.norm(P-P0), np.linalg.norm(H-H0),
                maxerr(P, data.sensor("com_velocity_world").data*sum(model.body_mass)),
                maxerr(H, data.sensor("angular_momentum_world").data),
                maxerr(E, data.energy), abs(sum(E-E0)-work),
                abs(np.linalg.norm(data.qpos[3:7])-1),
                np.linalg.norm(c-c0-(P0/sum(model.body_mass))*data.time),
            ]
            maximum = np.maximum(maximum, deviations)
            if step == 300:
                break
            data.ctrl[:] = np.array([.003, -.002, .0025]) * (1 if step < 150 else -1)
            mujoco.mj_forward(model, data)
            before = data.ctrl @ data.qvel[6:]
            mujoco.mj_step(model, data)
            mujoco.mj_forward(model, data)
            work += .5*model.opt.timestep*(before+data.ctrl @ data.qvel[6:])
            assert data.ncon == 0
        assert max(maximum[:4]) < 1e-10, maximum
        assert maximum[4] < 1e-11 and maximum[5] < 1e-7
        assert maximum[6] < 1e-12 and maximum[7] < 1e-10
        result[name] = {
            "duration_s": .6, "dt_s": model.opt.timestep,
            "initial_qpos": initial.tolist(), "initial_qvel": initial_velocity.tolist(),
            "pulse_nm": [.003, -.002, .0025], "reverse_at_s": .3,
            "stationary_zero_input_100ms_exact": True,
            "initial_P_world_kg_m_s": P0.tolist(), "initial_H_com_world_nms": H0.tolist(),
            "max_linear_momentum_drift_kg_m_s": float(maximum[0]),
            "max_angular_momentum_drift_nms": float(maximum[1]),
            "max_P_sensor_error": float(maximum[2]), "max_H_sensor_error": float(maximum[3]),
            "max_independent_energy_vs_engine_j": float(maximum[4]),
            "max_energy_minus_motor_work_j": float(maximum[5]),
            "max_quaternion_norm_error": float(maximum[6]),
            "max_com_affine_motion_error_m": float(maximum[7]),
        }
    return result


CSV_NAMES = {
    "time": ["time_s"],
    "qpos": ["x_m", "y_m", "z_m", "qw", "qx", "qy", "qz", "wheel_x_rad", "wheel_y_rad", "wheel_z_rad"],
    "qvel": ["vx_world_m_s", "vy_world_m_s", "vz_world_m_s", "wx_body_rad_s", "wy_body_rad_s",
             "wz_body_rad_s", "wheel_x_relative_rad_s", "wheel_y_relative_rad_s", "wheel_z_relative_rad_s"],
    "contact": ["active_contacts", "normal_force_n", "minimum_contact_distance_m", "max_loaded_point_slip_m_s"],
    "energy": ["potential_j", "kinetic_j"],
    "work": ["motor_work_j", "passive_work_j", "constraint_work_j"],
}
for _key, _unit in (
    ("command", "nm"), ("delayed", "nm"), ("applied", "nm"), ("saturated", "bool"),
    ("speed_cutoff", "bool"), ("speed_exceeded", "bool"), ("angular_momentum", "world_nms"),
    ("linear_momentum", "world_kg_m_s"), ("omega_world", "rad_s"),
    ("wheel_absolute_axial", "rad_s"), ("attitude_error", "body_rad"),
):
    CSV_NAMES[_key] = [f"{_key}_{axis}_{_unit}" for axis in "xyz"]


def artifact_checks():
    rows = {}
    index = jread(EVIDENCE/"index-manifest.json")
    for name, digest in index["files"].items():
        assert sha(EVIDENCE/name) == digest, name
    for kind in ("reference", "rev5-proxy"):
        config = load_config(SIM/"models"/f"{kind}.json")
        for scenario_name in scenarios():
            path = EVIDENCE/kind/scenario_name
            manifest, values = visualize.verify_current(path)
            assert manifest["source_revision"] == IMPLEMENTATION
            config_at_run = jread(path/"input.json")
            assert config == config_at_run
            scenario = jread(path/"scenario.json")
            result = jread(path/"summary.json")
            assert result["scenario"] == scenario
            assert scenario == json.loads(json.dumps(scenarios()[scenario_name].record()))
            with (path/"trajectory.csv").open(newline="") as stream:
                records = list(csv.DictReader(stream))
            expected_columns = {col for cols in CSV_NAMES.values() for col in cols}
            assert set(records[0]) == expected_columns
            for key, names in CSV_NAMES.items():
                actual = np.array([[float(row[col]) for col in names] for row in records])
                if key == "time":
                    actual = actual[:, 0]
                assert np.array_equal(actual, values[key]), (kind, scenario_name, key)
            vectors = np.array([independent_error(q, scenario["target"]) for q in values["qpos"][:, 3:7]])
            assert maxerr(vectors, values["attitude_error"]) < 1e-13
            angles = np.degrees(np.linalg.norm(vectors, axis=1))
            assert abs(angles[-1]-result["final_attitude_error_deg"]) < 1e-10
            assert result["samples"] == len(values["time"])
            count = round(scenario["duration_s"]*25)
            with (path/"video-frames.csv").open(newline="") as stream:
                frames = list(csv.DictReader(stream))
            assert len(frames) == count == manifest["rendering"]["frames"]
            for frame, row in enumerate(frames):
                sample = frame*4
                assert int(row["video_frame"]) == frame and int(row["sample_index"]) == sample
                assert abs(float(row["time_s"])-frame/25) < 1e-12
                assert float(row["time_s"]) == values["time"][sample]
                assert row["qpos_float64_le_sha256"] == hashlib.sha256(
                    values["qpos"][sample].astype("<f8").tobytes()).hexdigest()
            rate_error = energy_error = p_error = h_error = 0.
            gravity = config["gravity_m_s2"] if scenario["gravity"] else [0, 0, 0]
            for q, v, e, H, P, w in zip(
                values["qpos"], values["qvel"], values["energy"], values["angular_momentum"],
                values["linear_momentum"], values["omega_world"]
            ):
                pi, hi, ei, _ = quantities(config, q, v, gravity)
                energy_error = max(energy_error, maxerr(ei, e))
                p_error = max(p_error, maxerr(pi, P))
                h_error = max(h_error, maxerr(hi, H))
                rate_error = max(rate_error, maxerr(rotation(q[3:7]) @ v[3:6], w))
            assert max(energy_error, p_error, h_error, rate_error) < 1e-11
            assert np.array_equal(values["wheel_absolute_axial"], values["qvel"][:, 3:6]+values["qvel"][:, 6:])
            residual = values["energy"].sum(axis=1)-values["energy"][0].sum()-values["work"].sum(axis=1)
            assert abs(residual[-1]-result["rigid_energy_minus_logged_work_j"]) < 1e-12
            half = config["body"]["side_m"]/2
            corners = np.array(list(itertools.product((-half, half), repeat=3)))
            first_q = values["qpos"][0]
            lowest = float((corners @ rotation(first_q[3:7]).T + first_q[:3])[:, 2].min())
            assert abs(lowest-scenario["initial_clearance_m"]) < 1e-14
            if scenario_name == "rest":
                assert values["contact"][-1, 0] >= 3
                assert abs(values["contact"][-1, 1]-sum(p[0] for p in parts(config))*abs(gravity[2])) < .001
                assert result["max_penetration_m"] < .0002
            rows[f"{kind}/{scenario_name}"] = {
                "manifest_sha256": sha(path/"manifest.json"),
                "outputs": manifest["outputs"],
                "csv_columns": len(expected_columns), "csv_npz_exact_all_columns": True,
                "exact_frame_rows_hashes": True, "frames": count,
                "initial_height_m": float(values["qpos"][0, 2]),
                "independent_lowest_corner_initial_world_z_m": lowest,
                "initial_penetration_m": float(-min(0, values["contact"][0, 2])),
                "initial_qvel_max_abs": float(abs(values["qvel"][0]).max()),
                "initial_attitude_error_deg": float(angles[0]),
                "final_attitude_error_deg": float(angles[-1]), "outcome": result["outcome"],
                "max_independent_energy_error_j": energy_error,
                "max_independent_P_error_kg_m_s": p_error,
                "max_independent_H_error_nms": h_error,
                "max_world_angular_rate_error_rad_s": rate_error,
                "max_sampled_energy_work_residual_j": float(abs(residual).max()),
                "final_energy_work_residual_j": float(residual[-1]),
                "max_sampled_penetration_m": result["max_penetration_m"],
                "max_loaded_point_slip_m_s": result["max_loaded_point_slip_m_s"],
                "last_normal_force_n": float(values["contact"][-1, 1]),
                "weight_n": sum(p[0] for p in parts(config))*abs(gravity[2]),
            }
    return rows


def representative_repeats():
    result = {}
    for kind, name in (
        ("reference", "three-wheel"), ("rev5-proxy", "fall"),
        ("rev5-proxy", "vertex-balance"), ("rev5-proxy", "face-to-vertex-attempt"),
    ):
        config = load_config(SIM/"models"/f"{kind}.json")
        path = EVIDENCE/kind/name
        fresh, xml = runner.simulate(config, scenarios()[name])
        _, archived = visualize.read_run(path)
        equal = all(np.array_equal(fresh[k], archived[k]) for k in archived)
        assert equal and xml == (path/"model.xml").read_text()
        result[f"{kind}/{name}"] = {
            "all_npz_arrays_exact": equal, "xml_exact": True,
            "trajectory_npz_sha256": sha(path/"trajectory.npz"),
        }
    return result


def controller_checks():
    result = {}
    for name in ("reference", "rev5-proxy"):
        for trial in ("three-wheel", "vertex-balance", "face-to-vertex-attempt"):
            path = EVIDENCE/name/trial
            config, scenario = jread(path/"input.json"), jread(path/"scenario.json")
            _, v = visualize.read_run(path)
            times = v["time"]
            if scenario["controller"] == "pulse":
                expected = np.array([
                    np.array(scenario["pulse_nm"])*(1 if t < .5-1e-9 else -1 if t < 1-1e-9 else 0)
                    for t in times
                ])
            else:
                expected = np.array([
                    -scenario["kp_nm_rad"]*independent_error(q[3:7], scenario["target"])
                    +scenario["kd_nm_s_rad"]*rate[3:6]
                    for q, rate in zip(v["qpos"], v["qvel"])
                ])
            assert maxerr(expected, v["command"]) < 1e-13
            assert np.array_equal(v["delayed"][:2], np.zeros((2, 3)))
            assert np.array_equal(v["delayed"][2:], v["command"][:-2])
            limit = np.array(config["actuation"]["torque_limit_nm"])
            speed = np.array(config["actuation"]["speed_cutoff_rad_s"])
            clipped = np.clip(v["delayed"], -limit, limit)
            cutoff = (abs(v["qvel"][:, 6:]) >= speed) & (clipped*v["qvel"][:, 6:] > 0)
            clipped[cutoff] = 0
            assert np.array_equal(v["applied"], clipped)
            assert np.array_equal(v["speed_cutoff"], cutoff)
            assert np.array_equal(v["saturated"], abs(v["delayed"]) > limit)
            assert np.array_equal(v["speed_exceeded"], abs(v["qvel"][:, 6:]) > speed)
            result[f"{name}/{trial}"] = {
                "pd_or_pulse_equation_max_error_nm": maxerr(expected, v["command"]),
                "20ms_fifo_exact_on_100Hz_rows": True,
                "clip_and_outward_cutoff_exact": True,
                "max_relative_speed_rad_s": abs(v["qvel"][:, 6:]).max(axis=0).tolist(),
                "cutoff_samples": cutoff.sum(axis=0).tolist(),
                "saturated_samples": v["saturated"].sum(axis=0).tolist(),
                "overspeed_samples": v["speed_exceeded"].sum(axis=0).tolist(),
                "reversing_torque_while_overspeed_samples": int(np.count_nonzero(
                    (abs(v["qvel"][:, 6:]) > speed) & (v["applied"]*v["qvel"][:, 6:] < 0))),
            }
    reference = load_config()
    pd_trial = Scenario(
        "reviewer-sign", "Independent rotated free-space PD sign test",
        contact=False, gravity=False, controller="pd",
        target=tuple(axis_quat([0, 0, 1], math.pi/2)),
        perturbation_rad=.035, duration_s=1.2,
    )
    v, _ = runner.simulate(reference, pd_trial)
    result["rotated_free_PD"] = {
        "initial_error_rad": float(np.linalg.norm(v["attitude_error"][0])),
        "final_error_rad": float(np.linalg.norm(v["attitude_error"][-1])),
        "positive_initial_wheel_x_effort_nm": float(v["applied"][2, 0]),
        "initial_world_body_y_velocity_after_effort_rad_s": float(v["omega_world"][3, 1]),
    }
    assert result["rotated_free_PD"]["final_error_rad"] < .035
    assert v["omega_world"][3, 1] < 0
    return result


def contact_point_check(config, model, data):
    R = rotation(data.qpos[3:7])
    normal, max_slip, min_dist = 0., 0., 0.
    positive_tangent_power = 0.
    jac_error = constraint_error = 0.
    count = 0
    contact_power = 0.
    for i in range(data.ncon):
        contact = data.contact[i]
        min_dist = min(min_dist, float(contact.dist))
        if contact.efc_address < 0:
            continue
        force = np.zeros(6)
        mujoco.mj_contactForce(model, data, i, force)
        velocity = data.qvel[:3] + R @ np.cross(
            data.qvel[3:6], R.T @ (contact.pos-data.qpos[:3])
        )
        jac = np.zeros((3, model.nv))
        mujoco.mj_jac(model, data, jac, None, contact.pos, 1)
        jac_error = max(jac_error, maxerr(jac @ data.qvel, velocity))
        local_velocity = contact.frame.reshape(3, 3) @ velocity
        contact_power += force[:3] @ local_velocity
        positive_tangent_power = max(positive_tangent_power, float(force[1:3] @ local_velocity[1:]))
        normal += force[0]
        if force[0] > 1e-8:
            count += 1
            max_slip = max(max_slip, float(np.linalg.norm(velocity[:2])))
    constraint_error = abs(contact_power - data.qfrc_constraint @ data.qvel)
    recorded = runner.contacts(model, data)
    assert maxerr(recorded, [count, normal, min_dist, max_slip]) < 1e-11
    return jac_error, constraint_error, positive_tangent_power


def contact_energy():
    """Record four actual RK4 evaluation states without modifying dynamics.

    The read-only control callback records state before acceleration evaluation.
    After mj_step returns, a separate MjData evaluates the same states, with the
    callback removed. Thus quadrature cannot alter the integrated trajectory.
    """
    rows = []
    source_model = load_config(SIM/"models/rev5-proxy.json")
    for name in ("fall", "vertex-balance"):
        scenario = scenarios()[name]
        path = EVIDENCE/"rev5-proxy"/name
        _, archived = visualize.read_run(path)
        for dt, solver, iterations in (
            (.002, "Newton", 50), (.001, "Newton", 50),
            (.0005, "Newton", 100), (.002, "CG", 100),
        ):
            config = copy.deepcopy(source_model)
            config["integration"].update(timestep_s=dt, solver=solver, iterations=iterations)
            values, xml = runner.simulate(config, scenario)
            residual = values["energy"].sum(axis=1)-values["energy"][0].sum()-values["work"].sum(axis=1)
            row = {
                "scenario": name, "dt_s": dt, "solver": solver, "iterations": iterations,
                "max_100Hz_energy_work_residual_j": float(abs(residual).max()),
                "final_energy_work_residual_j": float(residual[-1]),
                "outcome": runner.summary(values, scenario, config)["outcome"],
                "final_height_m": float(values["qpos"][-1, 2]),
                "max_100Hz_penetration_m": float(-values["contact"][:, 2].min()),
                "final_attitude_error_deg": float(np.degrees(np.linalg.norm(values["attitude_error"][-1]))),
            }
            if solver != "Newton":
                rows.append(row)
                continue
            model = mujoco.MjModel.from_xml_string(xml)
            data = mujoco.MjData(model)
            probe = mujoco.MjData(model)
            data.qpos[:] = values["qpos"][0]
            data.qvel[:] = values["qvel"][0]
            mujoco.mj_forward(model, data)
            initial_energy = quantities(config, data.qpos, data.qvel, model.opt.gravity)[2].sum()
            snapshots = []
            work_trap = np.zeros(3)
            work_rk = np.zeros(3)
            maxima = np.zeros(9)
            delay_steps = round(scenario.command_delay_s/dt)
            requested_history = []
            all_step_peak = None
            virtual_power_peak = None

            def capture(_model, d):
                snapshots.append((d.qpos.copy(), d.qvel.copy(), d.ctrl.copy(), float(d.time),
                                  d.qacc_warmstart.copy()))

            def effort(d):
                if scenario.controller == "off":
                    return np.zeros(3)
                return (-scenario.kp_nm_rad*independent_error(d.qpos[3:7], scenario.target)
                        +scenario.kd_nm_s_rad*d.qvel[3:6])

            def power(d):
                return np.array([d.ctrl @ d.qvel[6:], d.qfrc_passive @ d.qvel,
                                 d.qfrc_constraint @ d.qvel])

            stride = round(.01/dt)
            count = round(scenario.duration_s/dt)
            for step in range(count):
                requested_history.append(effort(data))
                delayed = requested_history[step-delay_steps] if step >= delay_steps else np.zeros(3)
                applied = np.clip(delayed, -.02, .02)
                applied[(abs(data.qvel[6:]) >= 80) & (applied*data.qvel[6:] > 0)] = 0
                data.ctrl[:] = applied
                mujoco.mj_forward(model, data)
                before = power(data)
                snapshots.clear()
                assert mujoco.get_mjcb_control() is None
                mujoco.set_mjcb_control(capture)
                try:
                    mujoco.mj_step(model, data)
                finally:
                    mujoco.set_mjcb_control(None)
                mujoco.mj_forward(model, data)
                work_trap += dt*.5*(before+power(data))
                powers = []
                for q, v, u, t, warm in snapshots:
                    probe.qpos[:] = q
                    probe.qvel[:] = v
                    probe.ctrl[:] = u
                    probe.time = t
                    probe.qacc_warmstart[:] = warm
                    mujoco.mj_forward(model, probe)
                    p = power(probe)
                    powers.append(p)
                    independent = quantities(config, q, v, model.opt.gravity)[2]
                    maxima[2] = max(maxima[2], maxerr(independent, probe.energy))
                    rate_difference = energy_rate(config, q, v, probe.qacc, model.opt.gravity)-sum(p)
                    mass_acceleration = np.zeros(model.nv)
                    mujoco.mj_mulM(model, probe, mass_acceleration, probe.qacc)
                    force_residual = (mass_acceleration + probe.qfrc_bias - probe.qfrc_actuator
                                      - probe.qfrc_passive - probe.qfrc_constraint)
                    residual_power = float(v @ force_residual)
                    if abs(rate_difference) > maxima[3]:
                        virtual_power_peak = {
                            "time_s": t, "independent_dE_dt_minus_force_power_w": rate_difference,
                            "solver_force_equation_v_dot_residual_w": residual_power,
                            "unexplained_difference_w": rate_difference-residual_power,
                        }
                    maxima[3] = max(maxima[3], abs(rate_difference))
                    maxima[7] = max(maxima[7], abs(rate_difference-residual_power))
                    maxima[8] = max(maxima[8], np.linalg.norm(force_residual))
                    if probe.ncon:
                        jp, cp, tp = contact_point_check(config, model, probe)
                        maxima[4:7] = np.maximum(maxima[4:7], [jp, cp, tp])
                assert len(powers) == 4
                work_rk += dt*np.array([1, 2, 2, 1]) @ np.array(powers)/6
                E = quantities(config, data.qpos, data.qvel, model.opt.gravity)[2].sum()
                trap_resid = E-initial_energy-sum(work_trap)
                rk_resid = E-initial_energy-sum(work_rk)
                if abs(trap_resid) > maxima[0]:
                    all_step_peak = {"time_s": float(data.time), "trapezoid_residual_j": float(trap_resid),
                                     "rk4_stage_residual_j": float(rk_resid),
                                     "four_constraint_powers_w": [float(p[2]) for p in powers]}
                maxima[:2] = np.maximum(maxima[:2], [abs(trap_resid), abs(rk_resid)])
                if (step+1) % stride == 0:
                    index = (step+1)//stride
                    assert maxerr(data.qpos, values["qpos"][index]) < 1e-10
                    assert maxerr(work_trap, values["work"][index]) < 1e-8
            assert maxima[2] < 1e-9 and maxima[4] < 1e-10, maxima
            assert maxima[5] < 1e-8 and maxima[7] < 1e-8, maxima
            row.update({
                "independent_controller_and_stage_probe_qpos_match_max_tolerance": 1e-10,
                "all_step_max_trapezoid_residual_j": float(maxima[0]),
                "all_step_max_rk4_stage_residual_j": float(maxima[1]),
                "final_rk4_stage_residual_j": float(rk_resid),
                "max_independent_energy_error_j": float(maxima[2]),
                "max_instantaneous_dE_dt_minus_force_power_w": float(maxima[3]),
                "max_point_velocity_vs_engine_jacobian_m_s": float(maxima[4]),
                "max_contact_power_vs_generalized_constraint_power_w": float(maxima[5]),
                "max_positive_tangential_contact_power_w": float(maxima[6]),
                "max_virtual_power_difference_after_solver_residual_w": float(maxima[7]),
                "max_generalized_force_equation_residual_norm": float(maxima[8]),
                "peak_virtual_power_difference": virtual_power_peak,
                "peak_trapezoid_step": all_step_peak,
                "stage_recorder_changes_integrated_state": False,
            })
            rows.append(row)
    return rows


def invalidation():
    target = SCRATCH/"invalidation"
    if target.exists():
        shutil.rmtree(target)
    copied_sim = target/"simulation"
    run = copied_sim/"evidence/run"
    shutil.copytree(EVIDENCE/"rev5-proxy/fall", run)
    for subdir in ("cube_sim", "models", "intake"):
        shutil.copytree(SIM/subdir, copied_sim/subdir, ignore=shutil.ignore_patterns("__pycache__"))
    shutil.copyfile(SIM/"requirements-lock.txt", copied_sim/"requirements-lock.txt")
    results = {}
    with patch.object(visualize, "ROOT", copied_sim):
        visualize.verify_current(run)
        for label, path in (
            ("code_changed", copied_sim/"cube_sim/scenarios.py"),
            ("input_model_changed", copied_sim/"models/rev5-proxy.json"),
            ("frozen_intake_changed", copied_sim/"intake/rev5-v1.json"),
            ("dependency_lock_changed", copied_sim/"requirements-lock.txt"),
            ("trajectory_csv_changed", run/"trajectory.csv"),
            ("video_changed", run/"motion.mp4"),
        ):
            original = path.read_bytes()
            path.write_bytes(original+b"\nchanged in reviewer scratch only\n")
            try:
                try:
                    visualize.verify_current(run)
                    raise AssertionError(f"Mutation was accepted: {label}")
                except ValueError as error:
                    current_error = str(error)
                historical_readable = True
                try:
                    visualize.read_run(run)
                except ValueError:
                    historical_readable = False
                assert historical_readable == (path.parent != run)
                results[label] = {
                    "rejected_as_current": True, "error": current_error,
                    "historical_readable": historical_readable,
                }
            finally:
                path.write_bytes(original)
        file = run/"model.xml"
        original = file.read_bytes()
        file.unlink()
        try:
            try:
                visualize.verify_current(run)
                raise AssertionError("Missing XML was accepted")
            except FileNotFoundError:
                results["missing_xml"] = {"rejected": True, "exception": "FileNotFoundError"}
        finally:
            file.write_bytes(original)
        visualize.verify_current(run)
    try:
        runner.run(load_config(), scenarios()["rest"], run)
        raise AssertionError("Existing directory was overwritten")
    except FileExistsError:
        results["existing_run_directory"] = {"overwrite_refused": True}
    shutil.rmtree(target)
    return results


def media():
    result = {}
    contact_sheet_rows = []
    for kind, name in (
        ("reference", "three-wheel"), ("rev5-proxy", "fall"),
        ("rev5-proxy", "vertex-balance"), ("rev5-proxy", "face-to-vertex-attempt"),
    ):
        path = EVIDENCE/kind/name
        movie = path/"motion.mp4"
        info = json.loads(subprocess.check_output([
            "ffprobe", "-v", "error", "-count_frames", "-select_streams", "v:0",
            "-show_entries", "stream=codec_name,width,height,r_frame_rate,avg_frame_rate,nb_read_frames,duration",
            "-of", "json", str(movie),
        ]))["streams"][0]
        assert info["codec_name"] == "h264"
        assert (info["width"], info["height"], info["r_frame_rate"]) == (960, 720, "25/1")
        count = int(info["nb_read_frames"])
        assert count == jread(path/"manifest.json")["rendering"]["frames"]
        subprocess.run(
            ["ffmpeg", "-v", "error", "-i", str(movie), "-f", "null", "-"],
            check=True, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE,
        )
        wanted = [0, count//2, count-1]
        expression = "+".join(f"eq(n\\,{i})" for i in wanted)
        decoded = subprocess.check_output([
            "ffmpeg", "-v", "error", "-i", str(movie), "-vf", "select="+expression,
            "-fps_mode", "passthrough", "-f", "rawvideo", "-pix_fmt", "rgb24", "-",
        ])
        frames = np.frombuffer(decoded, np.uint8).reshape(3, 720, 960, 3)
        _, values = visualize.read_run(path)
        model = mujoco.MjModel.from_xml_path(str(path/"model.xml"))
        data = mujoco.MjData(model)
        matches = []
        row = Image.new("RGB", (960, 264), "#132134")
        draw = ImageDraw.Draw(row)
        draw.text((8, 3), f"{kind}/{name}: first / middle / last decoded frames", fill="white")
        with mujoco.Renderer(model, height=520, width=960) as renderer:
            for slot, frame in enumerate(wanted):
                index = frame*4
                data.qpos[:] = values["qpos"][index]
                data.qvel[:] = values["qvel"][index]
                data.ctrl[:] = values["applied"][index]
                data.time = values["time"][index]
                mujoco.mj_forward(model, data)
                camera = mujoco.MjvCamera()
                camera.lookat[:] = data.qpos[:3]
                camera.distance, camera.azimuth, camera.elevation = .85, 135, -24
                renderer.update_scene(data, camera=camera)
                raw = renderer.render()
                diff = raw.astype(float)-frames[slot, 100:620].astype(float)
                mae, rms = float(abs(diff).mean()), float(np.sqrt(np.mean(diff*diff)))
                assert mae < 2.0, (kind, name, index, mae)
                matches.append({
                    "video_frame": frame, "trajectory_sample": index,
                    "time_s": float(data.time), "scene_mean_absolute_rgb_error": mae,
                    "scene_rgb_rmse": rms,
                })
                row.paste(Image.fromarray(frames[slot]).resize((320, 240)), (320*slot, 24))
        preview = np.array(Image.open(path/"preview.png").convert("RGB")).astype(float)
        preview_mae = float(abs(preview-frames[1]).mean())
        assert preview_mae < 2.0
        copied = SCRATCH/"plots"/kind/name
        if copied.exists():
            shutil.rmtree(copied)
        shutil.copytree(path, copied)
        original_plot_sha = sha(path/"plots.png")
        visualize.plot(copied)
        exact = sha(copied/"plots.png") == original_plot_sha
        assert exact, (kind, name, "plot not reproducible")
        result[f"{kind}/{name}"] = {
            "movie_sha256": sha(movie), "ffprobe": info, "full_decode_error_free": True,
            "direct_scene_rerenders": matches, "middle_frame_vs_preview_mean_rgb_error": preview_mae,
            "plot_regeneration_pixel_file_exact": exact, "plot_sha256": original_plot_sha,
        }
        shutil.rmtree(copied)
        contact_sheet_rows.append(row)
    sheet = Image.new("RGB", (960, 264*len(contact_sheet_rows)))
    for i, row in enumerate(contact_sheet_rows):
        sheet.paste(row, (0, i*264))
    path = SCRATCH/"decoded-contact-sheet.png"
    sheet.save(path)
    result["contact_sheet"] = {"path": str(path.relative_to(REPO)), "sha256": sha(path)}
    result["native_GUI_playback_exercised"] = False
    return result


def bindings():
    tracked = [
        p for p in git("diff", "--name-only", BASE, HEAD).splitlines()
        if (REPO/p).is_file()
    ]
    return {
        "reviewer": "Fresh independent Simulation Reviewer, general-purpose invocation; not implementation author",
        "base_commit": git("rev-parse", BASE), "reviewed_head": HEAD,
        "actual_head_at_execution": git("rev-parse", "HEAD"),
        "implementation_source_commit": IMPLEMENTATION,
        "branch": git("branch", "--show-current"),
        "reviewer_witness_sha256": sha(__file__),
        "primary_sources_retrieved_2026_09_05_sha256": PRIMARY_SOURCES,
        "tracked_change_set_file_sha256": {p: sha(REPO/p) for p in tracked},
        "installed_environment": {
            "python": platform.python_version(), "platform": platform.platform(),
            **{name: importlib.metadata.version(name)
               for name in ("mujoco", "numpy", "matplotlib", "pillow")},
        },
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--bundle", type=Path, default=BUNDLE)
    args = parser.parse_args()
    SCRATCH.mkdir(parents=True, exist_ok=True)
    before = bindings()
    assert before["actual_head_at_execution"] == HEAD
    implementation_diff = git("diff", "--name-only", IMPLEMENTATION, HEAD, "--",
                              "simulation/cube_sim", "simulation/models", "simulation/intake")
    assert not implementation_diff
    report = {
        "schema": "independent-simulation-review-witness-r1-v1",
        "started_utc": datetime.now(timezone.utc).isoformat(),
        "bindings": before, "tolerances_are_numerical_not_physical": True,
    }
    for name, function in (
        ("frozen_source_and_mass", lambda: frozen_intake(args.bundle)),
        ("closed_form_mechanics", mechanics), ("free_space_invariants", free_space),
        ("archived_artifacts", artifact_checks), ("representative_repeats", representative_repeats),
        ("controller", controller_checks), ("contact_energy_diagnostics", contact_energy),
        ("invalidation", invalidation), ("media", media),
    ):
        print(f"R1 witness: {name}", flush=True)
        report[name] = function()
    after = bindings()
    assert before["tracked_change_set_file_sha256"] == after["tracked_change_set_file_sha256"]
    assert before["actual_head_at_execution"] == after["actual_head_at_execution"]
    report["tracked_reviewed_inputs_and_outputs_unchanged"] = True
    report["completed_utc"] = datetime.now(timezone.utc).isoformat()
    report["witness_assertions_completed"] = True
    output_json(HERE/"witness.json", report)
    print("R1 independent witness assertions completed; simulation/reviews/r1/witness.json")


if __name__ == "__main__":
    main()
