# 写真を「1枚目のポスター」風（暖色・夕暮れ・光のにじみ・周辺減光）に加工し、縦9:16に切り出す
import sys, numpy as np
from PIL import Image, ImageFilter
U = "/root/.claude/uploads/6db65ea1-742b-5a73-ace9-1a82506d9891/"
OUT = "public/lalamarche/"
W, H = 1242, 2208  # 1080x1920 の1.15倍（ゆっくりズーム用の余白）
# name: (file, 横方向の中心位置0-1, 明るさ, 空を夕焼けにする強さ)
SHOTS = {
  "exterior":  ("6dcd7e3d-image.jpg", 0.50, 0.80, 1.0),
  "chandelier":("4f10d794-image.jpg", 0.57, 0.86, 0.0),
  "whitehall": ("4b3bd69b-image.jpg", 0.62, 0.84, 0.0),
  "woodhall":  ("5b0b202c-image.jpg", 0.52, 0.82, 0.0),
  "greenwall": ("f8a171a4-image.jpg", 0.36, 0.86, 0.0),
  "table":     ("85a12404-image.jpg", 0.46, 0.88, 0.0),
  "lobby":     ("e85a950f-image.jpg", 0.66, 0.86, 0.0),
  "lounge":    ("497e083b-image.jpg", 0.40, 0.88, 0.0),
  "gourmet":   ("/home/user/workspace/projects/lalamarche/assets/src_gourmet.webp", 0.43, 0.82, 0.0),
  "stage":     ("7293dc61-image.jpg", 0.505, 0.80, 0.0),
}
def grade(name, f, cx, bright, sky):
    im = Image.open(f if f.startswith("/") else U + f).convert("RGB")
    w, h = im.size; cw = int(h * 9 / 16)
    x0 = int(min(max(cx * w - cw / 2, 0), w - cw))
    im = im.crop((x0, 0, x0 + cw, h)).resize((W, H), Image.LANCZOS)
    a = np.asarray(im).astype(np.float32) / 255.0
    lum = a @ np.array([0.299, 0.587, 0.114], np.float32)
    # 彩度を少し落とす（緑・青を落ち着かせる）
    a = lum[..., None] + (a - lum[..., None]) * 0.78
    # 暖色トーン（シャンパンゴールド〜アンバー）
    a = a * np.array([1.06, 0.95, 0.80], np.float32) * bright
    # シャドウを茶色に、ハイライトを金色に
    a = a + (1 - a) * 0.0 + np.array([0.035, 0.018, 0.0], np.float32) * (1 - lum[..., None])
    # 空を夕焼け色に（上ほど強い、明るい部分ほど強い）
    if sky > 0:
        yy = np.linspace(1, 0, H, dtype=np.float32)[:, None, None] ** 1.5
        mask = np.clip((lum[..., None] - 0.55) / 0.35, 0, 1) * yy * sky
        sunset = np.array([1.0, 0.72, 0.45], np.float32)
        a = a * (1 - mask * 0.75) + sunset * mask * 0.75 * np.maximum(lum[..., None], 0.6)
    # S字のコントラスト
    a = np.clip(a, 0, 1); a = a * a * (3 - 2 * a) * 0.35 + a * 0.65
    img = Image.fromarray((np.clip(a, 0, 1) * 255).astype(np.uint8))
    # 光のにじみ（明るい部分を金色にぼかして重ねる）
    hi = img.point(lambda v: max(0, v - 170) * 3).filter(ImageFilter.GaussianBlur(28))
    b = np.asarray(hi).astype(np.float32) / 255 * np.array([1.0, 0.78, 0.45], np.float32) * 0.55
    a = np.asarray(img).astype(np.float32) / 255
    a = 1 - (1 - a) * (1 - b)  # スクリーン合成
    # 周辺減光（こげ茶）
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    d = np.sqrt(((xx - W / 2) / (W * 0.62)) ** 2 + ((yy - H / 2) / (H * 0.6)) ** 2)
    v = np.clip((d - 0.55) / 0.6, 0, 1)[..., None] ** 1.4
    a = a * (1 - v * 0.72) + np.array([0.12, 0.06, 0.02], np.float32) * v * 0.72
    Image.fromarray((np.clip(a, 0, 1) * 255).astype(np.uint8)).save(f"{OUT}{name}.jpg", quality=92)
    # 比較用（元の切り出し）
    im.resize((W // 4, H // 4)).save(f"projects/lalamarche/assets/orig_{name}.jpg")
for k, v in SHOTS.items():
    if len(sys.argv) == 1 or k in sys.argv[1:]:
        grade(k, *v); print("graded", k)
