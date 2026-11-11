"""REVIEW ONLY - three NEW kid designs (new face, hair, clothes, everything) and the catch done properly.
Not production; engine/cast.py is not changed. Nothing here copies an existing cartoon character.

Harshith, 2026-11-11: "I want different looks, not the same kid: change face, attire, hairstyle, everything, and draw
like how professionals draw. And that is not how you catch a ball."

Professional practice used (cartoon-animation-director/pilot/Drawing_Lessons.md):
  - shape language and a silhouette test (each design must read as a black shape)
  - line weight hierarchy: heavy outer contour, light inner detail lines
  - one cel shadow per part (light from the upper left), one highlight on hair
  - built on construction: head circle, body bean, joints, mitten hands
The catch: palms UP, hands side by side, little fingers together, fingers pointing at the ball - the way hands are held
in dua. Ball drops into the bowl of the hands, the hands give, then he hugs it in. Shown side-on, where the bowl reads.

Run:  python3 new_kid_designs.py  ->  ../storyboard/new_kid_designs.png, ../storyboard/new_kid_catch.png
"""
import math, os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', '..', '..', 'engine'))
import skia
from toon import G, oval, poly, smooth, tube
from cast import _U, _I

SB = os.path.join(HERE, '..', 'storyboard')
INK = (48, 30, 32)
OUT_W, IN_W = 5.0, 2.4                      # line weight: outer contour heavy, inner details light


def darker(c, k=0.78):
    return tuple(int(v * k) for v in c[:3])


def _D(a, b):
    r = skia.Op(a, b, skia.kDifference_PathOp)
    return r if r is not None else a


def moved(path, dx, dy):
    m = skia.Matrix(); m.setTranslate(dx, dy); out = skia.Path(); path.transform(m, out); return out


def part(g, path, col, shade=True, w=OUT_W, sdx=7, sdy=-6):
    """Fill, cel shadow, then the contour. The shadow: the part is filled dark, then the light colour is painted
    again, moved towards the light (upper left) and clipped to the part, so a crescent of shadow stays bottom right."""
    if shade:
        g.shape(path, darker(col), False)
        g.c.save(); g.c.clipPath(g._tx(path), skia.ClipOp.kIntersect, True)
        g.shape(moved(path, -abs(sdx), -abs(sdy)), col, False)
        g.c.restore()
    else:
        g.shape(path, col, False)
    g.shape(path, None, True, w, INK)


def detail(g, pts, w=IN_W, col=INK, closed=False, k=0.5):
    g.shape(smooth(pts, closed, k), None, True, w, col)


def seg_tube(a, b, c, r0, r1, r2):
    return _U(tube([a, ((a[0] + b[0]) / 2, (a[1] + b[1]) / 2), b], r0, r1), tube([b, ((b[0] + c[0]) / 2, (b[1] + c[1]) / 2), c], r1, r2))


# ======================================================================== the three designs
DESIGNS = [
    dict(key='A', name='A  "Cricket kid"', note='round + square: sturdy, sporty. Backwards cap, gap-tooth grin.',
         skin=(196, 134, 92), hair=(30, 26, 30), head='roundsq', hairstyle='cap', cap=(244, 244, 240), cap2=(40, 72, 150),
         eyes='round', brows='thick', nose='button', mouth='gap', ears=1.0,
         top='polo', top_col=(246, 246, 242), top2=(40, 72, 150), bottom='track', bot_col=(40, 72, 150), bot2=(246, 246, 242),
         feet='sneakers', shoe=(250, 250, 250), shoe2=(40, 72, 150), height=1.0, width=1.06),
    dict(key='B', name='B  "Curly dreamer"', note='soft circles: gentle, curious. Cloud of curls, big ears.',
         skin=(178, 118, 82), hair=(52, 34, 30), head='egg', hairstyle='curls', eyes='oval', brows='thin', nose='long',
         mouth='open', ears=1.25,
         top='kurta', top_col=(240, 180, 50), top2=(210, 70, 60), bottom='pyjama', bot_col=(70, 140, 100), bot2=None,
         feet='sandals', shoe=(150, 90, 50), shoe2=None, height=1.02, width=0.96),
    dict(key='C', name='C  "Neat schoolboy"', note='tall rectangle + triangle puff: proper, a bit bossy.',
         skin=(214, 160, 116), hair=(26, 22, 28), head='long', hairstyle='puff', eyes='dot', brows='heavy', nose='triangle',
         mouth='smirk', ears=0.95,
         top='shirt', top_col=(150, 200, 236), top2=(30, 40, 90), bottom='shorts', bot_col=(36, 46, 92), bot2=(200, 40, 40),
         feet='school', shoe=(30, 26, 30), shoe2=(250, 250, 250), height=1.04, width=0.98),
]


# ------------------------------------------------------------------ heads (front)
def head_path(kind, cx, cy):
    if kind == 'roundsq':
        pts = [(0, -66), (46, -62), (70, -34), (76, 0), (72, 32), (54, 58), (24, 70), (0, 72), (-24, 70), (-54, 58), (-72, 32), (-76, 0), (-70, -34), (-46, -62)]
    elif kind == 'egg':
        pts = [(0, -76), (40, -68), (62, -38), (66, 0), (58, 34), (40, 60), (18, 74), (0, 77), (-18, 74), (-40, 60), (-58, 34), (-66, 0), (-62, -38), (-40, -68)]
    else:  # long
        pts = [(0, -78), (42, -72), (62, -44), (64, -6), (60, 30), (46, 58), (22, 74), (0, 78), (-22, 74), (-46, 58), (-60, 30), (-64, -6), (-62, -44), (-42, -72)]
    return smooth([(cx + x, cy + y) for x, y in pts], True, 0.55)


def ears(g, d, cx, cy, half):
    s = d['ears']
    for sd in (-1, 1):
        e = smooth([(cx + sd * (half - 4), cy - 14 * s), (cx + sd * (half + 12 * s), cy - 12 * s), (cx + sd * (half + 15 * s), cy + 3),
                    (cx + sd * (half + 9 * s), cy + 16 * s), (cx + sd * (half - 4), cy + 14 * s)], True, 0.6)
        part(g, e, d['skin'], False)
        detail(g, [(cx + sd * (half + 3), cy - 6), (cx + sd * (half + 9 * s), cy + 2), (cx + sd * (half + 3), cy + 9)], 2.2, darker(d['skin'], 0.6))


def hair_front(g, d, head, cx, cy):
    hc = d['hair']
    if d['hairstyle'] == 'cap':
        # short hair peeking at the sides, cap worn backwards (strap and peak at the back, so we see the crown + a strap)
        sides = _U(_I(head, poly([(cx + 52, cy - 40), (cx + 95, cy - 40), (cx + 95, cy + 6), (cx + 60, cy - 6)])), _I(head, poly([(cx - 52, cy - 40), (cx - 95, cy - 40), (cx - 95, cy + 6), (cx - 60, cy - 6)])))
        if sides is not None:
            part(g, sides, hc, False)
        crown = smooth([(cx - 74, cy - 32), (cx - 68, cy - 62), (cx - 40, cy - 86), (cx, cy - 92), (cx + 40, cy - 86), (cx + 68, cy - 62), (cx + 74, cy - 32),
                        (cx + 40, cy - 40), (cx, cy - 42), (cx - 40, cy - 40)], True, 0.5)
        part(g, crown, d['cap'])
        band = smooth([(cx - 75, cy - 32), (cx - 40, cy - 42), (cx, cy - 44), (cx + 40, cy - 42), (cx + 75, cy - 32), (cx + 74, cy - 23), (cx + 40, cy - 33), (cx, cy - 35), (cx - 40, cy - 33), (cx - 74, cy - 23)], True, 0.5)
        part(g, band, d['cap2'], False, 3.6)
        g.shape(oval(cx, cy - 90, 6, 4), d['cap2'], True, 2.4, INK)                       # button
        for k in (-1, 1):
            detail(g, [(cx + k * 8, cy - 88), (cx + k * 30, cy - 60), (cx + k * 36, cy - 42)], 2.0, darker(d['cap'], 0.7))
        # a few strands sticking out under the cap at the front

    elif d['hairstyle'] == 'curls':
        blobs = None
        for x, y, r in ((-64, -22, 16), (-60, -48, 22), (-40, -72, 24), (-12, -86, 26), (18, -84, 25), (44, -70, 23), (62, -46, 21), (66, -20, 15),
                        (-30, -56, 18), (0, -62, 18), (28, -56, 18)):
            o = oval(cx + x, cy + y, r, r * 0.92)
            blobs = o if blobs is None else _U(blobs, o)
        base = _I(head, smooth([(cx - 120, cy - 140), (cx + 120, cy - 140), (cx + 70, cy - 36), (cx - 70, cy - 36)], True, 0.3))
        hair = _U(blobs, base) if base is not None else blobs
        part(g, hair, hc, True, OUT_W, 6, 6)
        for x, y in ((-40, -66), (-10, -80), (20, -76), (46, -62), (-56, -40), (58, -40), (-2, -50)):
            detail(g, [(cx + x - 8, cy + y + 5), (cx + x, cy + y - 4), (cx + x + 8, cy + y + 4)], 2.0, (110, 80, 70))
        g.shape(smooth([(cx + 2, cy - 46), (cx + 12, cy - 36), (cx + 4, cy - 30), (cx - 4, cy - 37)], True, 0.7), hc, True, 2.6, INK)   # forehead curl
    else:  # neat side parting with a big front puff
        cap = _I(head, smooth([(cx - 120, cy - 150), (cx + 120, cy - 150), (cx + 66, cy - 6), (cx + 58, cy - 34), (cx + 30, cy - 46), (cx - 20, cy - 50),
                                (cx - 58, cy - 34), (cx - 66, cy - 6)], True, 0.4))
        puff = smooth([(cx - 30, cy - 70), (cx - 34, cy - 94), (cx - 4, cy - 108), (cx + 34, cy - 102), (cx + 56, cy - 80), (cx + 40, cy - 66)], True, 0.6)
        hair = _U(cap, puff) if cap is not None else puff
        part(g, hair, hc, True, OUT_W, 6, 6)
        detail(g, [(cx - 30, cy - 50), (cx - 32, cy - 76)], 2.6, (120, 110, 120))         # parting
        for k in range(3):
            detail(g, [(cx - 22 + k * 16, cy - 90 + k * 3), (cx + 4 + k * 14, cy - 84 + k * 4), (cx + 26 + k * 10, cy - 70 + k * 3)], 1.8, (90, 84, 96))
        detail(g, [(cx - 10, cy - 98), (cx + 20, cy - 98)], 4, (110, 104, 116))               # oil shine


def face(g, d, cx, cy, look=(0, 0), happy=0.0):
    lx, ly = look
    sk = d['skin']
    # brows
    for sd in (-1, 1):
        ex = cx + sd * 26
        if d['brows'] == 'thick':
            g.shape(smooth([(ex - sd * 14, cy - 22), (ex, cy - 30), (ex + sd * 14, cy - 25)], False), None, True, 6.5, d['hair'])
        elif d['brows'] == 'thin':
            g.shape(smooth([(ex - sd * 12, cy - 24), (ex, cy - 31), (ex + sd * 12, cy - 27)], False), None, True, 3.4, d['hair'])
        else:
            g.shape(smooth([(ex - sd * 15, cy - 20), (ex - sd * 2, cy - 28), (ex + sd * 15, cy - 26)], False), None, True, 8.0, d['hair'])
    # eyes
    for sd in (-1, 1):
        ex, ey = cx + sd * 26, cy + 2
        if d['eyes'] == 'round':
            g.shape(oval(ex, ey, 15, 17), (255, 255, 255), True, 3.0, INK)
            g.shape(oval(ex + lx * 5, ey + ly * 6 + 1, 9, 10), (40, 26, 22), False)
            g.shape(oval(ex + lx * 5 + 3, ey + ly * 6 - 3, 3.2, 3.2), (255, 255, 255), False)
            detail(g, [(ex - 15, ey - 6), (ex, ey - 18), (ex + 15, ey - 6)], 4.4)                 # thick upper lid
        elif d['eyes'] == 'oval':
            g.shape(oval(ex, ey, 12, 18), (255, 255, 255), True, 3.0, INK)
            g.shape(oval(ex + lx * 4, ey + ly * 6 + 3, 7.5, 10), (40, 26, 22), False)
            g.shape(oval(ex + lx * 4 + 2.5, ey + ly * 6 - 1, 2.6, 2.6), (255, 255, 255), False)
            detail(g, [(ex + sd * 10, ey - 13), (ex + sd * 17, ey - 19)], 2.6)                     # one lash
        else:  # dot eyes, no whites
            g.shape(oval(ex + lx * 3, ey + ly * 3, 6, 8), (30, 22, 22), False)
            g.shape(oval(ex + lx * 3 + 2, ey + ly * 3 - 3, 2, 2), (255, 255, 255), False)
    # nose
    if d['nose'] == 'button':
        g.shape(oval(cx, cy + 22, 7, 5.5), darker(sk, 0.86), True, 2.2, INK)
    elif d['nose'] == 'long':
        detail(g, [(cx - 2, cy + 6), (cx + 6, cy + 24), (cx - 4, cy + 28)], 2.8)
    else:
        detail(g, [(cx + 2, cy + 10), (cx + 8, cy + 26), (cx - 4, cy + 27)], 2.8)
    # cheeks
    for sd in (-1, 1):
        g.shape(oval(cx + sd * 44, cy + 28, 10, 6), (232, 110, 100), False, a=0.32)
    # mouth
    my = cy + 44
    if d['mouth'] == 'gap':
        m = smooth([(cx - 22, my - 4), (cx, my + 2), (cx + 22, my - 4), (cx + 12, my + 14), (cx, my + 17), (cx - 12, my + 14)], True, 0.6)
        g.shape(m, (120, 30, 40), True, 3.0, INK)
        teeth = _I(m, poly([(cx - 30, my - 10), (cx + 30, my - 10), (cx + 30, my + 4), (cx - 30, my + 4)]))
        if teeth is not None:
            g.shape(teeth, (255, 255, 255), False)
            gap = _I(m, poly([(cx - 3, my - 12), (cx + 5, my - 12), (cx + 5, my + 4), (cx - 3, my + 4)]))
            if gap is not None:
                g.shape(gap, (120, 30, 40), False)   # the gap
        g.shape(_I(m, oval(cx, my + 16, 10, 6)) or m, (226, 110, 120), False)
        g.shape(m, None, True, 3.0, INK)
    elif d['mouth'] == 'open':
        m = smooth([(cx - 14, my - 2), (cx + 14, my - 2), (cx + 9, my + 10), (cx, my + 12), (cx - 9, my + 10)], True, 0.6)
        g.shape(m, (120, 30, 40), True, 3.0, INK)
        g.shape(_I(m, oval(cx, my + 11, 8, 5)) or m, (226, 110, 120), False); g.shape(m, None, True, 3.0, INK)
    else:  # smirk
        detail(g, [(cx - 16, my + 2), (cx + 2, my + 6), (cx + 18, my - 4)], 3.4)
        detail(g, [(cx + 18, my - 4), (cx + 21, my - 8)], 2.4)


# ------------------------------------------------------------------ bodies (front)
def hand_relaxed(g, d, wx, wy, side, s=1.18):
    g.push(wx, wy, 0, s, s)
    mit = smooth([(-9, -3), (9, -3), (12, 8), (11, 20), (5, 27), (-3, 27), (-10, 20), (-12, 8)], True, 0.5)
    th = tube([(-side * 6, 4), (-side * 11, 14), (-side * 9, 21)], 4.4, 3.8)
    part(g, _U(mit, th), d['skin'], True, 3.8, 4, 4)
    for k, y in enumerate((13, 18, 22)):
        detail(g, [(side * 1, y), (side * 9, y - 1 + k)], 2.0)
    g.pop()


def feet_front(g, d, ax, ay, side):
    g.push(ax, ay)
    if d['feet'] == 'sneakers':
        shoe = smooth([(-14, -10), (14, -10), (side * 22, 0), (side * 20, 12), (0, 15), (-side * 16, 13), (-side * 18, 2)], True, 0.55)
        part(g, shoe, d['shoe'], True, 4.2, 4, 4)
        g.shape(smooth([(-side * 18, 8), (0, 12), (side * 21, 8), (side * 20, 14), (0, 17), (-side * 17, 15)], True, 0.5), d['shoe2'], True, 3.0, INK)
        for k in range(3):
            detail(g, [(-6 + k * 6, -6), (-2 + k * 6, -2)], 2.0)
    elif d['feet'] == 'sandals':
        f = smooth([(-11, -2), (11, -2), (side * 18, 6), (side * 16, 13), (0, 15), (-side * 13, 13), (-side * 14, 4)], True, 0.55)
        part(g, f, d['skin'], False, 3.6)
        g.shape(smooth([(-side * 18, 12), (side * 20, 12), (side * 20, 17), (-side * 18, 17)], True, 0.4), d['shoe'], True, 3.0, INK)
        g.shape(smooth([(-12, 2), (0, 6), (12, 2)], False), None, True, 5, d['shoe'])
    else:
        sock = smooth([(-11, -16), (11, -16), (11, -2), (-11, -2)], True, 0.3)
        part(g, sock, d['shoe2'], False, 3.4)
        shoe = smooth([(-13, -6), (13, -6), (side * 20, 2), (side * 19, 12), (0, 15), (-side * 15, 13), (-side * 16, 2)], True, 0.55)
        part(g, shoe, d['shoe'], True, 4.2, 4, 4)
        g.shape(oval(side * 6, 0, 5, 2.4), (240, 240, 240), False)                           # shine
    g.pop()


def front_figure(g, d, look=(0, 0)):
    sk = d['skin']; W_ = d['width']
    hx, hy = 0, -300
    arms = [((-46 * W_, -214), (-58 * W_, -160), (-60 * W_, -110)), ((46 * W_, -214), (58 * W_, -160), (60 * W_, -110))]
    legs = [((-20 * W_, -140), (-22 * W_, -66), (-23 * W_, -16)), ((20 * W_, -140), (22 * W_, -66), (23 * W_, -16))]
    # legs
    for i, (a, b, c) in enumerate(legs):
        sd = -1 if i == 0 else 1
        if d['bottom'] == 'pyjama':
            part(g, seg_tube(a, b, c, 16, 12.5, 10.5), sk)
        else:
            part(g, seg_tube(a, b, c, 16, 12.5, 10.5), sk)
            detail(g, [(b[0] - 6, b[1] + 2), (b[0], b[1] + 5), (b[0] + 6, b[1] + 2)], 2.0, darker(sk, 0.62))
        feet_front(g, d, c[0], c[1] + 2, sd)
    # arms (behind the torso edge)
    for a, b, c in arms:
        part(g, seg_tube(a, b, c, 11.5, 10, 8.4), sk)
    for i, (a, b, c) in enumerate(arms):
        hand_relaxed(g, d, c[0], c[1], -1 if i == 0 else 1)
    # bottoms
    bt = d['bottom']
    if bt == 'pyjama':
        pj = smooth([(-46 * W_, -152), (46 * W_, -152), (50 * W_, -110), (44 * W_, -60), (8, -60), (0, -100), (-8, -60), (-44 * W_, -60), (-50 * W_, -110)], True, 0.35)
        part(g, pj, d['bot_col'])
        for sd in (-1, 1):
            detail(g, [(sd * 8, -66), (sd * 26 * W_, -64), (sd * 44 * W_, -66)], 2.0)          # rolled hem
    else:
        sh_ = smooth([(-46 * W_, -152), (46 * W_, -152), (50 * W_, -118), (48 * W_, -96), (8, -96), (0, -112), (-8, -96), (-48 * W_, -96), (-50 * W_, -118)], True, 0.35)
        part(g, sh_, d['bot_col'])
        if bt == 'track':
            for sd in (-1, 1):
                g.shape(poly([(sd * 47 * W_, -146), (sd * 49 * W_, -146), (sd * 47 * W_, -98), (sd * 43 * W_, -98)]), d['bot2'], False)
                g.shape(smooth([(sd * 44 * W_, -148), (sd * 50 * W_, -116), (sd * 47 * W_, -98)], False), None, True, 6, d['bot2'])
        detail(g, [(0, -150), (0, -114)])
    # top
    tp = d['top']; tc = d['top_col']
    if tp == 'kurta':
        body = smooth([(-22, -236), (22, -236), (46 * W_, -226), (52 * W_, -200), (50 * W_, -150), (54 * W_, -106), (0, -100), (-54 * W_, -106), (-50 * W_, -150), (-52 * W_, -200), (-46 * W_, -226)], True, 0.45)
    else:
        body = smooth([(-22, -236), (22, -236), (46 * W_, -226), (52 * W_, -204), (50 * W_, -160), (48 * W_, -138), (0, -132), (-48 * W_, -138), (-50 * W_, -160), (-52 * W_, -204), (-46 * W_, -226)], True, 0.45)
    part(g, body, tc)
    if tp == 'polo':
        band = _I(body, poly([(-90, -196), (90, -196), (90, -184), (-90, -184)]))
        if band is not None:
            g.shape(band, d['top2'], False)
        g.shape(body, None, True, OUT_W, INK)
        for sd in (-1, 1):
            part(g, smooth([(0, -230), (sd * 22, -240), (sd * 30, -230), (sd * 10, -214)], True, 0.3), d['top2'], False, 3.4)
        detail(g, [(0, -224), (0, -202)])
        for y in (-218, -208):
            g.shape(oval(0, y, 2.6, 2.6), INK, False)
    elif tp == 'kurta':
        detail(g, [(0, -232), (0, -190)], 2.6)
        for y in (-224, -212, -200):
            g.shape(oval(0, y, 3, 3), d['top2'], True, 1.6, INK)
        hem = _I(body, poly([(-90, -114), (90, -114), (90, -100), (-90, -100)]))
        if hem is not None:
            g.shape(hem, d['top2'], False)
        g.shape(body, None, True, OUT_W, INK)
        detail(g, [(-16, -234), (0, -226), (16, -234)], 3.0)
    else:  # shirt with pocket, pen, collar
        g.shape(body, None, True, OUT_W, INK)
        for sd in (-1, 1):
            part(g, smooth([(0, -228), (sd * 20, -240), (sd * 28, -228), (sd * 8, -212)], True, 0.3), tc, False, 3.4)
        detail(g, [(0, -222), (0, -138)])
        part(g, smooth([(16, -206), (38, -206), (38, -186), (16, -186)], True, 0.2), tc, False, 2.6)
        g.shape(poly([(30, -214), (34, -214), (34, -200), (30, -200)]), d['top2'], True, 1.8, INK)
        g.shape(poly([(-50 * W_, -144), (50 * W_, -144), (50 * W_, -136), (-50 * W_, -136)]), d['bot2'], True, 2.4, INK)   # belt
    # sleeves
    for a, b, c in arms:
        e = (a[0] + (b[0] - a[0]) * 0.5, a[1] + (b[1] - a[1]) * 0.5)
        r = (a[0] + (a[0] - b[0]) * 0.12, a[1] + (a[1] - b[1]) * 0.12)
        sl = tube([r, a, e], 13.5, 13.0, cap=True, tip=False)
        part(g, sl, tc, True, 4.2, 4, 4)
        if tp == 'polo':
            g.shape(_I(sl, oval(e[0], e[1], 16, 5)) or sl, d['top2'], False)
    # neck + head
    part(g, smooth([(-12, -248), (12, -248), (13, -230), (-13, -230)], True, 0.5), sk, False, 3.0)
    half = {'roundsq': 74, 'egg': 64, 'long': 62}[d['head']]
    ears(g, d, hx, hy + 6, half)
    head = head_path(d['head'], hx, hy)
    part(g, head, sk, True, OUT_W, 5, 5)
    hair_front(g, d, head, hx, hy)
    face(g, d, hx, hy + 2, look)


# ------------------------------------------------------------------ side view (the catch)
def side_figure(g, d, P):
    """Facing screen-left. P: knee, lean, arm keys and hand state."""
    sk = d['skin']; tc = d['top_col']
    knee = P['knee']; lean = P['lean']
    # far leg, near leg (feet pointing left)
    for far in (True, False):
        dx = 8 if far else -6
        hip = (dx, -140 + knee); kn = (dx - 10 - knee * 0.5, -70 + knee * 0.6); an = (dx, -16)
        col = darker(sk, 0.9) if far else sk
        part(g, seg_tube(hip, kn, an, 16, 12.5, 10.5), col)
        g.push(an[0], an[1] + 2)
        shoe = smooth([(10, -10), (8, 4), (4, 14), (-26, 14), (-30, 6), (-24, -2), (-8, -8)], True, 0.5)
        part(g, shoe, d['shoe'] if d['feet'] != 'sandals' else sk, True, 4.2, 4, 4)
        if d['feet'] == 'sneakers':
            g.shape(smooth([(8, 8), (4, 15), (-26, 15), (-31, 9), (-26, 10), (2, 10)], True, 0.5), d['shoe2'], True, 2.8, INK)
        g.pop()
    g.push(0, -140 + knee, -lean)
    # far arm (behind body)
    sh = (4, -76); el, wr = P['far']
    part(g, seg_tube(sh, el, wr, 11.5, 10, 8.4), darker(sk, 0.9))
    # shorts
    part(g, smooth([(-34, -12), (30, -12), (36, 22), (30, 44), (-30, 44), (-36, 20)], True, 0.4), d['bot_col'])
    if d['bottom'] == 'track':
        g.shape(smooth([(-2, -10), (2, 20), (-2, 42)], False), None, True, 6, d['bot2'])
    # torso (side): a bean, belly forward (left)
    body = smooth([(-12, -100), (20, -98), (30, -70), (30, -30), (26, 4), (-6, 8), (-34, 2), (-38, -30), (-32, -66), (-26, -92)], True, 0.5)
    part(g, body, tc)
    if d['top'] == 'polo':
        band = _I(body, poly([(-60, -62), (60, -62), (60, -50), (-60, -50)]))
        if band is not None:
            g.shape(band, d['top2'], False)
        g.shape(body, None, True, OUT_W, INK)
        part(g, smooth([(-22, -96), (0, -104), (8, -94), (-14, -86)], True, 0.4), d['top2'], False, 3.0)
    # neck + head (profile, facing left)
    part(g, smooth([(-8, -110), (10, -110), (10, -94), (-8, -94)], True, 0.5), sk, False, 3.0)
    hx, hy = -6 + P.get('head_dx', 0), -166 + P.get('head_dy', 0)
    g.push(hx, hy, P.get('head_rot', 0))
    hd = smooth([(-56, -40), (-30, -70), (10, -76), (46, -60), (66, -24), (64, 14), (46, 50), (18, 66), (-14, 70), (-40, 62), (-58, 44), (-70, 30),
                 (-72, 18), (-64, 8), (-66, -6), (-62, -22)], True, 0.5)
    part(g, hd, sk, True, OUT_W, 5, 5)
    # ear
    part(g, smooth([(18, -14), (32, -16), (36, 2), (30, 16), (18, 14)], True, 0.6), sk, False, 3.4)
    detail(g, [(24, -6), (30, 2), (24, 8)], 2.0, darker(sk, 0.6))
    if d['hairstyle'] == 'cap':
        crown = smooth([(-48, -44), (-20, -76), (20, -80), (52, -60), (66, -30), (56, -24), (20, -36), (-20, -34), (-44, -30)], True, 0.5)
        part(g, crown, d['cap'])
        peak = smooth([(56, -34), (86, -30), (96, -22), (84, -16), (56, -20)], True, 0.5)              # peak at the back (worn backwards)
        part(g, peak, d['cap2'], False, 3.6)
        part(g, smooth([(-48, -40), (60, -26), (58, -18), (-46, -32)], True, 0.4), d['cap2'], False, 3.0)
        side_hair = _I(hd, smooth([(44, -30), (74, -30), (70, 6), (50, 0), (46, -12)], True, 0.4))
        if side_hair is not None:
            part(g, side_hair, d['hair'], False, 3.6)
        g.shape(smooth([(8, -30), (20, -30), (17, -10), (10, -12)], True, 0.5), d['hair'], True, 2.4, INK)   # sideburn
    # eye (one, profile), brow, nose, mouth
    lx, ly = P.get('look', (-0.6, 0.6))
    g.shape(oval(-36, -6, 9, 15), (255, 255, 255), True, 3.0, INK)
    g.shape(oval(-39 + lx * 2, -4 + ly * 6, 6.5, 9), (40, 26, 22), False)
    g.shape(oval(-36 + lx * 3, -8 + ly * 6, 2.6, 2.6), (255, 255, 255), False)
    detail(g, [(-46, -12), (-34, -22), (-22, -12)], 4.2)
    g.shape(smooth([(-48, -30), (-34, -36), (-20, -32)], False), None, True, 6.5, d['hair'])
    g.shape(oval(-70, 14, 6, 5.5), darker(sk, 0.86), True, 2.2, INK)                                  # button nose
    g.shape(oval(-30, 26, 9, 5), (232, 110, 100), False, a=0.32)
    if P.get('smile', 0) > 0.5:
        m = smooth([(-62, 34), (-40, 36), (-46, 48), (-58, 46)], True, 0.6)
        g.shape(m, (120, 30, 40), True, 2.8, INK)
    else:
        detail(g, [(-62, 36), (-52, 40), (-42, 36)], 3.0)
    g.pop()
    # sleeve on the far arm hidden; near arm + sleeve in front of the body
    el, wr = P['near']
    part(g, seg_tube(sh, el, wr, 11.5, 10, 8.4), sk)
    e = (sh[0] + (el[0] - sh[0]) * 0.5, sh[1] + (el[1] - sh[1]) * 0.5)
    part(g, tube([(sh[0] + 4, sh[1] - 6), sh, e], 14, 13, cap=True, tip=False), tc, True, 4.2, 4, 4)
    if d['top'] == 'polo':
        g.shape(oval(e[0], e[1], 13, 4), d['top2'], True, 2.0, INK)
    # hands
    if P['hands'] == 'cup':
        cup_side(g, d, wr, P.get('ball'), P.get('curl', 0.0))
    else:
        hug_side(g, d, wr, P.get('ball'))
    g.pop()


def cup_side(g, d, wr, ball, curl):
    """Both hands palms up, little fingers together, fingers pointing at the ball (left). From the side we see the
    near hand's thumb edge: a scoop. The far hand's fingertips show just behind the near ones."""
    sk = d['skin']
    x, y = wr
    far = smooth([(x - 4, y - 4), (x - 34, y - 6), (x - 50, y - 16), (x - 54, y - 22), (x - 46, y - 18), (x - 30, y - 12), (x - 6, y - 10)], True, 0.5)
    part(g, far, darker(sk, 0.9), False, 3.4)
    if ball:
        bx, by = ball
        g.shape(oval(bx, by, 22, 22), (200, 50, 50), True, 3.6, INK)
        g.shape(smooth([(bx - 16, by - 2), (bx, by + 6), (bx + 16, by - 2)], False), None, True, 3, (255, 240, 230))
    # near hand: heel at the wrist, palm curving down then the fingers sweeping forward and up (the scoop rim)
    lift = 10 * curl
    scoop = smooth([(x + 4, y - 6), (x + 6, y + 8), (x - 10, y + 16), (x - 30, y + 16), (x - 46, y + 8), (x - 56, y - 6 - lift), (x - 58, y - 16 - lift),
                    (x - 52, y - 16 - lift), (x - 44, y - 6), (x - 30, y + 2), (x - 14, y), (x - 4, y - 8)], True, 0.5)
    part(g, scoop, sk, True, 4.2, 4, -4)
    for k in range(3):                                                    # finger divisions along the rim
        xx = x - 34 - k * 7
        detail(g, [(xx, y + 10), (xx - 4, y + 2 - lift * 0.5)], 2.0)
    thumb = tube([(x - 6, y - 6), (x - 22, y - 12), (x - 36, y - 12)], 4.6, 4.0)       # thumb along the top edge
    part(g, thumb, sk, False, 3.4)


def hug_side(g, d, wr, ball):
    sk = d['skin']
    bx, by = ball
    g.shape(oval(bx, by, 22, 22), (200, 50, 50), True, 3.6, INK)
    g.shape(smooth([(bx - 16, by - 2), (bx, by + 6), (bx + 16, by - 2)], False), None, True, 3, (255, 240, 230))
    x, y = wr
    mitt = smooth([(x + 4, y - 4), (x - 14, y - 14), (x - 26, y - 6), (x - 28, y + 8), (x - 16, y + 16), (x, y + 10)], True, 0.5)
    part(g, mitt, sk, True, 4.0, 4, 4)
    for k in range(3):
        detail(g, [(x - 18 + k * 4, y - 10 + k * 3), (x - 26 + k * 2, y - 2 + k * 3)], 2.0)


# ------------------------------------------------------------------ sheets
def text(c, s_, x, y, size, col=(40, 30, 30), bold=False):
    tf = skia.Typeface('DejaVu Sans', skia.FontStyle.Bold() if bold else skia.FontStyle.Normal())
    c.drawString(s_, x, y, skia.Font(tf, size), skia.Paint(AntiAlias=True, Color=skia.Color(*col)))


def designs_sheet():
    W, H = 2000, 1250
    surf = skia.Surface(W, H); c = surf.getCanvas(); c.clear(skia.Color(250, 247, 240))
    text(c, 'REVIEW ONLY - three NEW kid designs (new face, hair, clothes). Pick one; then a full turnaround follows.', 30, 44, 28, (150, 30, 30), True)
    text(c, 'Heavy outer line, light inner lines, one cel shadow per part (light from the top left). Small black shapes = silhouette test.', 30, 80, 20, (100, 90, 90))
    for i, d in enumerate(DESIGNS):
        ox = 340 + i * 660
        g = G(c); g.push(ox, 1080, 0, 1.75, 1.75); front_figure(g, d, (0.0, 0.1)); g.pop()
        text(c, d['name'], ox - 230, 1140, 30, (40, 30, 30), True)
        text(c, d['note'], ox - 230, 1176, 18, (100, 90, 90))
        # silhouette thumbnail
        rec = skia.PictureRecorder(); pc = rec.beginRecording(skia.Rect(0, 0, 300, 450))
        g2 = G(pc); g2.INK = (0, 0, 0); g2.push(150, 440, 0, 1.0, 1.0); front_figure(g2, d); g2.pop()
        pic = rec.finishRecordingAsPicture()
        c.save(); c.translate(ox + 170, 150); c.scale(0.4, 0.4)
        c.saveLayer(); c.drawPicture(pic)
        c.drawPaint(skia.Paint(Color=skia.Color(30, 26, 30), BlendMode=skia.BlendMode.kSrcIn))
        c.restore(); c.restore()
        # palette
        cols = [d['skin'], d['hair'], d['top_col'], d['bot_col'], d.get('cap') or d['shoe']]
        for k, col in enumerate(cols):
            c.drawRect(skia.Rect.MakeXYWH(ox + 175 + k * 26, 340, 22, 22), skia.Paint(Color=skia.Color(*col[:3])))
    out = os.path.join(SB, 'new_kid_designs.png')
    surf.makeImageSnapshot().save(out, skia.kPNG); print(out)


def catch_sheet():
    d = DESIGNS[0]
    W, H = 2000, 1000
    surf = skia.Surface(W, H); c = surf.getCanvas(); c.clear(skia.Color(250, 247, 240))
    text(c, 'REVIEW ONLY - the catch, done properly (shown with design A, side-on so the bowl of the hands reads)', 30, 44, 28, (150, 30, 30), True)
    text(c, 'Palms UP, hands side by side, little fingers together, fingers pointing at the ball (as hands are held in dua). '
            'The ball drops in, the hands give, he hugs it in.', 30, 80, 20, (100, 90, 90))
    keys = [
        ('1 READY', 'arms out, hands cupped, eyes on the ball', dict(knee=6, lean=6, far=((-30, -50), (-66, -40)), near=((-26, -48), (-62, -36)), hands='cup', look=(-0.8, -0.4), ball_air=(-150, -330))),
        ('2 CONTACT', 'it drops into the bowl of the hands', dict(knee=8, lean=8, far=((-30, -48), (-66, -38)), near=((-26, -46), (-62, -34)), hands='cup', ball=(-90, -52), look=(-0.6, 0.7), head_rot=-6)),
        ('3 GIVE', 'hands sink and come in, knees bend', dict(knee=18, lean=10, far=((-26, -34), (-50, -22)), near=((-22, -32), (-46, -20)), hands='cup', ball=(-74, -36), curl=1.0, look=(-0.4, 0.8), head_rot=-10)),
        ('4 HUG IT IN', 'ball held to the tummy, big grin', dict(knee=4, lean=0, far=((-20, -36), (-30, -54)), near=((-16, -34), (-26, -52)), hands='hug', ball=(-44, -56), look=(-0.4, 0.2), smile=1)),
    ]
    for i, (lab, note, P) in enumerate(keys):
        ox = 300 + i * 470
        g = G(c); g.push(ox, 860, 0, 1.55, 1.55)
        side_figure(g, d, P)
        if 'ball_air' in P:
            bx, by = P['ball_air']
            g.shape(oval(bx, by, 22, 22), (200, 50, 50), True, 3.6, INK)
            p0, p1, p2 = (bx + 8, by + 24), (bx + 26, by + 90), (bx + 56, by + 150)   # its path: down into the hands
            for k in range(8):
                t0, t1 = k / 8, (k + 0.5) / 8
                q = lambda t: ((1 - t) ** 2 * p0[0] + 2 * (1 - t) * t * p1[0] + t * t * p2[0], (1 - t) ** 2 * p0[1] + 2 * (1 - t) * t * p1[1] + t * t * p2[1])
                g.line([q(t0), q(t1)], (150, 140, 140), 2.4)
        g.pop()
        text(c, lab, ox - 150, 930, 28, (40, 30, 30), True)
        text(c, note, ox - 150, 962, 18, (100, 90, 90))
    out = os.path.join(SB, 'new_kid_catch.png')
    surf.makeImageSnapshot().save(out, skia.kPNG); print(out)


if __name__ == '__main__':
    designs_sheet()
    catch_sheet()
