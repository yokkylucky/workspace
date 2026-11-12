#!/usr/bin/env bash
# 仮想ディスプレイ上でBlender(GUI)を起動し、Blender MCPアドオンのサーバーを localhost:9876 で待ち受ける
cd "$(dirname "$0")/.."
export DISABLE_TELEMETRY=true
unset WAYLAND_DISPLAY
export XDG_RUNTIME_DIR="${XDG_RUNTIME_DIR:-/tmp/xdg-$(id -u)}"; mkdir -p -m 700 "$XDG_RUNTIME_DIR"
exec xvfb-run -a -s "-screen 0 1280x720x24" tools/blender/blender --gpu-backend opengl --python scripts/blender_enable_mcp.py "$@"
