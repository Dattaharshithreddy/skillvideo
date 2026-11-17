# Downloads Google Maps place photos listed in refs/maps.json into refs/maps/<key>/NN.jpg and builds contact sheets.
import json, os, sys, urllib.request
from PIL import Image, ImageDraw
D = os.path.dirname(os.path.abspath(__file__))
data = json.load(open(f'{D}/maps.json'))
for k, ids in data.items():
    od = f'{D}/maps/{k}'; os.makedirs(od, exist_ok=True)
    ok = []
    for i, p in enumerate(ids):
        fn = f'{od}/{i:02d}.jpg'
        if not os.path.exists(fn):
            try:
                req = urllib.request.Request(f'https://lh3.googleusercontent.com/{p}=w1600-h1200-k-no', headers={'User-Agent': 'Mozilla/5.0'})
                open(fn, 'wb').write(urllib.request.urlopen(req, timeout=30).read())
            except Exception as e:
                print(k, i, 'fail', e); continue
        ok.append(fn)
    # contact sheet 4 cols, 400x300 tiles, numbered
    cols = 4; rows = (len(ok) + cols - 1) // cols or 1
    sh = Image.new('RGB', (cols * 400, rows * 300), (20, 20, 20)); dr = ImageDraw.Draw(sh)
    for j, fn in enumerate(ok):
        try: im = Image.open(fn).convert('RGB'); im.thumbnail((400, 300))
        except Exception: continue
        x, y = (j % cols) * 400, (j // cols) * 300
        sh.paste(im, (x, y)); n = os.path.basename(fn)[:2]
        dr.rectangle([x, y, x + 46, y + 30], fill=(0, 0, 0)); dr.text((x + 8, y + 8), n, fill=(255, 220, 0))
    sh.save(f'{D}/maps/sheet_{k}.jpg', quality=82)
    print(k, len(ok))
print('MAPS_DONE')
