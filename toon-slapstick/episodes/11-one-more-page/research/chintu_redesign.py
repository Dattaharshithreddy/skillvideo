"""REVIEW ONLY - PROPOSAL. Not production. Chintu redesign options asked for by Harshith on 2026-11-11
("change the attire and hairstyle of kid ... design the character that way").

Nothing here changes engine/cast.py. Each option is a subclass that redraws Chintu's body with a different
outfit and hairstyle; the face, eyes, mouth, ears, legs, feet and the approved hand shape are reused from
the existing model. The only hand change proposed is size: kid hands drawn a little bigger (hand scale
11.5 -> 13.5) so the fingers read in wide shots - see pilot/Kid_Hands_Study.md.

Run:  python3 chintu_redesign.py  ->  ../storyboard/chintu_redesign_options.png
"""
import math, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', '..', '..', 'engine'))
import skia
from toon import Stage, oval, poly, smooth, GROUND, W
from cast import Chintu, _I, _U
from scene import Prop
from show import ball

INK_T = (60, 36, 34)


class Option(Chintu):
    LABEL = ''
    SHIRT = (236, 76, 64); SHIRT_D = (200, 60, 50); SHORTS = (58, 92, 160); HAIR = (40, 34, 40)
    SLEEVE_N = 5
    HAND_S = 13.5

    def shirt_shape(self, k):
        return smooth([(-34 * k, -236), (34 * k, -236), (52 * k, -224), (54 * k, -180), (50 * k, -138), (0, -132), (-50 * k, -138), (-54 * k, -180), (-52 * k, -224)], True, 0.5)

    def shirt_details(self, g, shirt, k, p):
        pass

    def shorts(self, g, k):
        self._ink(g, smooth([(-46 * k, -152), (46 * k, -152), (50 * k, -112), (44 * k, -84), (10 * k, -86), (0, -108), (-10 * k, -86), (-44 * k, -84), (-50 * k, -112)], True, 0.4), self.SHORTS)

    def hair(self, g, head, hx_, p):
        raise NotImplementedError

    def draw(self, g, p, f):
        self.begin(g, p)
        face = p['face']
        k = 1 - 0.3 * abs(face)
        bob = -abs(math.sin(2 * math.pi * p['step'])) * p['stride'] * 0.12
        self._legs2(g, p, 24, -122, 52, 52, 17, 15, self.SKIN, self.HL)
        g.push(0, bob)
        far = 'armR' if face > 0.35 else 'armL' if face < -0.35 else None
        arm = lambda side, key: self._arm2(g, p, side, key, (side * 47 * (1 - 0.5 * abs(face)), -220), (side * 5, 100), 52, 50, 14, self.HAND_S,
                                           self.SKIN, self.HL, sleeve=(self.SHIRT, self.SLEEVE_N))
        if far:
            arm(1 if far == 'armR' else -1, far)
        self.shorts(g, k)
        shirt = self.shirt_shape(k)
        self._ink(g, shirt, self.SHIRT, 0, False)
        self.shirt_details(g, shirt, k, p)
        self._ink(g, shirt, None)
        self._ink(g, smooth([(-15 * k, -236), (-17 * k, -252), (17 * k, -252), (15 * k, -236), (0, -226)], True, 0.4), self.SKIN)
        self.collar(g, k)
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
        self.hair(g, head, hx_, p)
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

    def collar(self, g, k):
        self._ink(g, smooth([(-20 * k, -238), (0, -224), (20 * k, -238)], False), None, 4)


class A(Option):
    """A - School day: white half-shirt with a pocket and a pencil, navy shorts, neat side parting
    combed with oil, one curl that springs back up at the front."""
    LABEL = 'A  School day: white shirt, navy shorts, side parting'
    SHIRT = (246, 246, 240); SHORTS = (44, 58, 104); HAIR = (34, 30, 36)

    def shirt_details(self, g, shirt, k, p):
        self._ink(g, poly([(0, -232), (0, -140)], False), None, 3, col=(180, 180, 176))
        for y in (-210, -184, -158):
            self._ink(g, oval(4 * k, y, 3.5, 3.5), (210, 210, 205), True, 2)
        self._ink(g, smooth([(14 * k, -206), (40 * k, -206), (40 * k, -180), (14 * k, -180)], True, 0.2), None, 3)
        self._ink(g, poly([(30 * k, -206), (32 * k, -224)], False), None, 6, col=(60, 120, 200))     # pencil

    def collar(self, g, k):
        for s in (-1, 1):
            self._ink(g, smooth([(0, -228), (s * 22 * k, -244), (s * 30 * k, -232), (s * 10 * k, -218)], True, 0.3), self.SHIRT, True, 3.5)

    def hair(self, g, head, hx_, p):
        part = hx_ - 26
        cap = smooth([(-120, -130), (120, -130), (76, 6), (66, -10), (hx_ + 44, -22), (hx_ + 14, -30), (part, -40), (part - 16, -26), (-62, -8), (-76, 6)], True, 0.35)
        h = _I(head, cap)
        if h is not None:
            self._ink(g, h, self.HAIR)
        self._ink(g, smooth([(part, -40), (part - 3, -56)], False), None, 3, col=(90, 80, 90))      # the parting
        self._ink(g, smooth([(hx_ + 2, -34), (hx_ + 14, -16), (hx_ + 26, -20), (hx_ + 22, -32)], True, 0.4), self.HAIR)   # the one lock that won't stay combed
        self._ink(g, smooth([(hx_ - 40, -54), (hx_ - 10, -58), (hx_ + 30, -50)], False), None, 2.4, col=(110, 100, 110))   # oil shine


class B(Option):
    """B - Playground: mustard tee with a green band at the hem and sleeves, leaf-green shorts,
    a soft mop of curls."""
    LABEL = 'B  Playground: mustard tee, green shorts, curly mop'
    SHIRT = (246, 186, 52); SHORTS = (70, 140, 90); HAIR = (46, 32, 30)
    BAND = (70, 140, 90)

    def shirt_details(self, g, shirt, k, p):
        b = _I(shirt, poly([(-90, -152), (90, -152), (90, -120), (-90, -120)]))
        if b is not None:
            self._ink(g, b, self.BAND, 0, False)
        self._ink(g, oval(-22 * k, -186, 9, 9), (236, 96, 70), True, 2.5)                        # a small sun badge
        for i in range(8):
            t = i * math.pi / 4
            self._ink(g, poly([(-22 * k + 12 * math.cos(t), -186 + 12 * math.sin(t)), (-22 * k + 16 * math.cos(t), -186 + 16 * math.sin(t))], False), None, 2.5, col=(236, 96, 70))

    def hair(self, g, head, hx_, p):
        blobs = None
        for x, y, r in ((-62, -14, 18), (-56, -40, 22), (-34, -60, 24), (-6, -70, 25), (22, -66, 24), (48, -50, 22), (64, -24, 18),
                        (hx_ - 24, -44, 16), (hx_ + 2, -48, 16), (hx_ + 26, -42, 15)):
            o = oval(x, y, r, r * 0.92)
            blobs = o if blobs is None else _U(blobs, o)
        top = _U(blobs, _I(head, smooth([(-120, -130), (120, -130), (70, -20), (-70, -20)], True, 0.3)))
        self._ink(g, top, self.HAIR)
        for x, y in ((-30, -62), (2, -72), (30, -62), (-54, -38)):
            self._ink(g, smooth([(x - 7, y + 4), (x, y - 5), (x + 7, y + 3)], False), None, 2.4, col=(100, 76, 70))


class C(Option):
    """C - Home and festival: teal half-sleeve kurta to mid-thigh with three wooden buttons, cream
    shorts, short crop with a soft forelock."""
    LABEL = 'C  Home: teal kurta, cream shorts, short crop'
    SHIRT = (44, 150, 150); SHORTS = (236, 226, 200); HAIR = (38, 32, 34)
    SLEEVE_N = 6

    def shirt_shape(self, k):
        return smooth([(-30 * k, -238), (30 * k, -238), (52 * k, -226), (56 * k, -170), (56 * k, -116), (0, -110), (-56 * k, -116), (-56 * k, -170), (-52 * k, -226)], True, 0.45)

    def shirt_details(self, g, shirt, k, p):
        self._ink(g, poly([(0, -236), (0, -196)], False), None, 3, col=(30, 110, 110))
        for y in (-228, -214, -200):
            self._ink(g, oval(3, y, 4, 4), (176, 120, 70), True, 2)
        b = _I(shirt, poly([(-90, -126), (90, -126), (90, -112), (-90, -112)]))
        if b is not None:
            self._ink(g, b, (240, 200, 90), 0, False)                                              # a yellow border at the hem

    def collar(self, g, k):
        self._ink(g, smooth([(-16 * k, -240), (0, -244), (16 * k, -240)], False), None, 4, col=(30, 110, 110))

    def hair(self, g, head, hx_, p):
        cap = smooth([(-120, -130), (120, -130), (74, 0), (64, -18), (hx_ + 34, -30), (hx_ + 6, -36), (hx_ - 34, -30), (-64, -18), (-74, 0)], True, 0.35)
        h = _I(head, cap)
        if h is not None:
            self._ink(g, h, self.HAIR)
        self._ink(g, smooth([(hx_ - 14, -40), (hx_ + 2, -18), (hx_ + 18, -14), (hx_ + 14, -36)], True, 0.4), self.HAIR)   # the forelock


def sheet(path):
    st = Stage(4)
    x0 = 180
    acts = []
    for i, cls in enumerate((Chintu, A, B, C)):
        for j, (face, yaw) in enumerate(((0.0, 0.0), (-1, -0.7))):
            c = cls(x=x0 + i * 250 + 0, z=1, face=face, yaw=yaw)
            acts.append((c, i, j))
    return acts


if __name__ == '__main__':
    from PIL import Image, ImageDraw, ImageFont
    out_dir = os.path.join(HERE, '..', 'storyboard')
    tiles = []
    labels = ['NOW (approved, unchanged)', A.LABEL, B.LABEL, C.LABEL]
    for cls in (Chintu, A, B, C):
        row = []
        for face, yaw, extra in ((0.0, 0.0, {}), (-1, -0.7, {}),
                                 (-1, -0.7, dict(armL=(-72, -112), armR=(-114, -126), handL='open', handR='open', bendL=0.35, bendR=0.35, pupil=(-0.6, -0.5))),
                                 (-1, -0.7, dict(armL=(-58, -92), armR=(-100, -104), handL='grip', handR='grip', smile=0.9))):
            st = Stage(4)
            c = cls(x=W / 2, z=1, face=face, yaw=yaw)
            c.set(0, **extra)
            st.add(c)
            if extra.get('handL') == 'grip':
                b = Prop(ball, z=5); st.add(b)
                hl = st.probe(0, c, 'handL'); hr = st.probe(0, c, 'handR')
                b.set(0, x=(hl[0] + hr[0]) / 2 - 6, y=(hl[1] + hr[1]) / 2 - 4)
            st.still(0, '/tmp/_rd.png', scale=0.7)
            im = Image.open('/tmp/_rd.png').convert('RGB')
            row.append(im.crop((im.width * 0.22, im.height * 0.48, im.width * 0.78, im.height * 0.80)))
        tiles.append(row)
    tw, th = row[0].size
    lab = 44
    sheet_im = Image.new('RGB', (tw * 4, (th + lab) * 4 + 80), (250, 247, 240))
    d = ImageDraw.Draw(sheet_im)
    try:
        font = ImageFont.truetype('DejaVuSans-Bold.ttf', 24); big = ImageFont.truetype('DejaVuSans-Bold.ttf', 30)
    except Exception:
        font = big = ImageFont.load_default()
    d.text((16, 8), 'REVIEW ONLY - PROPOSAL: Chintu outfit + hair (cast.py not changed)', fill=(150, 30, 30), font=big)
    d.text((16, 44), 'Columns: front | 3/4 | ready to catch | caught.  Rows A-C: hands drawn 17% bigger', fill=(80, 60, 60), font=font)
    for r, row in enumerate(tiles):
        y = 80 + r * (th + lab)
        d.text((16, y + 8), labels[r], fill=(40, 30, 30), font=font)
        for cidx, t in enumerate(row):
            sheet_im.paste(t, (cidx * tw, y + lab))
    path = os.path.join(out_dir, 'chintu_redesign_options.png')
    sheet_im.save(path)
    print(path, sheet_im.size)
