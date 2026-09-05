"""Exact display-mesh correspondence, independent of vertex index ordering."""

import math


def cylinder_mesh(radius, depth, segments=48):
    vertices = []
    for i in range(segments):
        angle = 2 * math.pi * i / segments
        for z in (-depth / 2, depth / 2):
            vertices.append((radius * math.cos(angle), radius * math.sin(angle), z))
    faces = []
    for i in range(segments):
        a, b = 2 * i, 2 * ((i + 1) % segments)
        faces.append((a, b, b + 1, a + 1))
    faces.append(tuple(2 * i + 1 for i in range(segments)))
    faces.append(tuple(2 * i for i in reversed(range(segments))))
    return vertices, faces


def canonical_face(face):
    face = tuple(face)
    return min(face[i:] + face[:i] for i in range(len(face)))


def verify_mesh(actual_vertices, actual_faces, expected_vertices, expected_faces, label, tolerance=1e-6):
    if len(actual_vertices) != len(expected_vertices) or len(actual_faces) != len(expected_faces):
        raise ValueError(f"{label} mesh vertex/face count mismatch")
    unused = set(range(len(expected_vertices)))
    mapping = {}
    maximum_error = 0.0
    for index, vertex in enumerate(actual_vertices):
        if len(vertex) != 3 or not all(math.isfinite(float(x)) for x in vertex):
            raise ValueError(f"{label} non-finite mesh vertex")
        closest = min(unused, key=lambda j: math.dist(vertex, expected_vertices[j]))
        error = math.dist(vertex, expected_vertices[closest])
        if error > tolerance:
            raise ValueError(f"{label} mesh vertex mismatch: {error}")
        mapping[index] = closest
        unused.remove(closest)
        maximum_error = max(maximum_error, error)
    if any(len(face) < 3 or any(i not in mapping for i in face) for face in actual_faces):
        raise ValueError(f"{label} invalid mesh face indices")
    actual = sorted(canonical_face(tuple(mapping[i] for i in face)) for face in actual_faces)
    expected = sorted(canonical_face(face) for face in expected_faces)
    if actual != expected:
        raise ValueError(f"{label} mesh topology/winding mismatch")
    return maximum_error
