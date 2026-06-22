"""
material.py — PBR material definitions.
Models Blender's Principled BSDF material properties.
"""

from dataclasses import dataclass, field
from typing import Tuple, Optional
import json


@dataclass
class PBRMaterial:
    name: str
    albedo: Tuple[float, float, float] = (0.8, 0.8, 0.8)   # Base color (R,G,B) 0-1
    roughness: float = 0.5                                    # 0=mirror, 1=fully rough
    metalness: float = 0.0                                    # 0=dielectric, 1=metal
    opacity: float = 1.0                                      # 1=opaque, 0=transparent
    emission: Tuple[float, float, float] = (0.0, 0.0, 0.0)  # Emissive color
    ior: float = 1.45                                         # Index of refraction
    texture_path: Optional[str] = None                        # Optional diffuse texture

    def to_mtl(self) -> str:
        """Export material as Wavefront .mtl block."""
        r, g, b = self.albedo
        er, eg, eb = self.emission
        lines = [
            f"newmtl {self.name}",
            f"Kd {r:.4f} {g:.4f} {b:.4f}",          # Diffuse
            f"Ka {r*0.1:.4f} {g*0.1:.4f} {b*0.1:.4f}",  # Ambient
            f"Ks {self.metalness:.4f} {self.metalness:.4f} {self.metalness:.4f}",
            f"Ns {(1 - self.roughness) * 1000:.1f}",  # Shininess
            f"d {self.opacity:.4f}",                   # Dissolve (opacity)
            f"Ke {er:.4f} {eg:.4f} {eb:.4f}",         # Emission
            f"Ni {self.ior:.4f}",                      # IOR
            "illum 2",                                  # Illumination model
        ]
        if self.texture_path:
            lines.append(f"map_Kd {self.texture_path}")
        return "\n".join(lines)

    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "albedo": list(self.albedo),
            "roughness": self.roughness,
            "metalness": self.metalness,
            "opacity": self.opacity,
            "emission": list(self.emission),
            "ior": self.ior,
            "texture_path": self.texture_path,
        }

    @classmethod
    def from_dict(cls, d: dict) -> "PBRMaterial":
        return cls(
            name=d["name"],
            albedo=tuple(d.get("albedo", [0.8, 0.8, 0.8])),
            roughness=d.get("roughness", 0.5),
            metalness=d.get("metalness", 0.0),
            opacity=d.get("opacity", 1.0),
            emission=tuple(d.get("emission", [0, 0, 0])),
            ior=d.get("ior", 1.45),
            texture_path=d.get("texture_path"),
        )


# ---------------------------------------------------------------------------
# Preset materials (mirrors Blender's material presets)
# ---------------------------------------------------------------------------

PRESETS = {
    "chrome": PBRMaterial("chrome", albedo=(0.9, 0.9, 0.9), roughness=0.05, metalness=1.0),
    "matte_white": PBRMaterial("matte_white", albedo=(0.95, 0.95, 0.95), roughness=1.0, metalness=0.0),
    "plastic_blue": PBRMaterial("plastic_blue", albedo=(0.1, 0.3, 0.9), roughness=0.4, metalness=0.0),
    "gold": PBRMaterial("gold", albedo=(1.0, 0.77, 0.15), roughness=0.2, metalness=1.0),
    "glass": PBRMaterial("glass", albedo=(0.95, 0.95, 1.0), roughness=0.0, metalness=0.0, opacity=0.1, ior=1.52),
    "rubber": PBRMaterial("rubber", albedo=(0.05, 0.05, 0.05), roughness=0.95, metalness=0.0),
    "concrete": PBRMaterial("concrete", albedo=(0.55, 0.53, 0.50), roughness=0.9, metalness=0.0),
    "emissive_red": PBRMaterial("emissive_red", albedo=(1.0, 0.1, 0.1), roughness=0.5, emission=(5.0, 0.1, 0.1)),
}


def get_preset(name: str) -> PBRMaterial:
    if name not in PRESETS:
        raise ValueError(f"Unknown preset '{name}'. Available: {list(PRESETS.keys())}")
    mat = PRESETS[name]
    return PBRMaterial(**{**mat.to_dict(), "name": name})
