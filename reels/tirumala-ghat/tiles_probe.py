"""Probe Google Photorealistic 3D Tiles detail: depth-first search with backtracking toward a point; report finest geometric error."""
import math, subprocess, sys, urllib.parse, requests
K = subprocess.run(['aws', 'ssm', 'get-parameter', '--name', '/reel/google_maps_key', '--with-decryption', '--region', 'ap-south-1',
                    '--query', 'Parameter.Value', '--output', 'text'], capture_output=True, text=True).stdout.strip()
B = 'https://tile.googleapis.com'; S = requests.Session(); SESSION = [None]; CALLS = [0]
def ecef(lat, lon, h=0):
    a = 6378137.0; e2 = 6.69437999014e-3; la, lo = math.radians(lat), math.radians(lon)
    n = a / math.sqrt(1 - e2 * math.sin(la) ** 2)
    return ((n + h) * math.cos(la) * math.cos(lo), (n + h) * math.cos(la) * math.sin(lo), (n * (1 - e2) + h) * math.sin(la))
def get(uri):
    u = urllib.parse.urljoin(B, uri); q = {'key': K}
    if SESSION[0] and 'session=' not in u: q['session'] = SESSION[0]
    CALLS[0] += 1; r = S.get(u, params=q, timeout=60)
    if r.status_code != 200: raise SystemExit(f'HTTP {r.status_code} on {uri.split("?")[0][:80]}')
    if 'session=' in uri: SESSION[0] = urllib.parse.parse_qs(urllib.parse.urlparse(uri).query)['session'][0]
    return r
def inside(box, p, m=1.02):
    c = box[:3]; d = [p[i] - c[i] for i in range(3)]
    for ax in (box[3:6], box[6:9], box[9:12]):
        n2 = sum(a * a for a in ax)
        if n2 > 0 and abs(sum(d[i] * ax[i] for i in range(3))) / n2 > m: return False
    return True
def search(node, P, best):
    uri = node.get('content', {}).get('uri', '')
    if uri.split('?')[0].endswith('.json'):
        if 'session=' in uri: SESSION[0] = urllib.parse.parse_qs(urllib.parse.urlparse(uri).query)['session'][0]
        node = get(uri).json()['root']
    elif uri and node.get('geometricError', 1e9) < best[0]:
        best[0] = node['geometricError']; best[1] = uri
    for k in node.get('children', []):
        if inside(k['boundingVolume']['box'], P): search(k, P, best)
pts = {'bengaluru': (12.9763, 77.5929, 920), 'tirumala_temple': (13.6833, 79.3474, 850), 'ghat_mid': (13.66, 79.37, 500)}
for name in sys.argv[1:] or pts:
    la, lo, h = pts[name]; SESSION[0] = None; CALLS[0] = 0; best = [1e9, None]
    search(get('/v1/3dtiles/root.json').json()['root'], ecef(la, lo, h), best)
    r = get(best[1]); open(f'/tmp/{name}.glb', 'wb').write(r.content)
    print(name, 'finest error m', round(best[0], 2), 'glb KB', len(r.content) // 1024, 'requests', CALLS[0], flush=True)
