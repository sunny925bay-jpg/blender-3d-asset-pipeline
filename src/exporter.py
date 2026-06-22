"""
exporter.py — OBJ / MTL export pipeline.
Exports SceneObjects to industry-standard Wavefront .obj + .mtl files,
the same format Blender's File > Export > Wavefront (.obj) produces.
"""

import os
import numpy as np
from typing import List

from scene import SceneObject, Scene


def export_object(obj: SceneObject, output_dir: str) -> str:
    """
    Export a single SceneObject to .obj + .mtl.
    Returns the path to the exported .obj file.
    """
    os.makedirs(output_dir, exist_ok=True)

    safe_name = obj.name.replace(" ", "_")
    obj_path = os.path.join(output_dir, f"{safe_name}.obj")
    mtl_path = os.path.join(output_dir, f"{safe_name}.mtl")
    mtl_filename = f"{safe_name}.mtl"

    mesh = obj.mesh
    mat = obj.material
    world_verts = obj.world_vertices()

    lines = [
        f"# Exported by blender-3d-asset-pipeline",
        f"# Object: {obj.name}",
        f"mtllib {mtl_filename}",
        f"o {safe_name}",
        "",
    ]

    # Vertices
    for v in world_verts:
        lines.append(f"v {v[0]:.6f} {v[1]:.6f} {v[2]:.6f}")

    lines.append("")

    # UVs
    has_uvs = mesh.uvs is not None and len(mesh.uvs) > 0
    if has_uvs:
        for uv in mesh.uvs:
            lines.append(f"vt {uv[0]:.6f} {uv[1]:.6f}")
        lines.append("")

    # Normals
    for n in mesh.normals:
        lines.append(f"vn {n[0]:.6f} {n[1]:.6f} {n[2]:.6f}")

    lines.append("")
    lines.append(f"usemtl {mat.name}")
    lines.append("s 1")
    lines.append("")

    # Faces (OBJ is 1-indexed)
    for face in mesh.faces:
        i0, i1, i2 = face[0] + 1, face[1] + 1, face[2] + 1
        if has_uvs:
            lines.append(f"f {i0}/{i0}/{i0} {i1}/{i1}/{i1} {i2}/{i2}/{i2}")
        else:
            lines.append(f"f {i0}//{i0} {i1}//{i1} {i2}//{i2}")

    with open(obj_path, "w") as f:
        f.write("\n".join(lines))

    # Write MTL
    with open(mtl_path, "w") as f:
        f.write(f"# Material for {obj.name}\n")
        f.write(mat.to_mtl())
        f.write("\n")

    return obj_path


def export_scene(scene: Scene, output_dir: str) -> List[str]:
    """
    Export all objects in a scene.
    Each object becomes its own .obj + .mtl pair.
    Returns list of exported .obj paths.
    """
    exported = []
    for obj in scene.objects:
        prefixed_obj = SceneObject(
            name=f"{scene.name}_{obj.name}",
            mesh=obj.mesh,
            material=obj.material,
            transform=obj.transform,
        )
        path = export_object(prefixed_obj, output_dir)
        exported.append(path)
        print(f"  ✓ Exported: {path}")
    return exported


def export_scene_combined(scene: Scene, output_dir: str) -> str:
    """
    Export all objects into a single .obj file (like Blender's
    'Export Selected' with all objects in one file).
    """
    os.makedirs(output_dir, exist_ok=True)
    obj_path = os.path.join(output_dir, f"{scene.name}.obj")
    mtl_path = os.path.join(output_dir, f"{scene.name}.mtl")
    mtl_filename = f"{scene.name}.mtl"

    obj_lines = [
        f"# Exported by blender-3d-asset-pipeline",
        f"# Scene: {scene.name}",
        f"mtllib {mtl_filename}",
        "",
    ]
    mtl_lines = [f"# Materials for scene: {scene.name}\n"]

    vert_offset = 0
    uv_offset = 0
    normal_offset = 0

    for obj in scene.objects:
        mesh = obj.mesh
        mat = obj.material
        world_verts = obj.world_vertices()
        safe_name = obj.name.replace(" ", "_")

        obj_lines.append(f"o {safe_name}")

        for v in world_verts:
            obj_lines.append(f"v {v[0]:.6f} {v[1]:.6f} {v[2]:.6f}")

        has_uvs = mesh.uvs is not None and len(mesh.uvs) > 0
        if has_uvs:
            for uv in mesh.uvs:
                obj_lines.append(f"vt {uv[0]:.6f} {uv[1]:.6f}")

        for n in mesh.normals:
            obj_lines.append(f"vn {n[0]:.6f} {n[1]:.6f} {n[2]:.6f}")

        obj_lines.append(f"usemtl {mat.name}")
        obj_lines.append("s 1")

        for face in mesh.faces:
            i0 = face[0] + 1 + vert_offset
            i1 = face[1] + 1 + vert_offset
            i2 = face[2] + 1 + vert_offset
            if has_uvs:
                t0 = face[0] + 1 + uv_offset
                t1 = face[1] + 1 + uv_offset
                t2 = face[2] + 1 + uv_offset
                n0 = face[0] + 1 + normal_offset
                n1 = face[1] + 1 + normal_offset
                n2 = face[2] + 1 + normal_offset
                obj_lines.append(f"f {i0}/{t0}/{n0} {i1}/{t1}/{n1} {i2}/{t2}/{n2}")
            else:
                n0 = face[0] + 1 + normal_offset
                n1 = face[1] + 1 + normal_offset
                n2 = face[2] + 1 + normal_offset
                obj_lines.append(f"f {i0}//{n0} {i1}//{n1} {i2}//{n2}")

        obj_lines.append("")
        vert_offset += len(world_verts)
        if has_uvs:
            uv_offset += len(mesh.uvs)
        normal_offset += len(mesh.normals)

        mtl_lines.append(mat.to_mtl())
        mtl_lines.append("")

    with open(obj_path, "w") as f:
        f.write("\n".join(obj_lines))

    with open(mtl_path, "w") as f:
        f.write("\n".join(mtl_lines))

    print(f"  ✓ Combined export: {obj_path}")
    return obj_path
