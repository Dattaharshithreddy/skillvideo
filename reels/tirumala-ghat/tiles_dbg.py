import math, urllib.parse, subprocess, requests
exec(open('tiles_probe.py').read().split("for name, (la, lo, h) in pts.items():")[0])
P = ecef(13.6833, 79.3474, 850)
node = get('/v1/3dtiles/root.json').json()['root']
def show(n, depth):
    for k in n.get('children', []):
        b = k['boundingVolume']['box']; c = b[:3]; d = [P[i] - c[i] for i in range(3)]
        r = [abs(sum(d[i] * ax[i] for i in range(3))) / max(sum(a * a for a in ax), 1e-9) for ax in (b[3:6], b[6:9], b[9:12])]
        print('  ' * depth, 'err', round(k.get('geometricError', 0)), 'ratios', [round(x, 2) for x in r], 'uri', k.get('content', {}).get('uri', '')[-12:].split('?')[0])
print('P', [round(x) for x in P]); show(node, 0)
for k in node.get('children', []):
    print('child keys', list(k.keys())); show(k, 1); break
