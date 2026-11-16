"""Sri Venkateswara temple complex, Tirumala: an illustration built to the documented layout, on the real spot, facing east.
East to west on one line: Mahadwaram (white five-tier gopuram, seven kalasams) through the outer wall, the gold dhwajasthambham,
Vendivakili (three-tier gopuram) through the inner wall, then the gold three-tier Ananda Nilayam vimana over the sanctum.
Swami Pushkarini tank with its small mandapam lies on the north side. Sizes are enlarged (SCL) so it reads from the air.
Run from build.py (exec). Uses: bpy, sc, math, Vector, random, TP, elev_local, principled, emis. Sets TPTOP, TPAIM, GZ."""
SCL = 1.7
ROOT = bpy.data.objects.new('tpl_root', None); sc.collection.objects.link(ROOT); ROOT.location = (TP.x, TP.y, GZ); ROOT.scale = (SCL, SCL, SCL)
def _pm(name, col, rough, metal=0.0, emit=None, es=0.0):
    m = principled(name, col, rough); b_ = m.node_tree.nodes['Principled BSDF']; b_.inputs['Metallic'].default_value = metal
    if emit: b_.inputs['Emission Color'].default_value = (*emit, 1); b_.inputs['Emission Strength'].default_value = es
    return m
MT = {'stone': _pm('tpl_stone', (0.60, 0.47, 0.33), 0.85), 'white': _pm('tpl_white', (0.95, 0.90, 0.80), 0.7),
      'gold': _pm('tpl_gold', (1.0, 0.62, 0.13), 0.2, 1.0, (1.0, 0.5, 0.1), 1.4), 'roof': _pm('tpl_roof', (0.80, 0.70, 0.55), 0.8),
      'dark': _pm('tpl_dark', (0.05, 0.035, 0.03), 0.9), 'pave': _pm('tpl_pave', (0.74, 0.66, 0.54), 0.9),
      'water': _pm('tpl_water', (0.02, 0.22, 0.30), 0.04, 0.0, (0.02, 0.30, 0.38), 0.25), 'red': _pm('tpl_red', (0.75, 0.16, 0.08), 0.7),
      'lamp': emis('tpl_lamp', (1.0, 0.62, 0.2), 9.0)}
class Acc:
    def __init__(s): s.v = []; s.f = []
    def box(s, cx, cy, z0, sx, sy, sz, taper=1.0):
        n = len(s.v); hx, hy = sx / 2, sy / 2; tx, ty = hx * taper, hy * taper
        s.v += [(cx - hx, cy - hy, z0), (cx + hx, cy - hy, z0), (cx + hx, cy + hy, z0), (cx - hx, cy + hy, z0),
                (cx - tx, cy - ty, z0 + sz), (cx + tx, cy - ty, z0 + sz), (cx + tx, cy + ty, z0 + sz), (cx - tx, cy + ty, z0 + sz)]
        s.f += [(n, n + 3, n + 2, n + 1), (n + 4, n + 5, n + 6, n + 7), (n, n + 1, n + 5, n + 4), (n + 1, n + 2, n + 6, n + 5), (n + 2, n + 3, n + 7, n + 6), (n + 3, n, n + 4, n + 7)]
A_ = {k: Acc() for k in MT}
def prim(o, mat, smooth=True):
    o.data.materials.append(MT[mat]); o.parent = ROOT
    if smooth: o.data.polygons.foreach_set('use_smooth', [True] * len(o.data.polygons))
    o.name = 'tpl_' + o.name; return o
def kalasam(cx, cy, z, s=1.0):
    A_['gold'].box(cx, cy, z, 0.9 * s, 0.9 * s, 0.35 * s); A_['gold'].box(cx, cy, z + 0.35 * s, 0.75 * s, 0.75 * s, 0.9 * s, 1.35)
    A_['gold'].box(cx, cy, z + 1.25 * s, 1.0 * s, 1.0 * s, 0.8 * s, 0.25); A_['gold'].box(cx, cy, z + 2.05 * s, 0.22 * s, 0.22 * s, 1.1 * s, 0.2)
def gopuram(cx, cy, z0, wy, dx, tiers, H, body='white'):
    bh = H * 0.30
    A_['stone'].box(cx, cy, z0, dx, wy, bh); A_['stone'].box(cx, cy, z0 + bh, dx + 0.8, wy + 0.8, 0.5)
    A_['dark'].box(cx, cy, z0, dx + 0.4, wy * 0.27, bh * 0.8)
    for sx_ in (-1, 1):
        A_['gold'].box(cx + sx_ * (dx / 2 + 0.25), cy, z0, 0.25, wy * 0.24, bh * 0.74)
        for sy_ in (-1, 1): A_['white'].box(cx + sx_ * (dx / 2 + 0.2), cy + sy_ * wy * 0.19, z0, 0.5, 0.9, bh * 0.86)
    z = z0 + bh + 0.5; th = H * 0.52 / tiers
    for i in range(tiers):
        k = 1 - 0.12 * i; k2 = 1 - 0.12 * (i + 1); w_, d_ = wy * k, dx * k
        A_[body].box(cx, cy, z, d_, w_, th * 0.8, (k2 / k + 1) / 2); A_[body].box(cx, cy, z + th * 0.8, d_ * 0.97 + 0.7, w_ * 0.97 + 0.7, th * 0.2)
        n = max(3, 7 - i)
        for j in range(n):
            yy = cy - w_ / 2 + w_ * (j + 0.5) / n
            for sx_ in (-1, 1):
                A_[body].box(cx + sx_ * (d_ / 2 + 0.2), yy, z + th * 0.08, 0.6, w_ / n * 0.6, th * 0.62)
                A_['dark'].box(cx + sx_ * (d_ / 2 + 0.52), yy, z + th * 0.14, 0.06, w_ / n * 0.3, th * 0.4)
                A_[body].box(cx + sx_ * (d_ / 2 + 0.2), yy, z + th * 0.70, 0.75, w_ / n * 0.75, th * 0.16, 0.3)
        for sy_ in (-1, 1):
            A_[body].box(cx, cy + sy_ * (w_ / 2 + 0.2), z + th * 0.08, d_ * 0.4, 0.6, th * 0.62); A_['dark'].box(cx, cy + sy_ * (w_ / 2 + 0.52), z + th * 0.14, d_ * 0.2, 0.06, th * 0.4)
        z += th
    tw, td = wy * (1 - 0.12 * tiers), dx * (1 - 0.12 * tiers); rh = H * 0.16
    A_[body].box(cx, cy, z, td, tw, rh * 0.25)
    bpy.ops.mesh.primitive_cylinder_add(vertices=28, radius=1, depth=1, location=(cx, cy, z + rh * 0.25)); o = bpy.context.object
    o.rotation_euler = (math.pi / 2, 0, 0); o.scale = (td / 2, rh, tw); prim(o, body)
    for sy_ in (-1, 1): A_['gold'].box(cx, cy + sy_ * (tw / 2 + 0.05), z + rh * 0.25, td * 0.55, 0.12, rh * 0.8, 0.2)
    nk = 7 if tiers >= 5 else 3
    for j in range(nk): kalasam(cx, cy - tw * 0.42 + tw * 0.84 * j / (nk - 1), z + rh * 1.2, 0.8)
    return z + rh * 1.25 + 2.5
def ring(key, x0, x1, y0, y1, z0, h, t):
    A_[key].box((x0 + x1) / 2, y0 + t / 2, z0, x1 - x0, t, h); A_[key].box((x0 + x1) / 2, y1 - t / 2, z0, x1 - x0, t, h)
    A_[key].box(x0 + t / 2, (y0 + y1) / 2, z0, t, y1 - y0 - 2 * t, h); A_[key].box(x1 - t / 2, (y0 + y1) / 2, z0, t, y1 - y0 - 2 * t, h)
def wall(x0, x1, y0, y1, h, lamps=True):
    ring('stone', x0, x1, y0, y1, 0, h, 1.6); ring('white', x0 - 0.2, x1 + 0.2, y0 - 0.2, y1 + 0.2, h, 0.5, 2.0)
    ring('red', x0 - 0.05, x1 + 0.05, y0 - 0.05, y1 + 0.05, h * 0.45, 0.5, 1.7)
    if lamps:
        P_ = 2 * (x1 - x0 + y1 - y0); n = int(P_ / 3.2)
        for j in range(n):
            s = P_ * j / n
            if s < x1 - x0: px, py = x0 + s, y0
            elif s < x1 - x0 + y1 - y0: px, py = x1, y0 + s - (x1 - x0)
            elif s < 2 * (x1 - x0) + y1 - y0: px, py = x1 - (s - (x1 - x0) - (y1 - y0)), y1
            else: px, py = x0, y1 - (s - 2 * (x1 - x0) - (y1 - y0))
            A_['lamp'].box(px, py, h + 0.5, 0.42, 0.42, 0.42)
def hall(x0, x1, y0, y1, h):
    A_['roof'].box((x0 + x1) / 2, (y0 + y1) / 2, h - 0.8, x1 - x0, y1 - y0, 0.8); A_['white'].box((x0 + x1) / 2, (y0 + y1) / 2, h, x1 - x0 + 0.6, y1 - y0 + 0.6, 0.35)
    nx_, ny_ = max(2, int((x1 - x0) / 3.2)), max(2, int((y1 - y0) / 3.2))
    for i in range(nx_ + 1):
        for j in range(ny_ + 1):
            if 0 < i < nx_ and 0 < j < ny_: continue
            A_['stone'].box(x0 + 0.5 + (x1 - x0 - 1) * i / nx_, y0 + 0.5 + (y1 - y0 - 1) * j / ny_, 0, 0.7, 0.7, h - 0.8)
    A_['dark'].box((x0 + x1) / 2, (y0 + y1) / 2, 0, x1 - x0 - 2.2, y1 - y0 - 2.2, h - 1.0)
# plinth / paving
A_['pave'].box(0, 38, -45, 190, 216, 45)
# outer wall, Mahadwaram, inner wall, Vendivakili
wall(-63, 63, -40, 40, 7.5); wall(-46, 30, -26, 26, 6.5)
gopuram(63, 0, 0, 17, 11, 5, 23); gopuram(30, 0, 0, 11, 8, 3, 14)
# dhwajasthambham (gold flag pillar) and bali peetham
bpy.ops.mesh.primitive_cylinder_add(vertices=16, radius=0.55, depth=15, location=(46, 0, 7.5)); prim(bpy.context.object, 'gold')
A_['stone'].box(46, 0, 0, 3.2, 3.2, 1.6, 0.8); kalasam(46, 0, 15, 0.7); A_['gold'].box(50.5, 0, 0, 2.0, 2.0, 1.8, 0.6)
# halls: Tirumala Raya mantapam side, Ranga mantapam side, inner corridors
hall(36, 58, 12, 34, 6.5); hall(36, 58, -34, -12, 6.5); hall(-42, 22, 14, 23, 5.5); hall(-42, 22, -23, -14, 5.5); hall(2, 26, -9, 9, 6.0)
# Ananda Nilayam: gold three-tier vimana over the sanctum
vx = -20; A_['stone'].box(vx, 0, 0, 17, 17, 7.5); A_['white'].box(vx, 0, 7.5, 18, 18, 0.5); z = 8.0
for s, h in ((15.0, 4.2), (11.6, 3.7), (8.6, 3.2)):
    A_['gold'].box(vx, 0, z, s, s, h * 0.78, 0.9); A_['gold'].box(vx, 0, z + h * 0.78, s * 0.92 + 0.8, s * 0.92 + 0.8, h * 0.22)
    for ax in (-1, 1):
        for ay in (-1, 1):
            A_['gold'].box(vx + ax * s * 0.46, ay * s * 0.46, z + h * 0.15, 1.5, 1.5, h * 0.75); A_['gold'].box(vx + ax * s * 0.46, ay * s * 0.46, z + h * 0.9, 1.7, 1.7, 0.9, 0.2)
    for ax, ay in ((1, 0), (-1, 0), (0, 1), (0, -1)):
        A_['gold'].box(vx + ax * s * 0.5, ay * s * 0.5, z + h * 0.1, 0.7 if ax else 2.6, 0.7 if ay else 2.6, h * 0.7); A_['dark'].box(vx + ax * (s * 0.5 + 0.36), ay * (s * 0.5 + 0.36), z + h * 0.18, 0.06 if ax else 1.3, 0.06 if ay else 1.3, h * 0.45)
        A_['gold'].box(vx + ax * s * 0.5, ay * s * 0.5, z + h * 0.8, 1.0 if ax else 3.0, 1.0 if ay else 3.0, 1.0, 0.3)
    z += h
A_['gold'].box(vx, 0, z, 6.2, 6.2, 1.3, 0.9)
bpy.ops.mesh.primitive_uv_sphere_add(segments=32, ring_count=16, radius=3.7, location=(vx, 0, z + 3.6)); o = bpy.context.object; o.scale = (1, 1, 1.12); prim(o, 'gold')
kalasam(vx, 0, z + 7.5, 1.3); VTOP = z + 11.0
# small shrines in the inner court (Varadaraja, Yoga Narasimha sides) with gold kalasams
for sx_, sy_ in ((-38, 8), (10, -18.5), (-38, -8)):
    A_['white'].box(sx_, sy_, 0, 5, 5, 5); A_['white'].box(sx_, sy_, 5, 4.2, 4.2, 2.2, 0.55); kalasam(sx_, sy_, 7.2, 0.6)
# Swami Pushkarini on the north side: stepped tank, water, mandapam in the middle
tx0, tx1, ty0, ty1 = -42, 48, 62, 132
for k in range(5): ring('stone', tx0 + 2.6 * k, tx1 - 2.6 * k, ty0 + 2.6 * k, ty1 - 2.6 * k, 0, 2.0 - 0.38 * k, 2.7)
ring('white', tx0 - 0.3, tx1 + 0.3, ty0 - 0.3, ty1 + 0.3, 2.0, 0.45, 1.2)
A_['water'].box((tx0 + tx1) / 2, (ty0 + ty1) / 2, 0, tx1 - tx0 - 24, ty1 - ty0 - 24, 0.35)
mx_, my_ = (tx0 + tx1) / 2, (ty0 + ty1) / 2
A_['stone'].box(mx_, my_, 0, 9, 9, 1.2)
for ax in (-1, 1):
    for ay in (-1, 1): A_['stone'].box(mx_ + ax * 3.4, my_ + ay * 3.4, 1.2, 0.8, 0.8, 4.2)
A_['roof'].box(mx_, my_, 5.4, 9.4, 9.4, 0.7); A_['white'].box(mx_, my_, 6.1, 6.5, 6.5, 2.4, 0.5); kalasam(mx_, my_, 8.5, 0.7)
for k_, a_ in A_.items():
    if not a_.v: continue
    me_ = bpy.data.meshes.new('tpl_' + k_); me_.from_pydata(a_.v, [], a_.f); me_.update()
    o = bpy.data.objects.new('tpl_' + k_, me_); sc.collection.objects.link(o); o.data.materials.append(MT[k_]); o.parent = ROOT
# trees around the complex (Poly Haven, already loaded for the close sets)
try:
    srcs = [o for o in TREES.objects if o.type == 'MESH']; rt = random.Random(5)
    for i in range(70):
        if i < 44:
            a_ = rt.uniform(0, 2 * math.pi); px = math.cos(a_) * rt.uniform(118, 150); py = 38 + math.sin(a_) * rt.uniform(128, 160)
        else: px = rt.uniform(-88, 88); py = rt.choice((rt.uniform(44, 57), rt.uniform(-58, -45)))
        s_ = srcs[i % len(srcs)]; t_o = s_.copy(); sc.collection.objects.link(t_o)
        wx, wy_ = TP.x + px * SCL, TP.y + py * SCL
        inside = abs(px) < 95 and -70 < py < 146
        t_o.location = (wx, wy_, GZ if inside else elev_local(wx, wy_)); k_ = rt.uniform(1.5, 2.6); t_o.scale = (k_, k_, k_); t_o.rotation_euler = (0, 0, rt.uniform(0, 6.28)); t_o.name = f'tpl_tree{i}'
except Exception as ex_: print('temple trees skipped', ex_)
TPTOP = Vector((TP.x + vx * SCL, TP.y, GZ + VTOP * SCL)); TPAIM = Vector((TP.x + 8 * SCL, TP.y, GZ + 13 * SCL))
print('TEMPLE ground', round(GZ), 'dem at temple', round(TP.z), 'top', round(TPTOP.z))
