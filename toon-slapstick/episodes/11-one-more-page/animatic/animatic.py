"""ANIMATIC for the pilot "One More Page" (Bheemu & Gaju, vertical, about 25 s).

THIS IS AN ANIMATIC, NOT ANIMATION. Key poses pop from one to the next so that shot order, shot
length and the pauses can be judged in real time with scratch sound. It uses only the approved
production models, the existing presets in show.py, existing props and existing engine controls.
No engine file, model, preset or baseline is changed. Detailed animation starts only after
Harshith has reviewed this (gate B in cartoon-animation-director/knowledge/Production_Pipeline.md).

Run:  python3 animatic.py board     writes ../storyboard/board.png (one panel per shot beat)
      python3 animatic.py hookups   writes ../storyboard/hookups.png (frame before and after each cut)
      python3 animatic.py render    writes one_more_page_animatic_v002.mp4 (half size) beside this file

Version 002 (2026-11-11), after the hold at the animatic gate: wait shortened from 58 to 42 frames; the ball's
return in view for 10 frames with a soft falling note; gentler landing (no squash of Bheemu); the reveal of his
skill in its own full shot; one pass instead of two; the book stays in his hand (never on the floor at the frame
edge); bent-arm offer; Chintu's line plays over stillness, then a pause, then Gaju passes the ball to Bheemu.
Version 001 is the committed v001 file and this script's previous revision in Git.
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
from voice import load as _load_line
from sound import SR
LINE_END = 452 + int(len(_load_line('c_ball')) / SR * 24)      # where Chintu's line ends, so that nothing overlaps it
TOTAL = T + LINE_END + 8 + 88 + 34
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
bk.attach(0, T + 150, bheemu, 'belly', *BOOK_AT)
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
bk.attach(T + 150, T + 228, bheemu, 'belly', 0, -230)
P(gaju, 172, 3, sy=1.0, sx=1.0, yaw=-0.2, pupil=(-0.6, 0.0), ear=-0.5, smile=-0.2, happy=0.0, eye_open=1.0)   # hm.
P(gaju, 182, 6, 'out', sy=0.8, sx=1.2, trunk=(0, -120), trunk_curl=-0.2, brow_ang=14)                 # wind-up
P(gaju, 188, 2, sy=1.12, sx=0.92, trunk=(-30, 60), trunk_curl=0.4)                                    # throws it down, hard
bl.set(T + 188, x=GX - 60, y=G0 - 250); bl.move(T + 188, T + 190, 'in', y=G0 - 24, sy=0.6, sx=1.4)
sc.hit(T + 190, 'boing', 0.9); sc.slide(T + 190, 60, 96, 12, 0.5)
bl.move(T + 190, T + 198, 'out', y=-500, x=BX + 60, sy=1.2, sx=0.9)                                   # gone, drifting over Bheemu
P(gaju, 192, 3, 'over', sy=1.0, sx=1.0, pupil=(-0.4, -1.0), head_dy=-12, **dict(SHOCK, mouth_open=0.4))
sc.duck(T + 198, T + 256, 0.08)

BELLY_Y = st.probe(T + 100, bheemu, 'belly')[1]      # where his belly anchor is, read with the existing probe
# ------------------------------------------------------------ S5 wide, more sky: the wait (v002: 42 frames, was 58); the ball comes back  (204-271)
shot(204, 'S5', 'WIDE HIGH', MID, 1.0, note='The wait, shortened. Gaju gives up. Bheemu peeks and softens. The ball drops, in full view, on to the open book')
P(gaju, 214, 4, 'io', pupil=(0.0, 0.0), head_dy=0, **CALM)                                              # nothing came down
P(gaju, 222, 5, 'io', sy=0.93, sx=1.05, ear=-0.9, yaw=0.3, pupil=(0.5, 0.6), trunk=(30, 92), trunk_curl=0.7, **SORRY); gaju.set(T + 222, sweat=0.0)   # sulks, turns away
sc.hit(T + 224, 'ghatam', 0.4)
P(bheemu, 228, 4, 'io', armL=(70, -150), armR=(-70, -150)); bk.attach(T + 228, T + 342, bheemu, 'belly', *BOOK_AT)   # the book comes down
P(bheemu, 234, 3, 'io', pupil=(0.9, 0.3), lid=0.1, yaw=0.3)                                            # his first look at Gaju
P(bheemu, 240, 3, 'io', smile=0.6)                                                                     # he softens...
bl.set(T + 246, x=BX, y=G0 - 1540, sy=1.0, sx=1.0)                                                    # v002: enters at the top edge and is in view for 10 frames
bl.move(T + 246, T + 256, 'in', y=BELLY_Y - 100, sy=1.1, sx=0.93)
sc.slide(T + 246, 88, 64, 10, 0.3)                                                                     # a soft falling note so the return is heard as well as seen
bl.set(T + 256, sy=0.86, sx=1.12); bk.set(T + 256, sy=0.8)                                             # v002: a gentle landing. The book closes; nobody is squashed
bheemu.set(T + 256, pupil=(0.0, 0.8), yaw=0.0, eye_pop=1.15, lid=0.0, smile=0.0)
sc.hit(T + 256, 'pop', 0.55, note=72)                                                                  # soft, pitched, alone on its frame
bl.move(T + 258, T + 262, 'out', sy=1.0, sx=1.0)
bl.attach(T + 258, T + 346, bheemu, 'belly', 0, -100)
P(gaju, 258, 2, yaw=-0.7, pupil=(-0.9, 0.0), ear=0.8, **SHOCK)

# ------------------------------------------------------------ S6 medium close on Bheemu: the slow burn  (272-311)
shot(272, 'S6', 'MED CLOSE', BX, 2.6, up=210, note='Slow burn: the ball, a blink, then across to Gaju')
P(bheemu, 272, 1, eye_pop=1.0, pupil=(0.0, 0.9), lid=0.3); sc.hit(T + 278, 'ghatam', 0.5)
blink(bheemu, T + 284)
P(bheemu, 292, 6, 'io', pupil=(0.9, 0.2)); sc.hit(T + 294, 'ghatam', 0.5)
P(bheemu, 302, 6, 'io', yaw=0.5, brow_ang=8); sc.hit(T + 304, 'ghatam', 0.45)

# ------------------------------------------------------------ S7 medium on Gaju: guilt  (312-335)
shot(312, 'S7', 'MEDIUM', GX, 3.0, up=0, note='Guilt: ears down, the smallest wave of the trunk')
P(gaju, 312, 1, ear=-0.9, sy=0.94, sx=1.04, yaw=-0.5, pupil=(-0.8, 0.2), **SORRY)
P(gaju, 318, 3, 'io', trunk=(-60, -40), trunk_curl=-0.4); P(gaju, 324, 3, 'io', trunk=(-40, -60)); P(gaju, 328, 3, 'io', trunk=(-60, -40))
sc.note(T + 318, __import__('sound').bansuri, 72, 0.3, 0.4)

# ------------------------------------------------------------ S8a full on Bheemu: THE REVEAL. He can do it too  (336-379)   v002: its own shot
shot(336, 'S8a', 'FULL', BX, 1.8, up=60, note='The reveal, in its own shot: book under his arm, two calm, expert bounces')
sc.raga(T + 340, TOTAL - 34, 'sweet', v=0.8)
P(bheemu, 336, 1, yaw=0.0, brow_ang=0, pupil=(0.0, 0.5), smile=0.5, lid=0.0)
P(bheemu, 340, 4, 'io', armL=(0, 0), armR=(-30, -150), handR='grip', bendR=0.3)                        # v002: the book stays with him, in his left hand at his side
bk.attach(T + 342, T + 9999, bheemu, 'handL', 0, 30); bk.set(T + 342, sy=1.8, rot=8)
bl.attach(T + 346, T + 352, bheemu, 'handR', 0, -20)
P(bheemu, 348, 3, 'io', armR=(60, -110), handR='open')
bl.set(T + 352, x=BX + 115, y=G0 - 280)
for t0 in (352, 364):                                                         # two bounces, unhurried
    bl.move(T + t0, T + t0 + 6, 'in', y=G0 - 24); bl.move(T + t0 + 6, T + t0 + 12, 'out', y=G0 - 280); ep.tap(T + t0 + 6, 'ge', 0.9)
    P(bheemu, t0, 6, 'in', armR=(60, -70)); P(bheemu, t0 + 6, 6, 'out', armR=(60, -110))
bl.attach(T + 376, T + 404, bheemu, 'handR', 0, -20); sc.hit(T + 376, 'pop', 0.5, note=76)
P(bheemu, 376, 2, handR='grip', smile=0.9)

# ------------------------------------------------------------ S8b medium on Gaju: the take  (380-397)
shot(380, 'S8b', 'MEDIUM', GX, 3.0, up=0, note='Gaju sees it: a take, then delight')
P(gaju, 380, 2, 'over', sy=1.1, sx=0.93, ear=0.9, yaw=-0.6, pupil=(-0.8, 0.0), **dict(SHOCK, mouth_open=0.5))
P(gaju, 390, 4, 'io', sy=1.0, sx=1.0, ear=0.3, trunk=(30, 92), trunk_curl=0.7, **HAPPY)

# ------------------------------------------------------------ S8c wide: one pass  (398-425)   v002: one pass, was two
shot(398, 'S8c', 'WIDE', MID, 1.1, note='"Your turn." One pass. Gaju catches it')
P(bheemu, 400, 2, yaw=0.5, pupil=(0.8, 0.0)); P(bheemu, 402, 2, armR=(80, -150), bendR=0.35)
arc(bl, T + 404, T + 418, GX - 40, G0 - 300, 240); sc.hit(T + 404, 'whoosh', 0.4)
P(bheemu, 408, 4, 'io', armR=(0, 0), handR='mitt', bendR=0.12, **HAPPY)
P(gaju, 412, 3, yaw=-0.5, trunk=(-40, -230), trunk_curl=-0.6); sc.hit(T + 418, 'pop', 0.6, note=76)
bl.attach(T + 418, T + 9999, gaju, 'trunk', 0, -26)
P(gaju, 420, 3, 'over', sy=1.06, sx=0.96, **LAUGH)

# ------------------------------------------------------------ S9 wide, shifted right: Chintu delivers the last joke  (426-end)
shot(426, 'S9', 'WIDE', MID + 110, 1.0, note='Chintu: "Bheemu! Give the ball!" Gaju passes it to Bheemu at once. Bheemu, caught, hands it back. One more page')
chintu.set(T + 426, show=1.0); P(gaju, 426, 2, sy=1.0, sx=1.0)
for f in walk(chintu, T + 426, T + 448, CX, 8, 28):
    ep.tap(f, 'na', 0.6)
P(bheemu, 432, 3, yaw=0.6, pupil=(0.9, 0.0), happy=0.0, eye_open=1.0, smile=0.2); P(gaju, 432, 3, yaw=0.7, pupil=(0.9, 0.0), ear=0.5, **CALM)   # they see him
P(chintu, 448, 2, armL=(-20, -150), handL='open')                                                      # hand out. Everyone is still for the line
e = speak(ep, chintu, T + 452, 'c_ball') - T                                                           # generated Telugu voice: NOT approved until heard
assert e == LINE_END, (e, LINE_END)
b0 = e + 8                                                                                             # v002: a pause after the line, then the action
P(gaju, b0, 2, yaw=-0.5, pupil=(-0.8, 0.0), trunk=(-90, -160), trunk_curl=-0.3)                        # the joke: Gaju gets rid of the evidence
bl.attach(T + 418, T + b0, gaju, 'trunk', 0, -26)
arc(bl, T + b0, T + b0 + 10, BX + 115, G0 - 300, 160); sc.hit(T + b0, 'zip', 0.4)
P(bheemu, b0 + 6, 3, armR=(60, -110), handR='grip', bendR=0.3); sc.hit(T + b0 + 10, 'pop', 0.6, note=72)
bl.attach(T + b0 + 10, T + b0 + 44, bheemu, 'handR', 0, -20)
P(gaju, b0 + 12, 3, yaw=0.2, pupil=(0.3, -0.7), trunk=(30, 92), trunk_curl=0.7, ear=0.0, smile=0.6)   # innocent: studies the sky
P(bheemu, b0 + 12, 3, yaw=0.0, pupil=(0.6, 0.5), **SORRY); sc.hit(T + b0 + 14, 'ghatam', 0.5)          # holding it. Caught. Hold
P(bheemu, b0 + 30, 3, 'io', yaw=0.6, pupil=(0.9, 0.0), smile=0.4, sweat=0.0, brow_ang=0, brow=0)       # all right
P(bheemu, b0 + 36, 4, 'io', armR=(80, -150), bendR=0.35)                                               # a clear, bent-arm offer
arc(bl, T + b0 + 44, T + b0 + 58, CX - 50, G0 - 250, 200); sc.hit(T + b0 + 44, 'whoosh', 0.35)         # a gentle lob
P(bheemu, b0 + 50, 5, 'io', armR=(0, 0), handR='mitt', bendR=0.12)
bl.attach(T + b0 + 58, T + 9999, chintu, 'handL', 0, -20); sc.hit(T + b0 + 58, 'pop', 0.6, note=79)
P(chintu, b0 + 60, 3, 'over', sy=1.06, sx=0.96, **HAPPY); P(chintu, b0 + 66, 4, 'io', sy=1.0, sx=1.0)
P(bheemu, b0 + 64, 4, 'io', yaw=0.0, **READ); bk.attach(T + b0 + 66, T + 9999, bheemu, 'belly', *BOOK_AT); bk.set(T + b0 + 66, rot=0)   # the book opens again
P(bheemu, b0 + 68, 3, 'io', **dict(CALM, **EYES_DOWN))
P(gaju, b0 + 72, 4, 'io', yaw=-0.7, pupil=(-0.9, 0.3), head_dx=-20, ear=0.3, **HAPPY)                  # Gaju leans in to read too
END = T + b0 + 88
assert END + 34 == TOTAL, (END + 34, TOTAL)
ep.close(END, BX, G0 - 300)


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
        frames = [T + t for t in (20, 46, 70, 96, 116, 142, 160, 186, 194, 226, 242, 252, 256, 298, 310, 320, 346, 358, 376, 384, 412, 420, 450, LINE_END + 18, LINE_END + 24, LINE_END + 48, LINE_END + 62, LINE_END + 92)]
        st.sheet(frames, os.path.join(sb, 'board.png'), cols=6, scale=0.3)
        print('board frames (engine):', frames)
    elif mode == 'hookups':
        cuts = [s[0] for s in SHOTS[1:]]
        st.sheet([x for c in cuts for x in (c - 1, c)], os.path.join(sb, 'hookups.png'), cols=8, scale=0.22)
        print('cuts at engine frames:', cuts)
    elif mode == 'render':
        wav = sc.write(os.path.join(HERE, 'scratch_audio.wav'))
        st.render(os.path.join(HERE, 'one_more_page_animatic_v002.mp4'), audio=wav, scale=0.5)
    print('shots:', [(s[1], s[0] + 1, s[2]) for s in SHOTS], 'total frames', TOTAL)
