# Indian garment library for MPFB: cloth-simulated on the base human, saved as .mhclo so every
# character (any body, any pose) can wear them. Output: <MPFB user data>/clothes/ind_<name>/
import bpy, bmesh, math, os, uuid, traceback
from mathutils import Vector
bpy.ops.preferences.addon_enable(module='bl_ext.user_default.mpfb')
from bl_ext.user_default.mpfb.services.humanservice import HumanService
from bl_ext.user_default.mpfb.services.clothesservice import ClothesService
from bl_ext.user_default.mpfb.services.locationservice import LocationService
UD = LocationService.get_user_data()
ONLY = os.environ.get('ONLY', '')

def fresh():
    for o in list(bpy.data.objects): bpy.data.objects.remove(o)
def body_pts(bm):
    dg = bpy.context.evaluated_depsgraph_get(); ev = bm.evaluated_get(dg); me = ev.to_mesh()
    vg = bm.vertex_groups['body'].index; M = bm.matrix_world
    pts = [M @ v.co for v in me.vertices if any(g.group == vg and g.weight > 0.5 for g in v.groups)]
    ev.to_mesh_clear(); return pts
def ext(pts, z0, z1, xmax=None):
    s = [p for p in pts if z0 <= p.z < z1 and (xmax is None or abs(p.x) < xmax)]
    xs = [p.x for p in s]; ys = [p.y for p in s]
    return (min(xs) + max(xs)) / 2, (min(ys) + max(ys)) / 2, (max(xs) - min(xs)) / 2, (max(ys) - min(ys)) / 2

def grid_obj(name, cols, rows, fn, pin_rows=(), pin_fn=None):
    """Quad grid; fn(u, v) -> Vector (u around 0..1, v down 0..1). UV = (u, 1 - v)."""
    me = bpy.data.meshes.new(name); b = bmesh.new(); uv = b.loops.layers.uv.new('UVMap')
    V = [[b.verts.new(fn(i / cols, j / rows)) for i in range(cols + 1)] for j in range(rows + 1)]
    for j in range(rows):
        for i in range(cols):
            f = b.faces.new((V[j][i], V[j][i + 1], V[j + 1][i + 1], V[j + 1][i]))
            for l, (ii, jj) in zip(f.loops, ((i, j), (i + 1, j), (i + 1, j + 1), (i, j + 1))): l[uv].uv = (ii / cols, 1 - jj / rows)
    b.to_mesh(me); b.free(); o = bpy.data.objects.new(name, me); bpy.context.collection.objects.link(o)
    pin = o.vertex_groups.new(name='pin'); n = cols + 1
    for idx in range(len(me.vertices)):
        j, i = divmod(idx, n)
        w = 1.0 if j in pin_rows else (pin_fn(i / cols, j / rows) if pin_fn else 0.0)
        if w > 0: pin.add([idx], w, 'REPLACE')
    return o

def simulate(o, bm, frames=45, stiff=12.0, bend=0.4, mass=0.25):
    col = bm.modifiers.new('col', 'COLLISION'); bm.collision.thickness_outer = 0.006; bm.collision.cloth_friction = 8
    c = o.modifiers.new('Cloth', 'CLOTH'); s = c.settings
    s.quality = 6; s.mass = mass; s.tension_stiffness = s.compression_stiffness = stiff; s.shear_stiffness = stiff * 0.5
    s.bending_stiffness = bend; s.vertex_group_mass = 'pin'; s.air_damping = 2
    c.collision_settings.distance_min = 0.004; c.collision_settings.use_self_collision = False
    c.point_cache.frame_start = 1; c.point_cache.frame_end = frames
    for f in range(1, frames + 1): bpy.context.scene.frame_set(f)
    bpy.context.view_layer.objects.active = o; o.select_set(True)
    bpy.ops.object.modifier_apply(modifier='Cloth'); bm.modifiers.remove(col)
    o.vertex_groups.remove(o.vertex_groups['pin'])
    g = o.vertex_groups.new(name='body'); g.add(list(range(len(o.data.vertices))), 1.0, 'REPLACE')

def save(o, bm, name, desc):
    o.scale = bm.scale
    rep = ClothesService.mesh_is_valid_as_clothes(o, bm); print('VALID', name, rep['all_checks_ok'], rep['warnings'][:3])
    mh = ClothesService.create_mhclo_from_clothes_matching(bm, o, properties_dict={'name': name, 'description': desc, 'license': 'CC0', 'author': 'r3d', 'uuid': str(uuid.uuid4())})
    d = os.path.join(UD, 'clothes', name); os.makedirs(d, exist_ok=True)
    mh.write_mhclo(os.path.join(d, name + '.mhclo'), also_export_mhmat=True, also_export_obj=True)
    print('SAVED', name, os.listdir(d))

def make_base(gender):
    fresh()
    bm = HumanService.create_human(mask_helpers=True, feet_on_ground=True, scale=0.1, macro_detail_dict={'gender': gender, 'age': 0.5, 'muscle': 0.5, 'weight': 0.5, 'height': 0.5, 'proportions': 0.5, 'cupsize': 0.5, 'firmness': 0.5, 'race': {'african': 0.33, 'asian': 0.33, 'caucasian': 0.34}})
    bpy.context.view_layer.update(); P = body_pts(bm); H = max(p.z for p in P); return bm, P, H

def tube(name, P, H, top, bot, ease, flare, pleat_amp, cols=64, rows=36, front_pleats=True):
    cx, cy, rx0, ry0 = ext(P, top - 0.015, top + 0.015, xmax=0.25)
    def fn(u, v):
        z = top + (bot - top) * v
        rx = rx0 + ease + flare * v ** 1.3; ry = ry0 + ease + flare * 0.8 * v ** 1.3
        a = 2 * math.pi * u - math.pi / 2           # u=0 at the front (-y)
        fr = max(0.0, math.cos(a + math.pi / 2)) if front_pleats else 0.0   # 1 at front centre
        pl = 1 + pleat_amp * fr ** 2 * math.sin(u * 2 * math.pi * 22) * min(1, v * 4)
        return Vector((cx + rx * pl * math.cos(a), cy + ry * pl * math.sin(a), z))
    return grid_obj(name, cols, rows, fn, pin_rows=(0,))

def strip(name, pts, width, cols=6, rows=40, pin_ends=(True, False)):
    """Ribbon along a polyline of Vectors (crossed by width), pinned at chosen ends."""
    def at(v):
        t = v * (len(pts) - 1); k = min(int(t), len(pts) - 2); f = t - k
        p = pts[k].lerp(pts[k + 1], f); d = (pts[k + 1] - pts[k]).normalized()
        side = d.cross(Vector((0, 0, 1))); side = side.normalized() if side.length > 1e-4 else Vector((1, 0, 0))
        return p, side
    def fn(u, v): p, s = at(v); return p + s * (u - 0.5) * width
    def pf(u, v): return 1.0 if (pin_ends[0] and v < 0.04) or (pin_ends[1] and v > 0.96) else 0.0
    return grid_obj(name, cols, rows, fn, pin_fn=pf)

def join(objs):
    bpy.ops.object.select_all(action='DESELECT')
    for o in objs: o.select_set(True)
    bpy.context.view_layer.objects.active = objs[0]; bpy.ops.object.join(); return objs[0]

jobs = []
def job(f): jobs.append(f); return f

@job
def ind_dhoti():      # Telugu panche: ankle length, front pleats, pinned at the waist
    bm, P, H = make_base(1.0)
    o = tube('ind_dhoti', P, H, H * 0.565, H * 0.04, 0.012, 0.07, 0.10)
    simulate(o, bm, stiff=10, bend=0.3); save(o, bm, 'ind_dhoti', 'White cotton panche/dhoti with front pleats')
@job
def ind_kingdhoti():  # royal pattu dhoti, slightly fuller, mid-calf
    bm, P, H = make_base(1.0)
    o = tube('ind_kingdhoti', P, H, H * 0.57, H * 0.11, 0.015, 0.09, 0.14)
    simulate(o, bm, stiff=14, bend=0.6); save(o, bm, 'ind_kingdhoti', 'Silk dhoti for kings, mid-calf, deep front pleats')
@job
def ind_sareeskirt(): # nivi saree lower part: floor length, fan pleats at front
    bm, P, H = make_base(0.0)
    o = tube('ind_sareeskirt', P, H, H * 0.575, H * 0.005, 0.01, 0.10, 0.16)
    simulate(o, bm, stiff=8, bend=0.15); save(o, bm, 'ind_sareeskirt', 'Saree lower drape with front fan pleats')
@job
def ind_pallu():      # pallu: right hip -> across chest -> over left shoulder -> down the back
    bm, P, H = make_base(0.0)
    cx, cy, rx, ry = ext(P, H * 0.80, H * 0.82, xmax=0.22)
    sh = Vector((cx + rx * 0.55, cy, H * 0.835))   # model's left shoulder is +x
    path = [Vector((cx - rx * 0.9, cy - ry - 0.03, H * 0.58)), Vector((cx - rx * 0.2, cy - ry - 0.05, H * 0.70)),
            Vector((cx + rx * 0.35, cy - ry - 0.02, H * 0.79)), sh + Vector((0, 0, 0.03)),
            Vector((cx + rx * 0.6, cy + ry + 0.05, H * 0.76)), Vector((cx + rx * 0.6, cy + ry + 0.08, H * 0.45))]
    o = strip('ind_pallu', path, 0.24, cols=8, rows=48, pin_ends=(True, False))
    pin = o.vertex_groups['pin']
    for v in o.data.vertices:   # also pin across the shoulder so it stays put
        if (v.co - sh).length < 0.09: pin.add([v.index], 1.0, 'REPLACE')
    simulate(o, bm, frames=40, stiff=6, bend=0.1); save(o, bm, 'ind_pallu', 'Saree pallu over the left shoulder')
@job
def ind_uttariyam():  # angavastram/uttariyam: stole around the back of the neck, both ends down the front
    bm, P, H = make_base(1.0)
    cx, cy, rx, ry = ext(P, H * 0.82, H * 0.84, xmax=0.2)
    nk = ext(P, H * 0.855, H * 0.87, xmax=0.1)
    L = [Vector((cx - rx * 0.45, cy - ry - 0.01, H * 0.52)), Vector((cx - rx * 0.4, cy - ry - 0.02, H * 0.74)), Vector((nk[0] - nk[2] - 0.03, nk[1], H * 0.85)),
         Vector((nk[0], nk[1] + nk[3] + 0.03, H * 0.86)), Vector((nk[0] + nk[2] + 0.03, nk[1], H * 0.85)),
         Vector((cx + rx * 0.4, cy - ry - 0.02, H * 0.74)), Vector((cx + rx * 0.45, cy - ry - 0.01, H * 0.52))]
    o = strip('ind_uttariyam', L, 0.13, cols=6, rows=56, pin_ends=(False, False))
    pin = o.vertex_groups['pin']
    for v in o.data.vertices:
        if v.co.z > H * 0.82: pin.add([v.index], 1.0, 'REPLACE')
    simulate(o, bm, frames=35, stiff=8, bend=0.2); save(o, bm, 'ind_uttariyam', 'Angavastram / uttariyam stole')

for f in jobs:
    if ONLY and f.__name__ not in ONLY.split(','): continue
    try: f()
    except Exception: traceback.print_exc()
print('GARMENTS_DONE')
