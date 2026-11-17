# King-story prop kit: weapons, shields, royal regalia, banners, drums, chariot. Saved to /opt/r3d/assets/kit.blend
# (one collection per asset, marked as Blender assets) and rendered as a lineup sheet.
import bpy, bmesh, math, os, random
from mathutils import Vector
random.seed(3)
for o in list(bpy.data.objects): bpy.data.objects.remove(o)
PH = '/opt/r3d/assets/ph'
def M(name, col, rough=0.5, metal=0.0, emit=0.0, tex=None, scale=1.0):
    m = bpy.data.materials.new(name); m.use_nodes = True; nt = m.node_tree; b = nt.nodes['Principled BSDF']
    b.inputs['Base Color'].default_value = (*col, 1); b.inputs['Roughness'].default_value = rough; b.inputs['Metallic'].default_value = metal
    n = nt.nodes.new('ShaderNodeTexNoise'); n.inputs['Scale'].default_value = 60 * scale; n.inputs['Detail'].default_value = 10
    bp = nt.nodes.new('ShaderNodeBump'); bp.inputs['Strength'].default_value = 0.15; nt.links.new(n.outputs['Fac'], bp.inputs['Height']); nt.links.new(bp.outputs['Normal'], b.inputs['Normal'])
    rr = nt.nodes.new('ShaderNodeMapRange'); rr.inputs[3].default_value = rough * 0.7; rr.inputs[4].default_value = min(1, rough * 1.4)
    nt.links.new(n.outputs['Fac'], rr.inputs[0]); nt.links.new(rr.outputs[0], b.inputs['Roughness'])
    if tex and os.path.exists(f'{PH}/{tex}_diff.jpg'):
        t = nt.nodes.new('ShaderNodeTexImage'); t.image = bpy.data.images.load(f'{PH}/{tex}_diff.jpg'); t.projection = 'BOX'
        tc = nt.nodes.new('ShaderNodeTexCoord'); mp = nt.nodes.new('ShaderNodeMapping'); mp.inputs['Scale'].default_value = (4, 4, 4)
        nt.links.new(tc.outputs['Object'], mp.inputs['Vector']); nt.links.new(mp.outputs['Vector'], t.inputs['Vector'])
        mx = nt.nodes.new('ShaderNodeMix'); mx.data_type = 'RGBA'; mx.blend_type = 'MULTIPLY'; mx.inputs['Factor'].default_value = 1
        nt.links.new(t.outputs['Color'], mx.inputs['A']); mx.inputs['B'].default_value = (*col, 1); nt.links.new(mx.outputs['Result'], b.inputs['Base Color'])
    return m
GOLD = M('k_gold', (1.0, 0.71, 0.29), 0.25, 1.0); STEEL = M('k_steel', (0.62, 0.62, 0.64), 0.28, 1.0, scale=3)
BRONZE = M('k_bronze', (0.7, 0.45, 0.22), 0.35, 1.0); WOOD = M('k_wood', (0.55, 0.38, 0.24), 0.6, tex='wood')
LEATHER = M('k_leather', (0.22, 0.12, 0.07), 0.55, scale=2); RUBY = M('k_ruby', (0.6, 0.01, 0.03), 0.05); EMER = M('k_emerald', (0.0, 0.35, 0.12), 0.05)
PEARL = M('k_pearl', (0.95, 0.92, 0.86), 0.2); SAFF = M('k_saffron', (0.95, 0.42, 0.04), 0.8); RED = M('k_redcloth', (0.55, 0.03, 0.04), 0.75)
SKIN = M('k_drumskin', (0.78, 0.68, 0.52), 0.6)
for m in (RUBY, EMER):
    b = m.node_tree.nodes['Principled BSDF']; b.inputs['Transmission Weight'].default_value = 0.6; b.inputs['IOR'].default_value = 1.76

cur = None
def coll(name):
    global cur
    c = bpy.data.collections.new(name); bpy.context.scene.collection.children.link(c); cur = c; return c
def link(o):
    for c in o.users_collection: c.objects.unlink(o)
    cur.objects.link(o); return o
def mat(o, m):
    o.data.materials.clear(); o.data.materials.append(m); return o
def smooth(o):
    for p in o.data.polygons: p.use_smooth = True
    return o
def cyl(r, d, loc, m, rot=(0, 0, 0), v=32):
    bpy.ops.mesh.primitive_cylinder_add(radius=r, depth=d, location=loc, rotation=rot, vertices=v); return smooth(mat(link(bpy.context.object), m))
def sph(r, loc, m, sc=(1, 1, 1)):
    bpy.ops.mesh.primitive_uv_sphere_add(radius=r, location=loc, segments=32, ring_count=16); o = bpy.context.object; o.scale = sc; return smooth(mat(link(o), m))
def tor(R, r, loc, m, rot=(0, 0, 0), sc=(1, 1, 1)):
    bpy.ops.mesh.primitive_torus_add(major_radius=R, minor_radius=r, location=loc, rotation=rot, major_segments=48, minor_segments=12); o = bpy.context.object; o.scale = sc; return smooth(mat(link(o), m))
def cone(r1, r2, d, loc, m, rot=(0, 0, 0)):
    bpy.ops.mesh.primitive_cone_add(radius1=r1, radius2=r2, depth=d, location=loc, rotation=rot, vertices=32); return smooth(mat(link(bpy.context.object), m))
def box(sz, loc, m, rot=(0, 0, 0)):
    bpy.ops.mesh.primitive_cube_add(location=loc, rotation=rot); o = bpy.context.object; o.scale = (sz[0] / 2, sz[1] / 2, sz[2] / 2)
    bpy.ops.object.transform_apply(scale=True); return mat(link(o), m)
def loft(name, profile, m, seg=48):   # lathe: profile [(r, z)] around Z
    me = bpy.data.meshes.new(name); b = bmesh.new(); rings = []
    for r, z in profile: rings.append([b.verts.new((r * math.cos(2 * math.pi * i / seg), r * math.sin(2 * math.pi * i / seg), z)) for i in range(seg)])
    for a, c in zip(rings, rings[1:]):
        for i in range(seg): b.faces.new((a[i], a[(i + 1) % seg], c[(i + 1) % seg], c[i]))
    b.to_mesh(me); b.free(); o = bpy.data.objects.new(name, me); cur.objects.link(o); return smooth(mat(o, m))
def blade(name, length, w0, w1, curve, m, thick=0.006, seg=40):
    me = bpy.data.meshes.new(name); b = bmesh.new(); rows = []
    for k in range(seg + 1):
        t = k / seg; z = t * length; w = w0 + (w1 - w0) * t
        if t > 0.86: w *= max(0.02, (1 - t) / 0.14) ** 0.8         # point
        x = curve * (t ** 2) * length                              # sweep back (talwar)
        rows.append([b.verts.new((x - w / 2, 0, z)), b.verts.new((x, thick, z)), b.verts.new((x + w / 2, 0, z)), b.verts.new((x, -thick, z))])
    for a, c in zip(rows, rows[1:]):
        for i in range(4): b.faces.new((a[i], a[(i + 1) % 4], c[(i + 1) % 4], c[i]))
    b.to_mesh(me); b.free(); o = bpy.data.objects.new(name, me); cur.objects.link(o); return mat(o, m)
def place(c, x):
    for o in c.objects:
        if o.parent is None: o.location.x += x
    c.asset_mark()

X = 0.0; SP = 1.1; sheet = []
# 1 dhal shield
c = coll('shield_dhal'); loft('dhal', [(0.0, 0.08), (0.12, 0.075), (0.26, 0.05), (0.33, 0.02), (0.35, 0.0)], LEATHER)
tor(0.345, 0.015, (0, 0, 0.005), GOLD)
sph(0.05, (0, 0, 0.085), GOLD, (1, 1, 0.6))
for k in range(4): a = k * math.pi / 2 + math.pi / 4; sph(0.035, (0.15 * math.cos(a), 0.15 * math.sin(a), 0.066), GOLD, (1, 1, 0.55))
for k in range(16): a = k * math.pi / 8; sph(0.012, (0.3 * math.cos(a), 0.3 * math.sin(a), 0.03), GOLD)
for o in c.objects: o.rotation_euler = (math.pi / 2, 0, 0); o.location = Vector((o.location.x, -o.location.z, o.location.y + 1.0))
sheet.append(c)
# 2 talwar (curved sabre)
c = coll('sword_talwar'); blade('talwar_blade', 0.8, 0.04, 0.035, 0.12, STEEL); cyl(0.016, 0.11, (0, 0, -0.06), LEATHER)
box((0.16, 0.025, 0.015), (0, 0, 0.0), GOLD); sph(0.035, (0, 0, -0.13), GOLD, (1, 1, 0.35)); cone(0.012, 0, 0.04, (0, 0, -0.16), GOLD, (math.pi, 0, 0))
for o in c.objects: o.location.z += 0.25
sheet.append(c)
# 3 khanda (straight broadsword)
c = coll('sword_khanda'); blade('khanda_blade', 0.85, 0.045, 0.075, 0.0, STEEL); cyl(0.017, 0.13, (0, 0, -0.07), WOOD)
box((0.2, 0.03, 0.02), (0, 0, 0.0), GOLD); sph(0.04, (0, 0, -0.15), GOLD, (1, 1, 0.4)); cone(0.008, 0, 0.12, (0, 0, -0.2), GOLD, (math.pi, 0, 0))
for o in c.objects: o.location.z += 0.25
sheet.append(c)
# 4 spear (bhala) with tassel
c = coll('spear_bhala'); cyl(0.018, 2.3, (0, 0, 1.15), WOOD); blade('spear_head', 0.32, 0.07, 0.06, 0.0, STEEL, thick=0.01).location.z = 2.3
cyl(0.024, 0.06, (0, 0, 2.29), BRONZE); 
for k in range(10): a = k * 2 * math.pi / 10; cyl(0.004, 0.14, (0.025 * math.cos(a), 0.025 * math.sin(a), 2.2), RED, rot=(0.25 * math.sin(a), 0.25 * math.cos(a), 0), v=6)
cyl(0.02, 0.1, (0, 0, 0.05), BRONZE)
sheet.append(c)
# 5 bow + quiver with arrows
c = coll('bow_quiver')
bpy.ops.curve.primitive_bezier_curve_add(); bw = link(bpy.context.object); sp = bw.data.splines[0]; sp.bezier_points.add(1)
for p, co in zip(sp.bezier_points, [(0, 0, 0.2), (0.17, 0, 0.95), (0, 0, 1.7)]): p.co = co; p.handle_left_type = p.handle_right_type = 'AUTO'
bw.data.bevel_depth = 0.014; bw.data.bevel_resolution = 3; bw.data.materials.append(WOOD)
cyl(0.0015, 1.5, (0.0, 0, 0.95), PEARL, v=6); cyl(0.02, 0.18, (0.165, 0, 0.95), LEATHER)
cyl(0.075, 0.65, (0.45, 0.05, 0.7), LEATHER, rot=(0.0, 0.15, 0)); tor(0.077, 0.01, (0.405, 0.05, 1.02), GOLD, rot=(0, 0.15, 0))
for k in range(7): a = k * 2 * math.pi / 7; x = 0.45 + 0.04 * math.cos(a) + 0.06; y = 0.05 + 0.04 * math.sin(a)
for k in range(7):
    a = k * 2 * math.pi / 7; x = 0.4 + 0.04 * math.cos(a); y = 0.05 + 0.04 * math.sin(a)
    cyl(0.004, 0.75, (x + 0.06, y, 1.0), WOOD, rot=(0, 0.15, 0), v=6); cone(0.012, 0, 0.06, (x + 0.12, y, 1.38), SAFF, rot=(0, 0.15, 0))
sheet.append(c)
# 6 kireetam crown
c = coll('crown_kireetam')
loft('kireetam', [(0.105, 0.0), (0.11, 0.03), (0.1, 0.06), (0.085, 0.14), (0.07, 0.22), (0.05, 0.3), (0.03, 0.36), (0.012, 0.41), (0.0, 0.43)], GOLD)
for z, r in ((0.015, 0.108), (0.07, 0.097), (0.15, 0.083), (0.23, 0.068), (0.31, 0.047)): tor(r, 0.008, (0, 0, z), GOLD)
for k in range(12): a = k * 2 * math.pi / 12; sph(0.012, (0.11 * math.cos(a), 0.11 * math.sin(a), 0.035), RUBY if k % 2 else EMER)
for z, r, n in ((0.11, 0.09, 10), (0.19, 0.076, 8), (0.27, 0.058, 6)):
    for k in range(n): a = k * 2 * math.pi / n; sph(0.009, (r * math.cos(a), r * math.sin(a), z), PEARL)
sph(0.022, (0, -0.105, 0.09), RUBY, (1, 0.6, 1.3)); cone(0.014, 0, 0.05, (0, 0, 0.45), GOLD)
for o in c.objects: o.location.z += 1.3
sheet.append(c)
# 7 royal jewellery: necklace with pendant, armlets, earrings
c = coll('royal_jewellery')
for k in range(3): tor(0.12 + k * 0.025, 0.006, (0, 0, 1.45 - k * 0.04), GOLD, rot=(0.35, 0, 0), sc=(1, 1.15, 1))
for k in range(40): a = k * 2 * math.pi / 40; sph(0.009, (0.17 * math.cos(a), 0.17 * 1.15 * math.sin(a) * math.cos(0.35), 1.37 + 0.17 * 1.15 * math.sin(a) * math.sin(0.35)), PEARL)
sph(0.04, (0, -0.2, 1.24), GOLD, (1, 0.4, 1.3)); sph(0.022, (0, -0.215, 1.24), RUBY, (1, 0.6, 1.2))
for sx in (-1, 1): tor(0.055, 0.012, (sx * 0.3, 0, 1.2), GOLD, sc=(1, 1, 1.6)); sph(0.016, (sx * 0.3, -0.055, 1.2), EMER)
for sx in (-1, 1): tor(0.02, 0.005, (sx * 0.1, 0, 1.58), GOLD, rot=(math.pi / 2, 0, 0)); sph(0.012, (sx * 0.1, 0, 1.55), RUBY)
sheet.append(c)
# 8 battle banner
c = coll('banner_flag'); cyl(0.022, 3.2, (0, 0, 1.6), WOOD); sph(0.05, (0, 0, 3.22), GOLD)
me = bpy.data.meshes.new('flag'); b = bmesh.new(); W, Hh = 24, 12
V = [[b.verts.new((i / W * 1.1, 0.06 * math.sin(i / W * 9 + j * 0.3) * (i / W), 3.1 - j / Hh * 0.75 * (1 - 0.5 * i / W))) for i in range(W + 1)] for j in range(Hh + 1)]
for j in range(Hh):
    for i in range(W): b.faces.new((V[j][i], V[j][i + 1], V[j + 1][i + 1], V[j + 1][i]))
b.to_mesh(me); b.free(); f = bpy.data.objects.new('flag', me); cur.objects.link(f); mat(smooth(f), SAFF); f.modifiers.new('s', 'SOLIDIFY').thickness = 0.004
sheet.append(c)
# 9 war drum (nagara)
c = coll('war_drum_nagara'); loft('nagara', [(0.0, 0.0), (0.18, 0.02), (0.32, 0.12), (0.38, 0.28), (0.38, 0.32)], BRONZE)
cyl(0.375, 0.01, (0, 0, 0.325), SKIN, v=48); tor(0.38, 0.015, (0, 0, 0.32), GOLD)
for k in range(16): a = k * 2 * math.pi / 16; cyl(0.004, 0.3, (0.36 * math.cos(a), 0.36 * math.sin(a), 0.17), LEATHER, rot=(0.6 * math.sin(a), -0.6 * math.cos(a), 0), v=6)
for sx in (-1, 1): cyl(0.012, 0.4, (sx * 0.25, -0.3, 0.55), WOOD, rot=(0.6, sx * 0.4, 0)); sph(0.03, (sx * 0.33, -0.42, 0.72), RED)
sheet.append(c)
# 10 chariot (ratha)
c = coll('chariot_ratha')
for sx in (-1, 1):
    tor(0.55, 0.035, (sx * 0.75, 0, 0.6), WOOD, rot=(0, math.pi / 2, 0)); cyl(0.1, 0.18, (sx * 0.75, 0, 0.6), BRONZE, rot=(0, math.pi / 2, 0))
    for k in range(12): a = k * math.pi / 6; cyl(0.015, 0.5, (sx * 0.75, 0.27 * math.cos(a), 0.6 + 0.27 * math.sin(a)), WOOD, rot=(a - math.pi / 2, 0, 0), v=8)
cyl(0.035, 1.7, (0, 0, 0.6), WOOD, rot=(0, math.pi / 2, 0)); box((1.3, 1.0, 0.08), (0, 0, 0.85), WOOD)
box((1.3, 0.06, 0.55), (0, 0.48, 1.15), WOOD); 
for sx in (-1, 1): box((0.06, 1.0, 0.45), (sx * 0.63, 0, 1.1), WOOD)
for x in (-0.6, 0.6):
    for y in (-0.45, 0.45): cyl(0.03, 1.4, (x, y, 1.55), GOLD)
loft('canopy', [(0.95, 0.0), (0.8, 0.12), (0.5, 0.3), (0.2, 0.45), (0.0, 0.55)], RED).location = (0, 0, 2.25)
cone(0.06, 0, 0.35, (0, 0, 2.95), GOLD); box((0.06, 2.4, 0.06), (0, -1.6, 0.75), WOOD, rot=(-0.12, 0, 0))
for o in c.objects: o.scale = (0.8, 0.8, 0.8); o.location *= 0.8
sheet.append(c)

xs = [0.0, 0.9, 1.6, 2.3, 3.1, 4.0, 4.8, 5.8, 7.0, 8.9]
for c, x in zip(sheet, xs): place(c, x)
os.makedirs('/opt/r3d/assets', exist_ok=True)
bpy.ops.wm.save_as_mainfile(filepath='/opt/r3d/assets/kit.blend')
# lineup render
bpy.ops.mesh.primitive_plane_add(size=60); mat(bpy.context.object, M('floor', (0.55, 0.5, 0.45), 0.8))
w = bpy.data.worlds.new('w'); bpy.context.scene.world = w; w.use_nodes = True
if os.path.exists(PH + '/sky.hdr'):
    env = w.node_tree.nodes.new('ShaderNodeTexEnvironment'); env.image = bpy.data.images.load(PH + '/sky.hdr'); w.node_tree.links.new(env.outputs[0], w.node_tree.nodes['Background'].inputs[0])
bpy.ops.object.light_add(type='SUN', rotation=(math.radians(55), 0, math.radians(25))); bpy.context.object.data.energy = 3.5; bpy.context.object.data.color = (1, 0.88, 0.72)
bpy.ops.object.camera_add(location=(4.5, -11.5, 2.0)); cam = bpy.context.object; bpy.ops.object.empty_add(location=(4.5, 0, 1.1)); t = bpy.context.object
k = cam.constraints.new('TRACK_TO'); k.target = t; k.track_axis = 'TRACK_NEGATIVE_Z'; k.up_axis = 'UP_Y'; cam.data.lens = 42
s = bpy.context.scene; s.camera = cam; s.render.engine = 'CYCLES'; s.cycles.device = 'CPU'; s.cycles.samples = 64; s.cycles.use_denoising = True
s.render.resolution_x, s.render.resolution_y = 1920, 1080; s.render.resolution_percentage = 60; s.view_settings.view_transform = 'AgX'; s.view_settings.look = 'AgX - Medium High Contrast'
s.render.filepath = '/opt/r3d/out/props_sheet.png'; bpy.ops.render.render(write_still=True); print('PROPS_DONE')
