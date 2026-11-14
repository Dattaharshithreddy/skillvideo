"""Probe: Raju landmarks + Z-Anatomy organ centres in native coordinates (for X-ray fitting)."""
import bpy, os, sys, json
from mathutils import Vector
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
FBX = os.environ.get('ZA_FBX', '/opt/reel/za/Resources/Models/FBX/')
for o in list(bpy.data.objects): bpy.data.objects.remove(o, do_unlink=True)
RAJU_BLEND = os.environ.get('RAJU_BLEND', '/opt/reel/raju.blend')
with bpy.data.libraries.load(RAJU_BLEND, link=False) as (src, dst):
    dst.objects = [n for n in src.objects]
for o in dst.objects:
    if o is not None: bpy.context.scene.collection.objects.link(o)
bpy.context.view_layer.update()
rig = bpy.data.objects['raju_rig']
out = {'objects': [(o.name, o.type, len(o.data.vertices) if o.type == 'MESH' else 0) for o in bpy.data.objects]}
bones = {b.name: list(rig.matrix_world @ b.head_local) for b in rig.data.bones}
out['bones'] = {k: [round(x, 3) for x in v] for k, v in bones.items() if any(s in k for s in ('head', 'eye', 'neck', 'spine', 'pelvis', 'root', 'upperleg01', 'clavicle'))}
body = max((o for o in bpy.data.objects if o.type == 'MESH'), key=lambda o: len(o.data.vertices))
pts = [body.matrix_world @ v.co for v in body.data.vertices]
mn = Vector([min(p[i] for p in pts) for i in range(3)]); mx = Vector([max(p[i] for p in pts) for i in range(3)])
out['body'] = [body.name, [round(x, 3) for x in mn], [round(x, 3) for x in mx]]
# anatomy native centres
def imp(f):
    before = set(bpy.data.objects); bpy.ops.import_scene.fbx(filepath=FBX + f); return [o for o in bpy.data.objects if o not in before]
def ctr(objs):
    bpy.context.view_layer.update()
    ps = [o.matrix_world @ Vector(c) for o in objs for c in o.bound_box]
    a = Vector([min(p[i] for p in ps) for i in range(3)]); b = Vector([max(p[i] for p in ps) for i in range(3)])
    return [round(x, 4) for x in (a + b) / 2], [round(x, 4) for x in b - a]
new = imp('CardioVascular41.fbx')
hearts = [o for o in new if o.type == 'MESH' and any(o.name.startswith(k) for k in ('Right ventricle', 'Left ventricle', 'Right atrium', 'Left atrium'))]
out['heart'] = ctr(hearts)
arts = [o for o in new if o.type == 'MESH' and not o.name.endswith('.j') and ('artery' in o.name.lower() or 'aort' in o.name.lower())]
out['n_arteries'] = len(arts); out['arteries_box'] = ctr(arts)
out['artery_names_sample'] = sorted(o.name for o in arts)[:400:8]
new2 = imp('VisceralSystem100.fbx')
out['kidneys'] = ctr([o for o in new2 if o.name in ('Kidney.l', 'Kidney.r')])
st = [o for o in new2 if o.type == 'MESH' and o.name.lower().startswith('stomach')]
out['stomach'] = ctr(st) if st else None
new3 = imp('NervousSystem100.fbx')
def desc(o):
    r = []
    for c in o.children: r.append(c); r += desc(c)
    return r
br = [d for g in ('Cerebrum.g', 'Cerebellum.g', 'Brainstem.g') if g in bpy.data.objects for d in desc(bpy.data.objects[g]) if d.type == 'MESH']
out['brain'] = ctr(br)
ey = [d for d in desc(bpy.data.objects['Eyeball.g']) if d.type == 'MESH' and d.name.endswith('.r')] if 'Eyeball.g' in bpy.data.objects else []
out['eye_r'] = ctr(ey)
eyl = [d for d in desc(bpy.data.objects['Eyeball.g']) if d.type == 'MESH' and d.name.endswith('.l')] if 'Eyeball.g' in bpy.data.objects else []
out['eye_l'] = ctr(eyl) if eyl else None
print('PROBE', json.dumps(out))
