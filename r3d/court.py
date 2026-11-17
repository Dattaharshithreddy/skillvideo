# Royal darbar: pillared hall, throne, chatra, lamps; king, queen, mantri, senapati, purohit, guards, chamara maids, courtiers.
import bpy, sys, os, math, random, bmesh, traceback
sys.path.insert(0, os.path.dirname(__file__))
for o in list(bpy.data.objects): bpy.data.objects.remove(o)
from kitlib import *
random.seed(21)
S = solid
STONE = S('hall_stone', (0.95, 0.88, 0.76), 0.6, tex='stone', tscale=0.5); FLOOR = S('hall_floor', (0.55, 0.45, 0.36), 0.22, tex='ground', tscale=0.3)
PLAST = S('hall_plaster', (1.0, 0.95, 0.85), 0.7, tex='plaster', tscale=0.6); GLD = GOLD(); WOOD = S('hall_wood', (0.6, 0.38, 0.22), 0.5, tex='wood', tscale=1.0)
RED = cloth('velvet_red', (0.25, 0.01, 0.02), bw=0.04, sheen=0.6, rough=0.85); REDC = cloth('carpet_red', (0.3, 0.02, 0.03), mode='edge', bw=0.03, sheen=0.5, rough=0.9)
WHITE = S('chatra_white', (0.92, 0.9, 0.85), 0.6); FLAME = S('flame', (1.0, 0.55, 0.15), 0.5, emit=25.0, bump=0)
def box(sz, loc, m, bev=0.02, rot=(0, 0, 0)):
    bpy.ops.mesh.primitive_cube_add(location=loc, rotation=rot); o = bpy.context.object; o.scale = (sz[0] / 2, sz[1] / 2, sz[2] / 2)
    bpy.ops.object.transform_apply(scale=True)
    if bev: b = o.modifiers.new('b', 'BEVEL'); b.width = bev; b.segments = 2
    o.data.materials.append(m); return o
def lathe(name, prof, m, loc, seg=32):
    me = bpy.data.meshes.new(name); b = bmesh.new(); rings = []
    for r, z in prof: rings.append([b.verts.new((r * math.cos(2 * math.pi * i / seg), r * math.sin(2 * math.pi * i / seg), z)) for i in range(seg)])
    for a, c in zip(rings, rings[1:]):
        for i in range(seg): b.faces.new((a[i], a[(i + 1) % seg], c[(i + 1) % seg], c[i]))
    b.to_mesh(me); b.free(); o = bpy.data.objects.new(name, me); bpy.context.collection.objects.link(o); o.location = loc; o.data.materials.append(m)
    for p in o.data.polygons: p.use_smooth = True
    return o
def cylr(r, d, loc, m, rot=(0, 0, 0), v=32):
    bpy.ops.mesh.primitive_cylinder_add(radius=r, depth=d, location=loc, rotation=rot, vertices=v); o = bpy.context.object; o.data.materials.append(m); bpy.ops.object.shade_smooth(); return o

# ---- hall ----
bpy.ops.mesh.primitive_plane_add(size=60); bpy.context.object.data.materials.append(FLOOR)
HZ = 6.4
PILLAR = [(0.32, 0.0), (0.32, 0.35), (0.26, 0.45), (0.22, 0.55), (0.22, 1.6), (0.26, 1.7), (0.2, 1.8), (0.2, 3.6), (0.25, 3.7), (0.19, 3.8), (0.19, 5.4), (0.24, 5.5), (0.3, 5.75), (0.36, 5.95), (0.36, 6.05)]
for sx in (-1, 1):
    for k in range(6):
        y = -7 + k * 3.0; x = sx * 4.6
        box((0.75, 0.75, 0.35), (x, y, 0.175), STONE)
        lathe('pillar', PILLAR, STONE, (x, y, 0.3))
        for j in range(4):   # carved bands with tiny relief figures
            for a in range(8): ang = a * math.pi / 4; ball(0.035, (x + 0.22 * math.cos(ang), y + 0.22 * math.sin(ang), 2.7 + j * 0.02 if j < 1 else 4.6), STONE, (1, 1, 1.6), 8)
        box((1.3, 0.5, 0.25), (x, y, HZ + 0.3), STONE)                      # bracket (potika)
    box((0.7, 22, 0.45), (sx * 4.6, 0.5, HZ + 0.62), STONE)                  # beam
box((10.2, 22, 0.3), (0, 0.5, HZ + 1.0), PLAST, 0)                           # ceiling
for i in range(-3, 4):
    for j in range(-6, 8): box((1.1, 1.1, 0.1), (i * 1.35, j * 1.5, HZ + 0.82), GLD if (i + j) % 2 else PLAST, 0.01)   # coffers
# back wall + golden torana behind the throne
box((12, 0.6, HZ + 1.2), (0, 11.2, (HZ + 1.2) / 2), PLAST, 0.03)
for sx in (-1, 1):
    for k in range(3): box((0.9, 0.2, 1.6), (sx * (2.3 + k * 1.3), 10.85, 3.0), S('niche', (0.55, 0.45, 0.35), 0.8), 0.02); ball(0.22, (sx * (2.3 + k * 1.3), 10.75, 3.0), PLAST, (0.8, 0.5, 1.4), 16)
bpy.ops.mesh.primitive_torus_add(major_radius=1.9, minor_radius=0.12, location=(0, 10.85, 3.2), rotation=(math.pi / 2, 0, 0)); tor = bpy.context.object; tor.data.materials.append(GLD)
bpy.ops.object.select_all(action='DESELECT'); tor.select_set(True); bpy.context.view_layer.objects.active = tor
bpy.ops.object.mode_set(mode='EDIT'); bpy.ops.mesh.select_all(action='DESELECT'); bpy.ops.object.mode_set(mode='OBJECT')
for v in tor.data.vertices: v.select = v.co.y < -0.25     # local y below centre -> lower half (rotated torus)
bpy.ops.object.mode_set(mode='EDIT'); bpy.ops.mesh.delete(type='VERT'); bpy.ops.object.mode_set(mode='OBJECT')
for k in range(15): a = math.pi * k / 14; ball(0.09, (1.9 * math.cos(a), 10.7, 3.2 + 1.9 * math.sin(a)), GLD, (1, 1, 1), 12)
ball(0.35, (0, 10.7, 5.25), GLD, (1, 0.6, 1.1), 24)                          # kirtimukha boss
# dais steps
for k, (w, d, h) in enumerate(((9.0, 5.6, 0.2), (8.0, 4.8, 0.4), (7.0, 4.0, 0.6))):
    box((w, d, 0.2), (0, 8.5 + k * 0.4, h - 0.1), STONE, 0.03)
DZ = 0.6
# carpet runner
bpy.ops.mesh.primitive_grid_add(x_subdivisions=4, y_subdivisions=40, size=1); cp = bpy.context.object; cp.scale = (2.2, 16, 1); cp.location = (0, -1.5, 0.006)
bpy.ops.object.transform_apply(scale=True); cp.data.materials.append(REDC)
# throne (simhasana)
TX, TY = 0.7, 9.3
box((1.3, 0.9, 0.5), (TX, TY, DZ + 0.25), GLD, 0.04); box((1.15, 0.8, 0.12), (TX, TY - 0.02, DZ + 0.56), RED, 0.04)
box((1.3, 0.18, 1.5), (TX, TY + 0.45, DZ + 1.25), GLD, 0.05); box((1.0, 0.06, 1.2), (TX, TY + 0.35, DZ + 1.2), RED, 0.03)
bpy.ops.mesh.primitive_torus_add(major_radius=0.62, minor_radius=0.06, location=(TX, TY + 0.47, DZ + 2.0), rotation=(math.pi / 2, 0, 0)); bpy.context.object.data.materials.append(GLD)
ball(0.14, (TX, TY + 0.44, DZ + 2.62), GLD, (1, 0.6, 1.2), 16); ball(0.07, (TX, TY + 0.36, DZ + 2.62), S('k_ruby2', (0.6, 0.01, 0.03), 0.05), (1, 0.6, 1.2), 12)
for sx in (-1, 1):   # lion armrests
    x = TX + sx * 0.62; box((0.14, 0.8, 0.35), (x, TY, DZ + 0.72), GLD, 0.03)
    ball(0.13, (x, TY - 0.45, DZ + 0.95), GLD, (0.9, 1, 1), 16); bpy.ops.mesh.primitive_torus_add(major_radius=0.13, minor_radius=0.05, location=(x, TY - 0.42, DZ + 0.95), rotation=(math.pi / 2, 0, 0)); bpy.context.object.data.materials.append(GLD)
    for e in (-1, 1): ball(0.018, (x + e * 0.045, TY - 0.57, DZ + 1.0), S('lion_eye', (0.05, 0.02, 0.01), 0.3), (1, 1, 1), 8)
    for fy in (-0.35, 0.35): cylr(0.06, 0.5, (x, TY + fy, DZ + 0.25), GLD)
box((0.9, 0.5, 0.15), (TX, TY - 0.7, DZ + 0.075), RED, 0.03)    # footstool
# queen's throne
QX = -1.0
box((1.0, 0.8, 0.45), (QX, TY, DZ + 0.225), GLD, 0.04); box((0.9, 0.7, 0.1), (QX, TY - 0.02, DZ + 0.5), RED, 0.03); box((1.0, 0.15, 1.1), (QX, TY + 0.4, DZ + 1.0), GLD, 0.04)
ball(0.1, (QX, TY + 0.38, DZ + 1.62), GLD, (1, 0.6, 1.2), 16)
# chatra (royal umbrella) over the king
cylr(0.03, 3.0, (TX + 0.9, TY + 0.2, DZ + 1.5), GLD)
lathe('chatra', [(1.1, 0.0), (1.0, 0.12), (0.7, 0.3), (0.35, 0.42), (0.0, 0.48)], WHITE, (TX + 0.15, TY - 0.1, DZ + 2.95))
bpy.ops.mesh.primitive_torus_add(major_radius=1.1, minor_radius=0.03, location=(TX + 0.15, TY - 0.1, DZ + 2.95)); bpy.context.object.data.materials.append(GLD)
for k in range(28): a = k * 2 * math.pi / 28; cylr(0.012, 0.18, (TX + 0.15 + 1.1 * math.cos(a), TY - 0.1 + 1.1 * math.sin(a), DZ + 2.86), GLD, v=6)
ball(0.08, (TX + 0.15, TY - 0.1, DZ + 3.47), GLD, (1, 1, 1.4), 12)
# deepa stands + flames + warm lights
for x, y in ((-3.2, 7.2), (3.2, 7.2), (-3.2, 3.0), (3.2, 3.0), (-2.5, 10.4), (2.7, 10.4)):
    z0 = DZ if y > 6 else 0
    lathe('deepa', [(0.25, 0), (0.22, 0.05), (0.06, 0.15), (0.04, 0.4), (0.07, 0.45), (0.035, 0.5), (0.035, 1.2), (0.09, 1.25), (0.22, 1.33), (0.24, 1.38)], GLD, (x, y, z0))
    for k in range(5): a = k * 2 * math.pi / 5; ball(0.025, (x + 0.19 * math.cos(a), y + 0.19 * math.sin(a), z0 + 1.43), FLAME, (0.7, 0.7, 1.6), 8)
    bpy.ops.object.light_add(type='POINT', location=(x, y, z0 + 1.55)); L = bpy.context.object; L.data.energy = 120; L.data.color = (1.0, 0.6, 0.3); L.data.shadow_soft_size = 0.2
# hanging banners between pillars
for sx in (-1, 1):
    for k in range(5):
        y = -5.5 + k * 3.0
        bpy.ops.mesh.primitive_grid_add(x_subdivisions=2, y_subdivisions=12, size=1); b = bpy.context.object; b.scale = (0.7, 1.6, 1); b.rotation_euler = (math.pi / 2, 0, math.pi / 2)
        b.location = (sx * 4.6, y, HZ - 1.0); bpy.ops.object.transform_apply(scale=True, rotation=True); b.data.materials.append(cloth('banner', (0.55, 0.05, 0.05), mode='edge', bw=0.05, sheen=0.4))
        b.modifiers.new('w', 'SOLIDIFY').thickness = 0.01

# ---- cast ----
C = lambda n, col, **k: cloth(n, col, **k)
SILK = C('king_silk', (0.16, 0.004, 0.012), bw=0.08); KUTT = C('king_utt', (0.95, 0.72, 0.3), mode='edge', sheen=0.4)
QS = C('queen_saree', (0.42, 0.02, 0.12), bw=0.09, sheen=0.3); QP = C('queen_pallu', (0.42, 0.02, 0.12), mode='edge', sheen=0.3); QB = C('queen_blouse', (0.6, 0.38, 0.05), bw=0)
MW = C('mantri_dhoti', (0.92, 0.9, 0.84), bw=0.05); MU = C('mantri_utt', (0.9, 0.86, 0.72), mode='edge'); MT = C('mantri_turban', (0.95, 0.93, 0.86), bw=0)
SD = C('sena_dhoti', (0.55, 0.38, 0.2), border=(0.3, 0.02, 0.02), metal_border=False); SU = C('sena_utt', (0.5, 0.03, 0.03), mode='edge'); ST = C('sena_turban', (0.55, 0.05, 0.04), bw=0)
PD = C('purohit_dhoti', (0.95, 0.5, 0.1), bw=0.06); PU = C('purohit_utt', (0.95, 0.55, 0.15), mode='edge'); JN = C('janeu', (0.95, 0.94, 0.9), bw=0, metal_border=False)
GD = C('guard_dhoti', (0.75, 0.62, 0.45), border=(0.35, 0.05, 0.05), metal_border=False); GT = C('guard_turban', (0.75, 0.45, 0.1), bw=0)
MD = [C('maid_saree%d' % i, c, bw=0.07) for i, c in enumerate([(0.05, 0.3, 0.15), (0.6, 0.25, 0.02)])]
MDP = [C('maid_pallu%d' % i, c, mode='edge') for i, c in enumerate([(0.05, 0.3, 0.15), (0.6, 0.25, 0.02)])]
CT = [C('court_utt%d' % i, c, mode='edge') for i, c in enumerate([(0.85, 0.8, 0.65), (0.2, 0.3, 0.55), (0.55, 0.3, 0.45)])]
def held(rig, wrist, objs, off=(0, 0, 0)):
    attach([merge(objs)], rig, wrist)
def chamara(x, y, z):
    s = cylr(0.012, 0.9, (x, y, z + 0.45), GLD); h = lathe('plume', [(0.0, 0), (0.06, 0.05), (0.09, 0.25), (0.05, 0.5), (0.0, 0.55)], S('yakhair', (0.95, 0.94, 0.9), 0.9, bump=0.5), (x, y, z + 0.9)); return [s, h]
ROLES = []
def do(role, fn):
    try: fn(); ROLES.append(role); print('CAST', role, 'ok')
    except Exception: traceback.print_exc(limit=4); print('CAST', role, 'FAIL')
def king():
    bm, rig, P = person(0, 0, 0, True, [('ind_kingdhoti', SILK), ('ind_uttariya_diag', KUTT), ('ind_janeu', JN)], sit=True, muscle=0.7, hair=False)
    P = seat(rig, bm, DZ + 0.62, (TX, TY - 0.12)); top, r, hd = head_info(P)
    attach([merge(kit('crown_kireetam', (top.x, top.y, top.z - 0.06 - 1.3 * 0.9), 0.9))], rig, 'head')
    necklace(bm, rig); armlets(rig); moustache(bm, rig, P); tilak(P, rig)
def queen():
    bm, rig, P = person(0, 0, 0, False, [('ind_sareeskirt', QS), ('toigo_camisole_top', QB), ('ind_pallu', QP)], sit=True)
    P = seat(rig, bm, DZ + 0.55, (QX, TY - 0.1)); top, r, hd = head_info(P)
    attach([merge(kit('crown_kireetam', (top.x, top.y, top.z - 0.05 - 1.3 * 0.6), 0.6))], rig, 'head')
    necklace(bm, rig, layers=((0.06, 0.075, 30), (0.11, 0.09, 40))); armlets(rig); tilak(P, rig)
def mantri():
    bm, rig, P = person(2.4, 6.4, math.radians(-35), True, [('ind_dhoti', MW), ('ind_uttariya_diag', MU), ('ind_janeu', JN)], age=0.75, weight=0.6, hair=False)
    turban(P, rig, MT, 'mantri'); moustache(bm, rig, P, 0.006); tilak(P, rig, (0.9, 0.9, 0.85))
    w = bone_pos(rig, 'wrist.R'); held(rig, 'wrist.R', [cylr(0.025, 0.35, (w.x, w.y - 0.05, w.z - 0.05), S('scroll', (0.85, 0.75, 0.55), 0.8), rot=(math.pi / 2, 0, 0.3))])
def senapati():
    bm, rig, P = person(-2.4, 6.2, math.radians(30), True, [('ind_kingdhoti', SD), ('ind_uttariya_diag', SU)], muscle=0.9, hair=False)
    turban(P, rig, ST, 'pagadi'); moustache(bm, rig, P, 0.01); armlets(rig)
    w = bone_pos(rig, 'wrist.L'); held(rig, 'wrist.L', kit('sword_talwar', (w.x, w.y - 0.03, w.z - 0.95), 0.95))
    fa = bone_pos(rig, 'lowerarm01.R').lerp(bone_pos(rig, 'lowerarm02.R', True), 0.5)
    attach([merge(kit('shield_dhal', (fa.x - 0.07, fa.y, fa.z - 0.8), 0.8, rot=math.pi / 2))], rig, 'lowerarm02.R')
def purohit():
    bm, rig, P = person(3.3, 4.6, math.radians(-25), True, [('ind_dhoti', PD), ('ind_uttariyam', PU), ('ind_janeu', JN)], age=0.85, weight=0.55, muscle=0.4, hair=False)
    tilak(P, rig, (0.95, 0.95, 0.9))
def guard(x, y):
    def f():
        bm, rig, P = person(x, y, 0, True, [('ind_dhoti', GD)], muscle=0.85, hair=False)
        turban(P, rig, GT, 'pagadi'); moustache(bm, rig, P)
        w = bone_pos(rig, 'wrist.L'); held(rig, 'wrist.L', kit('spear_bhala', (w.x + 0.02, w.y - 0.03, w.z - 1.0), 0.95))
        fa = bone_pos(rig, 'lowerarm01.R').lerp(bone_pos(rig, 'lowerarm02.R', True), 0.5)
        attach([merge(kit('shield_dhal', (fa.x - 0.07, fa.y, fa.z - 0.8), 0.75, rot=math.pi / 2))], rig, 'lowerarm02.R')
    return f
def maid(x, y, i):
    def f():
        bm, rig, P = person(x, y, 0, False, [('ind_sareeskirt', MD[i]), ('toigo_camisole_top', QB), ('ind_pallu', MDP[i])])
        z0 = DZ
        rig.location.z += z0; bpy.context.view_layer.update()
        w = bone_pos(rig, 'wrist.R'); held(rig, 'wrist.R', chamara(w.x, w.y - 0.03, w.z - 0.45))
    return f
def courtier(x, y, rot, i):
    def f():
        bm, rig, P = person(x, y, rot, True, [('ind_dhoti', MW), ('ind_uttariya_diag', CT[i % 3])], age=random.uniform(0.45, 0.8), hair=False)
        turban(P, rig, cloth('ct_turb%d' % i, [(0.9, 0.88, 0.8), (0.75, 0.2, 0.05), (0.2, 0.25, 0.5)][i % 3], bw=0), 'mantri' if i % 2 else 'pagadi'); moustache(bm, rig, P)
    return f
do('king', king); do('queen', queen); do('mantri', mantri); do('senapati', senapati); do('purohit', purohit)
do('guardL', guard(-3.6, 8.2)); do('guardR', guard(3.6, 8.2))
do('maidL', maid(-0.1, 10.0, 0)); do('maidR', maid(1.9, 10.0, 1))
for i, (x, y, r) in enumerate(((-3.4, 1.0, 70), (-3.3, -1.2, 80), (3.4, 0.8, -70), (3.5, -1.5, -85))): do('courtier%d' % i, courtier(x, y, math.radians(r), i))
print('ROLES', ROLES)

# ---- light & render ----
w = bpy.data.worlds.new('w'); bpy.context.scene.world = w; w.use_nodes = True
env = w.node_tree.nodes.new('ShaderNodeTexEnvironment'); env.image = bpy.data.images.load(PH + '/sky.hdr'); w.node_tree.links.new(env.outputs[0], w.node_tree.nodes['Background'].inputs[0]); w.node_tree.nodes['Background'].inputs[1].default_value = 0.6
bpy.ops.object.light_add(type='SUN', rotation=(math.radians(58), 0, math.radians(-62))); sn = bpy.context.object; sn.data.energy = 4.0; sn.data.color = (1, 0.82, 0.6); sn.data.angle = math.radians(1.2)
bpy.ops.object.light_add(type='AREA', location=(0, 4, HZ + 0.3)); a = bpy.context.object; a.data.energy = 900; a.data.size = 8; a.data.color = (1, 0.85, 0.7)
bpy.ops.object.light_add(type='AREA', location=(TX - 0.3, TY - 3.5, 3.0)); k = bpy.context.object; k.data.energy = 250; k.data.size = 2; k.rotation_euler = (math.radians(70), 0, 0); k.data.color = (1, 0.8, 0.6)
s = bpy.context.scene; s.render.engine = 'CYCLES'; s.cycles.device = 'CPU'; s.cycles.samples = int(os.environ.get('SPP', 80)); s.cycles.use_denoising = True
s.view_settings.view_transform = 'AgX'; s.view_settings.look = 'AgX - Medium High Contrast'; s.view_settings.exposure = float(os.environ.get('EV', 0.0))
os.makedirs('/opt/r3d/out', exist_ok=True)
for name, loc, tgt, lens, fd, rx, ry in (('wide', (-1.2, -9.5, 1.5), (0.2, 7.5, 2.0), 22, 16, 1080, 1920), ('king', (0.3, 6.2, 1.55), (TX, TY, 1.75), 45, 3.2, 1080, 1920),
                                         ('ministers', (-0.2, 1.8, 1.45), (0.0, 6.4, 1.5), 32, 5.0, 1920, 1080)):
    bpy.ops.object.camera_add(location=loc); cam = bpy.context.object; bpy.ops.object.empty_add(location=tgt); e = bpy.context.object
    c = cam.constraints.new('TRACK_TO'); c.target = e; c.track_axis = 'TRACK_NEGATIVE_Z'; c.up_axis = 'UP_Y'; cam.data.lens = lens
    cam.data.dof.use_dof = True; cam.data.dof.focus_distance = fd; cam.data.dof.aperture_fstop = 4
    s.camera = cam; s.render.resolution_x, s.render.resolution_y = rx, ry; s.render.resolution_percentage = int(os.environ.get('PCT', 50))
    s.render.filepath = f'/opt/r3d/out/court_{name}.png'; bpy.ops.render.render(write_still=True)
bpy.ops.wm.save_as_mainfile(filepath='/opt/r3d/out/court.blend'); print('COURT_DONE')
