# narration.json の各文をChatterboxで生成（同じseedで声を揃える）
import json, sys, torch, torchaudio as ta
from chatterbox.mtl_tts import ChatterboxMultilingualTTS
lines = json.load(open(sys.argv[1])); outdir = sys.argv[2]
only = set(sys.argv[3].split(",")) if len(sys.argv) > 3 else None
m = ChatterboxMultilingualTTS.from_pretrained(device="cpu")
ref = f"{outdir}/voice_ref.wav"
import os
for l in lines:
    if only and l["id"] not in only: continue
    torch.manual_seed(7)
    kw = {"audio_prompt_path": ref} if os.path.exists(ref) else {}
    wav = m.generate(l["text"], language_id="ja", exaggeration=0.4, cfg_weight=0.5, temperature=0.7, **kw)
    ta.save(f"{outdir}/{l['id']}.wav", wav, m.sr)
    print(l["id"], f"{wav.shape[-1]/m.sr:.2f}s", flush=True)
