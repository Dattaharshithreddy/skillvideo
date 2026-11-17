#!/bin/bash
# Morning run on the swaram-gpu server (AWS): narration in Datta's voice, then the full GPU render, then upload.
# sudo -u ubuntu bash go_porus.sh   (from /opt/reel/sv/reels/porus after git pull)
set -e
cd "$(dirname "$0")"
(cd /home/ubuntu/Swaram && docker compose -f docker-compose.yml -f docker-compose.cloud.yml up -d voicebox) && sleep 20
python3 voice_porus.py
BL=/opt/reel/blender/blender NGPU=1 SPP=40 NARR=narr/narration.wav SENTS=narr/sentences.json CONC=6 bash render_all.sh
aws s3 cp mg/out/puru_reel.mp4 s3://claude-reels-730335199669/reels/puru-miniature-telugu-v2.mp4 --region ap-south-1 --quiet && echo S3_OK
