# ブースごとの短いナレーション（体験・ステージ・グルメ）を生成し、聞き取りで一番原稿に近いテイクを選ぶ
import difflib, torch, torchaudio as ta
from chatterbox.mtl_tts import ChatterboxMultilingualTTS
from faster_whisper import WhisperModel
JOBS = {
  "n4c": ("おいしい、グルメも。", "おいしいグルメも"),
}
m = ChatterboxMultilingualTTS.from_pretrained(device="cpu"); w = WhisperModel("small", device="cpu", compute_type="int8")
norm = lambda s: "".join(c for c in s if c not in "、。 ,.　!！")
for k, (text, target) in JOBS.items():
    best = (-1, None)
    for seed in [11, 7, 23, 42, 5, 99, 3, 17]:
        torch.manual_seed(seed)
        wav = m.generate(text, language_id="ja", exaggeration=0.4, cfg_weight=0.5, temperature=0.7)
        p = f"projects/lalamarche/audio/{k}_s{seed}.wav"; ta.save(p, wav, m.sr)
        heard = "".join(x.text for x in w.transcribe(p, language="ja")[0])
        sc = difflib.SequenceMatcher(None, norm(heard), norm(target)).ratio()
        print(k, seed, f"{wav.shape[-1]/m.sr:.2f}s", f"{sc:.2f}", heard, flush=True)
        if sc > best[0]: best = (sc, p)
        if sc >= 0.95: break
    print("BEST", k, best, flush=True)
