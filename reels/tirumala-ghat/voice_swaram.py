"""Telugu narration in the owner's voice "Datta" via the Swaram API (/indic/narrate) inside the voicebox container.
Step 'make': builds the mood-tagged script from brief/plan.json, calls the API, saves the reply to audio_te/narrate.json.
Step 'split <wav>': cuts the returned WAV into one clip per paragraph (audio_te/lNN.wav) using the per-line times."""
import json, os, re, subprocess, sys
W = '/opt/reel/sv/reels/tirumala-ghat'; os.chdir(W); os.makedirs('audio_te', exist_ok=True)
SW = '/home/ubuntu/Swaram'; VOL = '/var/lib/docker/volumes/swaram_voicebox-data/_data'
DC = ['docker', 'compose', '-f', 'docker-compose.yml', '-f', 'docker-compose.cloud.yml']
p = json.load(open('brief/plan.json'))
MOOD = {'hills': '(story)', 'open': '(talk)', 'two_roads': '(surprise)', 'cart_track': '(talk)', 'people': '(talk)', 'lay_road': '(talk)',
        'straight': '(talk)', 'hairpins': '(talk)', 'traffic': '(talk)', 'second_road': '(talk)', 'rockfall': '(talk)',
        'old_runs': '(happy)', 'finale': '(story)', 'seven': '(story)', 'govinda': '(happy)'}
def sentences(t): return [s.strip() for s in re.split(r'(?<=[.?!])\s+', t) if s.strip()]
if sys.argv[1] == 'make':
    lines, owner, names = [], [], []
    for i, l in enumerate(p['lines']):
        ss = sentences(l['tts'])
        for k, s in enumerate(ss):
            pause = 0.7 if k == len(ss) - 1 else (0.5 if s.endswith('…') else 0.3)
            if l['shot'] == 'seven' and s.count(',') >= 5:        # the seven hill names: one slow line each
                for nm in [x.strip(' .') for x in s.split(',')]:
                    lines.append(f"(story, slow) {nm}. [pause 0.45]"); owner.append(i); names.append(len(lines) - 1)
                continue
            lines.append(f"{MOOD[l['shot']]} {s} [pause {pause}]"); owner.append(i)
    script = '\n'.join(lines); words = sum(len(l['tts'].split()) for l in p['lines'])
    target = ''
    json.dump({'profile': 'Datta', 'script': script}, open(f'{VOL}/tirumala_te_req.json', 'w'), ensure_ascii=False)
    json.dump(owner, open('audio_te/owner.json', 'w')); json.dump(names, open('audio_te/names.json', 'w'))
    call = ("import json,os,urllib.request\n"
            "key=open('/app/data/.swk').read().strip()\n"
            "req=urllib.request.Request('http://localhost:17493/indic/narrate',data=open('/app/data/tirumala_te_req.json','rb').read(),"
            "headers={'Authorization':'Bearer '+key,'Content-Type':'application/json'})\n"
            "r=urllib.request.urlopen(req,timeout=3000).read(); open('/app/data/tirumala_te_resp.json','wb').write(r); print('ok', len(r))\n")
    open(f'{VOL}/tirumala_call.py', 'w').write(call)
    # only the key (not the whole .env) is handed to the container for this one call, then deleted; it is never printed
    key = [l.split('=', 1)[1].strip().strip('"').strip("'") for l in open(f'{SW}/.env') if l.startswith('SWARAM_API_KEY=')][0]
    fd = os.open(f'{VOL}/.swk', os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o600); os.write(fd, key.encode()); os.close(fd)
    try:
        r = subprocess.run(DC + ['exec', '-T', 'voicebox', 'python', '/app/data/tirumala_call.py'], cwd=SW, stdin=subprocess.DEVNULL,
                           capture_output=True, text=True, env={**os.environ, 'HOME': '/root'})
        print(r.stdout[-300:], r.stderr[-600:])
    finally:
        os.remove(f'{VOL}/.swk')
    resp = json.load(open(f'{VOL}/tirumala_te_resp.json')); json.dump(resp, open('audio_te/narrate.json', 'w'), ensure_ascii=False, indent=1)
    print('target', target, 'keys', list(resp.keys()), 'audio_url', resp.get('audio_url'), 'lines', len(resp.get('lines', [])), 'script lines', len(lines))
    print('MAKE_DONE')
if sys.argv[1] == 'split':
    wav = sys.argv[2]; resp = json.load(open('audio_te/narrate.json')); owner = json.load(open('audio_te/owner.json'))
    L = resp.get('lines') or resp.get('timings') or []
    def t(x, k): return float(x.get(k, x.get(k + '_s', x.get(k + '_time', 0))))
    st = [t(x, 'start') for x in L]
    dur = float(subprocess.run(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0', wav], capture_output=True, text=True).stdout)
    n = len(p['lines'])
    for i in range(n):
        idx = [j for j, o in enumerate(owner) if o == i]
        a = st[idx[0]] if i else 0.0
        nxt = [j for j, o in enumerate(owner) if o == i + 1]
        b = st[nxt[0]] if nxt else dur
        out = p['lines'][i]['audio']
        subprocess.run(['ffmpeg', '-y', '-v', 'error', '-i', wav, '-ss', f'{a:.3f}', '-to', f'{b:.3f}', '-ar', '44100', '-ac', '1', out], check=True)
        if os.path.exists(out + '.placeholder'): os.remove(out + '.placeholder')
    json.dump([{'line': x.get('text', ''), 'start': t(x, 'start'), 'end': t(x, 'end'), 'para': owner[j]} for j, x in enumerate(L)], open('brief/sentences.json', 'w'), ensure_ascii=False)
    names = json.load(open('audio_te/names.json')) if os.path.exists('audio_te/names.json') else []
    if names:
        i7 = owner[names[0]]; a7 = st[[j for j, o in enumerate(owner) if o == i7][0]] if i7 else 0.0
        nx7 = [j for j, o in enumerate(owner) if o == i7 + 1]; b7 = st[nx7[0]] if nx7 else dur
        json.dump({'seven': {'dur': b7 - a7, 'names': [st[j] - a7 for j in names]}}, open('brief/extra_times.json', 'w'))
    print('total', round(dur, 1), 'SPLIT_DONE')
