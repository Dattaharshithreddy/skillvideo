#!/bin/bash
# Full Puru reel: timing -> label tracks -> GPU render of all 12 shots -> music -> Telugu motion design -> reel.mp4
# env: BL (blender binary), NGPU (GPUs to use, default 1), SPP (default 40), NARR (narration wav, optional),
#      SENTS (narr/sentences.json from voice_porus.py, optional), CHROME (browser for Remotion, optional), PCT (resolution %, default 100)
set -e
cd "$(dirname "$0")"; P=$(pwd)
BL=${BL:-blender}; NGPU=${NGPU:-1}; SPP=${SPP:-40}; PCT=${PCT:-100}
OUT=$P/mini3d/out3; mkdir -p $OUT mg/public
if [ -n "$SENTS" ] && [ -f "$SENTS" ]; then python3 build_timing.py "$SENTS"; else python3 build_timing.py; fi
python3 -c "import json;t=json.load(open('mg/src/timing.json'));print('\n'.join(f\"{l['shot']} {n}\" for l,n in zip(t['lines'],t['nf'])))" > $OUT/shots.txt
echo "== label tracks"
while read -r s n; do
  [ -f $OUT/tracks_$s.json ] && [ "$(python3 -c "import json;print(len(json.load(open('$OUT/tracks_$s.json'))))")" = "$n" ] && continue
  ASSETS=$P/assets OUT=$OUT DEVICE=CPU TRACK=1 $BL -b -P mini3d/diorama3.py -- $s $n < /dev/null > $OUT/track_$s.log 2>&1 || { tail -20 $OUT/track_$s.log; exit 1; }
done < $OUT/shots.txt
python3 build_labels.py $OUT
echo "== render ($NGPU GPU)"
render_shot() {   # shot frames gpu
  local s=$1 n=$2 g=$3
  local have=$(ls $OUT/$s/[0-9]*.jpg 2>/dev/null | wc -l); local st=${STEP:-1}
  if [ "$have" -lt $(( (n + st - 1) / st )) ]; then
    ASSETS=$P/assets OUT=$OUT DEVICE=GPU GPU_INDEX=$g SPP=$SPP PCT=$PCT $BL -b -P mini3d/diorama3.py -- $s $n < /dev/null > $OUT/render_$s.log 2>&1 || { tail -30 $OUT/render_$s.log; return 1; }
  fi
  ffmpeg -nostdin -y -v error -framerate $((30 / st)) -pattern_type glob -i "$OUT/$s/[0-9]*.jpg" -vf "framerate=30,scale=1080:1920:flags=lanczos,format=yuv420p,tpad=stop_mode=clone:stop_duration=1" -frames:v $n -c:v libx264 -preset medium -crf 16 -r 30 $OUT/$s.tmp.mp4 && mv $OUT/$s.tmp.mp4 $OUT/$s.mp4
  echo "shot $s done ($n frames) on GPU $g"
}
i=0; pids=()
while read -r s n; do
  g=$((i % NGPU))
  if [ $NGPU -gt 1 ]; then
    while [ $(jobs -rp | wc -l) -ge $NGPU ]; do sleep 5; done
    ( render_shot $s $n $g ) & pids+=($!)
  else render_shot $s $n 0; fi
  i=$((i+1))
done < $OUT/shots.txt
wait
: > $OUT/concat.txt; while read -r s n; do echo "file '$OUT/$s.mp4'" >> $OUT/concat.txt; done < $OUT/shots.txt
ffmpeg -y -v error -f concat -safe 0 -i $OUT/concat.txt -c copy mg/public/bg.mp4
echo "== music + narration"
python3 music.py mg/src/timing.json mg/public/music.wav
AUD='""'
if [ -n "$NARR" ] && [ -f "$NARR" ]; then ffmpeg -y -v error -i "$NARR" -ar 48000 -ac 2 mg/public/narration.wav; AUD='"narration.wav"'; fi
echo "== Telugu motion design"
cd mg; [ -d node_modules ] || npm install --no-audit --no-fund --loglevel=error
BX=""; [ -n "$CHROME" ] && BX="--browser-executable=$CHROME"
npx remotion render src/index.ts Reel out/reel.mp4 --props="{\"bg\":\"bg.mp4\",\"audio\":$AUD,\"music\":\"music.wav\",\"preview\":false}" --concurrency=${CONC:-4} --crf=17 $BX --log=error
ffmpeg -y -v error -i out/reel.mp4 -c copy -movflags +faststart out/puru_reel.mp4
echo "REEL_DONE $(pwd)/out/puru_reel.mp4"
