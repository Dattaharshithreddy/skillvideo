#!/usr/bin/env bash
# Runs Model Forge (Hunyuan3D-2 + SDXL 2D art) on a GPU box and works through a jobs file.
#   JOBS=<path to jobs.json>  OUT=<output dir>  [IMAGE_MODEL=<sdxl id>]
# Outputs: $OUT/<name>.png (2d jobs) or $OUT/<name>.glb (+ <name>_input.png) for 3D jobs; logs in $OUT/_logs.
set -x
export DEBIAN_FRONTEND=noninteractive
mkdir -p "$OUT/_logs"
(apt-get update -qq && apt-get install -y -qq git curl libgl1 libglib2.0-0 libgomp1 libopengl0 libglu1-mesa libegl1 libxrender1 libxext6 libsm6 libxkbcommon0) >/dev/null 2>&1
[ -d /w/3dmodel ] || git clone -q --depth 1 https://github.com/Dattaharshithreddy/3dmodel /w/3dmodel
# private reference images: encrypted in git, key only in the private bucket (KEYFILE)
if [ -n "$KEYFILE" ] && [ -f "$KEYFILE" ]; then for f in "$(dirname "$JOBS")"/private/*.enc; do [ -f "$f" ] && openssl enc -d -aes-256-cbc -pbkdf2 -in "$f" -out "$OUT/$(basename "$f" .enc)" -pass file:"$KEYFILE"; done; fi
cd /w/3dmodel/server && PYTHON=python bash setup.sh > "$OUT/_logs/setup.log" 2>&1; tail -5 "$OUT/_logs/setup.log"
# one fresh server per job: the texture model leaks memory and the server dies after one textured job on 30 GB RAM
python - "$JOBS" > /tmp/jobsplit.txt <<'PY'
import json, sys
for i, j in enumerate(json.load(open(sys.argv[1]))['jobs']):
    p = f'/tmp/job_{i:02d}.json'; json.dump({'jobs': [j]}, open(p, 'w')); print(p)
PY
for jf in $(cat /tmp/jobsplit.txt); do
  PORT=8000 LOW_VRAM=1 OUTPUT_DIR=/w/forge_out nohup python server.py >> "$OUT/_logs/server.log" 2>&1 &
  SP=$!
  for i in $(seq 1 180); do curl -sf http://127.0.0.1:8000/health >/dev/null && break; sleep 5; done
  python "$(dirname "$0")/forge_client.py" "$jf" "$OUT" 2>&1 | tee -a "$OUT/_logs/client.log"
  kill $SP 2>/dev/null; sleep 5; kill -9 $SP 2>/dev/null; sleep 3
done
tail -40 "$OUT/_logs/server.log"
