#!/usr/bin/env python3
"""動画にオリジナルBGMを自動で作って入れる（作曲 → シーン切替に同期 → ナレーションに合わせて自動で音量を下げる → MP4書き出し）

  .venv/bin/python scripts/add_bgm.py input.mp4 output.mp4 --mood christmas_elegant
  .venv/bin/python scripts/add_bgm.py input.mp4 output.mp4 --mood wedding_romantic --seed 3 --bgm-volume -20

  入力動画に音声（ナレーション）があれば、喋っている間だけBGMを自動で下げる（ダッキング）。
  音声がなければBGMだけの動画にする。
  --accents を省略すると、映像のシーン切り替わりを自動検出して曲を合わせる。
  --timeline に Remotion の timeline.json を渡すと、ナレーションの開始位置を盛り上げポイントに使う。
"""
import argparse, json, os, re, subprocess, sys, tempfile
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import bgm  # noqa: E402

def probe(path):
    j = json.loads(subprocess.check_output(["ffprobe", "-v", "error", "-show_entries", "format=duration:stream=codec_type",
                                            "-of", "json", path]))
    return float(j["format"]["duration"]), any(s["codec_type"] == "audio" for s in j["streams"])

def detect_scenes(path, window=0.6, min_gap=1.5):
    """映像の切り替わり時刻を検出。クロスフェードでも拾えるよう、0.6秒離れたコマ同士の差の山を探す"""
    import numpy as np
    fps, w, h = 10, 32, 56
    raw = subprocess.run(["ffmpeg", "-v", "error", "-i", path, "-vf", f"fps={fps},scale={w}:{h},format=gray",
                          "-f", "rawvideo", "-"], capture_output=True, check=True).stdout
    fr = np.frombuffer(raw, np.uint8).reshape(-1, h, w).astype(np.float32)
    k = max(1, round(window * fps))
    if len(fr) <= k + 2: return []
    d = np.abs(fr[k:] - fr[:-k]).mean(axis=(1, 2))
    thr = max(d.mean() + 0.8 * d.std(), 6.0)
    res = []
    for i in range(1, len(d) - 1):
        if d[i] >= thr and d[i] >= d[i - 1] and d[i] >= d[i + 1]:
            t = (i + k / 2) / fps - window / 2   # 切り替えが始まるあたり
            if t > 0.8 and (not res or t - res[-1] >= min_gap): res.append(round(t, 2))
            elif res and t - res[-1] < min_gap and d[i] > 0: pass
    return res

def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("input"); ap.add_argument("output")
    ap.add_argument("--mood", default="christmas_elegant", help="曲調（scripts/bgm.py --list で一覧）")
    ap.add_argument("--seed", type=int, default=1, help="数字を変えると別の曲になる")
    ap.add_argument("--accents", help="盛り上げる秒数（カンマ区切り）。省略時は自動検出")
    ap.add_argument("--timeline", help="Remotion の timeline.json（ナレーション開始位置を使う）")
    ap.add_argument("--bgm-volume", type=float, default=-10.0, help="ナレーションがない部分のBGMの音量(dB, 0が最大)")
    ap.add_argument("--duck", type=float, default=7.0, help="ナレーション中にBGMを下げる量(dB)")
    ap.add_argument("--keep-bgm", help="作ったBGMのWAVを保存するパス")
    a = ap.parse_args()

    dur, has_audio = probe(a.input)
    if a.accents:
        accents = [float(x) for x in a.accents.split(",") if x.strip()]
    elif a.timeline:
        accents = [l["start"] - 0.25 for l in json.load(open(a.timeline))["lines"]][1:]
    else:
        accents = detect_scenes(a.input)
    print(f"duration={dur:.2f}s narration={'yes' if has_audio else 'no'} accents={[round(x, 2) for x in accents]}")

    with tempfile.TemporaryDirectory() as td:
        wav = a.keep_bgm or os.path.join(td, "bgm.wav")
        mid, bpm, bars = bgm.compose(dur, a.mood, accents, a.seed)
        bgm.render(mid, dur, wav)
        print(f"BGM: mood={a.mood} bpm={bpm:.1f} bars={bars} seed={a.seed}")
        g = a.bgm_volume
        if has_audio:
            # ナレーションの音量に反応してBGMを下げる（sidechaincompress）。下げ幅は --duck で調整
            ratio = max(2.0, a.duck / 2.5)
            fc = (f"[1:a]volume={g}dB,aformat=channel_layouts=stereo[b];"
                  f"[0:a]aformat=channel_layouts=stereo,asplit=2[v][sc];"
                  f"[b][sc]sidechaincompress=threshold=0.015:ratio={ratio}:attack=25:release=450:makeup=1[bd];"
                  f"[v][bd]amix=inputs=2:normalize=0:duration=first,loudnorm=I=-14:TP=-1.5:LRA=9[a]")
        else:
            fc = f"[1:a]volume={g}dB,loudnorm=I=-16:TP=-1.5:LRA=9[a]"
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", a.input, "-i", wav, "-filter_complex", fc,
                        "-map", "0:v", "-map", "[a]", "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", "-ar", "48000",
                        "-movflags", "+faststart", "-shortest", a.output], check=True)
    print(f"ADD_BGM_OK {a.output}")

if __name__ == "__main__":
    main()
