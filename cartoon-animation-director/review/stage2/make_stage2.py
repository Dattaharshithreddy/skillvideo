"""REVIEW ONLY. Builds the Stage 2 review package (2026-11-11).

Run: python3 make_stage2.py            all sheets + measurements
     python3 make_stage2.py video      also renders the review-only animation test (mp4)
Writes only into this folder. Reads the production engine; changes no production file.
"""
import math
import os
import subprocess
import sys
import numpy as np
import skia
from PIL import Image
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, '..', 'stage1'))
import sheetkit                                                                      # noqa: E402
sheetkit.BANNER = 'REVIEW ONLY  ·  PROPOSAL  ·  NOT AN APPROVED PRODUCTION ASSET  ·  Stage 2  ·  2026-11-11'
sheetkit.TMP = os.path.join(HERE, '_tmp.png')
from sheetkit import tile, place, sheet, BEIGE                                       # noqa: E402
from review_models import Doodle, LadduProfile, GajuProfile, trunk_draw             # noqa: E402
from review_models2 import LadduSideProfile, LadduAct, GajuProfile2, profile_head, oval, poly, smooth, tube, bez, arc_pts   # noqa: E402
from life_test import STUDIES, LAG, cumulative                                       # noqa: E402
from toon import Stage, W, H, GROUND                                                 # noqa: E402
from chars import Gaju                                                               # noqa: E402
from cast import Laddu                                                               # noqa: E402

STEEL = (206, 212, 220); STEEL_D = (176, 184, 196); MILK = (255, 255, 250); CLAY = (196, 112, 70); CLAY_D = (160, 86, 52)
L0 = Laddu(); G0 = Gaju()


def out(name):
    return os.path.join(HERE, name)


def ground(g, p, f):
    g.shape(poly([(-1200, 0), (1200, 0)], False), None, True, 3, (190, 176, 150))


def bowl(g, p, f):
    g.shape(smooth([(-58, -30), (58, -30), (44, -2), (-44, -2)], True, 0.35), STEEL)
    g.shape(oval(0, -30, 60, 11), STEEL_D)
    lv = p.get('level', 1.0)
    if lv > 0.03:
        g.shape(oval(0, -29 + (1 - lv) * 6, 50 * (0.6 + 0.4 * lv), 7 * (0.5 + 0.5 * lv)), MILK, True, 3)


def bowl_front(g, p, f):
    g.shape(poly(arc_pts(0, -30, 60, 11, 0, 180, 14) + [(-44, -2), (44, -2)]), STEEL)


def pot(g, p, f):
    g.shape(smooth([(-34, -104), (34, -104), (58, -60), (44, -6), (-44, -6), (-58, -60)], True, 0.5), CLAY)
    g.shape(oval(0, -104, 38, 10), CLAY_D)
    g.shape(smooth([(-50, -66), (0, -58), (50, -66)], False), None, True, 3, CLAY_D)


def wind(n=3, length=120, wob=10):
    def fn(g, p, f):
        for i in range(n):
            y = -i * 34
            g.shape(smooth([(0, y), (length * 0.35, y - wob), (length * 0.7, y + wob), (length, y)], False), None, True, 4, (150, 170, 190))
    return fn


def at(fn, dx=0, dy=0):
    return Doodle(fn, x=W / 2 + dx, y=GROUND - dy)


class Bowl(Doodle):
    POSE = dict(level=1.0)


def bowl_at(dx, level=1.0, front=False):
    a = Bowl(bowl_front if front else bowl, x=W / 2 + dx, y=GROUND, level=level)
    return a


G = at(ground)


def mk(cls, pose, base_dx=0, **more):
    q = dict(pose); q.update(more)
    dx = base_dx + q.pop('dxw', 0.0); dy = q.pop('y_up', 0.0)
    return place(cls, dx=dx, dy=dy, **q)


def mask_of(actors, box, scale=0.5):
    im = tile(actors, box, scale, bg=(255, 0, 255))
    a = np.asarray(im).astype(int)
    return np.abs(a - np.array((255, 0, 255))).sum(axis=2) > 60


def sil(m):
    return Image.fromarray(np.where(m[..., None], np.uint8(30), np.uint8(BEIGE)).astype(np.uint8))


def changed(m0, m1):
    """Share of the combined silhouette that differs between two poses (0 = identical outline)."""
    return 100.0 * (1 - (m0 & m1).sum() / max(1, (m0 | m1).sum()))


def share(cls, col, **pose):
    m = mask_of([place(cls, **pose)], (-400, -30, 400, 420))
    im = tile([place(cls, **pose)], (-400, -30, 400, 420), 0.5)
    d = np.sqrt(((np.asarray(im)[m].astype(int) - np.array(col)) ** 2).sum(axis=1))
    return 100 * (d < 40).mean()


def size(cls, **pose):
    m = mask_of([place(cls, **pose)], (-400, -30, 400, 420))
    ys, xs = np.where(m)
    return (ys.max() - ys.min()) / 0.5, (xs.max() - xs.min()) / 0.5


REPORT = []


def say(s=''):
    print(s); REPORT.append(s)


VIDEO = len(sys.argv) > 1 and sys.argv[1] == 'video'

# ================================================================== 1  Laddu: revised profile head
B = (-60, 60, 270, 330)
gl = [(0, (330 - 206) / 270, 'top of skull'), (0, (330 - 151) / 270, 'eye line'), (0, (330 - 93) / 270, 'chin')]


class _NoHead(Laddu):
    def _head(self, g, p):
        pass


def head_only(g, p, f):
    g.push(0, 0, 0, 0.86, 0.86)
    g.push(108, -178, 0, 1, 1, 0, 56)
    profile_head(L0, g, L0.pose(0))
    g.pop(); g.pop()


row1 = [
    (tile([place(Laddu, dx=105)], B, 0.9), 'Approved front head', 'prod'),
    (tile([place(Laddu, face=1.0)], B, 0.9), 'Approved side view today', 'prod'),
    (tile([place(LadduProfile)], B, 0.9), 'Stage 1 proposal (superseded): neck merged, far ear darker', 'info'),
    (tile([place(LadduSideProfile, face=1.0)], B, 0.9), 'REVISED: approved side body unchanged, profile head as a separate component', 'prop'),
]
row2 = [
    (tile([place(_NoHead, face=1.0)], B, 0.9), 'Construction 1: the approved side body alone, exactly as in production', 'prod'),
    (tile([at(head_only)], B, 0.9), 'Construction 2: the profile head alone, a separate piece', 'prop'),
    (tile([place(LadduSideProfile, face=1.0, head_dx=22.0, head_dy=10.0, head_rot=10.0)], B, 0.9), 'Head moved 22 forward, 10 down, tilted 10: still overlaps the body', 'prop'),
    (tile([place(LadduSideProfile, face=1.0, head_dx=56.0)], B, 0.9), 'Head moved 56 forward: a gap opens. This is the D10 limit, not fixed here', 'prop'),
]
sheet(out('REVIEW_S2_1_laddu_profile_head_revised.png'), 'Stage 2 · 1 · Laddu: revised profile head, separate head and body', [row1, row2], guide=gl,
      note='Changes from Stage 1: the head is a separate component placed at the approved head anchor; the body is the approved side body, untouched. '
           'Both ears are in the approved main fur colour. Muzzle shortened by 8. Skull made deeper at the back and flatter on top to match the approved head. '
           'Cheek fur redrawn as two points, as on the approved head.')

# ================================================================== 2  Gaju: revised profile + trunk alignment
B = (-190, -16, 190, 300)
gl = [(0, (300 - 276) / 316, 'top of cap'), (0, (300 - 172) / 316, 'eye line'), (0, (300 - 158) / 316, 'trunk root'), (0, (300 - 98) / 316, 'chin'), (0, 300 / 316, 'ground')]
EB = (-150, 60, 60, 280)
row1 = [
    (tile([G, place(Gaju)], B, 0.9), 'Approved front', 'prod'),
    (tile([G, place(Gaju, face=0.6, yaw=0.7)], B, 0.9), 'Approved three-quarter (face 0.6, yaw 0.7)', 'prod'),
    (tile([G, place(GajuProfile)], B, 0.9), 'Stage 1 proposal (superseded): no pink at rest, far ear darker', 'info'),
    (tile([G, place(GajuProfile2)], B, 0.9), 'REVISED: pink rim on the near ear, both ears in the main skin colour', 'prop'),
]
row2 = [
    (tile([place(GajuProfile)], EB, 1.5), 'Stage 1 ear, enlarged', 'info'),
    (tile([place(GajuProfile2)], EB, 1.5), 'REVISED ear, enlarged: same size, pink rim along the front edge', 'prop'),
    (tile([place(GajuProfile2, ear=0.9, ear_open=0.9)], EB, 1.5), 'REVISED, ear lifted: the inside shows', 'prop'),
]
sheet(out('REVIEW_S2_2_gaju_profile_revised.png'), 'Stage 2 · 2 · Gaju: revised profile, and trunk alignment', [row1, row2], guide=gl,
      note='The ear is the same size as in Stage 1. The pink is the approved inner-ear pink; no new colour. The darker tone is now used only for the tail, as in the approved model. '
           'Trunk root raised from 16 to 8 below the head centre (approved front view: 6), and moved 8 forward so it still clears the eye.')


def arc_len(pts):
    return sum(math.hypot(pts[i + 1][0] - pts[i][0], pts[i + 1][1] - pts[i][1]) for i in range(len(pts) - 1))


# the approved rest trunk, rebuilt from the production formula (trunk=(30, 92), bend 0, curl 0.7)
root = (0.0, 6.0); tx, ty = 30.0, 92.0; tip = (root[0] + tx, root[1] + ty)
c1 = (root[0] + tx * 0.05, root[1] + ty * 0.5 + 18); c2 = (tip[0] - tx * 0.2 - 0.7 * 30, tip[1] + 0.7 * 34)
appr = bez(root, c1, c2, tip, 22)
r0 = GajuProfile2.ROOT; a_, b_, t_ = GajuProfile2.REST
prof = bez(r0, (r0[0] + a_[0], r0[1] + a_[1]), (r0[0] + b_[0], r0[1] + b_[1]), (r0[0] + t_[0], r0[1] + t_[1]), 22)
say('TRUNK ALIGNMENT (approved front view against the revised profile proposal)')
say('| Measure | Approved front | Revised profile | Match |')
say('|---|---|---|---|')
say('| Root height below head centre | 6 | %d | within 2 |' % r0[1])
say('| Radius at the root, at the tip | 31, 12 | 31, 12 | same drawing |')
say('| Rest length along the centre line | %d | %d | %+d%% |' % (arc_len(appr), arc_len(prof), round(100 * (arc_len(prof) - arc_len(appr)) / arc_len(appr))))
say('| Lowest point of the rest trunk below head centre | %d | %d | |' % (max(q[1] for q in appr), max(q[1] for q in prof)))
say('| Wrinkle rings, nostrils, gripping finger | 8, 2, 1 | 8, 2, 1 | same drawing |')
say('| Nails per foot | 3 | 3 | same |')
say()
say('GAJU PINK SHARE: approved front %.0f%%, three-quarter %.0f%%, Stage 1 profile %.0f%%, revised profile at rest %.0f%%, revised with ear lifted %.0f%%' % (
    share(Gaju, Gaju.PINK), share(Gaju, Gaju.PINK, face=0.6, yaw=0.7), share(GajuProfile, Gaju.PINK), share(GajuProfile2, Gaju.PINK), share(GajuProfile2, Gaju.PINK, ear=0.9, ear_open=0.9)))
h0, w0 = size(Gaju); h1, w1 = size(GajuProfile2)
say('GAJU SIZE: approved %d tall; revised profile %d tall, %d wide' % (h0, h1, w1))
h0, w0 = size(Laddu, face=1.0); h1, w1 = size(LadduSideProfile, face=1.0)
say('LADDU SIZE: approved side %d tall x %d long; revised profile head on the approved body %d x %d' % (h0, w0, h1, w1))
say()

# trunk positions re-drawn on the revised profile
B = (-150, -14, 290, 300)
TR = [
    ('rest', None, dict(), []),
    ('creep along the floor', ((36, 50), (30, 160), (180, 150)), dict(lid=0.3, pupil=(0.8, 0.5)), []),
    ('dip and drink', ((60, 24), (112, 62), (118, 134)), dict(gulp=0.55, eye_open=0.0, happy=1.0), ['bowl']),
    ('sneeze', ((60, 4), (112, 0), (160, 12)), dict(eye_open=0.0, brow_ang=14, mouth_open=0.3), []),
    ('frozen', ((46, 64), (104, 126), (184, 148)), dict(eye_pop=1.3, pupil_s=0.5, pupil=(0.6, 0.6), brow=12, smile=-0.6, sweat=1.0), []),
]
tiles = []
for lab, cl, pose, extra in TR:
    a = place(GajuProfile2, **pose); a.trunk_cl = cl
    acts = [G] + ([bowl_at(204)] if extra else []) + [a] + ([bowl_at(204, front=True)] if extra else [])
    tiles.append((tile(acts, B, 0.6), lab, 'prop'))
sheet(out('REVIEW_S2_2b_gaju_trunk_on_revised_profile.png'), 'Stage 2 · 2b · Gaju: the pilot trunk positions on the revised profile', [tiles],
      note='The five positions the pilot needs, redrawn with the raised trunk root. The trunk is the approved drawing on new centre lines.')

# ================================================================== 3  Gaju: hiding pose B refined
B = (-250, -14, 250, 330)
HIDE = dict(sy=0.82, sx=1.22, ear=0.0, trunk=(4.0, 44.0), trunk_curl=1.0, brow=10, smile=-0.2, mouth_w=0.6)
rows = [[
    (tile([G, place(Gaju, sy=0.7, sx=1.12, ear=0.0, trunk=(4.0, 44.0), trunk_curl=1.0, pupil=(0.0, 0.7), brow=10, smile=-0.2, mouth_w=0.6), at(pot)], B, 0.7),
     'Stage 1 pose B', 'info'),
    (tile([G, place(Gaju, pupil=(-0.9, 0.1), brow_ang=-14, sweat=1.0, **HIDE), at(pot)], B, 0.7),
     'B1 squats behind the pot, eyes slide to the side to check', 'prod'),
    (tile([G, place(Gaju, pupil=(0.0, -0.2), eye_pop=1.15, brow_asym=1.0, head_dy=-14.0, **HIDE), at(pot)], B, 0.7),
     'B2 peeks: head rises a little, one brow up', 'prod'),
    (tile([G, place(Gaju, pupil=(0.0, 0.8), lid=0.5, head_dy=26.0, cap_dy=6.0, **dict(HIDE, sy=0.74, sx=1.35)), at(pot)], B, 0.7),
     'B3 ducks: only the cap, the ears and the feet show', 'prod'),
]]
sheet(out('REVIEW_S2_3_gaju_hiding_B_refined.png'), 'Stage 2 · 3 · Gaju: hiding pose B, refined', rows,
      note='All three are the approved model with controls it already has; nothing new is drawn. Upright posture kept. '
           'Squash now keeps volume (0.82 tall by 1.22 wide). The joke is that the ears and feet cannot be hidden. The pot is a placeholder prop.')

# ================================================================== 4  Gaju: small hops and fan
B = (-200, -14, 200, 400); S = 0.55
HOPS = [
    ('1 crouch\nframes 1-6', 0, dict(sy=0.78, sx=1.28, ear=-0.5, brow=6, pupil=(0.0, -0.6))),
    ('2 push off\nframes 7-8', 30, dict(sy=1.2, sx=0.83, ear=-0.9)),
    ('3 top, 80 px\nframes 9-14, slowest here', 80, dict(ear=0.3, smile=1.0, mouth_open=0.3)),
    ('4 down\nframes 15-18', 30, dict(sy=1.12, sx=0.89, ear=0.9)),
    ('5 land\nframe 19, one frame', 0, dict(sy=0.72, sx=1.39, ear=0.6)),
    ('6 settle\nframes 20-28, ears arrive late', 0, dict(sy=1.04, sx=0.96, ear=-0.5)),
]
hop = [(tile([G, place(Gaju, dy=dy, **pose)], B, S), lab, 'prod') for lab, dy, pose in HOPS]
fanA = []
for lab, pose, w in [('ears down', dict(ear=-0.5, brow=4), 0), ('ears up: air moves', dict(ear=0.9, mouth_open=0.3, smile=1.0), 1), ('ears down', dict(ear=-0.5), 0),
                     ('ears up', dict(ear=0.9, eye_open=0.0, happy=1.0, smile=1.0), 1)]:
    ex = [at(wind(2, 70, 6), dx=120, dy=250), at(wind(2, 70, 6), dx=-190, dy=250)] if w else []
    fanA.append((tile([G, place(Gaju, **pose)] + ex, B, S), lab + '\napproved model, ear control only', 'prod'))
fanB = []
for lab, pose, w in [('ear back', dict(ear_ang=-24, rot=-3, brow=6), 0), ('ear sweeps forward', dict(ear_ang=52, ear_open=0.9, rot=3, mouth_open=0.3, smile=1.0), 1),
                     ('ear back', dict(ear_ang=-20, rot=-2), 0), ('ear sweeps forward', dict(ear_ang=48, ear_open=0.9, eye_open=0.0, happy=1.0, smile=1.0), 1)]:
    ex = [at(wind(3, 100), dx=110, dy=200)] if w else []
    fanB.append((tile([G, place(GajuProfile2, dx=-40, **pose)] + ex, B, S), lab + '\nrevised profile', 'prop'))
sheet(out('REVIEW_S2_4_gaju_hops_and_fan.png'), 'Stage 2 · 4 · Gaju: small hops (preferred) and fan (for testing)', [hop, fanA, fanB],
      note='HOPS: approved model, existing controls, no new drawing. Squash and stretch keep volume. Top of the hop is 80 px, under a third of his height. '
           'Proposed timing: 28 frames per hop. These are key poses and a timing plan; they have not been tested in motion.\n'
           'FAN: feet stay on the ground in every pose; the ears are never enlarged; flapping gives no lift. Row 2 uses only the approved ear control. '
           'Row 3 needs the profile, which is still a proposal.\n'
           'Parachute and sail are deferred and are not in this package.')

# ================================================================== 6  Laddu Character Life Test
B = (-340, -16, 290, 330); S = 0.5
BOWLX = 150
NEUTRAL = place(Laddu, face=1.0)
say('LIFE TEST: how much of the silhouette changes between START and ACTION (0% = the outline did not move)')
say('| Study | Face-only change (how Stage 1 expressions worked) | Approved model, existing controls | Proposed acting rig |')
say('|---|---|---|---|')
for st in STUDIES:
    n = st['n']; dx0 = st['start_dx']
    props = cumulative(st['proposal']); exist = cumulative(st['existing'])
    bw = [G, bowl_at(BOWLX, st['level'])]; bf = [bowl_at(BOWLX, st['level'], front=True)]
    r_today = [
        (tile(bw + [place(Laddu, dx=dx0, face=1.0)] + bf, B, S), 'Model-sheet look: the approved side model at rest', 'prod'),
        (tile(bw + [place(Laddu, dx=dx0, face=1.0, **st['face_only'])] + bf, B, S), 'Stage 1 method: the face changes, the body does not', 'prod'),
    ]
    r_exist = []
    for i, pose in enumerate(exist):
        q = dict(pose); q.setdefault('face', 1.0)
        r_exist.append((tile(bw + [mk(Laddu, q, dx0)] + bf, B, S), 'key %d, existing controls only' % (i + 1), 'prod'))
    r_prop, r_sil, masks = [], [], []
    for i, (k, pose) in enumerate(zip(st['proposal'], props)):
        r_prop.append((tile(bw + [mk(LadduAct, pose, dx0)] + bf, B, S), 'f%d  %s' % (k[0] + 1, k[2]), 'prop'))
        m = mask_of([mk(LadduAct, pose, dx0)], B, S); masks.append(m)
        r_sil.append((sil(m).resize((m.shape[1] * 2 // 3, m.shape[0] * 2 // 3)), 'silhouette %d' % (i + 1), 'info'))
    m_face0 = mask_of([place(Laddu, dx=dx0, face=1.0)], B, S); m_face1 = mask_of([place(Laddu, dx=dx0, face=1.0, **st['face_only'])], B, S)
    e0 = dict(exist[0]); e0.setdefault('face', 1.0); e2 = dict(exist[2]); e2.setdefault('face', 1.0)
    m_e0 = mask_of([mk(Laddu, e0, dx0)], B, S); m_e2 = mask_of([mk(Laddu, e2, dx0)], B, S)
    say('| %d %s | %.0f%% | %.0f%% | %.0f%% |' % (n, st['name'], changed(m_face0, m_face1), changed(m_e0, m_e2), changed(masks[0], masks[2])))
    sheet(out('REVIEW_S2_6_%d_life_%s.png' % (n, st['name'].lower().replace(' ', '_'))),
          'Stage 2 · 6.%d · Laddu Character Life Test: %s' % (n, st['name'].upper()), [r_today, r_exist, r_prop, r_sil],
          note='INTENTION: %s\nPROPOSED TIMING at 24 fps (a plan, not yet judged in motion): %s\nWHAT MAKES IT ALIVE: %s\n'
               'Row 1 is the approved model as a model sheet shows it. Row 2 is the most the approved model can do with its existing controls. '
               'Row 3 uses a review-only acting rig: the approved head, paws, colours and line on a body whose spine, chest, hips, legs and tail can be posed. '
               'Row 4 is row 3 in silhouette.' % (st['intent'], st['timing'], st['alive']))
say()

# ================================================================== review-only animation test
if VIDEO:
    FB_ = skia.Font(skia.Typeface('DejaVu Sans', skia.FontStyle.Bold()), 30); FS_ = skia.Font(skia.Typeface('DejaVu Sans'), 26)
    parts = []
    for st in STUDIES:
        end = st['end']
        stg = Stage(end, bg=lambda c, cam, f: c.clear(skia.Color(*BEIGE))); stg.grain = 0
        gr = Doodle(ground, x=W / 2, y=GROUND); b0 = bowl_at(BOWLX, st['level']); b1 = bowl_at(BOWLX, st['level'], front=True)
        cat = LadduAct(x=W / 2 + st['start_dx'], y=GROUND, face=0.0); cat.shadow = 60
        stg.add(gr, b0, cat, b1)
        stg.cut(0, x=W / 2 - 20, y=GROUND - 170, zoom=1.75)
        keys = st['proposal']
        first = dict(keys[0][3]); first.pop('dxw', None); first.pop('y_up', None)
        cat.set(0, **first)
        for (fr, ease, label, ch), du in zip(keys[1:], st['dur']):
            prev = fr - du
            body, lagged = {}, {}
            for k, v in ch.items():
                if k == 'dxw':
                    body['x'] = W / 2 + st['start_dx'] + v
                elif k == 'y_up':
                    body['y'] = GROUND - v
                elif k in LAG and LAG[k]:
                    lagged.setdefault(LAG[k], {})[k] = v
                else:
                    body[k] = v
            if body:
                cat.move(prev, fr, ease, **body)
            for lg, d_ in lagged.items():
                cat.move(prev + lg, fr + lg, 'over', **d_)
        if st['n'] == 2:                                              # two small sniffs while he holds
            cat.move(19, 21, 'io', head_dy=-17.0); cat.move(21, 23, 'io', head_dy=-12.0)
        if st['n'] == 1:
            cat.move(45, 47, 'out', earflick=1.0); cat.move(47, 50, 'out', earflick=0.0)
        if st['n'] == 5:
            cat.move(69, 73, 'io', lid=1.0); cat.move(73, 78, 'io', lid=0.65)
        labels = [(k[0], k[2]) for k in keys]

        def overlay(g, f, st=st, labels=labels):
            c = g.c
            c.drawRect(skia.Rect.MakeLTRB(0, 0, W, 64), skia.Paint(Color=skia.Color(176, 32, 40)))
            c.drawString('REVIEW ONLY · ANIMATION TEST · NOT APPROVED · Stage 2', 24, 42, FB_, skia.Paint(AntiAlias=True, Color=skia.ColorWHITE))
            ink = skia.Paint(AntiAlias=True, Color=skia.Color(58, 42, 40))
            c.drawString('Study %d: %s' % (st['n'], st['name']), 24, 120, FB_, ink)
            cur = [l for fr, l in labels if fr <= f][-1]
            c.drawString(cur[:62], 24, 160, FS_, ink)
            c.drawString('frame %d of %d  (24 fps)' % (f + 1, st['end']), 24, H - 40, FS_, ink)
        stg.overlays.append(overlay)
        part = out('_part%d.mp4' % st['n'])
        stg.render(part, scale=0.5, crf=22)
        parts.append(part)
        fr_pick = sorted(set([k[0] for k in keys] + [min(end - 1, k[0] + 3) for k in keys] + [end - 1]))
        stg.sheet(fr_pick, out('_frames_study%d.png' % st['n']), cols=6, scale=0.2)
    with open(out('_list.txt'), 'w') as fh:
        for p_ in parts:
            fh.write("file '%s'\n" % p_)
    subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-f', 'concat', '-safe', '0', '-i', out('_list.txt'), '-c:v', 'libx264', '-crf', '22',
                    '-preset', 'slow', '-tune', 'animation', '-pix_fmt', 'yuv420p', '-movflags', '+faststart', out('REVIEW_S2_6_laddu_life_test_animation.mp4')], check=True)
    for p_ in parts + [out('_list.txt')]:
        os.remove(p_)
    say('animation test written: REVIEW_S2_6_laddu_life_test_animation.mp4')

open(out('measurements.txt'), 'w').write('\n'.join(REPORT) + '\n')
if os.path.exists(sheetkit.TMP):
    os.remove(sheetkit.TMP)
print('sheets:', sorted(f for f in os.listdir(HERE) if f.startswith('REVIEW_S2_')))
