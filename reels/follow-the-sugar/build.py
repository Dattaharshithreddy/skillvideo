"""'Follow the Sugar' - X-ray Raju scene built as a row of stations (one continuous shot each). Both reels (public and
student) are cut from this one render using brief/stations.json. Motion graphics are added in Remotion."""
import bpy, bmesh, json, math, random, sys, os
from mathutils import Vector
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import anat
os.chdir(HERE)
random.seed(11)
FPS = 30
STN = json.load(open('brief/stations.json'))
END = STN['end']
def S(name):
    a = STN['offset'][name]; return a, a + STN['frames'][name] - 1
def fr(name, x):
    a, b = S(name); return int(a + (b - a) * x)
ALLFR = list(range(1, END + 1))
INSIDE = [s for s in STN['order'] if not s.startswith('room')]

bpy.ops.wm.read_factory_settings(use_empty=True)
sc = bpy.context.scene
sc.frame_start, sc.frame_end, sc.render.fps = 1, END, FPS

# ---------------- helpers ----------------
def mat(name, color, rough=0.5, metal=0.0, emit=None, estr=0.0, sss=0.0, trans=0.0):
    m = bpy.data.materials.new(name); m.use_nodes = True
    b = m.node_tree.nodes['Principled BSDF']
    b.inputs['Base Color'].default_value = (*color, 1); b.inputs['Roughness'].default_value = rough
    b.inputs['Metallic'].default_value = metal
    if sss: b.inputs['Subsurface Weight'].default_value = sss; b.inputs['Subsurface Radius'].default_value = (0.05, 0.01, 0.01)
    if trans: b.inputs['Transmission Weight'].default_value = trans
    b.inputs['Emission Color'].default_value = (*(emit or color), 1); b.inputs['Emission Strength'].default_value = estr
    return m
def bsdf(m): return m.node_tree.nodes['Principled BSDF']
def obj_setup(o, name, m, smooth=True):
    o.name = name
    if m: o.data.materials.append(m)
    if smooth and o.type == 'MESH': o.data.polygons.foreach_set('use_smooth', [True] * len(o.data.polygons))
    return o
def sphere(name, loc, r, m, scale=(1, 1, 1), seg=32, ring=16):
    bpy.ops.mesh.primitive_uv_sphere_add(segments=seg, ring_count=ring, radius=r, location=loc)
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
    return o
def text(name, s, loc, size, m, rot=(math.radians(90), 0, 0), extrude=0.002):
    bpy.ops.object.text_add(location=loc, rotation=rot); o = bpy.context.object; o.name = name
    o.data.body = s; o.data.size = size; o.data.extrude = extrude; o.data.align_x = 'CENTER'; o.data.align_y = 'CENTER'
    o.data.materials.append(m); return o
def parent(child, par):
    bpy.context.view_layer.update(); child.parent = par; child.matrix_parent_inverse = par.matrix_world.inverted()
def fcurves(idb):
    ad = idb.animation_data
    if not ad or not ad.action: return []
    act = ad.action; out = []
    for layer in getattr(act, 'layers', []):
        for strip in layer.strips:
            for cb in strip.channelbags: out += list(cb.fcurves)
    if not out and hasattr(act, 'fcurves'): out = list(act.fcurves)
    return out
def interp(idb, path, mode):
    for fc in fcurves(idb):
        if fc.data_path == path:
            for kp in fc.keyframe_points: kp.interpolation = mode
def show(o, ranges):
    base = tuple(o.scale)
    o.scale = (0, 0, 0); o.keyframe_insert('scale', frame=1)
    for a, b in ranges:
        o.scale = base; o.keyframe_insert('scale', frame=a)
        o.scale = (0, 0, 0); o.keyframe_insert('scale', frame=b)
    interp(o, 'scale', 'CONSTANT')
def keys(sock, pairs):
    for f, v in sorted(pairs, key=lambda x: x[0]):
        sock.default_value = v; sock.keyframe_insert('default_value', frame=f)
def ranges_for(names):
    return [(S(n)[0], S(n)[1] + 1) for n in names]

# ================= materials =================
M = dict(
    wood=mat('wood_floor', (0.32, 0.2, 0.12), 0.45), wall=mat('wall', (0.42, 0.36, 0.3), 0.8),
    table=mat('table', (0.38, 0.22, 0.12), 0.35), cloth=mat('cloth', (0.75, 0.12, 0.1), 0.7),
    plate=mat('plate', (0.93, 0.93, 0.95), 0.15), steel=mat('steel', (0.8, 0.8, 0.82), 0.18, 1.0),
    rice=mat('rice', (0.95, 0.94, 0.9), 0.6), dal=mat('dal', (0.95, 0.68, 0.12), 0.4), leaf=mat('leaf', (0.1, 0.4, 0.06), 0.5),
    carrot=mat('carrot', (0.95, 0.4, 0.05), 0.45), monitor=mat('meter', (0.9, 0.91, 0.93), 0.3), screen=mat('screen', (0.01, 0.015, 0.02), 0.15),
    lcdr=mat('lcd_red', (1, 0.1, 0.05), 0.5, emit=(1, 0.12, 0.05), estr=6), lcdg=mat('lcd_green', (0.1, 1, 0.3), 0.5, emit=(0.15, 1, 0.35), estr=5),
    gold=mat('glucose', (1.0, 0.72, 0.12), 0.3, emit=(1.0, 0.7, 0.12), estr=3.5),
    key=mat('insulin', (0.15, 0.85, 1.0), 0.3, emit=(0.2, 0.85, 1.0), estr=5.0),
    fat=mat('visceral_fat', (1.0, 0.55, 0.1), 0.6, emit=(1.0, 0.5, 0.08), estr=0.0),
    burst=mat('burst', (1, 0.1, 0.05), 0.4, emit=(1, 0.08, 0.03), estr=0.0),
)
bsdf(M['fat']).inputs['Alpha'].default_value = 0.35
try: M['fat'].surface_render_method = 'BLENDED'
except Exception: pass

# ================= world / lights =================
w = bpy.data.worlds.new('w'); sc.world = w; w.use_nodes = True
w.node_tree.nodes['Background'].inputs['Color'].default_value = (0.006, 0.008, 0.016, 1)
LIGHTS = {'out': [], 'in': []}
def area(name, loc, target, e, size, col, grp):
    bpy.ops.object.light_add(type='AREA', location=loc); l = bpy.context.object; l.name = name
    l.data.energy = e; l.data.size = size; l.data.color = col; l.visible_camera = False; l.visible_glossy = False
    l.rotation_euler = (Vector(target) - Vector(loc)).to_track_quat('-Z', 'Y').to_euler(); LIGHTS[grp].append(l); return l

# ================= OUTSIDE: dining room =================
bpy.ops.mesh.primitive_plane_add(size=12, location=(-1, 1, 0)); obj_setup(bpy.context.object, 'room_floor', M['wood'])
box('room_wall', (-1, 1.6, 1.6), (12, 0.1, 3.2), M['wall'], bevel=0)
TX, TY = 0.15, 0.2
box('table_top', (TX, TY, 0.75), (1.2, 0.75, 0.05), M['table'], bevel=0.01)
for sx in (-1, 1):
    for sy in (-1, 1): box(f'table_leg{sx}{sy}', (TX + sx * 0.54, TY + sy * 0.31, 0.37), (0.05, 0.05, 0.74), M['table'], bevel=0.005)
box('table_runner', (TX, TY, 0.778), (1.25, 0.3, 0.006), M['cloth'], bevel=0.002)
cyl('plate', (TX - 0.05, TY - 0.15, 0.785), 0.16, 0.015, M['plate'], bevel=0.004)
big_rice = [sphere('rice_heap', (TX - 0.05, TY - 0.15, 0.79), 0.11, M['rice'], scale=(1, 1, 0.55)),
            sphere('rice_heap2', (TX - 0.1, TY - 0.12, 0.83), 0.06, M['rice'], scale=(1, 1, 0.7))]
cyl('rice_pot', (TX + 0.3, TY + 0.05, 0.85), 0.11, 0.14, M['steel'], bevel=0.006)
sphere('rice_in_pot', (TX + 0.3, TY + 0.05, 0.92), 0.1, M['rice'], scale=(1, 1, 0.35))
healthy = [sphere('rice_small', (TX - 0.1, TY - 0.15, 0.79), 0.05, M['rice'], scale=(1, 1, 0.5)),
           sphere('salad', (TX + 0.0, TY - 0.13, 0.79), 0.06, M['leaf'], scale=(1, 1, 0.45)),
           sphere('carrots', (TX + 0.01, TY - 0.19, 0.8), 0.025, M['carrot'], scale=(1.6, 1, 0.6)),
           cyl('dal_bowl', (TX - 0.32, TY - 0.08, 0.8), 0.07, 0.05, M['steel'], bevel=0.004),
           cyl('dal', (TX - 0.32, TY - 0.08, 0.82), 0.062, 0.01, M['dal'])]
gm = box('glucometer', (TX + 0.36, TY - 0.16, 0.8), (0.07, 0.12, 0.025), M['monitor'], bevel=0.008, seg=4)
gm.rotation_euler = (0, 0, math.radians(-15))
gscr = box('glucometer_screen', (TX + 0.36, TY - 0.17, 0.8135), (0.05, 0.05, 0.002), M['screen'], bevel=0.002); parent(gscr, gm)
def lcd(name, s_, m):
    o = text(name, s_, (TX + 0.36, TY - 0.17, 0.815), 0.022, m, rot=(0, 0, math.radians(-15)), extrude=0.0003); parent(o, gm); return o
read_hi, read_ok = lcd('reading_hi', '180', M['lcdr']), lcd('reading_ok', '110', M['lcdg'])
show(read_hi, ranges_for(['room_in', 'room_out'])); show(read_ok, ranges_for(['room_healthy']))
for o in big_rice: show(o, ranges_for(['room_in', 'room_out', 'body_wide']))
for o in healthy: show(o, ranges_for(['room_healthy']))

# Raju: realistic MPFB2 (MakeHuman, CC0) character generated by raju_make.py
RAJU_BLEND = os.environ.get('RAJU_BLEND', '/opt/reel/raju.blend')
with bpy.data.libraries.load(RAJU_BLEND, link=False) as (src, dst):
    dst.objects = [n for n in src.objects]
for o in dst.objects:
    if o is not None and o.type in ('MESH', 'ARMATURE'): sc.collection.objects.link(o)
raju = bpy.data.objects['raju_rig']; raju.location = (-0.55, 0.15, 0.0)
import mathutils
REST = {}
for side in ('L', 'R'):
    for bn in ('upperarm01.', 'upperleg01.', 'lowerleg01.'):
        pb = raju.pose.bones.get(bn + side)
        if pb: pb.rotation_mode = 'QUATERNION'; REST[bn + side] = pb.rotation_quaternion.copy()
def bone_rot(bn, axis_angles):
    pb = raju.pose.bones.get(bn)
    if not pb: return
    Rb = pb.bone.matrix_local.to_3x3().to_quaternion(); q = mathutils.Quaternion()
    for ax, ang in axis_angles: q = mathutils.Quaternion(ax, math.radians(ang)) @ q
    pb.rotation_quaternion = (Rb.inverted() @ q @ Rb) @ REST[bn]
legs, arms = ['upperleg01.L', 'upperleg01.R'], ['upperarm01.L', 'upperarm01.R']
area('out_key', (1.5, -2.5, 2.6), (0, 0.2, 0.9), 140, 2.0, (1.0, 0.88, 0.72), 'out')
area('out_rim', (-2.5, 1.2, 2.2), (-0.5, 0.2, 1.2), 120, 1.2, (0.6, 0.75, 1.0), 'out')
area('out_fill', (-1.5, -3.5, 1.5), (0, 0, 1), 25, 3.0, (1, 0.95, 0.9), 'out')
area('out_top', (0.2, 0.2, 2.8), (0.2, 0.2, 0.8), 45, 1.2, (1, 0.95, 0.85), 'out')

# ================= INSIDE: X-ray organs, placed in Raju's own body =================
from mathutils.bvhtree import BVHTree
bpy.context.view_layer.update()
RL = raju.matrix_world.translation.copy()
def bone_head(n): return raju.matrix_world @ raju.data.bones[n].head_local
EYE_R = (bone_head('eye.R') + bone_head('eye.L')) / 2
ANAT_EYE = Vector((0.0, -0.0645, 1.5907))
body = bpy.data.objects['raju_body']
dg = bpy.context.evaluated_depsgraph_get(); be = body.evaluated_get(dg)
bm_ = bmesh.new(); bm_.from_mesh(be.to_mesh()); bm_.transform(body.matrix_world); BVH = BVHTree.FromBMesh(bm_)
def torso_mid_y(z):
    ys = [v.co.y for v in bm_.verts if abs(v.co.z - z) < 0.015 and abs(v.co.x - RL.x) < 0.12]
    return (min(ys) + max(ys)) / 2 if ys else RL.y
def inside_body(p):
    loc, nrm, idx, d = BVH.find_nearest(p); return loc is not None and (p - loc).dot(nrm) < 0
HEAD_OFF = EYE_R - ANAT_EYE
TORSO_OFF = Vector((RL.x, torso_mid_y(1.29) - 0.012, HEAD_OFF.z))
def off_for(z):
    t = min(1, max(0, (z - 1.36) / 0.16)); return TORSO_OFF.lerp(HEAD_OFF, t)
def place(objs):
    for o in objs:
        c, _ = anat.centre([o]); o.location += off_for(c.z)
    bpy.context.view_layer.update()
# legs: map Z-Anatomy's legs onto Raju's (height scale about the floor, x/y to his knees)
KNEE = {'l': bone_head('lowerleg01.L'), 'r': bone_head('lowerleg01.R')}
ANAT_KNEE_Z, ANAT_KNEE_X = 0.49, 0.09
def place_leg(objs):
    from mathutils import Matrix
    for o in objs:
        side = 'l' if o.name.endswith('.l') else 'r'; k = KNEE[side]; s = k.z / ANAT_KNEE_Z
        ax = ANAT_KNEE_X if side == 'l' else -ANAT_KNEE_X
        T = Matrix.Translation(Vector((k.x - ax, k.y - 0.0, 0)))
        o.matrix_world = T @ Matrix.Diagonal((1, 1, s, 1)) @ o.matrix_world
    bpy.context.view_layer.update()

heart_root, heart_m = anat.load_native('heart', 'heart')
art_root, art_m = anat.load_native('arteries', 'arteries')
kid_root, kid_m = anat.load_native('kidneys', 'kidneys')
brain_root, brain_m = anat.load_native('brain', 'brain')
eye_root, eye_m = anat.load_native('eyes', 'eye')
brain_m = [o for o in brain_m if anat.centre([o])[0].z > 1.47]
for o in list(brain_root.children):
    if o not in brain_m: bpy.data.objects.remove(o, do_unlink=True)

def load_set(fname, groups):
    """import one Z-Anatomy file once and keep several named groups: {key: (names, colour, rough)}"""
    before = set(bpy.data.objects)
    bpy.ops.import_scene.fbx(filepath=anat.FBX + fname)
    new = [o for o in bpy.data.objects if o not in before]
    bpy.context.view_layer.update()
    out, keepset = {}, set()
    for key, (names, col, rough) in groups.items():
        m = anat._mat('sg_' + key, col, rough, 0.3)
        sel = [o for o in new if o.type == 'MESH' and o.name in names]
        for o in sel:
            mw = o.matrix_world.copy(); o.parent = None; o.matrix_world = mw
            o.data.materials.clear(); o.data.materials.append(m)
            o.data.polygons.foreach_set('use_smooth', [True] * len(o.data.polygons))
        out[key] = sel; keepset |= set(sel)
    for o in new:
        if o not in keepset: bpy.data.objects.remove(o, do_unlink=True)
    for key, sel in out.items():
        for o in sel: o.name = key + '_' + o.name
    bpy.context.view_layer.update()
    return out
V = load_set('VisceralSystem100.fbx', {
    'liver': (['Liver'], (0.33, 0.07, 0.05), 0.4),
    'stomach': (['Stomach', 'Duodenum'], (0.72, 0.38, 0.34), 0.45),
    'pancreas': (['Pancreas'], (0.85, 0.6, 0.38), 0.45),
    'gut': (['Jejunum', 'Ascending colon', 'Transverse colon', 'Descending colon', 'Sigmoid colon'], (0.66, 0.36, 0.32), 0.45)})
MU = load_set('MuscularSystem100.fbx', {
    'thigh': (['Rectus femoris muscle.l', 'Rectus femoris muscle.r', 'Vastus lateralis muscle.l', 'Vastus lateralis muscle.r',
               'Vastus medialis muscle.l', 'Vastus medialis muscle.r'], (0.5, 0.06, 0.05), 0.4)})
NV = load_set('NervousSystem100.fbx', {
    'nerves': ([f'{n} nerve.{s}' for n in ('Sciatic', 'Tibial', 'Common fibular', 'Deep fibular', 'Superficial fibular',
                                          'Medial plantar', 'Lateral plantar') for s in ('l', 'r')], (0.95, 0.82, 0.3), 0.4)})
liver_m, stom_m, panc_m, gut_m = V['liver'], V['stomach'], V['pancreas'], V['gut']
thigh_m, nerve_m = MU['thigh'], NV['nerves']
for g in (heart_m, art_m, kid_m, brain_m, eye_m, liver_m, stom_m, panc_m, gut_m): place(g)
place_leg(thigh_m); place_leg(nerve_m)
C = lambda objs: anat.centre(objs)[0]
HC, KC, BC, EC = C(heart_m), C(kid_m), C(brain_m), C(eye_m)
LC, PC, GC, SC_ = C(liver_m), C(panc_m), C(gut_m), C(stom_m)
TH = C([o for o in thigh_m if o.name.endswith('.l')]); FT = C([o for o in nerve_m if o.name.endswith('.l') and 'plantar' in o.name.lower()])
SHIN = C([o for o in nerve_m if o.name.endswith('.l') and 'fibular' in o.name.lower()])
for nm_, p_ in (('heart', HC), ('kidneys', KC), ('liver', LC), ('pancreas', PC), ('gut', GC), ('thigh', TH), ('foot', FT)):
    print('XRAY fit', nm_, tuple(round(x, 3) for x in p_), inside_body(p_))
def named(sub):
    for o in art_m:
        if sub in o.name.lower(): return C([o])
AO_T = named('thoracic aorta') or HC + Vector((0.01, 0.05, -0.05))
AO_A = named('abdominal aorta') or KC + Vector((0, 0.02, 0.05))
heart = bpy.data.objects.new('heart_pivot', None); sc.collection.objects.link(heart); heart.location = HC
for o in heart_m: parent(o, heart)
ORG = heart_m + art_m + kid_m + brain_m + eye_m + liver_m + stom_m + panc_m + gut_m + thigh_m + nerve_m
# visceral fat: a soft glowing mass around the gut (only in the fat station)
fatb = sphere('visceral_fat', GC + Vector((0, -0.035, 0.04)), 0.1, M['fat'], scale=(1.25, 0.55, 0.95), seg=48, ring=24)

# ---- X-ray state per station ----
XK = []
for s in STN['order']:
    a, b = S(s)
    if s == 'room_in': XK += [(a, 0), (fr(s, 0.55), 0), (fr(s, 0.78), 1), (b, 1)]
    elif s == 'room_out': XK += [(a, 1), (fr(s, 0.2), 1), (fr(s, 0.45), 0), (b, 0)]
    elif s == 'room_healthy': XK += [(a, 0), (b, 0)]
    else: XK += [(a, 1), (b, 1)]
X_ON0, X_OFF1 = fr('room_in', 0.55), fr('room_out', 0.45)
xmats = set()
FACE_PARTS = ('raju_body.teeth_base', 'raju_body.high-poly', 'raju_body.eyelashes02', 'raju_body.eyebrow006')
for o in [o for o in bpy.data.objects if o.name.startswith('raju_body') and o.name not in FACE_PARTS]:
    for slot in o.material_slots:
        m = slot.material
        if not m or m.name in xmats or not m.use_nodes: continue
        xmats.add(m.name); nt = m.node_tree
        outn = next((n for n in nt.nodes if n.type == 'OUTPUT_MATERIAL' and n.is_active_output), None) or \
            next((n for n in nt.nodes if n.type == 'OUTPUT_MATERIAL'), None)
        if not outn or not outn.inputs['Surface'].links: continue
        src_ = outn.inputs['Surface'].links[0].from_socket
        mix = nt.nodes.new('ShaderNodeMixShader'); tr = nt.nodes.new('ShaderNodeBsdfTransparent'); em = nt.nodes.new('ShaderNodeEmission')
        shell = nt.nodes.new('ShaderNodeMixShader'); lw = nt.nodes.new('ShaderNodeLayerWeight'); mr = nt.nodes.new('ShaderNodeMapRange')
        lw.inputs['Blend'].default_value = 0.22
        mr.inputs['To Min'].default_value = 0.0; mr.inputs['To Max'].default_value = 0.55
        em.inputs['Color'].default_value = (0.25, 0.65, 1.0, 1); em.inputs['Strength'].default_value = 1.6
        nt.links.new(lw.outputs['Facing'], mr.inputs['Value']); nt.links.new(mr.outputs['Result'], shell.inputs['Fac'])
        nt.links.new(tr.outputs[0], shell.inputs[1]); nt.links.new(em.outputs[0], shell.inputs[2])
        nt.links.new(src_, mix.inputs[1]); nt.links.new(shell.outputs[0], mix.inputs[2]); nt.links.new(mix.outputs[0], outn.inputs['Surface'])
        keys(mix.inputs['Fac'], XK)
        try: m.surface_render_method = 'BLENDED'
        except Exception: pass
        m.use_backface_culling = True
def inside_except(hide):
    """visible from X_ON0 to X_OFF1 except during the given stations (organs in front of the target are hidden)"""
    cuts = sorted(S(n) for n in hide)
    out, a = [], X_ON0
    for s0, s1 in cuts:
        if s0 > a: out.append((a, s0))
        a = max(a, s1 + 1)
    out.append((a, X_OFF1 + 1)); return out
HIDE = {id(o): [] for o in ORG}
for o in stom_m + gut_m: HIDE[id(o)] = ['pancreas', 'pancreas_tired', 'vessels', 'vessels_stuck', 'kidney']
for o in liver_m: HIDE[id(o)] = ['vessels', 'vessels_stuck', 'kidney']
for o in panc_m: HIDE[id(o)] = ['vessels', 'vessels_stuck', 'kidney']
for o in ORG: show(o, inside_except(HIDE[id(o)]))
for nm in FACE_PARTS:
    o = bpy.data.objects.get(nm)
    if o: show(o, [(1, fr('room_in', 0.78)), (fr('room_out', 0.2) + 4, END + 1)])
show(fatb, ranges_for(['fat']))

# ---- lights: room dims while inside; organ lights come up ----
def ramp(l, base, pairs):
    for f, k in pairs: l.data.energy = base * k; l.data.keyframe_insert('energy', frame=f)
for i, (p, e) in enumerate([(HC, 10), (KC, 8), (BC, 10), (GC, 9), (PC, 8), (LC, 8), (TH, 10), (SHIN, 10), (FT, 8)]):
    area(f'in_key{i}', p + Vector((-0.5, -0.9, 0.5)), p, e, 0.6, (1, 0.92, 0.88), 'in')
    area(f'in_rim{i}', p + Vector((0.6, 0.6, 0.3)), p, e * 0.8, 0.5, (0.45, 0.65, 1), 'in')
for l in LIGHTS['out']: ramp(l, l.data.energy, [(f, 1 - 0.97 * v) for f, v in XK])
for l in LIGHTS['in']: ramp(l, l.data.energy, XK)
for mname in ('wall', 'wood', 'table', 'cloth', 'plate', 'steel', 'rice', 'dal', 'leaf', 'carrot', 'monitor', 'screen'):
    bb = bsdf(M[mname]); base_c = tuple(bb.inputs['Base Color'].default_value)
    for f, v in XK:
        c_ = tuple(base_c[i] * (1 - v) + (0.004, 0.006, 0.012, 1)[i] * v for i in range(4))
        bb.inputs['Base Color'].default_value = c_; bb.inputs['Base Color'].keyframe_insert('default_value', frame=f)

# ---- organ glow: alive inside; per-station accents ----
def glow(objs, pairs, color=None):
    for m in {s.material for o in objs for s in o.material_slots if s.material}:
        b = bsdf(m)
        b.inputs['Emission Color'].default_value = (*(color or tuple(b.inputs['Base Color'].default_value)[:3]), 1)
        keys(b.inputs['Emission Strength'], pairs)
BASE = [(f, 0.12 * v) for f, v in XK]
def with_station(name, inner):
    """base glow everywhere, replaced by `inner` keys inside the station"""
    a, b = S(name)
    return [(f, v) for f, v in BASE if f < a - 1 or f > b + 1] + [(a - 1, 0.12), (b + 1, 0.12)] + inner
for grp in (brain_m, stom_m):
    glow(grp, BASE)
# pancreas: steady pulse (insulin release) / tired: fast flicker fading out
pa, pb = S('pancreas'); ta, tb = S('pancreas_tired')
pan = [(f, 0.35 + 0.9 * abs(math.sin((f - pa) / FPS * 3.0))) for f in range(pa, pb + 1, 5)]
tir = [(f, (0.4 + 1.1 * abs(math.sin((f - ta) / FPS * 7.0))) * max(0.04, 1 - (f - ta) / max(1, tb - ta)) ** 1.5) for f in range(ta, tb + 1, 3)]
pk = [(f, v) for f, v in BASE if not (pa - 1 <= f <= pb + 1 or ta - 1 <= f <= tb + 1)] + pan + tir + [(pa - 1, 0.12), (pb + 1, 0.12), (ta - 1, 0.12), (tb + 1, 0.12)]
glow(panc_m, pk, (1.0, 0.75, 0.35))
# muscle: fills with sugar (gold) in the muscle station
ma, mb = S('muscle')
glow(thigh_m, with_station('muscle', [(ma, 0.15), (fr('muscle', 0.35), 0.15), (mb, 1.3)]), (1.0, 0.65, 0.12))
# liver: releases sugar, then insulin shuts it down
la, lb = S('liver')
glow(liver_m, with_station('liver', [(la, 1.0), (fr('liver', 0.4), 1.0), (lb, 0.1)]), (1.0, 0.6, 0.12))
# gut: sugar glow while absorbing
glow(gut_m, with_station('gut', [(S('gut')[0], 0.3), (S('gut')[1], 1.0)]), (1.0, 0.65, 0.15))
# kidneys: straining
ka, kb = S('kidney')
glow(kid_m, with_station('kidney', [(f, 0.35 + 0.9 * abs(math.sin((f - ka) / FPS * 3.0))) for f in range(ka, kb + 1, 6)]))
# heart: flushes red in its station
ha, hb = S('heart')
glow(heart_m, with_station('heart', [(ha, 0.3), (ha + 12, 1.4), (hb, 1.4)]), (1.0, 0.08, 0.04))
# eye: retina flushes red; nerves: bright -> fading red (numb)
ea, eb = S('eye')
glow(eye_m, with_station('eye', [(ea, 0.12), (fr('eye', 0.3), 0.12), (fr('eye', 0.45), 1.4), (eb, 1.4)]), (1.0, 0.08, 0.04))
fa, fb = S('feet')
glow(nerve_m, with_station('feet', [(fa, 2.0), (fr('feet', 0.3), 2.0), (fb, 0.15)]))
NB = bsdf(nerve_m[0].material_slots[0].material)
for f, col in ((1, (0.95, 0.82, 0.3)), (fr('feet', 0.3), (0.95, 0.82, 0.3)), (fb, (0.9, 0.1, 0.05)), (fb + 1, (0.95, 0.82, 0.3))):
    NB.inputs['Emission Color'].default_value = (*col, 1); NB.inputs['Emission Color'].keyframe_insert('default_value', frame=f)
# visceral fat glow pulse
FB = bsdf(M['fat'])
keys(FB.inputs['Emission Strength'], [(f, 0.6 + 0.5 * abs(math.sin((f - S('fat')[0]) / FPS * 2.0))) for f in range(S('fat')[0], S('fat')[1] + 1, 6)])
# arteries: normal red, yellowish and stiff while sugar is stuck
WALL = bsdf(art_m[0].material_slots[0].material)
va, vb = S('vessels_stuck')
for f, col, rough in ((1, (0.55, 0.02, 0.015), 0.3), (va - 1, (0.55, 0.02, 0.015), 0.3), (fr('vessels_stuck', 0.5), (0.75, 0.5, 0.12), 0.6),
                      (vb, (0.75, 0.5, 0.12), 0.6), (vb + 1, (0.55, 0.02, 0.015), 0.3)):
    WALL.inputs['Base Color'].default_value = (*col, 1); WALL.inputs['Base Color'].keyframe_insert('default_value', frame=f)
    WALL.inputs['Roughness'].default_value = rough; WALL.inputs['Roughness'].keyframe_insert('default_value', frame=f)
glow(art_m, with_station('vessels_stuck', [(va, 0.12), (vb, 0.6)]), (1.0, 0.6, 0.12))

# ---- heartbeat ----
phase = 0.0
for f in ALLFR:
    phase += (1.6 if ha <= f <= hb else 1.2) / FPS
    bt = max(0.0, math.sin(phase * 2 * math.pi)) ** 3
    s_ = 1 + 0.06 * bt; heart.scale = (s_, s_, s_); heart.keyframe_insert('scale', frame=f)
for fc in fcurves(heart):
    for kp in fc.keyframe_points: kp.interpolation = 'LINEAR'

# ---- flowing glucose (gold) and insulin (cyan keys) along paths, per station ----
def path_curve(name, pts):
    cu = bpy.data.curves.new(name, 'CURVE'); cu.dimensions = '3D'; cu.resolution_u = 24
    sp = cu.splines.new('BEZIER'); sp.bezier_points.add(len(pts) - 1)
    for p, c in zip(sp.bezier_points, pts): p.co = c; p.handle_left_type = p.handle_right_type = 'AUTO'
    o = bpy.data.objects.new(name, cu); sc.collection.objects.link(o); cu.use_path = True; cu.path_duration = 100; return o
def flowers(prefix, pts, n, kind, period, stations, radial=0.008):
    crv = path_curve('route_' + prefix, pts)
    for i in range(n):
        e = bpy.data.objects.new(f'{prefix}_e{i}', None); sc.collection.objects.link(e)
        c = e.constraints.new('FOLLOW_PATH'); c.target = crv; c.use_fixed_location = True; c.use_curve_follow = True
        c.offset_factor = 0.0; c.keyframe_insert('offset_factor', frame=1)
        c.offset_factor = 1.0; c.keyframe_insert('offset_factor', frame=1 + period)
        ph = random.uniform(0, period)
        for fc in fcurves(e):
            if 'offset_factor' in fc.data_path:
                for kp in fc.keyframe_points:
                    kp.interpolation = 'LINEAR'; kp.co[0] -= ph; kp.handle_left[0] -= ph; kp.handle_right[0] -= ph
                fc.modifiers.new('CYCLES')
        if kind == 'gold': o = sphere(f'{prefix}{i}', (0, 0, 0), 0.0035, M['gold'], seg=12, ring=6)
        else: o = box(f'{prefix}{i}', (0, 0, 0), (0.008, 0.0025, 0.0025), M['key'], bevel=0.0006, seg=1)
        rr = radial * math.sqrt(random.random()); a = random.uniform(0, 6.283)
        o.parent = e; o.location = (0, rr * math.cos(a), rr * math.sin(a))
        o.rotation_euler = (random.uniform(0, 6.3), random.uniform(0, 6.3), random.uniform(0, 6.3))
        show(o, ranges_for(stations))
V3 = Vector
HIP_L = bone_head('upperleg01.L')
flowers('gutsugar', [GC + V3((0.03, -0.02, -0.03)), GC + V3((0.0, -0.01, 0.05)), LC + V3((0.02, 0.0, -0.02)), HC + V3((0, 0, -0.04)), HC],
        60, 'gold', 150, ['gut', 'body_wide'], 0.012)
flowers('aorta', [HC + V3((0, 0.03, 0.08)), AO_T, AO_A, AO_A + V3((0, 0, -0.12))], 45, 'gold', 120, ['vessels', 'body_wide', 'pancreas', 'liver'], 0.008)
flowers('aorta_stuck', [HC + V3((0, 0.03, 0.08)), AO_T, AO_A, AO_A + V3((0, 0, -0.12))], 160, 'gold', 260, ['vessels_stuck', 'kidney', 'eye', 'heart', 'fat', 'pancreas_tired'], 0.01)
flowers('insulin', [PC + V3((0.01, -0.01, 0.0)), PC + V3((0.0, -0.03, 0.05)), HC + V3((0.0, -0.01, -0.06)), AO_A, AO_A + V3((0, 0, -0.12))],
        40, 'key', 110, ['pancreas'], 0.01)
flowers('legsugar', [AO_A, AO_A + V3((0, 0, -0.12)), HIP_L + V3((0, -0.02, -0.05)), TH + V3((0, -0.01, 0.1)), TH + V3((0, -0.01, -0.08))],
        55, 'gold', 120, ['muscle'], 0.012)
flowers('legkeys', [AO_A, AO_A + V3((0, 0, -0.12)), HIP_L + V3((0, -0.02, -0.05)), TH + V3((0, -0.01, 0.1)), TH + V3((0, -0.01, -0.08))],
        25, 'key', 120, ['muscle'], 0.012)
flowers('liversugar', [LC + V3((-0.02, -0.02, 0)), LC + V3((0.02, -0.01, 0.06)), HC + V3((0, 0, -0.05))], 35, 'gold', 90, ['liver'], 0.01)
for side in (-1, 1):
    k0 = KC + V3((side * 0.05, 0, 0))
    flowers(f'urine{side}', [k0, k0 + V3((-side * 0.02, -0.01, -0.08)), k0 + V3((-side * 0.04, -0.02, -0.2)), V3((RL.x, KC.y - 0.03, KC.z - 0.3))],
            30, 'gold', 90, ['kidney'], 0.004)
# eye: damage sparks
EYE_P = EC + V3((0, 0.01, 0))
for i in range(20):
    sp_ = sphere(f'eyespark{i}', EYE_P, 0.0025, M['burst'], seg=10, ring=5)
    f0 = fr('eye', 0.45) + (i % 5) * 9
    dv = V3((random.uniform(-1, 1), random.uniform(-0.5, 0.5), random.uniform(-1, 1))).normalized() * random.uniform(0.01, 0.025)
    sp_.location = EYE_P; sp_.keyframe_insert('location', frame=f0); sp_.location = EYE_P + dv; sp_.keyframe_insert('location', frame=f0 + 20)
    show(sp_, [(f0, min(eb + 1, f0 + 24))])
keys(bsdf(M['burst']).inputs['Emission Strength'], [(1, 0), (ea, 0), (fr('eye', 0.45), 12), (eb, 8), (eb + 1, 0)])

# ================= room_healthy: Raju walks after his meal =================
a11, b11 = fr('room_healthy', 0.05), fr('room_healthy', 0.6)
x0 = raju.location.x
def keybones(f):
    for bn in legs + arms + ['lowerleg01.L', 'lowerleg01.R']:
        pb = raju.pose.bones.get(bn)
        if pb: pb.keyframe_insert('rotation_quaternion', frame=f)
for bn in REST: raju.pose.bones[bn].rotation_quaternion = REST[bn]
raju.keyframe_insert('location', frame=1, index=0); raju.keyframe_insert('rotation_euler', frame=1, index=2)
keybones(1); keybones(a11 - 1)
raju.keyframe_insert('location', frame=a11 - 1, index=0); raju.keyframe_insert('rotation_euler', frame=a11 - 1, index=2)
for f in range(a11, b11 + 1, 2):
    tt = (f - a11) / (b11 - a11)
    raju.location.x = x0 - 1.6 * math.sin(min(1, tt / 0.5) * math.pi / 2) if tt < 0.5 else x0 - 1.6 + 1.6 * math.sin((tt - 0.5) / 0.5 * math.pi / 2)
    raju.keyframe_insert('location', frame=f, index=0)
    raju.rotation_euler[2] = math.radians(-90 if tt < 0.5 else 90) * min(1, abs(math.sin(tt * math.pi * 2)) * 3)
    raju.keyframe_insert('rotation_euler', frame=f, index=2)
    ph = (f - a11) / FPS * 2 * math.pi * 0.9; sw = math.sin(ph) * 24
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
raju.location.x = x0; raju.keyframe_insert('location', frame=b11 + 1, index=0)
raju.rotation_euler[2] = 0; raju.keyframe_insert('rotation_euler', frame=b11 + 1, index=2)

# ================= camera: one shot per station =================
cd = bpy.data.cameras.new('cam'); cam = bpy.data.objects.new('cam', cd); sc.collection.objects.link(cam); sc.camera = cam
cd.sensor_width = 24; cd.dof.use_dof = True
tgt = bpy.data.objects.new('cam_target', None); sc.collection.objects.link(tgt)
c = cam.constraints.new('TRACK_TO'); c.target = tgt; c.track_axis = 'TRACK_NEGATIVE_Z'; c.up_axis = 'UP_Y'
cd.dof.focus_object = tgt
KEYS = []
def K(f, c_, t_, fs, ln): KEYS.append((int(f), V3(c_), V3(t_), fs, ln))
def drift(name, c0, c1, t_, ln, fs=5.6, t1=None):
    a, b = S(name); K(a, c0, t_, fs, ln); K(b, c1, t1 or t_, fs, ln)
RW = RL + V3((0, 0, 1.0))
s = 'room_in'
K(S(s)[0], (1.6, -2.6, 1.7), (-0.1, 0.1, 1.0), 4.0, 32)
K(fr(s, 0.45), (0.9, -1.8, 1.45), RL + V3((0.15, 0, 1.15)), 3.5, 32)
K(fr(s, 0.75), RL + V3((0.3, -1.25, 1.25)), GC + V3((0, 0, 0.06)), 4.0, 35)
K(S(s)[1], GC + V3((0.12, -0.85, 0.08)), GC + V3((0, 0, 0.06)), 5.6, 35)
drift('body_wide', RL + V3((0.3, -1.9, 1.25)), RL + V3((-0.2, -1.75, 1.2)), RW + V3((0, 0, 0.1)), 32, 4.5)
drift('gut', GC + V3((0.15, -0.72, 0.1)), GC + V3((0.06, -0.6, 0.06)), GC + V3((0, 0, 0.04)), 35)
drift('vessels', AO_T.lerp(AO_A, 0.5) + V3((0.14, -0.6, 0.06)), AO_T.lerp(AO_A, 0.5) + V3((0.07, -0.5, 0.03)), AO_T.lerp(AO_A, 0.5), 36)
drift('pancreas', PC + V3((0.16, -0.5, 0.08)), PC + V3((0.08, -0.4, 0.04)), PC, 40, 6.3)
drift('muscle', TH + V3((0.25, -0.8, 0.12)), TH + V3((0.14, -0.66, 0.06)), TH + V3((0, 0, 0.02)), 35)
drift('liver', LC + V3((-0.16, -0.58, 0.06)), LC + V3((-0.08, -0.48, 0.03)), LC, 38)
drift('fat', GC + V3((0.22, -0.85, 0.12)), GC + V3((0.1, -0.7, 0.06)), GC + V3((0, 0, 0.04)), 32, 4.5)
drift('pancreas_tired', PC + V3((-0.12, -0.45, 0.05)), PC + V3((-0.05, -0.37, 0.02)), PC, 42, 6.3)
drift('vessels_stuck', AO_T.lerp(AO_A, 0.5) + V3((-0.12, -0.5, 0.08)), AO_T.lerp(AO_A, 0.5) + V3((-0.05, -0.42, 0.04)), AO_T.lerp(AO_A, 0.5), 40, 6.3)
drift('kidney', KC + V3((0.18, -0.72, 0.08)), KC + V3((0.12, -0.6, 0.05)), KC, 35)
drift('eye', EC + V3((0.15, -0.42, 0.02)), EC + V3((0.09, -0.33, 0.0)), EC, 40)
drift('feet', SHIN.lerp(FT, 0.5) + V3((0.35, -0.95, 0.2)), SHIN.lerp(FT, 0.5) + V3((0.22, -0.78, 0.12)), SHIN.lerp(FT, 0.6), 35, 4.5)
drift('heart', HC + V3((0.12, -0.42, 0.04)), HC + V3((0.08, -0.34, 0.03)), HC, 42, 6.3)
s = 'room_out'
K(S(s)[0], HC + V3((0.15, -0.6, 0.0)), HC + V3((0, 0, -0.06)), 5.6, 38)
K(fr(s, 0.4), RL + V3((0.6, -1.7, 1.4)), RL + V3((0, 0, 1.25)), 3.5, 35)
K(S(s)[1], RL + V3((0.95, -2.1, 1.55)), RL + V3((0, 0, 1.2)), 3.5, 35)
s = 'room_healthy'
K(S(s)[0], (1.4, -3.2, 1.6), (-0.9, 0.1, 1.0), 4.5, 26)
K(S(s)[1], (1.1, -2.7, 1.55), (-0.3, 0.1, 1.0), 4.5, 28)
starts = {S(n)[0] for n in STN['order']}
for f, c_, t_, fs, ln in KEYS:
    cam.location = c_; cam.keyframe_insert('location', frame=f)
    tgt.location = t_; tgt.keyframe_insert('location', frame=f)
    cd.dof.aperture_fstop = fs; cd.dof.keyframe_insert('aperture_fstop', frame=f)
    cd.lens = ln; cd.keyframe_insert('lens', frame=f)
ends = {S(n)[1] for n in STN['order']}
for idb, path in ((cam, 'location'), (tgt, 'location'), (cd, 'dof.aperture_fstop'), (cd, 'lens')):
    for fc in fcurves(idb):
        if fc.data_path == path:
            for kp in fc.keyframe_points:
                f_ = int(round(kp.co[0]))
                kp.handle_left_type = kp.handle_right_type = 'AUTO_CLAMPED'
                if f_ in starts or f_ in ends: kp.handle_left_type = kp.handle_right_type = 'VECTOR'
                if f_ in ends: kp.interpolation = 'CONSTANT'

# ================= render settings (EEVEE is applied by /opt/reel/eevee.py at render time) =================
sc.render.resolution_x, sc.render.resolution_y = 1080, 1920; sc.render.resolution_percentage = 100
sc.view_settings.view_transform = 'AgX'; sc.view_settings.look = 'AgX - Medium High Contrast'
sc.render.image_settings.file_format = 'JPEG'; sc.render.image_settings.quality = 92
os.makedirs(os.path.join(HERE, 'scene'), exist_ok=True)
bpy.ops.wm.save_as_mainfile(filepath=os.path.join(HERE, 'scene', 'sugar.blend'))
print('built', END, {n: S(n) for n in STN['order']})
