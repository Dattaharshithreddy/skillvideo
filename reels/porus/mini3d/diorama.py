# Puru vs Alexander — tilt-shift miniature diorama (thekitiki style): toy-pawn crowds, puffy trees, river, signboards.
# blender -b -P diorama.py -- SHOT [frames]   (renders out/<SHOT>/####.png on GPU)
import bpy, bmesh, math, random, os, sys, glob
from mathutils import Vector, Matrix
argv = sys.argv[sys.argv.index('--') + 1:] if '--' in sys.argv else ['A']
SHOT = argv[0]; NF = int(argv[1]) if len(argv) > 1 else 144
OUT = f'/opt/reel/mini3d/out/{SHOT}'; os.makedirs(OUT, exist_ok=True)
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

# ---------------- toy pawn figurines ----------------
SKIN = mat('skin', (0.55, 0.36, 0.24), 0.6)
def pawn(name, body, head_col=None, hat=None, hat_kind='turban', spear=False, shield=None, cape=None):
    parts = []
    bpy.ops.mesh.primitive_cylinder_add(radius=0.11, depth=0.42, location=(0, 0, 0.21), vertices=16); bd = bpy.context.object; bd.data.materials.append(body); parts.append(bd)
    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.11, location=(0, 0, 0.42), segments=16, ring_count=8); s = bpy.context.object; s.scale.z = 0.5; s.data.materials.append(body); parts.append(s)
    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.075, location=(0, 0, 0.53), segments=16, ring_count=8); h = bpy.context.object; h.data.materials.append(head_col or SKIN); parts.append(h)
    if hat:
        if hat_kind == 'turban': bpy.ops.mesh.primitive_uv_sphere_add(radius=0.082, location=(0, 0, 0.575), segments=16, ring_count=8); t = bpy.context.object; t.scale.z = 0.6
        else:   # greek crested helmet
            bpy.ops.mesh.primitive_uv_sphere_add(radius=0.08, location=(0, 0, 0.565), segments=16, ring_count=8); t = bpy.context.object
            t.data.materials.append(hat); parts.append(t)
            bpy.ops.mesh.primitive_cube_add(location=(0, 0, 0.64)); t = bpy.context.object; t.scale = (0.012, 0.07, 0.04); hat = mat('crest', (0.6, 0.02, 0.03), 0.7)
        t.data.materials.append(hat); parts.append(t)
    if cape:
        bpy.ops.mesh.primitive_cylinder_add(radius=0.115, depth=0.3, location=(0, 0.01, 0.28), vertices=16); c = bpy.context.object; c.scale = (1.02, 1.02, 1); c.data.materials.append(cape); parts.append(c)
        bm_ = bmesh.new(); bm_.from_mesh(c.data)
        bmesh.ops.delete(bm_, geom=[v for v in bm_.verts if v.co.y < -0.02], context='VERTS'); bm_.to_mesh(c.data); bm_.free()
    if spear:
        bpy.ops.mesh.primitive_cylinder_add(radius=0.008, depth=1.1, location=(0.13, -0.02, 0.5), vertices=6); sp = bpy.context.object; sp.data.materials.append(mat('wood', (0.35, 0.22, 0.12), 0.7)); parts.append(sp)
        bpy.ops.mesh.primitive_cone_add(radius1=0.02, depth=0.07, location=(0.13, -0.02, 1.08), vertices=6); parts.append(bpy.context.object); bpy.context.object.data.materials.append(mat('steel', (0.7, 0.7, 0.72), 0.3, 1.0))
    if shield:
        bpy.ops.mesh.primitive_cylinder_add(radius=0.12, depth=0.02, location=(-0.11, -0.06, 0.28), rotation=(math.pi / 2, 0, 0.5), vertices=20); sh = bpy.context.object; sh.data.materials.append(shield); parts.append(sh)
    bpy.ops.object.select_all(action='DESELECT')
    for o in parts: o.select_set(True)
    bpy.context.view_layer.objects.active = parts[0]; bpy.ops.object.join(); p = bpy.context.object; p.name = name; return p
INDIAN = new_coll('INDIAN', hide=True); GREEK = new_coll('GREEK', hide=True)
for i, (bc, tc) in enumerate([((0.92, 0.9, 0.85), (0.9, 0.45, 0.05)), ((0.92, 0.9, 0.85), (0.92, 0.9, 0.85)), ((0.85, 0.55, 0.15), (0.7, 0.08, 0.05)), ((0.92, 0.9, 0.85), (0.7, 0.08, 0.05)), ((0.2, 0.35, 0.15), (0.92, 0.9, 0.85))]):
    link(pawn(f'ind{i}', mat(f'ib{i}', bc, 0.8), hat=mat(f'it{i}', tc, 0.8), spear=(i % 2 == 0), shield=mat('leather', (0.3, 0.17, 0.08), 0.6) if i % 2 else None), INDIAN)
BRONZE = mat('bronze', (0.75, 0.5, 0.22), 0.35, 1.0); RED = mat('greek_red', (0.55, 0.04, 0.04), 0.7)
for i in range(3):
    link(pawn(f'gr{i}', mat(f'gb{i}', [(0.85, 0.8, 0.68), (0.55, 0.04, 0.04), (0.8, 0.75, 0.62)][i], 0.8), hat=BRONZE, hat_kind='helmet', spear=True, shield=BRONZE, cape=RED), GREEK)

# elephants: Model Forge glb if present, else a toy elephant
ELE = new_coll('ELE', hide=True)
glbs = sorted(glob.glob('/opt/reel/mini3d/mf/war_elephant*.glb'))
if glbs:
    bpy.ops.import_scene.gltf(filepath=glbs[0]); imp = [o for o in bpy.context.selected_objects if o.type == 'MESH']
    bpy.ops.object.select_all(action='DESELECT')
    for o in imp: o.select_set(True)
    bpy.context.view_layer.objects.active = imp[0]; bpy.ops.object.join(); e = bpy.context.object
    bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
    dz = min(v.co.z for v in e.data.vertices); h = max(v.co.z for v in e.data.vertices) - dz; s = 1.4 / h
    for v in e.data.vertices: v.co = Vector((v.co.x * s, v.co.y * s, (v.co.z - dz) * s))
    e.name = 'elephant'; link(e, ELE); print('ELEPHANT from Model Forge', glbs[0])
else:
    GREY = mat('ele', (0.32, 0.3, 0.3), 0.8, bump=0.4, bscale=40); CAP = mat('caparison', (0.6, 0.05, 0.05), 0.7); GOLDM = mat('gold', (1, 0.72, 0.3), 0.3, 1.0)
    parts = []
    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.55, location=(0, 0, 0.95)); b_ = bpy.context.object; b_.scale = (0.75, 1.15, 0.8); b_.data.materials.append(GREY); parts.append(b_)
    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.33, location=(0, -0.68, 1.15)); parts.append(bpy.context.object); bpy.context.object.data.materials.append(GREY)
    for sx in (-1, 1):
        for sy in (-0.4, 0.4):
            bpy.ops.mesh.primitive_cylinder_add(radius=0.13, depth=0.65, location=(sx * 0.25, sy, 0.33)); parts.append(bpy.context.object); bpy.context.object.data.materials.append(GREY)
        bpy.ops.mesh.primitive_uv_sphere_add(radius=0.25, location=(sx * 0.3, -0.62, 1.2)); ear = bpy.context.object; ear.scale = (0.15, 0.8, 1); ear.data.materials.append(GREY); parts.append(ear)
        bpy.ops.mesh.primitive_cone_add(radius1=0.03, depth=0.35, location=(sx * 0.12, -0.92, 0.92), rotation=(-1.2, 0, 0)); parts.append(bpy.context.object); bpy.context.object.data.materials.append(mat('ivory', (0.95, 0.92, 0.82), 0.4))
    bpy.ops.curve.primitive_bezier_curve_add(); cu = bpy.context.object; sp_ = cu.data.splines[0]
    sp_.bezier_points[0].co = (0, -0.9, 1.05); sp_.bezier_points[1].co = (0, -1.05, 0.3)
    for p_ in sp_.bezier_points: p_.handle_left_type = p_.handle_right_type = 'AUTO'
    cu.data.bevel_depth = 0.07; cu.data.materials.append(GREY); bpy.ops.object.convert(target='MESH'); parts.append(bpy.context.object)
    bpy.ops.mesh.primitive_cube_add(location=(0, 0.05, 1.42)); cp = bpy.context.object; cp.scale = (0.45, 0.55, 0.06); cp.data.materials.append(CAP); parts.append(cp)
    bpy.ops.mesh.primitive_cube_add(location=(0, 0.05, 1.62)); hw = bpy.context.object; hw.scale = (0.3, 0.35, 0.15); hw.data.materials.append(GOLDM); parts.append(hw)
    bpy.ops.mesh.primitive_cube_add(location=(0, -0.62, 1.3)); hp = bpy.context.object; hp.scale = (0.2, 0.05, 0.2); hp.data.materials.append(GOLDM); parts.append(hp)
    bpy.ops.object.select_all(action='DESELECT')
    for o in parts: o.select_set(True)
    bpy.context.view_layer.objects.active = parts[0]; bpy.ops.object.join(); e = bpy.context.object; e.name = 'elephant'; smooth(e); link(e, ELE)

# ---------------- armies ----------------
def army(coll, x0, x1, y0, y1, step, jitter, face, name, move=None):
    objs = list(coll.objects); out = []
    x = x0
    while x <= x1:
        y = y0
        while y <= y1:
            src = random.choice(objs); o = src.copy(); o.data = src.data; bpy.context.scene.collection.objects.link(o)
            px, py = x + random.uniform(-jitter, jitter), y + random.uniform(-jitter, jitter); o.location = (px, py, ground_z(px, py))
            o.rotation_euler.z = face + random.uniform(-0.15, 0.15); o.name = name; out.append(o); y += step
        x += step
    if move:   # march: keyframe whole block
        e = bpy.data.objects.new(name + '_rig', None); bpy.context.scene.collection.objects.link(e)
        for o in out: o.parent = e
        e.location = (0, 0, 0); e.keyframe_insert('location', frame=1); e.location = Vector(move); e.keyframe_insert('location', frame=NF)
        for fc in e.animation_data.action.fcurves:
            for kp in fc.keyframe_points: kp.interpolation = 'LINEAR'
    return out
# Greeks on the far bank (north, +y), facing the river; Indians on the near bank (south)
army(GREEK, -16, 16, 11, 22, 0.45, 0.06, 0.0, 'greek')
army(INDIAN, -16, 16, -22, -13, 0.5, 0.1, math.pi, 'indian', move=(0, 1.2, 0) if SHOT in ('B',) else None)
army(ELE, -15, 15, -11.2, -10.8, 2.0, 0.15, math.pi, 'eleline')
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
board('326 BC', (-6, -4.2, 2.6), 0.0, w=4.2, size=0.9)
board('HYDASPES RIVER', (8, -5.0, 2.3), 0.0, w=7.5, bg=(0.08, 0.2, 0.55), size=0.7)
board('ALEXANDER', (0, 9.0, 2.6), math.pi, w=5.5, bg=(0.5, 0.05, 0.05), size=0.8)
board('200 WAR ELEPHANTS', (-10, -9.0, 2.4), 0.0, w=9.0, bg=(0.07, 0.07, 0.09), size=0.7)

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
  # A: aerial push-in from high over the Indian army toward the river + Greek camp, crane down slightly
  'A': [((-4, -40, 26), (0, -2, 0)), ((2, -24, 13), (0, 2, 0))],
  # B: low tilt-shift glide along the elephant line, focus on elephants, signboard passes
  'B': [((-20, -17, 3.2), (-12, -11, 0.8)), ((6, -16, 2.6), (8, -11, 0.8))],
}
(c0, t0), (c1, t1) = SHOTS.get(SHOT, SHOTS['A'])
key(cam, 1, c0); key(cam, NF, c1); key(tgt, 1, t0); key(tgt, NF, t1); ease_all(cam); ease_all(tgt)
sc.render.filepath = OUT + '/'
bpy.ops.wm.save_as_mainfile(filepath=f'/opt/reel/mini3d/diorama_{SHOT}.blend')
if os.environ.get('STILL'):
    sc.frame_set(int(os.environ['STILL'])); sc.render.filepath = OUT + f'/still_{os.environ["STILL"]}.jpg'; bpy.ops.render.render(write_still=True)
else:
    bpy.ops.render.render(animation=True)
print('DIORAMA_DONE', SHOT)
