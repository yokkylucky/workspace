#!/usr/bin/env bash
# 14ツールを1つずつ動作確認する（重いナレーション生成/画像生成はFULL=1のときのみ）
cd "$(dirname "$0")/.."
export DISABLE_TELEMETRY=true HYPERFRAMES_NO_TELEMETRY=1 DO_NOT_TRACK=1
CHROME=/opt/pw-browsers/chromium-1243/chrome-linux64/chrome
mkdir -p out; pass=0; fail=0
run() { local name=$1; shift; if "$@" >"out/check_$(echo "$name" | tr -c "A-Za-z0-9\n" _).log" 2>&1; then echo "✅ $name"; pass=$((pass+1)); else echo "❌ $name (out/check_$(echo "$name" | tr -c "A-Za-z0-9\n" _).log)"; fail=$((fail+1)); fi; }

run "FFmpeg"        bash -c 'ffmpeg -v error -y -f lavfi -i testsrc2=s=640x360:r=30 -t 1 -pix_fmt yuv420p out/ffmpeg_test.mp4'
run "yt-dlp"        .venv/bin/yt-dlp -q --no-warnings --force-overwrites -o out/ytdlp_test.mp4 https://raw.githubusercontent.com/mediaelement/mediaelement-files/master/big_buck_bunny.mp4
run "Blender"       bash -c 'tools/blender/blender -b --factory-startup --python tests/blender_test.py | grep -q BLENDER_OK'
run "Remotion+GSAP+Three.js" bash -c "REMOTION_CHROME=$CHROME npx remotion render src/index.ts Demo out/remotion_test.mp4 --log=error --frames=0-29"
run "HyperFrames"   bash -c 'cd hyperframes/demo && npx hyperframes render -o ../../out/hyperframes_test.mp4 --quiet'
run "BGM自動作曲"    bash -c '.venv/bin/python scripts/bgm.py --duration 12 --mood christmas_elegant --accents 4,8 --out out/bgm_test.wav --midi out/bgm_test.mid | grep -q BGM_OK && .venv/bin/python tests/bgm_theory_check.py out/bgm_test.mid 62'
run "Impeccable"    bash -c 'npx impeccable detect tests/fixtures/sloppy.html 2>&1 | grep -q "anti-patterns found"'
run "Agent Skills (Remotion, HyperFrames, Impeccable)" bash -c 'for s in remotion-best-practices hyperframes impeccable; do test -f .claude/skills/$s/SKILL.md || exit 1; done'
run "Chrome DevTools MCP" bash -c 'timeout 120 .venv/bin/python tests/chrome_devtools_mcp_test.py | grep -q "screenshot saved"'
if (echo > /dev/tcp/127.0.0.1/9876) 2>/dev/null; then
  run "Blender MCP" bash -c 'timeout 120 .venv/bin/python tests/blender_mcp_test.py | grep -q "MCP_Torus"'
else echo "⏭  Blender MCP（先に scripts/start-blender-mcp.sh & を起動）"; fi
if [ "${FULL:-0}" = 1 ]; then
  run "Chatterbox"     bash -c '.venv/bin/python tests/chatterbox_test.py | grep -q CHATTERBOX_OK'
  run "faster-whisper" bash -c '.venv/bin/python scripts/transcribe.py out/narration_ja.wav --lang ja | grep -q WHISPER_OK'
  if curl -s -o /dev/null http://127.0.0.1:8188/system_stats; then
    run "ComfyUI" python3 scripts/comfy_generate.py "a red fox in snow" out/comfyui_test.png
  else echo "⏭  ComfyUI（先に scripts/start-comfyui.sh & を起動）"; fi
else
  run "Chatterbox(import)"     .venv/bin/python -c "import chatterbox.mtl_tts, perth; assert perth.PerthImplicitWatermarker"
  run "faster-whisper(import)" .venv/bin/python -c "import faster_whisper"
  run "ComfyUI(import)"        bash -c 'cd tools/ComfyUI && .venv/bin/python -c "import torch, comfy"'
fi
echo "---- pass=$pass fail=$fail"; [ $fail = 0 ]
