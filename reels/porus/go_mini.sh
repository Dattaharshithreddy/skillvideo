set -x
W=/opt/reel/sv/reels/porus; cd $W; B=/opt/reel/blender/blender
$B -b --python build_mini.py > /tmp/pmbuild.log 2>&1; grep -E "^built|hidden|Traceback" /tmp/pmbuild.log | cut -c1-200
N=$(python3 -c "import json;print(json.load(open('brief/timing.json'))['end'])")
mkdir -p renders/mseq
$B -b scene/porus_mini.blend -P /opt/reel/eevee.py -o "$W/renders/mseq/f_#####" -s 1 -e $N -a > /tmp/pmrender.log 2>&1
while pgrep -f "porus_mini.blend" >/dev/null; do sleep 20; done
echo RENDERED $(ls renders/mseq | wc -l) of $N
mkdir -p mg/public mg/out
ffmpeg -y -v error -framerate 30 -i renders/mseq/f_%05d.jpg -c:v libx264 -preset medium -crf 17 -pix_fmt yuv420p mg/public/bg.mp4
$B -b --python-expr "import sys,runpy; sys.argv=['music_mini.py','renders/music.wav']; runpy.run_path('music_mini.py', run_name='__main__')" > /tmp/pmmusic.log 2>&1; grep music /tmp/pmmusic.log
python3 - <<'PY'
import json, subprocess, os
p = json.load(open('brief/plan.json')); T = json.load(open('brief/timing.json'))
open('renders/a.txt','w').write(''.join(f"file '{os.path.abspath(l['audio'])}'\n" for l in p['lines']))
subprocess.run(['ffmpeg','-y','-v','error','-f','concat','-safe','0','-i','renders/a.txt','-af',f"aresample=48000,apad=whole_dur={T['end']/30:.3f}",'-ac','1','renders/narr.wav'],check=True)
subprocess.run(['ffmpeg','-y','-v','error','-i','renders/narr.wav','-i','renders/music.wav','-filter_complex',
  '[0]loudnorm=I=-15:TP=-2:LRA=11[v];[1]aresample=48000,volume=0.22[m];[v][m]amix=inputs=2:duration=first:normalize=0,alimiter=limit=0.95',
  '-ar','48000','mg/public/narration.wav'],check=True)
PY
cp brief/timing.json mg/src/timing.json; cp ../tirumala-ghat/brand/logo_wm.png mg/public/logo_wm.png
ln -sfn /opt/reel/sv/reels/follow-the-salt/mg/node_modules mg/node_modules
(cd mg && npx remotion render src/index.ts Main out/final.mp4 --concurrency=4 --log=error)
ls -la mg/out/final.mp4
aws s3 cp --only-show-errors mg/out/final.mp4 s3://claude-reels-730335199669/reels/porus-miniature-telugu.mp4 && echo S3_OK
python3 - <<'PY'
import json, subprocess
T = json.load(open('brief/timing.json')); ts = [s + d * 0.55 for s, d in zip(T['starts'], T['durs'])]
for i, t in enumerate(ts): subprocess.run(['ffmpeg','-y','-v','error','-ss',f'{t:.2f}','-i','mg/out/final.mp4','-frames:v','1','-vf','scale=270:480',f'renders/fin_{i:02d}.jpg'])
subprocess.run('ffmpeg -y -v error -pattern_type glob -i "renders/fin_*.jpg" -vf tile=6x2 -frames:v 1 renders/final_sheet.jpg', shell=True)
PY
aws s3 cp --only-show-errors renders/final_sheet.jpg s3://claude-reels-730335199669/preview/final_sheet.jpg
echo MINI_ALLDONE
