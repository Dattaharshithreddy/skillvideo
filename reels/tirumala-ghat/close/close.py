"""Close-up road sets, run from build.py (exec) after the aerial scene and cameras exist.
Each set is a 2 m-grid terrain patch around a real point of the ghat road, the road carved into it, a road ribbon
(asphalt today, red laterite dirt in 1944 shots), parapet walls, rock-cut faces, Poly Haven trees/shrubs/boulders, and
Sketchfab vehicles (CC-BY) driving the real road line. Close shots get their own cameras, switched with timeline markers.
Uses names from build.py: sc, S, fr, END, R, DN, UP, loc, elev_local, emis, principled, show, fcurves, terr, meta, OX, OY, plan, H, RC, A."""
import bpy, json, math, os, random
import numpy as np
from mathutils import Vector
random.seed(11); rng = np.random.default_rng(11)
PH = '/opt/reel/assets/ph/'; SF = '/opt/reel/assets/sf/'
OLD_SHOTS = ['cart_track', 'people', 'lay_road', 'straight', 'hairpins', 'traffic']
def in_old(f): return any(S(n)[0] <= f <= S(n)[1] for n in OLD_SHOTS)

# aerial-only overlays (glowing road lines, track dots, light-dot traffic, big aerial boulders, beacons) hide in close shots
AERIAL = [o for o in sc.objects if o.type in ('MESH', 'CURVE') and o.name != 'terrain' and not o.name.startswith(('Sphere', 'Cylinder', 'path_'))]
CLOSE_SHOTS = ['open', 'traffic', 'old_runs', 'cart_track', 'rockfall']
def key_hidden(o, hidden_in):
    prev = None
    for l_ in plan['lines']:
        a_ = S(l_['shot'])[0]; h_ = hidden_in(l_['shot'])
        if h_ != prev: o.hide_render = h_; o.keyframe_insert('hide_render', frame=a_); prev = h_
    for fc in fcurves(o):
        if fc.data_path == 'hide_render':
            for kp in fc.keyframe_points: kp.interpolation = 'CONSTANT'
for o in AERIAL: key_hidden(o, lambda n: n in CLOSE_SHOTS)

# ---------------- road segments (local coords, z = ground) ----------------
def pts_of(raw):
    return [Vector((x - OX, y - OY, elev_local(x - OX, y - OY))) for x, y, z, d in raw]
DNp = pts_of(DN)                       # 1944 road, listed top -> bottom (today: downhill one-way)
UPp = pts_of(UP)                       # 1974 road, bottom -> top (uphill one-way)
def resample(pts, step=2.0):
    out = [pts[0]]
    for a, b in zip(pts, pts[1:]):
        L = (b - a).length; n = max(1, int(L / step))
        for k in range(1, n + 1): out.append(a.lerp(b, k / n))
    return out
def smooth_z(pts, k=6):
    zs = np.array([p.z for p in pts]); ker = np.ones(2 * k + 1) / (2 * k + 1)
    zz = np.convolve(np.pad(zs, k, mode='edge'), ker, mode='valid')
    return [Vector((p.x, p.y, z)) for p, z in zip(pts, zz)]
def segment(pts, centre, radius):
    idx = [i for i, p in enumerate(pts) if (p.xy - centre.xy).length < radius]
    if not idx: return []
    i0, i1 = min(idx), max(idx)
    return smooth_z(resample(pts[i0:i1 + 1]))
def curvature_pick(pts, dmin, dmax, raw):
    best, bi = -1, None
    for i in range(3, len(pts) - 3):
        if not (dmin <= raw[i][3] <= dmax): continue
        a = (pts[i] - pts[i - 3]).xy.normalized(); b = (pts[i + 3] - pts[i]).xy.normalized()
        c = 1 - a.dot(b)
        if c > best: best, bi = c, i
    return pts[bi] if bi is not None else pts[len(pts) // 2]

# ---------------- materials ----------------
def img(nt, path, non_color=False, vec=None):
    t = nt.nodes.new('ShaderNodeTexImage'); t.image = bpy.data.images.load(path)
    if non_color: t.image.colorspace_settings.name = 'Non-Color'
    if vec is not None: nt.links.new(vec, t.inputs['Vector'])
    return t
def tiled(nt, scale):
    tc = nt.nodes.new('ShaderNodeTexCoord'); mp = nt.nodes.new('ShaderNodeMapping'); mp.inputs['Scale'].default_value = (scale, scale, scale)
    nt.links.new(tc.outputs['Object'], mp.inputs['Vector']); return mp.outputs['Vector']
def pbr_tex(name, folder, scale, rough_default=0.8):
    m = bpy.data.materials.new(name); m.use_nodes = True; nt = m.node_tree; b = nt.nodes['Principled BSDF']
    v = tiled(nt, scale); d = img(nt, f'{PH}t/{folder}/Diffuse.jpg', vec=v); nt.links.new(d.outputs['Color'], b.inputs['Base Color'])
    if os.path.exists(f'{PH}t/{folder}/Rough.jpg'):
        r = img(nt, f'{PH}t/{folder}/Rough.jpg', True, v); nt.links.new(r.outputs['Color'], b.inputs['Roughness'])
    else: b.inputs['Roughness'].default_value = rough_default
    if os.path.exists(f'{PH}t/{folder}/nor_gl.jpg'):
        n = img(nt, f'{PH}t/{folder}/nor_gl.jpg', True, v); nm = nt.nodes.new('ShaderNodeNormalMap'); nm.inputs['Strength'].default_value = 1.0
        nt.links.new(n.outputs['Color'], nm.inputs['Color']); nt.links.new(nm.outputs['Normal'], b.inputs['Normal'])
    return m, nt, b, d
# road: asphalt today, red laterite dirt in 1944 shots (keyed 'era' value)
M_road, nt, b, d_as = pbr_tex('road_close', 'asphalt_04', 0.25)
dirt = img(nt, f'{PH}t/red_laterite_soil_stones/Diffuse.jpg', vec=tiled(nt, 0.3))
era_r = nt.nodes.new('ShaderNodeValue'); era_r.name = 'era'
mx = nt.nodes.new('ShaderNodeMix'); mx.data_type = 'RGBA'; nt.links.new(era_r.outputs[0], mx.inputs['Factor'])
dk = nt.nodes.new('ShaderNodeMix'); dk.data_type = 'RGBA'; dk.blend_type = 'MULTIPLY'; dk.inputs['Factor'].default_value = 1.0; dk.inputs[7].default_value = (0.5, 0.5, 0.52, 1)
nt.links.new(d_as.outputs['Color'], dk.inputs[6])
nt.links.new(dk.outputs[2], mx.inputs[6]); nt.links.new(dirt.outputs['Color'], mx.inputs[7]); nt.links.new(mx.outputs[2], b.inputs['Base Color'])
# ground: satellite colour from far, forest-floor / laterite detail near, rock face on steep cuts
def ground_material():
    m = bpy.data.materials.new('ground_close'); m.use_nodes = True; nt = m.node_tree; b = nt.nodes['Principled BSDF']
    b.inputs['Roughness'].default_value = 0.95
    uv = nt.nodes.new('ShaderNodeUVMap'); uv.uv_map = 'UV'
    sat = img(nt, os.path.abspath('geo/gm.jpg' if os.path.exists('geo/gm.jpg') else 'geo/s2.png'), vec=uv.outputs['UV'])
    v = tiled(nt, 0.22)
    g1 = img(nt, f'{PH}t/sparse_grass/Diffuse.jpg', vec=v); g2 = img(nt, f'{PH}t/forrest_ground_01/Diffuse.jpg', vec=v)
    rk = img(nt, f'{PH}t/rock_face_03/Diffuse.jpg', vec=tiled(nt, 0.12))
    nz = nt.nodes.new('ShaderNodeTexNoise'); nz.inputs['Scale'].default_value = 0.03; nt.links.new(nt.nodes.new('ShaderNodeTexCoord').outputs['Object'], nz.inputs['Vector'])
    gm = nt.nodes.new('ShaderNodeMix'); gm.data_type = 'RGBA'; nt.links.new(nz.outputs['Fac'], gm.inputs['Factor'])
    nt.links.new(g1.outputs['Color'], gm.inputs[6]); nt.links.new(g2.outputs['Color'], gm.inputs[7])
    # tint the detail with the satellite colour (keeps the aerial look), then rock on steep faces
    bw = nt.nodes.new('ShaderNodeRGBToBW'); nt.links.new(gm.outputs[2], bw.inputs[0])
    gain = nt.nodes.new('ShaderNodeMath'); gain.operation = 'MULTIPLY'; gain.inputs[1].default_value = 2.4; nt.links.new(bw.outputs[0], gain.inputs[0])
    tint = nt.nodes.new('ShaderNodeMix'); tint.data_type = 'RGBA'; tint.blend_type = 'MULTIPLY'; tint.inputs['Factor'].default_value = 1.0
    nt.links.new(sat.outputs['Color'], tint.inputs[6]); nt.links.new(gain.outputs[0], tint.inputs[7])
    grn = nt.nodes.new('ShaderNodeMix'); grn.data_type = 'RGBA'; grn.blend_type = 'MULTIPLY'; grn.inputs['Factor'].default_value = 1.0; grn.inputs[7].default_value = (0.55, 0.85, 0.35, 1)
    nt.links.new(gm.outputs[2], grn.inputs[6])
    blend = nt.nodes.new('ShaderNodeMix'); blend.data_type = 'RGBA'; blend.inputs['Factor'].default_value = 0.75
    nt.links.new(tint.outputs[2], blend.inputs[6]); nt.links.new(grn.outputs[2], blend.inputs[7])
    geo = nt.nodes.new('ShaderNodeNewGeometry'); sep = nt.nodes.new('ShaderNodeSeparateXYZ'); nt.links.new(geo.outputs['Normal'], sep.inputs[0])
    steep = nt.nodes.new('ShaderNodeMapRange'); steep.inputs['From Min'].default_value = 0.82; steep.inputs['From Max'].default_value = 0.62
    nt.links.new(sep.outputs['Z'], steep.inputs['Value'])
    fin = nt.nodes.new('ShaderNodeMix'); fin.data_type = 'RGBA'; nt.links.new(steep.outputs['Result'], fin.inputs['Factor'])
    nt.links.new(blend.outputs[2], fin.inputs[6]); nt.links.new(rk.outputs['Color'], fin.inputs[7]); nt.links.new(fin.outputs[2], b.inputs['Base Color'])
    return m
M_ground = ground_material()
M_white = principled('parapet_white', (0.85, 0.85, 0.82), 0.7); M_black = principled('parapet_black', (0.03, 0.03, 0.03), 0.6)
M_stone = principled('km_stone', (0.9, 0.88, 0.8), 0.8)

# ---------------- set builder ----------------
SQ = 300.0; STEP = 2.0
def build_set(name, centre, road, width, lower_main=True):
    """Terrain patch (2 m grid) around centre with the road carved in; returns (patch object, road object, dist-to-road per vertex)."""
    n = int(2 * SQ / STEP) + 1
    xs = centre.x - SQ + np.arange(n) * STEP; ys = centre.y - SQ + np.arange(n) * STEP
    X, Y = np.meshgrid(xs, ys)
    Z = np.vectorize(elev_local)(X, Y).astype(np.float64)
    # fine noise so the ground is not glassy
    Z += (rng.random(Z.shape) - 0.5) * 0.35
    RP = np.array([[p.x, p.y, p.z] for p in road])
    D = np.full(X.shape, 1e9); ZR = np.zeros(X.shape)
    for i0 in range(0, len(RP), 200):
        seg = RP[i0:i0 + 200]
        dd = np.sqrt((X[..., None] - seg[:, 0]) ** 2 + (Y[..., None] - seg[:, 1]) ** 2)
        k = dd.argmin(-1); m = dd.min(-1); better = m < D
        D[better] = m[better]; ZR[better] = seg[k[better], 2]
    half = width / 2 + 0.8
    w_ = np.clip((D - half) / 14.0, 0, 1); w_ = w_ * w_ * (3 - 2 * w_)        # smoothstep blend from road bed to natural ground
    Z = ZR * (1 - w_) + Z * w_ - 0.12 * (D < half)
    # edges sink a little so the patch tucks under the main terrain seam
    edge = np.minimum.reduce([X - xs[0], xs[-1] - X, Y - ys[0], ys[-1] - Y]); Z -= np.clip((25 - edge) / 25, 0, 1) * 0.6
    verts = np.stack([X.ravel(), Y.ravel(), Z.ravel()], 1).astype(np.float32)
    ii = np.arange(n * n).reshape(n, n)
    quads = np.stack([ii[:-1, :-1].ravel(), ii[:-1, 1:].ravel(), ii[1:, 1:].ravel(), ii[1:, :-1].ravel()], 1)
    me = bpy.data.meshes.new(name + '_ground'); me.vertices.add(len(verts)); me.vertices.foreach_set('co', verts.ravel())
    me.loops.add(quads.size); me.loops.foreach_set('vertex_index', quads.ravel().astype(np.int32))
    me.polygons.add(len(quads)); me.polygons.foreach_set('loop_start', np.arange(0, quads.size, 4, dtype=np.int32)); me.polygons.foreach_set('loop_total', np.full(len(quads), 4, np.int32))
    vi = quads.ravel(); gx = X.ravel()[vi] + OX; gy = Y.ravel()[vi] + OY
    uv = me.uv_layers.new(name='UV')
    uv.data.foreach_set('uv', np.stack([(gx - meta['x0']) / (meta['x1'] - meta['x0']), (gy - meta['y0']) / (meta['y1'] - meta['y0'])], 1).astype(np.float32).ravel())
    me.update(); me.validate(); me.polygons.foreach_set('use_smooth', [True] * len(me.polygons))
    a = me.attributes.new('veg', 'FLOAT', 'POINT'); vg = np.clip((D - (half + 4)) / 10, 0, 1) * np.clip((75 - D) / 15, 0, 1) * (0.5 + 0.5 * rng.random(D.shape))
    a.data.foreach_set('value', vg.ravel().astype(np.float32))
    ob = bpy.data.objects.new(name + '_ground', me); sc.collection.objects.link(ob); ob.data.materials.append(M_ground)
    if lower_main:   # hide the coarse terrain under the patch
        tv = np.empty(len(terr.data.vertices) * 3, np.float32); terr.data.vertices.foreach_get('co', tv); tv = tv.reshape(-1, 3)
        inside = (np.abs(tv[:, 0] - centre.x) < SQ - 22) & (np.abs(tv[:, 1] - centre.y) < SQ - 22); tv[inside, 2] -= 6.0
        terr.data.vertices.foreach_set('co', tv.ravel()); terr.data.update()
    # road ribbon
    rv, rf = [], []
    for i, p in enumerate(road):
        t = (road[min(i + 1, len(road) - 1)] - road[max(i - 1, 0)]); t.z = 0; t = t.normalized(); nn = Vector((-t.y, t.x, 0))
        rv += [tuple(p + nn * width / 2 + Vector((0, 0, 0.12))), tuple(p - nn * width / 2 + Vector((0, 0, 0.12)))]
        if i: rf.append((2 * i - 2, 2 * i - 1, 2 * i + 1, 2 * i))
    rm = bpy.data.meshes.new(name + '_road'); rm.from_pydata(rv, [], rf); rm.update()
    ro = bpy.data.objects.new(name + '_road', rm); sc.collection.objects.link(ro); ro.data.materials.append(M_road)
    return ob, ro, D

def parapets(name, road, width, ranges):
    """Low white-and-black parapet blocks on the downhill edge, like the ghat road walls."""
    objs = []
    acc = 0.0
    for i in range(1, len(road) - 1):
        p = road[i]; t = (road[i + 1] - road[i - 1]); t.z = 0; t = t.normalized(); nn = Vector((-t.y, t.x, 0))
        acc += (road[i] - road[i - 1]).length
        if acc < 2.6: continue
        acc = 0.0
        side = nn if elev_local(*(p + nn * 8).xy) < elev_local(*(p - nn * 8).xy) else -nn     # downhill side
        c = p + side * (width / 2 + 0.45) + Vector((0, 0, 0.45))
        bpy.ops.mesh.primitive_cube_add(size=1, location=c); o = bpy.context.object; o.scale = (0.45, 2.0, 0.75)
        o.rotation_euler = (0, 0, math.atan2(t.y, t.x) - math.pi / 2)
        o.data.materials.append(M_white if (len(objs) // 1) % 2 == 0 else M_black); objs.append(o)
    for o in objs: show(o, ranges)
    return objs

# ---------------- Poly Haven scatter (trees, shrubs, boulders) ----------------
def ph_collection(name, keys, ratio):
    c = bpy.data.collections.new(name); sc.collection.children.link(c); bpy.context.view_layer.layer_collection.children[name].exclude = True
    for k in keys:
        before = set(bpy.data.objects); bpy.ops.import_scene.gltf(filepath=f'{PH}m/{k}/{k}.gltf')
        new = [o for o in bpy.data.objects if o not in before]; names = [o.name for o in new]; meshes = [o for o in new if o.type == 'MESH']
        bpy.ops.object.select_all(action='DESELECT')
        for o in meshes: o.select_set(True)
        bpy.context.view_layer.objects.active = meshes[0]
        if len(meshes) > 1: bpy.ops.object.join()
        ob = bpy.context.view_layer.objects.active; ob.parent = None; bpy.ops.object.transform_apply(location=False, rotation=True, scale=True)
        if ratio < 1: dm = ob.modifiers.new('d', 'DECIMATE'); dm.ratio = ratio; bpy.ops.object.modifier_apply(modifier='d')
        ob.location = (0, 0, 0); ob.name = k
        for cc in list(ob.users_collection): cc.objects.unlink(ob)
        c.objects.link(ob)
        for nme in names:
            o = bpy.data.objects.get(nme)
            if o is not None and o != ob: bpy.data.objects.remove(o, do_unlink=True)
        for m in ob.data.materials:
            if m: m.surface_render_method = 'DITHERED'
    return c
TREES = ph_collection('close_trees', ['island_tree_01', 'island_tree_02', 'tree_small_02'], 0.06)
SHRUBS = ph_collection('close_shrubs', ['shrub_01', 'shrub_02', 'shrub_03', 'shrub_04', 'wild_rooibos_bush', 'boulder_01'], 0.3)
GRASSC = ph_collection('close_grass', ['grass_medium_01', 'grass_medium_02'], 0.35)
def scatter(ob):
    ng = bpy.data.node_groups.new(ob.name + '_scatter', 'GeometryNodeTree')
    ng.interface.new_socket('Geometry', in_out='INPUT', socket_type='NodeSocketGeometry'); ng.interface.new_socket('Geometry', in_out='OUTPUT', socket_type='NodeSocketGeometry')
    N, L = ng.nodes, ng.links; gi = N.new('NodeGroupInput'); go = N.new('NodeGroupOutput'); j = N.new('GeometryNodeJoinGeometry'); L.new(gi.outputs[0], j.inputs[0])
    for coll, dens, s0, s1, seed in ((TREES, 1 / 16, 0.8, 1.6, 3), (SHRUBS, 1 / 8, 0.7, 1.7, 4), (GRASSC, 1 / 4, 0.8, 1.8, 5)):
        na = N.new('GeometryNodeInputNamedAttribute'); na.data_type = 'FLOAT'; na.inputs['Name'].default_value = 'veg'
        mul = N.new('ShaderNodeMath'); mul.operation = 'MULTIPLY'; mul.inputs[1].default_value = dens; L.new(next(o_ for o_ in na.outputs if o_.enabled), mul.inputs[0])
        dp = N.new('GeometryNodeDistributePointsOnFaces'); dp.distribute_method = 'RANDOM'; dp.inputs['Seed'].default_value = seed
        L.new(gi.outputs[0], dp.inputs['Mesh']); L.new(mul.outputs[0], dp.inputs['Density'])
        ci = N.new('GeometryNodeCollectionInfo'); ci.inputs['Collection'].default_value = coll; ci.inputs['Separate Children'].default_value = True; ci.inputs['Reset Children'].default_value = True
        rr = N.new('FunctionNodeRandomValue'); rr.data_type = 'FLOAT_VECTOR'; rr.inputs[1].default_value = (0, 0, 6.283); rr.inputs['Seed'].default_value = seed + 1
        rs = N.new('FunctionNodeRandomValue'); rs.data_type = 'FLOAT'; rs.inputs[2].default_value = s0; rs.inputs[3].default_value = s1; rs.inputs['Seed'].default_value = seed + 2
        io = N.new('GeometryNodeInstanceOnPoints'); io.inputs['Pick Instance'].default_value = True
        L.new(dp.outputs['Points'], io.inputs['Points']); L.new(ci.outputs[0], io.inputs['Instance']); L.new(rr.outputs[0], io.inputs['Rotation']); L.new(rs.outputs[1], io.inputs['Scale'])
        L.new(io.outputs[0], j.inputs[0])
    L.new(j.outputs[0], go.inputs[0]); md = ob.modifiers.new('scatter', 'NODES'); md.node_group = ng

# ---------------- Sketchfab vehicles (CC-BY), normalised so +Y is forward, wheels on z=0 ----------------
VEH = {}   # key -> collection
SPEC = {'bus_tata': 11.0, 'bus_indian': 11.5, 'bus_1940': 9.0, 'car_wagonr': 3.6, 'car_sx4': 4.3, 'car_nano': 3.1, 'car_1940': 4.6,
        'bullock': 5.0, 'bullock2': 4.2, 'zebu': 2.3, 'walker': 1.68, 'barrier_closed': 2.4, 'barrier_concrete': 2.0}
FLIP = json.load(open('close/flip.json')) if os.path.exists('close/flip.json') else {}
def bbox(objs):
    pts = [o.matrix_world @ Vector(c) for o in objs if o.type == 'MESH' for c in o.bound_box]
    return Vector([min(p[i] for p in pts) for i in range(3)]), Vector([max(p[i] for p in pts) for i in range(3)])
def vehicle(key):
    if key in VEH: return VEH[key]
    gl = [os.path.join(r, f) for r, _, fs in os.walk(SF + key) for f in fs if f.endswith('.gltf')][0]
    before = set(bpy.data.objects); bpy.ops.import_scene.gltf(filepath=gl); new = [o for o in bpy.data.objects if o not in before]
    try:
        J = json.load(open(gl)); base = os.path.dirname(gl)
        for mj in J.get('materials', []):
            sg = (mj.get('extensions') or {}).get('KHR_materials_pbrSpecularGlossiness')
            bm = bpy.data.materials.get(mj.get('name', ''))
            if not sg or bm is None or not bm.use_nodes: continue
            pb_ = bm.node_tree.nodes.get('Principled BSDF')
            if pb_ is None or pb_.inputs['Base Color'].links: continue
            if 'diffuseTexture' in sg:
                uri = J['images'][J['textures'][sg['diffuseTexture']['index']]['source']].get('uri')
                if uri and os.path.exists(os.path.join(base, uri)):
                    tx = bm.node_tree.nodes.new('ShaderNodeTexImage'); tx.image = bpy.data.images.load(os.path.join(base, uri))
                    bm.node_tree.links.new(tx.outputs['Color'], pb_.inputs['Base Color']); continue
            if 'diffuseFactor' in sg: pb_.inputs['Base Color'].default_value = sg['diffuseFactor']
    except Exception as ex: print('specgloss fix skipped', key, ex)
    bpy.context.view_layer.update()
    # drop stray ground slabs / backdrops: meshes much wider than the model is tall
    names = [o.name for o in new]; drop = []
    for o in new:
        if o.type != 'MESH' or o.children: continue
        lo, hi = bbox([o]); dd = hi - lo
        if max(dd.x, dd.y) > 25 or (min(dd.x, dd.y) > 5.5 and dd.z < 0.3): drop.append(o.name)
    for n_ in drop: bpy.data.objects.remove(bpy.data.objects[n_], do_unlink=True)
    new = [bpy.data.objects[n_] for n_ in names if n_ not in drop and n_ in bpy.data.objects]
    roots = [o for o in new if o.parent is None]
    e = bpy.data.objects.new('veh_' + key, None); sc.collection.objects.link(e)
    for r in roots: r.parent = e
    bpy.context.view_layer.update(); lo, hi = bbox(new); dd = hi - lo
    walker = key == 'walker'
    if not walker and dd.x > dd.y: e.rotation_euler.z = math.pi / 2          # long axis -> Y
    if FLIP.get(key): e.rotation_euler.z += math.pi
    bpy.context.view_layer.update(); lo, hi = bbox(new); dd = hi - lo
    k = SPEC[key] / (dd.z if walker else max(dd.x, dd.y)); e.scale = (k, k, k); bpy.context.view_layer.update()
    lo, hi = bbox(new); e.location -= Vector(((lo.x + hi.x) / 2, (lo.y + hi.y) / 2, lo.z)); bpy.context.view_layer.update()
    if key in ('bus_tata', 'bus_indian'):
        lo, hi = bbox(new); Hh = hi.z - lo.z
        pm = bpy.data.materials.new('apsrtc_' + key); pm.use_nodes = True; pb = pm.node_tree.nodes['Principled BSDF']
        ca = pm.node_tree.nodes.new('ShaderNodeVertexColor'); ca.layer_name = 'paint'; pm.node_tree.links.new(ca.outputs['Color'], pb.inputs['Base Color'])
        sp_ = pm.node_tree.nodes.new('ShaderNodeSeparateColor'); pm.node_tree.links.new(ca.outputs['Color'], sp_.inputs[0])
        rg = pm.node_tree.nodes.new('ShaderNodeMapRange'); rg.inputs['From Min'].default_value = 0.0; rg.inputs['From Max'].default_value = 0.2
        rg.inputs['To Min'].default_value = 0.08; rg.inputs['To Max'].default_value = 0.45; pm.node_tree.links.new(sp_.outputs[0], rg.inputs['Value']); pm.node_tree.links.new(rg.outputs[0], pb.inputs['Roughness'])
        BANDS = [(0.10, (0.02, 0.02, 0.02)), (0.25, (0.50, 0.03, 0.06)), (0.30, (1.0, 0.72, 0.05)), (0.52, (0.93, 0.90, 0.82)),
                 (0.78, (0.03, 0.05, 0.07)), (0.86, (0.93, 0.90, 0.82)), (0.91, (1.0, 0.72, 0.05)), (1.01, (0.93, 0.90, 0.82))]
        for o in new:
            if o.type != 'MESH': continue
            me_ = o.data; va = me_.color_attributes.new('paint', 'FLOAT_COLOR', 'POINT'); mw = o.matrix_world
            for v in me_.vertices:
                q = ((mw @ v.co).z - lo.z) / Hh
                col_ = next(c_ for lim, c_ in BANDS if q <= lim)
                va.data[v.index].color = (*col_, 1)
            me_.materials.clear(); me_.materials.append(pm)
        # APSRTC lettering on the front and both sides
        fnt = bpy.data.curves.new('apsrtc_txt', 'FONT'); fnt.body = 'A P S R T C'; fnt.align_x = 'CENTER'; fnt.size = 0.34
        tm_ = emis('apsrtc_white', (1, 1, 1), 1.2)
        for nm_, loc_, rot_ in (('f', (0, hi.y + 0.03, lo.z + Hh * 0.82), (math.pi / 2, 0, math.pi)), ('l', (lo.x - 0.03, 0, lo.z + Hh * 0.42), (math.pi / 2, 0, -math.pi / 2)),
                                ('r', (hi.x + 0.03, 0, lo.z + Hh * 0.42), (math.pi / 2, 0, math.pi / 2))):
            t_o = bpy.data.objects.new(f'apsrtc_{key}_{nm_}', fnt); sc.collection.objects.link(t_o); t_o.location = loc_; t_o.rotation_euler = rot_
            t_o.data.materials.append(tm_) if not t_o.data.materials else None; new.append(t_o)
    c = bpy.data.collections.new('veh_' + key); sc.collection.children.link(c); bpy.context.view_layer.layer_collection.children[c.name].exclude = True
    for o in [e] + new:
        if o.type == 'FONT' and o.parent is None: o.parent = e; o.matrix_parent_inverse = e.matrix_world.inverted()
        for cc in list(o.users_collection): cc.objects.unlink(o)
        c.objects.link(o)
    walk = [a_ for a_ in bpy.data.actions if 'walk' in a_.name.lower()]
    if key == 'zebu' and walk:
        for o in new:
            if o.type == 'ARMATURE' and o.animation_data: o.animation_data.action = walk[0]
    # looping animations (bullock walk, pedestrian walk)
    for o in new:
        if o.animation_data and o.animation_data.action:
            for fc in fcurves(o):
                if not fc.modifiers: fc.modifiers.new('CYCLES')
    VEH[key] = c; return c
def path(name, pts, lane):
    """Curve along pts shifted sideways by lane metres (positive = left of travel; India drives on the left)."""
    sh = []
    for i, p in enumerate(pts):
        t = (pts[min(i + 1, len(pts) - 1)] - pts[max(i - 1, 0)]); t.z = 0; t = t.normalized(); nn = Vector((-t.y, t.x, 0))
        sh.append(p + nn * lane + Vector((0, 0, 0.14)))
    cu = bpy.data.curves.new(name, 'CURVE'); cu.dimensions = '3D'; cu.use_path = True; cu.path_duration = 100
    sp = cu.splines.new('POLY'); sp.points.add(len(sh) - 1)
    for q, c in zip(sp.points, sh): q.co = (*c, 1)
    o = bpy.data.objects.new(name, cu); sc.collection.objects.link(o)
    return o, sum((b - a).length for a, b in zip(sh, sh[1:]))
def driver(name, crv, length, f0, f1, s0, speed, ranges, coll=None):
    """Empty (optionally carrying a model) that moves along crv from distance s0 at f0 at `speed` m/s."""
    e = bpy.data.objects.new(name, None); sc.collection.objects.link(e)
    if coll is not None: e.instance_type = 'COLLECTION'; e.instance_collection = coll
    c = e.constraints.new('FOLLOW_PATH'); c.target = crv; c.use_fixed_location = True; c.use_curve_follow = True
    c.forward_axis = 'FORWARD_Y'; c.up_axis = 'UP_Z'
    s1 = s0 + speed * (f1 - f0) / 30.0
    for f, s in ((f0, s0), (f1, s1)):
        c.offset_factor = min(max(s / length, 0), 1); c.keyframe_insert('offset_factor', frame=f)
    for fc in fcurves(e):
        for kp in fc.keyframe_points: kp.interpolation = 'LINEAR'
    if coll is not None: show(e, ranges)
    return e

# ---------------- the four sets ----------------
CLOSE = {}       # shot -> (camera object)
def cam_obj(name, lens=32):
    cd = bpy.data.cameras.new(name); cd.lens = lens; cd.sensor_width = 24; cd.clip_start = 0.2; cd.clip_end = 30000
    cd.dof.use_dof = True; cd.dof.aperture_fstop = 4.0
    o = bpy.data.objects.new(name, cd); sc.collection.objects.link(o); return o
def track_cam(shot, target, positions, lens=32):
    """Camera keyed through positions [(frac, Vector)] in the shot, always aimed at target (an object)."""
    c = cam_obj('cam_' + shot, lens); tc = c.constraints.new('TRACK_TO'); tc.target = target; tc.track_axis = 'TRACK_NEGATIVE_Z'; tc.up_axis = 'UP_Y'
    c.data.dof.focus_object = target
    for q, p in positions: c.location = p; c.keyframe_insert('location', frame=fr(shot, q))
    CLOSE[shot] = c; return c
def side_point(road, s, off, up):
    """Point beside the road at arc length s: off metres to the side (+left), up metres above the road."""
    acc = 0.0
    for a, b in zip(road, road[1:]):
        L = (b - a).length
        if acc + L >= s:
            p = a.lerp(b, (s - acc) / L); t = (b - a); t.z = 0; t = t.normalized(); return p + Vector((-t.y, t.x, 0)) * off + Vector((0, 0, up))
        acc += L
    return road[-1] + Vector((0, 0, up))
def roadlen(r): return sum((b - a).length for a, b in zip(r, r[1:]))

# 1) TODAY, uphill on the 1974 road at a sharp curve away from the rock cut: buses and cars climbing (shot: open)
U = curvature_pick(UPp, 4000, 9000, UP)
rU = segment(UPp, U, 280)
gU, roadU, _ = build_set('setU', U, rU, 7.5); scatter(gU)
LU = roadlen(rU); a, b = S('open')
crvL, lenL = path('pathU_left', rU, 1.9); crvR, lenR = path('pathU_right', rU, -1.6 + 3.5)
lead = driver('U_bus', crvL, lenL, a, b + 1, LU * 0.12, 7.5, [(a, b + 1)], vehicle('bus_tata'))
for k, (key, s0, sp) in enumerate((('car_wagonr', 0.30, 8.5), ('bus_indian', 0.42, 7.0), ('car_nano', 0.02, 9.0), ('car_sx4', 0.55, 8.0))):
    driver(f'U_{key}', crvL if k % 2 == 0 else crvR, lenL, a, b + 1, LU * s0, sp, [(a, b + 1)], vehicle(key))
track_cam('open', lead, [(0.0, side_point(rU, LU * 0.12 - 25, 12, 7)), (1.0, side_point(rU, LU * 0.12 + 7.5 * (b - a) / 30 - 10, 14, 9))], 30)

# 2) HAIRPIN on the 1944 road: 1944 shot (dirt, old bus & car, both directions) and today (asphalt, parapets, downhill traffic)
rH = segment(DNp, H, 280)                 # top -> bottom
gH, roadH, _ = build_set('setH', H, rH, 7.0); scatter(gH)
LH = roadlen(rH)
ta, tb = S('traffic'); oa, ob_ = S('old_runs')
parapets('setH_par', rH, 7.0, [(oa, END + 1), (S('open')[0], S('two_roads')[1] + 1)])
upH = list(reversed(rH))
crvU, lU = path('pathH_up', upH, 1.8); crvD, lD = path('pathH_dn', rH, 1.8); crvD2, _ = path('pathH_dn2', rH, -1.6)
b40 = driver('H_bus1940', crvU, lU, ta, tb + 1, lU * 0.25, 6.0, [(ta, tb + 1)], vehicle('bus_1940'))
driver('H_car1940', crvD, lD, ta, tb + 1, lD * 0.35, 7.0, [(ta, tb + 1)], vehicle('car_1940'))
track_cam('traffic', b40, [(0.0, side_point(upH, lU * 0.25 - 20, -14, 10)), (1.0, side_point(upH, lU * 0.25 + 6 * (tb - ta) / 30 - 8, -16, 14))], 30)
todayH = driver('H_bus_today', crvD, lD, oa, ob_ + 1, lD * 0.2, 8.0, [(oa, ob_ + 1)], vehicle('bus_indian'))
for k, (key, s0, sp, crv) in enumerate((('car_sx4', 0.32, 9.0, crvD2), ('car_wagonr', 0.05, 9.5, crvD2), ('bus_tata', 0.45, 7.5, crvD))):
    driver(f'H_today_{key}', crv, lD, oa, ob_ + 1, lD * s0, sp, [(oa, ob_ + 1)], vehicle(key))
track_cam('old_runs', todayH, [(0.0, side_point(rH, lD * 0.2 - 15, 10, 6)), (1.0, side_point(rH, lD * 0.2 + 8 * (ob_ - oa) / 30, 30, 55))], 28)

# 3) BEFORE 1944: bullock carts and walking pilgrims on the lower track (shot: cart_track)
lowA = DNp[int(len(DNp) * 0.85)]          # a point low on the old track
rA = segment(DNp, lowA, 260); upA = list(reversed(rA))
gA, roadA, _ = build_set('setA', lowA, rA, 3.6); scatter(gA)
ca, cb = S('cart_track'); LA = roadlen(upA)
crvA, lA = path('pathA', upA, 0.0); crvA2, _ = path('pathA2', upA, 1.1)
cart = driver('A_cart', crvA, lA, ca, cb + 1, lA * 0.3, 1.2, [(ca, cb + 1)], vehicle('bullock2'))
driver('A_cart2', crvA, lA, ca, cb + 1, lA * 0.3 - 16, 1.2, [(ca, cb + 1)], vehicle('bullock2'))
crvB1, _ = path('pathA_b1', upA, 0.55); crvB2, _ = path('pathA_b2', upA, -0.55)
for nm_, s_off in (('c1', 0.0), ('c2', -16.0)):
    for crv_ in (crvB1, crvB2):
        driver(f'A_bull_{nm_}_{crv_.name[-2:]}', crv_, lA, ca, cb + 1, lA * 0.3 + s_off + 3.4, 1.2, [(ca, cb + 1)], vehicle('zebu'))
for k in range(4):
    driver(f'A_walk{k}', crvA2, lA, ca, cb + 1, lA * 0.3 + 9 + k * 2.6, 1.25, [(ca, cb + 1)], vehicle('walker'))
track_cam('cart_track', cart, [(0.0, side_point(upA, lA * 0.3 + 16, -7, 2.2)), (1.0, side_point(upA, lA * 0.3 + 1.2 * (cb - ca) / 30 + 13, -8, 2.8))], 35)

# 4) ROCK CUT on the 1974 road: falling boulders, barriers, road closed (shot: rockfall)
rR = segment(UPp, RC, 150)
gR, roadR, _ = build_set('setR', RC, rR, 7.5); scatter(gR)
ra, rb = S('rockfall'); LR = roadlen(rR)
mid_ = side_point(rR, LR * 0.5, 0, 0)
t_ = (side_point(rR, LR * 0.5 + 2, 0, 0) - side_point(rR, LR * 0.5 - 2, 0, 0)); t_.z = 0; t_ = t_.normalized(); n_ = Vector((-t_.y, t_.x, 0))
upslope = n_ if elev_local(*(mid_ + n_ * 30).xy) > elev_local(*(mid_ - n_ * 30).xy) else -n_
bpy.ops.import_scene.gltf(filepath=f'{PH}m/boulder_01/boulder_01.gltf'); bsrc = [o for o in bpy.context.selected_objects if o.type == 'MESH'][0]
M_rock2 = bsrc.data.materials[0] if bsrc.data.materials else principled('rock2', (0.4, 0.33, 0.28), 0.9)
for i in range(9):
    o = bsrc.copy(); o.data = bsrc.data; sc.collection.objects.link(o)
    s = random.uniform(0.9, 2.2); o.scale = (s, s, s)
    along = (i - 4) * 3.2 + random.uniform(-1, 1)
    st = mid_ + t_ * along + upslope * random.uniform(16, 26); st.z = elev_local(st.x, st.y) + 2 + s
    en = mid_ + t_ * along + upslope * random.uniform(-2.5, 2.5); en.z = mid_.z + 0.5 * s
    f0 = int(ra + (rb - ra) * (0.15 + 0.07 * i)); f1 = f0 + 20
    o.location = st; o.keyframe_insert('location', frame=f0); o.rotation_euler = (0, 0, 0); o.keyframe_insert('rotation_euler', frame=f0)
    o.location = en; o.keyframe_insert('location', frame=f1); o.rotation_euler = (random.uniform(3, 6), random.uniform(2, 5), 0); o.keyframe_insert('rotation_euler', frame=f1)
    show(o, [(f0, rb + 1)])
bsrc.hide_render = True; bsrc.hide_viewport = True
for k, (key, off) in enumerate((('barrier_closed', -14), ('barrier_concrete', -16.5), ('barrier_concrete', -16.5))):
    e = bpy.data.objects.new(f'R_{key}{k}', None); sc.collection.objects.link(e); e.instance_type = 'COLLECTION'; e.instance_collection = vehicle(key)
    p = mid_ + t_ * off + Vector((-t_.y, t_.x, 0)) * (k - 1) * 2.3; e.location = p; e.rotation_euler.z = math.atan2(t_.y, t_.x)
    show(e, [(int(ra + (rb - ra) * 0.75), rb + 1)])
rc_t = bpy.data.objects.new('R_focus', None); sc.collection.objects.link(rc_t); rc_t.location = mid_ + upslope * 6 + Vector((0, 0, 3))
track_cam('rockfall', rc_t, [(0.0, side_point(rR, LR * 0.5 - 46, 0, 3.4)), (1.0, side_point(rR, LR * 0.5 - 32, 0, 2.8))], 30)

def only_in(objs, shots):
    for o in objs: key_hidden(o, lambda n: n not in shots)
only_in([gU, roadU], ['open']); only_in([gH, roadH], ['traffic', 'old_runs']); only_in([gA, roadA], ['cart_track']); only_in([gR, roadR], ['rockfall'])

# era: road surface dirt in old shots
for l in plan['lines']:
    a_, b_ = S(l['shot']); era_r.outputs[0].default_value = 1.0 if in_old(a_) else 0.0; era_r.outputs[0].keyframe_insert('default_value', frame=a_)
for fc in fcurves(M_road.node_tree):
    for kp in fc.keyframe_points: kp.interpolation = 'CONSTANT'

# camera switching: a marker at every shot start (close camera where we have one)
for m in list(sc.timeline_markers): sc.timeline_markers.remove(m)
for l in plan['lines']:
    a_ = S(l['shot'])[0]; mk = sc.timeline_markers.new(l['shot'], frame=a_); mk.camera = CLOSE.get(l['shot'], cam)
sc.camera = cam
json.dump({k: {'U': list(U), 'H': list(H)} for k in ['sets']}, open('brief/close_points.json', 'w'))
print('CLOSE sets: U', tuple(round(v) for v in U), 'roads', len(rU), len(rH), len(rA), len(rR), 'close shots', sorted(CLOSE))
