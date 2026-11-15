"""Telugu story narration in the owner's voice: IndicF5 (Swaram voicebox, profile Datta-C) phrase by phrase with
story pauses -> one paragraph per file -> Seed-VC (fine-tuned on the owner) on the joined track -> clean -> split back."""
import json, os, re, subprocess, sys
sys.path.insert(0, '/opt/reel/myvoice'); import gen
W = '/opt/reel/sv/reels/porus'; os.chdir(W)
gen.PID = json.load(open('/opt/reel/vox/profiles.json'))['C']['id']
work = '/opt/reel/vox/porus'; os.makedirs(work, exist_ok=True); os.makedirs('audio', exist_ok=True)
SEP = 0.8
TRIM = ("silenceremove=start_periods=1:start_threshold=-45dB,areverse,"
        "silenceremove=start_periods=1:start_threshold=-45dB,areverse,afade=t=in:d=0.015")
POST = ("highpass=f=80,arnndn=m=/opt/reel/vox/sh.rnnn:mix=0.85,equalizer=f=3500:t=q:w=1:g=2,"
        "acompressor=threshold=-20dB:ratio=3:attack=5:release=80:makeup=3,loudnorm=I=-14:TP=-1:LRA=9")
def sh(*a): subprocess.run(a, check=True)
def dur(p): return float(subprocess.run(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0', p], capture_output=True, text=True).stdout)
p = json.load(open('brief/plan.json'))
sh('ffmpeg', '-y', '-v', 'error', '-f', 'lavfi', '-i', 'anullsrc=r=24000:cl=mono', '-t', str(SEP), f'{work}/sep.wav')
lst, bounds, t = [], [], 0.0
for i, l in enumerate(p['lines'], 1):
    # phrases split at sentence ends and at "…" (dramatic pause)
    phrases = [s.strip() for s in re.split(r'(?<=[.?!…])\s+', l['tts']) if s.strip()]
    parts = []
    for k, s in enumerate(phrases):
        raw = f'{work}/r{i:02d}_{k}.wav'
        if not os.path.exists(raw):
            gen.gen(s.replace('…', ',').rstrip(','), 'indicf5', raw, lang='te', seed=11)
        gap = 0.0 if k == len(phrases) - 1 else (0.55 if s.endswith('…') else 0.32)
        out = f'{work}/q{i:02d}_{k}.wav'
        sh('ffmpeg', '-y', '-v', 'error', '-i', raw, '-af', TRIM + (f',apad=pad_dur={gap}' if gap else ''), '-ar', '24000', '-ac', '1', out)
        parts.append(out)
    pl = f'{work}/p{i:02d}.txt'; open(pl, 'w').write(''.join(f"file '{x}'\n" for x in parts))
    sh('ffmpeg', '-y', '-v', 'error', '-f', 'concat', '-safe', '0', '-i', pl, '-ar', '24000', '-ac', '1', f'{work}/p{i:02d}.wav')
    d = dur(f'{work}/p{i:02d}.wav'); bounds.append((t, t + d)); t += d + SEP
    lst += [f"file '{work}/p{i:02d}.wav'", f"file '{work}/sep.wav'"]
    print('para', i, round(d, 1), flush=True)
open(f'{work}/list.txt', 'w').write('\n'.join(lst) + '\n')
sh('ffmpeg', '-y', '-v', 'error', '-f', 'concat', '-safe', '0', '-i', f'{work}/list.txt', '-ar', '22050', f'{work}/joined.wav')
vc = f'{work}/vc'; subprocess.run(['rm', '-rf', vc]); os.makedirs(vc)
subprocess.run(['/opt/reel/svenv/bin/python', 'inference.py', '--source', f'{work}/joined.wav', '--target', '/opt/reel/vox/ref_clean.wav',
                '--output', vc, '--diffusion-steps', '50', '--length-adjust', '1.0', '--inference-cfg-rate', '0.7', '--f0-condition', 'False',
                '--fp16', 'False', '--checkpoint', 'runs/harshith/ft_model.pth',
                '--config', 'configs/presets/config_dit_mel_seed_uvit_whisper_small_wavenet.yml'],
               cwd='/opt/reel/seed-vc', check=True, stdout=subprocess.DEVNULL, stderr=open('/tmp/vc_porus.log', 'w'))
out = sorted(os.listdir(vc))[0]
sh('ffmpeg', '-y', '-v', 'error', '-i', f'{vc}/{out}', '-af', POST, '-ar', '44100', '-ac', '1', f'{work}/post.wav')
sh('ffmpeg', '-y', '-v', 'error', '-i', f'{work}/joined.wav', '-af', POST, '-ar', '44100', '-ac', '1', f'{work}/direct.wav')
scale = dur(f'{work}/post.wav') / dur(f'{work}/joined.wav')
for i, (a, b) in enumerate(bounds):
    a0 = max(0, (a - SEP / 2) * scale) if i else 0; b0 = (b + SEP / 2) * scale
    sh('ffmpeg', '-y', '-v', 'error', '-i', f'{work}/post.wav', '-ss', f'{a0:.3f}', '-to', f'{b0:.3f}',
       '-af', TRIM + ',atempo=0.95,apad=pad_dur=0.6', '-ar', '44100', '-ac', '1', p['lines'][i]['audio'])
# a quick listen file: first paragraph + whole story
sh('ffmpeg', '-y', '-v', 'error', '-f', 'lavfi', '-i', 'color=c=black:s=720x1280:r=10', '-i', f'{work}/post.wav', '-shortest',
   '-c:v', 'libx264', '-tune', 'stillimage', '-pix_fmt', 'yuv420p', '-c:a', 'aac', '-b:a', '160k', '-movflags', '+faststart',
   '/opt/reel/share/e1376f7f43dd/porus_voice.mp4')
print('total', round(sum(dur(l['audio']) for l in p['lines']), 1))
print('VOICE_DONE')
