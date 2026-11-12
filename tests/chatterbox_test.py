# テキスト→ナレーション音声(WAV)。CPUで実行
import sys, time, torch, torchaudio as ta
from chatterbox.mtl_tts import ChatterboxMultilingualTTS
text = sys.argv[1] if len(sys.argv) > 1 else "こんにちは。これはオープンソースの音声合成で作ったナレーションです。"
out = sys.argv[2] if len(sys.argv) > 2 else "out/narration_ja.wav"
t = time.time()
model = ChatterboxMultilingualTTS.from_pretrained(device="cpu")
wav = model.generate(text, language_id="ja")
ta.save(out, wav, model.sr)
print(f"CHATTERBOX_OK {out} sr={model.sr} sec={wav.shape[-1]/model.sr:.1f} elapsed={time.time()-t:.0f}s")
