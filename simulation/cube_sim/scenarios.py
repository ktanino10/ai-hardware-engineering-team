"""Small fixed trials, never a search for a successful physical design."""

from dataclasses import asdict, dataclass
import math

import mujoco
import numpy as np
from .braking import Startup


def axis_angle(axis, angle):
    axis = np.asarray(axis, dtype=float)
    return np.r_[math.cos(angle / 2), axis / np.linalg.norm(axis) * math.sin(angle / 2)]


def multiply(left, right):
    result = np.zeros(4)
    mujoco.mju_mulQuat(result, np.asarray(left), np.asarray(right))
    return result


def rotation(quat):
    matrix = np.zeros(9)
    mujoco.mju_quat2Mat(matrix, np.asarray(quat))
    return matrix.reshape(3, 3)


def error_vector(quat, target):
    inverse = np.asarray(quat) * [1, -1, -1, -1]
    error = multiply(inverse, target)
    if error[0] < 0:
        error = -error
    length = np.linalg.norm(error[1:])
    if length < 1e-14:
        return 2 * error[1:]
    return error[1:] * (2 * math.atan2(length, error[0]) / length)


@dataclass(frozen=True)
class Scenario:
    name: str
    description: str
    duration_s: float = 2.0
    contact: bool = True
    gravity: bool = True
    target: tuple = (1.0, 0.0, 0.0, 0.0)
    initial_quat: tuple | None = None
    perturbation_rad: float = 0.0
    initial_clearance_m: float = 0.0
    controller: str = "off"
    pulse_nm: tuple = (0.0, 0.0, 0.0)
    pulse_half_period_s: float = 0.5
    kp_nm_rad: float = 0.08
    kd_nm_s_rad: float = 0.018
    command_delay_s: float = 0.02
    startup: Startup | None = None

    def __post_init__(self):
        if isinstance(self.startup, dict):
            object.__setattr__(self, "startup", Startup(**self.startup))
        if self.startup is not None and not isinstance(self.startup, Startup):
            raise ValueError("Invalid startup program.")
        for quat in (self.target, self.initial_quat):
            if quat is not None and (np.asarray(quat).shape != (4,) or
                                    not np.all(np.isfinite(quat)) or
                                    not np.isclose(np.linalg.norm(quat), 1, atol=1e-12, rtol=0)):
                raise ValueError("Scenario quaternions must be finite unit wxyz values.")
        for value in (self.duration_s, self.pulse_half_period_s):
            if not np.isfinite(value) or value <= 0:
                raise ValueError("Scenario duration and pulse period must be positive.")
        for value in (self.initial_clearance_m, self.command_delay_s, self.kp_nm_rad, self.kd_nm_s_rad):
            if not np.isfinite(value) or value < 0:
                raise ValueError("Scenario clearance, delay and gains must be nonnegative.")
        if not np.isfinite(self.perturbation_rad) or np.asarray(self.pulse_nm).shape != (3,) or not np.all(np.isfinite(self.pulse_nm)):
            raise ValueError("Invalid perturbation/pulse parameters.")
        if self.controller not in {"off", "pulse", "pd", "spin-brake"}:
            raise ValueError("Unknown controller.")
        if (self.controller == "spin-brake") != (self.startup is not None):
            raise ValueError("Spin/brake controller and explicit startup program must appear together.")
        if self.startup and self.duration_s <= self.startup.dense_end_s:
            raise ValueError("Startup trial must include the complete braking observation window.")

    def record(self):
        return asdict(self)


def scenarios():
    edge = tuple(axis_angle([1, 0, 0], math.pi / 4))
    vertex = tuple(axis_angle([1, -1, 0], math.acos(1 / math.sqrt(3))))
    return {
        s.name: s for s in [
            Scenario("rest", "Passive face rest; uncalibrated soft contact."),
            Scenario("fall", "Passive drop; no recovery controller.", initial_clearance_m=0.12,
                     perturbation_rad=0.18),
            Scenario("one-wheel", "Free space X-wheel torque then ideal reverse torque; NOT driver brake.",
                     contact=False, gravity=False, controller="pulse", pulse_nm=(0.006, 0, 0),
                     initial_clearance_m=0.18),
            Scenario("three-wheel", "Free space three orthogonal internal torques then reverse.",
                     contact=False, gravity=False, controller="pulse", pulse_nm=(0.006, -0.004, 0.005),
                     initial_clearance_m=0.18, duration_s=3.0),
            Scenario("edge-balance", "Pre-positioned edge, perturbed 2 deg; NOT face-to-edge transition.",
                     target=edge, perturbation_rad=math.radians(2), controller="pd", duration_s=3.0),
            Scenario("vertex-balance", "Pre-positioned vertex, perturbed 2 deg; NOT a jump/transition.",
                     target=vertex, perturbation_rad=math.radians(2), controller="pd", duration_s=3.0),
            Scenario("face-to-vertex-attempt", "Start on a face; ask for vertex attitude. Falling/saturation is valid.",
                     target=vertex, initial_quat=(1, 0, 0, 0), controller="pd", duration_s=3.0),
        ]
    }


def initialize(model, data, config, scenario):
    quat = np.asarray(scenario.target if scenario.initial_quat is None else scenario.initial_quat)
    quat = multiply(quat, axis_angle([1, 0, 0], scenario.perturbation_rad))
    data.qpos[3:7] = quat
    half = config["body"]["side_m"] / 2
    data.qpos[:3] = [0, 0, half * np.abs(rotation(quat)[2]).sum() + scenario.initial_clearance_m]
    mujoco.mj_forward(model, data)


def startup_scenario(config=None):
    if config is not None:
        return Scenario(**config["scenario"])
    return Scenario("spin-brake", "Rest -> wheel spin -> coast -> independent finite brake; first edge attempt only.",
                    duration_s=10.0, target=tuple(axis_angle([1, 0, 0], math.pi / 4)),
                    initial_quat=(1, 0, 0, 0), controller="spin-brake", startup=Startup())


def command(data, scenario):
    if scenario.controller == "off":
        return np.zeros(3)
    if scenario.controller == "pulse":
        phase = int((data.time + 1e-10) / scenario.pulse_half_period_s)
        return np.asarray(scenario.pulse_nm) * (1 if phase == 0 else -1 if phase == 1 else 0)
    if scenario.controller == "pd":
        # The desired BODY moment has the opposite sign to wheel-joint torque.
        body_torque = (scenario.kp_nm_rad * error_vector(data.qpos[3:7], scenario.target)
                       - scenario.kd_nm_s_rad * data.qvel[3:6])
        return -body_torque
    if scenario.controller == "spin-brake":
        return scenario.startup.requested_motor(data.time, data.qvel[6:])
    raise ValueError(f"Unknown simulation-only controller: {scenario.controller}")
