# v2: body-fitted dhoti/saree/angavastram/turban + carved gopuram, two cameras (wide + close)
import bpy, bmesh, glob, os, random, math, traceback
from mathutils import Vector
bpy.ops.preferences.addon_enable(module='bl_ext.user_default.mpfb')
from bl_ext.user_default.mpfb.services.humanservice import HumanService
from bl_ext.user_default.mpfb.services.locationservice import LocationService
UD = LocationService.get_user_data(); SD = LocationService.get_mpfb_data()
def find(kind, pat):
    r = []
    for root in (UD, SD): r += glob.glob(os.path.join(root, kind, '**', pat), recursive=True)
    return sorted(set(r))
allskins = find('skins', '*.mhmat')
skins_m = [s for s in allskins if ('indian' in s.lower() or 'middleage_african_male' in s or 'middleage_asian_male' in s or 'young_african_male' in s or 'young_asian_male' in s)]
skins_f = [s for s in allskins if ('indian_female' in s.lower() or 'middleage_african_female' in s or 'middleage_asian_female' in s or 'young_asian_female' in s or 'young_african_female' in s)]
skins_m = skins_m or allskins; skins_f = skins_f or allskins
eyes = find('eyes', '*.mhclo'); brows = find('eyebrows', '*.mhclo')
hair_f = [h for h in find('hair', '*.mhclo') if any(k in h.lower() for k in ('long', 'braid', 'bun', 'ponytail'))] or find('hair', '*.mhclo')
hair_m = [h for h in find('hair', '*.mhclo') if 'short' in h.lower()]
print('SK', len(skins_m), len(skins_f), 'HAIRF', len(hair_f))
for o in list(bpy.data.objects): bpy.data.objects.remove(o)
random.seed(7)

def nmat(name, col, rough=0.8, metal=0.0, bump=0.0, scale=40.0, var=0.0):
    m = bpy.data.materials.new(name); m.use_fake_user = True; m.use_nodes = True
    nt = m.node_tree; b = nt.nodes['Principled BSDF']
    b.inputs['Base Color'].default_value = (*col, 1); b.inputs['Roughness'].default_value = rough; b.inputs['Metallic'].default_value = metal
    if bump or var:
        tc = nt.nodes.new('ShaderNodeTexCoord'); n = nt.nodes.new('ShaderNodeTexNoise'); n.inputs['Scale'].default_value = scale; n.inputs['Detail'].default_value = 8
        nt.links.new(tc.outputs['Object'], n.inputs['Vector'])
        if bump:
            bp = nt.nodes.new('ShaderNodeBump'); bp.inputs['Strength'].default_value = bump
            nt.links.new(n.outputs['Fac'], bp.inputs['Height']); nt.links.new(bp.outputs['Normal'], b.inputs['Normal'])
        if var:
            mx = nt.nodes.new('ShaderNodeMix'); mx.data_type = 'RGBA'; mx.inputs['Factor'].default_value = var
            n2 = nt.nodes.new('ShaderNodeTexNoise'); n2.inputs['Scale'].default_value = scale / 20
            nt.links.new(tc.outputs['Object'], n2.inputs['Vector']); nt.links.new(n2.outputs['Fac'], mx.inputs['Factor'])
            mx.inputs['A'].default_value = (*col, 1); mx.inputs['B'].default_value = tuple(c * 0.6 for c in col) + (1,)
            nt.links.new(mx.outputs['Result'], b.inputs['Base Color'])
    return m
COTTON = nmat('cotton', (0.86, 0.84, 0.78), 0.92, bump=0.15, scale=120)
BORDER = nmat('zari', (0.85, 0.6, 0.18), 0.35, 0.8)
SAREES = [nmat(f'saree{i}', c, 0.6, bump=0.08, scale=150) for i, c in enumerate([(0.7, 0.05, 0.12), (0.95, 0.45, 0.05), (0.1, 0.35, 0.15), (0.45, 0.05, 0.4), (0.9, 0.75, 0.1)])]
BLOUSE = [nmat(f'bl{i}', c, 0.7) for i, c in enumerate([(0.1, 0.15, 0.5), (0.6, 0.05, 0.05), (0.15, 0.4, 0.1)])]
TURBANS = [nmat(f'tb{i}', c, 0.85, bump=0.2, scale=60) for i, c in enumerate([(0.86, 0.84, 0.78), (0.8, 0.3, 0.05), (0.7, 0.08, 0.06)])]
STONE = nmat('stone', (0.66, 0.58, 0.47), 0.9, bump=0.6, scale=6, var=0.35)
PLASTER = nmat('plaster', (0.78, 0.72, 0.6), 0.85, bump=0.3, scale=10, var=0.25)
GOLD = nmat('gold', (1.0, 0.7, 0.25), 0.22, 1.0)
GROUND = nmat('ground', (0.42, 0.36, 0.28), 0.95, bump=0.15, scale=2, var=0.2)

PH = '/opt/r3d/assets/ph'
def texify(m, role, scale, tint=None):
    d = f'{PH}/{role}_diff.jpg'
    if not os.path.exists(d): print('NOTEX', role); return
    nt = m.node_tree; b = nt.nodes['Principled BSDF']
    for l in list(b.inputs['Base Color'].links) + list(b.inputs['Normal'].links): nt.links.remove(l)
    tc = nt.nodes.new('ShaderNodeTexCoord'); mp = nt.nodes.new('ShaderNodeMapping'); mp.inputs['Scale'].default_value = (scale, scale, scale)
    nt.links.new(tc.outputs['Object'], mp.inputs['Vector'])
    def img(path, non_color):
        n = nt.nodes.new('ShaderNodeTexImage'); n.image = bpy.data.images.load(path); n.projection = 'BOX'; n.projection_blend = 0.25
        if non_color: n.image.colorspace_settings.name = 'Non-Color'
        nt.links.new(mp.outputs['Vector'], n.inputs['Vector']); return n
    di = img(d, False)
    if tint:
        mx = nt.nodes.new('ShaderNodeMix'); mx.data_type = 'RGBA'; mx.blend_type = 'MULTIPLY'; mx.inputs['Factor'].default_value = 1.0
        nt.links.new(di.outputs['Color'], mx.inputs['A']); mx.inputs['B'].default_value = (*tint, 1); nt.links.new(mx.outputs['Result'], b.inputs['Base Color'])
    else: nt.links.new(di.outputs['Color'], b.inputs['Base Color'])
    if os.path.exists(f'{PH}/{role}_rough.jpg'): nt.links.new(img(f'{PH}/{role}_rough.jpg', True).outputs['Color'], b.inputs['Roughness'])
    if os.path.exists(f'{PH}/{role}_nor.jpg'):
        nm = nt.nodes.new('ShaderNodeNormalMap'); nt.links.new(img(f'{PH}/{role}_nor.jpg', True).outputs['Color'], nm.inputs['Color']); nt.links.new(nm.outputs['Normal'], b.inputs['Normal'])
DARK = nmat('dark', (0.04, 0.03, 0.025), 0.9)
texify(GROUND, 'ground', 0.45); texify(STONE, 'stone', 0.5, (1.0, 0.92, 0.8)); texify(PLASTER, 'plaster', 0.6, (1.05, 1.0, 0.9))
WOOD = nmat('wood', (0.3, 0.18, 0.1), 0.7); texify(WOOD, 'wood', 0.8, (0.8, 0.55, 0.35))
NICHE = nmat('niche', (0.32, 0.28, 0.22), 0.9, bump=0.3, scale=10)

def body_slices(bm):
    dg = bpy.context.evaluated_depsgraph_get(); ev = bm.evaluated_get(dg); me = ev.to_mesh(); M = bm.matrix_world
    vg = bm.vertex_groups.get('body'); idx = vg.index if vg else None
    pts = []
    for v in me.vertices:
        if idx is not None and not any(g.group == idx and g.weight > 0.5 for g in v.groups): continue
        pts.append(M @ v.co)
    ev.to_mesh_clear()
    return pts
def ring_extent(pts, z0, z1):
    sel = [p for p in pts if z0 <= p.z < z1]
    if not sel: return None
    xs = [p.x for p in sel]; ys = [p.y for p in sel]
    return ((min(xs) + max(xs)) / 2, (min(ys) + max(ys)) / 2, (max(xs) - min(xs)) / 2, (max(ys) - min(ys)) / 2)
def loft(name, rings, mat, seg=32, close_top=False):
    # rings: list of (z, cx, cy, rx, ry, wobble)
    me = bpy.data.meshes.new(name); b = bmesh.new(); prev = None
    for zi, (z, cx, cy, rx, ry, wob) in enumerate(rings):
        cur = []
        for i in range(seg):
            a = 2 * math.pi * i / seg; pl = 1 + wob * math.sin(a * 9 + zi)  # pleats
            cur.append(b.verts.new((cx + rx * pl * math.cos(a), cy + ry * pl * math.sin(a), z)))
        if prev:
            for i in range(seg): b.faces.new((prev[i], prev[(i + 1) % seg], cur[(i + 1) % seg], cur[i]))
        prev = cur
    b.to_mesh(me); b.free(); o = bpy.data.objects.new(name, me); bpy.context.collection.objects.link(o)
    o.data.materials.append(mat)
    for p in o.data.polygons: p.use_smooth = True
    sd = o.modifiers.new('sub', 'SUBSURF'); sd.levels = sd.render_levels = 1
    so = o.modifiers.new('sol', 'SOLIDIFY'); so.thickness = 0.008
    return o
def garment(pts, z_top, z_bot, pad, flare, mat, wob=0.025, n=10):
    rings = []
    for k in range(n + 1):
        z = z_top + (z_bot - z_top) * k / n; e = ring_extent(pts, z - 0.03, z + 0.03)
        if not e: continue
        t = k / n; cx, cy, rx, ry = e
        # skirt: below the crotch, merge both legs into one tube
        if rings and rx < rings[-1][3] * 0.9: rx = rings[-1][3] * 0.97
        if rings and ry < rings[-1][4] * 0.9: ry = rings[-1][4] * 0.97
        if rings: cx, cy = rings[-1][1] * 0.6 + cx * 0.4, rings[-1][2] * 0.6 + cy * 0.4
        rings.append((z, cx, cy, rx + pad + flare * t, ry + pad + flare * t * 0.8, wob * t))
    return loft('cloth', rings, mat)
def sash(p0, p1, p2, width, mat):
    # curved band across chest/shoulder (angavastram / pallu): quadratic bezier strip
    me = bpy.data.meshes.new('sash'); b = bmesh.new(); prev = None
    for k in range(13):
        t = k / 12; c = (1 - t) ** 2 * p0 + 2 * (1 - t) * t * p1 + t * t * p2
        tang = (2 * (1 - t) * (p1 - p0) + 2 * t * (p2 - p1)).normalized(); side = tang.cross(Vector((0, 1, 0))).normalized() * width / 2
        cur = (b.verts.new(c - side), b.verts.new(c + side))
        if prev: b.faces.new((prev[0], prev[1], cur[1], cur[0]))
        prev = cur
    b.to_mesh(me); b.free(); o = bpy.data.objects.new('sash', me); bpy.context.collection.objects.link(o); o.data.materials.append(mat)
    so = o.modifiers.new('sol', 'SOLIDIFY'); so.thickness = 0.01; sd = o.modifiers.new('sub', 'SUBSURF'); sd.levels = sd.render_levels = 2
    return o


from bl_ext.user_default.mpfb.services.animationservice import AnimationService
POSES = find('poses', 'standing0*.bvh'); print('POSES', len(POSES))
def cl(name): 
    r = find('clothes', name + '.mhclo'); return r[0] if r else None
DHOTI = cl('toigo_harem_pants') or cl('elvs_gored_elephant_pants'); SKIRT = cl('toigo_long_full_skirt'); TOP = cl('toigo_camisole_top') or cl('toigo_bodice-style_top')
print('CLOTHES', DHOTI, SKIRT, TOP)
def recolor(obj, m):
    if obj is None or not hasattr(obj, 'data') or not hasattr(obj.data, 'materials'): return
    obj.data.materials.clear(); obj.data.materials.append(m)
def add(path, bm, typ='Clothes', mat=None):
    before = set(bpy.data.objects)
    try: HumanService.add_mhclo_asset(path, bm, asset_type=typ, subdiv_levels=1 if typ == 'Clothes' else 0, material_type='MAKESKIN')
    except Exception: traceback.print_exc(limit=1); return None
    new = [o for o in bpy.data.objects if o not in before and o.type == 'MESH']
    if mat:
        for o in new: recolor(o, mat)
    return new[0] if new else None
def person(x, y, rot, male):
    macro = {'gender': 1.0 if male else 0.0, 'age': random.uniform(0.45, 0.62), 'muscle': random.uniform(0.45, 0.7), 'weight': random.uniform(0.4, 0.65),
             'height': random.uniform(0.35, 0.6), 'proportions': 0.6, 'cupsize': 0.5, 'firmness': 0.5, 'race': {'african': 0.3, 'asian': 0.45, 'caucasian': 0.25}}
    bm = HumanService.create_human(mask_helpers=True, feet_on_ground=True, scale=0.1, macro_detail_dict=macro)
    try: HumanService.set_character_skin(random.choice(skins_m if male else skins_f), bm, skin_type='ENHANCED_SSS')
    except Exception: traceback.print_exc(limit=1)
    rig = None
    try: rig = HumanService.add_builtin_rig(bm, 'default')
    except Exception: traceback.print_exc(limit=1)
    if rig is None: rig = bm.parent
    if eyes: add(eyes[0], bm, 'Eyes')
    if brows: add(brows[0], bm, 'Eyebrows')
    hl = hair_m if male else hair_f
    if hl and not (male and random.random() < 0.6): add(random.choice(hl), bm, 'Hair')
    if male:
        add(DHOTI, bm, 'Clothes', COTTON)
    else:
        sm = random.choice(SAREES); add(SKIRT, bm, 'Clothes', sm); add(TOP, bm, 'Clothes', random.choice(BLOUSE))
    root = rig if rig is not None else bm
    if rig is not None and POSES:
        try: AnimationService.import_bvh_file_as_pose(rig, random.choice(POSES))
        except Exception: traceback.print_exc(limit=1)
    root.location = (x, y, 0); root.rotation_euler[2] = rot; bpy.context.view_layer.update()
    pts = body_slices(bm); h = max(p.z for p in pts)
    neck = [p for p in pts if h * 0.86 < p.z < h * 0.89]
    nx = sum(p.x for p in neck) / len(neck); ny = sum(p.y for p in neck) / len(neck)
    head = [p for p in pts if p.z > h * 0.9 and (p.x - nx) ** 2 + (p.y - ny) ** 2 < 0.15 ** 2]
    if male and head and random.random() < 0.7:   # pagadi: wrapped bands spiralling up
        hx = (min(p.x for p in head) + max(p.x for p in head)) / 2; hy = (min(p.y for p in head) + max(p.y for p in head)) / 2
        r0 = max(max(p.x for p in head) - min(p.x for p in head), max(p.y for p in head) - min(p.y for p in head)) / 2 + 0.012
        tm = random.choice(TURBANS); top = max(p.z for p in head)
        for k in range(5):
            rr = r0 * (1.0 - k * 0.09); zz = top - 0.085 + k * 0.024
            bpy.ops.mesh.primitive_torus_add(major_radius=rr, minor_radius=0.018 + 0.004 * (k % 2), major_segments=40, minor_segments=10, location=(hx, hy, zz),
                                             rotation=(random.uniform(-0.18, 0.18), random.uniform(-0.18, 0.18), 0))
            o = bpy.context.object; o.scale = (1.0, 1.12, 1.0); o.data.materials.append(tm); bpy.ops.object.shade_smooth()
        bpy.ops.mesh.primitive_uv_sphere_add(radius=r0 * 0.78, location=(hx, hy, top - 0.01)); o = bpy.context.object; o.scale = (1, 1.12, 0.55); o.data.materials.append(tm); bpy.ops.object.shade_smooth()
    if not male:   # pallu: drape from left shoulder down the back
        tor = [p for p in pts if h * 0.78 < p.z < h * 0.84]
        cx = sum(p.x for p in tor) / len(tor); cy = sum(p.y for p in tor) / len(tor)
        fw = Vector((-math.sin(rot), math.cos(rot), 0)); rt = Vector((math.cos(rot), math.sin(rot), 0))
        c = Vector((cx, cy, 0)); sw = 0.15
        sash(c + rt * 0.12 + fw * -0.1 + Vector((0, 0, h * 0.6)), c - fw * 0.17 + Vector((0, 0, h * 0.74)), c - rt * sw + Vector((0, 0, h * 0.83)), 0.11, sm)
        sash(c - rt * sw + Vector((0, 0, h * 0.83)), c - rt * (sw + 0.03) + fw * 0.15 + Vector((0, 0, h * 0.72)), c - rt * 0.08 + fw * 0.17 + Vector((0, 0, h * 0.42)), 0.14, sm)
    return bm

# ---------- temple ----------
def box(loc, size, mat, bevel=0.0):
    bpy.ops.mesh.primitive_cube_add(location=loc); o = bpy.context.object; o.scale = (size[0] / 2, size[1] / 2, size[2] / 2); o.data.materials.append(mat)
    if bevel: m = o.modifiers.new('b', 'BEVEL'); m.width = bevel; m.segments = 2
    return o
def kudu(x, y, z, s, mat):  # horseshoe arch window ornament
    bpy.ops.mesh.primitive_torus_add(major_radius=0.22 * s, minor_radius=0.05 * s, location=(x, y, z), rotation=(math.pi / 2, 0, 0))
    o = bpy.context.object; o.data.materials.append(mat)
    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.07 * s, location=(x, y - 0.02, z + 0.3 * s)); bpy.context.object.data.materials.append(mat)
def figure(x, y, z, s, mat):  # stylised deity sculpture in a niche
    box((x, y + 0.12, z), (0.55 * s, 0.25, 0.95 * s), NICHE)
    bpy.ops.mesh.primitive_cylinder_add(radius=0.1 * s, depth=0.5 * s, location=(x, y, z - 0.12 * s)); bpy.context.object.data.materials.append(mat)
    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.08 * s, location=(x, y, z + 0.2 * s)); bpy.context.object.data.materials.append(mat)
    bpy.ops.mesh.primitive_cone_add(radius1=0.07 * s, depth=0.16 * s, location=(x, y, z + 0.33 * s)); bpy.context.object.data.materials.append(mat)
    for sx in (-1, 1):
        bpy.ops.mesh.primitive_cylinder_add(radius=0.025 * s, depth=0.35 * s, location=(x + sx * 0.13 * s, y, z + 0.02 * s), rotation=(0, sx * 0.5, 0)); bpy.context.object.data.materials.append(mat)
def gopuram(GX, GY, tiers=9, base_w=15.0, base_d=9.0):
    box((GX, GY, 2.6), (base_w + 1.2, base_d + 1.2, 5.2), STONE, 0.05)    # granite base storeys
    for z in (0.3, 1.6, 3.4, 5.0):
        box((GX, GY, z), (base_w + 1.5, base_d + 1.5, 0.25), STONE, 0.04)  # mouldings
    for j in range(-6, 7):
        if abs(j) <= 1: continue
        bpy.ops.mesh.primitive_cylinder_add(radius=0.18, depth=4.6, location=(GX + j * 1.15, GY - base_d / 2 - 0.65, 2.75)); bpy.context.object.data.materials.append(STONE)
        if abs(j) in (3, 5): figure(GX + j * 1.15 + 0.57, GY - base_d / 2 - 0.62, 2.8, 1.6, STONE)
    box((GX, GY - 0.3, 2.6), (2.6, base_d + 1.6, 5.0), DARK)
    for sx in (-1, 1): box((GX + sx * 0.95, GY - base_d / 2 - 0.55, 2.4), (0.75, 0.12, 4.6), WOOD, 0.02)   # open wooden doors
    z = 5.2; th = 2.0
    for k in range(tiers):
        f = (k / tiers) ** 0.8; w = base_w * (1 - f * 0.6); d = base_d * (1 - f * 0.5)
        box((GX, GY, z + th / 2), (w, d, th), PLASTER, 0.06)
        box((GX, GY, z + th - 0.1), (w + 0.5, d + 0.5, 0.2), PLASTER, 0.05)  # cornice
        n = max(2, int(w / 1.4))
        for j in range(n):
            xx = GX - w / 2 + (j + 0.5) * w / n; yy = GY - d / 2 - 0.15
            (figure if j % 2 else kudu)(xx, yy, z + th * 0.5, (1.2 if j % 4 == 1 else 0.9) if j % 2 else 1.3, PLASTER)
            if j % 2: figure(xx, yy + 0.05, z + th * 0.5, 0.55, PLASTER) if False else None
            bpy.ops.mesh.primitive_cube_add(location=(xx + w / n / 2, yy + 0.05, z + th * 0.45)); p = bpy.context.object; p.scale = (0.08, 0.08, th * 0.4); p.data.materials.append(PLASTER)
        z += th
    bpy.ops.mesh.primitive_cylinder_add(radius=base_d * 0.5 / 2 + 0.3, depth=base_w * 0.4 + 0.4, location=(GX, GY, z + 0.2), rotation=(0, math.pi / 2, 0))
    s = bpy.context.object; s.scale = (1, 1, 1); s.data.materials.append(PLASTER)     # barrel-vault shala roof
    for j in range(-3, 4):
        x = GX + j * 0.85
        bpy.ops.mesh.primitive_uv_sphere_add(radius=0.28, location=(x, GY, z + 1.6)); bpy.context.object.data.materials.append(GOLD)
        bpy.ops.mesh.primitive_cone_add(radius1=0.2, depth=0.7, location=(x, GY, z + 2.05)); bpy.context.object.data.materials.append(GOLD)
        bpy.ops.mesh.primitive_cylinder_add(radius=0.12, depth=0.3, location=(x, GY, z + 1.3)); bpy.context.object.data.materials.append(GOLD)
    for k in range(2):   # side kirtimukha horns
        bpy.ops.mesh.primitive_cone_add(radius1=0.35, depth=1.2, location=(GX + (k * 2 - 1) * (base_w * 0.4 / 2 + 0.4), GY, z + 0.9)); bpy.context.object.data.materials.append(PLASTER)
bpy.ops.mesh.primitive_plane_add(size=300); bpy.context.object.data.materials.append(GROUND)
for k in range(-9, 7):  # granite slab path
    for j in range(-2, 3): box((j * 1.2, k * 1.6 + 6, 0.02), (1.15, 1.55, 0.06), STONE, 0.02)
gopuram(0, 24)
for sx in (-1, 1):
    box((sx * 28, 24, 3), (40, 1.2, 6), STONE, 0.05)
    for j in range(20): bpy.ops.mesh.primitive_cone_add(radius1=0.35, depth=0.7, location=(sx * (9 + j * 2), 23.3, 6.3)); bpy.context.object.data.materials.append(PLASTER)
# coconut trees
for i in range(10):
    tx = random.choice([-1, 1]) * random.uniform(9, 22); ty = random.uniform(-6, 18)
    bpy.ops.curve.primitive_bezier_curve_add(location=(tx, ty, 0)); c = bpy.context.object
    c.data.splines[0].bezier_points[0].co = (0, 0, 0); c.data.splines[0].bezier_points[1].co = (random.uniform(-1, 1), 0.5, 9)
    for bp in c.data.splines[0].bezier_points: bp.handle_left_type = bp.handle_right_type = 'AUTO'
    c.data.bevel_depth = 0.16; c.data.materials.append(nmat('trunk', (0.35, 0.28, 0.2), 0.9, bump=0.5, scale=8))
    for a in range(9):
        ang = a * 2 * math.pi / 9; top = Vector((tx + c.data.splines[0].bezier_points[1].co.x, ty + 0.5, 9))
        sash(top, top + Vector((math.cos(ang) * 1.6, math.sin(ang) * 1.6, 0.6)), top + Vector((math.cos(ang) * 3.2, math.sin(ang) * 3.2, -1.2)), 0.45, nmat('leaf', (0.12, 0.3, 0.06), 0.6))
# crowd
n = 0
for r in range(5):
    for cidx in range(7):
        x = -6 + cidx * 1.9 + random.uniform(-0.5, 0.5); y = -6 + r * 2.6 + random.uniform(-0.7, 0.7)
        if abs(x) < 1.4 and y < 2: continue
        try: person(x, y, math.pi + random.uniform(-0.5, 0.5), (n % 5) not in (1, 3)); n += 1
        except Exception: traceback.print_exc(limit=3)
print('HUMANS', n)
# light: HDRI sky + low warm sun
w = bpy.data.worlds.new('w'); bpy.context.scene.world = w; w.use_nodes = True
if os.path.exists(PH + '/sky.hdr'):
    env = w.node_tree.nodes.new('ShaderNodeTexEnvironment'); env.image = bpy.data.images.load(PH + '/sky.hdr')
    w.node_tree.links.new(env.outputs[0], w.node_tree.nodes['Background'].inputs[0]); w.node_tree.nodes['Background'].inputs[1].default_value = 0.7
bpy.ops.object.light_add(type='SUN', rotation=(math.radians(70), 0, math.radians(235))); sun = bpy.context.object
sun.data.energy = 4.5; sun.data.color = (1.0, 0.82, 0.62); sun.data.angle = math.radians(1.5)
s = bpy.context.scene; s.render.engine = 'CYCLES'; s.cycles.device = 'CPU'; s.cycles.samples = int(os.environ.get('SPP', 64)); s.cycles.use_denoising = True
s.render.resolution_x, s.render.resolution_y = 1080, 1920; s.render.resolution_percentage = int(os.environ.get('PCT', 50))
s.view_settings.view_transform = 'AgX'; s.view_settings.look = 'AgX - Medium High Contrast'; s.view_settings.exposure = float(os.environ.get('EV', -0.3))
cams = {'wide': ((-7.5, -17, 1.1), (0, 14, 9), 21, 11), 'close': ((-2.6, -10.5, 1.35), (0.5, -3, 1.55), 35, 6.5)}
os.makedirs('/opt/r3d/out', exist_ok=True)
for name, (loc, tgt, lens, fd) in cams.items():
    bpy.ops.object.camera_add(location=loc); cam = bpy.context.object
    bpy.ops.object.empty_add(location=tgt); e = bpy.context.object
    tc = cam.constraints.new('TRACK_TO'); tc.target = e; tc.track_axis = 'TRACK_NEGATIVE_Z'; tc.up_axis = 'UP_Y'
    cam.data.lens = lens; cam.data.dof.use_dof = True; cam.data.dof.focus_distance = fd; cam.data.dof.aperture_fstop = 3.5
    s.camera = cam; s.render.filepath = f'/opt/r3d/out/v4_{name}.png'; bpy.ops.render.render(write_still=True)
bpy.ops.wm.save_as_mainfile(filepath='/opt/r3d/out/scene4.blend')
print('RENDER_DONE')
