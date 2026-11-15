# kill running render, rebuild, drop frames of stations whose occluders changed, render what is missing
pkill -f "scene/sugar.blend" ; pkill -f go.sh; sleep 3
W=/opt/reel/sv/reels/follow-the-sugar; cd $W
export ZA_FBX=/opt/reel/za/Resources/Models/FBX/ RAJU_BLEND=/opt/reel/raju.blend
B=/opt/reel/blender/blender
$B -b --python build.py > /tmp/sbuild.log 2>&1; grep -E "^built|Traceback|Error" /tmp/sbuild.log | cut -c1-120
python3 - <<'PY'
import json, os
st = json.load(open('brief/stations.json'))
for n in ('vessels', 'pancreas', 'pancreas_tired', 'vessels_stuck', 'kidney'):
    a = st['offset'][n]
    for f in range(a, a + st['frames'][n]):
        p = f'renders/seq/f_{f:05d}.jpg'
        if os.path.exists(p): os.remove(p)
PY
N=$(python3 -c "import json;print(json.load(open('brief/stations.json'))['end'])")
python3 - > /tmp/todo_ranges.txt <<PY
import os
miss=[f for f in range(1,$N+1) if not os.path.exists(f'renders/seq/f_{f:05d}.jpg')]
k=len(miss)//3
parts=[miss[:k],miss[k:2*k],miss[2*k:]]
for p in parts: print(p[0], p[-1])
PY
cat /tmp/todo_ranges.txt
while read s e; do $B -b scene/sugar.blend -P /opt/reel/eevee.py -o "$W/renders/seq/f_#####" -s $s -e $e -a > /tmp/rr_$s.log 2>&1 & done < /tmp/todo_ranges.txt
wait; echo RENDERED $(ls renders/seq | wc -l) of $N
python3 cut.py
bash mg.sh
echo ALLDONE
