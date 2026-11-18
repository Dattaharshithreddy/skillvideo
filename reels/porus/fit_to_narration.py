"""Fit the reel to a finished narration without re-rendering 3D.
1. join the per-sentence wavs (Kaggle studio-voice render) with fixed pauses -> narr/narration.wav + narr/sentences.json
2. build_timing.py with the exact sentence times
3. retime every rendered shot (mini3d/out3/<shot>.mp4) to its new length, and resample its label tracks to match
python3 fit_to_narration.py <dir with part-XXXXX.wav + parts.json>"""
import json, os, subprocess, sys, wave, contextlib
HERE = os.path.dirname(os.path.abspath(__file__)); os.chdir(HERE)
SRC = sys.argv[1]; OUT3 = 'mini3d/out3'; os.makedirs('narr', exist_ok=True)
def dur(p):
    with contextlib.closing(wave.open(p)) as w: return w.getnframes() / w.getframerate()
def run(*a): subprocess.run(list(a), check=True)
parts = sorted(json.load(open(os.path.join(SRC, 'parts.json'))), key=lambda p: p['i'])
GAP_IN, GAP_LINE, LEAD = 0.32, 0.7, 0.35
files, sents, t = [], [], LEAD
run('ffmpeg', '-nostdin', '-y', '-v', 'error', '-f', 'lavfi', '-i', 'anullsrc=r=24000:cl=mono', '-t', str(LEAD), 'narr/lead.wav'); files.append('narr/lead.wav')
for j, p in enumerate(parts):
    src = os.path.join(SRC, f"part-{p['i']:05d}.wav")
    trimmed = f"narr/s{p['i']:03d}.wav"      # trim leading/trailing silence so pauses are exactly ours
    run('ffmpeg', '-nostdin', '-y', '-v', 'error', '-i', src, '-af',
        'silenceremove=start_periods=1:start_threshold=-42dB,areverse,silenceremove=start_periods=1:start_threshold=-42dB,areverse', '-ar', '24000', '-ac', '1', trimmed)
    d = dur(trimmed); sents.append({'para': p['para'], 'start': round(t, 3), 'end': round(t + d, 3), 'text': p['text']}); files.append(trimmed); t += d
    g = GAP_LINE if j + 1 < len(parts) and parts[j + 1]['para'] != p['para'] else GAP_IN
    gp = f'narr/gap{int(g * 100)}.wav'
    if not os.path.exists(gp): run('ffmpeg', '-nostdin', '-y', '-v', 'error', '-f', 'lavfi', '-i', 'anullsrc=r=24000:cl=mono', '-t', str(g), gp)
    files.append(gp); t += g
open('narr/list.txt', 'w').write(''.join(f"file '{os.path.abspath(f)}'\n" for f in files))
run('ffmpeg', '-nostdin', '-y', '-v', 'error', '-f', 'concat', '-safe', '0', '-i', 'narr/list.txt', '-af', 'loudnorm=I=-15:TP=-1.5:LRA=11', '-ar', '48000', 'narr/narration.wav')
json.dump(sents, open('narr/sentences.json', 'w'), ensure_ascii=False, indent=1)
print('narration', round(t, 1), 's,', len(sents), 'sentences')
old = json.load(open('mg/src/timing.json'))
old_nf = {l['shot']: n for l, n in zip(old['lines'], old['nf'])}
run('python3', 'build_timing.py', 'narr/sentences.json')
new = json.load(open('mg/src/timing.json'))
lab = json.load(open('mg/src/labels.json')); newlab = {}
for l, n in zip(new['lines'], new['nf']):
    s = l['shot']; o = old_nf[s]; k = n / o
    src = f'{OUT3}/{s}.mp4'; dst = f'{OUT3}/{s}.fit.mp4'
    run('ffmpeg', '-nostdin', '-y', '-v', 'error', '-i', src, '-vf', f'setpts={k:.6f}*PTS,fps=30,tpad=stop_mode=clone:stop_duration=2',
        '-frames:v', str(n), '-c:v', 'libx264', '-preset', 'medium', '-crf', '16', '-pix_fmt', 'yuv420p', '-an', dst)
    tr = lab.get(s, {}); keys = sorted(int(x) for x in tr)
    out = {}
    for f in range(1, n + 1, 2):                                   # map new frame -> nearest old tracked frame
        of = 1 + round((f - 1) / max(1, n - 1) * (o - 1)); of = min(keys, key=lambda q: abs(q - of)) if keys else of
        if keys: out[str(f)] = tr[str(of)]
    newlab[s] = out
    print(f'{s}: {o} -> {n} frames ({k:.2f}x)')
json.dump(newlab, open('mg/src/labels.json', 'w'), separators=(',', ':'))
open(f'{OUT3}/concat_fit.txt', 'w').write(''.join(f"file '{os.path.abspath(OUT3)}/{l['shot']}.fit.mp4'\n" for l in new['lines']))
run('ffmpeg', '-nostdin', '-y', '-v', 'error', '-f', 'concat', '-safe', '0', '-i', f'{OUT3}/concat_fit.txt', '-c', 'copy', 'mg/public/bg.mp4')
run('ffmpeg', '-nostdin', '-y', '-v', 'error', '-i', 'narr/narration.wav', '-ar', '48000', '-ac', '2', 'mg/public/narration.wav')
run('python3', 'music.py', 'mg/src/timing.json', 'mg/public/music.wav')
print('FIT_DONE')
