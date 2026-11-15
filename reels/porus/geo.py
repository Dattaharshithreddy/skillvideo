"""Jhelum (Hydaspes) valley near Jalalpur: Copernicus DEM, Sentinel-2 colour, OSM river centreline. UTM 43N metres."""
import json, math, os
import numpy as np, requests, rasterio
from rasterio.warp import reproject, Resampling, transform_bounds
from rasterio.transform import from_origin
from pyproj import Transformer
from PIL import Image
os.makedirs('geo', exist_ok=True)
W_, S_, E_, N_ = 73.28, 32.55, 73.50, 32.71
UTM = 'EPSG:32643'
tf = Transformer.from_crs('EPSG:4326', UTM, always_xy=True)
x0, y0, x1, y1 = transform_bounds('EPSG:4326', UTM, W_, S_, E_, N_)
RES = 25.0; w, h = int((x1 - x0) / RES), int((y1 - y0) / RES)
if not os.path.exists('geo/dem.npy'):
    DEM = 'https://copernicus-dem-30m.s3.amazonaws.com/Copernicus_DSM_COG_10_N32_00_E073_00_DEM/Copernicus_DSM_COG_10_N32_00_E073_00_DEM.tif'
    with rasterio.Env(GDAL_DISABLE_READDIR_ON_OPEN='EMPTY_DIR', AWS_NO_SIGN_REQUEST='YES'):
        with rasterio.open(DEM) as src:
            dem = np.zeros((h, w), np.float32)
            reproject(rasterio.band(src, 1), dem, dst_transform=from_origin(x0, y1, RES, RES), dst_crs=UTM, resampling=Resampling.bilinear)
    np.save('geo/dem.npy', dem)
dem = np.load('geo/dem.npy'); print('DEM', dem.shape, round(float(dem.min())), round(float(dem.max())))
if not os.path.exists('geo/s2.png'):
    r = requests.post('https://earth-search.aws.element84.com/v1/search', json={'collections': ['sentinel-2-l2a'], 'bbox': [W_, S_, E_, N_],
        'datetime': '2025-10-01T00:00:00Z/2026-04-30T00:00:00Z', 'query': {'eo:cloud_cover': {'lt': 3}}, 'limit': 50}, timeout=60).json()
    items = sorted(r.get('features', []), key=lambda it: it['properties'].get('eo:cloud_cover', 100))
    for it in items[:6]:
        try:
            with rasterio.Env(GDAL_DISABLE_READDIR_ON_OPEN='EMPTY_DIR'):
                with rasterio.open(it['assets']['visual']['href']) as src:
                    out = np.zeros((3, h * 2, w * 2), np.uint8)
                    for b in range(3):
                        reproject(rasterio.band(src, b + 1), out[b], dst_transform=from_origin(x0, y1, RES / 2, RES / 2), dst_crs=UTM, resampling=Resampling.bilinear)
            if (out.sum(0) == 0).mean() < 0.02:
                Image.fromarray(np.transpose(out, (1, 2, 0))).save('geo/s2.png'); print('S2', it['id']); break
        except Exception as e: print('S2 skip', str(e)[:80])
q = f'[out:json][timeout:90];way["waterway"="river"]({S_},{W_},{N_},{E_});(._;>;);out body;'
HDR = {'User-Agent': 'reel-maker/1.0 (educational video)', 'Accept': 'application/json'}
osm = None
for url in ('https://overpass-api.de/api/interpreter', 'https://overpass.private.coffee/api/interpreter', 'https://maps.mail.ru/osm/tools/overpass/api/interpreter'):
    try: osm = requests.post(url, data={'data': q}, headers=HDR, timeout=150).json(); break
    except Exception as e: print('overpass fail', url)
nodes = {e['id']: (e['lon'], e['lat']) for e in osm['elements'] if e['type'] == 'node'}
ways = [e for e in osm['elements'] if e['type'] == 'way' and ('Jhelum' in e.get('tags', {}).get('name', '') or 'جہلم' in e.get('tags', {}).get('name', ''))]
print('river ways', len(ways), {e.get('tags', {}).get('name') for e in ways})
# chain ways into one line
segs = [[tf.transform(*nodes[n]) for n in e['nodes'] if n in nodes] for e in ways]
line = segs.pop(0) if segs else []
while segs:
    best = None
    for i, s in enumerate(segs):
        for rev in (False, True):
            ss = s[::-1] if rev else s
            for atend in (True, False):
                a = line[-1] if atend else line[0]; b = ss[0] if atend else ss[-1]
                d = math.hypot(a[0] - b[0], a[1] - b[1])
                if best is None or d < best[0]: best = (d, i, ss, atend)
    d, i, ss, atend = best; segs.pop(i)
    line = line + ss if atend else ss + line
json.dump({'x0': x0, 'y0': y0, 'x1': x1, 'y1': y1, 'res': RES, 'w': w, 'h': h, 'origin': [(x0 + x1) / 2, (y0 + y1) / 2]}, open('geo/meta.json', 'w'))
json.dump({'river': line}, open('geo/river.json', 'w'))
print('river pts', len(line), 'GEO_DONE')
