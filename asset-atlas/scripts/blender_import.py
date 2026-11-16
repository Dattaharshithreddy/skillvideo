"""Turn a folder of downloaded models into one .blend asset library.

  blender -b -P scripts/blender_import.py -- --src assets/kaykit-city --out library/kaykit-city.blend
  blender -b -P scripts/blender_import.py -- --src assets/kaykit-city --out library/kaykit-city.blend --match building,car

Each model file becomes one collection named after the file, marked as a Blender asset, so it
shows up in the Asset Browser (add the library/ folder under Preferences > File Paths > Asset
Libraries) and can be linked or appended into any reel scene by name:

  bpy.ops.wm.append(directory=".../kaykit-city.blend/Collection/", filename="building_A")

Works with glTF/GLB, FBX and OBJ. Also runs with the `bpy` pip module: python3 blender_import.py --src ... --out ...
"""
import argparse, pathlib, sys

import bpy

EXTS = (".glb", ".gltf", ".fbx", ".obj")


def args():
    argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else sys.argv[1:]
    p = argparse.ArgumentParser()
    p.add_argument("--src", required=True)
    p.add_argument("--out", required=True)
    p.add_argument("--match", default="", help="comma-separated words; keep files whose name contains any")
    p.add_argument("--prefer", default="glb,gltf,fbx,obj", help="when the same model exists in several formats")
    p.add_argument("--limit", type=int, default=0)
    return p.parse_args(argv)


def pick_files(src, match, prefer):
    order = {"." + e: i for i, e in enumerate(prefer.split(","))}
    best = {}
    for f in sorted(pathlib.Path(src).rglob("*")):
        if f.suffix.lower() not in EXTS or "unity" in str(f.parent).lower():
            continue
        if match and not any(m in f.stem.lower() for m in match):
            continue
        k = f.stem.lower()
        if k not in best or order.get(f.suffix.lower(), 9) < order.get(best[k].suffix.lower(), 9):
            best[k] = f
    return list(best.values())


def import_one(f):
    ext = f.suffix.lower()
    if ext in (".glb", ".gltf"):
        bpy.ops.import_scene.gltf(filepath=str(f))
    elif ext == ".fbx":
        bpy.ops.import_scene.fbx(filepath=str(f))
    else:
        bpy.ops.wm.obj_import(filepath=str(f))


def main():
    a = args()
    match = [m.strip().lower() for m in a.match.split(",") if m.strip()]
    files = pick_files(a.src, match, a.prefer)
    if a.limit:
        files = files[: a.limit]
    if not files:
        sys.exit(f"no model files under {a.src}")

    bpy.ops.wm.read_factory_settings(use_empty=True)
    scene = bpy.context.scene
    ok, failed = 0, []
    for f in files:
        before = set(bpy.data.objects)
        try:
            import_one(f)
        except Exception as e:  # one broken file must not stop the batch
            failed.append((f.name, str(e)[:80]))
            continue
        new = [o for o in bpy.data.objects if o not in before]
        if not new:
            failed.append((f.name, "imported nothing"))
            continue
        col = bpy.data.collections.new(f.stem)
        scene.collection.children.link(col)
        for o in new:
            for c in list(o.users_collection):
                c.objects.unlink(o)
            col.objects.link(o)
        col.asset_mark()
        col.asset_data.description = f"from {f.name}"
        col.asset_data.tags.new(pathlib.Path(a.src).name)
        ok += 1

    out = pathlib.Path(a.out).resolve()
    out.parent.mkdir(parents=True, exist_ok=True)
    bpy.ops.file.pack_all()  # keep textures inside the .blend so the library is one portable file
    bpy.ops.wm.save_as_mainfile(filepath=str(out))
    print(f"ATLAS: {ok} assets -> {out}")
    for name, why in failed:
        print(f"ATLAS: skipped {name}: {why}")


if __name__ == "__main__":
    main()
