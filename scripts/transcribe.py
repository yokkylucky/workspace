# 音声/動画 → SRT字幕（faster-whisper, CPU int8）
# 使い方: .venv/bin/python scripts/transcribe.py input.wav [out.srt] [--model small] [--lang ja]
import argparse, os
from faster_whisper import WhisperModel
ap = argparse.ArgumentParser()
ap.add_argument("input"); ap.add_argument("output", nargs="?")
ap.add_argument("--model", default="small"); ap.add_argument("--lang", default=None)
a = ap.parse_args()
out = a.output or os.path.splitext(a.input)[0] + ".srt"
def ts(t):
    h, r = divmod(t, 3600); m, s = divmod(r, 60)
    return f"{int(h):02}:{int(m):02}:{int(s):02},{int(round((s-int(s))*1000)):03}"
model = WhisperModel(a.model, device="cpu", compute_type="int8")
segs, info = model.transcribe(a.input, language=a.lang, vad_filter=True)
with open(out, "w", encoding="utf-8") as f:
    for i, s in enumerate(segs, 1):
        f.write(f"{i}\n{ts(s.start)} --> {ts(s.end)}\n{s.text.strip()}\n\n")
print(f"WHISPER_OK lang={info.language} -> {out}")
