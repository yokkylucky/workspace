#!/usr/bin/env python3
"""画像編集の補助（ChatGPT/OpenAI と Claude の分担用）

  # A. 手渡し：ChatGPTで作った画像を、動画用の縦1080x1920に整える
  .venv/bin/python scripts/image_edit.py fit chatgpt.png out.jpg

  # B. 直接つなぐ：元画像＋指示文をOpenAIの画像APIに送り、結果を受け取って1080x1920に整える
  .venv/bin/python scripts/image_edit.py openai --image original.jpg --prompt-file prompt_v1.md --out result_v1.jpg

  B には OpenAI API の鍵が必要（ChatGPT Plus とは別契約・従量課金）。鍵はこの環境の
  「ネットワークの秘密情報」として api.openai.com 向けに保存し、通信時に自動で付けられる
  （この会話やファイルには書かない）。
"""
import argparse, base64, io, os, re, sys
from PIL import Image

W, H = 1080, 1920

def fit(img: Image.Image, out: str):
    """縦9:16になるよう中央で切り抜いてから 1080x1920 にする（引き伸ばさない）"""
    img = img.convert("RGB"); w, h = img.size; target = W / H
    if w / h > target:
        nw = int(h * target); img = img.crop(((w - nw) // 2, 0, (w - nw) // 2 + nw, h))
    else:
        nh = int(w / target); img = img.crop((0, (h - nh) // 2, w, (h - nh) // 2 + nh))
    img.resize((W, H), Image.LANCZOS).save(out, quality=93)
    print(f"FIT_OK {out} ({w}x{h} -> {W}x{H})")

def read_prompt(path):
    """prompt_vN.md の '---' より下（指示文の本文）だけを取り出す"""
    text = open(path, encoding="utf-8").read()
    return text.split("\n---\n", 1)[1].strip() if "\n---\n" in text else text.strip()

def call_openai(image, prompt, out, model, quality):
    import requests
    # 鍵は環境のネットワーク設定が自動で付ける。手元に鍵があれば OPENAI_API_KEY も使える
    key = os.environ.get("OPENAI_API_KEY", "sk-proxy-injected")
    try:
        with open(image, "rb") as f:
            r = requests.post("https://api.openai.com/v1/images/edits",
                              headers={"Authorization": f"Bearer {key}"},
                              files={"image[]": (os.path.basename(image), f, "image/jpeg")},
                              data={"model": model, "prompt": prompt, "size": "1024x1536", "quality": quality, "n": "1"},
                              timeout=600)
    except requests.exceptions.ProxyError:
        sys.exit("OpenAIに接続できません。api.openai.com 向けのAPI鍵がこの環境にまだ保存されていません。")
    if r.status_code != 200:
        msg = r.text[:400]
        if r.status_code in (401, 403) or "request blocked" in msg:
            sys.exit(f"OpenAIに接続できません（{r.status_code}）。APIの鍵が未設定か、接続が許可されていません。\n{msg}")
        sys.exit(f"OpenAI APIエラー {r.status_code}: {msg}")
    data = r.json()["data"][0]
    raw = base64.b64decode(data["b64_json"]) if data.get("b64_json") else requests.get(data["url"], timeout=120).content
    stem = re.sub(r"\.(jpe?g|png)$", "", out)
    open(stem + "_raw.png", "wb").write(raw)          # 生成そのもの（比較用に保存）
    fit(Image.open(io.BytesIO(raw)), out)

def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    f = sub.add_parser("fit"); f.add_argument("input"); f.add_argument("output")
    o = sub.add_parser("openai"); o.add_argument("--image", required=True); o.add_argument("--prompt-file", required=True)
    o.add_argument("--out", required=True); o.add_argument("--model", default="gpt-image-1")
    o.add_argument("--quality", default="high", choices=["low", "medium", "high"])
    a = ap.parse_args()
    if a.cmd == "fit":
        fit(Image.open(a.input), a.output)
    else:
        call_openai(a.image, read_prompt(a.prompt_file), a.out, a.model, a.quality)

if __name__ == "__main__":
    main()
