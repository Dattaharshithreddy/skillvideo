#!/usr/bin/env bash
# Hugging Face Job (CPU): frames + voice + temple music + Telugu overlay -> final reel.
# Inputs in the bucket mounted at /out: seq/f_#####.jpg, audio/l01..l13.wav, timing.json, labels.json
# Output: /out/final/tirumala_guesthouses_telugu.mp4 (+ contact sheet). Image: node:22-bookworm, flavor cpu-performance.
set -x
export DEBIAN_FRONTEND=noninteractive
apt-get update -qq && apt-get install -y -qq git ffmpeg python3 python3-numpy fonts-noto-core libnss3 libatk-bridge2.0-0 libgbm1 \
  libxkbcommon0 libasound2 libpangocairo-1.0-0 libcups2 libxcomposite1 libxdamage1 libxrandr2 libdrm2 >/dev/null 2>&1
cd "$(dirname "$0")/.."
python3 plan.py >/dev/null 2>&1; mkdir -p audio renders mg/public mg/out /out/final
cp /out/audio/l*.wav audio/; cp /out/timing.json /out/labels.json brief/
N=$(python3 -c "import json;print(json.load(open('brief/timing.json'))['end'])"); echo "frames needed $N, have $(ls /out/seq | wc -l)"
ffmpeg -y -v error -framerate 30 -i /out/seq/f_%05d.jpg -frames:v $N -vf "eq=saturation=1.08:contrast=1.03" -c:v libx264 -preset medium -crf 16 -pix_fmt yuv420p mg/public/bg.mp4
python3 - <<'PY'
import json, subprocess, os
p = json.load(open('brief/plan.json')); t = json.load(open('brief/timing.json'))
open('renders/a.txt', 'w').write(''.join(f"file '{os.path.abspath(l['audio'])}'\n" for l in p['lines']))
dur = t['end'] / 30
subprocess.run(['ffmpeg','-y','-v','error','-f','concat','-safe','0','-i','renders/a.txt','-af',f"loudnorm=I=-14:TP=-1.5:LRA=11,aresample=48000,apad=whole_dur={dur:.3f}",'-ac','1','renders/voice.wav'], check=True)
st = {l['shot']: s for s, l in zip(t['starts'], t['lines'])}
subprocess.run(['python3', 'music.py', str(dur), 'renders/music.wav', f"0.15,{st['rename'] + 0.1:.2f},{st['gods'] - 0.1:.2f},{st['finale'] + 0.1:.2f},{dur - 2.6:.2f}"], check=True)
subprocess.run(['ffmpeg','-y','-v','error','-i','renders/voice.wav','-i','renders/music.wav','-filter_complex',
                '[1:a]aresample=48000,volume=0.20[m];[0:a][m]amix=inputs=2:duration=first:normalize=0,alimiter=limit=0.95','-ar','48000','mg/public/narration.wav'], check=True)
print('AUDIO_OK')
PY
cp brief/timing.json brief/labels.json mg/src/; cp ../tirumala-ghat/brand/logo_wm.png mg/public/logo_wm.png
cd mg && npm install --silent --no-audit --no-fund >/dev/null 2>&1 && npx remotion browser ensure >/dev/null 2>&1
npx remotion render src/index.ts Main out/final.mp4 --concurrency=8 --log=error && cd ..
ffmpeg -y -v error -i mg/out/final.mp4 -c:v libx264 -preset slow -crf 20 -maxrate 9000k -bufsize 18000k -pix_fmt yuv420p -c:a aac -b:a 192k -movflags +faststart /out/final/tirumala_guesthouses_telugu.mp4
python3 - <<'PY'
import json, subprocess
T = json.load(open('brief/timing.json')); ts = [s + d * 0.6 for s, d in zip(T['starts'], T['durs'])]
for i, t in enumerate(ts): subprocess.run(['ffmpeg','-y','-v','error','-ss',f'{t:.2f}','-i','/out/final/tirumala_guesthouses_telugu.mp4','-frames:v','1','-vf','scale=270:480',f'renders/fin_{i:02d}.jpg'])
subprocess.run('ffmpeg -y -v error -pattern_type glob -i "renders/fin_*.jpg" -vf tile=7x2 -frames:v 1 /out/final/final_sheet.jpg', shell=True)
PY
ls -la /out/final; echo POST_DONE
