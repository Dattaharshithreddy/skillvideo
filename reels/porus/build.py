"""Porus / Hydaspes story: real Jhelum terrain (Copernicus DEM + Sentinel-2 + OSM river) with low-poly CC0 armies
(Quaternius knight, horse, king; OpenGameArt CC0 elephant). One shot per story paragraph."""
import bpy, json, math, os, random, subprocess
import numpy as np
from mathutils import Vector, Matrix
HERE = os.path.dirname(os.path.abspath(__file__)); os.chdir(HERE); random.seed(5)
FPS = 30; GLB = '/opt/reel/assets/qs/public/glb/'
plan = json.load(open('brief/plan.json'))
durs = [float(subprocess.run(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0', l['audio']], capture_output=True, text=True).stdout) + plan['gap'] for l in plan['lines']]
starts, t = [], 0.0
for d in durs: starts.append(t); t += d
SH = [(round(s * FPS) + 1, round((s + d) * FPS)) for s, d in zip(starts, durs)]
END = SH[-1][1] + 45
SHOT = {l['shot']: i for i, l in enumerate(plan['lines'])}
def S(n): return SH[SHOT[n]]
def fr(n, x): a, b = S(n); return int(a + (b - a) * x)
json.dump({'starts': starts, 'durs': durs, 'end': END, 'lines': [{'text': l['text'], 'keywords': l['keywords'], 'shot': l['shot']} for l in plan['lines']]},
          open('brief/timing.json', 'w'), indent=1, ensure_ascii=False)
bpy.ops.wm.read_factory_settings(use_empty=True)
sc = bpy.context.scene; sc.frame_start, sc.frame_end, sc.render.fps = 1, END, FPS
V = Vector

# ---------------- helpers ----------------
def fcurves(idb):
    ad = idb.animation_data
    if not ad or not ad.action: return []
    out = []
    for layer in getattr(ad.action, 'layers', []):
        for strip in layer.strips:
            for cb in strip.channelbags: out += list(cb.fcurves)
    if not out and hasattr(ad.action, 'fcurves'): out = list(ad.action.fcurves)
    return out
def act_fcurves(act):
    out = []
    for layer in getattr(act, 'layers', []):
        for strip in layer.strips:
            for cb in strip.channelbags: out += list(cb.fcurves)
    if not out and hasattr(act, 'fcurves'): out = list(act.fcurves)
    return out
def const(idb, path=None):
    for fc in fcurves(idb):
        if path is None or fc.data_path == path:
            for kp in fc.keyframe_points: kp.interpolation = 'CONSTANT'
def show(o, ranges):
    base = tuple(o.scale); o.scale = (0, 0, 0); o.keyframe_insert('scale', frame=1)
    for a, b in ranges:
        o.scale = base; o.keyframe_insert('scale', frame=a); o.scale = (0, 0, 0); o.keyframe_insert('scale', frame=b)
    const(o, 'scale')
def emis(name, col, s):
    m = bpy.data.materials.new(name); m.use_nodes = True; nt = m.node_tree
    for n in list(nt.nodes): nt.nodes.remove(n)
    e = nt.nodes.new('ShaderNodeEmission'); o = nt.nodes.new('ShaderNodeOutputMaterial')
    e.inputs['Color'].default_value = (*col, 1); e.inputs['Strength'].default_value = s; nt.links.new(e.outputs[0], o.inputs[0]); return m
def pbr(name, col, rough=0.6, metal=0.0):
    m = bpy.data.materials.new(name); m.use_nodes = True; b = m.node_tree.nodes['Principled BSDF']
    b.inputs['Base Color'].default_value = (*col, 1); b.inputs['Roughness'].default_value = rough; b.inputs['Metallic'].default_value = metal; return m
def box(name, loc, dims, m):
    bpy.ops.mesh.primitive_cube_add(location=loc); o = bpy.context.object; o.name = name
    o.scale = (dims[0] / 2, dims[1] / 2, dims[2] / 2); bpy.ops.object.transform_apply(scale=True); o.data.materials.append(m); return o
def coll(name):
    c = bpy.data.collections.new(name); sc.collection.children.link(c); return c
def move_to(objs, c):
    for o in objs:
        for uc in list(o.users_collection): uc.objects.unlink(o)
        c.objects.link(o)

# ---------------- terrain + river ----------------
meta = json.load(open('geo/meta.json')); dem = np.load('geo/dem.npy'); h, w = dem.shape; RES = meta['res']
OX, OY = meta['origin']; ZB = float(dem.min())
def elev(x, y):
    c = (x + OX - meta['x0']) / RES - 0.5; r = (meta['y1'] - (y + OY)) / RES - 0.5
    c = min(max(c, 0), w - 1.001); r = min(max(r, 0), h - 1.001); c0, r0 = int(c), int(r); fc, fq = c - c0, r - r0
    return float(dem[r0, c0] * (1 - fc) * (1 - fq) + dem[r0, c0 + 1] * fc * (1 - fq) + dem[r0 + 1, c0] * (1 - fc) * fq + dem[r0 + 1, c0 + 1] * fc * fq) - ZB
def ground(p, lift=0.0): return V((p.x, p.y, elev(p.x, p.y) + lift))
xs = meta['x0'] + (np.arange(w) + 0.5) * RES - OX; ys = meta['y1'] - (np.arange(h) + 0.5) * RES - OY
X, Y = np.meshgrid(xs, ys)
verts = np.stack([X.ravel(), Y.ravel(), (dem - ZB).ravel()], 1).astype(np.float32)
ii = np.arange(h * w).reshape(h, w)
quads = np.stack([ii[:-1, :-1].ravel(), ii[1:, :-1].ravel(), ii[1:, 1:].ravel(), ii[:-1, 1:].ravel()], 1)
me = bpy.data.meshes.new('terrain'); me.vertices.add(len(verts)); me.vertices.foreach_set('co', verts.ravel())
me.loops.add(quads.size); me.loops.foreach_set('vertex_index', quads.ravel().astype(np.int32))
me.polygons.add(len(quads)); me.polygons.foreach_set('loop_start', np.arange(0, quads.size, 4, dtype=np.int32)); me.polygons.foreach_set('loop_total', np.full(len(quads), 4, np.int32))
uv = me.uv_layers.new(name='UV'); vi = quads.ravel()
uv.data.foreach_set('uv', np.stack([(vi % w) / (w - 1), 1 - (vi // w) / (h - 1)], 1).astype(np.float32).ravel())
me.update(); me.validate(); me.polygons.foreach_set('use_smooth', [True] * len(me.polygons))
terr = bpy.data.objects.new('terrain', me); sc.collection.objects.link(terr)
tm = bpy.data.materials.new('terrain'); tm.use_nodes = True; nt = tm.node_tree; bs = nt.nodes['Principled BSDF']; bs.inputs['Roughness'].default_value = 0.95
if os.path.exists('geo/s2.png'):
    img = nt.nodes.new('ShaderNodeTexImage'); img.image = bpy.data.images.load(os.path.abspath('geo/s2.png')); img.interpolation = 'Cubic'
    hsv = nt.nodes.new('ShaderNodeHueSaturation'); hsv.inputs['Saturation'].default_value = 1.1; hsv.inputs['Value'].default_value = 1.5
    nt.links.new(img.outputs['Color'], hsv.inputs['Color']); nt.links.new(hsv.outputs['Color'], bs.inputs['Base Color'])
terr.data.materials.append(tm)
riv = [V((x - OX, y - OY, 0)) for x, y in json.load(open('geo/river.json'))['river']]
HW, HH = (w - 4) * RES / 2, (h - 4) * RES / 2
inside = [abs(p.x) < HW and abs(p.y) < HH for p in riv]
best, cur = [], []
for p, ok in zip(riv, inside):
    if ok: cur.append(p)
    else:
        if len(cur) > len(best): best = cur
        cur = []
if len(cur) > len(best): best = cur
R = [best[0]]
for p in best[1:]:
    if (p - R[-1]).length > 60: R.append(p)
for _ in range(3): R = [R[0]] + [(R[i - 1] + R[i] * 2 + R[i + 1]) / 4 for i in range(1, len(R) - 1)] + [R[-1]]
def tangent(i): return (R[min(i + 1, len(R) - 1)] - R[max(i - 1, 0)]).normalized()
RW = 380.0
wl = []; wverts = []
for i, p in enumerate(R):
    tn = tangent(i); nn = V((-tn.y, tn.x, 0))
    z = min(elev(*(p + nn * k).xy) for k in (-150, 0, 150)) + 1.5
    wverts += [(p + nn * RW / 2).to_tuple()[:2] + (z,), (p - nn * RW / 2).to_tuple()[:2] + (z,)]
wm = bpy.data.meshes.new('river'); wm.from_pydata(wverts, [], [(2 * i, 2 * i + 1, 2 * i + 3, 2 * i + 2) for i in range(len(R) - 1)])
riverO = bpy.data.objects.new('river', wm); sc.collection.objects.link(riverO)
M_water = pbr('water', (0.08, 0.16, 0.2), 0.08); riverO.data.materials.append(M_water)
# battle reference on the river: point nearest the centre
bi = min(range(len(R)), key=lambda i: R[i].length)
B = R[bi]; TU = tangent(bi); NN = V((-TU.y, TU.x, 0))
if NN.y < 0: NN = -NN                       # NN points to the north bank (Alexander's side)
up_i = max(0, bi - int(4500 / 60)) if (R[max(0, bi - 10)] - B).dot(TU) < 0 else min(len(R) - 1, bi + int(4500 / 60))
CROSS = R[up_i]                              # upstream crossing point (storm)
print('river pts', len(R), 'B', tuple(round(v) for v in B), 'NN', tuple(round(v, 2) for v in NN))

# ---------------- sky / sun (time of day per shot) ----------------
wd = bpy.data.worlds.new('w'); sc.world = wd; wd.use_nodes = True; wn = wd.node_tree
sky = wn.nodes.new('ShaderNodeTexSky'); sky.sky_type = 'NISHITA'; sky.altitude = 600; sky.air_density = 1.5; sky.dust_density = 3
bg = wn.nodes['Background']; wn.links.new(sky.outputs['Color'], bg.inputs['Color'])
bpy.ops.object.light_add(type='SUN'); sun = bpy.context.object; sun.data.angle = math.radians(1.5)
TOD = {  # shot: (sun elevation deg, sun azimuth deg, sun energy, sun colour, world strength)
    'open': (7, 250, 4.0, (1.0, 0.72, 0.45), 0.7), 'ambhi': (35, 140, 4.5, (1, 0.95, 0.88), 1.0), 'river': (18, 230, 4.5, (1, 0.85, 0.65), 0.9),
    'feint': (25, 120, 0.25, (0.55, 0.65, 1.0), 0.04), 'storm': (25, 120, 0.12, (0.5, 0.6, 1.0), 0.02), 'battle': (9, 100, 4.0, (1.0, 0.75, 0.55), 0.7),
    'king': (5, 260, 3.5, (1.0, 0.6, 0.35), 0.5), 'return': (40, 150, 4.5, (1, 0.95, 0.9), 1.0), 'murder': (30, 100, 0.0, (1, 1, 1), 0.0),
    'legacy': (2.5, 255, 5.0, (1.0, 0.55, 0.25), 0.8)}
for name, (el, az, en, col, ws) in TOD.items():
    for f in S(name):
        sky.sun_elevation = math.radians(max(el, 1)); sky.sun_rotation = math.radians(az); sky.keyframe_insert('sun_elevation', frame=f); sky.keyframe_insert('sun_rotation', frame=f)
        bg.inputs['Strength'].default_value = ws; bg.inputs['Strength'].keyframe_insert('default_value', frame=f)
        sun.rotation_euler = (math.radians(90 - el), 0, math.radians(az - 90)); sun.keyframe_insert('rotation_euler', frame=f)
        sun.data.energy = en; sun.data.keyframe_insert('energy', frame=f); sun.data.color = col; sun.data.keyframe_insert('color', frame=f)
for idb in (sun, sun.data, wd.node_tree): const(idb)
for fc in act_fcurves(wd.node_tree.animation_data.action) if wd.node_tree.animation_data else []:
    for kp in fc.keyframe_points: kp.interpolation = 'CONSTANT'
# lightning (storm): short sun spikes
lit = [fr('storm', x) for x in (0.12, 0.38, 0.41, 0.7, 0.88)]
for f in lit:
    for df, e in ((-1, 0.12), (0, 9.0), (2, 0.12)):
        sun.data.energy = e; sun.data.keyframe_insert('energy', frame=f + df)
const(sun.data)

# ---------------- assets (CC0) ----------------
SRC = coll('sources'); bpy.context.view_layer.layer_collection.children['sources'].exclude = True
def import_glb(path):
    before = set(bpy.data.objects); bpy.ops.import_scene.gltf(filepath=path); return [o for o in bpy.data.objects if o not in before]
def norm_height(objs, height, axis=2):
    bpy.context.view_layer.update()
    pts = [o.matrix_world @ V(c) for o in objs if o.type == 'MESH' for c in o.bound_box]
    d = max(p[axis] for p in pts) - min(p[axis] for p in pts); zmin = min(p[2] for p in pts)
    roots = [o for o in objs if o.parent is None]
    s = height / d
    for r in roots:
        r.scale = r.scale * s; r.location = r.location * s
    bpy.context.view_layer.update()
    pts = [o.matrix_world @ V(c) for o in objs if o.type == 'MESH' for c in o.bound_box]; zmin = min(p[2] for p in pts)
    for r in roots: r.location.z -= zmin
def set_action(objs, key):
    arm = next((o for o in objs if o.type == 'ARMATURE'), None)
    if not arm: return
    act = next((a for a in bpy.data.actions if key.lower() in a.name.lower()), None)
    if not act: return
    arm.animation_data_create(); arm.animation_data.action = act
    for fc in act_fcurves(act):
        if not any(m.type == 'CYCLES' for m in fc.modifiers): fc.modifiers.new('CYCLES')
def tint(objs, col, keep=('skin', 'face', 'eye', 'hair')):
    for o in objs:
        if o.type != 'MESH': continue
        for sl in o.material_slots:
            m = sl.material
            if not m or any(k in m.name.lower() for k in keep): continue
            nm = m.copy(); nm.name = m.name + '_' + str(col)[:12]; b = nm.node_tree.nodes.get('Principled BSDF') if nm.use_nodes else None
            if b:
                for l in list(b.inputs['Base Color'].links): nm.node_tree.links.remove(l)
                bc = b.inputs['Base Color'].default_value; lum = 0.3 * bc[0] + 0.59 * bc[1] + 0.11 * bc[2]
                k = 0.55 + 0.9 * lum; b.inputs['Base Color'].default_value = (col[0] * k, col[1] * k, col[2] * k, 1)
            sl.material = nm
def unit(name, path, height, action=None, color=None, extra=None):
    objs = import_glb(path); norm_height(objs, height)
    if color: tint(objs, color)
    if action: set_action(objs, action)
    if extra: objs += extra(objs)
    c = bpy.data.collections.new(name); SRC.children.link(c); move_to(objs, c); return c
M_spear = pbr('spear', (0.45, 0.32, 0.18), 0.6); M_tip = pbr('tip', (0.8, 0.8, 0.82), 0.3, 1.0)
def sarissa(objs):
    root = next(o for o in objs if o.parent is None)
    bpy.ops.mesh.primitive_cylinder_add(radius=0.035, depth=6.0, location=(0.35, 1.6, 1.55), rotation=(math.radians(80), 0, 0))
    sp = bpy.context.object; sp.data.materials.append(M_spear); return [sp]
BRONZE, SAFF, PURP, WHITE = (0.72, 0.42, 0.12), (1.0, 0.55, 0.1), (0.45, 0.2, 0.6), (0.92, 0.9, 0.85)
K = GLB + 'single_knight_pack/KnightCharacter.glb'
U = {'mac_walk': unit('mac_walk', K, 1.8, 'Walking', BRONZE),
     'mac_idle': unit('mac_idle', K, 1.8, 'Idle_HumanArmature', BRONZE, sarissa),
     'mac_run': unit('mac_run', K, 1.8, 'Run_HumanArmature', BRONZE),
     'por_idle': unit('por_idle', K, 1.8, 'Idle_HumanArmature', WHITE),
     'por_run': unit('por_run', K, 1.8, 'Run_HumanArmature', SAFF),
     'amb_walk': unit('amb_walk', K, 1.8, 'Walking', PURP),
     'horse': unit('horse', GLB + 'animals_pack/Horse.glb', 1.65, 'Gallop_AnimalArmature', None),
     'horse_walk': unit('horse_walk', GLB + 'animals_pack/Horse.glb', 1.65, 'Walk_AnimalArmature', None)}
# rider on horses
for key in ('horse', 'horse_walk'):
    objs = import_glb(K); norm_height(objs, 1.3); tint(objs, BRONZE); set_action(objs, 'Idle_HumanArmature')
    for r in [o for o in objs if o.parent is None]: r.location += V((0, 0.1, 1.15))
    move_to(objs, U[key])
# elephant (OpenGameArt CC0, syncopika) with a howdah
with bpy.data.libraries.load('/opt/reel/assets/elephant.blend', link=False) as (src, dst): dst.objects = list(src.objects); dst.actions = list(src.actions)
eobjs = [o for o in dst.objects if o]
for o in eobjs: sc.collection.objects.link(o)
norm_height(eobjs, 3.0)
M_hide = pbr('elephant_skin', (0.36, 0.34, 0.33), 0.85)
for o in eobjs:
    if o.type == 'MESH': o.data.materials.clear(); o.data.materials.append(M_hide)
def elephant_unit(name, action):
    c = bpy.data.collections.new(name); SRC.children.link(c)
    new = []
    for o in eobjs:
        n = o.copy(); n.data = o.data.copy() if o.type == 'MESH' else o.data; new.append(n)
    for n in new:
        if n.type == 'MESH':
            for md in n.modifiers:
                if md.type == 'ARMATURE': md.object = next(x for x in new if x.type == 'ARMATURE')
            if n.parent and n.parent.type == 'ARMATURE': n.parent = next(x for x in new if x.type == 'ARMATURE')
    for n in new: c.objects.link(n)
    arm = next(x for x in new if x.type == 'ARMATURE'); act = bpy.data.actions.get(action)
    if act:
        arm.animation_data_create(); arm.animation_data.action = act
        for fc in act_fcurves(act):
            if not any(m.type == 'CYCLES' for m in fc.modifiers): fc.modifiers.new('CYCLES')
    hb = box(name + '_howdah', (0, 0, 3.15), (1.3, 1.6, 0.6), pbr('howdah', (0.55, 0.2, 0.08), 0.5)); c.objects.link(hb); sc.collection.objects.unlink(hb)
    cl = box(name + '_cloth', (0, 0, 2.6), (1.9, 2.4, 0.08), pbr('cloth', SAFF, 0.7)); c.objects.link(cl); sc.collection.objects.unlink(cl)
    return c
U['eleph'] = elephant_unit('eleph', 'Angry'); U['eleph_idle'] = elephant_unit('eleph_idle', 'Idle')
for o in eobjs: bpy.data.objects.remove(o, do_unlink=True)
# Porus figure (king's crown on a white/saffron knight) and Alexander (bronze knight)
def hero(name, color, crown):
    objs = import_glb(K); norm_height(objs, 2.0 if crown else 1.85); tint(objs, color); set_action(objs, 'Idle_HumanArmature')
    if crown:
        bpy.ops.mesh.primitive_cone_add(vertices=8, radius1=0.16, radius2=0.2, depth=0.18, location=(0, 0, 2.0)); cr = bpy.context.object
        cr.data.materials.append(pbr('gold', (1.0, 0.75, 0.2), 0.25, 1.0)); objs.append(cr)
    c = bpy.data.collections.new(name); SRC.children.link(c); move_to(objs, c); return c
U['porus'] = hero('porus', SAFF, True); U['alex'] = hero('alex', BRONZE, False)
U['shadow'] = hero('shadow', (0.05, 0.05, 0.06), False)
def glb_unit(name, path, height):
    objs = import_glb(path); norm_height(objs, height); c = bpy.data.collections.new(name); SRC.children.link(c); move_to(objs, c); return c
U['boat'] = glb_unit('boat', GLB + 'ships_pack/Viking_boat.glb', 2.2)
U['tent'] = glb_unit('tent', GLB + 'survival_pack/Tent.glb', 3.0)
U['gate'] = glb_unit('gate', GLB + 'modular_medieval_buildings_pack/TallWallEntrance.glb', 9.0)
U['tower'] = glb_unit('tower', GLB + 'modular_medieval_buildings_pack/LargeTower.glb', 15.0)
U['wall'] = glb_unit('wall', GLB + 'modular_medieval_buildings_pack/TallWall.glb', 9.0)
U['banner'] = glb_unit('banner', GLB + 'modular_medieval_buildings_pack/Banner.glb', 4.0)

def inst(cname, loc, yaw=0.0, s=1.0, parent=None, name=None):
    o = bpy.data.objects.new(name or ('i_' + cname), None); o.instance_type = 'COLLECTION'; o.instance_collection = U[cname]
    sc.collection.objects.link(o); o.location = loc; o.rotation_euler = (0, 0, yaw); o.scale = (s, s, s)
    if parent: o.parent = parent
    return o
def empty(name, loc=(0, 0, 0)):
    e = bpy.data.objects.new(name, None); sc.collection.objects.link(e); e.location = loc; return e
def yaw_of(d): return math.atan2(d.x, -d.y)     # glTF models face -Y after import
def block(cname, centre, facing, rows, cols, dx, dy, ranges, jitter=0.3, lift=0.0):
    """formation of instances on the ground, facing direction `facing`"""
    f = facing.normalized(); side = V((f.y, -f.x, 0)); out = []
    for r in range(rows):
        for c in range(cols):
            p = centre + side * ((c - (cols - 1) / 2) * dx + random.uniform(-jitter, jitter)) - f * (r * dy + random.uniform(-jitter, jitter))
            o = inst(cname, ground(p, lift), yaw_of(f)); show(o, ranges); out.append(o)
    return out
def march(objs, a, b, d):
    for o in objs:
        o.keyframe_insert('location', frame=a); o.location += d; o.location.z = elev(o.location.x, o.location.y); o.keyframe_insert('location', frame=b)
        for fc in fcurves(o):
            if fc.data_path == 'location':
                for kp in fc.keyframe_points: kp.interpolation = 'LINEAR'

# ---------------- aerial formation markers ----------------
M_blue = emis('mac_marker', (0.25, 0.55, 1.0), 3.0); M_saff = emis('por_marker', (1.0, 0.55, 0.1), 3.0); M_purp = emis('amb_marker', (0.7, 0.3, 1.0), 3.0)
M_grey = pbr('eleph_marker', (0.55, 0.55, 0.55), 0.8)
def marker(name, centre, along, length, width, m, ranges, lift=6):
    f = along.normalized(); o = box(name, ground(centre, lift), (width, length, 4), m); o.rotation_euler = (0, 0, yaw_of(f)); show(o, ranges); return o
NB_ = B + NN * 900; SB_ = B - NN * 900
mac_col = [marker(f'mac_col{i}', NB_ + NN * 1800 - TU * (2400 - i * 650), TU, 520, 120, M_blue, [(S('open')[0], S('ambhi')[1] + 1)]) for i in range(6)]
for o in mac_col:
    o.keyframe_insert('location', frame=S('open')[0]); o.location += TU * 1500; o.location.z = elev(*o.location.xy) + 6; o.keyframe_insert('location', frame=S('ambhi')[1])
mac_camp = [marker(f'mac_camp{i}', NB_ + TU * (i - 2) * 700, TU, 500, 160, M_blue, [(S('river')[0], S('river')[1] + 1), (S('return')[0], S('return')[1] + 1)]) for i in range(5)]
por_line = [marker(f'por_line{i}', SB_ + TU * (i - 3) * 600, TU, 480, 140, M_saff, [(S('river')[0], S('river')[1] + 1), (S('return')[0], S('return')[1] + 1)]) for i in range(7)]
el_line = [marker(f'el{i}', SB_ + NN * 160 + TU * (i - 12) * 160, TU, 40, 40, M_grey, [(S('river')[0], S('river')[1] + 1)], lift=20) for i in range(25)]

# ---------------- AMBHI: Taxila gate opens, purple army joins ----------------
FORT = NB_ + NN * 2600 - TU * 3200
fd = (B - FORT); fd.z = 0; fd.normalize(); fs = V((fd.y, -fd.x, 0))
fz = elev(*FORT.xy)
inst('gate', V((FORT.x, FORT.y, fz)), yaw_of(fd)); inst('tower', V((*(FORT + fs * 14).xy, fz)), yaw_of(fd)); inst('tower', V((*(FORT - fs * 14).xy, fz)), yaw_of(fd))
for k in (2, 3, 4): inst('wall', V((*(FORT + fs * (14 + 9 * k - 13)).xy, fz)), yaw_of(fd)); inst('wall', V((*(FORT - fs * (14 + 9 * k - 13)).xy, fz)), yaw_of(fd))
for k in (-1, 1): inst('banner', V((*(FORT + fs * 6 * k + fd * 1).xy, fz + 8)), yaw_of(fd))
amb = block('amb_walk', FORT + fd * 6, fd, 8, 5, 1.6, 2.0, [(S('ambhi')[0], S('ambhi')[1] + 1)], 0.2)
march(amb, fr('ambhi', 0.25), S('ambhi')[1], fd * 40)
macw = block('mac_walk', FORT + fd * 60 + fs * 60, -fs, 6, 8, 1.6, 2.0, [(S('ambhi')[0], S('ambhi')[1] + 1)], 0.2)
march(macw, S('ambhi')[0], S('ambhi')[1], -fs * 35)

# ---------------- FEINT (night): cavalry with torches on the north bank; Porus's watch fires opposite ----------------
M_fire = emis('torch', (1.0, 0.45, 0.1), 25.0)
FN = B + NN * (RW / 2 + 40); FS = B - NN * (RW / 2 + 60)
cav = []
for i in range(14):
    p = FN + TU * (-60 + i * 4.5) + NN * random.uniform(0, 12)
    o = inst('horse', ground(p), yaw_of(TU)); show(o, [(S('feint')[0], S('storm')[1] + 1)]); cav.append(o)
    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.18, location=o.location + V((0, 0, 2.9))); t_ = bpy.context.object; t_.data.materials.append(M_fire)
    t_.parent = o; t_.location = (0.3, 0.2, 2.9); show(t_, [(S('feint')[0], S('feint')[1] + 1)])
fa, fb = S('feint')
for o in cav:
    base = o.location.copy()
    for k, f in enumerate(range(fa, fb + 1, 6)):
        ph = (f - fa) / 120.0; o.location = ground(base + TU * 70 * math.sin(ph * math.pi)); o.keyframe_insert('location', frame=f)
        o.rotation_euler.z = yaw_of(TU if math.cos(ph * math.pi) >= 0 else -TU); o.keyframe_insert('rotation_euler', frame=f, index=2)
watch = block('por_idle', FS - NN * 8, NN, 3, 12, 2.2, 2.4, [(S('feint')[0], S('feint')[1] + 1)], 0.3)
for i, o in enumerate(watch[:12]):
    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.16, location=(0, 0, 0)); t_ = bpy.context.object; t_.data.materials.append(M_fire); t_.parent = o; t_.location = (0.4, 0.2, 2.2)
    # watch fires: bright early, then fewer and fewer (they stop reacting)
    off = fr('feint', 0.35 + 0.5 * (i / 12)); show(t_, [(fa, off)])
for k in range(4):
    bpy.ops.object.light_add(type='POINT', location=ground(FN + TU * (k * 30 - 45), 4)); pl = bpy.context.object; pl.data.energy = 6000; pl.data.color = (1, 0.55, 0.2)
    pl.data.shadow_soft_size = 1.5; show(pl, [(fa, S('feint')[1] + 1)])

# ---------------- STORM: boats and horses cross upstream at night ----------------
ci = R.index(CROSS); CT = tangent(ci); CN = V((-CT.y, CT.x, 0)); CN = CN if CN.dot(NN) > 0 else -CN
wz = min(elev(*(CROSS + CN * k).xy) for k in (-150, 0, 150)) + 1.5
sa, sb = S('storm')
boats = []
for i in range(9):
    p = CROSS + CN * (RW / 2 + 10) + CT * (i - 4) * 14
    o = inst('boat', V((p.x, p.y, wz)), yaw_of(-CN), 3.0); show(o, [(sa, sb + 1)]); boats.append(o)
    o.keyframe_insert('location', frame=sa); o.location += -CN * (RW + 20); o.location.z = wz; o.keyframe_insert('location', frame=sb)
    for fc in fcurves(o):
        if fc.data_path == 'location':
            for kp in fc.keyframe_points: kp.interpolation = 'LINEAR'
    for j in range(5):
        m_ = inst('mac_idle', V((0, 0, 0)), 0, 1 / 3.0, parent=o); m_.location = (0.0, -2.0 + j * 1.0, 0.25); show(m_, [(sa, sb + 1)])
swim = []
for i in range(10):
    p = CROSS + CN * (RW / 2 + 30) + CT * (70 + i * 6)
    o = inst('horse', V((p.x, p.y, wz - 0.9)), yaw_of(-CN)); show(o, [(sa, sb + 1)]); swim.append(o)
march(swim, sa, sb, -CN * (RW + 40))
for o in swim:
    for fc in fcurves(o):
        if fc.data_path == 'location' and fc.array_index == 2:
            for kp in fc.keyframe_points: kp.co[1] = wz - 0.9

# ---------------- BATTLE (dawn) on the south bank ----------------
O = B - NN * (RW / 2 + 700)
ba, bb = S('battle')
phal = block('mac_idle', O - TU * 60, TU, 8, 16, 1.0, 1.1, [(ba, bb + 1)], 0.05)
porinf = block('por_idle', O + TU * 140, -TU, 5, 20, 1.4, 1.6, [(ba, bb + 1)], 0.3)
els = []
for i in range(7):
    p = O + TU * 95 + NN * ((i - 3) * 9)
    o = inst('eleph', ground(p), yaw_of(-TU)); show(o, [(ba, bb + 1)]); els.append(o)
# elephants charge into the phalanx with a heavy bob
for i, o in enumerate(els):
    base = o.location.copy()
    for f in range(ba, bb + 1, 3):
        tt = min(1, max(0, (f - ba - 20) / max(1, (bb - ba) * 0.55)))
        p = base - TU * (148 * tt * tt * (3 - 2 * tt)); g = ground(p); g.z += 0.25 * abs(math.sin((f - ba) / 6.0 + i)) * (1 if 0 < tt < 1 else 0)
        o.location = g; o.keyframe_insert('location', frame=f)
# cavalry sweeps around Porus's flank
cav2 = []
for i in range(24):
    p0 = O - TU * 120 - NN * (70 + (i % 6) * 3) - TU * (i // 6) * 4
    o = inst('horse', ground(p0), yaw_of(TU)); show(o, [(fr('battle', 0.3), bb + 1)]); cav2.append(o)
    for k, f in enumerate(range(fr('battle', 0.3), bb + 1, 4)):
        tt = (f - fr('battle', 0.3)) / max(1, bb - fr('battle', 0.3))
        ang = math.pi * tt; centre = O + TU * 60 - NN * 20
        p = centre - TU * 180 * math.cos(ang) - NN * (90 + (i % 6) * 3) * math.sin(ang) * 1.2 - NN * 30
        o.location = ground(p); o.keyframe_insert('location', frame=f)
        d = (-TU * 180 * -math.sin(ang) - NN * 108 * math.cos(ang)); o.rotation_euler.z = yaw_of(d.normalized()); o.keyframe_insert('rotation_euler', frame=f, index=2)

# ---------------- KING (dusk): Porus before Alexander ----------------
KG = O + TU * 20 + NN * 40
ka, kb = S('king')
pz = inst('porus', ground(KG + TU * 2.2), yaw_of(-TU)); show(pz, [(ka, kb + 1)])
az_ = inst('alex', ground(KG - TU * 2.2), yaw_of(TU)); show(az_, [(ka, kb + 1)])
guards = block('mac_idle', KG - TU * 8, TU, 2, 10, 1.3, 1.5, [(ka, kb + 1)], 0.1)
eld = inst('eleph_idle', ground(KG + TU * 14 + NN * 6), yaw_of(-TU)); show(eld, [(ka, kb + 1)])

# ---------------- RETURN: aerial map day (markers re-used) ----------------

# ---------------- MURDER: dark hall far below the terrain ----------------
HALL = V((0, 0, -3000))
M_stone = pbr('stone', (0.25, 0.22, 0.2), 0.9)
floor_ = box('hall_floor', HALL, (40, 40, 0.5), M_stone)
for k in range(-3, 4):
    for side in (-1, 1):
        bpy.ops.mesh.primitive_cylinder_add(radius=0.7, depth=10, location=HALL + V((side * 7, k * 5, 5))); col_ = bpy.context.object; col_.data.materials.append(M_stone)
box('hall_back', HALL + V((0, 16, 6)), (30, 1, 12), M_stone); box('hall_roof', HALL + V((0, 0, 10.5)), (40, 40, 0.5), M_stone)
throne = box('throne', HALL + V((0, 12, 0.8)), (2.2, 1.5, 1.6), pbr('throne', (0.5, 0.1, 0.08), 0.5))
ma, mb = S('murder')
kp_ = inst('porus', HALL + V((0, 10.5, 0.25)), math.pi); show(kp_, [(ma, mb + 1)])
sh_ = inst('shadow', HALL + V((-3.5, 3, 0.25)), yaw_of(V((0.5, 1, 0)))); show(sh_, [(ma, mb + 1)])
sh_.keyframe_insert('location', frame=ma); sh_.location = HALL + V((-0.9, 9.2, 0.25)); sh_.keyframe_insert('location', frame=fr('murder', 0.75))
torch_l = []
for k in (-1, 1):
    bpy.ops.object.light_add(type='POINT', location=HALL + V((k * 6, 12, 4))); tl = bpy.context.object; tl.data.color = (1, 0.5, 0.18); tl.data.shadow_soft_size = 0.3
    for f in range(ma, mb + 2, 3):
        dead = f > fr('murder', 0.85)
        tl.data.energy = 0 if dead else 900 * (0.8 + 0.4 * random.random()); tl.data.keyframe_insert('energy', frame=f)
    for f in (1, ma - 1, mb + 2):
        tl.data.energy = 0; tl.data.keyframe_insert('energy', frame=f)
    const(tl.data)

# ---------------- LEGACY: Porus on his elephant on a ridge at sunset ----------------
RIDGE_i = int(np.argmax(dem)); rr, rc = divmod(RIDGE_i, w)
RIDGE = V((xs[rc], ys[rr], 0)); RIDGE = RIDGE + (B - RIDGE).normalized() * 250
la, lb = S('legacy')
le = inst('eleph_idle', ground(RIDGE), yaw_of(V((math.cos(math.radians(255)), math.sin(math.radians(255)), 0)))); show(le, [(la, END + 1)])
lp = inst('porus', ground(RIDGE, 3.3), le.rotation_euler.z); show(lp, [(la, END + 1)])

# ---------------- cameras ----------------
cd = bpy.data.cameras.new('cam'); cam = bpy.data.objects.new('cam', cd); sc.collection.objects.link(cam); sc.camera = cam
cd.sensor_width = 24; cd.clip_start = 0.3; cd.clip_end = 60000
tgt = empty('cam_target'); c_ = cam.constraints.new('TRACK_TO'); c_.target = tgt; c_.track_axis = 'TRACK_NEGATIVE_Z'; c_.up_axis = 'UP_Y'
KEYS = []
def KK(f, cpos, tpos, ln): KEYS.append((int(f), V(cpos), V(tpos), ln))
def shot(n, c0, c1, t0, t1=None, ln=30, mid=None):
    a, b = S(n); KK(a, c0, t0, ln)
    if mid: KK(int(a + (b - a) * mid[0]), mid[1], mid[2], ln)
    KK(b, c1, t1 or t0, ln)
def G(p, up): q = ground(p); q.z += up; return q
shot('open', G(NB_ + NN * 5500 - TU * 4500, 1900), G(NB_ + NN * 4300 - TU * 2600, 1400), G(B, 0), G(B + TU * 800, 0), 28)
shot('ambhi', G(FORT + fd * 45 - fs * 25, 8), G(FORT + fd * 75 + fs * 10, 14), G(FORT + fd * 5, 4), G(FORT + fd * 30, 3), 28)
shot('river', G(B - TU * 4200 + NN * 600, 900), G(B - TU * 3200 - NN * 300, 700), G(B, 0), G(B + TU * 900, 0), 30)
shot('feint', G(FS - NN * 30 - TU * 50, 6), G(FS - NN * 28 + TU * 10, 6), G(FN, 2), G(FN + TU * 20, 2), 32)
shot('storm', G(CROSS - CN * (RW / 2 + 60) + CT * 40, 12), G(CROSS - CN * (RW / 2 + 40) + CT * 20, 9), V((CROSS.x, CROSS.y, wz + 2)), V((*(CROSS - CN * 120).xy, wz + 2)), 30)
shot('battle', G(O - NN * 140 + TU * 10, 45), G(O - NN * 110 - TU * 20, 30), G(O + TU * 40, 2), G(O - TU * 30, 2), 30, mid=(0.5, G(O - NN * 70 - TU * 10, 18), G(O - TU * 40, 2)))
shot('king', G(KG + NN * 6 + TU * 0.5, 2.0), G(KG + NN * 4.2 + TU * 0.2, 1.9), G(KG, 1.6), None, 40)
shot('return', G(B + NN * 300, 14000), G(B + NN * 300 - TU * 200, 13000), G(B, 0), None, 30)
shot('murder', HALL + V((5, -6, 2.5)), HALL + V((3, 1, 2.2)), HALL + V((0, 10, 1.6)), None, 32)
KK(la, G(RIDGE - V((math.cos(math.radians(255)), math.sin(math.radians(255)), 0)) * 60, 8) + V((0, 0, 0)), G(RIDGE, 3), 45)
KK(END, G(RIDGE - V((math.cos(math.radians(255)), math.sin(math.radians(255)), 0)) * 85, 10), G(RIDGE, 3.5), 40)
for f, cpos, tpos, ln in KEYS:
    cam.location = cpos; cam.keyframe_insert('location', frame=f); tgt.location = tpos; tgt.keyframe_insert('location', frame=f); cd.lens = ln; cd.keyframe_insert('lens', frame=f)
ends = {S(l['shot'])[1] for l in plan['lines']}
for idb, path in ((cam, 'location'), (tgt, 'location'), (cd, 'lens')):
    for fc in fcurves(idb):
        if fc.data_path == path:
            for kp in fc.keyframe_points:
                kp.handle_left_type = kp.handle_right_type = 'AUTO_CLAMPED'
                if int(round(kp.co[0])) in ends: kp.interpolation = 'CONSTANT'
sc.render.resolution_x, sc.render.resolution_y = 1080, 1920
sc.view_settings.view_transform = 'AgX'; sc.view_settings.look = 'AgX - Medium High Contrast'
sc.render.image_settings.file_format = 'JPEG'; sc.render.image_settings.quality = 92
P_ = {'B': B, 'O': O, 'FORT': FORT, 'KG': KG, 'RIDGE': RIDGE, 'FN': FN, 'FS': FS, 'CROSS': CROSS, 'NB': NB_, 'SB': SB_}
json.dump({'pts': {k: list(v.xy) for k, v in P_.items()}, 'river': [list(p.xy) for p in R], 'RW': RW,
           'tod': {k: [v[3][0], v[3][1], v[3][2], v[4]] for k, v in TOD.items()}, 'SH': SH, 'shots': [l['shot'] for l in plan['lines']]},
          open('brief/points.json', 'w'))
os.makedirs('scene', exist_ok=True); bpy.ops.wm.save_as_mainfile(filepath=os.path.abspath('scene/porus.blend'))
print('built', END, SH)
