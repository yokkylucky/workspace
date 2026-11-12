#!/usr/bin/env python3
"""オリジナルBGMの自動作曲 → WAV書き出し（著作権フリー：毎回プログラムが作曲する）

  .venv/bin/python scripts/bgm.py --duration 30 --mood christmas_elegant --accents 4,8.5,16.3 --out out/bgm.wav

  --mood     曲調のプリセット（下の MOODS を参照。--list で一覧表示）
  --duration 曲の長さ（秒）。動画の長さに合わせる。最後は主和音で余韻を残して終わる
  --accents  シーンが切り替わる秒数（カンマ区切り）。その瞬間にキラッとした音を入れ、曲を一段盛り上げる
  --seed     数字を変えると別のメロディになる
  --key      調の主音（MIDI番号。62=レ/D）。省略時はプリセットの値

音源は FluidR3_GM（MITライセンス）を FluidSynth で鳴らす。
"""
import argparse, os, random, subprocess, sys, tempfile
import mido

SF2 = os.environ.get("BGM_SOUNDFONT", "/usr/share/sounds/sf2/FluidR3_GM.sf2")
PPQ = 480
MAJOR = [0, 2, 4, 5, 7, 9, 11]

# GM音色番号: 0ピアノ 8チェレスタ 9グロッケン 10オルゴール 11ビブラフォン 45ピチカート 46ハープ 48/49弦 52コーラス 88/89パッド 42チェロ 32アコベ 33エレベ
MOODS = {
    "christmas_elegant": dict(desc="上品なクリスマス（オルゴール＋ピアノ＋ストリングス＋鈴）", bpm=82, key=62,
        prog=[1, 5, 6, 3, 4, 1, 4, 5], lead=10, lead2=8, arp=0, pad=49, bass=42, bells=True, swing=0.0),
    "wedding_romantic": dict(desc="ロマンチックなウェディング（ピアノ＋ストリングス＋ハープ）", bpm=72, key=65,
        prog=[1, 5, 6, 4, 1, 5, 4, 5], lead=0, lead2=46, arp=46, pad=48, bass=42, bells=False, swing=0.0),
    "bright_pop": dict(desc="明るく弾む告知向け（ピチカート＋グロッケン＋ピアノ）", bpm=112, key=60,
        prog=[1, 5, 6, 4], lead=9, lead2=45, arp=0, pad=48, bass=33, bells=True, swing=0.0),
    "calm_warm": dict(desc="落ち着いた温かい雰囲気（ピアノ＋パッド）", bpm=66, key=63,
        prog=[1, 4, 6, 5], lead=0, lead2=11, arp=0, pad=89, bass=32, bells=False, swing=0.0),
}

def scale_note(key, degree, octave_shift=0):
    """度数(1始まり, 8以上で上のオクターブ) → MIDIノート"""
    d = degree - 1
    return key + MAJOR[d % 7] + 12 * (d // 7) + 12 * octave_shift

def chord_tones(key, root_deg):
    return [scale_note(key, root_deg + i) for i in (0, 2, 4)]

def nearest(pitches, target):
    return min(pitches, key=lambda p: abs(p - target))

class Track:
    def __init__(self, ch, program, volume=100, reverb=90, pan=64):
        self.ch, self.ev = ch, []
        self.ev += [(0, mido.Message("program_change", channel=ch, program=program)),
                    (0, mido.Message("control_change", channel=ch, control=7, value=volume)),
                    (0, mido.Message("control_change", channel=ch, control=91, value=reverb)),
                    (0, mido.Message("control_change", channel=ch, control=10, value=pan))]
    def note(self, t_beats, dur_beats, pitch, vel):
        if not 0 <= pitch <= 127: return
        on = int(t_beats * PPQ); off = int((t_beats + dur_beats) * PPQ)
        self.ev.append((on, mido.Message("note_on", channel=self.ch, note=int(pitch), velocity=max(1, min(127, int(vel))))))
        self.ev.append((max(on + 1, off), mido.Message("note_off", channel=self.ch, note=int(pitch), velocity=0)))
    def to_track(self):
        tr = mido.MidiTrack(); last = 0
        for t, m in sorted(self.ev, key=lambda x: (x[0], x[1].type == "note_on")):
            tr.append(m.copy(time=t - last)); last = t
        return tr

def compose(duration, mood, accents, seed, key=None, tail=2.2):
    p = MOODS[mood]; rnd = random.Random(seed)
    key = key or p["key"]; beats_per_bar = 4
    body = max(4.0, duration - tail)
    bars = max(3, round(body * p["bpm"] / 60 / beats_per_bar))
    bpm = bars * beats_per_bar * 60 / body           # 小節がちょうど収まるようにテンポを微調整
    spb = 60 / bpm
    to_beat = lambda sec: sec / spb
    acc_bars = sorted({min(bars - 1, int(to_beat(a) // beats_per_bar)) for a in accents if 0 < a < body})
    # 盛り上がりの段階：0=イントロ 1=伴奏が入る 2=フル
    if acc_bars:
        lvl1 = acc_bars[min(1, len(acc_bars) - 1)] if len(acc_bars) > 1 else acc_bars[0]
        lvl2 = acc_bars[len(acc_bars) // 2] if len(acc_bars) > 2 else max(lvl1 + 1, bars // 2)
    else:
        lvl1, lvl2 = 1, max(2, bars // 2)
    level = lambda b: 0 if b < lvl1 else (1 if b < lvl2 else 2)

    lead = Track(0, p["lead"], 108, 100, 70); lead2 = Track(1, p["lead2"], 70, 110, 50)
    arp = Track(2, p["arp"], 82, 85, 56); pad = Track(3, p["pad"], 72, 110, 64)
    bass = Track(4, p["bass"], 80, 70, 64); spark = Track(5, 9, 70, 120, 80)
    drums = Track(9, 0, 70, 60, 64)

    prog = p["prog"]
    rhythms = [[1, 1, 1, 1], [1.5, 0.5, 1, 1], [2, 1, 1], [1, 1, 2], [1, 0.5, 0.5, 2], [3, 1], [0.5, 0.5, 1, 2]]
    # 4小節のモチーフを作って繰り返し、最後の繰り返しで少し変化をつける（曲らしさのため）
    motif_r = [rnd.choice(rhythms) for _ in range(4)]
    motif_contour = [rnd.choice([-2, -1, 1, 2, 0]) for _ in range(16)]
    prev = scale_note(key, 5, 1)
    for b in range(bars):
        t0 = b * beats_per_bar; lv = level(b)
        last = b == bars - 1
        deg = 1 if last else prog[b % len(prog)]
        ct = chord_tones(key, deg)
        # パッド（和音を伸ばす）
        for n in ct:
            pad.note(t0, beats_per_bar if not last else beats_per_bar + tail / spb, n, 46 + 10 * lv)
        # ベース
        if lv >= 1 or last:
            bass.note(t0, 2 if not last else beats_per_bar + 2, ct[0] - 24, 62 + 6 * lv)
            if not last: bass.note(t0 + 2, 2, (ct[2] - 24) if rnd.random() < 0.5 else ct[0] - 24, 54 + 6 * lv)
        # 分散和音（8分音符）
        if (lv >= 1 and not last) or (lv == 0 and b > 0):
            pat = [ct[0] - 12, ct[1] - 12, ct[2] - 12, ct[0], ct[1], ct[2], ct[0], ct[2] - 12]
            step = 0.5 if lv >= 1 else 1.0
            for i in range(int(beats_per_bar / step)):
                arp.note(t0 + i * step, step * 1.6, pat[i % len(pat)], (52 if i % 2 else 64) + 6 * lv)
        # メロディ
        if last:
            lead.note(t0, beats_per_bar + tail / spb, scale_note(key, 1, 1), 84)
            lead2.note(t0 + 0.5, beats_per_bar, scale_note(key, 3, 1), 50)
            lead2.note(t0 + 1.0, beats_per_bar, scale_note(key, 5, 1), 46)
            continue
        rhythm = motif_r[b % 4] if not (b >= 8 and b % 4 == 3) else rnd.choice(rhythms)
        t = 0.0
        for j, d in enumerate(rhythm):
            pool = [scale_note(key, s, 1) for s in range(-1, 10)]
            if j == 0:
                cand = [n + 12 * o for n in ct for o in (0, 1)]
                n = nearest(cand, prev + motif_contour[(b * 4) % 16])
            else:
                idx = min(range(len(pool)), key=lambda i: abs(pool[i] - prev))
                idx = max(0, min(len(pool) - 1, idx + motif_contour[(b * 4 + j) % 16]))
                n = pool[idx]
                if d >= 1.5: n = nearest([x + 12 * o for x in ct for o in (0, 1)], n)  # 長い音は和音の音に
            n = max(scale_note(key, 1, 1) - 3, min(scale_note(key, 3, 2), n))
            vel = 70 + 8 * lv + (8 if j == 0 else 0)
            if lv >= 0 and b >= 1:
                lead.note(t0 + t, d * 0.95, n, vel)
                if lv >= 1 and rnd.random() < 0.5: lead2.note(t0 + t, d * 0.9, n - 12, vel - 22)
            prev = n; t += d
        # 冒頭1小節はオルゴールで分散和音だけ
        if b == 0:
            for i, n in enumerate([ct[0], ct[1], ct[2], ct[0] + 12, ct[2], ct[1] + 12, ct[0] + 12, ct[2] + 12]):
                lead.note(t0 + i * 0.5, 1.2, n + 12, 64 + (i % 2) * 6)
        # 鈴（フルの時だけ・控えめ）
        if p["bells"] and lv >= 2:
            for k in range(8):
                drums.note(t0 + k * 0.5, 0.25, 83, (46 if k % 2 == 0 else 32) + rnd.randint(-4, 4))
            drums.note(t0, 1, 81, 34)  # トライアングル
    # シーン切り替えのキラッ（グロッケンの上昇アルペジオ）
    for a in accents:
        if not 0.2 < a < body: continue
        beat = to_beat(a) - 0.5
        bar = int(max(0, beat) // beats_per_bar); deg = 1 if bar >= bars - 1 else prog[bar % len(prog)]
        ct = chord_tones(key, deg)
        for i, n in enumerate([ct[0] + 24, ct[1] + 24, ct[2] + 24, ct[0] + 36]):
            spark.note(max(0, beat) + i * 0.125, 1.0, n, 58 + i * 6)

    mid = mido.MidiFile(ticks_per_beat=PPQ)
    meta = mido.MidiTrack(); meta.append(mido.MetaMessage("set_tempo", tempo=mido.bpm2tempo(bpm), time=0)); mid.tracks.append(meta)
    for tr in (lead, lead2, arp, pad, bass, spark, drums): mid.tracks.append(tr.to_track())
    return mid, bpm, bars

def render(mid, duration, out, lufs=-16.0):
    with tempfile.TemporaryDirectory() as td:
        mp, raw = os.path.join(td, "bgm.mid"), os.path.join(td, "raw.wav")
        mid.save(mp)
        subprocess.run(["fluidsynth", "-ni", "-q", "-g", "0.6", "-r", "48000", "-F", raw,
                        "-o", "synth.reverb.room-size=0.82", "-o", "synth.reverb.level=0.75", "-o", "synth.reverb.width=1.0",
                        "-o", "synth.chorus.active=0", SF2, mp], check=True)
        fo = max(0.0, duration - 2.4)
        af = (f"atrim=0:{duration},apad=whole_dur={duration},afade=t=in:d=0.4,afade=t=out:st={fo}:d=2.4,"
              f"highpass=f=40,equalizer=f=3500:t=q:w=1:g=-2,loudnorm=I={lufs}:TP=-1.5:LRA=9")
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", raw, "-af", af, "-ar", "48000", "-ac", "2", out], check=True)

def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--duration", type=float); ap.add_argument("--mood", default="christmas_elegant")
    ap.add_argument("--accents", default=""); ap.add_argument("--seed", type=int, default=1)
    ap.add_argument("--key", type=int); ap.add_argument("--out", default="out/bgm.wav")
    ap.add_argument("--midi", help="MIDIも保存する場合のパス"); ap.add_argument("--list", action="store_true")
    a = ap.parse_args()
    if a.list:
        for k, v in MOODS.items(): print(f"{k:20s} {v['desc']} (bpm {v['bpm']})")
        return
    if not a.duration: ap.error("--duration が必要です")
    if a.mood not in MOODS: sys.exit(f"不明なmood: {a.mood}（--list で一覧）")
    accents = [float(x) for x in a.accents.split(",") if x.strip()]
    mid, bpm, bars = compose(a.duration, a.mood, accents, a.seed, a.key)
    if a.midi: mid.save(a.midi)
    os.makedirs(os.path.dirname(os.path.abspath(a.out)), exist_ok=True)
    render(mid, a.duration, a.out)
    print(f"BGM_OK {a.out} mood={a.mood} bpm={bpm:.1f} bars={bars} seed={a.seed}")

if __name__ == "__main__":
    main()
