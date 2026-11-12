# n4 を「3つのブース」の文に差し替え（複数seedで生成し、聞き取りが原稿に一番近いものを採用）
import difflib, torch, torchaudio as ta
from chatterbox.mtl_tts import ChatterboxMultilingualTTS
from faster_whisper import WhisperModel
text = "ブーケづくりに、ステージ、グルメも。どなたでも、おきがるに。"
target = "ブーケ作りにステージグルメもどなたでもお気軽に"
m = ChatterboxMultilingualTTS.from_pretrained(device="cpu"); w = WhisperModel("small", device="cpu", compute_type="int8")
norm = lambda s: "".join(c for c in s if c not in "、。 ,.　!！")
best = (-1, None)
for seed in [7, 11, 23, 42, 5, 99]:
    torch.manual_seed(seed)
    wav = m.generate(text, language_id="ja", exaggeration=0.4, cfg_weight=0.5, temperature=0.7)
    p = f"projects/lalamarche/audio/n4b_s{seed}.wav"; ta.save(p, wav, m.sr)
    heard = "".join(x.text for x in w.transcribe(p, language="ja")[0])
    sc = difflib.SequenceMatcher(None, norm(heard), norm(target)).ratio()
    print(seed, f"{wav.shape[-1]/m.sr:.2f}s", f"{sc:.2f}", heard, flush=True)
    if sc > best[0]: best = (sc, p)
    if sc >= 0.95: break
print("BEST", best)
