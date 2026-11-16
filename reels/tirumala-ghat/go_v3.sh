# Version 3: whole script re-voiced in one pass (hill names slow, roads introduced before the twist); unchanged shots are
# retimed from the version 2 frames; hills, seven, cart_track and the closing shot are rendered again.
W=/opt/reel/sv/reels/tirumala-ghat; cd $W; B=/opt/reel/blender/blender; O=/opt/reel/share/e1376f7f43dd
PY=$(ls /opt/reel/blender/*/python/bin/python3* | head -1)
[ -f brief/timing_v2.json ] || cp brief/timing.json brief/timing_v2.json
[ -d audio_te_v2 ] || cp -r audio_te audio_te_v2
python3 plan.py > /dev/null
python3 -u voice_swaram.py make > /opt/reel/swmake3.log 2>&1
F=/home/ubuntu/Swaram/output/narrations/$(python3 -c "import json;print(json.load(open('audio_te/narrate.json'))['audio_url'].split('/')[-1])")
cp "$F" audio_te/full.wav && python3 voice_swaram.py split audio_te/full.wav >> /opt/reel/swmake3.log 2>&1
tail -1 /opt/reel/swmake3.log; cat brief/extra_times.json; echo
grep -q SPLIT_DONE /opt/reel/swmake3.log || { echo VOICE_FAILED; exit 1; }
$B -b --python build.py > /opt/reel/gbuild3.log 2>&1
grep -E "^built|^TEMPLE|Traceback|Error" /opt/reel/gbuild3.log | cut -c1-400; grep -A14 Traceback /opt/reel/gbuild3.log | head -18
python3 - <<'PY'
import json, os
o = json.load(open('brief/timing_v2.json')); n = json.load(open('brief/timing.json'))
def table(t): return {l['shot']: (round(s * 30) + 1, round((s + d) * 30)) for s, d, l in zip(t['starts'], t['durs'], t['lines'])}
Ot, Nt = table(o), table(n); os.makedirs('renders/seq3', exist_ok=True); c = 0
for sh, (a, b) in Nt.items():
    if sh in ('hills', 'seven', 'govinda', 'cart_track') or sh not in Ot: continue
    oa, ob = Ot[sh]; Ln, Lo = b - a + 1, ob - oa + 1
    for k in range(Ln):
        src = f'renders/seq2/f_{oa + min(Lo - 1, int(k * Lo / Ln)):05d}.jpg'; dst = f'renders/seq3/f_{a + k:05d}.jpg'
        if os.path.exists(src) and not os.path.exists(dst): os.link(src, dst); c += 1
print('linked', c, 'of', n['end'])
PY
N=$(python3 -c "import json;print(json.load(open('brief/timing.json'))['end'])")
for try in 1 2 3; do
  [ $(ls renders/seq3 | wc -l) -ge $N ] && break
  $B -b scene/ghat3.blend -P /opt/reel/eevee.py -o "$W/renders/seq3/f_#####" -s 1 -e $N -a > /opt/reel/gp3all.log 2>&1
done
echo RENDERED $(ls renders/seq3 | wc -l) of $N
mkdir -p mg/public mg/out
ffmpeg -y -v error -framerate 30 -i renders/seq3/f_%05d.jpg -vf "eq=saturation=1.12:contrast=1.03" -c:v libx264 -preset medium -crf 17 -pix_fmt yuv420p mg/public/bg.mp4
python3 - "$PY" <<'PY'
import json, subprocess, os, sys
p = json.load(open('brief/plan.json')); t = json.load(open('brief/timing.json'))
subprocess.run(['ffmpeg','-y','-v','error','-f','lavfi','-i','anullsrc=r=44100:cl=mono','-t',str(p['gap']),'renders/gap.wav'],check=True)
open('renders/a.txt','w').write(''.join(f"file '{os.path.abspath(l['audio'])}'\nfile '{os.path.abspath('renders/gap.wav')}'\n" for l in p['lines']))
subprocess.run(['ffmpeg','-y','-v','error','-f','concat','-safe','0','-i','renders/a.txt','-af','loudnorm=I=-14:TP=-1.5:LRA=11','-ar','48000','renders/voice.wav'],check=True)
st = {l['shot']: s for s, l in zip(t['starts'], t['lines'])}; dur = t['end'] / 30
subprocess.run([sys.argv[1], 'music.py', str(dur), 'renders/music.wav', f"0.15,{st['seven'] + 0.1:.2f},{st['govinda'] - 0.2:.2f},{dur - 2.6:.2f}"], check=True)
subprocess.run(['ffmpeg','-y','-v','error','-i','renders/voice.wav','-i','renders/music.wav','-filter_complex',
                '[1:a]aresample=48000,volume=0.20[m];[0:a][m]amix=inputs=2:duration=longest:normalize=0,alimiter=limit=0.95','-ar','48000','mg/public/narration.wav'],check=True)
print('AUDIO_OK')
PY
cp brief/timing.json brief/labels.json mg/src/
(cd mg && npx remotion render src/index.ts Main out/final3.mp4 --concurrency=4 --log=error)
ffmpeg -y -v error -i mg/out/final3.mp4 -c:v libx264 -preset veryfast -crf 26 -maxrate 4500k -bufsize 9000k -pix_fmt yuv420p -c:a aac -b:a 160k -movflags +faststart /opt/reel/v3small.mp4
aws s3 cp /opt/reel/v3small.mp4 s3://claude-reels-730335199669/reels/tirumala-ghat-telugu-v3.mp4 --region ap-south-1 --quiet && echo S3_OK
D=$O/v3f; rm -rf $D; mkdir -p $D; for tt in 003 009 012 015 018 021 040 055; do ffmpeg -y -v error -ss $tt -i /opt/reel/v3small.mp4 -frames:v 1 -vf scale=540:960 -q:v 4 $D/s_$tt.jpg; done
ffmpeg -y -v error -pattern_type glob -i "$D/s_*.jpg" -vf "scale=270:480,tile=8x1" -frames:v 1 -q:v 4 $D/all.jpg
ffprobe -v error -show_entries format=duration,size -of csv=p=0 /opt/reel/v3small.mp4; echo ALLDONE3
