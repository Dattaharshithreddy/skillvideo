"""Load real anatomy (Z-Anatomy / BodyParts3D, CC BY-SA) as a normalised group under one empty."""
import bpy, os, statistics
from mathutils import Vector

FBX = os.environ.get('ZA_FBX', '/opt/reel/za/Resources/Models/FBX/')
HEART_KEEP = ['Right ventricle', 'Left ventricle', 'Right atrium', 'Left atrium', 'Ascending aorta', 'Arch of aorta', 'Aortic arch',
              'Pulmonary trunk', 'Bifurcation of pulmonary trunk', 'Superior vena cava', 'Right coronary artery', 'Left coronary artery',
              'Circumflex artery of heart', 'Anterior interventricular branch', 'Brachiocephalic trunk', 'Left common carotid artery',
              'Left subclavian artery']


def _mat(name, color, rough=0.4, sss=0.2, trans=0.0):
    m = bpy.data.materials.new(name); m.use_nodes = True
    b = m.node_tree.nodes['Principled BSDF']
    b.inputs['Base Color'].default_value = (*color, 1); b.inputs['Roughness'].default_value = rough
    b.inputs['Subsurface Weight'].default_value = sss; b.inputs['Subsurface Radius'].default_value = (0.03, 0.008, 0.006)
    if trans: b.inputs['Transmission Weight'].default_value = trans
    b.inputs['Emission Color'].default_value = (1.0, 0.08, 0.04, 1); b.inputs['Emission Strength'].default_value = 0.0
    return m


def _import(fname):
    before = set(bpy.data.objects)
    bpy.ops.import_scene.fbx(filepath=FBX + fname)
    return [o for o in bpy.data.objects if o not in before]


def _desc(o):
    out = []
    for c in o.children: out.append(c); out += _desc(c)
    return out


def _center(o):
    return sum((o.matrix_world @ Vector(c) for c in o.bound_box), Vector()) / 8


def load(kind, size, loc, name=None):
    name = name or kind
    sc = bpy.context.scene
    if kind == 'heart':
        new = _import('CardioVascular41.fbx')
        keep = [o for o in new if o.type == 'MESH' and not o.name.endswith('.j') and any(o.name.startswith(k) for k in HEART_KEEP)]
        M = dict(muscle=_mat(name + '_muscle', (0.36, 0.035, 0.035), 0.32, 0.35), art=_mat(name + '_artery', (0.55, 0.05, 0.04), 0.3, 0.3),
                 vein=_mat(name + '_vein', (0.08, 0.1, 0.38), 0.3, 0.3), pul=_mat(name + '_pulm', (0.16, 0.18, 0.5), 0.3, 0.3))
        def pick(o):
            n = o.name.lower()
            if 'vena' in n: return M['vein']
            if 'pulmonary' in n: return M['pul']
            if any(k in n for k in ('aort', 'coronary', 'circumflex', 'interventricular', 'carotid', 'subclavian', 'brachiocephalic')): return M['art']
            return M['muscle']
    elif kind == 'brain':
        new = _import('NervousSystem100.fbx')
        keep = []
        for g in ('Cerebrum.g', 'Cerebellum.g', 'Brainstem.g'):
            if g in bpy.data.objects:
                keep += [d for d in _desc(bpy.data.objects[g]) if d.type == 'MESH' and len(d.data.vertices) > 200]
        m = _mat(name + '_tissue', (0.72, 0.45, 0.43), 0.45, 0.3)
        pick = lambda o: m
    elif kind == 'eye':
        new = _import('NervousSystem100.fbx')
        keep = [d for d in _desc(bpy.data.objects['Eyeball.g']) if d.type == 'MESH' and len(d.data.vertices) > 200 and d.name.endswith('.r')] \
            if 'Eyeball.g' in bpy.data.objects else []
        M = dict(scl=_mat(name + '_sclera', (0.9, 0.88, 0.85), 0.2, 0.1), iris=_mat(name + '_iris', (0.22, 0.12, 0.05), 0.3, 0.0),
                 clr=_mat(name + '_clear', (1, 1, 1), 0.02, 0.0, 1.0), ret=_mat(name + '_retina', (0.5, 0.1, 0.08), 0.5, 0.0))
        def pick(o):
            n = o.name.lower()
            if any(k in n for k in ('cornea', 'lens', 'chamber', 'vitreous', 'zonular', 'anterior segment')): return M['clr']
            if 'iris' in n: return M['iris']
            if 'retina' in n or 'posterior segment' in n: return M['ret']
            return M['scl']
    elif kind == 'kidneys':
        new = _import('VisceralSystem100.fbx')
        keep = [o for o in new if o.type == 'MESH' and o.name in ('Kidney.l', 'Kidney.r')]
        m = _mat(name + '_tissue', (0.35, 0.06, 0.05), 0.35, 0.3)
        pick = lambda o: m
    else:
        raise ValueError(kind)
    bpy.context.view_layer.update()
    # outlier removal (stray parts far from the organ)
    cs = [_center(o) for o in keep]
    med = Vector([statistics.median(c[i] for c in cs) for i in range(3)])
    dists = [(c - med).length for c in cs]
    lim = max(0.02, statistics.median(dists) * 4)
    keep = [o for o, d in zip(keep, dists) if d <= lim]
    keepset = set(keep)
    for o in keep:
        mw = o.matrix_world.copy(); o.parent = None; o.matrix_world = mw
    for o in new:
        if o not in keepset:
            bpy.data.objects.remove(o, do_unlink=True)
    bpy.context.view_layer.update()
    pts = [o.matrix_world @ Vector(c) for o in keep for c in o.bound_box]
    mn = Vector([min(p[i] for p in pts) for i in range(3)]); mx = Vector([max(p[i] for p in pts) for i in range(3)])
    ctr = (mn + mx) / 2; dim = max(mx - mn)
    root = bpy.data.objects.new(name, None); sc.collection.objects.link(root); root.location = ctr
    bpy.context.view_layer.update()
    for o in keep:
        o.data.materials.clear(); o.data.materials.append(pick(o))
        o.data.polygons.foreach_set('use_smooth', [True] * len(o.data.polygons))
        o.parent = root; o.matrix_parent_inverse = root.matrix_world.inverted()
        o.name = name + '_' + o.name
    s = size / dim
    root.scale = (s, s, s); root.location = Vector(loc)
    bpy.context.view_layer.update()
    root['parts'] = len(keep)
    return root


LIMB_WORDS = ('brachial', 'radial', 'ulnar', 'palmar', 'digital', 'femoral', 'tibial', 'plantar', 'popliteal', 'genicular', 'fibular',
              'peroneal', 'tarsal', 'metatarsal', 'carpal', 'interosseous', 'axillary', 'circumflex humeral', 'collateral', 'recurrent',
              'dorsalis pedis', 'arcuate', 'sural', 'malleolar', 'calcaneal', 'penis', 'scrotal', 'perineal')


def load_native(kind, name):
    """Import organs in Z-Anatomy's native, life-size body coordinates (metres, front = -Y). Returns (root empty, meshes)."""
    sc = bpy.context.scene
    if kind == 'heart':
        new = _import('CardioVascular41.fbx')
        keep = [o for o in new if o.type == 'MESH' and not o.name.endswith('.j') and any(o.name.startswith(k) for k in HEART_KEEP[:4])]
        m = _mat(name + '_muscle', (0.32, 0.015, 0.015), 0.32, 0.35); pick = lambda o: m
    elif kind == 'arteries':
        new = _import('CardioVascular41.fbx')
        keep = []
        MAJOR = ('aorta', 'aortic', 'carotid', 'subclavian', 'brachiocephalic', 'renal artery', 'common iliac', 'external iliac',
                 'internal iliac', 'coronary', 'vertebral artery', 'basilar', 'middle cerebral', 'anterior cerebral', 'posterior cerebral',
                 'celiac', 'superior mesenteric', 'internal thoracic')
        bpy.context.view_layer.update()
        for o in new:
            n = o.name.lower()
            if o.type != 'MESH' or o.name.endswith('.j') or not ('arter' in n or 'aort' in n or 'trunk' in n): continue
            if any(w in n for w in LIMB_WORDS) or 'pulmonary' in n or 'lung' in n or 'branch' in n: continue
            if not any(k in n for k in MAJOR) and max(centre([o])[1]) < 0.12: continue
            keep.append(o)
        m = _mat(name + '_wall', (0.55, 0.02, 0.015), 0.3, 0.25); pick = lambda o: m
    elif kind == 'kidneys':
        new = _import('VisceralSystem100.fbx')
        keep = [o for o in new if o.type == 'MESH' and o.name in ('Kidney.l', 'Kidney.r')]
        m = _mat(name + '_tissue', (0.3, 0.04, 0.03), 0.35, 0.3); pick = lambda o: m
    elif kind == 'brain':
        new = _import('NervousSystem100.fbx')
        keep = []
        for g in ('Cerebrum.g', 'Cerebellum.g', 'Brainstem.g'):
            if g in bpy.data.objects:
                keep += [d for d in _desc(bpy.data.objects[g]) if d.type == 'MESH' and len(d.data.vertices) > 200]
        m = _mat(name + '_tissue', (0.62, 0.32, 0.32), 0.45, 0.3); pick = lambda o: m
    elif kind == 'eyes':
        new = _import('NervousSystem100.fbx')
        keep = [d for d in _desc(bpy.data.objects['Eyeball.g']) if d.type == 'MESH' and len(d.data.vertices) > 200] \
            if 'Eyeball.g' in bpy.data.objects else []
        M = dict(scl=_mat(name + '_sclera', (0.9, 0.88, 0.85), 0.2, 0.1), iris=_mat(name + '_iris', (0.22, 0.12, 0.05), 0.3, 0.0),
                 ret=_mat(name + '_retina', (0.6, 0.12, 0.1), 0.5, 0.0))
        def pick(o):
            n = o.name.lower()
            if 'iris' in n: return M['iris']
            if 'retina' in n or 'posterior segment' in n: return M['ret']
            return M['scl']
        keep = [o for o in keep if not any(k in o.name.lower() for k in ('cornea', 'lens', 'chamber', 'vitreous', 'zonular', 'anterior segment'))]
    else:
        raise ValueError(kind)
    bpy.context.view_layer.update()
    keepset = set(keep)
    for o in keep:
        mw = o.matrix_world.copy(); o.parent = None; o.matrix_world = mw
    for o in new:
        if o not in keepset: bpy.data.objects.remove(o, do_unlink=True)
    root = bpy.data.objects.new(name, None); sc.collection.objects.link(root)
    for o in keep:
        o.data.materials.clear(); o.data.materials.append(pick(o))
        o.data.polygons.foreach_set('use_smooth', [True] * len(o.data.polygons))
        o.parent = root; o.name = name + '_' + o.name
    bpy.context.view_layer.update()
    return root, keep


def centre(objs):
    pts = [o.matrix_world @ Vector(c) for o in objs for c in o.bound_box]
    mn = Vector([min(p[i] for p in pts) for i in range(3)]); mx = Vector([max(p[i] for p in pts) for i in range(3)])
    return (mn + mx) / 2, mx - mn


def meshes(root):
    return [d for d in _desc(root) if d.type == 'MESH']
