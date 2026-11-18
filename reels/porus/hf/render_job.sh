#!/usr/bin/env bash
# Hugging Face Job: full-quality Puru reel (12 Cycles shots on the GPU, Telugu motion design, owner's narration).
# Needs: image ubuntu:22.04; bucket mounted at /out (renders resume from it); private dataset with key.txt at /priv.
# The narration is AES-encrypted on the Swaram porus-src branch and only decrypted inside the job.
set -x
export DEBIAN_FRONTEND=noninteractive
apt-get update -qq && apt-get install -y -qq git curl xz-utils ca-certificates ffmpeg python3 openssl libegl1 libgl1 libxrender1 libxi6 \
  libxkbcommon0 libsm6 libxxf86vm1 libxfixes3 libx11-6 libnss3 libatk1.0-0 libatk-bridge2.0-0 libcups2 libdrm2 libxcomposite1 \
  libxdamage1 libxrandr2 libgbm1 libpango-1.0-0 libcairo2 libasound2 >/dev/null 2>&1
UA='Mozilla/5.0 (X11; Linux x86_64) Chrome/124'
for B in https://mirrors.ocf.berkeley.edu/blender/release https://ftp.halifax.rwth-aachen.de/blender/release https://download.blender.org/release; do
  curl -fsSL -A "$UA" $B/Blender4.2/blender-4.2.3-linux-x64.tar.xz -o /tmp/b.tar.xz && break
done
mkdir -p /opt/blender && tar -xf /tmp/b.tar.xz -C /opt/blender --strip-components=1; /opt/blender/blender -b --version | head -1
curl -fsSL https://nodejs.org/dist/v20.18.0/node-v20.18.0-linux-x64.tar.xz | tar -xJ -C /opt && export PATH=/opt/node-v20.18.0-linux-x64/bin:$PATH; node -v
nvidia-smi --query-gpu=name,memory.total --format=csv
cd "$(dirname "$0")/.."                       # reels/porus
mkdir -p narr /out/out3 && rm -rf mini3d/out3 && ln -s /out/out3 mini3d/out3
curl -fsSL https://raw.githubusercontent.com/Dattaharshithreddy/Swaram/porus-src/narr.flac.enc -o /tmp/n.enc
openssl enc -d -aes-256-cbc -pbkdf2 -in /tmp/n.enc -out /tmp/n.flac -pass file:/priv/key.txt && ffmpeg -v error -y -i /tmp/n.flac narr/narration.wav && rm /tmp/n.enc /tmp/n.flac
(cd mg && npm install --no-audit --no-fund --loglevel=error && npx remotion browser ensure >/dev/null) &
NPMPID=$!
export BL=/opt/blender/blender NGPU=${NGPU:-1} SPP=${SPP:-40} CONC=${CONC:-6} NARR=narr/narration.wav SENTS=hf/sentences.json
wait $NPMPID
bash render_all.sh 2>&1 | grep -vE 'INFO|^\s*$' | tee /out/render.log | grep -E "==|shot|REEL_DONE|rror|Traceback" 
cp mg/out/puru_reel.mp4 /out/puru_reel_final.mp4 && ls -la /out/puru_reel_final.mp4 && echo JOB_DONE
