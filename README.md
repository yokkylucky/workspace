# video-studio

Claude Code で動画を作るためのツール一式。クラウド環境（GPUなし・CPUのみ）で全ツールの動作を確認済み。

## セットアップ

```bash
./setup.sh                 # 入っていない物だけ入れる（SKIP_SD_TURBO=1 で画像モデル5.2GBを省略）
tests/check_all.sh         # 全ツールを1つずつ動作確認（FULL=1 で音声生成・字幕・画像生成まで実行）
```

大きいファイル（Blender本体、Python環境、ComfyUI、モデル）は `tools/` と `.venv/` に入り、Gitには含めない。

## ツールと使い方

| ツール | 役割 | 使い方 |
|---|---|---|
| Remotion | Reactで動画を組んでレンダリング | `src/` を編集 → `REMOTION_CHROME=/opt/pw-browsers/chromium-1243/chrome-linux64/chrome npx remotion render src/index.ts Demo out/x.mp4` |
| Remotion Skills | エージェント向けの公式ガイド | `.claude/skills/remotion-*`（Claude Codeが自動で使う） |
| GSAP | 文字・UIの動きをタイムラインで制御 | Remotionでは `timeline({paused:true})` をフレームで `seek`（`src/Demo.tsx` 参照） |
| Three.js | ブラウザ上の3D | `@remotion/three` の `<ThreeCanvas>` で使用（GPUなしでもSwiftShaderで描画） |
| HyperFrames | HTMLを書けば動画になる | `hyperframes/demo/` で `npx hyperframes render`。スキルは `.claude/skills/hyperframes*` |
| Blender | モデリング・本格3Dレンダリング | `tools/blender/blender -b --python script.py`（Cycles CPU） |
| Blender MCP | ClaudeがBlenderを直接操作 | `scripts/start-blender-mcp.sh &` で起動（仮想ディスプレイ上のBlender）→ `.mcp.json` の `blender` |
| Chrome DevTools MCP | 描画結果を見て直す | `.mcp.json` の `chrome-devtools`（スクショ・JS実行・コンソール確認） |
| Impeccable | デザインの講評・チェック | `npx impeccable detect <file or url>`。スキルは `.claude/skills/impeccable` |
| Chatterbox | テキストからナレーション | `.venv/bin/python scripts/tts.py "文章" out/n.wav --lang ja` |
| faster-whisper | ナレーションから字幕 | `.venv/bin/python scripts/transcribe.py out/n.wav --lang ja` → `out/n.srt` |
| ComfyUI | 画像・動画生成パイプライン | `scripts/start-comfyui.sh &` → `python3 scripts/comfy_generate.py "prompt" out/img.png` |
| yt-dlp | 参考クリップ・音声の取得 | `.venv/bin/yt-dlp <URL>` |
| FFmpeg | エンコード・確認・MP4書き出し | 例: 映像＋音声＋字幕焼き込み（下記） |
| BGM自動作曲（自作） | 動画に合うオリジナルBGMを作って入れる | `.venv/bin/python scripts/add_bgm.py in.mp4 out.mp4 --mood christmas_elegant`（曲調一覧は `scripts/bgm.py --list`） |

### 合成の例（映像＋ナレーション＋字幕）

```bash
ffmpeg -i out/video.mp4 -i out/n.wav \
  -vf "subtitles=out/n.srt:force_style='FontName=IPAGothic,FontSize=22,Outline=2'" \
  -c:v libx264 -pix_fmt yuv420p -c:a aac -shortest -movflags +faststart out/final.mp4
```

`samples/pipeline_demo.mp4` がこの流れで作った確認用の動画。

## この環境での注意

- CPUのみ。Chatterboxは4秒の音声で約45秒、ComfyUI(SD-Turbo 512px)は1枚約16秒。
- ネットワークは許可制。YouTubeは動画配信ホストがワイルドカードのため未許可（yt-dlpはGitHub等の許可済みホストで確認）。
- CDN(jsdelivr等)は使えないので、HyperFramesのGSAPはローカルの `gsap.min.js` を読む。
