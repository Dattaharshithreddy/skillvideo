pkill -f "scene/ghat.blend"; pkill -f go.sh; sleep 2
W=/opt/reel/sv/reels/tirumala-ghat; cd $W; B=/opt/reel/blender/blender
$B -b --python build.py > /tmp/gbuild.log 2>&1; grep -E "^built|Traceback" /tmp/gbuild.log | cut -c1-120
rm -rf renders/test; mkdir -p renders/test
$B -b scene/ghat.blend -P /opt/reel/eevee.py -o "$W/renders/test/t_#####" -f 100,300,700,1000,1300,1500,1700,1900,2250 > /tmp/gtest.log 2>&1
python3 - <<'PY'
import subprocess, glob
for f in sorted(glob.glob('renders/test/t_*.jpg')):
    raw=subprocess.run(['ffmpeg','-v','error','-i',f,'-vf','scale=54:96','-f','rawvideo','-pix_fmt','rgb24','-'],capture_output=True).stdout
    px=[raw[i:i+3] for i in range(0,len(raw),3)]; W=54
    def st(sel): return tuple(round(sum(p[k] for p in sel)/len(sel)) for k in range(3))
    print(f[-9:-4],'top',st(px[:W*24]),'mid',st(px[W*36:W*60]),'bot',st(px[W*72:]))
PY
