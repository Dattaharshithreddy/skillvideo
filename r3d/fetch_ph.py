# Poly Haven CC0 textures + HDRI for the temple scene
import json, urllib.request, os, sys
UA = {'User-Agent': 'r3d-scene/1.0'}
def get(u): return json.load(urllib.request.urlopen(urllib.request.Request(u, headers=UA), timeout=60))
OUT = '/opt/r3d/assets/ph'; os.makedirs(OUT, exist_ok=True)
tex = get('https://api.polyhaven.com/assets?t=textures')
want = {'ground': ['granite_tile', 'stone_tiles', 'paving_stones', 'cobblestone_floor', 'square_tiles'],
        'stone': ['granite', 'rock_wall', 'stone_wall', 'castle_wall', 'sandstone'],
        'plaster': ['plaster', 'painted_plaster', 'white_plaster', 'concrete_wall'],
        'wood': ['wood_planks', 'old_planks', 'weathered_planks']}
pick = {}
for role, keys in want.items():
    for k in keys:
        c = sorted(i for i in tex if k in i)
        if c: pick[role] = c[0]; break
hdr = get('https://api.polyhaven.com/assets?t=hdris&c=outdoor')
for k in ['kiara_1_dawn', 'golden_bay', 'spruit_sunrise', 'kloofendal_43d_clear', 'sunflowers']:
    if k in hdr: pick['hdri'] = k; break
else: pick['hdri'] = sorted(hdr)[0]
pick = {'ground': 'precast_stone_paving', 'stone': 'white_sandstone_blocks_02', 'plaster': 'white_stucco', 'wood': 'oak_wood_planks', 'hdri': 'qwantani_late_afternoon_puresky'}
import shutil; [os.remove(os.path.join(OUT, f)) for f in os.listdir(OUT)]
print('PICK', pick)
def dl(u, p):
    if not os.path.exists(p): urllib.request.urlretrieve(u, p) if False else open(p, 'wb').write(urllib.request.urlopen(urllib.request.Request(u, headers=UA), timeout=120).read())
for role, aid in pick.items():
    f = get('https://api.polyhaven.com/files/' + aid)
    if role == 'hdri':
        u = f['hdri']['2k']['hdr']['url']; dl(u, f'{OUT}/sky.hdr'); continue
    for mapk, name in (('Diffuse', 'diff'), ('nor_gl', 'nor'), ('Rough', 'rough'), ('AO', 'ao')):
        m = f.get(mapk) or f.get(mapk.lower())
        if m: dl(m['2k']['jpg']['url'], f'{OUT}/{role}_{name}.jpg')
json.dump(pick, open(f'{OUT}/pick.json', 'w')); print(sorted(os.listdir(OUT)))
