# 読み間違えた文を、ひらがな表記・複数seedで作り直し、whisperで聞き取って一番原稿に近いものを採用
import sys, difflib, torch, torchaudio as ta
from chatterbox.mtl_tts import ChatterboxMultilingualTTS
from faster_whisper import WhisperModel
JOBS = {
  "n3": ("けっこんしきじょうで、はじめて、かいさい。ララマルシェ。", "結婚式場で初めて開催ララマルシェ"),
}
m = ChatterboxMultilingualTTS.from_pretrained(device="cpu")
w = WhisperModel("small", device="cpu", compute_type="int8")
norm = lambda s: "".join(c for c in s if c not in "、。 ,.　")
for k, (text, target) in JOBS.items():
    best = (-1, None, "")
    for seed in [7, 11, 23, 42, 5, 99]:
        torch.manual_seed(seed)
        wav = m.generate(text, language_id="ja", exaggeration=0.4, cfg_weight=0.5, temperature=0.7)
        p = f"projects/lalamarche/audio/{k}_s{seed}.wav"; ta.save(p, wav, m.sr)
        heard = "".join(x.text for x in w.transcribe(p, language="ja")[0])
        score = difflib.SequenceMatcher(None, norm(heard), norm(target)).ratio()
        print(k, seed, f"{wav.shape[-1]/m.sr:.2f}s", f"{score:.2f}", heard, flush=True)
        if score > best[0]: best = (score, p, heard)
        if score >= 0.95: break
    print("BEST", k, best, flush=True)
