from dataclasses import replace
import unittest

import numpy as np

from cube_sim.model import load_config
from cube_sim.numerics import collect
from cube_sim.runner import simulate
from cube_sim.scenarios import Scenario, scenarios


class ScenarioTests(unittest.TestCase):
    def test_delay_torque_saturation_and_speed_cutoff_are_visible_not_velocity_clamps(self):
        config = load_config()
        config["actuation"]["speed_cutoff_rad_s"] = [.5, .5, .5]
        scenario = Scenario("limit", "Limit witness", duration_s=.2, gravity=False, contact=False,
                            controller="pulse", pulse_nm=(.2, 0, 0), command_delay_s=.02)
        values, _ = simulate(config, scenario)
        np.testing.assert_array_equal(values["applied"][:2], 0)
        self.assertAlmostEqual(values["applied"][2, 0], .02)
        self.assertTrue(values["saturated"][2, 0])
        self.assertTrue(values["speed_cutoff"][:, 0].any())
        self.assertTrue(values["speed_exceeded"][:, 0].any())
        self.assertGreater(max(values["qvel"][:, 6]), .5)
        self.assertTrue(np.all(abs(values["applied"]) <= .02))

    def test_simulation_pd_sign_reduces_small_free_space_error(self):
        config = load_config()
        scenario = Scenario("pd-sign", "Pure numerical controller sign witness", duration_s=2,
                            gravity=False, contact=False, controller="pd",
                            perturbation_rad=.04, command_delay_s=.02)
        values, _ = simulate(config, scenario)
        self.assertLess(np.linalg.norm(values["attitude_error"][-1]),
                        np.linalg.norm(values["attitude_error"][0]) * .5)

    def test_initial_edge_vertex_support_is_not_an_impulsive_launch(self):
        config = load_config()
        for name in ("edge-balance", "vertex-balance"):
            values, _ = simulate(config, replace(scenarios()[name], duration_s=.1))
            self.assertAlmostEqual(values["contact"][0, 2], 0, places=14)
            np.testing.assert_array_equal(values["qvel"][0], 0)
            self.assertGreater(values["qpos"][0, 2], config["body"]["side_m"] / 2)

    def test_invalid_scenarios_and_nonintegral_delay_fail(self):
        with self.assertRaises(ValueError):
            Scenario("bad", "bad quaternion", target=(2, 0, 0, 0))
        with self.assertRaises(ValueError):
            simulate(load_config(), Scenario("bad", "nonintegral delay", command_delay_s=.003))

    def test_step_and_solver_sensitivity_and_passive_dissipation(self):
        result = collect()
        for case in ("reference", "rev5-partial-proxy"):
            free = [row for row in result["rows"] if row["case"] == case and row["scenario"] == "three-wheel"]
            for row in free:
                self.assertLess(row["max_linear_momentum_kg_m_s"], 1e-10)
                self.assertLess(row["max_angular_momentum_nms"], 1e-10)
                self.assertLess(row["max_abs_energy_work_residual_j"], 1e-7)
                np.testing.assert_allclose(row["final_qpos"], free[0]["final_qpos"], atol=1e-8, rtol=0)
            rest = [row for row in result["rows"] if row["case"] == case and row["scenario"] == "rest"]
            for row in rest:
                self.assertLess(row["summary"]["max_penetration_m"], .0002)
                self.assertLess(abs(row["final_qpos"][2] - rest[0]["final_qpos"][2]), 1e-5)
            drops = [row for row in result["rows"] if row["case"] == case and row["scenario"] == "fall"]
            for row in drops:
                # Dissipative contact: conservation of rigid-body energy is NOT expected.
                self.assertLess(row["max_sampled_rigid_energy_j"] - row["initial_rigid_energy_j"], .001)
                self.assertLess(row["summary"]["max_penetration_m"], .01)
                self.assertLess(abs(row["final_qpos"][2] - drops[0]["final_qpos"][2]), .001)
            balance = [row for row in result["rows"] if row["case"] == case and "balance" in row["scenario"]]
            self.assertTrue(all(row["summary"]["outcome"] == "DEPARTED_TARGET" for row in balance))


if __name__ == "__main__":
    unittest.main()
