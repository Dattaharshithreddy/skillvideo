"""Bheemu & Gaju, episode 4: "Afternoon Nap"  (about 30 s, vertical, silent; only Chintu speaks)

Bheemu hangs up "I am sleeping. Wake me and I bite!" and naps. Chintu's cricket ball keeps coming through
the window: on his head, then bouncing on his snoring belly. The third time he catches it in his sleep and
belly-bumps it back out for a six. Chintu and Gaju carry the hero off, still asleep.
"""
import os, sys, math
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', 'engine'))
from toon import GROUND, oval
from chars import Bheemu, Gaju
from cast import Chintu
from scene import Painted, Prop, rect, puffs, stars
from india import illu, telugu
from acting import blink, look, walk, squash, take, zip_off, arc, flap
from sound import veena, bansuri, xylo
from voice import speak
from show import Show, face, enter, ball, zzz, CALM, HAPPY, LAUGH, ANGRY, SHOCK, SORRY, SLEEP

G0 = GROUND
ep = Show(4, 'Afternoon Nap', 'afternoon_nap', 694, Painted(3400, illu))
st, sc, cam = ep.st, ep.sc, ep.cam
BX = 2440
WIN = (3190, G0 - 900)                                  # the window the ball comes through


def card(g, p, f):                                     # "I am sleeping. Wake me and I bite!"
    g.shape(rect(-4, -40, 8, 44), (90, 80, 80), False)
    g.shape(rect(-170, 0, 340, 150, 10), (255, 250, 220), True, 4, (58, 42, 40))
    telugu(g, 'నిద్రపోతున్నాను.', 0, 58, 40, (40, 60, 150), 'Ramabhadra')
    telugu(g, 'లేపితే కరుస్తాను!', 0, 114, 40, (190, 30, 40), 'Ramabhadra')


bheemu = Bheemu(x=BX, z=3)
chintu = Chintu(x=3500, z=4, show=0.0)
gaju = Gaju(x=3600, z=3.5, show=0.0)
sign = Prop(card, x=2790, y=G0 - 800, z=0, rot=3, sx=1.25, sy=1.25)
bl = Prop(ball, x=0, y=0, z=6, show=0.0)
st.add(sign, bheemu, gaju, chintu, bl)
ep.shot(0, 2730, 0.95, cut=False)


def snore(f0, f1):
    for f in range(f0, f1 - 23, 24):
        bheemu.move(f, f + 12, 'io', sy=1.05, sx=0.98, mouth_open=0.35); bheemu.move(f + 12, f + 24, 'io', sy=0.97, sx=1.02, mouth_open=0.0)
        sc.slide(f, 43, 48, 11, 0.22); sc.slide(f + 13, 60, 55, 9, 0.12)


# ------------------------------------------------------------------ 1. nap time  (36-150)
sc.raga(36, 150, 'sweet', v=0.8)
bheemu.move(40, 48, 'over', mouth_open=0.9, mouth_w=0.8, eye_open=0.0, armL=(-50, -420), armR=(50, -420), handL='open', handR='open', sy=1.06, sx=0.96)   # a huge yawn
sc.slide(40, 55, 67, 8, 0.3); sc.slide(50, 67, 50, 10, 0.3)
bheemu.move(54, 62, 'io', mouth_open=0.0, mouth_w=1.0, armL=(0, 0), armR=(0, 0), handL='mitt', handR='mitt', sy=1.0, sx=1.0)
look(bheemu, 62, yaw=0.5, pupil=(0.6, -0.7)); bheemu.move(62, 64, 'out', eye_open=1.0); blink(bheemu, 68)            # checks his sign is straight
sign.move(70, 74, 'over', rot=0); bheemu.move(68, 71, 'snap', armR=(150, -300), handR='point'); bheemu.move(74, 78, 'io', armR=(0, 0), handR='mitt'); sc.note(72, xylo, 79, 0.2, 0.6)
bheemu.move(80, 84, 'in', sy=0.8, sx=1.12, yaw=0.0, pupil=(0, 0)); bheemu.set(84, sit=1.0); bheemu.move(84, 94, 'elastic', sy=1.0, sx=1.0)
sc.hit(84, 'timp', 0.6, note=38); puffs(st, 84, BX, G0, n=4, size=34, spread=140, life=12)
face(bheemu, 92, 6, **SLEEP)
zzz(st, bheemu, 100, 168); snore(100, 150)

# ------------------------------------------------------------------ 2. first ball: on the head  (150-296)
B = 150
tx, ty = st.probe(B + 16, bheemu, 'top')
bl.set(B, show=1.0, x=WIN[0], y=WIN[1]); arc(bl, B, B + 18, tx, ty + 6, 60, spin=500); sc.hit(B, 'whoosh', 0.6, d=0.5)
bheemu.set(B + 18, head_sy=0.74, head_sx=1.18, head_dy=20, glasses_rot=12, mouth_open=0.0); bheemu.move(B + 20, B + 30, 'elastic', head_sy=1.0, head_sx=1.0, head_dy=0)
sc.hit(B + 18, 'bonk', 1.0, note=62); stars(st, B + 18, tx, ty - 20, n=5, r=110, life=10); st.shake(B + 18, 10, 6)
arc(bl, B + 18, B + 34, 2880, G0 - 22, 220, spin=300); arc(bl, B + 34, B + 44, 2960, G0 - 22, 60, spin=200); sc.hit(B + 34, 'pop', 0.5, note=60)
bheemu.move(B + 22, B + 24, 'snap', eye_open=1.0, brow_ang=22, lid=0.3, pupil=(0.8, 0.3))       # one grumpy look... and back to sleep
bheemu.move(B + 40, B + 48, 'io', eye_open=0.0, brow_ang=0, lid=0.0, glasses_rot=0)
zzz(st, bheemu, B + 52, 318); snore(B + 52, 296)
sc.raga(196, 296, 'sneak')
chintu.set(200, show=1.0, x=3380, face=-1, yaw=-0.8, armL=(-10, -60), armR=(10, -60), handL='open', handR='open', **SORRY)       # tiptoes in for his ball
for f in walk(chintu, 200, 236, 3010, 12, 26):
    sc.note(f, xylo, 76, 0.15, 0.5)
chintu.move(238, 241, 'snap', armL=(-40, 60), handL='grip', sy=0.9); bl.attach(242, 300, chintu, 'handL', 0, 10); sc.hit(241, 'pop', 0.5, note=79)
chintu.move(244, 248, 'over', sy=1.0, armL=(-10, -30), face=1, yaw=0.8)
for f in walk(chintu, 250, 282, 3420, 12, 26):
    sc.note(f, xylo, 74, 0.15, 0.5)
chintu.set(284, show=0.0); bl.set(284, show=0.0)

# ------------------------------------------------------------------ 3. second ball: the belly trampoline  (300-490)
B = 304
bx, by = st.probe(B + 16, bheemu, 'belly')
bl.set(B - 1, x=WIN[0], y=WIN[1]); bl.set(B, show=1.0); arc(bl, B, B + 16, bx, by - 40, 80, spin=500); sc.hit(B, 'whoosh', 0.6, d=0.5)
for i in range(3):
    f = B + 16 + i * 16
    bheemu.set(f, sy=0.9, sx=1.1); bheemu.move(f + 1, f + 9, 'elastic', sy=1.0, sx=1.0)
    sc.hit(f, 'boing', 0.8, note=50 + i * 4)
    if i < 2:
        arc(bl, f, f + 16, bx, by - 40, 260 + i * 120, spin=200)
arc(bl, B + 48, B + 62, 2650, G0 - 22, 330, spin=300)
bheemu.move(B + 34, B + 36, 'snap', **SHOCK); sc.hit(B + 35, 'timp', 0.7)
face(bheemu, B + 46, 4, yaw=0.6, pupil=(0.8, 0.3), **ANGRY)
bheemu.move(B + 62, B + 66, 'over', armR=(96, 4), handR='grip'); bl.attach(B + 66, B + 144, bheemu, 'handR', 0, 0)
sc.raga(B + 60, B + 150, 'calm', v=0.7)
enter(ep, chintu, B + 62, B + 78, 3420, 3060, 5, 30, 'na', 0.5); enter(ep, gaju, B + 66, B + 84, 3560, 3220, 6, 26, 'na', 0.4)
chintu.set(B + 62, armR=(0, 0), handL='open', **CALM)
chintu.move(B + 78, B + 82, 'over', armL=(-70, -90), handL='open', yaw=-0.8)
e = speak(ep, chintu, B + 82, 'c_ball')                                                     # "Bheemu! Give the ball!"
T = max(e + 4, B + 140)
bheemu.move(T - 8, T, 'out', armR=(-40, -160), rot=-6); bheemu.move(T, T + 3, 'snap', armR=(210, -260), handR='open', rot=5); bheemu.move(T + 3, T + 12, 'elastic', rot=0, armR=(0, 0), handR='mitt')
bl.attach(B + 66, T + 1, bheemu, 'handR', 0, 0); arc(bl, T + 1, T + 11, 3700, G0 - 800, 200, spin=600); sc.hit(T, 'whoosh', 0.9, d=0.3)
for a in (chintu, gaju):
    a.move(T + 2, T + 4, 'snap', sy=0.72, sx=1.12, **SHOCK); a.move(T + 8, T + 16, 'elastic', sy=1.0, sx=1.0)
sc.hit(T + 16, 'crash', 0.8); st.shake(T + 16, 14, 8)
for a in (chintu, gaju):
    look(a, T + 18, yaw=0.9, pupil=(0.9, 0)); face(a, T + 28, 4, **SORRY)
g1 = zip_off(st, chintu, T + 34, 3700, wind=7); g2 = zip_off(st, gaju, T + 37, 3800, wind=7); sc.hit(g1, 'zip', 0.8)
face(bheemu, T + 20, 6, yaw=0.0, pupil=(0, 0), **SLEEP)
zzz(st, bheemu, T + 30, T + 110); snore(T + 30, T + 78)

# ------------------------------------------------------------------ 4. third ball: caught asleep, and a six
B = T + 80
sc.duck(B - 6, B + 60, 0.3)
bl.set(B - 1, show=1.0, x=3500, y=G0 - 700, rot=0); bl.move(B, B + 6, 'lin', x=BX + 150, y=G0 - 330); sc.hit(B, 'whoosh', 0.8, d=0.25)
bheemu.move(B + 3, B + 6, 'snap', armR=(98, -270), handR='grip')                               # the arm goes up on its own
bl.attach(B + 6, B + 30, bheemu, 'handR', 0, -6); sc.hit(B + 6, 'pop', 1.0, note=72); stars(st, B + 6, BX + 150, G0 - 340, n=4, r=80, life=8)
snore(B + 8, B + 32)
bheemu.move(B + 30, B + 33, 'snap', armR=(60, -330), handR='open')                             # a little toss...
bx, by = st.probe(B + 30, bheemu, 'belly')
bl.set(B + 30, x=BX + 110, y=G0 - 400); arc(bl, B + 30, B + 44, bx + 60, by - 20, 240, spin=300)
bheemu.move(B + 40, B + 44, 'out', sx=0.9, sy=1.06, armR=(0, 0), handR='mitt')
bheemu.set(B + 44, sx=1.3, sy=0.92); bheemu.move(B + 46, B + 58, 'elastic', sx=1.0, sy=1.0)   # ...and the belly does the rest
bl.move(B + 44, B + 50, 'lin', x=WIN[0], y=WIN[1]); bl.set(B + 51, show=0.0)
sc.hit(B + 44, 'bonk', 1.0, note=50); ep.tap(B + 44, 'dha', 1.4); st.shake(B + 44, 22, 10); sc.slide(B + 44, 60, 96, 8, 0.6)
zzz(st, bheemu, B + 56, 694); snore(B + 60, B + 108)
C = B + 60
sc.hit(C, 'tada', 0.8); sc.raga(C + 4, C + 110, 'chase', v=0.8)
chintu.set(C, show=1.0, x=3500, wheel=0.0, stride=0.0, rot=0, sx=1, sy=1, armL=(-30, -210), armR=(30, -210), handL='open', handR='open', **LAUGH)
gaju.set(C, show=1.0, x=3650, wheel=0.0, stride=0.0, rot=0, sx=1, sy=1, **HAPPY)
enter(ep, chintu, C, C + 18, 3500, 2700, 4, 34, 'na', 0.5); enter(ep, gaju, C + 4, C + 24, 3650, 2880, 5, 28, 'na', 0.4)
speak(ep, chintu, C + 2, 'c_six')                                                              # "Sixer!"
for fb in flap(gaju, C + 4, C + 110, 4, 0.6):
    pass
L = C + 30                                                                                     # they carry the hero out, still asleep
chintu.move(L - 4, L, 'over', face=1, yaw=0.5, armL=(-60, -150), armR=(-110, -150), x=2640); gaju.move(L - 4, L, 'over', x=2560, trunk=(-90, -120), trunk_curl=-0.6, yaw=-0.3)
bheemu.move(L, L + 6, 'over', y=G0 - 170, rot=-6); sc.slide(L, 55, 72, 6, 0.4)
for a, dx in ((bheemu, 0), (chintu, 0), (gaju, 0)):
    a.move(L + 8, L + 70, 'lin', x=a.value('x', L + 8) + 520)
for a in (chintu, gaju):
    a.move(L + 8, L + 70, 'lin', step=a.value('step', L + 8) + 8, stride=24)
for f in range(L + 8, L + 70, 8):
    bheemu.move(f, f + 4, 'out', y=G0 - 190); bheemu.move(f + 4, f + 8, 'in', y=G0 - 170); ep.tap(f, 'ge', 0.6)
END = L + 44
ep.close(END, bheemu.value('x', END + 8) + 20, G0 - 560)
print('frames needed', END + 34)

if __name__ == '__main__':
    ep.main(__file__)
