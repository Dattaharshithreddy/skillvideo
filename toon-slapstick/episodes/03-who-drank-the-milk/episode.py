"""Bheemu & Gaju, episode 3: "Who Drank the Milk?"  (about 30 s, vertical, silent; lines on boards)

Ammamma leaves a pot of milk and puts Bheemu on guard. Each time he looks away, Laddu laps from one
side and Gaju's trunk drinks from the other. Ammamma returns to an empty pot, the thieves point at
Bheemu, and two milk moustaches give them away.
"""
import os, sys, math
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', 'engine'))
from toon import GROUND, smooth, oval, poly
from chars import Bheemu, Gaju
from cast import Ammamma, Laddu
from scene import Painted, Prop, table, rect, puffs, stars, marks
from india import illu, telugu
from acting import blink, look, bob, walk, squash, take, shake, chew
from sound import veena, bansuri, xylo
from voice import speak
from show import Show, face, laugh, enter, ladle, milkpot, CALM, HAPPY, LAUGH, ANGRY, SHOCK, SORRY, SLY

G0 = GROUND
ep = Show(3, 'Who Drank the Milk?', 'who_drank_the_milk', 722, Painted(3400, illu))
st, sc, cam = ep.st, ep.sc, ep.cam
TX, TS, TOP = 800, 1.15, G0 - 224
PX = TX - 110


def tash(g, p, f):                                      # a milk moustache
    g.shape(smooth([(-22, 0), (-10, -8), (0, -3), (10, -8), (22, 0), (10, 7), (0, 3), (-10, 7)], True, 0.6), (255, 255, 250), True, 3, (150, 150, 170))


def tumbler(g, p, f):
    g.shape(poly([(-20, 0), (20, 0), (26, -56), (-26, -56)]), (206, 212, 220))
    g.shape(oval(0, -56, 26, 7), (255, 255, 250), True, 3)


bheemu = Bheemu(x=400, z=3, face=0.3, yaw=0.7)
amma = Ammamma(x=1090, z=3, face=-1, yaw=-0.7)
laddu = Laddu(x=850, y=G0, z=-1, show=0.0, lid=0.3)
gaju = Gaju(x=1000, y=G0, z=-0.5, show=0.0, sy=0.7, sx=0.8)
tbl = Prop(table, x=TX, y=G0, z=0, sx=TS)
pot = Prop(milkpot, x=PX, y=TOP, z=1, level=1.0)
ldl = Prop(ladle, x=0, y=0, z=3.5, show=0.0)
t1, t2 = Prop(tash, x=0, y=0, z=0.5, show=0.0), Prop(tash, x=0, y=0, z=0.6, show=0.0, sx=0.8, sy=0.8)
def note(g, p, f):                                      # Ammamma's notice, pinned to the tablecloth
    g.shape(rect(-150, -150, 300, 150, 6), (255, 250, 220), True, 4, (58, 42, 40))
    g.shape(oval(0, -150, 9, 9), (214, 60, 56), True, 3, (58, 42, 40))
    telugu(g, 'ముట్టుకుంటే', 0, -100, 40, (170, 30, 40), 'Ramabhadra')
    telugu(g, 'చెంప పగులుద్ది!', 0, -54, 40, (170, 30, 40), 'Ramabhadra')
    telugu(g, '- అమ్మమ్మ', 80, -16, 28, (90, 60, 60), 'Mallanna')


notice = Prop(note, x=TX + 30, y=G0 - 24, z=0.4, rot=-3)
cups = [Prop(tumbler, x=0, y=0, z=6, show=0.0) for _ in range(3)]
st.add(gaju, laddu, tbl, notice, pot, t1, t2, bheemu, amma, ldl, *cups)
ep.shot(0, 770, 1.05, cut=False)


def level(f0, f1, a, b):
    for f in range(f0, f1 + 1, 2):
        pot.set(f, level=a + (b - a) * (f - f0) / max(1, f1 - f0))


def cat_up(f):
    laddu.set(f, show=1.0, y=G0); laddu.move(f, f + 5, 'over', y=G0 - 190, pupil=(-0.9, 0), head_dx=0, head_rot=0)


def cat_down(f):
    laddu.move(f, f + 3, 'in', y=G0, head_dx=0, head_rot=0, head_dy=0); laddu.set(f + 3, show=0.0)


def cat_lap(f0, n):
    laddu.move(f0 - 4, f0, 'over', head_dx=-66, head_rot=-18, pupil=(-0.5, 0.8))
    for i in range(n):
        f = f0 + i * 6
        laddu.move(f, f + 3, 'out', head_dy=16); laddu.move(f + 3, f + 6, 'in', head_dy=0); sc.hit(f + 3, 'munch', 0.45)


def trunk_in(f):
    gaju.set(f - 1, show=1.0, y=G0 - 16, sy=0.7, sx=0.8, trunk=(0, 10), trunk_curl=0.2)
    hx, hy = st.probe(f, gaju, 'head')
    gaju.move(f, f + 8, 'out', trunk=(-20, -330), trunk_curl=-0.9); sc.slide(f, 55, 74, 8, 0.4)
    gaju.move(f + 12, f + 16, 'over', trunk=(PX + 20 - hx, TOP - 200 - hy), trunk_curl=1.0)


def trunk_out(f):
    gaju.move(f, f + 3, 'in', trunk=(0, 10), trunk_curl=0.2); gaju.set(f + 4, show=0.0); sc.hit(f, 'zip', 0.5, d=0.14)


# ------------------------------------------------------------------ 1. the order  (36-120)
sc.raga(36, 120, 'calm')
amma.move(40, 44, 'over', armL=(-60, -60), handL='point', brow_ang=14, pupil=(-0.5, 0.6))   # points at her notice: "Touch it and get a slap! - Ammamma"
for f in (52, 64):
    amma.move(f, f + 3, 'snap', armL=(-84, -44)); amma.move(f + 3, f + 8, 'over', armL=(-60, -60)); sc.hit(f, 'ghatam', 0.7, note=66)
bheemu.move(72, 75, 'snap', armR=(-52, -318), handR='open', sy=1.05, sx=0.97, brow=6, smile=0.2); ep.tap(74, 'dha', 1.1)   # salute
bheemu.move(96, 100, 'io', armR=(0, 0), handR='mitt', sy=1.0, sx=1.0, brow=0)
amma.move(108, 111, 'over', armL=(0, 0), handL='mitt', face=1, yaw=0.7, brow_ang=0)
for f in walk(amma, 112, 134, 1560, 7, 30):
    ep.tap(f, 'na', 0.5)
amma.set(135, show=0.0)

# ------------------------------------------------------------------ 2. the cat  (120-210)
sc.raga(120, 392, 'sneak')
bob(bheemu, 100, 262)
look(bheemu, 124, yaw=0.8, pupil=(0.8, 0.3)); look(bheemu, 140, yaw=-0.8, pupil=(-0.8, 0))
laddu.set(143, show=1.0, y=G0 + 60); laddu.move(144, 149, 'out', y=G0); sc.hit(145, 'ghatam', 0.6, note=72)       # two ears
cat_up(156); cat_lap(170, 3); level(170, 188, 1.0, 0.72)
cat_down(189); look(bheemu, 190, yaw=0.8, pupil=(0.9, 0.3))
face(bheemu, 196, 3, lid=0.3, brow_asym=1.0); blink(bheemu, 204); face(bheemu, 210, 3, lid=0.0, brow_asym=0.0)
look(bheemu, 214, yaw=-0.8, pupil=(-0.8, 0))

# ------------------------------------------------------------------ 3. the trunk  (218-340)
trunk_in(218)
for f in (238, 246, 254):
    sc.hit(f, 'gulp', 0.6); pot.set(f, sx=1.05, sy=0.96); pot.move(f + 1, f + 6, 'elastic', sx=1.0, sy=1.0)
level(236, 260, 0.72, 0.36)
trunk_out(263); look(bheemu, 265, yaw=0.8, pupil=(0.9, 0.3))
for f in walk(bheemu, 270, 282, 450, 12, 30):
    ep.tap(f, 'ge', 0.9)
bheemu.move(282, 286, 'over', pitch=0.7, head_dx=36, pupil=(0.6, 0.9))                   # peers into the pot
f = take(st, bheemu, 290, 0.7, hold=5); sc.note(293, veena, 50, 0.6, 0.9)
bheemu.move(f - 6, f, 'io', pitch=0.0, head_dx=0)
bheemu.move(338, 342, 'over', face=0.0, yaw=0.0, pupil=(0.2, -0.8), armR=(-40, -326), handR='open', brow_asym=1.0, smile=-0.2)   # scratches his head
for f in range(344, 380, 6):
    bheemu.move(f, f + 3, 'io', armR=(-58, -330)); bheemu.move(f + 3, f + 6, 'io', armR=(-34, -322)); sc.note(f, xylo, 74, 0.1, 0.3)

# ------------------------------------------------------------------ 4. both at once, right behind him  (346-400)
cat_up(346); cat_lap(356, 4); trunk_in(344)
for f in (362, 370, 378):
    sc.hit(f, 'gulp', 0.7); pot.set(f, sx=1.06, sy=0.95); pot.move(f + 1, f + 6, 'elastic', sx=1.0, sy=1.0)
level(356, 382, 0.36, 0.0)
sc.hit(383, 'gulp', 1.0)
cat_down(385); trunk_out(385)
bheemu.move(386, 389, 'snap', armR=(0, 0), handR='mitt', face=0.3, yaw=0.8, pupil=(0.8, 0.5), brow_asym=0.0)
blink(bheemu, 392)
f = take(st, bheemu, 398, 1.0); sc.hit(401, 'timp', 0.9); ep.tap(401, 'dha', 1.2)

# ------------------------------------------------------------------ 5. Ammamma is back  (416-520)
ep.push(404, 420, 810, 1.05)
amma.set(416, armR=(34, -130), handR='grip', **CALM)
ldl.set(416, show=1.0); ldl.attach(416, 900, amma, 'handR', 0, 20)
enter(ep, amma, 416, 440, 1500, 1160, 8, 30, 'dha', 0.9)
look(amma, 442, yaw=-0.6, pupil=(-0.7, 0.5)); face(amma, 446, 3, **SHOCK); face(amma, 456, 4, **ANGRY)
face(bheemu, 446, 4, yaw=0.7, pupil=(0.8, 0), **SORRY)
U = 484                                                                                 # two innocent helpers pop up and point
laddu.set(U, show=1.0, y=G0); laddu.move(U, U + 4, 'over', y=G0 - 190, pupil=(-0.8, 0), lid=0.0, smile=0.9); gaju.move(U + 2, U + 6, 'over', y=G0 - 150, yaw=-0.4, pupil=(-0.8, 0), smile=0.9)
gaju.set(U + 2, show=1.0, y=G0, sy=1.0, sx=1.0, trunk=(30, 60))
t1.set(U, show=1.0); t1.attach(U, 900, laddu, 'mouth', 0, -8); t2.set(U + 2, show=1.0); t2.attach(U + 2, 900, gaju, 'trunk', 0, 0)
sc.hit(U, 'pop', 0.8, note=72); sc.hit(U + 2, 'pop', 0.8, note=76)
laddu.move(U + 8, U + 11, 'snap', armL=(-90, -76)); gaju.move(U + 10, U + 13, 'snap', trunk=(-130, -30), trunk_curl=-1.0)
sc.hit(U + 8, 'ghatam', 0.9, note=62); sc.hit(U + 10, 'ghatam', 0.9, note=64)
bheemu.move(U + 16, U + 19, 'snap', armR=(-70, -200), handR='point', bendR=-0.5, **SHOCK)
amma.move(U + 22, U + 26, 'over', armR=(40, -270), yaw=-0.8, pupil=(-0.9, 0))            # up goes the ladle
sc.slide(U + 22, 60, 76, 6, 0.4); shake(bheemu, U + 26, U + 40, 5)

# ------------------------------------------------------------------ 6. the moustaches  (530-600)
M = U + 44
amma.move(M, M + 2, 'snap', pupil=(-0.3, 0.2)); sc.duck(M, M + 46, 0.3); sc.note(M, xylo, 88, 0.2, 0.7)
ep.push(M + 2, M + 14, 950, 1.5, up=150)
look(laddu, M + 16, pupil=(-0.9, 0)); look(gaju, M + 20, pupil=(0.9, 0), yaw=0.4)
for a in (laddu, gaju):
    a.move(M + 28, M + 30, 'snap', eye_pop=1.3, brow=10, smile=-0.2)
laddu.move(M + 28, M + 30, 'snap', armL=(0, 0)); gaju.move(M + 28, M + 30, 'snap', trunk=(30, 60), trunk_curl=0.7)
sc.hit(M + 29, 'timp', 0.7)
laddu.move(M + 36, M + 38, 'snap', mouth_open=0.5); laddu.move(M + 39, M + 41, 'snap', mouth_open=0.0); t1.set(M + 39, show=0.0); sc.hit(M + 38, 'munch', 0.8)   # licks it off, too late
face(laddu, M + 44, 4, **SORRY); face(gaju, M + 44, 4, **SORRY); sc.hit(M + 46, 'gulp', 1.0)

# ------------------------------------------------------------------ 7. a glass for everyone
E = M + 58
ep.push(E, E + 12, 800, 1.05)
amma.move(E + 2, E + 6, 'over', armR=(34, -130), yaw=-0.6, pupil=(-0.6, 0))
laugh(ep, amma, E + 8, E + 34, 76)
sc.raga(E + 8, E + 110, 'sweet', v=0.9)
face(bheemu, E + 10, 4, armR=(0, 0), handR='mitt', bendR=0.14, **CALM)
P = E + 38
bheemu.move(P, P + 4, 'over', armR=(46, -170), handR='grip', bendR=0.5, **HAPPY)
laddu.move(P + 4, P + 8, 'over', armL=(-10, -96), **HAPPY); gaju.move(P + 8, P + 12, 'over', trunk=(-10, -60), trunk_curl=0.9, **HAPPY)
for i, (a, anc, dy) in enumerate(((bheemu, 'handR', 16), (laddu, 'handL', 6), (gaju, 'trunk', 16))):
    cups[i].set(P + i * 4, show=1.0); cups[i].attach(P + i * 4, 900, a, anc, 0, dy); sc.hit(P + i * 4, 'pop', 0.8, note=74 + i * 3)
cups[0].set(P, sx=1.6, sy=1.6)
t2.set(P, show=0.0)
face(amma, P, 4, **HAPPY)
for f in range(P + 24, P + 54, 10):
    bheemu.move(f, f + 4, 'io', head_rot=-8, armR=(30, -230)); bheemu.move(f + 5, f + 9, 'io', head_rot=0, armR=(46, -170)); sc.hit(f + 3, 'gulp', 0.5)
END = P + 62
speak(ep, amma, 38, 'a_kapala')                                      # "Mind the milk! You are the guard."
speak(ep, amma, 458, 'a_evaru_palu')                                 # "Who drank the milk?"
speak(ep, amma, P + 16, 'a_jeetam')                                  # "Wages for guard duty!"
ep.close(END, 800, G0 - 330)
print('frames needed', END + 34)

if __name__ == '__main__':
    ep.main(__file__)
