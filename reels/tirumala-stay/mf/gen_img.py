"""Model Forge image -> textured 3D for the real guest-house photos (refs/<key>.jpg -> mf/b_<key>.glb)."""
import base64, json, os, sys, time, urllib.request
pid = os.popen("pgrep -f '3dmodel/server/server.py' | head -1").read().strip()
env = dict(x.split('=', 1) for x in open(f'/proc/{pid}/environ', 'rb').read().decode(errors='ignore').split('\0') if '=' in x)
TOK = env.get('API_TOKEN') or ''; B = 'http://127.0.0.1:' + env.get('PORT', '8000')
H = {'Content-Type': 'application/json', **({'Authorization': 'Bearer ' + TOK} if TOK else {})}
keys = sys.argv[1:] or ['nandakam', 'panchajanyam', 'kausthubham', 'vakulamatha', 'pac5']
# REFDIR=refs/best uses the Google Maps picks; SUF names the output b_<key><SUF>.glb so both versions can be compared.
REFDIR = os.environ.get('REFDIR', 'refs'); SUF = os.environ.get('SUF', '')
tids = {}
for k0 in keys:
    k = k0 + SUF
    if os.path.exists(f'mf/b_{k}.glb'): continue
    img = 'data:image/jpeg;base64,' + base64.b64encode(open(f'{REFDIR}/{k0}.jpg', 'rb').read()).decode()
    body = json.dumps({'mode': 'image', 'image': img, 'texture': True, 'quality': 'high', 'polycount': 60000, 'fresh': True}).encode()
    r = json.load(urllib.request.urlopen(urllib.request.Request(B + '/generate', data=body, headers=H), timeout=60)); tids[k] = r['task_id']; print('queued', k, r, flush=True)
while tids:
    time.sleep(15)
    for k, t in list(tids.items()):
        s = json.load(urllib.request.urlopen(urllib.request.Request(B + f'/status/{t}', headers=H), timeout=60))
        if s['status'] == 'succeeded':
            open(f'mf/b_{k}.glb', 'wb').write(urllib.request.urlopen(urllib.request.Request(B + f'/models/{t}.glb', headers=H)).read())
            print('done', k, os.path.getsize(f'mf/b_{k}.glb') // 1024, 'KB', flush=True); del tids[k]
        elif s['status'] == 'failed': print('failed', k, str(s.get('error'))[:200], flush=True); del tids[k]
        else: print('..', k, s.get('stage'), s.get('progress'), flush=True)
print('MFIMG_DONE')
