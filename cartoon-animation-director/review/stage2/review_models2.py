"""REVIEW ONLY. Proposal drawings for Stage 2 of the character reference review (2026-11-11).

Nothing here is a production asset. The production classes in toon-slapstick/engine are imported
and subclassed, never modified. Presets and model_baseline.json are untouched.
"""
import math
import os
import sys
import skia
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', 'stage1'))
sys.path.insert(0, os.path.join(HERE, '..', '..', '..', 'toon-slapstick', 'engine'))
from toon import oval, poly, smooth, tube, bez, arc_pts                              # noqa: E402
from chars import Gaju                                                               # noqa: E402
from cast import Laddu, _U, _I, _limb_path, _two_bone                                # noqa: E402
from review_models import GajuProfile, Doodle, lerp                                  # noqa: E402,F401


def _D(a, b):
    return skia.Op(a, b, skia.kDifference_PathOp)


# =====================================================================  LADDU: revised profile head
def profile_head(self, g, p):
    """Revised proposal. A component drawn at the head anchor, exactly like the approved head:
    it is never merged with the body. Both ears use the approved main fur colour."""
    eb = p['ear_back']
    for far in (True, False):                                         # far ear first, then near ear
        ox = 40 if far else 0
        tip = (-12 + ox - eb * 46, -116 + eb * 46 + (4 if far else 0))
        pts = [(24 + ox, -46), (10 + ox - eb * 8, -86 + eb * 18), tip, (-32 + ox - eb * 16, -80 + eb * 26), (-40 + ox, -42), (-6 + ox, -34)]
        self._ink(g, smooth(pts, True, 0.4), self.FUR)
        cx_, cy_ = sum(q[0] for q in pts[:5]) / 5, sum(q[1] for q in pts[:5]) / 5 + 4
        self._ink(g, smooth([(cx_ + (x - cx_) * 0.55, cy_ + (y - cy_) * 0.6) for x, y in pts[:5]], True, 0.4), self.PINK, 0, False)
    for k in (-1, 0):                                                 # far-side whiskers
        self._ink(g, smooth([(90, 32 + k * 4), (120, 18 + k * 12), (142, 12 + k * 20)], False), None, 2.2, col=(255, 250, 240))
    # skull: top line and height taken from the approved head (-62 .. 70); muzzle shortened; cheek fur in two points
    head = smooth([(-14, -62), (26, -61), (56, -48), (74, -24), (80, 0), (92, 10), (102, 22), (100, 36), (92, 46), (84, 58), (58, 68), (22, 70),
                   (-16, 66), (-44, 56), (-70, 62), (-60, 42), (-88, 32), (-72, 12), (-84, -14), (-74, -40), (-48, -57)], True, 0.45)
    self._ink(g, head, self.FUR)
    for k in (0, 1):
        st_ = _I(head, oval(-70, -4 + k * 22, 24, 5, -12))
        if st_ is not None:
            self._ink(g, st_, self.STRIPE, 0, False)
    for x0, y0 in ((0, -61), (18, -59), (36, -53)):
        self._ink(g, smooth([(x0, y0), (x0 + 3, y0 + 11), (x0 + 5, y0 + 22)], False), None, 6.5, col=self.STRIPE)
    for q in (oval(78, 37, 23, 15), oval(70, 54, 17, 10)):
        c = _I(head, q)
        if c is not None:
            self._ink(g, c, self.CREAM, 0, False)
    self._ink(g, head, None)
    mo = p['mouth_open']; sm = p['smile'] * 5
    if p['tongue'] > 0.02:
        tl_ = 46 * p['tongue']
        self._ink(g, tube([(90, 42), (98, 42 + tl_ * 0.55), (100 + 4 * p['tongue'], 42 + tl_)], 8.5, 7), (244, 120, 140), 3)
    if mo < 0.06:
        self._ink(g, poly([(97, 28), (94, 37)], False), None, 3)
        self._ink(g, smooth([(94, 37), (83, 45), (68, 40 - sm)], False, 0.8), None, 3.4)
    else:
        m = smooth([(96, 35), (80, 40), (60, 36 - sm * 0.6), (64, 44 + mo * 20), (80, 46 + mo * 30), (93, 40 + mo * 20)], True, 0.6)
        self._ink(g, m, (96, 28, 44), 4)
        t_ = _I(oval(78, 46 + mo * 28, 14, 4 + mo * 12), m)
        if t_ is not None:
            self._ink(g, t_, (240, 120, 130), 0, False)
        self._ink(g, m, None, 4)
    self._ink(g, smooth([(93, 12), (105, 19), (96, 28)], True, 0.7), self.PINK, 3)
    for k in (-1, 0, 1):
        self._ink(g, oval(80 + abs(k) * 2, 37 + k * 6, 1.6, 1.6), self.HL, 0, False)
        self._ink(g, smooth([(88, 37 + k * 5), (122, 34 + k * 14), (152, 40 + k * 24)], False), None, 2.2, col=(255, 250, 240))
    ex, ey = 44, 0
    self._cat_eye(g, ex, ey, 18, 0.78, p, -1)
    self._brows(g, [(ex, ey, 0.78, -1)], p, 27, 12, 4.5, self.STRIPE)
    self.anchors['mouth'] = g.pt(94, 42); self.anchors['head'] = g.pt(0, 0); self.anchors['top'] = g.pt(0, -70)


class LadduSideProfile(Laddu):
    """The approved side body, completely unchanged, with the revised profile head placed at the
    approved head anchor as a separate component. Front view still draws the approved head."""

    def draw(self, g, p, f):
        self._prof = abs(p['face']) >= 0.5
        Laddu.draw(self, g, p, f)

    def _head(self, g, p):
        if getattr(self, '_prof', False):
            profile_head(self, g, p)
        else:
            Laddu._head(self, g, p)


# =====================================================================  LADDU: acting rig (proposal)
class LadduAct(Laddu):
    """Review-only acting rig, side view facing screen-right. Same cat: the approved head drawing
    (or the revised profile head with phead=1), the approved paws, tail stripes, colours and line.
    What is new is the body underneath: a spine that can curve, a chest and a hip that move
    independently, legs with real joints that reach for a paw position, shoulders that can rise,
    and a tail whose direction, curl and puff are separate controls.
    The head stays a separate component laid over the body, as in the approved model."""
    POSE = dict(Laddu.POSE,
                hip=(0.0, 0.0), chest=(0.0, 0.0), arch=0.0, shrug=0.0, belly=0.0,
                pawN=(0.0, 0.0), pawF=(0.0, 0.0), wristN=0.0, wristF=0.0,
                hindN=(0.0, 0.0), hindF=(0.0, 0.0),
                tail_a=12.0, tail_b=105.0, tail_tip=0.0, tail_puff=0.0, bristle=0.0,
                phead=0.0, breath=1.0, earflick=0.0)

    def _tail2(self, g, base, p, f, idle=True):
        a0 = math.radians(p['tail_a']); b = math.radians(p['tail_b']); tp = math.radians(p['tail_tip'])
        sway = math.sin(f * 0.14) * 0.3 if idle else 0.0
        n, seg = 12, 13.5
        pts = [base]; x, y = base
        for i in range(n):
            t = (i + 0.5) / n
            ang = a0 + b * t ** 1.3 + tp * max(0.0, t - 0.6) / 0.4 + sway * t
            x -= math.cos(ang) * seg; y -= math.sin(ang) * seg
            pts.append((x, y))
        pf = p['tail_puff']
        r0, r1 = 15 * (1 + 0.55 * pf), 9 * (1 + 1.5 * pf)
        self._ink(g, tube(pts, r0, r1, True), self.FUR)
        for i in (3, 5, 7, 9):
            q, q2 = pts[i], pts[i + 1]
            d = math.hypot(q2[0] - q[0], q2[1] - q[1]) or 1
            nn = (-(q2[1] - q[1]) / d, (q2[0] - q[0]) / d)
            r = (r0 + (r1 - r0) * i / n) - 2
            self._ink(g, poly([(q[0] + nn[0] * r, q[1] + nn[1] * r), (q[0] - nn[0] * r, q[1] - nn[1] * r)], False), None, 5.5, col=self.STRIPE)
        self._ink(g, tube(pts, r0, r1, True), None)
        if pf > 0.15:                                                 # fur standing on end
            for i in range(2, n, 1):
                q, q2 = pts[i], pts[i + 1]
                d = math.hypot(q2[0] - q[0], q2[1] - q[1]) or 1
                tx, ty = (q2[0] - q[0]) / d, (q2[1] - q[1]) / d
                r = r0 + (r1 - r0) * i / n
                for s in (-1, 1):
                    a_ = (q[0] - ty * s * r, q[1] + tx * s * r)
                    self._ink(g, poly([a_, (a_[0] - ty * s * 9 * pf + tx * 5, a_[1] + tx * s * 9 * pf + ty * 5)], False), None, 3)

    def _foreleg(self, g, sh, paw, wrist, near):
        c, el = _two_bone(sh, (paw[0], paw[1]), 46, 48, -1)
        self._ink(g, _limb_path(c, [19, 18.5, 18, 17.5, 17, 16.5, 16, 15.5, 15, 15, 15.5, 16.5, 17], tip=0.2), self.FUR if near else self.FAR)
        g.push(paw[0], paw[1], wrist)
        self._paw(g, 5, 2, 19, 11, self.CREAM, d=1)
        g.pop()

    def _hindleg(self, g, H, paw, near):
        o = 0 if near else 14
        hc = (H[0] + 2 + o, H[1] + 6)
        k = (hc[0] - 8, hc[1] + 28)
        pw = (paw[0] + o, paw[1])
        hock = ((k[0] + pw[0] - 12) / 2 - 16, (k[1] + pw[1] - 3) / 2)
        leg = _U(oval(hc[0], hc[1], 38, 42, 14), tube([k, hock, (pw[0] - 12, pw[1] - 3)], 15, 11.5))
        self._ink(g, leg, self.FUR if near else self.FAR)
        self._paw(g, pw[0], pw[1], 21, 11, self.CREAM, d=1)

    def draw(self, g, p, f):
        self.begin(g, p)
        d = -1 if p['face'] < 0 else 1
        g.push(0, 0, 0, self.S * d, self.S)
        H = (-58 + p['hip'][0], -92 + p['hip'][1])
        bs = p['breath'] * math.sin(f * 0.26)                          # breathing: the chest rises and widens a little, all the time
        C = (60 + p['chest'][0], -104 + p['chest'][1] - 1.8 * bs)
        mx, my = (H[0] + C[0]) / 2, (H[1] + C[1]) / 2
        L = math.hypot(C[0] - H[0], C[1] - H[1]) or 1
        ux, uy = (C[0] - H[0]) / L, (C[1] - H[1]) / L
        M = (mx + uy * p['arch'] * 2, my - ux * p['arch'] * 2)       # arch > 0 lifts the middle of the back
        spine = [((1 - t) ** 2 * H[0] + 2 * (1 - t) * t * M[0] + t * t * C[0], (1 - t) ** 2 * H[1] + 2 * (1 - t) * t * M[1] + t * t * C[1])
                 for t in [i / 8 for i in range(9)]]
        br = 1 + 0.03 * bs
        bl = p['belly']
        prof = [50, 55, 57 + 5 * bl, 58 + 7 * bl, 57 + 6 * bl, 55 * br, 52 * br, 49 * br, 46 * br]
        self._hindleg(g, H, (-58 + p['hindF'][0], -9 + p['hindF'][1]), False)
        self._foreleg(g, (C[0] + 12, C[1] + 6), (74 + p['pawF'][0], -11 + p['pawF'][1]), p['wristF'], False)
        self._tail2(g, (H[0] - 36, H[1] - 20), p, f)
        body = _limb_path(spine, prof, tip=0.72, root=0.8)
        if p['shrug'] > 0.02:                                         # shoulder blades rising above the line of the back
            body = _U(body, oval(C[0] - 8, C[1] - 44 - 14 * p['shrug'], 26, 20 * p['shrug'] + 6, math.degrees(math.atan2(uy, ux))))
        self._ink(g, body, self.FUR, 0, False)
        nrm = (uy, -ux)                                               # points to the back side of the spine (up when he stands)
        if nrm[1] > 0:
            nrm = (-nrm[0], -nrm[1])
        belly = _I(body, oval(mx - nrm[0] * 56, my - nrm[1] * 56 - p['arch'] * 0.6, 76, 22, math.degrees(math.atan2(uy, ux))))
        if belly is not None:
            self._ink(g, belly, self.CREAM, 0, False)
        for t in (0.2, 0.42, 0.64):                                   # back stripes ride on the spine, so they move with it
            q = spine[int(round(t * 8))]
            st_ = _I(body, oval(q[0] + nrm[0] * 46, q[1] + nrm[1] * 46, 7, 34, math.degrees(math.atan2(uy, ux)) - 8))
            if st_ is not None:
                self._ink(g, st_, self.STRIPE, 0, False)
        self._ink(g, body, None)
        if p['bristle'] > 0.1:                                        # fur standing along the spine
            for i in range(1, 8):
                q = spine[i]; r = prof[i] + 1
                a_ = (q[0] + nrm[0] * r, q[1] + nrm[1] * r)
                self._ink(g, poly([a_, (a_[0] + nrm[0] * 11 * p['bristle'] - ux * 5, a_[1] + nrm[1] * 11 * p['bristle'] - uy * 5)], False), None, 3)
        self._hindleg(g, H, (-58 + p['hindN'][0], -9 + p['hindN'][1]), True)
        paw = (58 + p['pawN'][0], -11 + p['pawN'][1])
        self._foreleg(g, (C[0] - 6, C[1] + 8), paw, p['wristN'], True)
        self.anchors['handR'] = g.pt(*paw); self.anchors['belly'] = g.pt(mx, my)
        # head: a separate component at an anchor that rides on the chest (approved offset when standing)
        hx, hy = C[0] + 48 + p['head_dx'], C[1] - 74 + p['head_dy']
        g.push(hx, hy, p['head_rot'], p['head_sx'], p['head_sy'], 0, 56)
        q = dict(p)
        if p['earflick'] > 0.02:
            q['ear_back'] = p['ear_back'] + 0.5 * p['earflick']
        if p['phead'] > 0.5:
            profile_head(self, g, q)
        else:
            Laddu._head(self, g, q)
        g.pop()
        g.pop()
        self.end(g)


# =====================================================================  GAJU: revised profile (proposal)
class GajuProfile2(GajuProfile):
    """Revised proposal: same size ears, both outer surfaces in the approved main skin colour,
    and a narrow rim of the pink inside showing along the front edge of the near ear at rest.
    Trunk root raised to the approved front-view height."""
    ROOT = (70, 8)

    def draw(self, g, p, f):
        self.begin(g, p)
        d = -1 if p['face'] < 0 else 1
        g.push(0, 0, 0, d, 1)
        tl = bez((-54, -64), (-80, -70), (-88, -40), (-100, -30), 8)
        self._ink(g, tube(tl, 5, 4), self.SKIN_D)
        self._ink(g, oval(-102, -26, 8, 10), self.INK)
        self._leg(g, 16, self.SKIN); self._leg(g, -10, self.SKIN)
        self._parm(g, (26, -112), (44 + p['armL'][0], -50 + p['armL'][1]), self.SKIN)
        body = smooth([(0, -146), (40, -138), (60, -98), (62, -62), (42, -28), (0, -20), (-42, -28), (-62, -62), (-60, -98), (-40, -138)], True, 0.5)
        self._ink(g, body, self.SKIN)
        hand = self._parm(g, (-8, -112), (6 + p['armR'][0], -46 + p['armR'][1]), self.SKIN)
        self.anchors['handR'] = g.pt(*hand)
        g.push(16 + p['head_dx'], -164 + p['head_dy'], p['head_rot'], p['head_sx'], p['head_sy'], -20, 50)
        py = p['pitch'] * 10
        g.push(-34, -26, -p['ear'] * 30)                              # far ear: main skin colour outside, pink inside facing us
        self._ink(g, oval(-26, 4, 54, 62), self.SKIN)
        self._ink(g, oval(-24, 6, 37, 44), self.PINK, 0, False)
        g.pop()
        head = smooth([(0, -68), (44, -60), (72, -26), (78, 6), (64, 40), (34, 60), (-6, 66), (-46, 52), (-70, 14), (-68, -28), (-44, -58)], True, 0.5)
        self._ink(g, head, self.SKIN)
        g.push(0, p['cap_dy'])
        self._ink(g, oval(52, -54, 50, 9), self.CAP)
        self._ink(g, smooth([(-56, -52), (-48, -84), (-4, -102), (40, -84), (48, -52), (-4, -60)], True, 0.5), self.CAP)
        self._ink(g, oval(-4, -104, 9, 8), self.CAP)
        g.pop()
        self._ink(g, oval(28, 26 + py, 12, 9), self.PINK, 0, False, a=0.9)
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
        x, y, ws = 34, -8 + py, 0.8
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
        root = (self.ROOT[0], self.ROOT[1] + py)
        c1, c2, tip = self.trunk_cl or self.REST
        cl = bez(root, (root[0] + c1[0], root[1] + c1[1]), (root[0] + c2[0], root[1] + c2[1]), (root[0] + tip[0], root[1] + tip[1]), 22)
        from review_models import trunk_draw
        tp = trunk_draw(self, g, cl, p['gulp'], up=p['trunk_up'])
        self._ink(g, oval(root[0] - 14, root[1] + 4, 22, 24), self.SKIN, 0, False)
        self.anchors['trunk'] = g.pt(*tp); self.anchors['mouth'] = g.pt(46, 44 + py)
        self.anchors['head'] = g.pt(0, 0); self.anchors['top'] = g.pt(0, -100)
        g.push(-30, -36, -p['ear'] * 34 - p['ear_ang'])               # near ear: same size as Stage 1
        ear = oval(-36, 46, 50, 62, 10)
        eo = p['ear_open']
        if eo > 0.03:
            self._ink(g, ear, self.SKIN)
            self._ink(g, oval(-36 + (1 - eo) * 14, 48, 34 * eo, 43, 10), self.PINK, 0, False)
        else:
            self._ink(g, ear, self.PINK)                              # the pink inside ...
            cover = _I(ear, oval(-50, 42, 50, 62, 10))                # ... covered by the outer surface, leaving a rim at the front edge
            if cover is not None:
                self._ink(g, cover, self.SKIN, 3)
            self._ink(g, ear, None)
        g.pop()
        g.pop()
        self.anchors['belly'] = g.pt(0, -80)
        g.pop()
        self.end(g)
