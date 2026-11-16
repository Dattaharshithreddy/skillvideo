---
name: 3d-asset-atlas
description: Find, download and import free 3D models, environments and generators (trains, humans, kings, buildings, temples, rocks, hills, trees, anatomy, space) for Blender reels. Use before modelling anything from scratch, and whenever a 3D scene needs an asset, a location, a sky or a character.
---

# 3d-asset-atlas

Use this before building any object by hand in Blender. Modelling from scratch is the last resort.

All commands below run from this folder (`asset-atlas/` inside the cgi-shorts skill): `cd <skill dir>/asset-atlas` first. Its `scripts/` is not the skill's top-level `scripts/`.
For Poly Haven inside a scene script, the skill's own `cz.ph_model / ph_hdri / ph_material` helpers already do the job; use `atlas.py` for everything else.

## Steps for every scene

1. List the things the shot needs (set, hero objects, characters, sky).
2. Pick ONE style for the whole video, low-poly or photoreal, and stay in that column of `SUBJECTS.md`.
3. For each thing run `python3 scripts/atlas.py find <subject>`. Read `SUBJECTS.md` for the ranked choice and known gaps.
4. Get it:
   - GitHub pack: `atlas.py fetch <id>` (Polygonal Mind sets: add `--set <name>`).
   - Poly Haven: `atlas.py polyhaven search <words> [--type models|hdris|textures]` then `polyhaven get <id> --res 2k`.
   - `manual` sources (Kenney, Quaternius, Sketchfab): the server usually cannot log in or click through. Tell the user exactly which pack to download and where to unzip it (`assets/<source>-<pack>/`). Do not substitute a different-looking asset silently.
   - Generators (MPFB2, Blosm, BlenderGIS, tree/building generators, Molecular Nodes): install the addon once on the render machine, then drive it from Python.
5. Build a library: `blender -b -P scripts/blender_import.py -- --src assets/<id> --out library/<id>.blend [--match word1,word2]`.
6. In the scene script, append by name:
   `bpy.ops.wm.append(directory="<abs>/library/<id>.blend/Collection/", filename="<model file name without extension>")`
7. Before delivering the video run `atlas.py credits` and give the user the lines to put in the caption.

## Rules

- Check `LICENSES.md`. Never use CC BY-NC assets or assets with no licence. CC-BY and CC-BY-SA need a caption credit: always report it.
- Scale: low-poly packs are not in metres (a KayKit building is ~2 units wide, a car 0.4). Scale the whole set to the hero character, do not scale pieces individually.
- Poly Haven models at 4k/8k are heavy. Use 1k-2k for 9:16 reels unless it is a close-up.
- Real places: Blosm for buildings/roads/railways, BlenderGIS for terrain. Use both for an accurate location.
- Real anatomy: Z-Anatomy. Do not approximate organs with primitives when accuracy matters.
- If nothing fits, say so and propose: generate the model (AI model generator or MPFB2), or model it. Do not fake a match.
- Adding a source: edit `catalog/build_catalog.py`, run it, commit. Record the licence exactly as its file states it.
