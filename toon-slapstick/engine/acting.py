"""acting.py - reusable slapstick moves. Each helper writes keys on an actor's timeline and
returns the frame where the move ends, so moves chain:  f = take(momo, f)

Frame counts follow the timing table in references/craft.md (24 fps).
"""
import math
from scene import puffs, zip_lines, marks, stars


def blink(a, f):
    a.move(f, f + 2, 'out', eye_open=0.0); a.move(f + 3, f + 5, 'out', eye_open=1.0)
    return f + 5


def look(a, f, yaw=None, pupil=None, frames=3):
    """Snap the head and eyes to a new direction. Eyes lead, the head follows a frame later."""
    if pupil is not None:
        a.move(f, f + 2, 'snap', pupil=pupil)
    if yaw is not None:
        a.move(f + 1, f + 1 + frames, 'over', yaw=yaw)
    return f + 1 + frames


def bob(a, f0, f1, beat=12, amp=0.035):
    """Bounce in time with the music so a standing character never goes dead."""
    f = f0
    while f + beat <= f1:
        a.move(f, f + beat // 2, 'io', sy=1 - amp, sx=1 + amp * 0.8)
        a.move(f + beat // 2, f + beat, 'io', sy=1 + amp * 0.5, sx=1 - amp * 0.4)
        f += beat
    a.move(f, f + 3, 'io', sy=1.0, sx=1.0)
    return f1


def walk(a, f0, f1, x1, step_frames=8, stride=34):
    """Walk to x1. One step every step_frames frames. Returns the frames where feet land (for step notes)."""
    x0 = a.value('x', f0)
    steps = max(1, round((f1 - f0) / step_frames))
    d = 1 if x1 >= x0 else -1
    a.move(f0, f0 + 3, 'io', stride=stride * d)
    a.move(f0, f1, 'lin', x=x1, step=a.value('step', f0) + steps / 2)
    a.move(f1 - 2, f1 + 1, 'io', stride=0.0)
    return [f0 + round(i * (f1 - f0) / steps) for i in range(1, steps + 1)]


def arc(a, f0, f1, x1, y1, height, spin=0.0):
    """Throw something along an arc: steady sideways, slowing up to the top, speeding up coming down."""
    y0 = a.value('y', f0); fm = (f0 + f1) // 2
    a.move(f0, f1, 'lin', x=x1)
    a.move(f0, fm, 'out', y=min(y0, y1) - height)
    a.move(fm, f1, 'in', y=y1)
    if spin:
        a.move(f0, f1, 'lin', rot=a.value('rot', f0) + spin)
    return f1


def squash(a, f, amount=0.3, settle=10):
    """Landing or impact squash, then a jelly settle. Volume is kept: wider when shorter."""
    a.set(f, sy=1 - amount, sx=1 + amount * 0.8)
    a.move(f + 2, f + settle, 'elastic', sy=1.0, sx=1.0)
    return f + settle


def take(stage, a, f, big=1.0, hold=7):
    """The classic take: see it, sink (anticipation), then stretch up with popping eyes, hold, settle.
    3 frames down, 2 frames up, hold on the extreme, about 12 frames to settle."""
    a.move(f, f + 3, 'out', sy=1 - 0.2 * big, sx=1 + 0.16 * big, eye_open=0.5, brow=-6, head_dy=10)
    a.move(f + 3, f + 5, 'snap', sy=1 + 0.24 * big, sx=1 - 0.13 * big, eye_open=1.3, eye_pop=1 + 0.55 * big,
           pupil_s=0.55, brow=22 * big, mouth_open=0.85, mouth_w=0.85, smile=-0.2, head_dy=-16 * big)
    if 'glasses_dy' in a.defaults:
        a.move(f + 3, f + 6, 'snap', glasses_dy=-46 * big, glasses_rot=-14)
        a.move(f + 6 + hold, f + 12 + hold, 'bounce', glasses_dy=6, glasses_rot=7)
    if 'ear' in a.defaults:
        a.move(f + 3, f + 5, 'snap', ear=0.9); a.move(f + 5 + hold, f + 14 + hold, 'elastic', ear=0.0)
    x, y = a.value('x', f), a.value('y', f)
    marks(stage, f + 4, x, y - a.HEIGHT * (1.28 + 0.2 * big), life=9)
    e = f + 5 + hold
    a.move(e, e + 10, 'elastic', sy=1.0, sx=1.0, head_dy=0)
    a.move(e, e + 5, 'out', eye_open=1.0, eye_pop=1.0, pupil_s=1.0, brow=8, mouth_open=0.0, mouth_w=1.0)
    return e + 10


def shake(a, f0, f1, amp=7):
    """Vibrate on ones (recoil after a hit, fear, strain)."""
    x = a.value('x', f0)
    for i, f in enumerate(range(f0, f1)):
        k = 1 - (f - f0) / (f1 - f0)
        a.set(f, x=x + (amp if i % 2 == 0 else -amp) * k)
    a.set(f1, x=x)
    return f1


def scramble(stage, a, f, frames=9, direction=1):
    """Run on the spot before taking off: lean back, legs become a wheel, dust flies."""
    a.move(f, f + 3, 'out', rot=-14 * direction, sx=1.08, sy=0.92, face=direction, yaw=direction)
    a.set(f + 3, wheel=1.0, stride=30)
    a.move(f + 3, f + 3 + frames, 'lin', step=a.value('step', f) + frames / 3.0, rot=16 * direction)
    x, y = a.value('x', f), a.value('y', f)
    for k in range(0, frames, 3):
        puffs(stage, f + 3 + k, x - 40 * direction, y, n=3, size=30, spread=50, life=10, dirx=-direction)
    return f + 3 + frames


def zip_off(stage, a, f, x1, frames=5, wind=9, hide=True):
    """Scramble, then vanish in a streak leaving a dust cloud and speed lines."""
    x0 = a.value('x', f); d = 1 if x1 >= x0 else -1
    g = scramble(stage, a, f, wind, d)
    a.move(g, g + frames, 'in', x=x1)
    y = a.value('y', f)
    puffs(stage, g, x0, y, n=6, size=52, spread=110, life=16, dirx=-d)
    zip_lines(stage, g + 1, x0 + d * 120, y, d, life=9, h=a.HEIGHT * 0.9)
    if hide:
        a.set(g + frames, show=0.0)
    return g + frames


def chew(a, f0, f1, every=6):
    f = f0
    while f < f1:
        a.move(f, f + every // 2, 'io', cheeks=1.0, head_sy=0.94, head_sx=1.05)
        a.move(f + every // 2, f + every, 'io', cheeks=0.7, head_sy=1.03, head_sx=0.98)
        f += every
    return f1


def flap(a, f0, f1, period=4, amp=1.0):
    """Ear flapping (flying). Returns the frames of each down-beat for the flap sound."""
    f = f0; beats = []
    while f < f1:
        a.move(f, f + period // 2, 'out', ear=amp); a.move(f + period // 2, f + period, 'out', ear=-amp * 0.7)
        beats.append(f + period // 2)
        f += period
    return beats
