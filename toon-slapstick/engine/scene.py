"""scene.py - painted backgrounds, props and effects for the slapstick engine."""
import math, random
import numpy as np
import skia
from toon import Actor, G, oval, poly, smooth, tube, bez, arc_pts, W, H, GROUND


# ----------------------------------------------------------------- painted background
class Painted:
    """A wide background painted once (soft, no ink lines) so inked characters pop in front of it.
    paint(g, width) draws flat shapes; this class adds brush dabs, a soft blur and paper tooth."""

    def __init__(self, width, paint, seed=3, dabs=500, blur=1.2, top=(112, 70, 50), bottom=(126, 42, 36)):
        self.width, self.top, self.bottom = width, top, bottom
        surf = skia.Surface(width, H)
        c = surf.getCanvas()
        g = G(c)
        paint(g, width)
        r = random.Random(seed)
        for _ in range(dabs):       # dry-brush dabs, lighter and darker
            x, y = r.uniform(0, width), r.uniform(0, H)
            col = (255, 250, 235) if r.random() < 0.5 else (60, 40, 50)
            c.drawOval(skia.Rect.MakeXYWH(x, y, r.uniform(30, 160), r.uniform(8, 40)),
                       skia.Paint(AntiAlias=True, Color=skia.Color(*col, int(r.uniform(5, 11))),
                                  MaskFilter=skia.MaskFilter.MakeBlur(skia.kNormal_BlurStyle, r.uniform(4, 14))))
        img = surf.makeImageSnapshot()
        out = skia.Surface(width, H)
        oc = out.getCanvas()
        oc.drawImage(img, 0, 0, skia.SamplingOptions(), skia.Paint(ImageFilter=skia.ImageFilters.Blur(blur, blur)))
        # vignette at top and bottom edges
        sh = skia.GradientShader.MakeLinear([(0, 0), (0, H)], [skia.Color(40, 20, 40, 46), skia.Color(0, 0, 0, 0), skia.Color(0, 0, 0, 0), skia.Color(40, 20, 40, 60)], [0, 0.22, 0.8, 1])
        oc.drawRect(skia.Rect(0, 0, width, H), skia.Paint(Shader=sh))
        self.img = out.makeImageSnapshot()

    def __call__(self, canvas, cam, f):
        canvas.save()
        canvas.concat(cam.matrix(f))
        canvas.drawRect(skia.Rect(-6000, -4000, self.width + 6000, 4), skia.Paint(Color=skia.Color(*self.top)))          # above the painting
        canvas.drawRect(skia.Rect(-6000, H - 4, self.width + 6000, H + 4000), skia.Paint(Color=skia.Color(*self.bottom)))  # below it
        canvas.drawImage(self.img, 0, 0, skia.SamplingOptions(skia.FilterMode.kLinear))
        canvas.restore()


def rect(x, y, w, h, r=0):
    p = skia.Path()
    if r:
        p.addRoundRect(skia.Rect.MakeXYWH(x, y, w, h), r, r)
    else:
        p.addRect(skia.Rect.MakeXYWH(x, y, w, h))
    return p


def grad(g, path, c0, c1, y0, y1):
    sh = skia.GradientShader.MakeLinear([(0, y0), (0, y1)], [skia.Color(*c0), skia.Color(*c1)])
    g.c.drawPath(path, skia.Paint(AntiAlias=True, Shader=sh))


def kitchen(g, width):
    """A long kitchen wall: stove, window, shelf, door, clock, cupboard, fridge."""
    FL = 800
    grad(g, rect(0, 0, width, FL), (247, 214, 150), (238, 190, 128), 0, FL)            # wall
    for x in range(0, width, 96):                                                     # faint wallpaper stripes
        g.shape(rect(x, 0, 40, 470), (255, 236, 186), False, a=0.33)
    grad(g, rect(0, 470, width, FL - 470), (118, 168, 150), (92, 142, 130), 470, FL)  # wainscot
    g.shape(rect(0, 462, width, 16), (214, 232, 214), False)
    for x in range(40, width, 240):
        g.shape(rect(x, 510, 190, 240, 10), (104, 154, 138), False)
    g.shape(rect(0, FL - 26, width, 30), (104, 66, 52), False)                         # baseboard
    grad(g, rect(0, FL, width, H - FL), (222, 196, 160), (190, 150, 120), FL, H)       # floor
    rows = [(FL, 44), (FL + 44, 62), (FL + 106, 82), (FL + 188, 100)]
    for j, (y, h) in enumerate(rows):                                                 # oblique checker tiles
        tw = 150 + j * 22
        for i in range(-2, width // tw + 3):
            if (i + j) % 2 == 0:
                x = i * tw - j * 46
                g.shape(poly([(x, y), (x + tw, y), (x + tw - 40, y + h), (x - 40, y + h)]), (160, 92, 78), False, a=0.62)

    def window(x):
        grad(g, rect(x, 130, 380, 300, 8), (150, 212, 244), (214, 238, 232), 130, 430)
        g.shape(oval(x + 110, 380, 150, 70), (126, 190, 120), False); g.shape(oval(x + 300, 400, 140, 60), (104, 170, 110), False)
        g.shape(oval(x + 280, 200, 44, 44), (255, 244, 190), False)
        for a, b, c, d in ((x - 14, 116, 408, 22), (x - 14, 424, 408, 22), (x - 14, 116, 22, 330), (x + 372, 116, 22, 330), (x + 180, 130, 16, 300), (x, 268, 380, 14)):
            g.shape(rect(a, b, c, d, 4), (250, 244, 226), False)
        for s in (0, 1):
            cx = x - 40 + s * 380
            g.shape(smooth([(cx, 96), (cx + 80, 96), (cx + 70 - s * 60, 300), (cx + 86 - s * 86, 450), (cx - 6 + s * 12, 450)], True), (232, 96, 84), False)
        g.shape(rect(x - 60, 84, 500, 20, 8), (150, 96, 70), False)

    def stove(x):
        g.shape(rect(x, 656, 360, 154, 10), (240, 240, 236), False)
        g.shape(rect(x + 30, 700, 300, 92, 12), (58, 62, 78), False)
        g.shape(rect(x + 50, 714, 260, 64, 8), (96, 104, 124), False)
        g.shape(rect(x - 10, 638, 380, 26, 8), (70, 74, 90), False)
        for i in range(4):
            g.shape(oval(x + 60 + i * 80, 682, 12, 12), (226, 86, 70), False)
        g.shape(rect(x + 110, 622, 140, 18, 6), (40, 42, 52), False)        # burner grate

    def counter(x, w):
        g.shape(rect(x, 662, w, 148, 8), (176, 122, 86), False)
        g.shape(rect(x - 10, 644, w + 20, 24, 8), (236, 226, 206), False)
        for i in range(int(w // 150)):
            g.shape(rect(x + 14 + i * 150, 690, 124, 104, 8), (196, 140, 98), False)
            g.shape(oval(x + 120 + i * 150, 742, 8, 8), (250, 226, 150), False)

    def shelf(x):
        g.shape(rect(x, 300, 360, 18, 6), (150, 96, 70), False)
        cols = [(232, 96, 84), (250, 200, 80), (120, 180, 150), (160, 130, 200)]
        for i, c in enumerate(cols):
            g.shape(rect(x + 20 + i * 84, 236 - (i % 2) * 16, 58, 64 + (i % 2) * 16, 12), c, False)
            g.shape(rect(x + 26 + i * 84, 226 - (i % 2) * 16, 46, 14, 5), (250, 244, 226), False)

    def door(x):
        g.shape(rect(x - 16, 110, 332, 700, 8), (250, 240, 214), False)
        g.shape(rect(x, 126, 300, 684, 6), (96, 150, 170), False)
        for yy in (160, 470):
            g.shape(rect(x + 34, yy, 232, 270, 8), (116, 170, 188), False)
        g.shape(oval(x + 258, 470, 14, 14), (250, 214, 110), False)

    def picture(x, y, col):
        g.shape(rect(x, y, 170, 130, 6), (150, 96, 70), False)
        g.shape(rect(x + 14, y + 14, 142, 102), col, False)
        g.shape(oval(x + 85, y + 78, 44, 26), (255, 240, 200), False)

    def clock(x):
        g.shape(rect(x, 190, 150, 620, 14), (132, 80, 60), False)
        g.shape(oval(x + 75, 270, 54, 54), (252, 244, 222), False)
        g.shape(poly([(x + 75, 270), (x + 75, 232)], False), None, True, 6, (60, 40, 40))
        g.shape(poly([(x + 75, 270), (x + 100, 282)], False), None, True, 6, (60, 40, 40))
        g.shape(rect(x + 40, 380, 70, 330, 8), (96, 56, 44), False)
        g.shape(oval(x + 75, 640, 24, 24), (250, 214, 110), False)

    def plant(x):
        g.shape(poly([(x, 700), (x + 120, 700), (x + 100, 810), (x + 20, 810)]), (196, 108, 78), False)
        for a in (-50, -20, 10, 40):
            g.shape(oval(x + 60 + a, 620 - abs(a), 26, 86, a * 0.7), (84, 150, 100), False)

    def fridge(x):
        g.shape(rect(x, 150, 380, 660, 26), (226, 240, 240), False)
        g.shape(rect(x + 14, 164, 352, 240, 18), (240, 250, 250), False)
        g.shape(rect(x + 14, 420, 352, 376, 18), (240, 250, 250), False)
        g.shape(rect(x + 34, 250, 16, 120, 8), (150, 170, 180), False); g.shape(rect(x + 34, 450, 16, 160, 8), (150, 170, 180), False)
        g.shape(rect(x + 200, 220, 70, 56, 4), (250, 200, 80), False); g.shape(rect(x + 240, 300, 60, 60, 4), (232, 96, 84), False)

    stove(240); counter(600, 320); window(820); shelf(1340)
    picture(1840, 210, (120, 170, 200)); door(2140); plant(2560); picture(2760, 180, (232, 150, 110)); clock(3040)
    counter(3320, 470); window(3360); picture(3980, 220, (150, 190, 140)); plant(4230)
    picture(4560, 200, (232, 200, 120)); shelf(4840); door(5400)


# ----------------------------------------------------------------- props
class Prop(Actor):
    """Any object. Pass a draw function fn(g, pose, f) that draws around (0,0)."""
    twos = False

    def __init__(self, fn, shadow=0, smear=False, **over):
        self.fn, self.shadow, self.smear = fn, shadow, smear
        self.POSE = dict(over)
        super().__init__()

    def draw(self, g, p, f):
        g.push(p['x'], p['y'], p['rot'], p['sx'], p['sy'])
        extra = self.fn(g, p, f) or {}
        self.anchors['c'] = g.pt(0, 0)
        for k, v in extra.items():
            self.anchors[k] = g.pt(*v)
        g.pop()


INK = (58, 42, 40)


def table(g, p, f):
    """Low table with a long cloth (things can hide behind it). Top surface is 210 px above the floor."""
    for x in (-226, 200):
        g.shape(rect(x, -200, 26, 200, 6), (150, 92, 64))
    cloth = smooth([(-262, -212), (262, -212), (268, -8), (200, 4), (134, -10), (66, 4), (0, -10), (-66, 4), (-134, -10), (-200, 4), (-268, -8)], True, 0.3)
    g.shape(cloth, (250, 246, 236))
    for i in range(-3, 4):
        g.shape(rect(i * 74 - 11, -206, 22, 186), (232, 96, 84), False, a=0.85)
    g.shape(rect(-270, -222, 540, 18, 7), (250, 246, 236))
    return {'top': (0, -224)}


def fridge(g, p, f):
    """A fridge standing in the running lane: something solid to run into."""
    g.shape(rect(-160, -660, 320, 660, 26), (226, 240, 240))
    g.shape(rect(-146, -646, 292, 236, 18), (242, 250, 250), True, 4)
    g.shape(rect(-146, -396, 292, 382, 18), (242, 250, 250), True, 4)
    g.shape(rect(-126, -560, 16, 120, 8), (150, 170, 180), True, 3); g.shape(rect(-126, -366, 16, 170, 8), (150, 170, 180), True, 3)
    g.shape(rect(30, -590, 70, 56, 4), (250, 200, 80), True, 3); g.shape(rect(64, -510, 58, 58, 4), (232, 96, 84), True, 3)
    return {'top': (0, -660)}


def plate(g, p, f):
    g.shape(oval(0, 0, 92, 20), (248, 250, 252))
    g.shape(oval(0, -3, 66, 12), (226, 234, 240), True, 3)


def dosa(g, p, f):
    """A folded golden dosa. 'bite' 0..1 removes part of it."""
    b = p.get('bite', 0.0)
    w = 96 * (1 - 0.6 * b)
    body = smooth([(-w, 2), (-w * 0.5, -22), (w * 0.4, -26), (w, -6), (w * 0.7, 12), (-w * 0.5, 14)], True, 0.5)
    g.shape(body, (236, 170, 70))
    g.shape(smooth([(-w * 0.7, 0), (0, -14), (w * 0.7, -4)], False), None, True, 3, (176, 108, 40))
    for i in (-0.4, 0.1, 0.5):
        g.shape(oval(w * i, -8 + abs(i) * 6, 9, 5), (250, 204, 110), False)


def pan(g, p, f):
    g.shape(tube([(60, -6), (190, -14)], 11, 9), (70, 60, 66))
    g.shape(oval(0, 0, 84, 17), (64, 60, 72))
    g.shape(oval(0, -4, 68, 11), (40, 38, 48), True, 3)


def book(g, p, f):
    g.shape(rect(-34, -46, 68, 92, 6), (96, 150, 190))
    g.shape(rect(-26, -40, 52, 80, 3), (250, 246, 236), True, 3)
    g.shape(rect(-34, -46, 12, 92, 4), (70, 116, 160))


# ----------------------------------------------------------------- effects (world space)
def puffs(stage, f0, x, y, n=5, size=46, spread=90, life=14, col=(250, 246, 236), dirx=0.0):
    """Dust cloud: a burst of puffs that swell and fade. Classic for zips, skids and landings."""
    r = random.Random(int(f0 * 31 + x))
    parts = [(r.uniform(-1, 1) * spread + dirx * r.uniform(20, 120), -r.uniform(0, spread * 0.7), r.uniform(0.6, 1.2), r.randint(0, 3)) for _ in range(n)]

    def fx(g, f):
        t = (f - f0) / life
        if 0 <= t <= 1:
            for dx, dy, s, d in parts:
                tt = min(1, max(0, (f - f0 - d) / (life - d)))
                e = 1 - (1 - tt) ** 3
                rr = size * s * (0.35 + 0.75 * e)
                cx, cy = x + dx * e, y + dy * e - 10
                blob = smooth([(cx + math.cos(a) * rr * (1 + 0.16 * math.sin(a * 5 + d)), cy + math.sin(a) * rr * 0.8 * (1 + 0.16 * math.cos(a * 4 + d))) for a in [i * math.pi / 6 for i in range(12)]], True)
                g.shape(blob, col, True, 4, INK, a=(1 - tt) ** 0.7)
    stage.fx.append(fx)


def stars(stage, f0, x, y, n=6, r=120, life=12, col=(255, 222, 70)):
    """Impact burst: stars fly out from a hit."""
    def star(cx, cy, s, rot):
        pts = []
        for i in range(10):
            a = math.radians(rot + i * 36)
            rr = s if i % 2 == 0 else s * 0.45
            pts.append((cx + math.cos(a) * rr, cy + math.sin(a) * rr))
        return poly(pts)

    def fx(g, f):
        t = (f - f0) / life
        if 0 <= t <= 1:
            e = 1 - (1 - t) ** 3
            for i in range(n):
                a = 2 * math.pi * i / n + 0.4
                g.shape(star(x + math.cos(a) * r * e, y + math.sin(a) * r * e * 0.8, 26 * (1 - 0.5 * t), f * 14 + i * 30), col, True, 4, INK, a=1 - t * t)
            if t < 0.3:   # white flash burst
                pts = []
                for i in range(16):
                    a = 2 * math.pi * i / 16
                    rr = (r * 0.9 if i % 2 == 0 else r * 0.45) * (0.6 + t * 2)
                    pts.append((x + math.cos(a) * rr, y + math.sin(a) * rr))
                g.shape(poly(pts), (255, 255, 255), True, 5, INK, a=0.95)
    stage.fx.append(fx)


def zip_lines(stage, f0, x, y, direction=1, life=8, length=260, n=5, h=220):
    """Horizontal speed streaks left hanging in the air after a character zips away."""
    def fx(g, f):
        t = (f - f0) / life
        if 0 <= t <= 1:
            for i in range(n):
                yy = y - h * (i + 0.5) / n
                x0 = x - direction * 40 * i % 3
                g.shape(poly([(x0, yy), (x0 - direction * length * (1 - 0.4 * t) * (0.6 + 0.4 * ((i * 7) % 3) / 2), yy)], False), None, True, 6, (255, 255, 255), a=1 - t)
    stage.fx.append(fx)


def marks(stage, f0, x, y, life=10, n=3, col=(255, 255, 255)):
    """Surprise ticks popping off a head during a take."""
    def fx(g, f):
        t = (f - f0) / life
        if 0 <= t <= 1:
            e = 1 - (1 - t) ** 3
            for i in range(n):
                a = math.radians(-90 + (i - (n - 1) / 2) * 34)
                r0, r1 = 30 + 40 * e, 70 + 60 * e
                g.shape(poly([(x + math.cos(a) * r0, y + math.sin(a) * r0), (x + math.cos(a) * r1, y + math.sin(a) * r1)], False), None, True, 9, INK, a=1 - t)
                g.shape(poly([(x + math.cos(a) * r0, y + math.sin(a) * r0), (x + math.cos(a) * r1, y + math.sin(a) * r1)], False), None, True, 5, col, a=1 - t)
    stage.fx.append(fx)


# ----------------------------------------------------------------- screen-space overlays
def iris(stage, f0, f1, cx, cy, closing=True, r_max=2300):
    """Classic iris-out (closing) or iris-in on a point of interest."""
    def ov(g, f):
        if f < f0:
            if closing:
                return
            t = 0
        else:
            t = min(1, (f - f0) / max(1, f1 - f0))
        r = r_max * ((1 - t) ** 2 if closing else t ** 2)
        hole = oval(cx, cy, max(r, 0.01), max(r, 0.01))
        full = rect(0, 0, W, H)
        mask = skia.Op(full, hole, skia.kDifference_PathOp)
        g.c.drawPath(mask, skia.Paint(AntiAlias=True, Color=skia.Color(18, 14, 20)))
    stage.overlays.append(ov)


def title_card(stage, f0, f1, title, sub='', bg=(126, 30, 44), ray=(160, 46, 52)):
    """Opening card: series title and episode name on a slowly turning sunburst."""
    def ov(g, f):
        if f0 <= f < f1:
            a = min(1, (f1 - f) / 8)
            g.c.drawRect(skia.Rect(0, 0, W, H), skia.Paint(Color=skia.Color(*bg, int(255 * a))))
            for i in range(9):
                ang = i * 40 + f * 0.6
                p = poly([(W / 2, H / 2), (W / 2 + math.cos(math.radians(ang)) * 2600, H / 2 + math.sin(math.radians(ang)) * 2600), (W / 2 + math.cos(math.radians(ang + 20)) * 2600, H / 2 + math.sin(math.radians(ang + 20)) * 2600)])
                g.c.drawPath(p, skia.Paint(AntiAlias=True, Color=skia.Color(*ray, int(255 * a))))
            tf = skia.Typeface('DejaVu Serif', skia.FontStyle.BoldItalic())
            y = H / 2 - 40
            for txt, size, col in ((title, 170, (255, 206, 72)), (sub, 76, (255, 246, 226))):
                font = skia.Font(tf, size)
                while font.measureText(txt) > W * 0.88 and size > 20:
                    size -= 4; font = skia.Font(tf, size)
                wdt = font.measureText(txt)
                for dx, dy, c in ((6, 7, (40, 10, 20)), (0, 0, col)):
                    g.c.drawString(txt, W / 2 - wdt / 2 + dx, y + dy, font, skia.Paint(AntiAlias=True, Color=skia.Color(*c, int(255 * a))))
                y += size * 0.95 + 30
    stage.overlays.append(ov)
