"""Download CC0 Poly Haven textures/HDRIs matching keywords (2k jpg) to OUT/<id>/. Prints the chosen ids."""
import json, os, sys, urllib.request
OUT = sys.argv[1]; want = json.loads(sys.argv[2])   # {"textures": ["granite", ...], "hdris": ["sunset", ...], "ids": [...]}
def get(u): return json.load(urllib.request.urlopen(urllib.request.Request(u, headers={'User-Agent': 'reel-assets/1.0'}), timeout=60))
def dl(u, p):
    os.makedirs(os.path.dirname(p), exist_ok=True); open(p, 'wb').write(urllib.request.urlopen(urllib.request.Request(u, headers={'User-Agent': 'reel-assets/1.0'}), timeout=120).read())
chosen = list(want.get('ids', []))
for kind, t in (('textures', 'textures'), ('hdris', 'hdris')):
    assets = get(f'https://api.polyhaven.com/assets?t={t}')
    for kw in want.get(kind, []):
        hits = sorted([k for k, v in assets.items() if kw in k or kw in ' '.join(v.get('tags', [])) or kw in ' '.join(v.get('categories', []))], key=lambda k: -assets[k].get('download_count', 0))[:3]
        print(kind, kw, '->', hits); chosen += [(kind, h) for h in hits]
for item in chosen:
    kind, aid = item if isinstance(item, (list, tuple)) else (('hdris' if item.startswith('hdri:') else 'textures'), item.split(':')[-1])
    f = get(f'https://api.polyhaven.com/files/{aid}')
    try:
        if kind == 'hdris': dl(f['hdri']['2k']['hdr']['url'], f'{OUT}/hdri/{aid}.hdr')
        else:
            for m in ('Diffuse', 'nor_gl', 'Rough', 'AO', 'arm'):
                if m in f and '2k' in f[m]: dl(f[m]['2k']['jpg']['url'], f'{OUT}/tex/{aid}/{m}.jpg')
        print('got', kind, aid)
    except Exception as e: print('fail', aid, e)
