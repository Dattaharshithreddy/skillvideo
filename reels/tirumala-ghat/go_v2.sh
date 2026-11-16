# Version 2: divine opening (temple dive), seven-hills fly-past, closing temple shot. Old shots reuse the version 1 frames.
# Usage: bash go_v2.sh prep | test | full
W=/opt/reel/sv/reels/tirumala-ghat; cd $W; B=/opt/reel/blender/blender; O=/opt/reel/share/e1376f7f43dd
if [ "$1" = "prep" ]; then
  [ -f brief/timing_v1.json ] || cp brief/timing.json brief/timing_v1.json
  python3 - <<'PY'
import json, shutil, os
for l in json.load(open('brief/plan_v1.json'))['lines']:
    d = f"audio_te/{l['shot']}.wav"
    if not os.path.exists(d): shutil.copy(l['audio'], d)
PY
  python3 plan.py
  python3 -u voice_extra.py > /opt/reel/extra.log 2>&1; tail -2 /opt/reel/extra.log | cut -c1-400
  H=/opt/reel/assets/ph/h
  [ -s $H/the_sky_is_on_fire_2k.exr ] || curl -sL -o $H/the_sky_is_on_fire_2k.exr https://dl.polyhaven.org/file/ph-assets/HDRIs/exr/2k/the_sky_is_on_fire_2k.exr
  ls -la $H | tail -3
  if ! fc-list | grep -qi "Noto Serif Telugu"; then
    mkdir -p /usr/local/share/fonts; curl -sL -o "/usr/local/share/fonts/NotoSerifTelugu.ttf" "https://github.com/google/fonts/raw/main/ofl/notoseriftelugu/NotoSerifTelugu%5Bwght%5D.ttf"; fc-cache -f
  fi
  fc-list | grep -i "telugu" | cut -c1-120
  echo PREP_DONE
fi
if [ "$1" = "prep" ] || [ "$1" = "build" ]; then
  python3 plan.py > /dev/null; $B -b --python build.py > /opt/reel/gbuild2.log 2>&1
  grep -E "^built|^CLOSE|^TEMPLE|^LENS|Traceback|Error" /opt/reel/gbuild2.log | cut -c1-400; grep -A14 Traceback /opt/reel/gbuild2.log | head -18
  echo BUILD_DONE
fi
if [ "$1" = "test" ]; then
  F=$(python3 - <<'PY'
import json; t = json.load(open('brief/timing.json')); out = []
Q = {'hills': (0.03, 0.42, 0.8, 0.99), 'seven': (0.05, 0.33, 0.45, 0.55, 0.68, 0.85, 0.99), 'govinda': (0.3, 1.25)}
for s, d, l in zip(t['starts'], t['durs'], t['lines']):
    for q in Q.get(l['shot'], ()): out.append(str(min(t['end'], round((s + d * q) * 30) + 1)))
print(','.join(out))
PY
)
  rm -rf renders/t2; mkdir -p renders/t2
  /usr/bin/time -f "render %e s" $B -b scene/ghat2.blend -P /opt/reel/eevee.py -o "$W/renders/t2/t_#####" -f $F > /opt/reel/t2.log 2>&1; tail -1 /opt/reel/t2.log
  grep -iE "error|out of memory" /opt/reel/t2.log | head -3
  D=$O/v2; rm -rf $D; mkdir -p $D
  cd renders/t2 && for f in t_*.jpg; do ffmpeg -y -v error -i $f -vf scale=540:960 -q:v 4 $D/$f; done
  ffmpeg -y -v error -pattern_type glob -i 't_*.jpg' -vf "scale=270:480,tile=7x2" -frames:v 1 -q:v 4 $D/all.jpg; ls $D | tr '\n' ' '; echo TEST_DONE
fi
if [ "$1" = "full" ]; then
  python3 - <<'PY'
import json, os
o = json.load(open('brief/timing_v1.json')); n = json.load(open('brief/timing.json'))
def table(t): return {l['shot']: (round(s * 30) + 1, round((s + d) * 30)) for s, d, l in zip(t['starts'], t['durs'], t['lines'])}
Ot, Nt = table(o), table(n); os.makedirs('renders/seq2', exist_ok=True); c = 0
for sh, (a, b) in Nt.items():
    if sh in ('hills', 'seven', 'govinda') or sh not in Ot: continue
    oa, ob = Ot[sh]
    for k in range(b - a + 1):
        src = f'renders/seq/f_{oa + k:05d}.jpg'; dst = f'renders/seq2/f_{a + k:05d}.jpg'
        if oa + k <= ob and os.path.exists(src) and not os.path.exists(dst): os.link(src, dst); c += 1
print('linked', c, 'have', len(os.listdir('renders/seq2')), 'of', n['end'])
PY
  N=$(python3 -c "import json;print(json.load(open('brief/timing.json'))['end'])")
  for try in 1 2 3; do
    [ $(ls renders/seq2 | wc -l) -ge $N ] && break
    $B -b scene/ghat2.blend -P /opt/reel/eevee.py -o "$W/renders/seq2/f_#####" -s 1 -e $N -a > /opt/reel/gp2all.log 2>&1
  done
  echo RENDERED $(ls renders/seq2 | wc -l) of $N
  mkdir -p mg/public mg/out
  ffmpeg -y -v error -framerate 30 -i renders/seq2/f_%05d.jpg -vf "eq=saturation=1.12:contrast=1.03" -c:v libx264 -preset medium -crf 17 -pix_fmt yuv420p mg/public/bg.mp4
  python3 - <<'PY'
import json, subprocess, os
p = json.load(open('brief/plan.json')); t = json.load(open('brief/timing.json'))
subprocess.run(['ffmpeg','-y','-v','error','-f','lavfi','-i','anullsrc=r=44100:cl=mono','-t',str(p['gap']),'renders/gap.wav'],check=True)
open('renders/a.txt','w').write(''.join(f"file '{os.path.abspath(l['audio'])}'\nfile '{os.path.abspath('renders/gap.wav')}'\n" for l in p['lines']))
subprocess.run(['ffmpeg','-y','-v','error','-f','concat','-safe','0','-i','renders/a.txt','-af','loudnorm=I=-14:TP=-1.5:LRA=11','-ar','48000','renders/voice.wav'],check=True)
st = {l['shot']: s for s, l in zip(t['starts'], t['lines'])}; dur = t['end'] / 30
subprocess.run(['python3', 'music.py', str(dur), 'renders/music.wav', f"0.15,{st['seven'] + 0.1:.2f},{st['govinda'] - 0.2:.2f},{dur - 2.6:.2f}"], check=True)
subprocess.run(['ffmpeg','-y','-v','error','-i','renders/voice.wav','-i','renders/music.wav','-filter_complex',
                '[1:a]aresample=48000,volume=0.20[m];[0:a][m]amix=inputs=2:duration=longest:normalize=0,alimiter=limit=0.95','-ar','48000','mg/public/narration.wav'],check=True)
PY
  cp brief/timing.json brief/labels.json mg/src/
  ln -sfn /opt/reel/sv/reels/follow-the-salt/mg/node_modules mg/node_modules
  (cd mg && npx remotion render src/index.ts Main out/final2.mp4 --concurrency=4 --log=error)
  ffmpeg -y -v error -i mg/out/final2.mp4 -c:v libx264 -preset fast -crf 23 -pix_fmt yuv420p -c:a aac -b:a 160k -movflags +faststart $O/tirumala_telugu_v2.mp4
  mkdir -p $O/v2f; for tt in 2 6 10 13 16 19 60 118; do ffmpeg -y -v error -ss $tt -i mg/out/final2.mp4 -frames:v 1 -vf scale=540:960 -q:v 4 $O/v2f/s_$tt.jpg; done
  aws s3 cp mg/out/final2.mp4 s3://claude-reels-730335199669/reels/tirumala-ghat-telugu-v2.mp4 --region ap-south-1 --quiet && echo S3_OK
  echo ALLDONE2
fi
