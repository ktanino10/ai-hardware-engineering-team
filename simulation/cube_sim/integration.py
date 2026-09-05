"""Diagnostic quadrature at the engine's actual integration states.

MuJoCo 3.12.0 RK4 skips intermediate sensors, not the control callback:
https://github.com/google-deepmind/mujoco/blob/3.12.0/src/engine/engine_forward.c
"""

import mujoco
import numpy as np


def quadrature_method(integrator):
    return ("RK4_STAGE_REEVALUATION_1_2_2_1"
            if integrator == "RK4"
            else "ENDPOINT_TRAPEZOID_APPROXIMATION")


def advance(model, data, probe, rates):
    if mujoco.get_mjcb_control() is not None:
        raise RuntimeError("Simulation owns its control loop; an existing native control callback would alter it.")
    if model.opt.integrator != mujoco.mjtIntegrator.mjINT_RK4:
        before = rates(data)
        mujoco.mj_step(model, data)
        mujoco.mj_forward(model, data)
        return .5 * model.opt.timestep * (before + rates(data))
    states = []

    def capture(_model, current):
        states.append((current.qpos.copy(), current.qvel.copy(), current.ctrl.copy(),
                       current.time, current.qacc_warmstart.copy()))

    mujoco.set_mjcb_control(capture)
    try:
        mujoco.mj_step(model, data)
    finally:
        mujoco.set_mjcb_control(None)
    if len(states) != 4:
        raise RuntimeError(f"Expected four documented RK4 evaluations, got {len(states)}.")
    mujoco.mj_forward(model, data)
    evaluations = []
    for qpos, qvel, ctrl, timestamp, warmstart in states:
        probe.qpos[:], probe.qvel[:], probe.ctrl[:] = qpos, qvel, ctrl
        probe.time = timestamp
        probe.qacc_warmstart[:] = warmstart
        mujoco.mj_forward(model, probe)
        if any(warning.number for warning in probe.warning):
            raise RuntimeError("Numerical warning in the independent diagnostic-state reevaluation.")
        evaluations.append(rates(probe))
    if not np.all(np.isfinite(evaluations)):
        raise FloatingPointError("Non-finite diagnostic rate in an RK4 stage.")
    return model.opt.timestep * (np.array([1, 2, 2, 1]) @ np.asarray(evaluations)) / 6
