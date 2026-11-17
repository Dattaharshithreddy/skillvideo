# full chain after the voice takes: select best takes -> encode prompts -> generate clips -> cut -> music -> remotion -> upload
set -x
W=/opt/reel/sv/reels/porus; cd $W; . /opt/wan/venv/bin/activate
python ai/prompts.py
REF=$(ls -d /var/lib/docker/volumes/swaram_voicebox-data/_data/mood_clips/*/ | head -1)
python select_takes.py $REF 1 2 3 > /opt/reel/pselect.log 2>&1; tail -3 /opt/reel/pselect.log
python ai/wan_encode.py > /opt/reel/pwenc.log 2>&1; tail -1 /opt/reel/pwenc.log
python ai/wan_gen.py > /opt/reel/pwgen.log 2>&1; tail -2 /opt/reel/pwgen.log
deactivate
python3 ai/cut_ai.py > /opt/reel/pcut.log 2>&1; tail -1 /opt/reel/pcut.log
B=/opt/reel/blender/blender
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
(cd mg && npx remotion render src/index.ts Main out/final_ai.mp4 --concurrency=4 --log=error)
aws s3 cp --only-show-errors mg/out/final_ai.mp4 s3://claude-reels-730335199669/reels/porus-miniature-ai-telugu.mp4 && echo S3_OK
python3 - <<'PY'
import json, subprocess
T = json.load(open('brief/timing.json'))
for i, (s, d) in enumerate(zip(T['starts'], T['durs'])):
    subprocess.run(['ffmpeg','-y','-v','error','-ss',f'{s + d * 0.5:.2f}','-i','mg/out/final_ai.mp4','-frames:v','1','-vf','scale=360:640',f'renders/ai_{i:02d}.jpg'])
subprocess.run('ffmpeg -y -v error -pattern_type glob -i "renders/ai_*.jpg" -vf tile=6x2 -frames:v 1 renders/ai_sheet.jpg', shell=True)
PY
aws s3 cp --only-show-errors renders/ai_sheet.jpg s3://claude-reels-730335199669/preview/ai_sheet.jpg
echo AI_ALLDONE
