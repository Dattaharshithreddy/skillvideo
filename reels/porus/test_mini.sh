W=/opt/reel/sv/reels/porus; cd $W; B=/opt/reel/blender/blender
$B -b --python build_mini.py > /tmp/pmbuild.log 2>&1; grep -E "^built|Traceback|Error" /tmp/pmbuild.log | cut -c1-300; grep -B2 -A12 Traceback /tmp/pmbuild.log | head -30
python3 - > /tmp/pmframes.txt <<'PY'
import json; t=json.load(open('brief/timing.json')); out=[]
for x in (0.15, 0.6):
    for i,(s,d) in enumerate(zip(t['starts'],t['durs'])): out.append(round((s+d*x)*30)+1)
print(','.join(map(str,sorted(out))))
PY
rm -rf renders/mtest; mkdir -p renders/mtest
/usr/bin/time -f "render %e s" $B -b scene/porus_mini.blend -P /opt/reel/eevee.py -o "$W/renders/mtest/t_#####" -f $(cat /tmp/pmframes.txt) > /tmp/pmtest.log 2>&1; tail -1 /tmp/pmtest.log
grep -E "Error|rror:" /tmp/pmtest.log | head -5
ffmpeg -y -v error -pattern_type glob -i 'renders/mtest/*.jpg' -vf "scale=270:480,tile=6x4" -frames:v 1 renders/mtest_sheet.jpg
aws s3 cp --only-show-errors renders/mtest_sheet.jpg s3://claude-reels-730335199669/preview/mtest_sheet.jpg && echo SHEET_UP
echo TEST_DONE
