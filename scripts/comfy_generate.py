# ComfyUI(API)にSD-Turboのtext-to-imageワークフローを投げ、出力画像を保存する
# 使い方: python scripts/comfy_generate.py "prompt" out/image.png [width] [height]
import json, sys, time, urllib.request, shutil, os
prompt, out = sys.argv[1], sys.argv[2]
w = int(sys.argv[3]) if len(sys.argv) > 3 else 512; h = int(sys.argv[4]) if len(sys.argv) > 4 else 512
API = "http://127.0.0.1:8188"
wf = {
 "1": {"class_type": "CheckpointLoaderSimple", "inputs": {"ckpt_name": "sd_turbo.safetensors"}},
 "2": {"class_type": "CLIPTextEncode", "inputs": {"text": prompt, "clip": ["1", 1]}},
 "3": {"class_type": "CLIPTextEncode", "inputs": {"text": "", "clip": ["1", 1]}},
 "4": {"class_type": "EmptyLatentImage", "inputs": {"width": w, "height": h, "batch_size": 1}},
 "5": {"class_type": "KSampler", "inputs": {"model": ["1", 0], "positive": ["2", 0], "negative": ["3", 0], "latent_image": ["4", 0],
       "seed": 42, "steps": 1, "cfg": 1.0, "sampler_name": "euler_ancestral", "scheduler": "simple", "denoise": 1.0}},
 "6": {"class_type": "VAEDecode", "inputs": {"samples": ["5", 0], "vae": ["1", 2]}},
 "7": {"class_type": "SaveImage", "inputs": {"images": ["6", 0], "filename_prefix": "api"}},
}
req = urllib.request.Request(f"{API}/prompt", data=json.dumps({"prompt": wf}).encode(), headers={"Content-Type": "application/json"})
pid = json.load(urllib.request.urlopen(req))["prompt_id"]; t = time.time()
while True:
    hist = json.load(urllib.request.urlopen(f"{API}/history/{pid}"))
    if pid in hist: break
    time.sleep(1)
img = hist[pid]["outputs"]["7"]["images"][0]
src = os.path.join(os.path.dirname(__file__), "..", "tools", "ComfyUI", "output", img["subfolder"], img["filename"])
shutil.copy(src, out); print(f"COMFY_OK {out} ({time.time()-t:.0f}s)")
