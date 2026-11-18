#!/usr/bin/env bash
# Hugging Face Job: build the Tirumala guest-house miniature and render frames with Cycles on the GPU.
#   FRAMES="43,199,..."  -> stills into /out/$TAG/   (or)   START=1 END=980 -> sequence chunk into /out/$TAG/
# Needs: image ubuntu:22.04, bucket hf://buckets/HarshithReddy05/tirumala-reel mounted at /out.
set -x
export DEBIAN_FRONTEND=noninteractive
apt-get update -qq && apt-get install -y -qq git curl xz-utils ca-certificates ffmpeg python3 libegl1 libgl1 libxrender1 libxi6 \
  libxkbcommon0 libsm6 libxxf86vm1 libxfixes3 libx11-6 >/dev/null 2>&1
UA='Mozilla/5.0 (X11; Linux x86_64) Chrome/124'
for B in https://mirrors.ocf.berkeley.edu/blender/release https://ftp.halifax.rwth-aachen.de/blender/release https://download.blender.org/release; do
  T=$(curl -fsSL -A "$UA" $B/Blender4.5/ | grep -oE 'blender-4\.5\.[0-9]+-linux-x64\.tar\.xz' | sort -V | tail -1)
  [ -n "$T" ] && curl -fsSL -A "$UA" $B/Blender4.5/$T -o /tmp/b.tar.xz && break
done
mkdir -p /opt/reel/blender /opt/reel/assets && tar -xf /tmp/b.tar.xz -C /opt/reel/blender --strip-components=1
BL=/opt/reel/blender/blender; $BL -b --version | head -1
# Quaternius CC0 models (same library the AWS server used)
git clone -q --depth 1 --filter=blob:none --sparse https://github.com/trebeljahr/quaternius-showcase /opt/reel/assets/qs
cd /opt/reel/assets/qs && git sparse-checkout set public/glb >/dev/null 2>&1; ls public/glb | head -50
for d in modular_men modular_women; do [ -d public/glb/$d ] || { s=$(ls -d public/glb/${d}* 2>/dev/null | head -1); [ -n "$s" ] && ln -s "$(basename $s)" public/glb/$d; }; done
[ -n "$MFVIEWS" ] && $BL -b -P "$(dirname "$0")/mf_views.py" 2>&1 | grep MFVIEW
cd "$(dirname "$0")/.."            # reels/tirumala-stay
mkdir -p mf && cp -n /out/mf/b_*.glb mf/ 2>/dev/null; ls mf
[ -d /out/audio ] && mkdir -p audio && cp /out/audio/l*.wav audio/ 2>/dev/null
python3 hf/fake_audio.py
$BL -b --python build.py > /out/${TAG}_build.log 2>&1; grep -E "^built|MF BUILD|TEMPLE|Traceback|Error" /out/${TAG}_build.log | head; grep -A12 Traceback /out/${TAG}_build.log | head -20
cp brief/timing.json brief/labels.json /out/ 2>/dev/null
mkdir -p /out/$TAG
if [ "$FRAMES" = "auto" ]; then   # one key frame per shot (60% through it)
  FRAMES=$(python3 -c "
import json; t = json.load(open('brief/timing.json'))
print(','.join(str(round((s + d * 0.6) * 30) + 1) for s, d in zip(t['starts'], t['durs'])))"); echo "stills $FRAMES"
fi
if [ -n "$FRAMES" ]; then
  $BL -b scene/stay.blend -P hf/cycles_hq.py -o "/out/$TAG/f_#####" -f $FRAMES 2>&1 | grep -E "CYCLES|Saved|rror|Time:" | tail -40
else
  $BL -b scene/stay.blend -P hf/cycles_hq.py -o "/out/$TAG/f_#####" -s $START -e $END -a 2>&1 | grep -E "CYCLES|Saved|rror" | tail -20
fi
ls /out/$TAG | wc -l; echo RENDER_JOB_DONE
