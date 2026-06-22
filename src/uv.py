"""
uv.py — UV unwrapping utilities.
Generates UV coordinates for mesh primitives, mirroring
Blender's Smart UV Project and cube projection methods.
"""

import numpy as np
from mesh import Mesh


def cube_project(mesh: Mesh) -> np.ndarray:
    """
    Box/cube projection: project each vertex onto the face of a
    unit cube and map to [0,1] UV space. Works well for cube-like shapes.
    """
    v = mesh.vertices
    abs_v = np.abs(v)
    dominant = np.argmax(abs_v, axis=1)  # 0=X, 1=Y, 2=Z

    uvs = np.zeros((len(v), 2), dtype=np.float32)

    # +/-X faces
    mask_x = dominant == 0
    uvs[mask_x, 0] = (v[mask_x, 1] + 1) / 2
    uvs[mask_x, 1] = (v[mask_x, 2] + 1) / 2

    # +/-Y faces
    mask_y = dominant == 1
    uvs[mask_y, 0] = (v[mask_y, 0] + 1) / 2
    uvs[mask_y, 1] = (v[mask_y, 2] + 1) / 2

    # +/-Z faces
    mask_z = dominant == 2
    uvs[mask_z, 0] = (v[mask_z, 0] + 1) / 2
    uvs[mask_z, 1] = (v[mask_z, 1] + 1) / 2

    return np.clip(uvs, 0, 1)


def spherical_project(mesh: Mesh) -> np.ndarray:
    """
    Spherical UV projection — maps vertices by longitude/latitude.
    Ideal for sphere meshes (matches Blender's sphere UV layout).
    """
    v = mesh.vertices
    x, y, z = v[:, 0], v[:, 1], v[:, 2]
    u = 0.5 + np.arctan2(y, x) / (2 * np.pi)
    r = np.sqrt(x**2 + y**2 + z**2) + 1e-8
    w = 0.5 - np.arcsin(np.clip(z / r, -1, 1)) / np.pi
    return np.column_stack([u, w]).astype(np.float32)


def planar_project(mesh: Mesh, axis: str = "z") -> np.ndarray:
    """
    Planar (orthographic) projection along a given axis.
    Best for flat surfaces like planes.
    """
    v = mesh.vertices
    axes = {"x": (1, 2), "y": (0, 2), "z": (0, 1)}
    if axis not in axes:
        raise ValueError(f"axis must be one of {list(axes.keys())}")
    a, b = axes[axis]
    coords = v[:, [a, b]]
    mins, maxs = coords.min(axis=0), coords.max(axis=0)
    ranges = maxs - mins + 1e-8
    return ((coords - mins) / ranges).astype(np.float32)


def cylindrical_project(mesh: Mesh) -> np.ndarray:
    """
    Cylindrical projection — wraps UVs around the Z axis.
    Great for cylinders and barrel-shaped objects.
    """
    v = mesh.vertices
    x, y, z = v[:, 0], v[:, 1], v[:, 2]
    u = 0.5 + np.arctan2(y, x) / (2 * np.pi)
    z_min, z_max = z.min(), z.max()
    w = (z - z_min) / (z_max - z_min + 1e-8)
    return np.column_stack([u, w]).astype(np.float32)


def auto_unwrap(mesh: Mesh) -> np.ndarray:
    """
    Smart auto-unwrap: pick the best projection based on mesh name/shape.
    Mirrors Blender's 'Smart UV Project' heuristic.
    """
    name = mesh.name.lower()
    if "sphere" in name:
        return spherical_project(mesh)
    elif "plane" in name:
        return planar_project(mesh, axis="z")
    elif "cylinder" in name:
        return cylindrical_project(mesh)
    else:
        return cube_project(mesh)


def apply_uvs(mesh: Mesh, uvs: np.ndarray) -> Mesh:
    """Return a new Mesh with UVs applied."""
    return Mesh(
        name=mesh.name,
        vertices=mesh.vertices,
        faces=mesh.faces,
        normals=mesh.normals,
        uvs=uvs,
    )
