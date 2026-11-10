"""chars.py - Pandu (panda) and Gajju (baby elephant) as fully parametric 2D characters.

Each character is redrawn every frame from its pose parameters, so it can squash, stretch,
smear, turn its head, blink and act. Local coordinates: (0,0) is the point between the feet,
up is negative y.
"""
import math
import skia
from toon import Actor, oval, poly, smooth, tube, limb, bez, arc_pts, GROUND


def _mirror(p):
    return (-p[0], p[1])


class Character(Actor):
    POSE = dict(
        face=0.0,                # body turn: -1 = facing screen-left, 0 = front, 1 = screen-right
        yaw=0.0, pitch=0.0,      # head turn / nod, -1..1 (features slide around the head)
        head_dx=0.0, head_dy=0.0, head_rot=0.0, head_sx=1.0, head_sy=1.0,
        eye_open=1.0, eye_pop=1.0, pupil=(0.0, 0.0), pupil_s=1.0, happy=0.0,
        lid=0.0,                 # upper lid drop 0..1 (sleepy, suspicious)
        brow=0.0, brow_ang=0.0,  # brow lift (px up) and tilt in degrees: + angry, - sad
        brow_asym=0.0,           # raises one brow only (cheeky), -1..1
        mouth_w=1.0, mouth_open=0.0, smile=0.3, cheeks=0.0,
        armL=(0.0, 0.0), armR=(0.0, 0.0), bendL=0.12, bendR=0.12,  # hand offsets from the rest position
        handL='mitt', handR='mitt',
        step=0.0, stride=0.0, wheel=0.0,   # walk cycle phase (cycles), stride px, run-blur amount
        footL=(0.0, 0.0), footR=(0.0, 0.0),
        ground=GROUND, sweat=0.0,
    )
    INK = (45, 40, 48)
    smear_from = 46.0  # px per frame where smearing starts

    # ---- shared helpers
    def begin(self, g, p):
        g.ink_col = self.INK
        vx, vy = p['_fx'], p['_fy']
        sp = math.hypot(vx, vy)
        self._smear = 0.0
        if self.smear and sp > self.smear_from:
            k = min(1.0 + (sp - self.smear_from) / 90.0, 2.3)
            self._smear = k
            ang = math.degrees(math.atan2(vy, vx))
            cx, cy = p['x'] + vx * 0.15, p['y'] - self.HEIGHT * 0.5 * p['sy'] + vy * 0.15
            m = skia.Matrix()
            m.setRotate(ang, cx, cy)
            m.preScale(k, 1 / math.sqrt(k), cx, cy)
            m.preRotate(-ang, cx, cy)
            g.push_m(m)
            self._speedlines(g, p, vx, vy, sp)
        else:
            g.push()
        g.push(p['x'], p['y'], p['rot'], p['sx'], p['sy'])

    def end(self, g):
        g.pop(); g.pop()

    def _speedlines(self, g, p, vx, vy, sp):
        cx, cy = p['x'], p['y'] - self.HEIGHT * 0.5
        d = (-vx / sp, -vy / sp)
        for i, off in enumerate((-0.38, -0.16, 0.08, 0.3)):
            ox, oy = -d[1] * off * self.HEIGHT, d[0] * off * self.HEIGHT
            a = (cx + ox + d[0] * self.HEIGHT * 0.25, cy + oy + d[1] * self.HEIGHT * 0.25)
            b = (a[0] + d[0] * (120 + 60 * (i % 2)), a[1] + d[1] * (120 + 60 * (i % 2)))
            g.shape(poly([a, b], False), None, True, 5, self.STREAK, 0.75)

    def _yaw(self, x0, R, a):
        """Slide a face feature around a round head. Returns (x, width_scale)."""
        t0 = math.asin(max(-0.98, min(0.98, x0 / R)))
        t = t0 + a
        return R * math.sin(t), max(0.12, math.cos(t)) / max(0.3, math.cos(t0))

    LINE = None

    def _ink(self, g, path, fill, w=None, ink=True, col=None, a=1.0):
        g.shape(path, fill, ink, w or self.LINE, col or self.INK, a)

    def _eye(self, g, cx, cy, r, ws, p, lid_col, white=(255, 255, 255), pupil_col=(40, 34, 40), side=1, closed_col=None):
        e = p['eye_open']; pop = p['eye_pop']
        r = r * pop
        rx, ry = r * ws, r * min(e, 1.35)
        if e <= 0.1:
            # closed eye: ^ when happy, gentle downward curve otherwise
            k = 1 if p['happy'] > 0.5 else -0.55
            pts = [(cx - rx, cy + 3 * k), (cx, cy - 9 * k), (cx + rx, cy + 3 * k)]
            self._ink(g, smooth(pts, False), None, 6, col=closed_col)
            return
        eye = oval(cx, cy, rx, ry)
        self._ink(g, eye, white, 4)
        px, py = p['pupil']
        pr = r * 0.5 * p['pupil_s']
        ex, ey = cx + px * (rx - pr * ws) * 0.9, cy + py * (ry - min(pr, ry * 0.9)) * 0.9
        pup = oval(ex, ey, pr * ws, min(pr, ry * 0.92))
        self._ink(g, pup, pupil_col, 0, False)
        self._ink(g, oval(ex - pr * 0.3 * ws, ey - pr * 0.35, pr * 0.3 * ws, pr * 0.3), (255, 255, 255), 0, False)
        lid = p['lid']; ang = p['brow_ang']
        if lid > 0.02 or abs(ang) > 6:
            # upper lid: skin-coloured cover above a tilted line, clipped to the eye
            drop = -ry + 2 * ry * max(lid, 0.18 if abs(ang) > 6 else 0)
            t = math.radians(ang * 0.8) * side
            dx, dy = math.cos(t), math.sin(t)
            a = (cx - dx * 3 * rx, cy + drop - dy * 3 * rx)
            b = (cx + dx * 3 * rx, cy + drop + dy * 3 * rx)
            cover = poly([a, b, (b[0], b[1] - 4 * ry), (a[0], a[1] - 4 * ry)])
            cut = skia.Op(cover, eye, skia.kIntersect_PathOp)
            if cut is not None:
                self._ink(g, cut, lid_col, 4)

    def _mouth(self, g, cx, cy, ws, p, w0=22):
        w = w0 * p['mouth_w'] * ws
        o = p['mouth_open']; s = p['smile']
        if o < 0.06:
            pts = [(cx - w, cy - s * 9), (cx, cy + s * 9), (cx + w, cy - s * 9)]
            self._ink(g, smooth(pts, False, 0.9), None, 5)
            return
        h = 8 + 44 * o
        top = [(cx - w, cy - s * 7), (cx, cy + 2 - s * 2), (cx + w, cy - s * 7)]
        bot = [(cx + w * 0.82, cy + h * 0.62), (cx, cy + h), (cx - w * 0.82, cy + h * 0.62)]
        m = smooth(top + bot, True, 0.7)
        self._ink(g, m, (96, 28, 44), 5)
        tongue = skia.Op(oval(cx, cy + h * 0.98, w * 0.7, h * 0.42), m, skia.kIntersect_PathOp)
        if tongue is not None:
            self._ink(g, tongue, (240, 120, 130), 0, False)
        self._ink(g, m, None, 5)

    def _legs(self, g, p, hips, feet_y, foot_rx, foot_ry, leg_r, fill, toes=None):
        """Draws both legs with the walk cycle. Returns nothing; feet stay near the ground."""
        st, amp, wh = p['step'], p['stride'], p['wheel']
        face = p['face']
        if wh > 0.5:   # run blur: a wheel of feet
            R = foot_rx * 1.7
            cy = feet_y - R * 0.62
            self._ink(g, oval(0, cy, R * 1.3, R), fill, 0, False, a=0.22)
            for i in range(3):
                a0 = 360 * (st + i / 3)
                self._ink(g, poly(arc_pts(0, cy, R * 1.45, R * 1.12, a0, a0 + 80), False), None, 5, col=self.STREAK, a=0.85)
                self._ink(g, poly(arc_pts(0, cy, R * 0.95, R * 0.72, a0 + 40, a0 + 110), False), None, 4, col=self.INK, a=0.5)
            for i in range(4):
                a = 2 * math.pi * (st + i / 4)
                fx, fy = math.cos(a) * R * 1.12, cy + math.sin(a) * R * 0.86
                self._ink(g, oval(fx, fy, foot_rx * 0.86, foot_ry * 0.86, math.degrees(a) + 90), fill, 4, a=1.0 if i % 2 == 0 else 0.6)
            return
        for i, hip in enumerate(hips):
            ph = 2 * math.pi * (st + i * 0.5)
            dx = amp * math.cos(ph) + p['footL' if i == 0 else 'footR'][0]
            lift = max(0.0, math.sin(ph)) * amp * 0.5 - p['footL' if i == 0 else 'footR'][1]
            hx = hip[0] * (1 - 0.35 * abs(face))
            fx = hx + dx + face * 8
            fy = feet_y - lift
            side = -1 if i == 0 else 1
            knee = 0.16 * side * (1 - abs(face)) + 0.22 * face + lift * 0.004 * (face or side)
            c = limb((hx, hip[1]), (fx, fy - foot_ry * 0.5), knee, 8)
            self._ink(g, tube(c, leg_r * 1.12, leg_r * 0.86, False), fill)
            tilt = -lift * 0.3 * (face or side)
            foot = smooth([(fx - foot_rx * 0.9 + face * foot_rx * 0.3, fy + foot_ry * 0.75), (fx - foot_rx + face * foot_rx * 0.3, fy - foot_ry * 0.2),
                           (fx - foot_rx * 0.45 + face * foot_rx * 0.3, fy - foot_ry), (fx + foot_rx * 0.45 + face * foot_rx * 0.3, fy - foot_ry),
                           (fx + foot_rx + face * foot_rx * 0.3, fy - foot_ry * 0.2), (fx + foot_rx * 0.9 + face * foot_rx * 0.3, fy + foot_ry * 0.75)], True, 0.7)
            if tilt:
                m = skia.Matrix(); m.setRotate(tilt, fx, fy); q = skia.Path(); foot.transform(m, q); foot = q
            self._ink(g, foot, fill)
            cx0 = fx + face * foot_rx * 0.3
            if toes:      # elephant: three toenails
                for k in (-1, 0, 1):
                    tx = cx0 + face * foot_rx * 0.3 + k * foot_rx * 0.52 * (1 - 0.4 * abs(face))
                    self._ink(g, smooth([(tx - foot_rx * 0.2, fy + foot_ry * 0.7), (tx - foot_rx * 0.17, fy + foot_ry * 0.1), (tx, fy - foot_ry * 0.12), (tx + foot_rx * 0.17, fy + foot_ry * 0.1), (tx + foot_rx * 0.2, fy + foot_ry * 0.7)], True, 0.7), toes, 3)
                kx, ky = c[4]
                self._ink(g, poly(arc_pts(kx, ky, leg_r * 0.6, 5, 20, 160, 6), False), None, 2.5, a=0.7)      # knee wrinkle
            else:         # bear paw: five toes along the front, each with a small claw
                hl = getattr(self, 'HL', self.INK); claw = getattr(self, 'CLAW', (250, 240, 214))
                for k in (-2, -1, 0, 1, 2):
                    tx = cx0 + face * foot_rx * 0.4 + k * foot_rx * 0.36 * (1 - 0.35 * abs(face))
                    ty = fy + foot_ry * (0.7 - 0.1 * abs(k))
                    self._ink(g, oval(tx, ty, foot_rx * 0.2, foot_ry * 0.56), fill, 4)
                self._ink(g, foot, fill)
                for k in (-1.5, -0.5, 0.5, 1.5):
                    tx = cx0 + face * foot_rx * 0.4 + k * foot_rx * 0.36 * (1 - 0.35 * abs(face))
                    self._ink(g, poly([(tx, fy + foot_ry * 0.25), (tx, fy + foot_ry * 0.8)], False), None, 2.5, col=hl)


# =====================================================================  PANDU
class Pandu(Character):
    """The original Pandu face and body (round head, big eye patches, gold glasses, orange scarf)
    on natural panda limbs: thick forelegs that hang from behind the shoulders and end in a broad
    paw with short toes, and sturdy straight hind legs with flat, toed feet."""
    HEIGHT = 560
    shadow = 150
    INK = (38, 34, 42)
    STREAK = (250, 248, 240)
    WHITE = (250, 247, 240)
    BLACK = (58, 54, 64)
    HL = (116, 110, 126)        # lighter line for toe partings on the black fur
    PAD = (226, 158, 168)
    GOLD = (236, 184, 40)
    SCARF = (255, 138, 76)
    UP = 60                     # how far the upper body sits above the old short-legged design
    POSE = dict(Character.POSE, glasses_dy=0.0, glasses_rot=0.0, scarf_fly=0.0, sit=0.0, glasses=1.0, bendL=0.14, bendR=0.14)

    def _arm(self, g, p, side, key):
        face = p['face']
        sh = (side * 108 * (1 - 0.5 * abs(face)), -238 - self.UP)
        rest = (side * 54, 150)
        off = p[key]
        hand = (sh[0] + rest[0] + off[0], sh[1] + rest[1] + off[1])
        bend = -p['bendL' if side < 0 else 'bendR'] * side
        c = limb(sh, hand, bend, 12)
        ang = math.atan2(c[-1][1] - c[-3][1], c[-1][0] - c[-3][0])
        dx, dy = math.cos(ang), math.sin(ang)
        nx, ny = -dy, dx
        deg = math.degrees(ang)
        kind = p['handL' if side < 0 else 'handR']
        # slim at the shoulder, heavy through the forearm, widest at the paw: a real panda foreleg
        prof = [26, 29, 32, 34, 36, 37, 38, 38, 39, 39, 40, 40, 39]
        L, R = [], []
        for i, q in enumerate(c):
            a0, a1 = c[max(i - 1, 0)], c[min(i + 1, 12)]
            d = math.hypot(a1[0] - a0[0], a1[1] - a0[1]) or 1
            n = (-(a1[1] - a0[1]) / d, (a1[0] - a0[0]) / d)
            L.append((q[0] + n[0] * prof[i], q[1] + n[1] * prof[i])); R.append((q[0] - n[0] * prof[i], q[1] - n[1] * prof[i]))
        shape = smooth(L + [(hand[0] + dx * 30, hand[1] + dy * 30)] + R[::-1] + [(sh[0] - (c[1][0] - sh[0]), sh[1] - (c[1][1] - sh[1]))], True, 0.5)
        curled = kind in ('fist', 'grip')
        toes = []
        if kind == 'point':
            toes.append(tube([hand, (hand[0] + dx * 80, hand[1] + dy * 80)], 14, 12))
        elif not curled:                                   # four short toes along the end of the paw
            spread = 1.25 if kind == 'open' else 1.0
            for k in (-1.5, -0.5, 0.5, 1.5):
                tx = hand[0] + dx * (30 - 5 * abs(k)) + nx * k * 19 * spread
                ty = hand[1] + dy * (30 - 5 * abs(k)) + ny * k * 19 * spread
                toes.append(oval(tx, ty, 15 if kind == 'open' else 13, 11.5, deg))
        for t in toes:
            u = skia.Op(shape, t, skia.kUnion_PathOp)
            shape = u if u is not None else shape
        self._ink(g, shape, self.BLACK)
        if kind == 'open':                                 # palm: one big pad and four toe pads
            self._ink(g, oval(hand[0] - dx * 2, hand[1] - dy * 2, 15, 20, deg), self.PAD, 0, False)
            for k in (-1.5, -0.5, 0.5, 1.5):
                self._ink(g, oval(hand[0] + dx * (29 - 5 * abs(k)) + nx * k * 24, hand[1] + dy * (29 - 5 * abs(k)) + ny * k * 24, 6.5, 6, deg), self.PAD, 0, False)
        elif kind != 'point':                              # toe partings
            for k in (-1, 0, 1):
                px_, py_ = hand[0] + nx * k * 19, hand[1] + ny * k * 19
                self._ink(g, poly([(px_ + dx * 14, py_ + dy * 14), (px_ + dx * (32 - 4 * abs(k)), py_ + dy * (32 - 4 * abs(k)))], False), None, 3.5, col=self.HL)
        self.anchors['handL' if side < 0 else 'handR'] = g.pt(hand[0] + dx * 22, hand[1] + dy * 22)

    def _hindlegs(self, g, p):
        st, amp, face = p['step'], p['stride'], p['face']
        for i, hx0 in enumerate((-64, 64)):
            ph = 2 * math.pi * (st + i * 0.5)
            key = 'footL' if i == 0 else 'footR'
            dx = amp * math.cos(ph) + p[key][0]
            lift = max(0.0, math.sin(ph)) * amp * 0.5 - p[key][1]
            side = -1 if i == 0 else 1
            hx = hx0 * (1 - 0.35 * abs(face))
            fx, fy = hx + dx + face * 6, -lift
            fo = face * 20 + (0 if abs(face) > 0.2 else side * 8)
            k = (fx - hx) * 0.5
            leg = smooth([(hx - 46, -150), (hx + 46, -150), (hx + 45 + k, -80), (fx + 43, fy - 40),
                          (fx + 54 + fo, fy - 28), (fx + 58 + fo, fy - 10), (fx + 48 + fo, fy), (fx - 48 + fo, fy), (fx - 58 + fo, fy - 10), (fx - 54 + fo, fy - 28),
                          (fx - 43, fy - 40), (hx - 45 + k, -80)], True, 0.5)
            for kk in (-1.5, -0.5, 0.5, 1.5):               # four toes across the front of the foot
                tx = fx + fo + face * 22 + kk * 25 * (1 - 0.35 * abs(face))
                u = skia.Op(leg, oval(tx, fy - 5, 13, 11), skia.kUnion_PathOp)
                leg = u if u is not None else leg
            self._ink(g, leg, self.BLACK)
            for kk in (-1, 0, 1):
                tx = fx + fo + face * 22 + kk * 25 * (1 - 0.35 * abs(face))
                self._ink(g, poly([(tx, fy - 22), (tx, fy - 4)], False), None, 3.5, col=self.HL)

    def _sole(self, g, cx, cy, s):
        g.push(cx, cy, s * 14)
        for k in (-1.5, -0.5, 0.5, 1.5):
            a1 = math.radians(-90 + k * 30)
            self._ink(g, oval(math.cos(a1) * 44, math.sin(a1) * 54 + 6, 14, 13), self.BLACK)
        self._ink(g, oval(0, 6, 50, 60), self.BLACK)
        self._ink(g, smooth([(-30, 2), (0, -14), (30, 2), (24, 34), (0, 42), (-24, 34)], True, 0.8), self.PAD, 0, False)
        for k in (-1.5, -0.5, 0.5, 1.5):
            a1 = math.radians(-90 + k * 30)
            self._ink(g, oval(math.cos(a1) * 40, math.sin(a1) * 49 + 6, 8, 7), self.PAD, 0, False)
        g.pop()

    def draw(self, g, p, f):
        self.begin(g, p)
        face = p['face']
        U = self.UP
        bob = -abs(math.sin(2 * math.pi * p['step'])) * p['stride'] * 0.10
        sit = p['sit'] > 0.5
        if sit:
            for s in (-1, 1):
                self._ink(g, oval(s * 128, -58, 70, 58), self.BLACK)
        elif p['wheel'] > 0.5:
            self._legs(g, p, [(-64, -150), (64, -150)], -26, 56, 26, 38, self.BLACK)
        else:
            self._hindlegs(g, p)
        g.push(0, bob + (96 if sit else 0))

        def in_front(key, side):
            if abs(face) > 0.35:
                return (side > 0) != (face > 0)
            off = p[key]
            return math.hypot(off[0], off[1]) > 60 or p['handL' if side < 0 else 'handR'] != 'mitt'
        order = [('armL', -1), ('armR', 1)]
        for key, side in order:                            # forelegs hang from behind the shoulders
            if not in_front(key, side):
                self._arm(g, p, side, key)
        if abs(face) > 0.35:
            self._ink(g, oval(-face * 140, -92 - U, 24, 22), self.WHITE)
        body = smooth([(0, -300 - U), (84, -272 - U), (140, -180 - U), (150, -118 - U), (112, -58 - U), (0, -40 - U),
                       (-112, -58 - U), (-150, -118 - U), (-140, -180 - U), (-84, -272 - U)], True, 0.5)
        self._ink(g, body, self.WHITE)
        # scarf
        kx = face * 46 + p['yaw'] * 20
        fly = p['scarf_fly'] - p['_vx'] * 0.035
        tail = bez((kx, -262 - U), (kx + 6 - fly * 40, -230 - U), (kx + 4 - fly * 95, -205 - U - abs(fly) * 30), (kx + 10 - fly * 130, -176 - U - abs(fly) * 62))
        self._ink(g, tube(tail, 15, 21, True), self.SCARF)
        self._ink(g, smooth([(-104, -286 - U), (0, -262 - U), (104, -286 - U), (112, -262 - U), (60, -238 - U), (0, -232 - U), (-60, -238 - U), (-112, -262 - U)], True, 0.5), self.SCARF)
        self._ink(g, oval(kx, -256 - U, 21, 19), self.SCARF)
        for key, side in order:
            if in_front(key, side):
                self._arm(g, p, side, key)
        # ---- head: unchanged from the first version
        g.push(p['head_dx'] + face * 14, -372 - U + p['head_dy'], p['head_rot'], p['head_sx'], p['head_sy'], 0, 96)
        a = p['yaw'] * 0.6
        R = 120
        for s in (-1, 1):
            self._ink(g, oval(s * 86 - p['yaw'] * 26, -84 + p['pitch'] * 8, 39, 38), self.BLACK)
        self._ink(g, smooth([(0, -106), (82, -84), (122, -8), (104, 62), (52, 96), (0, 102), (-52, 96), (-104, 62), (-122, -8), (-82, -84)], True, 0.5), self.WHITE)
        py = p['pitch'] * 16
        eyes = []
        for s in (-1, 1):
            x, ws = self._yaw(s * 50, R, a)
            self._ink(g, oval(x + s * 3 * ws, 0 + py, 43 * ws, 54, -s * 18), self.BLACK, 0, False)
            eyes.append((x - s * 3 * ws, -6 + py, ws, s))
        mx, mw = self._yaw(0, R * 0.95, a)
        self._ink(g, oval(mx, 46 + py, 46 * max(mw, 0.7), 32), (255, 255, 252), 3, True, (214, 206, 196))
        self._ink(g, smooth([(mx - 15, 26 + py), (mx + 15, 26 + py), (mx, 42 + py)], True, 0.9), (34, 30, 38))
        self._mouth(g, mx, 58 + py, max(mw, 0.7), p)
        self.anchors['mouth'] = g.pt(mx, 66 + py)
        for x, y, ws, s in eyes:
            self._eye(g, x, y, 24, ws, p, self.BLACK, side=s, closed_col=(240, 236, 228))
        for x, y, ws, s in eyes:
            lift = p['brow'] + (p['brow_asym'] * 14 if s > 0 else -p['brow_asym'] * 6)
            t = math.radians(p['brow_ang']) * s
            bx, by = x, -74 + py - lift
            d = (math.cos(t) * 18 * ws, -math.sin(t) * 18)
            self._ink(g, smooth([(bx - d[0], by - d[1]), (bx, by - 4), (bx + d[0], by + d[1])], False), None, 9, col=self.BLACK)
        if p['glasses'] > 0.5:
            g.push(0, p['glasses_dy'], p['glasses_rot'])
            rims = []
            for x, y, ws, s in eyes:
                rims.append((x, y + 2, 33 * ws))
                self._ink(g, oval(x, y + 2, 33 * ws, 33), None, 10, col=self.INK)
                self._ink(g, oval(x, y + 2, 33 * ws, 33), None, 6, col=self.GOLD)
            (x0, y0, r0), (x1, y1, r1) = rims
            self._ink(g, smooth([(x0 + r0, y0 - 6), ((x0 + x1) / 2, y0 - 16), (x1 - r1, y1 - 6)], False), None, 6, col=self.GOLD)
            self._ink(g, poly([(x0 - r0, y0 - 4), (min(x0 - r0 - 4, -112), y0 - 14)], False), None, 5, col=self.GOLD)
            self._ink(g, poly([(x1 + r1, y1 - 4), (max(x1 + r1 + 4, 112), y1 - 14)], False), None, 5, col=self.GOLD)
            g.pop()
        if p['sweat'] > 0.3:
            for i in range(3):
                sx = 104 + i * 22; sy = -70 + i * 26 - (f * 6 % 24)
                self._ink(g, smooth([(sx, sy - 14), (sx + 8, sy + 4), (sx, sy + 11), (sx - 8, sy + 4)], True), (150, 215, 250), 3)
        self.anchors['head'] = g.pt(0, 0)
        self.anchors['top'] = g.pt(0, -112)
        g.pop()
        self.anchors['belly'] = g.pt(0, -150 - U)
        g.pop()
        if sit:
            self._sole(g, -112, -62, -1); self._sole(g, 112, -62, 1)
        self.end(g)


# =====================================================================  GAJJU
class Gajju(Character):
    HEIGHT = 250
    shadow = 80
    INK = (44, 70, 112)
    STREAK = (226, 240, 252)
    SKIN = (150, 198, 236)
    SKIN_D = (124, 174, 220)
    PINK = (255, 170, 186)
    CAP = (255, 201, 60)
    NAIL = (255, 244, 222)
    POSE = dict(Character.POSE, ear=0.0, trunk=(46.0, 58.0), trunk_bend=0.0, trunk_curl=0.5, cap_dy=0.0,
                bendL=0.2, bendR=0.2)

    def _arm(self, g, p, side, key):
        face = p['face']
        sh = (side * 58 * (1 - 0.5 * abs(face)), -108)
        rest = (side * 22, 44)
        off = p[key]
        hand = (sh[0] + rest[0] + off[0], sh[1] + rest[1] + off[1])
        c = limb(sh, hand, -p['bendL' if side < 0 else 'bendR'] * side, 8)
        self._ink(g, tube(c, 19, 12, True), self.SKIN)
        ang = math.atan2(c[-1][1] - c[-3][1], c[-1][0] - c[-3][0])
        dx, dy = math.cos(ang), math.sin(ang)
        for k in (-1, 0, 1):                                                                               # three stubby fingers
            a1 = ang + k * 0.5 * side
            fb = (hand[0] + math.cos(a1) * 11, hand[1] + math.sin(a1) * 11)
            ft = (hand[0] + math.cos(a1) * 27, hand[1] + math.sin(a1) * 27)
            self._ink(g, tube([fb, ft], 8.5, 7.5), self.SKIN, 4)
        ta = ang - 1.2 * side
        self._ink(g, tube([(hand[0] + math.cos(ta) * 9, hand[1] + math.sin(ta) * 9), (hand[0] + math.cos(ta + 0.4 * side) * 23, hand[1] + math.sin(ta + 0.4 * side) * 23)], 8, 7), self.SKIN, 4)
        self._ink(g, oval(hand[0], hand[1], 17, 16, math.degrees(ang)), self.SKIN, 4)                         # palm
        self.anchors['handL' if side < 0 else 'handR'] = g.pt(*hand)

    def _ear(self, g, p, s):
        flap = p['ear']
        g.push(s * 54 - p['yaw'] * 30, -4, -s * flap * 38, max(0.35, 1 - 0.55 * abs(flap) * (flap < 0)) * (1 - 0.25 * s * p['yaw']), 1)
        self._ink(g, oval(s * 52, -6, 64, 70), self.SKIN)
        self._ink(g, oval(s * 46, -4, 43, 49), self.PINK, 0, False)
        g.pop()

    def draw(self, g, p, f):
        self.begin(g, p)
        face = p['face']
        bob = -abs(math.sin(2 * math.pi * p['step'])) * p['stride'] * 0.12
        # tail
        tdir = -1 if face >= 0 else 1
        if abs(face) > 0.2:
            tl = bez((tdir * 52, -64), (tdir * 84, -70), (tdir * 92, -40), (tdir * 104, -30), 8)
            self._ink(g, tube(tl, 5, 4), self.SKIN_D)
            self._ink(g, oval(tdir * 106, -26, 8, 10), self.INK)
        self._legs(g, p, [(-30, -52), (30, -52)], -15, 31, 17, 23, self.SKIN, toes=self.NAIL)
        g.push(0, bob)
        far, near = ('armR', 'armL') if face > 0.35 else ('armL', 'armR') if face < -0.35 else (None, None)
        if far:
            self._arm(g, p, 1 if far == 'armR' else -1, far)
        self._ink(g, oval(0, -80, 68, 64), self.SKIN)
        if not far:
            self._arm(g, p, -1, 'armL'); self._arm(g, p, 1, 'armR')
        # ---- head
        g.push(p['head_dx'] + face * 10, -164 + p['head_dy'], p['head_rot'], p['head_sx'], p['head_sy'], 0, 60)
        a = p['yaw'] * 0.62
        R = 78
        self._ear(g, p, -1); self._ear(g, p, 1)
        ch = p['cheeks']
        head = smooth([(0, -68), (54, -56), (80, -6), (70 + ch * 16, 36), (36, 62), (0, 66), (-36, 62), (-70 - ch * 16, 36), (-80, -6), (-54, -56)], True, 0.5)
        self._ink(g, head, self.SKIN)
        py = p['pitch'] * 10
        # cap
        g.push(-p['yaw'] * 6, p['cap_dy'])
        cap = smooth([(-52, -52), (-44, -84), (0, -102), (44, -84), (52, -52), (0, -60)], True, 0.5)
        brim = oval(p['yaw'] * 46 + (0 if abs(p['yaw']) > 0.2 else 0), -54, 34 + 22 * abs(p['yaw']), 9)
        self._ink(g, brim, self.CAP)
        self._ink(g, cap, self.CAP)
        self._ink(g, oval(0, -104, 9, 8), self.CAP)
        g.pop()
        eyes = []
        for s in (-1, 1):
            x, ws = self._yaw(s * 29, R, a)
            eyes.append((x, -8 + py, ws, s))
            cx, cw = self._yaw(s * 54, R, a)
            self._ink(g, oval(cx, 24 + py, 14 * cw * (1 + ch * 0.3), 9), self.PINK, 0, False, a=0.9)
        tx0, tw = self._yaw(0, R * 0.92, a)
        # mouth sits under the trunk root
        self._mouth(g, tx0 - (p['trunk'][0] > 0) * 10 + (p['trunk'][0] < 0) * 10, 40 + py, max(tw, 0.7), p, w0=17)
        self.anchors['mouth'] = g.pt(tx0, 46 + py)
        for x, y, ws, s in eyes:
            self._eye(g, x, y, 18, ws, p, self.SKIN, pupil_col=(70, 46, 40), side=s)
            if p['eye_open'] > 0.1:   # lashes on the outer side
                for k in (0, 1, 2):
                    la = math.radians(-150 + k * 22) if s < 0 else math.radians(-30 - k * 22)
                    r = 18 * p['eye_pop']
                    self._ink(g, poly([(x + math.cos(la) * r * ws, y + math.sin(la) * r * min(p['eye_open'], 1.3)),
                                       (x + math.cos(la) * (r + 9) * ws, y + math.sin(la) * (r + 9))], False), None, 3.5)
            lift = p['brow'] + (p['brow_asym'] * 12 if s > 0 else -p['brow_asym'] * 5)
            t = math.radians(p['brow_ang']) * s
            d = (math.cos(t) * 15 * ws, -math.sin(t) * 15)
            self._ink(g, poly([(x - d[0], -36 + py - lift - d[1]), (x + d[0], -36 + py - lift + d[1])], False), None, 6)
        # trunk
        tx, ty = p['trunk']
        root = (tx0, 14 + py)
        tip = (root[0] + tx, root[1] + ty)
        L = math.hypot(tx, ty) or 1
        nx, ny = -ty / L, tx / L
        b = p['trunk_bend']
        c1 = (root[0] + tx * 0.15 + nx * b * L, root[1] + ty * 0.55 + ny * b * L + 14)
        cu = p['trunk_curl']
        c2 = (tip[0] - tx * 0.25 + nx * cu * 26 * (1 if tx >= 0 else -1), tip[1] + cu * 30)
        cl = bez(root, c1, c2, tip, 22)
        R0, R1 = 25, 12
        self._ink(g, tube(cl, R0, R1, True, tip=False), self.SKIN)
        for i in range(3, 21, 2):   # rings all the way down, like a real trunk
            q, q2 = cl[i], cl[i + 1]
            d = math.hypot(q2[0] - q[0], q2[1] - q[1]) or 1
            n = (-(q2[1] - q[1]) / d, (q2[0] - q[0]) / d)
            r = R0 + (R1 - R0) * i / 22
            mid = (q[0] + (q2[0] - q[0]) * 0.35, q[1] + (q2[1] - q[1]) * 0.35)
            self._ink(g, smooth([(q[0] + n[0] * r * 0.92, q[1] + n[1] * r * 0.92), mid, (q[0] - n[0] * r * 0.92, q[1] - n[1] * r * 0.92)], False, 0.9), None, 2.5, a=0.42)
        # flared tip with the opening, two nostrils and the little gripping finger
        q, q2 = cl[-2], cl[-1]
        d = math.hypot(q2[0] - q[0], q2[1] - q[1]) or 1
        tdx, tdy = (q2[0] - q[0]) / d, (q2[1] - q[1]) / d
        ta = math.degrees(math.atan2(tdy, tdx))
        self._ink(g, oval(tip[0] + tdx * 1, tip[1] + tdy * 1, 8, R1 * 1.22, ta), self.SKIN)
        self._ink(g, oval(tip[0] + tdx * 3, tip[1] + tdy * 3, 4.5, R1 * 0.8, ta), self.PINK, 2.5)
        for k in (-1, 1):
            self._ink(g, oval(tip[0] + tdx * 3 - tdy * k * 4.5, tip[1] + tdy * 3 + tdx * k * 4.5, 1.6, 2.4, ta), self.INK, 0, False)
        up = -1 if tx >= 0 else 1
        fb = (tip[0] - tdy * up * R1 * 0.9, tip[1] + tdx * up * R1 * 0.9)
        self._ink(g, tube([fb, (fb[0] + tdx * 9, fb[1] + tdy * 9)], 5, 3.5), self.SKIN, 3)
        self.anchors['trunk'] = g.pt(*tip)
        self.anchors['head'] = g.pt(0, 0)
        self.anchors['top'] = g.pt(0, -100)
        g.pop()
        if far:
            self._arm(g, p, 1 if near == 'armR' else -1, near)
        self.anchors['belly'] = g.pt(0, -80)
        g.pop()
        self.end(g)
