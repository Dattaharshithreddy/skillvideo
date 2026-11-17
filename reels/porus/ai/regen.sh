# new look: swap transformer out, re-encode prompts, swap back, regenerate all clips at 20 steps
set -x
. /opt/wan/venv/bin/activate; cd /opt/reel/sv/reels/porus; M=/opt/wan/model
python ai/prompts.py
rm -rf $M/transformer
hf download Wan-AI/Wan2.2-TI2V-5B-Diffusers --local-dir $M --include "text_encoder/*" > /tmp/wdl3.log 2>&1
python ai/wan_encode.py > /opt/reel/pwenc2.log 2>&1; tail -1 /opt/reel/pwenc2.log
grep -q ENCODED /opt/reel/pwenc2.log && rm -rf $M/text_encoder
hf download Wan-AI/Wan2.2-TI2V-5B-Diffusers --local-dir $M --include "transformer/*" > /tmp/wdl4.log 2>&1
rm -rf $M/.cache; df -h / | tail -1
mkdir -p ai/clips_v1 && mv ai/clips/*.mp4 ai/clips_v1/ 2>/dev/null
ORDER="open_0 demand_0 ambhi_0 river_0 feint_0 storm_0 son_0 battle_0 king_0 return_0 murder_0 legacy_1 open_1 open_2 river_1 feint_1 storm_1 ambhi_1 legacy_0 son_1 battle_1 battle_2 king_1 return_1"
STEPS=20 python ai/wan_gen.py $ORDER > /opt/reel/pwgen3.log 2>&1
echo REGEN_DONE
