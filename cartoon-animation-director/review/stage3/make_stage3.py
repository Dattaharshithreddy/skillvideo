"""REVIEW ONLY. Builds the Stage 3 comparison: current (Stage 2) beside revised (Stage 3).
Run: python3 make_stage3.py [video]. Writes only into this folder; changes no production file."""
import math, os, subprocess, sys
import numpy as np
import skia
from PIL import Image
HERE = os.path.dirname(os.path.abspath(__file__))
for d in ('', '../stage2', '../stage1'):
    sys.path.insert(0, os.path.join(HERE, d))
import sheetkit
sheetkit.BANNER = 'REVIEW ONLY  ·  PROPOSAL  ·  NOT AN APPROVED PRODUCTION ASSET  ·  Stage 3  ·  2026-11-11'
sheetkit.TMP = os.path.join(HERE, '_tmp.png')
from sheetkit import sheet, tile, place, BEIGE
from review_models import Doodle
from review_models2 import LadduAct, oval, poly, smooth, arc_pts
from review_models3 import LadduAct2, LEG
from life_test import STUDIES, LAG
from life_test3 import S3, VERDICT, CHANGES
from toon import Stage, W, H, GROUND
from cast import Laddu

STEEL = (206, 212, 220); STEEL_D = (176, 184, 196); MILK = (255, 255, 250)
BOWLX = 150; VIDEO = len(sys.argv) > 1 and sys.argv[1] == 'video'
out = lambda n: os.path.join(HERE, n)
REPORT = []


def say(s=''):
    print(s); REPORT.append(s)


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


class Bowl(Doodle):
    POSE = dict(level=1.0)


def v1_moves(st):
    """The Stage 2 study expressed as moves, exactly as it was rendered then."""
    keys = st['proposal']; mv = []
    for (fr, ease, label, ch), du in zip(keys[1:], st['dur']):
        body, lag = {}, {}
        for k, v in ch.items():
            (lag.setdefault(LAG[k], {}) if k in LAG and LAG[k] else body)[k] = v
        mv.append((fr, du, ease, label, body))
        for lg, d_ in lag.items():
            mv.append((fr + lg, du, 'over', None, d_))
    if st['n'] == 2:
        mv += [(21, 2, 'io', None, dict(head_dy=-17.0)), (23, 2, 'io', None, dict(head_dy=-12.0))]
    if st['n'] == 1:
        mv += [(47, 2, 'out', None, dict(earflick=1.0)), (50, 3, 'out', None, dict(earflick=0.0))]
    if st['n'] == 5:
        mv += [(73, 4, 'io', None, dict(lid=1.0)), (78, 5, 'io', None, dict(lid=0.65))]
    return dict(n=st['n'], name=st['name'], start_dx=st['start_dx'], end=st['end'], level=st['level'], start=dict(keys[0][3]), start_label=keys[0][2], moves=mv)


FB_ = skia.Font(skia.Typeface('DejaVu Sans', skia.FontStyle.Bold()), 30); FS_ = skia.Font(skia.Typeface('DejaVu Sans'), 26)


def build(st, cls, tag, zoom=True, end=None):
    end = end or st['end']
    stg = Stage(end, bg=lambda c, cam, f: c.clear(skia.Color(*BEIGE))); stg.grain = 0
    cat = cls(x=W / 2 + st['start_dx'], y=GROUND, face=0.0); cat.shadow = 60 if zoom else 0
    stg.add(Doodle(ground, x=W / 2, y=GROUND), Bowl(bowl, x=W / 2 + BOWLX, y=GROUND, level=st['level']), cat, Bowl(bowl_front, x=W / 2 + BOWLX, y=GROUND))
    if zoom:
        stg.cut(0, x=W / 2 - 20, y=GROUND - 170, zoom=1.75)
    cat.set(0, **st['start'])
    labels = [(0, st['start_label'])]
    for fr, du, ease, label, ch in st['moves']:
        q = {}
        for k, v in ch.items():
            if k == 'dxw':
                q['x'] = W / 2 + st['start_dx'] + v
            elif k == 'y_up':
                q['y'] = GROUND - v
            else:
                q[k] = v
        cat.move(fr - du, fr, ease, **q)
        if label:
            labels.append((fr, label))

    def overlay(g, f):
        c = g.c
        c.drawRect(skia.Rect.MakeLTRB(0, 0, W, 64), skia.Paint(Color=skia.Color(176, 32, 40)))
        c.drawString('REVIEW ONLY · ANIMATION TEST · NOT APPROVED', 24, 42, FB_, skia.Paint(AntiAlias=True, Color=skia.ColorWHITE))
        ink = skia.Paint(AntiAlias=True, Color=skia.Color(58, 42, 40))
        c.drawString(tag, 24, 112, FB_, skia.Paint(AntiAlias=True, Color=skia.Color(200, 100, 20) if 'REVISED' in tag else skia.Color(110, 110, 120)))
        c.drawString('Study %d: %s' % (st['n'], st['name']), 24, 154, FB_, ink)
        cur = [l for fr, l in labels if fr <= f][-1]
        c.drawString(cur[:58], 24, 192, FS_, ink); c.drawString(cur[58:116], 24, 224, FS_, ink)
        c.drawString('frame %d of %d  (24 fps)' % (min(f, st['end'] - 1) + 1, st['end']), 24, H - 40, FS_, ink)
    if zoom:
        stg.overlays.append(overlay)
    return stg, cat, labels


BOX = (-340, -16, 290, 330); SC = 0.5


def grab(stg, f):
    stg.still(f, sheetkit.TMP, SC)
    im = Image.open(sheetkit.TMP).convert('RGB')
    return im.crop((int((W / 2 + BOX[0]) * SC), int((GROUND - BOX[3]) * SC), int((W / 2 + BOX[2]) * SC), int((GROUND - BOX[1]) * SC)))


# ---------------------------------------------------------------- identity and proportion checks
def mask(cls, **pose):
    a = np.asarray(tile([place(cls, **pose)], (-400, -30, 400, 420), 0.5, bg=(255, 0, 255))).astype(int)
    return np.abs(a - np.array((255, 0, 255))).sum(axis=2) > 60


def dims(m):
    ys, xs = np.where(m)
    return (ys.max() - ys.min()) * 2, (xs.max() - xs.min()) * 2


A = mask(Laddu, face=1.0); R1 = mask(LadduAct, breath=0.0); R2 = mask(LadduAct2, breath=0.0)
say('IDENTITY AT REST (acting rig against the approved side model)')
say('| | Approved side model | Stage 2 rig | Stage 3 rig |')
say('|---|---|---|---|')
say('| Height x length | %d x %d | %d x %d | %d x %d |' % (dims(A) + dims(R1) + dims(R2)))
say('| Outline overlap with the approved model | 100%% | %.0f%% | %.0f%% |' % (100 * (A & R1).sum() / (A | R1).sum(), 100 * (A & R2).sum() / (A | R2).sum()))
say()
sit1 = dict(STUDIES[4]['proposal'][0][3]); [sit1.update(k[3]) for k in STUDIES[4]['proposal'][1:3]]
r1 = math.hypot(58 + sit1['pawN'][0] - (60 + sit1['chest'][0] - 6), -11 + sit1['pawN'][1] - (-104 + sit1['chest'][1] + 8)) / 94.0
say('FORELEG LENGTH (shoulder-to-paw reach as a share of the natural leg length)')
say('| Pose | Stage 2 | Stage 3 |'); say('|---|---|---|')
rig = LadduAct2()
worst = (0, '')
rows_reach = {}
for st in S3:
    stg, cat, labels = build(st, LadduAct2, '', zoom=False)
    for fr, lab in labels:
        r = rig.reach(cat.pose(fr))
        rows_reach[(st['n'], lab.split(' ')[0])] = r
        if r > worst[0]:
            worst = (r, 'study %d %s' % (st['n'], lab.split(' ')[0]))
say('| Sitting (satisfaction) | %.0f%% | %.0f%% |' % (100 * r1, 100 * rows_reach[(5, 'SIT')]))
say('| Longest reach in any labelled key, all five studies | not measured | %.0f%% (%s) |' % (100 * worst[0], worst[1]))
say()

# ---------------------------------------------------------------- comparison sheets, one per study
row_id = [
    (tile([place(Laddu, face=1.0)], (-250, -16, 250, 320), 0.6), 'Approved side model', 'prod'),
    (tile([place(LadduAct, breath=0.0)], (-250, -16, 250, 320), 0.6), 'Stage 2 rig at rest: a new body outline, %d%% overlap' % round(100 * (A & R1).sum() / (A | R1).sum()), 'info'),
    (tile([place(LadduAct2, breath=0.0)], (-250, -16, 250, 320), 0.6), 'Stage 3 rig at rest: the approved outline on a spine, %d%% overlap' % round(100 * (A & R2).sum() / (A | R2).sum()), 'prop'),
    (tile([place(LadduAct, **sit1)], (-250, -16, 250, 320), 0.6), 'Stage 2 sitting: forelegs %d%% of natural length' % round(100 * r1), 'info'),
]
stg5, cat5, lab5 = build(S3[4], LadduAct2, '', zoom=False)
sitf = [fr for fr, l in lab5 if l.startswith('SIT')][0]
p5 = {k: v for k, v in cat5.pose(sitf).items() if k in LadduAct2.POSE and k not in ('face',)}
row_id.append((tile([place(LadduAct2, **p5)], (-250, -16, 250, 320), 0.6), 'Stage 3 sitting: shoulders stay at standing height, forelegs %d%%' % round(100 * rows_reach[(5, 'SIT')]), 'prop'))
sheet(out('REVIEW_S3_0_identity_and_proportion_fixes.png'), 'Stage 3 · 0 · Laddu acting rig: outline and foreleg fixes', [row_id[:3], row_id[3:]],
      note='OUTLINE: the Stage 2 rig drew a new tube-shaped body, which is why only 86% of its outline matched (reported as 85% in Stage 2). The Stage 3 rig carries the approved body outline, belly patch and stripes on a spine: at rest it is the approved drawing, and it bends from there.\n'
           'FORELEGS: in Stage 2 I raised the chest when he sat, so the legs had to stretch. A sitting cat keeps its shoulders at about standing height and lowers its hips. Corrected: legs stay at natural length.\n'
           'The head is a separate component in both. Nothing here is implemented in production.')

for st in S3:
    n = st['n']; old = v1_moves(STUDIES[n - 1])
    s1, c1, l1 = build(old, LadduAct, '', zoom=False)
    s2, c2, l2 = build(st, LadduAct2, '', zoom=False)
    r_old = [(grab(s1, min(old['end'] - 1, fr + (3 if fr else 0))), 'f%d %s' % (fr + 1, lab), 'info') for fr, lab in l1]
    tiles = [(grab(s2, min(st['end'] - 1, fr)), 'f%d %s' % (fr + 1, lab), 'prop') for fr, lab in l2]
    half = (len(tiles) + 1) // 2
    timing = ' | '.join('%d %s' % (fr + 1, lab.split(' ')[0].lower() if lab.split(' ')[0].isupper() else lab.split(' ')[0]) for fr, lab in l2)
    sheet(out('REVIEW_S3_%d_%s_current_vs_revised.png' % (n, st['name'].lower().replace(' ', '_'))),
          'Stage 3 · %d · %s: current (grey, Stage 2) beside revised (orange)' % (n, st['name'].upper()), [r_old, tiles[:half], tiles[half:]],
          note='YOUR DIRECTION: %s.\nWHAT CHANGED: %s\nTIMING NOTES (frame each key is reached, 24 fps): %s | end %d.\n'
               'Tiles are frames taken from the animation test, so sheet and video show the same thing. Key poses and timing are proposals; motion has not been judged.' % (VERDICT[n], CHANGES[n], timing, st['end']))

# ---------------------------------------------------------------- animation tests
if VIDEO:
    sides, solo = [], []
    for st in S3:
        n = st['n']; old = v1_moves(STUDIES[n - 1]); end = max(st['end'], old['end'])
        a, _, _ = build(old, LadduAct, 'CURRENT (Stage 2)', end=end); b, _, _ = build(st, LadduAct2, 'REVISED (Stage 3)', end=end)
        pa, pb, ps = out('_a%d.mp4' % n), out('_b%d.mp4' % n), out('_s%d.mp4' % n)
        a.render(pa, scale=0.5, crf=20); b.render(pb, scale=0.5, crf=20)
        subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-i', pa, '-i', pb, '-filter_complex', 'hstack', '-c:v', 'libx264', '-crf', '20', '-pix_fmt', 'yuv420p', ps], check=True)
        b2, _, _ = build(st, LadduAct2, 'REVISED (Stage 3)'); pc = out('_c%d.mp4' % n); b2.render(pc, scale=0.5, crf=20)
        sides.append(ps); solo.append(pc); os.remove(pa); os.remove(pb)
    for parts, name in ((sides, 'REVIEW_S3_laddu_life_test_current_vs_revised.mp4'), (solo, 'REVIEW_S3_laddu_life_test_revised.mp4')):
        with open(out('_list.txt'), 'w') as fh:
            fh.writelines("file '%s'\n" % p_ for p_ in parts)
        subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-f', 'concat', '-safe', '0', '-i', out('_list.txt'), '-c:v', 'libx264', '-crf', '22', '-preset', 'slow',
                        '-tune', 'animation', '-pix_fmt', 'yuv420p', '-movflags', '+faststart', out(name)], check=True)
        for p_ in parts:
            os.remove(p_)
    os.remove(out('_list.txt'))
    say('animation tests written: side-by-side and revised-only')
open(out('measurements.txt'), 'w').write('\n'.join(REPORT) + '\n')
if os.path.exists(sheetkit.TMP):
    os.remove(sheetkit.TMP)
print(sorted(f for f in os.listdir(HERE) if f.startswith('REVIEW_S3_')))
