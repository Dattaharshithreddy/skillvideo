#!/bin/bash
# Full pipeline on the GPU box. Usage: bash run.sh [stage]   stages: setup raju tts build test render encode mg all
set -e
R=/opt/reel; W=$(cd "$(dirname "$0")" && pwd); cd "$W"
B=$R/blender/blender
export ZA_FBX=$R/za/Resources/Models/FBX/ RAJU_BLEND=$R/raju.blend
stage=${1:-all}
log(){ echo "[$(date +%H:%M:%S)] $*"; }
if [[ $stage == setup || $stage == all ]]; then
  log setup
  for w in Black ExtraBold SemiBold Medium; do f=/usr/share/fonts/truetype/poppins/Poppins-$w.ttf; [ -f $f ] || curl -sSL -o $f https://github.com/google/fonts/raw/main/ofl/poppins/Poppins-$w.ttf; done; fc-cache -f >/dev/null
  if ! command -v node >/dev/null || [[ $(node -v | cut -c2-3) -lt 20 ]]; then curl -fsSL https://deb.nodesource.com/setup_20.x | bash - >/dev/null && apt-get install -y -qq nodejs >/dev/null; fi
  (cd mg && npm install --no-audit --no-fund >/dev/null 2>&1 && npx remotion browser ensure >/dev/null 2>&1 || true)
fi
if [[ $stage == raju || $stage == all ]]; then log raju; $B -b --python raju_make.py > $R/raju_make.log 2>&1; grep -E "FAIL|DONE" $R/raju_make.log | tail -3; fi
if [[ $stage == tts || $stage == all ]]; then log tts; mkdir -p audio; $R/venv/bin/python tts.py $R/kokoro; python3 timing.py; fi
if [[ $stage == build || $stage == all ]]; then log build; mkdir -p scene; $B -b --python build.py > $R/build.log 2>&1; grep -E "^built|Error|Traceback" $R/build.log | cut -c1-200; fi
if [[ $stage == test ]]; then
  log test; mkdir -p renders
  for f in 120 260 450 640 830 1000 1230 1480 1670 1880 2100 2250 2420; do
    $B -b scene/salt.blend -o "$W/renders/test_####" -f $f -- --cycles-device OPTIX > /dev/null 2>&1
  done; ls renders | head -20
fi
if [[ $stage == render || $stage == all ]]; then log render; mkdir -p renders/seq; $B -b scene/salt.blend -o "$W/renders/seq/f_#####" -a -- --cycles-device OPTIX > $R/render.log 2>&1; log rendered $(ls renders/seq | wc -l); fi
if [[ $stage == encode || $stage == all ]]; then
  log encode; mkdir -p out
  ffmpeg -v error -y -framerate 30 -i renders/seq/f_%05d.jpg -c:v libx264 -preset slow -crf 16 -pix_fmt yuv420p out/bg.mp4
  python3 reel_captions.py brief/plan.json out > /dev/null
fi
if [[ $stage == mg || $stage == all ]]; then
  log mg; python3 timing.py; cp out/bg.mp4 mg/public/bg.mp4 2>/dev/null || (mkdir -p mg/public && cp out/bg.mp4 mg/public/); cp out/narration.wav mg/public/
  (cd mg && npx remotion render src/index.ts Main out/final.mp4 --concurrency=4 --log=error)
  cp mg/out/final.mp4 out/final.mp4
  aws s3 cp out/final.mp4 s3://claude-reels-730335199669/reels/follow-the-salt.mp4 --region ap-south-1 >/dev/null
  log done
fi
