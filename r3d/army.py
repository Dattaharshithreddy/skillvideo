# Army kit: real MPFB humans in the costume library -> one merged, decimated mesh per variant, saved as collections in army.blend.
# Variants: Indian spearmen (3 colours), Indian swordsman, Greek hoplites (2), Alexander, Puru. Also renders a lineup sheet.
import bpy, sys, os, math, random, traceback
sys.path.insert(0, os.path.dirname(__file__))
for o in list(bpy.data.objects): bpy.data.objects.remove(o)
from kitlib import *
random.seed(11)
SHIRT = G('toigo_fisherman_sweater') or G('janexx_old_female_sweater')
BRONZE = solid('a_bronze', (0.78, 0.5, 0.22), 0.3, 1.0, bump=0.03); GOLDM = GOLD()
LEATHER = solid('a_leather', (0.28, 0.15, 0.07), 0.6)
def T(n, col, band=None): return turban_mat('t_' + n, col, band=band or tuple(min(1, c * 1.2) for c in col))
def C(n, col, border=(0.85, 0.6, 0.2), mode='hem', bw=0.06): return cloth('c_' + n, col, border=border, mode=mode, bw=bw, metal_border=False)

def helmet(P, rig, m, crest_m):
    c, r, hd = head_info(P); R = r + 0.02; z0 = c.z - 0.1
    prof = [(R + 0.006, 0.0), (R + 0.012, 0.05), (R + 0.012, 0.1), (R * 0.88, 0.155), (R * 0.55, 0.19), (0.0, 0.2)]
    h = lathe_obj('helm', prof, m, (c.x, c.y, z0), seg=40); h.scale = (1, 1.12, 1); parts = [h]
    for sx in (-1, 1):   # cheek guards
        bpy.ops.mesh.primitive_cube_add(location=(c.x + sx * (R + 0.008), c.y - 0.03, z0 - 0.04)); g = bpy.context.object; g.scale = (0.006, 0.04, 0.05); g.data.materials.append(m); parts.append(g)
    for k in range(11):  # horsehair crest arc, front to back
        a = math.pi * (0.1 + 0.8 * k / 10); y = c.y - 0.17 * math.cos(a); z = z0 + 0.1 + 0.17 * math.sin(a)
        bpy.ops.mesh.primitive_cube_add(location=(c.x, y, z), rotation=(a - math.pi / 2, 0, 0)); b = bpy.context.object; b.scale = (0.013, 0.022, 0.045); b.data.materials.append(crest_m); parts.append(b)
    o = merge(parts); attach([o], rig, 'head'); return o
def aspis(rig, m, scale=0.85):
    e = bone_pos(rig, 'lowerarm01.L'); w = bone_pos(rig, 'wrist.L'); mid = (e + w) / 2
    prof = [(0.0, 0.07), (0.2, 0.06), (0.36, 0.03), (0.45, 0.005), (0.47, 0.0)]
    s = lathe_obj('aspis', [(a * scale, b * scale) for a, b in prof], m, (0, 0, 0), seg=48)
    bpy.ops.mesh.primitive_torus_add(major_radius=0.46 * scale, minor_radius=0.018 * scale); t = bpy.context.object; t.data.materials.append(m)
    o = merge([s, t]); o.rotation_euler = (math.pi / 2, 0, 0); o.location = (mid.x + 0.06, mid.y - 0.12, mid.z); bpy.context.view_layer.update()
    attach([o], rig, 'lowerarm02.L'); return o
def dhal(rig):
    e = bone_pos(rig, 'lowerarm01.L'); w = bone_pos(rig, 'wrist.L'); mid = (e + w) / 2
    objs = kit('shield_dhal', (mid.x + 0.05, mid.y - 0.1, mid.z - 1.0), 1.0); o = merge(objs); attach([o], rig, 'lowerarm02.L'); return o
def spear(rig, s=1.0):
    w = bone_pos(rig, 'wrist.R'); o = merge(kit('spear_bhala', (w.x, w.y - 0.03, 0.0), s)); attach([o], rig, 'wrist.R'); return o
def sword(rig, name='sword_talwar'):
    w = bone_pos(rig, 'wrist.R'); o = merge(kit(name, (w.x, w.y - 0.03, w.z - 0.98), 0.95)); attach([o], rig, 'wrist.R'); return o

def build(name, x, fn):
    before = set(bpy.data.objects)
    try: fn(x)
    except Exception: traceback.print_exc(limit=5); print('VARIANT', name, 'FAIL'); return None
    new = [o for o in bpy.data.objects if o not in before]
    rigs = [o for o in new if o.type == 'ARMATURE']; meshes = [o for o in new if o.type in ('MESH', 'CURVE')]
    meshes = [o for o in meshes if not o.hide_render]
    names = [o.name for o in new]
    m = merge(meshes); mw = m.matrix_world.copy(); m.parent = None; m.matrix_world = mw; keep = m.name
    bpy.context.view_layer.objects.active = m; bpy.ops.object.transform_apply(location=False, rotation=True, scale=True)
    for nm in names:
        o = bpy.data.objects.get(nm)
        if o and nm != keep: bpy.data.objects.remove(o)
    me = m.data; zmin = min(v.co.z for v in me.vertices); cx = sum(v.co.x for v in me.vertices) / len(me.vertices); cy = sum(v.co.y for v in me.vertices) / len(me.vertices)
    for v in me.vertices: v.co.x -= cx; v.co.y -= cy; v.co.z -= zmin
    m.location = (0, 0, 0)
    n0 = len(me.polygons)
    if n0 > 24000:
        d = m.modifiers.new('dec', 'DECIMATE'); d.ratio = 24000 / n0; bpy.context.view_layer.objects.active = m; bpy.ops.object.modifier_apply(modifier='dec')
    m.name = 'A_' + name; col = bpy.data.collections.new('A_' + name); bpy.context.scene.collection.children.link(col)
    for c in m.users_collection: c.objects.unlink(m)
    col.objects.link(m); col.asset_mark(); print('VARIANT', name, n0, '->', len(m.data.polygons), 'h', max(v.co.z for v in me.vertices)); return m

def ind_spear(dh, ut, tb):
    def f(x):
        bm, rig, P = person(x, 0, 0, True, [('ind_dhoti', C('dh' + str(dh), dh)), ('ind_uttariya_diag', C('ut' + str(ut), ut, mode='edge'))], muscle=random.uniform(0.6, 0.85), weight=random.uniform(0.4, 0.6), hair=False)
        turban2(P, rig, T(str(tb), tb), 'pagdi', jewel=False, kalgi=False, pearls=False); moustache(bm, rig, P); spear(rig); dhal(rig)
    return f
def ind_sword(x):
    bm, rig, P = person(x, 0, 0, True, [('ind_dhoti', C('dh_sw', (0.85, 0.55, 0.12))), ('ind_uttariya_diag', C('ut_sw', (0.6, 0.05, 0.04), mode='edge'))], muscle=0.8, hair=False)
    turban2(P, rig, T('sw', (0.6, 0.05, 0.04)), 'pagdi', jewel=False, kalgi=False, pearls=False); moustache(bm, rig, P); sword(rig); dhal(rig)
def greek(tun, crest):
    def f(x):
        bm, rig, P = person(x, 0, 0, True, [('ind_jama_skirt', C('gt' + str(tun), tun, border=(0.5, 0.05, 0.04), bw=0.04)), ('ind_uttariya_diag', C('gc', (0.55, 0.03, 0.03), mode='edge', bw=0.0))], muscle=0.75, hair=False)
        add(SHIRT, bm, 'Clothes', C('gt' + str(tun), tun)); bpy.context.view_layer.update(); P = body_pts(bm)
        helmet(P, rig, BRONZE, solid('crest_' + str(crest), crest, 0.8)); spear(rig); aspis(rig, BRONZE)
    return f
def alexander(x):
    bm, rig, P = person(x, 0, 0, True, [('ind_jama_skirt', C('al_t', (0.95, 0.93, 0.88), border=(1, 0.72, 0.3), bw=0.06)), ('ind_uttariya_diag', C('al_c', (0.3, 0.04, 0.3), mode='edge', border=(1, 0.72, 0.3)))], age=0.4, muscle=0.7, hair=False)
    add(SHIRT, bm, 'Clothes', C('al_t', (0.95, 0.93, 0.88))); bpy.context.view_layer.update(); P = body_pts(bm)
    helmet(P, rig, GOLDM, solid('crest_white', (0.95, 0.95, 0.92), 0.8)); sword(rig, 'sword_khanda'); aspis(rig, GOLDM, 0.75)
def puru(x):
    bm, rig, P = person(x, 0, 0, True, [('ind_kingdhoti', cloth('king_silk', (0.16, 0.004, 0.012), bw=0.08)), ('ind_uttariya_diag', cloth('king_utt', (0.95, 0.72, 0.3), mode='edge', sheen=0.4)), ('ind_janeu', cloth('janeu', (0.95, 0.94, 0.9), bw=0, metal_border=False))], muscle=0.85, weight=0.6, hair=False)
    top, r, hd = head_info(P); attach([merge(kit('crown_kireetam', (top.x, top.y, top.z - 0.06 - 1.3 * 0.9), 0.9))], rig, 'head')
    necklace(bm, rig); armlets(rig); earrings(P, rig); moustache(bm, rig, P); sword(rig, 'sword_khanda')
VARS = [('ind_spear_saffron', ind_spear((0.93, 0.9, 0.84), (0.9, 0.45, 0.05), (0.9, 0.42, 0.04))),
        ('ind_spear_white', ind_spear((0.93, 0.9, 0.84), (0.7, 0.08, 0.05), (0.95, 0.93, 0.88))),
        ('ind_spear_red', ind_spear((0.85, 0.75, 0.55), (0.93, 0.9, 0.84), (0.65, 0.05, 0.04))),
        ('ind_sword', ind_sword),
        ('greek_white', greek((0.92, 0.88, 0.78), (0.6, 0.03, 0.03))),
        ('greek_red', greek((0.55, 0.05, 0.04), (0.08, 0.06, 0.05))),
        ('alexander', alexander), ('puru', puru)]
only = os.environ.get('ONLY'); built = []
for i, (n, f) in enumerate(VARS):
    if only and n not in only.split(','): continue
    m = build(n, 0.0, f)
    if m: built.append(m)
bpy.ops.wm.save_as_mainfile(filepath='/opt/r3d/assets/army.blend')
# lineup sheet (instances of each collection)
for i, m in enumerate(built):
    e = bpy.data.objects.new('L_' + m.name, None); e.instance_type = 'COLLECTION'; e.instance_collection = m.users_collection[0]; e.location = (i * 0.9 - (len(built) - 1) * 0.45, 0, 0); bpy.context.scene.collection.objects.link(e)
    m.users_collection[0].hide_render = False
bpy.ops.mesh.primitive_plane_add(size=40); bpy.context.object.data.materials.append(solid('floor_g', (0.35, 0.42, 0.22), 0.9))
w = bpy.data.worlds.new('w'); bpy.context.scene.world = w; w.use_nodes = True; w.node_tree.nodes['Background'].inputs[0].default_value = (0.6, 0.65, 0.7, 1); w.node_tree.nodes['Background'].inputs[1].default_value = 0.6
bpy.ops.object.light_add(type='SUN', rotation=(math.radians(50), 0, math.radians(-30))); bpy.context.object.data.energy = 3.5
s = bpy.context.scene; s.render.engine = 'CYCLES'; s.cycles.device = 'CPU'; s.cycles.samples = int(os.environ.get('SPP', 48)); s.cycles.use_denoising = True
s.view_settings.view_transform = 'AgX'; s.view_settings.look = 'AgX - Medium High Contrast'
bpy.ops.object.camera_add(location=(0, -8.5, 1.4)); cam = bpy.context.object; bpy.ops.object.empty_add(location=(0, 0, 0.95)); k = cam.constraints.new('TRACK_TO'); k.target = bpy.context.object; k.track_axis = 'TRACK_NEGATIVE_Z'; k.up_axis = 'UP_Y'; cam.data.lens = 40
s.camera = cam; s.render.resolution_x, s.render.resolution_y = 1920, 1080; s.render.resolution_percentage = int(os.environ.get('PCT', 60)); s.render.filepath = '/opt/r3d/out/army_sheet.jpg'
s.render.image_settings.file_format = 'JPEG'; bpy.ops.render.render(write_still=True); print('ARMY_DONE')
