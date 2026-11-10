"""Bheemu & Gaju, episode 5: "One Umbrella"  (about 29 s, vertical, silent)

Rain in Chinna Veedhi. One umbrella, two friends. Sharing fails, riding on Bheemu's head fails, Gaju's ears
work until he sneezes, and then an auto finds the puddle. They give up and sail paper boats, and Laddu
floats past, dry, in the lost umbrella.
"""
import os, sys, math
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', 'engine'))
from toon import GROUND, poly, smooth
from chars import Bheemu, Gaju
from cast import Laddu
from scene import Painted, Prop, puffs, stars, zip_lines
from sets import lane, auto
from acting import blink, look, bob, walk, squash, take, shake, arc, flap
from sound import veena, bansuri, xylo
from show import Show, face, laugh, enter, umbrella, rain, splash, CALM, HAPPY, LAUGH, ANGRY, SHOCK, SORRY, SLY

G0 = GROUND
ep = Show(5, 'One Umbrella', 'one_umbrella', 696, Painted(3000, lane, top=(120, 134, 156), bottom=(104, 96, 96)))
st, sc, cam = ep.st, ep.sc, ep.cam
BX = 1270


def boat(g, p, f):
    g.shape(poly([(-44, -14), (44, -14), (26, 8), (-26, 8)]), (255, 255, 250))
    g.shape(poly([(0, -52), (20, -14), (-20, -14)]), (255, 255, 250))


bheemu = Bheemu(x=500, z=3)
gaju = Gaju(x=420, z=2, show=0.0)
laddu = Laddu(x=0, z=8, show=0.0, lid=0.4, smile=0.9)
umb = Prop(umbrella, x=0, y=0, z=3.4, open=1.0, flip=0.0)
parked = Prop(auto, x=830, y=G0 - 30, z=0.2, sx=0.9, sy=0.9)
racer = Prop(auto, x=-400, y=G0 + 150, z=7, show=0.0)
boats = [Prop(boat, x=0, y=0, z=7.5, show=0.0) for _ in range(2)]
st.add(parked, gaju, bheemu, umb, laddu, racer, *boats)
ep.shot(0, 1300, 0.95, cut=False)
rain(st, 30, 700)
WET = dict(sweat=1.0)

# ------------------------------------------------------------------ 1. one umbrella  (36-110)
sc.raga(36, 176, 'calm', v=0.8); sc.hit(38, 'timp', 0.7, note=36)
bheemu.set(0, armR=(40, -150), handR='grip', bendR=0.5, face=1, yaw=0.7, smile=0.8)
umb.attach(0, 204, bheemu, 'handR', 0, 10)
enter(ep, bheemu, 38, 76, 520, BX, 10, 32, 'ge', 0.7)
bheemu.move(76, 80, 'over', face=0.0, yaw=0.0); bob(bheemu, 80, 110)
gaju.set(60, ear=-0.8, brow_ang=-16, smile=-0.4, **WET)
enter(ep, gaju, 62, 96, 560, 1020, 8, 26, 'na', 0.4)
shake(gaju, 98, 108, 3); look(gaju, 98, yaw=0.5, pupil=(0.7, -0.8))

# ------------------------------------------------------------------ 2. yours, mine, yours, mine  (110-176)
look(bheemu, 110, yaw=-0.5, pupil=(-0.7, 0.6))


def tilt(f, to_gaju, n=4):
    umb.move(f, f + n, 'over', rot=-30 if to_gaju else 0)
    bheemu.move(f, f + n, 'over', armR=(-60, -160) if to_gaju else (40, -150), sweat=1.0 if to_gaju else 0.0, smile=-0.4 if to_gaju else 0.6)
    gaju.move(f, f + n, 'over', sweat=0.0 if to_gaju else 1.0, smile=0.9 if to_gaju else -0.4, ear=0.0 if to_gaju else -0.8, brow_ang=0 if to_gaju else -16)
    sc.hit(f, 'ghatam', 0.7, note=62 if to_gaju else 57)


for f, g_ in ((116, True), (134, False), (146, True), (154, False), (160, True), (165, False), (169, True), (172, False)):
    tilt(f, g_, 4 if f < 150 else 3)
face(bheemu, 176, 3, yaw=-0.6, **ANGRY); face(gaju, 176, 3, ear=0.0, **ANGRY)

# ------------------------------------------------------------------ 3. upstairs  (182-262)
sc.raga(182, 372, 'sneak')
gaju.move(184, 187, 'snap', brow=10, brow_asym=1.0, smile=0.9, brow_ang=0, lid=0.0); sc.hit(184, 'ghatam', 0.8, note=76)
tx, ty = st.probe(182, bheemu, 'top')
gaju.set(190, z=5)
for fb in flap(gaju, 188, 208, 4):
    sc.hit(fb, 'flap', 0.5)
gaju.move(190, 200, 'io', y=ty - 60, x=BX); gaju.move(200, 205, 'in', y=ty + 34, face=0.0, yaw=0.0); sc.slide(190, 60, 80, 10, 0.4)
bheemu.set(205, head_sy=0.8, head_sx=1.14, head_dy=14); bheemu.move(207, 214, 'elastic', head_sy=1.0, head_sx=1.0, head_dy=0); sc.hit(205, 'pop', 0.8, note=60)
face(bheemu, 196, 3, yaw=0.0, pupil=(0, -0.9), brow_ang=0, lid=0.0, smile=0.0)
gaju.move(206, 210, 'over', trunk=(70, -40), trunk_curl=-0.5, **HAPPY)
umb.attach(204, 232, gaju, 'trunk', 0, 40); umb.set(204, rot=0, z=5.5)
bheemu.move(206, 212, 'io', armR=(0, 0), handR='mitt', bendR=0.14, pupil=(0, 0), **HAPPY)
W0 = 226                                                                                     # the wind has other plans
sc.hit(W0, 'whoosh', 1.0, d=0.6); zip_lines(st, W0, 700, G0 - 700, 1, life=12, length=500, h=500)
umb.set(W0 + 4, flip=1.0); sc.hit(W0 + 4, 'pop', 1.0, note=55)
for a in (gaju, bheemu):
    a.move(W0 + 4, W0 + 6, 'snap', **SHOCK)
gaju.move(W0 + 4, W0 + 8, 'out', trunk=(120, -120), sx=0.9, sy=1.15)
ux, uy = st.probe(W0 + 6, gaju, 'trunk')
umb.set(W0 + 6, x=ux, y=uy + 40); arc(umb, W0 + 6, W0 + 22, 2400, G0 - 1300, 100, spin=500)
gaju.move(W0 + 8, W0 + 16, 'elastic', sx=1.0, sy=1.0, trunk=(30, 60), trunk_curl=0.7)
for a in (gaju, bheemu):
    look(a, W0 + 12, yaw=0.8, pupil=(0.9, -0.5)); face(a, W0 + 26, 4, yaw=0.0, pupil=(0, 0), ear=-0.6 if a is gaju else 0, **SORRY) if a is gaju else face(a, W0 + 26, 4, yaw=0.0, pupil=(0, 0), **SORRY)

# ------------------------------------------------------------------ 4. ears  (262-360)
E = 262
gaju.move(E, E + 3, 'snap', brow=10, brow_asym=1.0, smile=0.9, brow_ang=0, sweat=0.0); sc.hit(E, 'ghatam', 0.8, note=78)
gaju.move(E + 8, E + 12, 'over', ear=1.0, sx=1.5, brow=0, brow_asym=0.0); sc.slide(E + 8, 62, 76, 4, 0.4); sc.hit(E + 12, 'pop', 0.7, note=67)
face(bheemu, E + 16, 4, pupil=(0, -0.8), **HAPPY); bheemu.move(E + 26, E + 30, 'io', pupil=(0, 0))
for f in (E + 44, E + 52):                                                                    # a tickle in the trunk...
    gaju.move(f, f + 2, 'snap', trunk=(40, 40)); gaju.move(f + 2, f + 6, 'over', trunk=(30, 60)); sc.hit(f, 'sniff', 0.9)
gaju.move(E + 58, E + 66, 'out', pitch=-0.8, eye_open=0.0, mouth_open=0.8, trunk=(20, -90), trunk_curl=-0.8, sy=1.12); sc.slide(E + 58, 60, 84, 8, 0.4)
S = E + 68
sc.duck(S - 8, S + 30, 0.3)
gaju.move(S, S + 2, 'snap', pitch=0.6, trunk=(10, 150), trunk_curl=0.0, mouth_open=0.2, sy=0.86, sx=1.6)
hx, hy = st.probe(S, bheemu, 'head')
splash(st, S + 1, hx, hy + 40, n=12, life=14); splash(st, S + 2, hx, hy + 120, n=9, life=14)
sc.hit(S, 'crash', 0.7); sc.hit(S, 'boing', 0.8, note=60); st.shake(S, 16, 8)
bheemu.set(S + 1, sx=1.14, sy=0.9, eye_open=0.0, happy=0.0, smile=-0.4, glasses_rot=12, glasses_dy=8, sweat=1.0); bheemu.move(S + 3, S + 12, 'elastic', sx=1.0, sy=1.0)
gaju.move(S + 4, S + 12, 'elastic', sy=1.0, sx=1.0, pitch=0.0, ear=0.0, trunk=(30, 60), trunk_curl=0.7); face(gaju, S + 12, 3, **SORRY)
face(bheemu, S + 18, 4, glasses_rot=0, glasses_dy=0, **ANGRY)
arc(gaju, S + 26, S + 38, BX + 200, G0, 140); gaju.set(S + 38, z=3.5); squash(gaju, S + 38, 0.25, 8); sc.hit(S + 38, 'pop', 0.6, note=55)

# ------------------------------------------------------------------ 5. the auto and the puddle
A = S + 52
sc.duck(A, A + 40, 0.25)
sc.note(A, bansuri, 84, 0.12, 0.8); sc.note(A + 6, bansuri, 84, 0.12, 0.8)                    # peep peep
for a in (gaju, bheemu):
    look(a, A + 10, yaw=-0.9, pupil=(-0.9, 0)); a.move(A + 12, A + 14, 'snap', **SHOCK)
gaju.move(A + 14, A + 22, 'out', y=G0 - 520)
for fb in flap(gaju, A + 12, A + 76, 4):
    sc.hit(fb, 'flap', 0.4)
H = A + 24
racer.set(H - 1, show=1.0, x=200); racer.move(H, H + 7, 'lin', x=2400); sc.hit(H, 'zip', 1.0, d=0.3)
for k in range(3):
    splash(st, H + 3 + k, BX - 60 + k * 50, G0 + 40, n=14, life=18)
bheemu.set(H + 4, sx=1.25, sy=0.8, face=0.0, yaw=0.0, eye_open=0.0, eye_pop=1.0, mouth_open=0.0, smile=-0.5, brow=0, brow_ang=0, glasses_rot=-14, glasses_dy=12, sweat=1.0)
bheemu.move(H + 6, H + 16, 'elastic', sx=1.0, sy=1.0)
sc.hit(H + 4, 'crash', 1.0); ep.tap(H + 4, 'dha', 1.4); sc.hit(H + 4, 'timp', 1.0, note=36); st.shake(H + 4, 34, 12)
bheemu.move(H + 30, H + 33, 'snap', mouth_open=0.4, mouth_w=0.5); splash(st, H + 32, BX + 30, G0 - 470, n=5, life=10); sc.hit(H + 32, 'pop', 0.6, note=64)   # spits out a little fountain
bheemu.move(H + 38, H + 40, 'snap', mouth_open=0.0, mouth_w=1.0); blink(bheemu, H + 44)
gaju.move(H + 30, H + 40, 'in', y=G0, yaw=-0.6, pupil=(-0.8, 0)); squash(gaju, H + 40, 0.25, 8)
laugh(ep, gaju, H + 44, H + 70)
face(bheemu, H + 50, 4, yaw=0.6, pupil=(0.8, 0.2), glasses_rot=0, glasses_dy=0, **ANGRY)

# ------------------------------------------------------------------ 6. if you can't beat the rain
P = H + 78
sc.raga(P, P + 150, 'sweet', v=0.9)
face(gaju, P - 6, 4, **SORRY)
bheemu.move(P, P + 8, 'io', yaw=0.0, pupil=(0.3, 0.8), brow_ang=0, lid=0.0, smile=0.2)        # looks at the puddle. Oh well.
bheemu.move(P + 12, P + 16, 'in', sy=0.82, sx=1.1); bheemu.set(P + 16, sit=1.0); bheemu.move(P + 16, P + 26, 'elastic', sy=1.0, sx=1.0)
splash(st, P + 16, BX, G0 + 20, n=8, life=10); sc.hit(P + 16, 'pop', 0.8, note=50)
PX_, PY_ = 1260, G0 + 176
bheemu.move(P + 28, P + 32, 'over', armR=(70, -120), handR='grip', **HAPPY)
boats[0].set(P + 32, show=1.0); boats[0].attach(P + 32, P + 44, bheemu, 'handR', 0, -30); sc.hit(P + 32, 'pop', 0.7, note=76)
bx_, by_ = st.probe(P + 44, bheemu, 'handR')
boats[0].set(P + 44, x=bx_, y=by_ - 30); arc(boats[0], P + 44, P + 56, PX_ - 60, PY_, 80)
bheemu.move(P + 46, P + 52, 'io', armR=(0, 0), handR='mitt')
gaju.move(P + 40, P + 44, 'over', trunk=(-40, -30), trunk_curl=-0.4, **HAPPY)
boats[1].set(P + 46, show=1.0); boats[1].attach(P + 46, P + 58, gaju, 'trunk', 0, -10); sc.hit(P + 46, 'pop', 0.7, note=81)
gx_, gy_ = st.probe(P + 58, gaju, 'trunk')
boats[1].set(P + 58, x=gx_, y=gy_ - 10); arc(boats[1], P + 58, P + 70, PX_ + 70, PY_ + 6, 60)
gaju.move(P + 60, P + 66, 'io', trunk=(30, 60), trunk_curl=0.7)
for i, b in enumerate(boats):
    f0 = P + 56 + i * 14
    for f in range(f0, 700, 2):
        b.set(f, x=(PX_ - 60 + i * 130) + (f - f0) * 0.5, rot=math.sin(f * 0.2 + i) * 6)
U = P + 84                                                                                    # and who is the only dry one in the lane?
umb.set(U, show=1.0, flip=0.0, rot=180, z=7.8, x=560, y=G0 - 60); umb.move(U, U + 90, 'lin', x=2000)
laddu.set(U, show=1.0); laddu.attach(U, 700, umb, 'c', 0, 300)
for f in range(U, U + 90, 12):
    umb.move(f, f + 6, 'io', rot=176); umb.move(f + 6, f + 12, 'io', rot=184)
for a in (bheemu, gaju):
    a.move(U + 20, U + 24, 'over', happy=0.0, eye_open=1.0, yaw=-0.5, pupil=(-0.8, 0.6), smile=0.0, mouth_w=1.0)
    a.move(U + 24, U + 60, 'lin', yaw=0.5, pupil=(0.8, 0.6))
    blink(a, U + 62)
sc.note(U + 24, veena, 62, 0.6, 0.7)
laugh(ep, gaju, U + 68, U + 92); laugh(ep, bheemu, U + 70, U + 92, 72)
END = U + 92
ep.close(END, BX + 90, G0 - 300)
print('frames needed', END + 34)

if __name__ == '__main__':
    ep.main(__file__)
