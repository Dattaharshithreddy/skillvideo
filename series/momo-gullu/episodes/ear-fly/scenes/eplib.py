"""eplib: shared staging + acting helpers for the Ear Fly episode.

Runs inside the cgi-shorts blender driver (czlib scene already reset, 24 fps).
Conventions: characters face -Y, camera on -Y. All keyframing helpers both set
and key, so anything not re-keyed holds its last pose.
"""
import os, sys, math
HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.expanduser("~/momo-gullu/characters/src")
for p in (HERE, SRC):
    if p not in sys.path:
        sys.path.insert(0, p)
import bpy
from mathutils import Vector, Matrix, Euler
import czlib as cz
import charlib as cl
import build_momo, build_gullu  # noqa: F401 (shots import via eplib)


def F(t):
    """Seconds -> frame number (frame 1 = t 0)."""
    return int(round(t * cz.FPS)) + 1


def stage(key=680, target=(0, 0, 0.8), scale=1.0):
    cz.S.view_settings.view_transform = "Khronos PBR Neutral"
    cz.S.view_settings.look = "None"
    cz.world_studio(cl.hex_lin("#BEE3F2"), top=cl.hex_lin("#FFEBB0"), strength=1.0)
    cz.plane(40, (0, 0, 0), cz.mat_pbr("floor", cl.hex_lin("#CFE8DB"), rough=0.85, rough_var=0.04))
    cz.studio_rig(target=target, scale=scale, key=key)


# ---------------------------------------------------------------- keyframing
def kb(arm, bone, f, rot=None, scale=None):
    pb = arm.pose.bones[bone]
    if rot is not None:
        pb.rotation_euler = Euler([math.radians(a) for a in rot])
        pb.keyframe_insert("rotation_euler", frame=f)
    if scale is not None:
        pb.scale = Vector(scale)
        pb.keyframe_insert("scale", frame=f)


def ko(obj, f, loc=None, rot=None, scale=None):
    if loc is not None:
        obj.location = loc
        obj.keyframe_insert("location", frame=f)
    if rot is not None:
        obj.rotation_euler = Euler([math.radians(a) for a in rot])
        obj.keyframe_insert("rotation_euler", frame=f)
    if scale is not None:
        obj.scale = Vector(scale)
        obj.keyframe_insert("scale", frame=f)


def kx(face, f, **keys):
    """Keyframe shape keys by name (browOneUp -> browOneUp)."""
    for name, v in keys.items():
        cz.shape_key(face, name, float(v), frame=f)


def expr(face, f, name, amt=1.0):
    vals = cl.EXPRESSIONS[name]
    for k in cl.KEYS:
        cz.shape_key(face, k, float(vals.get(k, 0.0)) * amt, frame=f)


def blink(face, f):
    for dt, v in ((-3, 0.0), (0, 1.0), (2, 1.0), (5, 0.0)):
        cz.shape_key(face, "blink", v, frame=f + dt)


def key_hand(arm, side, pose_name, f):
    build_momo.hand_pose(arm, pose_name, side=side)
    for i in range(4):
        for seg in ("prox", "dist"):
            arm.pose.bones[f"f{i + 1}.{seg}.{side}"].keyframe_insert("rotation_euler", frame=f)
    for seg in ("prox", "dist"):
        arm.pose.bones[f"thumb.{seg}.{side}"].keyframe_insert("rotation_euler", frame=f)


# ---------------------------------------------------------------- gullu acting
def flap(arm, f0, f1, freq0, freq1=None, amp0=40.0, amp1=None, droop0=0.0, droop1=None, root=None, bob=0.0):
    """Dense per-frame ear flaps, with frequency/amplitude/droop ramps and optional body bob."""
    freq1 = freq0 if freq1 is None else freq1
    amp1 = amp0 if amp1 is None else amp1
    droop1 = droop0 if droop1 is None else droop1
    phase, n = 0.0, max(1, f1 - f0)
    base_z = root.location.z if root else 0.0
    for i, f in enumerate(range(f0, f1 + 1)):
        k = i / n
        phase += 2 * math.pi * (freq0 + (freq1 - freq0) * k) / cz.FPS
        a = (droop0 + (droop1 - droop0) * k) + (amp0 + (amp1 - amp0) * k) * math.sin(phase)
        kb(arm, "ear.L", f, rot=(a, 0, 0))
        kb(arm, "ear.R", f, rot=(a, 0, 0))
        if root is not None and bob:
            root.location.z = base_z + bob * math.sin(phase)
            root.keyframe_insert("location", frame=f)


def ear_settle(arm, f0, droop=-40.0, amp0=22.0, cycles=3.0, dur=18):
    """Damped wobble into a droop (secondary motion after landings)."""
    for i in range(dur + 1):
        k = i / dur
        a = droop + amp0 * (1 - k) * math.sin(2 * math.pi * cycles * k)
        kb(arm, "ear.L", f0 + i, rot=(a, 0, 0))
        kb(arm, "ear.R", f0 + i, rot=(a, 0, 0))


def trunk_flop(arm, f0, kick=25.0, dur=16):
    """Overshoot-and-settle on the trunk chain after an impact."""
    for i in range(dur + 1):
        k = i / dur
        a = kick * (1 - k) * math.cos(2 * math.pi * 1.6 * k)
        for j, w in ((1, 0.4), (2, 0.7), (3, 1.0), (4, 1.3)):
            kb(arm, f"trunk.{j}", f0 + i, rot=(a * w, 0, 0))


def waddle(gullu, f0, f1, x0, x1, y=0.0, rate=2.4):
    """Side-to-side toddler walk from x0 to x1 (ease-out), legs/arms/ears/trunk following."""
    root, arm = gullu["root"], gullu["arm"]
    n = max(1, f1 - f0)
    for i, f in enumerate(range(f0, f1 + 1)):
        k = cz.ease(i / n, "out")
        t = i / cz.FPS
        s = math.sin(2 * math.pi * rate * t)
        fade = min(1.0, (1 - i / n) * 6)                      # calm down on arrival
        ko(root, f, loc=(x0 + (x1 - x0) * k, y, abs(s) * 0.012 * fade),
           rot=(0, 7 * s * fade, 0))
        kb(arm, "leg.L", f, rot=(18 * s * fade, 0, 0))
        kb(arm, "leg.R", f, rot=(-18 * s * fade, 0, 0))
        kb(arm, "arm.L", f, rot=(-12 * s * fade, 0, 0))
        kb(arm, "arm.R", f, rot=(12 * s * fade, 0, 0))
        kb(arm, "ear.L", f, rot=(-12 + 9 * s * fade, 0, 0))
        kb(arm, "ear.R", f, rot=(-12 - 9 * s * fade, 0, 0))
        kb(arm, "trunk.2", f, rot=(0, 0, 6 * s * fade))
        kb(arm, "trunk.3", f, rot=(0, 0, 8 * s * fade))


# ---------------------------------------------------------------- momo acting
def breathe(arm, f0, f1, amp=1.2, rate=0.30, bone="spine"):
    """Gentle chest sway so nothing is frozen."""
    for f in range(f0, f1 + 1, 2):
        t = (f - f0) / cz.FPS
        kb(arm, bone, f, rot=(amp * math.sin(2 * math.pi * rate * t), 0, 0))


def give_book(momo, yaw=0.0):
    """Pose Momo's left arm to read and put a small box-built book on the palm, tilted to his face."""
    arm = momo["arm"]
    kb(arm, "upperarm.L", 1, rot=(-20, 0, -62))
    kb(arm, "forearm.L", 1, rot=(-70, 0, 6))
    kb(arm, "upperarm.R", 1, rot=(-6, 0, -10))
    bpy.context.view_layer.update()
    pb = arm.pose.bones["hand.L"]
    Mh = arm.matrix_world @ pb.matrix
    hp = Mh.to_translation() + Mh.to_3x3() @ Vector((0, pb.length * 0.5, 0))
    Rz = Matrix.Rotation(yaw, 3, "Z")
    root = cz.empty(hp + Rz @ Vector((-0.01, -0.085, 0.03)))
    root.rotation_euler = Euler((math.radians(58), math.radians(-6), yaw))
    R = root.rotation_euler.to_matrix()
    cover = cz.box((0.19, 0.03, 0.15), (0, 0, 0), cz.mat_pbr("book_cover", cl.hex_lin("#C65B3A"), rough=0.65))
    pages = cz.box((0.175, 0.024, 0.136), (0, 0, 0), cz.mat_pbr("book_pages", cl.hex_lin("#F4EFE2"), rough=0.8))
    for o, off in ((cover, Vector((0, 0, 0))), (pages, Vector((0, 0.007, 0.004)))):
        o.rotation_euler = root.rotation_euler
        o.location = root.location + R @ off
        cz.parent(o, root)
    Mp = arm.matrix_world @ pb.matrix @ Matrix.Translation((0, pb.length, 0))
    root.parent, root.parent_type, root.parent_bone = arm, "BONE", "hand.L"
    root.matrix_parent_inverse = Mp.inverted()
    return root
