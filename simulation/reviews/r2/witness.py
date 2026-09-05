#!/usr/bin/env python3
"""Bounded independent R2 review. Run with simulation/.venv/bin/python.

No R1/STL re-review, external design uploads, implementation writes, or live
Blender access. All experiment files are under runs/reviewer-r2. Native ROOT
is compiled without JIT; Blender runs only in a separate background process.
"""

import copy
import csv
from dataclasses import replace
from datetime import datetime, timezone
import hashlib
import importlib.metadata
import io
import itertools
import json
import math
import os
from pathlib import Path
import shlex
import shutil
import subprocess
import sys
from unittest.mock import patch
import xml.etree.ElementTree as ET

sys.dont_write_bytecode = True
REPO = Path(__file__).resolve().parents[3]
SIM = REPO/"simulation"
HERE = SIM/"reviews/r2"
SCRATCH = SIM/"runs/reviewer-r2"
EVIDENCE = SIM/"evidence/startup-v3"
BLEND = SIM/"evidence/blender-replay-v4/startup-mechanism-fixture"
ROOT_FILES = SIM/"evidence/root-v3"
HEAD = "08adc390a391acb5ad654be7cd279a14f1e780a4"
PHYSICS = "560c70279c0916068abd9a54b76db4f0f920c990"
FRAMING = "bfb5ffbc7f9ad2878fd52f4ce8544ada54ebc428"
CASES = ("startup-reference", "startup-rev5-proxy", "startup-mechanism-fixture")
BLENDER = "/Applications/Blender.app/Contents/MacOS/Blender"
os.environ["MPLCONFIGDIR"] = str(SCRATCH/"mpl-cache")
os.environ["TMPDIR"] = str(SCRATCH/"native-work")
os.environ["PYTHONDONTWRITEBYTECODE"] = "1"
sys.path.insert(0, str(SIM))

import mujoco
import numpy as np
from PIL import Image, ImageDraw
from cube_sim import integration, model, runner, visualize
from cube_sim.scenarios import Scenario, scenarios, startup_scenario


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def jread(path):
    return json.loads(Path(path).read_text())


def dump(path, obj):
    Path(path).write_text(json.dumps(obj, indent=2, sort_keys=True, allow_nan=False)+"\n")


def git(*args):
    return subprocess.check_output(["git", "--no-pager", *args], cwd=REPO, text=True).strip()


def delta(a, b):
    return float(np.max(np.abs(np.asarray(a)-np.asarray(b))))


def rot(q):
    w, x, y, z = q
    return np.array([[1-2*(y*y+z*z), 2*(x*y-w*z), 2*(x*z+w*y)],
                     [2*(x*y+w*z), 1-2*(x*x+z*z), 2*(y*z-w*x)],
                     [2*(x*z-w*y), 2*(y*z+w*x), 1-2*(x*x+y*y)]])


def inertia(x):
    x = np.asarray(x)
    return np.diag(x) if x.ndim == 1 else x


def pa(r):
    return np.eye(3)*np.dot(r, r)-np.outer(r, r)


def part_list(config):
    return [(config["body"]["mass_kg"], np.array(config["body"]["com_m"]),
             inertia(config["body"]["inertia_kg_m2"]))] + [
        (w["mass_kg"], np.array(w["center_m"]), inertia(w["inertia_kg_m2"]))
        for w in config["wheels"]]


def physical(config, q, v, g):
    parts = part_list(config)
    M = math.fsum(m for m, _, _ in parts)
    c = sum((m*r for m, r, _ in parts), np.zeros(3))/M
    R = rot(q[3:7])
    H, P = np.zeros(3), np.zeros(3)
    E = np.zeros(2)
    for i, (m, r, J) in enumerate(parts):
        vi = v[:3]+R@np.cross(v[3:6], r)
        wi = v[3:6].copy()
        if i:
            wi[i-1] += v[5+i]
        P += m*vi
        H += R@(J@wi)+np.cross(R@(r-c), m*vi)
        E[0] -= m*np.dot(g, q[:3]+R@r)
        E[1] += .5*m*(vi@vi)+.5*wi@J@wi
    return E, P, H


def corner_height(qpos, side):
    corners = np.array(list(itertools.product((-side/2, side/2), repeat=3)))
    return np.array([np.min((corners@rot(q[3:7]).T+q[:3])[:, 2]) for q in qpos])


def intervals(t, mask):
    indices = np.flatnonzero(mask)
    result = []
    if not len(indices):
        return result
    for group in np.split(indices, np.flatnonzero(np.diff(indices) != 1)+1):
        first, last = int(group[0]), int(group[-1])
        result.append({
            "first_s": float(t[first]), "last_s": float(t[last]),
            "observed_span_s": float(t[last]-t[first]), "samples": len(group),
            "previous_nonqualifying_s": float(t[first-1]) if first else None,
            "next_nonqualifying_s": float(t[last+1]) if last+1 < len(t) else None,
        })
    return result


def bindings():
    prefixes = (
        "simulation/cube_sim/", "simulation/blender/", "simulation/root/",
        "simulation/models/startup-", "simulation/intake/mechanism-v1.json",
        "simulation/evidence/startup-v3/", "simulation/evidence/root-v3/",
        "simulation/evidence/blender-replay-v4/", "simulation/tests/test_startup.py",
        "simulation/tests/test_quadrature.py", "simulation/STARTUP.md", "simulation/README.md",
        "simulation/evidence/index.html", "docs/simulation.md",
    )
    paths = [p for p in git("ls-files").splitlines() if p.startswith(prefixes)]
    return {
        "head": HEAD, "actual_head": git("rev-parse", "HEAD"),
        "physics_source": PHYSICS, "blender_framing_source": FRAMING,
        "scope_sha256": {p: sha(REPO/p) for p in paths},
        "r1_preserved_sha256": {p.name: sha(p) for p in sorted((SIM/"reviews/r1").iterdir()) if p.is_file()},
        "reviewer_sources_sha256": {p.name: sha(p) for p in sorted(HERE.iterdir())
                                   if p.suffix in {".py", ".cxx"}},
        "environment": {k: importlib.metadata.version(k) for k in ("mujoco", "numpy", "pillow")},
    }


def sources():
    source = jread(SIM/"intake/mechanism-v1.json")
    checked = {}
    for item in source["sources"]:
        url = f"https://raw.githubusercontent.com/{source['repository']}/{source['revision']}/{item['path']}"
        data = subprocess.check_output(["curl", "-fLsS", "--max-time", "45", url])
        actual = hashlib.sha256(data).hexdigest()
        assert actual == item["sha256"]
        checked[url] = actual
    assert not git("diff", "--name-only", "7c067bd", HEAD, "--", "simulation/reviews/r1")
    return {"secondary_mechanism_sources": checked, "notes_executed": False,
            "old_STL_or_source_bundle_revisited": False, "R1_files_changed": False}


def quadrature_correction():
    r1 = jread(SIM/"reviews/r1/witness.json")
    results = []
    for dt, iters in ((.002, 50), (.001, 50), (.0005, 100)):
        c = model.load_config(SIM/"models/rev5-proxy.json")
        c["integration"].update(timestep_s=dt, iterations=iters)
        values, _ = runner.simulate(c, scenarios()["fall"])
        old = next(r for r in r1["contact_energy_diagnostics"]
                   if r["scenario"] == "fall" and r["solver"] == "Newton" and r["dt_s"] == dt)
        error = abs(values["peak_energy_residual"][-1]-old["all_step_max_rk4_stage_residual_j"])
        assert error < 1e-10
        report = runner.summary(values, scenarios()["fall"], c)["energy_accounting"]
        assert report["method"] == "RK4_STAGE_REEVALUATION_1_2_2_1"
        assert not report["physical_energy_heat_impact_qualified"]
        if dt == .002:
            with np.load(SIM/"evidence/initial-v1/rev5-proxy/fall/trajectory.npz") as a:
                assert all(np.array_equal(a[k], values[k]) for k in a.files if k != "work")
        results.append({"dt_s": dt, "peak_j": report["max_abs_residual_all_steps_j"],
                        "max_grid_j": report["max_abs_residual_recorded_grid_j"],
                        "final_j": report["final_residual_j"], "error_vs_R1_independent_stage_work_j": error})
    m, d, _ = model.build(model.load_config(), contact=False, gravity=False)
    probe = mujoco.MjData(m)
    def present(_m, _d):
        pass
    mujoco.set_mjcb_control(present)
    try:
        try:
            integration.advance(m, d, probe, lambda state: np.zeros(1))
            raise AssertionError("Pre-existing callback was overwritten")
        except RuntimeError:
            assert mujoco.get_mjcb_control() is present
    finally:
        mujoco.set_mjcb_control(None)
    original_step = integration.mujoco.mj_step
    def deliberate_failure(_m, _d):
        raise ValueError("reviewer-injected step exception")
    with patch.object(integration.mujoco, "mj_step", deliberate_failure):
        try:
            integration.advance(m, d, probe, lambda state: np.zeros(1))
        except ValueError:
            assert mujoco.get_mjcb_control() is None
        else:
            raise AssertionError("Missing deliberate exception")
    assert integration.mujoco.mj_step is original_step
    return {"R1_001_stage_correction_matches_independent_R1_values": results,
            "unchanged_2ms_physical_arrays": True,
            "preexisting_callback_rejected_and_preserved": True,
            "callback_removed_after_step_exception": True}


CSV = {
    "time": ["time_s"],
    "qpos": ["x_m", "y_m", "z_m", "qw", "qx", "qy", "qz", "wheel_x_rad", "wheel_y_rad", "wheel_z_rad"],
    "qvel": ["vx_world_m_s", "vy_world_m_s", "vz_world_m_s", "wx_body_rad_s", "wy_body_rad_s",
             "wz_body_rad_s", "wheel_x_relative_rad_s", "wheel_y_relative_rad_s", "wheel_z_relative_rad_s"],
    "contact": ["active_contacts", "normal_force_n", "minimum_contact_distance_m", "max_loaded_point_slip_m_s"],
    "energy": ["potential_j", "kinetic_j"],
    "work": ["motor_work_j", "passive_work_j", "constraint_work_j"],
}
for key, unit in (("command", "nm"), ("delayed", "nm"), ("applied", "nm"), ("saturated", "bool"),
                  ("speed_cutoff", "bool"), ("speed_exceeded", "bool"),
                  ("angular_momentum", "world_nms"), ("linear_momentum", "world_kg_m_s"),
                  ("omega_world", "rad_s"), ("wheel_absolute_axial", "rad_s"), ("attitude_error", "body_rad"),
                  ("brake_limit", "nm"), ("brake_torque", "nm"), ("ground_angular_impulse", "world_nms"),
                  ("momentum_residual", "world_nms"), ("ground_force", "world_n"),
                  ("wheel_relative_axial_momentum", "body_axis_nms")):
    CSV[key] = [f"{key}_{a}_{unit}" for a in "xyz"]
for key, column in (
    ("energy_residual", "energy_work_residual_j"),
    ("peak_energy_residual", "max_abs_energy_work_residual_all_steps_j"),
    ("brake_work", "brake_work_j_subset_of_constraint_work"),
    ("peak_positive_brake_power", "max_positive_brake_power_stage_w"),
    ("phase", "phase_code"), ("minimum_corner_height", "minimum_cube_corner_height_m"),
    ("geometric_contacts", "geometric_contact_count"),
):
    CSV[key] = [column]


def archives():
    result = {}
    for relative, digest in jread(EVIDENCE/"index-manifest.json")["files"].items():
        assert sha(EVIDENCE/relative) == digest
    assert len(jread(EVIDENCE/"numerics.json")["rows"]) == 48
    for name in CASES:
        path = EVIDENCE/name
        manifest, values = visualize.verify_current(path)
        assert manifest["source_revision"] == PHYSICS and not manifest["uncommitted_model_code"]
        c = jread(path/"input.json")
        assert c == jread(SIM/"models"/f"{name}.json")
        scenario = startup_scenario(c)
        assert scenario.duration_s == 10.
        assert np.array_equal(values["qvel"][0], np.zeros(9))
        with (path/"trajectory.csv").open(newline="") as f:
            rows = list(csv.DictReader(f))
        assert len(rows) == 2189
        assert len(rows[0]) == 87
        for key, names in CSV.items():
            observed = np.array([[float(row[col]) for col in names] for row in rows])
            if values[key].ndim == 1:
                observed = observed[:, 0]
            assert np.array_equal(observed, values[key]), (name, key)
        errors = np.zeros(3)
        for q, v, e, P, H in zip(values["qpos"], values["qvel"], values["energy"],
                                 values["linear_momentum"], values["angular_momentum"]):
            ei, pi, hi = physical(c, q, v, np.array(c["gravity_m_s2"]))
            errors = np.maximum(errors, [delta(e, ei), delta(P, pi), delta(H, hi)])
        assert max(errors) < 1e-9
        gap = corner_height(values["qpos"], c["body"]["side_m"])
        assert delta(gap, values["minimum_corner_height"]) < 1e-14
        mask = ((values["geometric_contacts"] == 0) & (values["contact"][:, 1] <= 1e-8) & (gap > .0001))
        events = intervals(values["time"], mask)
        summary = jread(path/"summary.json")
        assert len(events) == len(summary["startup"]["flight_assessment"]["observed_intervals"])
        for own, other in zip(events, summary["startup"]["flight_assessment"]["observed_intervals"]):
            assert own["first_s"] == other["first_observed_s"] and own["last_s"] == other["last_observed_s"]
            assert own["samples"] == other["consecutive_samples"]
        assert abs(summary["startup"]["floor_contact_work_on_assembly_j"]
                   -(values["work"][-1, 2]-values["brake_work"][-1])) < 1e-12
        residual = values["energy"].sum(axis=1)-sum(values["energy"][0])-values["work"].sum(axis=1)
        assert delta(residual, values["energy_residual"]) < 1e-12
        target = np.array(scenario.startup.target_rad_s)
        cmd = scenario.startup.speed_gain_nm_per_rad_s*(target-values["qvel"][:, 6:])
        cmd *= (target != 0)
        cmd[values["time"] >= scenario.startup.spin_until_s] = 0
        assert delta(cmd, values["command"]) < 1e-13
        step_time = np.rint(values["time"]/c["integration"]["timestep_s"])*c["integration"]["timestep_s"]
        expected_limit = (np.clip((step_time-scenario.startup.brake_on_s)/scenario.startup.ramp_s, 0, 1)[:, None]
                          *np.array(c["actuation"]["independent_brake"]["capacity_nm"]))
        assert delta(expected_limit, values["brake_limit"]) < 1e-12
        assert np.all(abs(values["brake_torque"]) <= expected_limit+1e-9)
        fresh, xml = runner.simulate(c, scenario)
        assert all(np.array_equal(fresh[k], values[k]) for k in values), name
        assert xml == (path/"model.xml").read_text()
        if name != "startup-mechanism-fixture":
            base = jread(SIM/"models"/("reference.json" if name == "startup-reference" else "rev5-proxy.json"))
            assert all(c[k] == base[k] for k in ("body", "wheels", "contact"))
        else:
            for axis, w in enumerate(c["wheels"]):
                axial = w["mass_kg"]*(w["radius_m"]**2+w["inner_radius_m"]**2)/2
                moments = np.full(3, axial/2+w["mass_kg"]*w["thickness_m"]**2/12)
                moments[axis] = axial
                assert delta(moments, w["inertia_kg_m2"]) < 1e-18
        result[name] = {
            "manifest_sha256": sha(path/"manifest.json"), "all_output_sha256": manifest["outputs"],
            "all_87_csv_columns_exact": True, "all_fresh_arrays_and_xml_exact": True,
            "independent_energy_P_H_max_errors": errors.tolist(),
            "gap_intervals": events, "max_lowest_corner_m": float(max(gap)),
            "energy_accounting": summary["energy_accounting"], "startup": summary["startup"],
            "outcome": summary["outcome"], "max_H_minus_ground_impulse_nms": summary["max_angular_momentum_balance_residual_nms"],
            "wrongly_double_counting_brake_work_final_error_j": float(residual[-1]-values["brake_work"][-1]),
        }
    return result


def brake_force_path():
    c = model.load_config(SIM/"models/startup-reference.json")
    m, d, _ = model.build(c, contact=False, gravity=False)
    d.qpos[3:7] = [math.cos(.37), 0, 0, math.sin(.37)]
    d.qvel[6:] = [40, -30, 20]
    capacities = np.array([.012, .010, .008])
    m.dof_frictionloss[6:] = capacities
    mujoco.mj_forward(m, d)
    assert not np.any(m.dof_frictionloss[:6]) and m.neq == 0
    assert not np.any(d.xfrc_applied) and not np.any(d.qfrc_applied)
    parts = part_list(c)
    mass = sum(p[0] for p in parts)
    center = sum((mass*r for mass, r, _ in parts), np.zeros(3))/mass
    J = sum((j+mass*pa(r-center) for mass, r, j in parts), np.zeros((3, 3)))
    D = np.array([inertia(w["inertia_kg_m2"])[axis, axis] for axis, w in enumerate(c["wheels"])])
    tau = -np.sign(d.qvel[6:])*capacities
    predicted = np.linalg.solve(J-np.diag(D), -tau)
    assert delta(d.qfrc_constraint[6:], tau) < 1e-12
    body_error = delta(d.qacc[3:6], predicted)
    wheel_error = delta(d.qacc[6:], tau/D-predicted)
    assert max(body_error, wheel_error) < 1e-9
    initial_E, initial_P, initial_H = physical(c, d.qpos, d.qvel, np.zeros(3))
    maximum = np.zeros(2)
    for _ in range(1500):
        mujoco.mj_step(m, d)
        mujoco.mj_forward(m, d)
        _, P, H = physical(c, d.qpos, d.qvel, np.zeros(3))
        maximum = np.maximum(maximum, [np.linalg.norm(P-initial_P), np.linalg.norm(H-initial_H)])
        assert d.ncon == 0 and not np.any(d.qfrc_constraint[:6])
    assert max(maximum) < 1e-8
    return {"diagnostic_only_initial_spins_not_startup_initialization": [40, -30, 20],
            "brake_capacities_nm": capacities.tolist(), "signed_internal_efforts_nm": tau.tolist(),
            "predicted_body_alpha_rad_s2": predicted.tolist(),
            "body_acceleration_error_rad_s2": body_error, "wheel_acceleration_error_rad_s2": wheel_error,
            "free_space_max_P_H_drifts": maximum.tolist(), "root_constraint_force_and_torque_zero": True}


def contact_sensitivity():
    c0 = model.load_config(SIM/"models/startup-mechanism-fixture.json")
    initial_scenario = replace(startup_scenario(c0), duration_s=4.1)
    original_build = runner.build
    rows = []
    for label, dt, solver, iterations_count, margin, envelope in (
        ("baseline", .0001, "Newton", 50, 0., 0.),
        ("half_step", .00005, "Newton", 50, 0., 0.),
        ("newton_100", .0001, "Newton", 100, 0., 0.),
        ("cg_100", .0001, "CG", 100, 0., 0.),
        ("margin_0.1mm", .0001, "Newton", 50, .0001, 0.),
        ("margin_0.2mm", .0001, "Newton", 50, .0002, 0.),
        ("box_envelope_plus_0.2mm", .0001, "Newton", 50, 0., .0002),
    ):
        c = copy.deepcopy(c0)
        c["integration"].update(timestep_s=dt, solver=solver, iterations=iterations_count)
        def modified_build(config, **kwargs):
            m, d, xml = original_build(config, **kwargs)
            if margin or envelope:
                tree = ET.fromstring(xml)
                geom = tree.find(".//geom[@name='cube_collision']")
                geom.set("margin", str(margin))
                geom.set("size", " ".join([str(c["body"]["side_m"]/2+envelope)]*3))
                xml = ET.tostring(tree, encoding="unicode")
                m = mujoco.MjModel.from_xml_string(xml)
                d = mujoco.MjData(m)
                mujoco.mj_forward(m, d)
            return m, d, xml
        with patch.object(runner, "build", modified_build):
            values, _ = runner.simulate(c, initial_scenario)
        gap = corner_height(values["qpos"], c["body"]["side_m"]+2*envelope)
        mask = (values["geometric_contacts"] == 0) & (values["contact"][:, 1] <= 1e-8) & (gap > .0001)
        q = values["qpos"][:, 3:7]
        rotations = 2*np.arccos(np.clip(abs(q[:, 0]), 0, 1))
        row = {"case": label, "dt_s": dt, "solver": solver, "iterations": iterations_count,
               "contact_margin_m": margin, "box_expansion_per_side_m": envelope,
               "max_gap_m_for_tested_box": float(max(gap)), "gap_intervals": intervals(values["time"], mask),
               "max_penetration_m": float(-values["contact"][:, 2].min()),
               "max_rotation_deg": float(np.degrees(max(rotations))),
               "all_step_energy_residual_j": float(values["peak_energy_residual"][-1])}
        if label == "baseline":
            base = values
            row["nominal_minus_0.2mm_uncertainty_max_m"] = float(max(gap)-.0002)
            row["nominal_minus_2mm_visual_capsule_max_m"] = float(max(gap)-.002)
        if label == "half_step":
            thinned_scenario = replace(initial_scenario,
                                       startup=replace(initial_scenario.startup, dense_period_s=.001))
            thinned, _ = runner.simulate(c, thinned_scenario)
            assert np.array_equal(values["qpos"][-1], thinned["qpos"][-1])
            assert values["peak_energy_residual"][-1] == thinned["peak_energy_residual"][-1]
            row["output_thinning_does_not_change_final_state_or_work"] = True
            row["dense_rows_vs_thinned_rows"] = [len(values["time"]), len(thinned["time"])]
        rows.append(row)
        print("R2 sensitivity:", label, row["max_gap_m_for_tested_box"], flush=True)
    return rows


def native_root():
    build = SCRATCH/"root"
    build.mkdir(exist_ok=True)
    flags = shlex.split(subprocess.check_output(["root-config", "--cflags", "--libs"], text=True))
    for binary, source in (("inspect-root", HERE/"inspect_root.cxx"), ("author-export", SIM/"root/export.cxx")):
        subprocess.run(["c++", str(source), *flags, "-o", str(build/binary)], check=True)
    result = {}
    for name in CASES:
        run = EVIDENCE/name
        directory = ROOT_FILES/name
        manifest = jread(directory/"manifest.json")
        assert manifest["source_csv_sha256"] == sha(run/"trajectory.csv")
        assert manifest["source_manifest_sha256"] == sha(run/"manifest.json")
        assert manifest["cpp_sha256"] == sha(SIM/"root/export.cxx")
        for path, digest in manifest["files"].items():
            assert sha(directory/path) == digest
        with (run/"trajectory.csv").open(newline="") as f:
            reader = csv.reader(f)
            columns = next(reader)
            expected = np.array([[float(x) for x in row] for row in reader])
        t, speed = expected[:, columns.index("time_s")], expected[:, columns.index("wheel_x_relative_rad_s")]
        weights = np.r_[np.diff(t), 0.]
        fresh = build/name
        if fresh.exists():
            shutil.rmtree(fresh)
        fresh.mkdir()
        exported = subprocess.run([str(build/"author-export"), str(run/"trajectory.csv"),
                                   str(fresh/"trajectory.root"), str(fresh/"summary.json")],
                                  capture_output=True, text=True)
        (fresh/"export.log").write_text(exported.stdout+exported.stderr)
        exported.check_returncode()
        comparisons = []
        for label, root in (("delivered", directory/"trajectory.root"), ("reexported", fresh/"trajectory.root")):
            read = subprocess.run([str(build/"inspect-root"), str(root)], capture_output=True, text=True)
            (fresh/f"{label}-read.log").write_text(read.stderr)
            read.check_returncode()
            data = json.loads(read.stdout)
            trajectory = data["trajectory"]
            assert trajectory["columns"] == columns+["sample_dt_s"]
            actual = np.array(trajectory["values"])
            assert np.array_equal(actual[:, :-1], expected)
            assert np.array_equal(actual[:, -1], weights)
            bins = data["time_weighted_wheel_x_rpm"]
            assert bins["columns"] == ["lower_rpm", "upper_rpm", "simulated_seconds"]
            actual_bins = np.array(bins["values"])
            rpm = speed*60/(2*np.pi)
            extent = max(1., float(max(abs(rpm))))*1.05+1
            edges = -extent+np.arange(81)*(2*extent/80)
            durations = np.zeros(80)
            for value, weight in zip(rpm, weights):
                durations[int((value+extent)/(2*extent/80))] += weight
            assert delta(actual_bins[:, 0], edges[:-1]) < 1e-10
            assert delta(actual_bins[:, 1], edges[1:]) < 1e-10
            assert np.array_equal(actual_bins[:, 2], durations)
            comparisons.append({"file": label, "root_sha256": sha(root), "exact_all_values": True,
                                "exact_time_weights_and_bin_durations": True,
                                "native_stderr_diagnostics_present": bool(read.stderr)})
        summary = jread(directory/"summary.json")
        weighted_mean = float(np.dot(rpm, weights)/sum(weights))
        assert abs(weighted_mean-summary["time_weighted_mean_x_rpm"]) < 1e-9
        result[name] = {"source_rows": len(expected), "source_columns": len(columns),
                        "native_columns": actual.shape[1], "weighted_seconds": float(sum(weights)),
                        "time_weighted_mean_rpm": weighted_mean, "naive_row_mean_rpm": float(np.mean(rpm)),
                        "brake_window_weight_seconds": float(sum(weights[(t >= 3.48)&(t < 3.6)])),
                        "files_checked": comparisons,
                        "native_manifest_sha256": sha(directory/"manifest.json")}
    result["runtime"] = {"root_config_version": subprocess.check_output(["root-config", "--version"], text=True).strip(),
                          "jit_pyroot_graphics_used": False, "global_installation_changed": False}
    return result


def decode_selected(path, frames):
    expression = "+".join(f"eq(n\\,{i})" for i in frames)
    data = subprocess.check_output(["ffmpeg", "-v", "error", "-i", str(path), "-vf", "select="+expression,
                                    "-fps_mode", "passthrough", "-f", "rawvideo", "-pix_fmt", "rgb24", "-"])
    return np.frombuffer(data, np.uint8).reshape(len(frames), 720, 960, 3)


def movie_info(path):
    p = subprocess.run(["ffmpeg", "-v", "error", "-i", str(path), "-f", "null", "-"],
                       capture_output=True)
    p.check_returncode()
    data = json.loads(subprocess.check_output([
        "ffprobe", "-v", "error", "-count_frames", "-select_streams", "v:0",
        "-show_entries", "stream=codec_name,width,height,r_frame_rate,nb_read_frames,duration", "-of", "json", str(path)
    ]))["streams"][0]
    assert (int(data["nb_read_frames"]), data["r_frame_rate"], float(data["duration"])) == (250, "25/1", 10.)
    return data


def movies_and_plots():
    result, sheet_rows = {}, []
    for name in CASES:
        path = EVIDENCE/name
        config = jread(path/"input.json")
        _, values = visualize.read_run(path)
        m = mujoco.MjModel.from_xml_path(str(path/"model.xml"))
        d = mujoco.MjData(m)
        with mujoco.Renderer(m, height=520, width=960) as renderer:
            for stem, mapping_name, start, step in (
                ("motion", "video-frames.csv", 0., .04),
                ("brake-detail", "brake-detail-frames.csv", 3.48, .0004),
            ):
                info = movie_info(path/f"{stem}.mp4")
                with (path/mapping_name).open(newline="") as f:
                    mapping = list(csv.DictReader(f))
                assert len(mapping) == 250
                for i, row in enumerate(mapping):
                    sample = int(row["sample_index"])
                    assert int(row["video_frame"]) == i
                    assert abs(float(row["time_s"])-(start+i*step)) < 1e-8
                    assert values["time"][sample] == float(row["time_s"])
                    assert hashlib.sha256(values["qpos"][sample].astype("<f8").tobytes()).hexdigest() == row["qpos_float64_le_sha256"]
                frames = [0, 100, 125, 249] if stem == "brake-detail" else [0, 88, 89, 90, 249]
                images = decode_selected(path/f"{stem}.mp4", frames)
                errors = []
                contact = Image.new("RGB", (960, 264))
                ImageDraw.Draw(contact).text((6, 3), f"{name}/{stem} — selected decoded frames", fill="white")
                for i, frame in enumerate(frames):
                    sample = int(mapping[frame]["sample_index"])
                    d.qpos[:] = values["qpos"][sample]
                    d.qvel[:] = values["qvel"][sample]
                    d.ctrl[:] = values["applied"][sample]
                    m.dof_frictionloss[6:] = values["brake_limit"][sample]
                    d.time = values["time"][sample]
                    mujoco.mj_forward(m, d)
                    cam = mujoco.MjvCamera()
                    cam.lookat[:] = d.qpos[:3]
                    cam.lookat[2] = values["qpos"][0, 2]
                    cam.distance = max(.4, config["body"]["side_m"]*3.5)
                    cam.azimuth, cam.elevation = 135, -24
                    renderer.update_scene(d, camera=cam)
                    error = float(abs(renderer.render().astype(float)-images[i, 100:620]).mean())
                    assert error < 2
                    errors.append({"frame": frame, "time_s": float(d.time), "scene_rgb_mae": error})
                for column, index in enumerate((0, 2, len(frames)-1)):
                    contact.paste(Image.fromarray(images[index]).resize((320, 240)), (column*320, 24))
                sheet_rows.append(contact)
                result[f"{name}/{stem}"] = {"sha256": sha(path/f"{stem}.mp4"), "decode": info,
                                            "exact_map_hashes": True, "scene_comparisons": errors,
                                            "simulated_span_half_open_s": [start, start+250*step],
                                            "playback_duration_s": 10.}
        copied = SCRATCH/"plots"/name
        if copied.exists():
            shutil.rmtree(copied)
        shutil.copytree(path, copied)
        visualize.plot(copied)
        visualize.plot_startup(copied)
        assert sha(path/"plots.png") == sha(copied/"plots.png")
        assert sha(path/"startup-plots.png") == sha(copied/"startup-plots.png")
        shutil.rmtree(copied)
    sheet = Image.new("RGB", (960, len(sheet_rows)*264))
    for i, row in enumerate(sheet_rows):
        sheet.paste(row, (0, i*264))
    sheet.save(SCRATCH/"mujoco-decoded-contact-sheet.png")
    result["all_six_plots_reproduced_exactly"] = True
    return result


def native_blender():
    destination = SCRATCH/"blender"
    command = [BLENDER, "--background", "--factory-startup", "--threads", "2",
               "--python-exit-code", "1", "--python", str(HERE/"inspect_blend.py"), "--",
               "--blend", str(BLEND/"replay.blend"), "--run", str(EVIDENCE/CASES[2]),
               "--output", str(destination), "--author-checker", str(SIM/"blender/check_replay.py"), "--all-frames"]
    native = subprocess.run(command, capture_output=True, text=True)
    (SCRATCH/"blender-native.log").write_text(native.stdout+native.stderr)
    native.check_returncode()
    result = jread(destination/"native-witness.json")
    manifest = jread(BLEND/"manifest.json")
    for path, digest in manifest["files"].items():
        assert sha(BLEND/path) == digest
    info = movie_info(BLEND/"blender-motion.mp4")
    selected = [0, 87, 88, 89, 90, 100, 249]
    decoded = decode_selected(BLEND/"blender-motion.mp4", selected)
    comparisons = []
    sheet = Image.new("RGB", (960, 504))
    for i, frame in enumerate(selected):
        raw = np.asarray(Image.open(destination/"frames"/f"frame_{frame+1:04}.png").convert("RGB"))
        error = float(abs(raw.astype(float)-decoded[i, 100:620]).mean())
        assert error < 2
        comparisons.append({"frame": frame, "scene_rgb_mae": error})
        if i < 6:
            sheet.paste(Image.fromarray(decoded[i]).resize((320, 240)), ((i % 3)*320, (i//3)*252+12))
    sheet.save(SCRATCH/"blender-decoded-contact-sheet.png")
    result["video"] = {"decode": info, "comparisons": comparisons,
                       "sha256": sha(BLEND/"blender-motion.mp4")}

    bad_source = SCRATCH/"encoder-negative/source"
    bad_render = SCRATCH/"encoder-negative/render"
    if bad_source.parent.exists():
        shutil.rmtree(bad_source.parent)
    shutil.copytree(EVIDENCE/CASES[2], bad_source)
    bad_render.mkdir()
    shutil.copyfile(BLEND/"provenance.json", bad_render/"provenance.json")
    shutil.copytree(destination/"frames", bad_render/"frames")
    csv_path = bad_source/"trajectory.csv"
    original_sha = sha(csv_path)
    with csv_path.open(newline="") as f:
        reader = csv.DictReader(f)
        names = reader.fieldnames
        rows = list(reader)
    for row in rows:
        row["wheel_x_relative_rad_s"] = "12345"
    with csv_path.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=names)
        writer.writeheader()
        writer.writerows(rows)
    try:
        visualize.verify_current(bad_source)
        raise AssertionError("Corrupted source unexpectedly passed core verifier")
    except ValueError:
        pass
    encoded = subprocess.run([
        str(SIM/".venv/bin/python"), str(SIM/"blender/encode_replay.py"),
        "--run", str(bad_source), "--render", str(bad_render),
    ], capture_output=True, text=True)
    (SCRATCH/"encoder-negative/encoder.log").write_text(encoded.stdout+encoded.stderr)
    result["negative_changed_source_csv"] = {
        "original_csv_sha256": original_sha, "mutated_csv_sha256": sha(csv_path),
        "core_verifier_rejected": True, "encoder_returncode": encoded.returncode,
        "encoder_accepted_changed_csv": encoded.returncode == 0,
        "injected_wheel_x_label_rad_s": 12345,
        "note": "Negative-test movie uses correct source poses but intentionally false speed labels; NOT deliverable evidence.",
    }
    if encoded.returncode == 0:
        bad_manifest = jread(bad_render/"manifest.json")
        result["negative_changed_source_csv"]["still_claimed_original_manifest_sha256"] = bad_manifest["source_manifest_sha256"]
    return result


def main():
    SCRATCH.mkdir(parents=True, exist_ok=True)
    (SCRATCH/"native-work").mkdir(exist_ok=True)
    before = bindings()
    assert before["actual_head"] == HEAD
    result = {"schema": "independent-r2-witness-v1", "started_utc": datetime.now(timezone.utc).isoformat(),
              "bindings": before, "witness_complete": False}
    for name, fn in (("source_scope", sources), ("quadrature_correction", quadrature_correction),
                     ("startup_archives", archives), ("brake_force_path", brake_force_path),
                     ("contact_sensitivity", contact_sensitivity), ("root", native_root),
                     ("mujoco_media", movies_and_plots), ("blender", native_blender)):
        print("R2 witness:", name, flush=True)
        result[name] = fn()
        dump(HERE/"witness.json", result)
    after = bindings()
    assert before == after
    result["reviewed_inputs_outputs_and_R1_unchanged"] = True
    result["witness_complete"] = True
    result["completed_utc"] = datetime.now(timezone.utc).isoformat()
    dump(HERE/"witness.json", result)
    print("R2 independent witness completed; findings are assessed separately in review.md.")


if __name__ == "__main__":
    main()
