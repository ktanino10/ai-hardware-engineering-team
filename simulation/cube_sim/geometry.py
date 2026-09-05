"""Display meshes only; inertias remain explicit analytical inputs."""

import math


def annulus_mesh(outer, inner, thickness, segments=48):
    vertices = []
    for i in range(segments):
        angle = 2 * math.pi * i / segments
        for radius, z in ((outer, -thickness / 2), (outer, thickness / 2),
                          (inner, -thickness / 2), (inner, thickness / 2)):
            vertices.append((radius * math.cos(angle), radius * math.sin(angle), z))
    faces = []
    for i in range(segments):
        a, b = 4 * i, 4 * ((i + 1) % segments)
        faces += [(a, b, b+1), (a, b+1, a+1), (a+2, a+3, b+3), (a+2, b+3, b+2),
                  (a+1, b+1, b+3), (a+1, b+3, a+3), (a, a+2, b+2), (a, b+2, b)]
    return vertices, faces
