"""Causal six-IMU gyro consensus plus explicitly assumed-gravity correction.

No file access, truth generator, scorer, or known injected bias input here.
"""

import math
from . import math3d as m
from .schema import InputError, keys, number, require, vector, validate_config, UNITS, dumps


class Estimator:
    def __init__(self, config):
        self.c = validate_config(config)
        self.sensors = {s["id"]: s for s in config["sensors"]}
        self.last = {}
        self.quarantined = set()
        self.time = None
        self.omega = None
        self.q = None
        self.invalid = None

    def _sample(self, row, t, used):
        keys(row, ["id", "seq", "t_local_s", "epoch", "calibration_id",
                   "units", "gyro", "accel"], "sample_fields")
        sid = row["id"]
        require(isinstance(sid, str) and sid in self.sensors, "unknown_sensor")
        require(sid not in used, "duplicate_sensor")
        s = self.sensors[sid]
        if row["epoch"] != s["clock"]["epoch"]:
            self.quarantined.add(sid)
            raise InputError("clock_reset")
        require(sid not in self.quarantined, "clock_quarantined")
        require(row["calibration_id"] == s["calibration"]["id"], "calibration_mismatch")
        require(row["units"] == UNITS, "units")
        require(type(row["seq"]) is int and row["seq"] >= 0, "sequence")
        vector(row["gyro"], 3, "nonfinite_or_malformed_gyro")
        vector(row["accel"], 3, "nonfinite_or_malformed_accel")
        number(row["t_local_s"], "timestamp")
        mapped = row["t_local_s"] * s["clock"]["scale"] + s["clock"]["offset_s"]
        number(mapped, "mapped_timestamp")
        previous = self.last.get(sid)
        require(previous is None or
                (mapped > previous[0] and row["seq"] > previous[1]), "out_of_order")
        tol = self.c["policy"]["alignment_s"]
        require(mapped >= t-tol, "stale")
        require(mapped <= t+tol, "future_sample")
        self.last[sid] = (mapped, row["seq"])
        return sid, m.mv(s["R_BS"], row["gyro"]), m.mv(s["R_BS"], row["accel"])

    def fail(self, reason, t=None):
        if self.invalid is None:
            self.invalid = reason
        return {"t_s": t, "q_WB": None, "status": "invalid",
                "accepted_ids": [], "rejected": [], "reasons": [reason],
                "absolute_yaw_observable": False}

    def _invalid_batch(self, batch, reason):
        """Keep input-time labels and every discarded ID even after latching.

        t_s is the supplied batch time, NOT a claim of restored continuity.
        No vectors from these rows are used.
        """
        t, rows = None, []
        if isinstance(batch, dict):
            candidate = batch.get("t_s")
            if type(candidate) in (int, float):
                try:
                    if math.isfinite(candidate):
                        t = candidate
                except OverflowError:
                    pass
            if isinstance(batch.get("samples"), list):
                rows = batch["samples"]
        result = self.fail(reason, t)
        for row in rows:
            sid = row.get("id") if isinstance(row, dict) else None
            result["rejected"].append({
                "id": sid if isinstance(sid, str) else None,
                "reason": "continuity_invalid:" + reason})
        for sid in self.sensors:
            if not any(r["id"] == sid for r in result["rejected"]):
                result["rejected"].append({"id": sid, "reason": "missing"})
        return result

    def step(self, batch):
        try:
            result = self._step(batch)
            # Extreme but finite JSON numbers can overflow intermediate math.
            # Never serialize NaN/Infinity or publish a success-shaped estimate.
            dumps(result)
            return result
        except (ValueError, ArithmeticError) as exc:
            return self._invalid_batch(batch, "numerical_or_input_failure:" + str(exc))

    def _step(self, batch):
        if self.invalid:
            return self._invalid_batch(batch, "continuity_latched:" + self.invalid)
        try:
            keys(batch, ["t_s", "samples"], "batch_fields")
            t = number(batch["t_s"], "batch_time")
            require(isinstance(batch["samples"], list), "samples_list")
            if self.time is not None:
                require(t > self.time, "batch_time_reset_or_out_of_order")
                require(t-self.time <= self.c["policy"]["max_gap_s"]+1e-12,
                        "integration_gap")
        except InputError as exc:
            return self._invalid_batch(batch, str(exc))
        used, gyro, accel, rejected = [], [], [], []
        for row in batch["samples"]:
            try:
                sid, g, a = self._sample(row, t, used)
            except InputError as exc:
                sid = row.get("id") if isinstance(row, dict) else None
                if not isinstance(sid, str):
                    sid = None
                rejected.append({"id": sid, "reason": str(exc)})
            else:
                used.append(sid)
                gyro.append(g)
                accel.append(a)
        for sid in self.sensors:
            if sid not in used and not any(r["id"] == sid for r in rejected):
                rejected.append({"id": sid, "reason": "missing"})
        if not used:
            out = self.fail("zero_accepted", t)
            out["rejected"] = rejected
            return out
        omega = m.mean(gyro)
        dt = None if self.time is None else t-self.time
        alpha = [0., 0., 0.] if dt is None else m.scale(m.sub(omega, self.omega), 1/dt)
        # f_S = R_BS^T [R_WB^T(a_W - g_W) + alpha_B x r_B
        #                                     + omega_B x (omega_B x r_B)].
        corrected = []
        for sid, force in zip(used, accel):
            r = self.sensors[sid]["r_B_m"]
            rotational = m.add(m.cross(alpha, r), m.cross(omega, m.cross(omega, r)))
            corrected.append(m.sub(force, rotational))
        force = m.mean(corrected)
        reasons = ["relative_yaw_gauge", "gravity_translation_ambiguity"]
        degraded = len(used) < 6 or bool(rejected)
        if dt is None:
            ini = self.c["initialization"]
            if ini["method"] == "explicit":
                self.q = list(ini["q_WB"])
            else:
                # At start alpha is unknown: require effectively zero gyro and
                # a gravity-sized force. This is still a declared static assumption.
                if m.norm(omega) > 0.01 or abs(m.norm(force)-9.80665) > 0.3:
                    return self._invalid_batch(batch, "gravity_initialization_gate")
                self.q = m.tilt_yaw_zero(force)
            status = "initializing"
            reasons.append("alpha_unavailable_first_sample")
        else:
            mid = m.scale(m.add(self.omega, omega), 0.5)
            self.q = m.unit(m.multiply(self.q, m.exp_rot(m.scale(mid, dt))))
            status = "tracking"
        gravity_use = "diagnostic_only"
        if self.c["acceleration_mode"] == "gravity_assumed":
            expected = m.mv(m.transpose(m.matrix(self.q)), [0., 0., 9.80665])
            fn = m.norm(force)
            cosine = m.dot(force, expected)/(fn*9.80665) if fn > 0 else -1
            angle = math.acos(max(-1., min(1., cosine)))
            if abs(fn-9.80665) <= 0.3 and angle <= 0.15:
                gravity_use = "assumed_gravity_not_observed_translation"
                if dt is not None:
                    correction = m.scale(m.cross(m.scale(force, 1/fn),
                                                m.scale(expected, 1/9.80665)), 0.5*dt)
                    self.q = m.unit(m.multiply(self.q, m.exp_rot(correction)))
            else:
                gravity_use = "gated"
                degraded = True
                reasons.append("acceleration_not_usable_as_assumed_gravity")
        else:
            degraded = True
            reasons.append("no_accelerometer_attitude_correction")
        if status != "initializing" and degraded:
            status = "degraded"
        self.time, self.omega = t, omega
        return {"t_s": t, "q_WB": self.q[:], "status": status,
                "accepted_ids": used, "rejected": rejected, "reasons": reasons,
                "absolute_yaw_observable": False,
                "omega_B_rad_s": omega, "alpha_B_rad_s2": alpha if dt else None,
                "common_specific_force_B_m_s2": force,
                "specific_force_spread_m_s2": max(m.norm(m.sub(v, force)) for v in corrected),
                "gyro_spread_rad_s": max(m.norm(m.sub(v, omega)) for v in gyro),
                "acceleration_use": gravity_use}
