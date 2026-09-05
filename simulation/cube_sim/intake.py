"""Decompose a frozen locked tensor using common-origin moments, not CG tensors."""

import copy
import json
from pathlib import Path

import numpy as np

from .model import ROOT, inertia_matrix, load_config, validate_config
from .runner import sha256, write_json

INTAKE = ROOT / "intake/rev5-v1.json"


def parallel_axis(vector):
    vector = np.asarray(vector)
    return (vector @ vector) * np.eye(3) - np.outer(vector, vector)


def derive_proxy(path=INTAKE):
    path = Path(path)
    intake = json.loads(path.read_text(encoding="utf-8"))
    locked = intake["locked_partial"]
    total_mass = locked["mass_kg"]
    total_com = np.asarray(locked["com_m"])
    origin_tensor = inertia_matrix(locked["inertia_kg_m2"]) + total_mass * parallel_axis(total_com)
    first_moment = total_mass * total_com
    wheel_source = intake["wheel_definition"]
    wheels = []
    for i, axis in enumerate(np.eye(3)):
        mass, radius, thickness = (wheel_source[key] for key in ("mass_kg", "radius_m", "thickness_m"))
        moments = np.full(3, mass * (3 * radius**2 + thickness**2) / 12)
        moments[i] = mass * radius**2 / 2
        centre = wheel_source["axial_center_m"] * axis
        wheels.append({"name": "xyz"[i], "axis": axis.tolist(), "center_m": centre.tolist(),
                       "mass_kg": mass, "radius_m": radius, "thickness_m": thickness,
                       "inertia_kg_m2": moments.tolist()})
        total_mass -= mass
        first_moment -= mass * centre
        origin_tensor -= np.diag(moments) + mass * parallel_axis(centre)
    chassis_com = first_moment / total_mass
    chassis_tensor = origin_tensor - total_mass * parallel_axis(chassis_com)
    config = copy.deepcopy(load_config())
    config.update(case_id="rev5-partial-solid-cad-proxy-v1", classification="WIP_DESIGN_PROXY",
                  description="Partial solid-CAD moment proxy + assumed actuator/contact, NOT the complete Rev5 cube.")
    config["body"] = {"side_m": intake["cube_side_m"], "mass_kg": total_mass,
                      "com_m": chassis_com.tolist(), "inertia_kg_m2": chassis_tensor.tolist()}
    config["wheels"] = wheels
    config["provenance"] = {
        "status": "DERIVED_FROM_FROZEN_WIP_PLUS_EXPLICIT_ASSUMPTIONS",
        "source_snapshot": {"path": str(path.relative_to(ROOT.parent)), "sha256": sha256(path),
                            "upstream_revision": intake["source_revision"],
                            "upstream_sources": intake["upstream_sources"],
                            "upstream_bundle": intake["upstream_bundle"]},
        "decomposition": "Subtract each wheel's mass, first moment and tensor about cube origin; then recenter residual chassis. Motor whole-body surrogates remain locked.",
        "actuation_and_contact": "ASSUMPTION: copy synthetic reference ideal torque limits, cutoff, contact and integrator unchanged; NOT a claimed actual-driver case or outcome fit.",
        "reference_model_sha256": sha256(ROOT / "models/reference.json"),
        "actual_driver_case_status": "BLOCKED_UNKNOWN_TORQUE_SPEED_LATENCY_CURRENT_SOURCE_PARAMETERS",
        "locked_recomposition": locked,
    }
    config["gravity_m_s2"] = [0, 0, -9.80665]
    config["omissions"] = intake["omissions"] + config["omissions"]
    validate_config(config)
    return config


def write_proxy(destination):
    destination = Path(destination)
    if destination.exists():
        raise FileExistsError("Versioned proxy already exists; compare or create a new model version.")
    write_json(destination, derive_proxy())
