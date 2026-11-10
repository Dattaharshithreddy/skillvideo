"""Render every character-sheet cell with Cycles OptiX.

    blender -b --factory-startup -P render_cells.py [-- CELLS_DIR]

Produces: per-view turnaround cells, per-expression head cells, a hand-pose row for
Momo, and the raw lineup frame. make_sheets.py composites them into the final PNGs.
"""
import os, sys, math
HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)
sys.path.insert(0, os.path.expanduser("~/.claude/skills/cgi-shorts/blender"))
import bpy
from mathutils import Vector
import czlib as cz
import charlib as cl
import build_momo
import build_gullu

argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
CELLS = os.path.abspath(argv[0]) if argv else os.path.expanduser("~/momo-gullu/renders/.cells")
os.makedirs(CELLS, exist_ok=True)

TURN = [("front", 0), ("side_r", 90), ("back", 180), ("side_l", 270)]
EXPR = ["neutral", "happy", "laugh", "surprised", "sleepy", "angry", "sad", "cheeky"]
HANDS = ["open", "relax", "point", "fist"]


def fresh():
    cz.reset()
    dev = cz.gpu_setup()
    cz.render_preset("final", motion_blur=False)
    cz.S.cycles.samples = 96
    try:                       # colour-accurate transform so spec colours (#FFC93C cap) stay vivid
        cz.S.view_settings.view_transform = "Khronos PBR Neutral"
        cz.S.view_settings.look = "None"
    except TypeError:
        pass
    print(f"[cells] device={dev}", flush=True)


def still(path, rx, ry):
    cz.S.render.resolution_x, cz.S.render.resolution_y = rx, ry
    cz.S.render.resolution_percentage = 100
    cz.S.render.filepath = path
    bpy.ops.render.render(write_still=True)
    print(f"[cells] wrote {os.path.basename(path)}", flush=True)


def momo_cells():
    fresh()
    ch = build_momo.build()
    cl.stage(bottom="#BEE3F2", top="#E7F5EC", floor="#CFE8DB", target=(0, 0, 0.9), scale=1.0, key=1000)
    cam = cz.camera(lens=60)
    cz.aim(cam, (0, -3.3, 0.95), (0, 0, 0.80))
    for name, ang in TURN:
        ch["root"].rotation_euler.z = math.radians(ang)
        still(f"{CELLS}/momo_turn_{name}.png", 520, 1040)
    ch["root"].rotation_euler.z = 0
    cam.data.lens = 85
    cz.aim(cam, (0, -1.65, 1.40), (0, -0.05, 1.36))
    for name in EXPR:
        cl.apply_expression(ch["face"], name)
        still(f"{CELLS}/momo_expr_{name}.png", 640, 640)
    cl.apply_expression(ch["face"], "neutral")
    cam.data.lens = 80
    arm = ch["arm"]
    for name in HANDS:
        cl.pose_reset(arm)
        cl.pose(arm, "upperarm.L", (0, 0, -125))         # raise the arm in the image plane: palm stays to camera
        cl.pose(arm, "forearm.L", (0, 0, -25))
        build_momo.hand_pose(arm, name, side="L")
        bpy.context.view_layer.update()
        hp = (arm.matrix_world @ arm.pose.bones["hand.L"].matrix).translation
        tgt = hp + Vector((-0.03, 0, 0.075))
        cz.aim(cam, tgt + Vector((0, -0.80, 0)), tgt)
        still(f"{CELLS}/momo_hand_{name}.png", 640, 640)
    cl.pose_reset(arm)


def curl_trunk(arm):
    """Curl the long trunk up beside the cheek so the mouth stays visible (trunk = his hand)."""
    for i, rot in enumerate(((-10, 0, 55), (-20, 0, 30), (-30, 0, 10), (-35, 0, 0))):
        cl.pose(arm, f"trunk.{i + 1}", rot)


def gullu_cells():
    fresh()
    ch = build_gullu.build()
    cl.stage(bottom="#FFE9C9", top="#FFD9C2", floor="#F2E3C8", target=(0, 0, 0.33), scale=0.6, key=1000)
    cam = cz.camera(lens=50)
    cz.aim(cam, (0, -1.75, 0.42), (0, 0, 0.345))
    curl_trunk(ch["arm"])                                # gentle curl, mouth visible in every view
    for name, ang in TURN:
        ch["root"].rotation_euler.z = math.radians(ang)
        still(f"{CELLS}/gullu_turn_{name}.png", 760, 1000)
    ch["root"].rotation_euler.z = 0
    cam.data.lens = 65
    cz.aim(cam, (0, -1.55, 0.49), (0, -0.02, 0.465))
    for name in EXPR:
        cl.apply_expression(ch["face"], name)
        still(f"{CELLS}/gullu_expr_{name}.png", 640, 640)
    cl.apply_expression(ch["face"], "neutral")
    cl.pose_reset(ch["arm"])


def lineup():
    fresh()
    momo = build_momo.build(loc=(-0.52, 0, 0))
    gullu = build_gullu.build(loc=(0.45, 0, 0))
    momo["root"].rotation_euler.z = math.radians(-10)
    gullu["root"].rotation_euler.z = math.radians(12)
    cl.apply_expression(momo["face"], "happy")
    cl.apply_expression(gullu["face"], "laugh")
    curl_trunk(gullu["arm"])
    cl.stage(bottom="#BEE3F2", top="#E7F5EC", floor="#CFE8DB", target=(0, 0, 0.8), scale=1.0, key=1100)
    cam = cz.camera(lens=50)
    cz.aim(cam, (0, -5.0, 0.98), (-0.03, 0, 0.84))
    still(f"{CELLS}/lineup_raw.png", 1920, 1150)


momo_cells()
gullu_cells()
lineup()
print("[cells] all done", flush=True)
