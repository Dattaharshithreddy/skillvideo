"""Bheemu & Gaju, episode 1: "The Dosa Snatch"  (about 32 s, vertical 1080x1920, 24 fps, no dialogue)

calm setup -> the thief appears -> sneak and snatch -> slow burn and take -> reveal
-> scramble and chase -> big hit -> small topper -> make-up ending -> iris out
Run:  python3 episode.py [preview|final|sheet f1,f2,... name.png]
"""
import os, sys, math
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', '..', 'engine'))
from toon import Stage, W, H, GROUND, poly
from chars import Bheemu, Gaju
from scene import Painted, Prop, table, dosa, pan, fridge, puffs, stars, zip_lines, marks, iris, title_card
from india import illu, thali, telugu
from acting import blink, look, bob, walk, squash, take, shake, scramble, zip_off, chew, flap, arc
from sound import Score, xylo, pizz, reed, veena, bansuri, tabla

TOTAL = 780
G0 = GROUND
st = Stage(TOTAL, bg=Painted(3400, illu))
sc = Score(TOTAL)
cam = st.cam


def cy(z, up=0):
    """Camera height that keeps the floor near the bottom of the frame at zoom z."""
    return G0 - 600 / z - up


TS = 0.8                                             # table width scale
TX = 1000
bheemu = Bheemu(x=600, z=3, face=-0.25, yaw=-0.7, smile=0.6)
gaju = Gaju(x=1100, z=-1, show=0.0)
tbl = Prop(table, x=TX, y=G0, z=0, sx=TS)
plt = Prop(thali, x=TX, y=G0 - 228, z=1)
dos = Prop(dosa, x=0, y=0, z=5, bite=0.0)
pn = Prop(pan, x=0, y=0, z=4)
frg = Prop(fridge, x=3080, y=G0 + 12, z=1)
st.add(gaju, tbl, plt, frg, bheemu, pn, dos)
cam.set(0, x=720, y=cy(1.15), zoom=1.15)

# ------------------------------------------------------------------ title
title_card(st, 0, 36, 'Bheemu & Gaju', 'The Dosa Snatch')
st.overlays.append(lambda g, f: telugu(g, 'భీము - గజు', W / 2, H / 2 - 260, 120, (255, 246, 226), 'Ramabhadra', a=min(1, (36 - f) / 8)) if f < 36 else None)
sc.hit(2, 'manjira', 0.9); sc.note(2, bansuri, 74, 0.5, 0.6); sc.note(14, bansuri, 81, 0.7, 0.6)

# ------------------------------------------------------------------ 1. calm setup: Bheemu flips dosas  (f36-156)
sc.raga(36, 156, 'calm')
BASE = (18, -210)
bheemu.set(0, armL=BASE, bendL=0.5, handL='fist')
ax, ay = st.probe(40, bheemu, 'handL')
BX, BY = 336, G0 - 352                               # the burner
pn.attach(0, 331, bheemu, 'handL', BX - ax, BY - ay)
bob(bheemu, 36, 84)
bheemu.move(46, 49, 'out', armL=(18, -192)); bheemu.move(49, 52, 'snap', armL=(18, -244)); bheemu.move(52, 58, 'elastic', armL=BASE)
bheemu.move(51, 56, 'out', pitch=-0.7); bheemu.move(58, 64, 'io', pitch=0.0)
px, py = BX, BY
dos.attach(0, 50, pn, 'c', 0, -14)
dos.set(51, x=px, y=py - 50)
arc(dos, 51, 63, px, py - 14, 230, spin=360)
dos.attach(63, 87, pn, 'c', 0, -14)
dos.set(63, rot=0, sy=0.6, sx=1.25); dos.move(64, 70, 'elastic', sy=1.0, sx=1.0)
bheemu.move(63, 65, 'out', armL=(18, -200)); bheemu.move(65, 70, 'elastic', armL=BASE)
sc.hit(50, 'whoosh', 0.35, d=0.2); sc.slide(51, 72, 84, 6, 0.3); sc.slide(57, 84, 72, 6, 0.3); sc.hit(63, 'pop', 0.7)
look(bheemu, 70, yaw=0.7, pupil=(0.8, 0.1)); blink(bheemu, 75); look(bheemu, 79, yaw=-0.7, pupil=(-0.4, 0.2))
bheemu.move(82, 87, 'out', armL=(4, -170), sy=0.92, sx=1.06, rot=-5)                 # wind-up
bheemu.move(87, 90, 'snap', armL=(70, -300), sy=1.08, sx=0.95, rot=6)                # throw
bheemu.move(90, 100, 'elastic', sy=1.0, sx=1.0, rot=0, armL=BASE)
dos.set(88, x=px + 40, y=py - 90)
arc(dos, 88, 110, TX, G0 - 242, 520, spin=720)
bheemu.move(88, 96, 'out', pitch=-0.8, yaw=0.0); bheemu.move(96, 108, 'io', pitch=0.1, yaw=0.75, pupil=(0.8, 0.2))
dos.set(110, rot=0, sy=0.55, sx=1.3, z=2); dos.move(111, 118, 'elastic', sy=1.0, sx=1.0)
for i, f in enumerate(range(110, 118)):
    plt.set(f, rot=(4 if i % 2 == 0 else -4) * (1 - i / 8))
plt.set(118, rot=0)
sc.hit(86, 'whoosh', 0.6, d=0.25); sc.slide(88, 67, 93, 11, 0.45); sc.slide(99, 93, 67, 11, 0.45)
sc.hit(110, 'pop', 0.9); sc.hit(110, 'manjira', 0.7)
bheemu.move(112, 116, 'over', happy=1.0, eye_open=0.0, smile=1.0, mouth_w=1.3, sx=1.04, sy=1.02, pitch=0.0)   # proud
for f in (120, 132):
    bheemu.move(f, f + 3, 'out', head_dy=10); bheemu.move(f + 3, f + 8, 'over', head_dy=0)
    sc.note(f + 3, veena, 74 if f == 120 else 78, 0.4, 0.6)
bheemu.move(144, 148, 'io', eye_open=1.0, happy=0.0, smile=0.6, mouth_w=1.0, sx=1.0, sy=1.0)
look(bheemu, 146, yaw=-0.7, pupil=(-0.4, 0.2))
bob(bheemu, 156, 286)

# ------------------------------------------------------------------ 2. the thief: a trunk comes up like a periscope  (f156-240)
sc.raga(156, 288, 'sneak')
gaju.set(150, show=1.0, sy=0.7, sx=1.05, ear=-1.0, trunk=(0, 10), trunk_curl=0.2, yaw=-0.4, pupil=(-0.6, 0))
gaju.move(156, 168, 'out', trunk=(4, -250), trunk_curl=-0.9)
sc.slide(156, 55, 74, 12, 0.5)
for f in (172, 180):                                # sniff, sniff
    gaju.move(f, f + 2, 'snap', trunk=(-30, -262)); gaju.move(f + 2, f + 6, 'over', trunk=(4, -250))
    sc.hit(f, 'sniff', 0.9)
gaju.move(186, 190, 'over', trunk=(-60, -226), trunk_curl=-1.0)                    # points at the dosa
sc.hit(187, 'ghatam', 0.8, note=69)
gaju.move(194, 202, 'over', y=G0 - 84, sy=1.0, sx=1.0, ear=0.0, trunk=(-60, -90))  # eyes rise over the table edge
sc.slide(194, 60, 67, 7, 0.35)
gaju.move(206, 208, 'snap', pupil=(-0.95, 0.0)); sc.note(206, veena, 50, 0.4, 0.8)   # checks on Bheemu
gaju.move(214, 216, 'snap', pupil=(-0.7, 0.55)); sc.note(214, veena, 53, 0.4, 0.8)   # looks at the dosa
for f in (220, 230):                                # eyebrow waggle
    gaju.move(f, f + 3, 'snap', brow=13, brow_asym=0.6); gaju.move(f + 4, f + 8, 'out', brow=0, brow_asym=0.0)
    sc.hit(f, 'ghatam', 0.6, note=74)

# ------------------------------------------------------------------ 3. sneak and snatch  (f240-288)
hx, hy = st.probe(238, gaju, 'head')
goal = (TX + 38 - hx, (G0 - 250) - (hy + 6))
cur = (-60, -90)
for i, f in enumerate((240, 248, 256)):              # three tiptoe reaches: move 3, hold 5
    k = (i + 1) / 3
    gaju.move(f, f + 3, 'snap', trunk=(cur[0] + (goal[0] - cur[0]) * k, cur[1] + (goal[1] - cur[1]) * k), trunk_curl=0.4)
    sc.note(f, xylo, 78 + i * 2, 0.2, 0.7)
dos.attach(262, 498, gaju, 'trunk', -10, 6)
gaju.move(262, 264, 'snap', trunk_curl=1.0, pupil=(-0.95, -0.1))                    # got it... is he looking?
sc.hit(262, 'manjira', 0.5)
dos.set(269, z=-0.5)
gaju.move(268, 271, 'in', y=G0, sy=0.62, sx=1.1, ear=-1.0, trunk=(20, 30))          # zip down out of sight
tbl.set(270, sx=TS * 1.04, sy=0.97); tbl.move(271, 280, 'elastic', sx=TS, sy=1.0)
sc.hit(267, 'zip', 0.7, d=0.16)
gaju.set(276, x=TX, pupil=(0, 0), yaw=0.0, trunk=(34, 34), trunk_curl=0.9, sy=0.88, sx=1.05, ear=-0.6, happy=1.0, eye_open=0.0, smile=0.9)
dos.set(276, bite=0.5)
gaju.set(277, show=0.0); dos.set(277, show=0.0)     # fully hidden until the table is lifted
gaju.set(404, show=1.0); dos.set(404, show=1.0)

# ------------------------------------------------------------------ 4. slow burn and take  (f288-420)
cam.move(288, 304, 'io', x=700, y=cy(1.35, 60), zoom=1.35)
bheemu.move(288, 292, 'over', yaw=0.7, face=0.25, pupil=(0.8, 0.25), smile=0.9)        # turns to admire his dosa
bheemu.move(296, 298, 'out', smile=0.0, mouth_w=0.7)                                # ...the plate is empty
blink(bheemu, 300)                                                                  # held pose, one blink
f = take(st, bheemu, 308, 1.0)
sc.note(311, veena, 50, 0.8, 1.0); sc.note(311, veena, 57, 0.8, 0.8); sc.hit(311, 'timp', 0.9)
sc.note(311, tabla, 'dha', 0.4, 1.0) if False else sc._add(sc.fx, 311, tabla('dha', 1.2)); sc.hit(311, 'manjira', 0.8)
bheemu.move(328, 332, 'out', brow_ang=16, lid=0.25, smile=-0.6, brow=0)
pn.set(331, x=BX, y=BY)                                                            # throws the pan over his shoulder
bheemu.move(331, 334, 'snap', armL=(-40, -260), handL='open'); bheemu.move(334, 342, 'io', armL=(0, 0), bendL=0.14, handL='mitt')
arc(pn, 331, 345, -500, G0 - 100, 420, spin=-500)
sc.hit(331, 'whoosh', 0.5); sc.hit(348, 'crash', 0.5); st.shake(348, 8, 6)
look(bheemu, 336, yaw=-0.9, pupil=(-0.9, 0)); sc.hit(337, 'ghatam', 0.9, note=50)
look(bheemu, 348, yaw=0.9, pupil=(0.9, 0)); sc.hit(349, 'ghatam', 0.9, note=53)
for f in (360, 368, 376):                                                          # munch... munch... from under the table
    tbl.set(f, sy=1.07, sx=TS * 0.98); tbl.move(f + 1, f + 6, 'elastic', sy=1.0, sx=TS)
    plt.set(f, y=G0 - 252); plt.move(f + 1, f + 5, 'bounce', y=G0 - 228)
    sc.hit(f, 'munch', 1.0)
bheemu.move(362, 364, 'snap', pupil=(0.8, 0.6), yaw=0.6)
bheemu.move(366, 370, 'out', brow_ang=26, lid=0.32, smile=-0.9)
cam.move(376, 400, 'io', x=860, y=cy(1.15, 30), zoom=1.15)
for i, f in enumerate(walk(bheemu, 384, 404, 700, 10, 30)):
    sc._add(sc.fx, f, tabla('ge', 1.0))
GRAB = (-58, -76)
bheemu.move(404, 407, 'out', armR=GRAB, handR='fist', sy=0.94, sx=1.04)             # grabs the table edge, sinks
bheemu.move(408, 413, 'over', armR=(-32, -312), sy=1.0, sx=1.0)                     # and lifts it one-handed
tbl.move(408, 413, 'over', y=G0 - 215, rot=9); plt.move(408, 413, 'over', y=G0 - 215 - 228, x=TX + 36, rot=9)
sc.slide(408, 58, 77, 5, 0.5); sc.hit(413, 'pop', 0.8, note=60)
bheemu.move(414, 420, 'io', armL=(74, -96), bendL=0.5, handL='fist')                # other fist on his hip

# ------------------------------------------------------------------ 5. reveal  (f420-520)
chew(gaju, 404, 430, 6)
for f in (416, 422, 428):
    sc.hit(f, 'munch', 0.8)
gaju.move(430, 432, 'snap', eye_open=1.0, happy=0.0, pupil=(0.0, 0.0), cheeks=1.0, head_sx=1.0, head_sy=1.0, smile=0.0)   # freezes mid-chew
gaju.move(438, 440, 'snap', pupil=(-0.8, -0.8), yaw=-0.3)                                   # slowly looks up
sc.hit(438, 'ghatam', 0.6, note=62)
foot = 424
while foot < 492:                                                                             # Bheemu taps his foot
    bheemu.move(foot, foot + 3, 'out', footR=(0, 16)); bheemu.move(foot + 3, foot + 5, 'in', footR=(0, 0))
    sc._add(sc.fx, foot + 5, tabla('te', 0.9))
    foot += 10
gaju.move(450, 454, 'over', smile=1.0, mouth_w=1.6, brow=8, sweat=1.0, trunk=(60, 40))        # sheepish grin (trunk aside so we see it)
gaju.move(456, 464, 'over', trunk=(-96, -92), trunk_curl=-0.4)                               # offers what is left
sc.slide(456, 62, 69, 7, 0.3)
gaju.move(470, 473, 'snap', head_sy=1.25, head_sx=0.85); gaju.move(473, 476, 'snap', head_sy=0.84, head_sx=1.12, cheeks=0.0)
gaju.move(476, 482, 'elastic', head_sy=1.0, head_sx=1.0)
sc.hit(471, 'gulp', 1.0)
gaju.move(480, 482, 'out', trunk=(40, 30), trunk_curl=0.9, mouth_w=1.0, smile=0.3, pupil=(0.9, 0))
cam.move(476, 488, 'io', x=900, y=cy(1.05), zoom=1.05)
sc.raga(494, 610, 'chase')
gone = zip_off(st, gaju, 482, 2700, wind=9)
sc.run(485, 494, 62, 1, 0.5); sc.hit(494, 'zip', 1.0)
dos.set(gone, show=0.0)
bheemu.move(495, 498, 'snap', yaw=0.95, pupil=(0.9, 0), eye_pop=1.3, brow_ang=0, lid=0, brow=14, mouth_open=0.5, footR=(0, 0))
bheemu.move(500, 503, 'in', armR=(0, 0), handR='mitt', armL=(0, 0), bendL=0.14, handL='mitt')
tbl.move(500, 504, 'in', y=G0, rot=0); plt.move(500, 504, 'in', y=G0 - 228, x=TX, rot=0)
tbl.set(504, sy=0.9, sx=TS * 1.05); tbl.move(505, 512, 'elastic', sy=1.0, sx=TS)
sc.hit(504, 'bonk', 0.9, note=52); sc.hit(504, 'timp', 0.6); st.shake(504, 10, 6)
bheemu.move(503, 506, 'out', eye_pop=1.0, brow_ang=24, lid=0.2, mouth_open=0.0, smile=-0.8, brow=0)
gone_p = zip_off(st, bheemu, 506, 2800, wind=8)
sc.run(509, 517, 50, 1, 0.5); sc.hit(517, 'zip', 1.0)

# ------------------------------------------------------------------ 6. chase through the house  (f524-610)
C0 = 524
X0 = 1250
st.cut(C0, x=X0, y=cy(1.05), zoom=1.05)
tbl.set(C0, show=0.0); plt.set(C0, show=0.0)       # new angle: the table is behind us now
cam.move(C0, 596, 'lin', x=2640); cam.move(596, 608, 'out', x=2760)
spd = (2640 - X0) / (596 - C0)
gaju.set(C0, show=1.0, x=X0 + 270, y=G0, z=2, wheel=1.0, stride=30, rot=12, face=1, yaw=1, sy=1, sx=1, eye_pop=1.2, pupil=(0.7, 0),
          trunk=(60, 10), trunk_curl=-0.6, happy=0.0, eye_open=1.0, sweat=0.0, brow=6, smile=0.2, mouth_open=0.3, ear=0.0)
gaju.move(C0, 572, 'lin', x=X0 + 270 + spd * 48, step=gaju.value('step', C0) + 48 / 3)
bheemu.set(C0, show=1.0, x=X0 - 520, y=G0, wheel=1.0, stride=40, rot=14, face=1, yaw=1, scarf_fly=1.0, armR=(120, -150), armL=(90, -130), handR='open', handL='open',
          brow_ang=24, lid=0.15, smile=-0.6, mouth_open=0.35, eye_pop=1.0, pupil=(0.8, 0))
bheemu.move(C0, 572, 'lin', x=X0 + 270 + spd * 48 - 330, step=bheemu.value('step', C0) + 48 / 3)
for f in range(C0, 598, 3):
    sc._add(sc.fx, f, tabla('ge', 0.45))
look(gaju, 540, yaw=-0.9, pupil=(-0.9, 0)); gaju.move(541, 544, 'snap', eye_pop=1.5, brow=14, mouth_open=0.7)   # looks back: he is close!
look(gaju, 556, yaw=1.0, pupil=(0.7, 0)); gaju.move(556, 560, 'out', eye_pop=1.0, brow_asym=1.0, smile=1.0, mouth_open=0.0, mouth_w=1.3)   # an idea
gaju.set(572, wheel=0.0, stride=0.0)
FLY = G0 - 640                                       # vertical frame: he can go really high
gaju.move(572, 592, 'out', y=FLY, rot=0); gaju.move(572, 604, 'out', x=2640)
for fb in flap(gaju, 566, 640, 4):
    sc.hit(fb, 'flap', 0.5)
sc.slide(572, 62, 86, 18, 0.5)
mx = bheemu.value('x', 572)
bheemu.move(572, 578, 'lin', x=mx + spd * 6, step=bheemu.value('step', 572) + 2)
bheemu.set(578, wheel=0.0, stride=0.0)
bheemu.move(576, 579, 'out', sy=0.88, sx=1.08)
bheemu.move(579, 584, 'out', y=G0 - 190, rot=52, sy=1.12, sx=0.94, armR=(150, -260), armL=(120, -240), mouth_open=0.8, pitch=-0.5)   # dives... and misses
bheemu.move(584, 590, 'in', y=G0, rot=14, sy=1.0, sx=1.0)
bheemu.move(579, 590, 'lin', x=mx + spd * 6 + 28 * 11)
sc.hit(578, 'whoosh', 0.8, d=0.4)
squash(bheemu, 590, 0.16, 6)
bheemu.set(590, wheel=1.0, stride=40, armR=(70, -90), armL=(50, -70), mouth_open=0.3, pitch=0.0)
x590 = bheemu.value('x', 590)
bheemu.move(590, 598, 'lin', x=x590 + 22 * 8, step=bheemu.value('step', 590) + 8 / 3)
look(bheemu, 590, yaw=-0.6, pupil=(-0.6, -0.8))                    # looks up and back at Gaju...
look(bheemu, 595, yaw=1.0, pupil=(0.9, 0))                         # ...then ahead. Fridge!
bheemu.move(597, 599, 'snap', eye_pop=1.6, brow=20, brow_ang=0, lid=0, mouth_open=0.9, mouth_w=0.8, pupil_s=0.55)
sc.duck(596, 612, 0.4)
bheemu.set(599, wheel=0.0, stride=0.0)
bheemu.move(599, 602, 'snap', rot=-22, footL=(70, 0), footR=(96, 0), armR=(-40, -250), armL=(-70, -230))
IMP = 610
bheemu.move(599, IMP, 'lin', x=2850)
sc.hit(599, 'skid', 1.0, d=0.45)
for f in (600, 603, 606):
    puffs(st, f, bheemu.value('x', f) + 90, G0, n=3, size=30, spread=40, life=9, dirx=1)

# ------------------------------------------------------------------ 7. the hit, the topper, the make-up  (f610-780)
bheemu.set(IMP, x=2874, rot=0, sx=0.36, sy=1.22, face=1, yaw=0.0, armR=(40, -330), armL=(-40, -330), handR='open', handL='open', footL=(0, 0), footR=(0, 0),
          eye_open=0.0, eye_pop=1.0, pupil_s=1.0, mouth_open=0.0, smile=-0.4, mouth_w=1.2, brow=0, scarf_fly=0.0, glasses_rot=16, glasses_dy=10)
stars(st, IMP, 2930, G0 - 360, n=7, r=210, life=14)
st.shake(IMP, 34, 12)
sc.hit(IMP, 'crash', 1.0); sc.hit(IMP, 'bonk', 1.0, note=50); sc._add(sc.fx, IMP, tabla('dha', 1.4))
frg.set(IMP, rot=3.5); frg.move(IMP + 1, IMP + 16, 'elastic', rot=0)
shake(bheemu, IMP + 1, IMP + 7, 5)
bheemu.move(IMP + 14, IMP + 24, 'io', rot=-12, sx=0.5); sc.slide(IMP + 14, 76, 55, 12, 0.5)       # peels off...
SIT = IMP + 30
bheemu.move(IMP + 24, SIT, 'in', x=2760, rot=0, sx=1.1, sy=0.86, face=0, yaw=0, armR=(0, 0), armL=(0, 0), handR='mitt', handL='mitt')
bheemu.set(SIT, sit=1.0)                                                                      # ...and sits down hard, like a real panda
bheemu.move(SIT, SIT + 10, 'elastic', sx=1.0, sy=1.0)
sc.hit(SIT, 'timp', 0.9, note=36); sc._add(sc.fx, SIT, tabla('ge', 1.3)); st.shake(SIT, 12, 6)
puffs(st, SIT, 2760, G0, n=5, size=40, spread=150, life=14)
bheemu.set(SIT, eye_open=1.0, pupil_s=0.5, smile=-0.2, mouth_open=0.12, mouth_w=0.8, brow_ang=-10)
for i, f in enumerate(range(SIT, SIT + 44, 2)):                  # dazed: eyes roll, head wobbles
    a = i * 0.9
    bheemu.set(f, pupil=(math.cos(a) * 0.8, math.sin(a) * 0.8), head_rot=math.sin(a * 0.5) * 7)


def dizzy(g, f, f0=SIT, f1=SIT + 46):
    if f0 <= f < f1:
        hx_, hy_ = bheemu.anchors.get('top', (2760, G0 - 500))
        for i in range(4):
            a = f * 0.42 + i * math.pi / 2
            cx, cy_ = hx_ + math.cos(a) * 110, hy_ - 26 + math.sin(a) * 26
            pts = []
            for k in range(10):
                t = math.radians(k * 36 + f * 10)
                r = 20 if k % 2 == 0 else 9
                pts.append((cx + math.cos(t) * r, cy_ + math.sin(t) * r))
            g.shape(poly(pts), (255, 222, 70), True, 4, (58, 42, 40), a=min(1, (f1 - f) / 6))


st.fx.append(dizzy)
for i, f in enumerate(range(SIT + 2, SIT + 42, 5)):
    sc.note(f, xylo, 98 - (i % 4) * 2, 0.15, 0.3)

# Gaju laughs up above, then his ears get tired
gaju.move(606, 612, 'out', yaw=0.0, face=0.0, pupil=(0.6, 0.9), trunk=(40, 30), trunk_curl=0.9)
gaju.move(614, 618, 'over', happy=1.0, eye_open=0.0, mouth_open=0.9, mouth_w=1.4, smile=1.0, trunk=(60, -70), trunk_curl=-0.8)
for f in range(618, 640, 4):                                    # laugh bounce
    gaju.move(f, f + 2, 'out', y=FLY - 16, sy=1.05); gaju.move(f + 2, f + 4, 'in', y=FLY, sy=0.96)
    sc.note(f, bansuri, 86 - (f - 618) // 4, 0.09, 0.5)
DROP = 646
gaju.move(640, 644, 'out', ear=-0.5, eye_open=1.0, happy=0.0, mouth_open=0.0, smile=-0.3, mouth_w=0.8, pupil=(0, 0.9), sy=1.0, sweat=1.0, trunk=(30, 60), trunk_curl=0.6)
sc.slide(640, 80, 70, 5, 0.4)
gaju.move(644, DROP, 'snap', pupil=(0, 0), brow=12, eye_pop=1.3)                 # hangs in the air for a moment: he knows
gaju.move(DROP, DROP + 3, 'out', ear=1.0, sy=1.2, sx=0.88)                       # ears shoot up as he falls
topx, topy = st.probe(DROP, bheemu, 'top')
gaju.move(DROP, DROP + 10, 'in', y=topy + 14, x=2760)
sc.slide(DROP, 86, 50, 10, 0.6)
LAND = DROP + 10                                                # lands on Bheemu's head
gaju.set(LAND, z=5, sy=0.6, sx=1.3, eye_pop=1.0, sweat=0.0, ear=0.2)
bheemu.set(LAND, head_sy=0.6, head_sx=1.25, head_dy=34, head_rot=0, eye_open=0.0, pupil=(0, 0), pupil_s=1.0)
bheemu.move(LAND + 3, LAND + 12, 'elastic', head_sy=1.0, head_sx=1.0, head_dy=0)
sc.hit(LAND, 'bonk', 1.0, note=60); sc.hit(LAND, 'boing', 0.9, note=52); st.shake(LAND, 12, 6)
stars(st, LAND, 2760, topy, n=5, r=110, life=10)
gaju.move(LAND + 2, LAND + 4, 'out', sy=1.15, sx=0.9)
arc(gaju, LAND + 2, LAND + 16, 2520, G0, 220)                   # bounces off and lands beside him
gaju.move(LAND + 4, LAND + 14, 'io', sy=1.0, sx=1.0, face=0.5, yaw=0.7, ear=0.0)
squash(gaju, LAND + 16, 0.28, 9)
sc.hit(LAND + 16, 'pop', 0.8, note=55)
puffs(st, LAND + 16, 2520, G0, n=3, size=26, spread=60, life=10)

# make-up: Gaju offers the last bite
M0 = LAND + 28
sc.raga(M0, M0 + 66, 'sweet', v=0.9)
CZ = 1.35
cam.move(M0 - 8, M0 + 14, 'io', x=2650, y=cy(CZ, 30), zoom=CZ)
bheemu.move(M0 - 6, M0, 'io', eye_open=1.0, brow_ang=22, lid=0.3, smile=-0.8, mouth_open=0.0, mouth_w=1.0, yaw=-0.5, pupil=(-0.8, 0.3), glasses_rot=8, glasses_dy=6)
gaju.move(M0 - 4, M0, 'over', pupil=(0.7, -0.6), brow_ang=-18, smile=-0.3, sweat=1.0, ear=-0.35)                       # sorry face
dos.set(M0, show=1.0, z=6, bite=0.62, rot=0)
dos.attach(M0, M0 + 40, gaju, 'trunk', 6, -2)
hx, hy = st.probe(M0, gaju, 'head'); mx_, my_ = st.probe(M0, bheemu, 'mouth')
gaju.move(M0 + 4, M0 + 14, 'over', trunk=(mx_ - hx - 50, my_ - hy - 12), trunk_curl=-0.3)
sc.slide(M0 + 4, 62, 72, 9, 0.3)
for f in (M0 + 18, M0 + 25):                                    # Bheemu sniffs it
    bheemu.move(f, f + 2, 'snap', head_dy=6, head_dx=-6); bheemu.move(f + 2, f + 5, 'out', head_dy=0, head_dx=0)
    sc.hit(f, 'sniff', 0.8)
bheemu.move(M0 + 28, M0 + 34, 'io', brow_ang=-6, lid=0.0, smile=0.0)                                                     # the anger melts
bheemu.move(M0 + 36, M0 + 38, 'snap', mouth_open=1.0, mouth_w=1.3, head_dx=-22)
bheemu.move(M0 + 40, M0 + 42, 'snap', mouth_open=0.0, head_dx=0)
dos.set(M0 + 40, show=0.0)
sc.hit(M0 + 40, 'munch', 1.0)
gaju.move(M0 + 40, M0 + 46, 'out', trunk=(60, 40), trunk_curl=0.9, sweat=0.0)
for f in range(M0 + 42, M0 + 58, 5):
    bheemu.move(f, f + 2, 'out', mouth_open=0.2, head_sy=0.96); bheemu.move(f + 2, f + 5, 'in', mouth_open=0.0, head_sy=1.02)
    sc.hit(f + 2, 'munch', 0.5)
bheemu.move(M0 + 58, M0 + 62, 'over', smile=1.0, mouth_w=1.4, happy=1.0, eye_open=0.0, brow_ang=0, head_sy=1.0, glasses_rot=0, glasses_dy=0, yaw=-0.2)
gaju.move(M0 + 60, M0 + 64, 'over', happy=1.0, eye_open=0.0, smile=1.0, mouth_w=1.3, brow_ang=0, ear=0.3, pupil=(0, 0))
gaju.move(M0 + 62, M0 + 70, 'io', x=2580, rot=10)                                                                       # leans on his friend
flap(gaju, M0 + 64, M0 + 80, 4, 0.35)
END = M0 + 70
sc.hit(END - 25, 'tihai', 0.9)                                   # the drum cadence lands exactly on END
icx = W / 2 + (2670 - 2650) * CZ
icy = H / 2 + (G0 - 250 - cy(CZ, 30)) * CZ
iris(st, END + 8, END + 26, icx, icy, closing=True)

if __name__ == '__main__':
    print('frames', TOTAL, dict(IMP=IMP, SIT=SIT, LAND=LAND, M0=M0, END=END))
    out = os.path.join(HERE, 'out'); os.makedirs(out, exist_ok=True)
    mode = sys.argv[1] if len(sys.argv) > 1 else 'final'
    if mode == 'sheet':
        frames = [int(x) for x in sys.argv[2].split(',')]
        st.sheet(frames, os.path.join(out, sys.argv[3] if len(sys.argv) > 3 else 'sheet.png'), cols=6, scale=0.3)
    else:
        wav = sc.write(os.path.join(out, 'audio.wav'))
        scale = 0.5 if mode == 'preview' else 1.0
        st.render(os.path.join(out, 'ep01_raw%s.mp4' % ('_preview' if mode == 'preview' else '')), audio=wav, scale=scale)
