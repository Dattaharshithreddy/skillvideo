# Shared helpers for king-story scenes: MPFB characters in the Indian garment library, regalia, bone attachment.
import bpy, glob, os, random, math, traceback
from mathutils import Vector, Matrix
from mathutils.bvhtree import BVHTree
bpy.ops.preferences.addon_enable(module='bl_ext.user_default.mpfb')
from bl_ext.user_default.mpfb.services.humanservice import HumanService
from bl_ext.user_default.mpfb.services.locationservice import LocationService
from bl_ext.user_default.mpfb.services.animationservice import AnimationService
UD = LocationService.get_user_data(); SD = LocationService.get_mpfb_data(); PH = '/opt/r3d/assets/ph'; KIT = '/opt/r3d/assets/kit.blend'
def find(kind, pat):
    r = []
    for root in (UD, SD): r += glob.glob(os.path.join(root, kind, '**', pat), recursive=True)
    return sorted(set(r))
SKINS = find('skins', '*.mhmat')
SK_M = [s for s in SKINS if any(k in s for k in ('middleage_asian_male', 'middleage_african_male', 'young_asian_male', 'old_darkskinned_male', 'young_african_male'))] or SKINS
SK_F = [s for s in SKINS if any(k in s.lower() for k in ('indian_female', 'middleage_asian_female', 'young_asian_female'))] or SKINS
EYES = find('eyes', '*.mhclo'); BROWS = find('eyebrows', '*.mhclo')
HAIR_F = [h for h in find('hair', '*.mhclo') if any(k in h.lower() for k in ('braid', 'bun', 'long'))] or find('hair', '*.mhclo')
HAIR_M = [h for h in find('hair', '*.mhclo') if 'short' in h.lower()] or find('hair', '*.mhclo')
POSES = find('poses', 'standing0*.bvh'); SIT = [p for p in find('poses', '*.bvh') if any(k in p for k in ('sittingdefault', 'sit01', 'sittingnatural'))]
def G(name):
    p = os.path.join(UD, 'clothes', name, name + '.mhclo')
    return p if os.path.exists(p) else (find('clothes', name + '.mhclo') or [None])[0]

def cloth(name, col, border=(1.0, 0.7, 0.25), mode='hem', bw=0.045, sheen=0.15, metal_border=True, rough=0.75):
    m = bpy.data.materials.get(name)
    if m: return m
    m = bpy.data.materials.new(name); m.use_fake_user = True; m.use_nodes = True; nt = m.node_tree; b = nt.nodes['Principled BSDF']
    b.inputs['Roughness'].default_value = rough; b.inputs['Sheen Weight'].default_value = sheen
    uv = nt.nodes.new('ShaderNodeUVMap'); sep = nt.nodes.new('ShaderNodeSeparateXYZ'); nt.links.new(uv.outputs['UV'], sep.inputs[0])
    if mode == 'hem':
        fac = nt.nodes.new('ShaderNodeMath'); fac.operation = 'LESS_THAN'; fac.inputs[1].default_value = bw; nt.links.new(sep.outputs['Y'], fac.inputs[0])
    else:
        a = nt.nodes.new('ShaderNodeMath'); a.operation = 'SUBTRACT'; a.inputs[1].default_value = 0.5; nt.links.new(sep.outputs['X'], a.inputs[0])
        ab = nt.nodes.new('ShaderNodeMath'); ab.operation = 'ABSOLUTE'; nt.links.new(a.outputs[0], ab.inputs[0])
        fac = nt.nodes.new('ShaderNodeMath'); fac.operation = 'GREATER_THAN'; fac.inputs[1].default_value = 0.5 - bw * 3; nt.links.new(ab.outputs[0], fac.inputs[0])
    mx = nt.nodes.new('ShaderNodeMix'); mx.data_type = 'RGBA'; mx.inputs['A'].default_value = (*col, 1); mx.inputs['B'].default_value = (*border, 1)
    nt.links.new(fac.outputs[0], mx.inputs['Factor']); nt.links.new(mx.outputs['Result'], b.inputs['Base Color'])
    if metal_border: nt.links.new(fac.outputs[0], b.inputs['Metallic'])
    w = nt.nodes.new('ShaderNodeTexNoise'); w.inputs['Scale'].default_value = 400; bp = nt.nodes.new('ShaderNodeBump'); bp.inputs['Strength'].default_value = 0.08
    nt.links.new(w.outputs['Fac'], bp.inputs['Height']); nt.links.new(bp.outputs['Normal'], b.inputs['Normal'])
    return m
def solid(name, col, rough=0.5, metal=0.0, emit=0.0, tex=None, tscale=1.0, bump=0.1):
    m = bpy.data.materials.get(name)
    if m: return m
    m = bpy.data.materials.new(name); m.use_fake_user = True; m.use_nodes = True; nt = m.node_tree; b = nt.nodes['Principled BSDF']
    b.inputs['Base Color'].default_value = (*col, 1); b.inputs['Roughness'].default_value = rough; b.inputs['Metallic'].default_value = metal
    if emit: b.inputs['Emission Color'].default_value = (*col, 1); b.inputs['Emission Strength'].default_value = emit
    tc = nt.nodes.new('ShaderNodeTexCoord'); mp = nt.nodes.new('ShaderNodeMapping'); mp.inputs['Scale'].default_value = (tscale,) * 3; nt.links.new(tc.outputs['Object'], mp.inputs['Vector'])
    if tex and os.path.exists(f'{PH}/{tex}_diff.jpg'):
        t = nt.nodes.new('ShaderNodeTexImage'); t.image = bpy.data.images.load(f'{PH}/{tex}_diff.jpg', check_existing=True); t.projection = 'BOX'; t.projection_blend = 0.3
        nt.links.new(mp.outputs['Vector'], t.inputs['Vector'])
        mx = nt.nodes.new('ShaderNodeMix'); mx.data_type = 'RGBA'; mx.blend_type = 'MULTIPLY'; mx.inputs['Factor'].default_value = 1
        nt.links.new(t.outputs['Color'], mx.inputs['A']); mx.inputs['B'].default_value = (*col, 1); nt.links.new(mx.outputs['Result'], b.inputs['Base Color'])
        if os.path.exists(f'{PH}/{tex}_nor.jpg'):
            n = nt.nodes.new('ShaderNodeTexImage'); n.image = bpy.data.images.load(f'{PH}/{tex}_nor.jpg', check_existing=True); n.image.colorspace_settings.name = 'Non-Color'; n.projection = 'BOX'
            nt.links.new(mp.outputs['Vector'], n.inputs['Vector']); nm = nt.nodes.new('ShaderNodeNormalMap'); nt.links.new(n.outputs['Color'], nm.inputs['Color']); nt.links.new(nm.outputs['Normal'], b.inputs['Normal'])
    elif bump:
        n = nt.nodes.new('ShaderNodeTexNoise'); n.inputs['Scale'].default_value = 60; nt.links.new(mp.outputs['Vector'], n.inputs['Vector'])
        bp = nt.nodes.new('ShaderNodeBump'); bp.inputs['Strength'].default_value = bump; nt.links.new(n.outputs['Fac'], bp.inputs['Height']); nt.links.new(bp.outputs['Normal'], b.inputs['Normal'])
    return m
GOLD = lambda: solid('k_gold2', (1.0, 0.71, 0.29), 0.25, 1.0, bump=0.05)
HAIRMAT = lambda: solid('hair_black', (0.02, 0.015, 0.012), 0.45)

def tint_skin(bm, col):
    seen = set()
    def walk(nt):
        if nt is None or id(nt) in seen: return
        seen.add(id(nt))
        for n in list(nt.nodes):
            if n.type == 'GROUP': walk(n.node_tree)
            if n.type == 'TEX_IMAGE' and n.image and n.image.colorspace_settings.name == 'sRGB':
                links = [l for l in nt.links if l.from_node == n and l.from_socket.name == 'Color']
                if not links: continue
                mx = nt.nodes.new('ShaderNodeMix'); mx.data_type = 'RGBA'; mx.blend_type = 'MULTIPLY'; mx.inputs['Factor'].default_value = 1; mx.inputs['B'].default_value = (*col, 1)
                nt.links.new(n.outputs['Color'], mx.inputs['A'])
                for l in links: s = l.to_socket; nt.links.remove(l); nt.links.new(mx.outputs['Result'], s)
    for sl in bm.material_slots:
        if sl.material and sl.material.use_nodes and 'body' in sl.material.name.lower() or (sl.material and 'ears' in sl.material.name.lower()):
            walk(sl.material.node_tree)
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
def bone_pos(rig, bone, tail=False):
    pb = rig.pose.bones[bone]; return rig.matrix_world @ (pb.tail if tail else pb.head)
def pose(rig, bm, sit=False):
    lst = SIT if sit else POSES
    for pz in random.sample(lst, len(lst)):
        try: AnimationService.import_bvh_file_as_pose(rig, pz)
        except Exception: continue
        bpy.context.view_layer.update()
        if sit: return pz
        P = body_pts(bm); cx = sum(p.x for p in P) / len(P); cy = sum(p.y for p in P) / len(P)
        if max(((p.x - cx) ** 2 + (p.y - cy) ** 2) ** 0.5 for p in P) < 0.42: return pz
def merge(objs):
    objs = [o for o in objs if o and o.name in bpy.data.objects]
    bpy.ops.object.select_all(action='DESELECT')
    for o in objs: o.select_set(True)
    bpy.context.view_layer.objects.active = objs[0]; bpy.ops.object.convert(target='MESH')
    if len(objs) > 1: bpy.ops.object.join()
    o = bpy.context.view_layer.objects.active; bpy.ops.object.transform_apply(location=False, rotation=True, scale=True); return o
def attach(objs, rig, bone):
    bpy.context.view_layer.update(); pb = rig.pose.bones[bone]
    B = rig.matrix_world @ pb.matrix @ Matrix.Translation((0, pb.bone.length, 0))
    for o in objs:
        mw = o.matrix_world.copy(); o.parent = rig; o.parent_type = 'BONE'; o.parent_bone = bone; o.matrix_parent_inverse = B.inverted(); o.matrix_basis = mw
    bpy.context.view_layer.update()
def kit(name, at, scale=1.0, rot=None):
    with bpy.data.libraries.load(KIT, link=False) as (src, dst): dst.collections = [name]
    c = dst.collections[0]; bpy.context.scene.collection.children.link(c)
    objs = list(c.objects); base = Vector((sum(o.location.x for o in objs) / len(objs), 0, 0))
    for o in objs: o.location = (o.location - base) * scale + Vector(at); o.scale *= scale
    if rot:
        bpy.context.view_layer.update(); A = Vector(at); R = Matrix.Translation(A) @ Matrix.Rotation(rot, 4, 'Z') @ Matrix.Translation(-A)
        for o in objs: o.matrix_world = R @ o.matrix_world
    return objs
def head_info(P):
    H = max(q.z for q in P); nk = [p for p in P if 0.86 * H < p.z < 0.89 * H] or P
    nx = sum(p.x for p in nk) / len(nk); ny = sum(p.y for p in nk) / len(nk)
    hd = [p for p in P if (p.x - nx) ** 2 + (p.y - ny) ** 2 < 0.15 ** 2 and p.z > 0.89 * H]
    top = Vector(((min(p.x for p in hd) + max(p.x for p in hd)) / 2, (min(p.y for p in hd) + max(p.y for p in hd)) / 2, max(p.z for p in hd)))
    return top, (max(p.x for p in hd) - min(p.x for p in hd)) / 2, hd
def surface(bm):
    dg = bpy.context.evaluated_depsgraph_get(); ev = bm.evaluated_get(dg); bvh = BVHTree.FromObject(ev, dg); M = bm.matrix_world; Mi = M.inverted(); N = M.to_3x3()
    def near(p):
        loc, nrm, i, d = bvh.find_nearest(Mi @ p)
        return (M @ loc, (N @ nrm).normalized()) if loc is not None else (p, Vector((0, -1, 0)))
    return near
def ball(r, p, m, sc=(1, 1, 1), seg=12):
    bpy.ops.mesh.primitive_uv_sphere_add(radius=r, location=p, segments=seg, ring_count=max(6, seg // 2)); o = bpy.context.object; o.scale = sc; o.data.materials.append(m); bpy.ops.object.shade_smooth(); return o
def necklace(bm, rig, layers=((0.07, 0.085, 36), (0.13, 0.1, 44)), gem=None):
    near = surface(bm); n0 = bone_pos(rig, 'neck01'); out = []; gold = GOLD(); pearl = solid('k_pearl2', (0.95, 0.92, 0.86), 0.2); gem = gem or solid('k_ruby2', (0.6, 0.01, 0.03), 0.05)
    fw = (bone_pos(rig, 'spine01', True) - bone_pos(rig, 'spine05')).cross(bone_pos(rig, 'clavicle.L') - bone_pos(rig, 'clavicle.R')).normalized()   # character's front
    rt = (bone_pos(rig, 'clavicle.R') - bone_pos(rig, 'clavicle.L')).normalized()
    for s, (drop, rad, nb) in enumerate(layers):
        strand = []
        for k in range(nb + 1):
            a = math.pi * k / nb
            p = n0 + rt * (rad * 1.2 * math.cos(a)) + fw * (rad * math.sin(a)) - Vector((0, 0, 0.01 + drop * math.sin(a) ** 2))
            loc, nrm = near(p); strand.append(ball(0.006 + 0.001 * s, loc + nrm * 0.007, gold if k % 3 else pearl))
        out += strand
        if s == len(layers) - 1:
            lo = min(strand, key=lambda o: o.location.z).location
            out.append(ball(0.022, lo + fw * 0.008 - Vector((0, 0, 0.025)), gold, (1, 0.45, 1.3))); out.append(ball(0.013, lo + fw * 0.016 - Vector((0, 0, 0.025)), gem, (1, 0.6, 1.2)))
    m = merge(out); attach([m], rig, 'spine01'); return m
def armlets(rig):
    for side in ('L', 'R'):
        a, b = bone_pos(rig, f'upperarm01.{side}'), bone_pos(rig, f'upperarm02.{side}', True)
        bpy.ops.mesh.primitive_torus_add(major_radius=0.05, minor_radius=0.009, location=a.lerp(b, 0.55)); o = bpy.context.object; o.data.materials.append(GOLD())
        o.rotation_mode = 'QUATERNION'; o.rotation_quaternion = Vector((0, 0, 1)).rotation_difference((b - a).normalized()); attach([o], rig, f'upperarm02.{side}')
def turban(P, rig, m, style='pagadi'):
    c, r, hd = head_info(P); parts = []
    if style == 'pagadi':
        for k in range(5):
            bpy.ops.mesh.primitive_torus_add(major_radius=(r + 0.012) * (1 - k * 0.09), minor_radius=0.02, location=(c.x, c.y, c.z - 0.085 + k * 0.024), rotation=(random.uniform(-0.15, 0.15), random.uniform(-0.15, 0.15), 0))
            o = bpy.context.object; o.scale = (1, 1.12, 1); parts.append(o)
        parts.append(ball(r * 0.78, (c.x, c.y, c.z - 0.01), m, (1, 1.12, 0.55), 24))
    else:   # mantri: tall, flat-topped, cloth-wrapped with a gold band and jewel
        for k in range(7):
            bpy.ops.mesh.primitive_torus_add(major_radius=(r + 0.016) * (1 + k * 0.025), minor_radius=0.019, location=(c.x, c.y, c.z - 0.09 + k * 0.026), rotation=(0.12 * (-1) ** k, 0.08 * (-1) ** (k + 1), 0))
            o = bpy.context.object; o.scale = (1, 1.12, 1); parts.append(o)
        bpy.ops.mesh.primitive_cylinder_add(radius=(r + 0.02) * 1.15, depth=0.02, location=(c.x, c.y, c.z + 0.095)); o = bpy.context.object; o.scale = (1, 1.12, 1); parts.append(o)
    for o in parts:
        if not o.data.materials: o.data.materials.append(m)
        bpy.ops.object.select_all(action='DESELECT'); o.select_set(True); bpy.context.view_layer.objects.active = o; bpy.ops.object.shade_smooth()
    t = merge(parts)
    if style != 'pagadi':
        front = min(hd, key=lambda p: p.y); attach([t, ball(0.016, (c.x, front.y - 0.03, c.z - 0.02), solid('k_emer2', (0.0, 0.35, 0.12), 0.05), (1, 0.6, 1.3))], rig, 'head')
    else: attach([t], rig, 'head')
def moustache(bm, rig, P, thick=0.008):
    c, r, hd = head_info(P); near = surface(bm)
    z = c.z - 0.155; front = min([p for p in hd if abs(p.z - z) < 0.02] or hd, key=lambda p: p.y)
    objs = []
    for sx in (-1, 1):
        bpy.ops.curve.primitive_bezier_curve_add(); cu = bpy.context.object; sp = cu.data.splines[0]; sp.bezier_points.add(1)
        pts = [Vector((front.x + sx * 0.004, front.y - 0.004, z)), Vector((front.x + sx * 0.03, front.y + 0.008, z - 0.012)), Vector((front.x + sx * 0.05, front.y + 0.02, z + 0.006))]
        for bp, p in zip(sp.bezier_points, pts):
            loc, nrm = near(p); bp.co = cu.matrix_world.inverted() @ (loc + nrm * 0.004); bp.handle_left_type = bp.handle_right_type = 'AUTO'
        sp.bezier_points[0].radius = 1.0; sp.bezier_points[1].radius = 0.9; sp.bezier_points[2].radius = 0.2
        cu.data.bevel_depth = thick; cu.data.bevel_resolution = 3; cu.data.materials.append(HAIRMAT()); objs.append(cu)
    attach([merge(objs)], rig, 'head')
def tilak(P, rig, col=(0.8, 0.05, 0.02)):
    c, r, hd = head_info(P); z = c.z - 0.06; front = min([p for p in hd if abs(p.z - z) < 0.015] or hd, key=lambda p: p.y)
    attach([ball(0.006, (front.x, front.y - 0.002, z), solid('tilak', col, 0.6), (0.6, 0.3, 2.2))], rig, 'head')

def person(x, y, rot, male, outfit, sit=False, age=0.5, muscle=0.6, weight=0.5, hair=True, skin=None):
    macro = {'gender': 1.0 if male else 0.0, 'age': age, 'muscle': muscle if male else 0.45, 'weight': weight, 'height': 0.55 if male else 0.45, 'proportions': 0.6,
             'cupsize': 0.5, 'firmness': 0.5, 'race': {'african': 0.3, 'asian': 0.5, 'caucasian': 0.2}}
    bm = HumanService.create_human(mask_helpers=True, feet_on_ground=True, scale=0.1, macro_detail_dict=macro)
    HumanService.set_character_skin(skin or random.choice(SK_M if male else SK_F), bm, skin_type='ENHANCED_SSS')
    tint_skin(bm, (0.74, 0.52, 0.38) if male else (0.84, 0.62, 0.48))
    rig = HumanService.add_builtin_rig(bm, 'default')
    add(EYES[0], bm, 'Eyes'); add(BROWS[0], bm, 'Eyebrows')
    if hair: add(random.choice(HAIR_M if male else HAIR_F), bm, 'Hair')
    for g, m in outfit: add(G(g), bm, 'Clothes', m)
    pz = pose(rig, bm, sit)
    rig.rotation_euler[2] = rot; rig.location = (x, y, 0); bpy.context.view_layer.update()
    return bm, rig, body_pts(bm)
def seat(rig, bm, seat_z, at_xy):
    """Move a seated character so the pelvis rests on a seat top at seat_z, centred at at_xy."""
    p = (bone_pos(rig, 'pelvis.L') + bone_pos(rig, 'pelvis.R')) / 2
    rig.location += Vector((at_xy[0] - p.x, at_xy[1] - p.y, seat_z + 0.09 - p.z)); bpy.context.view_layer.update(); return body_pts(bm)
