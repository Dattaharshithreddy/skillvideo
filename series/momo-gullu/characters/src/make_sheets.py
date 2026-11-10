"""Composite rendered cells into the final character sheets (run with the cgi-venv python).

    python make_sheets.py [CELLS_DIR] [OUT_DIR]
"""
import os, sys, glob
from PIL import Image, ImageDraw, ImageFont

CELLS = os.path.abspath(sys.argv[1]) if len(sys.argv) > 1 else os.path.expanduser("~/momo-gullu/renders/.cells")
OUT = os.path.abspath(sys.argv[2]) if len(sys.argv) > 2 else os.path.expanduser("~/momo-gullu/renders")
os.makedirs(OUT, exist_ok=True)

GAP, MARGIN, TITLE_H, LABEL_H = 22, 44, 96, 50
INK = (62, 66, 74)


def font(size, bold=True):
    pats = ["/usr/share/fonts/dejavu-sans-fonts/DejaVuSans%s.ttf" % ("-Bold" if bold else ""),
            "/usr/share/fonts/**/DejaVuSans%s.ttf" % ("-Bold" if bold else "")]
    for p in pats:
        hits = glob.glob(p, recursive=True)
        if hits:
            return ImageFont.truetype(hits[0], size)
    return ImageFont.load_default()


def sheet(out_name, title, rows):
    """rows: list of (row_label_or_None, [(cell_file, label), ...])"""
    imgs = [[(Image.open(os.path.join(CELLS, f)), lab) for f, lab in row] for _, row in rows]
    cw, ch = imgs[0][0][0].size
    ncols = max(len(r) for r in imgs)
    W = 2 * MARGIN + ncols * cw + (ncols - 1) * GAP
    H = TITLE_H + MARGIN + len(imgs) * (ch + LABEL_H + GAP)
    bg = imgs[0][0][0].getpixel((8, 8))[:3]
    canvas = Image.new("RGB", (W, H), bg)
    d = ImageDraw.Draw(canvas)
    d.text((MARGIN, 30), title, font=font(44), fill=INK)
    y = TITLE_H + MARGIN // 2
    for (row_label, _), row_imgs in zip(rows, imgs):
        rw = len(row_imgs) * cw + (len(row_imgs) - 1) * GAP
        x = (W - rw) // 2
        for im, lab in row_imgs:
            canvas.paste(im.convert("RGB"), (x, y))
            if lab:
                bb = d.textbbox((0, 0), lab, font=font(26, bold=False))
                d.text((x + (cw - bb[2]) // 2, y + ch + 10), lab, font=font(26, bold=False), fill=INK)
            x += cw + GAP
        if row_label:
            d.text((MARGIN, y - 2), row_label, font=font(24), fill=INK)
        y += ch + LABEL_H + GAP
    canvas.save(os.path.join(OUT, out_name))
    print("wrote", out_name, canvas.size)


TURN = [("front", "front"), ("side_r", "90°"), ("back", "180°"), ("side_l", "270°")]
EXPR = ["neutral", "happy", "laugh", "surprised", "sleepy", "angry", "sad", "cheeky"]
HANDS = [("open", "open"), ("relax", "relaxed"), ("point", "point"), ("fist", "fist")]

for who, nice in (("momo", "MOMO — turnaround"), ("gullu", "GULLU — turnaround")):
    sheet(f"{who}_turnaround.png", nice,
          [(None, [(f"{who}_turn_{k}.png", lab) for k, lab in TURN])])

sheet("momo_expressions.png", "MOMO — expressions & hands",
      [(None, [(f"momo_expr_{e}.png", e) for e in EXPR[:4]]),
       (None, [(f"momo_expr_{e}.png", e) for e in EXPR[4:]]),
       ("hand poses", [(f"momo_hand_{k}.png", lab) for k, lab in HANDS])])

sheet("gullu_expressions.png", "GULLU — expressions",
      [(None, [(f"gullu_expr_{e}.png", e) for e in EXPR[:4]]),
       (None, [(f"gullu_expr_{e}.png", e) for e in EXPR[4:]])])

lu = Image.open(os.path.join(CELLS, "lineup_raw.png")).convert("RGB")
d = ImageDraw.Draw(lu)
cap = "Momo 1.61 m  ·  Gullu 0.645 m  —  2.5×"
bb = d.textbbox((0, 0), cap, font=font(30, bold=False))
d.text((lu.width - bb[2] - 36, lu.height - 58), cap, font=font(30, bold=False), fill=INK)
lu.save(os.path.join(OUT, "lineup.png"))
print("wrote lineup.png", lu.size)
