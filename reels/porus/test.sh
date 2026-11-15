W=/opt/reel/sv/reels/porus; cd $W; B=/opt/reel/blender/blender
$B -b --python build.py > /tmp/pbuild.log 2>&1; grep -E "^built|^river|Traceback|Error" /tmp/pbuild.log | cut -c1-200; grep -A6 Traceback /tmp/pbuild.log | head -12
python3 - > /tmp/pframes.txt <<'PY'
import json; t=json.load(open('brief/timing.json')); out=[]
for i,(s,d) in enumerate(zip(t['starts'],t['durs'])): out.append(str(round((s+d*0.6)*30)+1))
print(','.join(out))
PY
rm -rf renders/test; mkdir -p renders/test
$B -b scene/porus.blend -P /opt/reel/eevee.py -o "$W/renders/test/t_#####" -f $(cat /tmp/pframes.txt) > /tmp/ptest.log 2>&1
python3 - <<'PY'
import subprocess, glob
for f in sorted(glob.glob('renders/test/t_*.jpg')):
    raw=subprocess.run(['ffmpeg','-v','error','-i',f,'-vf','scale=54:96','-f','rawvideo','-pix_fmt','rgb24','-'],capture_output=True).stdout
    px=[raw[i:i+3] for i in range(0,len(raw),3)]; W=54
    def st(sel): return tuple(round(sum(p[k] for p in sel)/len(sel)) for k in range(3))
    print(f[-9:-4],'top',st(px[:W*24]),'mid',st(px[W*36:W*60]),'bot',st(px[W*72:]))
PY
