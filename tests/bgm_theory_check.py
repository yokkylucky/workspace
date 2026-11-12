# 生成BGM（MIDI）の音楽的な健全性チェック：調外の音・強拍の不協和・大跳躍・音域
import sys, mido
from collections import defaultdict
mid = mido.MidiFile(sys.argv[1]); key = int(sys.argv[2]) if len(sys.argv) > 2 else 62
scale = {(key + i) % 12 for i in (0, 2, 4, 5, 7, 9, 11)}
notes = defaultdict(list)  # ch -> [(beat, pitch)]
for tr in mid.tracks:
    t = 0
    for m in tr:
        t += m.time
        if m.type == "note_on" and m.velocity > 0: notes[m.channel].append((t / mid.ticks_per_beat, m.note))
out_key = sum(1 for ch, ns in notes.items() if ch != 9 for _, p in ns if p % 12 not in scale)
pad = notes[3]; lead = sorted(notes[0])
def chord_at(b):
    bar = int(b // 4); return {p % 12 for (t, p) in pad if int(t // 4) == bar}
strong = [(b, p) for b, p in lead if abs(b - round(b)) < 1e-6 and int(round(b)) % 2 == 0]
clash = [(b, p) for b, p in strong if p % 12 not in chord_at(b)]
leaps = [abs(b2[1] - b1[1]) for b1, b2 in zip(lead, lead[1:]) if b2[0] - b1[0] <= 1.01 and abs(b2[1] - b1[1]) > 9]
print(f"notes={sum(len(v) for v in notes.values())} out_of_key={out_key} strong_beats={len(strong)} "
      f"strong_beat_non_chord={len(clash)} big_leaps(>6th)={len(leaps)} lead_range={min(p for _,p in lead)}-{max(p for _,p in lead)}")
