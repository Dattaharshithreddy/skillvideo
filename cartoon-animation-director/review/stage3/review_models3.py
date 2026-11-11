"""REVIEW ONLY. Stage 3 revision of the Laddu acting rig (2026-11-11). Not a production asset.

Change from Stage 2: the body is no longer a new tube. It is the approved side-body outline,
its belly patch and its three back stripes, carried on a spine. With the spine at rest the
body is the approved drawing; when the spine bends, the same outline bends with it.
Forelegs keep their natural length. The head is still a separate component.
"""
import math
import os
import sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', 'stage2'))
sys.path.insert(0, os.path.join(HERE, '..', 'stage1'))
from review_models2 import LadduAct, profile_head, oval, poly, smooth, tube, bez, _U, _I, _limb_path, _two_bone   # noqa: E402
from cast import Laddu                                                               # noqa: E402

BODY = [(-100, -104), (-82, -142), (-30, -160), (30, -160), (70, -150), (94, -122), (90, -88), (60, -54), (0, -38), (-60, -50), (-98, -76)]
H0, C0 = (-58.0, -92.0), (60.0, -104.0)
L0 = math.hypot(C0[0] - H0[0], C0[1] - H0[1])
U0 = ((C0[0] - H0[0]) / L0, (C0[1] - H0[1]) / L0); N0 = (U0[1], -U0[0])
TAIL0 = bez((-90, -116), (-152, -126), (-162, -196), (-120, -238), 12)
LEG = 90.0                                                            # natural foreleg length, shoulder to paw


class LadduAct2(LadduAct):
    def _skin(self, H, M, C):
        def pos(t):
            return ((1 - t) ** 2 * H[0] + 2 * (1 - t) * t * M[0] + t * t * C[0], (1 - t) ** 2 * H[1] + 2 * (1 - t) * t * M[1] + t * t * C[1])

        def tan(t):
            x = 2 * (1 - t) * (M[0] - H[0]) + 2 * t * (C[0] - M[0]); y = 2 * (1 - t) * (M[1] - H[1]) + 2 * t * (C[1] - M[1])
            d = math.hypot(x, y) or 1
            return x / d, y / d

        def f(P, grow=1.0):
            t = ((P[0] - H0[0]) * U0[0] + (P[1] - H0[1]) * U0[1]) / L0
            n = ((P[0] - H0[0]) * N0[0] + (P[1] - H0[1]) * N0[1]) * grow
            tc = max(0.0, min(1.0, t)); q = pos(tc); u = tan(tc)
            ext = (t - tc) * L0
            return (q[0] + u[0] * ext + u[1] * n, q[1] + u[1] * ext - u[0] * n), math.degrees(math.atan2(u[1], u[0]))
        return f

    def reach(self, p):
        """Foreleg reach as a fraction of its natural length, for the near leg in pose p."""
        C = (60 + p['chest'][0], -104 + p['chest'][1])
        return math.hypot(58 + p['pawN'][0] - (C[0] - 6), -11 + p['pawN'][1] - (C[1] + 8)) / LEG

    def _foreleg(self, g, sh, paw, wrist, near):
        c, el = _two_bone(sh, (paw[0], paw[1]), 44, 46, -1)
        self._ink(g, _limb_path(c, [18, 18, 17.5, 17, 16.5, 16, 15.5, 15, 15, 15, 15.5, 16.5, 17], tip=0.2), self.FUR if near else self.FAR)
        g.push(paw[0], paw[1], wrist)
        self._paw(g, 5, 2, 19, 11, self.CREAM, d=1)
        g.pop()

    def _tail3(self, g, base, p, f):
        d = abs(p['tail_a'] - 12) + abs(p['tail_b'] - 105) + abs(p['tail_tip']) + 60 * p['tail_puff']
        w = max(0.0, 1 - d / 40.0)
        if w <= 0:
            return self._tail2(g, base, p, f)
        # close to the default: use the approved tail curve (blended), so at rest it is the approved tail
        a0 = math.radians(p['tail_a']); b = math.radians(p['tail_b']); tp = math.radians(p['tail_tip'])
        sway = math.sin(f * 0.14) * 0.3
        pts = [base]; x, y = base
        for i in range(12):
            t = (i + 0.5) / 12
            ang = a0 + b * t ** 1.3 + tp * max(0.0, t - 0.6) / 0.4 + sway * t
            x -= math.cos(ang) * 13.5; y -= math.sin(ang) * 13.5
            pts.append((x, y))
        ox, oy = base[0] - TAIL0[0][0], base[1] - TAIL0[0][1]
        k = math.sin(f * 0.14) * 0.25
        appr = [(q[0] + ox - k * 16 * (i / 12) ** 2, q[1] + oy) for i, q in enumerate(TAIL0)]
        self._tail(g, [(a[0] * w + q[0] * (1 - w), a[1] * w + q[1] * (1 - w)) for a, q in zip(appr, pts)])

    def draw(self, g, p, f):
        self.begin(g, p)
        d = -1 if p['face'] < 0 else 1
        g.push(0, 0, 0, self.S * d, self.S)
        bs = p['breath'] * math.sin(f * 0.26)
        H = (H0[0] + p['hip'][0], H0[1] + p['hip'][1])
        C = (C0[0] + p['chest'][0], C0[1] + p['chest'][1] - 1.6 * bs)
        mx, my = (H[0] + C[0]) / 2, (H[1] + C[1]) / 2
        L = math.hypot(C[0] - H[0], C[1] - H[1]) or 1
        ux, uy = (C[0] - H[0]) / L, (C[1] - H[1]) / L
        M = (mx + uy * p['arch'] * 2, my - ux * p['arch'] * 2)
        sk = self._skin(H, M, C)
        self._hindleg(g, H, (-58 + p['hindF'][0], -9 + p['hindF'][1]), False)
        self._foreleg(g, (C[0] + 12, C[1] + 6), (74 + p['pawF'][0], -11 + p['pawF'][1]), p['wristF'], False)
        self._tail3(g, (H[0] - 32, H[1] - 24), p, f)
        grow = 1 + 0.02 * bs
        pts = []
        for P in BODY:
            below = (P[1] - H0[1]) > 20                                # belly side
            pts.append(sk(P, grow * (1 + 0.14 * p['belly'] if below else 1))[0])
        body = smooth(pts, True, 0.5)
        if p['shrug'] > 0.02:
            q, a = sk((52, -150))
            body = _U(body, oval(q[0], q[1] - 6 - 12 * p['shrug'], 26, 8 + 18 * p['shrug'], a))
        self._ink(g, body, self.FUR, 0, False)
        q, a = sk((4, -38), 1 + 0.14 * p['belly'])
        belly = _I(body, oval(q[0], q[1], 76, 22, a))
        if belly is not None:
            self._ink(g, belly, self.CREAM, 0, False)
        for x in (-44, -10, 24):                                      # the approved stripes, carried on the spine
            q, a = sk((x, -150))
            st_ = _I(body, oval(q[0], q[1], 7, 34, a - 8))
            if st_ is not None:
                self._ink(g, st_, self.STRIPE, 0, False)
        self._ink(g, body, None)
        if p['bristle'] > 0.1:
            for x in (-70, -46, -22, 2, 26, 50, 70):
                q, a = sk((x, -160))
                r = math.radians(a)
                self._ink(g, poly([q, (q[0] + math.sin(r) * 11 * p['bristle'] - math.cos(r) * 5, q[1] - math.cos(r) * 11 * p['bristle'] - math.sin(r) * 5)], False), None, 3)
        self._hindleg(g, H, (-58 + p['hindN'][0], -9 + p['hindN'][1]), True)
        paw = (58 + p['pawN'][0], -11 + p['pawN'][1])
        self._foreleg(g, (C[0] - 6, C[1] + 8), paw, p['wristN'], True)
        self.anchors['handR'] = g.pt(*paw); self.anchors['belly'] = g.pt(mx, my)
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
