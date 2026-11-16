"""Rich look pass on top of scene/porus.blend: photoreal CC0 vegetation (Poly Haven) scattered on the real terrain,
detailed ground and water, depth haze, soft glow, ray-traced EEVEE, depth of field. Saves scene/porus_rich.blend."""
import bpy, json, math, os, random
import numpy as np
from mathutils import Vector as V
HERE = os.path.dirname(os.path.abspath(__file__)); os.chdir(HERE); random.seed(7); rng = np.random.default_rng(7)
bpy.ops.wm.open_mainfile(filepath=os.path.abspath('scene/porus.blend'))
sc = bpy.context.scene; PH = '/opt/reel/assets/ph/'
P = json.load(open('brief/points.json')); pts = {k: np.array(v) for k, v in P['pts'].items()}; R = np.array(P['river']); RW = P['RW']
terr = bpy.data.objects['terrain']; me = terr.data

# ---------- density maps on terrain vertices ----------
co = np.empty(len(me.vertices) * 3, np.float32); me.vertices.foreach_get('co', co); co = co.reshape(-1, 3); xy = co[:, :2].astype(np.float64)
def dist_to(p): return np.hypot(xy[:, 0] - p[0], xy[:, 1] - p[1])
# distance to river centre line (dense sampling)
seg = np.concatenate([np.linspace(R[i], R[i + 1], 8, endpoint=False) for i in range(len(R) - 1)])
driver = np.empty(len(xy))
for i0 in range(0, len(xy), 20000):
    q = xy[i0:i0 + 20000]; driver[i0:i0 + 20000] = np.sqrt(((q[:, None, :] - seg[None, ::2, :]) ** 2).sum(-1).min(1))
# clumpy farmland noise: low-res random grid, bilinear upsampled
def field(cell, seed):
    g = np.random.default_rng(seed).random((80, 80)); mn = xy.min(0)
    u = (xy[:, 0] - mn[0]) / cell; v = (xy[:, 1] - mn[1]) / cell
    u0 = np.clip(u.astype(int), 0, 78); v0 = np.clip(v.astype(int), 0, 78); fu = np.clip(u - u0, 0, 1); fv = np.clip(v - v0, 0, 1)
    return g[v0, u0] * (1 - fu) * (1 - fv) + g[v0, u0 + 1] * fu * (1 - fv) + g[v0 + 1, u0] * (1 - fu) * fv + g[v0 + 1, u0 + 1] * fu * fv
clump = np.clip((field(450, 1) * 0.7 + field(160, 2) * 0.3 - 0.42) * 3.0, 0, 1)
FOC = [('B', 3500), ('O', 3000), ('FORT', 2000), ('RIDGE', 1800), ('FN', 1500), ('FS', 1500), ('CROSS', 2200), ('NB', 2500), ('SB', 2500)]
near = np.zeros(len(xy))
for k, r in FOC: near = np.maximum(near, np.clip(1 - dist_to(pts[k]) / r, 0, 1) ** 0.6)
veg = near * clump
veg[driver < RW / 2 + 25] = 0                                    # no trees in the water
veg *= np.clip((driver - RW / 2 - 25) / 120, 0, 1) * 0.6 + 0.4   # thinner right at the bank
veg[dist_to(pts['O']) < 520] = 0                                 # open battlefield
veg[dist_to(pts['KG']) < 120] = 0
veg[dist_to(pts['FORT']) < 140] = 0
grass = np.zeros(len(xy))
for k, r in [('O', 650), ('KG', 160), ('FORT', 260), ('RIDGE', 220), ('FN', 260), ('FS', 260), ('CROSS', 420)]:
    grass = np.maximum(grass, np.clip(1 - dist_to(pts[k]) / r, 0, 1))
grass[driver < RW / 2 + 6] = 0
grass *= 0.55 + 0.45 * field(40, 3)
for name, arr in (('veg', veg), ('grass', grass)):
    a = me.attributes.get(name) or me.attributes.new(name, 'FLOAT', 'POINT'); a.data.foreach_set('value', arr.astype(np.float32))
print('veg mean', round(float(veg.mean()), 4), 'grass mean', round(float(grass.mean()), 4))

# ---------- import Poly Haven models into hidden collections ----------
def collection(name):
    c = bpy.data.collections.new(name); sc.collection.children.link(c)
    bpy.context.view_layer.layer_collection.children[name].exclude = True; return c
def load(key, target, ratio):
    before = set(bpy.data.objects); bpy.ops.import_scene.gltf(filepath=f'{PH}m/{key}/{key}.gltf')
    new = [o for o in bpy.data.objects if o not in before]; names = [o.name for o in new]; meshes = [o for o in new if o.type == 'MESH']
    bpy.ops.object.select_all(action='DESELECT')
    for o in meshes: o.select_set(True)
    bpy.context.view_layer.objects.active = meshes[0]
    if len(meshes) > 1: bpy.ops.object.join()
    ob = bpy.context.view_layer.objects.active; ob.parent = None
    bpy.ops.object.transform_apply(location=False, rotation=True, scale=True)
    if ratio < 1:
        d = ob.modifiers.new('dec', 'DECIMATE'); d.ratio = ratio; bpy.ops.object.modifier_apply(modifier='dec')
    ob.location = (0, 0, 0); ob.name = key; keep = ob.name
    for c in list(ob.users_collection): c.objects.unlink(ob)
    target.objects.link(ob)
    for n in names:
        o = bpy.data.objects.get(n)
        if o is not None and o != ob: bpy.data.objects.remove(o, do_unlink=True)
    for m in ob.data.materials:
        if m: m.surface_render_method = 'DITHERED'
    return ob
TREES = collection('veg_trees'); SHRUBS = collection('veg_shrubs'); GRASS = collection('veg_grass')
for k in ('island_tree_01', 'island_tree_02', 'island_tree_03', 'tree_small_02'): load(k, TREES, 0.25)
for k in ('shrub_01', 'shrub_02', 'shrub_03', 'shrub_04', 'wild_rooibos_bush', 'boulder_01'): load(k, SHRUBS, 0.4)
for k in ('grass_medium_01', 'grass_medium_02', 'grass_bermuda_01'): load(k, GRASS, 0.5)
tris = {o.name: sum(len(p.vertices) - 2 for p in o.data.polygons) for c in (TREES, SHRUBS, GRASS) for o in c.objects}
print('tris', tris)

# ---------- geometry nodes scatter ----------
ng = bpy.data.node_groups.new('scatter', 'GeometryNodeTree')
ng.interface.new_socket('Geometry', in_out='INPUT', socket_type='NodeSocketGeometry')
ng.interface.new_socket('Geometry', in_out='OUTPUT', socket_type='NodeSocketGeometry')
N, L = ng.nodes, ng.links
gi = N.new('NodeGroupInput'); go = N.new('NodeGroupOutput'); join = N.new('GeometryNodeJoinGeometry')
L.new(gi.outputs[0], join.inputs[0])
def layer(attr, coll, density, smin, smax, seed):
    na = N.new('GeometryNodeInputNamedAttribute'); na.data_type = 'FLOAT'; na.inputs['Name'].default_value = attr
    dp = N.new('GeometryNodeDistributePointsOnFaces'); dp.distribute_method = 'RANDOM'
    dp.inputs['Density'].default_value = density; dp.inputs['Seed'].default_value = seed
    L.new(gi.outputs[0], dp.inputs['Mesh']); L.new(na.outputs['Attribute'], dp.inputs['Density Factor'])
    ci = N.new('GeometryNodeCollectionInfo'); ci.inputs['Collection'].default_value = coll
    ci.inputs['Separate Children'].default_value = True; ci.inputs['Reset Children'].default_value = True
    rr = N.new('FunctionNodeRandomValue'); rr.data_type = 'FLOAT_VECTOR'; rr.inputs[1].default_value = (0, 0, 6.283); rr.inputs['Seed'].default_value = seed + 1
    rs = N.new('FunctionNodeRandomValue'); rs.data_type = 'FLOAT'; rs.inputs[2].default_value = smin; rs.inputs[3].default_value = smax; rs.inputs['Seed'].default_value = seed + 2
    io = N.new('GeometryNodeInstanceOnPoints'); io.inputs['Pick Instance'].default_value = True
    L.new(dp.outputs['Points'], io.inputs['Points']); L.new(ci.outputs[0], io.inputs['Instance'])
    L.new(rr.outputs[0], io.inputs['Rotation']); L.new(rs.outputs[1], io.inputs['Scale'])
    L.new(io.outputs[0], join.inputs[0])
layer('veg', TREES, 1 / 900, 0.8, 1.5, 10)
layer('veg', SHRUBS, 1 / 250, 0.7, 1.6, 20)
layer('grass', GRASS, 0.35, 0.7, 1.4, 30)
L.new(join.outputs[0], go.inputs[0])
mod = terr.modifiers.new('scatter', 'NODES'); mod.node_group = ng

# ---------- ground: satellite colour + tiled photo detail + bump ----------
tm = terr.data.materials[0]; nt = tm.node_tree; bs = nt.nodes['Principled BSDF']
s2 = bs.inputs['Base Color'].links[0].from_node if bs.inputs['Base Color'].links else None
tc = nt.nodes.new('ShaderNodeTexCoord'); mp = nt.nodes.new('ShaderNodeMapping'); mp.inputs['Scale'].default_value = (0.14, 0.14, 0.14)
nt.links.new(tc.outputs['Object'], mp.inputs['Vector'])
def tex(path, non_color=False):
    t = nt.nodes.new('ShaderNodeTexImage'); t.image = bpy.data.images.load(path)
    if non_color: t.image.colorspace_settings.name = 'Non-Color'
    nt.links.new(mp.outputs['Vector'], t.inputs['Vector']); return t
ga = tex(PH + 't/sparse_grass/Diffuse.jpg'); gb = tex(PH + 't/dry_ground_01/Diffuse.jpg'); gn = tex(PH + 't/sparse_grass/nor_gl.jpg', True)
nz = nt.nodes.new('ShaderNodeTexNoise'); nz.inputs['Scale'].default_value = 0.02; nt.links.new(tc.outputs['Object'], nz.inputs['Vector'])
mx = nt.nodes.new('ShaderNodeMix'); mx.data_type = 'RGBA'; nt.links.new(nz.outputs['Fac'], mx.inputs['Factor'])
nt.links.new(ga.outputs['Color'], mx.inputs[6]); nt.links.new(gb.outputs['Color'], mx.inputs[7])
bw = nt.nodes.new('ShaderNodeRGBToBW'); nt.links.new(mx.outputs[2], bw.inputs[0])
gain = nt.nodes.new('ShaderNodeMath'); gain.operation = 'MULTIPLY'; gain.inputs[1].default_value = 2.6; nt.links.new(bw.outputs[0], gain.inputs[0])
if s2:
    mul = nt.nodes.new('ShaderNodeMix'); mul.data_type = 'RGBA'; mul.blend_type = 'MULTIPLY'; mul.inputs['Factor'].default_value = 1.0
    nt.links.new(s2.outputs[0], mul.inputs[6]); nt.links.new(gain.outputs[0], mul.inputs[7])
    fin = nt.nodes.new('ShaderNodeMix'); fin.data_type = 'RGBA'; fin.inputs['Factor'].default_value = 0.3
    nt.links.new(mul.outputs[2], fin.inputs[6]); nt.links.new(mx.outputs[2], fin.inputs[7]); nt.links.new(fin.outputs[2], bs.inputs['Base Color'])
nm = nt.nodes.new('ShaderNodeNormalMap'); nm.inputs['Strength'].default_value = 0.8
nt.links.new(gn.outputs['Color'], nm.inputs['Color']); nt.links.new(nm.outputs[0], bs.inputs['Normal'])

# ---------- water: dark, glossy, rippled ----------
wm = bpy.data.objects['river'].data.materials[0]; wn = wm.node_tree; wb = wn.nodes['Principled BSDF']
wb.inputs['Base Color'].default_value = (0.035, 0.07, 0.075, 1); wb.inputs['Roughness'].default_value = 0.04
wb.inputs['Specular IOR Level'].default_value = 0.9
rn = wn.nodes.new('ShaderNodeTexNoise'); rn.inputs['Scale'].default_value = 0.35; rn.inputs['Detail'].default_value = 8
bump = wn.nodes.new('ShaderNodeBump'); bump.inputs['Strength'].default_value = 0.15; bump.inputs['Distance'].default_value = 0.4
wn.links.new(rn.outputs['Fac'], bump.inputs['Height']); wn.links.new(bump.outputs['Normal'], wb.inputs['Normal'])

# ---------- render: ray tracing, AO, DOF ----------
ee = sc.eevee
for attr, val in (('use_raytracing', True), ('use_shadows', True), ('use_gtao', True), ('shadow_ray_count', 2), ('shadow_step_count', 8),
                  ('fast_gi_method', 'GLOBAL_ILLUMINATION'), ('use_fast_gi', True)):
    try: setattr(ee, attr, val)
    except Exception as e: print('skip', attr, e)
try: ee.ray_tracing_options.resolution_scale = '2'
except Exception: pass
cam = sc.camera; cd = cam.data; cd.dof.use_dof = True; cd.dof.focus_object = bpy.data.objects['cam_target']; cd.dof.aperture_fstop = 5.6

# ---------- haze (mist pass) + glow in the compositor, haze colour keyed per shot ----------
vl = sc.view_layers[0]; vl.use_pass_mist = True
ms = sc.world.mist_settings; ms.start = 150; ms.depth = 9000; ms.falloff = 'QUADRATIC'
sc.use_nodes = True; ct = sc.node_tree
for n in list(ct.nodes): ct.nodes.remove(n)
rl = ct.nodes.new('CompositorNodeRLayers'); comp = ct.nodes.new('CompositorNodeComposite')
amt = ct.nodes.new('CompositorNodeMath'); amt.operation = 'MULTIPLY'; ct.links.new(rl.outputs['Mist'], amt.inputs[0])
col = ct.nodes.new('CompositorNodeRGB'); mix = ct.nodes.new('CompositorNodeMixRGB'); mix.blend_type = 'MIX'
ct.links.new(amt.outputs[0], mix.inputs[0]); ct.links.new(rl.outputs['Image'], mix.inputs[1]); ct.links.new(col.outputs[0], mix.inputs[2])
gl = ct.nodes.new('CompositorNodeGlare'); gl.glare_type = 'FOG_GLOW'; gl.quality = 'MEDIUM'; gl.threshold = 0.9; gl.mix = -0.75; gl.size = 8
ct.links.new(mix.outputs[0], gl.inputs[0]); ct.links.new(gl.outputs[0], comp.inputs[0])
HAZE = {'open': ((0.95, 0.7, 0.48), 0.55), 'ambhi': ((0.78, 0.82, 0.88), 0.35), 'river': ((0.93, 0.8, 0.62), 0.5),
        'feint': ((0.03, 0.04, 0.07), 0.6), 'storm': ((0.02, 0.025, 0.04), 0.7), 'battle': ((0.92, 0.72, 0.5), 0.6),
        'king': ((0.85, 0.5, 0.3), 0.4), 'return': ((0.8, 0.84, 0.9), 0.35), 'murder': ((0, 0, 0), 0.0), 'legacy': ((0.95, 0.55, 0.3), 0.55)}
for (a, b), name in zip(P['SH'], P['shots']):
    c, s = HAZE[name]
    col.outputs[0].default_value = (*c, 1); col.outputs[0].keyframe_insert('default_value', frame=a)
    amt.inputs[1].default_value = s; amt.inputs[1].keyframe_insert('default_value', frame=a)
if ct.animation_data and ct.animation_data.action:
    for fc in ct.animation_data.action.fcurves:
        for kp in fc.keyframe_points: kp.interpolation = 'CONSTANT'
bpy.ops.wm.save_as_mainfile(filepath=os.path.abspath('scene/porus_rich.blend'))
print('ENRICHED')
