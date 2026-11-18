# Puru vs Alexander: 12-shot tilt-shift miniature diorama, built only from the GLBs in reels/porus/assets.
# blender -b -P diorama3.py -- SHOT NF            render one shot (NF frames) to $OUT/<shot>/####.jpg
# env: ASSETS (assets dir), OUT (render dir), FPS (30), PCT (resolution %), SPP (samples), DEVICE (GPU|CPU),
#      STILL=<frame> render one frame only, TRACK=1 write label tracks json and exit, SAVE=1 save .blend
import bpy, bmesh, math, random, os, sys, json
from mathutils import Vector, Matrix
argv = sys.argv[sys.argv.index('--') + 1:] if '--' in sys.argv else ['open', '120']
SHOT = argv[0]; NF = int(argv[1]) if len(argv) > 1 else 120
HERE = os.path.dirname(os.path.abspath(__file__))
ASSETS = os.environ.get('ASSETS', os.path.join(HERE, '..', 'assets'))
OUT = os.environ.get('OUT', os.path.join(HERE, 'out3')); SD = os.path.join(OUT, SHOT); os.makedirs(SD, exist_ok=True)
FPS = int(os.environ.get('FPS', 30))
random.seed(7)
for o in list(bpy.data.objects): bpy.data.objects.remove(o)
sc = bpy.context.scene; sc.frame_start, sc.frame_end = 1, NF; sc.render.fps = FPS
S = 0.4                      # miniature scale: 1 m in the world = 0.4 scene units (a 1.75 m man is 0.7)
def T(u): return 1 + round(u * (NF - 1))       # normalised shot time 0..1 -> frame

# ---------------------------------------------------------------- helpers
def mat(name, col, rough=0.6, metal=0.0, emit=0.0, bump=0.0, bscale=30.0, ecol=None):
    m = bpy.data.materials.get(name)
    if m: return m
    m = bpy.data.materials.new(name); m.use_nodes = True; nt = m.node_tree; b = nt.nodes['Principled BSDF']
    b.inputs['Base Color'].default_value = (*col, 1); b.inputs['Roughness'].default_value = rough; b.inputs['Metallic'].default_value = metal
    if emit: b.inputs['Emission Color'].default_value = (*(ecol or col), 1); b.inputs['Emission Strength'].default_value = emit
    if bump:
        tc = nt.nodes.new('ShaderNodeTexCoord'); n = nt.nodes.new('ShaderNodeTexNoise'); n.inputs['Scale'].default_value = bscale; n.inputs['Detail'].default_value = 8
        nt.links.new(tc.outputs['Object'], n.inputs['Vector'])
        bp = nt.nodes.new('ShaderNodeBump'); bp.inputs['Strength'].default_value = bump; nt.links.new(n.outputs['Fac'], bp.inputs['Height']); nt.links.new(bp.outputs['Normal'], b.inputs['Normal'])
    return m
def new_coll(name, hide=False):
    c = bpy.data.collections.new(name); sc.collection.children.link(c)
    if hide: bpy.context.view_layer.layer_collection.children[name].exclude = True
    return c
def link(o, coll):
    for c in o.users_collection: c.objects.unlink(o)
    coll.objects.link(o); return o
def smooth(o):
    for p in o.data.polygons: p.use_smooth = True
    return o
def join(objs, name):
    bpy.ops.object.select_all(action='DESELECT')
    for o in objs: o.select_set(True)
    bpy.context.view_layer.objects.active = objs[0]
    bpy.ops.object.transform_apply(location=True, rotation=True, scale=True); bpy.ops.object.join(); o = bpy.context.object; o.name = name; return o
def key(o, f, **kw):
    for k, v in kw.items():
        setattr(o, k, v); o.keyframe_insert(k, frame=f)
def ease(o, kind='EASE_IN_OUT', interp='BEZIER'):
    ad = o.animation_data
    if not ad or not ad.action: return
    for fc in ad.action.fcurves:
        for kp in fc.keyframe_points: kp.interpolation = interp; kp.easing = kind
def linear(o): ease(o, 'AUTO', 'LINEAR')

# ---------------------------------------------------------------- terrain
def river_y(x): return 2.5 * math.sin(x * 0.07)
def ground_z(x, y):
    z = 0.25 * math.sin(x * 0.11) * math.cos(y * 0.13) + 0.15 * math.sin(x * 0.3 + y * 0.2); d = abs(y - river_y(x))
    if d < 4.5: z -= 0.6 * (1 - d / 4.5) ** 1.5
    return z
GRASS = mat('grass', (0.16, 0.25, 0.08), 0.95, bump=0.6, bscale=180)
nt = GRASS.node_tree; b = nt.nodes['Principled BSDF']; tc = nt.nodes.new('ShaderNodeTexCoord'); n2 = nt.nodes.new('ShaderNodeTexNoise'); n2.inputs['Scale'].default_value = 0.15
nt.links.new(tc.outputs['Object'], n2.inputs['Vector']); cr = nt.nodes.new('ShaderNodeValToRGB'); cr.color_ramp.elements[0].position = 0.45; cr.color_ramp.elements[1].position = 0.62
cr.color_ramp.elements[0].color = (0.16, 0.26, 0.08, 1); cr.color_ramp.elements[1].color = (0.32, 0.31, 0.13, 1); nt.links.new(n2.outputs['Fac'], cr.inputs['Fac']); nt.links.new(cr.outputs['Color'], b.inputs['Base Color'])
bpy.ops.mesh.primitive_grid_add(x_subdivisions=220, y_subdivisions=220, size=130); g = bpy.context.object; g.name = 'ground'
for v in g.data.vertices: v.co.z = ground_z(v.co.x, v.co.y)
smooth(g); g.data.materials.append(GRASS)
WATER = mat('water', (0.07, 0.19, 0.24), 0.04, bump=0.08, bscale=12); WATER.node_tree.nodes['Principled BSDF'].inputs['Transmission Weight'].default_value = 0.3
bpy.ops.mesh.primitive_grid_add(x_subdivisions=80, y_subdivisions=8, size=1); river = bpy.context.object; river.scale = (130, 9, 1); river.location.z = -0.22
for v in river.data.vertices: v.co.y += river_y(v.co.x * 130) / 9
river.data.materials.append(WATER); river.name = 'river'
nz = [n for n in WATER.node_tree.nodes if n.type == 'TEX_NOISE'][0]; nz.noise_dimensions = '4D'
nz.inputs['W'].default_value = 0; nz.inputs['W'].keyframe_insert('default_value', frame=1); nz.inputs['W'].default_value = NF / 40; nz.inputs['W'].keyframe_insert('default_value', frame=NF)
HILL = mat('hill', (0.2, 0.3, 0.14), 0.95, bump=0.5, bscale=40)
for k in range(10):
    bpy.ops.mesh.primitive_uv_sphere_add(radius=random.uniform(14, 22), location=(-70 + k * 15 + random.uniform(-4, 4), 62 + random.uniform(0, 8), -8)); h = bpy.context.object
    h.scale = (1.0, 0.6, random.uniform(0.5, 0.8)); h.data.materials.append(HILL); smooth(h)
# puffy toy trees
TREES = new_coll('TREES', hide=True)
LEAF = [mat(f'leaf{i}', c, 0.85, bump=1.2, bscale=14) for i, c in enumerate([(0.12, 0.22, 0.09), (0.16, 0.27, 0.1), (0.1, 0.18, 0.08)])]
TRUNK = mat('trunk', (0.22, 0.15, 0.1), 0.9)
for t in range(4):
    parts = []
    bpy.ops.mesh.primitive_cylinder_add(radius=0.08, depth=1.0, location=(0, 0, 0.5)); parts.append(bpy.context.object); bpy.context.object.data.materials.append(TRUNK)
    for k in range(5 + t):
        bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=3, radius=random.uniform(0.35, 0.6), location=(random.uniform(-0.4, 0.4), random.uniform(-0.4, 0.4), 1.1 + random.uniform(0, 0.6)))
        o = bpy.context.object; o.data.materials.append(LEAF[(t + k) % 3]); smooth(o); parts.append(o)
    link(join(parts, f'tree{t}'), TREES)
def inst(col, loc, rot=0.0, s=1.0, name='m'):
    e = bpy.data.objects.new(name, None); e.instance_type = 'COLLECTION'; e.instance_collection = col
    e.location = loc; e.rotation_euler.z = rot; e.scale = (s, s, s); sc.collection.objects.link(e); return e
TREE_C = list(TREES.objects)
TC = {}
for t in TREE_C:
    c = new_coll('T_' + t.name, hide=True); link(t, c); TC[t.name] = c
def tree_at(x, y, s=None):
    return inst(random.choice(list(TC.values())), (x, y, ground_z(x, y)), random.uniform(0, 6.28), s or random.uniform(0.9, 1.8), 'tree')
FIELDS = [(-22, 22, -26, -5), (-22, 22, 8, 26), (18, 42, -24, -2), (-42, -26, 10, 24)]
def clear(x, y):
    if abs(y - river_y(x)) < 5.5: return False
    return not any(a < x < b and c < y < d for a, b, c, d in FIELDS)
tp = 0
while tp < 300:
    x, y = random.uniform(-60, 60), random.uniform(-55, 58)
    if clear(x, y) and not (-6 < x < 6 and -44 < y < -30): tree_at(x, y); tp += 1

# ---------------------------------------------------------------- figures (GLB) and animals
def load_glb(path, name):
    before = set(bpy.data.objects); bpy.ops.import_scene.gltf(filepath=path)
    new = [o for o in bpy.data.objects if o not in before]
    c = new_coll(name, hide=True)
    for o in new: link(o, c)
    return c
SOLD = {}
for n in ['ind_spear_red', 'ind_spear_saffron', 'ind_spear_white', 'ind_sword', 'greek_white', 'greek_red', 'alexander', 'puru']:
    SOLD[n] = load_glb(os.path.join(ASSETS, 'soldiers_glb', n + '.glb'), 'S_' + n)
ANI = {n: load_glb(os.path.join(ASSETS, 'animals_glb', n + '.glb'), 'A_' + n) for n in ['war_elephant', 'puru_elephant', 'horse']}
SEAT = 3.2                                  # howdah seat height in metres (animals_glb README)
IND = [SOLD[k] for k in ['ind_spear_red'] * 6 + ['ind_spear_saffron'] * 3 + ['ind_spear_white'] * 1 + ['ind_sword'] * 1]
GRK = [SOLD['greek_white'], SOLD['greek_red'], SOLD['greek_red']]
def man(col, x, y, rot, name='man', dz=0.0):
    return inst(col, (x, y, ground_z(x, y) + dz), rot, S * random.uniform(0.95, 1.05), name)
def army(cols, x0, x1, y0, y1, sx, sy, face, name, jit=0.04, keep=None):
    out = []; x = x0
    while x <= x1:
        y = y0
        while y <= y1:
            px, py = x + random.uniform(-jit, jit), y + random.uniform(-jit, jit)
            if keep is None or keep(px, py): out.append(man(random.choice(cols), px, py, face + random.uniform(-0.1, 0.1), name))
            y += sy
        x += sx
    return out
FACE_N, FACE_S = 0.0, math.pi       # glb figures face -Y; rot pi faces +Y (north, toward the river from the south bank)

# ---------------------------------------------------------------- props
GOLD = mat('gold', (1.0, 0.72, 0.3), 0.28, 1.0)
WOOD = mat('wood', (0.33, 0.2, 0.1), 0.8, bump=0.3, bscale=40)
STONE = mat('stone', (0.62, 0.56, 0.48), 0.9, bump=0.8, bscale=25)
TENT = mat('tent', (0.9, 0.86, 0.75), 0.8); TENTR = mat('tentr', (0.55, 0.06, 0.05), 0.8)
def cube(loc, scale, m, rot=(0, 0, 0)):
    bpy.ops.mesh.primitive_cube_add(location=loc, rotation=rot); o = bpy.context.object; o.scale = scale; o.data.materials.append(m); return o
def tents(n=34):
    for k in range(n):
        x, y = random.uniform(-20, 20), random.uniform(24, 32)
        bpy.ops.mesh.primitive_cone_add(vertices=6, radius1=0.7, depth=0.9, location=(x, y, ground_z(x, y) + 0.45)); bpy.context.object.data.materials.append(TENT if k % 3 else TENTR)
def torch(loc, strength=6.0):
    fl = mat('flame', (1.0, 0.45, 0.1), 0.5, emit=60.0)
    bpy.ops.mesh.primitive_cylinder_add(radius=0.012, depth=0.32, location=(loc[0], loc[1], loc[2] - 0.16)); bpy.context.object.data.materials.append(WOOD)
    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.045, location=loc); f = bpy.context.object; f.data.materials.append(fl); f.scale = (1, 1, 1.7)
    bpy.ops.object.light_add(type='POINT', location=(loc[0], loc[1], loc[2] + 0.05)); L = bpy.context.object; L.data.energy = strength; L.data.color = (1, 0.55, 0.2); L.data.shadow_soft_size = 0.05
    return [f, L]
def banner(loc, col, h=1.1):
    bpy.ops.mesh.primitive_cylinder_add(radius=0.012, depth=h, location=(loc[0], loc[1], loc[2] + h / 2)); p = bpy.context.object; p.data.materials.append(WOOD)
    bpy.ops.mesh.primitive_plane_add(size=1, location=(loc[0] + 0.16, loc[1], loc[2] + h - 0.12), rotation=(math.pi / 2, 0, 0)); f = bpy.context.object; f.scale = (0.3, 0.2, 1)
    f.data.materials.append(mat('flag' + str(col), col, 0.7)); f.modifiers.new('w', 'WAVE').height = 0.02
    return [p, f]
def fort(cx, cy, rot=0.0):
    """Taxila: stone walls with crenellations, two gate towers, an arched wooden gate facing -Y local."""
    parts = []
    W, D, H = 6.0, 4.0, 1.2
    for (x, y, sx, sy) in [(0, D / 2, W / 2, 0.15), (-W / 2, 0, 0.15, D / 2), (W / 2, 0, 0.15, D / 2), (-W / 4 - 0.45, -D / 2, W / 4 - 0.45, 0.15), (W / 4 + 0.45, -D / 2, W / 4 - 0.45, 0.15)]:
        parts.append(cube((x, y, H / 2), (sx, sy, H / 2), STONE))
        n = int(max(sx, sy) * 2 / 0.3)
        for k in range(n):
            t = -1 + (2 * k + 1) / n
            parts.append(cube((x + (t * sx if sx > sy else 0), y + (t * sy if sy > sx else 0), H + 0.08), (0.08 if sx > sy else 0.17, 0.17 if sx > sy else 0.08, 0.08), STONE))
    for sx in (-1, 1):
        bpy.ops.mesh.primitive_cylinder_add(radius=0.45, depth=1.9, location=(sx * 0.9, -D / 2, 0.95), vertices=20); t = bpy.context.object; t.data.materials.append(STONE); parts.append(t)
        bpy.ops.mesh.primitive_cone_add(radius1=0.55, depth=0.7, location=(sx * 0.9, -D / 2, 2.25), vertices=20); c = bpy.context.object; c.data.materials.append(TENTR); parts.append(c)
    parts.append(cube((0, -D / 2 + 0.02, 0.5), (0.45, 0.06, 0.5), WOOD))
    o = join(parts, 'fort'); o.location = (cx, cy, ground_z(cx, cy)); o.rotation_euler.z = rot; return o
def chariot(x, y, rot, sink=0.0, name='chariot'):
    parts = [cube((0, 0, 0.5), (0.32, 0.24, 0.05), WOOD), cube((0, -0.23, 0.68), (0.32, 0.015, 0.14), GOLD),
             cube((-0.31, 0, 0.62), (0.015, 0.24, 0.1), WOOD), cube((0.31, 0, 0.62), (0.015, 0.24, 0.1), WOOD)]
    bpy.ops.mesh.primitive_cylinder_add(radius=0.022, depth=1.0, location=(0, 0, 0.4), rotation=(0, math.pi / 2, 0)); parts.append(bpy.context.object); bpy.context.object.data.materials.append(WOOD)
    for sx in (-1, 1):
        bpy.ops.mesh.primitive_torus_add(major_radius=0.38, minor_radius=0.03, location=(sx * 0.46, 0, 0.4), rotation=(0, math.pi / 2, 0)); w = bpy.context.object; w.data.materials.append(WOOD); parts.append(w)
        for k in range(4):
            bpy.ops.mesh.primitive_cylinder_add(radius=0.01, depth=0.76, location=(sx * 0.46, 0, 0.4), rotation=(k * math.pi / 4, 0, 0)); sp = bpy.context.object; sp.data.materials.append(WOOD); parts.append(sp)
    bpy.ops.mesh.primitive_cylinder_add(radius=0.02, depth=1.3, location=(0, -0.85, 0.5), rotation=(math.pi / 2, 0, 0)); parts.append(bpy.context.object); bpy.context.object.data.materials.append(WOOD)
    o = join(parts, name); o.scale = (S * 1.7,) * 3; o.location = (x, y, ground_z(x, y) - sink); o.rotation_euler.z = rot; return o

# ---------------------------------------------------------------- lighting presets
w_ = bpy.data.worlds.new('w'); sc.world = w_; w_.use_nodes = True; wn = w_.node_tree; bg = wn.nodes['Background']
sky = wn.nodes.new('ShaderNodeTexSky'); sky.sky_type = 'NISHITA'; sky.sun_disc = False; wn.links.new(sky.outputs[0], bg.inputs[0])
bpy.ops.object.light_add(type='SUN'); sun = bpy.context.object; sun.data.angle = math.radians(4)
PRESET = ['day']
def light(preset):
    PRESET[0] = preset; az = math.radians(140)
    if preset == 'day':
        el = math.radians(35); sun.data.energy = 3.2; sun.data.color = (1, 0.9, 0.78); bg.inputs[1].default_value = 0.18
    elif preset == 'golden':
        el = math.radians(16); sun.data.energy = 3.0; sun.data.color = (1, 0.74, 0.48); bg.inputs[1].default_value = 0.3
    elif preset == 'sunset':
        el = math.radians(5); sun.data.energy = 2.6; sun.data.color = (1, 0.55, 0.3); bg.inputs[1].default_value = 0.14; az = math.radians(200)
    elif preset in ('night', 'storm'):
        el = math.radians(40); sun.data.energy = 0.55; sun.data.color = (0.55, 0.66, 1.0)
        wn.links.remove(bg.inputs[0].links[0]); bg.inputs[0].default_value = (0.025, 0.04, 0.09, 1); bg.inputs[1].default_value = 1.0
    elif preset == 'interior':
        el = math.radians(40); sun.data.energy = 0.0; bg.inputs[0].default_value = (0, 0, 0, 1)
        if bg.inputs[0].links: wn.links.remove(bg.inputs[0].links[0])
    sky.sun_elevation = el; sky.sun_rotation = az + math.pi          # Nishita measures rotation from the opposite side to the lamp
    sun.rotation_euler = (math.pi / 2 - el, 0, az)
def lightning(times):
    """storm flashes: world strength and a big area light spike at the given normalised times"""
    bpy.ops.object.light_add(type='AREA', location=(20, 10, 40)); fl = bpy.context.object; fl.data.size = 60; fl.data.color = (0.8, 0.85, 1)
    fl.data.energy = 0; fl.data.keyframe_insert('energy', frame=1)
    for u in times:
        f = T(u)
        for df, e in ((-1, 0), (0, 45000), (1, 12000), (2, 30000), (4, 0)):
            fl.data.energy = e; fl.data.keyframe_insert('energy', frame=max(1, f + df))
    for fc in fl.data.animation_data.action.fcurves:
        for kp in fc.keyframe_points: kp.interpolation = 'CONSTANT'

# ---------------------------------------------------------------- base armies (most shots)
def base_armies(greek=True, indian=True, elephants=True, tents_=True):
    if greek: army(GRK, -16, 16, 11, 22, 0.42, 0.42, FACE_N, 'greek')
    if indian: army(IND, -16, 16, -22, -13, 0.46, 0.46, FACE_S, 'indian')
    if elephants:
        for x in [x for x in range(-15, 16, 2) if abs(x) > 1]:
            inst(ANI['war_elephant'], (x, -11.0, ground_z(x, -11)), FACE_S + random.uniform(-0.06, 0.06), S, 'ele')
    if tents_: tents()
def puru_on_elephant(x=0.0, y=-10.4, rot=FACE_S):
    e = inst(ANI['puru_elephant'], (x, y, ground_z(x, y)), rot, S * 1.1, 'puru_ele')
    p = inst(SOLD['puru'], (x, y + 0.42 * S * 1.1 * (1 if rot == FACE_S else -1) * 0, ground_z(x, y) + SEAT * S * 1.1 - 0.02), rot, S, 'puru')
    return e, p
def alexander_and_horse():
    inst(SOLD['alexander'], (0.6, 9.4, ground_z(0.6, 9.4)), FACE_N, S * 1.03, 'alexander')
    inst(ANI['horse'], (-0.4, 9.6, ground_z(-0.4, 9.6)), 0.3, S, 'bucephalus')

# ---------------------------------------------------------------- camera
cam_d = bpy.data.cameras.new('cam'); cam = bpy.data.objects.new('cam', cam_d); sc.collection.objects.link(cam); sc.camera = cam
tgt = bpy.data.objects.new('tgt', None); sc.collection.objects.link(tgt)
c_ = cam.constraints.new('TRACK_TO'); c_.target = tgt; c_.track_axis = 'TRACK_NEGATIVE_Z'; c_.up_axis = 'UP_Y'
cam_d.dof.use_dof = True; cam_d.dof.focus_object = tgt; cam_d.lens = 35
def move(keys, lens=35):
    """keys: [(u, cam_xyz, target_xyz, fstop)] -- eased between keys"""
    cam_d.lens = lens
    for u, c, t, fs in keys:
        key(cam, T(u), location=Vector(c)); key(tgt, T(u), location=Vector(t))
        cam_d.dof.aperture_fstop = fs; cam_d.dof.keyframe_insert('aperture_fstop', frame=T(u))
    ease(cam); ease(tgt)
TRACKS = {}                                   # label name -> world point (or callable frame->point) for the Telugu pins
def gz(x, y, h=0.0): return (x, y, ground_z(x, y) + h)

# ================================================================= the twelve shots
if SHOT == 'open':          # aerial crane-down over the valley to the river
    light('golden'); base_armies(); puru_on_elephant(); alexander_and_horse()
    move([(0, (-9, -60, 38), (0, 4, 0), 2.2), (1, (4, -31, 11.5), (0, -2.5, 0.4), 1.2)])
    TRACKS = {'greek': gz(0, 16.5, 0.6), 'indian': gz(0, -17.5, 0.6), 'river': (-3.0, river_y(-3.0), 0.0)}
elif SHOT == 'demand':      # a Greek messenger rides across the ford to Puru's lines; slow push-in
    light('day'); base_armies(); puru_on_elephant(); alexander_and_horse()
    hx = 5.0
    hr = inst(ANI['horse'], gz(hx, 8.0), FACE_N, S, 'messenger_horse'); rd = inst(SOLD['greek_white'], gz(hx + 0.18, 8.0), FACE_N, S, 'messenger')
    for o, dx in ((hr, 0.0), (rd, 0.18)):
        for u, y in ((0, 7.5), (1, -6.2)):
            key(o, T(u), location=Vector((hx + dx, y, ground_z(hx, y) + (0.0 if abs(y - river_y(hx)) > 3 else 0.0))))
        o.rotation_euler.z = FACE_N; linear(o)   # rides from the Greek bank (+Y) toward Puru (-Y): face the way it goes
    move([(0, (11, 1.5, 3.2), (hx, 5.0, 0.4), 1.6), (1, (8.0, -9.5, 1.2), (hx, -5.5, 0.35), 1.0)])
    TRACKS = {'messenger': lambda f: tuple(rd.matrix_world.translation + Vector((0, 0, 0.75))), 'puru': gz(0, -10.4, SEAT * S * 1.1 + 0.7)}
elif SHOT == 'ambhi':       # pull-out from Taxila's gate as Ambhi's men march to the Greek camp
    light('day'); base_armies(); alexander_and_horse()
    fort(-34, 17, 0.0)
    col = []
    for r_ in range(12):
        for c in range(5):
            col.append(man(SOLD['ind_spear_white'], -34 + (c - 2) * 0.42, 14.4 - r_ * 0.42, FACE_N, 'ambhi_men'))
    fl = banner(gz(-34.9, 14.6), (0.95, 0.55, 0.08))
    for o in col + fl:
        p0 = o.location.copy(); key(o, 1, location=p0); key(o, NF, location=p0 + Vector((7.5, 1.2, 0))); linear(o)
    move([(0, (-30.2, 11.8, 1.1), (-34, 16.0, 0.8), 1.2), (1, (-26, 3.5, 6.5), (-31, 14, 0.5), 2.2)])
    TRACKS = {'fort': gz(-34, 19, 2.4), 'ambhi': lambda f: tuple(fl[1].matrix_world.translation + Vector((0, 0, 0.2)))}
elif SHOT == 'river':       # low glide over the swollen river toward the elephant line
    light('day'); base_armies(); puru_on_elephant(); alexander_and_horse()
    key(river, 1, location=Vector((0, 0, -0.26))); key(river, NF, location=Vector((0, 0, -0.06))); ease(river)
    move([(0, (2, 3.8, 0.3), (0, -6, 0.2), 1.0), (1, (0.5, -5.2, 0.75), (-2, -11, 0.55), 1.4)], lens=28)
    TRACKS = {'river': (1.0, river_y(1.0), 0.0), 'elephants': gz(-5, -11, 1.1)}
elif SHOT == 'feint':       # night; torch riders run up and down the far bank; lateral dolly
    light('night'); base_armies(); alexander_and_horse()
    for i in range(7):
        x0 = -14 + i * 4.2; y = 6.4 + (i % 2) * 0.5
        h = inst(ANI['horse'], gz(x0, y), FACE_N + math.pi / 2, S, 'rider_h'); r_ = inst(SOLD['greek_red'], gz(x0, y), FACE_N + math.pi / 2, S, 'rider')
        fl = torch((x0, y, ground_z(x0, y) + 0.95), 25)
        for o in [h, r_] + fl:
            p0 = o.location.copy(); amp = 2.6
            for k in range(5):
                key(o, T(k / 4), location=p0 + Vector(((amp if k % 2 else -amp) * (1 if i % 2 else -1), 0, 0)))
            ease(o, 'EASE_IN_OUT')
        sgn = 1 if i % 2 else -1
        for o in (h, r_):                  # turn round at each end so the horse always runs head first
            for k in range(4):
                d = sgn if k % 2 == 0 else -sgn   # direction of travel from key k to key k+1
                yaw = FACE_N + (math.pi / 2 if d > 0 else -math.pi / 2)
                if k: key(o, max(1, T(k / 4) - 4), rotation_euler=Vector((0, 0, o.rotation_euler.z)))
                key(o, T(k / 4) + (4 if k else 0), rotation_euler=Vector((0, 0, yaw)))
    for i in range(14):    # Puru's camp fires along the near bank
        x = -15 + i * 2.3; torch((x, -8.2, ground_z(x, -8.2) + 0.35), 18)
    move([(0, (-16, -2.2, 1.6), (-12, 6.5, 0.45), 1.4), (1, (12, -2.2, 1.6), (16, 6.5, 0.45), 1.4)])
    TRACKS = {'torches': gz(0, 6.6, 1.0)}
elif SHOT == 'storm':       # storm night, high wide; Greeks cross upstream on rafts at the bend
    light('storm'); base_armies(); lightning([0.12, 0.43, 0.47, 0.78])
    rafts = []
    for i in range(6):
        x = 29 + i * 1.5; yc = river_y(x); y0 = yc + 1.7 - (i % 2) * 0.4; y1 = yc - 1.7 + (i % 3) * 0.3
        rf = cube((x, y0, -0.16), (0.55, 0.38, 0.04), WOOD); rafts.append(rf)
        for k in range(6):
            m_ = inst(random.choice(GRK), (0, 0, 0), FACE_S, S, 'crosser'); m_.parent = rf
            m_.location = ((k % 3 - 1) * 0.3 / 0.55, (k // 3 - 0.5) * 0.35 / 0.38, 0.04 / 0.04)
            m_.scale = (S / 0.55, S / 0.38, S / 0.04)
        key(rf, 1, location=Vector((x, y0, -0.16))); key(rf, NF, location=Vector((x, y1, -0.16))); linear(rf)
    move([(0, (22, -16, 7.5), (31, 2, 0), 2.2), (1, (27.5, -10.5, 3.6), (33, 0.5, 0), 1.8)])
    TRACKS = {'crossing': (32.8, river_y(32.8), 0.5)}
elif SHOT == 'son':         # tracking beside chariots stuck in the mud; Puru's son
    light('day'); base_armies(elephants=False)
    MUD = mat('mud', (0.17, 0.11, 0.06), 0.25, bump=0.5, bscale=30)
    bpy.ops.mesh.primitive_grid_add(x_subdivisions=80, y_subdivisions=30, size=1, location=(0, 0, 0)); md = bpy.context.object
    for v in md.data.vertices:
        v.co.x = 26 + v.co.x * 16; v.co.y = -11.5 + v.co.y * 5; v.co.z = ground_z(v.co.x, v.co.y) + 0.012
    smooth(md); md.data.materials.append(MUD)
    chs = []
    for i in range(5):
        x = 20 + i * 2.8; ch = chariot(x, -12 + (i % 2) * 1.2, FACE_N + math.pi, 0.0, f'chariot{i}'); chs.append(ch)
        z0 = ch.location.z; key(ch, 1, location=Vector((x, ch.location.y, z0))); key(ch, NF, location=Vector((x, ch.location.y, z0 - 0.14))); ease(ch)
        ch.rotation_euler.y = 0.05 * (1 if i % 2 else -1)
        for dx in (-0.22, 0.22):
            inst(ANI['horse'], gz(x + dx * 1.3, ch.location.y + 1.65), FACE_N + math.pi, S * 0.9, 'ch_horse')
        inst(SOLD['ind_sword' if i == 2 else 'ind_spear_red'], (x, ch.location.y, z0 + 0.5 * S * 1.7 + 0.02), FACE_N + math.pi, S, 'charioteer' if i != 2 else 'prince')
    move([(0, (17.5, -17.6, 1.25), (20.5, -11.6, 0.5), 1.2), (1, (30.5, -17.6, 1.25), (32.0, -11.6, 0.45), 1.2)])
    TRACKS = {'prince': (25.6, -12.0, ground_z(25.6, -12) + 1.2), 'mud': gz(22.0, -14.0, 0.05)}
elif SHOT == 'battle':      # elephants charge the sarissa wall; low hero shot rising to aerial
    light('golden'); base_armies(greek=False, elephants=False)
    eles = []
    for i in range(9):
        x = 22 + i * 2.2; e = inst(ANI['war_elephant'], gz(x, -20), FACE_S, S, 'charge'); eles.append(e)
        key(e, 1, location=Vector((x, -20, ground_z(x, -20)))); key(e, NF, location=Vector((x, -14.5, ground_z(x, -14.5)))); ease(e, 'EASE_IN')
    army(GRK, 21, 41, -11.5, -6.5, 0.42, 0.42, FACE_S + math.pi, 'phalanx')
    puru_on_elephant(31.0, -22.5)
    move([(0, (43.5, -17.5, 0.45), (33, -19.5, 0.7), 1.0), (0.5, (43.0, -19.0, 1.6), (32, -15.5, 0.5), 1.4), (1, (40, -34, 14), (31, -13, 0), 2.6)])
    TRACKS = {'elephants': lambda f: tuple(eles[4].matrix_world.translation + Vector((0, 0, 1.4))), 'phalanx': gz(31, -9, 0.9)}
elif SHOT in ('king', 'return'):   # wounded Puru before Alexander; then an orbit as the kingdom is returned
    light('golden' if SHOT == 'king' else 'day')
    army(GRK, 26, 36, -6, -3.5, 0.42, 0.42, FACE_S + math.pi, 'guard'); army(IND, 26, 36, -18, -15.5, 0.46, 0.46, FACE_S, 'captives')
    px, py, ax, ay = 31.0, -11.6, 31.0, -10.4
    inst(SOLD['puru'], gz(px, py), FACE_S, S * 1.05, 'puru_king'); inst(SOLD['alexander'], gz(ax, ay), FACE_N, S * 1.03, 'alexander_king')
    inst(ANI['horse'], gz(32.1, -10.0), 0.4, S, 'bucephalus')
    if SHOT == 'king':
        move([(0, (32.6, -14.6, 0.9), (31, -11, 0.6), 1.2), (1, (31.7, -12.7, 0.62), (31, -11.0, 0.58), 0.9)], lens=40)
        TRACKS = {'puru': gz(px, py, 0.82), 'alexander': gz(ax, ay, 0.84)}
    else:
        RING = mat('ring', (1.0, 0.75, 0.3), 0.3, emit=12.0)
        bpy.ops.mesh.primitive_torus_add(major_radius=1.0, minor_radius=0.03, location=gz(31, -11, 0.03)); rg = bpy.context.object; rg.data.materials.append(RING)
        key(rg, 1, scale=Vector((0.3, 0.3, 1))); key(rg, NF, scale=Vector((9, 9, 1))); ease(rg, 'EASE_OUT')
        R = 2.3; ks = []
        for k in range(6):
            u = k / 5; a = math.radians(200 + 140 * u)
            ks.append((u, (31 + R * math.cos(a), -11 + R * math.sin(a), 0.85 + 0.5 * u), (31, -11, 0.5), 1.4))
        move(ks, lens=32)
        TRACKS = {'puru': gz(px, py, 0.82), 'kingdom': gz(31, -11, 0.05)}
elif SHOT == 'murder':      # dark interior, single lamp, Eudemus in shadow
    light('interior')
    FL = mat('floor', (0.25, 0.16, 0.09), 0.7, bump=0.3, bscale=20); WL = mat('wall', (0.36, 0.27, 0.19), 0.9, bump=0.12, bscale=6)
    cube((0, -80, -0.02), (3, 3, 0.02), FL); cube((0, -78.2, 1.2), (3, 0.05, 1.2), WL); cube((-2.2, -80, 1.2), (0.05, 3, 1.2), WL); cube((2.2, -80, 1.2), (0.05, 3, 1.2), WL)
    cube((0.6, -79.2, 0.25), (0.5, 0.3, 0.25), WOOD)
    torch((0.6, -79.2, 0.62), 35)
    inst(SOLD['greek_red'], (-0.6, -79.6, 0), FACE_N + math.radians(20), S, 'eudemus')
    inst(SOLD['puru'], (0.9, -79.0, 0), FACE_N + math.radians(-160), S, 'puru_room')
    move([(0, (-0.2, -82.6, 0.75), (-0.4, -79.5, 0.55), 1.0), (1, (-0.5, -80.9, 0.62), (-0.6, -79.6, 0.6), 0.8)], lens=35)
    TRACKS = {'eudemus': (-0.6, -79.6, 0.8)}
elif SHOT == 'legacy':      # pull-out from Puru's statue to the whole valley at sunset
    light('sunset'); sun.rotation_euler = (math.radians(78), 0, math.radians(-20)); base_armies(greek=False, tents_=False, elephants=True)
    STATUE = mat('statue', (0.62, 0.42, 0.22), 0.38, 0.85, bump=0.15, bscale=60)
    bpy.ops.import_scene.gltf(filepath=os.path.join(ASSETS, 'soldiers_glb', 'puru.glb'))
    st = [o for o in bpy.context.selected_objects if o.type == 'MESH']
    for o in st:
        o.data.materials.clear(); o.data.materials.append(STATUE)
    stat = st[0]; stat.parent = None; stat.scale = (S * 2.2,) * 3
    zb = ground_z(0, -37) + 0.55; stat.location = (0, -37, zb); stat.rotation_euler.z = FACE_N
    cube((0, -37, zb - 0.28), (0.55, 0.55, 0.28), STONE); cube((0, -37, zb - 0.04), (0.58, 0.58, 0.03), GOLD); cube((0, -37, zb - 0.52), (0.62, 0.62, 0.04), GOLD)
    move([(0, (0.35, -39.2, 1.9), (0, -37, 1.75), 1.0), (0.4, (0.8, -41.5, 2.6), (0, -37, 1.4), 1.6), (1, (-6, -62, 22), (0, -18, 0), 3.0)], lens=35)
    TRACKS = {'statue': (0, -37, zb + 1.6)}
else:
    raise SystemExit('unknown shot ' + SHOT)

# ---------------------------------------------------------------- render settings
sc.render.engine = 'CYCLES'; dev = os.environ.get('DEVICE', 'GPU')
if dev == 'GPU':
    prefs = bpy.context.preferences.addons['cycles'].preferences
    for kind in ('OPTIX', 'CUDA'):
        try: prefs.compute_device_type = kind; break
        except TypeError: continue
    prefs.get_devices()
    gpus = [d for d in prefs.devices if d.type in ('OPTIX', 'CUDA')]
    want = os.environ.get('GPU_INDEX')
    for i, d in enumerate([d for d in prefs.devices if d.type == prefs.compute_device_type]):
        d.use = want is None or str(i) == want
    sc.cycles.device = 'GPU' if gpus else 'CPU'
else:
    sc.cycles.device = 'CPU'
sc.cycles.samples = int(os.environ.get('SPP', 48)); sc.cycles.use_denoising = True
sc.cycles.denoiser = 'OPENIMAGEDENOISE'
if sc.cycles.device == 'GPU' and prefs.compute_device_type == 'OPTIX':
    try: sc.cycles.denoiser = 'OPTIX'
    except TypeError: pass
try: sc.cycles.denoising_use_gpu = sc.cycles.device == 'GPU'
except AttributeError: pass
sc.cycles.max_bounces = 6; sc.cycles.caustics_reflective = sc.cycles.caustics_refractive = False
sc.render.use_persistent_data = True
sc.render.resolution_x, sc.render.resolution_y = 1080, 1920; sc.render.resolution_percentage = int(os.environ.get('PCT', 100))
sc.view_settings.view_transform = 'AgX'; sc.view_settings.look = 'AgX - Medium High Contrast'
sc.view_settings.exposure = {'night': 1.1, 'storm': 1.0, 'interior': 1.2}.get(PRESET[0], 0.0)
sc.render.use_motion_blur = True; sc.render.motion_blur_shutter = 0.4
sc.render.image_settings.file_format = 'JPEG'; sc.render.image_settings.quality = 93
sc.render.filepath = SD + '/'; sc.frame_step = int(os.environ.get('STEP', 1)); sc.render.use_overwrite = False
if os.environ.get('SAVE'): bpy.ops.wm.save_as_mainfile(filepath=os.path.join(OUT, f'{SHOT}.blend'))

if os.environ.get('TRACK'):
    from bpy_extras.object_utils import world_to_camera_view
    out = {}
    for f in range(1, NF + 1):
        sc.frame_set(f); fr = {}
        for k, p in TRACKS.items():
            pt = Vector(p(f) if callable(p) else p); v = world_to_camera_view(sc, cam, pt)
            vis = 1 if (0 <= v.x <= 1 and 0 <= v.y <= 1 and v.z > 0) else 0
            fr[k] = [round(v.x, 4), round(1 - v.y, 4), vis]
        out[f] = fr
    json.dump(out, open(os.path.join(OUT, f'tracks_{SHOT}.json'), 'w')); print('TRACKS_DONE', SHOT, flush=True); os._exit(0)
if os.environ.get('STILL'):
    sc.frame_set(int(os.environ['STILL'])); sc.render.filepath = os.path.join(SD, f'still_{os.environ["STILL"]}.jpg'); bpy.ops.render.render(write_still=True)
else:
    bpy.ops.render.render(animation=True)
print('SHOT_DONE', SHOT, flush=True); os._exit(0)
