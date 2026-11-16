W=/opt/reel/sv/reels/porus; cd $W; B=/opt/reel/blender/blender
BAD=$(for f in renders/mseq/f_*.jpg; do ffmpeg -v error -i $f -f null - 2>&1 | grep -q . && echo $f; done | sed 's/.*f_0*\([0-9]*\).jpg/\1/' | paste -sd,)
echo BAD=$BAD
if [ -n "$BAD" ]; then for n in $(echo $BAD | tr , ' '); do rm -f renders/mseq/f_$(printf %05d $n).jpg; done
$B -b scene/porus_mini.blend -P /opt/reel/eevee.py -o "$W/renders/mseq/f_#####" -f $BAD > /tmp/pmfix.log 2>&1; fi
echo FIXED $(ls renders/mseq | wc -l)
bash post_mini.sh > /opt/reel/pmpost.log 2>&1
