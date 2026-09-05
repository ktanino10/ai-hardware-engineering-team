"""Simulation-only spin/coast/finite independent brake; no velocity reset."""

import copy
from dataclasses import dataclass
import json
import math
from pathlib import Path

import numpy as np

from .model import ROOT, inertia_matrix, load_config, validate_config

MECHANISM = ROOT / "intake/mechanism-v1.json"
PHASES = ("ordinary trial", "spin-up command", "coast command", "brake command delay",
          "brake torque ramp", "braking", "wheel near rest; no capture")


@dataclass(frozen=True)
class Startup:
    spin_until_s: float = 3.0
    brake_command_s: float = 3.5
    engagement_delay_s: float = .02
    ramp_s: float = .001
    target_rad_s: tuple = (3000 * 2 * math.pi / 60, 0.0, 0.0)
    speed_gain_nm_per_rad_s: float = .0005
    stop_relative_rad_s: float = 1
    dense_start_s: float = 3.48
    dense_end_s: float = 3.60
    dense_period_s: float = .0001

    def __post_init__(self):
        numbers = [value for name, value in vars(self).items() if name != "target_rad_s"]
        if not all(np.isfinite(x) and x > 0 for x in numbers):
            raise ValueError("Startup parameters must be finite positive numbers.")
        target = np.asarray(self.target_rad_s, dtype=float)
        if target.shape != (3,) or not np.all(np.isfinite(target)) or not np.any(target):
            raise ValueError("Specify a finite signed XYZ wheel-speed target with at least one active axis.")
        if not self.spin_until_s < self.brake_command_s:
            raise ValueError("A separate coast interval is required before brake command.")
        if not self.dense_start_s <= self.brake_on_s < self.brake_on_s + self.ramp_s < self.dense_end_s:
            raise ValueError("The dense observation window must include the brake ramp.")

    @property
    def brake_on_s(self):
        return self.brake_command_s + self.engagement_delay_s

    def requested_motor(self, timestamp, relative_speed):
        target = np.asarray(self.target_rad_s)
        effort = self.speed_gain_nm_per_rad_s * (target - relative_speed)
        return effort * (target != 0) if timestamp < self.spin_until_s else np.zeros(3)

    def brake_fraction(self, timestamp):
        return float(np.clip((timestamp - self.brake_on_s) / self.ramp_s, 0, 1))

    def phase(self, timestamp, relative_speed):
        if timestamp < self.spin_until_s:
            return 1
        if timestamp < self.brake_command_s:
            return 2
        if timestamp < self.brake_on_s:
            return 3
        if timestamp < self.brake_on_s + self.ramp_s:
            return 4
        active = np.asarray(self.target_rad_s) != 0
        return 5 if np.any(np.abs(relative_speed[active]) >= self.stop_relative_rad_s) else 6


def derive_startup_config(base_path, *, mechanism_fixture=False):
    from .runner import sha256

    base_path = Path(base_path)
    config = copy.deepcopy(load_config(base_path))
    mechanism = json.loads(MECHANISM.read_text())
    assumptions = mechanism["experiment_assumptions"]
    target = mechanism["target_only_operating_point"]["rpm"] * 2 * math.pi / 60
    if mechanism_fixture:
        config["case_id"] = "synthetic-annular-mechanism-fixture"
        config["classification"] = "SYNTHETIC_REFERENCE"
        config["body"] = {"side_m": .1, "mass_kg": .1, "com_m": [0, 0, 0],
                          "inertia_kg_m2": [.1 * .1**2 / 6] * 3}
        for axis, wheel in enumerate(config["wheels"]):
            mass, outer, inner, thickness = .08, .04, .035, .004
            axial = mass * (outer**2 + inner**2) / 2
            tensor = np.full(3, axial / 2 + mass * thickness**2 / 12)
            tensor[axis] = axial
            wheel.update(mass_kg=mass, radius_m=outer, inner_radius_m=inner, thickness_m=thickness,
                         center_m=(np.eye(3)[axis] * .044).tolist(), inertia_kg_m2=tensor.tolist())
        config["contact"]["sliding_friction"] = 1.2
        config["description"] = "Synthetic 100 mm / 0.34 kg annular-wheel mechanism fixture. NOT Rev5 or a JAXA replica."
        config["provenance"] = {
            "status": "SYNTHETIC_ASSUMPTION", "source_snapshot": None,
            "rationale": "Explicit momentum-sufficient demonstration: 0.1 kg uniform cube plus three 0.08 kg uniform annuli (40/35 mm radii, 4 mm thick). Geometry/mass/friction are mathematical fixture assumptions, not selected hardware.",
            "inertia_formula": "Annulus axial I=m*(Ro^2+Ri^2)/2; transverse I=Iax/2+m*h^2/12.",
        }
    capacity = inertia_matrix(config["wheels"][0]["inertia_kg_m2"])[0, 0] * target / assumptions["nominal_H_over_t_brake_capacity_time_s"]
    config["case_id"] += "-spin-brake-v2"
    config["description"] += " Spin from rest, coast, finite independent dry brake; no capture controller."
    config["integration"]["timestep_s"] = assumptions["integrator_step_s"]
    config["actuation"]["speed_cutoff_rad_s"][0] = target
    config["actuation"]["independent_brake"] = {
        "model": "IDEAL_DRY_HINGE_BRAKE_NOT_ACTUAL_DRIVER",
        "capacity_nm": [capacity, 0, 0],
        "solref": assumptions["brake_constraint_solref"],
        "solimp": assumptions["brake_constraint_solimp"],
        "rationale": "ASSUMPTION capacity = I_axis*target_omega/5 ms; finite torque, not an imposed stop duration.",
    }
    config["provenance"]["mechanism_source"] = {
        "path": str(MECHANISM.relative_to(ROOT.parent)), "sha256": sha256(MECHANISM),
        "repository": mechanism["repository"], "revision": mechanism["revision"],
        "source_files": mechanism["sources"],
    }
    config["provenance"]["base_model"] = {"path": str(base_path.resolve().relative_to(ROOT.parent)),
                                         "sha256": sha256(base_path)}
    config["provenance"]["actuation_and_contact"] = (
        "SYNTHETIC fixture: the base file is a software template only. Body size/mass/inertia, wheel "
        "mass/annular geometry/inertia/centres and floor friction are intentionally different assumptions. "
        "Startup target/cutoff, step and independent brake are also assumptions; no actual hardware is adopted."
        if mechanism_fixture else
        "Startup-only ASSUMPTION overrides: X target/cutoff, integration step and independent dry brake. "
        "Base mass moments and floor law are unchanged; no actual-driver capability is claimed."
    )
    config["omissions"] += [
        "Dedicated ideal dry brake is NOT the selected hardware, motor reverse effort or a DRV10983 command.",
        "3000 rpm is a prior target-only analysis point, not a qualified or safe speed.",
        "Brake delay/ramp/capacity/constraint response are numerical assumptions, not a manufacturer waveform.",
        "Only the first face-to-edge kick is attempted; no forced edge capture or second vertex jump."
    ]
    from .scenarios import startup_scenario
    config["scenario"] = startup_scenario().record()
    validate_config(config)
    return config
