set -x
W=/opt/reel/sv/reels/tirumala-ghat; cd $W; B=/opt/reel/blender/blender
[ "$1" = "skipbuild" ] || $B -b --python build.py > /opt/reel/gbuild.log 2>&1
grep -E "^built|^CLOSE|Traceback" /opt/reel/gbuild.log | cut -c1-200
N=$(python3 -c "import json;print(json.load(open('brief/timing.json'))['end'])")
rm -rf renders/seq; mkdir -p renders/seq; A=$((N/3)); C=$((2*N/3))
$B -b scene/ghat.blend -P /opt/reel/eevee.py -o "$W/renders/seq/f_#####" -s 1 -e $A -a > /opt/reel/gp1.log 2>&1 &
$B -b scene/ghat.blend -P /opt/reel/eevee.py -o "$W/renders/seq/f_#####" -s $((A+1)) -e $C -a > /opt/reel/gp2.log 2>&1 &
$B -b scene/ghat.blend -P /opt/reel/eevee.py -o "$W/renders/seq/f_#####" -s $((C+1)) -e $N -a > /opt/reel/gp3.log 2>&1 &
wait; echo RENDERED $(ls renders/seq | wc -l) of $N
mkdir -p mg/public mg/out
ffmpeg -y -v error -framerate 30 -i renders/seq/f_%05d.jpg -c:v libx264 -preset medium -crf 17 -pix_fmt yuv420p mg/public/bg.mp4
python3 - <<'PY'
import json, subprocess, os
p = json.load(open('brief/plan.json'))
subprocess.run(['ffmpeg','-y','-v','error','-f','lavfi','-i','anullsrc=r=44100:cl=mono','-t',str(p['gap']),'renders/gap.wav'],check=True)
open('renders/a.txt','w').write(''.join(f"file '{os.path.abspath(l['audio'])}'\nfile '{os.path.abspath('renders/gap.wav')}'\n" for l in p['lines']))
subprocess.run(['ffmpeg','-y','-v','error','-f','concat','-safe','0','-i','renders/a.txt','-af','loudnorm=I=-14:TP=-1.5:LRA=11','-ar','48000','mg/public/narration.wav'],check=True)
PY
cp brief/timing.json brief/labels.json mg/src/
ln -sfn /opt/reel/sv/reels/follow-the-salt/mg/node_modules mg/node_modules
(cd mg && npx remotion render src/index.ts Main out/final.mp4 --concurrency=4 --log=error)
O=/opt/reel/share/e1376f7f43dd
ffmpeg -y -v error -i mg/out/final.mp4 -c:v libx264 -preset fast -crf 23 -pix_fmt yuv420p -c:a aac -b:a 160k -movflags +faststart $O/tirumala_telugu.mp4
aws s3 cp mg/out/final.mp4 s3://claude-reels-730335199669/reels/tirumala-ghat-telugu.mp4 --region ap-south-1 --quiet && echo S3_OK
echo ALLDONE
