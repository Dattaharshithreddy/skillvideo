"""Download real terrain for a bbox: AWS Terrain Tiles (terrarium, SRTM-based) + EOX Sentinel-2 cloudless imagery + OSM features.
Output dir: height_z{Z}.png (16-bit, metres+offset in meta), sat_z{Z}.jpg, osm.json, meta.json.
Attribution: Sentinel-2 cloudless by EOX IT Services GmbH (contains modified Copernicus Sentinel data) CC BY 4.0;
terrain: Mapzen/AWS Terrain Tiles (SRTM, NASA); map data (c) OpenStreetMap contributors (ODbL)."""
import io, json, math, os, sys, urllib.request, urllib.parse
import numpy as np
from PIL import Image
cfg = json.load(open(sys.argv[1])); OUT = sys.argv[2]; os.makedirs(OUT, exist_ok=True)
S, W, N, E = cfg['bbox']
def tile(lat, lon, z):
    n = 2 ** z; x = (lon + 180) / 360 * n; y = (1 - math.asinh(math.tan(math.radians(lat))) / math.pi) / 2 * n
    return x, y
def get(url):
    r = urllib.request.Request(url, headers={'User-Agent': 'reel-terrain/1.0'})
    return urllib.request.urlopen(r, timeout=60).read()
def mosaic(z, url_fmt, mode):
    x0, y0 = tile(N, W, z); x1, y1 = tile(S, E, z)
    xs, ys = range(int(x0), int(x1) + 1), range(int(y0), int(y1) + 1)
    im = Image.new(mode, (256 * len(xs), 256 * len(ys)))
    for i, x in enumerate(xs):
        for j, y in enumerate(ys):
            try: im.paste(Image.open(io.BytesIO(get(url_fmt.format(z=z, x=x, y=y)))).convert(mode).resize((256, 256)), (i * 256, j * 256))
            except Exception as e: print('miss', z, x, y, e)
    # crop to exact bbox
    box = ((x0 - xs[0]) * 256, (y0 - ys[0]) * 256, (x1 - xs[0]) * 256, (y1 - ys[0]) * 256)
    return im.crop(tuple(int(v) for v in box))
meta = {'bbox': cfg['bbox'], 'attribution': __doc__.split('Attribution:')[1].strip()}
for z in cfg['height_z']:
    t = np.asarray(mosaic(z, 'https://s3.amazonaws.com/elevation-tiles-prod/terrarium/{z}/{x}/{y}.png', 'RGB')).astype(np.float64)
    h = t[..., 0] * 256 + t[..., 1] + t[..., 2] / 256 - 32768
    lo, hi = float(h.min()), float(h.max())
    Image.fromarray(np.round((h - lo) / (hi - lo) * 65535).astype(np.uint16)).save(f'{OUT}/height_z{z}.png')
    meta[f'height_z{z}'] = {'min_m': lo, 'max_m': hi, 'size': list(h.shape[::-1])}; print('height', z, h.shape, lo, hi)
for z in cfg['sat_z']:
    im = mosaic(z, 'https://tiles.maps.eox.at/wmts/1.0.0/s2cloudless-2021_3857/default/g/{z}/{y}/{x}.jpg', 'RGB')
    im.save(f'{OUT}/sat_z{z}.jpg', quality=93); meta[f'sat_z{z}'] = list(im.size); print('sat', z, im.size)
q = f'[out:json][timeout:120];(way["natural"="water"]({S},{W},{N},{E});way["amenity"="place_of_worship"]({S},{W},{N},{E});way["building"]({S},{W},{N},{E});way["highway"~"primary|secondary|tertiary|trunk"]({S},{W},{N},{E});node["amenity"="place_of_worship"]({S},{W},{N},{E}););out geom;'
try:
    d = get('https://overpass-api.de/api/interpreter?data=' + urllib.parse.quote(q)); open(f'{OUT}/osm.json', 'wb').write(d); print('osm', len(d))
except Exception as e: print('osm fail', e)
json.dump(meta, open(f'{OUT}/meta.json', 'w'), indent=1)
