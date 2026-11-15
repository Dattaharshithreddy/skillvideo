"""Tirumala ghat roads: real-terrain fly-over (Copernicus DEM + Sentinel-2 colour + OSM roads), one shot per narration line."""
import bpy, json, math, os, random, subprocess, sys
import numpy as np
from mathutils import Vector
HERE = os.path.dirname(os.path.abspath(__file__)); os.chdir(HERE); random.seed(3)
FPS = 30
plan = json.load(open('brief/plan.json'))
durs = []
for l in plan['lines']:
    d = float(subprocess.run(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0', l['audio']], capture_output=True, text=True).stdout)
    durs.append(d + plan['gap'])
starts, t = [], 0.0
for d in durs: starts.append(t); t += d
SH = [(round(s * FPS) + 1, round((s + d) * FPS)) for s, d in zip(starts, durs)]
END = SH[-1][1] + 45   # short tail for the end card
SHOT = {l['shot']: i for i, l in enumerate(plan['lines'])}
def S(name): return SH[SHOT[name]]
def fr(name, x): a, b = S(name); return int(a + (b - a) * x)
json.dump({'starts': starts, 'durs': durs, 'end': END, 'lines': [{'text': l['text'], 'keywords': l['keywords'], 'shot': l['shot']} for l in plan['lines']]},
          open('brief/timing.json', 'w'), indent=1)

bpy.ops.wm.read_factory_settings(use_empty=True)
sc = bpy.context.scene; sc.frame_start, sc.frame_end, sc.render.fps = 1, END, FPS

# ---------------- data ----------------
meta = json.load(open('geo/meta.json')); R = json.load(open('geo/roads.json'))
dem = np.load('geo/dem.npy'); h, w = dem.shape; RES = meta['res']
OX, OY = meta['origin']; ZB = float(dem.min())
def loc(x, y, z, lift=0.0): return Vector((x - OX, y - OY, z - ZB + lift))
def elev_local(x, y):
    c = (x + OX - meta['x0']) / RES - 0.5; r = (meta['y1'] - (y + OY)) / RES - 0.5
    c = min(max(c, 0), w - 1.001); r = min(max(r, 0), h - 1.001); c0, r0 = int(c), int(r); fc, frr = c - c0, r - r0
    return float(dem[r0, c0] * (1 - fc) * (1 - frr) + dem[r0, c0 + 1] * fc * (1 - frr) + dem[r0 + 1, c0] * (1 - fc) * frr + dem[r0 + 1, c0 + 1] * fc * frr) - ZB

# ---------------- helpers ----------------
def fcurves(idb):
    ad = idb.animation_data
    if not ad or not ad.action: return []
    out = []
    for layer in getattr(ad.action, 'layers', []):
        for strip in layer.strips:
            for cb in strip.channelbags: out += list(cb.fcurves)
    if not out and hasattr(ad.action, 'fcurves'): out = list(ad.action.fcurves)
    return out
def show(o, ranges):
    base = tuple(o.scale); o.scale = (0, 0, 0); o.keyframe_insert('scale', frame=1)
    for a, b in ranges:
        o.scale = base; o.keyframe_insert('scale', frame=a); o.scale = (0, 0, 0); o.keyframe_insert('scale', frame=b)
    for fc in fcurves(o):
        if fc.data_path == 'scale':
            for kp in fc.keyframe_points: kp.interpolation = 'CONSTANT'
def emis(name, col, strength):
    m = bpy.data.materials.new(name); m.use_nodes = True; nt = m.node_tree
    for n in list(nt.nodes): nt.nodes.remove(n)
    e = nt.nodes.new('ShaderNodeEmission'); o = nt.nodes.new('ShaderNodeOutputMaterial')
    e.inputs['Color'].default_value = (*col, 1); e.inputs['Strength'].default_value = strength
    nt.links.new(e.outputs[0], o.inputs[0]); return m
def principled(name, col, rough=0.6):
    m = bpy.data.materials.new(name); m.use_nodes = True
    b = m.node_tree.nodes['Principled BSDF']; b.inputs['Base Color'].default_value = (*col, 1); b.inputs['Roughness'].default_value = rough
    return m
def curve(name, pts, radius, m):
    cu = bpy.data.curves.new(name, 'CURVE'); cu.dimensions = '3D'; cu.bevel_depth = radius; cu.bevel_resolution = 2
    cu.resolution_u = 2; cu.use_fill_caps = True
    sp = cu.splines.new('POLY'); sp.points.add(len(pts) - 1)
    for p, c in zip(sp.points, pts): p.co = (*c, 1)
    o = bpy.data.objects.new(name, cu); sc.collection.objects.link(o); o.data.materials.append(m); return o
def grow(o, pairs):
    for f, v in pairs:
        o.data.bevel_factor_end = v; o.data.keyframe_insert('bevel_factor_end', frame=f)

# ---------------- terrain ----------------
xs = meta['x0'] + (np.arange(w) + 0.5) * RES - OX
ys = meta['y1'] - (np.arange(h) + 0.5) * RES - OY
X, Y = np.meshgrid(xs, ys)
verts = np.stack([X.ravel(), Y.ravel(), (dem - ZB).ravel()], 1).astype(np.float32)
ii = np.arange(h * w).reshape(h, w)
quads = np.stack([ii[:-1, :-1].ravel(), ii[1:, :-1].ravel(), ii[1:, 1:].ravel(), ii[:-1, 1:].ravel()], 1)
me = bpy.data.meshes.new('terrain'); me.vertices.add(len(verts)); me.vertices.foreach_set('co', verts.ravel())
me.loops.add(quads.size); me.loops.foreach_set('vertex_index', quads.ravel().astype(np.int32))
me.polygons.add(len(quads)); me.polygons.foreach_set('loop_start', np.arange(0, quads.size, 4, dtype=np.int32))
me.polygons.foreach_set('loop_total', np.full(len(quads), 4, np.int32))
uv = me.uv_layers.new(name='UV')
vi = quads.ravel(); cols, rows = vi % w, vi // w
uv.data.foreach_set('uv', np.stack([cols / (w - 1), 1 - rows / (h - 1)], 1).astype(np.float32).ravel())
me.update(); me.validate()
me.polygons.foreach_set('use_smooth', [True] * len(me.polygons))
terr = bpy.data.objects.new('terrain', me); sc.collection.objects.link(terr)
tm = bpy.data.materials.new('terrain'); tm.use_nodes = True; nt = tm.node_tree; bs = nt.nodes['Principled BSDF']
bs.inputs['Roughness'].default_value = 0.9
if os.path.exists('geo/s2.png'):
    img = nt.nodes.new('ShaderNodeTexImage'); img.image = bpy.data.images.load(os.path.abspath('geo/s2.png')); img.interpolation = 'Cubic'
    hsv = nt.nodes.new('ShaderNodeHueSaturation'); hsv.inputs['Saturation'].default_value = 1.25; hsv.inputs['Value'].default_value = 1.35
    bc = nt.nodes.new('ShaderNodeBrightContrast'); bc.inputs['Contrast'].default_value = 0.15
    nt.links.new(img.outputs['Color'], hsv.inputs['Color']); nt.links.new(hsv.outputs['Color'], bc.inputs['Color'])
    nt.links.new(bc.outputs['Color'], bs.inputs['Base Color'])
else:
    bs.inputs['Base Color'].default_value = (0.12, 0.18, 0.07, 1)
terr.data.materials.append(tm)

# ---------------- sky, sun, haze ----------------
wd = bpy.data.worlds.new('w'); sc.world = wd; wd.use_nodes = True; wn = wd.node_tree
sky = wn.nodes.new('ShaderNodeTexSky'); sky.sky_type = 'NISHITA'
sky.sun_elevation = math.radians(14); sky.sun_rotation = math.radians(250); sky.altitude = 900; sky.air_density = 1.6; sky.dust_density = 2.5
wn.links.new(sky.outputs['Color'], wn.nodes['Background'].inputs['Color']); wn.nodes['Background'].inputs['Strength'].default_value = 0.35
vol = wn.nodes.new('ShaderNodeVolumePrincipled'); vol.inputs['Density'].default_value = 0.00006
vol.inputs['Color'].default_value = (0.75, 0.82, 1.0, 1)
wn.links.new(vol.outputs[0], wn.nodes['World Output'].inputs['Volume'])
bpy.ops.object.light_add(type='SUN'); sun = bpy.context.object; sun.data.energy = 4.0; sun.data.color = (1.0, 0.85, 0.65)
sun.rotation_euler = (math.radians(90 - 14), 0, math.radians(250 - 90))
sun.data.angle = math.radians(1.5)

# ---------------- roads, track, straight line ----------------
def road_pts(key, lift=6.0):
    return [tuple(loc(x, y, z, lift)) for x, y, z, d in R[key]]
UP, DN = R['up'], R['down']                     # up: Alipiri -> Tirumala (1974 road); down: Tirumala -> Alipiri (1944 road)
road1_up = list(reversed(road_pts('down')))     # first road drawn from Alipiri upward
road2 = road_pts('up')
M_old = emis('road_old', (0.25, 1.0, 0.45), 6.0); M_new = emis('road_new', (1.0, 0.62, 0.12), 6.0)
M_red = emis('road_red', (1.0, 0.08, 0.05), 9.0); M_line = emis('straight', (1.0, 0.1, 0.08), 7.0)
M_track = emis('track', (1.0, 0.82, 0.45), 5.0); M_gold = emis('beacon', (1.0, 0.75, 0.25), 12.0)
M_car = emis('car', (1.0, 0.95, 0.85), 14.0)
r1 = curve('road_1944', road1_up, 7.0, M_old)
r2 = curve('road_1974', road2, 7.0, M_new)
L2 = UP[-1][3]
red_pts = [tuple(loc(x, y, z, 7.0)) for x, y, z, d in UP if 11000 <= d <= 17000]
rred = curve('road_1974_cut', red_pts, 9.0, M_red)
sa, sb = R['straight']['a'], R['straight']['b']
sline = curve('straight_up', [tuple(loc(*sa, 30)), tuple(loc(*sb, 30))], 9.0, M_line)
# old bullock-cart track: dots along the first road
dots = []
acc = 0.0
for i, (x, y, z, d) in enumerate(reversed(DN)):
    if i % 3: continue
    bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=1, radius=6, location=loc(x, y, z, 6)); o = bpy.context.object
    o.data.materials.append(M_track); dots.append(o)
# markers: Alipiri and Tirumala beacons
A = loc(DN[-1][0], DN[-1][1], DN[-1][2]); T_ = loc(DN[0][0], DN[0][1], DN[0][2])
def beacon(name, p, hgt):
    bpy.ops.mesh.primitive_cylinder_add(radius=6, depth=hgt, location=p + Vector((0, 0, hgt / 2))); o = bpy.context.object; o.name = name
    o.data.materials.append(M_gold); return o
bT = beacon('beacon_tirumala', T_, 260); bA = beacon('beacon_alipiri', A, 160)

# ---------------- vehicles (light dots) ----------------
def path_obj(name, pts):
    cu = bpy.data.curves.new(name, 'CURVE'); cu.dimensions = '3D'; cu.use_path = True; cu.path_duration = 100
    sp = cu.splines.new('POLY'); sp.points.add(len(pts) - 1)
    for p, c in zip(sp.points, pts): p.co = (*c, 1)
    o = bpy.data.objects.new(name, cu); sc.collection.objects.link(o); return o
def traffic(prefix, pts, n, period, ranges):
    crv = path_obj('path_' + prefix, pts)
    for i in range(n):
        e = bpy.data.objects.new(f'{prefix}_e{i}', None); sc.collection.objects.link(e)
        c = e.constraints.new('FOLLOW_PATH'); c.target = crv; c.use_fixed_location = True; c.use_curve_follow = True
        c.offset_factor = 0.0; c.keyframe_insert('offset_factor', frame=1); c.offset_factor = 1.0; c.keyframe_insert('offset_factor', frame=1 + period)
        ph = i / n * period
        for fc in fcurves(e):
            if 'offset_factor' in fc.data_path:
                for kp in fc.keyframe_points:
                    kp.interpolation = 'LINEAR'; kp.co[0] -= ph; kp.handle_left[0] -= ph; kp.handle_right[0] -= ph
                fc.modifiers.new('CYCLES')
        bpy.ops.mesh.primitive_cube_add(size=1); o = bpy.context.object; o.scale = (16, 7, 7); o.data.materials.append(M_car)
        o.parent = e; o.location = (0, 0, 4); show(o, ranges)
r1_dn = [tuple(loc(x, y, z, 6)) for x, y, z, d in DN]
SHOWN_OPEN = [(S('open')[0], S('two_roads')[1] + 1)]
traffic('car_up2', road2, 34, 1800, SHOWN_OPEN + [(S('finale')[0], END + 1)])
traffic('car_dn1', r1_dn, 34, 1800, SHOWN_OPEN + [(S('old_runs')[0], END + 1)])
traffic('car_1944_up', road1_up, 22, 1800, [(S('traffic')[0], S('traffic')[1] + 1)])
traffic('car_1944_dn', r1_dn, 22, 1800, [(S('traffic')[0], S('traffic')[1] + 1)])

# ---------------- visibility & growth by shot ----------------
show(r1, [(S('open')[0], S('two_roads')[1] + 1), (S('lay_road')[0], END + 1)])
grow(r1, [(1, 1.0), (S('two_roads')[1], 1.0), (S('lay_road')[0], 0.0), (fr('lay_road', 0.9), 1.0)])
show(r2, [(S('open')[0], S('two_roads')[1] + 1), (S('second_road')[0], END + 1)])
grow(r2, [(1, 1.0), (S('two_roads')[1], 1.0), (S('second_road')[0], 0.0), (fr('second_road', 0.55), 1.0)])
show(rred, [(fr('two_roads', 0.55), S('two_roads')[1] + 1), (fr('second_road', 0.6), S('rockfall')[1] + 1)])
show(sline, [(S('straight')[0], S('straight')[1] + 1)])
grow(sline, [(S('straight')[0], 0.0), (fr('straight', 0.5), 1.0)])
nD = len(dots)
for i, o in enumerate(dots):
    a = int(S('cart_track')[0] + (S('cart_track')[1] - S('cart_track')[0]) * 0.9 * i / nD)
    show(o, [(a, S('lay_road')[1] + 1)])
for o in (bT, bA): show(o, [(1, END + 1)])

# ---------------- rockfall on the 1974 cut ----------------
mid = [p for p in UP if 13000 <= p[3] <= 15000]
M_rock = principled('rock', (0.35, 0.3, 0.26), 0.9)
ra, rb = S('rockfall')
for i in range(14):
    x, y, z, d = mid[int(i / 14 * (len(mid) - 1))]
    k = min(len(UP) - 2, UP.index([x, y, z, d]) if [x, y, z, d] in UP else 0)
    nx_, ny_ = UP[k + 1][0] - x, UP[k + 1][1] - y; nn = math.hypot(nx_, ny_) or 1
    perp = Vector((-ny_ / nn, nx_ / nn, 0))
    # pick the uphill side
    p1 = Vector((x - OX, y - OY, 0)) + perp * 90; p2 = Vector((x - OX, y - OY, 0)) - perp * 90
    up_side = p1 if elev_local(p1.x, p1.y) > elev_local(p2.x, p2.y) else p2
    st_ = Vector((up_side.x, up_side.y, elev_local(up_side.x, up_side.y) + 12)); en_ = loc(x, y, z, 10)
    bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=2, radius=random.uniform(7, 12), location=st_); o = bpy.context.object
    o.scale = (1, random.uniform(0.7, 1), random.uniform(0.6, 0.9)); o.data.materials.append(M_rock)
    f0 = int(ra + (rb - ra) * (0.2 + 0.5 * i / 14)); f1 = f0 + 22
    o.location = st_; o.keyframe_insert('location', frame=f0); o.rotation_euler = (0, 0, 0); o.keyframe_insert('rotation_euler', frame=f0)
    o.location = en_; o.keyframe_insert('location', frame=f1); o.rotation_euler = (random.uniform(4, 8), random.uniform(2, 5), 0); o.keyframe_insert('rotation_euler', frame=f1)
    show(o, [(f0, rb + 1)])

# ---------------- cameras ----------------
cd = bpy.data.cameras.new('cam'); cam = bpy.data.objects.new('cam', cd); sc.collection.objects.link(cam); sc.camera = cam
cd.sensor_width = 24; cd.clip_start = 5; cd.clip_end = 60000; cd.dof.use_dof = False
tgt = bpy.data.objects.new('cam_target', None); sc.collection.objects.link(tgt)
c = cam.constraints.new('TRACK_TO'); c.target = tgt; c.track_axis = 'TRACK_NEGATIVE_Z'; c.up_axis = 'UP_Y'
allp = [Vector(p) for p in road1_up + road2]
C = sum(allp, Vector()) / len(allp)
def at(pts, frac_): return Vector(pts[min(len(pts) - 1, int(frac_ * (len(pts) - 1)))])
hp = R['down_report']['hairpin_at_m']
if hp:
    # densest 1.5 km window of hairpins on the first road (distance measured from the top)
    best = max(hp, key=lambda m: sum(1 for q in hp if 0 <= q - m <= 1500))
    dmid = best + 750; H = Vector(loc(*min(DN, key=lambda p: abs(p[3] - dmid))[:3]))
else:
    H = at(road1_up, 0.6)
RC = Vector(loc(*mid[len(mid) // 2][:3])) if mid else at(road2, 0.7)
KEYS = []
def K(f, c_, t_, ln): KEYS.append((int(f), Vector(c_), Vector(t_), ln))
def shot(name, c0, c1, t0, t1=None, ln=30):
    a, b = S(name); K(a, c0, t0, ln); K(b, c1, t1 or t0, ln)
V = Vector
D = (T_ - A); D.z = 0; Dn = D.normalized(); Pn = V((-Dn.y, Dn.x, 0))
shot('open', A - Dn * 3500 + Pn * 1500 + V((0, 0, 2200)), A - Dn * 2600 + Pn * 1100 + V((0, 0, 1900)), C + V((0, 0, 200)), ln=28)
shot('two_roads', C - Dn * 1500 - Pn * 4200 + V((0, 0, 3200)), C - Dn * 900 - Pn * 3800 + V((0, 0, 2900)), C, ln=30)
shot('cart_track', A - Dn * 900 + Pn * 500 + V((0, 0, 450)), A + Dn * 400 + Pn * 450 + V((0, 0, 520)), A + Dn * 1800 + V((0, 0, 150)), A + Dn * 2800 + V((0, 0, 250)), ln=32)
shot('people', C + Pn * 4500 + V((0, 0, 3600)), C + Pn * 3600 + Dn * 2200 + V((0, 0, 3400)), C, ln=30)
shot('lay_road', C - Pn * 4000 - Dn * 1200 + V((0, 0, 3000)), C - Pn * 3500 + Dn * 600 + V((0, 0, 2800)), C, ln=30)
shot('straight', (A + T_) / 2 + Pn * 5200 + V((0, 0, 900)), (A + T_) / 2 + Pn * 4700 + V((0, 0, 1000)), (A + T_) / 2 + V((0, 0, 200)), ln=30)
shot('hairpins', H - Pn * 900 - Dn * 300 + V((0, 0, 700)), H - Pn * 650 + Dn * 200 + V((0, 0, 560)), H, ln=32)
shot('traffic', C - Dn * 2500 - Pn * 3000 + V((0, 0, 2400)), C - Dn * 2000 - Pn * 2600 + V((0, 0, 2200)), C, ln=30)
shot('second_road', C + Pn * 3500 - Dn * 2500 + V((0, 0, 3000)), C + Pn * 3000 - Dn * 1800 + V((0, 0, 2800)), C, ln=30)
shot('rockfall', RC + Pn * 500 - Dn * 300 + V((0, 0, 330)), RC + Pn * 380 - Dn * 150 + V((0, 0, 260)), RC, ln=32)
shot('old_runs', at(road1_up, 0.55) - Pn * 700 + V((0, 0, 500)), at(road1_up, 0.75) - Pn * 600 + V((0, 0, 480)), at(road1_up, 0.65), at(road1_up, 0.85), ln=30)
fa, fb = S('finale')
K(fa, C - Dn * 4500 - Pn * 3000 + V((0, 0, 3600)), C, 28); K(END, C - Dn * 6500 - Pn * 4500 + V((0, 0, 5200)), C, 26)
starts_ = {k[0] for k in KEYS}
for f, c_, t_, ln in KEYS:
    cam.location = c_; cam.keyframe_insert('location', frame=f); tgt.location = t_; tgt.keyframe_insert('location', frame=f)
    cd.lens = ln; cd.keyframe_insert('lens', frame=f)
ends = {S(l['shot'])[1] for l in plan['lines']}
for idb, path in ((cam, 'location'), (tgt, 'location'), (cd, 'lens')):
    for fc in fcurves(idb):
        if fc.data_path == path:
            for kp in fc.keyframe_points:
                kp.handle_left_type = kp.handle_right_type = 'AUTO_CLAMPED'
                if int(round(kp.co[0])) in ends: kp.interpolation = 'CONSTANT'

# camera targets for overlay labels (projected later in Remotion via a json)
json.dump({'A': list(A), 'T': list(T_), 'H': list(H), 'RC': list(RC)}, open('brief/points.json', 'w'))
sc.render.resolution_x, sc.render.resolution_y = 1080, 1920
sc.view_settings.view_transform = 'AgX'; sc.view_settings.look = 'AgX - Medium High Contrast'
sc.render.image_settings.file_format = 'JPEG'; sc.render.image_settings.quality = 92
try: sc.eevee.volumetric_end = 30000; sc.eevee.volumetric_tile_size = '16'
except Exception: pass
os.makedirs('scene', exist_ok=True)
bpy.ops.wm.save_as_mainfile(filepath=os.path.abspath('scene/ghat.blend'))
print('built', END, SH, 'hairpin_centre', tuple(round(v) for v in H))
