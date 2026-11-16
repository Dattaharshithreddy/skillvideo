"""Line up the downloaded Sketchfab models on a ground plane under an HDRI and render one preview image; print real-world sizes."""
import bpy, json, math, os
from mathutils import Vector
D = '/opt/reel/assets/sf'; man = json.load(open(f'{D}/manifest.json'))
import sys
if '--' in sys.argv: man = {k: man[k] for k in sys.argv[sys.argv.index('--') + 1:]}
bpy.ops.wm.read_factory_settings(use_empty=True); sc = bpy.context.scene
def bbox(objs):
    pts = [o.matrix_world @ Vector(c) for o in objs if o.type == 'MESH' for c in o.bound_box]
    return Vector([min(p[i] for p in pts) for i in range(3)]), Vector([max(p[i] for p in pts) for i in range(3)])
x = 0.0; sizes = {}
for key in man:
    gl = [os.path.join(r, f) for r, _, fs in os.walk(f'{D}/{key}') for f in fs if f.endswith('.gltf')]
    if not gl: continue
    before = set(bpy.data.objects); bpy.ops.import_scene.gltf(filepath=gl[0]); new = [o for o in bpy.data.objects if o not in before]
    J = json.load(open(gl[0])); base = os.path.dirname(gl[0]); print('EXT', key, J.get('extensionsUsed'), 'meshes', len([o for o in new if o.type == 'MESH']), 'anims', len(J.get('animations', [])))
    for mj in J.get('materials', []):
        sg = (mj.get('extensions') or {}).get('KHR_materials_pbrSpecularGlossiness'); bm = bpy.data.materials.get(mj.get('name', ''))
        if not sg or bm is None or not bm.use_nodes: continue
        pb_ = bm.node_tree.nodes.get('Principled BSDF')
        if pb_ is None or pb_.inputs['Base Color'].links: continue
        if 'diffuseTexture' in sg:
            uri = J['images'][J['textures'][sg['diffuseTexture']['index']]['source']].get('uri')
            if uri and os.path.exists(os.path.join(base, uri)):
                tx = bm.node_tree.nodes.new('ShaderNodeTexImage'); tx.image = bpy.data.images.load(os.path.join(base, uri)); bm.node_tree.links.new(tx.outputs['Color'], pb_.inputs['Base Color']); continue
        if 'diffuseFactor' in sg: pb_.inputs['Base Color'].default_value = sg['diffuseFactor']
    roots = [o for o in new if o.parent is None]; bpy.context.view_layer.update()
    lo, hi = bbox(new); d = hi - lo; sizes[key] = [round(v, 2) for v in d]
    # scale anything that is clearly not in metres to a plausible size (vehicles ~ length, people ~ height)
    target = {'bus': 11.0, 'car': 4.0, 'bul': 4.5, 'wal': 1.7, 'bar': 2.0}[key[:3]]
    print('MATS', key, len([o for o in new if o.type=='MESH']), sorted({(m.name if m else None) for o in new if o.type=='MESH' for m in o.data.materials})[:8])
    ref = d.z if key.startswith('wal') else max(d.x, d.y)
    k = target / ref if ref > 0 else 1
    e = bpy.data.objects.new(key + '_root', None); sc.collection.objects.link(e)
    for r in roots: r.parent = e
    e.scale = (k, k, k); bpy.context.view_layer.update(); lo, hi = bbox(new)
    e.location = (x - lo.x, -(lo.y + hi.y) / 2, -lo.z); x += (hi.x - lo.x) + 2.0
print('SIZES', json.dumps(sizes))
bpy.ops.mesh.primitive_plane_add(size=400, location=(x / 2, 0, 0))
w = bpy.data.worlds.new('w'); sc.world = w; w.use_nodes = True; env = w.node_tree.nodes.new('ShaderNodeTexEnvironment')
env.image = bpy.data.images.load('/opt/reel/assets/ph/h/golden_bay.exr'); w.node_tree.links.new(env.outputs[0], w.node_tree.nodes['Background'].inputs[0])
cd = bpy.data.cameras.new('c'); cam = bpy.data.objects.new('c', cd); sc.collection.objects.link(cam); sc.camera = cam
cam.location = (x / 2, -x * 0.75, x * 0.22); cd.lens = 35
t = bpy.data.objects.new('t', None); sc.collection.objects.link(t); t.location = (x / 2, 0, 1.2)
cc = cam.constraints.new('TRACK_TO'); cc.target = t
sc.render.engine = 'BLENDER_EEVEE_NEXT'; sc.render.resolution_x, sc.render.resolution_y = 1800, 700
sc.view_settings.view_transform = 'AgX'; sc.render.image_settings.file_format = 'JPEG'; sc.render.filepath = '/opt/reel/share/e1376f7f43dd/models_lineup.jpg'
bpy.ops.render.render(write_still=True); print('PREVIEW_DONE')
