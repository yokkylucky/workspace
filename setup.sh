#!/usr/bin/env bash
# 動画制作ツール一式をセットアップ（何度実行してもOK。入っている物はスキップ）
# 重いもの: Blender(~400MB), PyTorch CPU(~1GB), SD-Turbo(5.2GB, SKIP_SD_TURBO=1 で省略可)
set -euo pipefail
cd "$(dirname "$0")"
ROOT=$(pwd)
mkdir -p tools logs out
BLENDER_VER=5.3.0
TORCH_IDX=https://download.pytorch.org/whl/cpu

echo "== apt: ffmpeg / xvfb / 日本語フォント"
need=()
command -v ffmpeg >/dev/null || need+=(ffmpeg)
command -v xvfb-run >/dev/null || need+=(xvfb)
fc-list :lang=ja | grep -q . || need+=(fonts-ipafont-gothic)
if [ ${#need[@]} -gt 0 ]; then apt-get update -qq && apt-get install -y -qq "${need[@]}"; fi

echo "== npm: Remotion / GSAP / Three.js / HyperFrames / Chrome DevTools MCP / Impeccable"
[ -d node_modules/remotion ] || npm install --no-audit --no-fund

echo "== Python(.venv): Chatterbox / faster-whisper / yt-dlp / Blender MCP"
[ -x .venv/bin/python ] || uv venv -q -p 3.11 .venv
[ -d tools/blender-mcp ] || git clone -q --depth 1 https://github.com/ahujasid/blender-mcp.git tools/blender-mcp
if ! .venv/bin/python -c "import chatterbox, faster_whisper, yt_dlp, blender_mcp" 2>/dev/null; then
  VIRTUAL_ENV=.venv uv pip install -q --index-strategy unsafe-best-match --extra-index-url "$TORCH_IDX" \
    "torch==2.6.0+cpu" "torchaudio==2.6.0+cpu" "torchvision==0.21.0+cpu" \
    chatterbox-tts faster-whisper yt-dlp "setuptools<81" ./tools/blender-mcp
fi

echo "== Blender $BLENDER_VER"
if [ ! -x tools/blender/blender ]; then
  curl -sSfL -o tools/blender.tar.xz "https://download.blender.org/release/Blender${BLENDER_VER%.*}/blender-${BLENDER_VER}-linux-x64.tar.xz"
  tar xf tools/blender.tar.xz -C tools && rm tools/blender.tar.xz
  ln -sfn "blender-${BLENDER_VER}-linux-x64" tools/blender
fi

echo "== ComfyUI (CPU)"
[ -d tools/ComfyUI ] || git clone -q --depth 1 https://github.com/Comfy-Org/ComfyUI.git tools/ComfyUI
if [ ! -x tools/ComfyUI/.venv/bin/python ]; then
  (cd tools/ComfyUI && uv venv -q -p 3.12 .venv && VIRTUAL_ENV=.venv uv pip install -q \
    --index-strategy unsafe-best-match --extra-index-url "$TORCH_IDX" torch torchvision torchaudio -r requirements.txt)
fi
CKPT=tools/ComfyUI/models/checkpoints/sd_turbo.safetensors
if [ "${SKIP_SD_TURBO:-0}" != 1 ] && [ ! -s "$CKPT" ]; then
  curl -sSfL -o "$CKPT.part" https://huggingface.co/stabilityai/sd-turbo/resolve/main/sd_turbo.safetensors && mv "$CKPT.part" "$CKPT"
fi

echo "== 参照用リポジトリ（Skillsの原本）"
[ -d tools/remotion-skills ] || git clone -q --depth 1 https://github.com/remotion-dev/skills.git tools/remotion-skills
[ -d tools/impeccable ] || git clone -q --depth 1 https://github.com/pbakaus/impeccable.git tools/impeccable

npx --yes impeccable telemetry off >/dev/null 2>&1 || true
echo "SETUP_DONE"
