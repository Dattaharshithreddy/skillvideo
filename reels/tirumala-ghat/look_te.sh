# Test the new look before the Telugu voice exists: silent stand-in clips sized from word counts (replaced by real voice later).
W=/opt/reel/sv/reels/tirumala-ghat; cd $W; B=/opt/reel/blender/blender
python3 plan.py > /dev/null; mkdir -p audio_te
python3 - <<'PY'
import json, os, subprocess
p = json.load(open('brief/plan.json'))
for l in p['lines']:
    if os.path.exists(l['audio']) and not os.path.exists(l['audio'] + '.placeholder'): continue
    d = 0.5 * len(l['tts'].split()) + 0.8
    subprocess.run(['ffmpeg', '-y', '-v', 'error', '-f', 'lavfi', '-i', 'anullsrc=r=44100:cl=mono', '-t', f'{d:.2f}', l['audio']], check=True)
    open(l['audio'] + '.placeholder', 'w').write('silent stand-in')
PY
[ -f geo/places.json ] || /opt/reel/geovenv/bin/python geo_places.py
$B -b --python build.py > /tmp/gbuild.log 2>&1; grep -E "^built|Traceback|Error" /tmp/gbuild.log | cut -c1-300; grep -A8 Traceback /tmp/gbuild.log | head -12
python3 - > /tmp/tframes.txt <<'PY'
import json; t = json.load(open('brief/timing.json')); out = []
for i, (s, d) in enumerate(zip(t['starts'], t['durs'])):
    for q in ((0.1, 0.5, 0.95) if i == 0 else (0.6,)): out.append(str(round((s + d * q) * 30) + 1))
print(','.join(out))
PY
rm -rf renders/test; mkdir -p renders/test
$B -b scene/ghat.blend -P /opt/reel/eevee.py -o "$W/renders/test/t_#####" -f $(cat /tmp/tframes.txt) > /tmp/gtest.log 2>&1
ls renders/test | wc -l
# overlay stills on top of the test frames
mkdir -p mg/public mg/out; cp brief/timing.json brief/labels.json mg/src/; ln -sfn /opt/reel/sv/reels/follow-the-salt/mg/node_modules mg/node_modules
fc-list | grep -ci telugu
D=/opt/reel/share/e1376f7f43dd/tl2; rm -rf $D; mkdir -p $D
for f in $(cat /tmp/tframes.txt | tr ',' ' '); do
  n=$(printf "%05d" $f)
  (cd mg && npx remotion still src/index.ts Main out/o_$n.png --frame=$((f-1)) --props='{"bg":"bg.mp4","audio":"narration.wav","preview":true}' --log=error) 
  ffmpeg -y -v error -i renders/test/t_$n.jpg -i mg/out/o_$n.png -filter_complex "[1]colorkey=0x26304a:0.35:0.2[o];[0][o]overlay" -vf scale=540:960 $D/s_$n.jpg 2>/dev/null || cp renders/test/t_$n.jpg $D/s_$n.jpg
done
ls $D | wc -l; echo LOOK_TE_DONE
