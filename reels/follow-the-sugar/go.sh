# Full Follow-the-Sugar pipeline after voice.py: stations -> build -> render -> cut -> remotion -> share
set -x
W=/opt/reel/sv/reels/follow-the-sugar; cd $W
export ZA_FBX=/opt/reel/za/Resources/Models/FBX/ RAJU_BLEND=/opt/reel/raju.blend
B=/opt/reel/blender/blender
python3 stations.py
$B -b --python build.py > /tmp/sbuild.log 2>&1; grep -E "^built|Traceback|Error" /tmp/sbuild.log | cut -c1-200
mkdir -p renders/seq
N=$(python3 -c "import json;print(json.load(open('brief/stations.json'))['end'])")
A=$((N/3)); C=$((2*N/3))
$B -b scene/sugar.blend -P /opt/reel/eevee.py -o "$W/renders/seq/f_#####" -s 1 -e $A -a > /tmp/sp1.log 2>&1 &
$B -b scene/sugar.blend -P /opt/reel/eevee.py -o "$W/renders/seq/f_#####" -s $((A+1)) -e $C -a > /tmp/sp2.log 2>&1 &
$B -b scene/sugar.blend -P /opt/reel/eevee.py -o "$W/renders/seq/f_#####" -s $((C+1)) -e $N -a > /tmp/sp3.log 2>&1 &
wait; echo RENDERED $(ls renders/seq | wc -l) of $N
python3 cut.py
bash mg.sh
echo ALLDONE
