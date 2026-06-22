"""
mesh.py — Procedural geometry primitives.
Generates vertices, faces, and normals for basic 3D shapes,
mirroring the kind of mesh data Blender works with internally.
"""

import numpy as np
from dataclasses import dataclass, field
from typing import List, Tuple


@dataclass
class Mesh:
    name: str
    vertices: np.ndarray      # (N, 3) float32
    faces: np.ndarray         # (F, 3) int   — triangle indices
    normals: np.ndarray       # (N, 3) float32
    uvs: np.ndarray = field(default_factory=lambda: np.array([]))  # (N, 2)

    def vertex_count(self) -> int:
        return len(self.vertices)

    def face_count(self) -> int:
        return len(self.faces)

    def __repr__(self):
        return (f"Mesh('{self.name}', verts={self.vertex_count()}, "
                f"faces={self.face_count()})")


# ---------------------------------------------------------------------------
# Primitive generators
# ---------------------------------------------------------------------------

def make_cube(name: str = "Cube", size: float = 1.0) -> Mesh:
    """Unit cube centered at origin, triangulated."""
    h = size / 2
    verts = np.array([
        [-h, -h, -h], [ h, -h, -h], [ h,  h, -h], [-h,  h, -h],  # bottom
        [-h, -h,  h], [ h, -h,  h], [ h,  h,  h], [-h,  h,  h],  # top
    ], dtype=np.float32)

    # 6 faces × 2 triangles each
    faces = np.array([
        [0,1,2],[0,2,3],  # -Z
        [4,6,5],[4,7,6],  # +Z
        [0,4,5],[0,5,1],  # -Y
        [2,6,7],[2,7,3],  # +Y
        [0,3,7],[0,7,4],  # -X
        [1,5,6],[1,6,2],  # +X
    ], dtype=np.int32)

    normals = _compute_vertex_normals(verts, faces)
    return Mesh(name=name, vertices=verts, faces=faces, normals=normals)


def make_plane(name: str = "Plane", size: float = 1.0, subdivisions: int = 1) -> Mesh:
    """Flat XY plane, optionally subdivided."""
    n = subdivisions + 1
    lin = np.linspace(-size / 2, size / 2, n)
    xs, ys = np.meshgrid(lin, lin)
    verts = np.column_stack([xs.ravel(), ys.ravel(),
                              np.zeros(n * n)]).astype(np.float32)

    faces = []
    for row in range(n - 1):
        for col in range(n - 1):
            tl = row * n + col
            tr = tl + 1
            bl = tl + n
            br = bl + 1
            faces += [[tl, bl, tr], [tr, bl, br]]

    faces = np.array(faces, dtype=np.int32)
    normals = np.tile([0, 0, 1], (len(verts), 1)).astype(np.float32)
    return Mesh(name=name, vertices=verts, faces=faces, normals=normals)


def make_sphere(name: str = "Sphere", radius: float = 1.0,
                segments: int = 16, rings: int = 8) -> Mesh:
    """UV sphere."""
    verts, faces = [], []

    for ring in range(rings + 1):
        phi = np.pi * ring / rings
        for seg in range(segments):
            theta = 2 * np.pi * seg / segments
            x = radius * np.sin(phi) * np.cos(theta)
            y = radius * np.sin(phi) * np.sin(theta)
            z = radius * np.cos(phi)
            verts.append([x, y, z])

    for ring in range(rings):
        for seg in range(segments):
            next_seg = (seg + 1) % segments
            tl = ring * segments + seg
            tr = ring * segments + next_seg
            bl = (ring + 1) * segments + seg
            br = (ring + 1) * segments + next_seg
            faces += [[tl, bl, tr], [tr, bl, br]]

    verts = np.array(verts, dtype=np.float32)
    faces = np.array(faces, dtype=np.int32)
    normals = verts / (np.linalg.norm(verts, axis=1, keepdims=True) + 1e-8)
    return Mesh(name=name, vertices=verts, faces=faces, normals=normals.astype(np.float32))


def make_cylinder(name: str = "Cylinder", radius: float = 0.5,
                  height: float = 1.0, segments: int = 16) -> Mesh:
    """Capped cylinder."""
    h = height / 2
    verts, faces = [], []

    # Side rings
    for z in [-h, h]:
        for i in range(segments):
            theta = 2 * np.pi * i / segments
            verts.append([radius * np.cos(theta), radius * np.sin(theta), z])

    # Side faces
    for i in range(segments):
        j = (i + 1) % segments
        b, t = i, i + segments
        bj, tj = j, j + segments
        faces += [[b, bj, t], [t, bj, tj]]

    # Caps
    bot_center = len(verts); verts.append([0, 0, -h])
    top_center = len(verts); verts.append([0, 0,  h])

    for i in range(segments):
        j = (i + 1) % segments
        faces.append([bot_center, j, i])
        faces.append([top_center, i + segments, j + segments])

    verts = np.array(verts, dtype=np.float32)
    faces = np.array(faces, dtype=np.int32)
    normals = _compute_vertex_normals(verts, faces)
    return Mesh(name=name, vertices=verts, faces=faces, normals=normals)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _compute_vertex_normals(verts: np.ndarray, faces: np.ndarray) -> np.ndarray:
    normals = np.zeros_like(verts)
    v0 = verts[faces[:, 0]]
    v1 = verts[faces[:, 1]]
    v2 = verts[faces[:, 2]]
    face_normals = np.cross(v1 - v0, v2 - v0)
    for i, f in enumerate(faces):
        normals[f[0]] += face_normals[i]
        normals[f[1]] += face_normals[i]
        normals[f[2]] += face_normals[i]
    norms = np.linalg.norm(normals, axis=1, keepdims=True)
    return (normals / (norms + 1e-8)).astype(np.float32)


PRIMITIVE_MAP = {
    "cube": make_cube,
    "plane": make_plane,
    "sphere": make_sphere,
    "cylinder": make_cylinder,
}
