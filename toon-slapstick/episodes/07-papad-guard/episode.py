"""Bheemu & Gaju, episode 7: "The Papad Guard"  (about 29 s, vertical, silent; only Ammamma speaks)

Ammamma lays six papads to dry and puts Bheemu on guard. He nods off. Laddu takes one, Bujji two, Gaju two
from the air. Bheemu wakes to one papad and footsteps, and eats the evidence just as Ammamma walks in.
"""
import os, sys, math
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', 'engine'))
from toon import GROUND
from chars import Bheemu, Gaju
from cast import Ammamma, Laddu, Bujji
from scene import Painted, Prop, rect, puffs, stars
from india import telugu
from sets import terrace
from acting import blink, look, bob, walk, squash, take, shake, zip_off, chew, flap, arc
from sound import veena, bansuri, xylo
from voice import speak
from show import Show, face, enter, ladle, papad, cloth, zzz, CALM, HAPPY, LAUGH, ANGRY, SHOCK, SORRY, SLEEP

G0 = GROUND
ep = Show(7, 'The Papad Guard', 'papad_guard', 798, Painted(2800, terrace, top=(110, 190, 244), bottom=(166, 110, 90)))
st, sc, cam = ep.st, ep.sc, ep.cam
SPOT = [(x, y) for y in (G0 + 96, G0 + 140) for x in (1100, 1260, 1420)]


def notice(g, p, f):                                   # "Papads drying. Thieves will be beaten!"
    g.shape(rect(-210, -150, 420, 150, 8), (255, 250, 220), True, 4, (58, 42, 40))
    telugu(g, 'అప్పడాలు ఎండుతున్నాయి.', 0, -92, 36, (40, 60, 150), 'Ramabhadra')
    telugu(g, 'దొంగలకు దెబ్బలు!', 0, -38, 42, (190, 30, 40), 'Ramabhadra')


bheemu = Bheemu(x=850, z=3, face=0.3, yaw=0.6)
amma = Ammamma(x=1600, z=3, face=-1, yaw=-0.7)
laddu = Laddu(x=2000, z=4, show=0.0, lid=0.3)
bujji = Bujji(x=400, z=4, show=0.0)
gaju = Gaju(x=1260, y=G0 - 1400, z=5, show=0.0)
ldl = Prop(ladle, x=0, y=0, z=3.5, show=0.0)
ct = Prop(cloth, x=1260, y=G0 + 118, z=5.5)
pp = [Prop(papad, x=x, y=y, z=6) for x, y in SPOT]
extra = [Prop(papad, x=0, y=0, z=6, show=0.0) for _ in range(3)]
nb = Prop(notice, x=1500, y=G0 - 130, z=0)
st.add(nb, bheemu, amma, ldl, laddu, bujji, ct, *pp, gaju, *extra)
ep.shot(0, 1210, 0.95, cut=False)


def snore(f0, f1):
    for f in range(f0, f1 - 23, 24):
        bheemu.move(f, f + 12, 'io', sy=1.05, sx=0.98, mouth_open=0.35); bheemu.move(f + 12, f + 24, 'io', sy=0.97, sx=1.02, mouth_open=0.0)
        sc.slide(f, 43, 48, 11, 0.22); sc.slide(f + 13, 60, 55, 9, 0.12)


def grab(i, f, who, anchor, dx=0, dy=0, n=4, until=900):
    ax, ay = st.probe(f + n, who, anchor)
    arc(pp[i], f, f + n, ax + dx, ay + dy, 40); pp[i].attach(f + n, until, who, anchor, dx, dy); sc.hit(f + n, 'pop', 0.6, note=76)


# ------------------------------------------------------------------ 1. the order  (36-180)
sc.raga(36, 180, 'calm')
amma.move(38, 42, 'over', armL=(-70, -40), handL='point', brow_ang=12, pupil=(-0.6, 0.6))
e = speak(ep, amma, 40, 'a_papad')                                    # "Mind the papads! If even one is missing, I won't keep quiet."
for f in range(52, e - 10, 20):
    amma.move(f, f + 3, 'snap', armL=(-90, -24)); amma.move(f + 3, f + 9, 'over', armL=(-70, -40))
bheemu.move(e - 20, e - 17, 'snap', armR=(-52, -318), handR='open', sy=1.05, sx=0.97, brow=6); ep.tap(e - 18, 'dha', 1.1)
bheemu.move(e, e + 4, 'io', armR=(0, 0), handR='mitt', sy=1.0, sx=1.0, brow=0)
amma.move(e, e + 3, 'over', armL=(0, 0), handL='mitt', face=1, yaw=0.7, brow_ang=0, pupil=(0.5, 0))
for f in walk(amma, e + 4, e + 28, 2100, 7, 30):
    ep.tap(f, 'na', 0.5)
amma.set(e + 29, show=0.0)

# ------------------------------------------------------------------ 2. eyelids  (e+30 ...)
S = e + 30
bheemu.move(S, S + 4, 'in', sy=0.82, sx=1.1, face=0.0, yaw=0.3); bheemu.set(S + 4, sit=1.0); bheemu.move(S + 4, S + 14, 'elastic', sy=1.0, sx=1.0)
sc.hit(S + 4, 'timp', 0.5, note=38)
sc.raga(S + 10, S + 250, 'sneak')
bheemu.move(S + 20, S + 34, 'io', lid=0.65, head_dy=10); bheemu.move(S + 36, S + 38, 'snap', lid=0.0, head_dy=0); shake(bheemu, S + 38, S + 44, 3); sc.note(S + 36, xylo, 84, 0.1, 0.5)
bheemu.move(S + 50, S + 66, 'io', lid=0.8, head_dy=14); face(bheemu, S + 68, 5, head_dy=8, yaw=0.0, **SLEEP)
Z = S + 74
zzz(st, bheemu, Z, Z + 190); snore(Z, Z + 190)

# ------------------------------------------------------------------ 3. three visitors
T = Z + 16                                                              # Laddu, on tiptoe
laddu.set(T, show=1.0, x=1980, face=-1, yaw=-0.8)
for f in walk(laddu, T, T + 30, 1500, 10, 26):
    sc.note(f, xylo, 76, 0.12, 0.5)
laddu.move(T + 32, T + 35, 'snap', head_dy=30, head_rot=14); grab(2, T + 34, laddu, 'mouth', -14, 6, 3, T + 76)
laddu.move(T + 38, T + 42, 'over', head_dy=0, head_rot=0, pupil=(-0.9, 0)); laddu.move(T + 46, T + 49, 'over', face=1, yaw=0.8, pupil=(0, 0))
for f in walk(laddu, T + 48, T + 74, 2000, 9, 26):
    sc.note(f, xylo, 79, 0.12, 0.5)
laddu.set(T + 76, show=0.0); pp[2].set(T + 76, show=0.0)
T2 = T + 80                                                             # Bujji, in a blur
bujji.set(T2, show=1.0, x=420, face=1, yaw=0.9, stride=60, ear=-0.6); bujji.move(T2, T2 + 5, 'lin', x=1190, step=2.0); sc.hit(T2, 'zip', 0.7)
bujji.move(T2 + 5, T2 + 8, 'over', face=0.0, yaw=0.0, stride=0.0, ear=1.0, pupil=(-0.9, 0)); puffs(st, T2 + 5, 1100, G0, n=3, size=26, spread=40, life=9, dirx=-1)
grab(1, T2 + 12, bujji, 'handR', 10, 0, 3, T2 + 34); grab(4, T2 + 16, bujji, 'handL', -10, 0, 3, T2 + 34)
bujji.move(T2 + 22, T2 + 25, 'snap', face=-1, yaw=-0.9, stride=60, ear=-0.6); bujji.move(T2 + 26, T2 + 31, 'lin', x=400, step=4.0); sc.hit(T2 + 26, 'zip', 0.7)
for i in (1, 4):
    pp[i].set(T2 + 32, show=0.0)
bujji.set(T2 + 32, show=0.0)
T3 = T2 + 40                                                            # Gaju, from the sky
gaju.set(T3, show=1.0, x=1180, y=G0 - 1400, trunk=(0, 90), trunk_curl=0.3, pupil=(-0.7, 0.7))
gaju.move(T3, T3 + 28, 'io', y=G0 - 470)
for fb in flap(gaju, T3, T3 + 86, 4, 0.8):
    sc.hit(fb, 'flap', 0.25)
gaju.move(T3 + 30, T3 + 36, 'over', trunk=(-40, 300), trunk_curl=0.0); sc.slide(T3 + 30, 70, 58, 6, 0.3)
for k, i in enumerate((0, 3)):
    f = T3 + 40 + k * 8
    hx, hy = st.probe(f + 4, gaju, 'head')
    arc(pp[i], f, f + 5, hx, hy + 40, 30, spin=360); pp[i].set(f + 5, show=0.0); sc.hit(f + 4, 'gulp', 0.7)
    gaju.set(f + 5, head_sx=1.12, head_sy=0.92); gaju.move(f + 6, f + 10, 'elastic', head_sx=1.0, head_sy=1.0)
gaju.move(T3 + 58, T3 + 62, 'over', trunk=(30, 60), trunk_curl=0.7, **HAPPY)
gaju.move(T3 + 62, T3 + 86, 'in', y=G0 - 1500); gaju.set(T3 + 87, show=0.0)

# ------------------------------------------------------------------ 4. one papad and footsteps
K = T3 + 92
sc.duck(K, K + 50, 0.3)
for f in (K, K + 7):
    sc.hit(f, 'munch', 1.0)                                              # somebody is crunching, somewhere
bheemu.move(K + 10, K + 12, 'snap', eye_open=1.0, head_dy=0, mouth_open=0.0, sy=1.0, sx=1.0); look(bheemu, K + 14, yaw=0.5, pupil=(0.8, 0.8)); blink(bheemu, K + 22)
f = take(st, bheemu, K + 30, 1.0); sc.hit(K + 33, 'timp', 0.9); ep.tap(K + 33, 'dha', 1.2)
look(bheemu, f, yaw=-0.8, pupil=(-0.9, 0)); look(bheemu, f + 8, yaw=0.8, pupil=(0.9, 0)); face(bheemu, f + 4, 3, **SORRY)
W0 = f + 18
for i in range(4):
    ep.tap(W0 + i * 8, 'dha', 0.6 + i * 0.15)                             # she is coming back
bheemu.move(W0 + 2, W0 + 4, 'snap', **SHOCK)
bheemu.move(W0 + 12, W0 + 15, 'snap', armR=(230, 60), handR='open', rot=10, yaw=0.5, pupil=(0.8, 0.8), eye_pop=1.0, mouth_open=0.0, brow=0)
mx, my = st.probe(W0 + 20, bheemu, 'mouth')
arc(pp[5], W0 + 16, W0 + 21, mx, my, 120, spin=360); pp[5].set(W0 + 21, show=0.0)
bheemu.move(W0 + 18, W0 + 20, 'snap', mouth_open=1.0, armR=(0, 0), handR='mitt', rot=0); bheemu.move(W0 + 21, W0 + 23, 'snap', mouth_open=0.0, cheeks=1.0, yaw=0.0, pupil=(0, -0.8), smile=0.3, sweat=1.0, brow_ang=0)
sc.hit(W0 + 21, 'munch', 1.0)
amma.set(W0 + 14, armR=(34, -130), handR='grip', **CALM); ldl.set(W0 + 14, show=1.0); ldl.attach(W0 + 14, 900, amma, 'handR', 0, 20)
enter(ep, amma, W0 + 14, W0 + 34, 2100, 1640, 7, 30, 'dha', 0.9)
look(amma, W0 + 36, yaw=-0.5, pupil=(-0.6, 0.8)); face(amma, W0 + 40, 3, **SHOCK)
look(amma, W0 + 50, yaw=-0.8, pupil=(-0.9, 0.1)); face(amma, W0 + 52, 4, **ANGRY)
bheemu.set(W0 + 58, head_sy=1.2, head_sx=0.88); bheemu.set(W0 + 61, head_sy=0.86, head_sx=1.1, cheeks=0.0); bheemu.move(W0 + 62, W0 + 68, 'elastic', head_sy=1.0, head_sx=1.0)
sc.hit(W0 + 59, 'gulp', 1.0)
amma.move(W0 + 64, W0 + 67, 'snap', armR=(40, -270))
e2 = speak(ep, amma, W0 + 66, 'a_bheemu', v=1.2)                         # "BHEEMU!"
R = e2 + 2
sc.raga(R, R + 130, 'chase')
bheemu.set(R, sit=0.0); g1 = zip_off(st, bheemu, R, 300, wind=8); g2 = zip_off(st, amma, R + 6, 300, wind=8); sc.hit(g1, 'zip', 1.0); sc.hit(g2, 'zip', 0.9)
ldl.set(g2, show=0.0)

# ------------------------------------------------------------------ 5. and the real thieves
C = g2 + 6
ep.shot(C, 2085, 1.3)
for p_ in (ct, nb):
    p_.set(C, show=0.0)
laddu.set(C, show=1.0, x=1860, y=G0, face=0.0, yaw=0.2, head_dy=0, head_rot=0, **HAPPY)
bujji.set(C, show=1.0, x=2080, y=G0, face=0.0, yaw=0.0, stride=0.0, ear=0.7, armR=(8, -16), **HAPPY)
gaju.set(C, show=1.0, x=2310, y=G0, z=4, ear=0.0, trunk=(-30, -20), trunk_curl=0.9, yaw=-0.2, **HAPPY)
for i, (a, anc, dx, dy) in enumerate(((laddu, 'mouth', 0, 14), (bujji, 'handR', 0, -6), (gaju, 'trunk', 0, -6))):
    extra[i].set(C, show=1.0, sx=0.8, sy=0.8); extra[i].attach(C, 900, a, anc, dx, dy)
for a in (laddu, bujji, gaju):
    chew(a, C, C + 40, 6)
for f in range(C, C + 40, 6):
    sc.hit(f, 'munch', 0.5)
X = C + 40                                                               # the chase goes past behind them
for a, d in ((bheemu, 0), (amma, 7)):
    a.set(X + d, show=1.0, x=1300, y=G0, z=1, wheel=1.0, stride=36, rot=14, face=1, yaw=1.0, sx=1, sy=1)
    a.move(X + d, X + d + 9, 'lin', x=2900, step=a.value('step', X + d) + 3); a.set(X + d + 10, show=0.0)
    sc.hit(X + d, 'zip', 0.9)
bheemu.set(X, sit=0.0, **SHOCK)
for a in (laddu, bujji, gaju):
    a.move(X + 2, X + 4, 'snap', head_sx=1.0, head_sy=1.0, cheeks=0.0, happy=0.0, eye_open=1.0, yaw=-0.7, pupil=(-0.9, 0))
    a.move(X + 6, X + 20, 'lin', yaw=0.7, pupil=(0.9, 0)); blink(a, X + 26)
    face(a, X + 34, 4, yaw=0.0, pupil=(0, 0), **HAPPY)
    chew(a, X + 38, X + 70, 6)
sc.hit(X + 32, 'ghatam', 0.8, note=62)
END = X + 60
ep.close(END, 2080, G0 - 170)
print('frames needed', END + 34)

if __name__ == '__main__':
    ep.main(__file__)
