# Three takes of the Datta narration, then pick per sentence the take closest to his reference voice.
set -x
W=/opt/reel/sv/reels/tirumala-stay; cd $W
python3 plan.py
for k in 1 2 3; do python3 -u voice_swaram.py make $k > /opt/reel/tsv_$k.log 2>&1; grep -E "MAKE_DONE|Error|Traceback" /opt/reel/tsv_$k.log; done
cp audio/narrate1.json audio/narrate.json
PY=$(grep -l resemblyzer /opt/*/venv/bin/python* 2>/dev/null | head -1)
for p in /opt/wan/venv/bin/python /opt/reel/geovenv/bin/python; do $p -c "import resemblyzer" 2>/dev/null && PY=$p && break; done
REF=$(ls -d /opt/reel/myvoice/*/ 2>/dev/null | head -1); [ -d /opt/reel/myvoice/ref ] && REF=/opt/reel/myvoice/ref
echo "PY=$PY REF=$REF"
if [ -n "$PY" ]; then $PY select_takes.py ${REF%/} 1 2 3 > /opt/reel/tsv_sel.log 2>&1; tail -4 /opt/reel/tsv_sel.log; else python3 voice_swaram.py split audio/full1.wav; fi
ls -la audio
echo VOICE_DONE
