"""Acting test: Laddu and Gaju drink the milk (12.5 s, one close shot).

Made to find out how far the engine can go when every action gets full attention: paws that arrive one
at a time, a tongue that laps, a trunk that sneaks, swallows that travel up it, ripples in the milk,
ears that react, and a hand-drawn line wobble (Stage.boil).
Run:  python3 shot.py [final|sheet f1,f2,...]
"""
import os, sys, math
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', '..', 'engine'))
import skia
from toon import Stage, GROUND, W, H, oval, poly
from chars import Gaju
from cast import Laddu
from scene import Painted, Prop, table, stars
from india import illu
from acting import blink
from sound import Score, tabla, xylo, bansuri
from show import milkpot, splash, SHOCK, HAPPY, ANGRY, CALM

G0 = GROUND
N = 350
st = Stage(N, bg=Painted(3400, illu)); sc = Score(N); cam = st.cam
st.boil = True
TX, TOP, PX = 800, G0 - 224, 760
cam.set(0, x=850, y=TOP - 180, zoom=1.7)
cam.move(60, 84, 'io', x=840, y=TOP - 200, zoom=1.9)          # ease in as the lapping starts
cam.move(150, 170, 'io', x=870, y=TOP - 240, zoom=1.7)       # widen for the trunk going overhead
FUR, CREAM, HL = (244, 156, 66), (255, 236, 200), (170, 86, 34)


def paw(g, p, f):
    g.shape(oval(0, 26, 22, 34), FUR, True, 4, (110, 56, 30))
    g.shape(oval(0, 0, 27, 17), CREAM, True, 4, (110, 56, 30))
    for k in (-1, 0, 1):
        g.shape(poly([(k * 11, -2), (k * 12, 12)], False), None, True, 2.6, HL)


cat = Laddu(x=905, y=G0 - 30, z=-1, show=0.0, lid=0.2)
gaju = Gaju(x=1050, y=G0 + 20, z=-0.5, show=0.0, trunk=(-10, 40), trunk_curl=0.2)
tbl = Prop(table, x=TX, y=G0, z=0, sx=1.15)
pot = Prop(milkpot, x=PX, y=TOP, z=-1.5, level=1.0, ripple=0.0, ripple_x=40.0)
pL = Prop(paw, x=850, y=TOP + 70, z=0.5, show=0.0)
pR = Prop(paw, x=958, y=TOP + 70, z=0.5, show=0.0)
st.add(cat, gaju, tbl, pot, pL, pR)
tap = lambda f, s='na', v=0.5: sc._add(sc.fx, f, tabla(s, v))
sc.raga(0, 250, 'sneak', v=0.7)

# ---- two paws, then two ears, then two eyes
for pw, f in ((pL, 10), (pR, 20)):
    pw.set(f, show=1.0); pw.move(f, f + 3, 'out', y=TOP - 6, sx=0.85, sy=1.2); pw.move(f + 3, f + 5, 'in', y=TOP + 4, sx=1.25, sy=0.8); pw.move(f + 5, f + 11, 'elastic', sx=1.0, sy=1.0)
    tap(f + 4, 'na', 0.6)
cat.set(26, show=1.0, pupil=(-0.8, -0.2))
cat.move(26, 36, 'out', y=G0 - 112); sc.slide(26, 62, 70, 9, 0.25)
cat.move(40, 42, 'snap', pupil=(0.8, -0.2)); cat.move(48, 50, 'snap', pupil=(-0.5, 0.5)); blink(cat, 52)      # right... left... the pot
cat.move(56, 62, 'over', y=G0 - 206, lid=0.35, smile=0.9)
for f in (64, 68):                                                # whiskers twitch
    cat.move(f, f + 2, 'snap', head_rot=3); cat.move(f + 2, f + 4, 'snap', head_rot=-2)
cat.move(72, 80, 'io', head_dx=-44, head_rot=-9, head_dy=6, pupil=(-0.6, 0.7))
for f in (82, 87):                                                # sniff, sniff
    cat.move(f, f + 2, 'out', head_dy=11); cat.move(f + 2, f + 5, 'in', head_dy=6); sc.hit(f, 'sniff', 0.5)
cat.move(92, 99, 'io', head_dx=-118, head_rot=-21, head_dy=-26, lid=0.55)


def lap(f, n=6, quiet=0.45):
    """One lap: head dips, tongue flicks down and curls back, the milk rings."""
    cat.move(f, f + 2, 'out', tongue=1.0, head_dy=-18); cat.move(f + 3, f + n, 'in', tongue=0.0, head_dy=-26)
    pot.set(f + 2, ripple=0.25); pot.move(f + 2, f + n + 3, 'out', ripple=1.0); pot.set(f + n + 4, ripple=0.0)
    sc.note(f + 2, xylo, 91, 0.05, quiet); tap(f + 2, 'na', quiet * 0.5)


for i, f in enumerate(range(102, 132, 6)):
    lap(f)
    if i in (1, 3):
        splash(st, f + 2, PX + 44, TOP - 118, n=4, life=7, col=(255, 255, 250))
cat.move(112, 116, 'io', eye_open=0.0, happy=1.0)                 # bliss
for f in (110, 122):
    cat.move(f, f + 2, 'snap', ear_back=0.5); cat.move(f + 2, f + 7, 'out', ear_back=0.0)

# ---- a yellow cap, two eyes, and a trunk that walks along the table like a snake
gaju.set(108, show=1.0, pupil=(-0.8, 0.3), brow_asym=1.0)
gaju.move(108, 120, 'io', y=G0 - 112)
hx, hy = st.probe(122, gaju, 'head')
goal = lambda x, y: (x - hx, y - hy)
gaju.move(122, 140, 'io', trunk=goal(PX + 150, TOP - 34)); sc.slide(122, 52, 60, 18, 0.25)
for i, f in enumerate(range(122, 140, 4)):
    gaju.move(f, f + 4, 'io', trunk_curl=0.7 if i % 2 else -0.5)
B = 142                                                           # it pokes the wrong chin
gaju.move(140, B, 'snap', trunk=goal(PX + 100, TOP - 74), trunk_curl=-0.6)
cat.move(B, B + 2, 'snap', eye_open=1.0, happy=0.0, eye_pop=1.35, ear_back=1.0, tongue=0.0, head_dy=14, head_dx=-58, head_rot=-6, lid=0.0, smile=-0.2)
sc.hit(B, 'pop', 0.7, note=84); tap(B, 'ge', 0.8)
cat.move(B + 6, B + 12, 'io', pupil=(0.5, 0.9), eye_pop=1.0, lid=0.4, brow_ang=22)       # slow look down at it
gaju.move(B + 2, B + 5, 'over', trunk_curl=0.2)
S = B + 22                                                        # the swat: wind up, hit, settle
pR.move(S - 7, S - 1, 'out', x=958, y=TOP - 96, rot=-25, sx=0.9, sy=1.15)
pR.move(S - 1, S + 1, 'snap', x=PX + 110, y=TOP - 66, rot=20, sx=1.3, sy=0.8); pR.move(S + 2, S + 6, 'out', sx=1.0, sy=1.0)
pR.move(S + 8, S + 16, 'io', x=958, y=TOP + 4, rot=0)
sc.hit(S, 'bonk', 0.8, note=72); stars(st, S, PX + 112, TOP - 70, n=5, r=70, life=8); st.shake(S, 6, 5)
gaju.move(S, S + 2, 'snap', trunk=goal(PX + 240, TOP - 60), trunk_curl=1.0, ear=1.0, **SHOCK)
for i, f in enumerate(range(S + 2, S + 12, 2)):                   # the trunk tip throbs
    gaju.set(f, trunk_curl=1.0 if i % 2 else 0.5)
cat.move(S + 2, S + 8, 'io', pupil=(-0.4, 0.6), ear_back=0.3, brow_ang=8, smile=0.7, lid=0.4, head_dx=-118, head_rot=-21, head_dy=-26)
lap(S + 12); lap(S + 18)
gaju.move(S + 12, S + 16, 'over', ear=0.0, eye_pop=1.0, mouth_open=0.0, brow=0, pupil_s=1.0, pupil=(-0.7, -0.3), brow_ang=20, lid=0.2, smile=-0.4)      # right. Plan B.

# ---- over the top
O = S + 22
gaju.move(O, O + 9, 'out', trunk=goal(PX + 96, TOP - 330), trunk_curl=-0.8); sc.slide(O, 55, 79, 9, 0.35)
gaju.move(O + 9, O + 15, 'in', trunk=goal(PX + 30, TOP - 128), trunk_curl=1.0)
cat.move(O + 2, O + 9, 'io', tongue=0.0, head_dy=4, head_dx=-50, head_rot=-4, pupil=(0.5, -0.9), lid=0.0, ear_back=0.0, brow_ang=0, smile=0.0)
cat.move(O + 9, O + 15, 'io', pupil=(-0.6, 0.5), head_dy=14)
pot.set(O + 15, ripple_x=20.0, ripple=0.3); pot.move(O + 15, O + 22, 'out', ripple=1.0); sc.hit(O + 15, 'pop', 0.6, note=62)
G = O + 20
lv = 1.0
for k in range(3):                                                # three long swallows: each one travels up the trunk
    f = G + k * 12
    gaju.set(f, gulp=0.0); gaju.move(f, f + 8, 'lin', gulp=1.0); gaju.set(f + 9, gulp=-1.0)
    gaju.set(f + 8, head_sx=1.1, head_sy=0.94, cheeks=1.0); gaju.move(f + 9, f + 13, 'elastic', head_sx=1.0, head_sy=1.0); gaju.set(f + 12, cheeks=0.0)
    gaju.move(f + 6, f + 8, 'snap', ear=0.7); gaju.move(f + 8, f + 12, 'out', ear=0.0)
    pot.move(f, f + 8, 'io', level=lv - 0.26); lv -= 0.26
    sc.slide(f, 50 + k * 2, 62 + k * 2, 8, 0.4); sc.hit(f + 8, 'gulp', 0.8)
gaju.move(G + 2, G + 6, 'over', brow_ang=0, lid=0.0, **{k: v for k, v in HAPPY.items() if k not in ('brow_ang', 'lid')})
cat.move(G + 4, G + 6, 'snap', eye_pop=1.4, pupil=(-0.6, 0.8), ear_back=0.6)                   # the level is going down
cat.move(G + 14, G + 16, 'snap', pupil=(0.9, -0.3), head_rot=6)                                 # at the thief
cat.move(G + 24, G + 27, 'over', pupil=(0, 0), head_rot=0, head_dx=-40, eye_pop=1.0, lid=0.5, ear_back=0.2)   # at us. Unbelievable.
R = G + 38                                                        # the race
cat.move(R, R + 4, 'over', head_dx=-122, head_rot=-23, head_dy=-22, lid=0.2, brow_ang=18, pupil=(-0.5, 0.8))
for i, f in enumerate(range(R + 4, R + 28, 4)):
    lap(f, 4, 0.55)
    if i % 2 == 0:
        splash(st, f + 2, PX + 40, TOP - 110, n=4, life=6, col=(255, 255, 250))
for k in range(2):
    f = R + 6 + k * 10
    gaju.set(f, gulp=0.0); gaju.move(f, f + 7, 'lin', gulp=1.0); gaju.set(f + 8, gulp=-1.0); sc.hit(f + 7, 'gulp', 0.8)
    gaju.set(f + 7, head_sx=1.1, head_sy=0.94); gaju.move(f + 8, f + 12, 'elastic', head_sx=1.0, head_sy=1.0)
gaju.move(R, R + 3, 'snap', happy=0.0, eye_open=1.0, brow_ang=18, pupil=(-0.8, 0.2))
pot.move(R + 4, R + 28, 'lin', level=0.0)
E = R + 30                                                        # empty
sc.duck(E, N, 0.3)
cat.move(E, E + 2, 'snap', tongue=1.0); sc.note(E + 1, xylo, 96, 0.08, 0.7); cat.move(E + 4, E + 7, 'in', tongue=0.0, head_dy=-24)    # tongue on bare steel
gaju.move(E, E + 3, 'snap', trunk=goal(PX - 10, TOP - 122)); gaju.move(E + 4, E + 7, 'snap', trunk=goal(PX + 40, TOP - 122)); sc.hit(E + 2, 'sniff', 0.9); sc.hit(E + 6, 'sniff', 0.9)
cat.move(E + 10, E + 15, 'io', head_dx=-30, head_rot=0, head_dy=4, brow_ang=0, lid=0.3, pupil=(0.9, 0), smile=0.6)
gaju.move(E + 10, E + 15, 'io', trunk=goal(PX + 150, TOP - 90), trunk_curl=0.8, brow_ang=0, pupil=(-0.9, 0), smile=0.8)
cat.move(E + 18, E + 20, 'snap', tongue=0.5); cat.move(E + 21, E + 24, 'out', tongue=0.0)       # licks his lips
D = E + 30                                                        # somebody big is standing behind the camera
st.overlays.append(lambda g, f: g.c.drawRect(skia.Rect(0, 0, W * min(1, (f - D) / 8.0), H), skia.Paint(Color=skia.Color(30, 20, 50, 70))) if f >= D else None)
tap(D, 'dha', 1.0); tap(D + 8, 'dha', 1.1)
for a in (cat, gaju):
    a.move(D + 4, D + 6, 'snap', **SHOCK); a.move(D + 6, D + 8, 'snap', pupil=(-0.9, -0.3))
cat.move(D + 4, D + 6, 'snap', ear_back=1.0); gaju.move(D + 4, D + 6, 'snap', ear=1.0, trunk_curl=1.0)
cat.move(D + 16, D + 30, 'in', y=G0 - 20); gaju.move(D + 16, D + 30, 'in', y=G0 + 40, trunk=(-10, 40)); sc.slide(D + 16, 70, 50, 14, 0.3)   # down, slowly, as if that helps
cat.set(D + 31, show=0.0); gaju.set(D + 31, show=0.0)
for pw, f in ((pR, D + 30), (pL, D + 34)):
    pw.move(f, f + 3, 'in', y=TOP + 70); pw.set(f + 4, show=0.0); tap(f + 2, 'na', 0.4)
print('needs', D + 44)

if __name__ == '__main__':
    here = os.path.dirname(os.path.abspath(__file__)); out = os.path.join(here, 'out'); os.makedirs(out, exist_ok=True)
    if len(sys.argv) > 2 and sys.argv[1] == 'sheet':
        st.sheet([int(x) for x in sys.argv[2].split(',')], sys.argv[3], cols=6, scale=0.3)
    else:
        raw = os.path.join(out, 'raw.mp4')
        st.render(raw, audio=sc.write(os.path.join(out, 'audio.wav')))
        os.system('ffmpeg -y -loglevel error -i %s -c:v libx264 -crf 20 -preset slow -tune animation -c:a aac -b:a 160k -movflags +faststart %s' % (raw, os.path.join(out, 'acting_test_milk.mp4')))
