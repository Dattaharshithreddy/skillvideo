W=/opt/reel/sv/reels/tirumala-ghat; cd $W; B=/opt/reel/blender/blender
$B -b --python build.py > /opt/reel/gbuild.log 2>&1; grep -E "^built|^CLOSE|Traceback|Error" /opt/reel/gbuild.log | cut -c1-300; grep -A12 Traceback /opt/reel/gbuild.log | head -16
python3 - > /opt/reel/cframes.txt <<'PY'
import json; t = json.load(open('brief/timing.json')); out = []
for i, (s, d, l) in enumerate(zip(t['starts'], t['durs'], t['lines'])):
    qs = (0.15, 0.6, 0.92) if l['shot'] in ('open', 'traffic', 'old_runs', 'cart_track', 'rockfall') else ((0.1, 0.9) if l['shot'] == 'hills' else (0.6,))
    for q in qs: out.append(str(round((s + d * q) * 30) + 1))
print(','.join(out))
PY
rm -rf renders/ctest; mkdir -p renders/ctest
/usr/bin/time -f "render %e s" $B -b scene/ghat.blend -P /opt/reel/eevee.py -o "$W/renders/ctest/c_#####" -f $(cat /opt/reel/cframes.txt) > /opt/reel/ctest.log 2>&1; tail -1 /opt/reel/ctest.log
grep -iE "error|out of memory" /opt/reel/ctest.log | head -3
D=/opt/reel/share/e1376f7f43dd/close; rm -rf $D; mkdir -p $D
cd renders/ctest && for f in c_*.jpg; do ffmpeg -y -v error -i $f -vf scale=540:960 -q:v 4 $D/$f; done
ffmpeg -y -v error -pattern_type glob -i 'c_*.jpg' -vf "scale=216:384,tile=7x3" -frames:v 1 -q:v 4 $D/all.jpg; ls $D | wc -l; echo CTEST_DONE
