"""sets.py - the outdoor places around Ammamma's house: back garden, lane, terrace, courtyard.

Painted relative to GROUND like india.illu. Use with Painted(width, fn, top=sky, bottom=ground).
Walls, shop boards and the auto carry Telugu lines; see series/bheemu-gaju.md for what they mean.
"""
import math, random
import skia
from toon import oval, poly, smooth, tube, bez, W, H, GROUND
from scene import rect, grad
from india import telugu, _window

G0 = GROUND
FL = GROUND - 90
SKY = (132, 204, 244)
EARTH = (150, 104, 70)
NIGHT = (24, 26, 58)


def _sky(g, width, c0=(120, 196, 244), c1=(226, 244, 240), clouds=True, seed=4):
    grad(g, rect(0, 0, width, FL), c0, c1, 0, FL)
    if clouds:
        r = random.Random(seed)
        for i in range(width // 520 + 1):
            x, y = i * 520 + r.uniform(0, 260), r.uniform(120, 520)
            for k in range(4):
                g.shape(oval(x + k * 62, y + (k % 2) * 16, 86, 44), (255, 255, 255), False, a=0.85)


def _ground(g, width, c0, c1, tufts=None, seed=2):
    grad(g, rect(0, FL, width, H - FL), c0, c1, FL, H)
    r = random.Random(seed)
    for _ in range(width // 40):
        x, y = r.uniform(0, width), r.uniform(FL + 20, H - 60)
        g.shape(oval(x, y, r.uniform(30, 110), r.uniform(5, 12)), (255, 240, 210), False, a=0.1)
    if tufts:
        for _ in range(width // 90):
            x, y = r.uniform(0, width), r.uniform(FL + 6, H - 180)
            for a in (-22, 0, 22):
                g.shape(oval(x + a * 0.5, y - 12, 5, 16, a), tufts, False)


def _palm(g, x, y, s=1.0, col=(60, 140, 90)):
    g.shape(tube([(x, y), (x + 20 * s, y - 260 * s), (x + 6 * s, y - 480 * s)], 16 * s, 11 * s), (140, 104, 78), False)
    tx, ty = x + 6 * s, y - 480 * s
    for a in (-170, -135, -100, -60, -20, 10):
        ex, ey = tx + math.cos(math.radians(a)) * 190 * s, ty + math.sin(math.radians(a)) * 110 * s + 50 * s
        g.shape(smooth([(tx, ty), ((tx + ex) / 2, (ty + ey) / 2 - 52 * s), (ex, ey), ((tx + ex) / 2, (ty + ey) / 2 - 10 * s)], True), col, False)


def _wall(g, x0, x1, h, c0=(246, 238, 220), c1=(226, 210, 184), cap=(190, 110, 80)):
    grad(g, rect(x0, FL - h, x1 - x0, h), c0, c1, FL - h, FL)
    g.shape(rect(x0, FL - h - 22, x1 - x0, 26, 4), cap, False)
    r = random.Random(int(x0) + 7)
    for _ in range(int((x1 - x0) / 130)):                       # damp patches
        g.shape(oval(r.uniform(x0, x1), FL - r.uniform(0, 70), r.uniform(40, 120), r.uniform(16, 46)), (150, 150, 120), False, a=0.22)


def garden(g, width):
    """Back garden: compound wall with a warning nobody obeys, a big mango tree (trunk at x=1300),
    banana plants, a hand pump and a clothesline."""
    _sky(g, width)
    for x in (260, 2250):
        _palm(g, x, FL - 300, 1.0)
    _wall(g, 0, width, 430)
    telugu(g, 'ఇక్కడ పండ్లు కోయరాదు', 640, FL - 310, 66, (170, 40, 40), 'Ramabhadra')        # "Do not pluck fruit here"
    telugu(g, '- అమ్మమ్మ', 850, FL - 240, 46, (170, 40, 40), 'Mallanna')                       # "- Ammamma"
    _ground(g, width, (156, 176, 96), (112, 136, 70), tufts=(84, 150, 80))
    g.shape(oval(1300, FL + 120, 520, 60), (120, 96, 60), False, a=0.35)
    # the mango tree
    g.shape(smooth([(1215, FL + 70), (1238, FL - 300), (1220, FL - 640), (1150, FL - 820), (1250, FL - 800), (1300, FL - 700), (1350, FL - 800),
                    (1470, FL - 860), (1400, FL - 640), (1372, FL - 300), (1400, FL + 70)], True, 0.5), (126, 86, 60), False)
    for yy in (FL - 120, FL - 330, FL - 520):
        g.shape(smooth([(1262, yy), (1290, yy + 30), (1320, yy - 6)], False), None, True, 6, (96, 62, 44))
    g.shape(tube([(1380, FL - 660), (1560, FL - 730), (1760, FL - 700)], 30, 16), (126, 86, 60), False)       # the branch the mango hangs from
    r = random.Random(5)
    for cx, cy_, rx, ry in ((1000, FL - 1010, 300, 200), (1340, FL - 1120, 380, 240), (1700, FL - 1000, 300, 210), (1180, FL - 880, 260, 150), (1560, FL - 900, 280, 150),
                            (860, FL - 860, 200, 130), (1860, FL - 860, 190, 130)):
        g.shape(oval(cx, cy_, rx, ry), (58, 128, 74), False)
    for _ in range(90):
        a, d = r.uniform(0, 6.28), r.uniform(0, 1)
        x, y = 1340 + math.cos(a) * 560 * d, FL - 990 + math.sin(a) * 250 * d
        g.shape(oval(x, y, 44, 16, r.uniform(-40, 40)), (84, 160, 86) if r.random() < 0.6 else (44, 108, 64), False, a=0.8)
    for mx, my in ((960, FL - 850), (1120, FL - 790), (1700, FL - 830), (1820, FL - 790), (1460, FL - 960), (1230, FL - 980)):   # green mangoes
        g.shape(smooth([(mx, my - 30), (mx + 16, my - 22), (mx + 18, my - 2), (mx + 4, my + 8), (mx - 12, my + 2), (mx - 16, my - 16)], True, 0.7), (120, 170, 70), False)
    # banana plants
    for bx in (2040, 2180):
        g.shape(rect(bx - 16, FL - 330, 32, 360, 10), (150, 180, 96), False)
        for a in (-70, -30, 10, 50):
            ex, ey = bx + math.sin(math.radians(a)) * 220, FL - 330 - math.cos(math.radians(a)) * 220
            g.shape(smooth([(bx, FL - 330), ((bx + ex) / 2 - 40, (FL - 330 + ey) / 2), (ex, ey), ((bx + ex) / 2 + 40, (FL - 330 + ey) / 2)], True), (86, 164, 90), False)
    # hand pump
    g.push(-230, 0)
    g.shape(rect(330, FL - 210, 40, 250, 8), (70, 110, 150), False); g.shape(rect(310, FL - 250, 80, 50, 12), (70, 110, 150), False)
    g.shape(tube([(370, FL - 226), (470, FL - 260), (520, FL - 200)], 9, 8), (60, 96, 132), False)
    g.shape(tube([(330, FL - 180), (270, FL - 170), (262, FL - 130)], 10, 10), (60, 96, 132), False)
    g.shape(oval(262, FL + 50, 90, 22), (120, 130, 140), False)
    g.pop()
    # clothesline
    g.shape(rect(2330, FL - 520, 14, 560), (120, 86, 60), False); g.shape(rect(2580, FL - 520, 14, 560), (120, 86, 60), False) if width > 2600 else None
    g.shape(smooth([(1900, FL - 560), (2120, FL - 520), (2337, FL - 510)], False), None, True, 4, (90, 80, 80))
    for i, col in enumerate(((232, 96, 84), (250, 208, 80), (120, 170, 220))):
        g.shape(rect(1960 + i * 110, FL - 548 + i * 8, 90, 150 + (i % 2) * 40, 6), col, False)


def lane(g, width, rain=True):
    """Chinna Veedhi: house wall with posters, a tea stall, a parked auto, a street lamp, puddles."""
    if rain:
        _sky(g, width, (120, 134, 156), (176, 188, 196), clouds=False)
        for i in range(width // 300 + 1):
            g.shape(oval(i * 300 + 80, 150 + (i % 3) * 60, 260, 90), (96, 106, 126), False, a=0.7)
    else:
        _sky(g, width)
    for x in (180, 1500, 2500):
        _palm(g, x, FL - 520, 0.9, (56, 120, 86))
    # houses
    _wall(g, 0, 900, 760, (236, 214, 170), (214, 186, 140), (170, 80, 60))
    g.shape(poly([(-40, FL - 782), (940, FL - 782), (880, FL - 900), (20, FL - 900)]), (176, 84, 60), False)       # tiled roof
    _window(g, 90, FL - 620, 230, 250)
    g.shape(rect(420, FL - 520, 250, 524, 4), (96, 60, 44), False); g.shape(rect(440, FL - 500, 210, 500, 4), (60, 120, 130), False)      # door
    g.shape(oval(620, FL - 250, 10, 10), (250, 214, 110), False)
    _wall(g, 900, 1500, 560, (226, 226, 214), (200, 200, 190), (120, 120, 120))                                                  # the poster wall
    telugu(g, 'ఇక్కడ పోస్టర్లు అంటించరాదు', 1200, FL - 440, 44, (40, 60, 150), 'Ramabhadra')                              # "Stick no posters here"
    for i, (px, py, pw, ph, col) in enumerate(((930, 380, 150, 200, (232, 96, 84)), (1090, 360, 130, 170, (250, 208, 80)), (1230, 390, 150, 210, (120, 180, 150)), (1390, 350, 100, 150, (220, 130, 190)))):
        g.shape(rect(px, FL - py, pw, ph, 3), col, False)
        g.shape(oval(px + pw / 2, FL - py + ph * 0.36, pw * 0.22, pw * 0.26), (250, 236, 210), False)
        g.shape(rect(px + 14, FL - py + ph * 0.72, pw - 28, 12, 3), (255, 250, 240), False)
    # tea stall
    sx = 1560
    g.shape(rect(sx, FL - 470, 560, 474, 6), (120, 170, 190), False)
    g.shape(rect(sx + 30, FL - 290, 500, 150, 4), (60, 52, 60), False, a=0.8)
    g.shape(rect(sx - 10, FL - 150, 580, 154, 6), (96, 140, 160), False)
    g.shape(rect(sx - 20, FL - 168, 600, 24, 6), (236, 226, 206), False)
    g.shape(poly([(sx - 60, FL - 470), (sx + 620, FL - 470), (sx + 580, FL - 560), (sx - 20, FL - 560)]), (214, 60, 56), False)
    for i in range(6):
        g.shape(poly([(sx - 60 + i * 114, FL - 470), (sx - 3 + i * 114, FL - 470), (sx + 9 + i * 106, FL - 560), (sx - 40 + i * 106, FL - 560)]), (250, 246, 236), False, a=0.9)
    g.shape(rect(sx + 60, FL - 690, 440, 120, 8), (250, 208, 80), False)
    telugu(g, 'బాబాయ్ టీ కొట్టు', sx + 280, FL - 612, 56, (126, 30, 44), 'Ramabhadra')                                         # "Uncle's Tea Stall"
    g.shape(rect(sx + 330, FL - 410, 190, 96, 4), (250, 246, 236), False)
    telugu(g, 'అప్పు రేపు', sx + 425, FL - 346, 42, (200, 40, 40), 'Timmana')                                                   # "Credit tomorrow"
    g.shape(oval(sx + 130, FL - 196, 54, 30), (206, 150, 70), False); g.shape(rect(sx + 110, FL - 250, 40, 40, 8), (206, 212, 220), False)   # kettle
    for i in range(4):
        g.shape(rect(sx + 250 + i * 46, FL - 204, 30, 38, 4), (236, 240, 246), False, a=0.9)
    # street lamp
    g.shape(rect(2290, FL - 900, 18, 910), (80, 84, 96), False); g.shape(tube([(2299, FL - 900), (2330, FL - 960), (2400, FL - 950)], 9, 7), (80, 84, 96), False)
    g.shape(oval(2410, FL - 940, 34, 16), (255, 240, 170), False); g.soft(oval(2410, FL - 900, 150, 130), (255, 236, 170), 60, 0.3)
    _wall(g, 2360, width, 500, (240, 220, 196), (214, 190, 160), (150, 90, 70))
    # road
    _ground(g, width, (140, 128, 120) if rain else (176, 150, 120), (104, 96, 96) if rain else (140, 112, 90))
    if rain:
        for px, py, pw in ((400, 150, 240), (1250, 260, 300), (2000, 130, 220), (2700, 240, 280)):
            g.shape(oval(px, FL + py, pw, 34), (150, 170, 196), False, a=0.75)
            g.shape(oval(px - pw * 0.3, FL + py - 6, pw * 0.3, 8), (226, 236, 246), False, a=0.6)


def auto(g, p, f):
    """A parked yellow auto-rickshaw seen from behind and a little to the side, with its slogan."""
    INK = (50, 44, 40)
    for wx in (-150, 150):
        g.shape(oval(wx, -44, 46, 46), (44, 42, 50)); g.shape(oval(wx, -44, 18, 18), (150, 150, 160), False)
    g.shape(smooth([(-200, -70), (-210, -300), (-150, -470), (150, -470), (210, -300), (200, -70)], True, 0.35), (250, 204, 50))
    g.shape(smooth([(-176, -330), (-140, -448), (140, -448), (176, -330)], True, 0.3), (44, 42, 50))                 # black hood
    g.shape(rect(-120, -420, 240, 80, 10), (150, 190, 210), True, 4)
    g.shape(rect(-170, -300, 340, 110, 8), (255, 244, 200), True, 4)
    telugu(g, 'నన్ను చూసి', 0, -252, 38, (190, 30, 40), 'Ramabhadra')                                                # "Don't look at me and cry"
    telugu(g, 'ఏడవకురా!', 0, -206, 38, (190, 30, 40), 'Ramabhadra')
    g.shape(rect(-90, -160, 180, 54, 6), (255, 255, 255), True, 3)
    telugu(g, 'AP 07 BG 143', 0, -122, 30, (30, 30, 30), 'NTR')
    for lx in (-180, 180):
        g.shape(oval(lx, -150, 14, 20), (230, 70, 60), True, 3)
    g.shape(rect(-214, -92, 428, 30, 8), (60, 56, 64))
    return {'top': (0, -470)}


def terrace(g, width):
    """The terrace: low parapet, water tank on a stand, dish antenna, a saree drying, rooftops beyond."""
    _sky(g, width, (110, 190, 244), (236, 244, 226))
    r = random.Random(9)
    for i in range(width // 260 + 1):                              # the town beyond
        x = i * 260 + r.uniform(-30, 30); h = r.uniform(120, 300)
        g.shape(rect(x, FL - 330 - h, 220, h + 100, 4), r.choice(((236, 214, 180), (214, 226, 230), (240, 200, 190), (220, 230, 200))), False)
        g.shape(rect(x + 40, FL - 300 - h * 0.6, 40, 50, 3), (120, 150, 170), False, a=0.7)
    for x in (140, 1180, 2360):
        _palm(g, x, FL - 240, 0.8)
    for kx, ky, col in ((500, 330, (232, 80, 70)), (900, 520, (250, 200, 60)), (1900, 400, (120, 110, 210)), (2300, 600, (60, 170, 150))):   # Sankranti kites far away
        g.shape(poly([(kx, ky - 26), (kx + 20, ky), (kx, ky + 26), (kx - 20, ky)]), col, False)
        g.shape(smooth([(kx, ky + 26), (kx - 30, ky + 80), (kx + 10, ky + 130)], False), None, True, 2, (90, 90, 100))
    _wall(g, 0, width, 250, (240, 226, 200), (216, 196, 166), (176, 96, 70))                    # parapet
    for x in range(60, width, 220):
        g.shape(rect(x, FL - 200, 120, 130, 6), (226, 206, 176), False)
    # water tank on a stand, with the name of the house
    tx = 2000
    for lx in (tx - 150, tx + 120):
        g.shape(rect(lx, FL - 330, 30, 340, 4), (130, 130, 140), False)
    g.shape(rect(tx - 180, FL - 350, 360, 28, 4), (110, 110, 120), False)
    g.shape(rect(tx - 160, FL - 760, 320, 414, 60), (40, 44, 56), False)
    for yy in (FL - 660, FL - 560, FL - 460):
        g.shape(rect(tx - 160, yy, 320, 12), (70, 76, 92), False)
    g.shape(oval(tx, FL - 762, 70, 22), (60, 66, 80), False)
    telugu(g, 'అమ్మమ్మ ఇల్లు', tx, FL - 590, 44, (240, 240, 240), 'Ramabhadra')                 # "Grandma's house"
    g.shape(tube([(tx + 160, FL - 400), (tx + 230, FL - 380), (tx + 236, FL)], 9, 9), (150, 150, 160), False)
    # dish antenna and clothesline
    g.shape(rect(420, FL - 520, 14, 300), (110, 110, 120), False); g.shape(oval(400, FL - 560, 90, 70, -30), (206, 212, 220), False); g.shape(oval(392, FL - 566, 70, 52, -30), (176, 184, 196), False)
    g.shape(rect(820, FL - 640, 14, 420), (120, 86, 60), False); g.shape(rect(1500, FL - 640, 14, 420), (120, 86, 60), False)
    g.shape(smooth([(827, FL - 630), (1160, FL - 590), (1507, FL - 630)], False), None, True, 4, (90, 80, 80))
    g.shape(smooth([(900, FL - 618), (1420, FL - 618), (1430, FL - 330), (1300, FL - 316), (1160, FL - 334), (1020, FL - 316), (892, FL - 330)], True, 0.2), (220, 90, 140), False)
    g.shape(rect(896, FL - 380, 530, 30), (250, 208, 80), False)
    # floor
    grad(g, rect(0, FL, width, H - FL), (206, 150, 120), (166, 110, 90), FL, H)
    for j, (y, h) in enumerate(((FL, 60), (FL + 60, 90), (FL + 150, 130), (FL + 280, 250))):
        g.shape(rect(0, y, width, 4), (150, 96, 80), False, a=0.6)
        tw = 200 + j * 40
        for i in range(-1, width // tw + 2):
            g.shape(poly([(i * tw - j * 30, y), (i * tw - j * 30 + 4, y), (i * tw - j * 30 - 26, y + h), (i * tw - j * 30 - 30, y + h)]), (150, 96, 80), False, a=0.5)


def courtyard(g, width, night=False):
    """The courtyard: house wall with the front door, veranda pillars, the tulasi plant on its painted
    stand (x=1300), a muggu drawn on the floor. night=True lights the lamps for Diwali."""
    if night:
        _sky(g, width, (14, 16, 48), (50, 44, 96), clouds=False)
        r = random.Random(3)
        for _ in range(140):
            g.shape(oval(r.uniform(0, width), r.uniform(0, 620), 2.5, 2.5), (255, 250, 220), False, a=r.uniform(0.4, 1))
        g.shape(oval(520, 300, 60, 60), (255, 246, 214), False); g.soft(oval(520, 300, 130, 130), (255, 246, 214), 50, 0.3)
    else:
        _sky(g, width)
    wall0, wall1 = ((250, 232, 190), (236, 210, 160)) if not night else ((120, 108, 130), (96, 84, 112))
    _wall(g, 0, width, 800, wall0, wall1, (150, 70, 56))
    g.shape(poly([(-40, FL - 822), (width + 40, FL - 822), (width, FL - 940), (0, FL - 940)]), (176, 84, 60) if not night else (92, 52, 66), False)
    for i in range(width // 60 + 1):
        g.shape(oval(i * 60 + 30, FL - 824, 30, 16), (150, 66, 50) if not night else (76, 42, 58), False)
    grad(g, rect(0, FL - 240, width, 240), (190, 96, 70) if not night else (96, 56, 70), (160, 76, 56) if not night else (80, 46, 62), FL - 240, FL)   # red plinth band
    # the front door with a welcome
    dx = 620
    g.shape(rect(dx - 30, FL - 660, 360, 664, 4), (110, 66, 46), False)
    g.shape(rect(dx, FL - 630, 300, 630, 4), (64, 124, 132) if not night else (40, 70, 92), False)
    g.shape(rect(dx + 146, FL - 630, 8, 630), (40, 80, 90), False)
    for yy in (FL - 590, FL - 300):
        for xx in (dx + 20, dx + 166):
            g.shape(rect(xx, yy, 114, 250, 6), (84, 148, 154) if not night else (52, 88, 110), False)
    for i in range(11):
        lx = dx - 20 + i * 34
        g.shape(poly([(lx - 13, FL - 664), (lx + 13, FL - 664), (lx, FL - 590)]), (72, 150, 78) if i % 2 else (96, 170, 86), False)
    g.shape(rect(dx + 20, FL - 780, 260, 86, 8), (250, 240, 214), False)
    telugu(g, 'స్వాగతం', dx + 150, FL - 720, 54, (190, 40, 40), 'Ramabhadra')                           # "Welcome"
    _window(g, 1720, FL - 620, 300, 300)
    telugu(g, 'చెప్పులు ఇక్కడ విడవండి', 2260, FL - 300, 40, (250, 240, 214), 'Mallanna')              # "Leave your slippers here"
    for px in (300, 1160, 2100):                                                                          # veranda pillars
        g.shape(rect(px, FL - 800, 56, 804, 6), (250, 246, 236) if not night else (140, 136, 160), False)
        g.shape(rect(px - 14, FL - 60, 84, 64, 6), (214, 200, 180) if not night else (120, 112, 140), False)
    # floor and muggu
    grad(g, rect(0, FL, width, H - FL), (206, 186, 160) if not night else (84, 76, 104), (170, 146, 122) if not night else (56, 50, 80), FL, H)
    cx, cy_ = 1300, FL + 300
    for k in range(8):
        a = k * math.pi / 4
        g.shape(smooth([(cx, cy_), (cx + math.cos(a - 0.3) * 150, cy_ + math.sin(a - 0.3) * 44), (cx + math.cos(a) * 230, cy_ + math.sin(a) * 66), (cx + math.cos(a + 0.3) * 150, cy_ + math.sin(a + 0.3) * 44)], True), None, True, 5, (255, 255, 250))
    g.shape(oval(cx, cy_, 250, 74), None, True, 4, (255, 255, 250))
    # tulasi kota
    g.shape(poly([(cx - 90, FL + 60), (cx + 90, FL + 60), (cx + 70, FL - 170), (cx - 70, FL - 170)]), (236, 200, 80), False)
    g.shape(rect(cx - 84, FL - 190, 168, 30, 6), (200, 70, 60), False); g.shape(rect(cx - 100, FL + 40, 200, 30, 6), (200, 70, 60), False)
    for i in (-1, 0, 1):
        g.shape(oval(cx + i * 44, FL - 60, 10, 10), (200, 70, 60), False)
    for a in (-50, -25, 0, 25, 50):
        g.shape(tube([(cx, FL - 190), (cx + a * 1.2, FL - 300), (cx + a * 2, FL - 400)], 5, 3), (70, 110, 60), False)
        for t in (0.4, 0.7, 1.0):
            g.shape(oval(cx + a * 2 * t, FL - 190 - 210 * t, 24, 12, a), (60, 150, 80), False)
    if night:
        g.c.drawRect(skia.Rect(0, 0, width, H), skia.Paint(Color=skia.Color(20, 16, 60, 60)))
        for i in range(width // 150 + 1):                                                                 # a row of lamps along the plinth and the roof
            for lx, ly in ((i * 150 + 40, FL - 248), (i * 150 + 110, FL - 830)):
                g.shape(oval(lx, ly, 20, 8), (176, 96, 60), False)
                g.shape(smooth([(lx - 7, ly - 6), (lx, ly - 34), (lx + 7, ly - 6)], True, 0.7), (255, 200, 70), False)
                g.soft(oval(lx, ly - 14, 60, 60), (255, 190, 80), 26, 0.5)
        for lx in (cx - 60, cx, cx + 60):
            g.soft(oval(lx, FL - 200, 70, 70), (255, 190, 80), 30, 0.6)
            g.shape(smooth([(lx - 7, FL - 196), (lx, FL - 226), (lx + 7, FL - 196)], True, 0.7), (255, 210, 90), False)
