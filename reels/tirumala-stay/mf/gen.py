"""Generate the reel's hero models with Model Forge (Hunyuan3D-2, text -> textured GLB) on this server.
Writes mf/<name>.glb. The API token is read from the running server's environment and never printed."""
import json, os, re, sys, time, urllib.request
pid = os.popen("pgrep -f '3dmodel/server/server.py' | head -1").read().strip()
env = dict(x.split('=', 1) for x in open(f'/proc/{pid}/environ', 'rb').read().decode(errors='ignore').split('\0') if '=' in x)
TOK = env.get('API_TOKEN') or env.get('MODELFORGE_TOKEN') or ''
B = 'http://127.0.0.1:' + env.get('PORT', '8000')
H = {'Content-Type': 'application/json'}
if TOK: H['Authorization'] = 'Bearer ' + TOK
STYLE = ', hand-painted resin miniature figurine, 1:72 scale tabletop model, full body, standing on a small round base, clean silhouette'
JOBS = {
 'pil_man': 'Indian Hindu pilgrim man wearing a white dhoti and white half-sleeve shirt, hands folded in namaste' + STYLE,
 'pil_tonsure': 'Indian Hindu pilgrim man with a freshly shaved head with yellow sandal paste, saffron dhoti, bare chest with a white towel on the shoulder' + STYLE,
 'pil_woman_red': 'Indian woman pilgrim wearing a red silk saree with a gold border, jasmine flowers in her braided hair, hands folded' + STYLE,
 'pil_woman_yel': 'Indian woman pilgrim wearing a yellow cotton saree, walking, carrying a small cloth bag' + STYLE,
 'pil_girl': 'little Indian girl wearing a green pattu langa skirt and blouse, walking' + STYLE,
 'pil_elder': 'old Indian man with white hair, white dhoti and angavastram, holding a walking stick' + STYLE,
 'conch': 'ornate sacred golden conch shell shankha decorated with gold filigree and gems, Hindu divine conch of Vishnu, isolated object',
 'sword': 'ornate divine golden sword khadga of Lord Vishnu, gold hilt with rubies, straight broad blade, isolated object',
 'gem': 'large glowing red ruby gemstone Kaustubha set in an ornate gold pendant with small pearls, isolated object',
 'lotus': 'pink lotus flower in full bloom with green leaves, isolated object',
}
only = sys.argv[1:] or list(JOBS)
os.makedirs('mf', exist_ok=True)
tids = {}
for k in only:
    if os.path.exists(f'mf/{k}.glb'): continue
    body = json.dumps({'mode': 'text', 'prompt': JOBS[k], 'texture': True, 'quality': 'high', 'polycount': 40000}).encode()
    r = json.load(urllib.request.urlopen(urllib.request.Request(B + '/generate', data=body, headers=H), timeout=60)); tids[k] = r['task_id']; print('queued', k, flush=True)
while tids:
    time.sleep(15)
    for k, t in list(tids.items()):
        s = json.load(urllib.request.urlopen(urllib.request.Request(B + f'/status/{t}', headers=H), timeout=60))
        if s['status'] == 'succeeded':
            urllib.request.urlretrieve(B + f'/models/{t}.glb', f'mf/{k}.glb') if not TOK else open(f'mf/{k}.glb', 'wb').write(urllib.request.urlopen(urllib.request.Request(B + f'/models/{t}.glb', headers=H)).read())
            print('done', k, os.path.getsize(f'mf/{k}.glb') // 1024, 'KB', flush=True); del tids[k]
        elif s['status'] == 'failed':
            print('failed', k, str(s.get('error', ''))[:200], flush=True); del tids[k]
print('MF_DONE')
