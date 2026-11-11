"""ANIMATIC for the pilot "One More Page" (Bheemu & Gaju, vertical, about 25 s).

THIS IS AN ANIMATIC, NOT ANIMATION. Key poses pop from one to the next so that shot order, shot
length and the pauses can be judged in real time with scratch sound. It uses only the approved
production models, the existing presets in show.py, existing props and existing engine controls.
No engine file, model, preset or baseline is changed. Detailed animation starts only after
Harshith has reviewed this (gate B in cartoon-animation-director/knowledge/Production_Pipeline.md).

Run:  python3 animatic.py board     writes ../storyboard/board.png (one panel per shot beat)
      python3 animatic.py hookups   writes ../storyboard/hookups.png (frame before and after each cut)
      python3 animatic.py render    writes one_more_page_animatic_v001.mp4 (half size) beside this file
"""
import os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', '..', '..', 'engine'))
from toon import GROUND, W, H
from chars import Bheemu, Gaju
from cast import Chintu
from scene import Painted, Prop, book
from india import telugu
from sets import courtyard, SKY
from acting import blink, walk, arc, flap
from voice import speak
from show import Show, ball, CALM, HAPPY, LAUGH, SHOCK, SORRY, SLY

G0 = GROUND
T = 36                                   # the title card that every episode has
TOTAL = T + 552 + 34
ep = Show(11, 'One More Page', 'one_more_page', TOTAL, Painted(2700, courtyard, top=SKY, bottom=(170, 150, 130)))
st, sc, cam = ep.st, ep.sc, ep.cam
BX, GX, CX = 520, 930, 1140              # home positions: Bheemu left, Gaju right, Chintu far right (later)
MID = 725

bheemu = Bheemu(x=BX, z=2, face=0.0); gaju = Gaju(x=1500, z=3, face=-1, yaw=-0.8); chintu = Chintu(x=1700, z=1, show=0.0, face=-1, yaw=-0.7)
bk = Prop(book, z=4, sx=1.8, sy=1.8); bl = Prop(ball, z=5)
st.add(bheemu, gaju, chintu, bk, bl)
READ = dict(armL=(70, -150), armR=(-70, -150), handL='grip', handR='grip')        # both hands hold the book at the chest
EYES_DOWN = dict(pupil=(0.0, 0.8), lid=0.25, smile=0.3)
BOOK_AT = (0, -40)                        # book offset from Bheemu's belly anchor
SHOTS = []                                # (first frame, name, size, note) for the burn-in and the board


def shot(t, name, size, x, z, up=0, note=''):
    ep.shot(T + t, x, z, up)
    SHOTS.append((T + t, name, size, note))


def P(a, t, n=2, ease='snap', **kw):      # pop to a pose over n frames, starting at film-relative time t
    a.move(T + t, T + t + n, ease, **kw)


# ------------------------------------------------------------ start state
bheemu.set(0, **CALM); bheemu.set(0, **READ); bheemu.set(0, **EYES_DOWN)
bk.attach(0, T + 372, bheemu, 'belly', *BOOK_AT)
gaju.set(0, **HAPPY); gaju.set(0, trunk=(-10, -150), trunk_curl=-0.5)
bl.attach(0, T + 60, gaju, 'trunk', 0, -26)
sc.raga(T, T + 196, 'calm', v=0.8)

# ------------------------------------------------------------ S1 wide: he reads; Gaju arrives with a ball  (0-59)
shot(0, 'S1', 'WIDE', MID, 1.1, note='Bheemu reads. Gaju arrives with a ball and wants to play')
for f in walk(gaju, T + 4, T + 34, GX, 8, 30):
    ep.tap(f, 'na', 0.5)
P(gaju, 36, 3, yaw=-0.6, pupil=(-0.8, 0.0)); P(gaju, 42, 3, 'over', sy=1.08, sx=0.95, ear=0.6); P(gaju, 48, 4, 'io', sy=1.0, sx=1.0, ear=0.0)   # "look!"
blink(bheemu, T + 50)                                                         # the only thing Bheemu does

# ------------------------------------------------------------ S2 full on Gaju: attempt 1, two small bounces  (60-107)
shot(60, 'S2', 'FULL', GX + 10, 2.2, note='Attempt 1: two neat bounces. He looks across, hopeful')
gaju.set(T + 60, face=0.0, yaw=-0.3, trunk=(-120, 40), trunk_curl=0.3, **CALM)
bl.set(T + 60, x=GX - 170, y=G0 - 150)
for t0, n, h in ((62, 12, 150), (76, 14, 150)):
    bl.move(T + t0, T + t0 + n // 2, 'in', y=G0 - 24); bl.move(T + t0 + n // 2, T + t0 + n, 'out', y=G0 - 24 - h)
    ep.tap(T + t0 + n // 2, 'ge', 0.7)
bl.attach(T + 90, T + 187, gaju, 'trunk', 0, -26)
P(gaju, 90, 2, trunk=(-90, -60), trunk_curl=-0.3); P(gaju, 94, 3, yaw=-0.8, pupil=(-0.9, 0.0), **HAPPY)     # caught it; "did you see?"
sc.hit(T + 90, 'pop', 0.5, note=79)

# ------------------------------------------------------------ S3 medium close on Bheemu: he turns a page  (108-131)
shot(108, 'S3', 'MED CLOSE', BX, 2.8, up=230, note='No reaction. He turns a page')
P(bheemu, 114, 2, armR=(-40, -175)); P(bheemu, 118, 3, 'io', armR=(-70, -150)); sc.hit(T + 116, 'ghatam', 0.5)
P(bheemu, 122, 2, pupil=(0.3, 0.8)); P(bheemu, 126, 2, pupil=(-0.3, 0.8))                              # eyes travel along the line

# ------------------------------------------------------------ S4 wide: attempt 2 (bigger), then attempt 3 (far too hard)  (132-203)
shot(132, 'S4', 'WIDE', MID, 1.1, note='Attempt 2: hopping, ears flapping. The book goes up. Attempt 3: far too hard')
gaju.set(T + 132, yaw=-0.6, pupil=(-0.8, 0.0), trunk=(0, -230), trunk_curl=-0.6)
for t0 in (134, 146, 158):                                                    # three hops, ball held high
    gaju.move(T + t0, T + t0 + 5, 'out', y=G0 - 70, sy=1.08, sx=0.95); gaju.move(T + t0 + 5, T + t0 + 10, 'in', y=G0, sy=0.9, sx=1.08)
    gaju.move(T + t0 + 10, T + t0 + 12, 'out', sy=1.0, sx=1.0); ep.tap(T + t0 + 10, 'ge', 0.8)
for f in flap(gaju, T + 134, T + 168, 4, 0.9):
    sc.hit(f, 'flap', 0.35)
P(gaju, 168, 2, ear=0.0)
P(bheemu, 150, 3, 'out', armL=(60, -330), armR=(-60, -330)); bk.set(T + 150, sy=1.8)                    # without looking, the book rises between them
bk.attach(T + 150, T + 240, bheemu, 'belly', 0, -230)
P(gaju, 172, 3, sy=1.0, sx=1.0, yaw=-0.2, pupil=(-0.6, 0.0), ear=-0.5, smile=-0.2, happy=0.0, eye_open=1.0)   # hm.
P(gaju, 182, 6, 'out', sy=0.8, sx=1.2, trunk=(0, -120), trunk_curl=-0.2, brow_ang=14)                 # wind-up
P(gaju, 188, 2, sy=1.12, sx=0.92, trunk=(-30, 60), trunk_curl=0.4)                                    # throws it down, hard
bl.set(T + 188, x=GX - 60, y=G0 - 250); bl.move(T + 188, T + 190, 'in', y=G0 - 24, sy=0.6, sx=1.4)
sc.hit(T + 190, 'boing', 0.9); sc.slide(T + 190, 60, 96, 12, 0.5)
bl.move(T + 190, T + 198, 'out', y=-500, x=BX + 60, sy=1.2, sx=0.9)                                   # gone, drifting over Bheemu
P(gaju, 192, 3, 'over', sy=1.0, sx=1.0, pupil=(-0.4, -1.0), head_dy=-12, **dict(SHOCK, mouth_open=0.4))
sc.duck(T + 198, T + 268, 0.08)

BELLY_Y = st.probe(T + 100, bheemu, 'belly')[1]      # where his belly anchor is, read with the existing probe
# ------------------------------------------------------------ S5 wide, more sky: the wait; Gaju gives up; the ball comes back  (204-283)
shot(204, 'S5', 'WIDE HIGH', MID, 1.0, note='The wait. Gaju gives up and sulks. Bheemu finally peeks. Then the ball lands on the open book')
P(gaju, 222, 4, 'io', pupil=(0.0, 0.0), head_dy=0, **CALM)                                              # nothing came down
P(gaju, 232, 5, 'io', sy=0.93, sx=1.05, ear=-0.9, yaw=0.3, pupil=(0.5, 0.6), trunk=(30, 92), trunk_curl=0.7, **SORRY); gaju.set(T + 232, sweat=0.0)   # sulks, turns away
sc.hit(T + 234, 'ghatam', 0.4)
P(bheemu, 240, 4, 'io', armL=(70, -150), armR=(-70, -150)); bk.attach(T + 240, T + 372, bheemu, 'belly', *BOOK_AT)   # the book comes down
P(bheemu, 248, 3, 'io', pupil=(0.9, 0.3), lid=0.1, yaw=0.3)                                            # his first look at Gaju
P(bheemu, 256, 3, 'io', smile=0.6)                                                                     # he softens...
bl.set(T + 262, x=BX, y=G0 - 1560, sy=1.0, sx=1.0)
bl.move(T + 262, T + 268, 'in', y=BELLY_Y - 100, sy=1.2, sx=0.88)                                          # ...and the ball arrives. Contact on an even engine frame
bl.set(T + 268, sy=0.72, sx=1.28); bk.set(T + 268, sy=0.8); bheemu.set(T + 268, sy=0.94, sx=1.05, head_dy=8, pupil=(0.0, 0.8), yaw=0.0, eye_pop=1.3, lid=0.0, smile=0.0)
sc.hit(T + 268, 'pop', 1.0, note=67)                                                                   # the book snaps shut: alone on its frame
bl.move(T + 270, T + 274, 'out', sy=1.0, sx=1.0); bheemu.move(T + 270, T + 278, 'elastic', sy=1.0, sx=1.0, head_dy=0)
bl.attach(T + 270, T + 372, bheemu, 'belly', 0, -100)
P(gaju, 268, 2, yaw=-0.7, pupil=(-0.9, 0.0), ear=0.8, **SHOCK)

# ------------------------------------------------------------ S6 medium close on Bheemu: the slow burn  (284-331)
shot(284, 'S6', 'MED CLOSE', BX, 2.6, up=210, note='Slow burn: the ball, a blink, then across to Gaju')
P(bheemu, 284, 1, eye_pop=1.0, pupil=(0.0, 0.9), lid=0.3); sc.hit(T + 290, 'ghatam', 0.5)
blink(bheemu, T + 298)
P(bheemu, 308, 6, 'io', pupil=(0.9, 0.2)); sc.hit(T + 310, 'ghatam', 0.5)
P(bheemu, 318, 6, 'io', yaw=0.5, brow_ang=8); sc.hit(T + 320, 'ghatam', 0.45)

# ------------------------------------------------------------ S7 medium on Gaju: guilt  (332-355)
shot(332, 'S7', 'MEDIUM', GX, 3.0, up=0, note='Guilt: ears down, the smallest wave of the trunk')
P(gaju, 332, 1, ear=-0.9, sy=0.94, sx=1.04, yaw=-0.5, pupil=(-0.8, 0.2), **SORRY)
P(gaju, 338, 3, 'io', trunk=(-60, -40), trunk_curl=-0.4); P(gaju, 344, 3, 'io', trunk=(-40, -60)); P(gaju, 348, 3, 'io', trunk=(-60, -40))
sc.note(T + 338, __import__('sound').bansuri, 72, 0.3, 0.4)

# ------------------------------------------------------------ S8 wide: the reversal. Bheemu can do it too  (356-451)
shot(356, 'S8', 'WIDE', MID, 1.1, note='Reversal: Bheemu puts the book down and bounces the ball, well. They play')
sc.raga(T + 362, T + 552, 'sweet', v=0.8)
P(bheemu, 360, 4, 'io', yaw=0.0, brow_ang=0, pupil=(0.0, 0.5), smile=0.5, lid=0.0)
bk.set(T + 372, x=BX - 215, y=G0 - 20, rot=-90, sy=1.8)                                               # the book is set down on the floor, flat
P(bheemu, 368, 4, 'io', armL=(0, 0), handL='mitt', armR=(-40, -150), handR='grip')
bl.attach(T + 372, T + 380, bheemu, 'handR', 0, -20)
bl.set(T + 380, x=BX + 125, y=G0 - 300)
for t0 in (380, 392):                                                         # two calm, expert bounces
    bl.move(T + t0, T + t0 + 6, 'in', y=G0 - 24); bl.move(T + t0 + 6, T + t0 + 12, 'out', y=G0 - 300); ep.tap(T + t0 + 6, 'ge', 0.9)
    P(bheemu, t0, 6, 'in', armR=(90, -90)); P(bheemu, t0 + 6, 6, 'out', armR=(90, -140))
P(gaju, 384, 3, 'over', sy=1.1, sx=0.93, ear=0.9, yaw=-0.6, pupil=(-0.8, 0.0), **dict(SHOCK, mouth_open=0.5))   # a take: he is GOOD at this
P(gaju, 396, 4, 'io', sy=1.0, sx=1.0, ear=0.3, **HAPPY)
P(bheemu, 404, 2, yaw=0.5, pupil=(0.8, 0.0), smile=0.9)                                                # "your turn"
arc(bl, T + 406, T + 420, GX - 40, G0 - 300, 240); sc.hit(T + 406, 'whoosh', 0.4)
P(gaju, 416, 3, trunk=(-40, -230), trunk_curl=-0.6); sc.hit(T + 420, 'pop', 0.6, note=76)
arc(bl, T + 422, T + 436, BX + 125, G0 - 300, 260)
P(bheemu, 432, 3, armR=(90, -140)); sc.hit(T + 436, 'pop', 0.6, note=72)
bl.attach(T + 436, T + 520, bheemu, 'handR', 0, -20)
P(gaju, 438, 3, trunk=(30, 92), trunk_curl=0.7, **LAUGH); P(bheemu, 438, 3, **HAPPY)

# ------------------------------------------------------------ S9 wide, shifted right: Chintu wants his ball back  (452-551)
shot(452, 'S9', 'WIDE', MID + 130, 1.0, note='Chintu: "Bheemu! Give the ball!" It was his. They give it back. Bheemu returns to his page')
chintu.set(T + 452, show=1.0)
for f in walk(chintu, T + 452, T + 474, CX, 8, 28):
    ep.tap(f, 'na', 0.6)
P(chintu, 474, 2, armL=(-20, -150), handL='open')                                                      # hand out
e = speak(ep, chintu, T + 476, 'c_ball')                                                               # generated Telugu voice: not approved until heard
P(bheemu, 478, 3, yaw=0.6, pupil=(0.9, 0.0), happy=0.0, eye_open=1.0, smile=0.2); P(gaju, 478, 3, yaw=0.7, pupil=(0.9, 0.0), ear=0.5, **CALM)
P(bheemu, 494, 4, 'io', pupil=(0.5, 0.6)); P(bheemu, 502, 4, 'io', pupil=(0.9, 0.0)); P(gaju, 500, 3, **SORRY)   # the ball... the boy... ah
arc(bl, T + 520, T + 534, CX - 50, G0 - 250, 200); sc.hit(T + 520, 'whoosh', 0.35)                     # a gentle underhand return
P(bheemu, 518, 2, armR=(110, -200)); P(bheemu, 524, 6, 'io', armR=(0, 0), handR='mitt', yaw=0.0, pupil=(0.0, 0.0), **CALM)
bl.attach(T + 534, TOTAL, chintu, 'handL', 0, -20); sc.hit(T + 534, 'pop', 0.6, note=79)
P(chintu, 536, 3, 'over', sy=1.06, sx=0.96, **HAPPY); P(chintu, 542, 4, 'io', sy=1.0, sx=1.0)
P(gaju, 536, 3, yaw=-0.6, pupil=(-0.8, 0.0), trunk=(-150, 30), trunk_curl=0.2, ear=0.2, **HAPPY)       # Gaju points at the book: "one more page?"
P(bheemu, 542, 4, 'io', yaw=-0.4, pupil=(-0.8, 0.6), smile=0.8)                                        # he looks at it. Yes.
END = T + 552
ep.close(END, BX - 120, G0 - 200)


# ------------------------------------------------------------ burn-in: this must never be mistaken for animation
def burn(g, f):
    cur = [s for s in SHOTS if s[0] <= f]
    telugu(g, 'ANIMATIC  -  timing rough, not animation', W / 2, 150, 34, (255, 255, 255), 'NTR', outline=(40, 30, 30))
    if cur and f >= T:
        s = cur[-1]
        telugu(g, '%s  %s   film frame %d' % (s[1], s[2], f + 1), W / 2, 200, 34, (255, 240, 120), 'NTR', outline=(40, 30, 30))


st.overlays.append(burn)

if __name__ == '__main__':
    mode = sys.argv[1] if len(sys.argv) > 1 else 'board'
    sb = os.path.join(HERE, '..', 'storyboard')
    if mode == 'board':
        frames = [T + t for t in (20, 46, 70, 96, 116, 142, 160, 186, 194, 236, 256, 266, 268, 300, 322, 346, 386, 412, 440, 486, 504, 528, 548)]
        st.sheet(frames, os.path.join(sb, 'board.png'), cols=6, scale=0.3)
        print('board frames (engine):', frames)
    elif mode == 'hookups':
        cuts = [s[0] for s in SHOTS[1:]]
        st.sheet([x for c in cuts for x in (c - 1, c)], os.path.join(sb, 'hookups.png'), cols=8, scale=0.22)
        print('cuts at engine frames:', cuts)
    elif mode == 'render':
        wav = sc.write(os.path.join(HERE, 'scratch_audio.wav'))
        st.render(os.path.join(HERE, 'one_more_page_animatic_v001.mp4'), audio=wav, scale=0.5)
    print('shots:', [(s[1], s[0] + 1, s[2]) for s in SHOTS], 'total frames', TOTAL)
