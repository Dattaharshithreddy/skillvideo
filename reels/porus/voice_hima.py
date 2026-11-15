"""Full Porus story with Hima TTS nano (Telugu), owner's voice copied from a clip, normal pace, story pauses.
audio/pNN.wav = Hima direct; audio_vc/pNN.wav = same through the owner's Seed-VC model (same timing)."""
import json, os, re, subprocess, sys
sys.path.insert(0, '/opt/reel/hima/hima-tts-nano-te'); os.chdir('/opt/reel/hima/hima-tts-nano-te')
from hima_tts import TTS
W = '/opt/reel/sv/reels/porus'; O = '/opt/reel/vox/hima_full'; os.makedirs(O, exist_ok=True)
def sh(*a): subprocess.run(a, check=True)
def dur(p): return float(subprocess.run(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0', p], capture_output=True, text=True).stdout)
TRIM = "silenceremove=start_periods=1:start_threshold=-45dB,areverse,silenceremove=start_periods=1:start_threshold=-45dB,areverse,afade=t=in:d=0.015"
POST = "highpass=f=80,arnndn=m=/opt/reel/vox/sh.rnnn:mix=0.6,acompressor=threshold=-20dB:ratio=3:attack=5:release=80:makeup=3,loudnorm=I=-14:TP=-1:LRA=9"
SEP = 0.8
tts = TTS('.'); VOICE = '/opt/reel/vox/hima/harshith.safetensors'
p = json.load(open(f'{W}/brief/plan.json'))
sh('ffmpeg', '-y', '-v', 'error', '-f', 'lavfi', '-i', 'anullsrc=r=24000:cl=mono', '-t', str(SEP), f'{O}/sep.wav')
lst, bounds, t = [], [], 0.0
for i, l in enumerate(p['lines'], 1):
    phrases = [s.strip() for s in re.split(r'(?<=[.?!…])\s+', l['tts']) if s.strip()]
    parts = []
    for k, s in enumerate(phrases):
        raw = f'{O}/r{i:02d}_{k}.wav'
        tts.save(tts.say(s.replace('…', ',').rstrip(','), voice=VOICE, seed=11), raw)
        gap = 0.0 if k == len(phrases) - 1 else (0.75 if s.endswith('…') else 0.4)
        out = f'{O}/q{i:02d}_{k}.wav'
        sh('ffmpeg', '-y', '-v', 'error', '-i', raw, '-af', TRIM + (f',apad=pad_dur={gap}' if gap else ''), '-ar', '24000', '-ac', '1', out); parts.append(out)
    open(f'{O}/p{i:02d}.txt', 'w').write(''.join(f"file '{x}'\n" for x in parts))
    sh('ffmpeg', '-y', '-v', 'error', '-f', 'concat', '-safe', '0', '-i', f'{O}/p{i:02d}.txt', '-ar', '24000', '-ac', '1', f'{O}/p{i:02d}.wav')
    d = dur(f'{O}/p{i:02d}.wav'); bounds.append((t, t + d)); t += d + SEP
    lst += [f"file '{O}/p{i:02d}.wav'", f"file '{O}/sep.wav'"]
open(f'{O}/list.txt', 'w').write('\n'.join(lst) + '\n')
sh('ffmpeg', '-y', '-v', 'error', '-f', 'concat', '-safe', '0', '-i', f'{O}/list.txt', '-ar', '22050', f'{O}/joined.wav')
vc = f'{O}/vc'; subprocess.run(['rm', '-rf', vc]); os.makedirs(vc)
subprocess.run(['/opt/reel/svenv/bin/python', 'inference.py', '--source', f'{O}/joined.wav', '--target', '/opt/reel/vox/ref_clean.wav', '--output', vc,
                '--diffusion-steps', '50', '--length-adjust', '1.0', '--inference-cfg-rate', '0.7', '--f0-condition', 'False', '--fp16', 'False',
                '--checkpoint', 'runs/harshith/ft_model.pth', '--config', 'configs/presets/config_dit_mel_seed_uvit_whisper_small_wavenet.yml'],
               cwd='/opt/reel/seed-vc', check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
sh('ffmpeg', '-y', '-v', 'error', '-i', f'{O}/joined.wav', '-af', POST, '-ar', '44100', '-ac', '1', f'{O}/A.wav')
sh('ffmpeg', '-y', '-v', 'error', '-i', f'{vc}/{sorted(os.listdir(vc))[0]}', '-af', POST, '-ar', '44100', '-ac', '1', f'{O}/B.wav')
for name, folder in (('A', 'audio'), ('B', 'audio_vc')):
    src = f'{O}/{name}.wav'; scale = dur(src) / dur(f'{O}/joined.wav'); os.makedirs(f'{W}/{folder}', exist_ok=True)
    for i, (a, b) in enumerate(bounds):
        a0 = max(0, (a - SEP / 2) * scale) if i else 0; b0 = (b + SEP / 2) * scale
        sh('ffmpeg', '-y', '-v', 'error', '-i', src, '-ss', f'{a0:.3f}', '-to', f'{b0:.3f}', '-af', TRIM + ',apad=pad_dur=0.8', '-ar', '44100', '-ac', '1', f'{W}/{folder}/p{i + 1:02d}.wav')
    sh('ffmpeg', '-y', '-v', 'error', '-f', 'lavfi', '-i', 'color=c=black:s=720x1280:r=10', '-i', src, '-shortest', '-c:v', 'libx264', '-tune', 'stillimage',
       '-pix_fmt', 'yuv420p', '-c:a', 'aac', '-b:a', '160k', '-movflags', '+faststart', f'/opt/reel/share/e1376f7f43dd/story_{name}.mp4')
print('total', round(sum(dur(f'{W}/audio/p{i:02d}.wav') for i in range(1, 11)), 1)); print('HIMA_FULL_DONE')
