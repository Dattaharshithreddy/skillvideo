"""Telugu narration in the owner's voice "Datta" via the Swaram API (/indic/narrate) inside the voicebox container.
Step 'make': builds the mood-tagged script from brief/plan.json, calls the API, saves the reply to audio_te/narrate.json.
Step 'split <wav>': cuts the returned WAV into one clip per paragraph (audio_te/lNN.wav) using the per-line times."""
import json, os, re, subprocess, sys
W = '/opt/reel/sv/reels/tirumala-ghat'; os.chdir(W); os.makedirs('audio_te', exist_ok=True)
SW = '/home/ubuntu/Swaram'; VOL = '/var/lib/docker/volumes/swaram_voicebox-data/_data'
DC = ['docker', 'compose', '-f', 'docker-compose.yml', '-f', 'docker-compose.cloud.yml']
p = json.load(open('brief/plan.json'))
MOOD = {'hills': '(story, slow)', 'open': '(story)', 'two_roads': '(surprise)', 'cart_track': '(story)', 'people': '(talk)', 'lay_road': '(talk)',
        'straight': '(talk)', 'hairpins': '(story)', 'traffic': '(story)', 'second_road': '(story)', 'rockfall': '(fear, slow)',
        'old_runs': '(story, speed 0.95)', 'finale': '(happy, slow)'}
def sentences(t): return [s.strip() for s in re.split(r'(?<=[.?!])\s+', t) if s.strip()]
if sys.argv[1] == 'make':
    lines, owner = [], []
    for i, l in enumerate(p['lines']):
        ss = sentences(l['tts'])
        for k, s in enumerate(ss):
            pause = 0.9 if k == len(ss) - 1 else (0.6 if s.endswith('…') else 0.4)
            lines.append(f"{MOOD[l['shot']]} {s} [pause {pause}]"); owner.append(i)
    script = '\n'.join(lines); words = sum(len(l['tts'].split()) for l in p['lines'])
    target = round(words * 0.62 + 0.5 * len(lines))
    json.dump({'profile': 'Datta', 'script': script, 'target_seconds': target}, open(f'{VOL}/tirumala_te_req.json', 'w'), ensure_ascii=False)
    json.dump(owner, open('audio_te/owner.json', 'w'))
    call = ("import json,os,urllib.request\n"
            "key=[l.split('=',1)[1].strip().strip('\"') for l in open('/run/swaram.env') if l.startswith('SWARAM_API_KEY=')][0]\n"
            "req=urllib.request.Request('http://localhost:17493/indic/narrate',data=open('/app/data/tirumala_te_req.json','rb').read(),"
            "headers={'Authorization':'Bearer '+key,'Content-Type':'application/json'})\n"
            "r=urllib.request.urlopen(req,timeout=3000).read(); open('/app/data/tirumala_te_resp.json','wb').write(r); print('ok', len(r))\n")
    open(f'{VOL}/tirumala_call.py', 'w').write(call)
    # the key file is copied into the container only for this call, then removed; it is never printed
    subprocess.run(DC + ['cp', f'{SW}/.env', 'voicebox:/run/swaram.env'], cwd=SW, check=True, stdin=subprocess.DEVNULL, env={**os.environ, 'HOME': '/root'})
    try:
        r = subprocess.run(DC + ['exec', '-T', 'voicebox', 'python', '/app/data/tirumala_call.py'], cwd=SW, stdin=subprocess.DEVNULL,
                           capture_output=True, text=True, env={**os.environ, 'HOME': '/root'})
        print(r.stdout[-300:], r.stderr[-600:])
    finally:
        subprocess.run(DC + ['exec', '-T', 'voicebox', 'rm', '-f', '/run/swaram.env'], cwd=SW, stdin=subprocess.DEVNULL, env={**os.environ, 'HOME': '/root'})
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
    print('total', round(dur, 1), 'SPLIT_DONE')
