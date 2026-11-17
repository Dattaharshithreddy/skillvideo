# Costume check: villager, woman, soldier, king, queen in the draped garment library + kit props.
import bpy, glob, os, random, math, traceback
from mathutils import Vector
bpy.ops.preferences.addon_enable(module='bl_ext.user_default.mpfb')
from bl_ext.user_default.mpfb.services.humanservice import HumanService
from bl_ext.user_default.mpfb.services.locationservice import LocationService
from bl_ext.user_default.mpfb.services.animationservice import AnimationService
UD = LocationService.get_user_data(); SD = LocationService.get_mpfb_data(); PH = '/opt/r3d/assets/ph'
def find(kind, pat):
    r = []
    for root in (UD, SD): r += glob.glob(os.path.join(root, kind, '**', pat), recursive=True)
    return sorted(set(r))
for o in list(bpy.data.objects): bpy.data.objects.remove(o)
random.seed(11)
skins = find('skins', '*.mhmat')
SK_M = [s for s in skins if 'indian' in s.lower() or 'middleage_asian_male' in s or 'middleage_african_male' in s] or skins
SK_F = [s for s in skins if 'indian_female' in s.lower() or 'middleage_asian_female' in s] or skins
eyes = find('eyes', '*.mhclo'); brows = find('eyebrows', '*.mhclo')
hair_f = [h for h in find('hair', '*.mhclo') if any(k in h.lower() for k in ('braid', 'bun', 'long'))] or find('hair', '*.mhclo')
POSES = find('poses', 'standing0*.bvh')
G = lambda n: (find('clothes', n + '.mhclo') or [None])[0]
TOP = G('toigo_camisole_top') or G('toigo_bodice-style_top')

def cloth(name, col, border=(1.0, 0.7, 0.25), mode='hem', bw=0.045, sheen=0.3, metal_border=True):
    m = bpy.data.materials.new(name); m.use_fake_user = True; m.use_nodes = True; nt = m.node_tree; b = nt.nodes['Principled BSDF']
    b.inputs['Roughness'].default_value = 0.75; b.inputs['Sheen Weight'].default_value = sheen
    uv = nt.nodes.new('ShaderNodeUVMap'); sep = nt.nodes.new('ShaderNodeSeparateXYZ'); nt.links.new(uv.outputs['UV'], sep.inputs[0])
    if mode == 'hem':
        lt = nt.nodes.new('ShaderNodeMath'); lt.operation = 'LESS_THAN'; lt.inputs[1].default_value = bw; nt.links.new(sep.outputs['Y'], lt.inputs[0]); fac = lt
    else:   # long edges of a strip
        a = nt.nodes.new('ShaderNodeMath'); a.operation = 'SUBTRACT'; a.inputs[1].default_value = 0.5; nt.links.new(sep.outputs['X'], a.inputs[0])
        ab = nt.nodes.new('ShaderNodeMath'); ab.operation = 'ABSOLUTE'; nt.links.new(a.outputs[0], ab.inputs[0])
        fac = nt.nodes.new('ShaderNodeMath'); fac.operation = 'GREATER_THAN'; fac.inputs[1].default_value = 0.5 - bw * 3; nt.links.new(ab.outputs[0], fac.inputs[0])
    weave = nt.nodes.new('ShaderNodeTexNoise'); weave.inputs['Scale'].default_value = 400
    mx = nt.nodes.new('ShaderNodeMix'); mx.data_type = 'RGBA'; mx.inputs['A'].default_value = (*col, 1); mx.inputs['B'].default_value = (*border, 1)
    nt.links.new(fac.outputs[0], mx.inputs['Factor']); nt.links.new(mx.outputs['Result'], b.inputs['Base Color'])
    if metal_border: nt.links.new(fac.outputs[0], b.inputs['Metallic'])
    bp = nt.nodes.new('ShaderNodeBump'); bp.inputs['Strength'].default_value = 0.08; nt.links.new(weave.outputs['Fac'], bp.inputs['Height']); nt.links.new(bp.outputs['Normal'], b.inputs['Normal'])
    return m
COTTON = cloth('cotton', (0.88, 0.86, 0.8)); SILK_R = cloth('silk_red', (0.5, 0.02, 0.05), bw=0.08, sheen=0.8)
SAREE_G = cloth('saree_green', (0.05, 0.32, 0.12), bw=0.07, sheen=0.7); SAREE_GP = cloth('pallu_green', (0.05, 0.32, 0.12), mode='edge', sheen=0.7)
SAREE_M = cloth('saree_maroon', (0.42, 0.02, 0.12), bw=0.08, sheen=0.8); SAREE_MP = cloth('pallu_maroon', (0.42, 0.02, 0.12), mode='edge', sheen=0.8)
UTT = cloth('utt_cream', (0.9, 0.85, 0.7), mode='edge'); UTT_K = cloth('utt_gold', (0.95, 0.75, 0.35), mode='edge', sheen=0.8)
BLOUSE = cloth('blouse', (0.65, 0.4, 0.05), bw=0.0); SOLD = cloth('soldier_dhoti', (0.75, 0.6, 0.45), border=(0.4, 0.05, 0.05), metal_border=False)
TURB = cloth('turban_red', (0.7, 0.07, 0.05), bw=0.0)

def body_pts(bm):
    dg = bpy.context.evaluated_depsgraph_get(); ev = bm.evaluated_get(dg); me = ev.to_mesh(); vg = bm.vertex_groups['body'].index; M = bm.matrix_world
    p = [M @ v.co for v in me.vertices if any(g.group == vg and g.weight > 0.5 for g in v.groups)]; ev.to_mesh_clear(); return p
def add(path, bm, typ='Clothes', mat=None):
    if not path: print('MISSING', typ); return []
    before = set(bpy.data.objects)
    try: HumanService.add_mhclo_asset(path, bm, asset_type=typ, subdiv_levels=1 if typ == 'Clothes' else 0, material_type='MAKESKIN')
    except Exception: traceback.print_exc(limit=2); return []
    new = [o for o in bpy.data.objects if o not in before and o.type == 'MESH']
    for o in new:
        if mat: o.data.materials.clear(); o.data.materials.append(mat)
    return new
def pose_ok(rig, bm):
    for pz in random.sample(POSES, len(POSES)):
        try: AnimationService.import_bvh_file_as_pose(rig, pz)
        except Exception: continue
        bpy.context.view_layer.update(); P = body_pts(bm); cx = sum(p.x for p in P) / len(P); cy = sum(p.y for p in P) / len(P)
        if max(((p.x - cx) ** 2 + (p.y - cy) ** 2) ** 0.5 for p in P) < 0.42: return
def person(x, y, male, outfit):
    macro = {'gender': 1.0 if male else 0.0, 'age': 0.5, 'muscle': 0.62 if male else 0.45, 'weight': 0.5, 'height': 0.55 if male else 0.45, 'proportions': 0.6, 'cupsize': 0.5, 'firmness': 0.5,
             'race': {'african': 0.3, 'asian': 0.5, 'caucasian': 0.2}}
    bm = HumanService.create_human(mask_helpers=True, feet_on_ground=True, scale=0.1, macro_detail_dict=macro)
    HumanService.set_character_skin(random.choice(SK_M if male else SK_F), bm, skin_type='ENHANCED_SSS')
    rig = HumanService.add_builtin_rig(bm, 'default')
    add(eyes[0], bm, 'Eyes'); add(brows[0], bm, 'Eyebrows')
    if not male: add(random.choice(hair_f), bm, 'Hair')
    for g, m in outfit: add(G(g) if not g.endswith('.mhclo') else g, bm, 'Clothes', m)
    if not male: add(TOP, bm, 'Clothes', BLOUSE)
    pose_ok(rig, bm)
    rig.location = (x, y, 0); bpy.context.view_layer.update(); return bm, body_pts(bm)
def head_top(P):
    nk = [p for p in P if 0.86 * max(q.z for q in P) < p.z < 0.89 * max(q.z for q in P)]
    nx = sum(p.x for p in nk) / len(nk); ny = sum(p.y for p in nk) / len(nk)
    hd = [p for p in P if (p.x - nx) ** 2 + (p.y - ny) ** 2 < 0.15 ** 2 and p.z > nk[0].z]
    return Vector(((min(p.x for p in hd) + max(p.x for p in hd)) / 2, (min(p.y for p in hd) + max(p.y for p in hd)) / 2, max(p.z for p in hd))), (max(p.x for p in hd) - min(p.x for p in hd)) / 2
def turban(P, m):
    c, r = head_top(P)
    for k in range(5):
        bpy.ops.mesh.primitive_torus_add(major_radius=(r + 0.012) * (1 - k * 0.09), minor_radius=0.02, location=(c.x, c.y, c.z - 0.085 + k * 0.024), rotation=(random.uniform(-0.15, 0.15), random.uniform(-0.15, 0.15), 0))
        o = bpy.context.object; o.scale = (1, 1.12, 1); o.data.materials.append(m); bpy.ops.object.shade_smooth()
    bpy.ops.mesh.primitive_uv_sphere_add(radius=r * 0.78, location=(c.x, c.y, c.z - 0.01)); o = bpy.context.object; o.scale = (1, 1.12, 0.55); o.data.materials.append(m); bpy.ops.object.shade_smooth()
def kit(name, at, scale=1.0, rot=None, zero_to_origin=True):
    with bpy.data.libraries.load('/opt/r3d/assets/kit.blend', link=False) as (src, dst): dst.collections = [name]
    c = dst.collections[0]; bpy.context.scene.collection.children.link(c)
    objs = [o for o in c.objects]; mn = Vector((min(o.location.x for o in objs), 0, 0))
    for o in objs:
        o.location = (o.location - Vector((sum(q.location.x for q in objs) / len(objs), 0, 0))) * scale + Vector(at); o.scale *= scale
        if rot: o.rotation_euler.rotate_axis('Z', rot)
    return objs

KD = os.path.join(UD, 'clothes')
cast = [(-1.6, 0.3, True, [('ind_dhoti', COTTON), ('ind_uttariyam', UTT)], 'villager'),
        (-0.8, 0.0, False, [('ind_sareeskirt', SAREE_G), ('ind_pallu', SAREE_GP)], 'woman'),
        (0.0, -0.2, True, [('ind_kingdhoti', SILK_R), ('ind_uttariyam', UTT_K)], 'king'),
        (0.8, 0.0, False, [('ind_sareeskirt', SAREE_M), ('ind_pallu', SAREE_MP)], 'queen'),
        (1.65, 0.3, True, [('ind_dhoti', SOLD)], 'soldier')]
for x, y, male, outfit, role in cast:
    try:
        bm, P = person(x, y, male, [(os.path.join(KD, g, g + '.mhclo'), m) for g, m in outfit])
        top, r = head_top(P); H = max(p.z for p in P)
        if role == 'villager': turban(P, TURB)
        if role == 'king': kit('crown_kireetam', (top.x, top.y, top.z - 0.07 - 1.3 * 0.95), 0.95); kit('royal_jewellery', (x, y + 0.02, H * 0.81 - 1.45 * 0.9 + 0.0), 0.9)
        if role == 'queen': kit('crown_kireetam', (top.x, top.y, top.z - 0.06 - 1.3 * 0.6), 0.6)
        if role == 'soldier':
            turban(P, cloth('turb_s', (0.5, 0.35, 0.2), bw=0.0)); kit('shield_dhal', (x - 0.32, y - 0.15, H * 0.55 - 1.0 * 0.9), 0.9)
            kit('spear_bhala', (x + 0.38, y + 0.05, 0), 0.95)
        print('CAST', role, 'ok')
    except Exception: traceback.print_exc(limit=3)
kit('banner_flag', (-2.6, 1.6, 0), 1.0); kit('war_drum_nagara', (2.6, 0.9, 0), 1.0)
# set: paving + HDRI + warm key
bpy.ops.mesh.primitive_plane_add(size=80); g = bpy.context.object
gm = bpy.data.materials.new('gr'); gm.use_nodes = True; nt = gm.node_tree; b = nt.nodes['Principled BSDF']
if os.path.exists(PH + '/ground_diff.jpg'):
    t = nt.nodes.new('ShaderNodeTexImage'); t.image = bpy.data.images.load(PH + '/ground_diff.jpg'); tc = nt.nodes.new('ShaderNodeTexCoord'); mp = nt.nodes.new('ShaderNodeMapping'); mp.inputs['Scale'].default_value = (0.35, 0.35, 0.35)
    nt.links.new(tc.outputs['Object'], mp.inputs['Vector']); nt.links.new(mp.outputs['Vector'], t.inputs['Vector']); nt.links.new(t.outputs['Color'], b.inputs['Base Color'])
g.data.materials.append(gm)
w = bpy.data.worlds.new('w'); bpy.context.scene.world = w; w.use_nodes = True
env = w.node_tree.nodes.new('ShaderNodeTexEnvironment'); env.image = bpy.data.images.load(PH + '/sky.hdr'); w.node_tree.links.new(env.outputs[0], w.node_tree.nodes['Background'].inputs[0]); w.node_tree.nodes['Background'].inputs[1].default_value = 0.8
bpy.ops.object.light_add(type='SUN', rotation=(math.radians(55), 0, math.radians(-30))); sun = bpy.context.object; sun.data.energy = 3.5; sun.data.color = (1, 0.85, 0.66)
bpy.ops.object.light_add(type='AREA', location=(0, -4, 3)); f = bpy.context.object; f.data.energy = 300; f.data.size = 4; f.rotation_euler = (math.radians(60), 0, 0)
s = bpy.context.scene; s.render.engine = 'CYCLES'; s.cycles.device = 'CPU'; s.cycles.samples = int(os.environ.get('SPP', 96)); s.cycles.use_denoising = True
s.view_settings.view_transform = 'AgX'; s.view_settings.look = 'AgX - Medium High Contrast'; s.view_settings.exposure = -0.2
for name, loc, tgt, lens, rx, ry in (('cast', (0, -6.2, 1.15), (0, 0, 0.95), 35, 1920, 1080), ('king', (0.15, -2.4, 1.45), (0, -0.2, 1.3), 50, 1080, 1920)):
    bpy.ops.object.camera_add(location=loc); cam = bpy.context.object; bpy.ops.object.empty_add(location=tgt); e = bpy.context.object
    k = cam.constraints.new('TRACK_TO'); k.target = e; k.track_axis = 'TRACK_NEGATIVE_Z'; k.up_axis = 'UP_Y'; cam.data.lens = lens
    s.camera = cam; s.render.resolution_x, s.render.resolution_y = rx, ry; s.render.resolution_percentage = int(os.environ.get('PCT', 50))
    s.render.filepath = f'/opt/r3d/out/costume_{name}.png'; bpy.ops.render.render(write_still=True)
bpy.ops.wm.save_as_mainfile(filepath='/opt/r3d/out/costume_test.blend'); print('COSTUME_DONE')
