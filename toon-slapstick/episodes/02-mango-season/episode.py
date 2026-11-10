"""Bheemu & Gaju, episode 2: "Mango Season"  (about 32 s, vertical, no dialogue)

The wall says "Do not pluck fruit here - Ammamma". One ripe mango hangs too high. Gaju tries his trunk,
a hop and his ears. Bheemu shakes the tree and gets every green mango on his head. The ripe one falls by
itself, Bujji takes it, and under the sign she shares it three ways. Ammamma arrives with her ladle.
Run:  python3 episode.py [preview|final|sheet f1,f2,... name.png]
"""
import os, sys, math
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', 'engine'))
from toon import GROUND, smooth, oval, poly
from chars import Bheemu, Gaju
from cast import Ammamma, Bujji
from scene import Painted, Prop, puffs, stars, marks
from india import mango
from sets import garden, SKY
from acting import blink, look, bob, walk, squash, take, shake, zip_off, chew, flap, arc
from sound import veena, bansuri, xylo
from voice import speak
from show import Show, face, hop, laugh, enter, ladle, word, CALM, HAPPY, LAUGH, ANGRY, SHOCK, SORRY, SLY

G0 = GROUND
ep = Show(2, 'Mango Season', 'mango_season', 846, Painted(2700, garden, top=SKY, bottom=(112, 136, 70)))
st, sc, cam = ep.st, ep.sc, ep.cam


def green(g, p, f):
    g.shape(smooth([(0, -52), (22, -40), (26, -12), (6, 2), (-16, -6), (-24, -28)], True, 0.7), (120, 176, 70))
    g.shape(oval(-8, -34, 7, 12), (176, 214, 110), False, a=0.7)


def slice_(g, p, f):
    g.shape(smooth([(-34, -8), (0, -26), (34, -8), (20, 12), (0, 18), (-20, 12)], True, 0.6), (252, 196, 50))
    g.shape(smooth([(-34, -8), (0, -26), (34, -8)], False), None, True, 5, (120, 170, 70))


MX, MY = 1640, G0 - 716                       # where the ripe mango hangs
gaju = Gaju(x=150, z=3, face=1, yaw=0.8)
bheemu = Bheemu(x=700, z=2, show=0.0)
bujji = Bujji(x=2600, z=4, show=0.0)
amma = Ammamma(x=-200, z=1, show=0.0)
ripe = Prop(mango, x=MX, y=MY, z=1, sx=1.5, sy=1.5)
greens = [Prop(green, x=0, y=0, z=5, show=0.0, sx=1.3, sy=1.3) for _ in range(8)]
slices = [Prop(slice_, x=0, y=0, z=6, show=0.0) for _ in range(3)]
ldl = Prop(ladle, x=0, y=0, z=1.5, show=0.0)
st.add(amma, ldl, ripe, bheemu, gaju, bujji, *greens, *slices)

# ------------------------------------------------------------------ 1. the sign, and somebody who cannot read  (36-104)
ep.shot(0, 660, 0.95, cut=False)
sc.raga(36, 150, 'calm')
for f in walk(gaju, 36, 60, 560, 8, 30):
    ep.tap(f, 'na', 0.6)
look(gaju, 62, yaw=0.0, pupil=(0, -0.9)); gaju.move(62, 66, 'over', face=0.0, pitch=-0.6)       # reads the wall
blink(gaju, 70)
for f in (76, 84):                                                                              # eyebrow waggle: rules are for other people
    gaju.move(f, f + 3, 'snap', brow=13, brow_asym=0.6); gaju.move(f + 4, f + 8, 'out', brow=0, brow_asym=0.0)
    sc.hit(f, 'ghatam', 0.6, note=74)
gaju.move(92, 95, 'over', face=1, yaw=0.8, pitch=0.0, pupil=(0.6, 0))
for f in walk(gaju, 94, 110, 1300, 5, 34):
    ep.tap(f, 'na', 0.6)

# ------------------------------------------------------------------ 2. the mango, three tries  (104-296)
ep.shot(104, 1470, 0.9)
gaju.set(104, x=1000)
for f in walk(gaju, 104, 130, MX - 10, 8, 32):
    ep.tap(f, 'na', 0.6)
for i, f in enumerate(range(104, 300, 2)):                                                      # the mango swings gently
    ripe.set(f, rot=math.sin(i * 0.22) * 5)
gaju.move(130, 134, 'over', face=0.0, yaw=0.0, pitch=-0.8, pupil=(0, -0.9))
f = take(st, gaju, 138, 0.7, hold=5); marks(st, 142, MX, MY - 120, life=10)
sc.note(141, veena, 74, 0.5, 0.8); sc.hit(141, 'manjira', 0.7)
gaju.move(f, f + 4, 'over', smile=1.0, mouth_w=1.3, pitch=-0.8, pupil=(0, -0.9))
for i, f in enumerate((166, 180, 194)):                                                         # trunk: reach, reach, reach
    gaju.move(f, f + 3, 'snap', trunk=(0, -240 - i * 34), trunk_curl=-0.9 + i * 0.3, sy=1.04 + i * 0.07, sx=1 - i * 0.03)
    sc.slide(f, 62 + i * 3, 74 + i * 4, 4, 0.4)
shake(gaju, 198, 208, 4); gaju.move(198, 200, 'out', sweat=1.0, brow_ang=14)
gaju.move(209, 213, 'in', trunk=(30, 92), trunk_curl=0.7, sy=0.94, sx=1.05, brow_ang=-10, smile=-0.4, mouth_w=0.9); gaju.move(213, 220, 'elastic', sy=1.0, sx=1.0)
sc.hit(209, 'wah', 0.6)
gaju.move(222, 225, 'snap', brow=10, brow_asym=1.0, smile=0.9, brow_ang=0, sweat=0.0); sc.hit(222, 'ghatam', 0.8, note=76)   # idea: ears
FLY = G0 - 330
gaju.move(232, 262, 'io', y=FLY); gaju.move(250, 262, 'out', trunk=(4, -250), trunk_curl=-0.6)
for fb in flap(gaju, 228, 268, 4):
    sc.hit(fb, 'flap', 0.5)
sc.slide(232, 60, 84, 28, 0.4)
sc.hit(263, 'pop', 0.6, note=80)                                                                # the tip of the trunk just touches it
for i, f in enumerate(range(263, 300, 2)):
    ripe.set(f, rot=math.sin(i * 0.7) * 22 * max(0, 1 - i / 18))
for fb in flap(gaju, 268, 280, 6, 0.5):                                                         # ...and the ears run out of puff
    sc.hit(fb, 'flap', 0.3)
gaju.move(270, 274, 'out', sweat=1.0, pupil=(0, 0), pitch=0.0, smile=-0.3, brow=12, eye_pop=1.3, trunk=(30, 60), trunk_curl=0.6)
gaju.move(282, 284, 'out', ear=1.0, sy=1.2, sx=0.88); gaju.move(282, 289, 'in', y=G0); sc.slide(282, 84, 50, 7, 0.6)
squash(gaju, 289, 0.34, 10); puffs(st, 289, MX, G0, n=5, size=40, spread=120, life=14); sc.hit(289, 'bonk', 0.9, note=55); st.shake(289, 10, 6)
gaju.set(289, eye_pop=1.0, ear=-0.4, brow=0, sweat=0.0, pupil_s=0.6, smile=-0.2)
for i, f in enumerate(range(290, 322, 2)):
    gaju.set(f, pupil=(math.cos(i * 0.9) * 0.8, math.sin(i * 0.9) * 0.8))

# ------------------------------------------------------------------ 3. Bheemu knows a better way  (300-480)
sc.raga(300, 366, 'sneak')
enter(ep, bheemu, 300, 336, 760, 1080, 12, 34, 'ge', 0.9)
look(bheemu, 338, yaw=0.6, pupil=(0.8, 0.5)); look(bheemu, 346, yaw=0.5, pupil=(0.6, -0.9)); bheemu.move(346, 350, 'over', pitch=-0.6)
face(gaju, 322, 4, pupil=(-0.8, -0.2), pupil_s=1.0, yaw=-0.5, ear=0.0, smile=0.2)
face(bheemu, 354, 4, pitch=0.0, yaw=0.5, **SLY); sc.hit(354, 'ghatam', 0.8, note=62)
for f in walk(bheemu, 360, 372, 1196, 12, 30):
    ep.tap(f, 'ge', 0.9)
bheemu.move(372, 376, 'over', armR=(70, -120), armL=(120, -120), handR='open', handL='open', yaw=0.9, **CALM)   # hugs the trunk


def drop(i, f, x0, bounce_x, rest_x, v=0.9):
    """Green mango number i falls on Bheemu's head on frame f + 8, bounces off and stays on the grass."""
    m = greens[i]
    tx, ty = st.probe(f + 8, bheemu, 'top')
    m.set(f, show=1.0, x=x0, y=G0 - 900, rot=0)
    m.move(f, f + 8, 'in', x=tx, y=ty + 10)
    arc(m, f + 8, f + 20, rest_x, G0 - 6, 150, spin=300 if rest_x > tx else -300)
    bheemu.set(f + 8, head_sy=0.78, head_sx=1.14, head_dy=16, eye_open=0.0); bheemu.move(f + 10, f + 18, 'elastic', head_sy=1.0, head_sx=1.0, head_dy=0)
    bheemu.set(f + 13, eye_open=1.0)
    sc.hit(f + 8, 'bonk', v, note=64 + i * 2); stars(st, f + 8, tx, ty - 20, n=4, r=90, life=8)


def shake_tree(f0, n, amp):
    bheemu.move(f0 - 5, f0, 'out', rot=-7, sx=1.05, sy=0.96)                                  # wind-up
    for k in range(n):
        f = f0 + k * 4
        bheemu.move(f, f + 2, 'snap', rot=7, x=1196 + amp); bheemu.move(f + 2, f + 4, 'snap', rot=-5, x=1196 - amp)
        sc.hit(f, 'ghatam', 0.7, note=50 + k)
    st.shake(f0, amp, n * 4)
    bheemu.move(f0 + n * 4, f0 + n * 4 + 4, 'over', rot=0, x=1196, sx=1.0, sy=1.0)


shake_tree(382, 3, 8); drop(0, 388, 1240, 0, 1010)
face(bheemu, 402, 3, pitch=-0.6, yaw=0.3, brow_ang=14, smile=-0.5); face(bheemu, 410, 3, pitch=0.0, yaw=0.9, brow_ang=0)
shake_tree(418, 4, 14); drop(1, 424, 1150, 0, 940); drop(2, 430, 1300, 0, 1400)
face(bheemu, 444, 3, **ANGRY)
sc.duck(448, 494, 0.5)
shake_tree(456, 6, 22)
for k, (x0, rx) in enumerate(((1180, 1060), (1260, 1340), (1140, 900), (1290, 1450))):
    drop(3 + k, 464 + k * 5, x0, 0, rx)
BIG = 492                                                                                       # the last and biggest one
big = greens[7]
big.set(BIG - 10, show=1.0, x=1200, y=G0 - 960, sx=2.6, sy=2.6); big.move(BIG - 10, BIG, 'in', y=G0 - 560)
bheemu.set(BIG, sit=1.0, armR=(0, 0), armL=(0, 0), handR='mitt', handL='mitt', face=0.0, yaw=0.0, rot=0, x=1196, sx=1.3, sy=0.7, eye_open=0.0, glasses_rot=14, glasses_dy=10,
           smile=-0.3, brow_ang=0, lid=0.0)
bheemu.move(BIG + 2, BIG + 12, 'elastic', sx=1.0, sy=1.0)
tx, ty = st.probe(BIG + 14, bheemu, 'top')
big.set(BIG, y=ty + 26); big.set(BIG + 1, z=1.9)
sc.hit(BIG, 'crash', 1.0); sc.hit(BIG, 'bonk', 1.0, note=48); ep.tap(BIG, 'dha', 1.4); st.shake(BIG, 34, 12)
stars(st, BIG, 1196, G0 - 420, n=7, r=200, life=14); word(st, BIG, 1196, G0 - 620, 'ధబ్!', 150); puffs(st, BIG, 1196, G0, n=5, size=40, spread=160, life=14)
bheemu.set(BIG + 16, eye_open=1.0, pupil_s=0.5)
for i, f in enumerate(range(BIG + 16, BIG + 60, 2)):
    bheemu.set(f, pupil=(math.cos(i * 0.9) * 0.8, math.sin(i * 0.9) * 0.8), head_rot=math.sin(i * 0.45) * 6)
face(gaju, 404, 3, yaw=-0.7, pupil=(-0.9, 0), smile=0.8)
laugh(ep, gaju, BIG + 6, BIG + 30)
face(gaju, BIG + 30, 3, **CALM)

# ------------------------------------------------------------------ 4. it falls by itself, and somebody is faster  (530-580)
F = BIG + 40
ep.push(F - 14, F, 1560, 1.05)
sc.hit(F, 'pop', 0.9, note=84)
look(gaju, F + 1, yaw=0.0, pupil=(0, -0.9)); gaju.move(F + 1, F + 4, 'snap', pitch=-0.8, trunk=(0, -230), trunk_curl=-1.0, mouth_open=0.8, **{k: v for k, v in HAPPY.items() if k != 'mouth_open'})
ripe.move(F, F + 9, 'in', y=G0 - 330, rot=0); sc.slide(F, 86, 62, 9, 0.5)
bujji.set(F + 5, show=1.0, x=2500, face=-1, yaw=-0.9, stride=60, ear=-0.6)
bujji.move(F + 5, F + 12, 'lin', x=700, step=2.0); bujji.set(F + 12, show=0.0)
ripe.set(F + 9, show=0.0); sc.hit(F + 7, 'zip', 1.0); puffs(st, F + 9, MX, G0, n=4, size=34, spread=140, life=10, dirx=1)
gaju.move(F + 11, F + 13, 'snap', trunk=(0, -200), trunk_curl=1.0, mouth_open=0.0)              # closes on nothing
face(gaju, F + 20, 3, eye_open=1.0, happy=0.0, smile=0.0, pitch=-0.5); blink(gaju, F + 26)
face(bheemu, F + 22, 3, pupil=(0.8, 0), pupil_s=1.0, head_rot=0, yaw=0.5, glasses_rot=0, glasses_dy=0)
f = take(st, gaju, F + 32, 1.0); sc.hit(F + 35, 'timp', 0.9); ep.tap(F + 35, 'dha', 1.2)
gaju.move(f - 8, f - 4, 'over', pitch=0.0, yaw=-0.9, pupil=(-0.9, 0), trunk=(30, 92), trunk_curl=0.7, **ANGRY)
bheemu.set(f - 6, sit=0.0); big.set(f - 6, z=5); arc(big, f - 6, f + 6, 1330, G0 - 6, 120, spin=200)
face(bheemu, f - 6, 3, yaw=-0.9, **ANGRY)
sc.raga(f, f + 30, 'chase')
g1 = zip_off(st, gaju, f, 300, wind=8); g2 = zip_off(st, bheemu, f + 6, 300, wind=8)
sc.hit(g1, 'zip', 0.9); sc.hit(g2, 'zip', 0.9)

# ------------------------------------------------------------------ 5. under the sign  (cut)
C = g2 + 6
ep.shot(C, 690, 0.95)
for m in greens:
    m.set(C, show=0.0)
bujji.set(C, show=1.0, x=560, face=0.0, yaw=0.3, stride=0.0, ear=0.7, **HAPPY)
ripe.set(C, show=1.0, x=572, y=G0 - 52, rot=0, sx=1.3, sy=1.3, z=5)
chew(bujji, C, C + 20, 6)
for a, x0, x1, d in ((gaju, 1500, 810, 0), (bheemu, 1700, 1090, 5)):                             # they skid in
    a.set(C + 4 + d, show=1.0, x=x0, y=G0, wheel=0.0, stride=0.0, rot=-16, face=-1, yaw=-0.9, sx=1.0, sy=1.0, **ANGRY)
    a.move(C + 4 + d, C + 16 + d, 'out', x=x1); a.move(C + 16 + d, C + 22 + d, 'elastic', rot=0)
    puffs(st, C + 12 + d, x1 + 120, G0, n=3, size=30, spread=40, life=9, dirx=-1)
sc.hit(C + 5, 'skid', 0.9, d=0.5)
bujji.move(C + 22, C + 24, 'snap', eye_open=1.0, happy=0.0, yaw=0.6, pupil=(0.8, 0), ear=1.0, head_sx=1.0, head_sy=1.0, cheeks=0.0, smile=0.0)
sc.hit(C + 22, 'ghatam', 0.7, note=70)
P = C + 34                                                                                      # she points at the wall: it FELL, nobody plucked it
bujji.move(P, P + 3, 'snap', armL=(-26, -70), pupil=(-0.3, -0.9), yaw=0.0, smile=0.8, ear=0.7); sc.note(P, xylo, 86, 0.2, 0.7)
for a in (gaju, bheemu):
    look(a, P + 8, yaw=-0.4, pupil=(-0.5, -0.9)); a.move(P + 8, P + 12, 'over', pitch=-0.6, face=-0.4)
    blink(a, P + 22)
    face(a, P + 30, 5, pitch=0.0, pupil=(-0.6, 0.2), **SORRY)
sc.hit(P + 30, 'wah', 0.5)
S = P + 44                                                                                      # she shares
sc.raga(S, S + 110, 'sweet', v=0.9)
bujji.move(S, S + 3, 'over', armL=(0, 0), yaw=0.4, **HAPPY); sc.hit(S + 2, 'pop', 0.9)
ripe.set(S + 2, show=0.0)
hx, hy = st.probe(S, gaju, 'head')
gaju.move(S + 2, S + 8, 'over', trunk=(-70, -40), trunk_curl=-0.5, face=-0.3, yaw=-0.3, **HAPPY)
bheemu.move(S + 2, S + 8, 'over', armL=(30, -150), handL='grip', bendL=0.5, face=-0.2, yaw=-0.3, **HAPPY)
slices[0].set(S + 2, show=1.0, x=572, y=G0 - 60); slices[0].attach(S + 3, 900, bujji, 'handL', 0, -8)
slices[1].set(S + 2, show=1.0, x=572, y=G0 - 60); arc(slices[1], S + 2, S + 9, 740, G0 - 200, 120, spin=360); slices[1].attach(S + 9, 900, gaju, 'trunk', 0, -6)
slices[2].set(S + 3, show=1.0, x=572, y=G0 - 60); arc(slices[2], S + 3, S + 12, 1030, G0 - 330, 160, spin=360); slices[2].attach(S + 12, 900, bheemu, 'handL', 0, -20)
for a in (bujji, gaju, bheemu):
    chew(a, S + 16, S + 52, 6)
for f in range(S + 16, S + 52, 6):
    sc.hit(f, 'munch', 0.5)

# ------------------------------------------------------------------ 6. Ammamma always knows
A = S + 44
amma.set(A, show=1.0, x=-140, face=1, yaw=0.7, armR=(30, -130), handR='grip', **ANGRY)
ldl.set(A, show=1.0); ldl.attach(A, 900, amma, 'handR', 0, 20)
for f in walk(amma, A, A + 24, 300, 8, 30):
    ep.tap(f, 'dha', 1.0)
for a in (bujji, gaju, bheemu):
    a.move(A + 24, A + 26, 'snap', head_sx=1.0, head_sy=1.0, cheeks=0.0, yaw=-0.8, pupil=(-0.9, 0), **SHOCK)
bujji.move(A + 24, A + 26, 'snap', ear=1.0)
sc.hit(A + 25, 'timp', 0.8); sc.hit(A + 34, 'gulp', 1.0)
bujji.move(A + 40, A + 48, 'over', armL=(-60, -70), yaw=-0.5, ear=0.2, **SORRY)                 # a slice for Ammamma
gaju.move(A + 40, A + 46, 'over', **SORRY); bheemu.move(A + 40, A + 46, 'over', **SORRY)
sc.slide(A + 40, 62, 72, 8, 0.3)
face(amma, A + 52, 5, **HAPPY); amma.move(A + 52, A + 57, 'over', armR=(10, -40), armL=(60, -60), handL='open')
for a in (bujji, gaju, bheemu):
    face(a, A + 58, 4, **HAPPY)
END = A + 72

speak(ep, amma, A + 26, 'a_vata')                                    # "Where is my share?"
ep.close(END, 640, G0 - 300)
print('frames needed', END + 34)

if __name__ == '__main__':
    ep.main(__file__)
