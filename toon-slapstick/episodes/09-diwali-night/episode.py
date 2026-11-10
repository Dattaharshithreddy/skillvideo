"""Bheemu & Gaju, episode 9: "Diwali Night"  (about 21 s, vertical, silent; the humans speak)

Lamps everywhere. The cracker box says "Keep away!". Gaju lights one flowerpot; it tips over and chases
Bheemu up and down the courtyard, then takes him up with it. He comes down by scarf under the fireworks,
and they finish with a sparkler.
"""
import os, sys, math
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', 'engine'))
import skia
from toon import GROUND, W, H, poly, oval
from chars import Bheemu, Gaju
from cast import Ammamma, Chintu
from scene import Painted, Prop, rect, puffs, stars
from india import telugu
from sets import courtyard, NIGHT
from acting import blink, look, bob, walk, squash, take, shake, flap, arc
from sound import veena, bansuri, xylo
from voice import speak
from show import Show, face, hop, enter, diya, rocket, sparks, CALM, HAPPY, LAUGH, ANGRY, SHOCK, SORRY, SLY

G0 = GROUND
ep = Show(9, 'Diwali Night', 'diwali_night', 498, Painted(2800, lambda g, w: courtyard(g, w, True), top=(14, 16, 48), bottom=(56, 50, 80)))
st, sc, cam = ep.st, ep.sc, ep.cam
INK = (58, 42, 40)


def banner(g, p, f):                                    # "Happy Diwali"
    g.shape(rect(-380, -60, 760, 120, 10), (126, 30, 44), True, 5, (250, 208, 80))
    telugu(g, 'దీపావళి శుభాకాంక్షలు', 0, 22, 62, (255, 214, 90), 'Ramabhadra')


def box(g, p, f):                                       # the cracker box: "Keep away!"
    g.shape(rect(-90, -110, 180, 110, 8), (214, 60, 56), True, 5, INK)
    g.shape(rect(-76, -92, 152, 56, 4), (255, 240, 200), True, 3, INK)
    telugu(g, 'దూరంగా ఉండండి!', 0, -54, 22, (170, 30, 40), 'Ramabhadra')
    for i in range(3):
        g.shape(poly([(-50 + i * 50, -110), (-40 + i * 50, -150), (-30 + i * 50, -110)]), (250, 208, 80), True, 3, INK)


def sparkler(g, p, f):
    g.shape(poly([(0, 0), (0, -120)], False), None, True, 5, (150, 150, 160))
    for i in range(9):
        a = math.radians(i * 40 + f * 37)
        L = 26 + 18 * math.sin(f * 1.7 + i)
        g.shape(poly([(0, -120), (math.cos(a) * L, -120 + math.sin(a) * L)], False), None, True, 4, (255, 236, 150) if i % 2 else (255, 180, 90))
    g.soft(oval(0, -120, 46, 46), (255, 220, 120), 18, 0.7)
    return {'tip': (0, -120)}


bheemu = Bheemu(x=1650, z=3, face=-0.2)
gaju = Gaju(x=2400, z=3.4, show=0.0)
chintu = Chintu(x=880, z=4, show=0.0)
amma = Ammamma(x=700, z=2, show=0.0)
bn = Prop(banner, x=1500, y=G0 - 1230, z=0)
bx = Prop(box, x=0, y=0, z=3.3, show=0.0, sx=1.5, sy=1.5)
rk = Prop(rocket, x=0, y=0, z=5, show=0.0, lit=0.0)
sp = Prop(sparkler, x=0, y=0, z=6, show=0.0)
lamps = [Prop(diya, x=1540 + i * 110, y=G0 + 70, z=5.5, show=0.0, sx=1.4, sy=1.4) for i in range(3)]
st.add(bn, amma, bheemu, gaju, bx, chintu, *lamps, rk, sp)
ep.shot(0, 1500, 0.85, cut=False)

# ------------------------------------------------------------------ 1. lamps and a warning  (36-140)
sc.raga(36, 180, 'sweet', v=0.9)
for i, f in enumerate((44, 58, 72)):
    bheemu.move(f - 4, f, 'over', armR=(20 + i * 60 - 60, 60), handR='open', pitch=0.5); bheemu.move(f + 2, f + 8, 'io', armR=(0, 0), pitch=0.0)
    lamps[i].set(f, show=1.0); sc.hit(f, 'pop', 0.6, note=72 + i * 3); sc.hit(f, 'manjira', 0.4)
face(bheemu, 82, 4, handR='mitt', **HAPPY)
chintu.set(36, armL=(-30, -200), armR=(30, -200), handL='open', handR='open', **LAUGH)
enter(ep, chintu, 36, 52, 860, 1090, 5, 30, 'na', 0.5)
speak(ep, chintu, 44, 'c_diwali')                                      # "Happy Diwali!"
hop(chintu, 56, 60); hop(chintu, 72, 60)
gaju.set(64, trunk=(40, 10), trunk_curl=0.9)
bx.set(64, show=1.0); bx.attach(64, 98, gaju, 'trunk', 0, 90)
enter(ep, gaju, 64, 92, 2350, 1960, 7, 26, 'na', 0.4)
gx, gy = st.probe(98, gaju, 'trunk')
bx.set(98, x=1960 - 150, y=G0); bx.set(99, z=3.3)
gaju.move(98, 102, 'over', trunk=(-60, 40), trunk_curl=0.5)
rk.set(106, show=1.0); rk.attach(106, 132, gaju, 'trunk', 0, 40); sc.hit(106, 'pop', 0.8, note=67)
gaju.move(106, 110, 'over', trunk=(-30, -30), trunk_curl=0.3, face=0.0, yaw=-0.3)
for f in (112, 120):
    gaju.move(f, f + 3, 'snap', brow=13, brow_asym=0.6); gaju.move(f + 4, f + 8, 'out', brow=0, brow_asym=0.0); sc.hit(f, 'ghatam', 0.6, note=74)
amma.set(96, armL=(0, 0), **CALM)
enter(ep, amma, 96, 112, 760, 960, 8, 28, 'na', 0.4)
amma.move(114, 118, 'over', armR=(60, -190), handR='point', brow_ang=14)
e = speak(ep, amma, 116, 'a_careful')                                   # "Careful, children!"
amma.move(e, e + 4, 'io', armR=(0, 0), handR='mitt', brow_ang=0)

# ------------------------------------------------------------------ 2. one little flowerpot  (132-190)
RX = 1840
gaju.move(128, 132, 'over', trunk=(-110, 80), trunk_curl=0.0); rk.set(132, x=RX, y=G0 + 20, rot=0)
gaju.move(134, 138, 'over', trunk=(-110, 20)); L = 142
rk.set(L, lit=1.0); sc.hit(L, 'pop', 0.8, note=84); sc.hit(L, 'whoosh', 0.5, d=1.6)
gaju.move(L, L + 3, 'snap', trunk=(30, 60), trunk_curl=0.7, ear=-1.0, eye_open=0.3); gaju.move(L + 2, L + 14, 'out', x=2010)
look(bheemu, L + 4, yaw=0.6, pupil=(0.8, 0.4)); face(bheemu, L + 6, 4, eye_open=1.0, happy=0.0, smile=0.9)
for i, f in enumerate(range(L + 18, L + 30, 3)):
    rk.set(f, rot=(12 if i % 2 else -12) * (1 + i * 0.4)); sc.hit(f, 'ghatam', 0.6, note=60 + i * 2)
T = L + 32
rk.move(T - 2, T, 'in', rot=-90, y=G0 - 20); sc.hit(T, 'bonk', 0.6, note=58)
f = take(st, bheemu, T + 2, 0.8, hold=4)

# ------------------------------------------------------------------ 3. the chase  (188-262)
C = T + 16
sc.raga(C, C + 80, 'chase')


def run(a, f0, f1, x0, x1, y=G0, **kw):
    d = 1 if x1 > x0 else -1
    a.set(f0, show=1.0, x=x0, y=y, wheel=1.0, stride=38, rot=14 * d, face=d, yaw=d, sx=1, sy=1, **kw)
    a.move(f0, f1, 'lin', x=x1, step=a.value('step', f0) + (f1 - f0) / 3)


def fly(f0, f1, x0, x1):
    d = 1 if x1 > x0 else -1
    rk.set(f0, x=x0, y=G0 - 30, rot=90 * d); rk.move(f0, f1, 'lin', x=x1); sc.hit(f0, 'zip', 0.8, d=0.3)


run(bheemu, C, C + 12, 1650, 500, scarf_fly=1.0, armR=(-90, -150), armL=(-120, -130), handR='open', handL='open', **SHOCK); fly(C + 2, C + 14, RX, 500)
run(bheemu, C + 22, C + 32, 500, 2500); fly(C + 24, C + 34, 500, 2500)
run(bheemu, C + 42, C + 50, 2500, 500); fly(C + 43, C + 51, 2500, 500)
for a in (chintu, amma, gaju):
    a.move(C + 2, C + 4, 'snap', **SHOCK)
    for f, d in ((C + 4, -1), (C + 24, 1), (C + 43, -1)):
        look(a, f, yaw=0.8 * d, pupil=(0.9 * d, 0))
hop(chintu, C + 26, 120, 6); hop(gaju, C + 46, 100, 6); gaju.move(C + 6, C + 10, 'over', ear=0.0, eye_open=1.0)
U = C + 60                                                              # fourth lap: it catches up
run(bheemu, U, U + 6, 500, 1300); fly(U + 1, U + 6, 500, 1300)
bheemu.set(U + 6, wheel=0.0, stride=0.0, rot=0, face=0.0, yaw=0.0, armR=(70, -200), armL=(-70, -200)); rk.set(U + 6, rot=0, y=G0, z=2.5)
bheemu.move(U + 6, U + 16, 'in', y=G0 - 1700); rk.move(U + 6, U + 16, 'in', y=G0 - 1640)
sc.slide(U + 6, 55, 96, 12, 0.7); sc.hit(U + 6, 'whoosh', 1.0, d=0.5); puffs(st, U + 6, 1300, G0, n=6, size=50, spread=120, life=14)
for a in (chintu, amma, gaju):
    a.move(U + 8, U + 11, 'over', yaw=0.0, pitch=-0.8, pupil=(0.3, -0.9), mouth_open=0.3)
sc.duck(U + 14, U + 30, 0.0)

# ------------------------------------------------------------------ 4. boom
B = U + 30
bheemu.set(B - 1, show=0.0); rk.set(B - 1, show=0.0)
for i, (dx, dy, d) in enumerate(((0, -1260, 0), (-260, -1120, 6), (250, -1330, 11))):
    sparks(st, B + d, 1450 + dx, G0 + dy, n=20, life=24, r=440 - i * 60)
sc.hit(B, 'crash', 1.0); sc.hit(B, 'timp', 1.0, note=36); ep.tap(B, 'dha', 1.4); st.shake(B, 30, 12); sc.hit(B + 6, 'crash', 0.6); sc.hit(B + 11, 'crash', 0.6)
st.overlays.append(lambda g, f: g.c.drawRect(skia.Rect(0, 0, W, H), skia.Paint(Color=skia.Color(255, 250, 230, 200 if f == B else 90))) if f in (B, B + 1) else None)
for i, f in enumerate(range(B + 30, 498, 17)):                           # the rest of the town joins in
    sparks(st, f, 1000 + (i * 397) % 900, G0 - 1150 - (i * 131) % 300, n=14, life=20, r=260 + (i % 3) * 60); sc.hit(f, 'pop', 0.5, note=50 + (i % 4) * 3)
sc.raga(B + 14, B + 200, 'sweet', v=0.9)
D = B + 18                                                               # down by scarf
bheemu.set(D, show=1.0, x=1500, y=G0 - 1700, sx=1, sy=1, scarf_fly=1.0, armR=(40, -330), armL=(-40, -330), handR='grip', handL='grip', eye_open=1.0, eye_pop=1.0, pupil_s=0.5,
           mouth_open=0.2, mouth_w=0.7, brow=0, glasses_rot=14, glasses_dy=8, smile=-0.2)
for i, f in enumerate(range(D, D + 60, 12)):
    bheemu.move(f, f + 12, 'io', x=1500 + (70 if i % 2 == 0 else -70), rot=8 if i % 2 == 0 else -8)
bheemu.move(D, D + 60, 'lin', y=G0); sc.slide(D, 84, 60, 60, 0.3)
for a in (chintu, amma, gaju):
    a.move(D + 6, D + 60, 'lin', pitch=0.0, pupil=(0.4, 0), mouth_open=0.0)
S = D + 60
bheemu.set(S, sit=1.0, rot=0, x=1500, scarf_fly=0.0, armR=(0, 0), armL=(0, 0), handR='mitt', handL='mitt', sx=1.25, sy=0.75); bheemu.move(S + 2, S + 12, 'elastic', sx=1.0, sy=1.0)
sc.hit(S, 'timp', 0.8, note=38); puffs(st, S, 1500, G0, n=5, size=40, spread=150, life=14)
blink(bheemu, S + 14)

# ------------------------------------------------------------------ 5. a sparkler for the pilot
for f in walk(gaju, S + 8, S + 30, 1740, 8, 26):
    ep.tap(f, 'na', 0.4)
gaju.set(S + 8, ear=-0.4, trunk=(-40, -40), trunk_curl=-0.2, **SORRY)
sp.set(S + 8, show=1.0); sp.attach(S + 8, S + 44, gaju, 'trunk', 0, 0)
face(bheemu, S + 20, 4, yaw=0.6, pupil=(0.8, 0), pupil_s=1.0, glasses_rot=0, glasses_dy=0, **ANGRY)
gaju.move(S + 30, S + 38, 'over', trunk=(-120, -70), trunk_curl=-0.3)
bheemu.move(S + 40, S + 44, 'over', armR=(120, -110), handR='grip'); sp.attach(S + 44, 900, bheemu, 'handR', 0, 10)
gaju.move(S + 44, S + 50, 'io', trunk=(30, 60), trunk_curl=0.7)
face(bheemu, S + 50, 6, brow_ang=0, lid=0.0, smile=0.6); face(bheemu, S + 60, 4, **HAPPY)
face(gaju, S + 56, 4, ear=0.2, **HAPPY)
for a in (chintu, amma):
    face(a, S + 50, 4, yaw=0.5, **HAPPY)
trail = []


def glow(g, f):
    t = sp.anchors.get('tip')
    if f >= S + 60 and t:
        trail.append(t)
        pts = trail[-26:]
        for i in range(1, len(pts)):
            g.shape(poly([pts[i - 1], pts[i]], False), None, True, 3 + 7 * i / len(pts), (255, 226, 130), a=i / len(pts))


st.fx.append(glow)
for i, f in enumerate(range(S + 60, S + 108, 3)):                       # he draws a circle of light
    a = i * 0.8
    bheemu.move(f, f + 3, 'lin', armR=(110 + math.cos(a) * 70, -210 + math.sin(a) * 70))
    if i % 2 == 0:
        sc.note(f, xylo, 86 + (i % 5), 0.12, 0.3)
END = S + 104
ep.close(END, 1620, G0 - 300)
print('frames needed', END + 34)

if __name__ == '__main__':
    ep.main(__file__)
