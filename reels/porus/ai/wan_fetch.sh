# stage 1: text encoder only -> encode prompts -> drop it; stage 2: transformer + vae (disk is tight)
set -x
. /opt/wan/venv/bin/activate; cd /opt/reel/sv/reels/porus
rm -rf /root/.cache/huggingface/hub/models--Wan-AI--Wan2.2-TI2V-5B-Diffusers /root/.cache/huggingface/xet
M=/opt/wan/model; mkdir -p $M
hf download Wan-AI/Wan2.2-TI2V-5B-Diffusers --local-dir $M --include "text_encoder/*" --include "tokenizer/*" --include "model_index.json" --include "scheduler/*" > /tmp/wdl1.log 2>&1
python ai/prompts.py; python ai/wan_encode.py > /opt/reel/pwenc.log 2>&1; tail -2 /opt/reel/pwenc.log
grep -q ENCODED /opt/reel/pwenc.log && rm -rf $M/text_encoder
df -h / | tail -1
hf download Wan-AI/Wan2.2-TI2V-5B-Diffusers --local-dir $M --include "transformer/*" --include "vae/*" > /tmp/wdl2.log 2>&1
rm -rf $M/.cache; du -sh $M; df -h / | tail -1
echo FETCH_DONE
