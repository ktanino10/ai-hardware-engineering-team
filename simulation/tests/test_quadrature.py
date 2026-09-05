from dataclasses import replace
import unittest

import mujoco
import numpy as np

from cube_sim.model import ROOT, load_config
from cube_sim.runner import simulate, summary
from cube_sim.scenarios import scenarios


class QuadratureTests(unittest.TestCase):
    def test_stage_work_corrects_contact_diagnostic_without_changing_trajectory(self):
        config = load_config(ROOT / "models/rev5-proxy.json")
        scenario = scenarios()["fall"]
        with np.load(ROOT / "evidence/initial-v1/rev5-proxy/fall/trajectory.npz") as archive:
            old = {key: archive[key] for key in archive.files}
        result, _ = simulate(config, scenario)
        for key in old:
            if key != "work":
                np.testing.assert_array_equal(result[key], old[key], err_msg=key)
        self.assertLess(result["peak_energy_residual"][-1], .05)
        self.assertGreater(result["peak_energy_residual"][-1], .001)
        old_residual = old["energy"].sum(axis=1) - old["energy"][0].sum() - old["work"].sum(axis=1)
        self.assertLess(max(abs(result["energy_residual"])), max(abs(old_residual)) / 10)
        report = summary(result, scenario, config)["energy_accounting"]
        self.assertEqual(report["method"], "RK4_STAGE_REEVALUATION_1_2_2_1")
        self.assertFalse(report["physical_energy_heat_impact_qualified"])
        self.assertIsNone(mujoco.get_mjcb_control())

    def test_contact_energy_error_decreases_with_step_refinement(self):
        config = load_config(ROOT / "models/rev5-proxy.json")
        peaks = []
        for dt, ceiling in ((.002, .05), (.001, .011), (.0005, .002)):
            config["integration"]["timestep_s"] = dt
            result, _ = simulate(config, replace(scenarios()["fall"], duration_s=.4))
            peak = result["peak_energy_residual"][-1]
            peaks.append(peak)
            self.assertLess(peak, ceiling)
        self.assertLess(peaks[1], peaks[0] / 2)
        self.assertLess(peaks[2], peaks[1] / 2)

    def test_existing_control_callback_is_not_silently_replaced(self):
        def existing(_model, _data):
            pass
        mujoco.set_mjcb_control(existing)
        try:
            with self.assertRaisesRegex(RuntimeError, "existing native control callback"):
                simulate(load_config(), replace(scenarios()["rest"], duration_s=.01))
            self.assertIs(mujoco.get_mjcb_control(), existing)
        finally:
            mujoco.set_mjcb_control(None)


if __name__ == "__main__":
    unittest.main()
