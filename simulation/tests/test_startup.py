from dataclasses import replace
import unittest

import mujoco
import numpy as np

from cube_sim.braking import Startup, derive_startup_config
from cube_sim.model import ROOT, build
from cube_sim.runner import simulate, summary
from cube_sim.scenarios import Scenario, startup_scenario
from cube_sim.visualize import detail_samples, video_samples


class StartupTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.cases = []
        for base, fixture in (("rev5-proxy", False), ("reference", True)):
            config = derive_startup_config(ROOT / "models" / f"{base}.json", mechanism_fixture=fixture)
            scenario = startup_scenario(config)
            values, xml = simulate(config, scenario)
            cls.cases.append((config, scenario, values, xml))

    def test_real_spinup_finite_brake_and_minimum_ten_second_movies(self):
        for config, scenario, values, _ in self.cases:
            np.testing.assert_array_equal(values["qvel"][0], 0)
            self.assertAlmostEqual(values["time"][-1], 10, places=8)
            self.assertEqual(len(video_samples(values)), 250)
            self.assertEqual(len(detail_samples(values, scenario.record()["startup"])), 250)
            report = summary(values, scenario, config)["startup"]
            self.assertGreater(report["pre_brake_relative_rpm_xyz"][0], 2990)
            self.assertGreater(report["observed_stop_delay_from_ramp_start_s"], .005)
            self.assertLess(report["observed_stop_delay_from_ramp_start_s"], .007)
            self.assertFalse(report["hardware_speed_or_brake_qualified"])
            self.assertLess(np.max(np.abs(values["brake_torque"]) -
                                   np.asarray(config["actuation"]["independent_brake"]["capacity_nm"])), 1e-9)
            ramp = values["brake_limit"][:, 0]
            self.assertTrue(np.any((ramp > 0) & (ramp < max(ramp))))

    def test_brake_energy_and_contact_momentum_have_correct_accounting(self):
        for config, scenario, values, _ in self.cases:
            report = summary(values, scenario, config)
            self.assertLess(report["energy_accounting"]["max_abs_residual_all_steps_j"], 5e-5)
            self.assertLess(report["max_angular_momentum_balance_residual_nms"], 1e-7)
            self.assertGreater(report["startup"]["modeled_brake_dissipation_j"], 2)
            self.assertLess(values["peak_positive_brake_power"][-1], 1e-3)
            model, data, _ = build(config)
            self.assertEqual(model.neq, 0)
            np.testing.assert_array_equal(model.dof_frictionloss[:6], 0)
            np.testing.assert_array_equal(data.xfrc_applied, 0)
            np.testing.assert_array_equal(data.qfrc_applied, 0)

    def test_synthetic_upset_is_not_a_claim_of_proxy_success_or_capture(self):
        proxy, fixture = self.cases
        proxy_report = summary(proxy[2], proxy[1], proxy[0])
        fixture_report = summary(fixture[2], fixture[1], fixture[0])
        self.assertEqual(proxy_report["outcome"], "TARGET_NOT_REACHED")
        self.assertLess(proxy_report["startup"]["max_body_rotation_from_initial_deg"], .1)
        self.assertEqual(fixture_report["outcome"], "TARGET_ATTITUDE_VISITED_NO_CAPTURE")
        self.assertGreater(fixture_report["startup"]["max_body_rotation_from_initial_deg"], 90)
        self.assertGreater(fixture_report["startup"]["max_body_centre_height_m"], .065)
        self.assertGreater(fixture_report["startup"]["max_minimum_corner_height_m"], .0001)
        self.assertEqual(fixture_report["startup"]["flight_assessment"]["status"],
                         "NUMERICALLY_UNRESOLVED_CONTACT_ENVELOPE")
        self.assertTrue(fixture_report["startup"]["flight_assessment"]["observed_intervals"])
        self.assertEqual(fixture[0]["classification"], "SYNTHETIC_REFERENCE")
        self.assertEqual(fixture[0]["body"]["side_m"], .1)

    def test_xyz_targets_are_internal_efforts_not_external_force_knobs(self):
        program = Startup(target_rad_s=(100, -100, 50))
        np.testing.assert_allclose(program.requested_motor(.1, np.zeros(3)), [.05, -.05, .025])
        np.testing.assert_array_equal(program.requested_motor(4, np.zeros(3)), 0)
        with self.assertRaises(ValueError):
            Startup(target_rad_s=(0, 0, 0))

    def test_three_axis_passive_brake_preserves_free_space_momentum(self):
        config = derive_startup_config(ROOT / "models/reference.json")
        config["actuation"]["independent_brake"]["capacity_nm"] = [.01, .01, .01]
        program = Startup(spin_until_s=.06, brake_command_s=.1, target_rad_s=(5, -4, 3),
                          dense_start_s=.09, dense_end_s=.2)
        scenario = Scenario("xyz-brake-witness", "Numerical fixture only", duration_s=.3,
                            contact=False, gravity=False, controller="spin-brake", startup=program)
        values, _ = simulate(config, scenario)
        self.assertLess(np.max(np.linalg.norm(values["angular_momentum"], axis=1)), 1e-8)
        self.assertLess(np.max(np.linalg.norm(values["linear_momentum"], axis=1)), 1e-8)
        np.testing.assert_allclose(values["ground_force"], 0, atol=1e-12)
        self.assertTrue(np.all(np.max(np.abs(values["brake_torque"]), axis=0) > 0))

    def test_step_refinement_and_output_sampling_are_distinct(self):
        config, scenario, coarse, _ = self.cases[0]
        config = dict(config, integration=dict(config["integration"], timestep_s=.00005))
        shorter = replace(scenario, duration_s=3.7)
        fine, _ = simulate(config, shorter)
        report = summary(fine, shorter, config)
        self.assertLess(report["energy_accounting"]["max_abs_residual_all_steps_j"],
                        coarse["peak_energy_residual"][-1])
        downsampled, _ = simulate(config, replace(shorter, startup=replace(shorter.startup, dense_period_s=.001)))
        np.testing.assert_array_equal(fine["qpos"][-1], downsampled["qpos"][-1])
        self.assertEqual(fine["peak_energy_residual"][-1], downsampled["peak_energy_residual"][-1])
        self.assertLess(len(downsampled["time"]), len(fine["time"]))


if __name__ == "__main__":
    unittest.main()
