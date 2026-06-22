# 🧊 Blender 3D Asset Pipeline

A Python-based 3D asset processing pipeline inspired by Blender workflows. This project demonstrates procedural geometry generation, UV mapping simulation, material assignment, and export to standard 3D formats — all without requiring a live Blender installation.

## 🔧 Features

- **Procedural Mesh Generation** — Create primitive geometry (cube, sphere, cylinder, plane) with configurable parameters
- **UV Mapping Simulation** — Auto-generate UV coordinates for texture mapping
- **Material Assignment** — Apply PBR-style material properties (albedo, roughness, metalness)
- **OBJ / MTL Export** — Export meshes to industry-standard `.obj` + `.mtl` format
- **Scene Graph** — Compose multi-object scenes with transforms (translate, rotate, scale)
- **Batch Processing** — Process entire asset folders via CLI

## 📁 Project Structure

```
blender-3d-asset-pipeline/
├── src/
│   ├── mesh.py          # Mesh data structures & geometry primitives
│   ├── uv.py            # UV unwrapping utilities
│   ├── material.py      # PBR material definitions
│   ├── scene.py         # Scene graph & object transforms
│   ├── exporter.py      # OBJ/MTL export pipeline
│   └── pipeline.py      # End-to-end CLI pipeline
├── samples/             # Sample scene configs (JSON)
├── exports/             # Output .obj / .mtl files
├── requirements.txt
└── README.md
```

## 🚀 Quickstart

```bash
# Install dependencies
pip install -r requirements.txt

# Run the demo pipeline (generates a sample scene and exports OBJ)
python src/pipeline.py --scene samples/demo_scene.json --output exports/

# Generate a single primitive
python src/pipeline.py --primitive cube --subdivisions 2 --output exports/
```

## 🗂️ Sample Scene Format

```json
{
  "name": "demo_scene",
  "objects": [
    {
      "name": "ground_plane",
      "type": "plane",
      "scale": [5.0, 5.0, 1.0],
      "position": [0, 0, 0],
      "material": { "albedo": [0.8, 0.8, 0.8], "roughness": 0.9, "metalness": 0.0 }
    },
    {
      "name": "hero_cube",
      "type": "cube",
      "scale": [1.0, 1.0, 1.0],
      "position": [0, 0, 1],
      "material": { "albedo": [0.2, 0.5, 1.0], "roughness": 0.3, "metalness": 0.8 }
    }
  ]
}
```

## 🛠️ Tech Stack

- **Python 3.10+**
- **NumPy** — vector/matrix math for transforms
- **Trimesh** — mesh validation & format utilities
- **Click** — CLI interface

## 📦 Relevant Skills

This project maps directly to experience with:
- **Blender** (procedural modeling, UV unwrapping, material nodes, OBJ export)
- **Maya / Cinema 4D / 3ds Max** (scene graph, transforms, PBR materials)
- **Python scripting** for 3D pipelines (Blender's `bpy` module patterns)

## 📸 Example Output

Running the demo scene produces:

```
exports/
├── demo_scene_ground_plane.obj
├── demo_scene_ground_plane.mtl
├── demo_scene_hero_cube.obj
└── demo_scene_hero_cube.mtl
```

---

Built by [Sunny](https://github.com/sunny925bay-jpg) · Inspired by real-world 3D asset pipelines used in game development and VFX.
