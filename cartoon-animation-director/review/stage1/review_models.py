"""REVIEW ONLY. Proposal drawings for Stage 1 of the character reference review (2026-11-11).

Nothing in this file is a production asset. It imports the production classes from
toon-slapstick/engine and subclasses them; it does not modify them. The production models,
presets and model_baseline.json are untouched. If a proposal is approved, it would be
implemented in the production code as a separate, explicitly approved step.
"""
import math
import os
import sys
import skia
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', '..', '..', 'toon-slapstick', 'engine'))
from toon import Actor, oval, poly, smooth, tube, limb, bez, arc_pts, GROUND          # noqa: E402
from chars import Gaju                                                               # noqa: E402
from cast import Laddu, _U, _I, _limb_path                                           # noqa: E402


def lerp(a, b, t):
    return a + (b - a) * t


def lerp_pts(A, B, t):
    return [(lerp(a[0], b[0], t), lerp(a[1], b[1], t)) for a, b in zip(A, B)]


def two_seg(a, el, b, n=9):
    """Centre line shoulder -> elbow -> paw sampled at n points (a real joint, slightly rounded)."""
    out = []
    for i in range(n):
        t = i / (n - 1) * 2
        if t <= 1:
            out.append((lerp(a[0], el[0], t), lerp(a[1], el[1], t)))
        else:
            out.append((lerp(el[0], b[0], t - 1), lerp(el[1], b[1], t - 1)))
    return out


class Doodle(Actor):
    """A prop or diagram drawn by a plain function fn(g, pose, f). Review sheets only."""
    POSE = {}

    def __init__(self, fn, **over):
        super().__init__(**over)
        self.fn = fn
        self.twos = False; self.smear = False

    def draw(self, g, p, f):
        g.push(p['x'], p['y'], p['rot'], p['sx'], p['sy'])
        self.fn(g, p, f)
        g.pop()


# =====================================================================  LADDU, profile (proposal)
class LadduProfile(Laddu):
    """Laddu seen from the side with a true profile head. Faces screen-right; face < 0 mirrors.
    crouch 0..1 lowers the chest and folds the forelegs (rump stays high); reach 0..1 pushes the
    head forward and down. Colours, line weights, paw and eye drawing come from the production class."""
    POSE = dict(Laddu.POSE, crouch=0.0, reach=0.0)

    BODY_S = [(-100, -104), (-82, -142), (-30, -160), (30, -160), (70, -150), (94, -122), (90, -88), (60, -54), (0, -38), (-60, -50), (-98, -76)]
    BODY_C = [(-102, -110), (-86, -150), (-36, -162), (22, -142), (62, -116), (88, -88), (86, -56), (58, -30), (0, -26), (-60, -44), (-100, -80)]

    def _phead(self, g, p):
        eb = p['ear_back']
        # far ear, then near ear (both sit behind the skull outline at their base)
        for far in (True, False):
            ox = 34 if far else 0
            tip = (-8 + ox - eb * 46, -114 + eb * 46 + (6 if far else 0))
            pts = [(26 + ox, -50), (12 + ox - eb * 8, -86 + eb * 18), tip, (-28 + ox - eb * 16, -80 + eb * 26), (-38 + ox, -44), (-6 + ox, -38)]
            self._ink(g, smooth(pts, True, 0.4), self.FAR if far else self.FUR)
            cx_, cy_ = sum(q[0] for q in pts[:5]) / 5, sum(q[1] for q in pts[:5]) / 5 + 4
            self._ink(g, smooth([(cx_ + (x - cx_) * 0.55, cy_ + (y - cy_) * 0.6) for x, y in pts[:5]], True, 0.4), self.PINK, 0, False)
        for k in (-1, 0):                                             # far-side whiskers
            self._ink(g, smooth([(98, 32 + k * 4), (128, 18 + k * 12), (150, 12 + k * 20)], False), None, 2.2, col=(255, 250, 240))
        head = smooth([(-8, -62), (28, -60), (56, -44), (72, -20), (80, 2), (98, 12), (110, 24), (106, 38), (96, 48), (88, 60), (60, 68), (24, 70),
                       (-14, 64), (-40, 54), (-64, 60), (-54, 40), (-78, 34), (-62, 14), (-72, -12), (-62, -38), (-38, -56)], True, 0.45)
        self._ink(g, head, self.FUR)
        for k in (0, 1):                                              # cheek stripes
            st_ = _I(head, oval(-60, -2 + k * 22, 24, 5, -12))
            if st_ is not None:
                self._ink(g, st_, self.STRIPE, 0, False)
        for x0, y0 in ((4, -60), (22, -57), (40, -49)):               # tabby mark on the forehead, seen from the side
            self._ink(g, smooth([(x0, y0), (x0 + 3, y0 + 10), (x0 + 5, y0 + 20)], False), None, 6.5, col=self.STRIPE)
        for q in (oval(84, 37, 23, 15), oval(76, 54, 17, 10)):        # whisker pad and chin
            c = _I(head, q)
            if c is not None:
                self._ink(g, c, self.CREAM, 0, False)
        self._ink(g, head, None)
        mo = p['mouth_open']; sm = p['smile'] * 5
        if p['tongue'] > 0.02:
            tl_ = 46 * p['tongue']
            self._ink(g, tube([(96, 42), (104, 42 + tl_ * 0.55), (106 + 4 * p['tongue'], 42 + tl_)], 8.5, 7), (244, 120, 140), 3)
        if mo < 0.06:
            self._ink(g, poly([(104, 29), (101, 37)], False), None, 3)
            self._ink(g, smooth([(101, 37), (90, 45), (74, 40 - sm)], False, 0.8), None, 3.4)
        else:
            m = smooth([(103, 35), (86, 40), (66, 36 - sm * 0.6), (70, 44 + mo * 20), (86, 46 + mo * 30), (100, 40 + mo * 20)], True, 0.6)
            self._ink(g, m, (96, 28, 44), 4)
            t_ = _I(oval(84, 46 + mo * 28, 14, 4 + mo * 12), m)
            if t_ is not None:
                self._ink(g, t_, (240, 120, 130), 0, False)
            self._ink(g, m, None, 4)
        self._ink(g, smooth([(100, 14), (112, 20), (103, 29)], True, 0.7), self.PINK, 3)   # nose at the tip of the muzzle
        for k in (-1, 0, 1):                                          # near whiskers and their dots
            self._ink(g, oval(86 + abs(k) * 2, 37 + k * 6, 1.6, 1.6), self.HL, 0, False)
            self._ink(g, smooth([(94, 37 + k * 5), (128, 34 + k * 14), (158, 40 + k * 24)], False), None, 2.2, col=(255, 250, 240))
        ex, ey = 46, -2
        self._cat_eye(g, ex, ey, 18, 0.74, p, -1)
        self._brows(g, [(ex, ey, 0.74, -1)], p, 27, 12, 4.5, self.STRIPE)
        self.anchors['mouth'] = g.pt(100, 42); self.anchors['head'] = g.pt(0, 0); self.anchors['top'] = g.pt(0, -70)

    def draw(self, g, p, f):
        self.begin(g, p)
        d = -1 if p['face'] < 0 else 1
        g.push(0, 0, 0, self.S * d, self.S)
        c = max(0.0, min(1.0, p['crouch'])); r = p['reach']
        sw = p['tail'] + math.sin(f * 0.14) * 0.25
        hx, hy = 110 + 40 * c + 22 * r, -178 + 40 * c + 30 * r
        hrot = 26 * c + 14 * r + p['head_rot']

        def fore(near):
            o = 0 if near else 16
            sh = (lerp(52, 58, c) + o, lerp(-96, -66, c))
            el = (lerp(55, 30, c) + o, lerp(-54, -30, c))
            paw = (lerp(58, 98, c) + o + p['armR' if near else 'armL'][0], -11 + p['armR' if near else 'armL'][1])
            cl = two_seg(sh, el, paw)
            self._ink(g, _limb_path(cl, [18, 17.5, 16.5, 15.5, 15, 15, 15.5, 16.5, 17], tip=0.2), self.FUR if near else self.FAR)
            self._paw(g, paw[0] + 5, paw[1] + 2, 19, 11, self.CREAM, d=1)
            return paw

        def hind(near):
            o = 0 if near else 14
            leg = _U(oval(-56 + o, -86, 38, 42, 14), tube([(-64 + o, -58), (-86 + o, -34), (-70 + o, -12)], 15, 11.5))
            self._ink(g, leg, self.FUR if near else self.FAR)
            self._paw(g, -58 + o, -9, 21, 11, self.CREAM, d=1)

        hind(False); fore(False)
        self._tail(g, bez((-90, -116), (lerp(-152, -150, c), lerp(-126, -150, c)), (lerp(-162, -150, c) - sw * 16, lerp(-196, -232, c)),
                          (lerp(-120, -96, c) - sw * 30, lerp(-238, -252, c)), 12))
        body = smooth(lerp_pts(self.BODY_S, self.BODY_C, c), True, 0.5)
        neck = tube([(lerp(64, 70, c), lerp(-124, -92, c)), ((lerp(64, 70, c) + hx - 24) / 2, (lerp(-124, -92, c) + hy + 14) / 2 - 4), (hx - 24, hy + 14)], 40, 34, True)
        torso = _U(body, neck)                                        # one outline: the neck can never separate from the body
        self._ink(g, torso, self.FUR, 0, False)
        belly = _I(body, oval(4, lerp(-38, -28, c), 76, 22))
        if belly is not None:
            self._ink(g, belly, self.CREAM, 0, False)
        for x, y in ((-44, lerp(-150, -152, c)), (-10, lerp(-150, -148, c)), (24, lerp(-150, -134, c))):
            st_ = _I(body, oval(x, y, 7, 34, -8 - 14 * c * (x > 0)))
            if st_ is not None:
                self._ink(g, st_, self.STRIPE, 0, False)
        self._ink(g, torso, None)
        if c > 0.3:                                                   # shoulder blade showing through the fur when he crouches
            self._ink(g, smooth([(26, lerp(-150, -138, c)), (44, lerp(-150, -132, c) - 6 * c), (58, lerp(-140, -114, c))], False), None, 3, a=0.75)
        hind(True)
        paw = fore(True)
        self.anchors['handR'] = g.pt(*paw); self.anchors['handL'] = g.pt(paw[0] + 16, paw[1])
        g.push(hx + p['head_dx'], hy + p['head_dy'], hrot, p['head_sx'], p['head_sy'], -20, 40)
        self._phead(g, p)
        g.pop()
        self.anchors['belly'] = g.pt(0, -100)
        g.pop()
        self.end(g)


# =====================================================================  GAJU, review variants (proposal)
def trunk_draw(self, g, cl, gulp=-1.0, up=-1):
    """The production trunk drawing (taper, wrinkles, flared tip, two nostrils, one finger), on any centre line."""
    R0, R1 = 31, 12
    n = len(cl) - 1
    gi = None
    if 0.0 <= gulp <= 1.0:
        gi = cl[min(n - 1, max(1, int(round((1 - gulp) * (n - 1)))))]
        gr = (R1 + (R0 - R1) * gulp) * 1.55
        self._ink(g, oval(gi[0], gi[1], gr, gr), self.SKIN)
    self._ink(g, tube(cl, R0, R1, True, tip=False), self.SKIN)
    if gi is not None:
        self._ink(g, oval(gi[0], gi[1], gr - 3, gr - 3), self.SKIN, 0, False)
    for i in range(4, n - 1, 2):
        q, q2 = cl[i], cl[i + 1]
        d = math.hypot(q2[0] - q[0], q2[1] - q[1]) or 1
        nn = (-(q2[1] - q[1]) / d, (q2[0] - q[0]) / d)
        r = R0 + (R1 - R0) * i / n
        mid = (q[0] + (q2[0] - q[0]) * 0.4, q[1] + (q2[1] - q[1]) * 0.4)
        self._ink(g, smooth([(q[0] + nn[0] * r * 0.6, q[1] + nn[1] * r * 0.6), mid, (q[0] - nn[0] * r * 0.6, q[1] - nn[1] * r * 0.6)], False, 0.9), None, 2.2, a=0.5)
    q, q2 = cl[-2], cl[-1]
    d = math.hypot(q2[0] - q[0], q2[1] - q[1]) or 1
    tdx, tdy = (q2[0] - q[0]) / d, (q2[1] - q[1]) / d
    ta = math.degrees(math.atan2(tdy, tdx))
    tip = cl[-1]
    self._ink(g, oval(tip[0] + tdx, tip[1] + tdy, 8, R1 * 1.22, ta), self.SKIN)
    self._ink(g, oval(tip[0] + tdx * 3, tip[1] + tdy * 3, 4.5, R1 * 0.8, ta), self.PINK, 2.5)
    for k in (-1, 1):
        self._ink(g, oval(tip[0] + tdx * 3 - tdy * k * 4.5, tip[1] + tdy * 3 + tdx * k * 4.5, 1.6, 2.4, ta), self.INK, 0, False)
    fb = (tip[0] - tdy * up * R1 * 0.9, tip[1] + tdx * up * R1 * 0.9)
    self._ink(g, tube([fb, (fb[0] + tdx * 9, fb[1] + tdy * 9)], 5, 3.5), self.SKIN, 3)
    return tip


class GajuReview(Gaju):
    """Production Gaju, unchanged, plus one review-only control: ear_size scales both ears
    (for the parachute and sail concepts). With ear_size 1 it draws exactly the production model."""
    POSE = dict(Gaju.POSE, ear_size=1.0)

    def _ear(self, g, p, s):
        k = p.get('ear_size', 1.0)
        if abs(k - 1.0) < 1e-3:
            return Gaju._ear(self, g, p, s)
        flap = p['ear']
        g.push(s * 54 - p['yaw'] * 30, -4, -s * flap * 38, max(0.35, 1 - 0.55 * abs(flap) * (flap < 0)) * (1 - 0.25 * s * p['yaw']) * k, k)
        self._ink(g, oval(s * 52, -6, 64, 70), self.SKIN)
        self._ink(g, oval(s * 46, -4, 43, 49), self.PINK, 0, False)
        g.pop()


class GajuProfile(Gaju):
    """Gaju seen from the side, standing upright on his hind legs as the approved model does.
    Faces screen-right; face < 0 mirrors. upright 0 gives an alternative on all fours.
    trunk_cl: three points (c1, c2, tip) relative to the trunk root, or None for the rest shape.
    ear (production control): lifts the near ear. ear_ang: swings the near ear forward (degrees).
    ear_open 0..1: how much of the pink inside of the near ear shows. hide 0..1 squeezes him thin."""
    POSE = dict(Gaju.POSE, ear_ang=0.0, ear_open=0.0, upright=1.0, trunk_up=-1.0)
    REST = ((56, 14), (34, 92), (62, 86))
    trunk_cl = None

    def _leg(self, g, hx, col):
        fx, fo = hx, 8
        leg = smooth([(hx - 27, -74), (hx + 27, -74), (hx + 27, -40), (fx + 27, -22), (fx + 31 + fo, -8), (fx + 27 + fo, 0), (fx - 27 + fo, 0),
                      (fx - 31 + fo, -8), (fx - 27, -22), (hx - 27, -40)], True, 0.5)
        self._ink(g, leg, col)
        self._nails(g, fx + fo + 10, 1, math.pi / 2, 24)
        self._ink(g, poly(arc_pts(fx, -34, 17, 4, 20, 160, 6), False), None, 2.5, a=0.6)

    def _parm(self, g, sh, hand, col):
        """Front leg hanging from the shoulder, as in the approved front view: a soft column ending in a nailed foot."""
        c = limb(sh, hand, 0.1, 12)
        ang = math.atan2(c[-1][1] - c[-3][1], c[-1][0] - c[-3][0])
        dx, dy = math.cos(ang), math.sin(ang)
        prof = [16, 18, 19, 20, 21, 21, 21, 21, 22, 22, 23, 24, 24]
        L, R = [], []
        for i, q in enumerate(c):
            a0, a1 = c[max(i - 1, 0)], c[min(i + 1, 12)]
            dd = math.hypot(a1[0] - a0[0], a1[1] - a0[1]) or 1
            n = (-(a1[1] - a0[1]) / dd, (a1[0] - a0[0]) / dd)
            L.append((q[0] + n[0] * prof[i], q[1] + n[1] * prof[i])); R.append((q[0] - n[0] * prof[i], q[1] - n[1] * prof[i]))
        end = (hand[0] + dx * 13, hand[1] + dy * 13)
        shape = smooth(L + [(L[-1][0] + dx * 11, L[-1][1] + dy * 11), end, (R[-1][0] + dx * 11, R[-1][1] + dy * 11)] + R[::-1] + [(sh[0] - (c[1][0] - sh[0]), sh[1] - (c[1][1] - sh[1]))], True, 0.5)
        self._ink(g, shape, col)
        self._nails(g, end[0], end[1], ang, 24)
        q = c[7]
        self._ink(g, poly(arc_pts(q[0], q[1], 15, 4, math.degrees(ang) + 60, math.degrees(ang) + 120, 4), False), None, 2.5, a=0.6)
        return hand

    def draw(self, g, p, f):
        self.begin(g, p)
        d = -1 if p['face'] < 0 else 1
        g.push(0, 0, 0, d, 1)
        up = p['upright'] > 0.5
        if up:                                                        # the approved posture: upright, front legs hanging like arms
            tl = bez((-54, -64), (-80, -70), (-88, -40), (-100, -30), 8)
            self._ink(g, tube(tl, 5, 4), self.SKIN_D)
            self._ink(g, oval(-102, -26, 8, 10), self.INK)
            self._leg(g, 16, self.SKIN_D); self._leg(g, -10, self.SKIN)
            self._parm(g, (26, -112), (44 + p['armL'][0], -50 + p['armL'][1]), self.SKIN_D)
            body = smooth([(0, -146), (40, -138), (60, -98), (62, -62), (42, -28), (0, -20), (-42, -28), (-62, -62), (-60, -98), (-40, -138)], True, 0.5)
            self._ink(g, body, self.SKIN)
            hand = self._parm(g, (-8, -112), (6 + p['armR'][0], -46 + p['armR'][1]), self.SKIN)
            self.anchors['handR'] = g.pt(*hand)
            hx0, hy0 = 16, -164
        else:                                                         # alternative: on all fours
            tl = bez((-78, -84), (-104, -92), (-112, -60), (-122, -44), 8)
            self._ink(g, tube(tl, 5, 4), self.SKIN_D)
            self._ink(g, oval(-124, -40, 8, 10), self.INK)
            self._leg(g, -16, self.SKIN_D); self._leg(g, 68, self.SKIN_D)
            self._leg(g, -48, self.SKIN); self._leg(g, 36, self.SKIN)
            body = smooth([(-70, -128), (-24, -148), (36, -142), (70, -106), (70, -62), (42, -28), (-20, -20), (-66, -36), (-86, -80)], True, 0.5)
            self._ink(g, body, self.SKIN)
            hx0, hy0 = 48, -166
        # ---- head
        g.push(hx0 + p['head_dx'], hy0 + p['head_dy'], p['head_rot'], p['head_sx'], p['head_sy'], -20, 50)
        py = p['pitch'] * 10
        g.push(-34, -26, -p['ear'] * 30)                              # far ear: its pink inside faces us
        self._ink(g, oval(-26, 4, 54, 62), self.SKIN_D)
        self._ink(g, oval(-24, 6, 37, 44), self.PINK, 0, False)
        g.pop()
        head = smooth([(0, -68), (44, -60), (72, -26), (78, 6), (64, 40), (34, 60), (-6, 66), (-46, 52), (-70, 14), (-68, -28), (-44, -58)], True, 0.5)
        self._ink(g, head, self.SKIN)
        g.push(0, p['cap_dy'])                                        # cap: brim to the front
        self._ink(g, oval(52, -54, 50, 9), self.CAP)
        self._ink(g, smooth([(-56, -52), (-48, -84), (-4, -102), (40, -84), (48, -52), (-4, -60)], True, 0.5), self.CAP)
        self._ink(g, oval(-4, -104, 9, 8), self.CAP)
        g.pop()
        self._ink(g, oval(28, 26 + py, 12, 9), self.PINK, 0, False, a=0.9)
        # mouth: visible in profile, under the trunk root
        mo = p['mouth_open']; sm = p['smile']
        if mo < 0.06:
            self._ink(g, smooth([(60, 38 + py), (46, 46 + py + sm * 3), (30, 40 + py - sm * 7)], False, 0.9), None, 5)
        else:
            m = smooth([(62, 36 + py), (44, 40 + py), (28, 36 + py - sm * 6), (32, 46 + py + mo * 22), (48, 48 + py + mo * 30), (60, 42 + py + mo * 18)], True, 0.7)
            self._ink(g, m, (96, 28, 44), 5)
            t_ = _I(oval(46, 48 + py + mo * 28, 12, 4 + mo * 12), m)
            if t_ is not None:
                self._ink(g, t_, (240, 120, 130), 0, False)
            self._ink(g, m, None, 5)
        x, y, ws = 36, -8 + py, 0.8
        self._eye(g, x, y, 18, ws, p, self.SKIN, pupil_col=(70, 46, 40), side=-1)
        if p['eye_open'] > 0.1:
            for k in (0, 1, 2):
                la = math.radians(-150 + k * 22)
                r = 18 * p['eye_pop']
                self._ink(g, poly([(x + math.cos(la) * r * ws, y + math.sin(la) * r * min(p['eye_open'], 1.3)),
                                   (x + math.cos(la) * (r + 9) * ws, y + math.sin(la) * (r + 9))], False), None, 3.5)
        lift = p['brow'] - p['brow_asym'] * 5
        t = -math.radians(p['brow_ang'])
        dd = (math.cos(t) * 15 * ws, -math.sin(t) * 15)
        self._ink(g, poly([(x - dd[0], -36 + py - lift - dd[1]), (x + dd[0], -36 + py - lift + dd[1])], False), None, 6)
        # trunk
        root = (62, 16 + py)
        c1, c2, tip = self.trunk_cl or self.REST
        cl = bez(root, (root[0] + c1[0], root[1] + c1[1]), (root[0] + c2[0], root[1] + c2[1]), (root[0] + tip[0], root[1] + tip[1]), 22)
        tp = trunk_draw(self, g, cl, p['gulp'], up=p['trunk_up'])
        self._ink(g, oval(root[0] - 12, root[1] + 2, 22, 24), self.SKIN, 0, False)    # the trunk grows out of the face: no seam
        self.anchors['trunk'] = g.pt(*tp); self.anchors['mouth'] = g.pt(46, 44 + py)
        self.anchors['head'] = g.pt(0, 0); self.anchors['top'] = g.pt(0, -100)
        # near ear: a big flap hinged at the upper back of the head
        g.push(-30, -36, -p['ear'] * 34 - p['ear_ang'])
        ear = oval(-36, 46, 50, 62, 10)
        self._ink(g, ear, self.SKIN)
        eo = p['ear_open']
        if eo > 0.03:
            self._ink(g, oval(-36 + (1 - eo) * 14, 48, 34 * eo, 43, 10), self.PINK, 0, False)
        else:
            self._ink(g, smooth([(-10, 8), (-20, 46), (-16, 86)], False), None, 2.5, a=0.5)           # the fold where it meets the head
        g.pop()
        g.pop()
        self.anchors['belly'] = g.pt(0, -80)
        g.pop()
        self.end(g)
