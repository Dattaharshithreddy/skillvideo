"""Temple position, six more hill-top label points, and a mask of the 1974 road on the imagery (to erase it in 1944 shots).
Writes geo/places.json and geo/road2mask.png. Coordinates are UTM 44N metres."""
import json
import numpy as np
from PIL import Image, ImageDraw, ImageFilter
from pyproj import Transformer
Image.MAX_IMAGE_PIXELS = None
meta = json.load(open('geo/meta.json')); R = json.load(open('geo/roads.json')); dem = np.load('geo/dem.npy'); h, w = dem.shape; RES = meta['res']
tf = Transformer.from_crs('EPSG:4326', 'EPSG:32644', always_xy=True)
TX, TY = tf.transform(79.3474, 13.6833)                       # Sri Venkateswara temple, Tirumala
def rc(x, y): return int((meta['y1'] - y) / RES), int((x - meta['x0']) / RES)
def xy(r, c): return meta['x0'] + (c + 0.5) * RES, meta['y1'] - (r + 0.5) * RES
# hill tops: local maxima (radius 600 m) above 650 m, at least 1.4 km apart and 0.9 km from the temple, highest first
k = int(600 / RES); cand = []
for r in range(k, h - k, 3):
    for c in range(k, w - k, 3):
        z = dem[r, c]
        if z > 650 and z >= dem[r - k:r + k + 1, c - k:c + k + 1].max(): cand.append((float(z), r, c))
cand.sort(reverse=True); peaks = []
for z, r, c in cand:
    x, y = xy(r, c)
    if np.hypot(x - TX, y - TY) < 900: continue
    if all(np.hypot(x - px, y - py) > 1400 for px, py, _ in peaks): peaks.append((x, y, z))
    if len(peaks) == 6: break
names = ['శేషాద్రి', 'నీలాద్రి', 'గరుడాద్రి', 'అంజనాద్రి', 'వృషభాద్రి', 'నారాయణాద్రి']
r_, c_ = rc(TX, TY)
json.dump({'temple': [TX, TY, float(dem[r_, c_])], 'temple_name': 'వేంకటాద్రి',
           'peaks': [{'name': n, 'x': x, 'y': y, 'z': z} for n, (x, y, z) in zip(names, peaks)]}, open('geo/places.json', 'w'), ensure_ascii=False, indent=1)
print('temple elev', round(float(dem[r_, c_])), 'peaks', [(round(z), round(np.hypot(x - TX, y - TY))) for x, y, z in peaks])
# 1974 road mask on the imagery grid
im = Image.open('geo/gm.jpg'); GW, GH = im.size; GR = (meta['x1'] - meta['x0']) / GW
m = Image.new('L', (GW, GH), 0); d = ImageDraw.Draw(m)
DN = np.array([[p[0], p[1]] for p in R['down']]); run = []
def flush():
    if len(run) > 1: d.line(run, fill=255, width=int(22 / GR))
for x, y, z, dd in R['up']:
    if np.sqrt(((DN - [x, y]) ** 2).sum(1)).min() > 45: run.append(((x - meta['x0']) / GR, (meta['y1'] - y) / GR))
    else: flush(); run = []
flush(); m = m.filter(ImageFilter.GaussianBlur(6 / GR))
m.resize((GW // 2, GH // 2)).save('geo/road2mask.png'); print('MASK_DONE', GW, GH)
