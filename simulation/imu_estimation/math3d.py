"""Small dependency-free right-handed SO(3) helpers (Hamilton wxyz)."""

import math


def add(a, b):
    return [x + y for x, y in zip(a, b)]


def sub(a, b):
    return [x - y for x, y in zip(a, b)]


def scale(a, s):
    return [x * s for x in a]


def dot(a, b):
    return sum(x * y for x, y in zip(a, b))


def norm(a):
    return math.sqrt(dot(a, a))


def cross(a, b):
    x, y, z = a
    u, v, w = b
    return [y*w-z*v, z*u-x*w, x*v-y*u]


def mean(vectors):
    return [sum(v[k] for v in vectors) / len(vectors) for k in range(3)]


def transpose(a):
    return [list(v) for v in zip(*a)]


def mv(a, v):
    return [dot(row, v) for row in a]


def conjugate(q):
    return [q[0], -q[1], -q[2], -q[3]]


def multiply(a, b):
    w, x, y, z = a
    s, u, v, t = b
    return [w*s-x*u-y*v-z*t, w*u+x*s+y*t-z*v,
            w*v-x*t+y*s+z*u, w*t+x*v-y*u+z*s]


def unit(q):
    n = norm(q)
    if not math.isfinite(n) or n <= 0:
        raise ValueError("invalid quaternion norm")
    return scale(q, 1/n)


def exp_rot(v):
    """Rotation vector in radians -> unit quaternion; no axis ambiguity at 0."""
    a = norm(v)
    factor = math.sin(a/2)/a if a > 1e-10 else 0.5-a*a/48
    return unit([math.cos(a/2), *scale(v, factor)])


def matrix(q):
    w, x, y, z = q
    return [[1-2*(y*y+z*z), 2*(x*y-z*w), 2*(x*z+y*w)],
            [2*(x*y+z*w), 1-2*(x*x+z*z), 2*(y*z-x*w)],
            [2*(x*z-y*w), 2*(y*z+x*w), 1-2*(x*x+y*y)]]


def tilt_yaw_zero(force):
    """Rz(0) Ry(pitch) Rx(roll); assumes force is -R_WB^T gravity."""
    x, y, z = force
    if norm(force) <= 0:
        raise ValueError("zero force cannot initialize tilt")
    roll = math.atan2(y, z)
    pitch = math.atan2(-x, math.hypot(y, z))
    return unit(multiply(exp_rot([0, pitch, 0]), exp_rot([roll, 0, 0])))


def distance(a, b):
    q = multiply(conjugate(a), b)
    return 2*math.atan2(norm(q[1:]), abs(q[0]))
