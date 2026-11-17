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
GROUND = nmat('ground', (0.55, 0.47, 0.36), 0.95, bump=0.4, scale=3, var=0.4)
DARK = nmat('dark', (0.04, 0.03, 0.025), 0.9)

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

def person(x, y, rot, male):
    macro = {'gender': 1.0 if male else 0.0, 'age': random.uniform(0.45, 0.62), 'muscle': random.uniform(0.45, 0.7), 'weight': random.uniform(0.4, 0.65),
             'height': random.uniform(0.35, 0.6), 'proportions': 0.6, 'cupsize': 0.5, 'firmness': 0.5, 'race': {'african': 0.3, 'asian': 0.45, 'caucasian': 0.25}}
    bm = HumanService.create_human(feet_on_ground=True, scale=0.1, macro_detail_dict=macro)
    try: HumanService.set_character_skin(random.choice(skins_m if male else skins_f), bm, skin_type='ENHANCED_SSS')
    except Exception: traceback.print_exc(limit=1)
    for lst, typ in ((eyes, 'Eyes'), (brows, 'Eyebrows'), ((hair_m if male else hair_f), 'Hair')):
        if lst:
            try: HumanService.add_mhclo_asset(random.choice(lst) if typ == 'Hair' else lst[0], bm, asset_type=typ, subdiv_levels=0, material_type='MAKESKIN')
            except Exception: traceback.print_exc(limit=1)
    bm.location = (x, y, 0); bm.rotation_euler[2] = rot; bpy.context.view_layer.update()
    pts = body_slices(bm); h = max(p.z for p in pts)
    if male:
        garment(pts, h * 0.56, h * 0.06, 0.03, 0.06, COTTON)          # panche / dhoti to the ankle
        garment(pts, h * 0.565, h * 0.545, 0.035, 0.0, BORDER, wob=0, n=2)  # zari waist band
        sh = ring_extent(pts, h * 0.80, h * 0.83); cx, cy, rx, ry = sh
        R = Vector((cx + rx * 0.8, cy, h * 0.82)); L = Vector((cx - rx * 0.7, cy, h * 0.6))
        sash(R, Vector((cx, cy - ry - 0.05, h * 0.72)), L, 0.14, COTTON)  # angavastram across chest
        hd = ring_extent(pts, h * 0.93, h * 0.97)
        if hd and random.random() < 0.6:
            hx, hy, hrx, hry = hd
            rings = [(h * 0.925 + k * 0.022, hx, hy, hrx + 0.035 - k * 0.004, hry + 0.04 - k * 0.004, 0.06) for k in range(6)]
            loft('turban', rings, random.choice(TURBANS))
    else:
        sm = random.choice(SAREES)
        garment(pts, h * 0.60, h * 0.035, 0.02, 0.09, sm, wob=0.035)      # saree skirt
        garment(pts, h * 0.78, h * 0.66, 0.012, 0.0, random.choice(BLOUSE), wob=0, n=5)  # blouse
        sh = ring_extent(pts, h * 0.80, h * 0.83); cx, cy, rx, ry = sh
        sash(Vector((cx + rx * 0.5, cy - 0.02, h * 0.6)), Vector((cx, cy - ry - 0.06, h * 0.76)), Vector((cx - rx * 0.85, cy + 0.02, h * 0.83)), 0.22, sm)  # pallu
        sash(Vector((cx - rx * 0.85, cy + 0.02, h * 0.83)), Vector((cx - rx * 0.9, cy + ry + 0.08, h * 0.7)), Vector((cx - rx * 0.6, cy + ry + 0.12, h * 0.45)), 0.25, sm)  # pallu down the back
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
    box((x, y + 0.12, z), (0.55 * s, 0.25, 0.95 * s), DARK)
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
    box((GX, GY - 0.3, 2.6), (2.6, base_d + 1.6, 5.0), DARK)                # doorway
    z = 5.2; th = 2.0
    for k in range(tiers):
        w = base_w - k * 1.25; d = base_d - k * 0.7
        box((GX, GY, z + th / 2), (w, d, th), PLASTER, 0.06)
        box((GX, GY, z + th - 0.1), (w + 0.5, d + 0.5, 0.2), PLASTER, 0.05)  # cornice
        n = max(2, int(w / 1.4))
        for j in range(n):
            xx = GX - w / 2 + (j + 0.5) * w / n; yy = GY - d / 2 - 0.15
            (figure if j % 2 else kudu)(xx, yy, z + th * 0.5, 1.0 if j % 2 else 1.3, PLASTER)
            bpy.ops.mesh.primitive_cube_add(location=(xx + w / n / 2, yy + 0.05, z + th * 0.45)); p = bpy.context.object; p.scale = (0.08, 0.08, th * 0.4); p.data.materials.append(PLASTER)
        z += th
    bpy.ops.mesh.primitive_cylinder_add(radius=(base_d - tiers * 0.7) / 2 + 0.3, depth=base_w - tiers * 1.25 + 0.4, location=(GX, GY, z + 0.2), rotation=(0, math.pi / 2, 0))
    s = bpy.context.object; s.scale = (1, 1, 1); s.data.materials.append(PLASTER)     # barrel-vault shala roof
    for j in range(-3, 4):
        x = GX + j * 0.85
        bpy.ops.mesh.primitive_uv_sphere_add(radius=0.28, location=(x, GY, z + 1.6)); bpy.context.object.data.materials.append(GOLD)
        bpy.ops.mesh.primitive_cone_add(radius1=0.2, depth=0.7, location=(x, GY, z + 2.05)); bpy.context.object.data.materials.append(GOLD)
        bpy.ops.mesh.primitive_cylinder_add(radius=0.12, depth=0.3, location=(x, GY, z + 1.3)); bpy.context.object.data.materials.append(GOLD)
    for k in range(2):   # side kirtimukha horns
        bpy.ops.mesh.primitive_cone_add(radius1=0.35, depth=1.2, location=(GX + (k * 2 - 1) * ((base_w - tiers * 1.25) / 2 + 0.4), GY, z + 0.9)); bpy.context.object.data.materials.append(PLASTER)
bpy.ops.mesh.primitive_plane_add(size=300); bpy.context.object.data.materials.append(GROUND)
for k in range(-6, 7):  # granite slab path
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
        x = -7 + cidx * 2.2 + random.uniform(-0.5, 0.5); y = -3 + r * 3.0 + random.uniform(-0.8, 0.8)
        if abs(x) < 1.4 and y < 2: continue
        try: person(x, y, math.pi + random.uniform(-0.5, 0.5), (n % 5) not in (1, 3)); n += 1
        except Exception: traceback.print_exc(limit=3)
print('HUMANS', n)
# light
w = bpy.data.worlds.new('w'); bpy.context.scene.world = w; w.use_nodes = True
sky = w.node_tree.nodes.new('ShaderNodeTexSky'); sky.sky_type = 'NISHITA'; sky.sun_elevation = math.radians(35); sky.sun_rotation = math.radians(215); sky.sun_disc = False
w.node_tree.links.new(sky.outputs[0], w.node_tree.nodes['Background'].inputs[0]); w.node_tree.nodes['Background'].inputs[1].default_value = 0.12
bpy.ops.object.light_add(type='SUN', rotation=(math.radians(55), 0, math.radians(215))); bpy.context.object.data.energy = 4; bpy.context.object.data.angle = math.radians(2)
s = bpy.context.scene; s.render.engine = 'CYCLES'; s.cycles.device = 'CPU'; s.cycles.samples = int(os.environ.get('SPP', 64)); s.cycles.use_denoising = True
s.render.resolution_x, s.render.resolution_y = 1080, 1920; s.render.resolution_percentage = int(os.environ.get('PCT', 50))
s.view_settings.view_transform = 'AgX'; s.view_settings.look = 'AgX - Medium High Contrast'; s.view_settings.exposure = -0.5
cams = {'wide': ((1.0, -14, 3.0), (84, 0, 3), 24, 12), 'close': ((-1.5, -6.5, 1.55), (88, 0, -12), 40, 4.0)}
os.makedirs('/opt/r3d/out', exist_ok=True)
bpy.ops.wm.save_as_mainfile(filepath='/opt/r3d/out/scene2.blend')
for name, (loc, rot, lens, fd) in cams.items():
    bpy.ops.object.camera_add(location=loc, rotation=tuple(math.radians(a) for a in rot)); cam = bpy.context.object
    cam.data.lens = lens; cam.data.dof.use_dof = True; cam.data.dof.focus_distance = fd; cam.data.dof.aperture_fstop = 4.0
    s.camera = cam; s.render.filepath = f'/opt/r3d/out/v2_{name}.png'; bpy.ops.render.render(write_still=True)
print('RENDER_DONE')
