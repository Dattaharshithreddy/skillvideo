"""REVIEW ONLY - a drawing of Chintu built the way the drawing lessons build a cartoon figure
(cartoon-animation-director/pilot/Drawing_Lessons.md). Not production; engine/cast.py is not changed.

Harshith, 2026-11-11: "can you draw kid properly since now you got drawing lessons".
Same identity as the approved Chintu (about seven, red shirt with yellow stripes, blue shorts, bare feet, black hair
with a tuft) so the drawing can be compared with the model. Outfit / hair options A-C can be put on afterwards.

Top row: the build, step by step. Bottom: finished front view, the catch (namaz / dua hands), and a hands page.
Run:  python3 chintu_drawn.py  ->  ../storyboard/chintu_drawn.png
"""
import math, os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', '..', '..', 'engine'))
import skia
from toon import G, oval, poly, smooth, tube
from cast import _U, _I

OUT = os.path.join(HERE, '..', 'storyboard', 'chintu_drawn.png')
SKIN, SKIN_D = (206, 146, 102), (176, 116, 80)
HAIR = (36, 30, 36)
SHIRT, STRIPE = (232, 72, 60), (252, 210, 76)
SHORTS = (56, 90, 158)
BLUE = (90, 150, 230)
INK = (58, 36, 34)
BALL = (200, 50, 50)

STEPS = ['action', 'shapes', 'skeleton', 'mittens', 'flesh', 'clothes', 'final']


# ------------------------------------------------------------------ pose data (feet at y=0, height ~ 390)
def pose_relaxed():
    return dict(
        head=(0, -292), tilt=0, look=(0.0, 0.0),
        arms=[((-46, -214), (-58, -160), (-60, -110)), ((46, -214), (58, -160), (60, -110))],
        legs=[((-20, -140), (-22, -66), (-23, -14)), ((20, -140), (22, -66), (23, -14))],
        hands='relaxed', ball=None, action=[(4, -380), (-6, -200), (2, 0)])


def pose_catch(ball=False, curl=0.0, low=0):
    return dict(
        head=(0, -290 + low), tilt=0, look=(0.0, 0.55),
        arms=[((-46, -214 + low), (-60, -156 + low), (-22, -166 + low)), ((46, -214 + low), (60, -156 + low), (22, -166 + low))],
        legs=[((-20, -140 + low), (-24 - low * 0.6, -66 + low * 0.5), (-23, -14)), ((20, -140 + low), (24 + low * 0.6, -66 + low * 0.5), (23, -14))],
        hands='namaz', curl=curl, ball=(0, -176 + low) if ball else None, action=[(0, -380), (8, -200), (0, 0)])


# ------------------------------------------------------------------ parts
def head_shape(cx, cy):
    # a kid's head: wide at the cheeks, round chin, slightly flat top
    pts = [(0, -72), (40, -66), (66, -40), (74, -6), (70, 26), (54, 52), (28, 66), (0, 70), (-28, 66), (-54, 52), (-70, 26), (-74, -6), (-66, -40), (-40, -66)]
    return smooth([(cx + x, cy + y) for x, y in pts], True, 0.55)


def ear(cx, cy, s):
    return smooth([(cx, cy - 16), (cx + s * 12, cy - 12), (cx + s * 15, cy + 2), (cx + s * 10, cy + 15), (cx, cy + 14)], True, 0.6)


def limb_tube(a, b, c, r0, r1, r2):
    pts = []
    for i in range(7):
        t = i / 6; pts.append((a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t))
    for i in range(1, 7):
        t = i / 6; pts.append((b[0] + (c[0] - b[0]) * t, b[1] + (c[1] - b[1]) * t))
    # radius profile: root r0, joint r1, end r2 (thicker in the middle of each segment: a little muscle)
    rad = []
    for i in range(13):
        if i <= 6:
            t = i / 6; rad.append(r0 + (r1 - r0) * t + math.sin(math.pi * t) * 1.5)
        else:
            t = (i - 6) / 6; rad.append(r1 + (r2 - r1) * t + math.sin(math.pi * t) * 1.2)
    L, R = [], []
    for i, (x, y) in enumerate(pts):
        p0 = pts[max(i - 1, 0)]; p1 = pts[min(i + 1, 12)]
        dx, dy = p1[0] - p0[0], p1[1] - p0[1]; d = math.hypot(dx, dy) or 1
        nx, ny = -dy / d, dx / d
        L.append((x + nx * rad[i], y + ny * rad[i])); R.append((x - nx * rad[i], y - ny * rad[i]))
    return smooth(L + R[::-1], True, 0.4)


def hand_up(g, cx, cy, side, s=1.0, curl=0.0, construct=False):
    """Palm to the viewer, fingers up. side=+1 is the screen-right hand: little finger on its inner (left) edge,
    thumb on its outer (right) edge. Built as the lesson says: palm, thumb, then four uneven fingers."""
    g.push(cx, cy, 0, s, s)
    if construct:
        g.shape(smooth([(-13, -30), (13, -30), (14, 8), (9, 14), (-9, 14), (-14, 8)], True, 0.7), None, True, 1.8, BLUE)
    palm = smooth([(-12, -9), (-9, -13), (9, -13), (12, -9), (13, 5), (8, 13), (-8, 13), (-13, 5)], True, 0.5)
    shape = palm
    tub = []
    th_a = math.radians(-90 + side * 52)
    tb = (side * 10, 2)
    thumb = tube([tb, (tb[0] + math.cos(th_a) * 13 * (1 - 0.35 * curl), tb[1] + math.sin(th_a) * 13 * (1 - 0.35 * curl))], 4.6, 4.0)
    shape = _U(shape, thumb)
    lens = [11, 15, 16.5, 14.5]                       # little, ring, middle, index (inner -> outer)
    xs = [-8.6, -3.0, 2.8, 8.4]
    fing = []
    for k in range(4):
        bx = side * xs[k]; by = -10
        a = math.radians(-90 + side * (k - 1.5) * 5)
        L = lens[k] * (1 - 0.45 * curl)
        mid = (bx + math.cos(a) * L * 0.55, by + math.sin(a) * L * 0.55)
        a2 = a - side * math.radians(70 * curl) if side > 0 else a + math.radians(70 * curl)
        tip = (mid[0] + math.cos(a2) * L * 0.45, mid[1] + math.sin(a2) * L * 0.45)
        f = tube([(bx, by + 3), mid, tip], 3.5, 3.1)
        fing.append(f)
    if curl < 0.3:
        for f in fing:
            shape = _U(shape, f)
    g.shape(shape, SKIN, True, 3.6)
    if curl < 0.3:
        for k in range(3):                             # short gaps between the fingers
            x0 = side * (xs[k] + xs[k + 1]) / 2
            g.line([(x0, -10), (x0, -15)], INK, 2.4)
        g.shape(smooth([(-6 * side, 2), (0, 5), (7 * side, 1)], False), None, True, 1.8, SKIN_D)   # palm crease
    g.pop()
    return fing


def hand_up_front(g, cx, cy, side, s, curl):
    """The curled fingers, drawn after the ball so they close over its front."""
    if curl < 0.3:
        return
    g.push(cx, cy, 0, s, s)
    lens = [11, 15, 16.5, 14.5]; xs = [-8.6, -3.0, 2.8, 8.4]
    sh = None
    for k in range(4):
        bx = side * xs[k]; by = -10
        a = math.radians(-90 + side * (k - 1.5) * 5)
        L = lens[k] * (1 - 0.2 * curl)
        mid = (bx + math.cos(a) * L * 0.5, by + math.sin(a) * L * 0.5)
        a2 = a - side * math.radians(110 * curl)
        tip = (mid[0] + math.cos(a2) * L * 0.5, mid[1] + math.sin(a2) * L * 0.5)
        f = tube([(bx, by + 2), mid, tip], 3.6, 3.2)
        sh = f if sh is None else _U(sh, f)
    g.shape(sh, SKIN, True, 3.4)
    g.pop()


def hand_relaxed(g, wx, wy, side, s=1.0):
    """Arm hanging down, seen from the front: we see the thumb side. Fingers softly curled, thumb in front."""
    g.push(wx, wy, 0, s, s)
    mit = smooth([(-9, -3), (9, -3), (12, 8), (11, 20), (5, 27), (-3, 27), (-10, 20), (-12, 8)], True, 0.5)
    th = tube([(-side * 6, 4), (-side * 11, 14), (-side * 9, 21)], 4.4, 3.8)
    g.shape(_U(mit, th), SKIN, True, 3.6)
    for k, y in enumerate((14, 19, 23)):
        g.line([(side * 1, y), (side * 9, y - 1 + k)], INK, 2.2)
    g.pop()


def sleeve(g, a, b):
    """Short sleeve: covers the top of the upper arm, a little wider than the arm, with a hem."""
    e = (a[0] + (b[0] - a[0]) * 0.5, a[1] + (b[1] - a[1]) * 0.5)
    r = (a[0] + (a[0] - b[0]) * 0.12, a[1] + (a[1] - b[1]) * 0.12)
    g.shape(tube([r, a, e], 13.5, 13.0, cap=True, tip=False), SHIRT, True, 3.4)
    dx, dy = e[0] - a[0], e[1] - a[1]; d = math.hypot(dx, dy) or 1
    nx, ny = -dy / d * 13, dx / d * 13
    g.line([(e[0] + nx, e[1] + ny), (e[0] - nx, e[1] - ny)], INK, 3.4)


def foot(g, ax, ay, side):
    """Bare foot, front view: heel hidden, wide at the toes, big toe on the inside, four small toe bumps."""
    g.push(ax, ay)
    f = smooth([(-11, -2), (11, -2), (side * 14 + side * 4, 4), (side * 16, 12), (side * 6, 16), (-side * 8, 16), (-side * 15, 11), (-side * 13, 3)], True, 0.55)
    for k, (x, r) in enumerate(((-side * 10, 5.2), (-side * 2, 4.2), (side * 5, 3.8), (side * 11, 3.4), (side * 16, 3.0))):
        f = _U(f, oval(x, 15 - k * 0.6, r, r * 1.05))
    g.shape(f, SKIN, True, 3.4)
    g.pop()


# ------------------------------------------------------------------ the figure
def figure(g, P, step):
    lvl = STEPS.index(step)
    hx, hy = P['head']
    if lvl == 0 or step != 'final':
        g.shape(smooth(P['action'], False, 0.6), None, True, 2.4, BLUE)
    if lvl >= 1 and step not in ('final',):
        g.shape(oval(hx, hy, 74, 72), None, True, 2.0, BLUE)
        g.line([(hx - 74, hy), (hx + 74, hy)], BLUE, 1.2); g.line([(hx, hy - 72), (hx, hy + 72)], BLUE, 1.2)
        g.shape(smooth([(-48, -226), (48, -226), (52, -180), (44, -140), (-44, -140), (-52, -180)], True, 0.6), None, True, 2.0, BLUE)
    if lvl >= 2 and step != 'final':
        for a, b, c in P['arms'] + P['legs']:
            g.line([a, b, c], BLUE, 2.4)
            for q in (a, b, c):
                g.shape(oval(q[0], q[1], 4.5, 4.5), BLUE, False)
    if lvl >= 3 and step in ('mittens', 'flesh', 'clothes'):
        for i, (a, b, c) in enumerate(P['arms']):
            sd = -1 if i == 0 else 1
            if P['hands'] == 'relaxed':
                g.shape(smooth([(c[0] - 11, c[1] - 2), (c[0] + 11, c[1] - 2), (c[0] + 12, c[1] + 26), (c[0] - 12, c[1] + 26)], True, 0.7), None, True, 1.8, BLUE)
            else:
                g.shape(smooth([(sd * 22 - 13, -214), (sd * 22 + 13, -214), (sd * 22 + 14, -172), (sd * 22 - 14, -172)], True, 0.7), None, True, 1.8, BLUE)
        for a, b, c in P['legs']:
            g.shape(oval(c[0] + (6 if c[0] > 0 else -6), c[1] + 8, 20, 9), None, True, 1.8, BLUE)
    if lvl < 4:
        return
    low = P['head'][1] + 290 if P['hands'] == 'namaz' else 0
    # legs and feet (behind the shorts)
    for i, (a, b, c) in enumerate(P['legs']):
        sd = -1 if i == 0 else 1
        g.shape(limb_tube(a, b, c, 16, 12.5, 10.5), SKIN, True, 3.6)
        g.shape(smooth([(b[0] - 6, b[1] + 2), (b[0], b[1] + 5), (b[0] + 6, b[1] + 2)], False), None, True, 1.8, SKIN_D)   # knee
        foot(g, c[0], c[1], sd)
    # arms behind the body only in the relaxed pose
    def arm(i, a, b, c):
        up = tube([a, ((a[0] + b[0]) / 2, (a[1] + b[1]) / 2), b], 11.5, 10.0)
        lo = tube([b, ((b[0] + c[0]) / 2, (b[1] + c[1]) / 2), c], 9.8, 8.2)
        g.shape(_U(up, lo), SKIN, True, 3.6)
    if P['hands'] == 'relaxed':
        for i, (a, b, c) in enumerate(P['arms']):
            arm(i, a, b, c)
    if lvl >= 5:
        # shorts
        g.shape(smooth([(-46, -152 + low), (46, -152 + low), (50, -118 + low), (48, -96 + low), (8, -96 + low), (0, -112 + low), (-8, -96 + low), (-48, -96 + low), (-50, -118 + low)], True, 0.35), SHORTS, True, 3.6)
        g.line([(0, -150 + low), (0, -114 + low)], INK, 2.2)
        # shirt with stripes, short sleeves
        shirt = smooth([(-22, -232 + low), (22, -232 + low), (44, -224 + low), (50, -206 + low), (48, -170 + low), (47, -140 + low), (0, -134 + low), (-47, -140 + low), (-48, -170 + low), (-50, -206 + low), (-44, -224 + low)], True, 0.45)
        g.shape(shirt, SHIRT, False)
        for y in (-208, -184, -160):
            st = _I(shirt, poly([(-90, y + low), (90, y + low), (90, y + 11 + low), (-90, y + 11 + low)]))
            if st is not None:
                g.shape(st, STRIPE, False)
        g.shape(shirt, None, True, 3.6)
        g.shape(smooth([(-16, -232 + low), (0, -220 + low), (16, -232 + low)], False), None, True, 3.0)   # neckline
    else:
        g.shape(smooth([(-48, -226), (48, -226), (52, -180), (44, -140), (-44, -140), (-52, -180)], True, 0.6), SKIN, True, 3.6)
    # neck
    g.shape(smooth([(-12, -246 + low), (12, -246 + low), (13, -228 + low), (-13, -228 + low)], True, 0.5), SKIN, True, 3.0)
    if lvl >= 5:
        g.shape(smooth([(-16, -232 + low), (0, -220 + low), (16, -232 + low)], False), None, True, 3.0)
    # arms in front of the body for the catch
    if P['hands'] == 'namaz':
        for i, (a, b, c) in enumerate(P['arms']):
            arm(i, a, b, c)
            if lvl >= 5:
                sleeve(g, a, b)
    elif lvl >= 5:
        for i, (a, b, c) in enumerate(P['arms']):
            sleeve(g, a, b)
    # head
    for sd in (-1, 1):
        g.shape(ear(hx + sd * 70, hy + 4, sd), SKIN, True, 3.4)
        g.shape(smooth([(hx + sd * 74, hy - 4), (hx + sd * 79, hy + 4), (hx + sd * 74, hy + 10)], False), None, True, 2.0, SKIN_D)
    g.shape(head_shape(hx, hy), SKIN, True, 4.0)
    if lvl >= 5:
        hair = _I(head_shape(hx, hy), smooth([(hx - 120, hy - 140), (hx + 120, hy - 140), (hx + 76, hy - 4), (hx + 62, hy - 30), (hx + 40, hy - 36),
                                              (hx + 30, hy - 26), (hx + 14, hy - 40), (hx - 6, hy - 30), (hx - 22, hy - 44), (hx - 42, hy - 32), (hx - 62, hy - 30), (hx - 76, hy - 4)], True, 0.35))
        tuft = smooth([(hx - 22, hy - 62), (hx - 24, hy - 90), (hx - 8, hy - 74), (hx + 2, hy - 100), (hx + 13, hy - 74), (hx + 28, hy - 92), (hx + 26, hy - 62)], True, 0.4)
        g.shape(_U(hair, tuft), HAIR, True, 3.6)
        g.shape(smooth([(hx - 30, hy - 56), (hx - 4, hy - 62), (hx + 26, hy - 52)], False), None, True, 2.4, (90, 82, 92))   # shine
    # face
    lx, ly = P['look']
    for sd in (-1, 1):
        ex, ey = hx + sd * 27, hy + 2
        g.shape(oval(ex, ey, 14, 17), (255, 255, 255), True, 3.2)
        g.shape(oval(ex + lx * 5, ey + ly * 6, 7.5, 8.5), (54, 34, 30), False)
        g.shape(oval(ex + lx * 5 + 2.5, ey + ly * 6 - 3, 2.6, 2.6), (255, 255, 255), False)
        g.shape(smooth([(ex - sd * 13, ey - 24), (ex, ey - 29), (ex + sd * 12, ey - 25)], False), None, True, 5.0, HAIR)   # brow
        g.shape(oval(hx + sd * 44, hy + 30, 10, 6), (236, 120, 110), False, a=0.35)                                          # cheek
    g.shape(smooth([(hx - 2, hy + 14), (hx + 5, hy + 24), (hx - 3, hy + 27)], False), None, True, 3.0)                      # nose
    g.shape(smooth([(hx - 16, hy + 38), (hx, hy + 48), (hx + 16, hy + 38)], False), None, True, 3.4)                        # smile
    # hands
    curl = P.get('curl', 0.0)
    if P['hands'] == 'relaxed':
        for i, (a, b, c) in enumerate(P['arms']):
            hand_relaxed(g, c[0], c[1], -1 if i == 0 else 1, 1.15)
    else:
        for i, (a, b, c) in enumerate(P['arms']):
            sd = -1 if i == 0 else 1
            hand_up(g, sd * 17, -186 + low, sd, 1.2, curl)
        if P['ball']:
            bx, by = P['ball']
            g.shape(oval(bx, by, 22, 22), BALL, True, 3.4)
            g.shape(smooth([(bx - 16, by - 4), (bx, by + 4), (bx + 16, by - 4)], False), None, True, 3, (255, 240, 230))
        for i in range(2):
            sd = -1 if i == 0 else 1
            hand_up_front(g, sd * 17, -186 + low, sd, 1.2, curl)


def draw_fig(c, P, step, ox, oy, s):
    g = G(c)
    g.push(ox, oy, 0, s, s)
    figure(g, P, step)
    g.pop()


def text(c, s_, x, y, size, col=(40, 30, 30)):
    c.drawString(s_, x, y, skia.Font(None, size), skia.Paint(AntiAlias=True, Color=skia.Color(*col)))


def main():
    W, H = 2000, 1420
    surf = skia.Surface(W, H); c = surf.getCanvas(); c.clear(skia.Color(250, 247, 240))
    text(c, 'REVIEW ONLY - Chintu drawn by construction (drawing lessons applied). Not the model; cast.py unchanged.', 30, 42, 30, (150, 30, 30))
    labels = ['1 line of action', '2 head circle + body bean', '3 stick skeleton, joints', '4 mitten hands, feet', '5 flesh on the sticks', '6 clothes, hair, face']
    for i, st in enumerate(STEPS[:-1]):
        draw_fig(c, pose_relaxed(), st if st != 'clothes' else 'clothes', 170 + i * 330, 520, 1.05)
        text(c, labels[i], 70 + i * 330, 560, 21)
    c.drawLine(30, 590, W - 30, 590, skia.Paint(Color=skia.Color(210, 200, 190), StrokeWidth=2))
    draw_fig(c, pose_relaxed(), 'final', 260, 1360, 1.75)
    text(c, 'FINAL - front, relaxed', 140, 1400, 24)
    draw_fig(c, pose_catch(), 'final', 760, 1360, 1.75)
    text(c, 'CATCH 1 - namaz / dua hands', 600, 1400, 24)
    draw_fig(c, pose_catch(ball=True, curl=0.0), 'final', 1220, 1360, 1.75)
    text(c, 'CATCH 2 - lands in the palms', 1090, 1400, 24)
    draw_fig(c, pose_catch(ball=True, curl=0.9, low=8), 'final', 1690, 1360, 1.75)
    text(c, 'CATCH 3 - fingers close, hands give', 1530, 1400, 24)
    surf.makeImageSnapshot().save(OUT, skia.kPNG)
    print(OUT)


if __name__ == '__main__':
    main()
