W=/opt/reel/sv/reels/porus; cd $W; B=/opt/reel/blender/blender
$B -b --python build.py > /tmp/pbuild.log 2>&1; grep -E "^built|Traceback|Error" /tmp/pbuild.log | cut -c1-200; grep -A8 Traceback /tmp/pbuild.log | head -12
$B -b --python enrich.py > /tmp/penrich.log 2>&1; grep -E "^veg|^tris|^skip|ENRICHED|Traceback|Error" /tmp/penrich.log | cut -c1-400; grep -A10 Traceback /tmp/penrich.log | head -14
python3 - > /tmp/lframes.txt <<'PY'
import json; t=json.load(open('brief/timing.json')); out=[]
for i,(s,d) in enumerate(zip(t['starts'],t['durs'])): out.append(str(round((s+d*0.6)*30)+1))
print(','.join(out))
PY
rm -rf renders/look; mkdir -p renders/look
/usr/bin/time -f "render %e s" $B -b scene/porus_rich.blend -P /opt/reel/eevee.py -o "$W/renders/look/l_#####" -f $(cat /tmp/lframes.txt) > /tmp/plook.log 2>&1; tail -1 /tmp/plook.log
grep -E "Error|out of memory" /tmp/plook.log | head -3; ls renders/look | wc -l
