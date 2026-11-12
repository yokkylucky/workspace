# video-studio：動画制作の進め方（Claude向け）

このリポジトリは動画制作用。ユーザーは日本語で依頼する。返答も日本語で、専門用語は避ける。

## 環境
- 初回・新しいコンテナでは `./setup.sh`（入っている物はスキップ）。確認は `tests/check_all.sh`
- GPUなし。Remotionのレンダリングは `REMOTION_CHROME=/opt/pw-browsers/chromium-1243/chrome-linux64/chrome` を付ける
- 縦長30秒・ぼかし多めで1本10〜15分かかる。長いレンダリングはバックグラウンドで回す

## 動画制作の標準手順
1. **素材を読む**：写真・企画書・参考画像。日付と曜日はカレンダーで照合し、食い違いは必ず確認する
2. **構成と言葉を心理学で点検**（`marketing-psychology` スキル）：最初の1秒で興味を引けるか、「無料」などの強い言葉が早く出るか、最後のお願いが1つに絞れているか、見た人が当日を思い浮かべられるか。事実でない急かし方や数字は使わない。結果は `projects/<案件>/review_marketing.md` に残す。内容を足すときはユーザーに確認する
3. **写真の加工**：参考の雰囲気に合わせて色調を統一する（例：`projects/lalamarche/grade.py`）。人物の多い写真や低解像度の写真は避ける
4. **ナレーション**（依頼があるとき）
   - `scripts/tts.py`（Chatterbox）で1文ずつ生成する
   - 数字や読み間違えやすい語はひらがなで書く
   - 全文を `scripts/transcribe.py`（faster-whisper）で聞き取り、原稿と照合する。違う文はseedを変えるか言い換える（`projects/lalamarche/regen.py`）
5. **映像**：Remotion（`src/`）。テキストはInstagramの安全領域（上250px・下420px・右140pxを避ける）に置く。`npx remotion still` で各シーンの静止画を確認してから本番を書き出す
6. **BGM（必ず入れる）**：レンダリング後に
   ```bash
   .venv/bin/python scripts/add_bgm.py 映像.mp4 完成.mp4 --mood <曲調> [--seed N]
   ```
   - 曲は毎回プログラムが作るオリジナル（FluidR3_GM音源・MITライセンス）なので、著作権の心配がない
   - シーンの切り替わりを自動検出して、そこで曲を盛り上げる
   - ナレーションがあれば、喋っている間だけBGMを自動で下げる
   - 曲調の一覧は `scripts/bgm.py --list`。結婚式場・上品な案件は `christmas_elegant`（冬）または `wedding_romantic`。告知・明るい案件は `bright_pop`。落ち着いた案件は `calm_warm`
   - 「曲を変えて」と言われたら `--seed` の数字を変える
   - 外部のAI作曲モデル（MusicGen 等）は商用不可のライセンスが多いので使わない
7. **確認**：完成動画から数コマ抜き出して目で見る。音量（ebur128）、長さ、解像度も確認する
8. **表紙画像**（`canvas-design` スキル）：リール・投稿の表紙を作る。先にデザインの考え方を `cover/philosophy.md` にまとめてから描く。動画と同じフォント・色を使う。プロフィール一覧で見える中央1080×1440に文字を収める（例：`projects/lalamarche/cover/make_cover.py`）
9. **納品**：`deliverables/` に置き、SendUserFile で送る。変えた点と注意点を短く伝える

## 参考
- 実例：`projects/lalamarche/`（ララマルシェのPRリール、ナレーションあり／なしの2本）
- 各ツールの使い方：`README.md`
