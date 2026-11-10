"""Bheemu & Gaju, episode 10: "Ten Laddus"  (about 31 s, vertical, silent; only Ammamma speaks)

Ammamma counts ten laddus out loud. Every time she turns her back one goes: a paw, a rabbit, a trunk.
"Nine? Eight? Seven?" She pretends to turn, catches all three red-handed, and they point at Bheemu, who
has been sitting with his eyes shut, resisting. The next laddu goes to him.
"""
import os, sys, math
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', 'engine'))
from toon import GROUND, oval
from chars import Bheemu, Gaju
from cast import Ammamma, Laddu, Bujji
from scene import Painted, Prop, table, rect, puffs, stars, marks
from india import illu, telugu, thali, laddu as laddu_draw
from acting import blink, look, bob, walk, squash, take, shake, chew, arc
from sound import veena, bansuri, xylo
from voice import speak
from show import Show, face, CALM, HAPPY, LAUGH, ANGRY, SHOCK, SORRY, SLY

G0 = GROUND
ep = Show(10, 'Ten Laddus', 'ten_laddus', 782, Painted(3400, illu))
st, sc, cam = ep.st, ep.sc, ep.cam
TX, TS, TOP = 800, 1.15, G0 - 224
PX = 780
SPOTS = [(PX - 66 + i * 44, TOP - 4) for i in range(4)] + [(PX - 44 + i * 44, TOP - 40) for i in range(3)] + [(PX - 22 + i * 44, TOP - 76) for i in range(2)] + [(PX, TOP - 112)]


def note(g, p, f):                                      # "Laddus: 10. They are counted! - Ammamma"
    g.shape(rect(-160, -150, 320, 150, 6), (255, 250, 220), True, 4, (58, 42, 40))
    g.shape(oval(0, -150, 9, 9), (214, 60, 56), True, 3, (58, 42, 40))
    telugu(g, 'లడ్డూలు: 10', 0, -98, 44, (170, 30, 40), 'Ramabhadra')
    telugu(g, 'లెక్క ఉంది!', 0, -50, 40, (40, 60, 150), 'Ramabhadra')
    telugu(g, '- అమ్మమ్మ', 86, -14, 26, (90, 60, 60), 'Mallanna')


bheemu = Bheemu(x=330, z=3, sit=1.0, eye_open=0.0, smile=0.2)
amma = Ammamma(x=1205, z=3, face=-1, yaw=-0.7)
cat = Laddu(x=610, y=G0, z=-1, show=0.0, lid=0.2)
bujji = Bujji(x=905, y=G0, z=-1, show=0.0)
gaju = Gaju(x=1010, y=G0 - 16, z=-0.5, show=0.0, sy=0.7, sx=0.8)
tbl = Prop(table, x=TX, y=G0, z=0, sx=TS)
nt = Prop(note, x=TX - 120, y=G0 - 24, z=0.4, rot=2)
pl = Prop(thali, x=PX, y=TOP, z=1, sx=1.2)
ld = [Prop(laddu_draw, x=x, y=y, z=1.1 + i * 0.01, sx=1.05, sy=1.05) for i, (x, y) in enumerate(SPOTS)]
st.add(gaju, bujji, cat, tbl, nt, pl, *ld, bheemu, amma)
ep.shot(0, 735, 1.0, cut=False)
UP = {cat: G0 - 190, bujji: G0 - 170}


def up(a, f, n=4):
    a.set(f, show=1.0, y=G0); a.move(f, f + n, 'over', y=UP[a]); sc.hit(f, 'pop', 0.5, note=70)


def down(a, f):
    a.move(f, f + 3, 'in', y=G0); a.set(f + 3, show=0.0); sc.hit(f, 'zip', 0.4, d=0.12)


def take_one(i, f, who, anchor, dx=0, dy=0, n=4):
    ax, ay = st.probe(f + n, who, anchor)
    arc(ld[i], f, f + n, ax + dx, ay + dy, 50); ld[i].set(f + n, z=-0.8 if who is not gaju else -0.4); ld[i].attach(f + n, 900, who, anchor, dx, dy)
    sc.note(f + n, xylo, 84, 0.15, 0.6)


def turn_away(f):
    amma.move(f, f + 3, 'over', face=1, yaw=0.7, pupil=(0.6, 0), armL=(0, 0), handL='mitt')
    for k in range(f + 6, f + 30, 12):
        amma.move(k, k + 6, 'io', head_rot=5); amma.move(k + 6, k + 12, 'io', head_rot=-5)


def turn_back(f, mood, line):
    amma.move(f, f + 3, 'snap', face=-1, yaw=-0.7, pupil=(-0.6, 0.5), head_rot=0); sc.hit(f, 'ghatam', 0.8, note=57)
    for k in range(3):                                                    # a quick recount
        amma.move(f + 6 + k * 4, f + 8 + k * 4, 'snap', armL=(-80 - k * 10, -50), handL='point'); sc.note(f + 6 + k * 4, xylo, 76 + k * 2, 0.08, 0.4)
    face(amma, f + 16, 3, **mood)
    return speak(ep, amma, f + 18, line)


# ------------------------------------------------------------------ 1. the count
sc.raga(36, 180, 'calm', v=0.8)
amma.move(36, 40, 'over', armL=(-90, -50), handL='point', pupil=(-0.6, 0.5))
e = speak(ep, amma, 38, 'a_count')                                         # "One, two, three ... ten!"
step = (e - 44) / 10.0
for k in range(10):
    f = int(40 + k * step)
    amma.move(f, f + 3, 'snap', armL=(-110, -36)); amma.move(f + 3, f + 8, 'over', armL=(-90, -50))
    ld[k].set(f + 2, sy=0.85, sx=1.2); ld[k].move(f + 3, f + 9, 'elastic', sy=1.05, sx=1.05)
bheemu.move(96, 98, 'snap', eye_open=1.0, pupil=(0.9, 0.2), yaw=0.5); bheemu.move(104, 108, 'over', mouth_open=0.3, smile=0.9)       # one eye on the plate...
bheemu.move(120, 123, 'snap', eye_open=0.0, mouth_open=0.0, smile=-0.2, yaw=0.0, sweat=1.0, brow_ang=14); shake(bheemu, 123, 133, 3)   # ...no. Be strong.
face(amma, e - 6, 4, **HAPPY)

# ------------------------------------------------------------------ 2. nine? eight? seven?
sc.raga(e, e + 330, 'sneak')
T = e + 6
turn_away(T)
up(cat, T + 8); cat.move(T + 12, T + 15, 'snap', armR=(110, -40), pupil=(0.8, 0.2)); take_one(9, T + 15, cat, 'handR', 0, -16)
cat.move(T + 20, T + 23, 'over', armR=(20, -60)); down(cat, T + 26); ld[9].set(T + 29, show=0.0)
e = turn_back(T + 34, dict(brow=10, brow_asym=1.0, smile=-0.2), 'a_nine')   # "Nine?"
T = e + 6
turn_away(T)
up(bujji, T + 6, 3); bujji.move(T + 9, T + 11, 'snap', armL=(-100, -30), ear=1.0); take_one(8, T + 11, bujji, 'handL', 0, -10, 3)
down(bujji, T + 17); ld[8].set(T + 20, show=0.0)
e = turn_back(T + 24, dict(brow_ang=14, brow=0, brow_asym=0.0, smile=-0.5), 'a_eight')   # "Eight?"
T = e + 6
turn_away(T)
gaju.set(T + 3, show=1.0, trunk=(0, 10), trunk_curl=0.2)
hx, hy = st.probe(T + 4, gaju, 'head')
gaju.move(T + 4, T + 9, 'out', trunk=(-60, -330), trunk_curl=-0.9); sc.slide(T + 4, 55, 74, 5, 0.4)
gaju.move(T + 10, T + 13, 'over', trunk=(SPOTS[7][0] - hx, SPOTS[7][1] - 30 - hy), trunk_curl=0.8); ld[7].attach(T + 13, 900, gaju, 'trunk', 0, 10); sc.note(T + 13, xylo, 84, 0.15, 0.6)
gaju.move(T + 15, T + 18, 'in', trunk=(0, 10), trunk_curl=0.2); gaju.set(T + 19, show=0.0); ld[7].set(T + 19, show=0.0)
e = turn_back(T + 22, ANGRY, 'a_seven')                                    # "Seven?"

# ------------------------------------------------------------------ 3. the trap
F = e + 6
sc.duck(F, F + 60, 0.2)
amma.move(F, F + 3, 'over', face=1, yaw=0.7, armL=(0, 0), handL='mitt', lid=0.3, brow_ang=0, brow_asym=1.0, smile=0.6, pupil=(-0.9, 0))   # turns... but keeps one eye back
for k, f in enumerate((F + 6, F + 14)):
    sc.hit(f, 'ghatam', 0.5, note=50 + k * 2)
up(cat, F + 16); up(bujji, F + 18, 3)
gaju.set(F + 19, show=1.0, y=G0, sy=1.0, sx=1.0, trunk=(30, 60), trunk_curl=0.7); gaju.move(F + 19, F + 24, 'over', y=G0 - 150)
cat.move(F + 22, F + 25, 'snap', armR=(110, -40)); take_one(6, F + 25, cat, 'handR', 0, -16, 3)
bujji.move(F + 22, F + 25, 'snap', armL=(-100, -30)); take_one(5, F + 26, bujji, 'handL', 0, -10, 3)
hx, hy = st.probe(F + 26, gaju, 'head')
gaju.move(F + 24, F + 28, 'over', trunk=(SPOTS[4][0] - hx, SPOTS[4][1] - 30 - hy), trunk_curl=0.8); ld[4].attach(F + 28, 900, gaju, 'trunk', 0, 10)
G = F + 34
amma.move(G, G + 2, 'snap', face=-1, yaw=-0.7, lid=0.0, brow_asym=0.0, pupil=(-0.7, 0.2), armL=(-60, -110), armR=(-30, -110), handL='fist', handR='fist', bendL=-0.8, **{k: v for k, v in ANGRY.items() if k != 'lid'})
sc.hit(G, 'timp', 1.0); ep.tap(G, 'dha', 1.4); sc.hit(G, 'crash', 0.6); st.shake(G, 18, 8)
for a in (cat, bujji, gaju):
    a.move(G + 1, G + 3, 'snap', **SHOCK); marks(st, G + 2, a.value('x', G), a.value('y', G + 2) - a.HEIGHT * 1.3, life=9)
gaju.move(G + 1, G + 3, 'snap', trunk=(-50, -40), trunk_curl=0.6)
e = speak(ep, amma, G + 16, 'a_evaru_laddu')                               # "Who ate the laddus?"

# ------------------------------------------------------------------ 4. him! (again)
P = e + 4
cat.move(P, P + 3, 'snap', armL=(-110, -80), yaw=-0.5, pupil=(-0.8, 0), eye_pop=1.0, mouth_open=0.0, smile=0.8, brow=0)
bujji.move(P + 3, P + 6, 'snap', armR=(-90, -60), yaw=-0.5, pupil=(-0.8, 0), eye_pop=1.0, mouth_open=0.0, smile=0.8, brow=0)
gaju.move(P + 6, P + 9, 'snap', yaw=-0.5, pupil=(-0.8, 0), eye_pop=1.0, mouth_open=0.0, smile=0.8, brow=0, ear=1.0)
for k in range(3):
    sc.hit(P + k * 3, 'ghatam', 0.9, note=62 + k * 2)
bheemu.move(P + 12, P + 14, 'snap', sweat=0.0, yaw=0.5, pupil=(0.8, 0), **SHOCK)
bheemu.move(P + 16, P + 19, 'snap', armR=(-60, -200), handR='point', bendR=-0.5)
look(amma, P + 22, yaw=-0.9, pupil=(-0.9, 0.3)); look(amma, P + 34, yaw=-0.5, pupil=(-0.5, 0.2))
face(amma, P + 36, 4, brow_ang=0, lid=0.3, brow_asym=1.0, smile=0.3)                                   # she looks at what is in their hands
for a in (cat, bujji, gaju):
    look(a, P + 44, pupil=(0, 0.8), yaw=0.0); a.move(P + 48, P + 50, 'snap', **SHOCK)
for i in (4, 5, 6):
    ld[i].set(P + 54, show=0.0)                                            # behind the back, quick
cat.move(P + 52, P + 55, 'snap', armR=(0, 0), armL=(0, 0)); bujji.move(P + 52, P + 55, 'snap', armL=(0, 0), armR=(0, 0)); gaju.move(P + 52, P + 55, 'snap', trunk=(30, 60), ear=0.0)
for a in (cat, bujji, gaju):
    face(a, P + 58, 4, **SORRY)
sc.hit(P + 60, 'gulp', 1.0)

# ------------------------------------------------------------------ 5. this one is yours
Q = P + 70
sc.raga(Q, Q + 160, 'sweet', v=0.9)
amma.move(Q, Q + 4, 'over', armR=(0, 0), handR='mitt', armL=(-150, -60), handL='grip', bendL=0.3, **CALM); ld[3].attach(Q + 4, Q + 70, amma, 'handL', 0, -16); ld[3].set(Q + 4, z=4)
bheemu.move(Q, Q + 6, 'io', armR=(0, 0), handR='mitt', bendR=0.14, **SORRY)
amma.set(Q + 6, z=4)
for f in walk(amma, Q + 6, Q + 28, 530, 7, 30):
    ep.tap(f, 'na', 0.5)
amma.move(Q + 28, Q + 32, 'over', armL=(-90, -120), **HAPPY)
e = speak(ep, amma, Q + 30, 'a_foryou')                                    # "This one is for you, Bheemu."
bheemu.move(Q + 40, Q + 44, 'over', yaw=0.5, pupil=(0.8, -0.3), **{k: v for k, v in SHOCK.items() if k != 'mouth_open'})
bheemu.move(e - 6, e, 'over', armR=(120, -150), handR='grip', **HAPPY); ld[3].attach(e, 900, bheemu, 'handR', 0, -24)
amma.move(e, e + 6, 'io', armL=(0, 0), handL='mitt')
mx, my = st.probe(e + 14, bheemu, 'mouth')
bheemu.move(e + 10, e + 14, 'over', armR=(60, -280), mouth_open=0.9); ld[3].set(e + 15, show=0.0); bheemu.move(e + 15, e + 17, 'snap', mouth_open=0.0, armR=(0, 0), handR='mitt')
sc.hit(e + 15, 'munch', 1.0); chew(bheemu, e + 16, e + 46, 6)
for a in (cat, bujji, gaju):
    face(a, e + 20, 5, yaw=-0.5, pupil=(-0.7, 0.3), brow_ang=-22, smile=-0.6)                           # three very sad faces
look(bheemu, e + 30, yaw=0.6, pupil=(0.9, 0)); blink(bheemu, e + 36)
bheemu.move(e + 44, e + 48, 'over', armR=(150, -160), handR='open', head_sx=1.0, head_sy=1.0, cheeks=0.0, **HAPPY)   # oh, go on then
sc.hit(e + 46, 'tada', 0.5)
for i, a in enumerate((cat, bujji, gaju)):
    k = (4, 5, 6)[i]
    ld[k].set(e + 52 + i * 3, show=1.0); sc.hit(e + 52 + i * 3, 'pop', 0.7, note=74 + i * 3)
    face(a, e + 52 + i * 3, 3, yaw=0.0, pupil=(0, 0), **HAPPY)
cat.move(e + 52, e + 55, 'over', armR=(10, -70)); bujji.move(e + 55, e + 58, 'over', armL=(-6, -20)); gaju.move(e + 58, e + 61, 'over', trunk=(-10, -30), trunk_curl=0.9)
for a in (cat, bujji, gaju):
    chew(a, e + 64, e + 96, 6)
for f in range(e + 64, e + 90, 6):
    sc.hit(f, 'munch', 0.4)
face(amma, e + 50, 4, yaw=0.5, **HAPPY)
END = e + 90
ep.close(END, 700, G0 - 330)
print('frames needed', END + 34)

if __name__ == '__main__':
    ep.main(__file__)
