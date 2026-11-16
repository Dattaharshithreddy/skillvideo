# Know Diabetes: voice -> cut from the sugar station render -> Remotion -> share + S3
W=/opt/reel/sv/reels/know-diabetes; cd $W; O=/opt/reel/share/e1376f7f43dd
if [ "$1" != "novoice" ]; then python3 plan.py && python3 -u voice.py > /opt/reel/kd_voice.log 2>&1; tail -2 /opt/reel/kd_voice.log; grep -q VOICE_DONE /opt/reel/kd_voice.log || exit 1; fi
python3 cut.py || exit 1
ln -sfn /opt/reel/sv/reels/follow-the-salt/mg/node_modules mg/node_modules; mkdir -p mg/out
(cd mg && npx remotion render src/index.ts Main out/final.mp4 --concurrency=4 --log=error)
ffmpeg -y -v error -i mg/out/final.mp4 -c:v libx264 -preset veryfast -crf 25 -maxrate 4500k -bufsize 9000k -pix_fmt yuv420p -c:a aac -b:a 160k -movflags +faststart /opt/reel/kd_small.mp4
aws s3 cp /opt/reel/kd_small.mp4 s3://claude-reels-730335199669/reels/know-diabetes.mp4 --region ap-south-1 --quiet && echo S3_OK
python3 - <<'PY'
import json, subprocess
t = json.load(open('mg/src/timing.json')); ins = []
for k, (s, d) in enumerate(zip(t['starts'], t['durs'])):
    f = f'/tmp/kd{k}.jpg'
    subprocess.run(['ffmpeg','-y','-v','error','-ss',f'{s + d * 0.75:.2f}','-i','/opt/reel/kd_small.mp4','-frames:v','1','-vf','scale=360:640',f], check=True); ins += ['-i', f]
import os; os.makedirs('/opt/reel/share/e1376f7f43dd/kd', exist_ok=True)
subprocess.run(['ffmpeg','-y','-v','error'] + ins + ['-filter_complex', f'xstack=inputs={len(ins)//2}:layout=' + '|'.join(f'{(k % 7) * 360}_{(k // 7) * 640}' for k in range(len(ins)//2)), '-q:v','3','/opt/reel/share/e1376f7f43dd/kd/all.jpg'], check=True)
PY
ffprobe -v error -show_entries format=duration,size -of csv=p=0 /opt/reel/kd_small.mp4; echo KD_DONE
