"""Builds the demonstration figures and prints the number tables used in Animation_Fundamentals.md.
Run: python3 make_figures.py   (needs skia-python, Pillow, and the toon-slapstick engine next door)"""
import math, os, sys
import skia
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', '..', '..', 'toon-slapstick', 'engine'))
INK = skia.Color(58, 42, 40); RED = skia.Color(214, 60, 56); BLUE = skia.Color(70, 120, 200); GREY = skia.Color(150, 150, 160)
F = skia.Font(skia.Typeface('DejaVu Sans'), 26); FB = skia.Font(skia.Typeface('DejaVu Sans', skia.FontStyle.Bold()), 30); FS = skia.Font(skia.Typeface('DejaVu Sans'), 20)


def P(col, w=0, a=255):
    p = skia.Paint(AntiAlias=True, Color=col); p.setAlpha(a)
    if w:
        p.setStyle(skia.Paint.kStroke_Style); p.setStrokeWidth(w)
    return p


def canvas(w, h):
    s = skia.Surface(w, h); c = s.getCanvas(); c.clear(skia.Color(252, 250, 244)); return s, c


EASES = {'linear (even spacing)': lambda t: t,
         'slow in and slow out': lambda t: t * t * (3 - 2 * t),
         'slow in only (arrives softly)': lambda t: 1 - (1 - t) ** 2,
         'slow out only (starts softly, then falls)': lambda t: t * t}

# ---------------------------------------------------------------- figure 1: spacing
s, c = canvas(1500, 760)
c.drawString('Same timing (12 frames), different spacing. Each circle is one frame.', 40, 50, FB, P(INK))
print('\nSPACING TABLE: position in px of a ball travelling 240 px in 12 frames')
print('frame | ' + ' | '.join(k.split(' (')[0] for k in EASES))
rows = {k: [round(240 * f(i / 12.0)) for i in range(13)] for k, f in EASES.items()}
for i in range(13):
    print('%5d | ' % i + ' | '.join('%4d' % rows[k][i] for k in EASES))
for r, (k, f) in enumerate(EASES.items()):
    y = 150 + r * 160
    c.drawString(k, 40, y - 52, F, P(INK))
    c.drawLine(120, y + 34, 1400, y + 34, P(GREY, 2))
    for i in range(13):
        x = 140 + 1240 * f(i / 12.0)
        c.drawCircle(x, y, 26, P(RED, 0, 60 if 0 < i < 12 else 255)); c.drawCircle(x, y, 26, P(INK, 3))
        c.drawLine(x, y + 28, x, y + 42, P(INK, 2))
        if i in (0, 3, 6, 9, 12) or k.startswith('linear'):
            c.drawString(str(i), x - 8, y + 68, FS, P(INK))
s.makeImageSnapshot().save(os.path.join(HERE, 'AF_fig1_spacing.png'), skia.kPNG)

# ---------------------------------------------------------------- figure 2: bouncing ball
H0, N1 = 400.0, 9
frames, f = [], 0
h, n, x = H0, N1, 0.0
print('\nBOUNCE TABLE: frame | height above floor (px) | stretch (height x width) | note')
while h > 12:
    for i in range(n + 1):                      # fall
        y = h * (1 - (i / n) ** 2); v = 2 * h * i / (n * n)
        frames.append((f, x, y, v, 'fall')); f += 1; x += 22
    frames[-1] = frames[-1][:4] + ('CONTACT',)
    h *= 0.6; n = max(2, round(N1 * math.sqrt(h / H0)))
    for i in range(1, n):                       # rise
        y = h * (1 - ((n - i) / n) ** 2); v = 2 * h * (n - i) / (n * n)
        frames.append((f, x, y, v, 'rise')); f += 1; x += 22
s, c = canvas(1500, 700)
c.drawString('Bouncing ball on ones: spacing grows as it falls, squash only on contact.', 40, 50, FB, P(INK))
c.drawLine(40, 600, 1460, 600, P(INK, 4))
for (fr, x, y, v, tag) in frames:
    st = 1 + min(0.45, v / 110.0); sq = tag == 'CONTACT'
    sy, sx = (0.62, 1.0 / 0.62) if sq else (st, 1.0 / st)
    cx, cy = 90 + x, 600 - 36 * sy - y
    c.drawOval(skia.Rect.MakeLTRB(cx - 36 * sx, cy - 36 * sy, cx + 36 * sx, cy + 36 * sy), P(RED, 0, 255 if sq else 90))
    c.drawOval(skia.Rect.MakeLTRB(cx - 36 * sx, cy - 36 * sy, cx + 36 * sx, cy + 36 * sy), P(INK, 3))
    if sq or fr == 0 or v < 1:
        c.drawString(('f%d' % fr), cx - 16, 640 if sq else cy - 36 * sy - 12, FS, P(INK))
    print('%5d | %6.0f | %.2f x %.2f | %s' % (fr, y, sy, sx, 'squash, 1 frame' if sq else ('top of arc' if v < 1 else tag)))
s.makeImageSnapshot().save(os.path.join(HERE, 'AF_fig2_bounce.png'), skia.kPNG)

# ---------------------------------------------------------------- figure 4: arcs and overlap
s, c = canvas(1500, 760)
c.drawString('Arcs: a head turn that dips, against one that slides straight across.', 40, 50, FB, P(INK))
print('\nHEAD TURN TABLE (9 drawings on twos = 18 frames): drawing | frame | turn % | dip px')
for row, dip in ((0, 0), (1, 26)):
    y0 = 170 + row * 180
    c.drawString('straight: mechanical' if not dip else 'arc: alive (lowest in the middle, blink on the way)', 40, y0 - 70, F, P(INK))
    for i in range(9):
        t = i / 8.0; e = t * t * (3 - 2 * t)
        x = 160 + i * 150; d = dip * math.sin(math.pi * e)
        c.drawCircle(x, y0 + d, 48, P(skia.Color(255, 236, 200))); c.drawCircle(x, y0 + d, 48, P(INK, 3))
        ex = (e - 0.5) * 56
        for k in (-1, 1):
            if dip and i in (3, 4):
                c.drawLine(x + ex + k * 16 - 8, y0 + d - 6, x + ex + k * 16 + 8, y0 + d - 6, P(INK, 3))
            else:
                c.drawCircle(x + ex + k * 16, y0 + d - 6, 6, P(INK))
        c.drawString(str(i + 1), x - 8, y0 + 84, FS, P(INK))
        if dip:
            print('%7d | %5d | %5.0f | %4.0f%s' % (i + 1, 1 + i * 2, 100 * e, d, '  (eyes shut)' if i in (3, 4) else ''))
c.drawString('Overlap: the root moves first, the tip arrives last and overshoots (tail, ear, trunk).', 40, 520, FB, P(INK))
print('\nOVERLAP TABLE: frame | root angle | middle angle | tip angle (degrees)')


def swing(fr, delay):
    t = (fr - delay) / 8.0
    if t <= 0:
        return 0.0
    if t >= 1:
        return 40 + 12 * math.exp(-(t - 1) * 3.0) * math.cos((t - 1) * 9.0) - 12 * math.exp(-(t - 1) * 3.0) * 1.0 + 12 * math.exp(-(t - 1) * 3) * (1 if delay else 0) * math.cos((t - 1) * 9.0) * 0
    return 40 * t * t * (3 - 2 * t)


for i, fr in enumerate(range(0, 22, 2)):
    a = [swing(fr, 0), swing(fr, 2), swing(fr, 4)]
    if fr >= 8 + 0:
        a[0] = 40
    for j, dl in ((1, 2), (2, 4)):
        t = (fr - dl) / 8.0
        if t > 1:
            a[j] = 40 + (8 + 6 * j) * math.exp(-(t - 1) * 4) * math.sin((t - 1) * 7)
    print('%5d | %5.0f | %5.0f | %5.0f' % (fr, a[0], a[1], a[2]))
    x, y = 130 + i * 128, 580; ang = 0
    for j in range(3):
        ang = math.radians(a[j]) ; nx, ny = x + math.sin(ang) * 46, y + math.cos(ang) * 46
        c.drawLine(x, y, nx, ny, P(BLUE if j < 2 else RED, 14 - j * 3)); x, y = nx, ny
    c.drawString('f%d' % fr, 110 + i * 128, 740, FS, P(INK))
s.makeImageSnapshot().save(os.path.join(HERE, 'AF_fig4_arcs_overlap.png'), skia.kPNG)

# ---------------------------------------------------------------- figure 3: a hop, drawn by our engine
from toon import Stage, W, H as HH, GROUND
from chars import Gaju
from PIL import Image, ImageDraw, ImageFont
Gaju.shadow = 60
st = Stage(40); st.grain = 0
g = Gaju(x=W / 2, y=GROUND, face=0.0)
st.add(g); st.cut(0, x=W / 2, y=GROUND - 330, zoom=1.9)
G0 = GROUND
g.move(2, 8, 'out', sy=0.74, sx=1.2, ear=-0.5, brow=6, pupil=(0, -0.6))          # anticipation: crouch
g.move(8, 10, 'snap', sy=1.3, sx=0.82, y=G0 - 60, ear=-1.0)                         # stretch off the ground
g.move(10, 16, 'out', y=G0 - 300, sy=1.05, sx=0.97, ear=0.2)                        # rise, slowing
g.move(16, 22, 'in', y=G0 - 20, sy=1.22, sx=0.86, ear=1.0)                          # fall, speeding, ears trail up
g.set(22, y=G0, sy=0.66, sx=1.3, ear=1.0)                                           # contact squash, 1 frame
g.move(23, 26, 'out', sy=1.1, sx=0.94, ear=-0.6)                                    # overshoot up; ears flop down late
g.move(26, 34, 'elastic', sy=1.0, sx=1.0, ear=0.0, brow=0, pupil=(0, 0))            # settle
PICK = [(0, 'rest'), (5, 'anticipation'), (8, 'crouch'), (10, 'stretch'), (13, 'rising'), (16, 'top'), (18, 'falling'), (20, 'stretch'), (22, 'SQUASH'), (24, 'overshoot'), (27, 'settle'), (34, 'rest')]
tiles = []
for fr, _ in PICK:
    st.still(fr, os.path.join(HERE, '_t.png'), 0.25); tiles.append(Image.open(os.path.join(HERE, '_t.png')).convert('RGB').crop((0, 60, 270, 430)))
out = Image.new('RGB', (270 * 6, 430 * 2 + 70), (252, 250, 244)); d = ImageDraw.Draw(out)
fb = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf', 26)
d.text((20, 16), 'One hop, twelve of its 34 frames: anticipation, stretch, slow top, fall, squash, overshoot, settle.', font=fb, fill=(58, 42, 40))
for i, (im, (fr, name)) in enumerate(zip(tiles, PICK)):
    x, y = (i % 6) * 270, 70 + (i // 6) * 430
    out.paste(im, (x, y)); d.text((x + 10, y + 380), 'f%d %s' % (fr, name), font=fb, fill=(150, 30, 40))
out.save(os.path.join(HERE, 'AF_fig3_hop.png')); os.remove(os.path.join(HERE, '_t.png'))
print('\nfigures written')
