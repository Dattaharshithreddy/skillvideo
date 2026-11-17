# Usage: bash go.sh build | test | full | post
set -x
W=/opt/reel/sv/reels/tirumala-stay; cd $W; B=/opt/reel/blender/blender; PY=$(ls /opt/reel/blender/*/python/bin/python3* | head -1)
if [ "$1" = "build" ]; then
  $B -b --python build.py > /opt/reel/tsbuild.log 2>&1
  grep -E "^built|PEOPLE|TEMPLE|skipped|hidden|Traceback|Error" /opt/reel/tsbuild.log | cut -c1-300; grep -A12 Traceback /opt/reel/tsbuild.log | head -16
  echo BUILD_DONE
fi
if [ "$1" = "test" ]; then
  F=$(python3 -c "
import json; t = json.load(open('brief/timing.json')); out = []
for s, d in zip(t['starts'], t['durs']):
    for q in (0.15, 0.7): out.append(str(round((s + d * q) * 30) + 1))
print(','.join(out))")
  rm -rf renders/t; mkdir -p renders/t
  /usr/bin/time -f "render %e s" $B -b scene/stay.blend -P eevee_hq.py -o "$W/renders/t/t_#####" -f $F > /opt/reel/tstest.log 2>&1; tail -1 /opt/reel/tstest.log
  cd renders/t && ffmpeg -y -v error -pattern_type glob -i 't_*.jpg' -vf "scale=270:480,tile=7x4" -frames:v 1 -q:v 3 ../sheet.jpg && cd ../..
  aws s3 cp --only-show-errors renders/sheet.jpg s3://claude-reels-730335199669/preview/stay_sheet.jpg
  for f in renders/t/t_*.jpg; do aws s3 cp --only-show-errors $f s3://claude-reels-730335199669/preview/stay/$(basename $f); done
  echo TEST_DONE
fi
if [ "$1" = "full" ]; then
  N=$(python3 -c "import json;print(json.load(open('brief/timing.json'))['end'])"); mkdir -p renders/seq
  for try in 1 2 3; do
    [ $(ls renders/seq | wc -l) -ge $N ] && break
    $B -b scene/stay.blend -P eevee_hq.py -o "$W/renders/seq/f_#####" -s 1 -e $N -a > /opt/reel/tsfull.log 2>&1
  done
  echo RENDERED $(ls renders/seq | wc -l) of $N
  bash go.sh post
fi
if [ "$1" = "post" ]; then
  mkdir -p mg/public mg/out
  ffmpeg -y -v error -framerate 30 -i renders/seq/f_%05d.jpg -vf "eq=saturation=1.1:contrast=1.03" -c:v libx264 -preset medium -crf 16 -pix_fmt yuv420p mg/public/bg.mp4
  python3 - "$PY" <<'PY'
import json, subprocess, os, sys
p = json.load(open('brief/plan.json')); t = json.load(open('brief/timing.json'))
open('renders/a.txt','w').write(''.join(f"file '{os.path.abspath(l['audio'])}'\n" for l in p['lines']))
dur = t['end'] / 30
subprocess.run(['ffmpeg','-y','-v','error','-f','concat','-safe','0','-i','renders/a.txt','-af',f"loudnorm=I=-14:TP=-1.5:LRA=11,aresample=48000,apad=whole_dur={dur:.3f}",'-ac','1','renders/voice.wav'],check=True)
st = {l['shot']: s for s, l in zip(t['starts'], t['lines'])}
subprocess.run([sys.argv[1], 'music.py', str(dur), 'renders/music.wav', f"0.15,{st['rename'] + 0.1:.2f},{st['gods'] - 0.1:.2f},{st['finale'] + 0.1:.2f},{dur - 2.6:.2f}"], check=True)
subprocess.run(['ffmpeg','-y','-v','error','-i','renders/voice.wav','-i','renders/music.wav','-filter_complex',
                '[1:a]aresample=48000,volume=0.20[m];[0:a][m]amix=inputs=2:duration=first:normalize=0,alimiter=limit=0.95','-ar','48000','mg/public/narration.wav'],check=True)
print('AUDIO_OK')
PY
  cp brief/timing.json brief/labels.json mg/src/; cp ../tirumala-ghat/brand/logo_wm.png mg/public/logo_wm.png
  ln -sfn /opt/reel/sv/reels/follow-the-salt/mg/node_modules mg/node_modules
  (cd mg && npx remotion render src/index.ts Main out/final.mp4 --concurrency=4 --log=error)
  ffmpeg -y -v error -i mg/out/final.mp4 -c:v libx264 -preset slow -crf 20 -maxrate 9000k -bufsize 18000k -pix_fmt yuv420p -c:a aac -b:a 192k -movflags +faststart renders/tirumala_stay.mp4
  aws s3 cp --only-show-errors renders/tirumala_stay.mp4 s3://claude-reels-730335199669/reels/tirumala-guesthouses-telugu.mp4 && echo S3_OK
  python3 - <<'PY'
import json, subprocess
T = json.load(open('brief/timing.json')); ts = [s + d * 0.6 for s, d in zip(T['starts'], T['durs'])]
for i, t in enumerate(ts): subprocess.run(['ffmpeg','-y','-v','error','-ss',f'{t:.2f}','-i','renders/tirumala_stay.mp4','-frames:v','1','-vf','scale=270:480',f'renders/fin_{i:02d}.jpg'])
subprocess.run('ffmpeg -y -v error -pattern_type glob -i "renders/fin_*.jpg" -vf tile=7x2 -frames:v 1 renders/final_sheet.jpg', shell=True)
PY
  aws s3 cp --only-show-errors renders/final_sheet.jpg s3://claude-reels-730335199669/preview/stay_final_sheet.jpg
  echo ALLDONE
fi
