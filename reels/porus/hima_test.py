"""Compare voices for paragraphs 1-2: Hima TTS nano (Telugu) with the owner's voice copied from a clip, the same run
through the owner's Seed-VC model, and the current IndicF5 + Seed-VC version."""
import json, os, re, subprocess, sys
sys.path.insert(0, '/opt/reel/hima/hima-tts-nano-te'); os.chdir('/opt/reel/hima/hima-tts-nano-te')
from hima_tts import TTS
import soundfile as sf
W = '/opt/reel/sv/reels/porus'; O = '/opt/reel/vox/hima'; os.makedirs(O, exist_ok=True)
def sh(*a): subprocess.run(a, check=True)
TRIM = "silenceremove=start_periods=1:start_threshold=-45dB,areverse,silenceremove=start_periods=1:start_threshold=-45dB,areverse,afade=t=in:d=0.015"
POST = "highpass=f=80,arnndn=m=/opt/reel/vox/sh.rnnn:mix=0.6,acompressor=threshold=-20dB:ratio=3:attack=5:release=80:makeup=3,loudnorm=I=-14:TP=-1:LRA=9"
# 9 s of the owner's clean reference speech
sh('ffmpeg', '-y', '-v', 'error', '-ss', '2', '-t', '9', '-i', '/opt/reel/vox/ref_clean.wav', '-ar', '24000', '-ac', '1', f'{O}/ref9.wav')
tts = TTS('.')
tts.make_voice(f'{O}/ref9.wav', path=f'{O}/harshith.safetensors')
p = json.load(open(f'{W}/brief/plan.json'))
parts = []
for i, l in enumerate(p['lines'][:2], 1):
    phrases = [s.strip() for s in re.split(r'(?<=[.?!…])\s+', l['tts']) if s.strip()]
    for k, s in enumerate(phrases):
        a = tts.say(s.replace('…', ',').rstrip(','), voice=f'{O}/harshith.safetensors', seed=11)
        raw = f'{O}/h{i}_{k}.wav'; tts.save(a, raw)
        gap = 0.85 if s.endswith('…') else 0.5
        out = f'{O}/hq{i}_{k}.wav'
        sh('ffmpeg', '-y', '-v', 'error', '-i', raw, '-af', TRIM + f',apad=pad_dur={gap}', '-ar', '24000', '-ac', '1', out); parts.append(out)
    parts.append('PARA')
lst = ''.join(f"file '{x}'\n" for x in parts if x != 'PARA')
open(f'{O}/list.txt', 'w').write(lst)
sh('ffmpeg', '-y', '-v', 'error', '-f', 'concat', '-safe', '0', '-i', f'{O}/list.txt', '-ar', '22050', f'{O}/hima_raw.wav')
sh('ffmpeg', '-y', '-v', 'error', '-i', f'{O}/hima_raw.wav', '-af', POST + ',atempo=0.92', '-ar', '44100', '-ac', '1', f'{O}/A_hima.wav')
vc = f'{O}/vc'; subprocess.run(['rm', '-rf', vc]); os.makedirs(vc)
subprocess.run(['/opt/reel/svenv/bin/python', 'inference.py', '--source', f'{O}/hima_raw.wav', '--target', '/opt/reel/vox/ref_clean.wav', '--output', vc,
                '--diffusion-steps', '50', '--length-adjust', '1.0', '--inference-cfg-rate', '0.7', '--f0-condition', 'False', '--fp16', 'False',
                '--checkpoint', 'runs/harshith/ft_model.pth', '--config', 'configs/presets/config_dit_mel_seed_uvit_whisper_small_wavenet.yml'],
               cwd='/opt/reel/seed-vc', check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
sh('ffmpeg', '-y', '-v', 'error', '-i', f'{vc}/{sorted(os.listdir(vc))[0]}', '-af', POST + ',atempo=0.92', '-ar', '44100', '-ac', '1', f'{O}/B_hima_vc.wav')
# current version: paragraphs 1-2 of the slower IndicF5 + Seed-VC narration
sh('ffmpeg', '-y', '-v', 'error', '-i', f'{W}/audio/p01.wav', '-i', f'{W}/audio/p02.wav', '-filter_complex', '[0][1]concat=n=2:v=0:a=1', '-ar', '44100', '-ac', '1', f'{O}/C_current.wav')
S = '/opt/reel/share/e1376f7f43dd'
for x in ('A_hima', 'B_hima_vc', 'C_current'):
    sh('ffmpeg', '-y', '-v', 'error', '-f', 'lavfi', '-i', 'color=c=black:s=720x1280:r=10', '-i', f'{O}/{x}.wav', '-shortest', '-c:v', 'libx264',
       '-tune', 'stillimage', '-pix_fmt', 'yuv420p', '-c:a', 'aac', '-b:a', '160k', '-movflags', '+faststart', f'{S}/voice_{x}.mp4')
print('HIMA_DONE')
