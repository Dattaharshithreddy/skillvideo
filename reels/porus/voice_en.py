"""English Porus story in the owner's voice: Chatterbox (voicebox container) sentence by sentence with story pauses
-> paragraphs -> joined -> Seed-VC (owner) -> clean -> split -> slightly slowed."""
import json, os, re, subprocess, sys
W = '/opt/reel/sv/reels/porus'; os.chdir(W)
V = '/var/lib/docker/volumes/swaram_voicebox-data/_data/porus_en'; os.makedirs(V, exist_ok=True)
work = '/opt/reel/vox/porus_en'; os.makedirs(work, exist_ok=True); os.makedirs('audio', exist_ok=True)
SEP = 0.8
TRIM = ("silenceremove=start_periods=1:start_threshold=-45dB,areverse,"
        "silenceremove=start_periods=1:start_threshold=-45dB,areverse,afade=t=in:d=0.01")
POST = ("highpass=f=80,arnndn=m=/opt/reel/vox/sh.rnnn:mix=0.8,equalizer=f=3500:t=q:w=1:g=2.5,"
        "acompressor=threshold=-20dB:ratio=3:attack=5:release=80:makeup=3,loudnorm=I=-14:TP=-1:LRA=9")
def sh(*a): subprocess.run(a, check=True)
def dur(p): return float(subprocess.run(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0', p], capture_output=True, text=True).stdout)
p = json.load(open('brief/plan.json'))
todo, struct = {}, []
for i, l in enumerate(p['lines'], 1):
    ph = [s.strip() for s in re.split(r'(?<=[.?!…])\s+', l['tts']) if s.strip()]
    struct.append(ph)
    for k, s in enumerate(ph): todo[f'{i:02d}_{k}'] = s.replace('…', ',').rstrip(',').rstrip() if not s.endswith('…') else s.replace('…', '.')
json.dump(todo, open(f'{V}/todo.json', 'w'))
CB = r'''
import json, torch, random, soundfile as sf, os
from chatterbox.tts import ChatterboxTTS
m = ChatterboxTTS.from_pretrained(device='cuda')
U = json.load(open('/app/data/porus_en/todo.json'))
for k, t in U.items():
    out = f'/app/data/porus_en/{k}.wav'
    if os.path.exists(out): continue
    words = len(t.split()); exp = words * 0.36 + 0.6; best = None
    for s in [11, 23, 37, 51, 67]:
        torch.manual_seed(s); random.seed(s)
        w = m.generate(t, audio_prompt_path='/app/data/ref_te.wav', exaggeration=0.65, cfg_weight=0.4, temperature=0.7)
        d = w.shape[-1] / m.sr; err = abs(d - exp) / exp
        if best is None or err < best[0]: best = (err, w, d, s)
        if err < 0.18: break
    sf.write(out, best[1].squeeze().cpu().numpy(), m.sr)
    print(k, round(best[2], 2), 'exp', round(exp, 2), flush=True)
'''
open(f'{V}/cb.py', 'w').write(CB)
if '--skip-tts' not in sys.argv:
    sh('docker', 'exec', 'voicebox', 'sh', '-c', 'cd /app && python /app/data/porus_en/cb.py')
sh('ffmpeg', '-y', '-v', 'error', '-f', 'lavfi', '-i', 'anullsrc=r=22050:cl=mono', '-t', str(SEP), f'{work}/sep.wav')
lst, bounds, t = [], [], 0.0
for i, ph in enumerate(struct, 1):
    parts = []
    for k, s in enumerate(ph):
        gap = 0.0 if k == len(ph) - 1 else (0.9 if s.endswith('…') else 0.5)
        out = f'{work}/q{i:02d}_{k}.wav'
        sh('ffmpeg', '-y', '-v', 'error', '-i', f'{V}/{i:02d}_{k}.wav', '-af', TRIM + (f',apad=pad_dur={gap}' if gap else ''), '-ar', '22050', '-ac', '1', out)
        parts.append(out)
    open(f'{work}/p{i:02d}.txt', 'w').write(''.join(f"file '{x}'\n" for x in parts))
    sh('ffmpeg', '-y', '-v', 'error', '-f', 'concat', '-safe', '0', '-i', f'{work}/p{i:02d}.txt', '-ar', '22050', '-ac', '1', f'{work}/p{i:02d}.wav')
    d = dur(f'{work}/p{i:02d}.wav'); bounds.append((t, t + d)); t += d + SEP
    lst += [f"file '{work}/p{i:02d}.wav'", f"file '{work}/sep.wav'"]
open(f'{work}/list.txt', 'w').write('\n'.join(lst) + '\n')
sh('ffmpeg', '-y', '-v', 'error', '-f', 'concat', '-safe', '0', '-i', f'{work}/list.txt', '-ar', '22050', f'{work}/joined.wav')
vc = f'{work}/vc'; subprocess.run(['rm', '-rf', vc]); os.makedirs(vc)
subprocess.run(['/opt/reel/svenv/bin/python', 'inference.py', '--source', f'{work}/joined.wav', '--target', '/opt/reel/vox/ref_clean.wav',
                '--output', vc, '--diffusion-steps', '50', '--length-adjust', '1.0', '--inference-cfg-rate', '0.7', '--f0-condition', 'False',
                '--fp16', 'False', '--checkpoint', 'runs/harshith/ft_model.pth', '--config', 'configs/presets/config_dit_mel_seed_uvit_whisper_small_wavenet.yml'],
               cwd='/opt/reel/seed-vc', check=True, stdout=subprocess.DEVNULL, stderr=open('/tmp/vc_porus_en.log', 'w'))
sh('ffmpeg', '-y', '-v', 'error', '-i', f'{vc}/{sorted(os.listdir(vc))[0]}', '-af', POST, '-ar', '44100', '-ac', '1', f'{work}/post.wav')
scale = dur(f'{work}/post.wav') / dur(f'{work}/joined.wav')
for i, (a, b) in enumerate(bounds):
    a0 = max(0, (a - SEP / 2) * scale) if i else 0; b0 = (b + SEP / 2) * scale
    sh('ffmpeg', '-y', '-v', 'error', '-i', f'{work}/post.wav', '-ss', f'{a0:.3f}', '-to', f'{b0:.3f}',
       '-af', TRIM + ',atempo=0.9,apad=pad_dur=1.0', '-ar', '44100', '-ac', '1', p['lines'][i]['audio'])
open(f'{work}/final.txt', 'w').write(''.join(f"file '{W}/{l['audio']}'\n" for l in p['lines']))
sh('ffmpeg', '-y', '-v', 'error', '-f', 'concat', '-safe', '0', '-i', f'{work}/final.txt', '-c:a', 'pcm_s16le', f'{work}/final.wav')
sh('ffmpeg', '-y', '-v', 'error', '-f', 'lavfi', '-i', 'color=c=black:s=720x1280:r=10', '-i', f'{work}/final.wav', '-shortest', '-c:v', 'libx264',
   '-tune', 'stillimage', '-pix_fmt', 'yuv420p', '-c:a', 'aac', '-b:a', '160k', '-movflags', '+faststart', '/opt/reel/share/e1376f7f43dd/porus_english_voice.mp4')
print('total', round(sum(dur(l['audio']) for l in p['lines']), 1)); print('VOICE_EN_DONE')
