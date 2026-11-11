#!/usr/bin/env python3
"""check_safe_area.py - READ-ONLY. Where do the characters stand on screen, against a chosen margin?

    python3 check_safe_area.py episode <episode.py> [--every 12] [--top 288 --bottom 672 --left 48 --right 192]
    python3 check_safe_area.py overlay <video.mp4> <out.png> [--times 3,9,15,21] [same margin options]

`episode` computes each visible character's screen box on sampled frames from the pose and the camera
(feet at x,y; top at y - HEIGHT*sy; half-width taken as HEIGHT*0.3) and reports how much of that box
lies inside each margin band. It is arithmetic, not a look at pixels.
`overlay` pulls frames from an existing rendered file and writes ONE new picture, to the path you give,
with the margin bands drawn over them, for a person to look at. Give a path outside the production folders.

The margins are NOT official figures. Sources disagree (Storyboard_and_Cinematography.md, 2.4). The
defaults are the most conservative set quoted. Only a look on a real phone settles it.
"""
import argparse, subprocess, sys
W, H = 1080, 1920


def box(a, cam, f):
    p = a.frame_pose(f)
    z, cx, cy = cam.value('zoom', f), cam.value('x', f), cam.value('y', f)
    sx = lambda x: W / 2 + (x - cx) * z
    sy = lambda y: H / 2 + (y - cy) * z
    half = a.HEIGHT * 0.3 * abs(p['sx'])
    return sx(p['x'] - half), sy(p['y'] - a.HEIGHT * p['sy']), sx(p['x'] + half), sy(p['y'])


def covered(b, top, bottom, left, right):
    x0, y0, x1, y1 = b
    h, w = max(1e-6, y1 - y0), max(1e-6, x1 - x0)
    over = lambda lo, hi, a, c: max(0.0, min(hi, c) - max(lo, a))
    return dict(top=over(y0, y1, 0, top) / h, bottom=over(y0, y1, H - bottom, H) / h, left=over(x0, x1, 0, left) / w, right=over(x0, x1, W - right, W) / w)


def episode(path, every, m, out=sys.stdout):
    from _load import load_stage, name_of
    st, ns = load_stage(path)
    chars = [a for a in st.actors if hasattr(a, 'HEIGHT')]
    worst = {}
    for f in range(0, st.frames, every):
        for a in chars:
            if a.value('show', f) < 0.5:
                continue
            b = box(a, st.cam, f)
            if b[2] < 0 or b[0] > W or b[3] < 0 or b[1] > H:
                continue
            c = covered(b, **m); nm = name_of(a, ns)
            w = worst.setdefault(nm, dict(n=0, top=0, bottom=0, left=0, right=0, feet=[], frame={}))
            w['n'] += 1; w['feet'].append(H - b[3])
            for k in ('top', 'bottom', 'left', 'right'):
                if c[k] > w[k]:
                    w[k] = c[k]; w['frame'][k] = f
    print('check_safe_area (read-only, arithmetic): %s' % path, file=out)
    print('margins used (px): top %(top)d, bottom %(bottom)d, left %(left)d, right %(right)d  -- NOT official figures' % m, file=out)
    print('| Character | Frames sampled | Feet above bottom edge, min-max (px) | Worst share of body in bottom band | in right band | in top band |', file=out)
    print('|---|---|---|---|---|---|', file=out)
    for nm, w in sorted(worst.items()):
        print('| %s | %d | %d-%d | %.0f%% (frame %s) | %.0f%% | %.0f%% |' % (nm, w['n'], min(w['feet']), max(w['feet']), 100 * w['bottom'], w['frame'].get('bottom', '-'), 100 * w['right'], 100 * w['top']), file=out)
    return worst


def overlay(video, out_png, times, m):
    from PIL import Image, ImageDraw
    import io
    tiles = []
    for t in times:
        raw = subprocess.run(['ffmpeg', '-v', 'error', '-ss', str(t), '-i', video, '-frames:v', '1', '-f', 'image2pipe', '-vcodec', 'png', '-'], capture_output=True, check=True).stdout
        im = Image.open(io.BytesIO(raw)).convert('RGBA').resize((W, H))
        ov = Image.new('RGBA', (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(ov)
        for r in ((0, 0, W, m['top']), (0, H - m['bottom'], W, H), (0, 0, m['left'], H), (W - m['right'], 0, W, H)):
            d.rectangle(r, fill=(220, 30, 40, 90))
        d.rectangle((m['left'], m['top'], W - m['right'], H - m['bottom']), outline=(30, 200, 60, 255), width=6)
        tiles.append(Image.alpha_composite(im, ov).convert('RGB').resize((W // 3, H // 3)))
    sheet = Image.new('RGB', (len(tiles) * (W // 3 + 8) + 8, H // 3 + 16), (250, 250, 246))
    for i, t in enumerate(tiles):
        sheet.paste(t, (8 + i * (W // 3 + 8), 8))
    sheet.save(out_png)
    print('wrote', out_png, '(red = quoted interface margins, unofficial; green = area left clear)')


if __name__ == '__main__':
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest='cmd', required=True)
    for name in ('episode', 'overlay'):
        s = sub.add_parser(name)
        s.add_argument('src')
        if name == 'overlay':
            s.add_argument('out'); s.add_argument('--times', default='3,9,15,21')
        else:
            s.add_argument('--every', type=int, default=12)
        s.add_argument('--top', type=int, default=288); s.add_argument('--bottom', type=int, default=672)
        s.add_argument('--left', type=int, default=48); s.add_argument('--right', type=int, default=192)
    a = ap.parse_args()
    m = dict(top=a.top, bottom=a.bottom, left=a.left, right=a.right)
    if a.cmd == 'episode':
        episode(a.src, a.every, m)
    else:
        overlay(a.src, a.out, [float(x) for x in a.times.split(',')], m)
