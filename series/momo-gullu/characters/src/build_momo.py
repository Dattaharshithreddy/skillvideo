"""Momo the panda — code-built toy-soft cartoon character (cgi-shorts / momo-gullu series).

Run headless to (re)build the .blend:
    blender -b --factory-startup -P build_momo.py
Importable: build() creates Momo in the current czlib scene and returns his parts.

Spec: pear body, ~1.6 m, black tilted eye patches, tiny gold reading glasses low on the
nose with temples curving back to the ears, orange scarf only, 4 fingers + thumb with
palm pads and finger bones, fuzzy fur. Face shape keys per series spec.
"""
import os, sys, math
HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)
sys.path.insert(0, os.path.expanduser("~/.claude/skills/cgi-shorts/blender"))
import bpy
from mathutils import Vector, Euler
import czlib as cz
import charlib as cl

WHITE, BLACK, ORANGE, GOLD = "#F4F1EA", "#1E1E24", "#FF7A1A", "#C9A227"
PAD = "#2F2F36"
H = 1.61                      # to ear tops; head top 1.58

FINGER_X = [-0.040, -0.0135, 0.0135, 0.040]   # knuckle offsets across the palm


def _finger_pts(s):
    """(knuckle, mid, tip) for 4 fingers + thumb on the +s side hand."""
    hx, hy, hz = 0.345 * s, -0.075, 0.525
    fingers = []
    for dx in FINGER_X:
        k = Vector((hx + dx * s, hy, hz))
        fingers.append((k, k + Vector((0, -0.004, -0.047)), k + Vector((0, -0.008, -0.088))))
    th = (Vector((0.298 * s, -0.068, 0.565)), Vector((0.276 * s, -0.076, 0.531)),
          Vector((0.258 * s, -0.083, 0.504)))
    return fingers, th


def build(loc=(0, 0, 0)):
    fur_w = cl.mat_fuzz("momo_white", WHITE)
    fur_b = cl.mat_fuzz("momo_black", BLACK, rough=0.58)
    scarf = cl.mat_cloth("momo_scarf", ORANGE)
    gold = cl.mat_metal("momo_gold", GOLD)
    pad = cz.mat_pbr("momo_pad", cl.hex_lin(PAD), rough=0.5, bump=0.15, bump_scale=200)
    arc_m = cz.mat_pbr("momo_arc", cl.hex_lin("#E8E2D6"), rough=0.5)
    eye_w = cl.mat_shiny("momo_sclera", "#F8F7F3", rough=0.15)
    eye_k = cl.mat_shiny("momo_iris", "#17151A", rough=0.08)
    nose = cl.mat_shiny("momo_nose", "#141317", rough=0.2)
    mouth_m = cz.mat_pbr("momo_mouth", cl.hex_lin("#241F22"), rough=0.6)
    glass = cz.mat_pbr("momo_lensglass", (1, 1, 1), rough=0.08, alpha=0.10, rough_var=0.0)
    glint = cz.mat_glow((1, 1, 1), 2.5, "momo_glint")

    P = {}  # bone_name -> [objs]
    def reg(bone, *objs):
        P.setdefault(bone, []).extend(objs)

    # body
    hips = cl.blob(0.40, (0, 0, 0.58), fur_w, scale=(1.0, 0.92, 1.05))
    chest = cl.blob(0.30, (0, 0, 0.98), fur_w, scale=(0.95, 0.85, 1.0))
    reg("spine", hips, cl.blob(0.065, (0, 0.375, 0.50), fur_w))                   # hips + tail pom
    reg("chest", chest)
    # head
    head = cl.blob(0.27, (0, 0, 1.33), fur_w, scale=(1.0, 0.95, 0.93))
    muzzle = cl.blob(1, (0, -0.245, 1.30), fur_w, scale=(0.115, 0.095, 0.080))
    nose_o = cl.blob(1, (0, -0.333, 1.332), nose, scale=(0.028, 0.018, 0.017))
    reg("head", head, muzzle, nose_o)
    for s in (1, -1):
        reg("head",
            cl.blob(1, (0.112 * s, -0.219, 1.375), fur_b, scale=(0.085, 0.055, 0.115),
                    rot=(0, math.radians(14 * s), 0)),                             # tilted eye patch
            cl.blob(0.046, (0.108 * s, -0.247, 1.383), eye_w))                     # eyeball
    # ears
    for s, side in ((1, "L"), (-1, "R")):
        ear = cl.blob(0.078, (0.180 * s, 0.02, 1.535), fur_b, scale=(1, 0.75, 1))
        cl.add_fuzz(ear, length=0.010, count=2500)
        reg(f"ear.{side}", ear)
    # visible short fuzz on the big fur shapes
    cl.add_fuzz(hips, length=0.016, count=16000)
    cl.add_fuzz(chest, length=0.014, count=10000)
    cl.add_fuzz(head, length=0.012, count=12000)
    cl.add_fuzz(muzzle, length=0.007, count=2500)
    # glasses: two closed round gold rims centred on the eyes, bridge, temples back to the ears
    reg("head",
        cl.capsule((-0.058, -0.300, 1.383), (0.058, -0.300, 1.383), 0.0055, gold))
    for s in (1, -1):
        reg("head",
            cl.torus(0.052, 0.0060, (0.108 * s, -0.302, 1.383), gold, rot=(math.pi / 2, 0, 0)),
            cl.tube([(0.162 * s, -0.290, 1.383), (0.215 * s, -0.200, 1.388),
                     (0.258 * s, -0.100, 1.395), (0.276 * s, -0.010, 1.415),
                     (0.255 * s, 0.040, 1.470), (0.215 * s, 0.050, 1.500)], [0.0060] * 6, gold, name="temple"))
    # scarf (the only outfit)
    reg("chest",
        cl.torus(0.21, 0.065, (0, 0, 1.13), scarf, scale=(1, 0.95, 0.6)),
        cl.blob(0.062, (0.095, -0.235, 1.06), scarf),
        cl.blob(1, (0.135, -0.245, 0.89), scarf, scale=(0.050, 0.028, 0.125),
                rot=(math.radians(-8), 0, math.radians(16))))
    # arms + hands: 4 fingers + thumb, palm pads
    for s, side in ((1, "L"), (-1, "R")):
        sh, el, wr = (0.265 * s, 0, 1.06), (0.33 * s, -0.02, 0.84), (0.345 * s, -0.05, 0.645)
        reg("chest", cl.blob(0.095, sh, fur_b))                                    # black shoulder
        ua = cl.capsule(sh, el, 0.075, fur_b)
        cl.add_fuzz(ua, length=0.009, count=2500)
        reg(f"upperarm.{side}", ua)
        reg(f"forearm.{side}", cl.capsule(el, wr, 0.065, fur_b), cl.blob(0.068, el, fur_b))
        hand = cl.blob(0.072, (0.345 * s, -0.055, 0.59), fur_b, scale=(0.95, 0.8, 1.0))
        bigpad = cl.blob(1, (0.345 * s, -0.114, 0.585), pad, scale=(0.030, 0.010, 0.038))
        reg(f"hand.{side}", hand, bigpad)
        fingers, th = _finger_pts(s)
        for i, (k, mid, tip) in enumerate(fingers):
            reg(f"f{i + 1}.prox.{side}", cl.capsule(k, mid, 0.0165, fur_b))
            reg(f"f{i + 1}.dist.{side}", cl.capsule(mid, tip, 0.0148, fur_b))
            reg(f"hand.{side}", cl.blob(1, (k.x, -0.108, 0.545), pad, scale=(0.010, 0.006, 0.012)))
        reg(f"thumb.prox.{side}", cl.capsule(th[0], th[1], 0.018, fur_b))
        reg(f"thumb.dist.{side}", cl.capsule(th[1], th[2], 0.016, fur_b))
    # legs
    for s, side in ((1, "L"), (-1, "R")):
        thigh = cl.capsule((0.155 * s, 0.01, 0.30), (0.165 * s, 0, 0.10), 0.085, fur_b)
        cl.add_fuzz(thigh, length=0.010, count=3000)
        reg(f"thigh.{side}", thigh,
            cl.blob(1, (0.165 * s, -0.035, 0.062), fur_b, scale=(0.082, 0.115, 0.060)))

    # face kit: brows, lids, glints, mouth, cheeks -> one mesh with the 7 shape keys
    kit = cl.FaceKit(scale=1.0, head_center=(0, 0, 1.33))
    kit.brow_drop = 0.042                 # keep angry brows above the black patch
    for s in (1, -1):
        E = Vector((0.108 * s, -0.247, 1.383))
        kit.add(cl.blob(1, (0.105 * s, -0.188, 1.515), fur_b, scale=(0.048, 0.012, 0.012),
                        rot=(0, math.radians(8 * s), 0)), "brow", cx=0.105 * s, w=0.048, side=s)
        kit.add(cl.dome(0.0485, E, fur_b, min_elev_deg=24),
                "lid", eye=E, angle=90)                    # cap rests over the top; blink swings it down
        kit.add(cl.dome(0.0463, E, eye_k, min_elev_deg=62, rot=(math.pi / 2, 0, 0)),
                "pupil", eye=E, R=0.0463)                  # round pupil lying on the eyeball surface
        kit.add(cl.blob(0.0075, (0.098 * s, -0.292, 1.396), glint), "glint", eye=E)
        kit.arc(E, 0.046, arc_m, k=1.0)                    # light happy arc for closed eyes
        C = Vector((0.092 * s, -0.190, 1.265))
        kit.add(cl.blob(0.045, C, fur_w, scale=(1, 0.6, 0.75)), "cheek", center=C,
                out=(C - Vector((0, 0, 1.31))).normalized())
    kit.mouth((0, -0.3365, 1.287), 0.047, 0.0055, mouth_m, curv=4.5, smile0=0.004)
    face = kit.finalize("momo_face")

    # armature: spine chain + arms with full finger bones + legs + ears
    bones = [("root", (0, 0, 0), (0, 0, 0.25), None),
             ("spine", (0, 0, 0.25), (0, 0, 0.95), "root"),
             ("chest", (0, 0, 0.95), (0, 0, 1.18), "spine"),
             ("head", (0, 0, 1.18), (0, 0, 1.50), "chest")]
    for s, side in ((1, "L"), (-1, "R")):
        bones += [(f"ear.{side}", (0.180 * s, 0.02, 1.50), (0.205 * s, 0.02, 1.60), "head"),
                  (f"upperarm.{side}", (0.265 * s, 0, 1.06), (0.33 * s, -0.02, 0.84), "chest"),
                  (f"forearm.{side}", (0.33 * s, -0.02, 0.84), (0.345 * s, -0.05, 0.645), f"upperarm.{side}"),
                  (f"hand.{side}", (0.345 * s, -0.05, 0.645), (0.345 * s, -0.06, 0.52), f"forearm.{side}"),
                  (f"thigh.{side}", (0.155 * s, 0.01, 0.30), (0.165 * s, 0, 0.10), "root")]
        fingers, th = _finger_pts(s)
        for i, (k, mid, tip) in enumerate(fingers):
            bones += [(f"f{i + 1}.prox.{side}", k, mid, f"hand.{side}"),
                      (f"f{i + 1}.dist.{side}", mid, tip, f"f{i + 1}.prox.{side}")]
        bones += [(f"thumb.prox.{side}", th[0], th[1], f"hand.{side}"),
                  (f"thumb.dist.{side}", th[1], th[2], f"thumb.prox.{side}")]
    arm = cl.build_armature("momo_rig", bones)
    for bone, objs in P.items():
        cl.bone_parent(arm, bone, *objs)
    cl.bone_parent(arm, "head", face)

    root = cz.empty((0, 0, 0))
    root.name = "momo_root"
    cz.parent(arm, root)
    root.location = loc
    return {"root": root, "arm": arm, "face": face, "H": H}


HAND_POSES = {   # (prox, dist) curl in degrees; index may override; splay spreads fingers
    "open":  {"curl": (0, 0), "thumb": (0, 0), "splay": 20},
    "relax": {"curl": (-48, -52), "thumb": (-24, -22), "splay": 3},
    "point": {"curl": (-96, -100), "index": (-4, 0), "thumb": (-50, -42), "splay": 0},
    "fist":  {"curl": (-98, -104), "thumb": (-62, -52), "splay": 0},
}


def hand_pose(arm, name, side="L"):
    p = HAND_POSES[name]
    for i in range(4):
        c = p.get("index", p["curl"]) if i == 0 else p["curl"]
        spread = p["splay"] * (-1 + i * 2 / 3)          # fan the 4 fingers
        cl.pose(arm, f"f{i + 1}.prox.{side}", (c[0], 0, spread))
        cl.pose(arm, f"f{i + 1}.dist.{side}", (c[1], 0, 0))
    cl.pose(arm, f"thumb.prox.{side}", (p["thumb"][0], 0, 0))
    cl.pose(arm, f"thumb.dist.{side}", (p["thumb"][1], 0, 0))


if __name__ == "__main__":
    cz.reset()
    cz.gpu_setup()
    cz.render_preset("final", motion_blur=False)
    ch = build()
    cl.stage(target=(0, 0, 0.9), scale=1.0, key=1000)
    cam = cz.camera(lens=60)
    cz.aim(cam, (0, -3.4, 0.95), (0, 0, 0.80))
    out = os.path.expanduser("~/momo-gullu/characters/momo.blend")
    os.makedirs(os.path.dirname(out), exist_ok=True)
    bpy.ops.wm.save_as_mainfile(filepath=out, compress=True)
    print(f"[build_momo] saved {out}")
