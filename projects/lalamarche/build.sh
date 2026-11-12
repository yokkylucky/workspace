#!/usr/bin/env bash
# ララマルシェ：2本レンダリング → BGM合成 → Instagram向けに圧縮 → deliverables/
set -e
cd "$(dirname "$0")/../.."
projects/lalamarche/render.sh
for v in narration silent; do
  .venv/bin/python scripts/add_bgm.py out/lm/${v}_raw.mp4 out/lm/${v}_bgm.mp4 --mood christmas_elegant --timeline src/lalamarche/timeline.json
done
ffmpeg -v error -y -i out/lm/narration_bgm.mp4 -c:v libx264 -preset slow -crf 19 -pix_fmt yuv420p -c:a copy -movflags +faststart deliverables/lalamarche_reel_narration_bgm.mp4
ffmpeg -v error -y -i out/lm/silent_bgm.mp4 -c:v libx264 -preset slow -crf 19 -pix_fmt yuv420p -c:a copy -movflags +faststart deliverables/lalamarche_reel_bgm_only.mp4
echo BUILD_DONE
