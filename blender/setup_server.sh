#!/usr/bin/env bash
# One-time setup for an NVIDIA GPU server. Supports:
#   - Amazon Linux 2023 (AWS "Deep Learning Base OSS Nvidia Driver GPU AMI (Amazon Linux 2023)")
#   - Ubuntu 22.04/24.04 (AWS "... (Ubuntu 22.04)")
# Installs: Blender (headless), ffmpeg, a Python 3.11 venv with pipeline deps, Kokoro offline voice.
# Run:  bash setup_server.sh      then:  source ~/.bashrc
set -euo pipefail
SERIES="${BLENDER_SERIES:-5.2}"
PREFIX="${BLENDER_PREFIX:-$HOME/blender}"
VENV="$HOME/cgi-venv"

echo "== GPU check"
nvidia-smi --query-gpu=name,memory.total,driver_version --format=csv || { echo "nvidia-smi failed: no NVIDIA driver?"; exit 1; }

. /etc/os-release
echo "== system packages for $PRETTY_NAME"
if command -v dnf >/dev/null; then
  sudo dnf install -y --allowerasing tar xz curl unzip which python3.11 python3.11-pip \
    libXi libXxf86vm libXfixes libXrender libxkbcommon libSM libICE libXrandr \
    mesa-libGL mesa-libEGL mesa-libGLU dejavu-sans-fonts fontconfig
  PY=python3.11
elif command -v apt-get >/dev/null; then
  sudo apt-get update -y
  sudo apt-get install -y xz-utils curl unzip python3-venv python3-pip ffmpeg \
    libxi6 libxxf86vm1 libxfixes3 libxrender1 libxkbcommon0 libsm6 libice6 libgl1 libegl1 libglu1-mesa libxrandr2 fonts-dejavu
  PY=python3
else
  echo "Unsupported OS: $PRETTY_NAME"; exit 1
fi

echo "== ffmpeg"
if ! command -v ffmpeg >/dev/null; then   # Amazon Linux has no ffmpeg package: use the static build
  curl -fL https://johnvansickle.com/ffmpeg/releases/ffmpeg-release-amd64-static.tar.xz -o /tmp/ffmpeg.tar.xz
  mkdir -p /tmp/ffmpeg && tar -xf /tmp/ffmpeg.tar.xz -C /tmp/ffmpeg --strip-components=1
  sudo install -m 755 /tmp/ffmpeg/ffmpeg /tmp/ffmpeg/ffprobe /usr/local/bin/
  rm -rf /tmp/ffmpeg /tmp/ffmpeg.tar.xz
fi
ffmpeg -version | head -1

echo "== Blender $SERIES (latest patch)"
if [ ! -x "$PREFIX/blender" ]; then
  TAR=$(curl -fsSL "https://download.blender.org/release/Blender${SERIES}/" | grep -oE "blender-${SERIES}\.[0-9]+-linux-x64\.tar\.xz" | sort -V | tail -1)
  [ -n "$TAR" ] || { echo "No Blender ${SERIES} linux tarball found; set BLENDER_SERIES"; exit 1; }
  curl -fL "https://download.blender.org/release/Blender${SERIES}/${TAR}" -o /tmp/blender.tar.xz
  mkdir -p "$PREFIX" && tar -xf /tmp/blender.tar.xz -C "$PREFIX" --strip-components=1 && rm /tmp/blender.tar.xz
fi
sudo ln -sf "$PREFIX/blender" /usr/local/bin/blender
blender -b --version | head -1

echo "== Python venv ($PY) with pipeline deps"
[ -d "$VENV" ] || $PY -m venv "$VENV"
"$VENV/bin/pip" install -q --upgrade pip
"$VENV/bin/pip" install -q fal-client requests pillow numpy soundfile kokoro-onnx edge-tts
grep -q "cgi-venv/bin/activate" ~/.bashrc || echo "source $VENV/bin/activate" >> ~/.bashrc

echo "== Kokoro voice model (offline narration)"
K="$HOME/.cache/kokoro"; mkdir -p "$K"
B=https://github.com/thewh1teagle/kokoro-onnx/releases/download/model-files-v1.0
[ -f "$K/kokoro-v1.0.int8.onnx" ] || curl -fL "$B/kokoro-v1.0.int8.onnx" -o "$K/kokoro-v1.0.int8.onnx"
[ -f "$K/voices-v1.0.bin" ] || curl -fL "$B/voices-v1.0.bin" -o "$K/voices-v1.0.bin"

echo "== GPU render test"
DIR="$(cd "$(dirname "$0")" && pwd)"
blender -b --factory-startup -P "$DIR/gpu_test.py" 2>&1 | grep -E "CYCLES device|render time|Error" || true
echo
echo "Setup done. Run:  source ~/.bashrc   (activates the Python venv)"
echo "Expect 'CYCLES device: OPTIX' above. If it says CPU, check nvidia-smi."
