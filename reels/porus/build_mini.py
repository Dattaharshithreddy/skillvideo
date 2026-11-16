"""Porus vs Alexander as a tabletop MINIATURE diorama (1:72 figures on a 1.2 x 0.8 m painted board), shot with
real macro depth of field so it reads like a tilt-shift model. One shot per narration line (brief/plan.json).
Figures: Quaternius CC0 (knight, horse, king), OpenGameArt CC0 elephant; trees/props Quaternius CC0; HDRI Poly Haven CC0."""
import bpy, json, math, os, random, subprocess
import numpy as np
from mathutils import Vector, noise
HERE = os.path.dirname(os.path.abspath(__file__)); os.chdir(HERE); random.seed(7)
V = Vector
FPS = 30; GLB = '/opt/reel/assets/qs/public/glb/'; K = 1 / 150.0; TK = 1 / 260.0      # figure scale, tree scale (compressed, like real dioramas)
plan = json.load(open('brief/plan.json'))
def adur(p): return float(subprocess.run(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0', p], capture_output=True, text=True).stdout)
durs = [adur(l['audio']) for l in plan['lines']]
durs[-1] += 3.0                                    # end card after the last line
starts, t = [], 0.0
for d in durs: starts.append(t); t += d
SH = [(round(s * FPS) + 1, round((s + d) * FPS)) for s, d in zip(starts, durs)]
END = SH[-1][1]
SHOT = {l['shot']: i for i, l in enumerate(plan['lines'])}
def S(n): return SH[SHOT[n]]
def fr(n, x): a, b = S(n); return int(a + (b - a) * x)
json.dump({'starts': starts, 'durs': durs, 'end': END, 'lines': [{'text': l['text'], 'keywords': l['keywords'], 'shot': l['shot']} for l in plan['lines']]},
          open('brief/timing.json', 'w'), indent=1, ensure_ascii=False)
bpy.ops.wm.read_factory_settings(use_empty=True)
sc = bpy.context.scene; sc.frame_start, sc.frame_end, sc.render.fps = 1, END, FPS
sc.unit_settings.scale_length = 1.0

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
def linear(idb, path):
    for fc in fcurves(idb):
        if fc.data_path == path:
            for kp in fc.keyframe_points: kp.interpolation = 'LINEAR'
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
def pbr(name, col, rough=0.75, metal=0.0):
    m = bpy.data.materials.new(name); m.use_nodes = True; b = m.node_tree.nodes['Principled BSDF']
    b.inputs['Base Color'].default_value = (*col, 1); b.inputs['Roughness'].default_value = rough; b.inputs['Metallic'].default_value = metal; return m
def box(name, loc, dims, m, link=True):
    me = bpy.data.meshes.new(name)
    x, y, z = dims[0] / 2, dims[1] / 2, dims[2] / 2
    vs = [(-x, -y, -z), (x, -y, -z), (x, y, -z), (-x, y, -z), (-x, -y, z), (x, -y, z), (x, y, z), (-x, y, z)]
    me.from_pydata(vs, [], [(0, 1, 2, 3), (4, 7, 6, 5), (0, 4, 5, 1), (1, 5, 6, 2), (2, 6, 7, 3), (3, 7, 4, 0)]); me.materials.append(m)
    o = bpy.data.objects.new(name, me); o.location = loc
    if link: sc.collection.objects.link(o)
    return o
def coll(name, parent=None):
    c = bpy.data.collections.new(name); (parent or sc.collection).children.link(c); return c
def move_to(objs, c):
    for o in objs:
        for uc in list(o.users_collection): uc.objects.unlink(o)
        c.objects.link(o)
def empty(name, loc=(0, 0, 0)):
    e = bpy.data.objects.new(name, None); sc.collection.objects.link(e); e.location = loc; return e

# ---------------- the board: painted terrain ----------------
BX, BY = 0.60, 0.40                       # half sizes (m)
BASE = 0.012                              # board surface height
RWH = 0.055                               # river half width
def yr(x): return 0.03 * math.sin(2.6 * x + 0.4) + 0.012 * math.sin(7.0 * x)
HILLS = [(0.22, -0.33, 0.055, 0.07), (-0.05, -0.37, 0.034, 0.06), (-0.36, -0.33, 0.042, 0.065), (0.47, -0.05, 0.02, 0.05),
         (0.10, 0.36, 0.03, 0.06), (-0.26, 0.37, 0.036, 0.06), (0.45, 0.33, 0.028, 0.05)]
FORT = V((0.40, -0.265)); TAXILA = V((-0.47, 0.30)); ISLAND = V((-0.42, yr(-0.42)))
def hfun(x, y):
    d = abs(y - yr(x))
    riv = min(1.0, max(0.0, (d - RWH * 0.75) / (RWH * 0.55)))       # 0 in river bed, 1 on the banks
    riv = riv * riv * (3 - 2 * riv)
    isl = ((x - ISLAND.x) / 0.06) ** 2 + ((y - ISLAND.y) / 0.022) ** 2
    if isl < 1: riv = max(riv, (1 - isl) ** 0.5 * 0.85)
    z = BASE - 0.006 + 0.006 * riv
    for hx, hy, hh, hs in HILLS:
        z += hh * math.exp(-((x - hx) ** 2 + (y - hy) ** 2) / (2 * hs * hs)) * riv
    z += 0.0018 * noise.noise(V((x * 9, y * 9, 0.3))) * riv + 0.0006 * noise.noise(V((x * 40, y * 40, 1.7)))
    fd = (x - FORT.x) ** 2 + (y - FORT.y) ** 2
    if fd < 0.07 ** 2:
        w = min(1, (0.07 - fd ** 0.5) / 0.02); z = z * (1 - w) + (BASE + 0.016) * w
    ex = min(1, (BX - abs(x)) / 0.035, (BY - abs(y)) / 0.035); ex = max(0, ex)
    return BASE + (z - BASE) * ex if riv > 0.5 else z * ex + BASE * (1 - ex)
def ground(x, y, lift=0.0): return V((x, y, hfun(x, y) + lift))
NXg, NYg = 360, 240
xs = np.linspace(-BX, BX, NXg); ys = np.linspace(-BY, BY, NYg)
verts, cols = [], []
for j, y in enumerate(ys):
    for i, x in enumerate(xs):
        z = hfun(x, y); verts.append((x, y, z))
faces = [(j * NXg + i, j * NXg + i + 1, (j + 1) * NXg + i + 1, (j + 1) * NXg + i) for j in range(NYg - 1) for i in range(NXg - 1)]
me = bpy.data.meshes.new('board'); me.from_pydata(verts, [], faces); me.update()
for p in me.polygons: p.use_smooth = True
terr = bpy.data.objects.new('board', me); sc.collection.objects.link(terr)
# painted colours as a vertex colour: flock greens, dry ochre, sandy banks, wet mud patch, rocky hill tops
ca = me.color_attributes.new('paint', 'FLOAT_COLOR', 'POINT')
MUD = V((-0.22, -0.14))
gw = terr.vertex_groups.new(name='grass'); gws = []
for k, (x, y, z) in enumerate(verts):
    d = abs(y - yr(x)); n1 = noise.noise(V((x * 14, y * 14, 2.0))); n2 = noise.noise(V((x * 55, y * 55, 5.0)))
    grass = V((0.20, 0.27, 0.07)).lerp(V((0.36, 0.33, 0.12)), 0.5 + 0.5 * n1)
    c = grass.lerp(V((0.48, 0.38, 0.22)), max(0, min(1, (0.2 - (z - BASE) * 6) * 0.0 + 0.25 + 0.3 * n2)))
    sand = V((0.62, 0.52, 0.36))
    bank = max(0, min(1, (d - RWH * 0.7) / (RWH * 0.9)))
    c = sand.lerp(c, bank)
    if z - BASE > 0.03: c = c.lerp(V((0.45, 0.40, 0.33)), min(1, (z - BASE - 0.03) / 0.02))
    md = ((x - MUD.x) ** 2 + (y - MUD.y) ** 2) ** 0.5
    if md < 0.07: c = c.lerp(V((0.22, 0.15, 0.09)), min(1, (0.07 - md) / 0.03) * (0.7 + 0.3 * n2))
    if d < RWH * 0.8: c = V((0.17, 0.14, 0.10))
    ca.data[k].color = (c.x, c.y, c.z, 1)
    gws.append(0.0 if (d < RWH * 1.05 or md < 0.06 or (x - FORT.x) ** 2 + (y - FORT.y) ** 2 < 0.075 ** 2) else 0.35 + 0.65 * max(0, n1))
for k, wv in enumerate(gws): gw.add([k], wv, 'REPLACE')
tm = bpy.data.materials.new('board_paint'); tm.use_nodes = True; nt = tm.node_tree; bs = nt.nodes['Principled BSDF']
attr = nt.nodes.new('ShaderNodeAttribute'); attr.attribute_name = 'paint'; nt.links.new(attr.outputs['Color'], bs.inputs['Base Color'])
bs.inputs['Roughness'].default_value = 0.95
nz = nt.nodes.new('ShaderNodeTexNoise'); nz.inputs['Scale'].default_value = 900; nz.inputs['Detail'].default_value = 6
bm = nt.nodes.new('ShaderNodeBump'); bm.inputs['Strength'].default_value = 0.35; bm.inputs['Distance'].default_value = 0.0006
nt.links.new(nz.outputs['Fac'], bm.inputs['Height']); nt.links.new(bm.outputs['Normal'], bs.inputs['Normal'])
terr.data.materials.append(tm)
# resin river
rv, rf = [], []
NR = 200
for i in range(NR + 1):
    x = -BX + 2 * BX * i / NR; y0 = yr(x)
    rv += [(x, y0 - RWH * 0.95, BASE - 0.0015), (x, y0 + RWH * 0.95, BASE - 0.0015)]
    if i: rf.append((2 * i - 2, 2 * i - 1, 2 * i + 1, 2 * i))
wm = bpy.data.meshes.new('river'); wm.from_pydata(rv, [], rf); riverO = bpy.data.objects.new('river', wm); sc.collection.objects.link(riverO)
M_water = bpy.data.materials.new('resin'); M_water.use_nodes = True; nt = M_water.node_tree; b = nt.nodes['Principled BSDF']
b.inputs['Base Color'].default_value = (0.02, 0.09, 0.09, 1); b.inputs['Roughness'].default_value = 0.14; b.inputs['Specular IOR Level'].default_value = 0.35
wv = nt.nodes.new('ShaderNodeTexWave'); wv.inputs['Scale'].default_value = 60; wv.inputs['Distortion'].default_value = 6; wv.wave_type = 'BANDS'; wv.bands_direction = 'X'
mp = nt.nodes.new('ShaderNodeMapping'); tc = nt.nodes.new('ShaderNodeTexCoord'); nt.links.new(tc.outputs['Object'], mp.inputs['Vector']); nt.links.new(mp.outputs['Vector'], wv.inputs['Vector'])
mp.inputs['Location'].default_value[0] = 0.0; mp.inputs['Location'].keyframe_insert('default_value', frame=1, index=0)
mp.inputs['Location'].default_value[0] = -0.004 * END / FPS; mp.inputs['Location'].keyframe_insert('default_value', frame=END, index=0)
wb = nt.nodes.new('ShaderNodeBump'); wb.inputs['Strength'].default_value = 0.25; wb.inputs['Distance'].default_value = 0.0004
nt.links.new(wv.outputs['Fac'], wb.inputs['Height']); nt.links.new(wb.outputs['Normal'], b.inputs['Normal'])
riverO.data.materials.append(M_water)
for fc in act_fcurves(nt.animation_data.action) if nt.animation_data else []:
    for kp in fc.keyframe_points: kp.interpolation = 'LINEAR'
# board edges (MDF), table, room
M_mdf = pbr('mdf', (0.10, 0.065, 0.04), 0.6)
for nm, loc, dims in (('edgeN', (0, BY + 0.004, BASE / 2 - 0.004), (2 * BX + 0.016, 0.008, BASE + 0.008)), ('edgeS', (0, -BY - 0.004, BASE / 2 - 0.004), (2 * BX + 0.016, 0.008, BASE + 0.008)),
                      ('edgeE', (BX + 0.004, 0, BASE / 2 - 0.004), (0.008, 2 * BY, BASE + 0.008)), ('edgeW', (-BX - 0.004, 0, BASE / 2 - 0.004), (0.008, 2 * BY, BASE + 0.008))):
    box(nm, loc, dims, M_mdf)
M_table = bpy.data.materials.new('table'); M_table.use_nodes = True; nt = M_table.node_tree; b = nt.nodes['Principled BSDF']
wt = nt.nodes.new('ShaderNodeTexWave'); wt.inputs['Scale'].default_value = 6; wt.inputs['Distortion'].default_value = 9; wt.inputs['Detail'].default_value = 4
cr = nt.nodes.new('ShaderNodeValToRGB'); cr.color_ramp.elements[0].color = (0.10, 0.045, 0.02, 1); cr.color_ramp.elements[1].color = (0.24, 0.12, 0.05, 1)
nt.links.new(wt.outputs['Fac'], cr.inputs['Fac']); nt.links.new(cr.outputs['Color'], b.inputs['Base Color']); b.inputs['Roughness'].default_value = 0.35
box('table', (0, 0, -0.025), (3.2, 2.2, 0.05), M_table)
M_wall = pbr('room', (0.05, 0.04, 0.035), 0.9)
bpy.ops.mesh.primitive_cylinder_add(radius=3.5, depth=4, location=(0, 0, 1.0), vertices=48); wall = bpy.context.object; wall.data.materials.append(M_wall)
wall.visible_shadow = False
for k in range(14):        # warm room lamps far behind -> bokeh balls
    a = random.uniform(0, 2 * math.pi); r = random.uniform(2.2, 3.2)
    bpy.ops.mesh.primitive_uv_sphere_add(radius=random.uniform(0.02, 0.05), location=(r * math.cos(a), r * math.sin(a), random.uniform(0.15, 0.9)))
    bl = bpy.context.object; bl.data.materials.append(emis(f'bokeh{k}', random.choice([(1, 0.62, 0.3), (1, 0.75, 0.45), (1, 0.5, 0.2)]), random.uniform(6, 14)))
    bl.visible_shadow = False

# ---------------- assets ----------------
SRC = coll('sources'); bpy.context.view_layer.layer_collection.children['sources'].exclude = True
def import_glb(path):
    before = set(bpy.data.objects); bpy.ops.import_scene.gltf(filepath=path); new = [o for o in bpy.data.objects if o not in before]
    return new
def norm_height(objs, height, axis=2):
    bpy.context.view_layer.update()
    pts = [o.matrix_world @ V(c) for o in objs if o.type == 'MESH' for c in o.bound_box]
    d = max(p[axis] for p in pts) - min(p[axis] for p in pts)
    roots = [o for o in objs if o.parent is None]; s = height / d
    for r in roots: r.scale = r.scale * s; r.location = r.location * s
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
def paint(objs, col, keep=('skin', 'face', 'eye', 'hair'), rough=0.7):
    """miniature paint job: flat acrylic colour, matte"""
    for o in objs:
        if o.type != 'MESH': continue
        for sl in o.material_slots:
            m = sl.material
            if not m: continue
            nm = m.copy(); nm.name = m.name + '_' + str(col)[:14]; b = nm.node_tree.nodes.get('Principled BSDF') if nm.use_nodes else None
            if b:
                if any(k in m.name.lower() for k in keep):
                    b.inputs['Roughness'].default_value = 0.6
                else:
                    for l in list(b.inputs['Base Color'].links): nm.node_tree.links.remove(l)
                    bc = b.inputs['Base Color'].default_value; lum = 0.3 * bc[0] + 0.59 * bc[1] + 0.11 * bc[2]
                    k = 0.6 + 0.8 * lum; b.inputs['Base Color'].default_value = (min(1, col[0] * k), min(1, col[1] * k), min(1, col[2] * k), 1)
                    b.inputs['Roughness'].default_value = rough; b.inputs['Metallic'].default_value = 0.0
            sl.material = nm
def unit(name, path, height, action=None, color=None, extra=None):
    objs = import_glb(path); norm_height(objs, height)
    if color: paint(objs, color)
    if action: set_action(objs, action)
    if extra: objs += extra(objs)
    c = bpy.data.collections.new(name); SRC.children.link(c); move_to(objs, c); return c
def add_base(objs, r=0.36, col=(0.18, 0.2, 0.08)):
    """every miniature stands on a small round painted base"""
    me_ = bpy.data.meshes.new('base'); n = 24
    vs = [(r * math.cos(2 * math.pi * i / n), r * math.sin(2 * math.pi * i / n), z) for z in (0.0, 0.12) for i in range(n)]
    fs = [tuple(range(n)), tuple(range(2 * n - 1, n - 1, -1))] + [(i, (i + 1) % n, n + (i + 1) % n, n + i) for i in range(n)]
    me_.from_pydata(vs, [], fs); me_.materials.append(pbr('base', col, 0.9)); o = bpy.data.objects.new('base', me_); sc.collection.objects.link(o)
    for r_ in [x for x in objs if x.parent is None]: r_.location.z += 0.12
    return [o]
M_wood = pbr('shaft', (0.42, 0.30, 0.16), 0.7); M_iron = pbr('iron', (0.55, 0.55, 0.58), 0.35, 0.8)
def cyl(r, d, loc, rot, m):
    bpy.ops.mesh.primitive_cylinder_add(radius=r, depth=d, location=loc, rotation=rot, vertices=8); o = bpy.context.object; o.data.materials.append(m); return o
def sarissa(objs):
    return [cyl(0.03, 5.5, (0.35, 0.3, 3.4), (math.radians(8), 0, 0), M_wood)] + add_base(objs)
def plume(objs, z=2.0, base=True):
    bpy.ops.mesh.primitive_cone_add(vertices=8, radius1=0.12, radius2=0.04, depth=0.55, location=(0, 0.05, z)); p = bpy.context.object
    p.data.materials.append(pbr('plume', (0.85, 0.08, 0.06), 0.8)); p.rotation_euler = (math.radians(-25), 0, 0)
    return [p] + (add_base(objs, 0.45, (0.2, 0.17, 0.1)) if base else [])
def turban(objs, col=(0.95, 0.93, 0.86), h=1.75):
    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.105 * h, location=(0, 0, 0.99 * h), segments=12, ring_count=8); tb = bpy.context.object; tb.scale = (1.05, 1.05, 0.7)
    tb.data.materials.append(pbr('turban', col, 0.8)); return [tb]
def bow(objs):
    return [cyl(0.03, 1.8, (0.45, -0.05, 1.0), (0, math.radians(8), 0), M_wood)]
BRONZE, CRIMSON, WHITE, SAFF, PURP, GOLD = (0.62, 0.40, 0.16), (0.55, 0.06, 0.05), (0.90, 0.88, 0.80), (0.95, 0.52, 0.08), (0.42, 0.18, 0.55), (0.95, 0.72, 0.2)
KN = GLB + 'single_knight_pack/KnightCharacter.glb'
U = {}
U['mac_walk'] = unit('mac_walk', KN, 1.8, 'Walking', BRONZE, lambda o: sarissa(o))
U['mac_idle'] = unit('mac_idle', KN, 1.8, 'Idle_HumanArmature', BRONZE, lambda o: sarissa(o))
U['ind_idle'] = unit('ind_idle', KN, 1.75, 'Idle_HumanArmature', WHITE, lambda o: turban(o) + bow(o) + add_base(o))
U['ind_walk'] = unit('ind_walk', KN, 1.75, 'Walking', WHITE, lambda o: turban(o) + bow(o) + add_base(o))
U['amb_walk'] = unit('amb_walk', KN, 1.75, 'Walking', PURP, lambda o: turban(o, (0.6, 0.3, 0.75)) + add_base(o))
def rider_unit(name, action, coat, extra, horse_col=None):
    c = unit(name, GLB + 'animals_pack/Horse.glb', 1.65, action, horse_col)
    objs = import_glb(KN); norm_height(objs, 1.3); paint(objs, coat); set_action(objs, 'Idle_HumanArmature')
    for r in [o for o in objs if o.parent is None]: r.location += V((0, 0.1, 1.15))
    objs += extra(objs); move_to(objs, c); return c
U['cav'] = rider_unit('cav', 'Gallop_AnimalArmature', BRONZE, lambda o: [cyl(0.04, 3.0, (0.3, -0.6, 2.4), (math.radians(70), 0, 0), M_wood)])
U['cav_walk'] = rider_unit('cav_walk', 'Walk_AnimalArmature', BRONZE, lambda o: [])
U['alex_horse'] = rider_unit('alex_horse', 'Idle', CRIMSON, lambda o: plume([], 2.5, False), (0.06, 0.05, 0.05))
U['messenger'] = rider_unit('messenger', 'Gallop_AnimalArmature', BRONZE, lambda o: [])
# elephant (OpenGameArt CC0) with a red/gold caparison and howdah
with bpy.data.libraries.load('/opt/reel/assets/elephant.blend', link=False) as (src, dst): dst.objects = list(src.objects); dst.actions = list(src.actions)
eobjs = [o for o in dst.objects if o]
for o in eobjs: sc.collection.objects.link(o)
norm_height(eobjs, 3.0)
M_hide = bpy.data.materials.new('eleph_skin'); M_hide.use_nodes = True; nt = M_hide.node_tree; b = nt.nodes['Principled BSDF']
b.inputs['Base Color'].default_value = (0.30, 0.28, 0.27, 1); b.inputs['Roughness'].default_value = 0.85
nz = nt.nodes.new('ShaderNodeTexNoise'); nz.inputs['Scale'].default_value = 40; bm = nt.nodes.new('ShaderNodeBump'); bm.inputs['Strength'].default_value = 0.3
nt.links.new(nz.outputs['Fac'], bm.inputs['Height']); nt.links.new(bm.outputs['Normal'], b.inputs['Normal'])
for o in eobjs:
    if o.type == 'MESH': o.data.materials.clear(); o.data.materials.append(M_hide)
M_cap = pbr('caparison', (0.62, 0.05, 0.04), 0.8); M_gold = pbr('gold', (0.95, 0.68, 0.18), 0.35, 1.0); M_howdah = pbr('howdah', (0.45, 0.22, 0.08), 0.6)
def elephant_unit(name, action, rider=None):
    c = bpy.data.collections.new(name); SRC.children.link(c); new = []
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
    parts = [box(name + '_cap', (0, 0, 2.55), (1.95, 2.3, 0.07), M_cap, False), box(name + '_trim', (0, 0, 2.52), (2.02, 2.36, 0.03), M_gold, False),
             box(name + '_howdah', (0, 0.1, 3.0), (1.2, 1.4, 0.55), M_howdah, False), box(name + '_hrim', (0, 0.1, 3.3), (1.3, 1.5, 0.08), M_gold, False)]
    for p in parts: c.objects.link(p)
    if rider:
        objs = import_glb(KN); norm_height(objs, rider[1]); paint(objs, rider[0]); set_action(objs, 'Idle_HumanArmature')
        objs += turban(objs, rider[2], rider[1])
        for r in [o for o in objs if o.parent is None]: r.location += V((0, 0.1, 3.3))
        move_to(objs, c)
    return c
U['eleph'] = elephant_unit('eleph', 'Angry', (WHITE, 1.4, (0.95, 0.93, 0.86)))
U['eleph_walk'] = elephant_unit('eleph_walk', 'Walk', (WHITE, 1.4, (0.95, 0.93, 0.86)))
U['eleph_idle'] = elephant_unit('eleph_idle', 'Idle', (WHITE, 1.4, (0.95, 0.93, 0.86)))
U['porus_eleph'] = elephant_unit('porus_eleph', 'Idle', (SAFF, 1.75, GOLD))
for o in eobjs: bpy.data.objects.remove(o, do_unlink=True)
def hero(name, color, height, extra):
    objs = import_glb(KN); norm_height(objs, height); paint(objs, color); set_action(objs, 'Idle_HumanArmature')
    objs += extra(objs); c = bpy.data.collections.new(name); SRC.children.link(c); move_to(objs, c); return c
U['porus'] = hero('porus', SAFF, 2.25, lambda o: turban(o, GOLD, 2.25) + [cyl(0.05, 0.3, (0, 0, 2.38), (0, 0, 0), M_gold)] + add_base(o, 0.5, (0.25, 0.2, 0.1)))
U['alex'] = hero('alex', CRIMSON, 1.8, lambda o: plume(o))
U['ambhi'] = hero('ambhi', PURP, 1.85, lambda o: turban(o, GOLD, 1.85) + add_base(o))
U['shadow'] = hero('shadow', (0.04, 0.04, 0.05), 1.85, lambda o: add_base(o, 0.4, (0.05, 0.05, 0.05)))
U['fallen'] = hero('fallen', SAFF, 1.75, lambda o: turban(o, GOLD))
for o in U['fallen'].objects:
    if o.parent is None: o.rotation_euler = (math.radians(88), 0, math.radians(30)); o.location.z += 0.25
def glb_unit(name, path, height, color=None):
    objs = import_glb(path); norm_height(objs, height)
    if color: paint(objs, color, rough=0.8)
    c = bpy.data.collections.new(name); SRC.children.link(c); move_to(objs, c); return c
U['chariot'] = glb_unit('chariot', GLB + 'medieval_village_pack/Cart.glb', 1.6, (0.5, 0.3, 0.12))
U['boat'] = glb_unit('boat', GLB + 'ships_pack/Boat.glb', 1.6)
U['tent'] = glb_unit('tent', GLB + 'survival_pack/Tent.glb', 3.0, (0.85, 0.8, 0.68))
U['tent_r'] = glb_unit('tent_r', GLB + 'survival_pack/Tent.glb', 3.4, (0.6, 0.12, 0.08))
U['gate'] = glb_unit('gate', GLB + 'modular_medieval_buildings_pack/WallEntranceBricks.glb', 8.0, (0.72, 0.55, 0.38))
U['tower'] = glb_unit('tower', GLB + 'modular_medieval_buildings_pack/SmallSquareTowerBricks.glb', 12.0, (0.72, 0.55, 0.38))
U['wall'] = glb_unit('wall', GLB + 'modular_medieval_buildings_pack/WallBricks.glb', 7.0, (0.72, 0.55, 0.38))
U['banner'] = glb_unit('banner', GLB + 'modular_medieval_buildings_pack/Banner.glb', 4.0, SAFF)
U['house'] = glb_unit('house', GLB + 'real_time_strategy_pack/Houses_FirstAge_1_Level1.glb', 5.0)
U['fire'] = glb_unit('fire', GLB + 'survival_pack/Bonfire.glb', 0.8)
U['torch'] = glb_unit('torch', GLB + 'survival_pack/WoodenTorch.glb', 1.2)
TREES = []; THT = {}
for nm, hgt in (('PalmTree_1', 11), ('PalmTree_2', 10), ('PalmTree_3', 12), ('CommonTree_1', 9), ('CommonTree_2', 8), ('CommonTree_3', 10), ('Bush_1', 2.2), ('Bush_2', 2.0)):
    U[nm] = glb_unit(nm, GLB + f'nature_pack/{nm}.glb', hgt); TREES.append(nm); THT[nm] = hgt
U['rock'] = glb_unit('rock', GLB + 'medieval_village_pack/Rock_1.glb', 3.0, (0.5, 0.46, 0.4))

def inst(cname, loc, yaw=0.0, s=K, name=None):
    o = bpy.data.objects.new(name or ('i_' + cname), None); o.instance_type = 'COLLECTION'; o.instance_collection = U[cname]
    sc.collection.objects.link(o); o.location = loc; o.rotation_euler = (0, 0, yaw); o.scale = (s, s, s); return o
def yaw_of(d): return math.atan2(d.x, -d.y)       # glTF figures face -Y after import
def G2(p, lift=0.0): return ground(p.x, p.y, lift)
def block(cname, centre, facing, rows, cols, dx, dy, ranges, jitter=0.0015, s=K):
    f = V((facing.x, facing.y)).normalized(); side = V((f.y, -f.x)); out = []; dx *= 0.55; dy *= 0.55; jitter *= 0.55
    for r in range(rows):
        for c in range(cols):
            p = centre + side * ((c - (cols - 1) / 2) * dx + random.uniform(-jitter, jitter)) - f * (r * dy + random.uniform(-jitter, jitter))
            o = inst(cname, G2(p), yaw_of(f) + random.uniform(-0.08, 0.08), s); show(o, ranges); out.append(o)
    return out
def march(objs, a, b, d, steps=8):
    """move a group by 2D offset d between frames a..b, following the ground"""
    for o in objs:
        p0 = V((o.location.x, o.location.y))
        for k in range(steps + 1):
            f = a + (b - a) * k / steps; p = p0 + d * (k / steps); o.location = G2(p); o.keyframe_insert('location', frame=int(f))
        linear(o, 'location')

# ---------------- dressing: trees, rocks, villages, camps ----------------
def free(x, y):
    if abs(y - yr(x)) < RWH * 1.25: return False
    for c, r in ((FORT, 0.09), (TAXILA, 0.08), (MUD, 0.08), (V((0.0, -0.17)), 0.14), (V((0.05, 0.17)), 0.12)):
        if (V((x, y)) - c).length < r: return False
    return abs(x) < BX - 0.02 and abs(y) < BY - 0.02
DRESS = []          # (object, radius, height) -> hidden in any shot where it would block the lens
n = 0
while n < 260:
    x, y = random.uniform(-BX, BX), random.uniform(-BY, BY)
    if not free(x, y): continue
    nm = random.choice(TREES); sz = random.uniform(0.75, 1.3); o = inst(nm, ground(x, y), random.uniform(0, 6.28), TK * sz); n += 1
    DRESS.append((o, 0.35 * THT[nm] * TK * sz + 0.004, THT[nm] * TK * sz))
for k in range(40):
    x, y = random.uniform(-BX, BX), random.uniform(-BY, BY)
    if free(x, y): sz = random.uniform(0.5, 1.2); o = inst('rock', ground(x, y), random.uniform(0, 6.28), K * sz); DRESS.append((o, 0.016 * sz + 0.004, 0.02 * sz))
# Porus's capital: brick walls, towers, gate, houses, saffron banners
fd = V((0, 1)); fs = V((1, 0))
inst('gate', G2(FORT + fd * 0.045), yaw_of(fd))
for k in (-1, 1):
    inst('tower', G2(FORT + fd * 0.045 + fs * 0.03 * k), 0); inst('wall', G2(FORT + fd * 0.045 + fs * 0.055 * k), yaw_of(fd))
    inst('tower', G2(FORT + fd * 0.045 + fs * 0.08 * k), 0); inst('wall', G2(FORT + fs * 0.08 * k), yaw_of(fs)); inst('banner', G2(FORT + fd * 0.045 + fs * 0.03 * k, 0.012), yaw_of(fd))
for k in range(9):
    inst('house', G2(FORT + V((random.uniform(-0.06, 0.06), random.uniform(-0.04, 0.03)))), random.choice((0, 1.57, 3.14)))
# Taxila (Ambhi)
td = V((0.6, -0.8)).normalized(); ts = V((td.y, -td.x))
inst('gate', G2(TAXILA), yaw_of(td))
for k in (-1, 1): inst('tower', G2(TAXILA + ts * 0.03 * k), 0); inst('wall', G2(TAXILA + ts * 0.055 * k), yaw_of(td))
for k in range(6): inst('house', G2(TAXILA - td * 0.04 + ts * random.uniform(-0.05, 0.05)), random.choice((0, 1.57)))
# camps
for k in range(10): DRESS.append((inst('tent_r', ground(-0.05 + k * 0.03, yr(-0.05 + k * 0.03) + 0.2 + 0.02 * (k % 2)), random.uniform(0, 6.28)), 0.022, 0.025))
for k in range(9): DRESS.append((inst('tent', ground(-0.12 + k * 0.035, yr(-0.12 + k * 0.035) - 0.2 - 0.02 * (k % 2)), random.uniform(0, 6.28)), 0.02, 0.022))
# flock grass tufts as hair particles
bpy.ops.mesh.primitive_cone_add(vertices=5, radius1=0.0005, radius2=0.0, depth=0.0018, location=(5, 5, -5)); tuft = bpy.context.object; tuft.name = 'tuft'
tuft.data.materials.append(pbr('tuft', (0.32, 0.36, 0.12), 0.9)); move_to([tuft], SRC)
ps = terr.modifiers.new('flock', 'PARTICLE_SYSTEM').particle_system; pst = ps.settings
pst.type = 'HAIR'; pst.count = 120000; pst.hair_length = 1.0; pst.render_type = 'OBJECT'; pst.instance_object = tuft
pst.particle_size = 1.0; pst.size_random = 0.6; pst.use_rotations = True; pst.rotation_mode = 'NOR'; pst.phase_factor_random = 2.0
ps.vertex_group_density = 'grass'

# ---------------- story staging ----------------
def bank(x, side, off=0.0):          # side +1 north (Alexander), -1 south (Porus)
    return V((x, yr(x) + side * (RWH + 0.012 + off)))
# OPEN: Macedonian columns march east along the north bank
oa, ob = S('open')
mac_cols = []
for c in range(4):
    mac_cols += block('mac_walk', V((-0.36 + c * 0.075, yr(-0.36 + c * 0.075) + 0.15)), V((1, 0)), 6, 4, 0.0055, 0.0065, [(oa, S('ambhi')[1] + 1)])
mac_cols += block('cav_walk', V((-0.40, yr(-0.4) + 0.19)), V((1, 0)), 3, 3, 0.009, 0.012, [(oa, S('ambhi')[1] + 1)])
alex_o = inst('alex_horse', G2(V((-0.06, yr(-0.06) + 0.17))), yaw_of(V((1, 0)))); show(alex_o, [(oa, S('open')[1] + 1)])
march(mac_cols + [alex_o], oa, S('ambhi')[1], V((0.10, 0)))
# DEMAND: messenger rides to Porus's gate; Porus on his elephant before the gate with his guard
da, db = S('demand')
pe = inst('porus_eleph', G2(FORT + fd * 0.085), yaw_of(fd)); show(pe, [(da, db + 1)])
guard = block('ind_idle', FORT + fd * 0.07 + fs * 0.0, fd, 2, 9, 0.006, 0.007, [(da, db + 1)])
for k in (-1, 1):
    e = inst('eleph_idle', G2(FORT + fd * 0.078 + fs * 0.035 * k), yaw_of(fd)); show(e, [(da, db + 1)])
msg = inst('messenger', G2(FORT + fd * 0.2 + fs * 0.06), yaw_of(-fd + fs * -0.3)); show(msg, [(da, db + 1)])
march([msg], da, fr('demand', 0.45), V((-0.05, -0.085)))
# AMBHI: Taxila gate, Ambhi bows, purple troops march out toward the Macedonians
aa, ab = S('ambhi')
amb = inst('ambhi', G2(TAXILA + td * 0.03), yaw_of(td)); show(amb, [(aa, ab + 1)])
alx2 = inst('alex_horse', G2(TAXILA + td * 0.06), yaw_of(-td)); show(alx2, [(aa, ab + 1)])
ambt = block('amb_walk', TAXILA - td * 0.002, td, 7, 4, 0.0055, 0.0065, [(aa, ab + 1)])
march(ambt, fr('ambhi', 0.15), ab, td * 0.05)
amb_e = [inst('eleph_walk', G2(TAXILA + td * 0.02 + ts * 0.035 * k), yaw_of(td)) for k in (-1, 1)]
for e in amb_e: show(e, [(aa, ab + 1)])
march(amb_e, fr('ambhi', 0.3), ab, td * 0.03)
# RIVER: both armies face each other across the flooded Jhelum; elephant wall on the south bank
ra, rb = S('river')
els = []
for k in range(15):
    x = -0.2 + k * 0.03; p = bank(x, -1, 0.006)
    o = inst('eleph_idle', G2(p), yaw_of(V((0, 1)))); show(o, [(ra, S('feint')[1] + 1)]); els.append(o)
ind_line = []
for k in range(5):
    x0 = -0.17 + k * 0.1; ind_line += block('ind_idle', bank(x0, -1, 0.03), V((0, 1)), 3, 12, 0.0055, 0.0065, [(ra, S('feint')[1] + 1)])
mac_line = []
for k in range(5):
    x0 = -0.15 + k * 0.1; mac_line += block('mac_idle', bank(x0, 1, 0.02), V((0, -1)), 3, 12, 0.0055, 0.0065, [(ra, rb + 1)])
# FEINT (night): cavalry with torches gallops up and down the north bank, watch fires on the south bank
fa, fb = S('feint')
M_fire = emis('flame', (1.0, 0.45, 0.12), 60.0)
cav = []
for i in range(12):
    x = -0.18 + i * 0.012; o = inst('cav', G2(bank(x, 1, 0.012 + 0.004 * (i % 2))), yaw_of(V((1, 0)))); show(o, [(fa, fb + 1)]); cav.append(o)
    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.0012, location=o.location + V((0, 0, 0.04))); fl = bpy.context.object; fl.data.materials.append(M_fire)
    fl.parent = o; fl.location = (0.3, -0.3, 3.0); fl.scale = (72, 72, 72); show(fl, [(fa, fb + 1)])
for o in cav:
    p0 = V((o.location.x, o.location.y))
    for f in range(fa, fb + 1, 5):
        ph = (f - fa) / 150.0; x = p0.x + 0.12 * math.sin(ph * math.pi); p = bank(x, 1, p0.y - yr(p0.x) - RWH - 0.012)
        o.location = G2(p); o.keyframe_insert('location', frame=f)
        o.rotation_euler.z = yaw_of(V((1, 0)) if math.cos(ph * math.pi) >= 0 else V((-1, 0))); o.keyframe_insert('rotation_euler', frame=f, index=2)
    const(o, 'rotation_euler')
for k in range(5):
    bpy.ops.object.light_add(type='POINT', location=ground(-0.12 + k * 0.06, yr(-0.12 + k * 0.06) + RWH + 0.02, 0.03)); pl = bpy.context.object
    pl.data.energy = 0.0; pl.data.keyframe_insert('energy', frame=1); pl.data.energy = 0.25; pl.data.keyframe_insert('energy', frame=fa); pl.data.energy = 0.0; pl.data.keyframe_insert('energy', frame=fb + 1)
    pl.data.color = (1, 0.5, 0.2); pl.data.shadow_soft_size = 0.004; const(pl.data)
watch = []
for k in range(8):
    x = -0.18 + k * 0.05; f_ = inst('fire', G2(bank(x, -1, 0.05)), 0); show(f_, [(fa, S('storm')[0])])
    bpy.ops.object.light_add(type='POINT', location=ground(x, yr(x) - RWH - 0.06, 0.012)); pl = bpy.context.object; pl.data.color = (1, 0.45, 0.15); pl.data.shadow_soft_size = 0.003
    off = fr('feint', 0.45 + 0.45 * k / 8)          # fires die one by one -> they stopped reacting
    for f, e in ((1, 0), (fa, 0.12), (off, 0.12), (off + 8, 0.0)): pl.data.energy = e; pl.data.keyframe_insert('energy', frame=f)
    const(pl.data); watch.append(pl)
# STORM (night, upstream): boats and swimming horses cross to the island, then wade on
sa, sb = S('storm')
boats = []
for i in range(7):
    p = V((ISLAND.x - 0.05 + i * 0.016, yr(ISLAND.x) + RWH + 0.01))
    o = inst('boat', V((p.x, p.y, BASE - 0.0012)), yaw_of(V((0, -1)))); show(o, [(sa, sb + 1)]); boats.append(o)
    for j in range(3):
        m_ = inst('mac_idle', V((0, 0, 0)), 0, 0.85); m_.parent = o; m_.location = (0.0, -0.4 + j * 0.45, 0.2); show(m_, [(sa, sb + 1)])
for o in boats:
    o.keyframe_insert('location', frame=sa); o.location.y -= 0.045; o.keyframe_insert('location', frame=fr('storm', 0.55))
    o.keyframe_insert('location', frame=sb); linear(o, 'location')
landed = block('mac_walk', V((ISLAND.x, ISLAND.y + 0.004)), V((0, -1)), 2, 8, 0.006, 0.007, [(fr('storm', 0.62), sb + 1)])
march(landed, fr('storm', 0.62), sb, V((0, -0.03)))
lights_storm = [fr('storm', x) for x in (0.06, 0.3, 0.33, 0.52, 0.8)]
# SON: chariots stuck in the mud; the prince falls
ca_, cb_ = S('son')
chs = []
for k in range(6):
    p = MUD + V((-0.04 + k * 0.016, 0.01 * (k % 2)))
    c_ = inst('chariot', G2(p, -0.0015), yaw_of(V((0.3, 1))) + random.uniform(-0.25, 0.25)); c_.rotation_euler.x = random.uniform(-0.12, 0.12); show(c_, [(ca_, cb_ + 1)]); chs.append(c_)
    h_ = inst('cav_walk', G2(p + V((0.004, 0.014))), yaw_of(V((0.3, 1)))); show(h_, [(ca_, cb_ + 1)])
enemy = block('cav', MUD + V((0.0, 0.09)), V((0, -1)), 2, 7, 0.01, 0.012, [(ca_, cb_ + 1)])
march(enemy, ca_, fr('son', 0.6), V((0, -0.05)))
prince = inst('fallen', G2(MUD + V((0.0, 0.03))), 0.6); show(prince, [(fr('son', 0.72), cb_ + 1)])
# BATTLE: elephants charge the phalanx, cavalry sweeps the flank
ba, bb = S('battle')
BF = V((0.0, -0.17))
phal = block('mac_idle', BF + V((-0.09, 0.0)), V((1, 0)), 7, 14, 0.0045, 0.0052, [(ba, bb + 1)], 0.0006)
porinf = block('ind_idle', BF + V((0.15, 0.0)), V((-1, 0)), 5, 18, 0.0055, 0.0062, [(ba, bb + 1)])
bels = []
for i in range(7):
    o = inst('eleph', G2(BF + V((0.095, (i - 3) * 0.016))), yaw_of(V((-1, 0)))); show(o, [(ba, bb + 1)]); bels.append(o)
pbe = inst('porus_eleph', G2(BF + V((0.13, 0.0))), yaw_of(V((-1, 0)))); show(pbe, [(ba, S('king')[0])])
for i, o in enumerate(bels):
    p0 = V((o.location.x, o.location.y))
    for f in range(ba, bb + 1, 3):
        tt = min(1, max(0, (f - ba - 15) / max(1, (bb - ba) * 0.5))); s_ = tt * tt * (3 - 2 * tt)
        back = max(0, (f - fr('battle', 0.62)) / max(1, bb - fr('battle', 0.62)))      # wounded elephants turn back into their own lines
        p = p0 + V((-0.075 * s_ + 0.06 * back, 0.004 * math.sin(i + f / 9)))
        o.location = G2(p, 0.0004 * abs(math.sin(f / 4 + i))); o.keyframe_insert('location', frame=f)
        o.rotation_euler.z = yaw_of(V((-1, 0)) if back < 0.15 else V((1, 0.3 * (i - 3)))); o.keyframe_insert('rotation_euler', frame=f, index=2)
    const(o, 'rotation_euler')
cav2 = []
for i in range(14):
    o = inst('cav', G2(BF + V((-0.12, -0.07 - (i % 4) * 0.008))), yaw_of(V((1, 0)))); show(o, [(fr('battle', 0.3), bb + 1)]); cav2.append(o)
    a0 = fr('battle', 0.3)
    for f in range(a0, bb + 1, 4):
        tt = (f - a0) / max(1, bb - a0); ang = math.pi * tt
        p = BF + V((0.03 - 0.15 * math.cos(ang) - (i // 4) * 0.01, -0.07 - (i % 4) * 0.008 - 0.06 * math.sin(ang)))
        o.location = G2(p); o.keyframe_insert('location', frame=f)
        d = V((0.15 * math.sin(ang), -0.06 * math.cos(ang))); o.rotation_euler.z = yaw_of(d.normalized()); o.keyframe_insert('rotation_euler', frame=f, index=2)
# KING: wounded Porus stands before Alexander
ka, kb = S('king')
KG = V((0.06, -0.245))
pz = inst('porus', G2(KG + V((0.012, 0))), yaw_of(V((-1, 0)))); show(pz, [(ka, kb + 1)])
az_ = inst('alex_horse', G2(KG + V((-0.016, 0.002))), yaw_of(V((1, 0)))); show(az_, [(ka, kb + 1)])
kg_guard = block('mac_idle', KG + V((-0.03, 0.025)), V((0, -1)), 2, 9, 0.0055, 0.0065, [(ka, kb + 1)])
kg_guard += block('mac_idle', KG + V((-0.03, -0.025)), V((0, 1)), 2, 9, 0.0055, 0.0065, [(ka, kb + 1)])
kge = inst('porus_eleph', G2(KG + V((0.05, 0.01))), yaw_of(V((-1, -0.2)))); show(kge, [(ka, kb + 1)])
# RETURN: day, top-down; Macedonian columns turn back west at the east edge (the Beas)
ra2, rb2 = S('return')
back_cols = []
for c in range(5):
    back_cols += block('mac_walk', V((0.45 - c * 0.02, 0.24 - c * 0.025)), V((-1, 0)), 4, 5, 0.0055, 0.0065, [(ra2, rb2 + 1)])
march(back_cols, fr('return', 0.4), rb2, V((-0.12, 0)))
ret_por = inst('porus_eleph', G2(FORT + fd * 0.085), yaw_of(fd)); show(ret_por, [(ra2, rb2 + 1)])
gl = bpy.data.meshes.new('realm'); gv = []; gfc = []
for k in range(41):
    x = -0.3 + 0.9 * k / 40; gv += [(x, yr(x) - RWH * 0.9, 0), (x, -BY + 0.02, 0)]
    if k: gfc.append((2 * k - 2, 2 * k - 1, 2 * k + 1, 2 * k))
gl.from_pydata(gv, [], gfc); realm = bpy.data.objects.new('realm', gl); sc.collection.objects.link(realm); realm.location.z = 0.09
M_realm = bpy.data.materials.new('realm'); M_realm.use_nodes = True; rn = M_realm.node_tree
for nd in list(rn.nodes): rn.nodes.remove(nd)
re_ = rn.nodes.new('ShaderNodeEmission'); re_.inputs['Color'].default_value = (1, 0.7, 0.2, 1); re_.inputs['Strength'].default_value = 1.5
tr_ = rn.nodes.new('ShaderNodeBsdfTransparent'); mx = rn.nodes.new('ShaderNodeMixShader'); mx.inputs['Fac'].default_value = 0.0; ro = rn.nodes.new('ShaderNodeOutputMaterial')
rn.links.new(tr_.outputs[0], mx.inputs[1]); rn.links.new(re_.outputs[0], mx.inputs[2]); rn.links.new(mx.outputs[0], ro.inputs[0])
M_realm.surface_render_method = 'BLENDED'; realm.data.materials.append(M_realm); realm.visible_shadow = False
for f, v in ((1, 0.0), (fr('return', 0.15), 0.0), (fr('return', 0.35), 0.28), (fr('return', 0.7), 0.28), (rb2, 0.0)):
    mx.inputs['Fac'].default_value = v; mx.inputs['Fac'].keyframe_insert('default_value', frame=f)
show(realm, [(ra2, rb2 + 1)])
# MURDER (night): Porus by the fire in front of his tent; a shadow comes up behind; the fire goes out
ma, mb = S('murder')
MT = V((0.29, -0.13))
inst('tent_r', G2(MT + V((0, -0.02))), 0)
mp_ = inst('porus', G2(MT + V((0.0, -0.002))), yaw_of(V((0, 1)))); show(mp_, [(ma, mb + 1)])
mfire = inst('fire', G2(MT + V((0.0, 0.016))), 0); show(mfire, [(ma, mb + 1)])
sh_ = inst('shadow', G2(MT + V((-0.05, -0.04))), yaw_of(V((1, 1)))); show(sh_, [(ma, mb + 1)])
march([sh_], ma, fr('murder', 0.75), V((0.042, 0.033)))
bpy.ops.object.light_add(type='POINT', location=ground(MT.x, MT.y + 0.016, 0.008)); mfl = bpy.context.object; mfl.data.color = (1, 0.45, 0.15); mfl.data.shadow_soft_size = 0.002
for f in range(1, END + 1, 3):
    on = ma <= f <= fr('murder', 0.82)
    mfl.data.energy = (0.06 * (0.8 + 0.4 * random.random())) if on else 0.0; mfl.data.keyframe_insert('energy', frame=f)
const(mfl.data)
# LEGACY: Porus on his elephant on the south hill at sunset; camera pulls back to reveal the whole table
la, lb = S('legacy')
HILL = V((0.22, -0.31))
lpe = inst('porus_eleph', G2(HILL), yaw_of(V((-0.6, 0.8)))); show(lpe, [(la, END + 1)])
lguard = block('ind_idle', HILL + V((0.03, -0.02)), V((-0.6, 0.8)), 2, 6, 0.0055, 0.0065, [(la, END + 1)])

# ---------------- light per shot (miniature studio + time of day) ----------------
wd = bpy.data.worlds.new('w'); sc.world = wd; wd.use_nodes = True; wn = wd.node_tree
env = wn.nodes.new('ShaderNodeTexEnvironment'); env.image = bpy.data.images.load('/opt/reel/assets/ph/h/kiara_1_dawn.exr')
bg = wn.nodes['Background']; wn.links.new(env.outputs['Color'], bg.inputs['Color'])
bpy.ops.object.light_add(type='SUN'); sun = bpy.context.object; sun.data.angle = math.radians(3)
TOD = {  # shot: (elevation, azimuth, energy, colour, world)
    'open': (16, 230, 4.0, (1.0, 0.78, 0.55), 0.35), 'demand': (30, 200, 4.2, (1, 0.9, 0.75), 0.4), 'ambhi': (35, 140, 4.2, (1, 0.93, 0.82), 0.4),
    'river': (22, 210, 4.2, (1, 0.85, 0.65), 0.35), 'feint': (40, 120, 2.2, (0.45, 0.6, 1.0), 0.12), 'storm': (40, 120, 1.6, (0.45, 0.55, 1.0), 0.1),
    'son': (20, 100, 2.6, (0.85, 0.85, 0.95), 0.2), 'battle': (12, 100, 4.0, (1.0, 0.78, 0.55), 0.3), 'king': (7, 260, 3.6, (1.0, 0.62, 0.35), 0.25),
    'return': (55, 160, 4.0, (1, 0.95, 0.88), 0.45), 'murder': (40, 100, 0.7, (0.45, 0.55, 1.0), 0.04), 'legacy': (6, 250, 4.5, (1.0, 0.58, 0.28), 0.3)}
for name, (el, az, en, col, ws) in TOD.items():
    for f in S(name):
        sun.rotation_euler = (math.radians(90 - el), 0, math.radians(az - 90)); sun.keyframe_insert('rotation_euler', frame=f)
        sun.data.energy = en; sun.data.keyframe_insert('energy', frame=f); sun.data.color = col; sun.data.keyframe_insert('color', frame=f)
        bg.inputs['Strength'].default_value = ws; bg.inputs['Strength'].keyframe_insert('default_value', frame=f)
for f in lights_storm:
    for df, e in ((-1, 0.15), (0, 7.0), (1, 2.0), (3, 0.15)):
        sun.data.energy = e; sun.data.keyframe_insert('energy', frame=f + df)
for idb in (sun, sun.data): const(idb)
for fc in act_fcurves(wn.animation_data.action) if wn.animation_data else []:
    for kp in fc.keyframe_points: kp.interpolation = 'CONSTANT'
# soft fill (studio bounce) that follows the day/night
bpy.ops.object.light_add(type='AREA', location=(0.0, 0.9, 0.9)); fill = bpy.context.object; fill.data.size = 1.2; fill.rotation_euler = (math.radians(-45), 0, 0)
fill.data.color = (0.75, 0.85, 1.0)
for name, (el, az, en, col, ws) in TOD.items():
    for f in S(name): fill.data.energy = 10 * min(1, en / 4); fill.data.keyframe_insert('energy', frame=f)
const(fill.data)

# ---------------- camera: macro lens with real depth of field ----------------
cd = bpy.data.cameras.new('cam'); cam = bpy.data.objects.new('cam', cd); sc.collection.objects.link(cam); sc.camera = cam
cd.sensor_width = 36; cd.clip_start = 0.002; cd.clip_end = 20
cd.dof.use_dof = True
tgt = empty('cam_target'); foc = empty('cam_focus'); cd.dof.focus_object = foc
c_ = cam.constraints.new('TRACK_TO'); c_.target = tgt; c_.track_axis = 'TRACK_NEGATIVE_Z'; c_.up_axis = 'UP_Y'
KEYS = []
def KK(f, cpos, tpos, ln, fst, fpos=None): KEYS.append((int(f), V(cpos), V(tpos), ln, fst, V(fpos) if fpos is not None else V(tpos)))
def shot(n, c0, c1, t0, t1=None, ln=50, fst=2.8, f0=None, f1=None, mid=None):
    a, b = S(n); KK(a, c0, t0, ln, fst, f0)
    if mid: KK(int(a + (b - a) * mid[0]), mid[1], mid[2], ln, fst, mid[3] if len(mid) > 3 else mid[2])
    KK(b, c1, t1 or t0, ln, fst, f1 if f1 is not None else (t1 or t0))
def P3(x, y, up): return ground(x, y, up)
def O3(c, dx, dy, h, lift=0.0): return ground(c.x + dx, c.y + dy, h) if lift == 0 else V((c.x + dx, c.y + dy, hfun(c.x, c.y) + h))
def T3(c, h): return ground(c.x, c.y, h)
C0 = V((-0.30, yr(-0.30) + 0.15))           # leading Macedonian column (moves +x during open)
shot('open', T3(C0, 0.0) + V((0.035, -0.03, 0.006)), V((-0.95, 0.32, 0.55)), T3(C0, 0.005), V((0.05, 0.0, 0.01)), 55, 4.0,
     f0=T3(C0, 0.005), f1=V((-0.1, 0.05, 0.02)), mid=(0.42, T3(C0, 0.0) + V((0.09, -0.11, 0.05)), T3(C0 + V((0.05, 0)), 0.005)))
PE = FORT + fd * 0.085
shot('demand', T3(PE, 0.0) + V((0.06, 0.07, 0.014)), T3(PE, 0.0) + V((0.035, 0.045, 0.01)), T3(PE, 0.012), None, 60, 3.2,
     f0=T3(PE + V((-0.02, 0.05)), 0.006), f1=T3(PE, 0.012))
AM = TAXILA + td * 0.04
shot('ambhi', T3(AM, 0.0) + V((0.08, -0.04, 0.016)), T3(AM, 0.0) + V((0.055, -0.03, 0.011)), T3(AM, 0.006), T3(AM + td * 0.02, 0.006), 55, 3.2)
shot('river', T3(bank(-0.12, 1, 0.03), 0.007), T3(bank(0.10, 1, 0.03), 0.008), T3(bank(-0.10, -1, 0.006), 0.008), T3(bank(0.13, -1, 0.006), 0.008),
     45, 2.8)
shot('feint', T3(bank(-0.12, -1, 0.09), 0.024), T3(bank(0.0, -1, 0.09), 0.022), T3(bank(-0.10, 1, 0.014), 0.005), T3(bank(0.03, 1, 0.014), 0.005), 50, 3.2)
shot('storm', T3(ISLAND, 0.0) + V((0.09, 0.05, 0.022)), T3(ISLAND, 0.0) + V((0.06, -0.035, 0.014)), T3(ISLAND + V((0, 0.02)), 0.004), T3(ISLAND + V((0, -0.025)), 0.004), 50, 3.5)
shot('son', T3(MUD, 0.0) + V((0.06, -0.05, 0.012)), T3(MUD, 0.0) + V((0.04, -0.03, 0.008)), T3(MUD + V((0, 0.01)), 0.004), T3(MUD + V((0, 0.025)), 0.003), 60, 3.0)
shot('battle', T3(BF, 0.0) + V((0.07, -0.07, 0.016)), T3(BF, 0.0) + V((-0.07, -0.05, 0.011)), T3(BF + V((0.06, 0)), 0.008), T3(BF + V((-0.05, 0)), 0.006), 50, 3.5,
     mid=(0.5, T3(BF, 0.0) + V((0.0, -0.06, 0.012)), T3(BF + V((0.01, 0)), 0.007)))
shot('king', T3(KG, 0.0) + V((-0.002, -0.035, 0.007)), T3(KG, 0.0) + V((0.0, -0.026, 0.007)), T3(KG, 0.008), None, 80, 2.4,
     f0=T3(KG + V((0.012, 0)), 0.013), f1=T3(KG + V((0.012, 0)), 0.014), mid=(0.62, T3(KG, 0.0) + V((-0.001, -0.03, 0.007)), T3(KG, 0.009), T3(KG + V((-0.016, 0)), 0.012)))
shot('return', V((0.85, -0.10, 0.95)), V((0.78, -0.06, 0.85)), V((-0.02, -0.02, 0.0)), V((0.0, -0.02, 0.0)), 45, 8.0)
shot('murder', T3(MT, 0.0) + V((0.035, 0.04, 0.008)), T3(MT, 0.0) + V((0.022, 0.028, 0.006)), T3(MT, 0.007), None, 65, 2.4,
     f0=T3(MT, 0.008), f1=T3(MT + V((-0.006, -0.004)), 0.008))
shot('legacy', T3(HILL, 0.0) + V((-0.05, 0.06, 0.02)), V((0.95, -0.40, 0.5)), T3(HILL, 0.012), V((0.0, -0.05, 0.01)), 55, 3.5,
     f0=T3(HILL, 0.012), f1=V((0.2, -0.2, 0.03)), mid=(0.55, T3(HILL, 0.0) + V((-0.12, 0.2, 0.1)), T3(HILL, 0.012)))
for f, cpos, tpos, ln, fst, fpos in KEYS:
    cam.location = cpos; cam.keyframe_insert('location', frame=f); tgt.location = tpos; tgt.keyframe_insert('location', frame=f)
    foc.location = fpos; foc.keyframe_insert('location', frame=f)
    cd.lens = ln; cd.keyframe_insert('lens', frame=f); cd.dof.aperture_fstop = fst; cd.dof.keyframe_insert('aperture_fstop', frame=f)
ends = {S(l['shot'])[1] for l in plan['lines']}
for idb, paths in ((cam, ('location',)), (tgt, ('location',)), (foc, ('location',)), (cd, ('lens', 'dof.aperture_fstop'))):
    for fc in fcurves(idb):
        if fc.data_path in paths:
            for kp in fc.keyframe_points:
                kp.handle_left_type = kp.handle_right_type = 'AUTO_CLAMPED'
                if int(round(kp.co[0])) in ends: kp.interpolation = 'CONSTANT'
def seg_dist(p, a, b):
    ab = b - a; t_ = max(0.0, min(1.0, (p - a).dot(ab) / max(ab.length_squared, 1e-9))); return (a + ab * t_ - p).length, t_
hide = {id(o): [] for o, _, _ in DRESS}
for l in plan['lines']:
    a_, b_ = S(l['shot'])
    for x in (0.0, 0.2, 0.4, 0.6, 0.8, 1.0):
        sc.frame_set(int(a_ + (b_ - a_) * x)); cp = cam.matrix_world.translation.copy(); tp = tgt.matrix_world.translation.copy()
        for o, r, hgt in DRESS:
            c = o.location + V((0, 0, hgt * 0.5)); d, t_ = seg_dist(c, cp, tp)
            if (d < r + 0.005 and t_ < 0.97) or (o.location - cp).length < r + 0.035:
                if (a_, b_) not in hide[id(o)]: hide[id(o)].append((a_, b_))
nh = 0
for o, r, hgt in DRESS:
    hs = sorted(hide[id(o)])
    if not hs: continue
    nh += 1; vis = []; cur = 1
    for a_, b_ in hs:
        if a_ > cur: vis.append((cur, a_))
        cur = max(cur, b_ + 1)
    vis.append((cur, END + 2)); show(o, vis)
print('hidden occluders', nh)
sc.frame_set(1)
sc.render.resolution_x, sc.render.resolution_y = 1080, 1920
sc.view_settings.view_transform = 'AgX'; sc.view_settings.look = 'AgX - Punchy'
sc.render.image_settings.file_format = 'JPEG'; sc.render.image_settings.quality = 92
sc.eevee.bokeh_max_size = 140
os.makedirs('scene', exist_ok=True); bpy.ops.wm.save_as_mainfile(filepath=os.path.abspath('scene/porus_mini.blend'))
print('built', END, SH)
