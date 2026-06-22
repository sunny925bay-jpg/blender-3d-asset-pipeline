"""
pipeline.py — End-to-end CLI pipeline.
Run this script to generate and export 3D assets.

Usage:
  python pipeline.py --scene samples/demo_scene.json --output exports/
  python pipeline.py --primitive cube --output exports/
  python pipeline.py --primitive sphere --segments 32 --rings 16 --output exports/
  python pipeline.py --primitive cylinder --segments 24 --output exports/
  python pipeline.py --primitive plane --subdivisions 4 --output exports/
"""

import argparse
import sys
import os

sys.path.insert(0, os.path.dirname(__file__))

import numpy as np
from mesh import PRIMITIVE_MAP
from uv import auto_unwrap, apply_uvs
from material import PBRMaterial, PRESETS
from scene import Scene, SceneObject, Transform
from exporter import export_scene, export_scene_combined


def build_primitive_scene(args) -> Scene:
    prim_type = args.primitive.lower()
    if prim_type not in PRIMITIVE_MAP:
        print(f"[error] Unknown primitive '{prim_type}'. Choose from: {list(PRIMITIVE_MAP.keys())}")
        sys.exit(1)

    kwargs = {"name": prim_type.capitalize()}
    if prim_type == "sphere":
        kwargs["segments"] = getattr(args, "segments", 16)
        kwargs["rings"] = getattr(args, "rings", 8)
    elif prim_type == "cylinder":
        kwargs["segments"] = getattr(args, "segments", 16)
    elif prim_type == "plane":
        kwargs["subdivisions"] = getattr(args, "subdivisions", 1)

    mesh = PRIMITIVE_MAP[prim_type](**kwargs)
    uvs = auto_unwrap(mesh)
    mesh = apply_uvs(mesh, uvs)

    preset_name = getattr(args, "material", "matte_white")
    mat = PRESETS.get(preset_name, PRESETS["matte_white"])

    obj = SceneObject(name=prim_type, mesh=mesh, material=mat)
    scene = Scene(name=f"single_{prim_type}")
    scene.add(obj)
    return scene


def main():
    parser = argparse.ArgumentParser(
        description="Blender-style 3D Asset Pipeline — generate and export geometry"
    )

    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--scene", type=str, help="Path to a JSON scene config file")
    mode.add_argument("--primitive", type=str,
                      choices=list(PRIMITIVE_MAP.keys()),
                      help="Generate a single primitive mesh")

    parser.add_argument("--output", type=str, default="exports/",
                        help="Output directory for .obj/.mtl files (default: exports/)")
    parser.add_argument("--combined", action="store_true",
                        help="Export scene as a single combined .obj file")
    parser.add_argument("--material", type=str, default="matte_white",
                        choices=list(PRESETS.keys()),
                        help="Material preset for single primitive export")

    # Primitive-specific options
    parser.add_argument("--segments", type=int, default=16,
                        help="Segments for sphere/cylinder (default: 16)")
    parser.add_argument("--rings", type=int, default=8,
                        help="Rings for sphere (default: 8)")
    parser.add_argument("--subdivisions", type=int, default=1,
                        help="Subdivisions for plane (default: 1)")

    args = parser.parse_args()

    print("\n🧊 Blender 3D Asset Pipeline")
    print("─" * 40)

    if args.scene:
        from scene import Scene
        print(f"📂 Loading scene: {args.scene}")
        scene = Scene.from_json(args.scene)
    else:
        print(f"🔷 Generating primitive: {args.primitive}")
        scene = build_primitive_scene(args)

    print(scene.summary())
    print(f"\n📤 Exporting to: {args.output}")

    if args.combined:
        from exporter import export_scene_combined
        export_scene_combined(scene, args.output)
    else:
        export_scene(scene, args.output)

    print("\n✅ Done!")


if __name__ == "__main__":
    main()
