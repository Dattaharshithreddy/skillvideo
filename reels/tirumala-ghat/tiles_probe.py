"""Probe Google Photorealistic 3D Tiles detail over Tirumala: descend toward a point, report geometric error per level."""
import json, math, subprocess, sys, urllib.parse, requests
K = subprocess.run(['aws', 'ssm', 'get-parameter', '--name', '/reel/google_maps_key', '--with-decryption', '--region', 'ap-south-1',
                    '--query', 'Parameter.Value', '--output', 'text'], capture_output=True, text=True).stdout.strip()
B = 'https://tile.googleapis.com'
def ecef(lat, lon, h=0):
    a = 6378137.0; e2 = 6.69437999014e-3; la, lo = math.radians(lat), math.radians(lon)
    n = a / math.sqrt(1 - e2 * math.sin(la) ** 2)
    return ((n + h) * math.cos(la) * math.cos(lo), (n + h) * math.cos(la) * math.sin(lo), (n * (1 - e2) + h) * math.sin(la))
pts = {'temple': (13.6833, 79.3474, 850), 'ghat_mid': (13.66, 79.37, 500)}
S = requests.Session(); session = None
def get(uri):
    global session
    u = urllib.parse.urljoin(B, uri); q = {'key': K}
    if session and 'session=' not in u: q['session'] = session
    r = S.get(u, params=q, timeout=60)
    if r.status_code != 200: raise SystemExit(f'HTTP {r.status_code} on {uri.split("?")[0][:80]}')
    return r
def inside(box, p, m=1.05):
    c = box[:3]; d = [p[i] - c[i] for i in range(3)]
    for ax in (box[3:6], box[6:9], box[9:12]):
        n2 = sum(a * a for a in ax)
        if n2 > 0 and abs(sum(d[i] * ax[i] for i in range(3))) / n2 > m: return False
    return True
def dist(box, p): return 0 if inside(box, p) else 1 + math.dist(box[:3], p)
for name, (la, lo, h) in pts.items():
    session = None; P = ecef(la, lo, h); node = get('/v1/3dtiles/root.json').json()['root']; lvl = 0; glbs = 0
    while True:
        kids = node.get('children', [])
        if not kids:
            c = node.get('content', {}).get('uri')
            if c and c.split('?')[0].endswith('.json'):
                if 'session=' in c: session = urllib.parse.parse_qs(urllib.parse.urlparse(c).query)['session'][0]
                node = get(c).json()['root']; continue
            break
        node = min(kids, key=lambda k: dist(k['boundingVolume']['box'], P)); lvl += 1
        c = node.get('content', {}).get('uri', '')
        if c and 'session=' in c: session = urllib.parse.parse_qs(urllib.parse.urlparse(c).query)['session'][0]
        if c.split('?')[0].endswith('.glb'):
            glbs += 1
            if True:
                print(name, 'lvl', lvl, 'err', round(node['geometricError'], 2), 'box half', round(math.dist((0, 0, 0), node['boundingVolume']['box'][3:6])), flush=True)
        if c.split('?')[0].endswith('.json'):
            node = get(c).json()['root']
    r = get(node['content']['uri']) if node.get('content', {}).get('uri', '').split('?')[0].endswith('.glb') else None
    print(name, 'deepest err', node.get('geometricError'), 'glb bytes', len(r.content) if r else None, flush=True)
    if r: open(f'/tmp/{name}.glb', 'wb').write(r.content)
