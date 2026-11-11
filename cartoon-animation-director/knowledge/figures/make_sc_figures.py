"""Builds the figures and prints the tables used in Slapstick_Comedy.md.
Run: python3 make_sc_figures.py
Uses only the approved production models, the existing presets in show.py and existing engine controls.
Nothing from the review branch. Nothing here is a tested animation: the output is frames and tables."""
import os, sys
import numpy as np
import skia
from PIL import Image, ImageDraw, ImageFont
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', '..', '..', 'toon-slapstick', 'engine'))
from toon import Stage, W, GROUND
from chars import Bheemu, Gaju
from cast import Ammamma, Chintu, Laddu, Bujji
from scene import Prop
from show import ball, CALM, HAPPY, LAUGH, ANGRY, SHOCK, SORRY, SLY, SLEEP
BEIGE = (240, 232, 214); PAPER = (252, 250, 244); INK = (58, 42, 40); RED = (150, 30, 40); ORANGE = (200, 100, 20); GREY = (120, 120, 130)
FB = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf', 24); F = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf', 17)
FS = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf', 15)
TMP = os.path.join(HERE, '_t.png')
BX, GX = W / 2 - 200, W / 2 + 230        # where Bheemu and Gaju stand
HEAD_B, HEAD_G = 588, 262                # ball-centre height above the floor when it rests on each head at rest (set by eye from stills)
HIT_B, HIT_G = 588 * 0.88 - 16, 262 * 0.84   # the same on the contact drawing, where the body is squashed


def stage(n):
    st = Stage(n, bg=lambda c, cam, f: c.clear(skia.Color(*BEIGE))); st.grain = 0
    return st


def frame(st, f, box, sc=0.5):
    st.still(f, TMP, sc)
    im = Image.open(TMP).convert('RGB')
    return im.crop((int((W / 2 + box[0]) * sc), int((GROUND - box[3]) * sc), int((W / 2 + box[2]) * sc), int((GROUND - box[1]) * sc)))


# ------------------------------------------------------------------ worked example 1: "The ball that went up" (original), 240 frames
BEATS = [  # (first frame, last frame, beat, what the audience should read)
    (0, 35, 'Setup', 'Bheemu dozes on his feet. Gaju has a ball. All calm'),
    (36, 47, 'Intention', 'Gaju looks at the ball, then at Bheemu. Sly'),
    (48, 59, 'Bounce 1', 'Small bounce. Pattern starts'),
    (60, 75, 'Bounce 2', 'Bigger bounce. Pattern confirmed'),
    (76, 87, 'Bounce 3', 'Far too hard. The ball leaves the top of the picture'),
    (88, 133, 'The wait', 'Gaju looks up. Nothing. He relaxes. Silence'),
    (134, 139, 'The fall', 'The ball comes back, over the wrong head. Fully in the picture for the last four frames'),
    (140, 141, 'Impact', 'Bonk on Bheemu. One clear drawing'),
    (142, 151, 'Hold', 'Nobody moves. Bheemu has not understood yet'),
    (152, 175, 'Slow burn', 'Eyes open, slide to Gaju, then the head follows'),
    (164, 183, 'Guilt', 'Gaju: sorry face, ears down'),
    (184, 199, 'Topper', 'The ball comes down once more, on Gaju'),
    (200, 239, 'Ending', 'Bheemu laughs. Gaju joins in. Friends'),
]


def build(contact=140, bheemu_twos=True):
    st = stage(242)
    b = Bheemu(x=BX, y=GROUND, face=0.0); g = Gaju(x=GX, y=GROUND, face=0.0); b.twos = bheemu_twos
    bl = Prop(ball, shadow=0, x=GX - 175, y=GROUND - 24)
    st.add(b, g, bl)
    b.set(0, **SLEEP); g.set(0, **CALM); g.set(0, yaw=-0.5)
    # intention
    g.move(36, 40, 'out', pupil=(-0.7, 0.6)); g.move(42, 46, 'over', **SLY); g.move(42, 46, 'out', pupil=(-0.9, -0.1))
    # three bounces: the trunk taps, the ball goes up and comes back; heights 110, 250, out of frame
    for f0, n, h in ((48, 12, 110), (60, 16, 250)):
        bl.move(f0, f0 + n // 2, 'out', y=GROUND - 24 - h); bl.move(f0 + n // 2, f0 + n, 'in', y=GROUND - 24)
        bl.set(f0 + n, sy=0.75, sx=1.25); bl.move(f0 + n, f0 + n + 2, 'out', sy=1.0, sx=1.0)
        g.move(f0, f0 + n // 2, 'out', pupil=(-0.7, -0.6), head_dy=-6); g.move(f0 + n // 2, f0 + n, 'in', pupil=(-0.7, 0.6), head_dy=0)
    g.move(72, 76, 'out', sy=0.86, sx=1.12)                                    # wind-up for the big one
    g.move(76, 79, 'snap', sy=1.1, sx=0.93); g.move(79, 86, 'io', sy=1.0, sx=1.0)
    bl.move(76, 86, 'out', y=-400, x=BX + 40)                                  # gone, and drifting over Bheemu
    g.move(76, 84, 'out', pupil=(-0.3, -1.0), head_dy=-14, **dict(SHOCK, mouth_open=0.4))
    # the wait
    g.move(108, 116, 'io', pupil=(0.0, 0.0), head_dy=0, **CALM); g.move(120, 126, 'io', smile=0.8)
    # the fall and the impact
    bl.set(contact - 6, y=GROUND - 1500, x=BX); bl.move(contact - 6, contact, 'in', y=GROUND - HIT_B, sy=1.25, sx=0.85)
    bl.set(contact, sy=0.7, sx=1.3)
    b.set(contact, sy=0.88, sx=1.09, head_dy=16)
    b.move(contact + 2, contact + 10, 'elastic', sy=1.0, sx=1.0, head_dy=0)
    bl.move(contact + 1, contact + 10, 'out', y=GROUND - HIT_B - 420, x=BX + 240, sy=1.0, sx=1.0)
    bl.move(contact + 10, contact + 20, 'in', y=-500, x=GX + 60)            # up and away again, towards Gaju
    g.move(contact, contact + 3, 'snap', pupil=(-0.9, -0.3), **SHOCK)
    # slow burn
    b.move(152, 155, 'out', eye_open=1.0, happy=0.0, lid=0.35, smile=-0.5, brow_ang=10)
    b.move(158, 166, 'io', pupil=(0.9, 0.0)); b.move(166, 176, 'io', yaw=0.7, brow_ang=20)
    g.move(164, 170, 'io', pupil=(-0.8, 0.2), ear=-0.8, **SORRY)
    # topper
    bl.set(186, y=GROUND - 1500, x=GX); bl.move(186, 192, 'in', y=GROUND - HIT_G, sy=1.2, sx=0.88); bl.set(192, sy=0.75, sx=1.25)
    g.set(192, sy=0.84, sx=1.14, **SHOCK); g.move(194, 202, 'elastic', sy=1.0, sx=1.0)
    bl.move(193, 200, 'out', y=GROUND - HIT_G - 190, x=GX + 150, sy=1.0, sx=1.0); bl.move(200, 208, 'in', y=GROUND - 24, x=GX + 250)
    # ending
    b.move(202, 206, 'over', **LAUGH); b.move(202, 206, 'io', brow_ang=0, lid=0.0, pupil=(0.0, 0.0))
    for f in range(206, 236, 6):
        b.move(f, f + 3, 'out', head_dy=-8, sy=1.03); b.move(f + 3, f + 6, 'in', head_dy=0, sy=0.98)
    g.move(212, 218, 'io', ear=0.3, pupil=(-0.6, 0.0), **HAPPY)
    return st, b, g, bl


st, b, g, bl = build()
print('BEAT SHEET, worked example 1 (24 fps; engine frame 0 = film frame 1)')
print('| Beat | Frames | Length (frames) | Seconds | What must read |')
print('|---|---|---|---|---|')
for f0, f1, name, what in BEATS:
    print('| %s | %d-%d | %d | %.2f | %s |' % (name, f0 + 1, f1 + 1, f1 - f0 + 1, (f1 - f0 + 1) / 24, what))
setup = 134; payoff = 8
print('before the hit (setup to end of the wait): %d frames = %.1f s; the fall and impact: %d frames = %.2f s; after the hit: %d frames = %.1f s' % (setup, setup / 24, payoff, payoff / 24, 240 - 142, (240 - 142) / 24))
print('longest single move-free stretch planned: the wait, 46 frames; fastest move: the fall, 6 frames')

PANELS = [(20, 'Setup'), (46, 'Intention'), (54, 'Bounce 1'), (68, 'Bounce 2'), (80, 'Bounce 3'), (124, 'The wait'), (139, 'The fall'), (140, 'IMPACT'), (148, 'Hold'), (172, 'Slow burn'), (192, 'Topper'), (224, 'Ending')]
BOX = (-470, -20, 470, 1000)
tiles = [frame(st, f, BOX, 0.33) for f, _ in PANELS]
tw, th = tiles[0].size
fig = Image.new('RGB', (tw * 6 + 20, (th + 50) * 2 + 60), PAPER); d = ImageDraw.Draw(fig)
d.text((14, 12), 'Worked example 1, "The ball that went up": twelve key frames. Poses only; not judged in motion.', font=FB, fill=INK)
for i, t in enumerate(tiles):
    x, y = 10 + (i % 6) * tw, 54 + (i // 6) * (th + 50)
    fig.paste(t, (x, y)); f, name = PANELS[i]
    col = RED if name == 'IMPACT' else INK
    d.rectangle((x, y, x + tw - 1, y + th - 1), outline=col, width=4 if name == 'IMPACT' else 1)
    d.text((x + 6, y + th + 4), '%d. %s  (frame %d)' % (i + 1, name, f + 1), font=F, fill=col)
fig.save(os.path.join(HERE, 'SC_fig1_ball_gag_key_frames.png'))

# ------------------------------------------------------------------ the impact, every frame, and what twos does to it
print('\nIMPACT, EVERY FRAME (contact keyed on engine frame 140, film frame 141; Bheemu on twos, ball on ones)')
print('| Frame | Ball height (px) | Ball tall | Bheemu tall | Bheemu drawing | Note |')
print('|---|---|---|---|---|---|')
IB = (-470, 250, 60, 1500); tiles = []; rows = []; prev = None
for f in range(132, 148):
    pb, pl = b.frame_pose(f), bl.frame_pose(f)
    key = (round(pb['sy'], 3), round(pb['head_dy'], 1), round(pb['eye_open'], 2))
    new = key != prev; prev = key
    note = {134: 'ball enters', 140: 'CONTACT', 142: 'ball leaves'}.get(f, '')
    rows.append((f, new, note))
    print('| %d | %d | %.2f | %.2f | %s | %s |' % (f + 1, round(GROUND - pl['y']), pl['sy'], pb['sy'], 'new' if new else 'held', note))
    tiles.append(frame(st, f, IB, 0.21))


def lowest(contact, twos):
    st_, b_, g_, bl_ = build(contact, twos)
    return min(b_.frame_pose(f)['sy'] for f in range(contact - 2, contact + 6)), [round(b_.frame_pose(f)['sy'], 2) for f in range(contact - 1, contact + 3)], [round(GROUND - bl_.frame_pose(f)['y']) for f in range(contact - 1, contact + 3)]


print('\nCONTACT PLACEMENT TEST (the squash keyed is 0.88 tall)')
print('| Contact keyed on engine frame | Bheemu on | Flattest drawing shown | Bheemu tall, frames c-1..c+2 | Ball height, frames c-1..c+2 | Result |')
print('|---|---|---|---|---|---|')
for c, tw_ in ((140, True), (141, True), (141, False)):
    lo, seq, bseq = lowest(c, tw_)
    res = 'squash shown on the contact frame' if seq[1] <= 0.885 else 'ball lands on a HELD drawing: head not squashed on the contact frame'
    print('| %d (%s) | %s | %.2f | %s | %s | %s |' % (c, 'even' if c % 2 == 0 else 'odd', 'twos' if tw_ else 'ones', lo, seq, bseq, res))

tw, th = tiles[0].size
fig = Image.new('RGB', (tw * 16 + 20, (th + 46) + 60), PAPER); d = ImageDraw.Draw(fig)
d.text((14, 12), 'The fall and the impact on every frame, film frames 133 to 148. Red = contact. Grey = Bheemu drawing held.', font=FB, fill=INK)
for i, t in enumerate(tiles):
    x, y = 10 + i * tw, 54
    fig.paste(t, (x, y)); f, new, note = rows[i]
    col = RED if note == 'CONTACT' else (INK if new else GREY)
    d.rectangle((x, y, x + tw - 1, y + th - 1), outline=col, width=4 if note == 'CONTACT' else 1)
    d.text((x + 4, y + th + 2), 'f%d' % (f + 1), font=F, fill=col)
    d.text((x + 4, y + th + 22), note or ('' if new else 'held'), font=FS, fill=col)
fig.save(os.path.join(HERE, 'SC_fig2_impact_every_frame.png'))

# ------------------------------------------------------------------ three timings of the same gag, and the escalation
VERSIONS = [
    ('A. Planned (worked example 1)', [('setup', 48), ('three bounces', 40), ('wait', 46), ('fall+hit', 8), ('hold', 10), ('slow burn', 32), ('topper', 16), ('ending', 40)]),
    ('B. Rushed: no wait, no hold', [('setup', 12), ('three bounces', 40), ('wait', 4), ('fall+hit', 8), ('hold', 0), ('slow burn', 8), ('topper', 16), ('ending', 12)]),
    ('C. Even: every beat one second', [('setup', 24), ('three bounces', 24), ('wait', 24), ('fall+hit', 24), ('hold', 24), ('slow burn', 24), ('topper', 24), ('ending', 24)]),
]
COL = {'setup': (150, 190, 210), 'three bounces': (240, 200, 110), 'wait': (225, 225, 225), 'fall+hit': (200, 50, 50), 'hold': (190, 190, 200), 'slow burn': (150, 200, 150), 'topper': (230, 150, 90), 'ending': (240, 180, 200)}
print('\nTHREE TIMINGS OF THE SAME GAG (frames)')
print('| Version | Total | Before the fall | Fall and hit | Stillness around the hit (wait + hold) | Reaction (slow burn) | Shortest and longest beat |')
print('|---|---|---|---|---|---|---|')
fig = Image.new('RGB', (1500, 640), PAPER); d = ImageDraw.Draw(fig)
d.text((14, 12), 'Top: one gag timed three ways (5.6 px per frame). Bottom: the escalation, measured.', font=FB, fill=INK)
for i, (name, beats) in enumerate(VERSIONS):
    tot = sum(n for _, n in beats); dct = dict(beats); x = 20; y = 70 + i * 86
    d.text((20, y - 22), '%s: %d frames, %.1f s' % (name, tot, tot / 24), font=F, fill=INK)
    for nm, n in beats:
        w = n * 5.6
        if n:
            d.rectangle((x, y, x + w, y + 40), fill=COL[nm], outline=INK)
            if w > 60:
                d.text((x + 4, y + 11), '%s %d' % (nm, n), font=FS, fill=INK)
        x += w
    nz = [n for _, n in beats if n]
    print('| %s | %d | %d | %d | %d | %d | %d and %d |' % (name, tot, dct['setup'] + dct['three bounces'] + dct['wait'], dct['fall+hit'], dct['wait'] + dct['hold'], dct['slow burn'], min(nz), max(nz)))
# escalation measured from the ball track
print('\nESCALATION (ball height above the floor at the top of each bounce, read from the timeline)')
print('| Bounce | Frames | Peak height (px) | Compared with the one before |')
print('|---|---|---|---|')
peaks = []
for name, f0, f1 in (('1', 48, 60), ('2', 60, 76), ('3', 76, 88)):
    pk = max(GROUND - bl.frame_pose(f)['y'] for f in range(f0, f1))
    peaks.append(pk)
    print('| %s | %d-%d | %d%s | %s |' % (name, f0 + 1, f1, round(pk), ' (leaves the picture at 1480)' if pk > GROUND else '', '' if len(peaks) == 1 else 'x %.1f' % (pk / peaks[-2])))
x0, y0 = 60, 600
d.line((x0, y0, 1440, y0), fill=INK, width=2)
pts = [(x0 + (f - 44) * 12.5, y0 - min(GROUND - bl.frame_pose(f)['y'], 1700) * 0.15) for f in range(44, 152)]  # 108 frames
d.line(pts, fill=RED, width=4)
d.line((x0, y0 - HEAD_B * 0.15, 1440, y0 - HEAD_B * 0.15), fill=GREY, width=1); d.text((700, y0 - HEAD_B * 0.15 - 20), "height of Bheemu's head", font=FS, fill=GREY)
for lab, f in (('bounce 1', 54), ('bounce 2', 68), ('bounce 3: gone', 80), ('the wait: empty air', 108), ('hit', 140)):
    d.text((x0 + (f - 44) * 12.5 - 30, y0 + 6), lab, font=FS, fill=INK)
d.text((x0, 345), 'Ball height against time, film frames 45 to 152 (clipped at the top of the picture)', font=F, fill=INK)
fig.save(os.path.join(HERE, 'SC_fig3_timing_and_escalation.png'))

# ------------------------------------------------------------------ same event, six characters: approved presets only
CAST = [(Bheemu, 'Bheemu', 0.42, (-330, -20, 330, 700)), (Gaju, 'Gaju', 0.6, (-230, -20, 230, 440)), (Ammamma, 'Ammamma', 0.42, (-300, -20, 300, 660)),
        (Chintu, 'Chintu', 0.55, (-240, -20, 240, 480)), (Laddu, 'Laddu', 0.75, (-180, -20, 180, 340)), (Bujji, 'Bujji', 0.7, (-170, -20, 170, 400))]
REACT = {  # which approved preset each character goes to first and second after a surprise; a choice, not a test result
    'Bheemu': ('CALM', 'ANGRY'), 'Gaju': ('SHOCK', 'SORRY'), 'Ammamma': ('CALM', 'SLY'), 'Chintu': ('SHOCK', 'LAUGH'), 'Laddu': ('ANGRY', 'SLEEP'), 'Bujji': ('SHOCK', 'SORRY')}
PRE = dict(CALM=CALM, HAPPY=HAPPY, LAUGH=LAUGH, ANGRY=ANGRY, SHOCK=SHOCK, SORRY=SORRY, SLY=SLY, SLEEP=SLEEP)
cells = []
for cls, name, sc, box in CAST:
    row = []
    for pre in REACT[name]:
        s = stage(2); a = cls(x=W / 2, y=GROUND, face=0.0); a.shadow = 0; s.add(a); a.set(0, **PRE[pre])
        row.append(frame(s, 0, box, sc))
    cells.append(row)
cw = max(c.size[0] for r in cells for c in r); ch = max(c.size[1] for r in cells for c in r)
fig = Image.new('RGB', (cw * 6 + 20, (ch + 34) * 2 + 60), PAPER); d = ImageDraw.Draw(fig)
d.text((14, 12), 'One surprise, six characters: first reaction (top) and second (bottom). Existing approved presets only.', font=FB, fill=INK)
for i, (cls, name, sc, box) in enumerate(CAST):
    for j in range(2):
        t = cells[i][j]; x = 10 + i * cw + (cw - t.size[0]) // 2; y = 54 + j * (ch + 34) + (ch - t.size[1])
        fig.paste(t, (x, y)); d.text((14 + i * cw, 54 + j * (ch + 34) + ch + 4), '%s: %s' % (name, REACT[name][j]), font=F, fill=INK)
fig.save(os.path.join(HERE, 'SC_fig4_character_reactions.png'))

# ------------------------------------------------------------------ staging: the same moment, clear and unclear
def moment(bx, gx, ballx, bally):
    s = stage(2); bb = Bheemu(x=bx, y=GROUND, face=0.0); gg = Gaju(x=gx, y=GROUND, face=0.0); pp = Prop(ball, x=ballx, y=bally)
    bb.shadow = gg.shadow = 0
    s.add(bb, gg, pp); bb.set(0, **SLEEP); gg.set(0, pupil=(-0.3, -1.0), **dict(SHOCK, mouth_open=0.4))
    return s


def sil(im):
    a = np.asarray(im).astype(int)
    m = (np.abs(a - np.array(BEIGE)).sum(axis=2) > 40)
    out = np.full(a.shape, 255, np.uint8); out[m] = (40, 40, 48)
    return Image.fromarray(out), m


SB = (-470, -20, 470, 900)
good = frame(moment(BX, GX, BX, GROUND - HEAD_B - 150), 0, SB, 0.4)
bad = frame(moment(W / 2 - 40, W / 2 + 70, W / 2 + 30, GROUND - 330), 0, SB, 0.4)
gs, gm = sil(good); bs, bm = sil(bad)


def gap(m):  # widest run of empty columns between the outermost ink columns: a simple measure of separation
    cols = m.any(axis=0); xs = np.where(cols)[0]; best = run = 0
    for x in range(xs[0], xs[-1] + 1):
        run = 0 if cols[x] else run + 1; best = max(best, run)
    return best / 0.4


print('\nSTAGING (same poses, two layouts; widest empty gap between the figures, in stage px)')
print('| Layout | Gap between figures (px) | Ball against | Reads in silhouette? |')
print('|---|---|---|---|')
print('| Clear | %d | empty background above Bheemu | my judgement: yes |' % gap(gm))
print('| Unclear | %d | Gaju and Bheemu overlapping | my judgement: no |' % gap(bm))
w, h = good.size
fig = Image.new('RGB', (w * 4 + 50, h + 110), PAPER); d = ImageDraw.Draw(fig)
d.text((14, 12), 'Staging the moment before the hit. Left pair: clear. Right pair: the same poses, crowded.', font=FB, fill=INK)
for i, (im, lab) in enumerate(((good, 'Clear: ball over empty space'), (gs, 'Clear, as a silhouette'), (bad, 'Unclear: everything overlaps'), (bs, 'Unclear, as a silhouette'))):
    fig.paste(im, (10 + i * (w + 10), 54)); d.text((14 + i * (w + 10), 58 + h), lab, font=F, fill=INK)
fig.save(os.path.join(HERE, 'SC_fig5_staging.png'))
if os.path.exists(TMP):
    os.remove(TMP)
print('\nfigures written')
