"""india.py - the Telugu small-town home where Pandu and Gajju live: painted sets and props.

Sets are painted relative to GROUND so characters stand in front of the furniture.
Furniture tops sit about 270-290 px above GROUND (Pandu's waist).
"""
import math, random
import skia
from toon import G, oval, poly, smooth, tube, bez, arc_pts, W, H, GROUND
from scene import rect, grad, Prop

G0 = GROUND
FL = GROUND - 90        # where the back wall meets the floor


def _room(g, x0, x1, wall0, wall1, dado0, dado1):
    grad(g, rect(x0, 0, x1 - x0, FL), wall0, wall1, 0, FL)
    grad(g, rect(x0, FL - 310, x1 - x0, 310), dado0, dado1, FL - 310, FL)
    g.shape(rect(x0, FL - 318, x1 - x0, 12), (236, 226, 196), False)


def _floor(g, width):
    grad(g, rect(0, FL, width, H - FL), (172, 66, 50), (126, 42, 36), FL, H)       # red-oxide floor
    g.shape(rect(0, FL + 70, width, 10), (206, 150, 96), False, a=0.55)
    g.shape(rect(0, FL + 92, width, 4), (206, 150, 96), False, a=0.4)
    for x in range(-100, width, 420):
        g.shape(oval(x + 200, FL + 250, 170, 26), (214, 110, 90), False, a=0.22)
    g.shape(rect(0, FL - 20, width, 30), (92, 54, 44), False)                      # skirting


def _beams(g, width):
    g.shape(rect(0, 0, width, 64), (112, 70, 50), False)
    for x in range(0, width, 250):
        g.shape(rect(x, 64, 46, 34), (96, 58, 42), False)


def _dabba(g, x, y, w, h, tint=(206, 212, 220)):
    """Steel storage tin."""
    g.shape(rect(x, y, w, h, 8), tint, False)
    g.shape(rect(x + w * 0.12, y + 6, w * 0.16, h - 12, 4), (246, 248, 252), False, a=0.8)
    g.shape(rect(x - 3, y - 10, w + 6, 16, 6), (176, 184, 196), False)
    g.shape(rect(x, y + h * 0.55, w, 4), (160, 168, 180), False)


def _window(g, x, y, w, h):
    grad(g, rect(x, y, w, h), (132, 204, 244), (214, 240, 236), y, y + h)
    g.shape(oval(x + w * 0.75, y + h * 0.26, 44, 44), (255, 240, 170), False)
    tr = x + w * 0.3                                                          # coconut palm outside
    g.shape(tube([(tr, y + h), (tr + 16, y + h * 0.55), (tr + 6, y + h * 0.3)], 12, 9), (150, 110, 80), False)
    for a in (-160, -120, -80, -40, 0, 30):
        ex, ey = tr + 6 + math.cos(math.radians(a)) * 130, y + h * 0.3 + math.sin(math.radians(a)) * 80 + 30
        g.shape(smooth([(tr + 6, y + h * 0.3), ((tr + 6 + ex) / 2, (y + h * 0.3 + ey) / 2 - 34), (ex, ey), ((tr + 6 + ex) / 2, (y + h * 0.3 + ey) / 2 - 8)], True), (70, 150, 96), False)
    g.c.save(); g.c.restore()
    for i in range(1, 6):                                                     # iron bars
        g.shape(rect(x + i * w / 6 - 4, y, 8, h), (70, 64, 70), False)
    for a, b, c, d in ((x - 18, y - 18, w + 36, 22), (x - 18, y + h - 4, w + 36, 22), (x - 18, y - 18, 22, h + 36), (x + w - 4, y - 18, 22, h + 36)):
        g.shape(rect(a, b, c, d, 4), (136, 86, 58), False)


def _photo(g, x, y, col):
    g.shape(rect(x, y, 170, 210, 6), (120, 76, 52), False)
    g.shape(rect(x + 14, y + 14, 142, 182), col, False)
    g.shape(oval(x + 85, y + 92, 34, 40), (214, 170, 130), False); g.shape(oval(x + 85, y + 176, 56, 46), (240, 240, 236), False)
    for i in range(9):                                                        # marigold garland
        a = math.pi * i / 8
        g.shape(oval(x + 85 - math.cos(a) * 96, y + 20 + math.sin(a) * 120, 13, 13), (250, 168, 40) if i % 2 == 0 else (250, 208, 60), False)


def illu(g, width):
    """Kitchen (0-1450), doorway (1500-1800) and hall (1850-3400) of an old Telugu house."""
    _room(g, 0, 1500, (164, 216, 202), (140, 198, 186), (86, 156, 150), (66, 136, 132))            # kitchen: sea-green lime wash
    _room(g, 1500, width, (250, 226, 170), (240, 206, 146), (222, 150, 96), (204, 128, 80))        # hall: warm yellow
    _floor(g, width); _beams(g, width)
    # ---- kitchen
    g.shape(rect(30, G0 - 270, 620, 190, 8), (176, 122, 86), False)            # counter cupboards
    for i in range(4):
        g.shape(rect(46 + i * 150, G0 - 244, 132, 148, 8), (198, 142, 100), False)
        g.shape(oval(160 + i * 150, G0 - 170, 8, 8), (250, 226, 150), False)
    g.shape(rect(18, G0 - 296, 644, 30, 6), (64, 62, 74), False)               # granite top
    g.shape(rect(18, G0 - 296, 644, 8, 4), (120, 120, 134), False)
    g.shape(rect(150, G0 - 340, 330, 46, 10), (206, 212, 220), False)          # two-burner gas stove
    for bx in (232, 398):
        g.shape(oval(bx, G0 - 340, 60, 12), (44, 42, 52), False)
        g.shape(oval(bx, G0 - 318, 11, 11), (60, 60, 70), False)
    g.shape(rect(520, G0 - 470, 88, 176, 26), (214, 80, 70), False)            # gas cylinder
    g.shape(rect(540, G0 - 500, 48, 36, 8), (170, 60, 54), False)
    for row, yy in enumerate((G0 - 900, G0 - 1090)):                           # shelves of steel tins
        g.shape(rect(50, yy, 560, 18, 6), (136, 86, 58), False)
        x = 70
        for i, (w_, h_) in enumerate(((86, 120), (70, 92), (104, 140), (64, 80), (90, 112))):
            _dabba(g, x, yy - h_, w_, h_, (206, 212, 220) if (i + row) % 3 else (232, 196, 110))
            x += w_ + 20
    g.shape(rect(70, G0 - 660, 520, 12, 6), (120, 120, 134), False)            # rail with hanging ladles
    for i, L in enumerate((120, 150, 110, 140, 126)):
        hx = 110 + i * 96
        g.shape(rect(hx - 4, G0 - 650, 8, L), (190, 196, 206), False)
        g.shape(oval(hx, G0 - 650 + L + 18, 24 if i % 2 else 18, 22), (206, 212, 220), False)
    _window(g, 760, G0 - 1090, 400, 420)
    g.shape(rect(1220, G0 - 1060, 170, 230, 6), (250, 248, 240), False)        # calendar
    g.shape(rect(1220, G0 - 1060, 170, 62, 6), (214, 60, 56), False)
    for r in range(3):
        for cc in range(4):
            g.shape(rect(1238 + cc * 36, G0 - 980 + r * 44, 24, 26, 3), (120, 120, 134), False, a=0.5)
    telugu(g, 'నవంబరు', 1305, G0 - 1016, 34, (255, 250, 240), 'Ramabhadra')
    # embroidered wall hanging with a proverb: "Unless you ask, even mother will not serve you"
    g.shape(rect(716, G0 - 590, 500, 120, 10), (250, 240, 214), False)
    g.shape(rect(716, G0 - 590, 500, 12), (214, 60, 56), False); g.shape(rect(716, G0 - 482, 500, 12), (214, 60, 56), False)
    g.shape(rect(700, G0 - 604, 532, 16, 6), (136, 86, 58), False)
    telugu(g, 'అడగనిదే అమ్మైనా పెట్టదు', 966, G0 - 514, 44, (126, 30, 44), 'Ramabhadra')
    g.shape(poly([(1210, G0 - 180), (1400, G0 - 180), (1380, G0 - 96), (1230, G0 - 96)]), (120, 76, 52), False)   # pot stand
    g.shape(oval(1305, G0 - 270, 96, 100), (196, 108, 72), False)              # clay water pot
    g.shape(oval(1305, G0 - 360, 50, 16), (160, 84, 58), False)
    g.shape(rect(1280, G0 - 420, 50, 56, 8), (206, 212, 220), False)           # steel tumbler on top
    g.shape(rect(676, 64, 6, 190), (60, 50, 50), False)                        # hanging bulb
    g.shape(oval(679, 280, 26, 32), (255, 240, 180), False)
    g.soft(oval(679, 290, 130, 130), (255, 236, 170), 60, 0.35)
    # ---- doorway with curtain and mango-leaf toran
    g.shape(rect(1490, G0 - 1010, 330, 920, 4), (120, 76, 52), False)
    grad(g, rect(1520, G0 - 980, 270, 890), (236, 200, 140), (212, 170, 116), G0 - 980, FL)
    g.shape(smooth([(1520, G0 - 980), (1700, G0 - 980), (1640, G0 - 560), (1560, G0 - 330), (1520, G0 - 300)], True, 0.4), (226, 92, 110), False)
    for i in range(7):
        g.shape(oval(1556 + (i % 3) * 30, G0 - 900 + i * 70, 10, 10), (255, 214, 120), False)
    g.shape(rect(1470, G0 - 1040, 370, 14, 6), (150, 110, 60), False)
    for i in range(11):
        lx = 1484 + i * 34
        g.shape(poly([(lx - 13, G0 - 1030), (lx + 13, G0 - 1030), (lx, G0 - 950)]), (72, 150, 78) if i % 2 else (96, 170, 86), False)
    # ---- hall
    _photo(g, 1930, G0 - 1060, (150, 170, 190)); _photo(g, 2150, G0 - 1060, (190, 170, 150))
    g.shape(oval(2470, G0 - 980, 78, 78), (120, 76, 52), False); g.shape(oval(2470, G0 - 980, 62, 62), (252, 246, 228), False)   # clock
    g.shape(poly([(2470, G0 - 980), (2470, G0 - 1026)], False), None, True, 7, (60, 40, 40)); g.shape(poly([(2470, G0 - 980), (2500, G0 - 966)], False), None, True, 7, (60, 40, 40))
    # framed motto over the cot: "Slow and steady is what matters"
    g.shape(rect(2010, G0 - 760, 520, 130, 8), (120, 76, 52), False)
    g.shape(rect(2024, G0 - 746, 492, 102, 4), (252, 246, 228), False)
    telugu(g, 'నిదానమే ప్రధానం', 2270, G0 - 676, 54, (38, 110, 90), 'Timmana')
    g.shape(rect(1960, G0 - 250, 620, 60, 10), (140, 90, 60), False)           # wooden cot with mattress and bolster
    for lx in (1975, 2535):
        g.shape(rect(lx, G0 - 200, 30, 110, 6), (120, 76, 52), False)
    g.shape(rect(1950, G0 - 300, 640, 62, 26), (120, 160, 206), False)
    for i in range(8):
        g.shape(rect(1980 + i * 78, G0 - 300, 26, 62), (250, 246, 236), False, a=0.5)
    g.shape(rect(1964, G0 - 366, 150, 76, 36), (230, 110, 96), False)
    g.shape(rect(2700, G0 - 300, 250, 210, 8), (150, 100, 66), False)          # TV stand
    g.shape(rect(2686, G0 - 318, 278, 24, 6), (250, 246, 236), False)
    g.shape(rect(2712, G0 - 500, 226, 184, 16), (70, 66, 78), False)
    g.shape(rect(2730, G0 - 484, 150, 150, 14), (120, 140, 150), False)
    for i in range(3):
        g.shape(oval(2908, G0 - 460 + i * 40, 10, 10), (206, 212, 220), False)
    _window(g, 3020, G0 - 1090, 330, 400)


# ----------------------------------------------------------------- props
def thali(g, p, f):
    """Steel plate."""
    g.shape(oval(0, 0, 96, 20), (206, 212, 220))
    g.shape(oval(0, -3, 72, 12), (236, 240, 246), True, 3)
    g.shape(oval(-30, -5, 18, 3), (255, 255, 255), False, a=0.9)


def laddu(g, p, f):
    g.shape(oval(0, -20, 22, 21), (240, 170, 50))
    for a in (20, 140, 260):
        g.shape(oval(math.cos(math.radians(a)) * 9, -20 + math.sin(math.radians(a)) * 9, 3, 3), (150, 90, 30), False)


def mango(g, p, f):
    g.shape(smooth([(0, -44), (20, -34), (24, -10), (6, 2), (-14, -4), (-22, -24)], True, 0.7), (250, 190, 40))
    g.shape(oval(-8, -30, 9, 12), (240, 120, 50), False, a=0.6)
    g.shape(poly([(0, -44), (4, -54)], False), None, True, 4, (96, 60, 40))
    g.shape(smooth([(4, -54), (22, -64), (30, -52), (14, -48)], True), (96, 170, 86), True, 3)


# ----------------------------------------------------------------- Telugu lettering
import os as _os
_FONT_DIR = _os.path.join(_os.path.dirname(_os.path.abspath(__file__)), '..', 'fonts')
_FONTS = {}


def _font(name):
    if name not in _FONTS:
        import uharfbuzz as hb
        path = _os.path.join(_FONT_DIR, name + '-Regular.ttf')
        data = open(path, 'rb').read()
        face = hb.Face(data)
        _FONTS[name] = (hb.Font(face), skia.Typeface.MakeFromFile(path), face.upem)
    return _FONTS[name]


def telugu(g, text, x, y, size=60, col=(60, 30, 30), font='Ramabhadra', align='center', a=1.0, outline=None):
    """Draw Telugu (or any) text with proper shaping. Telugu needs HarfBuzz: vowel signs and conjunct
    consonants are placed by the font's rules, which plain drawString does not apply.
    Fonts in ../fonts: Ramabhadra (bold signboard), Timmana (heavy), Mallanna (round), NTR (plain)."""
    import uharfbuzz as hb
    hbf, tf, upem = _font(font)
    buf = hb.Buffer(); buf.add_str(text); buf.guess_segment_properties()
    hb.shape(hbf, buf)
    k = size / upem
    ids, pos, pen = [], [], 0.0
    for info, p_ in zip(buf.glyph_infos, buf.glyph_positions):
        ids.append(info.codepoint); pos.append(skia.Point(pen + p_.x_offset * k, -p_.y_offset * k)); pen += p_.x_advance * k
    ox = x - (pen / 2 if align == 'center' else pen if align == 'right' else 0)
    builder = skia.TextBlobBuilder()
    builder.allocRunPos(skia.Font(tf, size), ids, pos)
    blob = builder.make()
    m = g.m[-1]
    g.c.save(); g.c.concat(m)
    if outline:
        g.c.drawTextBlob(blob, ox, y, skia.Paint(AntiAlias=True, Color=g._col(outline, a), Style=skia.Paint.kStroke_Style, StrokeWidth=size * 0.14, StrokeJoin=skia.Paint.kRound_Join))
    g.c.drawTextBlob(blob, ox, y, skia.Paint(AntiAlias=True, Color=g._col(col, a)))
    g.c.restore()
    return pen
