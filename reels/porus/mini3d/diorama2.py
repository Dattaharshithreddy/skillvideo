# Puru vs Alexander — tilt-shift miniature diorama (thekitiki style): toy-pawn crowds, puffy trees, river, signboards.
# blender -b -P diorama.py -- SHOT [frames]   (renders out/<SHOT>/####.png on GPU)
import bpy, bmesh, math, random, os, sys, glob
from mathutils import Vector, Matrix
argv = sys.argv[sys.argv.index('--') + 1:] if '--' in sys.argv else ['A']
SHOT = argv[0]; NF = int(argv[1]) if len(argv) > 1 else 144
OUT = f'/opt/reel/mini3d/out2/{SHOT}'; os.makedirs(OUT, exist_ok=True)
random.seed(7)
for o in list(bpy.data.objects): bpy.data.objects.remove(o)
sc = bpy.context.scene; sc.frame_start, sc.frame_end = 1, NF; sc.render.fps = 24

def mat(name, col, rough=0.6, metal=0.0, emit=0.0, bump=0.0, bscale=30.0):
    m = bpy.data.materials.get(name)
    if m: return m
    m = bpy.data.materials.new(name); m.use_nodes = True; nt = m.node_tree; b = nt.nodes['Principled BSDF']
    b.inputs['Base Color'].default_value = (*col, 1); b.inputs['Roughness'].default_value = rough; b.inputs['Metallic'].default_value = metal
    if emit: b.inputs['Emission Color'].default_value = (*col, 1); b.inputs['Emission Strength'].default_value = emit
    if bump:
        tc = nt.nodes.new('ShaderNodeTexCoord'); n = nt.nodes.new('ShaderNodeTexNoise'); n.inputs['Scale'].default_value = bscale; n.inputs['Detail'].default_value = 8
        nt.links.new(tc.outputs['Object'], n.inputs['Vector'])
        bp = nt.nodes.new('ShaderNodeBump'); bp.inputs['Strength'].default_value = bump; nt.links.new(n.outputs['Fac'], bp.inputs['Height']); nt.links.new(bp.outputs['Normal'], b.inputs['Normal'])
    return m
def link(o, coll):
    for c in o.users_collection: c.objects.unlink(o)
    coll.objects.link(o); return o
def new_coll(name, hide=False):
    c = bpy.data.collections.new(name); bpy.context.scene.collection.children.link(c)
    if hide: bpy.context.view_layer.layer_collection.children[name].exclude = True
    return c
def smooth(o):
    for p in o.data.polygons: p.use_smooth = True
    return o

# ---------------- ground, hills, river ----------------
GRASS = mat('grass', (0.16, 0.25, 0.08), 0.95, bump=0.6, bscale=180)
DIRT = mat('dirt', (0.42, 0.34, 0.24), 0.95, bump=0.4, bscale=90)
WATER = mat('water', (0.08, 0.2, 0.24), 0.05, bump=0.08, bscale=12)
WATER.node_tree.nodes['Principled BSDF'].inputs['Transmission Weight'].default_value = 0.3
bpy.ops.mesh.primitive_grid_add(x_subdivisions=200, y_subdivisions=200, size=120); g = bpy.context.object; g.name = 'ground'
for v in g.data.vertices:   # gentle undulation, river channel along x ~ 0
    x, y = v.co.x, v.co.y
    v.co.z = 0.25 * math.sin(x * 0.11) * math.cos(y * 0.13) + 0.15 * math.sin(x * 0.3 + y * 0.2)
    d = abs(y - 2.5 * math.sin(x * 0.07))
    if d < 4.5: v.co.z -= 0.6 * (1 - d / 4.5) ** 1.5
smooth(g)
# mix grass/dirt with noise
nt = GRASS.node_tree; b = nt.nodes['Principled BSDF']; tc = nt.nodes.new('ShaderNodeTexCoord'); n2 = nt.nodes.new('ShaderNodeTexNoise'); n2.inputs['Scale'].default_value = 0.15
nt.links.new(tc.outputs['Object'], n2.inputs['Vector']); cr = nt.nodes.new('ShaderNodeValToRGB'); cr.color_ramp.elements[0].position = 0.45; cr.color_ramp.elements[1].position = 0.6
cr.color_ramp.elements[0].color = (0.16, 0.26, 0.08, 1); cr.color_ramp.elements[1].color = (0.3, 0.3, 0.12, 1); nt.links.new(n2.outputs['Fac'], cr.inputs['Fac']); nt.links.new(cr.outputs['Color'], b.inputs['Base Color'])
g.data.materials.append(GRASS)
bpy.ops.mesh.primitive_grid_add(x_subdivisions=60, y_subdivisions=8, size=1); w = bpy.context.object; w.scale = (120, 9, 1); w.location.z = -0.22
for v in w.data.vertices: v.co.y += 2.5 * math.sin(v.co.x * 120 * 0.07) / 9
w.data.materials.append(WATER); w.name = 'river'
# animated water ripples
nt = WATER.node_tree; b = nt.nodes['Principled BSDF']; bp = [n for n in nt.nodes if n.type == 'BUMP'][0]; nz = [n for n in nt.nodes if n.type == 'TEX_NOISE'][0]
nz.noise_dimensions = '4D'; nz.inputs['W'].default_value = 0; nz.inputs['W'].keyframe_insert('default_value', frame=1); nz.inputs['W'].default_value = NF / 40; nz.inputs['W'].keyframe_insert('default_value', frame=NF)
# far hills
HILL = mat('hill', (0.2, 0.3, 0.14), 0.95, bump=0.5, bscale=40)
for k in range(9):
    bpy.ops.mesh.primitive_uv_sphere_add(radius=random.uniform(14, 22), location=(-60 + k * 15 + random.uniform(-4, 4), 60 + random.uniform(0, 8), -8)); h = bpy.context.object
    h.scale = (1.0, 0.6, random.uniform(0.5, 0.8)); h.data.materials.append(HILL); smooth(h)

# ---------------- toy trees (puffy sphere clusters) ----------------
TREES = new_coll('TREES', hide=True)
LEAF = [mat(f'leaf{i}', c, 0.85, bump=1.2, bscale=14) for i, c in enumerate([(0.12, 0.22, 0.09), (0.16, 0.27, 0.1), (0.1, 0.18, 0.08)])]
TRUNK = mat('trunk', (0.22, 0.15, 0.1), 0.9)
for t in range(4):
    parts = []
    bpy.ops.mesh.primitive_cylinder_add(radius=0.08, depth=1.0, location=(0, 0, 0.5)); parts.append(bpy.context.object); bpy.context.object.data.materials.append(TRUNK)
    for k in range(5 + t):
        bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=3, radius=random.uniform(0.35, 0.6), location=(random.uniform(-0.4, 0.4), random.uniform(-0.4, 0.4), 1.1 + random.uniform(0, 0.6)))
        o = bpy.context.object; o.data.materials.append(LEAF[(t + k) % 3]); smooth(o); parts.append(o)
    bpy.ops.object.select_all(action='DESELECT')
    for o in parts: o.select_set(True)
    bpy.context.view_layer.objects.active = parts[0]; bpy.ops.object.join(); tr = bpy.context.object; tr.name = f'tree{t}'; link(tr, TREES)
def scatter(coll, pts, scale=(0.8, 1.4), name='inst'):
    objs = list(coll.objects)
    for i, (x, y) in enumerate(pts):
        src = random.choice(objs); o = bpy.data.objects.new(f'{name}{i}', None); o.instance_type = 'COLLECTION'
        o.instance_collection = bpy.data.collections.new(f'_{name}{i}') if False else None
        o = src.copy(); o.data = src.data; bpy.context.scene.collection.objects.link(o)
        s = random.uniform(*scale); o.scale = (s, s, s); o.location = (x, y, ground_z(x, y)); o.rotation_euler.z = random.uniform(0, 6.28)
def ground_z(x, y):
    z = 0.25 * math.sin(x * 0.11) * math.cos(y * 0.13) + 0.15 * math.sin(x * 0.3 + y * 0.2); d = abs(y - 2.5 * math.sin(x * 0.07))
    if d < 4.5: z -= 0.6 * (1 - d / 4.5) ** 1.5
    return z
tp = []
while len(tp) < 260:
    x, y = random.uniform(-55, 55), random.uniform(-50, 55)
    if abs(y - 2.5 * math.sin(x * 0.07)) < 5.5: continue
    if -22 < x < 22 and (-26 < y < -5 or 8 < y < 26): continue   # keep army fields clear
    tp.append((x, y))
scatter(TREES, tp, (0.9, 1.8), 'tree')

# ---------------- soldiers: real MPFB humans from army.blend (instanced) ----------------
HS = float(os.environ.get('HS', 0.4))   # human scale in scene units (real 1.75 m -> 0.7)
ARMY = '/opt/reel/mini3d/army.blend'
with bpy.data.libraries.load(ARMY, link=False) as (src, dst): dst.collections = [c for c in src.collections if c.startswith('A_')]
HOLD = new_coll('HOLD', hide=True)
V = {}
for c in dst.collections:
    HOLD.children.link(c); V[c.name[2:]] = c
print('VARIANTS', list(V))
def inst(col, loc, rot, s=1.0, name='m'):
    e = bpy.data.objects.new(name, None); e.instance_type = 'COLLECTION'; e.instance_collection = col
    e.location = loc; e.rotation_euler.z = rot; e.scale = (s, s, s); bpy.context.scene.collection.objects.link(e); return e

# ---------------- animals: organic skin-modifier sculpts (real metres, facing -Y) ----------------
def skin_obj(name, verts, edges, radii, mat_, sub=2):
    me = bpy.data.meshes.new(name); me.from_pydata(verts, edges, []); o = bpy.data.objects.new(name, me); bpy.context.scene.collection.objects.link(o)
    sk = o.modifiers.new('skin', 'SKIN'); sk.use_smooth_shade = True
    for i, r in enumerate(radii):
        d = me.skin_vertices[0].data[i]; d.radius = r if isinstance(r, tuple) else (r, r)
    me.skin_vertices[0].data[0].use_root = True
    ss = o.modifiers.new('sub', 'SUBSURF'); ss.levels = ss.render_levels = sub
    o.data.materials.append(mat_)
    bpy.context.view_layer.objects.active = o; bpy.ops.object.select_all(action='DESELECT'); o.select_set(True)
    bpy.ops.object.convert(target='MESH'); return o
def wrinkled(name, col, scale=60.0, strength=0.5):
    m = bpy.data.materials.get(name)
    if m: return m
    m = mat(name, col, 0.85); nt = m.node_tree; b = nt.nodes['Principled BSDF']
    tc = nt.nodes.new('ShaderNodeTexCoord'); wv = nt.nodes.new('ShaderNodeTexWave'); wv.wave_type = 'RINGS'; wv.inputs['Scale'].default_value = scale * 0.2; wv.inputs['Distortion'].default_value = 8
    nz = nt.nodes.new('ShaderNodeTexNoise'); nz.inputs['Scale'].default_value = scale; nz.inputs['Detail'].default_value = 10
    nt.links.new(tc.outputs['Object'], wv.inputs['Vector']); nt.links.new(tc.outputs['Object'], nz.inputs['Vector'])
    mx = nt.nodes.new('ShaderNodeMath'); mx.operation = 'MULTIPLY'; nt.links.new(wv.outputs['Fac'], mx.inputs[0]); nt.links.new(nz.outputs['Fac'], mx.inputs[1])
    bp = nt.nodes.new('ShaderNodeBump'); bp.inputs['Strength'].default_value = strength; nt.links.new(mx.outputs[0], bp.inputs['Height']); nt.links.new(bp.outputs['Normal'], b.inputs['Normal'])
    return m
def cloth_mat(name, col, edge_z=1.62):
    m = bpy.data.materials.get(name)
    if m: return m
    m = mat(name, col, 0.75); nt = m.node_tree; b = nt.nodes['Principled BSDF']; b.inputs['Sheen Weight'].default_value = 0.5
    tc = nt.nodes.new('ShaderNodeTexCoord'); sep = nt.nodes.new('ShaderNodeSeparateXYZ'); nt.links.new(tc.outputs['Object'], sep.inputs[0])
    gt = nt.nodes.new('ShaderNodeMath'); gt.operation = 'LESS_THAN'; gt.inputs[1].default_value = edge_z; nt.links.new(sep.outputs['Z'], gt.inputs[0])
    mx = nt.nodes.new('ShaderNodeMix'); mx.data_type = 'RGBA'; mx.inputs['A'].default_value = (*col, 1); mx.inputs['B'].default_value = (1, 0.72, 0.3, 1)
    nt.links.new(gt.outputs[0], mx.inputs['Factor']); nt.links.new(mx.outputs['Result'], b.inputs['Base Color']); nt.links.new(gt.outputs[0], b.inputs['Metallic'])
    return m
def join(objs, name):
    bpy.ops.object.select_all(action='DESELECT')
    for o in objs: o.select_set(True)
    bpy.context.view_layer.objects.active = objs[0]; bpy.ops.object.join(); o = bpy.context.object; o.name = name; return o
def tusk(sx, IV):
    bpy.ops.curve.primitive_bezier_curve_add(); cu = bpy.context.object; sp = cu.data.splines[0]; cu.location = (0, 0, 0)
    p0, p1 = sp.bezier_points
    p0.co = (sx * 0.28, -2.15, 1.65); p0.handle_left = (sx * 0.27, -2.0, 1.8); p0.handle_right = (sx * 0.3, -2.4, 1.35)
    p1.co = (sx * 0.36, -2.8, 1.5); p1.handle_left = (sx * 0.35, -2.65, 1.3); p1.handle_right = (sx * 0.37, -2.9, 1.6); p1.radius = 0.25
    cu.data.bevel_depth = 0.075; cu.data.use_fill_caps = True; cu.data.materials.append(IV)
    bpy.ops.object.select_all(action='DESELECT'); cu.select_set(True); bpy.context.view_layer.objects.active = cu; bpy.ops.object.convert(target='MESH'); return cu
def elephant(name, cap_col=(0.55, 0.03, 0.04), royal=False):
    GREYM = wrinkled('ele_skin', (0.24, 0.22, 0.21)); IV = mat('ivory', (0.93, 0.9, 0.8), 0.35); G_ = mat('gold', (1, 0.72, 0.3), 0.3, 1.0)
    v = [(0, 0, 2.15), (0, -0.85, 2.1), (0, 0.85, 2.0), (0, -1.55, 2.25), (0, -1.95, 2.3), (0, -2.3, 2.0), (0, -2.42, 1.4), (0, -2.38, 0.8), (0, -2.25, 0.35), (0, 1.35, 1.75), (0, 1.5, 1.1)]
    r = [(1.0, 1.15), (0.92, 1.05), (0.9, 1.0), (0.62, 0.68), (0.6, 0.7), 0.3, 0.22, 0.15, 0.11, 0.1, 0.05]
    e = [(0, 1), (0, 2), (1, 3), (3, 4), (4, 5), (5, 6), (6, 7), (7, 8), (2, 9), (9, 10)]
    for sx in (-0.55, 0.55):
        for yy, root in ((-0.8, 1), (0.8, 2)):
            i = len(v); v += [(sx, yy, 1.5), (sx, yy - 0.05, 0.8), (sx, yy, 0.12)]; r += [0.42, 0.33, 0.36]; e += [(root, i), (i, i + 1), (i + 1, i + 2)]
    body = skin_obj(name, v, e, r, GREYM); parts = [body]
    for sx in (-1, 1):
        bpy.ops.mesh.primitive_uv_sphere_add(radius=0.55, location=(sx * 0.62, -1.7, 2.25), segments=24, ring_count=12); ear = bpy.context.object; ear.scale = (0.12, 0.85, 1.0); ear.rotation_euler = (0, sx * 0.25, sx * 0.35); ear.data.materials.append(GREYM); parts.append(ear)
        parts.append(tusk(sx, IV))
        bpy.ops.mesh.primitive_uv_sphere_add(radius=0.045, location=(sx * 0.5, -2.12, 2.42)); eye = bpy.context.object; eye.data.materials.append(mat('eye', (0.02, 0.015, 0.01), 0.1)); parts.append(eye)
    CAPM = cloth_mat('cap_' + name, cap_col)
    bpy.ops.mesh.primitive_cylinder_add(radius=1.12, depth=1.9, location=(0, 0, 2.1), rotation=(math.pi / 2, 0, 0), vertices=48); cp = bpy.context.object
    bm_ = bmesh.new(); bm_.from_mesh(cp.data); bmesh.ops.delete(bm_, geom=[f for f in bm_.faces if f.calc_center_median().y > 0.25 or len(f.verts) > 4], context='FACES'); bm_.to_mesh(cp.data); bm_.free()
    cp.modifiers.new('sol', 'SOLIDIFY').thickness = 0.03; cp.data.materials.append(CAPM); parts.append(cp)
    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.42, location=(0, -2.12, 2.35)); hp = bpy.context.object; hp.scale = (0.75, 0.15, 1.0); hp.data.materials.append(G_); parts.append(hp)
    bpy.ops.mesh.primitive_cube_add(location=(0, 0.05, 3.22)); hb = bpy.context.object; hb.scale = (0.62, 0.72, 0.06); hb.data.materials.append(G_); parts.append(hb)
    for sx in (-1, 1):
        for sy in (-1, 1):
            bpy.ops.mesh.primitive_cylinder_add(radius=0.035, depth=1.5 if royal else 0.55, location=(sx * 0.58, 0.05 + sy * 0.66, 3.25 + (0.75 if royal else 0.27)), vertices=10); parts.append(bpy.context.object); bpy.context.object.data.materials.append(G_)
        bpy.ops.mesh.primitive_cube_add(location=(sx * 0.6, 0.05, 3.52)); rl = bpy.context.object; rl.scale = (0.025, 0.7, 0.04); rl.data.materials.append(G_); parts.append(rl)
        bpy.ops.mesh.primitive_cube_add(location=(0, 0.05 + sx * 0.68, 3.52)); rl = bpy.context.object; rl.scale = (0.6, 0.025, 0.04); rl.data.materials.append(G_); parts.append(rl)
    if royal:
        bpy.ops.mesh.primitive_uv_sphere_add(radius=0.8, location=(0, 0.05, 4.0), segments=32, ring_count=16); dm = bpy.context.object; dm.scale = (0.9, 1.0, 0.7)
        bm_ = bmesh.new(); bm_.from_mesh(dm.data); bmesh.ops.delete(bm_, geom=[v_ for v_ in bm_.verts if v_.co.z < 0], context='VERTS'); bm_.to_mesh(dm.data); bm_.free(); dm.data.materials.append(G_); parts.append(dm)
        bpy.ops.mesh.primitive_cone_add(radius1=0.08, depth=0.35, location=(0, 0.05, 4.75)); parts.append(bpy.context.object); bpy.context.object.data.materials.append(G_)
    o = join(parts, name)
    for p in o.data.polygons: p.use_smooth = True
    return o
def horse(name, col=(0.03, 0.025, 0.02)):
    HM = wrinkled('horse_' + name, col, 120, 0.1)
    v = [(0, 0, 1.35), (0, -0.55, 1.4), (0, 0.6, 1.35), (0, -0.95, 1.75), (0, -1.15, 2.0), (0, -1.45, 1.75), (0, 0.85, 1.3), (0, 1.05, 0.7)]
    r = [(0.38, 0.45), (0.36, 0.42), (0.38, 0.44), 0.22, 0.17, 0.11, 0.08, 0.1]
    e = [(0, 1), (0, 2), (1, 3), (3, 4), (4, 5), (2, 6), (6, 7)]
    for sx in (-0.2, 0.2):
        for yy, root in ((-0.55, 1), (0.6, 2)):
            i = len(v); v += [(sx, yy, 1.05), (sx, yy + (0.08 if yy > 0 else 0), 0.55), (sx, yy, 0.05)]; r += [0.16, 0.07, 0.075]; e += [(root, i), (i, i + 1), (i + 1, i + 2)]
    o = skin_obj(name, v, e, r, HM)
    bpy.ops.mesh.primitive_cube_add(location=(0, -0.05, 1.8)); s_ = bpy.context.object; s_.scale = (0.4, 0.3, 0.05); s_.data.materials.append(mat('purple_saddle', (0.3, 0.03, 0.3), 0.6))
    o = join([o, s_], name)
    for p in o.data.polygons: p.use_smooth = True
    return o
MF = '/opt/reel/mini3d/mf'
def mf_asset(name, height, rot=0.0):
    p = f'{MF}/{name}.glb'
    if not os.path.exists(p): return None
    before = set(bpy.data.objects); bpy.ops.import_scene.gltf(filepath=p)
    objs = [o for o in bpy.data.objects if o not in before and o.type == 'MESH']
    for o in [o for o in bpy.data.objects if o not in before and o.type != 'MESH']: pass
    o = join(objs, name) if len(objs) > 1 else objs[0]; o.parent = None
    bpy.context.view_layer.objects.active = o; bpy.ops.object.select_all(action='DESELECT'); o.select_set(True)
    o.rotation_euler.z += rot; bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
    me = o.data; zs = [v.co.z for v in me.vertices]; z0 = min(zs); s_ = height / (max(zs) - z0)
    cx = sum(v.co.x for v in me.vertices) / len(me.vertices); cy = sum(v.co.y for v in me.vertices) / len(me.vertices)
    for v in me.vertices: v.co = Vector(((v.co.x - cx) * s_, (v.co.y - cy) * s_, (v.co.z - z0) * s_))
    o.location = (0, 0, 0); print('MF_ASSET', name, len(me.polygons)); return o
MFR = float(os.environ.get('MFROT', 0.0))
_we = mf_asset('war_elephant', 3.0, MFR); _pe = mf_asset('puru_elephant', 3.6, MFR); _hs = mf_asset('horse', 1.7, MFR)
ELE = new_coll('ELE', hide=True); link(_we or elephant('war_ele'), ELE); ROY = new_coll('ROY', hide=True); link(_pe or elephant('puru_ele', (0.08, 0.2, 0.55), royal=True), ROY)
HOR = new_coll('HOR', hide=True); link(_hs or horse('bucephalus'), HOR)
ES = HS / 1.75 * 1.0   # animals modelled in metres; humans are 1.75 m -> HS, so same metre scale
def army(cols, x0, x1, y0, y1, step, jitter, face, name):
    out = []; x = x0
    while x <= x1:
        y = y0
        while y <= y1:
            px, py = x + random.uniform(-jitter, jitter), y + random.uniform(-jitter, jitter)
            out.append(inst(random.choice(cols), (px, py, ground_z(px, py)), face + random.uniform(-0.12, 0.12), HS * random.uniform(0.94, 1.06), name)); y += step
        x += step
    return out
IND = [V[k] for k in V if k.startswith('ind_')]; GRK = [V[k] for k in V if k.startswith('greek')]
# Greeks on the far bank (north) facing the river (-Y = MPFB front); Indians on the near bank facing +Y
army(GRK, -16, 16, 11, 22, 0.42, 0.04, 0.0, 'greek')
army(IND, -16, 16, -22, -13, 0.46, 0.08, math.pi, 'indian')
for x in [x for x in range(-15, 16, 2) if abs(x) > 1]:
    inst(ELE, (x + random.uniform(-0.15, 0.15), -11.0, ground_z(x, -11)), math.pi + random.uniform(-0.08, 0.08), ES, 'ele')
inst(ROY, (0, -10.4, ground_z(0, -10.4)), math.pi, ES * 1.12, 'puru_ele')
inst(V['puru'], (0, -10.4 - 0.05 * ES, ground_z(0, -10.4) + float(os.environ.get('HOWDAH_Z', 3.28)) * ES * 1.12), math.pi, HS, 'puru')
inst(V['alexander'], (0.6, 9.4, ground_z(0.6, 9.4)), 0.0, HS * 1.03, 'alexander')
inst(HOR, (-0.4, 9.6, ground_z(-0.4, 9.6)), 0.3, ES, 'bucephalus')
# Greek camp tents
TENT = mat('tent', (0.9, 0.86, 0.75), 0.8); TENTR = mat('tentr', (0.55, 0.06, 0.05), 0.8)
for k in range(30):
    x, y = random.uniform(-20, 20), random.uniform(24, 32)
    bpy.ops.mesh.primitive_cone_add(vertices=6, radius1=0.7, depth=0.9, location=(x, y, ground_z(x, y) + 0.45)); bpy.context.object.data.materials.append(TENT if k % 3 else TENTR)
# ---------------- signboards (kitiki style) ----------------
def board(text, loc, rot_z=0.0, w=6.0, h=1.4, bg=(0.07, 0.07, 0.09), fg=(0.97, 0.95, 0.9), size=0.75, post=True):
    frame = mat('boardgold', (0.85, 0.62, 0.25), 0.35, 1.0)
    bpy.ops.mesh.primitive_cube_add(location=(0, 0, 0)); p = bpy.context.object; p.scale = (w / 2, 0.06, h / 2); p.data.materials.append(mat('board' + str(bg), bg, 0.5))
    bpy.ops.mesh.primitive_cube_add(location=(0, 0.01, 0)); fr = bpy.context.object; fr.scale = (w / 2 + 0.06, 0.055, h / 2 + 0.06); fr.data.materials.append(frame)
    bpy.ops.object.text_add(location=(0, -0.08, -size * 0.35)); t = bpy.context.object; t.data.body = text; t.data.align_x = 'CENTER'; t.data.size = size; t.data.extrude = 0.01
    t.rotation_euler = (math.pi / 2, 0, 0); t.data.materials.append(mat('boardtext' + str(fg), fg, 0.4))
    try: t.data.font = bpy.data.fonts.load('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf')
    except Exception: pass
    objs = [p, fr, t]
    if post:
        for sx in (-1, 1):
            bpy.ops.mesh.primitive_cylinder_add(radius=0.05, depth=2.2, location=(sx * w * 0.42, 0.02, -h / 2 - 1.05)); objs.append(bpy.context.object); bpy.context.object.data.materials.append(frame)
    e = bpy.data.objects.new('board_' + text[:8], None); bpy.context.scene.collection.objects.link(e)
    for o in objs: o.parent = e
    e.location = loc; e.rotation_euler.z = rot_z; return e
if not os.environ.get('NOBOARDS'): board('326 BC', (-6, -4.2, 2.6), 0.0, w=4.2, size=0.9)
if not os.environ.get('NOBOARDS'): board('HYDASPES RIVER', (8, -5.0, 2.3), 0.0, w=7.5, bg=(0.08, 0.2, 0.55), size=0.7)
if not os.environ.get('NOBOARDS'): board('ALEXANDER', (5.5, 7.2, 2.6), 0.0, w=5.5, bg=(0.5, 0.05, 0.05), size=0.8)
if not os.environ.get('NOBOARDS'): board('200 WAR ELEPHANTS', (-10, -9.0, 2.4), 0.0, w=9.0, bg=(0.07, 0.07, 0.09), size=0.7)

# ---------------- light, render ----------------
w_ = bpy.data.worlds.new('w'); sc.world = w_; w_.use_nodes = True; bg = w_.node_tree.nodes['Background']
sky = w_.node_tree.nodes.new('ShaderNodeTexSky'); sky.sky_type = 'NISHITA'; sky.sun_elevation = math.radians(32); sky.sun_rotation = math.radians(140); sky.sun_disc = False
w_.node_tree.links.new(sky.outputs[0], bg.inputs[0]); bg.inputs[1].default_value = 0.18
bpy.ops.object.light_add(type='SUN', rotation=(math.radians(55), 0, math.radians(140))); sun = bpy.context.object; sun.data.energy = 3.2; sun.data.color = (1, 0.9, 0.78); sun.data.angle = math.radians(4)
sc.render.engine = 'CYCLES'; sc.cycles.device = 'GPU'
prefs = bpy.context.preferences.addons['cycles'].preferences; prefs.compute_device_type = 'OPTIX'; prefs.get_devices()
for d in prefs.devices: d.use = (d.type == 'OPTIX')
sc.cycles.samples = int(os.environ.get('SPP', 32)); sc.cycles.use_denoising = True; sc.cycles.denoiser = 'OPTIX'
sc.render.resolution_x, sc.render.resolution_y = 1080, 1920; sc.render.resolution_percentage = int(os.environ.get('PCT', 100))
sc.view_settings.view_transform = 'AgX'; sc.view_settings.look = 'AgX - Medium High Contrast'; sc.view_settings.exposure = float(os.environ.get('EV', 0.0))
sc.render.image_settings.file_format = 'JPEG'; sc.render.image_settings.quality = 92

# ---------------- cameras (tilt-shift: strong DOF on a small focus band) ----------------
cam_d = bpy.data.cameras.new('cam'); cam = bpy.data.objects.new('cam', cam_d); sc.collection.objects.link(cam); sc.camera = cam
tgt = bpy.data.objects.new('tgt', None); sc.collection.objects.link(tgt)
tc = cam.constraints.new('TRACK_TO'); tc.target = tgt; tc.track_axis = 'TRACK_NEGATIVE_Z'; tc.up_axis = 'UP_Y'
cam_d.dof.use_dof = True; cam_d.dof.focus_object = tgt; cam_d.dof.aperture_fstop = 0.35; cam_d.lens = 35
def key(o, f, loc):
    o.location = loc; o.keyframe_insert('location', frame=f)
def ease_all(o):
    for fc in o.animation_data.action.fcurves:
        for kp in fc.keyframe_points: kp.interpolation = 'BEZIER'; kp.easing = 'EASE_IN_OUT'
SHOTS = {
  # A: establishing aerial over the valley, slow drift + crane down toward the river, both armies in frame
  'A': [((-9, -52, 32), (0, 2, 0), 1.6), ((5, -30, 11), (0, -3, 0.5), 1.1)],
  # B: low dolly along the Indian front between the elephants, ending in a push-in on Puru in his howdah
  'B': [((-15, -6.6, 1.3), (-9, -11, 1.0), 2.0), ((1.2, -7.0, 1.9), (0, -10.4, 1.6), 1.4)],
  # C: low hero orbit around Alexander with the phalanx behind
  'C': [((2.4, 7.3, 0.55), (0.5, 9.4, 0.5), 1.2), ((-1.6, 7.5, 0.7), (0.5, 9.4, 0.55), 1.2)],
}
(c0, t0, f0), (c1, t1, f1) = SHOTS.get(SHOT, SHOTS['A'])
key(cam, 1, c0); key(cam, NF, c1); key(tgt, 1, t0); key(tgt, NF, t1); ease_all(cam); ease_all(tgt)
cam_d.dof.aperture_fstop = f0; cam_d.dof.keyframe_insert('aperture_fstop', frame=1); cam_d.dof.aperture_fstop = f1; cam_d.dof.keyframe_insert('aperture_fstop', frame=NF)
sc.render.use_motion_blur = True; sc.render.motion_blur_shutter = 0.4
sc.render.filepath = OUT + '/'
bpy.ops.wm.save_as_mainfile(filepath=f'/opt/reel/mini3d/diorama2_{SHOT}.blend')
if os.environ.get('TRACK'):
    import json
    from bpy_extras.object_utils import world_to_camera_view
    pz = ground_z(0, -10.4) + float(os.environ.get('HOWDAH_Z', 3.28)) * ES * 1.12 + HS * 1.05
    A = {'river': (-3.0, 2.5 * math.sin(-0.21), 0.0), 'greek': (0, 16.5, 0.6), 'indian': (0, -17.5, 0.6), 'elephants': (-7.0, -11.0, 1.1),
         'puru': (0, -10.4, pz), 'alexander': (0.6, 9.4, ground_z(0.6, 9.4) + HS * 1.05), 'horse': (-0.4, 9.6, ground_z(-0.4, 9.6) + ES * 1.5)}
    out = {}
    for f in range(1, NF + 1):
        sc.frame_set(f); fr = {}
        for k, p in A.items():
            v = world_to_camera_view(sc, cam, Vector(p)); fr[k] = [round(v.x, 4), round(1 - v.y, 4), round(v.z, 2)]
        out[f] = fr
    json.dump(out, open(f'/opt/reel/mini3d/tracks_{SHOT}.json', 'w')); print('TRACKS_DONE', SHOT); raise SystemExit

if os.environ.get('STILL'):
    sc.frame_set(int(os.environ['STILL'])); sc.render.filepath = OUT + f'/still_{os.environ["STILL"]}.jpg'; bpy.ops.render.render(write_still=True)
else:
    bpy.ops.render.render(animation=True)
print('DIORAMA_DONE', SHOT)
