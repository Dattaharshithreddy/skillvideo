"""Bheemu & Gaju, episode 6: "Kite Day"  (about 26 s, vertical, silent; only Chintu speaks)

Sankranti on the terrace. Chintu's kite gets stuck on the water tank. Gaju flies up to free it, gets
wound up in the string and becomes the kite. A black kite attacks; Bheemu yanks the string and Gaju
knocks it out of the sky. Then Bheemu lets go to clap.
"""
import os, sys, math
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', 'engine'))
from toon import GROUND, poly, oval, smooth
from chars import Bheemu, Gaju
from cast import Chintu
from scene import Painted, Prop, rect, puffs, stars, zip_lines
from india import telugu
from sets import terrace
from acting import blink, look, bob, walk, squash, take, shake, arc, flap
from sound import veena, bansuri, xylo
from voice import speak
from show import Show, face, laugh, hop, kite, CALM, HAPPY, LAUGH, ANGRY, SHOCK, SORRY, SLY

G0 = GROUND
ep = Show(6, 'Kite Day', 'kite_day', 646, Painted(2800, terrace, top=(110, 190, 244), bottom=(166, 110, 90)))
st, sc, cam = ep.st, ep.sc, ep.cam
TANK = (2000, G0 - 905)


def banner(g, p, f):                                   # "Happy Sankranti"
    for x in (-380, 380):
        g.shape(poly([(x, -40), (x * 1.25, -260)], False), None, True, 4, (90, 80, 80))
    g.shape(rect(-400, -40, 800, 120, 10), (250, 208, 80), True, 5, (58, 42, 40))
    telugu(g, 'సంక్రాంతి శుభాకాంక్షలు', 0, 44, 62, (170, 30, 40), 'Ramabhadra')
    for i in range(9):
        x = -360 + i * 90
        g.shape(poly([(x - 30, 80), (x + 30, 80), (x, 136)]), ((232, 80, 70), (60, 170, 150), (120, 110, 210))[i % 3], True, 3, (58, 42, 40))


def rival(g, p, f):                                    # the black kite from the next terrace
    g.shape(poly([(0, -90), (72, 0), (0, 90), (-72, 0)]), (40, 40, 52))
    for s in (-1, 1):
        g.shape(poly([(s * 12, -20), (s * 44, -34), (s * 40, -8)]), (255, 240, 120), False)
    g.shape(poly([(-22, 26), (-8, 16), (0, 26), (8, 16), (22, 26)], False), None, True, 4, (255, 240, 120))
    g.shape(poly([(0, 90), (-16, 130), (16, 130)]), (214, 60, 56))


bheemu = Bheemu(x=1250, z=3, sit=1.0, yaw=0.5, pupil=(0.5, -0.8), smile=0.8)
chintu = Chintu(x=1490, z=4, armL=(-30, -200), armR=(34, -190), handL='grip', handR='grip', pitch=-0.6, pupil=(0.2, -0.8), smile=1.0)
gaju = Gaju(x=1700, z=3.5, pitch=-0.6, pupil=(0, -0.8), smile=0.8)
kt = Prop(kite, x=1500, y=G0 - 1250, z=2.5)
rk = Prop(rival, x=2700, y=G0 - 1500, z=6, show=0.0)
bn = Prop(banner, x=1690, y=G0 - 1700, z=0)
st.add(bn, kt, bheemu, gaju, chintu, rk)
ep.shot(0, 1690, 0.85, cut=False)
holder = {'who': chintu, 'hand': 'handR', 'to': 'kite', 'on': True}


def string(g, f):
    """The kite string, from whoever holds it to the kite (or to Gaju once he is the kite)."""
    for f0, who, hand, to in LINE:
        if f >= f0:
            cur = (who, hand, to)
    who, hand, to = cur
    if who is None:
        return
    a = who.anchors.get(hand)
    b = kt.anchors.get('tail') if to == 'kite' else gaju.anchors.get('belly')
    if a and b:
        mid = ((a[0] + b[0]) / 2 + 30, (a[1] + b[1]) / 2 + 90)
        g.shape(smooth([a, mid, b], False), None, True, 3, (250, 250, 250))


LINE = [(0, chintu, 'handR', 'kite')]
st.fx.append(string)

# ------------------------------------------------------------------ 1. a perfect day for kites  (36-130)
sc.raga(36, 130, 'calm')
for i, f in enumerate(range(0, 110, 2)):
    kt.set(f, x=1500 + math.sin(i * 0.16) * 70, y=G0 - 1250 + math.cos(i * 0.11) * 40, rot=math.sin(i * 0.16) * 12)
for f in range(40, 104, 16):
    chintu.move(f, f + 6, 'io', armR=(50, -170)); chintu.move(f + 8, f + 14, 'io', armR=(34, -190))
bob(bheemu, 36, 300); bob(gaju, 36, 240, 12, 0.03)
sc.hit(108, 'whoosh', 0.8, d=0.6); zip_lines(st, 108, 1300, G0 - 1200, 1, life=12, length=500, h=400)
kt.move(110, 128, 'in', x=TANK[0], y=TANK[1], rot=385); sc.slide(110, 84, 60, 18, 0.5)
kt.set(128, rot=25); sc.hit(128, 'bonk', 0.7, note=70)
for a in (chintu, gaju, bheemu):
    look(a, 114, yaw=0.7, pupil=(0.8, -0.6))
chintu.move(128, 130, 'snap', **SHOCK)
speak(ep, chintu, 132, 'c_kite')                                                              # "Oh no! My kite!"

# ------------------------------------------------------------------ 2. stuck  (186-250)
sc.raga(186, 300, 'sneak')
face(chintu, 184, 3, **ANGRY)
for i, f in enumerate((188, 198, 208)):
    chintu.move(f, f + 3, 'snap', rot=-10 - i * 3, armR=(10, -150), armL=(-40, -160)); chintu.move(f + 3, f + 8, 'over', rot=0, armR=(34, -190), armL=(-30, -200))
    kt.set(f + 1, rot=40); kt.move(f + 2, f + 8, 'elastic', rot=25); sc.hit(f, 'ghatam', 0.8, note=60 + i * 2)
chintu.move(216, 220, 'over', armL=(0, 0), handL='mitt', armR=(100, -230), handR='point', yaw=0.8, pitch=0.0, pupil=(0.8, 0), **CALM)
LINE.append((216, chintu, 'handL', 'kite'))
speak(ep, chintu, 220, 'c_fly')                                                               # "Gaju, fly!"
look(gaju, 222, yaw=-0.6, pupil=(-0.8, 0)); gaju.move(222, 225, 'over', pitch=0.0)
gaju.move(246, 249, 'snap', brow=12, smile=1.0); sc.hit(246, 'ghatam', 0.8, note=76)

# ------------------------------------------------------------------ 3. Gaju becomes the kite  (252-360)
for fb in flap(gaju, 250, 300, 4):
    sc.hit(fb, 'flap', 0.5)
gaju.move(252, 284, 'io', x=TANK[0] - 90, y=TANK[1] + 160, yaw=0.5, brow=0); sc.slide(252, 60, 84, 30, 0.4)
gaju.move(284, 290, 'over', trunk=(70, -60), trunk_curl=-0.6)
W0 = 298
sc.raga(W0, 480, 'chase', v=0.85)
sc.hit(W0, 'whoosh', 1.0, d=0.6); zip_lines(st, W0, 1500, G0 - 1100, 1, life=12, length=500, h=500)
gaju.move(W0, W0 + 18, 'lin', rot=720); gaju.set(W0 + 18, rot=0); sc.run(W0, W0 + 18, 72, 2, 0.4)       # round and round goes the string
kt.attach(W0, W0 + 18, gaju, 'trunk', 0, 0)
kt.set(W0 + 18, sx=2.4, sy=2.4, rot=0); kt.attach(W0 + 18, 900, gaju, 'belly', 0, -20)
LINE.append((W0 + 18, chintu, 'handL', 'gaju'))
gaju.move(W0 + 18, W0 + 20, 'snap', trunk=(30, 60), trunk_curl=0.7, ear=0.0, **SHOCK)
gaju.move(W0 + 18, W0 + 44, 'io', x=1700, y=G0 - 1300)
chintu.move(W0 + 20, W0 + 23, 'snap', handR='grip', armR=(60, -200), armL=(40, -210), handL='grip', rot=-16, **SHOCK)
chintu.move(W0 + 26, W0 + 46, 'out', x=1760); sc.hit(W0 + 26, 'skid', 0.9, d=0.6)                # ...and the kite is flying the boy
for f in (W0 + 28, W0 + 34, W0 + 40):
    puffs(st, f, chintu.value('x', f) + 40, G0, n=3, size=26, spread=30, life=9, dirx=1)
bheemu.move(W0 + 24, W0 + 26, 'snap', **SHOCK); bheemu.set(W0 + 30, sit=0.0, face=1, yaw=0.8)
bheemu.move(W0 + 30, W0 + 44, 'out', x=1590); bheemu.move(W0 + 30, W0 + 44, 'lin', step=2.0, stride=40)
bheemu.move(W0 + 44, W0 + 47, 'snap', stride=0.0, armR=(110, -120), armL=(90, -100), handR='grip', handL='grip', rot=-8, **ANGRY)
LINE.append((W0 + 46, bheemu, 'handR', 'gaju'))
ep.tap(W0 + 46, 'dha', 1.2); chintu.move(W0 + 46, W0 + 50, 'over', rot=-6)
F0 = W0 + 52
face(gaju, F0 + 6, 4, **HAPPY)


def fly(f):
    t = (f - F0) * 0.07
    return 1760 + math.cos(t) * 230, G0 - 1290 + math.sin(t * 2) * 80


# ------------------------------------------------------------------ 4. the black kite  (410-470)
R0 = F0 + 34
Y = R0 + 64                                                                                    # the yank
for f in range(F0, Y, 2):
    x, y = fly(f)
    gaju.set(f, x=x, y=y, rot=math.cos((f - F0) * 0.07) * 10)
rk.set(R0, show=1.0)
for f0, f1, (x, y) in ((R0, R0 + 14, fly(R0 + 14)), (R0 + 14, R0 + 26, (1150, G0 - 1560)), (R0 + 30, R0 + 42, fly(R0 + 42)), (R0 + 42, R0 + 56, (2260, G0 - 1400))):
    rk.move(f0, f1, 'io', x=x + 50, y=y - 60, rot=rk.value('rot', f0) + 200)
for f in (R0 + 12, R0 + 40):
    sc.hit(f, 'whoosh', 0.9, d=0.3); gaju.move(f, f + 2, 'snap', **SHOCK); face(gaju, f + 10, 3, **ANGRY)
rk.move(R0 + 56, Y + 8, 'io', rot=rk.value('rot', R0 + 56) + 30)
face(bheemu, R0 + 44, 3, pitch=-0.5, **ANGRY)
sc.duck(Y - 8, Y + 8, 0.3)
bheemu.move(Y - 8, Y, 'out', rot=6, armR=(140, -150)); bheemu.move(Y, Y + 3, 'snap', rot=-22, armR=(40, -60)); bheemu.move(Y + 3, Y + 12, 'elastic', rot=-8, armR=(110, -120))
sc.hit(Y, 'whoosh', 1.0, d=0.3)
gaju.move(Y, Y + 8, 'in', x=2200, y=G0 - 1410, rot=40)
HIT = Y + 8
gaju.set(HIT, sx=1.3, sy=0.78); gaju.move(HIT + 2, HIT + 12, 'elastic', sx=1.0, sy=1.0, rot=0); gaju.move(HIT + 2, HIT + 16, 'out', x=1800, y=G0 - 1300)
sc.hit(HIT, 'crash', 1.0); sc.hit(HIT, 'bonk', 1.0, note=55); ep.tap(HIT, 'dha', 1.4); st.shake(HIT, 30, 12); stars(st, HIT, 2240, G0 - 1420, n=8, r=230, life=14)
rk.set(HIT, x=2280, y=G0 - 1420); arc(rk, HIT, HIT + 22, 2900, G0 - 300, 200, spin=1200); sc.slide(HIT + 2, 86, 50, 20, 0.5)

# ------------------------------------------------------------------ 5. we won! ...oh
V = HIT + 18
sc.raga(V, V + 110, 'sweet', v=0.9)
face(gaju, V, 4, **HAPPY); face(bheemu, V, 4, pitch=0.0, rot=0, **HAPPY)
chintu.move(V, V + 4, 'over', rot=0, armL=(-40, -210), armR=(40, -210), handL='open', handR='open', pitch=-0.4, **LAUGH)
speak(ep, chintu, V + 4, 'c_won')                                                              # "We won!"
hop(chintu, V + 6, 70); hop(chintu, V + 24, 70)
D = V + 40
bheemu.move(D, D + 3, 'snap', armR=(60, -250), armL=(-20, -250), handR='open', handL='open'); sc.hit(D + 3, 'pop', 0.9, note=67)     # he lets go to clap
for f in (D + 8, D + 16):
    bheemu.move(f, f + 2, 'snap', armR=(30, -250), armL=(10, -250)); bheemu.move(f + 3, f + 6, 'out', armR=(60, -250), armL=(-20, -250)); sc.hit(f + 2, 'pop', 0.7, note=72)
LINE.append((D + 3, None, None, None))
gaju.move(D + 6, D + 30, 'out', y=G0 - 1500); gaju.move(D + 8, D + 10, 'snap', **SHOCK); sc.slide(D + 6, 70, 90, 22, 0.4)
for a in (bheemu, chintu):
    a.move(D + 24, D + 26, 'snap', pitch=-0.8, pupil=(0.3, -0.9), **SHOCK)
bheemu.move(D + 26, D + 30, 'io', armR=(0, 0), armL=(0, 0), handR='mitt', handL='mitt', face=0.0, yaw=0.0)
gaju.move(D + 34, D + 37, 'snap', brow_asym=1.0, smile=0.9, eye_pop=1.0, mouth_open=0.0, brow=8); sc.hit(D + 34, 'ghatam', 0.8, note=79)     # wait. I have ears.
tx, ty = st.probe(D + 60, bheemu, 'top')
for fb in flap(gaju, D + 38, D + 72, 4):
    sc.hit(fb, 'flap', 0.5)
gaju.set(D + 40, z=5); gaju.move(D + 40, D + 68, 'io', x=tx, y=ty + 34); sc.slide(D + 40, 88, 62, 28, 0.4)
bheemu.set(D + 68, head_sy=0.8, head_sx=1.14, head_dy=14); bheemu.move(D + 70, D + 78, 'elastic', head_sy=1.0, head_sx=1.0, head_dy=0); sc.hit(D + 68, 'pop', 0.8, note=60)
face(gaju, D + 68, 3, ear=0.0, brow_asym=0.0, **HAPPY)
for a in (bheemu, chintu):
    face(a, D + 70, 4, pitch=0.0, pupil=(0, 0), **HAPPY)
laugh(ep, chintu, D + 74, D + 96, 88)
END = D + 96
ep.close(END, tx, ty - 60)
print('frames needed', END + 34)

if __name__ == '__main__':
    ep.main(__file__)
