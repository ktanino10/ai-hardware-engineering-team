"""Explicit inertias; visual geoms never contribute mass (MJCF reference)."""

import itertools
import json
from pathlib import Path
import xml.etree.ElementTree as ET

import mujoco
import numpy as np
from .geometry import annulus_mesh

ROOT = Path(__file__).resolve().parents[1]


def vector(values):
    return " ".join(format(float(x), ".17g") for x in values)


def finite(value, shape, name, *, positive=False, nonnegative=False):
    array = np.asarray(value, dtype=float)
    if array.shape != shape or not np.all(np.isfinite(array)):
        raise ValueError(f"{name} must have shape {shape} and finite numeric values; UNKNOWN cannot be simulated.")
    if positive and np.any(array <= 0) or nonnegative and np.any(array < 0):
        raise ValueError(f"{name} is outside its allowed positive/nonnegative domain.")
    return array


def inertia_matrix(value):
    array = np.asarray(value, dtype=float)
    return np.diag(array) if array.shape == (3,) else array


def inertia_attributes(value):
    matrix = inertia_matrix(value)
    return {"fullinertia": vector([matrix[0, 0], matrix[1, 1], matrix[2, 2],
                                   matrix[0, 1], matrix[0, 2], matrix[1, 2]])}


def load_config(path=ROOT / "models/reference.json"):
    config = json.loads(Path(path).read_text(encoding="utf-8"))
    validate_config(config)
    return config


def validate_config(config):
    if config["schema_version"] != 1:
        raise ValueError("Unsupported model schema.")
    if config["classification"] not in {"SYNTHETIC_REFERENCE", "WIP_DESIGN_PROXY"}:
        raise ValueError("Only explicit synthetic or incomplete WIP proxy cases are runnable.")
    if config["actuation"]["model"] != "IDEAL_JOINT_TORQUE_NOT_ACTUAL_DRIVER":
        raise ValueError("Actual driver dynamics are UNKNOWN; no qualified driver model exists.")
    if len(config["wheels"]) != 3:
        raise ValueError("Exactly three distinct orthogonal wheels are required.")
    for index, wheel in enumerate(config["wheels"]):
        if wheel["name"] != "xyz"[index] or wheel["axis"] != np.eye(3)[index].tolist():
            raise ValueError("Wheel order and positive axes must be x, y, z in the cube frame.")
    for part in [config["body"], *config["wheels"]]:
        matrix = finite(inertia_matrix(part["inertia_kg_m2"]), (3, 3), "inertia")
        if not np.allclose(matrix, matrix.T, rtol=0, atol=1e-14):
            raise ValueError("Inertial tensor must be symmetric in the stated body frame.")
        inertia = np.linalg.eigvalsh(matrix)
        if np.any(inertia <= 0) or 2 * max(inertia) > sum(inertia) + 1e-14:
            raise ValueError("Inertias must be positive principal moments satisfying triangle inequalities.")
        finite(part["mass_kg"], (), "mass_kg", positive=True)
    half = float(finite(config["body"]["side_m"], (), "side_m", positive=True)) / 2
    com = finite(config["body"]["com_m"], (3,), "com_m")
    if np.any(np.abs(com) > half):
        raise ValueError("Body COM must lie inside this cube collision proxy.")
    for wheel in config["wheels"]:
        center = finite(wheel["center_m"], (3,), "wheel center")
        radius = finite(wheel["radius_m"], (), "radius", positive=True)
        thickness = finite(wheel["thickness_m"], (), "thickness", positive=True)
        extent = np.where(wheel["axis"], thickness / 2, radius)
        if np.any(np.abs(center) + extent > half):
            raise ValueError("Wheel visual envelope exceeds the declared cube proxy.")
        if "inner_radius_m" in wheel:
            inner = finite(wheel["inner_radius_m"], (), "inner radius", positive=True)
            if inner >= radius:
                raise ValueError("Annulus inner radius must be smaller than outer radius.")
    for key in ("torque_limit_nm", "speed_cutoff_rad_s"):
        finite(config["actuation"][key], (3,), key, positive=True)
    settings = config["integration"]
    dt = float(finite(settings["timestep_s"], (), "timestep", positive=True))
    finite(settings["tolerance"], (), "solver tolerance", positive=True)
    if settings["integrator"] not in {"implicitfast", "Euler", "RK4"} or settings["solver"] not in {"Newton", "CG", "PGS"}:
        raise ValueError("Unsupported documented integrator/solver.")
    if type(settings["iterations"]) is not int or settings["iterations"] < 1:
        raise ValueError("Solver iterations must be a positive integer.")
    floor = config["contact"]
    finite(floor["sliding_friction"], (), "friction", nonnegative=True)
    solref = finite(floor["solref"], (2,), "solref", positive=True)
    solimp = finite(floor["solimp"], (3,), "solimp", positive=True)
    if solref[0] < 2 * dt or not 0 < solimp[0] <= solimp[1] < 1 or floor["condim"] != 3:
        raise ValueError("Require condim=3, 0<dmin<=dmax<1, and contact time constant >=2*dt.")
    finite(config["gravity_m_s2"], (3,), "gravity")
    brake = config["actuation"].get("independent_brake")
    if brake is not None:
        if brake["model"] != "IDEAL_DRY_HINGE_BRAKE_NOT_ACTUAL_DRIVER":
            raise ValueError("Actual brake capability is unknown; only the explicit ideal fixture is supported.")
        finite(brake["capacity_nm"], (3,), "brake capacity", nonnegative=True)
        brake_ref = finite(brake["solref"], (2,), "brake solref", positive=True)
        brake_imp = finite(brake["solimp"], (5,), "brake solimp", positive=True)
        if brake_ref[0] < 2 * dt or not 0 < brake_imp[0] <= brake_imp[1] < 1 or brake_imp[3] > 1:
            raise ValueError("Invalid numerical brake constraint parameters.")


def make_xml(config, *, contact=True, gravity=True):
    root = ET.Element("mujoco", model=config["case_id"])
    ET.SubElement(root, "compiler", angle="radian", inertiafromgeom="false")
    settings = config["integration"]
    option = ET.SubElement(root, "option", timestep=str(settings["timestep_s"]),
                           integrator=settings["integrator"], solver=settings["solver"],
                           iterations=str(settings["iterations"]), tolerance=str(settings["tolerance"]),
                           gravity=vector(config["gravity_m_s2"] if gravity else [0, 0, 0]),
                           cone="elliptic")
    ET.SubElement(option, "flag", energy="enable")
    visual = ET.SubElement(root, "visual")
    ET.SubElement(visual, "global", offwidth="960", offheight="720")
    asset = ET.SubElement(root, "asset")
    ET.SubElement(asset, "texture", name="grid", type="2d", builtin="checker",
                  rgb1=".17 .20 .24", rgb2=".23 .27 .31", width="256", height="256")
    ET.SubElement(asset, "material", name="floor", texture="grid", texrepeat="12 12")
    world = ET.SubElement(root, "worldbody")
    ET.SubElement(world, "light", pos="0 -1 3", dir="0 0 -1", diffuse=".8 .8 .8")
    floor = config["contact"]
    ET.SubElement(world, "geom", name="floor", type="plane", size="3 3 .1",
                  material="floor", contype=str(int(contact)), conaffinity=str(int(contact)),
                  friction=vector([floor["sliding_friction"], 0, 0]), condim=str(floor["condim"]),
                  solref=vector(floor["solref"]), solimp=vector(floor["solimp"]))
    body = config["body"]
    half = body["side_m"] / 2
    cube = ET.SubElement(world, "body", name="cube", pos=vector([0, 0, half]))
    ET.SubElement(cube, "freejoint", name="floating")
    ET.SubElement(cube, "inertial", pos=vector(body["com_m"]), mass=str(body["mass_kg"]),
                  **inertia_attributes(body["inertia_kg_m2"]))
    ET.SubElement(cube, "geom", name="cube_collision", type="box", size=vector([half] * 3),
                  rgba=".3 .5 .7 .16", friction=vector([floor["sliding_friction"], 0, 0]),
                  condim=str(floor["condim"]), solref=vector(floor["solref"]),
                  solimp=vector(floor["solimp"]))
    for axis in range(3):
        for signs in itertools.product((-half, half), repeat=2):
            ends = np.zeros((2, 3))
            ends[:, [i for i in range(3) if i != axis]] = signs
            ends[:, axis] = [-half, half]
            ET.SubElement(cube, "geom", type="capsule", fromto=vector(ends.ravel()),
                          size=".002", rgba=".7 .8 .9 1", contype="0", conaffinity="0")
    rotations = ([.7071067811865476, 0, .7071067811865476, 0],
                 [.7071067811865476, -.7071067811865476, 0, 0], [1, 0, 0, 0])
    colors = (".9 .25 .2 1", ".2 .8 .4 1", ".3 .5 1 1")
    actuator = ET.SubElement(root, "actuator")
    for i, wheel in enumerate(config["wheels"]):
        name = "wheel_" + wheel["name"]
        rotor = ET.SubElement(cube, "body", name=name, pos=vector(wheel["center_m"]))
        ET.SubElement(rotor, "inertial", pos="0 0 0", mass=str(wheel["mass_kg"]),
                      **inertia_attributes(wheel["inertia_kg_m2"]))
        brake = config["actuation"].get("independent_brake")
        friction = ({"frictionloss": "0", "solreffriction": vector(brake["solref"]),
                     "solimpfriction": vector(brake["solimp"])} if brake else {})
        ET.SubElement(rotor, "joint", name=name, type="hinge", axis=vector(wheel["axis"]),
                      damping="0", armature="0", **friction)
        if "inner_radius_m" in wheel:
            vertices, faces = annulus_mesh(wheel["radius_m"], wheel["inner_radius_m"], wheel["thickness_m"])
            ET.SubElement(asset, "mesh", name=name + "_annulus",
                          vertex=vector(np.asarray(vertices).ravel()),
                          face=" ".join(str(index) for face in faces for index in face))
            shape = {"type": "mesh", "mesh": name + "_annulus"}
        else:
            shape = {"type": "cylinder", "size": vector([wheel["radius_m"], wheel["thickness_m"] / 2])}
        ET.SubElement(rotor, "geom", name=name + "_visual", **shape,
                      quat=vector(rotations[i]), rgba=colors[i], contype="0", conaffinity="0")
        marker_radius = ((wheel["radius_m"] + wheel["inner_radius_m"]) / 2
                         if "inner_radius_m" in wheel else wheel["radius_m"] * .8)
        marker = np.eye(3)[(i + 1) % 3] * marker_radius
        marker += np.asarray(wheel["axis"]) * wheel["thickness_m"] / 2
        ET.SubElement(rotor, "geom", type="sphere", size=".004", pos=vector(marker),
                      rgba="1 1 1 1", contype="0", conaffinity="0")
        limit = config["actuation"]["torque_limit_nm"][i]
        ET.SubElement(actuator, "motor", name=name, joint=name, gear="1", ctrllimited="true",
                      ctrlrange=vector([-limit, limit]))
    sensor = ET.SubElement(root, "sensor")
    ET.SubElement(sensor, "subtreeangmom", name="angular_momentum_world", body="cube")
    ET.SubElement(sensor, "subtreelinvel", name="com_velocity_world", body="cube")
    ET.indent(root)
    return ET.tostring(root, encoding="unicode") + "\n"


def build(config, *, contact=True, gravity=True):
    validate_config(config)
    xml = make_xml(config, contact=contact, gravity=gravity)
    model = mujoco.MjModel.from_xml_string(xml)
    data = mujoco.MjData(model)
    mujoco.mj_forward(model, data)
    return model, data, xml
