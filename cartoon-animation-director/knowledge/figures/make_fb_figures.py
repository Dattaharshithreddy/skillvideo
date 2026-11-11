"""Builds the figures and prints the tables used in Frame_By_Frame_Animation.md.
Run: python3 make_fb_figures.py
Uses only the approved production models and their existing controls. Nothing from the review branch."""
import os, sys
import numpy as np
import skia
from PIL import Image, ImageDraw, ImageFont
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', '..', '..', 'toon-slapstick', 'engine'))
from toon import Stage, W, GROUND
from chars import Gaju
from cast import Laddu
BEIGE = (240, 232, 214); PAPER = (252, 250, 244); INK = (58, 42, 40); RED = (150, 30, 40)
FB = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf', 24); F = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf', 17)
TMP = os.path.join(HERE, '_t.png')


def stage(n):
    st = Stage(n, bg=lambda c, cam, f: c.clear(skia.Color(*BEIGE))); st.grain = 0
    return st


def frame(st, f, box, sc=0.5):
    st.still(f, TMP, sc)
    im = Image.open(TMP).convert('RGB')
    return im.crop((int((W / 2 + box[0]) * sc), int((GROUND - box[3]) * sc), int((W / 2 + box[2]) * sc), int((GROUND - box[1]) * sc)))


# ------------------------------------------------------------------ the hop: 28 frames, approved Gaju, existing controls
st = stage(30); g = Gaju(x=W / 2, y=GROUND, face=0.0); g.shadow = 70; st.add(g)
KEYS = [  # (reached at frame, length, ease, role, what, pose)
    (6, 5, 'out', 'KEY', 'crouch (anticipation)', dict(sy=0.78, sx=1.28, ear=-0.5, brow=6, pupil=(0.0, -0.6))),
    (8, 2, 'snap', 'KEY', 'push off (stretch)', dict(y=GROUND - 30, sy=1.2, sx=0.83, ear=-0.9)),
    (14, 6, 'out', 'KEY', 'top of the hop', dict(y=GROUND - 80, sy=1.0, sx=1.0, ear=0.3, smile=1.0, mouth_open=0.3)),
    (18, 4, 'in', 'KEY', 'falling (stretch)', dict(y=GROUND - 6, sy=1.12, sx=0.89, ear=0.9)),
    (19, 1, 'lin', 'KEY', 'contact (squash, one frame)', dict(y=GROUND, sy=0.72, sx=1.39, ear=0.6)),
    (22, 3, 'out', 'BREAKDOWN', 'rebound past rest', dict(sy=1.06, sx=0.94, ear=-0.5)),
    (28, 6, 'io', 'KEY', 'settle to rest', dict(sy=1.0, sx=1.0, ear=0.0, brow=0, pupil=(0.0, 0.0), smile=0.3, mouth_open=0.0)),
]
for fr, ln, ease, role, what, pose in KEYS:
    g.move(fr - ln, fr, ease, **pose)
role = {0: ('KEY', 'rest')}
for fr, ln, ease, r, what, pose in KEYS:
    role[fr] = (r, what)
print('HOP X-SHEET (approved Gaju, existing controls; film frame 1 = engine frame 0)')
print('| Frame | Height (px) | Tall x wide | Drawing | Role | Note |')
print('|---|---|---|---|---|---|')
BOX = (-200, -14, 200, 400); tiles = []; prev = None; dn = 0; rows = []
for f in range(29):
    p = g.frame_pose(f)
    key = (round(p['y'], 1), round(p['sy'], 3), round(p['sx'], 3), round(p['ear'], 3))
    new = key != prev
    if new:
        dn += 1
    prev = key
    r, what = role.get(f, ('in-between' if new else 'held', ''))
    if not new and r == 'KEY':
        what = 'KEY LOST: ' + what + ' never appears'
    rows.append((f + 1, GROUND - p['y'], p['sy'], p['sx'], dn, new, r, what))
    print('| %d | %d | %.2f x %.2f | %s | %s | %s |' % (f + 1, round(GROUND - p['y']), p['sy'], p['sx'], ('D%d' % dn) if new else ('D%d (held)' % dn), r if new else 'held', what))
    tiles.append(frame(st, f, BOX, 0.36))
print('frames: 29, different drawings: %d, held frames: %d' % (dn, 29 - dn))
tw, th = tiles[0].size
out = Image.new('RGB', (tw * 10 + 20, (th + 46) * 3 + 60), PAPER); d = ImageDraw.Draw(out)
d.text((14, 12), 'One small hop, every frame. Red = key, orange = breakdown, grey = held drawing.', font=FB, fill=INK)
for i, t in enumerate(tiles):
    x, y = 10 + (i % 10) * tw, 54 + (i // 10) * (th + 46)
    out.paste(t, (x, y))
    fr, h, sy, sx, dnum, new, r, what = rows[i]
    col = RED if r == 'KEY' else (200, 100, 20) if r == 'BREAKDOWN' else (120, 120, 130) if not new else INK
    d.rectangle((x, y, x + tw - 1, y + th - 1), outline=col, width=3 if r in ('KEY', 'BREAKDOWN') else 1)
    d.text((x + 4, y + th + 2), 'f%d  D%d%s' % (fr, dnum, '' if new else ' held'), font=F, fill=col)
    d.text((x + 4, y + th + 22), (r if new else ('KEY LOST' if r == 'KEY' else ''))[:10], font=F, fill=col)
out.save(os.path.join(HERE, 'FB_fig1_hop_every_frame.png'))

# the same hop with twos switched off (the existing Actor.twos setting), to show what the hold on twos did to the one-frame contact
g1 = Gaju(x=W / 2, y=GROUND, face=0.0); g1.twos = False
for fr, ln, ease, r, what, pose in KEYS:
    g1.move(fr - ln, fr, ease, **pose)
print('\nCONTACT, ON TWOS AGAINST ON ONES (frames 17 to 23)')
print('| Frame | On twos (default): height, tall | On ones: height, tall |')
print('|---|---|---|')
for f in range(16, 23):
    a_, b_ = g.frame_pose(f), g1.frame_pose(f)
    print('| %d | %d, %.2f | %d, %.2f |' % (f + 1, round(GROUND - a_['y']), a_['sy'], round(GROUND - b_['y']), b_['sy']))
print('lowest "tall" value reached: on twos %.2f, on ones %.2f (the key asked for 0.72)' % (min(g.frame_pose(f)['sy'] for f in range(16, 24)), min(g1.frame_pose(f)['sy'] for f in range(16, 24))))

# onion-skin view of the same hop: the drawings laid over each other
st2 = stage(30); g2 = Gaju(x=W / 2, y=GROUND, face=0.0); g2.shadow = 0; st2.add(g2)
for fr, ln, ease, r, what, pose in KEYS:
    g2.move(fr - ln, fr, ease, **pose)
acc = None
pick = [0, 6, 8, 10, 12, 14, 16, 18, 19, 22, 28]
for f in pick:
    a = np.asarray(frame(st2, f, BOX, 0.8)).astype(float)
    acc = a if acc is None else np.minimum(acc, a * 0.45 + 255 * 0.55 if f not in (0, 14, 19) else a)
on = Image.fromarray(acc.clip(0, 255).astype(np.uint8))

# ------------------------------------------------------------------ head turn on the approved Laddu head (yaw control), 9 drawings on twos
st3 = stage(20); c = Laddu(x=W / 2, y=GROUND, face=0.0); c.shadow = 0; st3.add(c)
c.set(0, yaw=-0.9, pupil=(-0.6, 0.0), lid=0.2)
c.move(0, 4, 'out', pupil=(0.8, 0.0))                       # eyes lead
c.move(2, 16, 'io', yaw=0.9)
c.move(2, 9, 'io', head_dy=14.0, head_rot=5.0); c.move(9, 16, 'io', head_dy=0.0, head_rot=0.0)   # the dip that makes the arc
c.move(5, 8, 'io', eye_open=0.0); c.move(9, 12, 'io', eye_open=1.0)                               # blink in the middle
HB = (-150, 60, 150, 300)
print('\nHEAD TURN X-SHEET (approved Laddu head, yaw control, on twos)')
print('| Drawing | Frames | Turn (yaw) | Dip (px) | Eyes |')
print('|---|---|---|---|---|')
ht = []
for i in range(9):
    f = i * 2
    p = c.pose(f)
    print('| %d | %d-%d | %+.2f | %d | %s |' % (i + 1, f + 1, f + 2, p['yaw'], round(p['head_dy']), 'shut' if p['eye_open'] < 0.3 else ('half' if p['eye_open'] < 0.8 else 'open, pupils %+.1f' % p['pupil'][0])))
    ht.append(frame(st3, f, HB, 0.6))
w2, h2 = ht[0].size
fig = Image.new('RGB', (max(on.size[0] + 40 + 0, w2 * 9 + 20), on.size[1] + h2 + 150), PAPER); d = ImageDraw.Draw(fig)
d.text((14, 12), 'Top: the hop drawings laid over each other (what onion skin shows). Bottom: a head turn in nine drawings.', font=FB, fill=INK)
fig.paste(on, (10, 54))
d.multiline_text((on.size[0] + 30, 80), 'Drawings bunch at the top of the hop\nand spread out on the way down.\nSolid: rest, top and contact.\nFaded: the drawings between.', font=F, fill=INK, spacing=6)
for i, t in enumerate(ht):
    fig.paste(t, (10 + i * w2, on.size[1] + 70)); d.text((14 + i * w2, on.size[1] + 74 + h2), 'drawing %d, f%d-%d' % (i + 1, i * 2 + 1, i * 2 + 2), font=F, fill=INK)
fig.save(os.path.join(HERE, 'FB_fig2_onion_and_head_turn.png'))
if os.path.exists(TMP):
    os.remove(TMP)
print('\nfigures written')
