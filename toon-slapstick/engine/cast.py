"""cast.py - the rest of the household: Ammamma (grandmother), Chintu (the boy next door),
Laddu (the fat orange cat) and Bujji (the white rabbit). Same pose parameters as Pandu and Gajju.
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


class _Biped(Character):
    """Shared arm and leg drawing for the small cast."""
    LINE = 4.2

    def _simple_arm(self, g, p, side, key, sh, rest, r0, r1, fill, hand_fill=None, sleeve=None, thumb=True, bangle=None):
        off = p[key]
        hand = (sh[0] + rest[0] + off[0], sh[1] + rest[1] + off[1])
        c = limb(sh, hand, -p['bendL' if side < 0 else 'bendR'] * side, 10)
        ang = math.atan2(c[-1][1] - c[-3][1], c[-1][0] - c[-3][0])
        dx, dy = math.cos(ang), math.sin(ang)
        self._ink(g, tube(c, r0, r1, True), fill)
        if sleeve:
            col, upto = sleeve
            self._ink(g, tube(c[:upto], r0 + 3, r0 + 1, True), col)
        hf = hand_fill or fill
        if thumb:
            ta = ang - 1.2 * side
            self._ink(g, tube([(hand[0] + math.cos(ta) * r1 * 0.5, hand[1] + math.sin(ta) * r1 * 0.5),
                               (hand[0] + math.cos(ta + 0.5 * side) * r1 * 1.5, hand[1] + math.sin(ta + 0.5 * side) * r1 * 1.5)], r1 * 0.5, r1 * 0.42), hf)
        self._ink(g, oval(hand[0] + dx * r1 * 0.3, hand[1] + dy * r1 * 0.3, r1 * 1.25, r1 * 1.12, math.degrees(ang)), hf)
        if bangle:
            for k in (3, 2):
                q = c[-k]
                self._ink(g, poly([(q[0] - dy * r1, q[1] + dx * r1), (q[0] + dy * r1, q[1] - dx * r1)], False), None, 4.5, col=bangle)
        self.anchors['handL' if side < 0 else 'handR'] = g.pt(hand[0] + dx * r1, hand[1] + dy * r1)
        return hand, ang

    def _simple_legs(self, g, p, hips, hip_y, r, fill, shoe, foot=(30, 14), feet_y=-12):
        st, amp, face = p['step'], p['stride'], p['face']
        if p['wheel'] > 0.5:
            self._legs(g, p, [(-hips, hip_y), (hips, hip_y)], feet_y, foot[0], foot[1], r, shoe, toes=shoe)
            return
        for i, hx0 in enumerate((-hips, hips)):
            ph = 2 * math.pi * (st + i * 0.5)
            key = 'footL' if i == 0 else 'footR'
            dx = amp * math.cos(ph) + p[key][0]
            lift = max(0.0, math.sin(ph)) * amp * 0.5 - p[key][1]
            side = -1 if i == 0 else 1
            hx = hx0 * (1 - 0.35 * abs(face))
            fx, fy = hx + dx + face * 5, feet_y - lift
            c = limb((hx, hip_y), (fx, fy - foot[1] * 0.4), 0.05 * side + lift * 0.004 * (face or side), 6)
            self._ink(g, tube(c, r, r * 0.86, False), fill)
            self._ink(g, oval(fx + (face * foot[0] * 0.35 if abs(face) > 0.2 else side * 4), fy, foot[0], foot[1]), shoe)


# =====================================================================  AMMAMMA
class Ammamma(_Biped):
    """The grandmother who runs the house. Cotton saree, silver bun, big red bindi. Kind, but nobody
    argues with her ladle."""
    HEIGHT = 560
    shadow = 150
    INK = (70, 40, 36)
    STREAK = (250, 240, 220)
    SKIN = (200, 140, 100)
    HAIR = (226, 226, 232)
    SAREE = (44, 140, 112)
    BORDER = (236, 180, 52)
    BLOUSE = (150, 40, 60)
    POSE = dict(Character.POSE, bendL=0.3, bendR=0.3, smile=0.5)

    def draw(self, g, p, f):
        self.begin(g, p)
        face = p['face']
        sway = math.sin(2 * math.pi * p['step']) * p['stride'] * 0.2
        bob = -abs(math.sin(2 * math.pi * p['step'])) * p['stride'] * 0.08
        for i, s in enumerate((-1, 1)):                    # feet peeping out under the hem
            ph = 2 * math.pi * (p['step'] + i * 0.5)
            fx = s * 46 + p['stride'] * math.cos(ph) * 0.7 + face * 14
            self._ink(g, oval(fx, -8 - max(0, math.sin(ph)) * p['stride'] * 0.3, 30, 13), self.SKIN)
        g.push(0, bob)
        far = 'armR' if face > 0.35 else 'armL' if face < -0.35 else None
        arm = lambda side, key: self._simple_arm(g, p, side, key, (side * 74 * (1 - 0.45 * abs(face)), -372), (side * 34, 126), 21, 17, self.SKIN,
                                                 sleeve=(self.BLOUSE, 5), bangle=self.BORDER)
        if far:
            arm(1 if far == 'armR' else -1, far)
        # saree: a bell from the shoulders to the floor
        skirt = smooth([(-66, -400), (66, -400), (96, -300), (118, -150), (150 + sway, -14), (100 + sway, -4), (50 + sway, -16), (0 + sway, -4),
                        (-50 + sway, -16), (-100 + sway, -4), (-150 + sway, -14), (-118, -150), (-96, -300)], True, 0.4)
        self._ink(g, skirt, self.SAREE)
        hem = skia.Op(skirt, poly([(-200, -46), (200, -46), (200, 20), (-200, 20)]), skia.kIntersect_PathOp)
        if hem is not None:
            self._ink(g, hem, self.BORDER, 0, False)
            self._ink(g, skirt, None)
        for x in (-34, -8, 18):                            # pleats
            self._ink(g, poly([(x + 16, -250), (x + sway * 0.6, -50)], False), None, 3, col=(30, 104, 84))
        pallu = smooth([(-74, -396), (-20, -404), (96, -262), (104, -206), (40, -236), (-80, -330)], True, 0.5)   # drape over the shoulder
        self._ink(g, pallu, (58, 160, 128))
        self._ink(g, smooth([(-78, -340), (40, -244), (104, -212)], False), None, 9, col=self.BORDER)
        if not far:
            arm(-1, 'armL'); arm(1, 'armR')
        # ---- head
        g.push(p['head_dx'] + face * 8, -468 + p['head_dy'], p['head_rot'], p['head_sx'], p['head_sy'], 0, 70)
        a = p['yaw'] * 0.6
        R = 78
        self._ink(g, oval(-p['yaw'] * 40, -86, 40, 36), self.HAIR)                     # bun
        for s in (-1, 1):
            ex = s * 76 - p['yaw'] * 16
            self._ink(g, oval(ex, 4, 13, 18), self.SKIN)
            self._ink(g, oval(ex, 26, 6, 7), self.BORDER, 2.5)
        head = smooth([(0, -84), (56, -72), (80, -14), (70, 44), (34, 78), (0, 84), (-34, 78), (-70, 44), (-80, -14), (-56, -72)], True, 0.5)
        self._ink(g, head, self.SKIN)
        px_, _ = self._yaw(0, R, a)
        hair = skia.Op(head, smooth([(-110, -110), (110, -110), (96, -30), (px_ + 30, -52), (px_, -34), (px_ - 30, -52), (-96, -30)], True, 0.5), skia.kIntersect_PathOp)
        if hair is not None:
            self._ink(g, hair, self.HAIR)
        self._ink(g, poly([(px_, -80), (px_, -38)], False), None, 3, col=(170, 170, 180))
        py = p['pitch'] * 10
        self._ink(g, oval(px_, -16 + py, 8, 8), (214, 40, 44), 0, False)                 # bindi
        eyes = []
        for s in (-1, 1):
            x, ws = self._yaw(s * 30, R, a)
            eyes.append((x, 8 + py, ws, s))
        nx_, nw = self._yaw(0, R * 0.95, a)
        self._ink(g, smooth([(nx_ - 2, 14 + py), (nx_ + 10 * (1 if p['yaw'] >= 0 else -1), 36 + py), (nx_ - 4, 38 + py)], False), None, 3.5)
        self._ink(g, oval(nx_ + 12 * (1 if p['yaw'] >= 0 else -1), 32 + py, 2.5, 2.5), self.BORDER, 0, False)
        self._mouth(g, nx_, 54 + py, max(nw, 0.7), p, w0=20)
        for x, y, ws, s in eyes:
            self._eye(g, x, y, 15, ws, p, self.SKIN, pupil_col=(60, 36, 30), side=s)
            self._ink(g, poly([(x + s * 17 * ws, y + 2), (x + s * 26 * ws, y - 3)], False), None, 2.5, a=0.7)      # laugh line
            lift = p['brow'] + (p['brow_asym'] * 10 if s > 0 else -p['brow_asym'] * 4)
            t = math.radians(p['brow_ang']) * s
            d = (math.cos(t) * 15 * ws, -math.sin(t) * 15)
            self._ink(g, poly([(x - d[0], y - 24 - lift - d[1]), (x + d[0], y - 24 - lift + d[1])], False), None, 5, col=(150, 150, 160))
        self.anchors['mouth'] = g.pt(nx_, 58 + py); self.anchors['head'] = g.pt(0, 0); self.anchors['top'] = g.pt(0, -100)
        g.pop()
        if far:
            arm(-1 if far == 'armR' else 1, 'armL' if far == 'armR' else 'armR')
        self.anchors['belly'] = g.pt(0, -220)
        g.pop()
        self.end(g)


# =====================================================================  CHINTU
class Chintu(_Biped):
    """The boy next door, about seven. Striped T-shirt, shorts, a tuft of hair that never lies flat.
    Gajju's partner in mischief."""
    HEIGHT = 390
    shadow = 90
    INK = (60, 36, 34)
    STREAK = (250, 240, 220)
    SKIN = (204, 146, 104)
    HAIR = (40, 34, 40)
    SHIRT = (236, 76, 64)
    STRIPE = (252, 214, 80)
    SHORTS = (58, 92, 160)
    POSE = dict(Character.POSE, bendL=0.2, bendR=0.2, smile=0.7)

    def draw(self, g, p, f):
        self.begin(g, p)
        face = p['face']
        bob = -abs(math.sin(2 * math.pi * p['step'])) * p['stride'] * 0.12
        self._simple_legs(g, p, 30, -112, 17, self.SKIN, (120, 76, 52), foot=(27, 12))
        g.push(0, bob)
        far = 'armR' if face > 0.35 else 'armL' if face < -0.35 else None
        arm = lambda side, key: self._simple_arm(g, p, side, key, (side * 52 * (1 - 0.45 * abs(face)), -214), (side * 22, 88), 15, 13, self.SKIN, sleeve=(self.SHIRT, 4))
        if far:
            arm(1 if far == 'armR' else -1, far)
        self._ink(g, smooth([(-50, -148), (50, -148), (54, -100), (30, -86), (8, -92), (0, -110), (-8, -92), (-30, -86), (-54, -100)], True, 0.4), self.SHORTS)
        shirt = smooth([(-44, -232), (44, -232), (58, -200), (56, -136), (0, -128), (-56, -136), (-58, -200)], True, 0.5)
        self._ink(g, shirt, self.SHIRT, 0, False)
        for yy in (-206, -178, -150):
            st_ = skia.Op(shirt, poly([(-80, yy), (80, yy), (80, yy + 13), (-80, yy + 13)]), skia.kIntersect_PathOp)
            if st_ is not None:
                self._ink(g, st_, self.STRIPE, 0, False)
        self._ink(g, shirt, None)
        if not far:
            arm(-1, 'armL'); arm(1, 'armR')
        g.push(p['head_dx'] + face * 8, -300 + p['head_dy'], p['head_rot'], p['head_sx'], p['head_sy'], 0, 70)
        a = p['yaw'] * 0.6
        R = 80
        for s in (-1, 1):
            self._ink(g, oval(s * 80 - p['yaw'] * 16, 8, 14, 19), self.SKIN)
        head = smooth([(0, -80), (58, -68), (82, -10), (72, 44), (36, 74), (0, 80), (-36, 74), (-72, 44), (-82, -10), (-58, -68)], True, 0.5)
        self._ink(g, head, self.SKIN)
        hx_, _ = self._yaw(0, R, a)
        hair = skia.Op(head, smooth([(-120, -120), (120, -120), (92, -16), (hx_ + 44, -44), (hx_ + 10, -30), (hx_ - 30, -46), (-92, -16)], True, 0.5), skia.kIntersect_PathOp)
        if hair is not None:
            self._ink(g, hair, self.HAIR)
        self._ink(g, smooth([(-30, -76), (-22, -108), (-6, -84), (6, -116), (18, -86), (34, -104), (36, -74)], True, 0.5), self.HAIR)   # the tuft
        py = p['pitch'] * 10
        eyes = []
        for s in (-1, 1):
            x, ws = self._yaw(s * 32, R, a)
            eyes.append((x, 6 + py, ws, s))
        nx_, nw = self._yaw(0, R * 0.95, a)
        self._ink(g, poly(arc_pts(nx_, 30 + py, 7, 5, 20, 160, 5), False), None, 3.5)
        self._mouth(g, nx_, 48 + py, max(nw, 0.7), p, w0=22)
        for x, y, ws, s in eyes:
            self._eye(g, x, y, 18, ws, p, self.SKIN, pupil_col=(54, 34, 30), side=s)
            lift = p['brow'] + (p['brow_asym'] * 10 if s > 0 else -p['brow_asym'] * 4)
            t = math.radians(p['brow_ang']) * s
            d = (math.cos(t) * 15 * ws, -math.sin(t) * 15)
            self._ink(g, poly([(x - d[0], y - 28 - lift - d[1]), (x + d[0], y - 28 - lift + d[1])], False), None, 6, col=self.HAIR)
        self.anchors['mouth'] = g.pt(nx_, 52 + py); self.anchors['head'] = g.pt(0, 0); self.anchors['top'] = g.pt(0, -104)
        g.pop()
        if far:
            arm(-1 if far == 'armR' else 1, 'armL' if far == 'armR' else 'armR')
        self.anchors['belly'] = g.pt(0, -170)
        g.pop()
        self.end(g)


# =====================================================================  LADDU (cat)
class Laddu(_Biped):
    """A fat orange tabby who believes the house is his. Lazy, smug, and very fast when milk is involved."""
    HEIGHT = 250
    shadow = 86
    INK = (110, 56, 30)
    STREAK = (255, 236, 200)
    FUR = (244, 156, 66)
    STRIPE = (212, 110, 40)
    CREAM = (255, 236, 200)
    PINK = (250, 150, 150)
    POSE = dict(Character.POSE, lid=0.32, smile=0.6, tail=0.0, bendL=0.15, bendR=0.15)

    def draw(self, g, p, f):
        self.begin(g, p)
        face = p['face']
        bob = -abs(math.sin(2 * math.pi * p['step'])) * p['stride'] * 0.12
        td = -1 if face >= 0 else 1                         # tail curls up behind
        sw = p['tail'] + math.sin(f * 0.14) * 0.25
        tl = bez((td * 50, -40), (td * 110, -30), (td * (126 + sw * 20), -110), (td * (92 + sw * 46), -168), 12)
        self._ink(g, tube(tl, 15, 12, True), self.FUR)
        for i in (3, 6, 9):
            q, q2 = tl[i], tl[i + 1]
            d = math.hypot(q2[0] - q[0], q2[1] - q[1]) or 1
            n = (-(q2[1] - q[1]) / d, (q2[0] - q[0]) / d)
            self._ink(g, poly([(q[0] + n[0] * 12, q[1] + n[1] * 12), (q[0] - n[0] * 12, q[1] - n[1] * 12)], False), None, 6, col=self.STRIPE)
        self._simple_legs(g, p, 34, -40, 20, self.FUR, self.CREAM, foot=(27, 14), feet_y=-12)
        g.push(0, bob)
        far = 'armR' if face > 0.35 else 'armL' if face < -0.35 else None
        arm = lambda side, key: self._simple_arm(g, p, side, key, (side * 54 * (1 - 0.45 * abs(face)), -112), (side * 20, 56), 17, 15, self.FUR, hand_fill=self.CREAM, thumb=False)
        if far:
            arm(1 if far == 'armR' else -1, far)
        body = oval(0, -78, 76, 70)
        self._ink(g, body, self.FUR)
        self._ink(g, oval(face * 14, -66, 46, 48), self.CREAM, 0, False)
        for s in (-1, 1):
            for yy in (-104, -78):
                st_ = skia.Op(body, oval(s * 84, yy, 26, 8), skia.kIntersect_PathOp)
                if st_ is not None:
                    self._ink(g, st_, self.STRIPE, 0, False)
        self._ink(g, body, None)
        if not far:
            arm(-1, 'armL'); arm(1, 'armR')
        g.push(p['head_dx'] + face * 8, -166 + p['head_dy'], p['head_rot'], p['head_sx'], p['head_sy'], 0, 56)
        a = p['yaw'] * 0.6
        R = 84
        for s in (-1, 1):
            ex = s * 56 - p['yaw'] * 14
            self._ink(g, smooth([(ex - 26, -40), (ex + s * 12, -104), (ex + 28, -36)], True, 0.25), self.FUR)
            self._ink(g, smooth([(ex - 12, -46), (ex + s * 9, -86), (ex + 16, -44)], True, 0.25), self.PINK, 0, False)
        head = smooth([(0, -62), (56, -54), (88, -6), (96, 30), (58, 60), (0, 66), (-58, 60), (-96, 30), (-88, -6), (-56, -54)], True, 0.5)
        self._ink(g, head, self.FUR)
        hx_, _ = self._yaw(0, R, a)
        for k in (-22, 0, 22):                              # forehead stripes
            self._ink(g, poly([(hx_ + k, -60), (hx_ + k * 0.8, -38)], False), None, 7, col=self.STRIPE)
        py = p['pitch'] * 8
        mx, mw = self._yaw(0, R * 0.9, a)
        mw = max(mw, 0.7)
        self._ink(g, oval(mx, 34 + py, 46 * mw, 28), self.CREAM, 0, False)
        eyes = []
        for s in (-1, 1):
            x, ws = self._yaw(s * 36, R, a)
            eyes.append((x, 0 + py, ws, s))
        self._ink(g, smooth([(mx - 8, 18 + py), (mx + 8, 18 + py), (mx, 28 + py)], True, 0.8), self.PINK, 3)
        if p['mouth_open'] < 0.06:                          # the cat 'w' mouth
            sm = p['smile'] * 5
            self._ink(g, smooth([(mx - 22 * mw, 34 + py - sm), (mx - 10 * mw, 42 + py), (mx, 30 + py), (mx + 10 * mw, 42 + py), (mx + 22 * mw, 34 + py - sm)], False, 0.8), None, 3.5)
        else:
            self._mouth(g, mx, 36 + py, mw, p, w0=16)
        for s in (-1, 1):                                   # whiskers
            wx, _ = self._yaw(s * 52, R, a)
            for k in (-1, 0, 1):
                self._ink(g, poly([(wx, 34 + py + k * 5), (wx + s * 46, 28 + py + k * 14)], False), None, 2.5, col=(255, 250, 240))
        for x, y, ws, s in eyes:
            self._eye(g, x, y, 17, ws, p, self.FUR, white=(226, 240, 150), pupil_col=(40, 50, 30), side=s)
            lift = p['brow'] + (p['brow_asym'] * 10 if s > 0 else -p['brow_asym'] * 4)
            t = math.radians(p['brow_ang']) * s
            d = (math.cos(t) * 13 * ws, -math.sin(t) * 13)
            self._ink(g, poly([(x - d[0], y - 26 - lift - d[1]), (x + d[0], y - 26 - lift + d[1])], False), None, 5, col=self.STRIPE)
        self.anchors['mouth'] = g.pt(mx, 40 + py); self.anchors['head'] = g.pt(0, 0); self.anchors['top'] = g.pt(0, -70)
        g.pop()
        if far:
            arm(-1 if far == 'armR' else 1, 'armL' if far == 'armR' else 'armR')
        self.anchors['belly'] = g.pt(0, -78)
        g.pop()
        self.end(g)


# =====================================================================  BUJJI (rabbit)
class Bujji(_Biped):
    """A small white rabbit from the garden. Nervous, quick, and devoted to carrots. `ear` -1 droops the
    ears, 1 stands them straight up."""
    HEIGHT = 300
    shadow = 70
    INK = (116, 104, 128)
    STREAK = (255, 255, 255)
    FUR = (252, 250, 246)
    PINK = (252, 176, 190)
    POSE = dict(Character.POSE, ear=0.6, smile=0.4, bendL=0.15, bendR=0.15)

    def draw(self, g, p, f):
        self.begin(g, p)
        face = p['face']
        bob = -abs(math.sin(2 * math.pi * p['step'])) * p['stride'] * 0.16
        td = -1 if face >= 0 else 1
        self._ink(g, oval(td * 58, -52, 22, 20), self.FUR)                               # cotton tail
        self._simple_legs(g, p, 28, -34, 16, self.FUR, self.FUR, foot=(34, 13), feet_y=-11)
        g.push(0, bob)
        far = 'armR' if face > 0.35 else 'armL' if face < -0.35 else None
        arm = lambda side, key: self._simple_arm(g, p, side, key, (side * 40 * (1 - 0.45 * abs(face)), -92), (side * 16, 44), 13, 12, self.FUR, thumb=False)
        if far:
            arm(1 if far == 'armR' else -1, far)
        self._ink(g, smooth([(0, -122), (40, -110), (58, -66), (44, -28), (0, -20), (-44, -28), (-58, -66), (-40, -110)], True, 0.5), self.FUR)
        if not far:
            arm(-1, 'armL'); arm(1, 'armR')
        g.push(p['head_dx'] + face * 6, -148 + p['head_dy'], p['head_rot'], p['head_sx'], p['head_sy'], 0, 46)
        a = p['yaw'] * 0.6
        R = 64
        e = p['ear']
        for s in (-1, 1):                                   # long ears
            bx = s * 26 - p['yaw'] * 10
            ang = math.radians(-90 + s * (16 + (1 - e) * 62))
            tip = (bx + math.cos(ang) * 124, -40 + math.sin(ang) * 124)
            mid = (bx + math.cos(ang) * 60 + s * 10, -40 + math.sin(ang) * 60 + (1 - e) * 12)
            self._ink(g, tube([(bx, -40), mid, tip], 17, 13, True), self.FUR)
            self._ink(g, tube([(bx + (mid[0] - bx) * 0.3, -40 + (mid[1] + 40) * 0.3), mid, (mid[0] + (tip[0] - mid[0]) * 0.7, mid[1] + (tip[1] - mid[1]) * 0.7)], 7, 5, True), self.PINK, 0, False)
        head = smooth([(0, -52), (44, -44), (66, -4), (70, 26), (42, 50), (0, 54), (-42, 50), (-70, 26), (-66, -4), (-44, -44)], True, 0.5)
        self._ink(g, head, self.FUR)
        py = p['pitch'] * 8
        mx, mw = self._yaw(0, R * 0.9, a)
        mw = max(mw, 0.7)
        eyes = []
        for s in (-1, 1):
            x, ws = self._yaw(s * 28, R, a)
            eyes.append((x, -2 + py, ws, s))
            cx, cw = self._yaw(s * 44, R, a)
            self._ink(g, oval(cx, 22 + py, 11 * cw, 7), self.PINK, 0, False, a=0.7)
        self._ink(g, smooth([(mx - 7, 14 + py), (mx + 7, 14 + py), (mx, 23 + py)], True, 0.8), self.PINK, 3)
        if p['mouth_open'] < 0.06:
            sm = p['smile'] * 4
            self._ink(g, smooth([(mx - 16 * mw, 28 + py - sm), (mx - 7 * mw, 34 + py), (mx, 24 + py), (mx + 7 * mw, 34 + py), (mx + 16 * mw, 28 + py - sm)], False, 0.8), None, 3.2)
            self._ink(g, smooth([(mx - 7, 32 + py), (mx + 7, 32 + py), (mx + 6, 46 + py), (mx - 6, 46 + py)], True, 0.3), (255, 255, 255), 3)   # buck teeth
            self._ink(g, poly([(mx, 33 + py), (mx, 46 + py)], False), None, 2)
        else:
            self._mouth(g, mx, 30 + py, mw, p, w0=13)
        for s in (-1, 1):
            wx, _ = self._yaw(s * 40, R, a)
            for k in (-1, 1):
                self._ink(g, poly([(wx, 26 + py + k * 3), (wx + s * 34, 24 + py + k * 10)], False), None, 2, a=0.7)
        for x, y, ws, s in eyes:
            self._eye(g, x, y, 15, ws, p, self.FUR, pupil_col=(70, 40, 60), side=s)
            lift = p['brow'] + (p['brow_asym'] * 8 if s > 0 else -p['brow_asym'] * 3)
            t = math.radians(p['brow_ang']) * s
            d = (math.cos(t) * 10 * ws, -math.sin(t) * 10)
            self._ink(g, poly([(x - d[0], y - 22 - lift - d[1]), (x + d[0], y - 22 - lift + d[1])], False), None, 3.5)
        self.anchors['mouth'] = g.pt(mx, 34 + py); self.anchors['head'] = g.pt(0, 0); self.anchors['top'] = g.pt(0, -56)
        g.pop()
        if far:
            arm(-1 if far == 'armR' else 1, 'armL' if far == 'armR' else 'armR')
        self.anchors['belly'] = g.pt(0, -70)
        g.pop()
        self.end(g)
