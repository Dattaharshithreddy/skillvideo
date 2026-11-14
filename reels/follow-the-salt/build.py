"""'Follow the salt' — hypertension journey reel. Blender scene (3D only; motion graphics are added in Remotion)."""
import bpy, bmesh, json, math, random, subprocess, sys, os
from mathutils import Vector, Matrix
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import anat
os.chdir(HERE)
random.seed(7)
FPS = 30
plan = json.load(open('brief/plan.json'))
durs = []
for l in plan['lines']:
    d = float(subprocess.run(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0', l['audio']],
                             capture_output=True, text=True).stdout)
    durs.append(d + plan['gap'])
starts, t = [], 0.0
for d in durs: starts.append(t); t += d
SH = [(round(s * FPS) + 1, round((s + d) * FPS)) for s, d in zip(starts, durs)]
END = SH[-1][1]
json.dump({'shots': SH, 'starts': starts, 'durs': durs, 'fps': FPS, 'end': END}, open('brief/shots.json', 'w'))
S = lambda i: SH[i - 1]
ALLFR = list(range(1, END + 1))

bpy.ops.wm.read_factory_settings(use_empty=True)
sc = bpy.context.scene
sc.frame_start, sc.frame_end, sc.render.fps = 1, END, FPS
# ---------------- helpers ----------------
def mat(name, color, rough=0.5, metal=0.0, emit=None, estr=0.0, sss=0.0, trans=0.0):
    m = bpy.data.materials.new(name); m.use_nodes = True
    b = m.node_tree.nodes['Principled BSDF']
    b.inputs['Base Color'].default_value = (*color, 1)
    b.inputs['Roughness'].default_value = rough
    b.inputs['Metallic'].default_value = metal
    if sss: b.inputs['Subsurface Weight'].default_value = sss; b.inputs['Subsurface Radius'].default_value = (0.05, 0.01, 0.01)
    if trans: b.inputs['Transmission Weight'].default_value = trans
    b.inputs['Emission Color'].default_value = (*(emit or color), 1)
    b.inputs['Emission Strength'].default_value = estr
    return m

def bsdf(m): return m.node_tree.nodes['Principled BSDF']

def obj_setup(o, name, m, smooth=True):
    o.name = name
    if m: o.data.materials.append(m)
    if smooth and o.type == 'MESH':
        o.data.polygons.foreach_set('use_smooth', [True] * len(o.data.polygons))
    return o

def sphere(name, loc, r, m, scale=(1, 1, 1), seg=48, ring=24):
    bpy.ops.mesh.primitive_uv_sphere_add(segments=seg, ring_count=ring, radius=r, location=loc)
    o = obj_setup(bpy.context.object, name, m); o.scale = scale; return o

def ico(name, loc, r, m, sub=4, scale=(1, 1, 1)):
    bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=sub, radius=r, location=loc)
    o = obj_setup(bpy.context.object, name, m); o.scale = scale; return o

def box(name, loc, dims, m, bevel=0.003, seg=3):
    bpy.ops.mesh.primitive_cube_add(location=loc); o = bpy.context.object
    o.scale = (dims[0] / 2, dims[1] / 2, dims[2] / 2); bpy.ops.object.transform_apply(scale=True)
    obj_setup(o, name, m, smooth=False)
    if bevel:
        b = o.modifiers.new('bev', 'BEVEL'); b.width = bevel; b.segments = seg
        o.data.polygons.foreach_set('use_smooth', [True] * len(o.data.polygons))
    return o

def cyl(name, loc, r, h, m, rot=(0, 0, 0), verts=48, bevel=0.0):
    bpy.ops.mesh.primitive_cylinder_add(vertices=verts, radius=r, depth=h, location=loc, rotation=rot)
    o = obj_setup(bpy.context.object, name, m, smooth=False)
    if bevel:
        b = o.modifiers.new('bev', 'BEVEL'); b.width = bevel; b.segments = 3; b.limit_method = 'ANGLE'
    o.data.polygons.foreach_set('use_smooth', [True] * len(o.data.polygons))
    try:
        o.data.set_sharp_from_angle(angle=math.radians(40))
    except Exception: pass
    return o

def cone(name, loc, r1, r2, h, m, rot=(0, 0, 0)):
    bpy.ops.mesh.primitive_cone_add(vertices=48, radius1=r1, radius2=r2, depth=h, location=loc, rotation=rot)
    return obj_setup(bpy.context.object, name, m)

def tube(name, pts, radius, m):
    cu = bpy.data.curves.new(name, 'CURVE'); cu.dimensions = '3D'; cu.bevel_depth = radius
    cu.bevel_resolution = 6; cu.resolution_u = 24; cu.use_fill_caps = True
    sp = cu.splines.new('BEZIER'); sp.bezier_points.add(len(pts) - 1)
    for p, c in zip(sp.bezier_points, pts):
        p.co = c; p.handle_left_type = p.handle_right_type = 'AUTO'
    o = bpy.data.objects.new(name, cu); sc.collection.objects.link(o); o.data.materials.append(m); return o

def text(name, s, loc, size, m, rot=(math.radians(90), 0, 0), align='CENTER', extrude=0.002):
    bpy.ops.object.text_add(location=loc, rotation=rot); o = bpy.context.object; o.name = name
    o.data.body = s; o.data.size = size; o.data.extrude = extrude; o.data.align_x = align; o.data.align_y = 'CENTER'
    o.data.materials.append(m); return o

def parent(child, par):
    bpy.context.view_layer.update()
    child.parent = par; child.matrix_parent_inverse = par.matrix_world.inverted()

def kf(o, path, f, v, idx=None):
    if idx is None: setattr(o, path, v); o.keyframe_insert(path, frame=f)
    else: getattr(o, path)[idx] = v; o.keyframe_insert(path, frame=f, index=idx)

def fcurves(idb):
    ad = idb.animation_data
    if not ad or not ad.action: return []
    act = ad.action; out = []
    for layer in getattr(act, 'layers', []):
        for strip in layer.strips:
            for cb in strip.channelbags: out += list(cb.fcurves)
    if not out and hasattr(act, 'fcurves'): out = list(act.fcurves)
    return out

def interp(idb, path, mode, frames=None):
    for fc in fcurves(idb):
        if fc.data_path == path:
            for kp in fc.keyframe_points:
                if frames is None or int(round(kp.co[0])) in frames: kp.interpolation = mode

def show(o, ranges, s=1.0):
    """visibility by scale (constant keys)"""
    base = tuple(o.scale)
    o.scale = (0, 0, 0); o.keyframe_insert('scale', frame=1)
    for a, b in ranges:
        o.scale = tuple(x * s for x in base); o.keyframe_insert('scale', frame=a)
        o.scale = (0, 0, 0); o.keyframe_insert('scale', frame=b)
    interp(o, 'scale', 'CONSTANT')

def pop(o, f, dur=8):
    base = tuple(o.scale)
    o.scale = (0, 0, 0); o.keyframe_insert('scale', frame=1); o.keyframe_insert('scale', frame=f)
    o.scale = tuple(x * 1.12 for x in base); o.keyframe_insert('scale', frame=f + dur)
    o.scale = base; o.keyframe_insert('scale', frame=f + dur + 5)

def emit_keys(m, pairs, color=None):
    inp = bsdf(m).inputs['Emission Strength']
    for f, v in pairs:
        inp.default_value = v; inp.keyframe_insert('default_value', frame=f)

def frac(i, x):
    a, b = S(i); return int(a + (b - a) * x)


# ================= materials =================
M = dict(
    wood=mat('wood_floor', (0.32, 0.2, 0.12), 0.45), wall=mat('wall', (0.42, 0.36, 0.3), 0.8),
    table=mat('table', (0.38, 0.22, 0.12), 0.35), cloth=mat('cloth', (0.75, 0.12, 0.1), 0.7),
    skin=mat('skin', (0.62, 0.45, 0.35), 0.5, sss=0.15), kurta=mat('kurta', (0.92, 0.9, 0.84), 0.75),
    pant=mat('pant', (0.35, 0.33, 0.3), 0.8), hair=mat('hair', (0.75, 0.75, 0.75), 0.6),
    plate=mat('plate', (0.93, 0.93, 0.95), 0.15, 0.0), steel=mat('steel', (0.8, 0.8, 0.82), 0.18, 1.0),
    glassj=mat('jar_glass', (0.95, 0.95, 0.95), 0.03, trans=1.0), pickle=mat('pickle', (0.6, 0.12, 0.03), 0.35),
    papad=mat('papad', (0.92, 0.8, 0.45), 0.55), rice=mat('rice', (0.95, 0.94, 0.9), 0.6),
    salt=mat('salt', (0.97, 0.97, 0.97), 0.25, trans=0.3), monitor=mat('monitor', (0.9, 0.91, 0.93), 0.3),
    screen=mat('screen', (0.01, 0.015, 0.02), 0.15), dark=mat('dark', (0.03, 0.03, 0.035), 0.4),
    apple=mat('apple', (0.6, 0.03, 0.03), 0.3), banana=mat('banana', (0.95, 0.8, 0.15), 0.5), orange=mat('orange', (0.9, 0.38, 0.03), 0.45),
    leaf=mat('leaf', (0.1, 0.4, 0.06), 0.5), bowl=mat('bowl', (0.45, 0.3, 0.18), 0.4),
    pillA=mat('pill_blue', (0.1, 0.3, 0.8), 0.25), pillB=mat('pill_white', (0.92, 0.92, 0.94), 0.3),
    lcdr=mat('lcd_red', (1, 0.1, 0.05), 0.5, emit=(1, 0.12, 0.05), estr=6), lcdg=mat('lcd_green', (0.1, 1, 0.3), 0.5, emit=(0.15, 1, 0.35), estr=5),
    # inside world
    ground=mat('ground', (0.01, 0.012, 0.02), 0.25),
    tube=mat('tube', (1.0, 0.42, 0.42), 0.12, trans=0.85, emit=(1.0, 0.15, 0.1), estr=0.15),
    rbc=mat('rbc', (0.6, 0.02, 0.03), 0.35, sss=0.3), water=mat('water', (0.45, 0.75, 1.0), 0.03, trans=1.0, emit=(0.3, 0.6, 1), estr=0.4),
    crystal=mat('crystal', (1, 1, 1), 0.15, trans=0.5, emit=(1, 1, 1), estr=0.6),
    plaque=mat('plaque', (0.85, 0.6, 0.12), 0.55, sss=0.2),
    ped=mat('pedestal', (0.04, 0.05, 0.08), 0.2, 0.6), ring=mat('ring', (0.3, 0.6, 1), 0.3, emit=(0.25, 0.55, 1.0), estr=6),
    burst=mat('burst', (1, 0.1, 0.05), 0.4, emit=(1, 0.08, 0.03), estr=0.0),
)
# grid on the inside-world ground
g = M['ground'].node_tree; gb = bsdf(M['ground'])
tc = g.nodes.new('ShaderNodeTexCoord'); br_ = g.nodes.new('ShaderNodeTexBrick')
br_.inputs['Scale'].default_value = 0.5; br_.inputs['Mortar Size'].default_value = 0.012
br_.inputs['Color1'].default_value = (0, 0, 0, 1); br_.inputs['Color2'].default_value = (0, 0, 0, 1); br_.inputs['Mortar'].default_value = (0.15, 0.4, 1, 1)
br_.offset = 0.0; br_.squash = 1.0
g.links.new(tc.outputs['Object'], br_.inputs['Vector']); g.links.new(br_.outputs['Color'], gb.inputs['Emission Color'])
gb.inputs['Emission Strength'].default_value = 0.35

# ================= world / lights =================
w = bpy.data.worlds.new('w'); sc.world = w; w.use_nodes = True
w.node_tree.nodes['Background'].inputs['Color'].default_value = (0.006, 0.008, 0.016, 1)
LIGHTS = {'out': [], 'in': []}
def area(name, loc, target, e, size, col, grp):
    bpy.ops.object.light_add(type='AREA', location=loc); l = bpy.context.object; l.name = name
    l.data.energy = e; l.data.size = size; l.data.color = col
    l.visible_camera = False; l.visible_glossy = False
    l.rotation_euler = (Vector(target) - Vector(loc)).to_track_quat('-Z', 'Y').to_euler(); LIGHTS[grp].append(l); return l

# ================= OUTSIDE: dining room =================
bpy.ops.mesh.primitive_plane_add(size=12, location=(-1, 1, 0)); obj_setup(bpy.context.object, 'room_floor', M['wood'])
box('room_wall', (-1, 1.6, 1.6), (12, 0.1, 3.2), M['wall'], bevel=0)
TX, TY = 0.15, 0.2
box('table_top', (TX, TY, 0.75), (1.2, 0.75, 0.05), M['table'], bevel=0.01)
for sx in (-1, 1):
    for sy in (-1, 1):
        box(f'table_leg{sx}{sy}', (TX + sx * 0.54, TY + sy * 0.31, 0.37), (0.05, 0.05, 0.74), M['table'], bevel=0.005)
box('table_runner', (TX, TY, 0.778), (1.25, 0.3, 0.006), M['cloth'], bevel=0.002)
plate = cyl('plate', (TX - 0.05, TY - 0.15, 0.785), 0.14, 0.015, M['plate'], bevel=0.004)
rice = sphere('rice', (TX - 0.07, TY - 0.15, 0.79), 0.07, M['rice'], scale=(1, 1, 0.35))
pick = cyl('pickle_on_plate', (TX + 0.03, TY - 0.13, 0.796), 0.03, 0.012, M['pickle'])
jar = cyl('pickle_jar', (TX + 0.28, TY + 0.0, 0.85), 0.055, 0.13, M['glassj'], bevel=0.008)
jarc = cyl('pickle_inside', (TX + 0.28, TY + 0.0, 0.83), 0.05, 0.1, M['pickle'])
jarl = cyl('jar_lid', (TX + 0.28, TY + 0.0, 0.92), 0.056, 0.02, M['cloth'], bevel=0.004)
papads = [cyl(f'papad{i}', (TX - 0.32, TY - 0.05 + i * 0.005, 0.79 + i * 0.006), 0.11, 0.004, M['papad']) for i in range(4)]
shaker = cyl('shaker', (TX + 0.12, TY + 0.02, 0.82), 0.025, 0.08, M['glassj'], bevel=0.004)
shs = cyl('shaker_salt', (TX + 0.12, TY + 0.02, 0.81), 0.021, 0.055, M['salt'])
shc = cyl('shaker_cap', (TX + 0.12, TY + 0.02, 0.868), 0.026, 0.018, M['steel'], bevel=0.004)
salty = [rice, pick, jar, jarc, jarl, shaker, shs, shc] + papads
# healthy items (appear on line 10)
fb = sphere('fruit_bowl', (TX - 0.3, TY + 0.05, 0.8), 0.13, M['bowl'], scale=(1, 1, 0.45))
fruits = [fb, sphere('apple', (TX - 0.35, TY + 0.02, 0.86), 0.04, M['apple']), sphere('orange', (TX - 0.26, TY + 0.08, 0.86), 0.042, M['orange']),
          sphere('banana', (TX - 0.28, TY - 0.02, 0.855), 0.025, M['banana'], scale=(3.2, 1, 1))]
sal = sphere('salad', (TX - 0.05, TY - 0.15, 0.79), 0.07, M['leaf'], scale=(1, 1, 0.35))
fruits.append(sal)
# BP monitor (lines 9-13)
mon = box('bp_monitor', (TX + 0.36, TY + 0.05, 0.84), (0.13, 0.06, 0.16), M['monitor'], bevel=0.015, seg=4)
mon.rotation_euler = (math.radians(-10), 0, math.radians(-12))
scr = box('bp_screen', (TX + 0.36, TY + 0.018, 0.865), (0.1, 0.003, 0.08), M['screen'], bevel=0.003); parent(scr, mon)
def lcd(name, s_, z, m):
    o = text(name, s_, (TX + 0.36, TY + 0.0165, z), 0.03, m, extrude=0.0004); parent(o, mon); return o
r1 = [lcd('sys_hi', '150', 0.882, M['lcdr']), lcd('dia_hi', '95', 0.848, M['lcdr'])]
g1 = [lcd('sys_ok', '120', 0.882, M['lcdg']), lcd('dia_ok', '80', 0.848, M['lcdg'])]
pills = []
for i in range(4):
    p_ = cyl(f'tablet{i}', (TX - 0.12 + i * 0.03, TY - 0.3, 0.783), 0.009, 0.006, M['pillB'] if i % 2 else M['pillA'], bevel=0.002)
    pills.append(p_)

# Raju garu (stylised person, 1.65 m)
# Raju garu: realistic MPFB2 (MakeHuman, CC0) character generated by raju_make.py
RAJU_BLEND = os.environ.get('RAJU_BLEND', '/opt/reel/raju.blend')
with bpy.data.libraries.load(RAJU_BLEND, link=False) as (src, dst):
    dst.objects = [n for n in src.objects]
for o in dst.objects:
    if o is not None and o.type in ('MESH', 'ARMATURE'): sc.collection.objects.link(o)
raju = bpy.data.objects['raju_rig']
raju.location = (-0.55, 0.15, 0.0)
import mathutils
REST = {}
for side in ('L', 'R'):
    for bn in ('upperarm01.', 'upperleg01.', 'lowerleg01.'):
        pb = raju.pose.bones.get(bn + side)
        if pb:
            pb.rotation_mode = 'QUATERNION'; REST[bn + side] = pb.rotation_quaternion.copy()
def bone_rot(bn, axis_angles):
    """rotate a pose bone in ARMATURE space (on top of its current pose)"""
    pb = raju.pose.bones.get(bn)
    if not pb: return
    Rb = pb.bone.matrix_local.to_3x3().to_quaternion()
    q = mathutils.Quaternion()
    for ax, ang in axis_angles: q = mathutils.Quaternion(ax, math.radians(ang)) @ q
    pb.rotation_quaternion = (Rb.inverted() @ q @ Rb) @ REST[bn]
legs, arms = ['upperleg01.L', 'upperleg01.R'], ['upperarm01.L', 'upperarm01.R']
area('out_key', (1.5, -2.5, 2.6), (0, 0.2, 0.9), 140, 2.0, (1.0, 0.88, 0.72), 'out')
area('out_rim', (-2.5, 1.2, 2.2), (-0.5, 0.2, 1.2), 120, 1.2, (0.6, 0.75, 1.0), 'out')
area('out_fill', (-1.5, -3.5, 1.5), (0, 0, 1), 25, 3.0, (1, 0.95, 0.9), 'out')
area('out_top', (0.2, 0.2, 2.8), (0.2, 0.2, 0.8), 45, 1.2, (1, 0.95, 0.85), 'out')

# ================= INSIDE: X-ray view of Raju garu's own body =================
# Real organs (Z-Anatomy / BodyParts3D, life-size, native body coordinates) placed inside Raju; his skin and clothes
# fade to a glowing see-through shell while the camera pushes in (end of line 1) and come back when it pulls out (line 8).
from mathutils.bvhtree import BVHTree
bpy.context.view_layer.update()
RL = raju.matrix_world.translation.copy()
eyeR = raju.matrix_world @ raju.data.bones['eye.R'].head_local; eyeL = raju.matrix_world @ raju.data.bones['eye.L'].head_local
EYE_R = (eyeR + eyeL) / 2
ANAT_EYE = Vector((0.0, -0.0645, 1.5907))
body = bpy.data.objects['raju_body']
dg = bpy.context.evaluated_depsgraph_get(); be = body.evaluated_get(dg)
bm_ = bmesh.new(); bm_.from_mesh(be.to_mesh()); bm_.transform(body.matrix_world); BVH = BVHTree.FromBMesh(bm_)
def torso_mid_y(z):
    ys = [v.co.y for v in bm_.verts if abs(v.co.z - z) < 0.015 and abs(v.co.x - RL.x) < 0.12]
    return (min(ys) + max(ys)) / 2 if ys else RL.y
def inside_body(p):
    loc, nrm, idx, d = BVH.find_nearest(p)
    return loc is not None and (p - loc).dot(nrm) < 0
HEAD_OFF = EYE_R - ANAT_EYE
TORSO_OFF = Vector((RL.x, torso_mid_y(1.29) - 0.012, HEAD_OFF.z))
def off_for(z):
    t = min(1, max(0, (z - 1.36) / 0.16)); return TORSO_OFF.lerp(HEAD_OFF, t)
def place(objs):
    for o in objs:
        c, _ = anat.centre([o]); o.location += off_for(c.z)
    bpy.context.view_layer.update()

heart_root, heart_m = anat.load_native('heart', 'heart')
art_root, art_m = anat.load_native('arteries', 'arteries')
kid_root, kid_m = anat.load_native('kidneys', 'kidneys')
brain_root, brain_m = anat.load_native('brain', 'brain')
eye_root, eye_m = anat.load_native('eyes', 'eye')
brain_m = [o for o in brain_m if anat.centre([o])[0].z > 1.47]
for o in list(brain_root.children):
    if o not in brain_m: bpy.data.objects.remove(o, do_unlink=True)
for g in (heart_m, art_m, kid_m, brain_m, eye_m): place(g)
HC, _ = anat.centre(heart_m); KC, _ = anat.centre(kid_m); BC, BD = anat.centre(brain_m); EC, _ = anat.centre(eye_m)
print('XRAY fit: heart', HC, inside_body(HC), 'kidneys', KC, inside_body(KC), 'brain', BC, inside_body(BC), 'eyes', EC)
def named(sub):
    for o in art_m:
        if sub in o.name.lower(): return anat.centre([o])[0]
AO_T = named('thoracic aorta') or HC + Vector((0.01, 0.05, -0.05))
AO_A = named('abdominal aorta') or KC + Vector((0, 0.02, 0.05))
heart = bpy.data.objects.new('heart_pivot', None); sc.collection.objects.link(heart); heart.location = HC
for o in heart_m: parent(o, heart)
hroot = heart
# all organ meshes start hidden; they are revealed with the X-ray
ORG = heart_m + art_m + kid_m + brain_m + eye_m

# ---- the X-ray shell on Raju (skin, hair, clothes) ----
X_ON0, X_ON1 = frac(1, 0.70), S(1)[1] + 6
X_OFF0, X_OFF1 = S(8)[0], frac(8, 0.22)
def xray_keys(sock):
    for f, v in ((1, 0), (X_ON0, 0), (X_ON1, 1), (X_OFF0, 1), (X_OFF1, 0)):
        sock.default_value = v; sock.keyframe_insert('default_value', frame=f)
xmats = set()
for o in [o for o in bpy.data.objects if o.name.startswith('raju_body')]:
    for slot in o.material_slots:
        m = slot.material
        if not m or m.name in xmats or not m.use_nodes: continue
        xmats.add(m.name); nt = m.node_tree
        outn = next((n for n in nt.nodes if n.type == 'OUTPUT_MATERIAL' and n.is_active_output), None) or \
            next((n for n in nt.nodes if n.type == 'OUTPUT_MATERIAL'), None)
        if not outn or not outn.inputs['Surface'].links: continue
        src = outn.inputs['Surface'].links[0].from_socket
        mix = nt.nodes.new('ShaderNodeMixShader'); tr = nt.nodes.new('ShaderNodeBsdfTransparent'); em = nt.nodes.new('ShaderNodeEmission')
        shell = nt.nodes.new('ShaderNodeMixShader'); lw = nt.nodes.new('ShaderNodeLayerWeight'); mr = nt.nodes.new('ShaderNodeMapRange')
        lw.inputs['Blend'].default_value = 0.45
        mr.inputs['From Min'].default_value = 0.0; mr.inputs['From Max'].default_value = 1.0
        mr.inputs['To Min'].default_value = 0.10; mr.inputs['To Max'].default_value = 0.85
        em.inputs['Color'].default_value = (0.25, 0.65, 1.0, 1); em.inputs['Strength'].default_value = 2.5
        nt.links.new(lw.outputs['Facing'], mr.inputs['Value']); nt.links.new(mr.outputs['Result'], shell.inputs['Fac'])
        nt.links.new(tr.outputs[0], shell.inputs[1]); nt.links.new(em.outputs[0], shell.inputs[2])
        nt.links.new(src, mix.inputs[1]); nt.links.new(shell.outputs[0], mix.inputs[2]); nt.links.new(mix.outputs[0], outn.inputs['Surface'])
        xray_keys(mix.inputs['Fac'])
        try: m.surface_render_method = 'DITHERED'
        except Exception: pass
for o in ORG: show(o, [(X_ON0, X_OFF1 + 1)])

# ---- lights: the room dims while we are inside; organ lights come up ----
def light_ramp(l, base, pairs):
    for f, k in pairs:
        l.data.energy = base * k; l.data.keyframe_insert('energy', frame=f)
for i, (p, e) in enumerate([(HC, 10), (KC, 8), (BC, 10)]):
    area(f'in_key{i}', p + Vector((-0.5, -0.9, 0.5)), p, e, 0.6, (1, 0.92, 0.88), 'in')
    area(f'in_rim{i}', p + Vector((0.6, 0.6, 0.3)), p, e * 0.8, 0.5, (0.45, 0.65, 1), 'in')
for l in LIGHTS['out']: light_ramp(l, l.data.energy, [(1, 1), (X_ON0, 1), (X_ON1, 0.03), (X_OFF0, 0.03), (X_OFF1, 1)])
for mname in ('wall', 'wood', 'table', 'cloth'):
    bb = bsdf(M[mname]); base_c = tuple(bb.inputs['Base Color'].default_value)
    for f, c_ in ((1, base_c), (X_ON0, base_c), (X_ON1, (0.004, 0.006, 0.012, 1)), (X_OFF0, (0.004, 0.006, 0.012, 1)), (X_OFF1, base_c)):
        bb.inputs['Base Color'].default_value = c_; bb.inputs['Base Color'].keyframe_insert('default_value', frame=f)
for l in LIGHTS['in']: light_ramp(l, l.data.energy, [(1, 0), (X_ON0, 0), (X_ON1, 1), (X_OFF0, 1), (X_OFF1, 0)])

# ---- organ glow (alive) ----
for m in {s.material for o in ORG for s in o.material_slots if s.material}:
    b = bsdf(m); b.inputs['Emission Color'].default_value = (*tuple(b.inputs['Base Color'].default_value)[:3], 1)
    for f, v in ((1, 0.0), (X_ON0, 0.0), (X_ON1, 0.12), (X_OFF0, 0.12), (X_OFF1, 0.0)):
        b.inputs['Emission Strength'].default_value = v; b.inputs['Emission Strength'].keyframe_insert('default_value', frame=f)
WALL = bsdf(art_m[0].material_slots[0].material)

# ---- heartbeat: faster and harder as the pressure rises ----
def beat_hz(f): return 1.8 if S(4)[0] <= f <= S(4)[1] else 1.2
phase = 0.0
for f in ALLFR:
    phase += beat_hz(f) / FPS
    b = max(0.0, math.sin(phase * 2 * math.pi)) ** 3
    s_ = 1 + (0.09 if S(4)[0] <= f <= S(4)[1] else 0.05) * b
    heart.scale = (s_, s_, s_); heart.keyframe_insert('scale', frame=f)
for fc in fcurves(heart):
    for kp in fc.keyframe_points: kp.interpolation = 'LINEAR'
# vessel walls harden on line 6: red -> yellowish, rougher
for f, col, rough in ((1, (0.55, 0.02, 0.015), 0.3), (S(6)[0], (0.55, 0.02, 0.015), 0.3), (S(6)[1], (0.7, 0.45, 0.12), 0.6)):
    WALL.inputs['Base Color'].default_value = (*col, 1); WALL.inputs['Base Color'].keyframe_insert('default_value', frame=f)
    WALL.inputs['Emission Color'].default_value = (*col, 1); WALL.inputs['Emission Color'].keyframe_insert('default_value', frame=f)
    WALL.inputs['Roughness'].default_value = rough; WALL.inputs['Roughness'].keyframe_insert('default_value', frame=f)

# ---- the salt's route through his body: gut -> heart -> aorta -> kidneys, and heart -> carotid -> brain ----
GUT = HC + Vector((0.02, -0.01, -0.13))
ROUTE = [GUT, GUT + Vector((0, 0.01, 0.06)), HC + Vector((0.0, 0.0, -0.03)), HC + Vector((-0.005, 0.01, 0.06)),
         HC + Vector((0.0, 0.03, 0.10)), AO_T, AO_A, KC + Vector((0.045, 0.0, 0.0))]
BROUTE = [HC + Vector((-0.005, 0.01, 0.06)), HC + Vector((0.01, 0.0, 0.12)), HC + Vector((0.025, -0.01, 0.20)),
          EYE_R + Vector((0.03, 0.06, -0.12)), BC + Vector((0.02, 0.0, -0.02))]
def path_curve(name, pts):
    cu = bpy.data.curves.new(name, 'CURVE'); cu.dimensions = '3D'; cu.resolution_u = 24
    sp = cu.splines.new('BEZIER'); sp.bezier_points.add(len(pts) - 1)
    for p, c in zip(sp.bezier_points, pts): p.co = c; p.handle_left_type = p.handle_right_type = 'AUTO'
    o = bpy.data.objects.new(name, cu); sc.collection.objects.link(o); cu.use_path = True; cu.path_duration = 100; return o
route = path_curve('route', ROUTE); broute = path_curve('route_brain', BROUTE)
def flowers(prefix, crv, n, mesh_fn, period, vis, radial=0.006):
    out = []
    for i in range(n):
        e = bpy.data.objects.new(f'{prefix}_e{i}', None); sc.collection.objects.link(e)
        c = e.constraints.new('FOLLOW_PATH'); c.target = crv; c.use_fixed_location = True; c.use_curve_follow = True
        c.forward_axis = 'FORWARD_X'; c.up_axis = 'UP_Z'
        c.offset_factor = 0.0; c.keyframe_insert('offset_factor', frame=1)
        c.offset_factor = 1.0; c.keyframe_insert('offset_factor', frame=1 + period)
        ph = random.uniform(0, period)
        for fc in fcurves(e):
            if 'offset_factor' in fc.data_path:
                for kp in fc.keyframe_points:
                    kp.interpolation = 'LINEAR'; kp.co[0] -= ph; kp.handle_left[0] -= ph; kp.handle_right[0] -= ph
                fc.modifiers.new('CYCLES')
        o = mesh_fn(i); rr = radial * math.sqrt(random.random()); a = random.uniform(0, 6.283)
        o.parent = e; o.location = (0, rr * math.cos(a), rr * math.sin(a))
        o.rotation_euler = (random.uniform(0, 6.3), random.uniform(0, 6.3), random.uniform(0, 6.3))
        a_, b_ = vis(i); show(o, [(a_, b_)])
        out.append(o)
    return out
IN0, IN1 = S(2)[0], S(7)[1]
flowers('salt', route, 70, lambda i: box(f'salt{i}', (0, 0, 0), (0.0045, 0.0045, 0.0045), M['crystal'], bevel=0.0004, seg=1), 200,
        lambda i: (frac(1, 0.85), IN1 + 1))
W0 = frac(2, 0.45)
flowers('water', route, 90, lambda i: sphere(f'water{i}', (0, 0, 0), 0.0035, M['water'], seg=12, ring=6), 210,
        lambda i: (W0 + int(i * (S(3)[1] - W0) / 90), IN1 + 1), radial=0.008)
flowers('bsalt', broute, 30, lambda i: box(f'bsalt{i}', (0, 0, 0), (0.004, 0.004, 0.004), M['crystal'], bevel=0.0004, seg=1), 120,
        lambda i: (S(7)[0], IN1 + 1))
# plaque on the aorta wall (line 6)
for i in range(16):
    t_ = i / 15
    p0 = AO_T.lerp(AO_A, t_) + Vector((random.uniform(-0.008, 0.008), random.uniform(-0.012, -0.004), random.uniform(-0.01, 0.01)))
    p_ = sphere(f'plaque{i}', p0, 0.0028, M['plaque'], scale=(1.3, 0.7, 1.6), seg=16, ring=8)
    base = tuple(p_.scale); p_.scale = (0, 0, 0); p_.keyframe_insert('scale', frame=1); p_.keyframe_insert('scale', frame=S(6)[0] + i * 4)
    p_.scale = base; p_.keyframe_insert('scale', frame=S(6)[0] + 40 + i * 4)
    p_.scale = (0, 0, 0); p_.keyframe_insert('scale', frame=X_OFF1 + 1); interp(p_, 'scale', 'CONSTANT', {X_OFF1 + 1})
# kidneys: working hard on line 5 (glow pulse) + water leaving downwards
k5a, k5b = S(5)
km = bsdf(kid_m[0].material_slots[0].material)
for f in range(k5a, k5b + 1, 6):
    km.inputs['Emission Strength'].default_value = 0.35 + 0.9 * abs(math.sin((f - k5a) / FPS * 3.0))
    km.inputs['Emission Strength'].keyframe_insert('default_value', frame=f)
km.inputs['Emission Strength'].default_value = 0.35; km.inputs['Emission Strength'].keyframe_insert('default_value', frame=k5b + 6)
for i in range(24):
    side = 1 if i % 2 else -1
    d = sphere(f'kdrop{i}', KC + Vector((side * 0.05, 0, 0)), 0.003, M['water'], seg=12, ring=6)
    z0 = KC.z - 0.03
    for f in range(k5a, k5b + 1, 2):
        tt = ((f - k5a) / FPS * 0.8 + i / 24) % 1.0
        d.location = KC + Vector((side * (0.05 - 0.03 * tt), -0.01 * tt, -0.03 - 0.16 * tt)); d.keyframe_insert('location', frame=f)
    show(d, [(k5a, k5b + 1)])
# brain stroke (line 7)
a7, b7 = S(7)
bpt = BC + Vector((-0.05, -0.02, 0.02))
bs = sphere('stroke_burst', bpt, 0.012, M['burst'])
for f, sc_, e in ((1, 0.0, 0), (frac(7, 0.38), 0.0, 0), (frac(7, 0.45), 1.6, 18), (frac(7, 0.6), 1.2, 10), (b7, 1.2, 10), (b7 + 1, 0, 0)):
    bs.scale = (sc_, sc_, sc_); bs.keyframe_insert('scale', frame=f)
    bsdf(M['burst']).inputs['Emission Strength'].default_value = e; bsdf(M['burst']).inputs['Emission Strength'].keyframe_insert('default_value', frame=f)
for i in range(24):
    sp_ = sphere(f'spark{i}', bpt, 0.003, M['burst'], seg=12, ring=6)
    dv = Vector((random.uniform(-1, 0.2), random.uniform(-1, 1), random.uniform(-0.3, 1))).normalized() * random.uniform(0.03, 0.07)
    f0 = frac(7, 0.4)
    sp_.location = bpt; sp_.keyframe_insert('location', frame=f0)
    sp_.location = bpt + dv; sp_.keyframe_insert('location', frame=f0 + 25)
    show(sp_, [(f0, f0 + 30)])
def flush_objs(objs, f_on, f_off):
    for m in {s.material for o in objs for s in o.material_slots if s.material}:
        b = bsdf(m); base_c = tuple(b.inputs['Base Color'].default_value)[:3]
        for f, c_ in ((1, base_c), (f_on - 1, base_c), (f_on, (1.0, 0.08, 0.04)), (f_off + 1, (1.0, 0.08, 0.04)), (f_off + 2, base_c)):
            b.inputs['Emission Color'].default_value = (*c_, 1); b.inputs['Emission Color'].keyframe_insert('default_value', frame=f)
        for f, v in ((f_on, 0.35), (f_on + 12, 1.4), (f_off, 1.4), (f_off + 1, 0.0)):
            b.inputs['Emission Strength'].default_value = v; b.inputs['Emission Strength'].keyframe_insert('default_value', frame=f)
flush_objs(brain_m, frac(7, 0.45), b7)
flush_objs(eye_m, frac(7, 0.82), b7)

# ================= outside animation =================
# salty items until line 10, then healthy items
for o in salty: show(o, [(1, frac(10, 0.12))])
for i, o in enumerate(fruits): pop(o, frac(10, 0.2) + i * 4)
for o in [mon, scr]: show(o, [(S(9)[0], END + 1)])
for o in r1: show(o, [(frac(9, 0.25), S(12)[0])])
for o in g1: show(o, [(frac(12, 0.2), END + 1)])
for i, p_ in enumerate(pills): pop(p_, frac(11, 0.55) + i * 3)
# walking (line 11): Raju walks to the left and back (bone swing in armature space)
a11, b11 = S(11)
x0 = raju.location.x
def keybones(f):
    for bn in legs + arms + ['lowerleg01.L', 'lowerleg01.R']:
        pb = raju.pose.bones.get(bn)
        if pb: pb.keyframe_insert('rotation_quaternion', frame=f)
for bn in REST: raju.pose.bones[bn].rotation_quaternion = REST[bn]
keybones(1); keybones(a11 - 1)
for f in range(a11, b11 + 1, 2):
    tt = (f - a11) / (b11 - a11)
    raju.location.x = x0 - 1.8 * math.sin(min(1, tt / 0.5) * math.pi / 2) if tt < 0.5 else x0 - 1.8 + 1.8 * math.sin((tt - 0.5) / 0.5 * math.pi / 2)
    raju.keyframe_insert('location', frame=f, index=0)
    raju.rotation_euler[2] = math.radians(-90 if tt < 0.5 else 90) * min(1, abs(math.sin(tt * math.pi * 2)) * 3)
    raju.keyframe_insert('rotation_euler', frame=f, index=2)
    ph = (f - a11) / FPS * 2 * math.pi * 0.9
    sw = math.sin(ph) * 24
    bone_rot('upperleg01.L', [((1, 0, 0), sw)]); bone_rot('upperleg01.R', [((1, 0, 0), -sw)])
    for side, sg in (('L', 1), ('R', -1)):
        pb = raju.pose.bones.get('lowerleg01.' + side)
        if pb:
            Rb = pb.bone.matrix_local.to_3x3().to_quaternion(); bend = max(0, -math.sin(ph) * sg) * 30
            pb.rotation_quaternion = (Rb.inverted() @ mathutils.Quaternion((1, 0, 0), math.radians(-bend)) @ Rb) @ REST['lowerleg01.' + side]
    bone_rot('upperarm01.L', [((1, 0, 0), -sw * 0.7)]); bone_rot('upperarm01.R', [((1, 0, 0), sw * 0.7)])
    keybones(f)
for bn in REST: raju.pose.bones[bn].rotation_quaternion = REST[bn]
keybones(b11 + 1)
raju.rotation_euler[2] = 0; raju.keyframe_insert('rotation_euler', frame=b11 + 1, index=2)

# ================= camera =================
cd = bpy.data.cameras.new('cam'); cam = bpy.data.objects.new('cam', cd); sc.collection.objects.link(cam); sc.camera = cam
cd.sensor_width = 24; cd.dof.use_dof = True
tgt = bpy.data.objects.new('cam_target', None); sc.collection.objects.link(tgt)
c = cam.constraints.new('TRACK_TO'); c.target = tgt; c.track_axis = 'TRACK_NEGATIVE_Z'; c.up_axis = 'UP_Y'
cd.dof.focus_object = tgt
P = lambda *a: Vector(a)
KEYS = []  # (frame, cam, target, fstop, lens, cut_before)
def K(f, c_, t_, fs, ln, cut=False): KEYS.append((int(f), c_, t_, fs, ln, cut))
# line 1: dining room -> push into Raju garu's chest (X-ray comes on) ; lines 2-8: one continuous move inside his body, then out
V3 = Vector
K(S(1)[0], P(1.6, -2.6, 1.7), P(-0.1, 0.1, 1.0), 4.0, 32, True)
K(frac(1, 0.45), P(0.9, -1.8, 1.45), RL + V3((0.15, 0, 1.15)), 3.5, 32)
K(frac(1, 0.72), RL + V3((0.35, -1.3, 1.3)), HC + V3((0, 0, -0.05)), 4.0, 35)
K(S(1)[1], HC + V3((0.15, -0.95, 0.0)), HC + V3((0, 0, -0.08)), 5.6, 35)
K(S(2)[1], HC + V3((0.08, -0.78, -0.04)), HC + V3((0, 0, -0.08)), 5.6, 35)
K(frac(3, 0.5), HC + V3((-0.15, -0.66, 0.02)), HC + V3((0, 0, -0.03)), 5.6, 35)
K(S(3)[1], HC + V3((-0.06, -0.56, 0.02)), HC, 5.6, 38)
K(S(4)[0] + 15, HC + V3((0.08, -0.40, 0.03)), HC, 6.3, 40)
K(S(4)[1], HC + V3((0.12, -0.34, 0.04)), HC, 6.3, 42)
K(frac(5, 0.25), KC + V3((0.18, -0.72, 0.08)), KC, 5.6, 35)
K(S(5)[1], KC + V3((0.12, -0.6, 0.05)), KC, 5.6, 36)
K(frac(6, 0.2), AO_A + V3((0.12, -0.35, 0.05)), AO_T.lerp(AO_A, 0.5), 6.3, 40)
K(S(6)[1], AO_A + V3((0.08, -0.28, 0.08)), AO_T.lerp(AO_A, 0.5), 6.3, 42)
K(frac(7, 0.15), BC + V3((0.42, -0.6, 0.0)), BC + V3((0, 0, -0.03)), 5.6, 35)
K(frac(7, 0.62), BC + V3((0.3, -0.52, 0.0)), BC + V3((0, 0, -0.03)), 5.6, 36)
K(S(7)[1], EC + V3((0.12, -0.38, 0.0)), EC, 5.6, 40)
K(frac(8, 0.08), EC + V3((0.15, -0.45, -0.05)), EC + V3((0, 0, -0.1)), 4.5, 38)
K(frac(8, 0.4), RL + V3((0.6, -1.7, 1.4)), RL + V3((0, 0, 1.25)), 3.5, 35)
K(S(8)[1], RL + V3((0.95, -2.1, 1.55)), RL + V3((0, 0, 1.2)), 3.5, 35)
K(S(9)[0], P(TX + 0.45, -0.75, 1.1), P(TX + 0.36, TY + 0.05, 0.86), 2.4, 40, True)
K(S(9)[1], P(TX + 0.44, -0.62, 1.05), P(TX + 0.36, TY + 0.05, 0.86), 2.4, 42)
K(S(10)[0], P(TX + 0.05, -0.75, 1.45), P(TX + 0.05, TY, 0.8), 3.2, 35, True)
K(S(10)[1], P(TX + 0.1, -0.62, 1.35), P(TX + 0.08, TY, 0.8), 3.2, 35)
K(S(11)[0], P(-0.6, -3.2, 1.5), P(-0.8, 0.1, 1.0), 4.0, 30, True)
K(frac(11, 0.5), P(-2.4, -3.2, 1.5), P(-2.5, 0.1, 1.0), 4.0, 30)
K(S(11)[1], P(-0.8, -3.0, 1.5), P(-0.6, 0.1, 1.0), 4.0, 30)
K(S(12)[0], P(TX + 0.46, -0.68, 1.06), P(TX + 0.36, TY + 0.05, 0.86), 2.4, 42, True)
K(S(12)[1], P(TX + 0.45, -0.6, 1.04), P(TX + 0.36, TY + 0.05, 0.86), 2.4, 44)
K(S(13)[0], P(1.3, -3.0, 1.7), P(-0.1, 0.15, 1.0), 4.5, 30, True)
K(S(13)[1], P(1.0, -2.7, 1.65), P(-0.1, 0.15, 1.0), 4.5, 30)
cuts = set(); seg_starts = {KEYS[0][0]} | {k[0] for k in KEYS if k[5]}
for i, (f, c_, t_, fs, ln, cut) in enumerate(KEYS):
    cam.location = c_; cam.keyframe_insert('location', frame=f)
    tgt.location = t_; tgt.keyframe_insert('location', frame=f)
    cd.dof.aperture_fstop = fs; cd.dof.keyframe_insert('aperture_fstop', frame=f)
    cd.lens = ln; cd.keyframe_insert('lens', frame=f)
    if cut and i > 0: cuts.add(KEYS[i - 1][0])
for idb, path in ((cam, 'location'), (tgt, 'location'), (cd, 'dof.aperture_fstop'), (cd, 'lens')):
    for fc in fcurves(idb):
        if fc.data_path == path:
            for kp in fc.keyframe_points:
                f_ = int(round(kp.co[0]))
                kp.handle_left_type = kp.handle_right_type = 'AUTO_CLAMPED'
                if f_ in cuts or f_ in seg_starts: kp.handle_left_type = kp.handle_right_type = 'VECTOR'
                if f_ in cuts: kp.interpolation = 'CONSTANT'
# the shots before a cut must not ease into the next set: hold-end keys are the last key of each segment (handled by CONSTANT)
# line 11 walk: target follows Raju
# ================= render =================
sc.render.engine = 'CYCLES'
try:
    pr = bpy.context.preferences.addons['cycles'].preferences
    for dt in ('OPTIX', 'CUDA'):
        try:
            pr.compute_device_type = dt; pr.get_devices()
            if any(d.type == dt for d in pr.devices):
                for d in pr.devices: d.use = (d.type == dt)
                sc.cycles.device = 'GPU'; break
        except Exception: pass
except Exception: pass
sc.cycles.samples = int(os.environ.get('SAMPLES', '40')); sc.cycles.use_denoising = True
sc.cycles.max_bounces = 8; sc.cycles.diffuse_bounces = 3; sc.cycles.glossy_bounces = 3; sc.cycles.transmission_bounces = 8
sc.cycles.use_adaptive_sampling = True; sc.render.use_persistent_data = True
sc.render.resolution_x, sc.render.resolution_y = 1080, 1920; sc.render.resolution_percentage = 100
sc.render.use_motion_blur = True; sc.render.motion_blur_shutter = 0.35
sc.view_settings.view_transform = 'AgX'; sc.view_settings.look = 'AgX - Medium High Contrast'
sc.render.image_settings.file_format = 'JPEG'; sc.render.image_settings.quality = 92
out = sys.argv[-1] if sys.argv[-1].endswith('.blend') else os.path.join(HERE, 'scene', 'salt.blend')
bpy.ops.wm.save_as_mainfile(filepath=out)
print('built', END, SH)
