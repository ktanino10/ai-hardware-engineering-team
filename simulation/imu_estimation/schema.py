"""Strict synthetic schema. Missing physical facts are never defaulted."""

import json
import math
from .math3d import cross, dot, norm

UNITS = {"time": "s", "gyro": "rad/s", "accel": "m/s^2", "position": "m"}


class InputError(ValueError):
    pass


def require(test, reason):
    if not test:
        raise InputError(reason)


def keys(value, expected, label):
    require(isinstance(value, dict) and set(value) == set(expected), label)


def number(v, label):
    require(type(v) in (int, float) and math.isfinite(v), label)
    return v


def vector(v, n, label):
    require(isinstance(v, list) and len(v) == n, label)
    for x in v:
        number(x, label)
    return v


def text(v, label):
    require(isinstance(v, str) and bool(v.strip()), label)


def rotation(m):
    require(isinstance(m, list) and len(m) == 3, "invalid_rotation")
    for row in m:
        vector(row, 3, "invalid_rotation")
    require(all(abs(dot(m[i], m[j]) - int(i == j)) <= 1e-12
                for i in range(3) for j in range(3)), "invalid_rotation")
    require(abs(dot(m[0], cross(m[1], m[2])) - 1) <= 1e-12,
            "invalid_rotation")


def validate_config(c):
    keys(c, ["schema", "classification", "frames", "units", "sensors",
             "initialization", "acceleration_mode", "policy"], "config_fields")
    require(type(c["schema"]) is int and c["schema"] == 1, "schema")
    require(c["classification"] == "SYNTHETIC_REFERENCE", "synthetic_only")
    require(c["frames"] == "RH_W_z_up_B_S_R_BS_q_WB_wxyz", "frames")
    require(c["units"] == UNITS, "units")
    require(c["acceleration_mode"] in ("gravity_assumed", "diagnostic_only"),
            "acceleration_mode")
    p = c["policy"]
    keys(p, ["alignment_s", "max_gap_s", "gravity_m_s2", "force_gate_m_s2",
             "direction_gate_rad", "correction_gain_s_inv"], "policy_fields")
    # Deliberately fixed implementation envelope, not a hidden tuning API.
    fixed = dict(alignment_s=1e-8, max_gap_s=0.03, gravity_m_s2=9.80665,
                 force_gate_m_s2=0.3, direction_gate_rad=0.15,
                 correction_gain_s_inv=0.5)
    for k, v in fixed.items():
        number(p[k], "policy_number")
        require(p[k] == v, "unsupported_policy")
    ini = c["initialization"]
    keys(ini, ["method", "q_WB", "gauge"], "initialization_fields")
    require(ini["gauge"] == "relative_yaw_not_absolute", "gauge")
    require(ini["method"] in ("explicit", "gravity_tilt_yaw_zero"), "initialization")
    if ini["method"] == "explicit":
        vector(ini["q_WB"], 4, "initial_quaternion")
        require(abs(norm(ini["q_WB"])-1) <= 1e-12, "initial_quaternion")
    else:
        require(ini["q_WB"] is None and c["acceleration_mode"] == "gravity_assumed",
                "gravity_initialization_requires_assumption")
    require(isinstance(c["sensors"], list) and len(c["sensors"]) == 6, "six_sensors")
    ids = set()
    for s in c["sensors"]:
        keys(s, ["id", "R_BS", "r_B_m", "calibration", "clock"], "sensor_fields")
        text(s["id"], "sensor_id")
        require(s["id"] not in ids, "duplicate_sensor_config")
        ids.add(s["id"])
        rotation(s["R_BS"])
        vector(s["r_B_m"], 3, "lever_arm")
        cal = s["calibration"]
        keys(cal, ["id", "model", "provenance"], "calibration_missing_or_fields")
        text(cal["id"], "calibration_id")
        require(cal["model"] == "already_calibrated_SI_identity" and
                cal["provenance"] == "synthetic_declared", "unsupported_calibration")
        clock = s["clock"]
        keys(clock, ["epoch", "scale", "offset_s", "provenance"], "clock_missing_or_fields")
        text(clock["epoch"], "clock_epoch")
        number(clock["scale"], "clock_scale")
        number(clock["offset_s"], "clock_offset")
        require(clock["scale"] > 0 and clock["provenance"] == "synthetic_exact",
                "unsupported_clock")
    return c


def _pairs(pairs):
    result = {}
    for k, v in pairs:
        require(k not in result, "duplicate_json_key")
        result[k] = v
    return result


def loads(s):
    def reject(v):
        raise InputError("nonfinite_json")
    try:
        return json.loads(s, parse_constant=reject, object_pairs_hook=_pairs)
    except (ValueError, TypeError) as exc:
        raise InputError(str(exc)) from exc


def dumps(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False) + "\n"
