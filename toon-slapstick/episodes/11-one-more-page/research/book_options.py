"""PROPOSAL ONLY: book prop and holding options for the pilot, after Harshith's review of animatic v002
("it doesn't look like a book", "hands hidden", "doesn't look like he is holding a book").
Draws NEW prop shapes in this file only. Uses the approved Bheemu model and existing controls unchanged.
Nothing here is used in any animatic or episode until one option is chosen.
Run: python3 book_options.py   -> ../../../../cartoon-animation-director/proposals/book_prop_options.png
"""
import os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', '..', '..', 'engine'))
import skia
from PIL import Image, ImageDraw, ImageFont
from toon import Stage, W, GROUND, oval, poly, smooth
from chars import Bheemu
from scene import Prop, rect, book as old_book
from india import telugu
COVER, COVER_D, GOLD, PAGE, PAGE_D = (150, 44, 52), (112, 30, 40), (236, 190, 90), (250, 244, 228), (214, 204, 182)


def open_book(g, p, f):
    """An open hardback seen from outside while someone reads it: two covers meeting at a spine,
    the block of pages showing along the top and the outer edges, a title on the front cover."""
    for s in (-1, 1):                                              # page block, a little bigger than the covers at the top
        g.shape(poly([(s * 6, -74), (s * 118, -66), (s * 122, 58), (s * 6, 66)]), PAGE, True, 3)
        for k in (0.3, 0.6):
            g.shape(poly([(s * 8, -74 + 6 * k), (s * 118, -66 + 6 * k)], False), None, True, 2, PAGE_D)
    for s in (-1, 1):                                              # covers, angled like a shallow V
        g.shape(poly([(s * 4, -62), (s * 112, -56), (s * 116, 66), (s * 4, 74)]), COVER, True, 4)
        g.shape(poly([(s * 16, -48), (s * 100, -43), (s * 103, 54), (s * 16, 60)]), None, True, 2.5, GOLD)
    g.shape(rect(-7, -64, 14, 140, 5), COVER_D, True, 3)           # spine
    for y in (-40, 0, 40):
        g.shape(rect(-7, y, 14, 5, 0), GOLD, False)
    telugu(g, 'కథలు', 60, -6, 34, GOLD, 'Ramabhadra')               # "Stories": text as scenery, on the cover


def closed_book(g, p, f):
    g.shape(rect(-58, -74, 120, 150, 4), PAGE, True, 3)            # page block peeps out on the right and bottom
    g.shape(rect(-64, -78, 118, 150, 6), COVER, True, 4)
    g.shape(rect(-64, -78, 18, 150, 5), COVER_D, True, 3)
    g.shape(rect(-38, -64, 80, 122, 3), None, True, 2.5, GOLD)
    telugu(g, 'కథలు', 2, -6, 34, GOLD, 'Ramabhadra')


def paw_tips(g, p, f):
    """PROPOSAL, a cheat: four black toe tips on each outer edge, so the paws seem to wrap the cover.
    These are drawn by the PROP, not by the approved character model."""
    open_book(g, p, f)
    for s in (-1, 1):
        for k in range(4):
            g.shape(oval(s * 108, -22 + k * 22, 15, 11), (44, 40, 52), True, 3)


BEIGE = (240, 232, 214)
OPTS = [  # (label, prop fn, prop scale, book offset from the belly anchor, arm pose)
    ('NOW (v002)', old_book, 1.8, (0, -40), dict(armL=(70, -150), armR=(-70, -150), handL='grip', handR='grip')),
    ('A: paws under the corners', open_book, 1.25, (0, -70), dict(armL=(30, -60), armR=(-30, -60), handL='open', handR='open')),
    ('B: paws at the outer edges', open_book, 1.1, (0, -60), dict(armL=(-6, -120), armR=(6, -120), handL='grip', handR='grip')),
    ('C: B + toe tips on the prop', paw_tips, 1.1, (0, -60), dict(armL=(-6, -120), armR=(6, -120), handL='grip', handR='grip')),
]


def render(fn, sc, off, arms, raised, box, scale):
    st = Stage(2, bg=lambda c, cam, f: c.clear(skia.Color(*BEIGE))); st.grain = 0
    b = Bheemu(x=W / 2, y=GROUND, face=0.0); b.shadow = 0; bk = Prop(fn, z=5, sx=sc, sy=sc); st.add(b, bk)
    a = dict(arms)
    dy = -175 if raised else 0
    a['armL'] = (a['armL'][0], a['armL'][1] + dy); a['armR'] = (a['armR'][0], a['armR'][1] + dy)
    b.set(0, pupil=(0.0, 0.8), lid=0.25, smile=0.3, **a)
    bk.attach(0, 2, b, 'belly', off[0], off[1] + dy)
    st.still(0, '/tmp/_bk.png', scale)
    im = Image.open('/tmp/_bk.png').convert('RGB')
    return im.crop((int((W / 2 + box[0]) * scale), int((GROUND - box[3]) * scale), int((W / 2 + box[2]) * scale), int((GROUND - box[1]) * scale)))


if __name__ == '__main__':
    F = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf', 17); FB = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf', 22)
    cols = []
    for lab, fn, sc, off, arms in OPTS:
        cols.append((lab, render(fn, sc, off, arms, False, (-230, 120, 230, 640), 0.62), render(fn, sc, off, arms, True, (-230, 120, 230, 640), 0.62)))
    # D: a real grip from draw order. The book is drawn BEHIND Bheemu and held out to his side, so his own paw overlaps its edge
    def side(raised):
        st = Stage(2, bg=lambda c, cam, f: c.clear(skia.Color(*BEIGE))); st.grain = 0
        b = Bheemu(x=W / 2 - 150, y=GROUND, face=0.0, z=2); b.shadow = 0; bk = Prop(open_book, z=1, sx=1.15, sy=1.15); st.add(b, bk)
        b.set(0, armR=(120, -250 if raised else -200), handR='grip', bendR=0.25, yaw=0.55, pupil=(0.8, 0.3 if raised else 0.5), lid=0.2, smile=0.3)
        bk.attach(0, 2, b, 'handR', 112, -10)
        st.still(0, '/tmp/_bk.png', 0.62); im = Image.open('/tmp/_bk.png').convert('RGB')
        return im.crop((int((W / 2 - 340) * 0.62), int((GROUND - 640) * 0.62), int((W / 2 + 300) * 0.62), int((GROUND - 120) * 0.62)))
    dA, dR = side(False), side(True)
    # closed book in one hand
    st = Stage(2, bg=lambda c, cam, f: c.clear(skia.Color(*BEIGE))); st.grain = 0
    b = Bheemu(x=W / 2, y=GROUND, face=0.0); b.shadow = 0; bk = Prop(closed_book, z=5, rot=8); st.add(b, bk); bk.attach(0, 2, b, 'handL', 0, 40)
    st.still(0, '/tmp/_bk.png', 0.62); im = Image.open('/tmp/_bk.png').convert('RGB')
    closed = im.crop((int((W / 2 - 230) * 0.62), int((GROUND - 640) * 0.62), int((W / 2 + 230) * 0.62), int((GROUND + 20) * 0.62)))
    w, h = cols[0][1].size
    sheet = Image.new('RGB', (w * 4 + 60 + dA.size[0] + closed.size[0] + 20, h * 2 + 150), (252, 250, 244)); d = ImageDraw.Draw(sheet)
    d.rectangle((0, 0, sheet.size[0], 44), fill=(170, 30, 40)); d.text((14, 9), 'REVIEW ONLY / PROPOSAL  -  book prop and holding options. Not in any animatic. Approved Bheemu model unchanged.', font=FB, fill=(255, 255, 255))
    for i, (lab, a, r) in enumerate(cols):
        x = 10 + i * (w + 10)
        sheet.paste(a, (x, 54)); sheet.paste(r, (x, 54 + h + 40))
        d.text((x + 4, 56 + h), lab, font=F, fill=(40, 30, 30)); d.text((x + 4, 56 + h * 2 + 40), 'the same, raised to block Gaju', font=F, fill=(40, 30, 30))
    x = 10 + 4 * (w + 10)
    sheet.paste(dA, (x, 54)); sheet.paste(dR, (x, 54 + h + 40))
    d.text((x + 4, 56 + h), 'D: held to the side; his own paw in front', font=F, fill=(40, 30, 30)); d.text((x + 4, 56 + h * 2 + 40), 'D raised: a screen between him and Gaju', font=F, fill=(40, 30, 30))
    x += dA.size[0] + 10
    sheet.paste(closed, (x, 54)); d.text((x + 4, 58 + closed.size[1]), 'Closed book, carried in one paw', font=F, fill=(40, 30, 30))
    out = os.path.join(HERE, '..', '..', '..', '..', 'cartoon-animation-director', 'proposals', 'book_prop_options.png')
    sheet.save(out); print('wrote', os.path.normpath(out))
