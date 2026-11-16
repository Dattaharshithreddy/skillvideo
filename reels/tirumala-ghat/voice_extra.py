"""Narrate only the plan lines that have no audio yet (new lines added to an already voiced script), in the owner's
"Datta" voice via the Swaram API, and cut the reply into one clip per line. Same key handling as voice_swaram.py:
the key is read on the server, handed to the container in a 0600 file for one call, deleted, never printed."""
import json, os, re, subprocess
W = '/opt/reel/sv/reels/tirumala-ghat'; os.chdir(W); os.makedirs('audio_te', exist_ok=True)
SW = '/home/ubuntu/Swaram'; VOL = '/var/lib/docker/volumes/swaram_voicebox-data/_data'
DC = ['docker', 'compose', '-f', 'docker-compose.yml', '-f', 'docker-compose.cloud.yml']
p = json.load(open('brief/plan.json'))
MOOD = {'seven': '(story)', 'govinda': '(happy)'}
todo = [l for l in p['lines'] if not os.path.exists(l['audio'])]
print('to narrate:', [l['shot'] for l in todo])
if not todo: print('EXTRA_DONE'); raise SystemExit
def sentences(t): return [s.strip() for s in re.split(r'(?<=[.?!])\s+', t) if s.strip()]
lines, owner = [], []
for i, l in enumerate(todo):
    ss = sentences(l['tts'])
    for k, s in enumerate(ss):
        pause = 0.9 if k == len(ss) - 1 else (0.5 if s.endswith('…') else 0.35)
        lines.append(f"{MOOD.get(l['shot'], '(talk)')} {s} [pause {pause}]"); owner.append(i)
json.dump({'profile': 'Datta', 'script': '\n'.join(lines)}, open(f'{VOL}/tirumala_te_req.json', 'w'), ensure_ascii=False)
call = ("import json,os,urllib.request\n"
        "key=open('/app/data/.swk').read().strip()\n"
        "req=urllib.request.Request('http://localhost:17493/indic/narrate',data=open('/app/data/tirumala_te_req.json','rb').read(),"
        "headers={'Authorization':'Bearer '+key,'Content-Type':'application/json'})\n"
        "r=urllib.request.urlopen(req,timeout=3000).read(); open('/app/data/tirumala_te_resp.json','wb').write(r); print('ok', len(r))\n")
open(f'{VOL}/tirumala_call.py', 'w').write(call)
key = [l.split('=', 1)[1].strip().strip('"').strip("'") for l in open(f'{SW}/.env') if l.startswith('SWARAM_API_KEY=')][0]
fd = os.open(f'{VOL}/.swk', os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o600); os.write(fd, key.encode()); os.close(fd)
try:
    r = subprocess.run(DC + ['exec', '-T', 'voicebox', 'python', '/app/data/tirumala_call.py'], cwd=SW, stdin=subprocess.DEVNULL,
                       capture_output=True, text=True, env={**os.environ, 'HOME': '/root'})
    print(r.stdout[-300:], r.stderr[-600:])
finally:
    os.remove(f'{VOL}/.swk')
resp = json.load(open(f'{VOL}/tirumala_te_resp.json')); json.dump(resp, open('audio_te/narrate_extra.json', 'w'), ensure_ascii=False, indent=1)
wav = '/home/ubuntu/Swaram/output/narrations/' + resp['audio_url'].split('/')[-1]
subprocess.run(['cp', wav, 'audio_te/extra_full.wav'], check=True)
L = resp.get('lines') or resp.get('timings') or []
def t(x, k): return float(x.get(k, x.get(k + '_s', x.get(k + '_time', 0))))
st = [t(x, 'start') for x in L]; en = [t(x, 'end') for x in L]
dur = float(subprocess.run(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0', wav], capture_output=True, text=True).stdout)
info = {}
for i, l in enumerate(todo):
    idx = [j for j, o in enumerate(owner) if o == i]; nxt = [j for j, o in enumerate(owner) if o == i + 1]
    a = max(0.0, st[idx[0]] - 0.05) if i else 0.0; b = st[nxt[0]] - 0.05 if nxt else dur
    subprocess.run(['ffmpeg', '-y', '-v', 'error', '-i', wav, '-ss', f'{a:.3f}', '-to', f'{b:.3f}', '-ar', '44100', '-ac', '1', l['audio']], check=True)
    info[l['shot']] = {'dur': b - a, 'sent': [[st[j] - a, en[j] - a] for j in idx]}
json.dump(info, open('brief/extra_times.json', 'w'), indent=1)
print('total', round(dur, 1), info); print('EXTRA_DONE')
