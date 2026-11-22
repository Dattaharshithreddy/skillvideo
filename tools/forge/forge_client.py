"""Sends every job in a jobs file to the local Model Forge server, one at a time, and saves the results.
jobs.json: {"jobs": [{"name": "varaha_a", "mode": "2d", "prompt": "...", "aspect": "portrait", "seed": 1, ...}, ...]}
Any key besides "name" is passed to POST /generate. Jobs whose output already exists in OUT are skipped (resumable).
3D jobs may give "image_from": "<name of an earlier png in OUT>" instead of an image data URL."""
import base64, json, os, sys, time, urllib.request
jobs, OUT = json.load(open(sys.argv[1]))['jobs'], sys.argv[2]; API = 'http://127.0.0.1:8000'
def call(path, body=None):
    r = urllib.request.Request(API + path, data=json.dumps(body).encode() if body else None, headers={'Content-Type': 'application/json'})
    return json.load(urllib.request.urlopen(r, timeout=600))
for j in jobs:
    name = j.pop('name'); ext = 'png' if j.get('mode') == '2d' else 'glb'; dst = f'{OUT}/{name}.{ext}'
    if os.path.exists(dst): print('have', name); continue
    if 'image_from' in j:
        if not os.path.exists(f"{OUT}/{j['image_from']}.png"): print('SKIP', name, 'missing', j['image_from'], flush=True); continue
        j['image'] = 'data:image/png;base64,' + base64.b64encode(open(f"{OUT}/{j.pop('image_from')}.png", 'rb').read()).decode()
    j.setdefault('fresh', True); t0 = time.time()
    try:
        tid = call('/generate', j)['task_id']
        while True:
            s = call(f'/status/{tid}')
            if s['status'] in ('succeeded', 'failed'): break
            time.sleep(10)
        if s['status'] == 'failed': print('FAILED', name, s.get('error')); continue
        url = f'{API}/images/{tid}.png' if ext == 'png' else f'{API}/models/{tid}.glb'
        urllib.request.urlretrieve(url, dst)
        if ext == 'glb':
            try: urllib.request.urlretrieve(f'{API}/inputs/{tid}_input.png', f'{OUT}/{name}_input.png')
            except Exception: pass
        print('done', name, round(time.time() - t0), 's', flush=True)
    except Exception as e:
        print('ERROR', name, e, flush=True)
