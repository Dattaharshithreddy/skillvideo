"""charlib: shared helpers for building Momo & Gullu (toy-soft cartoon characters).

Used by build_momo.py / build_gullu.py; depends on czlib from the cgi-shorts skill.
Conventions: metres, +Z up, characters face -Y, standing on z=0.
"""
import os, sys, math
import bpy, bmesh
from mathutils import Vector, Matrix, Euler

SKILL = os.path.expanduser("~/.claude/skills/cgi-shorts/blender")
if SKILL not in sys.path:
    sys.path.insert(0, SKILL)
import czlib as cz


# ---------------------------------------------------------------- colour & materials
def hex_lin(h):
    """sRGB hex -> linear RGB tuple (what Principled Base Color expects)."""
    h = h.lstrip("#")
    out = []
    for i in (0, 2, 4):
        c = int(h[i:i + 2], 16) / 255.0
        out.append(c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4)
    return tuple(out)


def mat_fuzz(name, hexcode, rough=0.68, sheen=1.0, sss=0.08, bump=0.35, bump_scale=700):
    """Soft fuzzy plush-toy fur: strong sheen + fine noise bump + a little SSS. No coat (coat reads plastic).
    Pair with add_fuzz() hair particles on the big shapes for visible strands."""
    m = cz.mat_pbr(name, hex_lin(hexcode), rough=rough, sss=sss, sss_radius=(0.4, 0.3, 0.25),
                   bump=bump, bump_scale=bump_scale, rough_var=0.12)
    b = m.node_tree.nodes["Principled BSDF"]
    for sock, val in (("Sheen Weight", sheen), ("Sheen Roughness", 0.25)):
        if sock in b.inputs:
            b.inputs[sock].default_value = val
    if "Sheen Tint" in b.inputs:
        b.inputs["Sheen Tint"].default_value = (1, 1, 1, 1)
    return m


def mat_cloth(name, hexcode, rough=0.75, sheen=0.6, emit=0.0):
    m = mat_fuzz(name, hexcode, rough=rough, sheen=sheen, sss=0.0, bump=0.3, bump_scale=600)
    if emit > 0:                     # small same-colour emission keeps saturated colours vivid under AgX
        b = m.node_tree.nodes["Principled BSDF"]
        b.inputs["Emission Color"].default_value = (*hex_lin(hexcode), 1)
        b.inputs["Emission Strength"].default_value = emit
    return m


def mat_shiny(name, hexcode, rough=0.12, coat=1.0):
    """Eyes, noses, nails: wet glossy."""
    return cz.mat_pbr(name, hex_lin(hexcode), rough=rough, coat=coat, bump=0.0, rough_var=0.02)


def mat_metal(name, hexcode, rough=0.28):
    return cz.mat_pbr(name, hex_lin(hexcode), rough=rough, metal=1.0, rough_var=0.05)


def add_fuzz(obj, length=0.012, count=10000, radius=0.0007):
    """Visible short fur: a hair particle system using the object's own material."""
    obj.modifiers.new("fuzz", "PARTICLE_SYSTEM")
    ps = obj.particle_systems[-1].settings
    ps.type = "HAIR"
    ps.count = count
    ps.hair_length = length
    ps.use_advanced_hair = True
    ps.brownian_factor = 0.0
    for attr, val in (("roughness_1", 0.35), ("roughness_1_size", 0.25), ("roughness_endpoint", 0.08),
                      ("radius_scale", radius), ("root_radius", 1.0), ("tip_radius", 0.25),
                      ("child_type", "NONE")):
        try:
            setattr(ps, attr, val)
        except Exception:
            pass
    return ps


# ---------------------------------------------------------------- primitives
def blob(r, loc, m, scale=(1, 1, 1), rot=(0, 0, 0), seg=48):
    o = cz.sphere(r, loc, m, seg)
    o.scale = scale
    o.rotation_euler = Euler(rot)
    return o


def capsule(p1, p2, r, m, bulge=1.0, seg=40):
    """Soft limb: ellipsoid stretched from p1 to p2."""
    p1, p2 = Vector(p1), Vector(p2)
    d = p2 - p1
    o = cz.sphere(1.0, (p1 + p2) / 2, m, seg)
    o.scale = (r * bulge, r * bulge, d.length / 2 + r * 0.55)
    o.rotation_euler = d.to_track_quat("Z", "Y").to_euler()
    return o


def torus(maj, minr, loc, m, rot=(0, 0, 0), scale=(1, 1, 1)):
    bpy.ops.mesh.primitive_torus_add(major_radius=maj, minor_radius=minr, location=loc,
                                     major_segments=64, minor_segments=24)
    o = bpy.context.object
    bpy.ops.object.shade_smooth()
    o.rotation_euler = Euler(rot)
    o.scale = scale
    return cz.setmat(o, m)


def dome(r, loc, m, min_elev_deg=12, rot=(0, 0, 0), seg=28):
    """Spherical cap (eyelid shell): sphere surface above the given elevation, +Z axis."""
    me = bpy.data.meshes.new("dome")
    bm = bmesh.new()
    bmesh.ops.create_uvsphere(bm, u_segments=seg, v_segments=seg // 2, radius=r)
    cut = r * math.sin(math.radians(min_elev_deg))
    bmesh.ops.delete(bm, geom=[v for v in bm.verts if v.co.z < cut], context="VERTS")
    bm.to_mesh(me)
    bm.free()
    o = bpy.data.objects.new("dome", me)
    cz.S.collection.objects.link(o)
    o.location, o.rotation_euler = Vector(loc), Euler(rot)
    for p in me.polygons:
        p.use_smooth = True
    return cz.setmat(o, m)


def tube(points, radii, m, name="tube", bevel_res=8):
    """Smooth bezier tube through points with per-point radius, converted to mesh."""
    cu = bpy.data.curves.new(name, "CURVE")
    cu.dimensions, cu.fill_mode = "3D", "FULL"
    cu.bevel_depth, cu.bevel_resolution, cu.resolution_u = 1.0, bevel_res, 24
    cu.use_fill_caps = True
    sp = cu.splines.new("BEZIER")
    sp.bezier_points.add(len(points) - 1)
    for i, (p, r) in enumerate(zip(points, radii)):
        bp = sp.bezier_points[i]
        bp.co, bp.radius = Vector(p), r
        bp.handle_left_type = bp.handle_right_type = "AUTO"
    o = bpy.data.objects.new(name, cu)
    cz.S.collection.objects.link(o)
    bpy.ops.object.select_all(action="DESELECT")
    o.select_set(True)
    bpy.context.view_layer.objects.active = o
    bpy.ops.object.convert(target="MESH")
    o = bpy.context.object
    bpy.ops.object.shade_smooth()
    return cz.setmat(o, m)


# ---------------------------------------------------------------- armature
def build_armature(name, bones):
    """bones: list of (name, head, tail, parent_name_or_None). Returns the armature object (at origin)."""
    data = bpy.data.armatures.new(name)
    arm = bpy.data.objects.new(name, data)
    cz.S.collection.objects.link(arm)
    bpy.ops.object.select_all(action="DESELECT")
    arm.select_set(True)
    bpy.context.view_layer.objects.active = arm
    bpy.ops.object.mode_set(mode="EDIT")
    for bn, h, t, par in bones:
        eb = data.edit_bones.new(bn)
        eb.head, eb.tail = Vector(h), Vector(t)
        if par:
            eb.parent = data.edit_bones[par]
    bpy.ops.object.mode_set(mode="OBJECT")
    for pb in arm.pose.bones:
        pb.rotation_mode = "XYZ"
    return arm


def bone_parent(arm, bone_name, *objs):
    """Rigid-parent objects to a bone, keeping their current world transform."""
    b = arm.data.bones[bone_name]
    M = arm.matrix_world @ b.matrix_local @ Matrix.Translation((0, b.length, 0))
    Minv = M.inverted()
    for o in objs:
        o.parent, o.parent_type, o.parent_bone = arm, "BONE", bone_name
        o.matrix_parent_inverse = Minv


def pose(arm, bone, rot_deg):
    arm.pose.bones[bone].rotation_euler = Euler([math.radians(a) for a in rot_deg])


def pose_reset(arm):
    for pb in arm.pose.bones:
        pb.rotation_euler = (0, 0, 0)


def rig_chain_weights(obj, arm, chain_pts, prefix):
    """Weight a tube mesh to a bone chain laid along chain_pts (len = n_bones+1), normalized."""
    nb = len(chain_pts) - 1
    pts = [Vector(p) for p in chain_pts]
    groups = [obj.vertex_groups.new(name=f"{prefix}.{i + 1}") for i in range(nb)]
    for v in obj.data.vertices:
        best = (1e9, 0.0)
        for j in range(nb):
            a, d = pts[j], pts[j + 1] - pts[j]
            t = max(0.0, min(1.0, (v.co - a).dot(d) / max(1e-9, d.length_squared)))
            dist = (a + d * t - v.co).length
            if dist < best[0]:
                best = (dist, j + t)
        u = best[1]
        ws = [max(0.0, 1.0 - abs(u - (j + 0.5))) for j in range(nb)]
        tot = sum(ws) or 1.0
        for j, w in enumerate(ws):
            if w > 0.001:
                groups[j].add([v.index], w / tot, "REPLACE")
    mod = obj.modifiers.new("arm", "ARMATURE")
    mod.object = arm
    obj.parent = arm


# ---------------------------------------------------------------- face kit (shape keys)
KEYS = ["blink", "smile", "frown", "mouthOpen", "cheekPuff", "browsUp", "browsDown",
        "browsSad", "browOneUp", "smirk", "eyesWide", "pupilSmall",
        "lidSleepy", "lidNarrow", "lidSquint"]
LID_ANGLES = {"lidSleepy": 46, "lidNarrow": 28, "lidSquint": 16, "eyesWide": -20}   # own keys: partial blinks
                                                                                   # must rotate, not lerp

EXPRESSIONS = {
    "neutral":   {},
    "happy":     {"smile": 1.0, "lidSquint": 1.0, "browsUp": 0.5},
    "laugh":     {"smile": 0.6, "mouthOpen": 0.9, "blink": 1.0, "browsUp": 0.6},
    "surprised": {"mouthOpen": 1.0, "browsUp": 1.0, "eyesWide": 1.0},
    "sleepy":    {"lidSleepy": 1.0, "browsDown": 0.25, "frown": 0.10},
    "angry":     {"frown": 0.95, "browsDown": 1.0, "lidNarrow": 1.0},
    "sad":       {"frown": 1.0, "browsSad": 1.0, "lidSquint": 1.0, "pupilSmall": 1.0},
    "cheeky":    {"smirk": 1.0, "browOneUp": 1.0, "lidSquint": 0.8},
}


class FaceKit:
    """Collects brow/lid/lash/glint/arc/pupil/mouth/cheek parts, joins them into one mesh
    and builds the expression shape keys (the 7 spec keys + extra readability keys)."""

    def __init__(self, scale=1.0, head_center=(0, 0, 0)):
        self.s = scale
        self.hc = Vector(head_center)
        self.parts = []          # [obj, kind, meta, vstart, vcount]
        self.brow_drop = 0.070   # inner-end drop of browsDown

    def add(self, obj, kind, **meta):
        self.parts.append([obj, kind, meta, 0, 0])
        return obj

    def arc(self, eye, eye_r, m, k=1.0):
        """Closed-eye happy arc: hidden inside the eyeball at rest, swings forward on full blink."""
        hide = 0.06 * self.s
        c = Vector(eye) + Vector((0, -(eye_r + 0.009) + hide, -0.004 * k))
        o = tube([c + Vector((-0.032 * k, 0, 0.011 * k)), c + Vector((0, 0, -0.005 * k)),
                  c + Vector((0.032 * k, 0, 0.011 * k))], [0.0036 * k] * 3, m, name="eyearc")
        return self.add(o, "arc", hide=hide)

    def mouth(self, center, w, h, m, curv=0.0, smile0=0.0, depth=None):
        """Flattened dark ellipse on the face; smile0 = resting corner-lift (permanent smile)."""
        c = Vector(center)
        o = cz.sphere(1.0, c, m, 36)
        o.scale = (w, depth or h * 1.3, h)
        bpy.ops.object.select_all(action="DESELECT")
        o.select_set(True)
        bpy.context.view_layer.objects.active = o
        bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
        raw = [v.co.copy() for v in o.data.vertices]
        for v in o.data.vertices:            # bake resting smile + face curvature into the basis
            dx = v.co.x - c.x
            v.co.z += smile0 * (dx / w) ** 2
            v.co.y += curv * dx * dx
        return self.add(o, "mouth", center=c, w=w, h=h, curv=curv, smile0=smile0, raw=raw)

    def _mouth_target(self, meta, widen, bend, zscale, zshift):
        c, w, curv = meta["center"], meta["w"], meta["curv"]
        out = []
        for rv in meta["raw"]:
            dx = (rv.x - c.x) * widen
            dz = (rv.z - c.z) * zscale
            z = c.z + dz + bend * (dx / w) ** 2 + zshift
            y = rv.y + curv * dx * dx + curv * 0.6 * dz * dz
            out.append(Vector((c.x + dx, y, z)))
        return out

    def finalize(self, name):
        s = self.s
        me = bpy.data.meshes.new(name)
        me.from_pydata([tuple(self.hc)], [], [])      # anchor vert (inside head) keeps join order deterministic
        face = bpy.data.objects.new(name, me)
        cz.S.collection.objects.link(face)
        n = 1
        for p in self.parts:
            p[3], p[4] = n, len(p[0].data.vertices)
            n += p[4]
        for p in self.parts:                           # join one at a time: verts append in order
            bpy.ops.object.select_all(action="DESELECT")
            face.select_set(True)
            p[0].select_set(True)
            bpy.context.view_layer.objects.active = face
            bpy.ops.object.join()
        face.shape_key_add(name="Basis", from_mix=False)
        base = [v.co.copy() for v in face.data.vertices]
        amp = 0.030 * s                                # mouth motion scale
        for key in KEYS:
            kb = face.shape_key_add(name=key, from_mix=False)
            kb.value = 0.0                                 # new keys default to 1.0 in Blender 5.x
            for obj0, kind, meta, v0, cnt in self.parts:
                idx = range(v0, v0 + cnt)
                if kind in ("lid", "lash"):
                    ang = LID_ANGLES.get(key, meta.get("angle", 90) if key == "blink" else None)
                    if ang is not None and key in ("lidSleepy", "lidNarrow", "lidSquint"):
                        ang += meta.get("tilt", 0)          # lid rests tilted back; keys rotate from there
                    if ang is None:
                        continue
                    R = Matrix.Rotation(math.radians(ang), 4, "X")
                    e = meta["eye"]
                    for i in idx:
                        kb.data[i].co = e + R @ (base[i] - e)
                elif kind == "glint" and key == "blink":
                    for i in idx:                       # tuck highlights inside the head when lids close
                        kb.data[i].co = base[i] + Vector((0, 0.06 * s, 0))
                elif kind == "arc" and key == "blink":
                    for i in idx:                       # arc arrives at the lash line on a full blink
                        kb.data[i].co = base[i] + Vector((0, -meta["hide"], 0))
                elif kind == "pupil" and key == "pupilSmall":
                    e, R = meta["eye"], meta["R"]
                    front = Vector((0, -1, 0))
                    Rx = Matrix.Rotation(math.radians(14), 3, "X")      # look down
                    for i in idx:
                        n = (base[i] - e).normalized()
                        n2 = (front + (n - front) * 0.70).normalized()
                        kb.data[i].co = e + (Rx @ n2) * (base[i] - e).length
                elif kind == "brow":
                    cx, w, side = meta["cx"], meta["w"], meta["side"]
                    def t_in(i):
                        return max(0.0, min(1.0, ((cx + side * w) - base[i].x) * side / (2 * w)))
                    if key == "browsUp":
                        for i in idx:
                            kb.data[i].co = base[i] + Vector((0, 0, 0.026 * s))
                    elif key == "browsDown":            # sharp angle down toward the nose
                        for i in idx:
                            t = t_in(i)
                            kb.data[i].co = base[i] + Vector((-side * 0.016 * s * t, 0,
                                                              (0.008 - self.brow_drop * t) * s))
                    elif key == "browsSad":             # inner ends up
                        for i in idx:
                            t = t_in(i)
                            kb.data[i].co = base[i] + Vector((0, 0, (0.032 * t - 0.008 * (1 - t)) * s))
                    elif key == "browOneUp" and side == 1:
                        for i in idx:
                            kb.data[i].co = base[i] + Vector((0, 0, 0.032 * s))
                elif kind == "cheek":
                    if key == "cheekPuff":
                        c, od = meta["center"], meta["out"]
                        for i in idx:
                            kb.data[i].co = c + (base[i] - c) * 1.5 + od * 0.016 * s
                    elif key == "smile":                # happy = cheeks raised
                        for i in idx:
                            kb.data[i].co = base[i] + Vector((0, 0, 0.010 * s))
                elif kind == "mouth":
                    sm0 = meta["smile0"]
                    if key == "smile":
                        tgt = self._mouth_target(meta, 1.30, sm0 + amp, 1.0, 0.1 * amp)
                    elif key == "frown":
                        tgt = self._mouth_target(meta, 0.90, -0.8 * amp, 1.0, -0.15 * amp)
                    elif key == "mouthOpen":            # round surprised O (height ~0.75 of width)
                        zs = 0.38 * meta["w"] / meta["h"]
                        tgt = self._mouth_target(meta, 0.85, 0.2 * sm0, zs, -0.4 * amp)
                    elif key == "smirk":
                        c, w = meta["center"], meta["w"]
                        for i in idx:
                            dx = base[i].x - c.x
                            dz = (amp * 0.55 * (max(dx, 0) / w) ** 2
                                  - amp * 0.20 * (max(-dx, 0) / w) ** 2)
                            kb.data[i].co = base[i] + Vector((0.06 * max(dx, 0), 0, dz))
                        continue
                    else:
                        continue
                    for k, i in enumerate(idx):
                        kb.data[i].co = tgt[k]
        return face


def apply_expression(face, name):
    vals = EXPRESSIONS[name]
    for k in KEYS:
        kb = face.data.shape_keys.key_blocks.get(k)
        if kb:
            kb.value = float(vals.get(k, 0.0))


# ---------------------------------------------------------------- stage (backdrop, lights)
def stage(bottom="#BEE3F2", top="#E7F5EC", floor="#CFE8DB", target=(0, 0, 0.8), scale=1.0, key=1000):
    cz.world_studio(hex_lin(bottom), top=hex_lin(top), strength=1.0)
    f = cz.plane(40, (0, 0, 0), cz.mat_pbr("floor", hex_lin(floor), rough=0.85, rough_var=0.04))
    cz.studio_rig(target=target, scale=scale, key=key)
    return f
