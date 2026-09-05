"""Numerical regression tolerances, NOT physical qualification thresholds."""

import copy
from dataclasses import replace
import unittest

import mujoco
import numpy as np

from cube_sim.model import build, inertia_matrix, load_config, validate_config
from cube_sim.runner import simulate
from cube_sim.scenarios import Scenario, axis_angle, initialize, rotation, scenarios


class PhysicsTests(unittest.TestCase):
    def setUp(self):
        self.config = load_config()

    def test_three_articulated_rotors_and_mass_not_visual_density(self):
        model, data, _ = build(self.config)
        self.assertEqual((model.nq, model.nv, model.nu), (10, 9, 3))
        self.assertAlmostEqual(sum(model.body_mass), 1.3, places=14)
        self.assertEqual(data.qfrc_applied.sum(), 0)
        self.assertEqual(data.xfrc_applied.sum(), 0)
        np.testing.assert_array_equal(model.actuator_trnid[:, 0], [1, 2, 3])

    def test_zero_input_in_free_space_is_stationary(self):
        scenario = Scenario("zero", "Numerical witness", contact=False, gravity=False)
        values, _ = simulate(self.config, scenario)
        np.testing.assert_array_equal(values["qvel"], 0)
        np.testing.assert_array_equal(values["qpos"], np.tile(values["qpos"][0], (201, 1)))

    def test_independent_inertia_and_internal_torque_acceleration(self):
        model, data, _ = build(self.config, contact=False, gravity=False)
        parts = [self.config["body"], *self.config["wheels"]]
        masses = np.array([part["mass_kg"] for part in parts])
        positions = np.array([self.config["body"]["com_m"]] +
                             [wheel["center_m"] for wheel in self.config["wheels"]])
        centre = masses @ positions / masses.sum()
        locked = np.zeros((3, 3))
        for mass, position, part in zip(masses, positions, parts):
            r = position - centre
            locked += inertia_matrix(part["inertia_kg_m2"]) + mass * (r @ r * np.eye(3) - np.outer(r, r))
        axial = np.array([wheel["inertia_kg_m2"][i] for i, wheel in enumerate(self.config["wheels"])])
        torque = np.array([.01, -.003, .002])
        predicted_body = -np.linalg.solve(locked - np.diag(axial), torque)
        data.ctrl[:] = torque
        mujoco.mj_forward(model, data)
        np.testing.assert_allclose(data.qacc[3:6], predicted_body, atol=1e-12, rtol=1e-12)
        np.testing.assert_allclose(data.qacc[6:], torque / axial - predicted_body, atol=1e-10, rtol=1e-12)
        np.testing.assert_array_equal(data.qfrc_actuator[:6], 0)

    def test_internal_torque_conserves_world_momentum_and_accounts_for_work(self):
        values, _ = simulate(self.config, scenarios()["three-wheel"])
        self.assertLess(np.max(np.linalg.norm(values["angular_momentum"], axis=1)), 1e-10)
        self.assertLess(np.max(np.linalg.norm(values["linear_momentum"], axis=1)), 1e-10)
        residual = np.sum(values["energy"] - values["energy"][0], axis=1) - values["work"].sum(axis=1)
        self.assertLess(np.max(np.abs(residual)), 1e-7)
        np.testing.assert_allclose(np.linalg.norm(values["qpos"][:, 3:7], axis=1), 1, atol=1e-12)

    def test_coordinate_sign_and_velocity_frames(self):
        model, data, _ = build(self.config, contact=False, gravity=False)
        scenario = Scenario("rotated", "Frame witness", contact=False, gravity=False,
                            target=tuple(axis_angle([0, 0, 1], np.pi / 2)), command_delay_s=0)
        initialize(model, data, self.config, scenario)
        data.ctrl[:] = [.01, 0, 0]
        mujoco.mj_step(model, data)
        mujoco.mj_forward(model, data)
        omega = np.zeros(6)
        mujoco.mj_objectVelocity(model, data, mujoco.mjtObj.mjOBJ_BODY, model.body("cube").id, omega, 0)
        np.testing.assert_allclose(omega[:3], rotation(data.qpos[3:7]) @ data.qvel[3:6], atol=1e-12)
        self.assertLess(omega[1], 0)
        self.assertGreater(data.qvel[6], 0)

    def test_face_starts_without_penetration_and_supports_weight(self):
        values, _ = simulate(self.config, scenarios()["rest"])
        self.assertEqual(values["contact"][0, 2], 0)
        self.assertGreaterEqual(values["contact"][-1, 0], 3)
        self.assertAlmostEqual(values["contact"][-1, 1], 1.3 * 9.81, delta=.001)
        self.assertLess(-np.min(values["contact"][:, 2]), .0002)

    def test_reproducible_same_configuration(self):
        scenario = replace(scenarios()["fall"], duration_s=.2)
        left, _ = simulate(self.config, scenario)
        right, _ = simulate(self.config, scenario)
        for key in left:
            np.testing.assert_array_equal(left[key], right[key])

    def test_invalid_inputs_fail_instead_of_defaults(self):
        for part, key, value in (("body", "mass_kg", None), ("body", "side_m", -1),
                                 ("contact", "sliding_friction", float("nan")),
                                 ("integration", "timestep_s", 0)):
            with self.subTest(key=key):
                config = copy.deepcopy(self.config)
                config[part][key] = value
                with self.assertRaises((ValueError, TypeError)):
                    validate_config(config)
        config = copy.deepcopy(self.config)
        config["body"]["inertia_kg_m2"] = [1, 1, 3]
        with self.assertRaises(ValueError):
            validate_config(config)


if __name__ == "__main__":
    unittest.main()
