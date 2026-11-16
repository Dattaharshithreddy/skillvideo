"""High-resolution colour for the terrain from Google Map Tiles API (2D satellite tiles, zoom 17, ~1.2 m/px),
re-projected onto the same UTM 44N box as geo/dem.npy. Writes geo/gm.jpg and geo/gm_credit.txt (attribution to show on screen).
The API key is read from AWS SSM (/reel/google_maps_key) and never printed."""
import io, json, math, os, subprocess, concurrent.futures as cf
import numpy as np, requests
from PIL import Image
from pyproj import Transformer
Image.MAX_IMAGE_PIXELS = None
K = subprocess.run(['aws', 'ssm', 'get-parameter', '--name', '/reel/google_maps_key', '--with-decryption', '--region', 'ap-south-1',
                    '--query', 'Parameter.Value', '--output', 'text'], capture_output=True, text=True).stdout.strip()
meta = json.load(open('geo/meta.json')); x0, y0, x1, y1 = meta['x0'], meta['y0'], meta['x1'], meta['y1']
to_ll = Transformer.from_crs('EPSG:32644', 'EPSG:4326', always_xy=True)
lons, lats = to_ll.transform([x0, x1, x0, x1], [y0, y0, y1, y1])
W_, E_, S_, N_ = min(lons), max(lons), min(lats), max(lats)
Z = int(os.environ.get('GZ', 17))
def tx(lon): return (lon + 180) / 360 * 2 ** Z
def ty(lat): r = math.radians(lat); return (1 - math.log(math.tan(r) + 1 / math.cos(r)) / math.pi) / 2 * 2 ** Z
X0, X1, Y0, Y1 = int(tx(W_)), int(tx(E_)), int(ty(N_)), int(ty(S_))
print('tiles', (X1 - X0 + 1) * (Y1 - Y0 + 1), 'zoom', Z, flush=True)
s = requests.post(f'https://tile.googleapis.com/v1/createSession?key={K}', json={'mapType': 'satellite', 'language': 'en-US', 'region': 'IN'}, timeout=60)
if s.status_code != 200: raise SystemExit(f'session HTTP {s.status_code}: {s.text[:200]}')
sess = s.json()['session']; T = s.json().get('tileWidth', 256)
v = requests.get('https://tile.googleapis.com/tile/v1/viewport', params={'session': sess, 'key': K, 'zoom': Z, 'north': N_, 'south': S_, 'east': E_, 'west': W_}, timeout=60)
credit = v.json().get('copyright', '') if v.status_code == 200 else ''
open('geo/gm_credit.txt', 'w').write('Imagery: Google' + (f', {credit}' if credit else '')); print('credit:', credit)
mos = np.zeros(((Y1 - Y0 + 1) * T, (X1 - X0 + 1) * T, 3), np.uint8)
S = requests.Session()
def fetch(xy):
    x, y = xy
    for _ in range(4):
        r = S.get(f'https://tile.googleapis.com/v1/2dtiles/{Z}/{x}/{y}', params={'session': sess, 'key': K}, timeout=60)
        if r.status_code == 200: return xy, np.asarray(Image.open(io.BytesIO(r.content)).convert('RGB').resize((T, T)))
    return xy, None
miss = 0
with cf.ThreadPoolExecutor(16) as ex:
    for (x, y), a in ex.map(fetch, [(x, y) for x in range(X0, X1 + 1) for y in range(Y0, Y1 + 1)]):
        if a is None: miss += 1; continue
        mos[(y - Y0) * T:(y - Y0 + 1) * T, (x - X0) * T:(x - X0 + 1) * T] = a
print('missing tiles', miss, flush=True)
# resample onto the UTM grid (row 0 = north edge, like s2.png / dem.npy)
RES = float(os.environ.get('GRES', 1.5)); w, h = int((x1 - x0) / RES), int((y1 - y0) / RES)
out = np.zeros((h, w, 3), np.uint8); xs = x0 + (np.arange(w) + 0.5) * RES
for r0 in range(0, h, 256):
    rows = np.arange(r0, min(h, r0 + 256)); ys = y1 - (rows + 0.5) * RES
    XX, YY = np.meshgrid(xs, ys); lo, la = to_ll.transform(XX, YY)
    px = (tx(lo) - X0) * T; py = ((1 - np.log(np.tan(np.radians(la)) + 1 / np.cos(np.radians(la))) / np.pi) / 2 * 2 ** Z - Y0) * T
    px = np.clip(px, 0, mos.shape[1] - 2); py = np.clip(py, 0, mos.shape[0] - 2); ix, iy = px.astype(int), py.astype(int); fx, fy = (px - ix)[..., None], (py - iy)[..., None]
    out[rows] = (mos[iy, ix] * (1 - fx) * (1 - fy) + mos[iy, ix + 1] * fx * (1 - fy) + mos[iy + 1, ix] * (1 - fx) * fy + mos[iy + 1, ix + 1] * fx * fy).astype(np.uint8)
Image.fromarray(out).save('geo/gm.jpg', quality=90)
print('gm.jpg', w, 'x', h, 'at', RES, 'm/px'); print('GM_DONE')
