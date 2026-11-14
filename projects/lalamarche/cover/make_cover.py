# リール表紙（1080x1920）。2倍の解像度で描いて縮小し、線と文字をなめらかにする
import math, numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

S = 2; W, H = 1080 * S, 1920 * S
P = "public/lalamarche/"
GOLD = (216, 183, 120); GOLD_L = (244, 228, 189); GOLD_D = (169, 128, 63); CREAM = (251, 245, 232); NIGHT = (26, 15, 7)
font = lambda f, size: ImageFont.truetype(P + f, int(size * S))
MIN_B = "Shippori_Mincho_B1_wght_700.ttf"; MIN_M = "Shippori_Mincho_B1_wght_500.ttf"
CIN = "Cinzel_wght_500.ttf"; COR = "Cormorant_Garamond_ital_wght_1_500.ttf"
CX = W // 2

# ---- 背景：会場写真を深く沈め、中心だけランプのように温める ----
bg = Image.open(P + "woodhall.jpg").convert("RGB").resize((W, int(W * 2208 / 1242)), Image.LANCZOS)
top = (bg.height - H) // 2; bg = bg.crop((0, top, W, top + H)).filter(ImageFilter.GaussianBlur(5 * S))
a = np.asarray(bg).astype(np.float32) / 255
yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
r = np.sqrt(((xx - W / 2) / (W * 0.75)) ** 2 + ((yy - H * 0.47) / (H * 0.5)) ** 2)
lamp = np.clip(1 - r, 0, 1)[..., None] ** 1.6
night = np.array(NIGHT, np.float32) / 255
a = a * (0.25 + 0.27 * lamp) + night * (0.75 - 0.27 * lamp) + np.array([0.10, 0.06, 0.02], np.float32) * lamp * 0.5
img = Image.fromarray((np.clip(a, 0, 1) * 255).astype(np.uint8)).convert("RGBA")

glow = Image.new("RGBA", (W, H), (0, 0, 0, 0)); gd = ImageDraw.Draw(glow)
line = Image.new("RGBA", (W, H), (0, 0, 0, 0)); ld = ImageDraw.Draw(line)

# ---- 波紋：中心から広がる同心円（ひろがる笑顔） ----
RC = (CX, int(870 * S))
for i in range(1, 9):
    rad = (150 + i * 62) * S; al = int(100 * (1 - i / 9) ** 1.3)
    ld.ellipse([RC[0] - rad, RC[1] - rad, RC[0] + rad, RC[1] + rad], outline=GOLD + (al,), width=max(1, S))

# ---- 光の弧：13の灯りを細い糸でつなぐ（つながる想い／12.13） ----
N = 13; y0, sag = 300 * S, 150 * S
pt = lambda t: (int(90 * S + t * (W - 180 * S)), int(y0 + sag * 4 * t * (1 - t)))
ld.line([pt(i / 200) for i in range(201)], fill=GOLD + (150,), width=max(1, int(1.2 * S)))
for i in range(N):
    x, y = pt(i / (N - 1)); rr = (5.5 if i % 2 == 0 else 4.0) * S
    gd.ellipse([x - 34 * S, y - 34 * S, x + 34 * S, y + 34 * S], fill=(255, 200, 120, 115))
    ld.line([x, y, x, y + 14 * S], fill=GOLD + (170,), width=max(1, S))
    ld.ellipse([x - rr, y + 14 * S - rr, x + rr, y + 14 * S + rr], fill=GOLD_L + (255,))
glow = glow.filter(ImageFilter.GaussianBlur(18 * S))
img = Image.alpha_composite(img, glow); img = Image.alpha_composite(img, line)

# ---- 細い金の二重枠 ----
fr = ImageDraw.Draw(img)
fr.rectangle([34 * S, 34 * S, W - 34 * S, H - 34 * S], outline=GOLD + (190,), width=max(1, int(1.5 * S)))
fr.rectangle([46 * S, 46 * S, W - 46 * S, H - 46 * S], outline=GOLD + (90,), width=max(1, S))

# ---- 文字 ----
def text_w(t, f, sp=0):
    return sum(f.getlength(c) for c in t) + sp * (len(t) - 1)
def draw_text(t, f, y, fill, sp=0, gold=False, shadow=True):
    w = text_w(t, f, sp); x = CX - w / 2
    layer = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(layer)
    xx_ = x
    for c in t:
        d.text((xx_, y), c, font=f, fill=(255, 255, 255, 255) if gold else fill); xx_ += f.getlength(c) + sp
    if gold:  # 上から下へ明るい金→深い金のグラデーション
        bb = layer.getbbox(); g = Image.new("RGBA", (W, H))
        h0, h1 = bb[1], bb[3]; arr = np.zeros((H, W, 4), np.uint8)
        t_ = np.clip((np.arange(H) - h0) / max(1, h1 - h0), 0, 1)[:, None]
        for k in range(3):
            c = np.interp(t_, [0, 0.45, 1], [GOLD_L[k], GOLD[k], GOLD_D[k]]); arr[..., k] = c
        arr[..., 3] = np.asarray(layer)[..., 3]; layer = Image.fromarray(arr)
    if shadow:
        sh = Image.new("RGBA", (W, H), (0, 0, 0, 0)); sh.putalpha(layer.getchannel("A").point(lambda v: int(v * 0.7)))
        sh = Image.merge("RGBA", (*[Image.new("L", (W, H), 10)] * 3, sh.getchannel("A"))).filter(ImageFilter.GaussianBlur(7 * S))
        globals()["img"] = Image.alpha_composite(globals()["img"], sh)
    globals()["img"] = Image.alpha_composite(globals()["img"], layer)
    return layer.getbbox()

# 上：結婚式場で初開催（細い金の罫で挟む）
f = font(MIN_M, 40); y = 610 * S
bb = draw_text("結婚式場で初開催", f, y, CREAM, sp=8 * S)
d = ImageDraw.Draw(img); cy = (bb[1] + bb[3]) // 2
d.line([bb[0] - 130 * S, cy, bb[0] - 30 * S, cy], fill=GOLD + (200,), width=max(1, S))
d.line([bb[2] + 30 * S, cy, bb[2] + 130 * S, cy], fill=GOLD + (200,), width=max(1, S))

draw_text("LALA MARCHE", font(CIN, 42), 735 * S, GOLD_L, sp=16 * S)
draw_text("ララマルシェ", font(MIN_B, 152), 800 * S, None, sp=4 * S, gold=True)

# 雪の結晶の飾り罫
cy = 1040 * S; d = ImageDraw.Draw(img)
d.line([CX - 260 * S, cy, CX - 36 * S, cy], fill=GOLD + (170,), width=max(1, S))
d.line([CX + 36 * S, cy, CX + 260 * S, cy], fill=GOLD + (170,), width=max(1, S))
for ang in (0, 60, 120):
    for sgn in (1, -1):
        th = math.radians(ang + 90); dx, dy = math.cos(th) * 20 * S * sgn, math.sin(th) * 20 * S * sgn
        d.line([CX, cy, CX + dx, cy + dy], fill=GOLD + (230,), width=max(1, int(2 * S)))

draw_text("2026.12.13", font(CIN, 92), 1095 * S, None, sp=6 * S, gold=True)
draw_text("SUNDAY   11:00 START", font(CIN, 34), 1225 * S, CREAM, sp=6 * S)

# 入場無料（細い金の枠）
f = font(MIN_B, 50); txt = "入場無料"; sp = 22 * S
w = text_w(txt, f, sp); bx0, bx1 = CX - w / 2 - 50 * S, CX + w / 2 + 50 * S; by0, by1 = 1320 * S, 1420 * S
d = ImageDraw.Draw(img)
d.rectangle([bx0, by0, bx1, by1], fill=(42, 26, 15, 150), outline=GOLD + (230,), width=max(1, int(1.5 * S)))
draw_text(txt, f, by0 + 20 * S, CREAM, sp=sp, shadow=False)

draw_text("〜つながる想い、ひろがる笑顔。〜", font(MIN_M, 30), 1490 * S, CREAM, sp=3 * S)
draw_text("at  LA LA CHANCE BELAMI", font(CIN, 26), 1580 * S, GOLD_L, sp=5 * S)

out = img.convert("RGB").resize((1080, 1920), Image.LANCZOS)
out.save("deliverables/lalamarche_reel_cover.png", optimize=True)
# プロフィール一覧での見え方（中央 1080x1440）
out.crop((0, 240, 1080, 1680)).resize((540, 720), Image.LANCZOS).save("projects/lalamarche/cover/grid_preview.png")
print("COVER_OK")
