"""Gullu the baby elephant — code-built toy-soft cartoon character (momo-gullu series).

Run headless to (re)build the .blend:
    blender -b --factory-startup -P build_gullu.py
Importable: build() creates Gullu in the current czlib scene and returns his parts.

Spec: small round chunky, ~0.64 m (Momo is 2.5x), huge floppy ears wider than the body,
short trunk curling up at the tip (bendy-bone chain), backwards yellow cap exactly
#FFC93C and slightly too small, big shiny eyes with lashes, rosy cheeks, permanent
excited smile (mouth centred), no fingers — rounded nub hands — but toenails on the
front of his feet. Face shape keys per series spec; eyelids close flush (same centre
and near-same radius as the eyeball, so no bulge).
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

SKIN, PINK, CAP = "#8FA3B8", "#F4A6B8", "#FFC93C"
SCALE = 0.936                     # built 0.688 m to the cap button -> 0.644 m
H = 0.644
TRUNK = [(0, -0.150, 0.472), (0, -0.208, 0.408), (0, -0.228, 0.315),
         (0, -0.238, 0.235), (0, -0.276, 0.212)]      # long hanging trunk, gentle curl at the tip


def build(loc=(0, 0, 0)):
    skin = cl.mat_fuzz("gullu_skin", SKIN, rough=0.6)
    pink = cl.mat_fuzz("gullu_pink", PINK, rough=0.55, sheen=0.7)
    cap = cl.mat_cloth("gullu_cap", CAP, rough=0.55, sheen=0.0, emit=1.2)     # #FFC93C
    cb = cap.node_tree.nodes["Principled BSDF"]                              # emission-only: specular/base
    cb.inputs["Base Color"].default_value = (0, 0, 0, 1)                     # washes the colour out to pastel
    cb.inputs["Specular IOR Level"].default_value = 0.0
    eye_w = cl.mat_shiny("gullu_sclera", "#FAF9F6", rough=0.12)
    eye_k = cl.mat_shiny("gullu_iris", "#2A2B33", rough=0.06)
    lash = cz.mat_pbr("gullu_lash", cl.hex_lin("#23242B"), rough=0.5)
    nailm = cl.mat_shiny("gullu_nail", "#EFE6D8", rough=0.3)
    slate = cl.mat_fuzz("gullu_slate", "#4E6076", rough=0.6)
    brow_m = cl.mat_fuzz("gullu_brow", "#3D4C60", rough=0.6)
    arc_m = cz.mat_pbr("gullu_arc", cl.hex_lin("#2A3342"), rough=0.5)
    mouth_m = cz.mat_pbr("gullu_mouth", cl.hex_lin("#3A2A33"), rough=0.6)
    glint = cz.mat_glow((1, 1, 1), 2.5, "gullu_glint")

    P = {}
    def reg(bone, *objs):
        P.setdefault(bone, []).extend(objs)

    body = cl.blob(0.195, (0, 0, 0.26), skin, scale=(1.0, 0.95, 1.0))
    head = cl.blob(0.175, (0, -0.01, 0.468), skin, scale=(1.0, 0.95, 0.98))
    cl.add_fuzz(body, length=0.008, count=11000)           # visible short fuzz, not smooth plastic
    cl.add_fuzz(head, length=0.007, count=9000)
    reg("body", body)
    reg("head", head)
    # huge floppy ears: curved spherical shells with real thickness, swept back ~30deg
    # so they read edge-on in profile; pink inner shell on the concave (front) side
    EAR_R, EAR_SWEEP = 0.62, 5
    for s, side in ((1, "L"), (-1, "R")):
        eul = (math.radians(-90), 0, math.radians(-EAR_SWEEP * s))
        n = Euler(eul).to_matrix() @ Vector((0, 0, 1))       # shell bulge direction (back + out)
        eloc = Vector((0.250 * s, 0.050, 0.475)) - n * EAR_R   # cap centre sits beside the head
        ear = cl.dome(EAR_R, eloc, skin, min_elev_deg=73, rot=eul, seg=48)
        ear.modifiers.new("thick", "SOLIDIFY").thickness = 0.022
        ear.name = f"gullu_ear.{side}"
        cl.add_fuzz(ear, length=0.005, count=2200)
        inner = cl.dome(EAR_R - 0.028, eloc, pink, min_elev_deg=76, rot=eul, seg=40)
        reg(f"ear.{side}", ear, inner)
    # trunk: his "hand" — a long smooth tube weighted to a 4-bone chain
    trunk = cl.tube(TRUNK, [0.055, 0.047, 0.038, 0.030, 0.023], skin, name="gullu_trunk")
    reg(None, trunk)   # handled by rig_chain_weights
    # eyes: big and shiny with lashes; lids flush (same centre, radius barely larger)
    kit = cl.FaceKit(scale=0.8, head_center=(0, -0.01, 0.468))
    for s in (1, -1):
        E = Vector((0.068 * s, -0.150, 0.515))
        reg("head", cl.blob(0.040, E, eye_w))
        kit.add(cl.dome(0.0405, E, eye_k, min_elev_deg=40, rot=(math.pi / 2, 0, 0)),
                "pupil", eye=E, R=0.0405)
        kit.add(cl.blob(0.010, (0.061 * s, -0.196, 0.527), glint), "glint", eye=E)
        kit.add(cl.blob(0.005, (0.075 * s, -0.192, 0.508), glint), "glint", eye=E)
        kit.arc(E, 0.040, arc_m, k=0.95)                   # dark happy arc for closed eyes
        kit.add(cl.dome(0.0422, E, skin, min_elev_deg=24, rot=(math.radians(-14), 0, 0)),
                "lid", eye=E, angle=104, tilt=14)          # rests tilted back so neutral eyes are wide open
        for j, (dx, dz) in enumerate(((0.014, 0.034), (0.028, 0.028), (0.038, 0.018))):
            base = E + Vector((dx * s, -0.020, dz))
            kit.add(cl.capsule(base, base + Vector((0.011 * s, -0.011, 0.012)), 0.0030, lash),
                    "lash", eye=E, angle=104, tilt=14)
        kit.add(cl.blob(1, (0.070 * s, -0.1335, 0.578), brow_m, scale=(0.038, 0.010, 0.0095),
                        rot=(0, math.radians(3 * s), 0)), "brow", cx=0.070 * s, w=0.038, side=s)
        C = Vector((0.118 * s, -0.112, 0.43))
        kit.add(cl.blob(0.038, C, pink, scale=(1, 0.45, 0.8)), "cheek", center=C,
                out=(C - Vector((0, -0.01, 0.468))).normalized())
    # permanent excited smile, centred on the face directly under the trunk base
    kit.mouth((0, -0.160, 0.405), 0.075, 0.010, mouth_m, curv=3.0, smile0=0.036)
    face = kit.finalize("gullu_face")
    # backwards yellow cap, slightly too small, with button
    reg("head",
        cl.blob(0.105, (0, 0.012, 0.603), cap, scale=(1, 1, 0.72), rot=(math.radians(10), 0, 0)),
        cl.blob(1, (0, 0.118, 0.600), cap, scale=(0.070, 0.095, 0.011), rot=(math.radians(18), 0, 0)),
        cl.blob(0.016, (0, 0.025, 0.688), cap))
    # arms: rounded nubs, NO fingers
    for s, side in ((1, "L"), (-1, "R")):
        sh, nub = (0.160 * s, 0, 0.30), (0.200 * s, -0.045, 0.175)
        reg(f"arm.{side}", cl.capsule(sh, nub, 0.045, skin), cl.blob(0.050, nub, skin))
    # stubby legs; toenails on the FRONT of each foot
    for s, side in ((1, "L"), (-1, "R")):
        foot = (0.09 * s, -0.02, 0.045)
        objs = [cl.capsule((0.085 * s, 0, 0.14), (0.088 * s, 0, 0.05), 0.052, skin),
                cl.blob(1, foot, skin, scale=(0.062, 0.080, 0.042))]
        for dx in (-0.034, 0.0, 0.034):
            objs.append(cl.blob(1, (foot[0] + dx * 0.9, -0.097, 0.032), nailm,
                                scale=(0.021, 0.012, 0.019), rot=(0, 0, math.radians(-dx * 300))))
        reg(f"leg.{side}", *objs)
    # tiny tail with a tuft
    reg("body", cl.tube([(0, 0.178, 0.27), (0, 0.205, 0.225), (0, 0.208, 0.185)],
                        [0.009, 0.007, 0.006], skin, name="gullu_tail"),
        cl.blob(0.016, (0, 0.209, 0.175), slate))

    bones = [("root", (0, 0, 0), (0, 0, 0.10), None),
             ("body", (0, 0, 0.10), (0, 0, 0.40), "root"),
             ("head", (0, 0, 0.40), (0, 0, 0.62), "body")]
    for s, side in ((1, "L"), (-1, "R")):
        bones += [(f"ear.{side}", (0.155 * s, 0.01, 0.50), (0.30 * s, 0.01, 0.455), "head"),
                  (f"arm.{side}", (0.160 * s, 0, 0.30), (0.200 * s, -0.045, 0.175), "body"),
                  (f"leg.{side}", (0.085 * s, 0, 0.14), (0.09 * s, -0.01, 0.03), "root")]
    for i in range(4):
        bones.append((f"trunk.{i + 1}", TRUNK[i], TRUNK[i + 1],
                      "head" if i == 0 else f"trunk.{i}"))
    bones.append(("tail", (0, 0.178, 0.27), (0, 0.208, 0.18), "body"))
    arm = cl.build_armature("gullu_rig", bones)
    try:                                   # bendy-bone trunk per series spec
        for i in range(4):
            arm.data.bones[f"trunk.{i + 1}"].bbone_segments = 4
    except Exception:
        pass
    for bone, objs in P.items():
        if bone:
            cl.bone_parent(arm, bone, *objs)
    cl.bone_parent(arm, "head", face)
    cl.rig_chain_weights(trunk, arm, TRUNK, "trunk")

    root = cz.empty((0, 0, 0))
    root.name = "gullu_root"
    cz.parent(arm, root)
    root.location = loc
    root.scale = (SCALE,) * 3                 # cap button tops out at 0.644 m: Momo (1.61 m) is exactly 2.5x
    return {"root": root, "arm": arm, "face": face, "H": H}


if __name__ == "__main__":
    cz.reset()
    cz.gpu_setup()
    cz.render_preset("final", motion_blur=False)
    ch = build()
    cl.stage(bottom="#FFE9C9", top="#FFD9C2", floor="#F2E3C8",
             target=(0, 0, 0.33), scale=0.6, key=1000)
    cam = cz.camera(lens=60)
    cz.aim(cam, (0, -1.5, 0.38), (0, 0, 0.32))
    out = os.path.expanduser("~/momo-gullu/characters/gullu.blend")
    os.makedirs(os.path.dirname(out), exist_ok=True)
    bpy.ops.wm.save_as_mainfile(filepath=out, compress=True)
    print(f"[build_gullu] saved {out}")
