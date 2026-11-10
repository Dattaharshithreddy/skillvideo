"""toon.py - core of the 2D slapstick engine.

World units are pixels on a 1080x1920 (vertical) stage, y grows downward, 24 frames per second.
An Actor has a timeline of pose parameters. You animate pose-to-pose:

    bheemu.move(10, 16, 'snap', x=900, sy=1.2)   # from frame 10 to 16, snap to the new pose
    bheemu.set(40, mouth_open=0.8)               # instant change on frame 40

Everything not mentioned holds its last value. See references/api.md.
"""
import math, os, subprocess, random
import numpy as np
import skia

W, H, FPS = 1080, 1920, 24      # vertical 9:16 for Shorts and Reels
GROUND = 1480


# ----------------------------------------------------------------- easing
def _back(t, s=1.9):
    t -= 1
    return t * t * ((s + 1) * t + s) + 1


def _elastic(t):
    if t <= 0 or t >= 1:
        return max(0.0, min(1.0, t))
    return 1 - math.exp(-6 * t) * math.cos(t * 16)


def _antic(t, a=0.16, split=0.38):
    """Pull back first (anticipation), then shoot to the target."""
    if t < split:
        u = t / split
        return -a * math.sin(u * math.pi / 2)
    u = (t - split) / (1 - split)
    return -a + (1 + a) * (1 - (1 - u) ** 3)


def _bounce(t):
    if t < 0.55:
        return (t / 0.55) ** 2
    u = (t - 0.55) / 0.45
    return 1 - 0.22 * math.sin(u * math.pi) * (1 - u)


EASE = {
    'lin': lambda t: t,
    'in': lambda t: t * t * t,                     # slow start, fast finish (falls, wind-ups releasing)
    'out': lambda t: 1 - (1 - t) ** 3,             # fast start, soft landing
    'io': lambda t: t * t * (3 - 2 * t),           # gentle, for calm acting
    'snap': lambda t: 1 - (1 - t) ** 5,            # cartoon snap: nearly there by the 2nd frame
    'over': _back,                                 # overshoot the pose, then settle back
    'elastic': _elastic,                           # wobble into place (jelly settle)
    'antic': _antic,                               # built-in anticipation
    'bounce': _bounce,
    'step': lambda t: 0.0 if t < 1 else 1.0,       # hold, then pop on the last frame
}


def lerp(a, b, t):
    if isinstance(a, (tuple, list)):
        return tuple(x + (y - x) * t for x, y in zip(a, b))
    if isinstance(a, str) or isinstance(b, str) or a is None or b is None:
        return b if t >= 1 else a
    return a + (b - a) * t


# ----------------------------------------------------------------- timeline
class Timeline:
    def __init__(self, defaults):
        self.defaults = dict(defaults)
        self.keys = {}  # param -> sorted list of (frame, value, ease)

    def _put(self, p, f, v, ease):
        if p not in self.defaults:
            raise KeyError(f'unknown pose parameter "{p}"')
        ks = self.keys.setdefault(p, [])
        ks[:] = [k for k in ks if k[0] != f]
        ks.append((f, v, ease))
        ks.sort(key=lambda k: k[0])

    def value(self, p, f):
        ks = self.keys.get(p)
        if not ks:
            return self.defaults[p]
        if f <= ks[0][0]:
            return ks[0][1]
        prev = ks[0]
        for k in ks[1:]:
            if f < k[0]:
                t = (f - prev[0]) / (k[0] - prev[0])
                return lerp(prev[1], k[1], EASE[k[2]](t))
            prev = k
        return prev[1]

    def pose(self, f):
        return {p: self.value(p, f) for p in self.defaults}

    # -- authoring
    def set(self, f, **params):
        """Instant change at frame f (holds the old value up to f-1)."""
        for p, v in params.items():
            old = self.value(p, f - 1)
            self._put(p, f - 1, old, 'lin')
            self._put(p, f, v, 'step')
        return self

    def move(self, f0, f1, ease='snap', **params):
        """Hold until f0, then travel to the new values by f1 with the given ease."""
        if f1 <= f0:
            return self.set(f1, **params)
        for p, v in params.items():
            self._put(p, f0, self.value(p, f0), 'lin')
            self._put(p, f1, v, ease)
        return self


class Actor(Timeline):
    """Base for anything on stage. Subclasses implement draw(g, pose, f)."""
    DEFAULTS = dict(x=0.0, y=GROUND, rot=0.0, sx=1.0, sy=1.0, alpha=1.0, z=0.0, show=1.0)
    twos = True          # hold drawings for 2 frames (classic), auto-switching to ones on fast moves
    smear = True         # stretch along the path of action on very fast moves
    shadow = 0.0         # shadow half-width in px (0 = none)

    def __init__(self, **over):
        d = dict(Actor.DEFAULTS)
        d.update(getattr(self, 'POSE', {}))
        d.update(over)
        super().__init__(d)
        self.anchors = {}
        self.follow = []  # (f0, f1, actor, anchor, dx, dy)

    def attach(self, f0, f1, actor, anchor, dx=0, dy=0):
        """Between f0 and f1 this actor rides on another actor's anchor point (a hand, a trunk tip...)."""
        self.follow.append((f0, f1, actor, anchor, dx, dy))
        return self

    def frame_pose(self, f):
        ff = f
        if self.twos and f % 2 == 1:
            a, b = self.value('x', f), self.value('x', f - 1)
            c, d = self.value('y', f), self.value('y', f - 1)
            if math.hypot(a - b, c - d) < 26:
                ff = f - 1
        p = self.pose(ff)
        p['_vx'] = self.value('x', f) - self.value('x', f - 1)      # where it came from (drag: scarves, ears)
        p['_vy'] = self.value('y', f) - self.value('y', f - 1)
        p['_fx'] = self.value('x', f + 1) - self.value('x', f)      # where it is going (smears lead the move,
        p['_fy'] = self.value('y', f + 1) - self.value('y', f)      # so the arrival frame is clean for the squash)
        for f0, f1, actor, anchor, dx, dy in self.follow:
            if f0 <= f <= f1 and anchor in actor.anchors:
                ax, ay = actor.anchors[anchor]
                p['x'], p['y'] = ax + dx, ay + dy
                p['_vx'] = p['_vy'] = p['_fx'] = p['_fy'] = 0
        return p

    def draw(self, g, p, f):
        raise NotImplementedError


# ----------------------------------------------------------------- drawing context
class G:
    """Skia canvas plus a matrix stack. Paths are transformed first and inked afterwards,
    so squash, stretch and smears never distort the line weight."""
    INK = (58, 42, 40)

    def __init__(self, canvas):
        self.c = canvas
        self.m = [skia.Matrix()]
        self.alpha = 1.0
        self.ink_w = 5.0

    # matrix stack
    def push(self, x=0, y=0, rot=0, sx=1, sy=1, px=0, py=0):
        """Translate to (x,y), rotate (degrees), then scale about the pivot (px,py)."""
        m = skia.Matrix()
        m.setTranslate(x, y)
        m.preRotate(rot, px, py)
        m.preScale(sx, sy, px, py)
        cur = skia.Matrix.Concat(self.m[-1], m)
        self.m.append(cur)

    def push_m(self, m):
        self.m.append(skia.Matrix.Concat(self.m[-1], m))

    def set_camera(self, m):
        self.push_m(m)
        self.cam_inv = skia.Matrix()
        m.invert(self.cam_inv)

    def pop(self):
        self.m.pop()

    def pt(self, x, y):
        """World position of a local point (used for anchors)."""
        q = self.m[-1].mapXY(x, y)
        inv = getattr(self, 'cam_inv', None)
        if inv is not None:
            q = inv.mapXY(q.x(), q.y())
        return (q.x(), q.y())

    def _tx(self, path):
        out = skia.Path()
        path.transform(self.m[-1], out)
        return out

    def _col(self, c, a=1.0):
        if len(c) == 4:
            a *= c[3] / 255
        return skia.Color(int(c[0]), int(c[1]), int(c[2]), int(255 * max(0, min(1, a * self.alpha))))

    # primitives
    def shape(self, path, fill=None, ink=True, w=None, ink_col=None, a=1.0):
        p = self._tx(path)
        if fill is not None:
            self.c.drawPath(p, skia.Paint(AntiAlias=True, Color=self._col(fill, a)))
        if ink:
            pt = skia.Paint(AntiAlias=True, Color=self._col(ink_col or self.INK, a),
                            Style=skia.Paint.kStroke_Style, StrokeWidth=w or self.ink_w,
                            StrokeCap=skia.Paint.kRound_Cap, StrokeJoin=skia.Paint.kRound_Join)
            boil = getattr(self, 'boil', None)
            if boil is not None:                     # hand-drawn line: it never sits perfectly still
                pt.setPathEffect(skia.DiscretePathEffect.Make(14.0, 1.25, int(boil)))
            self.c.drawPath(p, pt)

    def line(self, pts, col=None, w=None, a=1.0, closed=False):
        self.shape(poly(pts, closed), None, True, w, col, a)

    def shade(self, clip, path, col, blur=14, a=1.0):
        """Soft tone painted inside another shape (form shading that stays within the outline)."""
        self.c.save()
        self.c.clipPath(self._tx(clip), skia.ClipOp.kIntersect, True)
        self.soft(path, col, blur, a)
        self.c.restore()

    def soft(self, path, col, blur=12, a=1.0):
        p = self._tx(path)
        self.c.drawPath(p, skia.Paint(AntiAlias=True, Color=self._col(col, a),
                                      MaskFilter=skia.MaskFilter.MakeBlur(skia.kNormal_BlurStyle, blur)))


# ----------------------------------------------------------------- path helpers
def oval(cx, cy, rx, ry, rot=0):
    p = skia.Path()
    p.addOval(skia.Rect(cx - rx, cy - ry, cx + rx, cy + ry))
    if rot:
        m = skia.Matrix(); m.setRotate(rot, cx, cy)
        q = skia.Path(); p.transform(m, q); return q
    return p


def poly(pts, closed=True):
    p = skia.Path()
    p.moveTo(*pts[0])
    for q in pts[1:]:
        p.lineTo(*q)
    if closed:
        p.close()
    return p


def smooth(pts, closed=True, k=0.5):
    """Smooth curve through points (Catmull-Rom converted to cubics)."""
    n = len(pts)
    p = skia.Path()
    p.moveTo(*pts[0])
    rng = range(n) if closed else range(n - 1)
    for i in rng:
        p0 = pts[(i - 1) % n] if closed or i > 0 else pts[i]
        p1, p2 = pts[i], pts[(i + 1) % n]
        p3 = pts[(i + 2) % n] if closed or i + 2 < n else p2
        c1 = (p1[0] + (p2[0] - p0[0]) * k / 3, p1[1] + (p2[1] - p0[1]) * k / 3)
        c2 = (p2[0] - (p3[0] - p1[0]) * k / 3, p2[1] - (p3[1] - p1[1]) * k / 3)
        p.cubicTo(c1[0], c1[1], c2[0], c2[1], p2[0], p2[1])
    if closed:
        p.close()
    return p


def bez(p0, p1, p2, p3, n=14):
    out = []
    for i in range(n + 1):
        t = i / n
        u = 1 - t
        out.append((u ** 3 * p0[0] + 3 * u * u * t * p1[0] + 3 * u * t * t * p2[0] + t ** 3 * p3[0],
                    u ** 3 * p0[1] + 3 * u * u * t * p1[1] + 3 * u * t * t * p2[1] + t ** 3 * p3[1]))
    return out


def tube(pts, r0, r1=None, cap=True, tip=True):
    """Tapered tube around a centre line (limbs, trunks, tails). Returns a closed path."""
    r1 = r0 if r1 is None else r1
    n = len(pts)
    L, R = [], []
    for i, (x, y) in enumerate(pts):
        a = pts[max(i - 1, 0)]
        b = pts[min(i + 1, n - 1)]
        dx, dy = b[0] - a[0], b[1] - a[1]
        d = math.hypot(dx, dy) or 1
        nx, ny = -dy / d, dx / d
        r = r0 + (r1 - r0) * i / (n - 1)
        L.append((x + nx * r, y + ny * r))
        R.append((x - nx * r, y - ny * r))
    out = L
    if cap and tip:  # round the tip and the root
        (x, y), a = pts[-1], pts[-2]
        dx, dy = x - a[0], y - a[1]
        d = math.hypot(dx, dy) or 1
        out = L + [(x + dx / d * r1 * 0.9, y + dy / d * r1 * 0.9)]
    out = out + R[::-1]
    if cap:
        (x, y), a = pts[0], pts[1]
        dx, dy = x - a[0], y - a[1]
        d = math.hypot(dx, dy) or 1
        out.append((x + dx / d * r0 * 0.9, y + dy / d * r0 * 0.9))
    return smooth(out, True, 0.45)


def limb(a, b, bend=0.0, n=10):
    """Curved centre line from a to b. bend bows it sideways (fraction of length)."""
    mx, my = (a[0] + b[0]) / 2, (a[1] + b[1]) / 2
    dx, dy = b[0] - a[0], b[1] - a[1]
    c = (mx - dy * bend, my + dx * bend)
    return [((1 - t) ** 2 * a[0] + 2 * (1 - t) * t * c[0] + t * t * b[0],
             (1 - t) ** 2 * a[1] + 2 * (1 - t) * t * c[1] + t * t * b[1]) for t in [i / n for i in range(n + 1)]]


def arc_pts(cx, cy, rx, ry, a0, a1, n=12):
    return [(cx + rx * math.cos(math.radians(a0 + (a1 - a0) * i / n)),
             cy + ry * math.sin(math.radians(a0 + (a1 - a0) * i / n))) for i in range(n + 1)]


# ----------------------------------------------------------------- camera
class Camera(Timeline):
    def __init__(self):
        super().__init__(dict(x=W / 2, y=H / 2, zoom=1.0, shake=0.0))

    def matrix(self, f, parallax=1.0):
        p = self.pose(f)
        sx = sy = 0
        if p['shake'] > 0.01:
            r = random.Random(f * 7919)
            sx, sy = (r.uniform(-1, 1) * p['shake'], r.uniform(-1, 1) * p['shake'])
        m = skia.Matrix()
        m.setTranslate(W / 2 + sx, H / 2 + sy)
        m.preScale(p['zoom'], p['zoom'])
        m.preTranslate(-(W / 2 + (p['x'] - W / 2) * parallax), -(H / 2 + (p['y'] - H / 2) * parallax))
        return m


# ----------------------------------------------------------------- stage
class Stage:
    def __init__(self, frames, bg=None, size=(W, H), fps=FPS):
        self.frames, self.size, self.fps = frames, size, fps
        self.cam = Camera()
        self.actors = []
        self.bg = bg                 # callable(canvas, camera, f)
        self.overlays = []           # callables(g, f) drawn in screen space
        self.fx = []                 # callables(g, f) drawn in world space above the actors
        self.cuts = set()            # frames where the shot changes (no smears across a cut)
        self.grain = 0.006

    def add(self, *actors):
        self.actors.extend(actors)
        return actors[0] if len(actors) == 1 else actors

    def cut(self, f, **cam):
        """Hard cut at frame f: jump the camera and suppress smears across the cut."""
        self.cuts.add(f)
        if cam:
            self.cam.set(f, **cam)

    def shake(self, f, amount=22, dur=8):
        self.cam.set(f, shake=amount)
        self.cam.move(f, f + dur, 'out', shake=0)

    def draw_frame(self, canvas, f):
        canvas.save()
        canvas.clear(skia.Color(240, 232, 214))
        if self.bg:
            self.bg(canvas, self.cam, f)
        g = G(canvas)
        g.set_camera(self.cam.matrix(f))
        live = []
        cvx = self.cam.value('x', f) - self.cam.value('x', f - 1)
        cvy = self.cam.value('y', f) - self.cam.value('y', f - 1)
        for a in self.actors:
            p = a.frame_pose(f)
            p['_vx'] -= cvx; p['_vy'] -= cvy      # smears follow motion as the camera sees it
            p['_fx'] -= self.cam.value('x', f + 1) - self.cam.value('x', f)
            p['_fy'] -= self.cam.value('y', f + 1) - self.cam.value('y', f)
            if f in self.cuts:
                p['_vx'] = p['_vy'] = 0.0
            if f + 1 in self.cuts:
                p['_fx'] = p['_fy'] = 0.0
            if p['show'] >= 0.5 and p['alpha'] > 0.01:
                live.append((p['z'], len(live), a, p))
        live.sort(key=lambda t: (t[0], t[1]))
        # pass 1 (dry): let actors publish anchors so followers can ride them
        null = G(_scratch.getCanvas()); null.set_camera(self.cam.matrix(f))
        for _, _, a, p in live:
            if not a.follow:
                a.draw(null, p, f)
        for _, _, a, p in live:
            if a.follow:
                p.update({k: v for k, v in a.frame_pose(f).items() if k in ('x', 'y')})
                a.draw(null, p, f)
        for _, _, a, p in live:
            if a.follow:
                p.update({k: v for k, v in a.frame_pose(f).items() if k in ('x', 'y')})
            g.alpha = p['alpha']
            if a.shadow:
                h = max(0.0, (p.get('ground', GROUND) - p['y']))
                k = max(0.25, 1 - h / 600)
                g.soft(oval(p['x'], p.get('ground', GROUND) + 6, a.shadow * k * abs(p['sx']) ** 0.5, 16 * k), (40, 30, 50), 9, 0.32 * k)
            g.boil = ((f // 3) * 13 + id(a) % 97) if (getattr(self, 'boil', False) and hasattr(a, 'POSE')) else None
            a.draw(g, p, f)
            g.boil = None
        g.alpha = 1.0
        for e in self.fx:
            e(g, f)
        g.alpha = 1.0
        g.pop()
        for o in self.overlays:
            o(G(canvas), f)
        canvas.restore()

    def render(self, out, f0=0, f1=None, audio=None, scale=1.0, crf=21):
        f1 = self.frames if f1 is None else f1
        w, h = int(self.size[0] * scale) // 2 * 2, int(self.size[1] * scale) // 2 * 2
        surf = skia.Surface(w, h)
        cmd = ['ffmpeg', '-y', '-loglevel', 'error', '-f', 'rawvideo', '-pix_fmt', 'rgba', '-s', f'{w}x{h}',
               '-r', str(self.fps), '-i', '-']
        if audio:
            cmd += ['-i', audio]
        cmd += ['-c:v', 'libx264', '-pix_fmt', 'yuv420p', '-crf', str(crf), '-preset', 'medium']
        if audio:
            cmd += ['-c:a', 'aac', '-b:a', '192k', '-shortest']
        cmd += ['-movflags', '+faststart', out]
        ff = subprocess.Popen(cmd, stdin=subprocess.PIPE)
        rng = np.random.default_rng(1)
        for f in range(f0, f1):
            c = surf.getCanvas()
            c.save(); c.scale(w / W, h / H)
            self.draw_frame(c, f)
            c.restore()
            a = surf.toarray(colorType=skia.kRGBA_8888_ColorType)
            if self.grain:
                n = rng.normal(0, 255 * self.grain, (h // 2, w // 2, 1)).repeat(2, 0).repeat(2, 1)
                a = a.astype(np.int16); a[..., :3] += n.astype(np.int16)
                a = a.clip(0, 255).astype(np.uint8)
            ff.stdin.write(a.tobytes())
        ff.stdin.close(); ff.wait()
        return out

    def probe(self, f, actor, anchor):
        """World position of an actor's anchor at frame f (lets you aim one thing at another)."""
        self.draw_frame(_scratch.getCanvas(), f)
        return actor.anchors[anchor]

    def still(self, f, path, scale=0.5):
        w, h = int(self.size[0] * scale), int(self.size[1] * scale)
        surf = skia.Surface(w, h)
        c = surf.getCanvas(); c.scale(w / W, h / H)
        self.draw_frame(c, f)
        surf.makeImageSnapshot().save(path, skia.kPNG)
        return path

    def sheet(self, frames, path, cols=4, scale=0.25):
        """Contact sheet of chosen frames, for checking the animation by eye."""
        w, h = int(self.size[0] * scale), int(self.size[1] * scale)
        rows = math.ceil(len(frames) / cols)
        surf = skia.Surface(w * cols, h * rows)
        c = surf.getCanvas(); c.clear(skia.ColorBLACK)
        font = skia.Font(skia.Typeface('DejaVu Sans'), 20)
        for i, f in enumerate(frames):
            c.save(); c.translate((i % cols) * w, (i // cols) * h); c.clipRect(skia.Rect(0, 0, w, h)); c.scale(w / W, h / H)
            self.draw_frame(c, f); c.restore()
            c.drawString(f'f{f}', (i % cols) * w + 8, (i // cols) * h + 24, font, skia.Paint(Color=skia.ColorWHITE))
            c.drawString(f'f{f}', (i % cols) * w + 7, (i // cols) * h + 23, font, skia.Paint(Color=skia.ColorBLACK))
        surf.makeImageSnapshot().save(path, skia.kPNG)
        return path


_scratch = skia.Surface(4, 4)
