# 採用テイクを整音（無音カット・1.08倍速・ラウドネス統一）し、timeline.json を実尺で作る
import json, subprocess
A = "projects/lalamarche/audio/"
TAKES = {"n1": "n1", "n2": "n2", "n3": "n3_s42", "n4": "n4b_s11", "n5": "n5", "n6": "n6_s7", "n7": "n7"}
CAPTIONS = {
 "n1": "いつもは、ふたりの特別な日を彩る結婚式場。",
 "n2": "その扉が、みんなのマルシェとして開きます。",
 "n3": "結婚式場で、はじめて開催。ララマルシェ。",
 "n4": "ブーケづくりに、ステージ、グルメも。どなたでも、お気軽に。",
 "n5": "12月13日、日曜日。午前11時から午後6時まで。入場は無料です。",
 "n6": "はじめてのララマルシェ、ぜひ遊びに来てください。",
 "n7": "イベントの詳細は、インスタグラムで随時お知らせします。フォローして、お待ちください。",
}
TEMPO, START, GAP = 1.08, 0.5, 0.32
GAPS = {"n3": 0.45, "n5": 1.1, "n7": 0.45}  # 場面の切り替わり前は少し長めに間をとる
af = ("silenceremove=start_periods=1:start_threshold=-45dB:start_silence=0.05,areverse,"
      "silenceremove=start_periods=1:start_threshold=-45dB:start_silence=0.08,areverse,"
      f"atempo={TEMPO},loudnorm=I=-16:TP=-1.5:LRA=7,aresample=48000")
lines, t = [], START
for k, take in TAKES.items():
    out = f"public/lalamarche/{k}.wav"
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", A + take + ".wav", "-af", af, "-ac", "1", out], check=True)
    d = float(subprocess.check_output(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", out]))
    t += GAPS.get(k, GAP) if lines else 0
    lines.append({"id": k, "start": round(t, 2), "dur": round(d, 2), "text": CAPTIONS[k]}); t += d
print("narration ends at", round(t, 2))
json.dump({"fps": 30, "total": 900, "lines": lines}, open("src/lalamarche/timeline.json", "w"), ensure_ascii=False, indent=1)
for l in lines: print(l)
