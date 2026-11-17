"""Tirumala guest houses as a tabletop MINIATURE diorama (painted board, the temple model from the ghat-road reel, Quaternius CC0
buildings and people, macro depth of field). One shot per narration line (brief/plan.json)."""
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

K = 1 / 290.0          # pilgrims: 1.75 m -> 6 mm (dioramas exaggerate people so they read)
TK = 1 / 700.0         # trees, same scale as temple and buildings
MS = 1 / 1200.0        # temple model (already x1.7 inside temple.py) -> about 1/700 overall

# ---------------- the board: Tirumala plateau ringed by the hills ----------------
BX, BY = 0.60, 0.40
BASE = 0.012
TPc = V((0.0, -0.06))                       # temple centre
# seven hills: six around the town, Venkatadri is the plateau the temple stands on
HILLS = [('seshadri', -0.50, 0.24, 0.085, 0.09), ('neeladri', -0.26, 0.35, 0.07, 0.075), ('garudadri', 0.04, 0.37, 0.09, 0.085),
         ('anjanadri', 0.31, 0.34, 0.075, 0.075), ('vrushabhadri', 0.52, 0.18, 0.07, 0.075), ('narayanadri', 0.52, -0.27, 0.095, 0.085)]
def hfun(x, y):
    z = BASE + 0.012 * math.exp(-((x - TPc.x) ** 2 / 0.09 + (y - TPc.y) ** 2 / 0.05))           # Venkatadri plateau
    for _, hx, hy, hh, hs in HILLS:
        z += hh * math.exp(-((x - hx) ** 2 + (y - hy) ** 2) / (2 * hs * hs))
    z += 0.004 * max(0.0, -y - 0.25) / 0.15 * (0.5 + 0.5 * noise.noise(V((x * 6, y * 6, 4.0))))   # south rim
    z += 0.0016 * noise.noise(V((x * 10, y * 10, 0.3))) + 0.0005 * noise.noise(V((x * 45, y * 45, 1.7)))
    ex = max(0, min(1, (BX - abs(x)) / 0.04, (BY - abs(y)) / 0.04))
    return BASE + (z - BASE) * ex
def ground(x, y, lift=0.0): return V((x, y, hfun(x, y) + lift))
def town(x, y): return ((x - TPc.x) / 0.47) ** 2 + ((y - TPc.y + 0.02) / 0.30) ** 2      # <1 inside the town
def road(x, y):
    """distance to the painted roads: a ring around the temple, four spokes, an outer loop"""
    dx, dy = x - TPc.x, y - TPc.y; r = math.hypot(dx / 1.25, dy)
    d = abs(r - 0.165)
    d = min(d, abs(math.hypot(dx / 1.5, dy / 1.0) - 0.30))
    for ang in (0.15, 1.75, 3.3, 4.6):
        ux, uy = math.cos(ang), math.sin(ang); t_ = dx * ux + dy * uy
        if 0.15 < t_ < 0.42: d = min(d, abs(-dx * uy + dy * ux))
    return d
NXg, NYg = 360, 240
xs = np.linspace(-BX, BX, NXg); ys = np.linspace(-BY, BY, NYg)
verts = [(x, y, hfun(x, y)) for y in ys for x in xs]
faces = [(j * NXg + i, j * NXg + i + 1, (j + 1) * NXg + i + 1, (j + 1) * NXg + i) for j in range(NYg - 1) for i in range(NXg - 1)]
me = bpy.data.meshes.new('board'); me.from_pydata(verts, [], faces); me.update()
for p in me.polygons: p.use_smooth = True
terr = bpy.data.objects.new('board', me); sc.collection.objects.link(terr)
ca = me.color_attributes.new('paint', 'FLOAT_COLOR', 'POINT')
gw = terr.vertex_groups.new(name='grass'); gws = []
for k, (x, y, z) in enumerate(verts):
    n1 = noise.noise(V((x * 14, y * 14, 2.0))); n2 = noise.noise(V((x * 55, y * 55, 5.0)))
    c = V((0.13, 0.22, 0.07)).lerp(V((0.24, 0.30, 0.10)), 0.5 + 0.5 * n1)             # Seshachalam forest green
    tw = max(0.0, min(1.0, (1.0 - town(x, y)) * 4))
    c = c.lerp(V((0.62, 0.55, 0.44)).lerp(V((0.55, 0.50, 0.42)), 0.5 + 0.5 * n2), tw)    # paved town
    if z - BASE > 0.05: c = c.lerp(V((0.42, 0.36, 0.28)), min(1, (z - BASE - 0.05) / 0.03) * (0.5 + 0.5 * n2))   # rocky tops
    rd = road(x, y)
    if rd < 0.008 and tw > 0.3: c = c.lerp(V((0.22, 0.21, 0.20)), min(1, (0.008 - rd) / 0.003))
    ca.data[k].color = (c.x, c.y, c.z, 1)
    gws.append(0.0 if tw > 0.2 else 0.4 + 0.6 * max(0, n1))
for k, wv in enumerate(gws): gw.add([k], wv, 'REPLACE')
tm = bpy.data.materials.new('board_paint'); tm.use_nodes = True; nt = tm.node_tree; bs = nt.nodes['Principled BSDF']
attr = nt.nodes.new('ShaderNodeAttribute'); attr.attribute_name = 'paint'; nt.links.new(attr.outputs['Color'], bs.inputs['Base Color'])
bs.inputs['Roughness'].default_value = 0.95
nz = nt.nodes.new('ShaderNodeTexNoise'); nz.inputs['Scale'].default_value = 900; nz.inputs['Detail'].default_value = 6
bm = nt.nodes.new('ShaderNodeBump'); bm.inputs['Strength'].default_value = 0.35; bm.inputs['Distance'].default_value = 0.0006
nt.links.new(nz.outputs['Fac'], bm.inputs['Height']); nt.links.new(bm.outputs['Normal'], bs.inputs['Normal'])
terr.data.materials.append(tm)
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

# ---------------- the temple (same model as the ghat-road reel), shrunk onto the board ----------------
TP = V((TPc.x, TPc.y, hfun(TPc.x, TPc.y)))
GZ = max(hfun(TPc.x + dx, TPc.y + dy) for dx in (-0.1, 0, 0.1) for dy in (-0.07, 0, 0.07, 0.14)) - 0.0005
def principled(name, col, rough): return pbr(name, col, rough)
TREES_T = None; elev_local = lambda x, y: GZ
_tg = dict(globals()); _tg['TREES'] = None
exec(open('../tirumala-ghat/temple.py').read(), _tg)
ROOT = _tg['ROOT']; ROOT.location = (TP.x, TP.y, GZ); s_ = _tg['SCL'] * MS; ROOT.scale = (s_, s_, s_)
for o in bpy.data.objects:
    if o.type == 'LIGHT' and o.name.startswith('tpl_light'): o.data.energy *= s_ * s_ * 3; o.data.shadow_soft_size *= s_
bpy.context.view_layer.update()
TPTOP = ROOT.matrix_world @ V((_tg['vx'], 0, _tg['VTOP']))
GOP = ROOT.matrix_world @ V((63, 0, 20))           # Mahadwaram gopuram top (east)
print('TEMPLE top', tuple(round(c, 4) for c in TPTOP), 'gopuram', tuple(round(c, 4) for c in GOP))
# temple flat platform so the model never floats
box('tpl_plinth', (TP.x + 0.0, TP.y + 0.06, GZ - 0.004), (0.20, 0.27, 0.008), pbr('plinth', (0.50, 0.44, 0.36), 0.9))

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
B3 = GLB + 'buildings_pack_3/'
def glb_unit(name, path, height, color=None):
    objs = import_glb(path); norm_height(objs, height)
    if color: paint(objs, color, rough=0.8)
    c = bpy.data.collections.new(name); SRC.children.link(c); move_to(objs, c); return c
U = {}
CREAM, WHITE, MAROON, SAFF, GOLD = (0.93, 0.86, 0.70), (0.95, 0.94, 0.90), (0.55, 0.12, 0.08), (0.95, 0.52, 0.08), (0.95, 0.72, 0.2)
BLD = {  # name: (file, height m, colour)
 'gen4': ('4Story_Mat', 0.024, CREAM), 'gen3': ('3Story_Balcony_Mat', 0.019, (0.95, 0.90, 0.78)), 'gen2': ('2Story_Wide_Mat', 0.013, (0.92, 0.84, 0.66)),
 'gen2b': ('2Story_Balcony_Mat', 0.013, (0.96, 0.92, 0.82)), 'cot': ('1Story_GableRoof_Mat', 0.008, (0.95, 0.88, 0.74)), 'cot2': ('1Story_Mat', 0.007, (0.97, 0.93, 0.85)),
 'nand': ('4Story_Wide_2Doors_Roof_Mat', 0.026, (0.95, 0.84, 0.62)), 'panch': ('4Story_Center_Mat', 0.026, (0.86, 0.90, 0.97)),
 'kaus': ('3Story_Balcony_Mat', 0.021, (0.82, 0.93, 0.80)), 'vakula': ('4Story_Wide_2Doors_Mat', 0.030, (0.98, 0.80, 0.66)),
 'pac': ('6Story_Stack_Mat', 0.034, WHITE), 'donor': ('2Story_Columns_Mat', 0.015, (0.96, 0.90, 0.76)),
}
for k_, (f_, h_, c_) in BLD.items(): U[k_] = glb_unit(k_, B3 + f_ + '.glb', h_, c_)
PEOPLE = [('m_cas', 'modular_men/Casual.glb', WHITE), ('m_farm', 'modular_men/Farmer.glb', (0.96, 0.95, 0.9)), ('m_cas2', 'modular_men/Casual2.glb', SAFF),
          ('w_cas', 'modular_women/Casual.glb', (0.85, 0.15, 0.35)), ('w_form', 'modular_women/Formal.glb', (0.95, 0.65, 0.1)), ('w_work', 'modular_women/Worker.glb', (0.15, 0.55, 0.35))]
WALK, IDLE = [], []
for nm, f_, col in PEOPLE:
    U[nm + '_w'] = unit(nm + '_w', GLB + f_, 1.75, 'Walk', col); WALK.append(nm + '_w')
    U[nm + '_i'] = unit(nm + '_i', GLB + f_, 1.75, 'Idle', col); IDLE.append(nm + '_i')
TREES = []; THT = {}
for nm, hgt in (('CommonTree_1', 9), ('CommonTree_2', 8), ('CommonTree_3', 10), ('CommonTree_4', 9), ('PineTree_1', 11), ('Bush_1', 2.2), ('Bush_2', 2.0)):
    try: U[nm] = glb_unit(nm, GLB + f'nature_pack/{nm}.glb', hgt); TREES.append(nm); THT[nm] = hgt
    except Exception as ex_: print('tree skipped', nm, ex_)
U['lamp'] = glb_unit('lamp', GLB + 'street_pack/Streetlight_Single.glb', 6.0, (0.2, 0.2, 0.2))
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

def binst(cname, p, yaw=0.0, name=None):
    o = bpy.data.objects.new(name or ('b_' + cname), None); o.instance_type = 'COLLECTION'; o.instance_collection = U[cname]
    sc.collection.objects.link(o); o.location = G2(p, -0.0008); o.rotation_euler = (0, 0, yaw); return o
M_sign = pbr('sign', (0.55, 0.06, 0.04), 0.5); M_signf = pbr('signframe', (0.95, 0.70, 0.22), 0.3, 1.0)
def sign(p, yaw, w=0.016, h=0.004, z=0.006):
    e = empty('sign', G2(p, z)); e.rotation_euler.z = yaw
    a = box('sign_b', (0, 0, 0), (w, 0.0008, h), M_sign); a.parent = e
    b = box('sign_f', (0, 0.0003, 0), (w + 0.0012, 0.0008, h + 0.0012), M_signf); b.parent = e
    for sx in (-1, 1):
        c = box('sign_p', (sx * w * 0.4, 0.0, -z / 2), (0.0006, 0.0006, z), M_signf); c.parent = e
    return e
# named guest houses (positions on the board); facing the nearest road
NB = {'nand': V((0.24, -0.15)), 'panch': V((0.34, 0.02)), 'kaus': V((0.20, 0.11)), 'vakula': V((-0.27, -0.13)), 'pac': V((-0.17, -0.29)), 'donor': V((0.08, -0.25))}
def face_to(p, q): return yaw_of((q - p).normalized())       # building fronts face -Y after glTF import, like the figures
TOPS = {}
for k_, p in NB.items():
    yaw = face_to(p, TPc); h_ = BLD[k_][1]
    n_ = 3 if k_ in ('nand', 'vakula') else (2 if k_ in ('panch', 'pac') else 1)
    side = V((math.cos(yaw), math.sin(yaw))); w_ = h_ * 1.05
    for j in range(n_): binst(k_, p + side * (j - (n_ - 1) / 2) * w_, yaw)
    fwd = (TPc - p).normalized()
    sign(p + fwd * (h_ * 0.62), yaw, w=0.014 + 0.004 * n_)
    TOPS[k_] = G2(p, h_ + 0.004)
# the town: rest houses and cottages fill the plateau
OCC = [(TPc + V((0, 0.06)), 0.16)] + [(p, 0.03 + 0.012 * (k in ('nand', 'vakula', 'pac'))) for k, p in NB.items()]
COL = {'seshadri': V((-0.40, 0.11)), 'garudadri': V((0.03, 0.235)), 'anjanadri': V((0.30, 0.20))}
for k, p in COL.items(): OCC.append((p, 0.06))
def ok(x, y, r):
    if town(x, y) > 1.0 or road(x, y) < 0.012 + r * 0.5: return False
    if hfun(x, y) - BASE > 0.03: return False
    return all((V((x, y)) - c).length > rr + r for c, rr in OCC)
GEN = []
tries = 0
while len(GEN) < 110 and tries < 20000:
    tries += 1; x, y = random.uniform(-0.48, 0.48), random.uniform(-0.38, 0.30)
    kind = random.choice(['gen4', 'gen3', 'gen2', 'gen2b', 'gen2', 'gen3']); r = 0.012 if kind in ('gen4', 'gen3') else 0.009
    if not ok(x, y, r): continue
    p = V((x, y)); o = binst(kind, p, face_to(p, TPc) + random.choice((0, 0, math.pi / 2))); GEN.append(o); OCC.append((p, r))
# cottage colonies on the hill slopes, named after the hills
for k, c in COL.items():
    up = V((c.x - [h for h in HILLS if h[0] == k][0][1], c.y - [h for h in HILLS if h[0] == k][0][2])).normalized()
    side = V((up.y, -up.x))
    for i in range(4):
        for j in range(5):
            p = c + side * ((j - 2) * 0.017 + random.uniform(-0.002, 0.002)) + up * ((i - 1.5) * 0.017)
            binst(random.choice(('cot', 'cot', 'cot2')), p, yaw_of(-up) + random.uniform(-0.1, 0.1))
    TOPS[k] = G2(c, 0.012)
TOPS['temple'] = TPTOP
# street lamps along the ring road
for i in range(36):
    a = 2 * math.pi * i / 36; p = TPc + V((1.25 * 0.178 * math.cos(a), 0.178 * math.sin(a)))
    if ok(p.x, p.y, 0.0) or town(p.x, p.y) < 1: inst('lamp', G2(p), a, TK)
# forest on the hills
DRESS = []
n = 0; tries = 0
while n < 700 and tries < 40000:
    tries += 1; x, y = random.uniform(-BX + 0.02, BX - 0.02), random.uniform(-BY + 0.02, BY - 0.02)
    if town(x, y) < 1.05 or any((V((x, y)) - c).length < 0.065 for c in COL.values()): continue
    nm = random.choice(TREES); sz = random.uniform(0.75, 1.35); o = inst(nm, ground(x, y), random.uniform(0, 6.28), TK * sz); n += 1
    DRESS.append((o, 0.35 * THT[nm] * TK * sz + 0.003, THT[nm] * TK * sz))
for k in range(90):        # trees inside the town gaps
    x, y = random.uniform(-0.45, 0.45), random.uniform(-0.35, 0.28)
    if not ok(x, y, 0.006): continue
    nm = random.choice(TREES[:5]); sz = random.uniform(0.6, 1.0); o = inst(nm, ground(x, y), random.uniform(0, 6.28), TK * sz)
    DRESS.append((o, 0.35 * THT[nm] * TK * sz + 0.003, THT[nm] * TK * sz))
bpy.ops.mesh.primitive_cone_add(vertices=5, radius1=0.0005, radius2=0.0, depth=0.0018, location=(5, 5, -5)); tuft = bpy.context.object; tuft.name = 'tuft'
tuft.data.materials.append(pbr('tuft', (0.32, 0.36, 0.12), 0.9)); move_to([tuft], SRC)
ps = terr.modifiers.new('flock', 'PARTICLE_SYSTEM').particle_system; pst = ps.settings
pst.type = 'HAIR'; pst.count = 120000; pst.hair_length = 1.0; pst.render_type = 'OBJECT'; pst.instance_object = tuft
pst.particle_size = 1.0; pst.size_random = 0.6; pst.use_rotations = True; pst.rotation_mode = 'NOR'; pst.phase_factor_random = 2.0
ps.vertex_group_density = 'grass'
# ---------------- pilgrims ----------------
ALL = [(1, END + 2)]
def crowd(c, facing, rows, cols, dx, dy, walk=True):
    out = []
    f = V((facing.x, facing.y)).normalized(); side = V((f.y, -f.x))
    for r in range(rows):
        for k in range(cols):
            p = c + side * ((k - (cols - 1) / 2) * dx + random.uniform(-0.0012, 0.0012)) - f * (r * dy + random.uniform(-0.0015, 0.0015))
            o = inst(random.choice(WALK if walk else IDLE), G2(p), yaw_of(f) + random.uniform(-0.15, 0.15), K * random.uniform(0.9, 1.08)); out.append(o)
    return out
# a river of pilgrims on the east road walking up to the Mahadwaram
east = crowd(TPc + V((0.30, 0.0)), V((-1, 0)), 26, 4, 0.0042, 0.0058)
march(east, 1, END, V((-0.13, 0)))
# waiting near the gopuram, outside the pushkarini, near the PAC
crowd(TPc + V((0.115, 0.0)), V((-1, 0)), 3, 9, 0.0045, 0.005, walk=False)
pd = (TPc - NB['pac']).normalized()
pq = crowd(NB['pac'] + pd * 0.075, -pd, 18, 3, 0.0042, 0.0058)
march(pq, 1, END, -pd * 0.045)
crowd(NB['pac'] + pd * 0.035, -pd, 3, 8, 0.0045, 0.005, walk=False)
for k_ in ('nand', 'panch', 'kaus', 'vakula'):
    d_ = (TPc - NB[k_]).normalized(); g_ = crowd(NB[k_] + d_ * 0.04, d_, 2, 5, 0.0048, 0.006); march(g_, 1, END, d_ * 0.03)
# families strolling along the ring road
for i in range(28):
    a = random.uniform(0, 2 * math.pi); r_ = 0.165
    p = TPc + V((1.25 * r_ * math.cos(a), r_ * math.sin(a))); tg = V((-math.sin(a) * 1.25, math.cos(a))).normalized()
    g_ = crowd(p, tg, random.randint(1, 3), random.randint(2, 3), 0.0045, 0.006); march(g_, 1, END, tg * random.uniform(0.02, 0.05))
# ---------------- light per shot ----------------
wd = bpy.data.worlds.new('w'); sc.world = wd; wd.use_nodes = True; wn = wd.node_tree
env = wn.nodes.new('ShaderNodeTexEnvironment'); env.image = bpy.data.images.load('/opt/reel/assets/ph/h/kiara_1_dawn.exr')
bg = wn.nodes['Background']; wn.links.new(env.outputs['Color'], bg.inputs['Color'])
bpy.ops.object.light_add(type='SUN'); sun = bpy.context.object; sun.data.angle = math.radians(3)
GOLDEN = (1.0, 0.72, 0.45)
TOD = {'hook': (14, 235, 4.2, GOLDEN, 0.32), 'count': (32, 210, 4.2, (1, 0.88, 0.72), 0.4), 'rename': (34, 200, 4.2, (1, 0.9, 0.78), 0.42),
       'nandakam': (30, 215, 4.2, (1, 0.88, 0.72), 0.4), 'panchajanyam': (30, 215, 4.2, (1, 0.88, 0.72), 0.4), 'kausthubham': (28, 220, 4.2, (1, 0.86, 0.68), 0.4),
       'vakula': (24, 225, 4.2, (1, 0.82, 0.62), 0.38), 'four': (45, 200, 4.2, (1, 0.9, 0.78), 0.42), 'pac': (26, 225, 4.2, (1, 0.84, 0.66), 0.38),
       'hills': (18, 235, 4.2, (1, 0.78, 0.52), 0.34), 'finale': (8, 250, 4.6, (1.0, 0.62, 0.32), 0.3)}
for name, (el, az, en, col, ws) in TOD.items():
    for f in S(name):
        sun.rotation_euler = (math.radians(90 - el), 0, math.radians(az - 90)); sun.keyframe_insert('rotation_euler', frame=f)
        sun.data.energy = en; sun.data.keyframe_insert('energy', frame=f); sun.data.color = col; sun.data.keyframe_insert('color', frame=f)
        bg.inputs['Strength'].default_value = ws; bg.inputs['Strength'].keyframe_insert('default_value', frame=f)
for idb in (sun, sun.data): const(idb)
for fc in act_fcurves(wn.animation_data.action) if wn.animation_data else []:
    for kp in fc.keyframe_points: kp.interpolation = 'CONSTANT'
bpy.ops.object.light_add(type='AREA', location=(0.0, -0.9, 0.9)); fill = bpy.context.object; fill.data.size = 1.2; fill.rotation_euler = (math.radians(45), 0, 0)
fill.data.color = (0.8, 0.88, 1.0); fill.data.energy = 9
# warm glow over the temple in the golden shots
bpy.ops.object.light_add(type='POINT', location=TPTOP + V((0.03, 0, 0.05))); tglow = bpy.context.object; tglow.data.color = (1, 0.6, 0.2); tglow.data.shadow_soft_size = 0.02
for name in TOD:
    for f in S(name): tglow.data.energy = 6.0 if name in ('hook', 'finale') else 1.5; tglow.data.keyframe_insert('energy', frame=f)
const(tglow.data)
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
def T3(c, h): return ground(c.x, c.y, h)
def CA(P, az, el, Wd, L):
    """camera that frames width Wd (m) at subject P with lens L (9:16 portrait)"""
    d = Wd / 2 * L / 10.125; a_, e_ = math.radians(az), math.radians(el)
    c = P + V((math.cos(e_) * math.cos(a_), math.cos(e_) * math.sin(a_), math.sin(e_))) * d
    gz = hfun(c.x, c.y) + 0.004
    if c.z < gz: c.z = gz
    return c
def SH2(n, P0, P1, az0, az1, el0, el1, W0, W1, L, fst, mid=None):
    a_, b_ = S(n); KK(a_, CA(P0, az0, el0, W0, L), P0, L, fst, P0)
    if mid: q, Pm, azm, elm, Wm = mid; KK(int(a_ + (b_ - a_) * q), CA(Pm, azm, elm, Wm, L), Pm, L, fst, Pm)
    KK(b_, CA(P1, az1, el1, W1, L), P1, L, fst, P1)
def T3(c, h): return ground(c.x, c.y, h)
def AZ(p, q): d = q - p; return math.degrees(math.atan2(d.y, d.x))       # azimuth of the camera placed at q, seen from p
EP = TPc + V((0.16, 0.0))
a0, b0 = S('hook')
KK(a0, CA(T3(EP, 0.006), 0, 6, 0.05, 35), T3(EP + V((-0.05, 0)), 0.008), 35, 3.2, T3(EP, 0.005))
KK(int(a0 + (b0 - a0) * 0.45), CA(T3(TPc + V((0.06, 0)), 0.02), 8, 16, 0.16, 35), T3(TPc + V((0.03, 0)), 0.02), 35, 4.0, T3(TPc + V((0.06, 0)), 0.02))
KK(b0, CA(T3(TPc + V((0, 0.03)), 0.01), -15, 38, 0.62, 35), T3(TPc + V((0, 0.03)), 0.01), 35, 9.0, T3(TPc + V((0, 0.03)), 0.01))
SH2('count', T3(V((-0.24, -0.10)), 0.008), T3(V((0.22, -0.10)), 0.008), -100, -80, 34, 30, 0.34, 0.30, 35, 7.0)
SH2('rename', T3(NB['donor'], 0.008), T3(NB['donor'], 0.009), AZ(NB['donor'], TPc) - 25, AZ(NB['donor'], TPc) - 8, 16, 12, 0.09, 0.06, 40, 4.0)
for sh, k_, dz in (('nandakam', 'nand', 0.012), ('panchajanyam', 'panch', 0.012), ('kausthubham', 'kaus', 0.01), ('vakula', 'vakula', 0.014)):
    az = AZ(NB[k_], TPc)
    SH2(sh, T3(NB[k_], dz), T3(NB[k_], dz), az - 30, az + 5, 20, 14, 0.13, 0.085, 35, 4.5)
SH2('four', T3(V((-0.02, -0.04)), 0.01), T3(V((-0.02, -0.04)), 0.01), -95, -80, 58, 52, 0.80, 0.72, 35, 11.0)
az = AZ(NB['pac'], TPc)
SH2('pac', T3(NB['pac'] + (TPc - NB['pac']).normalized() * 0.06, 0.006), T3(NB['pac'], 0.012), az + 30, az + 10, 9, 16, 0.07, 0.12, 35, 4.0)
SH2('hills', T3(COL['seshadri'], 0.012), T3(COL['anjanadri'], 0.012), -80, -100, 30, 26, 0.24, 0.24, 35, 6.0,
    mid=(0.5, T3(COL['garudadri'], 0.014), -90, 30, 0.26))
a9, b9 = S('finale'); P = T3(TPc + V((0.02, 0.0)), 0.02)
KK(a9, CA(P, 30, 32, 0.40, 35), P, 35, 6.0, P)
KK(int(a9 + (b9 - a9) * 0.6), CA(P, 10, 18, 0.20, 35), P, 35, 4.5, P)
KK(b9, CA(P, 0, 14, 0.15, 35), P, 35, 4.0, P)
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
            if (d < r + 0.006 and t_ < 0.97) or (o.location - cp).length < r + 0.06:
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
# ---------------- screen positions of the named places (for the Remotion pins) ----------------
from bpy_extras.object_utils import world_to_camera_view
PINS = {'rename': ['donor'], 'nandakam': ['nand'], 'panchajanyam': ['panch'], 'kausthubham': ['kaus'], 'vakula': ['vakula'],
        'four': ['nand', 'panch', 'kaus', 'vakula', 'pac', 'temple'], 'pac': ['pac'], 'hills': ['seshadri', 'garudadri', 'anjanadri'],
        'hook': ['temple'], 'finale': ['temple'], 'count': ['temple']}
TOPS['donor'] = G2(NB['donor'], BLD['donor'][1] + 0.004)
lab = {}
for shn, keys_ in PINS.items():
    a_, b_ = S(shn); rows = {}
    for f in range(a_, b_ + 1, 2):
        sc.frame_set(f); row = []
        for k_ in keys_:
            q = world_to_camera_view(sc, cam, TOPS[k_]); row.append([k_, round(q.x, 4), round(1 - q.y, 4), int(q.z > 0 and -0.1 <= q.x <= 1.1 and -0.1 <= q.y <= 1.1)])
        rows[f] = row
    lab[shn] = rows
json.dump({'step': 2, 'shots': lab}, open('brief/labels.json', 'w'))
sc.frame_set(1)
sc.render.resolution_x, sc.render.resolution_y = 1080, 1920
sc.view_settings.view_transform = 'AgX'; sc.view_settings.look = 'AgX - Punchy'
sc.render.image_settings.file_format = 'JPEG'; sc.render.image_settings.quality = 92
sc.eevee.bokeh_max_size = 140
os.makedirs('scene', exist_ok=True); bpy.ops.wm.save_as_mainfile(filepath=os.path.abspath('scene/stay.blend'))
print('built', END, SH)
