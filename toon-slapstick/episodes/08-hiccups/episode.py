"""Bheemu & Gaju, episode 8: "Hiccups"  (about 25 s, vertical, silent; only Ammamma speaks)

Gaju has hiccups: each one honks his trunk and throws him in the air. Bheemu tries to scare them away with
a demon mask, then a paper bag, then a bucket of water that finds Ammamma instead. That cures Gaju.
Then Bheemu hiccups, and Ammamma is holding the bucket.
"""
import os, sys, math
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', 'engine'))
from toon import GROUND, poly, oval, smooth
from chars import Bheemu, Gaju
from cast import Ammamma
from scene import Painted, Prop, rect, puffs, stars, marks
from sets import courtyard, SKY
from acting import blink, look, bob, walk, squash, take, shake, zip_off, arc
from sound import veena, bansuri, xylo
from voice import speak
from show import Show, face, hop, enter, splash, CALM, HAPPY, LAUGH, ANGRY, SHOCK, SORRY, SLY

G0 = GROUND
ep = Show(8, 'Hiccups', 'hiccups', 600, Painted(2800, courtyard, top=SKY, bottom=(170, 146, 122)))
st, sc, cam = ep.st, ep.sc, ep.cam
INK = (58, 42, 40)


def mask(g, p, f):                                      # the demon face people hang on new houses
    g.shape(smooth([(0, -120), (96, -96), (120, 0), (84, 96), (0, 124), (-84, 96), (-120, 0), (-96, -96)], True, 0.5), (214, 50, 50), True, 5, INK)
    for s in (-1, 1):
        g.shape(poly([(s * 60, -110), (s * 110, -190), (s * 96, -90)]), (250, 208, 80), True, 4, INK)
        g.shape(oval(s * 44, -24, 32, 36), (255, 250, 230), True, 4, INK); g.shape(oval(s * 44, -20, 13, 13), (30, 30, 30), False)
        g.shape(poly([(s * 16, -74), (s * 84, -52)], False), None, True, 9, INK)
        g.shape(poly([(s * 30, 56), (s * 22, 100), (s * 46, 60)]), (255, 255, 255), True, 3, INK)
    g.shape(smooth([(-64, 52), (0, 74), (64, 52), (0, 64)], True, 0.6), (60, 20, 30), True, 4, INK)
    g.shape(smooth([(-70, 96), (0, 150), (70, 96), (0, 120)], True, 0.5), (40, 30, 40), True, 4, INK)


def bag(g, p, f):
    g.shape(smooth([(-14, 0), (-60, -40), (-54, -110), (0, -130), (54, -110), (60, -40), (14, 0)], True, 0.5), (200, 160, 110), True, 5, INK)
    g.shape(poly([(-20, -40), (10, -100)], False), None, True, 3, (150, 110, 70))


def bucket(g, p, f):
    g.shape(smooth([(-70, -150), (0, -210), (70, -150)], False), None, True, 6, (120, 120, 130))
    g.shape(poly([(-72, -150), (72, -150), (54, 0), (-54, 0)]), (80, 140, 200), True, 5, INK)
    if p.get('full', 1.0) > 0.5:
        g.shape(oval(0, -150, 70, 16), (190, 220, 250), True, 4, INK)
    else:
        g.shape(oval(0, -150, 70, 16), (50, 90, 140), True, 4, INK)


def wave(g, p, f):
    g.shape(smooth([(-150, 0), (-60, -70), (40, -90), (150, -40), (170, 20), (60, 60), (-80, 50)], True, 0.6), (150, 200, 245), True, 5, (70, 110, 170))
    for x, y in ((-170, -40), (-120, 70), (190, -70)):
        g.shape(oval(x, y, 16, 20), (150, 200, 245), True, 4, (70, 110, 170))


gaju = Gaju(x=1630, z=3)
bheemu = Bheemu(x=1980, z=3.2, sit=1.0, smile=0.8, eye_open=0.0, happy=1.0)
amma = Ammamma(x=1100, z=2, show=0.0)
mk = Prop(mask, x=0, y=0, z=3.6, show=0.0, sx=1.25, sy=1.25)
bg_ = Prop(bag, x=0, y=0, z=3.6, show=0.0)
bk = Prop(bucket, x=0, y=0, z=3.8, show=0.0, full=1.0)
wv = Prop(wave, x=0, y=0, z=5, show=0.0)
st.add(amma, gaju, bheemu, mk, bg_, bk, wv)
ep.shot(0, 1740, 0.95, cut=False)


def hic(a, f, h=80):
    """One hiccup: a honk, a jump, a wobble."""
    y = a.value('y', f)
    a.set(f, sy=0.9, sx=1.08)
    a.move(f, f + 3, 'out', y=y - h, sy=1.12, sx=0.92); a.move(f + 3, f + 8, 'in', y=y)
    a.set(f + 8, sy=0.88, sx=1.1); a.move(f + 9, f + 15, 'elastic', sy=1.0, sx=1.0)
    a.move(f, f + 2, 'snap', eye_pop=1.3, mouth_open=0.4, mouth_w=0.6); a.move(f + 8, f + 12, 'out', eye_pop=1.0, mouth_open=0.0, mouth_w=1.0)
    if 'ear' in a.defaults:
        a.move(f, f + 2, 'snap', ear=1.0, trunk=(40, -50), trunk_curl=-0.8); a.move(f + 5, f + 12, 'elastic', ear=0.0, trunk=(30, 60), trunk_curl=0.7)
    if 'glasses_dy' in a.defaults:
        a.move(f, f + 3, 'snap', glasses_dy=-40, glasses_rot=-12); a.move(f + 6, f + 14, 'bounce', glasses_dy=0, glasses_rot=0)
    sc.hit(f, 'pop', 0.9, note=90); sc.slide(f, 76, 88, 3, 0.6); sc.hit(f + 8, 'pop', 0.4, note=55)
    marks(st, f + 1, a.value('x', f), y - a.HEIGHT * 1.5, life=7)
    return f + 15


# ------------------------------------------------------------------ 1. hic!  (36-120)
sc.raga(36, 120, 'calm')
bob(gaju, 36, 58, 12, 0.03)
hic(gaju, 60, 50); hic(gaju, 84, 90); hic(gaju, 104, 150)
bheemu.move(86, 88, 'snap', eye_open=1.0, happy=0.0, yaw=-0.6, pupil=(-0.9, 0)); bheemu.move(106, 108, 'snap', **SHOCK)
face(gaju, 120, 4, yaw=0.4, pupil=(0.7, 0), **SORRY)

# ------------------------------------------------------------------ 2. cure one: the demon mask  (120-212)
sc.raga(120, 330, 'sneak')
bheemu.set(122, sit=0.0); bheemu.move(122, 128, 'over', armR=(-30, -250), handR='fist', pupil=(0.3, -0.8), yaw=0.0, **CALM)    # thinks
bheemu.move(138, 141, 'snap', armR=(60, -330), handR='point', brow=10, smile=0.9); sc.hit(138, 'ghatam', 0.9, note=74)
face(gaju, 130, 4, yaw=0.0, pupil=(0, 0), **CALM)
mk.set(146, show=1.0); mk.attach(146, 190, bheemu, 'head', 0, 0); sc.hit(146, 'pop', 0.8, note=60)
bheemu.move(146, 150, 'over', armL=(-70, -280), armR=(70, -280), handL='open', handR='open', brow=0)
for f in walk(bheemu, 152, 170, 1830, 9, 28):
    sc.note(f, xylo, 72, 0.12, 0.5)
bheemu.move(172, 175, 'snap', sx=1.12, sy=1.08, rot=-8); sc.hit(172, 'timp', 0.9, note=38); sc.hit(172, 'boing', 0.6, note=40)          # BOO
look(gaju, 174, yaw=0.7, pupil=(0.8, -0.2)); blink(gaju, 180)
hic(gaju, 188, 110)
mx, my = st.probe(188, bheemu, 'head')
mk.set(190, x=mx, y=my); arc(mk, 190, 208, 2600, G0 - 1000, 200, spin=800); sc.hit(189, 'whoosh', 0.8, d=0.4)
bheemu.move(190, 192, 'snap', scarf_fly=1.0, sx=1.0, sy=1.0, rot=6, armL=(0, 0), armR=(0, 0), handL='mitt', handR='mitt', **SHOCK)
bheemu.move(198, 206, 'io', scarf_fly=0.0, rot=0); face(bheemu, 206, 4, **ANGRY)

# ------------------------------------------------------------------ 3. cure two: the paper bag  (212-290)
P = 214
face(bheemu, P, 3, **SLY)
hx, hy = st.probe(P + 6, bheemu, 'mouth')
bg_.set(P + 6, show=1.0, x=hx - 50, y=hy + 60, sx=0.3, sy=0.3, rot=20)
bheemu.move(P + 4, P + 8, 'over', armR=(-70, -230), handR='grip', yaw=-0.6)
for i in range(3):                                                                              # puff, puff, puff
    f = P + 10 + i * 10
    bheemu.move(f, f + 4, 'out', cheeks=1.0, sx=1.05); bheemu.move(f + 4, f + 9, 'in', cheeks=0.0, sx=1.0)
    bg_.move(f, f + 5, 'over', sx=0.6 + i * 0.45, sy=0.6 + i * 0.45); sc.slide(f, 60 + i * 4, 66 + i * 4, 5, 0.35)
B = P + 46
sc.duck(B - 6, B + 20, 0.3)
bheemu.move(B - 6, B, 'out', armL=(-150, -200), handL='open'); bheemu.move(B, B + 2, 'snap', armL=(-60, -230))
bg_.set(B + 1, show=0.0); stars(st, B + 1, hx - 60, hy - 20, n=9, r=240, life=12)
sc.hit(B + 1, 'crash', 1.0); ep.tap(B + 1, 'dha', 1.3); st.shake(B + 1, 26, 10)
f = take(st, bheemu, B + 1, 1.0, hold=5); hop(bheemu, B + 3, 90)                                 # he scares himself
bheemu.move(B + 4, B + 8, 'over', armL=(0, 0), armR=(0, 0), handL='mitt', handR='mitt')
blink(gaju, B + 8); look(gaju, B + 14, yaw=0.5, pupil=(0.6, 0))
hic(gaju, B + 24, 90)

# ------------------------------------------------------------------ 4. cure three: the bucket  (290-400)
K = B + 44
face(bheemu, K, 3, yaw=0.0, **ANGRY)
g1 = zip_off(st, bheemu, K + 2, 2800, wind=7); sc.hit(g1, 'zip', 0.9)
R = g1 + 8
bheemu.set(R, show=1.0, x=2600, wheel=0.0, stride=0.0, rot=0, sx=1, sy=1, face=-1, yaw=-0.8, armR=(-50, -60), handR='grip', bendR=0.3)
bk.set(R, show=1.0); bk.attach(R, R + 40, bheemu, 'handR', 0, 150)
for f in walk(bheemu, R, R + 18, 2010, 6, 34):
    ep.tap(f, 'ge', 0.8)
amma.set(R + 6, show=1.0, x=1120, face=1, yaw=0.6, **CALM)                                        # Ammamma picks this moment to come out
for f in walk(amma, R + 6, R + 28, 1400, 7, 28):
    ep.tap(f, 'na', 0.4)
sc.duck(R + 18, R + 76, 0.25)
bheemu.move(R + 20, R + 30, 'out', rot=12, armR=(90, -150), sx=1.04)                              # the wind-up
T = R + 32
hic(gaju, T - 1, 240)                                                                             # ...hic
bheemu.move(T, T + 3, 'snap', rot=-14, armR=(-150, -210)); sc.hit(T, 'whoosh', 0.9, d=0.3)
bk.attach(R, 900, bheemu, 'handR', 0, 150); bk.set(T + 1, full=0.0, rot=-80)
wv.set(T + 1, show=1.0, x=1860, y=G0 - 330); wv.move(T + 1, T + 6, 'lin', x=1440, y=G0 - 380); wv.set(T + 7, show=0.0)
for k in range(3):
    splash(st, T + 6 + k, 1400, G0 - 420 + k * 120, n=12, life=16)
amma.set(T + 6, sx=1.12, sy=0.9, sweat=1.0, eye_open=0.0, smile=-0.4, brow_ang=0, face=0.0, yaw=0.0); amma.move(T + 8, T + 18, 'elastic', sx=1.0, sy=1.0)
sc.hit(T + 6, 'crash', 1.0); sc.hit(T + 6, 'timp', 1.0, note=36); ep.tap(T + 6, 'dha', 1.4); st.shake(T + 6, 30, 12)
bheemu.move(T + 8, T + 12, 'over', rot=0, armR=(-40, -60), sweat=1.0, yaw=-0.8, pupil=(-0.9, 0), **{k: v for k, v in SHOCK.items()})
bk.move(T + 8, T + 12, 'over', rot=0)
look(gaju, T + 16, yaw=-0.7, pupil=(-0.9, 0)); gaju.move(T + 18, T + 20, 'snap', **SHOCK)
W0 = T + 34                                                                                       # ...is it gone?
face(gaju, W0, 3, yaw=0.0, pupil=(0, 0.6), eye_pop=1.0, mouth_open=0.0, brow=6, smile=0.0, pupil_s=1.0)
for i, f in enumerate((W0 + 6, W0 + 16, W0 + 26)):
    gaju.move(f, f + 2, 'snap', sy=1 - 0.06 / (i + 1)); gaju.move(f + 2, f + 6, 'out', sy=1.0); sc.hit(f, 'ghatam', 0.6, note=64 + i * 3)
face(gaju, W0 + 34, 3, **HAPPY); sc.hit(W0 + 34, 'tada', 0.6)
hop(gaju, W0 + 36, 90); hop(gaju, W0 + 52, 90)

# ------------------------------------------------------------------ 5. then Bheemu hiccups
H = W0 + 50
amma.move(H - 10, H - 6, 'over', eye_open=1.0, yaw=0.7, pupil=(0.9, 0), brow_ang=24, lid=0.25, smile=-0.8)
hic(bheemu, H + 4, 90)
bheemu.move(H + 20, H + 23, 'snap', armL=(40, -310), handL='open', pupil=(-0.9, 0))               # claps a paw over his mouth
hic(bheemu, H + 32, 130)
look(gaju, H + 6, yaw=0.7, pupil=(0.9, 0)); face(gaju, H + 8, 3, happy=0.0, eye_open=1.0, smile=0.3)
face(amma, H + 46, 5, brow_ang=0, lid=0.3, brow_asym=1.0, smile=0.9)                              # Ammamma has an idea
amma.set(H + 52, z=4); gaju.move(H + 48, H + 56, 'io', x=1470)
for f in walk(amma, H + 52, H + 68, 1720, 8, 30):
    ep.tap(f, 'dha', 0.8)
bk.attach(H + 68, 900, amma, 'handR', 0, 150); bk.set(H + 68, full=1.0, z=4.5)
amma.set(H + 68, armR=(40, -60), handR='grip'); bheemu.move(H + 68, H + 72, 'over', armR=(0, 0), handR='mitt', armL=(0, 0), handL='mitt')
e = speak(ep, amma, H + 70, 'a_water')                                                            # "Drink some water, dear."
amma.move(e - 16, e - 6, 'out', armR=(60, -330)); sc.slide(e - 16, 58, 76, 10, 0.4)
bheemu.move(e - 10, e - 8, 'snap', sweat=1.0, **SHOCK); gaju.move(e - 8, e - 5, 'snap', ear=-1.0, **HAPPY)
END = e
ep.close(END, 2010, G0 - 560)
sc.hit(END + 26, 'crash', 0.9); sc.hit(END + 26, 'timp', 0.9, note=36)                            # we only hear it
print('frames needed', END + 34)

if __name__ == '__main__':
    ep.main(__file__)
