"""Real data for the Tirumala ghat roads reel, all in UTM 44N metres:
- terrain: Copernicus DEM GLO-30 (AWS open data)
- colour: Sentinel-2 L2A true-colour (AWS open data, Element84 STAC)
- roads: OpenStreetMap via Overpass; routed uphill (Alipiri -> Tirumala) and downhill, respecting one-way tags
Writes geo/dem.npy, geo/meta.json, geo/s2.png, geo/roads.json and prints a measurement report."""
import json, math, os, sys
import numpy as np, requests, rasterio, networkx as nx
from rasterio.warp import reproject, Resampling, transform_bounds
from rasterio.transform import from_origin
from pyproj import Transformer
from PIL import Image
os.makedirs('geo', exist_ok=True)
W_, S_, E_, N_ = 79.322, 13.622, 79.438, 13.718           # lon/lat box around Tirupati (Alipiri) and Tirumala
UTM = 'EPSG:32644'
tf = Transformer.from_crs('EPSG:4326', UTM, always_xy=True)
x0, y0, x1, y1 = transform_bounds('EPSG:4326', UTM, W_, S_, E_, N_)
RES = 20.0
w, h = int((x1 - x0) / RES), int((y1 - y0) / RES)
dst_t = from_origin(x0, y1, RES, RES)

# ---- terrain ----
DEM = 'https://copernicus-dem-30m.s3.amazonaws.com/Copernicus_DSM_COG_10_N13_00_E079_00_DEM/Copernicus_DSM_COG_10_N13_00_E079_00_DEM.tif'
if os.path.exists('geo/dem.npy'): dem = np.load('geo/dem.npy')
else:
  with rasterio.Env(GDAL_DISABLE_READDIR_ON_OPEN='EMPTY_DIR', AWS_NO_SIGN_REQUEST='YES'):
    with rasterio.open(DEM) as src:
        dem = np.zeros((h, w), np.float32)
        reproject(rasterio.band(src, 1), dem, dst_transform=dst_t, dst_crs=UTM, resampling=Resampling.bilinear)
  np.save('geo/dem.npy', dem)
print('DEM', dem.shape, 'min', round(float(dem.min())), 'max', round(float(dem.max())))

# ---- satellite colour ----
cx, cy = (W_ + E_) / 2, (S_ + N_) / 2
r = requests.post('https://earth-search.aws.element84.com/v1/search', json={
    'collections': ['sentinel-2-l2a'], 'bbox': [W_, S_, E_, N_], 'datetime': '2024-12-01T00:00:00Z/2026-04-30T00:00:00Z',
    'query': {'eo:cloud_cover': {'lt': 3}}, 'limit': 50}, timeout=60).json()
items = [it for it in r.get('features', []) if it['properties'].get('mgrs:utm_zone', 44) == 44]
items.sort(key=lambda it: it['properties'].get('eo:cloud_cover', 100))
rgb = None
for it in ([] if os.path.exists('geo/s2.png') else items[:6]):
    href = it['assets']['visual']['href']
    try:
        with rasterio.Env(GDAL_DISABLE_READDIR_ON_OPEN='EMPTY_DIR'):
            with rasterio.open(href) as src:
                out = np.zeros((3, h * 2, w * 2), np.uint8)
                for b in range(3):
                    reproject(rasterio.band(src, b + 1), out[b], dst_transform=from_origin(x0, y1, RES / 2, RES / 2), dst_crs=UTM,
                              resampling=Resampling.bilinear)
        if (out.sum(0) == 0).mean() < 0.02:
            rgb = out; print('S2', it['id'], it['properties']['datetime'][:10], 'cloud', it['properties']['eo:cloud_cover']); break
    except Exception as e:
        print('S2 skip', it['id'], str(e)[:80])
if rgb is not None:
    Image.fromarray(np.transpose(rgb, (1, 2, 0))).save('geo/s2.png')

# ---- roads from OpenStreetMap ----
q = f'[out:json][timeout:90];way["highway"~"^(trunk|primary|secondary|tertiary|unclassified|road|residential)$"]({S_},{W_},{N_},{E_});(._;>;);out body;'
osm = None
HDR = {'User-Agent': 'reel-maker/1.0 (educational video; contact via github Dattaharshithreddy)', 'Accept': 'application/json'}
if os.path.exists('geo/osm.json'): osm = json.load(open('geo/osm.json'))
for url in ('https://overpass-api.de/api/interpreter', 'https://overpass.private.coffee/api/interpreter',
            'https://maps.mail.ru/osm/tools/overpass/api/interpreter', 'https://overpass.kumi.systems/api/interpreter'):
    if osm: break
    for attempt in range(2):
        try:
            rr = requests.post(url, data={'data': q}, headers=HDR, timeout=150)
            osm = rr.json(); json.dump(osm, open('geo/osm.json', 'w')); break
        except Exception as e:
            print('overpass fail', url, rr.status_code if 'rr' in dir() else '', rr.text[:120].replace(chr(10), ' ') if 'rr' in dir() else str(e)[:80])
            import time; time.sleep(5)
nodes = {e['id']: (e['lon'], e['lat']) for e in osm['elements'] if e['type'] == 'node'}
G = nx.DiGraph()
def xy(nid):
    lon, lat = nodes[nid]; return tf.transform(lon, lat)
for e in osm['elements']:
    if e['type'] != 'way': continue
    t = e.get('tags', {}); ow = t.get('oneway', 'no'); nm = t.get('name', '')
    ns = e['nodes']
    for a, b in zip(ns, ns[1:]):
        (ax, ay), (bx, by) = xy(a), xy(b); d = math.hypot(bx - ax, by - ay)
        if ow == '-1': G.add_edge(b, a, w=d, name=nm)
        else:
            G.add_edge(a, b, w=d, name=nm)
            if ow not in ('yes', 'true', '1'): G.add_edge(b, a, w=d, name=nm)
def nearest(lon, lat, maxd):
    px, py = tf.transform(lon, lat); best = None
    for n in G.nodes:
        x, y = xy(n); d = math.hypot(x - px, y - py)
        if d < maxd and (best is None or d < best[0]): best = (d, n)
    return best[1]
ALIPIRI = (79.4060, 13.6515); TEMPLE = (79.3474, 13.6833)
def elev(x, y):
    c = (x - x0) / RES; r_ = (y1 - y) / RES
    c = min(max(c, 0), w - 1.001); r_ = min(max(r_, 0), h - 1.001)
    c0, r0 = int(c), int(r_); fc, fr = c - c0, r_ - r0
    return float(dem[r0, c0] * (1 - fc) * (1 - fr) + dem[r0, c0 + 1] * fc * (1 - fr) + dem[r0 + 1, c0] * (1 - fc) * fr + dem[r0 + 1, c0 + 1] * fc * fr)
def route(a, b):
    p = nx.shortest_path(G, a, b, weight='w')
    pts = [xy(n) for n in p]; names = {}
    for u, v in zip(p, p[1:]):
        nm = G[u][v]['name']; names[nm] = names.get(nm, 0) + G[u][v]['w']
    return pts, names
start = nearest(*ALIPIRI, 1500); end = nearest(*TEMPLE, 2000)
up, up_names = route(start, end)
down, down_names = route(end, start)
def analyse(pts, label):
    # resample every 25 m with elevation
    out, acc = [], 0.0
    for (ax, ay), (bx, by) in zip(pts, pts[1:]):
        d = math.hypot(bx - ax, by - ay); n = max(1, int(d / 25))
        for k in range(n):
            t = k / n; x, y = ax + (bx - ax) * t, ay + (by - ay) * t
            out.append([x, y, elev(x, y), acc + d * t])
        acc += d
    out.append([pts[-1][0], pts[-1][1], elev(*pts[-1]), acc])
    # gradient over 200 m windows; hairpins = heading change > 135 deg within 120 m
    grads = []
    for i in range(len(out)):
        j = i
        while j < len(out) - 1 and out[j][3] - out[i][3] < 200: j += 1
        if out[j][3] > out[i][3] + 100: grads.append(abs(out[j][2] - out[i][2]) / (out[j][3] - out[i][3]) * 100)
    hp, i = [], 0
    while i < len(out) - 6:
        h0 = math.atan2(out[i + 1][1] - out[i][1], out[i + 1][0] - out[i][0])
        for j in range(i + 2, min(len(out) - 1, i + 6)):
            h1 = math.atan2(out[j + 1][1] - out[j][1], out[j + 1][0] - out[j][0])
            dd = abs((h1 - h0 + math.pi) % (2 * math.pi) - math.pi)
            if dd > math.radians(135): hp.append(round(out[j][3])); i = j; break
        i += 1
    rep = dict(length_km=round(acc / 1000, 2), z_start=round(out[0][2]), z_end=round(out[-1][2]), climb=round(out[-1][2] - out[0][2]),
               mean_grade=round(abs(out[-1][2] - out[0][2]) / acc * 100, 1), p90_grade=round(float(np.percentile(grads, 90)), 1),
               max_grade_200m=round(max(grads), 1), hairpins=len(hp), hairpin_at_m=hp)
    print(label, json.dumps(rep))
    return out, rep
up_s, up_r = analyse(up, 'UP (second road?)')
dn_s, dn_r = analyse(down, 'DOWN (first road?)')
print('UP names', {k: round(v) for k, v in sorted(up_names.items(), key=lambda kv: -kv[1])[:5]})
print('DOWN names', {k: round(v) for k, v in sorted(down_names.items(), key=lambda kv: -kv[1])[:5]})
sx, sy = up[0]; ex, ey = up[-1]
straight = math.hypot(ex - sx, ey - sy)
print('STRAIGHT', dict(dist_km=round(straight / 1000, 2), grade=round((elev(ex, ey) - elev(sx, sy)) / straight * 100, 1)))
json.dump({'x0': x0, 'y0': y0, 'x1': x1, 'y1': y1, 'res': RES, 'w': w, 'h': h,
           'origin': [(x0 + x1) / 2, (y0 + y1) / 2]}, open('geo/meta.json', 'w'))
json.dump({'up': up_s, 'down': dn_s, 'up_report': up_r, 'down_report': dn_r,
           'straight': {'a': [sx, sy, elev(sx, sy)], 'b': [ex, ey, elev(ex, ey)]}}, open('geo/roads.json', 'w'))
print('GEO_DONE')
