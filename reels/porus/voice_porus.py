"""Telugu narration for the Puru reel in the owner's voice "Datta" via the Swaram API (/indic/narrate), built to avoid drift:
  * one API call per sentence, each with its own mood tag from brief/plan.json (story / talk / anger / sad / fear / surprise / happy / slow),
    so the voice never runs long enough to wander;
  * every take is scored for speaker similarity against a reference clip of Datta (resemblyzer) and for pace (characters per second);
    a take that sounds less like Datta or runs too fast/slow is regenerated, up to TAKES times, and the best one is kept;
  * the kept takes are joined with fixed pauses and their exact start/end times are written to narr/sentences.json, which drives
    shot lengths and captions (no estimated timing, so captions cannot slip out of sync).
Runs on the swaram-gpu server:  python3 voice_porus.py   (env REF=<reference wav>, TAKES=3)"""
import json, os, re, subprocess, glob, wave, contextlib
HERE = os.path.dirname(os.path.abspath(__file__)); os.chdir(HERE); os.makedirs('narr/takes', exist_ok=True)
SW = '/home/ubuntu/Swaram'; VOL = '/var/lib/docker/volumes/swaram_voicebox-data/_data'
DC = ['docker', 'compose', '-f', 'docker-compose.yml', '-f', 'docker-compose.cloud.yml']
TAKES = int(os.environ.get('TAKES', 3))
plan = json.load(open('brief/plan.json'))
def sentences(t): return [s.strip() for s in re.split(r'(?<=[.?!])\s+', t) if s.strip()]
def dur(p):
    with contextlib.closing(wave.open(p)) as w: return w.getnframes() / w.getframerate()
items = []                                   # (para, mood, sentence)
for i, l in enumerate(plan['lines']):
    for mood, txt in l['parts']:
        for s in sentences(txt): items.append((i, mood, s))
key = [l.split('=', 1)[1].strip().strip('"').strip("'") for l in open(f'{SW}/.env') if l.startswith('SWARAM_API_KEY=')][0]
call = ("import json,sys,urllib.request\n"
        "key=open('/app/data/.swk').read().strip()\n"
        "req=urllib.request.Request('http://localhost:17493/indic/narrate',data=open('/app/data/porus_req.json','rb').read(),"
        "headers={'Authorization':'Bearer '+key,'Content-Type':'application/json'})\n"
        "open('/app/data/porus_resp.json','wb').write(urllib.request.urlopen(req,timeout=900).read())\n")
open(f'{VOL}/porus_call.py', 'w').write(call)
def narrate(text, mood, seed):
    json.dump({'profile': 'Datta', 'script': f'({mood}) {text} [pause 0.1]', 'seed': seed}, open(f'{VOL}/porus_req.json', 'w'), ensure_ascii=False)
    r = subprocess.run(DC + ['exec', '-T', 'voicebox', 'python', '/app/data/porus_call.py'], cwd=SW, stdin=subprocess.DEVNULL, capture_output=True, text=True)
    if r.returncode: raise RuntimeError(r.stderr[-400:])
    resp = json.load(open(f'{VOL}/porus_resp.json')); u = resp.get('audio_url') or resp.get('audio') or resp.get('path')
    src = u if u.startswith('/') else os.path.join(VOL, u.split('/data/')[-1].lstrip('/'))
    return src
# speaker check
from resemblyzer import VoiceEncoder, preprocess_wav
enc = VoiceEncoder()
REF = os.environ.get('REF') or (sorted(glob.glob(f'{VOL}/profiles/*Datta*/**/*.wav', recursive=True)) or sorted(glob.glob(f'{VOL}/mood_clips/**/*.wav', recursive=True)) or ['../tirumala-ghat/audio_te/l01.wav'])[0]
ref = enc.embed_utterance(preprocess_wav(REF)); print('reference', REF)
def score(p, text):
    e = enc.embed_utterance(preprocess_wav(p)); sim = float((e * ref).sum())
    cps = len(text.replace(' ', '')) / max(0.3, dur(p))
    pace_ok = 9.0 <= cps <= 19.0
    return sim - (0.0 if pace_ok else 0.15), sim, cps
fd = os.open(f'{VOL}/.swk', os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o600); os.write(fd, key.encode()); os.close(fd)
report = []
try:
    for k, (para, mood, text) in enumerate(items):
        best = None
        for take in range(TAKES):
            src = narrate(text, mood, 1000 + 17 * k + take)
            p = f'narr/takes/s{k:03d}_t{take}.wav'
            subprocess.run(['ffmpeg', '-y', '-v', 'error', '-i', src, '-af', 'silenceremove=start_periods=1:start_threshold=-45dB,areverse,silenceremove=start_periods=1:start_threshold=-45dB,areverse',
                            '-ar', '44100', '-ac', '1', p], check=True)
            sc, sim, cps = score(p, text)
            if best is None or sc > best[0]: best = (sc, p, sim, cps)
            if sim >= 0.86 and 9.0 <= cps <= 19.0: break          # good enough: same voice, natural pace
        report.append({'k': k, 'para': para, 'mood': mood, 'text': text, 'sim': round(best[2], 3), 'cps': round(best[3], 1), 'take': best[1]})
        print(k, para, mood, round(best[2], 3), round(best[3], 1), flush=True)
finally:
    os.remove(f'{VOL}/.swk')
# join with fixed pauses: 0.35 s inside a line, 0.75 s between lines; write exact sentence times
gap_in, gap_line = 0.35, 0.75
parts, t, sents = [], 0.3, []
subprocess.run(['ffmpeg', '-y', '-v', 'error', '-f', 'lavfi', '-i', 'anullsrc=r=44100:cl=mono', '-t', '0.3', 'narr/lead.wav'], check=True)
parts.append('narr/lead.wav')
for j, r in enumerate(report):
    d = dur(r['take']); sents.append({'para': r['para'], 'start': round(t, 3), 'end': round(t + d, 3), 'text': r['text']}); parts.append(r['take']); t += d
    g = gap_line if j + 1 < len(report) and report[j + 1]['para'] != r['para'] else gap_in
    gp = f'narr/gap_{int(g * 100)}.wav'
    if not os.path.exists(gp): subprocess.run(['ffmpeg', '-y', '-v', 'error', '-f', 'lavfi', '-i', 'anullsrc=r=44100:cl=mono', '-t', str(g), gp], check=True)
    parts.append(gp); t += g
open('narr/list.txt', 'w').write(''.join(f"file '{os.path.abspath(p)}'\n" for p in parts))
subprocess.run(['ffmpeg', '-y', '-v', 'error', '-f', 'concat', '-safe', '0', '-i', 'narr/list.txt', '-af', 'loudnorm=I=-14:TP=-1.5:LRA=11', '-ar', '48000', 'narr/narration.wav'], check=True)
json.dump(sents, open('narr/sentences.json', 'w'), ensure_ascii=False, indent=1); json.dump(report, open('narr/report.json', 'w'), ensure_ascii=False, indent=1)
print('VOICE_DONE', len(sents), 'sentences', round(t, 1), 's; lowest similarity', min(r['sim'] for r in report))
