"""REVIEW ONLY. Helpers that render tiles and lay them out as clearly marked review sheets."""
import os
import sys
import textwrap
import skia
from PIL import Image, ImageDraw, ImageFont
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', '..', '..', 'toon-slapstick', 'engine'))
from toon import Stage, W, GROUND                                                    # noqa: E402

BEIGE = (240, 232, 214); PAPER = (252, 250, 244); INK = (58, 42, 40)
RED = (176, 32, 40); GREEN = (30, 120, 70); ORANGE = (200, 100, 20)
_B = '/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'; _R = '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'
FB = ImageFont.truetype(_B, 26); F = ImageFont.truetype(_R, 19); FT = ImageFont.truetype(_B, 17); FS = ImageFont.truetype(_R, 16)
TMP = os.path.join(HERE, '_tmp.png')
BANNER = 'REVIEW ONLY  ·  PROPOSAL  ·  NOT AN APPROVED PRODUCTION ASSET  ·  Stage 1  ·  2026-11-11'


def tile(actors, box, scale=0.6, bg=BEIGE, frame=2):
    """Render actors on a flat background and crop. box = (x0, y0, x1, y1) in world units
    relative to (W/2, GROUND): x right, y up. Returns a PIL image."""
    st = Stage(8, bg=lambda c, cam, f: c.clear(skia.Color(*bg))); st.grain = 0
    for a in actors:
        st.add(a)
    st.still(frame, TMP, scale)
    im = Image.open(TMP).convert('RGB')
    x0, y0, x1, y1 = box
    return im.crop((int((W / 2 + x0) * scale), int((GROUND - y1) * scale), int((W / 2 + x1) * scale), int((GROUND - y0) * scale)))


def place(cls, dx=0, dy=0, shadow=False, **pose):
    """An actor of class cls standing at the sheet origin (plus an offset), with a pose set at frame 0."""
    a = cls(x=W / 2 + dx, y=GROUND - dy, face=pose.pop('face', 0.0))
    if not shadow:
        a.shadow = 0
    a.twos = False; a.smear = False
    if pose:
        a.set(0, **pose)
    return a


def sheet(path, title, rows, note=None, guide=None):
    """rows: list of rows; each row is a list of (image, label, kind) with kind 'prod', 'prop' or 'info'.
    guide: optional list of (row_index, y_fraction, text) horizontal guide lines across a row."""
    pad = 14
    widths = [sum(im.size[0] for im, _, _ in r) + pad * (len(r) + 1) for r in rows]
    Wd = max(max(widths), 1180)
    LAB = 72
    heights = [max(im.size[1] for im, _, _ in r) + LAB for r in rows]
    if note:
        note = '\n'.join('\n'.join(textwrap.wrap(par, int((Wd - 28) / 10.6))) for par in note.split('\n'))
    Hd = 142 + sum(heights) + (44 + 25 * note.count('\n') if note else 0) + 20
    out = Image.new('RGB', (Wd, Hd), PAPER); d = ImageDraw.Draw(out)
    d.rectangle((0, 0, Wd, 40), fill=RED); d.text((14, 9), BANNER, font=FT, fill=(255, 255, 255))
    d.text((14, 52), title, font=FB, fill=INK)
    d.rectangle((14, 90, 30, 106), fill=GREEN); d.text((36, 88), 'PRODUCTION: the approved model as it is today, unchanged', font=FS, fill=INK)
    d.rectangle((14, 114, 30, 130), fill=ORANGE); d.text((36, 112), 'PROPOSAL: new drawing for review; exists only in the review folder', font=FS, fill=INK)
    y = 142
    for ri, r in enumerate(rows):
        x = pad
        hmax = heights[ri] - LAB
        for im, label, kind in r:
            col = {'prod': GREEN, 'prop': ORANGE, 'info': (110, 110, 120)}[kind]
            out.paste(im, (x, y + hmax - im.size[1]))
            d.rectangle((x, y, x + im.size[0] - 1, y + hmax - 1), outline=col, width=3)
            d.rectangle((x, y + hmax, x + im.size[0] - 1, y + hmax + 6), fill=col)
            lines = [w for part in label.split('\n') for w in (textwrap.wrap(part, max(12, int(im.size[0] / 8.4))) or [''])]
            for li, line in enumerate(lines[:3]):
                d.text((x + 4, y + hmax + 9 + li * 19), line, font=FS, fill=INK)
            tag = {'prop': 'PROPOSAL', 'prod': 'PRODUCTION'}.get(kind)     # mark every tile itself
            if tag:
                tw = d.textlength(tag, font=FS)
                d.rectangle((x + 3, y + 3, x + tw + 13, y + 25), fill=PAPER)
                d.text((x + 8, y + 5), tag, font=FS, fill=col)
            x += im.size[0] + pad
        if guide:
            for gr, fy, text in guide:
                if gr == ri:
                    yy = y + int(hmax * fy)
                    for xx in range(pad, x - pad, 14):
                        d.line((xx, yy, xx + 7, yy), fill=(120, 60, 140), width=1)
                    d.text((x - pad - 6 - d.textlength(text, font=FS), yy - 18), text, font=FS, fill=(120, 60, 140))
        y += heights[ri]
    if note:
        d.multiline_text((14, y + 6), note, font=F, fill=INK, spacing=4)
    out.save(path)
    if os.path.exists(TMP):
        os.remove(TMP)
    return path
