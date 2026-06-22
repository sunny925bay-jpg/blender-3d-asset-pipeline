"""
scene.py — Scene graph and object transforms.
Models Blender's object hierarchy: each SceneObject has a mesh,
material, and a 4×4 transform matrix (TRS decomposition).
"""

import numpy as np
import json
from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any

from mesh import Mesh, PRIMITIVE_MAP
from material import PBRMaterial
from uv import auto_unwrap, apply_uvs


@dataclass
class Transform:
    position: np.ndarray = field(default_factory=lambda: np.zeros(3))
    rotation: np.ndarray = field(default_factory=lambda: np.zeros(3))  # Euler XYZ degrees
    scale: np.ndarray = field(default_factory=lambda: np.ones(3))

    def matrix(self) -> np.ndarray:
        """Build a 4×4 TRS matrix (Translation × Rotation × Scale)."""
        T = _translate(self.position)
        Rx = _rotate_x(np.deg2rad(self.rotation[0]))
        Ry = _rotate_y(np.deg2rad(self.rotation[1]))
        Rz = _rotate_z(np.deg2rad(self.rotation[2]))
        S = _scale(self.scale)
        return T @ Rx @ Ry @ Rz @ S


@dataclass
class SceneObject:
    name: str
    mesh: Mesh
    material: PBRMaterial
    transform: Transform = field(default_factory=Transform)

    def world_vertices(self) -> np.ndarray:
        """Return vertices transformed to world space."""
        M = self.transform.matrix()
        v = self.mesh.vertices
        ones = np.ones((len(v), 1), dtype=np.float32)
        v_h = np.hstack([v, ones])          # homogeneous
        return (v_h @ M.T)[:, :3]


@dataclass
class Scene:
    name: str
    objects: List[SceneObject] = field(default_factory=list)

    def add(self, obj: SceneObject):
        self.objects.append(obj)

    def object_count(self) -> int:
        return len(self.objects)

    def summary(self) -> str:
        lines = [f"Scene: '{self.name}' ({self.object_count()} objects)"]
        for obj in self.objects:
            lines.append(
                f"  • {obj.name} [{obj.mesh.name}] "
                f"pos={obj.transform.position.tolist()} "
                f"mat={obj.material.name}"
            )
        return "\n".join(lines)

    @classmethod
    def from_json(cls, path: str) -> "Scene":
        """Load scene from a JSON config file."""
        with open(path) as f:
            data = json.load(f)

        scene = cls(name=data.get("name", "untitled"))

        for obj_data in data.get("objects", []):
            prim_type = obj_data.get("type", "cube").lower()
            if prim_type not in PRIMITIVE_MAP:
                raise ValueError(f"Unknown primitive type: '{prim_type}'")

            mesh = PRIMITIVE_MAP[prim_type](name=obj_data["name"])
            uvs = auto_unwrap(mesh)
            mesh = apply_uvs(mesh, uvs)

            mat_data = obj_data.get("material", {})
            mat = PBRMaterial(
                name=f"{obj_data['name']}_mat",
                albedo=tuple(mat_data.get("albedo", [0.8, 0.8, 0.8])),
                roughness=mat_data.get("roughness", 0.5),
                metalness=mat_data.get("metalness", 0.0),
            )

            transform = Transform(
                position=np.array(obj_data.get("position", [0, 0, 0]), dtype=np.float32),
                rotation=np.array(obj_data.get("rotation", [0, 0, 0]), dtype=np.float32),
                scale=np.array(obj_data.get("scale", [1, 1, 1]), dtype=np.float32),
            )

            scene.add(SceneObject(name=obj_data["name"], mesh=mesh,
                                   material=mat, transform=transform))

        return scene


# ---------------------------------------------------------------------------
# Transform helpers
# ---------------------------------------------------------------------------

def _translate(t: np.ndarray) -> np.ndarray:
    M = np.eye(4, dtype=np.float32)
    M[:3, 3] = t
    return M

def _scale(s: np.ndarray) -> np.ndarray:
    return np.diag([s[0], s[1], s[2], 1.0]).astype(np.float32)

def _rotate_x(a: float) -> np.ndarray:
    M = np.eye(4, dtype=np.float32)
    M[1,1] = M[2,2] = np.cos(a)
    M[1,2] = -np.sin(a); M[2,1] = np.sin(a)
    return M

def _rotate_y(a: float) -> np.ndarray:
    M = np.eye(4, dtype=np.float32)
    M[0,0] = M[2,2] = np.cos(a)
    M[2,0] = -np.sin(a); M[0,2] = np.sin(a)
    return M

def _rotate_z(a: float) -> np.ndarray:
    M = np.eye(4, dtype=np.float32)
    M[0,0] = M[1,1] = np.cos(a)
    M[0,1] = -np.sin(a); M[1,0] = np.sin(a)
    return M
