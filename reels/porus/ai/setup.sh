set -x
mkdir -p /opt/wan && cd /opt/wan
[ -d venv ] || python3 -m venv venv
. venv/bin/activate
pip install -q --upgrade pip
pip install -q torch torchvision --index-url https://download.pytorch.org/whl/cu124
pip install -q "diffusers>=0.35" transformers accelerate ftfy imageio imageio-ffmpeg sentencepiece protobuf resemblyzer soundfile "huggingface_hub[cli]"
python -c "import torch,diffusers;print('TORCH',torch.__version__,torch.cuda.is_available(),'DIFF',diffusers.__version__)"
huggingface-cli download Wan-AI/Wan2.2-TI2V-5B-Diffusers > /tmp/wandl.log 2>&1; echo DL_DONE $(du -sh ~/.cache/huggingface 2>/dev/null)
