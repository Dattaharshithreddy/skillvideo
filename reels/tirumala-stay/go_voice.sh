# Three takes of the Datta narration; pick per sentence the take closest to his voice if a speaker model is available.
set -x
W=/opt/reel/sv/reels/tirumala-stay; cd $W
python3 plan.py
for k in 1 2 3; do python3 -u voice_swaram.py make $k > /opt/reel/tsv_$k.log 2>&1; grep -E "MAKE_DONE|Error|Traceback" /opt/reel/tsv_$k.log; done
cp audio/narrate1.json audio/narrate.json
PY=""; for p in /opt/reel/svenv/bin/python /opt/reel/venv/bin/python /opt/wan/venv/bin/python /opt/reel/geovenv/bin/python; do [ -x $p ] && $p -c "import resemblyzer" 2>/dev/null && PY=$p && break; done
REF=""; for d in /opt/reel/myvoice/ref /opt/reel/ref_datta /home/ubuntu/datta_ref /opt/reel/sv/reels/porus/ref; do [ -d $d ] && REF=$d && break; done
echo "PY=$PY REF=$REF"
if [ -n "$PY" ] && [ -n "$REF" ]; then $PY select_takes.py $REF 1 2 3 > /opt/reel/tsv_sel.log 2>&1; tail -4 /opt/reel/tsv_sel.log; fi
[ -f audio/l01.wav ] || python3 voice_swaram.py split audio/full1.wav
ls audio
echo VOICE_DONE
