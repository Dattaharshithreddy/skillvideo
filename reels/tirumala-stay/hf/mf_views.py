"""Render every Model Forge guest house alone from 4 sides (front = -Y after glTF import), to check orientation/quality."""
import bpy, glob, math, os
from mathutils import Vector
out = '/out/mfviews'; os.makedirs(out, exist_ok=True)
for path in sorted(glob.glob('/out/mf/b_*_m.glb')):
    k = os.path.basename(path)[2:-6]
    bpy.ops.wm.read_factory_settings(use_empty=True)
    s = bpy.context.scene; s.render.engine = 'CYCLES'; s.cycles.device = 'GPU'; s.cycles.samples = 32
    p = bpy.context.preferences.addons['cycles'].preferences; p.compute_device_type = 'OPTIX'; p.get_devices()
    for d in p.devices: d.use = d.type != 'CPU'
    s.render.resolution_x = s.render.resolution_y = 640
    bpy.ops.import_scene.gltf(filepath=path)
    objs = [o for o in s.objects if o.type == 'MESH']
    pts = [o.matrix_world @ Vector(c) for o in objs for c in o.bound_box]
    lo = Vector((min(p.x for p in pts), min(p.y for p in pts), min(p.z for p in pts))); hi = Vector((max(p.x for p in pts), max(p.y for p in pts), max(p.z for p in pts)))
    ctr = (lo + hi) / 2; r = (hi - lo).length
    print('MFVIEW', k, 'size', [round(v, 2) for v in (hi - lo)])
    w = bpy.data.worlds.new('w'); s.world = w; w.use_nodes = True; w.node_tree.nodes['Background'].inputs['Strength'].default_value = 1.0
    bpy.ops.object.light_add(type='SUN', rotation=(0.8, 0.2, 0.6)); bpy.context.object.data.energy = 3
    bpy.ops.object.camera_add(); cam = bpy.context.object; s.camera = cam
    for i, az in enumerate((-90, 0, 90, 180)):
        a = math.radians(az); cam.location = ctr + Vector((math.cos(a), math.sin(a), 0.45)) * r * 1.1
        cam.rotation_euler = (ctr - cam.location).to_track_quat('-Z', 'Y').to_euler()
        s.render.filepath = f'{out}/{k}_{i}.jpg'; s.render.image_settings.file_format = 'JPEG'
        bpy.ops.render.render(write_still=True)
