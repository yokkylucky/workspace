#!/usr/bin/env bash
# ララマルシェ：2本レンダリング → BGM合成 → deliverables へ
set -e
cd "$(dirname "$0")/../.."
export REMOTION_CHROME=/opt/pw-browsers/chromium-1243/chrome-linux64/chrome
npx remotion render src/index.ts LalaMarcheNarration out/lm/narration_raw.mp4 --concurrency=4 --crf=16 --log=error
npx remotion render src/index.ts LalaMarcheSilent out/lm/silent_raw.mp4 --concurrency=4 --crf=16 --muted --log=error
echo RENDER_DONE
