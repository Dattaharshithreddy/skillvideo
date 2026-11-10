"""cast.py - the rest of the household: Ammamma (grandmother), Chintu (the boy next door),
Laddu (the fat orange cat) and Bujji (the white rabbit). Same pose parameters as Bheemu and Gaju.
"""
import math
import skia
from toon import oval, poly, smooth, tube, limb, bez, arc_pts, GROUND
from chars import Character


def _profile_limb(c, prof):
    """Outline of a limb around centre line c with a radius per sample."""
    L, R = [], []
    n = len(c)
    for i, q in enumerate(c):
        a0, a1 = c[max(i - 1, 0)], c[min(i + 1, n - 1)]
        d = math.hypot(a1[0] - a0[0], a1[1] - a0[1]) or 1
        nx, ny = -(a1[1] - a0[1]) / d, (a1[0] - a0[0]) / d
        L.append((q[0] + nx * prof[i], q[1] + ny * prof[i])); R.append((q[0] - nx * prof[i], q[1] - ny * prof[i]))
    return L, R


def _U(a, b):
    u = skia.Op(a, b, skia.kUnion_PathOp)
    return u if u is not None else a


def _I(a, b):
    return skia.Op(a, b, skia.kIntersect_PathOp)


def _limb_path(c, prof, tip=0.5, root=0.8):
    """One closed outline around centre line c, radius per sample, rounded at both ends."""
    L, R = _profile_limb(c, prof)
    d = math.hypot(c[-1][0] - c[-2][0], c[-1][1] - c[-2][1]) or 1
    t = (c[-1][0] + (c[-1][0] - c[-2][0]) / d * prof[-1] * tip, c[-1][1] + (c[-1][1] - c[-2][1]) / d * prof[-1] * tip)
    d = math.hypot(c[0][0] - c[1][0], c[0][1] - c[1][1]) or 1
    r = (c[0][0] + (c[0][0] - c[1][0]) / d * prof[0] * root, c[0][1] + (c[0][1] - c[1][1]) / d * prof[0] * root)
    return smooth(L + [t] + R[::-1] + [r], True, 0.5)


def _two_bone(a, b, l1, l2, sg):
    """Shoulder a, wrist b: returns 13 centre-line points through a real elbow (or knee)."""
    ux, uy = b[0] - a[0], b[1] - a[1]
    d = math.hypot(ux, uy) or 1
    if d > (l1 + l2) * 0.995:
        k = d / ((l1 + l2) * 0.995); l1 *= k; l2 *= k
    ux, uy = ux / d, uy / d
    q = (l1 * l1 - l2 * l2 + d * d) / (2 * d)
    h = math.sqrt(max(l1 * l1 - q * q, 0.0))
    el = (a[0] + ux * q - uy * h * sg, a[1] + uy * q + ux * h * sg)
    c = [(a[0] + (el[0] - a[0]) * i / 6, a[1] + (el[1] - a[1]) * i / 6) for i in range(7)]
    c += [(el[0] + (b[0] - el[0]) * i / 6, el[1] + (b[1] - el[1]) * i / 6) for i in range(1, 7)]
    return c, el


class _Biped(Character):
    """Shared drawing for the people: arms with an elbow and a wrist, hands with four fingers and a
    thumb, legs with a knee, feet with toes."""
    LINE = 4.2
    ARM = [1.0, 1.02, 1.0, 0.96, 0.9, 0.84, 0.8, 0.82, 0.82, 0.76, 0.66, 0.57, 0.5]
    LEG = [1.0, 1.0, 0.98, 0.94, 0.88, 0.82, 0.78, 0.82, 0.86, 0.82, 0.72, 0.6, 0.52]

    def _hand(self, g, w, ang, side, s, kind, fill, hl):
        """A human hand as one outline: palm, four fingers, thumb. w is the wrist, ang the forearm
        direction. kind: mitt (relaxed), open, fist, grip, point."""
        dx, dy = math.cos(ang), math.sin(ang)
        tx, ty = -dy * side, dx * side                      # towards the thumb
        P = lambda u, v: (w[0] + dx * u * s + tx * v * s, w[1] + dy * u * s + ty * v * s)

        def finger(u0, v0, deg, ln, r, curl=0.0):
            a = math.radians(deg)
            fu, fv = math.cos(a), math.sin(a)
            a2 = math.radians(deg + curl)
            m = (u0 + fu * ln * 0.55, v0 + fv * ln * 0.55)
            e = (m[0] + math.cos(a2) * ln * 0.45, m[1] + math.sin(a2) * ln * 0.45)
            return tube([P(u0, v0), P(*m), P(*e)], r * s, r * s * 0.86)

        lines = []
        if kind in ('fist', 'grip', 'point'):
            shape = smooth([P(-0.1, -0.66), P(0.8, -0.98), P(1.7, -1.0), P(2.25, -0.55), P(2.3, 0.3), P(1.85, 0.95), P(0.8, 0.92), P(-0.1, 0.66)], True, 0.55)
            shape = _U(shape, tube([P(0.5, 0.8), P(1.2, 1.12), P(1.85, 0.62)], 0.32 * s, 0.27 * s))          # thumb folded over
            if kind == 'point':
                shape = _U(shape, finger(1.7, 0.56, 4, 1.9, 0.28))
            for v in (-0.5, 0.0, 0.5) if kind != 'point' else (-0.5, 0.0):
                lines.append([P(1.45, v), P(2.22 - 0.1 * abs(v), v * 1.04)])
        else:
            op = kind == 'open'
            shape = smooth([P(-0.1, -0.66), P(0.9, -0.98), P(1.75, -0.98), P(2.0, 0.0), P(1.75, 0.98), P(0.9, 0.95), P(-0.1, 0.66)], True, 0.5)
            fan = (20, 7, -6, -20) if op else (5, 1, -3, -8)
            ln = (1.5, 1.7, 1.55, 1.2) if op else (1.25, 1.42, 1.3, 1.02)
            for i, v in enumerate((0.72, 0.25, -0.24, -0.7)):
                shape = _U(shape, finger(1.7, v, fan[i], ln[i], 0.3 if i < 3 else 0.26, 0 if op else 14))
            shape = _U(shape, finger(0.5, 0.72, 64 if op else 38, 1.3 if op else 1.15, 0.31, -10 if op else -16))
            if not op:
                for i, v in enumerate((0.48, 0.0, -0.47)):
                    lines.append([P(1.85, v), P(1.85 + ln[i + 1] * 0.62, v * 1.25 - 0.06)])
        self._ink(g, shape, fill)
        for l in lines:
            self._ink(g, poly(l, False), None, 2.6, col=hl)
        return P(1.5, 0)

    def _arm2(self, g, p, side, key, sh, rest, l1, l2, r0, s, skin, hl, sleeve=None, bangles=None):
        off = p[key]
        w = (sh[0] + rest[0] + off[0], sh[1] + rest[1] + off[1])
        b = p['bendL' if side < 0 else 'bendR']
        c, el = _two_bone(sh, w, l1, l2, -side * (1 if b >= 0 else -1))
        prof = [r0 * k for k in self.ARM]
        self._ink(g, _limb_path(c, prof, tip=0.2), skin)
        ang = math.atan2(w[1] - c[-3][1], w[0] - c[-3][0])
        if bangles:
            for k in (2, 3):
                q = c[-k]; n = (-math.sin(ang), math.cos(ang)); r = prof[-k] + 1
                self._ink(g, poly([(q[0] + n[0] * r, q[1] + n[1] * r), (q[0] - n[0] * r, q[1] - n[1] * r)], False), None, 5, col=bangles)
        grip = self._hand(g, w, ang, side, s, p['handL' if side < 0 else 'handR'], skin, hl)
        if sleeve:
            col, n = sleeve
            self._ink(g, _limb_path(c[:n], [x + 3 for x in prof[:n]], tip=0.1), col)
        self.anchors['handL' if side < 0 else 'handR'] = g.pt(*grip)

    def _foot(self, g, fx, fy, face, side, s, skin, hl):
        """Bare foot with five toes. Front view shows the toes in a row, side view the whole sole."""
        if abs(face) > 0.4:
            d = 1 if face > 0 else -1
            Q = lambda u, v: (fx + u * s * d, fy + v * s)
            shape = smooth([Q(-0.75, -1.5), Q(-1.0, -0.5), Q(-0.7, 0.0), Q(1.5, 0.0), Q(2.25, -0.12), Q(2.3, -0.5), Q(1.6, -0.82), Q(0.75, -1.2), Q(0.45, -1.6)], True, 0.5)
            self._ink(g, shape, skin)
            for u in (1.75, 2.02):
                self._ink(g, poly([Q(u, -0.62 + (u - 1.75) * 0.5), Q(u + 0.06, -0.12)], False), None, 2.2, col=hl)
            return
        Q = lambda u, v: (fx + u * s * side, fy + v * s)                 # u grows outwards
        shape = smooth([Q(-0.9, -1.25), Q(-1.02, -0.5), Q(-0.8, -0.1), Q(0.9, -0.05), Q(1.12, -0.45), Q(0.8, -1.25)], True, 0.55)
        for i, (u, r) in enumerate(((-0.72, 0.36), (-0.2, 0.29), (0.2, 0.27), (0.56, 0.25), (0.88, 0.22))):   # big toe on the inside
            shape = _U(shape, oval(*Q(u, -0.02 - 0.04 * i), r * s, r * s * 1.05))
        self._ink(g, shape, skin)
        for u in (-0.44, 0.0, 0.38, 0.72):
            self._ink(g, poly([Q(u, -0.5), Q(u, -0.02)], False), None, 2.2, col=hl)

    def _legs2(self, g, p, hips, hip_y, l1, l2, r0, s, skin, hl):
        st, amp, face = p['step'], p['stride'], p['face']
        if p['wheel'] > 0.5:
            self._legs(g, p, [(-hips, hip_y), (hips, hip_y)], -12, s * 1.7, s * 0.8, r0, skin, toes=skin)
            return
        order = (0, 1) if face <= 0 else (1, 0)
        for i in order:
            hx0 = (-hips, hips)[i]
            ph = 2 * math.pi * (st + i * 0.5)
            key = 'footL' if i == 0 else 'footR'
            dx = amp * math.cos(ph) + p[key][0]
            lift = max(0.0, math.sin(ph)) * amp * 0.5 - p[key][1]
            side = -1 if i == 0 else 1
            hx = hx0 * (1 - 0.4 * abs(face))
            fx, fy = hx + dx, -lift
            ank = (fx - (face * s * 0.3), fy - s * 1.2)
            sg = (-1 if face > 0 else 1) if abs(face) > 0.2 else -side
            c, kn = _two_bone((hx, hip_y), ank, l1, l2, sg)
            self._ink(g, _limb_path(c, [r0 * k for k in self.LEG], tip=0.2), skin)
            self._foot(g, fx, fy, face, side, s, skin, hl)
            if abs(face) < 0.4:
                self._ink(g, poly(arc_pts(kn[0], kn[1] + 3, r0 * 0.5, 4, 200, 340, 5), False), None, 2.4, col=hl)

    def _brows(self, g, eyes, p, dy, half, w, col):
        for x, y, ws, s in eyes:
            lift = p['brow'] + (p['brow_asym'] * 10 if s > 0 else -p['brow_asym'] * 4)
            t = math.radians(p['brow_ang']) * s
            d = (math.cos(t) * half * ws, -math.sin(t) * half)
            self._ink(g, smooth([(x - d[0], y - dy - lift - d[1] + 2), (x, y - dy - lift - 3), (x + d[0], y - dy - lift + d[1] + 2)], False), None, w, col=col)

    def _ear(self, g, x, y, s, skin, hl):
        self._ink(g, oval(x, y, 12 * s, 17 * s), skin)
        self._ink(g, poly(arc_pts(x, y, 5 * s, 9 * s, 250, 470, 6), False), None, 2.4, col=hl)


# =====================================================================  AMMAMMA
class Ammamma(_Biped):
    """The grandmother who runs the house. Cotton saree, silver bun, big red bindi. Kind, but nobody
    argues with her ladle."""
    HEIGHT = 560
    shadow = 130
    INK = (70, 40, 36)
    STREAK = (250, 240, 220)
    SKIN = (200, 140, 100)
    HL = (150, 96, 70)
    HAIR = (226, 226, 232)
    SAREE = (44, 140, 112)
    SAREE2 = (58, 160, 128)
    FOLD = (30, 104, 84)
    BORDER = (236, 180, 52)
    BLOUSE = (150, 40, 60)
    POSE = dict(Character.POSE, bendL=0.3, bendR=0.3, smile=0.5)

    def draw(self, g, p, f):
        self.begin(g, p)
        face = p['face']
        sway = math.sin(2 * math.pi * p['step']) * p['stride'] * 0.2
        bob = -abs(math.sin(2 * math.pi * p['step'])) * p['stride'] * 0.08
        for i, s in enumerate((-1, 1)):                    # bare feet under the hem
            ph = 2 * math.pi * (p['step'] + i * 0.5)
            fx = s * 44 * (1 - 0.4 * abs(face)) + p['stride'] * math.cos(ph) * 0.7 + face * 30
            self._foot(g, fx, -max(0, math.sin(ph)) * p['stride'] * 0.3, face, s, 22, self.SKIN, self.HL)
        g.push(0, bob)
        k = 1 - 0.3 * abs(face)
        far = 'armR' if face > 0.35 else 'armL' if face < -0.35 else None
        arm = lambda side, key: self._arm2(g, p, side, key, (side * 72 * (1 - 0.5 * abs(face)), -376), (side * 8, 165), 88, 80, 22, 16,
                                           self.SKIN, self.HL, sleeve=(self.BLOUSE, 4), bangles=self.BORDER)
        if far:
            arm(1 if far == 'armR' else -1, far)
        self._ink(g, smooth([(52 * k, -398), (84 * k, -384), (104 * k, -300), (92 * k, -226), (66 * k, -236), (62 * k, -330)], True, 0.5), self.SAREE2)   # pallu end hanging behind the shoulder
        self._ink(g, poly([(98 * k, -246), (70 * k, -252)], False), None, 7, col=self.BORDER)
        body = smooth([(-56 * k, -400), (56 * k, -400), (82 * k, -382), (88 * k, -330), (82 * k, -280), (94 * k, -226), (102 * k, -120),
                       (110 * k + sway, -26), (104 * k + sway, -20), (-104 * k + sway, -20), (-110 * k + sway, -26), (-102 * k, -120), (-94 * k, -226),
                       (-82 * k, -280), (-88 * k, -330), (-82 * k, -382)], True, 0.5)
        self._ink(g, body, self.SAREE, 0, False)
        blouse = _I(body, poly([(-140, -420), (30 * k, -420), (-96 * k, -292), (-140, -292)]))
        if blouse is not None:
            self._ink(g, blouse, self.BLOUSE, 0, False)
        hem = _I(body, poly([(-200, -52), (200, -52), (200, 20), (-200, 20)]))
        if hem is not None:
            self._ink(g, hem, self.BORDER, 0, False)
        self._ink(g, body, None)
        self._ink(g, smooth([(-92 * k, -290), (-30 * k, -330), (40 * k, -396)], False), None, 9, col=self.BORDER)       # pallu border across the chest
        self._ink(g, smooth([(-92 * k, -290), (-30 * k, -330), (40 * k, -396)], False), None, 2.5, a=0.5)
        for x in (-30, -12, 6, 24):                        # pleats falling from the waist
            self._ink(g, smooth([(x * 0.4 * k, -262), (x * k + sway * 0.4, -150), (x * 1.5 * k + sway, -56)], False), None, 3, col=self.FOLD)
        self._ink(g, smooth([(-84 * k, -274), (-30 * k, -262), (40 * k, -270), (84 * k, -282)], False), None, 3, col=self.FOLD)
        self._ink(g, smooth([(-20 * k, -398), (-24 * k, -430), (24 * k, -430), (20 * k, -398), (0, -384)], True, 0.4), self.SKIN)   # neck
        if not far:
            arm(-1, 'armL'); arm(1, 'armR')
        # ---- head
        g.push(p['head_dx'] + face * 8, -476 + p['head_dy'], p['head_rot'], p['head_sx'], p['head_sy'], 0, 60)
        a = p['yaw'] * 0.6
        R = 66
        self._ink(g, oval(-p['yaw'] * 44, -62, 36, 32), self.HAIR)                     # bun
        self._ink(g, poly(arc_pts(-p['yaw'] * 44, -62, 20, 17, 200, 420, 8), False), None, 2.5, col=(176, 176, 188))
        for s in (-1, 1):
            ex = s * 64 - p['yaw'] * 14
            self._ear(g, ex, 6, 1.0, self.SKIN, self.HL)
            self._ink(g, oval(ex, 28, 6, 8), self.BORDER, 2.5)
        head = smooth([(0, -70), (40, -62), (64, -24), (66, 14), (52, 48), (26, 68), (0, 72), (-26, 68), (-52, 48), (-66, 14), (-64, -24), (-40, -62)], True, 0.5)
        self._ink(g, head, self.SKIN)
        px_, _ = self._yaw(0, R, a)
        hair = _I(head, smooth([(-110, -110), (110, -110), (84, -18), (px_ + 44, -34), (px_, -46), (px_ - 44, -34), (-84, -18)], True, 0.5))
        if hair is not None:
            self._ink(g, hair, self.HAIR)
        self._ink(g, poly([(px_, -68), (px_, -46)], False), None, 3, col=(176, 176, 188))
        py = p['pitch'] * 10
        self._ink(g, oval(px_, -22 + py, 7.5, 7.5), (214, 40, 44), 0, False)             # bindi
        eyes = []
        for s in (-1, 1):
            x, ws = self._yaw(s * 26, R, a)
            eyes.append((x, 2 + py, ws, s))
        nx_, nw = self._yaw(0, R * 0.95, a)
        nd = 1 if p['yaw'] >= 0 else -1
        self._ink(g, smooth([(nx_ + 1 * nd, 14 + py), (nx_ + 8 * nd, 26 + py), (nx_ + 1 * nd, 32 + py), (nx_ - 6 * nd, 29 + py)], False), None, 3.2)
        self._ink(g, oval(nx_ + 9 * nd, 22 + py, 2.5, 2.5), self.BORDER, 0, False)
        self._mouth(g, nx_, 46 + py, max(nw, 0.7), p, w0=17)
        for x, y, ws, s in eyes:
            self._eye(g, x, y, 13, ws, p, self.SKIN, pupil_col=(60, 36, 30), side=s)
            self._ink(g, poly([(x + s * 15 * ws, y + 1), (x + s * 23 * ws, y - 4)], False), None, 2.4, col=self.HL)      # laugh line
        self._brows(g, eyes, p, 21, 13, 4.5, (160, 160, 170))
        self.anchors['mouth'] = g.pt(nx_, 50 + py); self.anchors['head'] = g.pt(0, 0); self.anchors['top'] = g.pt(0, -90)
        g.pop()
        if far:
            arm(-1 if far == 'armR' else 1, 'armL' if far == 'armR' else 'armR')
        self.anchors['belly'] = g.pt(0, -220)
        g.pop()
        self.end(g)


# =====================================================================  CHINTU
class Chintu(_Biped):
    """The boy next door, about seven. Striped T-shirt, shorts, bare feet, a tuft of hair that never
    lies flat. Gaju's partner in mischief."""
    HEIGHT = 390
    shadow = 80
    INK = (60, 36, 34)
    STREAK = (250, 240, 220)
    SKIN = (204, 146, 104)
    HL = (156, 100, 72)
    HAIR = (40, 34, 40)
    SHIRT = (236, 76, 64)
    STRIPE = (252, 214, 80)
    SHORTS = (58, 92, 160)
    POSE = dict(Character.POSE, bendL=0.2, bendR=0.2, smile=0.7)

    def draw(self, g, p, f):
        self.begin(g, p)
        face = p['face']
        k = 1 - 0.3 * abs(face)
        bob = -abs(math.sin(2 * math.pi * p['step'])) * p['stride'] * 0.12
        self._legs2(g, p, 24, -122, 52, 52, 17, 15, self.SKIN, self.HL)
        g.push(0, bob)
        far = 'armR' if face > 0.35 else 'armL' if face < -0.35 else None
        arm = lambda side, key: self._arm2(g, p, side, key, (side * 47 * (1 - 0.5 * abs(face)), -220), (side * 5, 100), 52, 50, 14, 11.5,
                                           self.SKIN, self.HL, sleeve=(self.SHIRT, 5))
        if far:
            arm(1 if far == 'armR' else -1, far)
        self._ink(g, smooth([(-46 * k, -152), (46 * k, -152), (50 * k, -112), (44 * k, -84), (10 * k, -86), (0, -108), (-10 * k, -86), (-44 * k, -84), (-50 * k, -112)], True, 0.4), self.SHORTS)
        shirt = smooth([(-34 * k, -236), (34 * k, -236), (52 * k, -224), (54 * k, -180), (50 * k, -138), (0, -132), (-50 * k, -138), (-54 * k, -180), (-52 * k, -224)], True, 0.5)
        self._ink(g, shirt, self.SHIRT, 0, False)
        for yy in (-204, -176, -150):
            st_ = _I(shirt, poly([(-80, yy), (80, yy), (80, yy + 12), (-80, yy + 12)]))
            if st_ is not None:
                self._ink(g, st_, self.STRIPE, 0, False)
        self._ink(g, shirt, None)
        self._ink(g, smooth([(-15 * k, -236), (-17 * k, -252), (17 * k, -252), (15 * k, -236), (0, -226)], True, 0.4), self.SKIN)      # neck
        self._ink(g, smooth([(-20 * k, -238), (0, -224), (20 * k, -238)], False), None, 4)
        if not far:
            arm(-1, 'armL'); arm(1, 'armR')
        g.push(p['head_dx'] + face * 8, -306 + p['head_dy'], p['head_rot'], p['head_sx'], p['head_sy'], 0, 60)
        a = p['yaw'] * 0.6
        R = 70
        for s in (-1, 1):
            self._ear(g, s * 68 - p['yaw'] * 14, 10, 1.05, self.SKIN, self.HL)
        head = smooth([(0, -68), (44, -60), (68, -20), (70, 18), (56, 48), (28, 64), (0, 67), (-28, 64), (-56, 48), (-70, 18), (-68, -20), (-44, -60)], True, 0.5)
        self._ink(g, head, self.SKIN)
        hx_, _ = self._yaw(0, R, a)
        hair = _I(head, smooth([(-120, -120), (120, -120), (80, -10), (hx_ + 50, -30), (hx_ + 30, -42), (hx_ + 8, -26), (hx_ - 14, -44), (hx_ - 38, -30), (-80, -10)], True, 0.35))
        if hair is not None:
            self._ink(g, hair, self.HAIR)
        self._ink(g, smooth([(-26, -62), (-24, -92), (-8, -72), (2, -102), (14, -74), (30, -92), (30, -62)], True, 0.4), self.HAIR)   # the tuft
        py = p['pitch'] * 10
        eyes = []
        for s in (-1, 1):
            x, ws = self._yaw(s * 28, R, a)
            eyes.append((x, 8 + py, ws, s))
        nx_, nw = self._yaw(0, R * 0.95, a)
        nd = 1 if p['yaw'] >= 0 else -1
        self._ink(g, smooth([(nx_ - 1 * nd, 18 + py), (nx_ + 6 * nd, 28 + py), (nx_ - 3 * nd, 31 + py)], False), None, 3.2)
        self._mouth(g, nx_, 44 + py, max(nw, 0.7), p, w0=19)
        for x, y, ws, s in eyes:
            self._eye(g, x, y, 15, ws, p, self.SKIN, pupil_col=(54, 34, 30), side=s)
        self._brows(g, eyes, p, 24, 13, 5.5, self.HAIR)
        self.anchors['mouth'] = g.pt(nx_, 48 + py); self.anchors['head'] = g.pt(0, 0); self.anchors['top'] = g.pt(0, -90)
        g.pop()
        if far:
            arm(-1 if far == 'armR' else 1, 'armL' if far == 'armR' else 'armR')
        self.anchors['belly'] = g.pt(0, -180)
        g.pop()
        self.end(g)


class _Animal(_Biped):
    """Four-legged cast: sits up facing us (|face| < 0.5) or walks on all fours in profile."""
    S = 1.0

    def _paw(self, g, x, y, rx, ry, fill, n=3, d=0):
        self._ink(g, oval(x + d * rx * 0.25, y, rx, ry), fill)
        for k in range(n):
            u = (k - (n - 1) / 2) * rx * 0.52 + d * rx * 0.4
            self._ink(g, poly([(x + u, y - ry * 0.15), (x + u, y + ry * 0.8)], False), None, 2.4, col=self.HL)

    def _local(self, p, d):
        q = dict(p)
        q['yaw'] = p['yaw'] * d
        q['pupil'] = (p['pupil'][0] * d, p['pupil'][1])
        return q

    def draw(self, g, p, f):
        self.begin(g, p)
        g.push(0, 0, 0, self.S, self.S)
        if abs(p['face']) < 0.5:
            self._front(g, p, f)
        else:
            d = 1 if p['face'] > 0 else -1
            g.push(0, 0, 0, d, 1)
            self._side(g, self._local(p, d), f)
            g.pop()
        g.pop()
        self.end(g)


# =====================================================================  LADDU (cat)
class Laddu(_Animal):
    """A fat orange tabby who believes the house is his. Lazy, smug, and very fast when milk is
    involved. Sits like a cat, walks like a cat. `tail` swings the tail."""
    HEIGHT = 250
    S = 0.86
    shadow = 86
    INK = (110, 56, 30)
    HL = (170, 86, 34)
    STREAK = (255, 236, 200)
    FUR = (244, 156, 66)
    FAR = (222, 134, 52)
    STRIPE = (212, 110, 40)
    CREAM = (255, 236, 200)
    PINK = (250, 150, 150)
    IRIS = (196, 220, 96)
    POSE = dict(Character.POSE, lid=0.32, smile=0.6, tail=0.0, bendL=0.0, bendR=0.0)

    def _tail(self, g, tl):
        self._ink(g, tube(tl, 15, 9, True), self.FUR)
        for i in (3, 5, 7, 9):
            q, q2 = tl[i], tl[i + 1]
            d = math.hypot(q2[0] - q[0], q2[1] - q[1]) or 1
            n = (-(q2[1] - q[1]) / d, (q2[0] - q[0]) / d)
            r = 13 - i * 0.5
            self._ink(g, poly([(q[0] + n[0] * r, q[1] + n[1] * r), (q[0] - n[0] * r, q[1] - n[1] * r)], False), None, 5.5, col=self.STRIPE)
        self._ink(g, tube(tl, 15, 9, True), None)

    def _cat_eye(self, g, cx, cy, r, ws, p, s):
        e = p['eye_open']
        r = r * p['eye_pop']
        rx, ry = r * 1.12 * ws, r * min(e, 1.35) * 0.95
        if e <= 0.1:
            k = 1 if p['happy'] > 0.5 else -0.55
            self._ink(g, smooth([(cx - rx, cy + 3 * k), (cx, cy - 9 * k), (cx + rx, cy + 3 * k)], False), None, 5.5)
            return
        eye = smooth([(cx - s * rx, cy + ry * 0.3), (cx - s * rx * 0.35, cy - ry * 0.95), (cx + s * rx * 0.55, cy - ry * 0.9), (cx + s * rx * 1.08, cy - ry * 0.4),
                      (cx + s * rx * 0.45, cy + ry * 0.8), (cx - s * rx * 0.4, cy + ry * 0.92)], True, 0.55)
        self._ink(g, eye, self.IRIS, 4)
        px, py = p['pupil']
        pw = r * (0.2 + 0.34 * p['pupil_s'] * (p['eye_pop'] - 0.6)) * ws
        ex, ey = cx + px * (rx - pw) * 0.75, cy + py * ry * 0.2
        pup = _I(eye, oval(ex, ey, pw, ry * 0.86))
        if pup is not None:
            self._ink(g, pup, (40, 44, 30), 0, False)
        self._ink(g, oval(ex - pw * 0.6 - 2, ey - ry * 0.36, 3.6 * ws, 4.2), (255, 255, 255), 0, False)
        lid = p['lid']; ang = p['brow_ang']
        if lid > 0.02 or abs(ang) > 6:
            drop = -ry + 2 * ry * max(lid, 0.18 if abs(ang) > 6 else 0)
            t = math.radians(ang * 0.8) * s
            dx, dy = math.cos(t), math.sin(t)
            a = (cx - dx * 3 * rx, cy + drop - dy * 3 * rx); b = (cx + dx * 3 * rx, cy + drop + dy * 3 * rx)
            cut = _I(poly([a, b, (b[0], b[1] - 4 * ry), (a[0], a[1] - 4 * ry)]), eye)
            if cut is not None:
                self._ink(g, cut, self.FUR, 4)

    def _head(self, g, p):
        yw = p['yaw']
        a = yw * 0.6
        R = 84
        for s in (-1, 1):
            ex = s * 52 - yw * 14
            pts = [(ex - s * 26, -44), (ex - s * 4, -84), (ex + s * 18, -114), (ex + s * 32, -74), (ex + s * 36, -30), (ex, -30)]
            self._ink(g, smooth(pts, True, 0.4), self.FUR)
            cx_, cy_ = ex + s * 8, -62
            self._ink(g, smooth([(cx_ + (x - cx_) * 0.56, cy_ + (y - cy_) * 0.62) for x, y in pts[:5]], True, 0.4), self.PINK, 0, False)
            for k in (0, 1):
                self._ink(g, poly([(ex - s * (10 - k * 10), -44 + k * 2), (ex + s * (2 + k * 8), -70 + k * 4)], False), None, 2.4, col=self.CREAM)
        head = smooth([(0, -62), (44, -56), (76, -28), (88, 2), (106, 24), (86, 32), (94, 50), (64, 58), (30, 68), (0, 70),
                       (-30, 68), (-64, 58), (-94, 50), (-86, 32), (-106, 24), (-88, 2), (-76, -28), (-44, -56)], True, 0.45)
        self._ink(g, head, self.FUR)
        hx_, _ = self._yaw(0, R, a)
        for k in (-20, 0, 20):                               # the tabby mark on the forehead
            self._ink(g, smooth([(hx_ + k, -60), (hx_ + k * 0.9, -48), (hx_ + k * 0.7, -36)], False), None, 6.5, col=self.STRIPE)
        for s in (-1, 1):
            for k in (0, 1):
                st_ = _I(head, oval(s * 96 - yw * 10, 0 + k * 22, 24, 5, s * 12))
                if st_ is not None:
                    self._ink(g, st_, self.STRIPE, 0, False)
        self._ink(g, head, None)
        py = p['pitch'] * 8
        mx, mw = self._yaw(0, R * 0.9, a)
        mw = max(mw, 0.7)
        for s in (-1, 1):                                    # whisker pads and chin
            self._ink(g, oval(mx + s * 17 * mw, 38 + py, 22 * mw, 16), self.CREAM, 0, False)
        self._ink(g, oval(mx, 52 + py, 15 * mw, 10), self.CREAM, 0, False)
        if p['mouth_open'] < 0.06:
            sm = p['smile'] * 5
            self._ink(g, poly([(mx, 30 + py), (mx, 38 + py)], False), None, 3)
            self._ink(g, smooth([(mx - 21 * mw, 39 + py - sm), (mx - 10 * mw, 46 + py), (mx, 38 + py), (mx + 10 * mw, 46 + py), (mx + 21 * mw, 39 + py - sm)], False, 0.8), None, 3.4)
        else:
            self._mouth(g, mx, 40 + py, mw, p, w0=15)
        self._ink(g, smooth([(mx - 9, 20 + py), (mx + 9, 20 + py), (mx, 31 + py)], True, 0.7), self.PINK, 3)
        for s in (-1, 1):
            for k in (-1, 0, 1):
                self._ink(g, oval(mx + s * (15 + abs(k) * 2) * mw, 38 + py + k * 6, 1.6, 1.6), self.HL, 0, False)
                self._ink(g, smooth([(mx + s * 26 * mw, 38 + py + k * 5), (mx + s * 64, 32 + py + k * 12), (mx + s * 104, 34 + py + k * 22)], False), None, 2.2, col=(255, 250, 240))
        eyes = []
        for s in (-1, 1):
            x, ws = self._yaw(s * 37, R, a)
            eyes.append((x, 2 + py, ws, s))
            self._cat_eye(g, x, 2 + py, 18, ws, p, s)
        self._brows(g, eyes, p, 27, 12, 4.5, self.STRIPE)
        self.anchors['mouth'] = g.pt(mx, 44 + py); self.anchors['head'] = g.pt(0, 0); self.anchors['top'] = g.pt(0, -70)

    def _front(self, g, p, f):
        face = p['face']
        td = -1 if face >= 0 else 1
        sw = p['tail'] + math.sin(f * 0.14) * 0.25
        self._tail(g, bez((td * 56, -26), (td * 132, -14), (td * (142 + sw * 20), -104), (td * (106 + sw * 46), -158), 12))
        for s in (-1, 1):                                    # hind paws tucked under the haunches
            self._paw(g, s * 70, -10, 25, 12, self.CREAM)
        body = smooth([(0, -150), (34, -146), (58, -120), (80, -80), (100, -44), (102, -16), (78, -2), (0, 0),
                       (-78, -2), (-102, -16), (-100, -44), (-80, -80), (-58, -120), (-34, -146)], True, 0.5)
        self._ink(g, body, self.FUR, 0, False)
        bib = _I(body, smooth([(0, -156), (32, -124), (27, -66), (0, -36), (-27, -66), (-32, -124)], True, 0.5))
        if bib is not None:
            self._ink(g, bib, self.CREAM, 0, False)
        for s in (-1, 1):
            for yy in (-92, -66, -40):
                st_ = _I(body, oval(s * 104, yy, 26, 6, -s * 14))
                if st_ is not None:
                    self._ink(g, st_, self.STRIPE, 0, False)
        self._ink(g, body, None)
        for s in (-1, 1):                                    # the line of each haunch
            self._ink(g, smooth([(s * 62, -88), (s * 46, -52), (s * 52, -14)], False), None, 3.2, col=self.INK)
        for s, key in ((-1, 'armL'), (1, 'armR')):           # front legs: straight columns down the chest
            sh = (s * 25, -106)
            off = p[key]
            paw = (s * 21 + off[0], -11 + off[1])
            c = limb(sh, paw, -p['bendL' if s < 0 else 'bendR'] * s, 8)
            self._ink(g, _limb_path(c, [16, 16, 15.5, 15, 15, 15, 15.5, 16.5, 17], tip=0.2), self.FUR)
            self._ink(g, oval(sh[0], sh[1] - 8, 17, 13), self.FUR, 0, False)
            ang = math.atan2(c[-1][1] - c[-3][1], c[-1][0] - c[-3][0])
            g.push(paw[0], paw[1], max(-25, min(25, math.degrees(ang) - 90)))
            self._paw(g, 0, 2, 19, 12, self.CREAM)
            g.pop()
            self.anchors['handL' if s < 0 else 'handR'] = g.pt(*paw)
        g.push(p['head_dx'] + face * 10, -196 + p['head_dy'], p['head_rot'], p['head_sx'], p['head_sy'], 0, 56)
        self._head(g, p)
        g.pop()
        self.anchors['belly'] = g.pt(0, -80)

    def _side(self, g, p, f):
        st, amp = p['step'], p['stride']
        sw = p['tail'] + math.sin(f * 0.14) * 0.25
        ph = 2 * math.pi * st
        bob = -abs(math.sin(ph)) * amp * 0.06

        def fore(near, ph_, off=(0, 0)):
            o = 0 if near else 16
            dx = amp * 0.7 * math.cos(ph_); lift = max(0.0, math.sin(ph_)) * amp * 0.4
            paw = (58 + o + dx + off[0], -11 - lift + off[1])
            c = limb((52 + o, -96), paw, 0.05 + lift * 0.004, 8)
            self._ink(g, _limb_path(c, [18, 17.5, 16.5, 15.5, 15, 15, 15.5, 16.5, 17], tip=0.2), self.FUR if near else self.FAR)
            self._paw(g, paw[0] + 5, paw[1] + 2, 19, 11, self.CREAM, d=1)
            return paw

        def hind(near, ph_):
            o = 0 if near else 14
            dx = amp * 0.7 * math.cos(ph_); lift = max(0.0, math.sin(ph_)) * amp * 0.4
            leg = _U(oval(-56 + o, -86, 38, 42, 14), tube([(-64 + o, -58), (-86 + o + dx * 0.6, -34 - lift * 0.5), (-70 + o + dx, -12 - lift)], 15, 11.5))
            self._ink(g, leg, self.FUR if near else self.FAR)
            self._paw(g, -58 + o + dx, -9 - lift, 21, 11, self.CREAM, d=1)

        if p['wheel'] > 0.5:
            self._legs(g, p, [(-60, -70), (56, -70)], -12, 24, 12, 15, self.FUR, toes=self.CREAM)
        else:
            hind(False, ph); fore(False, ph + math.pi, p['armL'])
        g.push(0, bob)
        self._tail(g, bez((-90, -116), (-152, -126), (-162 - sw * 16, -196), (-120 - sw * 30, -238), 12))
        body = smooth([(-100, -104), (-82, -142), (-30, -160), (30, -160), (70, -150), (94, -122), (90, -88), (60, -54), (0, -38), (-60, -50), (-98, -76)], True, 0.5)
        self._ink(g, body, self.FUR, 0, False)
        belly = _I(body, oval(4, -38, 76, 22))
        if belly is not None:
            self._ink(g, belly, self.CREAM, 0, False)
        for x in (-44, -10, 24):
            st_ = _I(body, oval(x, -150, 7, 34, -8))
            if st_ is not None:
                self._ink(g, st_, self.STRIPE, 0, False)
        self._ink(g, body, None)
        g.pop()
        if p['wheel'] <= 0.5:
            hind(True, ph + math.pi)
            paw = fore(True, ph, p['armR'])
            self.anchors['handR'] = g.pt(*paw); self.anchors['handL'] = g.pt(paw[0] + 16, paw[1])
        g.push(108 + p['head_dx'], -178 + bob + p['head_dy'], p['head_rot'], p['head_sx'], p['head_sy'], 0, 56)
        self._head(g, p)
        g.pop()
        self.anchors['belly'] = g.pt(0, -100)


# =====================================================================  BUJJI (rabbit)
class Bujji(_Animal):
    """A small white rabbit from the garden. Nervous, quick, and devoted to carrots. Sits up on her
    haunches with her front paws at her chest; hops in profile. `ear` -1 droops the ears, 1 stands
    them straight up."""
    HEIGHT = 300
    S = 0.92
    shadow = 70
    INK = (116, 104, 128)
    HL = (168, 158, 178)
    STREAK = (255, 255, 255)
    FUR = (252, 250, 246)
    FAR = (232, 230, 236)
    PINK = (252, 176, 190)
    POSE = dict(Character.POSE, ear=0.6, smile=0.4, bendL=0.0, bendR=0.0)

    def _puff(self, g, x, y):
        t = oval(x, y, 19, 17)
        for ox, oy, r in ((12, -9, 11), (-8, -12, 11), (-15, 2, 10), (10, 9, 10)):
            t = _U(t, oval(x + ox, y + oy, r, r))
        self._ink(g, t, self.FUR)

    def _head(self, g, p, lean=0.0):
        yw = p['yaw']
        a = yw * 0.6
        R = 62
        e = p['ear']
        for s in (-1, 1):                                    # long leaf-shaped ears
            bx = s * 20 - yw * 8
            ang = math.radians(-90 + s * (12 + (1 - e) * 66) - lean)
            ux, uy = math.cos(ang), math.sin(ang)
            c = [(bx + ux * 136 * t + (-uy) * s * 9 * math.sin(math.pi * t), -38 + uy * 136 * t + ux * s * 9 * math.sin(math.pi * t)) for t in [i / 6 for i in range(7)]]
            self._ink(g, _limb_path(c, [10, 15, 19, 21, 20, 16, 9], tip=0.7, root=0.2), self.FUR)
            self._ink(g, _limb_path(c[1:6], [5, 9, 11.5, 11, 7], tip=0.6, root=0.5), self.PINK, 0, False)
        head = smooth([(0, -50), (34, -45), (54, -20), (61, 8), (57, 30), (39, 48), (16, 56), (0, 57),
                       (-16, 56), (-39, 48), (-57, 30), (-61, 8), (-54, -20), (-34, -45)], True, 0.5)
        self._ink(g, head, self.FUR)
        py = p['pitch'] * 8
        mx, mw = self._yaw(0, R * 0.9, a)
        mw = max(mw, 0.7)
        eyes = []
        for s in (-1, 1):
            x, ws = self._yaw(s * 31, R, a)
            eyes.append((x, -6 + py, ws, s))
            cx, cw = self._yaw(s * 44, R, a)
            self._ink(g, oval(cx, 20 + py, 11 * cw, 7), self.PINK, 0, False, a=0.6)
        if p['mouth_open'] < 0.06:
            sm = p['smile'] * 4
            self._ink(g, smooth([(mx - 6.5, 31 + py), (mx + 6.5, 31 + py), (mx + 5.5, 45 + py), (mx - 5.5, 45 + py)], True, 0.3), (255, 255, 255), 2.6)   # front teeth
            self._ink(g, poly([(mx, 32 + py), (mx, 45 + py)], False), None, 2)
            self._ink(g, oval(mx - 11 * mw, 27 + py, 12 * mw, 9), self.FUR, 0, False)
            self._ink(g, oval(mx + 11 * mw, 27 + py, 12 * mw, 9), self.FUR, 0, False)
            self._ink(g, poly([(mx, 21 + py), (mx, 26 + py)], False), None, 2.8)
            self._ink(g, smooth([(mx - 19 * mw, 27 + py - sm), (mx - 9 * mw, 34 + py), (mx, 26 + py), (mx + 9 * mw, 34 + py), (mx + 19 * mw, 27 + py - sm)], False, 0.8), None, 3)
        else:
            self._mouth(g, mx, 28 + py, mw, p, w0=12)
        self._ink(g, smooth([(mx - 8, 12 + py), (mx + 8, 12 + py), (mx, 22 + py)], True, 0.7), self.PINK, 2.8)
        for s in (-1, 1):
            for k in (-1, 0, 1):
                self._ink(g, smooth([(mx + s * 22 * mw, 27 + py + k * 3), (mx + s * 50, 22 + py + k * 9), (mx + s * 78, 24 + py + k * 17)], False), None, 1.8, col=self.HL)
        q = dict(p); q['pupil_s'] = p['pupil_s'] * 1.5
        for x, y, ws, s in eyes:
            self._eye(g, x, y, 14, ws, q, self.FUR, pupil_col=(74, 44, 56), side=s)
        self._brows(g, eyes, p, 22, 9, 3.2, self.INK)
        self.anchors['mouth'] = g.pt(mx, 32 + py); self.anchors['head'] = g.pt(0, 0); self.anchors['top'] = g.pt(0, -56)

    def _front(self, g, p, f):
        face = p['face']
        td = -1 if face >= 0 else 1
        self._puff(g, td * 58, -30)
        for s in (-1, 1):                                    # long hind feet pointing at us
            cx = s * 42
            self._ink(g, oval(cx, -10, 30, 13, -s * 6), self.FUR)
            for u in (4, 15):
                self._ink(g, poly([(cx + s * u, -13), (cx + s * (u + 1), -3)], False), None, 2.3, col=self.HL)
        body = smooth([(0, -132), (30, -124), (48, -88), (62, -46), (60, -16), (40, -3), (0, 0), (-40, -3), (-60, -16), (-62, -46), (-48, -88), (-30, -124)], True, 0.5)
        self._ink(g, body, self.FUR)
        for s in (-1, 1):
            self._ink(g, smooth([(s * 42, -72), (s * 27, -42), (s * 31, -12)], False), None, 3)
        self._ink(g, poly([(-11, -92), (-5, -84), (0, -92), (5, -84), (11, -92)], False), None, 2.4, col=self.HL)     # chest fluff
        for s, key in ((-1, 'armL'), (1, 'armR')):           # small front paws held at the chest
            sh = (s * 26, -102)
            off = p[key]
            paw = (s * 15 + off[0], -56 + off[1])
            c = limb(sh, paw, -(p['bendL' if s < 0 else 'bendR'] + (0.18 if abs(off[0]) + abs(off[1]) < 8 else 0.04)) * s, 6)
            self._ink(g, _limb_path(c, [12.5, 12, 11.5, 11, 11, 11.5, 12.5], tip=0.6), self.FUR)
            self._ink(g, oval(sh[0], sh[1] - 6, 13, 10), self.FUR, 0, False)
            ang = math.atan2(c[-1][1] - c[-2][1], c[-1][0] - c[-2][0])
            dx, dy = math.cos(ang), math.sin(ang)
            for k in (-1, 1):
                b0 = (paw[0] - dy * k * 4 - dx * 5, paw[1] + dx * k * 4 - dy * 5)
                self._ink(g, poly([b0, (b0[0] + dx * 9, b0[1] + dy * 9)], False), None, 2.2, col=self.HL)
            self.anchors['handL' if s < 0 else 'handR'] = g.pt(*paw)
        g.push(p['head_dx'] + face * 8, -172 + p['head_dy'], p['head_rot'], p['head_sx'], p['head_sy'], 0, 46)
        self._head(g, p)
        g.pop()
        self.anchors['belly'] = g.pt(0, -70)

    def _side(self, g, p, f):
        st, amp = p['step'], p['stride']
        ph = 2 * math.pi * st
        air = max(0.0, math.sin(ph)) * amp * 0.5
        dxh, dxf = -amp * 0.5 * math.cos(ph), amp * 0.5 * math.cos(ph)

        def fore(near, off=(0, 0)):
            o = 0 if near else 12
            paw = (46 + o + dxf + off[0], -9 + off[1])
            c = limb((38 + o, -66), paw, 0.06, 6)
            self._ink(g, _limb_path(c, [13, 12.5, 11.5, 11, 10.5, 11, 12], tip=0.6), self.FUR if near else self.FAR)
            for k in (0, 1):
                self._ink(g, poly([(paw[0] + 1 + k * 6, paw[1] - 2), (paw[0] + 2 + k * 6, paw[1] + 5)], False), None, 2.1, col=self.HL)
            return paw

        def foot(near):
            o = 0 if near else 12
            self._ink(g, tube([(-54 + o + dxh, -10), (-20 + o + dxh, -10), (16 + o + dxh, -9)], 11, 10.5), self.FUR if near else self.FAR)
            for k in (0, 1):
                self._ink(g, poly([(8 + o + dxh + k * 7, -13), (9 + o + dxh + k * 7, -2)], False), None, 2.1, col=self.HL)

        g.push(0, -air)
        self._puff(g, -76, -54)
        foot(False); fore(False, p['armL'])
        body = smooth([(-76, -60), (-64, -104), (-26, -130), (20, -128), (50, -110), (63, -82), (55, -46), (24, -22), (-36, -16), (-72, -34)], True, 0.5)
        self._ink(g, body, self.FUR)
        foot(True)
        self._ink(g, oval(-34, -50, 39, 35, -12), self.FUR)                               # the big thigh
        paw = fore(True, p['armR'])
        self.anchors['handR'] = g.pt(*paw); self.anchors['handL'] = g.pt(paw[0] + 12, paw[1])
        g.push(66 + p['head_dx'], -146 + p['head_dy'], p['head_rot'], p['head_sx'], p['head_sy'], 0, 46)
        self._head(g, p, lean=-26)
        g.pop()
        self.anchors['belly'] = g.pt(0, -80)
        g.pop()
