"""REVIEW ONLY - DRAWING STUDY, not the model and not animation.

Harshith, 2026-11-11: "catch the ball like how people do namaz, that pose, hands together facing towards" and
"get the drawing lessons first ... draw like how they build [classic cartoons] ... and then try".

Built the way the drawing lessons build a cartoon figure (notes in cartoon-animation-director/pilot/Drawing_Lessons.md):
  1 line of action  2 head circle + body bean  3 stick arms with joint dots  4 mitten for each hand
  5 thumb, then four fingers one at a time (uneven lengths, round tips)  6 clean line over the construction.
Chintu's proportions only (head r70, height 390); outfit and face are left plain on purpose.

Run:  python3 catch_construction_study.py  ->  ../storyboard/catch_construction_study.png
"""
import math, os
import skia

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, '..', 'storyboard', 'catch_construction_study.png')

BLUE = skia.Color(90, 150, 230)
INK = skia.Color(60, 36, 34)
SKIN = skia.Color(204, 146, 104)
SHIRT = skia.Color(236, 76, 64, 90)
GREY = skia.Color(120, 110, 110)
BALL = skia.Color(200, 50, 50)


def paint(col, w=0.0, fill=False):
    p = skia.Paint(AntiAlias=True, Color=col)
    if fill:
        p.setStyle(skia.Paint.kFill_Style)
    else:
        p.setStyle(skia.Paint.kStroke_Style); p.setStrokeWidth(w); p.setStrokeCap(skia.Paint.kRound_Cap)
        p.setStrokeJoin(skia.Paint.kRound_Join)
    return p


def line(c, pts, col, w):
    path = skia.Path(); path.moveTo(*pts[0])
    for q in pts[1:]:
        path.lineTo(*q)
    c.drawPath(path, paint(col, w))


def curve(c, a, b, d, col, w):
    path = skia.Path(); path.moveTo(*a); path.quadTo(*b, *d); c.drawPath(path, paint(col, w))


def sausage(c, base, ang, length, r, fill, ink, w=3.2):
    """A finger: a rounded tube from base along angle ang (radians)."""
    tip = (base[0] + math.cos(ang) * length, base[1] + math.sin(ang) * length)
    path = skia.Path(); path.moveTo(*base); path.lineTo(*tip)
    p = paint(ink, 2 * r + w); c.drawPath(path, p)
    c.drawPath(path, paint(fill, 2 * r))
    return tip


def hand_parts(cx, cy, side, curl, s):
    """Front view, palm to the viewer, fingers up. side=+1: screen-right hand (little finger on its LEFT = inner,
    thumb on its RIGHT = outer). curl 0..1 closes the fingers forward over whatever is in the palm."""
    pw, ph = 26 * s, 24 * s
    palm = skia.RRect.MakeRectXY(skia.Rect.MakeXYWH(cx - pw / 2, cy - ph / 2, pw, ph), 10 * s, 10 * s)
    thumb = ((cx + side * pw * 0.40, cy + ph * 0.12), math.radians(-60) if side > 0 else math.radians(-120),
             12 * s * (1 - 0.3 * curl), 4.4 * s)
    lengths = [13, 17, 19, 17]                              # little, ring, middle, index: uneven (avoid monotony)
    xs = [-0.34, -0.11, 0.12, 0.35]
    fingers = []
    for k in range(4):
        base = (cx + side * xs[k] * pw, cy - ph * 0.38)
        a = math.radians(-90 + side * (k - 1.5) * 4 - side * curl * 75)   # curl: tips come over, towards the middle
        fingers.append((base, a, lengths[k] * s * (1 - 0.3 * curl), 3.7 * s))
    return palm, thumb, fingers, pw, ph


def draw_tubes(c, tubes, ink):
    for base, a, L, r in tubes:
        tip = (base[0] + math.cos(a) * L, base[1] + math.sin(a) * L)
        p = skia.Path(); p.moveTo(*base); p.lineTo(*tip)
        c.drawPath(p, paint(INK, 2 * r + 3.4) if ink else paint(SKIN, 2 * r))


def hand_back(c, cx, cy, side, curl, s, construct=True):
    palm, thumb, fingers, pw, ph = hand_parts(cx, cy, side, curl, s)
    if construct:                                           # step 4: the mitten
        mit = skia.RRect.MakeRectXY(skia.Rect.MakeXYWH(cx - pw / 2, cy - ph / 2 - 22 * s, pw, ph + 22 * s), 13 * s, 13 * s)
        c.drawRRect(mit, paint(BLUE, 1.6))
    ink = paint(INK, 3.4)
    c.drawRRect(palm, ink)
    draw_tubes(c, [thumb], True)
    if curl < 0.3:
        draw_tubes(c, fingers, True)
    c.drawRRect(palm, paint(SKIN, 0, True))
    draw_tubes(c, [thumb], False)
    if curl < 0.3:
        draw_tubes(c, fingers, False)
        for k in range(3):                                  # short gaps between the fingers
            x0 = (fingers[k][0][0] + fingers[k + 1][0][0]) / 2
            line(c, [(x0, cy - ph * 0.38), (x0, cy - ph * 0.38 - 7 * s)], INK, 2.4)


def hand_front(c, cx, cy, side, curl, s):
    """Curled fingers are drawn after the ball, so they wrap over its front."""
    if curl < 0.3:
        return
    palm, thumb, fingers, pw, ph = hand_parts(cx, cy, side, curl, s)
    draw_tubes(c, fingers, True); draw_tubes(c, fingers, False)


def figure(c, ox, oy, pose, label, step_note):
    """pose: dict of hand height hy, hand spread, ball, curl, knee (crouch px), lean (deg), head_down."""
    hy = pose['hy']; knee = pose.get('knee', 0); lean = pose.get('lean', 0)
    c.save(); c.translate(ox, oy); c.scale(1.25, 1.25)
    # 1 line of action
    curve(c, (0, -390 + knee), (14 + lean, -200), (0, 0), BLUE, 2.2)
    c.save(); c.rotate(lean * 0.4, 0, 0)
    # 2 head circle + body bean + hips
    head_y = -306 + knee + pose.get('head_down', 0)
    c.drawCircle(0, head_y, 70, paint(BLUE, 1.8))
    line(c, [(-70, head_y), (70, head_y)], BLUE, 1.2); line(c, [(0, head_y - 70), (0, head_y + 70)], BLUE, 1.2)
    c.drawOval(skia.Rect.MakeLTRB(-54, -240 + knee, 54, -128 + knee), paint(BLUE, 1.8))
    c.drawOval(skia.Rect.MakeLTRB(-54, -240 + knee, 54, -128 + knee), paint(SHIRT, 0, True))
    # legs: sticks with knees
    for sd in (-1, 1):
        hip = (sd * 24, -128 + knee); kn = (sd * (24 + knee * 0.5), -64 + knee * 0.5); ft = (sd * 26, 0)
        line(c, [hip, kn, ft], BLUE, 2)
        for q in (hip, kn, ft):
            c.drawCircle(*q, 4, paint(BLUE, 0, True))
    # 3 arms: shoulder -> elbow (down at his sides) -> wrist (up and in, short: the forearm points at us)
    for sd in (-1, 1):
        sh = (sd * 44, -222 + knee)
        el = (sd * 58, hy + 52)
        wr = (sd * (pose['spread'] + 4), hy + 26)
        line(c, [sh, el, wr], BLUE, 2.4)
        for q in (sh, el, wr):
            c.drawCircle(*q, 4.5, paint(BLUE, 0, True))
        # clean arm: a skin tube over the sticks
        p = skia.Path(); p.moveTo(*sh); p.lineTo(*el); p.lineTo(*wr)
        c.drawPath(p, paint(INK, 19)); c.drawPath(p, paint(SKIN, 13))
    # 4-5 hands, built mitten first; the ball sits in the palms, in front of them; curled fingers go over it
    for sd in (-1, 1):
        hand_back(c, sd * pose['spread'], hy, sd, pose.get('curl', 0.0), 1.7)
    if pose.get('ball'):
        bx, by = 0, hy + 2
        c.drawCircle(bx, by, 22, paint(BALL, 0, True)); c.drawCircle(bx, by, 22, paint(INK, 3))
        curve(c, (bx - 16, by - 4), (bx, by + 4), (bx + 16, by - 4), skia.Color(255, 240, 230), 3)
    for sd in (-1, 1):
        hand_front(c, sd * pose['spread'], hy, sd, pose.get('curl', 0.0), 1.7)
    c.restore(); c.restore()
    font = skia.Font(None, 22)
    c.drawString(label, ox - 150, oy + 46, font, paint(INK, 0, True))
    c.drawString(step_note, ox - 150, oy + 74, skia.Font(None, 17), paint(GREY, 0, True))


def main():
    W, H = 1700, 860
    surf = skia.Surface(W, H); c = surf.getCanvas(); c.clear(skia.Color(250, 247, 240))
    c.drawString('REVIEW ONLY - drawing study for the namaz / dua catch (pose only, not the model)', 30, 40,
                 skia.Font(None, 28), paint(skia.Color(150, 30, 30), 0, True))
    c.drawString('Blue = construction (line of action, head circle, body bean, stick arms with joints, mitten hands). '
                 'Then thumb + four fingers, uneven, round tips.', 30, 72, skia.Font(None, 18), paint(GREY, 0, True))
    poses = [
        (dict(hy=-178, spread=22), '1  READY', 'palms up, little fingers together, eyes on the ball'),
        (dict(hy=-178, spread=22, ball=1, head_down=6), '2  CONTACT', 'ball lands in the palms'),
        (dict(hy=-176, spread=22, ball=1, curl=0.8, head_down=8), '3  CLOSE', 'fingers curl over the ball'),
        (dict(hy=-160, spread=22, ball=1, curl=0.8, knee=10, head_down=12), '4  GIVE', 'hands sink with it, knees soften'),
    ]
    for i, (p, lab, note) in enumerate(poses):
        figure(c, 230 + i * 410, 760, p, lab, note)
    surf.makeImageSnapshot().save(OUT, skia.kPNG)
    print(OUT)


if __name__ == '__main__':
    main()
