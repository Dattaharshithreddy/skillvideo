import bpy, json
from mathutils import Vector as V
sc = bpy.context.scene; cam = sc.camera; tgt = bpy.data.objects['cam_target']
T = json.load(open('brief/timing.json'))
for i, l in enumerate(T['lines']):
    for q in (0.15, 0.6):
        f = int((T['starts'][i] + T['durs'][i] * q) * 30) + 1; sc.frame_set(f)
        dg = bpy.context.evaluated_depsgraph_get(); o = cam.matrix_world.translation; d = (tgt.matrix_world.translation - o)
        hits = []
        for dx in (0.0, -0.25, 0.25):
            for dz in (0.0, -0.3):
                cm = cam.matrix_world.to_3x3(); dirv = (cm @ V((dx * 0.5, dz * 0.9, -1.0))).normalized()
                ok, loc, nrm, idx, ob, mw = sc.ray_cast(dg, o, dirv)
                hits.append((ob.name if ok else 'sky')[:14] + '@' + (f'{(loc - o).length*100:.1f}' if ok else '-'))
        print('PROBE', l['shot'], q, 'cam', tuple(round(x, 3) for x in o), 'tgt', round(d.length * 100, 1), 'cm', hits)
