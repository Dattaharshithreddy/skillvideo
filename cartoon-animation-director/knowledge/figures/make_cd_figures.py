"""Builds the figures and prints the measurement tables used in Character_Design_Bible.md.
Run: python3 make_cd_figures.py            figures + tables (writes model_baseline.json if missing)
     python3 make_cd_figures.py baseline   rewrite the baseline after an APPROVED design change
     python3 make_cd_figures.py check      re-measure and compare with the baseline; exit 1 on drift
(needs skia-python, Pillow, numpy and the toon-slapstick engine next door)

Everything here is measured from the engine's own drawings, so the numbers in the document
match what is actually on screen."""
import os, sys
import numpy as np
import skia
from PIL import Image, ImageDraw, ImageFont
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', '..', '..', 'toon-slapstick', 'engine'))
from toon import Stage, W, H, GROUND
from chars import Bheemu, Gaju
from cast import Ammamma, Chintu, Laddu, Bujji
import show

PAPER = (252, 250, 244); BEIGE = (240, 232, 214); KEY = (255, 0, 255); INK = (58, 42, 40); RED = (150, 30, 40)
FB = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf', 26)
F = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf', 20)
FS = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf', 16)
SC = 0.5                                     # render scale: 1 engine unit = 0.5 px
TMP = os.path.join(HERE, '_t.png')

# name: (class, skull top above the feet, skull height, head centre above the feet), in engine units.
# Read from the head outline and the head transform in chars.py / cast.py (animals include their S scale).
CAST = [
    ('Bheemu', Bheemu, 578.0, 208.0, 472.0),
    ('Ammamma', Ammamma, 546.0, 142.0, 476.0),
    ('Chintu', Chintu, 374.0, 135.0, 306.0),
    ('Gaju', Gaju, 232.0, 134.0, 164.0),
    ('Laddu', Laddu, 258.0 * 0.86, 132.0 * 0.86, 196.0 * 0.86),
    ('Bujji', Bujji, 222.0 * 0.92, 107.0 * 0.92, 172.0 * 0.92),
]


def render(cls, bg=BEIGE, shadow=False, **pose):
    """One still of one character standing at the centre. Returns (RGB image at SC, stage, actor)."""
    st = Stage(4, bg=lambda c, cam, f: c.clear(skia.Color(*bg))); st.grain = 0
    a = cls(x=W / 2, y=GROUND, face=0.0)
    if not shadow:
        a.shadow = 0
    st.add(a)
    if pose:
        a.set(0, **pose)
    st.still(2, TMP, SC)
    return Image.open(TMP).convert('RGB'), st, a


def mask_of(cls, **pose):
    im, _, _ = render(cls, bg=KEY, **pose)
    a = np.asarray(im).astype(int)
    return (np.abs(a - np.array(KEY)).sum(axis=2) > 60)


def bbox(m):
    ys, xs = np.where(m)
    return xs.min(), ys.min(), xs.max(), ys.max()


def crop_box(cx=W / 2, top=720, bottom=40, half=330):
    return (int((cx - half) * SC), int((GROUND - top) * SC), int((cx + half) * SC), int((GROUND + bottom) * SC))


# ------------------------------------------------------------------ figure 1: line-up with head units
print('SIZE TABLE (engine units; 1 unit = 1 px at 1080x1920)')
print('name | total height | width | skull height | heads tall (to top of skull) | heads tall (to top of everything) | % of Bheemu')
BOX = crop_box()
cw, ch = BOX[2] - BOX[0], BOX[3] - BOX[1]
out = Image.new('RGB', (cw * 6, ch * 2 + 150), PAPER); d = ImageDraw.Draw(out)
d.text((20, 14), 'Size comparison: all six at the same scale. Red ticks are each character\'s own head height.', font=FB, fill=INK)
gy = 60 + int(720 * SC)                                         # ground line in the figure
sizes = {}
MEAS = {}
MASKS = {}
for i, (name, cls, top, hh, hc) in enumerate(CAST):
    im, _, _ = render(cls, shadow=True)
    m = mask_of(cls)
    x0, y0, x1, y1 = bbox(m)
    tot = (GROUND * SC - y0) / SC; wid = (x1 - x0) / SC
    sizes[name] = (tot, wid, hh, top / hh, tot / hh)
    MEAS[name] = {'height': round(tot, 1), 'width': round(wid, 1), 'heads': round(top / hh, 3), 'colours': {}}
    MASKS[name] = m[y0:y1 + 1, x0:x1 + 1]
    out.paste(im.crop(BOX), (i * cw, 60))
    sil = Image.fromarray(np.where(m[..., None], np.uint8(30), np.uint8(BEIGE)).astype(np.uint8)).crop(BOX)
    out.paste(sil, (i * cw, 60 + ch + 40))
    for row in (0, 1):                                           # head-unit ruler
        base = gy + row * (ch + 40); x = i * cw + 22
        d.line((x, base, x, base - top * SC), fill=RED, width=3)
        k = 0
        while k * hh <= top + 1:
            d.line((x - 8, base - k * hh * SC, x + 8, base - k * hh * SC), fill=RED, width=3); k += 1
        d.line((x - 8, base - top * SC, x + 14, base - top * SC), fill=RED, width=3)
    d.text((i * cw + 40, 60 + ch + 6), '%s  %.1f heads' % (name, top / hh), font=F, fill=RED)
    d.text((i * cw + 40, 60 + ch * 2 + 46), '%d tall, %d wide' % (tot, wid), font=F, fill=INK)
for name, cls, top, hh, hc in CAST:
    tot, wid, hh, hd, hd2 = sizes[name]
    print('%-8s | %4.0f | %4.0f | %4.0f | %.2f | %.2f | %3.0f%%' % (name, tot, wid, hh, hd, hd2, 100 * tot / sizes['Bheemu'][0]))
d.line((0, gy, cw * 6, gy), fill=INK, width=2); d.line((0, gy + ch + 40, cw * 6, gy + ch + 40), fill=INK, width=2)
out.save(os.path.join(HERE, 'CD_fig1_lineup.png'))

# ------------------------------------------------------------------ figure 2: which views exist
VIEWS = [(-1.0, 'face -1'), (-0.5, 'face -0.5'), (0.0, 'face 0 (front)'), (0.5, 'face 0.5'), (1.0, 'face 1')]
VB = crop_box(top=700, half=300); vw, vh = VB[2] - VB[0], VB[3] - VB[1]
out = Image.new('RGB', (vw * 5 + 150, (vh + 6) * 6 + 70), PAPER); d = ImageDraw.Draw(out)
d.text((20, 14), 'View audit: what the body-turn control draws today. There is no back view for anyone.', font=FB, fill=INK)
for r, (name, cls, top, hh, hc) in enumerate(CAST):
    d.text((10, 70 + r * (vh + 6) + vh // 2), name, font=F, fill=INK)
    for c, (fv, lab) in enumerate(VIEWS):
        im, _, _ = render(cls, shadow=True, face=fv)
        out.paste(im.crop(VB), (150 + c * vw, 60 + r * (vh + 6)))
        if r == 0:
            d.text((150 + c * vw + 10, 62), lab, font=FS, fill=RED)
out.save(os.path.join(HERE, 'CD_fig2_views.png'))

# ------------------------------------------------------------------ figure 3: expression sheet
EXPR = [('CALM', show.CALM), ('HAPPY', show.HAPPY), ('LAUGH', show.LAUGH), ('ANGRY', show.ANGRY),
        ('SHOCK', show.SHOCK), ('SORRY', show.SORRY), ('SLY', show.SLY), ('SLEEP', show.SLEEP)]
T = 190
out = Image.new('RGB', (T * 8 + 150, (T + 6) * 6 + 90), PAPER); d = ImageDraw.Draw(out)
d.text((20, 14), 'Expression sheet: the eight presets on all six characters (heads only, each scaled to fit).', font=FB, fill=INK)
for c, (lab, _) in enumerate(EXPR):
    d.text((150 + c * T + 10, 58), lab, font=F, fill=RED)
for r, (name, cls, top, hh, hc) in enumerate(CAST):
    d.text((10, 90 + r * (T + 6) + T // 2), name, font=F, fill=INK)
    for c, (lab, pose) in enumerate(EXPR):
        im, _, _ = render(cls, **pose)
        half = hh * (1.05 if name not in ('Bujji', 'Gaju') else 1.25)
        cy = GROUND - hc - (hh * 0.35 if name == 'Bujji' else 0)
        box = (int((W / 2 - half) * SC), int((cy - half) * SC), int((W / 2 + half) * SC), int((cy + half) * SC))
        out.paste(im.crop(box).resize((T, T), Image.LANCZOS), (150 + c * T, 86 + r * (T + 6)))
out.save(os.path.join(HERE, 'CD_fig3_expressions.png'))

# ------------------------------------------------------------------ figure 6: eight PROPOSED expressions (not in show.py)
PROPOSED = [
    ('SAD', dict(happy=0.0, eye_open=1.0, lid=0.35, brow_ang=-22, brow=2, smile=-0.7, mouth_w=0.8, mouth_open=0.0, pupil=(0.0, 0.5), head_rot=-6)),
    ('FEAR', dict(happy=0.0, eye_open=1.0, eye_pop=1.35, pupil_s=0.5, brow=14, brow_ang=-16, mouth_open=0.45, mouth_w=1.25, smile=-0.6, sweat=1.0)),
    ('BORED', dict(happy=0.0, eye_open=1.0, lid=0.55, smile=-0.15, mouth_w=0.9, pupil=(0.6, 0.1), head_rot=8)),
    ('DETERMINED', dict(happy=0.0, eye_open=1.0, lid=0.2, brow_ang=14, brow=-2, smile=0.25, mouth_w=0.7)),
    ('GREEDY', dict(happy=0.0, eye_open=1.0, eye_pop=1.25, pupil_s=1.35, brow=10, smile=1.0, mouth_w=1.2, mouth_open=0.35, cheeks=1.0)),
    ('CONFUSED', dict(happy=0.0, eye_open=1.0, brow_asym=1.0, smile=-0.25, mouth_w=0.6, pupil=(-0.5, -0.4), head_rot=-10)),
    ('DIZZY', dict(happy=0.0, eye_open=1.0, lid=0.45, pupil_s=0.6, pupil=(0.5, 0.3), brow_ang=-10, smile=-0.1, mouth_open=0.3, mouth_w=0.7, head_rot=12)),
    ('PROUD', dict(happy=0.0, eye_open=0.0, brow=8, smile=0.6, mouth_w=0.8, pitch=-0.4, head_rot=-4)),
]
EXTRA = {   # species parts that act as extra eyebrows
    'Gaju': {'SAD': dict(ear=-0.8), 'FEAR': dict(ear=1.0), 'BORED': dict(ear=-0.4), 'GREEDY': dict(ear=0.8), 'PROUD': dict(ear=0.5)},
    'Bujji': {'SAD': dict(ear=-1.0), 'FEAR': dict(ear=1.0), 'BORED': dict(ear=-0.5), 'DIZZY': dict(ear=-0.8), 'CONFUSED': dict(ear=0.0)},
    'Laddu': {'FEAR': dict(ear_back=1.0), 'DETERMINED': dict(ear_back=0.6), 'SAD': dict(ear_back=0.5)},
}
out = Image.new('RGB', (T * 8 + 150, (T + 6) * 6 + 90), PAPER); d = ImageDraw.Draw(out)
d.text((20, 14), 'PROPOSED expressions (test renders only; not added to the engine presets).', font=FB, fill=INK)
for c, (lab, _) in enumerate(PROPOSED):
    d.text((150 + c * T + 10, 58), lab, font=F, fill=RED)
for r, (name, cls, top, hh, hc) in enumerate(CAST):
    d.text((10, 90 + r * (T + 6) + T // 2), name, font=F, fill=INK)
    for c, (lab, pose) in enumerate(PROPOSED):
        im, _, _ = render(cls, **dict(pose, **EXTRA.get(name, {}).get(lab, {})))
        half = hh * (1.05 if name not in ('Bujji', 'Gaju') else 1.25)
        cy = GROUND - hc - (hh * 0.35 if name == 'Bujji' else 0)
        box = (int((W / 2 - half) * SC), int((cy - half) * SC), int((W / 2 + half) * SC), int((cy + half) * SC))
        out.paste(im.crop(box).resize((T, T), Image.LANCZOS), (150 + c * T, 86 + r * (T + 6)))
out.save(os.path.join(HERE, 'CD_fig6_proposed_expressions.png'))

# ------------------------------------------------------------------ figure 4: colour and value
print('\nCOLOUR TABLE: share of each character\'s visible area taken by each named colour, and its value (0 black to 100 white)')


def value(c):
    return (0.2126 * c[0] + 0.7152 * c[1] + 0.0722 * c[2]) / 2.55


SW = 250
out = Image.new('RGB', (SW * 6, 620), PAPER); d = ImageDraw.Draw(out)
d.text((20, 14), 'Colour model: named colours by share of visible area; below, colour removed.', font=FB, fill=INK)
for i, (name, cls, top, hh, hc) in enumerate(CAST):
    im, _, _ = render(cls)
    m = mask_of(cls)
    px = np.asarray(im)[m].astype(int)
    named = {k: v for k, v in vars(cls).items() if k.isupper() and isinstance(v, tuple) and len(v) == 3 and k != 'STREAK'}
    named.setdefault('INK', cls.INK)
    keys = list(named); cols = np.array([named[k] for k in keys])
    near = np.argmin(((px[:, None, :] - cols[None, :, :]) ** 2).sum(axis=2), axis=1)
    dist = np.sqrt(((px - cols[near]) ** 2).sum(axis=1))
    share = [(100.0 * np.sum((near == j) & (dist < 40)) / len(px), keys[j]) for j in range(len(keys))]
    other = 100.0 - sum(s for s, _ in share)
    share.sort(reverse=True)
    d.text((i * SW + 12, 56), name, font=FB, fill=INK)
    y = 96
    print(name + ': ' + ', '.join('%s %d%% (v%d)' % (k, round(s), value(named[k])) for s, k in share if s >= 1) + ', unnamed/blended %d%%' % round(other))
    MEAS[name]['colours'] = {k: round(s, 1) for s, k in share if s >= 1}
    for s, k in share[:7]:
        if s < 1:
            continue
        col = named[k]
        d.rectangle((i * SW + 12, y, i * SW + 62, y + 34), fill=col, outline=INK)
        d.text((i * SW + 70, y - 2), '%s %d%%' % (k, round(s)), font=FS, fill=INK)
        d.text((i * SW + 70, y + 16), '#%02X%02X%02X  v%d' % (col + (value(col),)), font=FS, fill=INK)
        y += 44
    g = im.convert('L').convert('RGB').crop(crop_box(top=640, half=250))
    out.paste(g.resize((int(200 * 500 / 680), 200), Image.LANCZOS), (i * SW + 30, 410))
out.save(os.path.join(HERE, 'CD_fig4_colour.png'))

# ------------------------------------------------------------------ figure 5: hands
KINDS = ['mitt', 'open', 'fist', 'grip', 'point']
HT = 200
rows = [('Ammamma', Ammamma, 150), ('Chintu', Chintu, 120), ('Bheemu', Bheemu, 170)]
out = Image.new('RGB', (HT * 5 + 150, (HT + 6) * 3 + 90), PAPER); d = ImageDraw.Draw(out)
d.text((20, 14), 'Hand model sheet: the five hand shapes, from real renders.', font=FB, fill=INK)
for c, k in enumerate(KINDS):
    d.text((150 + c * HT + 10, 58), k, font=F, fill=RED)
for r, (name, cls, half) in enumerate(rows):
    d.text((10, 90 + r * (HT + 6) + HT // 2), name, font=F, fill=INK)
    for c, k in enumerate(KINDS):
        st = Stage(4, bg=lambda cv, cam, f: cv.clear(skia.Color(*BEIGE))); st.grain = 0
        a = cls(x=W / 2, y=GROUND, face=0.0); a.shadow = 0; st.add(a)
        a.set(0, handR=k, armR=(150.0, -150.0))
        hx, hy = st.probe(2, a, 'handR')
        st.still(2, TMP, 1.0)
        im = Image.open(TMP).convert('RGB')
        out.paste(im.crop((int(hx - half), int(hy - half), int(hx + half), int(hy + half))).resize((HT, HT), Image.LANCZOS), (150 + c * HT, 86 + r * (HT + 6)))
out.save(os.path.join(HERE, 'CD_fig5_hands.png'))
if os.path.exists(TMP):
    os.remove(TMP)
print('\nfigures written')

# ------------------------------------------------------------------ silhouette distinctness
def norm(m, n=96):
    """Scale a silhouette to n px tall, centre it in an n x 2n box, so shapes can be overlaid."""
    im = Image.fromarray((m * 255).astype(np.uint8))
    w = max(1, int(round(m.shape[1] * n / m.shape[0])))
    im = im.resize((min(w, 2 * n), n), Image.NEAREST)
    box = Image.new('L', (2 * n, n), 0); box.paste(im, ((2 * n - im.size[0]) // 2, 0))
    return np.asarray(box) > 127


print('\nSILHOUETTE OVERLAP (same height, centred; 0% = nothing in common, 100% = identical shape)')
names = [c[0] for c in CAST]; N = {k: norm(MASKS[k]) for k in names}
print('         ' + ' '.join('%8s' % k for k in names))
worst = (0, '', '')
for a in names:
    row = []
    for b in names:
        iou = 100.0 * (N[a] & N[b]).sum() / (N[a] | N[b]).sum()
        row.append('%7.0f%%' % iou)
        if a < b and iou > worst[0]:
            worst = (iou, a, b)
    print('%-8s ' % a + ' '.join(row))
print('most alike pair: %s and %s at %.0f%%' % (worst[1], worst[2], worst[0]))

# ------------------------------------------------------------------ value against the sets
import sets
print('\nVALUE AGAINST BACKGROUNDS (main body colour value minus background value; under 15 either way is a merge risk)')
BGS = {'SKY': sets.SKY, 'EARTH': sets.EARTH, 'NIGHT': sets.NIGHT}
print('background values: ' + ', '.join('%s v%d' % (k, value(v)) for k, v in BGS.items()))
MAIN = {'Bheemu': Bheemu.WHITE, 'Ammamma': Ammamma.SAREE, 'Chintu': Chintu.SKIN, 'Gaju': Gaju.SKIN, 'Laddu': Laddu.FUR, 'Bujji': Bujji.FUR}
for k in names:
    print('%-8s v%d: ' % (k, value(MAIN[k])) + ', '.join('%s %+d' % (b, value(MAIN[k]) - value(v)) for b, v in BGS.items()))

# ------------------------------------------------------------------ baseline and drift check
import json
BASE = os.path.join(HERE, '..', 'model_baseline.json')
if len(sys.argv) > 1 and sys.argv[1] == 'check':
    base = json.load(open(BASE)); bad = 0
    print('\nMODEL DRIFT CHECK against model_baseline.json (size within 2%, colour share within 3 points)')
    for k in names:
        b, m, why = base[k], MEAS[k], []
        for key in ('height', 'width', 'heads'):
            if abs(m[key] - b[key]) > 0.02 * b[key]:
                why.append('%s %s -> %s' % (key, b[key], m[key]))
        for c in set(b['colours']) | set(m['colours']):
            if abs(m['colours'].get(c, 0) - b['colours'].get(c, 0)) > 3:
                why.append('%s %s%% -> %s%%' % (c, b['colours'].get(c, 0), m['colours'].get(c, 0)))
        print('%-8s %s' % (k, 'PASS' if not why else 'FAIL: ' + '; '.join(why))); bad += bool(why)
    sys.exit(1 if bad else 0)
elif len(sys.argv) > 1 and sys.argv[1] == 'baseline' or not os.path.exists(BASE):
    json.dump(MEAS, open(BASE, 'w'), indent=1); print('\nbaseline written: model_baseline.json')
