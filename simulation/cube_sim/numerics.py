"""Small deterministic numerical witnesses; no parameter optimization."""

import copy
import mujoco
import numpy as np

from .intake import derive_proxy
from .model import ROOT, load_config
from .runner import sha256, simulate, summary, write_json
from .scenarios import scenarios


def collect():
    rows = []
    for case, config in (("reference", load_config()), ("rev5-partial-proxy", derive_proxy())):
        for dt, solver, iterations in ((.002, "Newton", 50), (.001, "Newton", 50),
                                       (.0005, "Newton", 100), (.002, "CG", 100)):
            config = copy.deepcopy(config)
            config["integration"].update(timestep_s=dt, solver=solver, iterations=iterations)
            for name in ("rest", "fall", "three-wheel", "edge-balance", "vertex-balance",
                         "face-to-vertex-attempt"):
                scenario = scenarios()[name]
                values, _ = simulate(config, scenario)
                residual = (values["energy"].sum(axis=1) - values["energy"][0].sum()
                            - values["work"].sum(axis=1))
                rows.append({
                    "case": case, "dt_s": dt, "solver": solver, "iterations": iterations,
                    "scenario": name, "summary": summary(values, scenario, config),
                    "max_linear_momentum_kg_m_s": float(np.linalg.norm(values["linear_momentum"], axis=1).max()),
                    "max_angular_momentum_nms": float(np.linalg.norm(values["angular_momentum"], axis=1).max()),
                    "max_abs_energy_work_residual_j": float(abs(residual).max()),
                    "final_qpos": values["qpos"][-1].tolist(),
                    "final_normal_force_n": float(values["contact"][-1, 1]),
                    "max_sampled_rigid_energy_j": float(values["energy"].sum(axis=1).max()),
                    "initial_rigid_energy_j": float(values["energy"][0].sum()),
                })
    return {
        "state": "NUMERICAL_WITNESSES_NOT_PHYSICAL_QUALIFICATION", "mujoco": mujoco.__version__,
        "reference_input_sha256": sha256(ROOT / "models/reference.json"),
        "intake_sha256": sha256(ROOT / "intake/rev5-v1.json"),
        "code": {str(p.relative_to(ROOT.parent)): sha256(p) for p in sorted((ROOT / "cube_sim").glob("*.py"))},
        "sampling": "Metrics at 100 Hz; unobserved inter-sample impact maxima are not bounded.",
        "rows": rows,
    }


def write_witnesses(destination):
    if destination.exists():
        raise FileExistsError("Do not overwrite versioned numerical witnesses.")
    write_json(destination, collect())
