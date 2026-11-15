set -e
mkdir -p /opt/reel/hima && cd /opt/reel/hima
[ -x venv/bin/python ] || python3 -m venv venv
venv/bin/pip install -q -U huggingface_hub
[ -f hima-tts-nano-te/model.safetensors ] || venv/bin/hf download Prahaladha/hima-tts-nano-te --local-dir hima-tts-nano-te
venv/bin/pip install -q -r hima-tts-nano-te/requirements.txt speechbrain soundfile
grep -aE "total|VOICE" /tmp/pvoice2.log | tail -2
cd /opt/reel/sv/reels/porus && /opt/reel/hima/venv/bin/python hima_test.py
