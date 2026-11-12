# テキスト → ナレーションWAV（Chatterbox 多言語, CPU）
# 使い方: .venv/bin/python scripts/tts.py "読み上げる文" out/narration.wav [--lang ja] [--ref 声の見本.wav]
import argparse, torchaudio as ta
from chatterbox.mtl_tts import ChatterboxMultilingualTTS
ap = argparse.ArgumentParser(); ap.add_argument("text"); ap.add_argument("output")
ap.add_argument("--lang", default="ja"); ap.add_argument("--ref", default=None, help="声質を真似る参照音声(任意)")
a = ap.parse_args()
m = ChatterboxMultilingualTTS.from_pretrained(device="cpu")
wav = m.generate(a.text, language_id=a.lang, audio_prompt_path=a.ref)
ta.save(a.output, wav, m.sr); print(f"saved {a.output} ({wav.shape[-1]/m.sr:.1f}s)")
