"""Narration for both scripts in the owner's voice: Chatterbox (in the voicebox container) -> joined -> Seed-VC -> clean -> split -> slow 0.92."""
import json, os, subprocess, sys
W = '/opt/reel/sv/reels/follow-the-sugar'
V = '/var/lib/docker/volumes/swaram_voicebox-data/_data/sugar'
os.makedirs(V, exist_ok=True); os.chdir(W)
SEP = 0.8
POST = ("highpass=f=80,arnndn=m=/opt/reel/vox/sh.rnnn:mix=0.8,equalizer=f=3500:t=q:w=1:g=2.5,"
        "acompressor=threshold=-20dB:ratio=3:attack=5:release=80:makeup=3,loudnorm=I=-14:TP=-1:LRA=9")
TRIM = ("silenceremove=start_periods=1:start_threshold=-45dB,areverse,"
        "silenceremove=start_periods=1:start_threshold=-45dB,areverse,afade=t=in:d=0.01")
def sh(*a): subprocess.run(a, check=True)
def dur(p): return float(subprocess.run(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0', p],
                                        capture_output=True, text=True).stdout)
plans = {k: json.load(open(f'brief/plan_{k}.json')) for k in ('public', 'student')}
todo = {f'{k[:3]}_{i + 1:02d}': l['tts'] for k, p in plans.items() for i, l in enumerate(p['lines'])}
json.dump(todo, open(f'{V}/todo.json', 'w'), ensure_ascii=False)
CB = r'''
import json, torch, random, soundfile as sf, os
from chatterbox.tts import ChatterboxTTS
m = ChatterboxTTS.from_pretrained(device='cuda')
U = json.load(open('/app/data/sugar/todo.json'))
for k, t in U.items():
    out = f'/app/data/sugar/{k}.wav'
    if os.path.exists(out): continue
    words = len(t.split()); exp = words * 0.33 + 0.6; best = None
    for s in [11, 23, 37, 51, 67]:
        torch.manual_seed(s); random.seed(s)
        w = m.generate(t, audio_prompt_path='/app/data/ref_te.wav', exaggeration=0.6, cfg_weight=0.4, temperature=0.7)
        d = w.shape[-1] / m.sr; err = abs(d - exp) / exp
        if best is None or err < best[0]: best = (err, w, d, s)
        if err < 0.18: break
    sf.write(out, best[1].squeeze().cpu().numpy(), m.sr)
    print(k, round(best[2], 2), 'exp', round(exp, 2), flush=True)
'''
open(f'{V}/cb_sugar.py', 'w').write(CB)
if '--skip-tts' not in sys.argv:
    sh('docker', 'exec', 'voicebox', 'sh', '-c', 'cd /app && python /app/data/sugar/cb_sugar.py')
work = '/opt/reel/vox/sugar'; os.makedirs(work, exist_ok=True)
sh('ffmpeg', '-y', '-v', 'error', '-f', 'lavfi', '-i', 'anullsrc=r=22050:cl=mono', '-t', str(SEP), f'{work}/sep.wav')
for k, p in plans.items():
    n = len(p['lines']); lst = []; bounds = []; t = 0.0
    for i in range(n):
        src = f'{V}/{k[:3]}_{i + 1:02d}.wav'; tr = f'{work}/{k}_{i + 1:02d}_t.wav'
        sh('ffmpeg', '-y', '-v', 'error', '-i', src, '-af', TRIM, '-ar', '22050', '-ac', '1', tr)
        d = dur(tr); bounds.append((t, t + d)); t += d + SEP
        lst += [f"file '{tr}'", f"file '{work}/sep.wav'"]
    open(f'{work}/{k}_list.txt', 'w').write('\n'.join(lst) + '\n')
    sh('ffmpeg', '-y', '-v', 'error', '-f', 'concat', '-safe', '0', '-i', f'{work}/{k}_list.txt', '-ar', '22050', f'{work}/{k}_joined.wav')
    vc = f'{work}/{k}_vc'; subprocess.run(['rm', '-rf', vc]); os.makedirs(vc)
    subprocess.run(['/opt/reel/svenv/bin/python', 'inference.py', '--source', f'{work}/{k}_joined.wav', '--target', '/opt/reel/vox/ref_clean.wav',
                    '--output', vc, '--diffusion-steps', '50', '--length-adjust', '1.0', '--inference-cfg-rate', '0.7', '--f0-condition', 'False',
                    '--fp16', 'False', '--checkpoint', 'runs/harshith/ft_model.pth',
                    '--config', 'configs/presets/config_dit_mel_seed_uvit_whisper_small_wavenet.yml'],
                   cwd='/opt/reel/seed-vc', check=True, stdout=subprocess.DEVNULL, stderr=open(f'/tmp/vc_{k}.log', 'w'))
    out = sorted(os.listdir(vc))[0]
    sh('ffmpeg', '-y', '-v', 'error', '-i', f'{vc}/{out}', '-af', POST, '-ar', '44100', '-ac', '1', f'{work}/{k}_post.wav')
    scale = dur(f'{work}/{k}_post.wav') / dur(f'{work}/{k}_joined.wav')
    folder = os.path.dirname(p['lines'][0]['audio']); os.makedirs(folder, exist_ok=True)
    for i, (a, b) in enumerate(bounds):
        a0 = max(0, (a - SEP / 2) * scale) if i else 0; b0 = (b + SEP / 2) * scale
        pad = 0.3 if p['lines'][i]['text'].endswith('?') else 0.45
        sh('ffmpeg', '-y', '-v', 'error', '-i', f'{work}/{k}_post.wav', '-ss', f'{a0:.3f}', '-to', f'{b0:.3f}',
           '-af', TRIM + f',atempo=0.92,apad=pad_dur={pad}', '-ar', '44100', '-ac', '1', p['lines'][i]['audio'])
    tot = sum(dur(l['audio']) + p['gap'] for l in p['lines'])
    print(k, 'lines', n, 'total', round(tot, 1), flush=True)
print('VOICE_DONE')
