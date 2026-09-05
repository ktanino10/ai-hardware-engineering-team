import json
import unittest

import mujoco
import numpy as np

from cube_sim.intake import INTAKE, derive_proxy, parallel_axis
from cube_sim.model import build, inertia_matrix
from cube_sim.scenarios import rotation


class IntakeTests(unittest.TestCase):
    def setUp(self):
        self.intake = json.loads(INTAKE.read_text(encoding="utf-8"))
        self.config = derive_proxy()

    def aggregate(self, parts):
        mass = sum(p["mass_kg"] for p in parts)
        com = sum(p["mass_kg"] * np.asarray(p["com_m"]) for p in parts) / mass
        inertia = sum(inertia_matrix(p["inertia_kg_m2"]) +
                      p["mass_kg"] * parallel_axis(np.asarray(p["com_m"]) - com) for p in parts)
        return mass, com, inertia

    def test_remove_rotors_at_common_origin_and_recompose_locked_tensor(self):
        parts = [self.config["body"]] + [
            dict(wheel, com_m=wheel["center_m"]) for wheel in self.config["wheels"]]
        mass, com, inertia = self.aggregate(parts)
        original = self.intake["locked_partial"]
        self.assertAlmostEqual(mass, original["mass_kg"], places=13)
        np.testing.assert_allclose(com, original["com_m"], atol=1e-14, rtol=0)
        np.testing.assert_allclose(inertia, original["inertia_kg_m2"], atol=1e-14, rtol=0)
        self.assertAlmostEqual(self.config["body"]["mass_kg"], 2.7642777978399987, places=13)

    def test_independent_forward_chassis_sum_of_prints_motors_and_laminate(self):
        parts = [self.intake["printed_aggregate"]]
        motor = self.intake["motor_surrogate"]
        for i, axis in enumerate(np.eye(3)):
            m, r, h = (motor[key] for key in ("mass_kg", "radius_m", "thickness_m"))
            diagonal = np.full(3, m * (3 * r*r + h*h) / 12)
            diagonal[i] = m * r*r / 2
            parts.append({"mass_kg": m, "com_m": motor["axial_center_m"] * axis,
                          "inertia_kg_m2": diagonal})
        laminate = self.intake["bare_laminate"]
        dimensions = np.asarray(laminate["dimensions_m"])
        parts.append(dict(laminate, inertia_kg_m2=laminate["mass_kg"] *
                          (np.sum(dimensions**2) - dimensions**2) / 12))
        mass, com, inertia = self.aggregate(parts)
        chassis = self.config["body"]
        self.assertAlmostEqual(mass, chassis["mass_kg"], places=13)
        np.testing.assert_allclose(com, chassis["com_m"], atol=1e-14, rtol=0)
        np.testing.assert_allclose(inertia, chassis["inertia_kg_m2"], atol=1e-14, rtol=0)

    def test_compiled_full_tensor_and_mass_match_proxy_not_double_counted(self):
        model, data, _ = build(self.config, contact=False, gravity=False)
        self.assertAlmostEqual(sum(model.body_mass), self.intake["locked_partial"]["mass_kg"], places=13)
        matrix = rotation(model.body_iquat[1])
        compiled = matrix @ np.diag(model.body_inertia[1]) @ matrix.T
        np.testing.assert_allclose(compiled, self.config["body"]["inertia_kg_m2"], atol=1e-12, rtol=0)
        np.testing.assert_allclose(data.subtree_com[1] - data.qpos[:3],
                                   self.intake["locked_partial"]["com_m"], atol=1e-13, rtol=0)
        self.assertTrue(np.all(model.body_inertia[1:] > 0))
        self.assertEqual(self.config["classification"], "WIP_DESIGN_PROXY")
        self.assertIsNone(self.intake["unknowns"]["motor_rotor_inertia"])

    def test_independent_angular_momentum_sum_with_off_centre_com_and_spinning_wheels(self):
        model, data, _ = build(self.config, contact=False, gravity=False)
        data.qpos[3:7] = [.5, .5, .5, .5]
        data.qvel[:] = [.2, -.1, .3, .1, .2, -.15, 15, -12, 7]
        mujoco.mj_forward(model, data)
        matrix = rotation(data.qpos[3:7])
        omega = matrix @ data.qvel[3:6]
        parts = [(self.config["body"], self.config["body"]["com_m"], omega)]
        for i, wheel in enumerate(self.config["wheels"]):
            parts.append((wheel, wheel["center_m"], omega + matrix[:, i] * data.qvel[6+i]))
        total_com = matrix @ np.asarray(self.intake["locked_partial"]["com_m"])
        angular_momentum = np.zeros(3)
        for part, position, angular_rate in parts:
            offset = matrix @ np.asarray(position)
            linear_velocity = data.qvel[:3] + np.cross(omega, offset)
            angular_momentum += matrix @ inertia_matrix(part["inertia_kg_m2"]) @ matrix.T @ angular_rate
            angular_momentum += np.cross(offset - total_com, part["mass_kg"] * linear_velocity)
        np.testing.assert_allclose(data.sensor("angular_momentum_world").data,
                                   angular_momentum, atol=1e-12, rtol=0)


if __name__ == "__main__":
    unittest.main()
