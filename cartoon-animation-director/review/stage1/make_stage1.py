"""REVIEW ONLY. Builds the Stage 1 reference sheets for Harshith's review (2026-11-11).

Run: python3 make_stage1.py
Writes REVIEW_S1_*.png next to this file and prints the consistency measurements.
Reads the production engine; writes nothing outside this folder; changes no production file.
"""
import math
import os
import sys
import numpy as np
from PIL import Image
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from sheetkit import tile, place, sheet, BEIGE                                       # noqa: E402
from review_models import Doodle, LadduProfile, GajuProfile, GajuReview, smooth, oval, poly, tube, two_seg, _limb_path, arc_pts   # noqa: E402
from toon import W, GROUND                                                           # noqa: E402
from chars import Gaju, Bheemu                                                       # noqa: E402
from cast import Laddu                                                               # noqa: E402

L0 = Laddu(); G0 = Gaju()
STEEL = (206, 212, 220); STEEL_D = (176, 184, 196); MILK = (255, 255, 250); CLAY = (196, 112, 70); CLAY_D = (160, 86, 52)
WOOD = (176, 128, 84); LINE = (150, 140, 120)


def out(name):
    return os.path.join(HERE, name)


# ------------------------------------------------------------------ props (review sheets only)
def ground(g, p, f):
    g.shape(poly([(-900, 0), (900, 0)], False), None, True, 3, (190, 176, 150))


def bowl(g, p, f):
    g.shape(smooth([(-58, -30), (58, -30), (44, -2), (-44, -2)], True, 0.35), STEEL)
    g.shape(oval(0, -30, 60, 11), STEEL_D)
    lv = p.get('level', 1.0)
    if lv > 0.03:
        g.shape(oval(0, -29 + (1 - lv) * 6, 50 * (0.6 + 0.4 * lv), 7 * (0.5 + 0.5 * lv)), MILK, True, 3)


def bowl_front(g, p, f):
    """The near wall of the bowl, drawn over the character so a tongue or trunk tip goes into it."""
    g.shape(poly(arc_pts(0, -30, 60, 11, 0, 180, 14) + [(-44, -2), (44, -2)]), STEEL)


def pot(g, p, f):
    g.shape(smooth([(-34, -104), (34, -104), (58, -60), (44, -6), (-44, -6), (-58, -60)], True, 0.5), CLAY)
    g.shape(oval(0, -104, 38, 10), CLAY_D)
    g.shape(smooth([(-50, -66), (0, -58), (50, -66)], False), None, True, 3, CLAY_D)


def stool(g, p, f):
    g.shape(poly([(-70, -150), (70, -150), (70, -134), (-70, -134)]), WOOD)
    for x in (-56, 56):
        g.shape(poly([(x - 8, -134), (x + 8, -134), (x + 12, 0), (x - 12, 0)]), WOOD)


def cart(g, p, f):
    g.shape(poly([(-110, -30), (110, -30), (110, -16), (-110, -16)]), WOOD)
    for x in (-74, 74):
        g.shape(oval(x, -8, 15, 15), (90, 80, 76)); g.shape(oval(x, -8, 4, 4), STEEL)


def laddu_ball(g, p, f):
    g.shape(oval(0, 0, 24, 24), (236, 176, 60))
    for a in (20, 140, 260):
        g.shape(oval(math.cos(math.radians(a)) * 9, math.sin(math.radians(a)) * 9, 3, 3), (200, 130, 40), False)


def wind(n=3, length=120, wob=10):
    def fn(g, p, f):
        for i in range(n):
            y = -i * 34
            g.shape(smooth([(0, y), (length * 0.35, y - wob), (length * 0.7, y + wob), (length, y)], False), None, True, 4, (150, 170, 190))
    return fn


def spray(g, p, f):
    for a in (-24, -10, 4, 18, 32):
        t = math.radians(a)
        g.shape(poly([(20 * math.cos(t), 20 * math.sin(t)), (70 * math.cos(t), 70 * math.sin(t))], False), None, True, 4, (230, 236, 246))
        g.shape(oval(84 * math.cos(t), 84 * math.sin(t), 5, 5), MILK, True, 2)


def arrow(dx, dy, dash=True):
    def fn(g, p, f):
        n = 9
        for i in range(n):
            if dash and i % 2:
                continue
            g.shape(poly([(dx * i / n, dy * i / n), (dx * (i + 1) / n, dy * (i + 1) / n)], False), None, True, 4, (120, 60, 140))
        L = math.hypot(dx, dy) or 1; ux, uy = dx / L, dy / L
        g.shape(poly([(dx - ux * 16 - uy * 9, dy - uy * 16 + ux * 9), (dx, dy), (dx - ux * 16 + uy * 9, dy - uy * 16 - ux * 9)], False), None, True, 4, (120, 60, 140))
    return fn


def at(fn, dx=0, dy=0, **kw):
    return Doodle(fn, x=W / 2 + dx, y=GROUND - dy, **kw)


def mask(cls, **pose):
    im = tile([place(cls, **pose)], (-400, -30, 400, 420), 0.5, bg=(255, 0, 255))
    a = np.asarray(im).astype(int)
    return (np.abs(a - np.array((255, 0, 255))).sum(axis=2) > 60), im


def size(cls, **pose):
    m, _ = mask(cls, **pose)
    ys, xs = np.where(m)
    return (ys.max() - ys.min()) / 0.5, (xs.max() - xs.min()) / 0.5


def palette_share(cls, base, **pose):
    """Share of the character's pixels that match one of the production class's named colours."""
    m, _ = mask(cls, **pose)
    im = tile([place(cls, **pose)], (-400, -30, 400, 420), 0.5)
    px = np.asarray(im)[m].astype(int)
    named = [v for k, v in vars(base).items() if k.isupper() and isinstance(v, tuple) and len(v) == 3 and k != 'STREAK'] + [base.INK]
    cols = np.array(named)
    dist = np.sqrt(((px[:, None, :] - cols[None, :, :]) ** 2).sum(axis=2)).min(axis=1)
    return 100.0 * (dist < 40).mean()


G = at(ground)

# ================================================================== 1a  Laddu: profile head
B = (-60, 60, 270, 330)
gl = [(0, (330 - 206) / 270, 'top of skull'), (0, (330 - 151) / 270, 'eye line'), (0, (330 - 93) / 270, 'chin')]
rows = [[
    (tile([place(Laddu, dx=105)], B, 1.0), 'Front head (approved model)', 'prod'),
    (tile([place(Laddu, face=1.0)], B, 1.0), 'Side view as it is today:\nfront-facing head on a side body', 'prod'),
    (tile([place(LadduProfile)], B, 1.0), 'Proposed true profile head', 'prop'),
    (tile([place(LadduProfile, ear_back=0.9)], B, 1.0), 'Proposed profile, ears back', 'prop'),
]]
sheet(out('REVIEW_S1_1a_laddu_profile_head.png'), 'Stage 1 · 1a · Laddu: profile head', rows, guide=gl,
      note='Same head height, eye line, eye drawing, colours and line weights as the approved front head.\nNew: the skull and muzzle outline, one visible eye, ear placement, side whisker pad, forehead stripes seen from the side.')

# ================================================================== 1b  Laddu: crouch and lap
B = (-200, -14, 340, 280)
seq = [
    ('1 walks in', dict(), 1.0, 0),
    ('2 sniffs: head reaches, chest starts down', dict(crouch=0.35, reach=0.5, lid=0.1), 1.0, 0),
    ('3 crouch: chest low, rump high', dict(crouch=1.0), 1.0, 0),
    ('4 lap: tongue out to the milk', dict(crouch=1.0, tongue=0.62, lid=0.5), 1.0, 0),
    ('5 lap: tongue back, eyes shut (bliss)', dict(crouch=1.0, tongue=0.0, eye_open=0.0, happy=1.0, smile=1.0, ear_back=0.3), 0.8, 0),
]
row = []
for lab, pose, lv, _ in seq:
    row.append((tile([G, at(bowl, dx=262), place(LadduProfile, **pose), at(bowl_front, dx=262)], B, 0.72), lab, 'prop'))
sheet(out('REVIEW_S1_1b_laddu_crouch_lap.png'), 'Stage 1 · 1b · Laddu: crouch-and-lap, in profile on the floor', [row[:3], row[3:]],
      note='Five key poses, not animation. The neck is drawn as one outline with the body, so the head cannot separate (the D10 problem).\nThe bowl is a placeholder prop.')

# ================================================================== 1c  Laddu: paw shapes
def paw_tile(fn, label, kind='prop'):
    return (tile([at(fn)], (-80, -22, 80, 100), 2.2), label, kind)


def paw_side(g, p, f):
    L0._ink(g, _limb_path(two_seg((-6, -96), (-4, -54), (0, -11)), [18, 17.5, 16.5, 15.5, 15, 15, 15.5, 16.5, 17], tip=0.2), L0.FUR)
    L0._paw(g, 5, -9, 19, 11, L0.CREAM, d=1)


def paw_front(g, p, f):
    L0._ink(g, _limb_path(two_seg((0, -96), (0, -54), (0, -11)), [16, 16, 15.5, 15, 15, 15, 15.5, 16.5, 17], tip=0.2), L0.FUR)
    L0._paw(g, 0, -9, 19, 12, L0.CREAM)


def paw_raised(g, p, f):
    L0._ink(g, _limb_path(two_seg((-20, -96), (-2, -62), (22, -46)), [18, 17.5, 16.5, 15.5, 15, 15, 15.5, 16.5, 17], tip=0.2), L0.FUR)
    g.push(30, -40, 62)
    L0._paw(g, 4, 0, 19, 11, L0.CREAM, d=1)
    g.pop()


def paw_press(g, p, f):
    G0._ink(g, tube([(-80, -10), (0, -12), (80, -10)], 13, 12, False), G0.SKIN)
    L0._ink(g, _limb_path(two_seg((-4, -96), (-2, -60), (0, -32)), [18, 17.5, 16.5, 15.5, 15, 15, 15.5, 17, 18], tip=0.2), L0.FUR)
    L0._paw(g, 4, -27, 24, 9, L0.CREAM, d=1)


def paw_under(g, p, f):
    L0._ink(g, _limb_path(two_seg((34, -4), (20, -24), (4, -44)), [17, 17, 16.5, 16, 15.5, 15.5, 16, 17, 18], tip=0.2), L0.FUR)
    L0._ink(g, oval(0, -58, 24, 25), L0.CREAM)
    L0._ink(g, smooth([(-11, -52), (0, -60), (11, -52), (8, -42), (-8, -42)], True, 0.8), L0.PINK, 2.5)
    for a in (-60, -22, 18, 56):
        t = math.radians(a - 90)
        L0._ink(g, oval(math.cos(t) * 17, -58 + math.sin(t) * 17 - 1, 5.5, 6.5, a), L0.PINK, 2.5)


def paw_reach(g, p, f):
    L0._ink(g, _limb_path(two_seg((-76, -66), (-36, -50), (4, -40)), [18, 17.5, 16.5, 15.5, 15, 15, 15.5, 16.5, 17], tip=0.2), L0.FUR)
    g.push(12, -38, 12)
    L0._paw(g, 4, 0, 21, 12, L0.CREAM, d=1)
    g.pop()


rows = [[paw_tile(paw_side, 'Side, flat on the ground\n(same paw drawing as production)', 'prod'),
         paw_tile(paw_front, 'Front, flat\n(same paw drawing as production)', 'prod'),
         paw_tile(paw_raised, 'Raised mid-step, wrist bent'),
         ], [
         paw_tile(paw_press, 'Pressing down on the trunk'),
         paw_tile(paw_reach, 'Reaching to pat'),
         paw_tile(paw_under, 'Underside: one large pad, four toe pads'),
         ]]
sheet(out('REVIEW_S1_1c_laddu_paws.png'), 'Stage 1 · 1c · Laddu: paw shapes', rows,
      note='Four visible toes on every paw (three partings). No dewclaw. No claws shown: nobody is ever really hurt in this series.\nThe underside with pads is new information; the approved model never shows the sole.')

# ================================================================== 2a  Gaju: turned views
B = (-190, -16, 190, 300)
gl = [(0, (300 - 276) / 316, 'top of cap'), (0, (300 - 172) / 316, 'eye line'), (0, (300 - 98) / 316, 'chin'), (0, 300 / 316, 'ground')]
rows = [[
    (tile([G, place(Gaju)], B, 0.95), 'Front (approved model)', 'prod'),
    (tile([G, place(Gaju, face=0.6, yaw=0.7)], B, 0.95), 'Three-quarter: approved model\nwith face 0.6, yaw 0.7', 'prod'),
    (tile([G, place(GajuProfile)], B, 0.95), 'Proposed profile, upright like the approved model', 'prop'),
    (tile([G, place(GajuProfile, ear=0.9, ear_open=0.9, mouth_open=0.5, smile=1.0)], B, 0.95), 'Proposed profile: ear lifted,\npink inside showing, mouth open', 'prop'),
    (tile([G, place(GajuProfile, upright=0.0, dx=-20)], B, 0.95), 'Alternative: on all fours.\nNOT the approved posture', 'prop'),
]]
sheet(out('REVIEW_S1_2a_gaju_views.png'), 'Stage 1 · 2a · Gaju: turned views', rows, guide=gl,
      note='Correction to my earlier audit: the approved model already has a head-turn control (yaw). It gives the three-quarter view shown here.\nWhat is missing from the approved model is a true profile and a back view. The profile is the proposal.')

# ================================================================== 2b  Gaju: trunk positions
B = (-150, -14, 290, 300)
TR = [
    ('1 rest', None, dict(), []),
    ('2 curl to the mouth (eating)', ((74, 6), (76, 118), (-2, 62)), dict(mouth_open=0.4, smile=1.0), []),
    ('3 reach forward', ((70, -6), (130, 20), (184, -4)), dict(), []),
    ('4 creep along the floor', ((36, 50), (30, 152), (186, 142)), dict(lid=0.3, pupil=(0.8, 0.5)), []),
    ('5 dip and drink: a swallow\ntravels up the trunk', ((66, 20), (120, 56), (126, 126)), dict(gulp=0.55, eye_open=0.0, happy=1.0), [at(bowl, dx=204), at(bowl_front, dx=204)]),
    ('6 wrap around a laddu', ((88, 0), (110, 150), (24, 104)), dict(smile=1.0), [at(laddu_ball, dx=16 + 62 + 56, dy=148 - 92)]),
    ('7 raised in alarm', ((70, -16), (128, -40), (92, -108)), dict(eye_pop=1.4, pupil_s=0.5, brow=14, mouth_open=0.5, ear=0.6, ear_open=0.7, trunk_up=1.0), []),
    ('8 sneeze', ((64, 0), (120, -4), (170, 8)), dict(eye_open=0.0, brow_ang=14, mouth_open=0.3), [at(spray, dx=16 + 62 + 172, dy=148 - 8)]),
    ('9 frozen: caught under a paw', ((50, 60), (110, 120), (196, 140)), dict(eye_pop=1.3, pupil_s=0.5, pupil=(0.6, 0.6), brow=12, smile=-0.6, sweat=1.0), []),
]
tiles = []
for lab, cl, pose, extra in TR:
    a = place(GajuProfile, **pose); a.trunk_cl = cl
    back = [e for e in extra if e.fn is bowl]
    front = [e for e in extra if e.fn is not bowl]
    tiles.append((tile([G] + back + [a] + front, B, 0.62), lab, 'prop'))
sheet(out('REVIEW_S1_2b_gaju_trunk.png'), 'Stage 1 · 2b · Gaju: trunk positions (drawn on the proposed profile)', [tiles[:5], tiles[5:]],
      note='The trunk itself is the approved drawing (taper, wrinkles, two nostrils, one gripping finger) placed on new centre lines.\nHe wraps objects with the trunk, he does not pinch them. Positions 4, 5, 8 and 9 are the ones the pilot uses.')

# ================================================================== 2c  Gaju: hiding pose
B = (-210, -14, 330, 320)
a1 = place(Gaju, sx=0.8, sy=1.1, ear=-1.0, trunk=(6.0, 52.0), trunk_curl=1.2, pupil=(0.9, 0.0), brow=8, brow_ang=-12, smile=-0.3, mouth_w=0.6, sweat=1.0)
a2 = place(Gaju, sy=0.7, sx=1.12, ear=0.0, trunk=(4.0, 44.0), trunk_curl=1.0, pupil=(0.0, 0.7), brow=10, smile=-0.2, mouth_w=0.6)
a3 = place(GajuProfile, sx=0.84, sy=1.08, pupil=(0.7, 0.6), brow=10, brow_ang=-12, smile=-0.4)
a3.trunk_cl = ((30, 60), (40, 150), (202, 116))
rows = [[
    (tile([G, a1, at(pot)], B, 0.8), 'A  Breathes in and stands thin behind the pot.\nApproved model, existing controls only', 'prod'),
    (tile([G, a2, at(pot)], B, 0.8), 'B  Squats low; ears stick out both sides.\nApproved model, existing controls only', 'prod'),
    (tile([G, at(bowl, dx=236), a3, at(pot, dx=-4), at(bowl_front, dx=236)], B, 0.8), 'C  Profile: the trunk on the floor gives him away.\nUses the proposed profile', 'prop'),
]]
sheet(out('REVIEW_S1_2c_gaju_hiding.png'), 'Stage 1 · 2c · Gaju: "hiding" behind a pot far too small', rows,
      note='A and B need no new drawing: they are the approved model posed with controls it already has. C depends on the profile proposal.\nThe pot is a placeholder prop.')

# ================================================================== 3  Gaju: movement concepts
B = (-250, -14, 250, 430); S = 0.5
fan = []
for lab, pose, extra in [
        ('wind-up: ear swings back', dict(ear_ang=-26, rot=-4, brow=6), []),
        ('sweep: ear swings forward', dict(ear_ang=58, ear_open=0.9, rot=3, mouth_open=0.3, smile=1.0), [at(wind(3, 110), dx=150, dy=190)]),
        ('back again', dict(ear_ang=-22, rot=-3), [at(wind(2, 80, 6), dx=190, dy=170)]),
        ('result: he cools the dosa, blows\nout a lamp, sends papers flying', dict(ear_ang=50, ear_open=0.9, eye_open=0.0, happy=1.0, smile=1.0), [at(wind(3, 130), dx=140, dy=190)])]:
    fan.append((tile([G, place(GajuProfile, dx=-50, **pose)] + extra, B, S), lab, 'prop'))
para = []
for lab, dy, pose, extra in [
        ('hops off a stool', 150, dict(sy=0.8, sx=1.12, ear=-0.6), [at(stool, dx=-60)]),
        ('falls: ears streaming up', 118, dict(sy=1.12, sx=0.92, ear=0.9, eye_pop=1.3, pupil_s=0.6, mouth_open=0.5, brow=12), [at(stool, dx=-190), at(arrow(0, 70), dx=180, dy=330)]),
        ('ears snap wide: the fall slows,\nhe sways down', 90, dict(ear=0.35, ear_size=1.4, rot=6, eye_open=0.0, happy=1.0, smile=1.0, armL=(-14.0, -18.0), armR=(14.0, -18.0)), [at(arrow(0, 40), dx=220, dy=250)]),
        ('soft landing', 0, dict(sy=0.84, sx=1.1, ear=-0.3, smile=0.8), [])]:
    para.append((tile([G] + [e for e in extra if e.fn is stool] + [place(GajuReview, dx=(-60 if lab.startswith('hops') else 10), dy=dy, **pose)] + [e for e in extra if e.fn is not stool], B, S), lab, 'prop'))
sail = []
for lab, dx, pose, extra in [
        ('on a wheeled plank, no wind:\nnothing happens', -60, dict(face=0.6, yaw=0.5, lid=0.4, smile=-0.2), []),
        ('a gust: ears fill like sails', -40, dict(face=0.6, yaw=0.5, ear_size=1.35, rot=5, eye_pop=1.3, brow=12), [at(wind(3, 100), dx=-230, dy=250)]),
        ('he rolls along', 20, dict(face=0.6, yaw=0.5, ear_size=1.35, rot=8, eye_open=0.0, happy=1.0, smile=1.0, mouth_open=0.5),
         [at(wind(3, 90), dx=-230, dy=250), at(wind(2, 60, 4), dx=-200, dy=60)]),
        ('wind drops: ears droop, he stops', 60, dict(face=0.6, yaw=0.5, ear=-0.7, lid=0.5, smile=-0.3), [])]:
    sail.append((tile([G, at(cart, dx=dx), place(GajuReview, dx=dx, dy=30, **pose)] + extra, B, S), lab, 'prop'))
hop = []
for lab, dy, pose in [
        ('crouch', 0, dict(sy=0.76, sx=1.18, ear=-0.5, brow=6, pupil=(0.0, -0.6))),
        ('push off', 40, dict(sy=1.22, sx=0.86, ear=-0.9)),
        ('top: about 90 px up', 90, dict(ear=0.3, smile=1.0, mouth_open=0.3)),
        ('down', 36, dict(sy=1.14, sx=0.9, ear=0.9)),
        ('land: squash, ears flop late', 0, dict(sy=0.7, sx=1.26, ear=-0.6))]:
    hop.append((tile([G, place(GajuReview, dy=dy, **pose)], (-200, -14, 200, 430), S), lab, 'prod'))
sheet(out('REVIEW_S1_3_gaju_movement.png'), 'Stage 1 · 3 · Gaju: proposed original movement concepts', [fan, para, sail, hop],
      note='Row 1 FAN: ears push air sideways; his feet stay on the ground.   Row 2 PARACHUTE: only ever downward; ears slow a fall, they never lift him.\n'
           'Row 3 SAIL: needs wind and wheels; no wind, no movement.   Row 4 SMALL HOPS: the approved model posed with its existing controls; nothing new is drawn.\n'
           'Rule in all four: flapping never gains height. Rows 2 and 3 use one review-only control (ear size); row 1 uses the proposed profile.')

# ================================================================== 4  pilot expressions
LAD = [
    ('BLISS', dict(eye_open=0.0, happy=1.0, smile=1.0, ear_back=0.3, head_rot=-6)),
    ('SUSPICION', dict(eye_open=1.0, lid=0.45, brow_ang=8, brow_asym=0.9, pupil=(0.9, 0.1), smile=-0.3, ear_back=0.35, head_rot=5)),
    ('SLOW BURN', dict(eye_open=1.0, lid=0.55, brow_ang=22, pupil=(0.9, 0.0), smile=-0.9, mouth_w=0.8, ear_back=0.85)),
    ('TAKE', dict(eye_open=1.0, lid=0.0, eye_pop=1.5, pupil_s=0.5, brow=16, mouth_open=0.8, ear_back=0.0, head_sy=1.1, head_dy=-12)),
]
GAJ = [
    ('SNEAKY', dict(lid=0.3, brow_asym=1.0, smile=0.9, pupil=(0.8, 0.1), ear=-0.5, head_rot=4)),
    ('FROZEN', dict(eye_pop=1.3, pupil_s=0.5, brow=12, smile=-0.5, mouth_w=0.6, ear=-1.0, sweat=1.0)),
    ('TAKE', dict(eye_pop=1.5, pupil_s=0.5, brow=18, mouth_open=0.8, ear=1.0, cap_dy=-26, head_sy=1.1, head_dy=-10)),
    ('GUILTY', dict(brow_ang=-20, brow=4, smile=-0.5, mouth_w=0.7, pupil=(-0.7, 0.4), ear=-0.7, head_rot=-6, sweat=1.0)),
]
HB = (-150, 50, 150, 300)                 # Laddu front head
HP = (-40, 40, 280, 300)                  # Laddu profile head
GB = (-190, 60, 190, 360)                 # Gaju front head
GP = (-150, 50, 210, 360)                 # Gaju profile head
r1 = [(tile([place(Laddu, **pose)], HB, 0.8), lab + '\napproved head, new recipe', 'prod') for lab, pose in LAD]
r2 = [(tile([place(LadduProfile, **{k: v for k, v in pose.items()})], HP, 0.8), lab + '\nproposed profile head', 'prop') for lab, pose in LAD]
r3 = [(tile([place(Gaju, **pose)], GB, 0.66), lab + '\napproved head, new recipe', 'prod') for lab, pose in GAJ]
gp = []
for lab, pose in GAJ:
    q = dict(pose); q['ear_open'] = 0.8 if q.get('ear', 0) > 0.5 else 0.0
    gp.append((tile([place(GajuProfile, **q)], GP, 0.66), lab + '\nproposed profile', 'prop'))
sheet(out('REVIEW_S1_4_pilot_expressions.png'), 'Stage 1 · 4 · Expression references for the pilot ("The Milk Bowl")', [r1, r2, r3, gp],
      note='Rows 1 and 2: the four requested, for Laddu: bliss, suspicion, slow burn, take.   Rows 3 and 4: Gaju\'s own beats in the pilot (extra).\n'
           'Rows 1 and 3 are the approved heads with new parameter recipes. No existing preset was changed and none of these is saved as a preset.\n'
           'NOT YET TESTED: nobody but Claude has tried to read these. None of them is claimed to pass.')

# ================================================================== consistency measurements
print('CONSISTENCY MEASUREMENTS (proposal against the approved model)')
h0, w0 = size(Laddu, face=1.0); h1, w1 = size(LadduProfile)
print('Laddu side, standing:  approved %d tall x %d wide   proposal %d x %d   (height %+.1f%%)' % (h0, w0, h1, w1, 100 * (h1 - h0) / h0))
h0, w0 = size(Gaju); h1, w1 = size(GajuProfile)
print('Gaju standing:         approved front %d tall x %d wide   proposed profile %d x %d   (height %+.1f%%)' % (h0, w0, h1, w1, 100 * (h1 - h0) / h0))
print('Named-colour share:    Laddu approved side %.0f%%, proposed profile %.0f%%, proposed crouch %.0f%%' % (
    palette_share(Laddu, Laddu, face=1.0), palette_share(LadduProfile, Laddu), palette_share(LadduProfile, Laddu, crouch=1.0)))
print('                       Gaju approved front %.0f%%, proposed profile %.0f%%' % (palette_share(Gaju, Gaju), palette_share(GajuProfile, Gaju)))
m0, _ = mask(Gaju); m1, _ = mask(GajuReview)
print('GajuReview with ear_size 1 is pixel-identical in outline to production Gaju:', bool((m0 == m1).all()))
print('sheets written:', sorted(f for f in os.listdir(HERE) if f.startswith('REVIEW_S1_')))
