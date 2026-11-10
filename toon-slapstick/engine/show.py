"""show.py - the parts every Bheemu & Gaju episode shares: opening card, closing iris, common props
and effects, and the command line.

    ep = Show(2, 'Mango Season', 'mango_season', 760, Painted(2700, garden, top=SKY, bottom=(112, 136, 70)))
    st, sc, cam = ep.st, ep.sc, ep.cam
    ...
    ep.close(END, x, y)       # tihai on END, iris closes on world point (x, y)
    ep.main(__file__)
"""
import os, sys, math, subprocess
import skia
from toon import Stage, W, H, GROUND, oval, poly, smooth, tube, bez
from scene import rect, title_card, iris, Prop
from india import telugu
from sound import Score, bansuri, veena, tabla, xylo

G0 = GROUND
INK = (58, 42, 40)


class Show:
    def __init__(self, n, title, slug, total, bg, intro=36):
        self.n, self.slug, self.total = n, slug, total
        self.st = Stage(total, bg=bg); self.sc = Score(total); self.cam = self.st.cam
        title_card(self.st, 0, intro, 'Bheemu & Gaju', title)
        self.st.overlays.append(lambda g, f: telugu(g, 'భీము - గజు', W / 2, H / 2 - 260, 120, (255, 246, 226), 'Ramabhadra', a=min(1, (intro - f) / 8)) if f < intro else None)
        self.sc.hit(2, 'manjira', 0.9); self.sc.note(2, bansuri, 74, 0.5, 0.6); self.sc.note(14, bansuri, 81, 0.7, 0.6)

    @staticmethod
    def cy(z, up=0):
        """Camera height that keeps the floor near the bottom of the frame at zoom z."""
        return G0 - 600 / z - up

    def shot(self, f, x, z=1.1, up=0, cut=True):
        (self.st.cut if cut else self.cam.set)(f, x=x, y=self.cy(z, up), zoom=z)

    def push(self, f0, f1, x, z=1.1, up=0, ease='io'):
        self.cam.move(f0, f1, ease, x=x, y=self.cy(z, up), zoom=z)

    def tap(self, f, stroke='ge', v=1.0):
        self.sc._add(self.sc.fx, f, tabla(stroke, v))

    def close(self, END, x, y):
        """Drum cadence lands on END, then the iris closes on world point (x, y)."""
        self.sc.hit(END - 25, 'tihai', 0.9)
        cx_, cy_, z = self.cam.value('x', END + 8), self.cam.value('y', END + 8), self.cam.value('zoom', END + 8)
        iris(self.st, END + 8, END + 26, W / 2 + (x - cx_) * z, H / 2 + (y - cy_) * z, closing=True)

    def main(self, file):
        here = os.path.dirname(os.path.abspath(file))
        out = os.path.join(here, 'out'); os.makedirs(out, exist_ok=True)
        mode = sys.argv[1] if len(sys.argv) > 1 else 'final'
        if mode == 'sheet':
            frames = [int(x) for x in sys.argv[2].split(',')]
            self.st.sheet(frames, sys.argv[3] if len(sys.argv) > 3 else os.path.join(out, 'sheet.png'), cols=6, scale=0.3)
            return
        wav = self.sc.write(os.path.join(out, 'audio.wav'))
        raw = os.path.join(out, 'raw%s.mp4' % ('_preview' if mode == 'preview' else ''))
        self.st.render(raw, audio=wav, scale=0.5 if mode == 'preview' else 1.0)
        if mode == 'final':
            dst = os.path.join(out, 'bheemu_gaju_ep%02d_%s.mp4' % (self.n, self.slug))
            subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-i', raw, '-c:v', 'libx264', '-crf', '22', '-preset', 'slow', '-tune', 'animation',
                            '-c:a', 'aac', '-b:a', '160k', '-movflags', '+faststart', dst], check=True)
            print('wrote', dst)


# ----------------------------------------------------------------- acting shortcuts
def face(a, f, n=4, ease='over', **kw):
    """Change expression over n frames."""
    a.move(f, f + n, ease, **kw)
    return f + n


CALM = dict(eye_open=1.0, happy=0.0, eye_pop=1.0, pupil_s=1.0, brow=0, brow_ang=0, brow_asym=0.0, lid=0.0, mouth_open=0.0, mouth_w=1.0, smile=0.4, sweat=0.0)
HAPPY = dict(happy=1.0, eye_open=0.0, eye_pop=1.0, smile=1.0, mouth_w=1.3, brow_ang=0, brow=0, lid=0.0, mouth_open=0.0, sweat=0.0)
LAUGH = dict(happy=1.0, eye_open=0.0, eye_pop=1.0, smile=1.0, mouth_w=1.4, mouth_open=0.9, brow_ang=0, brow=0, lid=0.0, sweat=0.0)
ANGRY = dict(happy=0.0, eye_open=1.0, brow_ang=24, lid=0.25, smile=-0.8, mouth_open=0.0, mouth_w=1.0, brow=0)
SHOCK = dict(happy=0.0, eye_open=1.0, eye_pop=1.5, pupil_s=0.55, brow=18, brow_ang=0, lid=0.0, mouth_open=0.8, mouth_w=0.85, smile=-0.2)
SORRY = dict(happy=0.0, eye_open=1.0, eye_pop=1.0, pupil_s=1.0, brow_ang=-18, brow=4, lid=0.0, smile=-0.4, mouth_open=0.0, mouth_w=0.8, sweat=1.0)
SLY = dict(happy=0.0, eye_open=1.0, lid=0.3, brow_asym=1.0, smile=0.9, mouth_w=1.2, mouth_open=0.0, brow_ang=0)
SLEEP = dict(happy=0.0, eye_open=0.0, smile=0.2, mouth_open=0.0, brow_ang=0, lid=0.0)


def hop(a, f, h=60, n=8):
    """A small jump on the spot. Returns the landing frame."""
    y = a.value('y', f)
    a.move(f, f + 2, 'out', sy=0.88, sx=1.08)
    a.move(f + 2, f + 2 + n // 2, 'out', y=y - h, sy=1.08, sx=0.95)
    a.move(f + 2 + n // 2, f + 2 + n, 'in', y=y)
    a.set(f + 2 + n, sy=0.86, sx=1.1); a.move(f + 3 + n, f + 9 + n, 'elastic', sy=1.0, sx=1.0)
    return f + 2 + n


def laugh(show, a, f0, f1, note=84, every=4):
    """Bouncing laugh with flute giggles."""
    face(a, f0, 3, **LAUGH)
    y = a.value('y', f0)
    for i, f in enumerate(range(f0 + 3, f1, every)):
        a.move(f, f + every // 2, 'out', head_dy=-8, sy=1.04); a.move(f + every // 2, f + every, 'in', head_dy=0, sy=0.97)
        show.sc.note(f, bansuri, note - i % 5, 0.09, 0.5)
    a.move(f1, f1 + 3, 'out', sy=1.0, head_dy=0)
    return f1


def enter(show, a, f0, f1, x0, x1, every=8, stride=30, stroke='ge', v=0.8):
    """Walk in from x0 to x1 with a drum tap on each step."""
    from acting import walk
    a.set(f0, show=1.0, x=x0, face=1 if x1 > x0 else -1, yaw=0.8 if x1 > x0 else -0.8)
    for f in walk(a, f0, f1, x1, every, stride):
        show.tap(f, stroke, v)
    return f1


# ----------------------------------------------------------------- props
def ladle(g, p, f):
    g.shape(tube([(0, 0), (0, -170)], 8, 7), (150, 100, 66))
    g.shape(oval(0, -196, 34, 30), (206, 212, 220)); g.shape(oval(0, -200, 22, 18), (236, 240, 246), True, 3)


def milkpot(g, p, f):
    """Steel pot of milk. 'level' 1..0 is how much is left."""
    lv = p.get('level', 1.0)
    g.shape(smooth([(-70, -110), (70, -110), (84, -60), (70, -6), (-70, -6), (-84, -60)], True, 0.5), (206, 212, 220))
    g.shape(oval(0, -110, 72, 18), (176, 184, 196))
    if lv > 0.03:
        g.shape(oval(0, -110 + (1 - lv) * 8, 62 * (0.6 + 0.4 * lv), 13 * (0.5 + 0.5 * lv)), (255, 255, 250), True, 3)
    g.shape(oval(-40, -60, 9, 30), (246, 248, 252), False, a=0.8)
    return {'top': (0, -112)}


def ball(g, p, f):
    g.shape(oval(0, 0, 22, 22), (200, 50, 50))
    g.shape(smooth([(-18, -8), (0, -2), (18, -8)], False), None, True, 3, (255, 240, 230))


def umbrella(g, p, f):
    """Open black umbrella. Origin is the handle grip. 'open' 1 open, 0 folded; 'flip' 1 turns it inside out."""
    fl = p.get('flip', 0.0); op = p.get('open', 1.0)
    g.shape(tube([(0, 0), (0, -330)], 6, 5), (120, 90, 70))
    g.shape(tube([(0, 0), (10, 22), (30, 16)], 7, 7), (150, 60, 50))
    w = 250 * (0.16 + 0.84 * op)
    if fl < 0.5:
        g.shape(smooth([(-w, -260), (-w * 0.7, -360), (0, -410), (w * 0.7, -360), (w, -260), (w * 0.5, -280), (0, -262), (-w * 0.5, -280)], True, 0.5), (50, 50, 66))
        for k in (-0.5, 0.5):
            g.shape(smooth([(0, -408), (w * k * 0.7, -350), (w * k, -272)], False), None, True, 3, (110, 110, 130))
    else:
        g.shape(smooth([(-w, -470), (-w * 0.5, -440), (0, -456), (w * 0.5, -440), (w, -470), (w * 0.6, -360), (0, -320), (-w * 0.6, -360)], True, 0.5), (50, 50, 66))
    return {'top': (0, -410)}


def kite(g, p, f):
    g.shape(poly([(0, -70), (56, 0), (0, 70), (-56, 0)]), (232, 80, 70))
    g.shape(poly([(0, -70), (0, 70)], False), None, True, 3, (120, 60, 40)); g.shape(smooth([(-56, 0), (0, -20), (56, 0)], False), None, True, 3, (120, 60, 40))
    g.shape(poly([(0, 70), (-14, 104), (14, 104)]), (250, 208, 80))
    return {'tail': (0, 104)}


def papad(g, p, f):
    g.shape(oval(0, 0, 54, 15), (250, 226, 150))
    for a in (20, 100, 200, 290):
        g.shape(oval(math.cos(math.radians(a)) * 26, math.sin(math.radians(a)) * 6, 4, 2), (200, 160, 90), False)


def cloth(g, p, f):
    """The white cloth the papads dry on."""
    g.shape(poly([(-330, -22), (330, -22), (380, 34), (-380, 34)]), (250, 250, 244))


def diya(g, p, f):
    g.shape(smooth([(-26, -10), (26, -10), (20, 6), (-20, 6)], True, 0.5), (176, 96, 60))
    fl = 1 + 0.15 * math.sin(f * 0.9)
    g.shape(smooth([(-8, -10), (0, -10 - 34 * fl), (8, -10)], True, 0.7), (255, 200, 70), True, 3, (230, 120, 40))


def rocket(g, p, f):
    """A flowerpot firework that has decided to run around. Sparks shoot from the back."""
    g.shape(poly([(-30, 0), (30, 0), (16, -50), (-16, -50)]), (214, 60, 56))
    g.shape(rect(-22, -34, 44, 10), (250, 208, 80), False)
    for i in range(7):
        a = math.radians(-90 + (i - 3) * 16 + math.sin(f * 1.3 + i) * 10)
        L = 60 + 40 * math.sin(f * 0.9 + i * 2)
        g.shape(poly([(0, -50), (math.cos(a) * L, -50 + math.sin(a) * L)], False), None, True, 5, (255, 220, 90) if i % 2 else (255, 150, 60))
        g.shape(oval(math.cos(a) * (L + 10), -50 + math.sin(a) * (L + 10), 5, 5), (255, 250, 200), False)


def carrot(g, p, f):
    g.shape(smooth([(-12, -6), (12, -6), (3, 54), (-3, 54)], True, 0.5), (244, 130, 50))
    for a in (-24, 0, 24):
        g.shape(oval(a * 0.4, -22, 6, 18, a), (90, 170, 90), True, 3)


def cot(g, p, f):
    """Rope cot (mancham) to lie on. Top is 150 above the floor."""
    for x in (-250, 226):
        g.shape(rect(x, -150, 24, 150, 5), (130, 84, 56))
    g.shape(rect(-270, -172, 540, 34, 10), (150, 100, 66))
    for i in range(-6, 7):
        g.shape(poly([(i * 40 - 8, -168), (i * 40 + 8, -142)], False), None, True, 3, (226, 206, 160))
    return {'top': (0, -172)}


def window_frame(g, p, f):
    pass


# ----------------------------------------------------------------- effects
def rain(stage, f0, f1, n=70, slant=0.25):
    def fx(g, f):
        if f0 <= f < f1:
            for i in range(n):
                x = (i * 137.5 + f * 31 * slant * 3) % (W + 200) - 100
                y = (i * 91.7 + f * 96) % (H + 200) - 100
                g.c.drawLine(x, y, x - 60 * slant, y + 60, skia.Paint(AntiAlias=True, Color=skia.Color(226, 236, 250, 150), StrokeWidth=3))
    stage.overlays.append(fx)


def word(stage, f0, x, y, text, size=110, col=(255, 222, 70), life=14, font='Timmana'):
    """A Telugu sound word that pops on a hit (world space)."""
    def fx(g, f):
        if f0 <= f < f0 + life:
            t = (f - f0) / life
            s = size * (0.5 + 1.2 * min(1, t * 4)) if t < 0.25 else size * (1.7 - 0.2 * t)
            telugu(g, text, x, y - 30 * t, s * 0.62, col, font, a=min(1, (1 - t) * 3), outline=(60, 30, 30))
    stage.fx.append(fx)


def zzz(stage, a, f0, f1):
    def fx(g, f):
        if f0 <= f < f1:
            hx, hy = a.anchors.get('top', (0, 0))
            for i in range(3):
                t = ((f - f0) / 30.0 + i / 3.0) % 1.0
                s = 26 + 40 * t
                x, y = hx + 60 + t * 110 + math.sin(t * 6) * 16, hy - 20 - t * 170
                p = poly([(x, y), (x + s, y), (x, y + s), (x + s, y + s)], False)
                g.shape(p, None, True, 7, (255, 255, 255), a=1 - t)
    stage.fx.append(fx)


def splash(stage, f0, x, y, n=8, life=12, col=(190, 214, 240)):
    def fx(g, f):
        if f0 <= f < f0 + life:
            t = (f - f0) / life
            for i in range(n):
                a = math.radians(-160 + i * 140 / (n - 1))
                d = 60 + 190 * t
                px, py = x + math.cos(a) * d, y + math.sin(a) * d * 0.9 + 260 * t * t
                g.shape(oval(px, py, 14 * (1 - t) + 4, 20 * (1 - t) + 5), col, True, 3, (90, 120, 170), a=1 - t * 0.6)
    stage.fx.append(fx)


def sparks(stage, f0, x, y, n=18, life=22, r=420):
    """Firework burst in the sky."""
    cols = ((255, 220, 90), (255, 120, 90), (140, 220, 255), (190, 255, 160))
    def fx(g, f):
        if f0 <= f < f0 + life:
            t = (f - f0) / life
            for i in range(n):
                a = 2 * math.pi * i / n
                d0, d1 = r * (t ** 0.5) * 0.7, r * (t ** 0.5)
                g.shape(poly([(x + math.cos(a) * d0, y + math.sin(a) * d0 + 80 * t * t), (x + math.cos(a) * d1, y + math.sin(a) * d1 + 80 * t * t)], False), None, True, 7, cols[i % 4], a=1 - t)
    stage.fx.append(fx)


# ----------------------------------------------------------------- hand-held boards
def _width(text, size, font):
    import uharfbuzz as hb
    from india import _font
    hbf, tf, upem = _font(font)
    buf = hb.Buffer(); buf.add_str(text); buf.guess_segment_properties(); hb.shape(hbf, buf)
    return sum(p.x_advance for p in buf.glyph_positions) * size / upem


def board(show, a, f0, text, hold=40, side=1, size=50, font='Ramabhadra', col=(126, 30, 44), up=0):
    """The silent-cartoon way to talk: the character holds up a wooden board with a Telugu line on it.
    It pops up beside them, wobbles, and drops. No speech bubbles in this series (Harshith's rule).
    Use '\n' for a second line; two to four words a line; hold 36 frames or more."""
    lines = text.split('\n')
    bw = max(_width(l, size, font) for l in lines) + 64
    bh = len(lines) * size * 1.3 + 40

    def fx(g, f):
        if not (f0 <= f < f0 + hold):
            return
        t = f - f0
        rise = (0.25, 0.7, 1.08, 1.0)[t] if t < 4 else (max(0.0, (f0 + hold - f) / 3) if f0 + hold - f < 3 else 1.0)
        x = a.value('x', f) + side * (a.HEIGHT * 0.22 + bw / 2 + 30)
        y0 = a.value('y', f)
        top = y0 - (a.HEIGHT + 60 + up + bh) * rise
        g.push(x, y0, math.sin(t * 0.5) * 2.5 * max(0, 1 - t / 16))
        g.shape(rect(-9, top - y0 + bh - 6, 18, (y0 - top) - bh + 6, 4), (150, 100, 66), True, 4, INK)
        g.shape(rect(-bw / 2, top - y0, bw, bh, 12), (255, 250, 236), True, 5, INK)
        g.shape(rect(-bw / 2 + 10, top - y0 + 10, bw - 20, bh - 20, 6), None, True, 3, (214, 160, 90))
        for i, l in enumerate(lines):
            telugu(g, l, 0, top - y0 + 20 + size * 0.95 + i * size * 1.3, size, col, font)
        g.pop()
    show.st.fx.append(fx)
    show.sc.hit(f0, 'pop', 0.5, note=76)
    return f0 + hold
