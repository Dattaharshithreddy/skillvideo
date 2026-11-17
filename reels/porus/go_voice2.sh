set -x
W=/opt/reel/sv/reels/porus; cd $W
python3 plan_mini.py
for k in 1 2 3; do python3 -u voice_swaram.py make $k > /opt/reel/pv2_$k.log 2>&1; grep -E "MAKE_DONE|Error" /opt/reel/pv2_$k.log; done
echo TAKES_DONE
