#!/usr/bin/env bash
# ComfyUIをCPUモードで起動（http://127.0.0.1:8188）
cd "$(dirname "$0")/../tools/ComfyUI"
exec .venv/bin/python main.py --cpu --listen 127.0.0.1 --port 8188 --disable-auto-launch "$@"
