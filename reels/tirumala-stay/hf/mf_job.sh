#!/usr/bin/env bash
# Hugging Face Job: rebuild the guest-house 3D models with Model Forge (Hunyuan3D-2mini + texture) from the
# best Google Maps photos. Output: /out/mf/b_<key>_m.glb  (bucket hf://buckets/HarshithReddy05/tirumala-reel)
# Run in image pytorch/pytorch:2.4.1-cuda12.4-cudnn9-devel on a10g-large.
set -x
export DEBIAN_FRONTEND=noninteractive
apt-get update -qq && apt-get install -y -qq git curl libgl1 libglib2.0-0 libgomp1 libopengl0 libglu1-mesa libegl1 libxrender1 libxext6 libsm6 libxkbcommon0 >/dev/null 2>&1
mkdir -p /out/mf
git clone -q --depth 1 https://github.com/Dattaharshithreddy/3dmodel /w/3dmodel
cd /w/3dmodel/server && PYTHON=python bash setup.sh > /out/mf/setup.log 2>&1; tail -5 /out/mf/setup.log
python - <<"PY" 2>&1 | tail -5
import pymeshlab, trimesh
trimesh.creation.box().export("/tmp/t.ply"); ms = pymeshlab.MeshSet(); ms.load_new_mesh("/tmp/t.ply"); print("PLY_OK", ms.current_mesh().vertex_number())
PY
PORT=8000 nohup python server.py > /out/mf/server.log 2>&1 &
for i in $(seq 1 120); do curl -sf http://127.0.0.1:8000/health && break; sleep 10; done; echo
python "$(dirname "$0")/mf_client.py" 2>&1 | tee /out/mf/client.log
cp /w/3dmodel/server/*.log /out/mf/ 2>/dev/null; tail -60 /out/mf/server.log
ls -la /out/mf
