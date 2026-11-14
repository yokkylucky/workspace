import React, {useEffect, useState} from 'react';
import {
  AbsoluteFill, Audio, Img, Sequence, continueRender, delayRender, interpolate, random,
  staticFile, useCurrentFrame, useVideoConfig, Easing,
} from 'remotion';
import timeline from './timeline.json';

// ===== デザイントークン（1枚目のポスターの色味に合わせる） =====
const GOLD = '#d8b778';
const GOLD_LIGHT = '#f4e4bd';
const GOLD_DEEP = '#a9803f';
const CREAM = '#fbf5e8';
const BROWN = '#2a1a0f';
const SERIF_EN = '"Cinzel", serif';
const ITALIC_EN = '"Cormorant Garamond", serif';
const MINCHO = '"Shippori Mincho B1", serif';
const FPS = timeline.fps;
const sec = (s: number) => Math.round(s * FPS);
const L = Object.fromEntries(timeline.lines.map((l) => [l.id, l])) as Record<string, (typeof timeline.lines)[number]>;
const ease = Easing.bezier(0.22, 1, 0.36, 1);

// ===== フォント読み込み =====
const FONTS: [string, string, string, string][] = [
  ['Cinzel', 'Cinzel_wght_500.ttf', '500', 'normal'],
  ['Cormorant Garamond', 'Cormorant_Garamond_ital_wght_1_500.ttf', '500', 'italic'],
  ['Shippori Mincho B1', 'Shippori_Mincho_B1_wght_500.ttf', '500', 'normal'],
  ['Shippori Mincho B1', 'Shippori_Mincho_B1_wght_700.ttf', '700', 'normal'],
];
const useFonts = () => {
  const [handle] = useState(() => delayRender('fonts'));
  useEffect(() => {
    Promise.all(FONTS.map(([fam, file, weight, style]) => {
      const f = new FontFace(fam, `url(${staticFile('lalamarche/' + file)})`, {weight, style});
      document.fonts.add(f);
      return f.load();
    })).then(() => continueRender(handle)).catch((e) => { console.error(e); continueRender(handle); });
  }, [handle]);
};

// ===== 共通パーツ =====
const fadeInOut = (f: number, dur: number, fin = 12, fout = 12) =>
  interpolate(f, [0, fin, dur - fout, dur], [0, 1, 1, 0], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'});

const goldText: React.CSSProperties = {
  backgroundImage: `linear-gradient(180deg, ${GOLD_LIGHT} 0%, ${GOLD} 45%, ${GOLD_DEEP} 100%)`,
  WebkitBackgroundClip: 'text', backgroundClip: 'text', color: 'transparent',
  filter: 'drop-shadow(0 2px 6px rgba(20,10,0,0.55))',
};

// 写真（ゆっくりズーム＋パン）
const Photo: React.FC<{src: string; dur: number; from?: number; to?: number; panY?: number; offsetY?: number; blur?: number; dim?: number}> = ({src, dur, from = 1.0, to = 1.1, panY = 0, offsetY = 0, blur = 0, dim = 0}) => {
  const f = useCurrentFrame();
  const t = interpolate(f, [0, dur], [0, 1], {extrapolateRight: 'clamp'});
  const s = from + (to - from) * t;
  return (
    <AbsoluteFill style={{overflow: 'hidden'}}>
      <Img src={staticFile('lalamarche/' + src)} style={{
        width: '100%', height: '100%', objectFit: 'cover',
        transform: `scale(${s}) translateY(${offsetY + panY * t}px)`, filter: blur ? `blur(${blur}px)` : undefined,
      }} />
      {dim > 0 && <AbsoluteFill style={{background: `rgba(26,14,6,${dim})`}} />}
    </AbsoluteFill>
  );
};

// 雪（決定的な乱数で毎フレーム同じ位置）
const Snow: React.FC<{count?: number; opacity?: number}> = ({count = 70, opacity = 0.85}) => {
  const f = useCurrentFrame();
  return (
    <AbsoluteFill style={{pointerEvents: 'none'}}>
      {new Array(count).fill(0).map((_, i) => {
        const r = (k: string) => random(`snow-${i}-${k}`);
        const size = 3 + r('s') * 8;
        const speed = 0.8 + r('v') * 1.6 + size * 0.12;
        const y = ((r('y') * 2100 + f * speed) % 2100) - 90;
        const x = r('x') * 1080 + Math.sin(f / (40 + r('p') * 40) + r('ph') * 6) * (14 + r('a') * 22);
        return <div key={i} style={{
          position: 'absolute', left: x, top: y, width: size, height: size, borderRadius: '50%',
          background: 'rgba(255,250,240,0.95)', opacity: opacity * (0.35 + r('o') * 0.65),
          filter: size > 8 ? 'blur(1.5px)' : 'blur(0.6px)',
        }} />;
      })}
    </AbsoluteFill>
  );
};

// ぼけた金色の光の粒
const Bokeh: React.FC<{count?: number}> = ({count = 16}) => {
  const f = useCurrentFrame();
  return (
    <AbsoluteFill style={{pointerEvents: 'none', mixBlendMode: 'screen'}}>
      {new Array(count).fill(0).map((_, i) => {
        const r = (k: string) => random(`bokeh-${i}-${k}`);
        const size = 40 + r('s') * 120;
        const tw = 0.45 + 0.55 * (0.5 + 0.5 * Math.sin(f / (18 + r('t') * 20) + r('p') * 6));
        return <div key={i} style={{
          position: 'absolute', left: r('x') * 1080 - size / 2, top: r('y') * 1920 - size / 2 - f * (0.15 + r('v') * 0.3),
          width: size, height: size, borderRadius: '50%', opacity: 0.22 * tw,
          background: `radial-gradient(circle, rgba(255,214,150,0.95) 0%, rgba(255,190,110,0.35) 45%, rgba(255,180,90,0) 70%)`,
        }} />;
      })}
    </AbsoluteFill>
  );
};

// 上部のガーランド（緑の葉と電球が瞬く）
const Garland: React.FC<{y?: number; sag?: number; delay?: number}> = ({y = 70, sag = 150, delay = 0}) => {
  const f = useCurrentFrame() - delay;
  const reveal = interpolate(f, [0, 24], [0, 1], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp', easing: ease});
  const pt = (t: number) => ({x: -40 + t * 1160, y: y + sag * 4 * t * (1 - t)});
  const leaves = new Array(64).fill(0).map((_, i) => {
    const t = i / 63; const p = pt(t);
    const a = random(`leaf-${i}`) * 360; const len = 26 + random(`ll-${i}`) * 22;
    return <ellipse key={i} cx={p.x} cy={p.y} rx={len / 2} ry={7} transform={`rotate(${a} ${p.x} ${p.y})`}
      fill={i % 3 === 0 ? '#2f4a2c' : i % 3 === 1 ? '#3d5c36' : '#24391f'} />;
  });
  const bulbs = new Array(22).fill(0).map((_, i) => {
    const t = (i + 0.5) / 22; const p = pt(t);
    const tw = 0.55 + 0.45 * Math.sin(f / 7 + random(`b-${i}`) * 12);
    return <g key={i} opacity={reveal}>
      <circle cx={p.x} cy={p.y + 14} r={30} fill="url(#glow)" opacity={tw} />
      <circle cx={p.x} cy={p.y + 14} r={5.5} fill="#fff1c9" opacity={0.6 + 0.4 * tw} />
    </g>;
  });
  return (
    <svg width={1080} height={420} style={{position: 'absolute', top: 0, left: 0, clipPath: `inset(0 ${100 - reveal * 100}% 0 0)`}}>
      <defs>
        <radialGradient id="glow"><stop offset="0%" stopColor="#ffd98f" stopOpacity="0.9" /><stop offset="100%" stopColor="#ffb85c" stopOpacity="0" /></radialGradient>
      </defs>
      {leaves}{bulbs}
    </svg>
  );
};

// ポスターと同じ細い金の二重枠
const GoldFrame: React.FC<{opacity?: number}> = ({opacity = 1}) => (
  <AbsoluteFill style={{pointerEvents: 'none', opacity}}>
    <div style={{position: 'absolute', inset: 34, border: `1.5px solid ${GOLD}`, opacity: 0.75}} />
    <div style={{position: 'absolute', inset: 44, border: `1px solid ${GOLD}`, opacity: 0.4}} />
  </AbsoluteFill>
);

// ── ✻ ── の飾り罫
const Divider: React.FC<{width?: number; progress?: number}> = ({width = 520, progress = 1}) => (
  <div style={{display: 'flex', alignItems: 'center', justifyContent: 'center', gap: 18, opacity: progress}}>
    <div style={{height: 1.5, width: (width / 2 - 30) * progress, background: `linear-gradient(90deg, transparent, ${GOLD})`}} />
    <SnowflakeIcon size={30} />
    <div style={{height: 1.5, width: (width / 2 - 30) * progress, background: `linear-gradient(90deg, ${GOLD}, transparent)`}} />
  </div>
);

const SnowflakeIcon: React.FC<{size?: number; color?: string}> = ({size = 30, color = GOLD}) => (
  <svg width={size} height={size} viewBox="-50 -50 100 100">
    {[0, 60, 120].map((a) => (
      <g key={a} transform={`rotate(${a})`} stroke={color} strokeWidth={5} strokeLinecap="round">
        <line x1={0} y1={-44} x2={0} y2={44} />
        <polyline points="-12,-32 0,-22 12,-32" fill="none" /><polyline points="-12,32 0,22 12,32" fill="none" />
      </g>
    ))}
  </svg>
);

// 1文字ずつふわっと現れるテキスト
const RevealText: React.FC<{text: string; delay?: number; stagger?: number; style?: React.CSSProperties; gold?: boolean}> = ({text, delay = 0, stagger = 2, style, gold}) => {
  const f = useCurrentFrame() - delay;
  return (
    <div style={{...style}}>
      {[...text].map((c, i) => {
        const t = interpolate(f - i * stagger, [0, 18], [0, 1], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp', easing: ease});
        return <span key={i} style={{
          display: 'inline-block', opacity: t, transform: `translateY(${(1 - t) * 26}px)`,
          filter: `blur(${(1 - t) * 6}px)`, whiteSpace: 'pre', ...(gold ? goldText : {}),
        }}>{c}</span>;
      })}
    </div>
  );
};

const FadeUp: React.FC<{delay?: number; children: React.ReactNode; style?: React.CSSProperties}> = ({delay = 0, children, style}) => {
  const f = useCurrentFrame() - delay;
  const t = interpolate(f, [0, 20], [0, 1], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp', easing: ease});
  return <div style={{opacity: t, transform: `translateY(${(1 - t) * 24}px)`, ...style}}>{children}</div>;
};

const textShadow = '0 2px 18px rgba(20,10,2,0.85), 0 1px 3px rgba(20,10,2,0.9)';
const jpBody: React.CSSProperties = {fontFamily: MINCHO, fontWeight: 500, color: CREAM, textShadow, textAlign: 'center'};

// ===== シーン =====
// シーン切り替えは0.6秒のクロスフェード
const XF = 18;
const Scene: React.FC<{from: number; to: number; first?: boolean; children: React.ReactNode}> = ({from, to, first, children}) => {
  const dur = to - from + XF;
  return (
    <Sequence from={from} durationInFrames={dur}>
      <SceneFade dur={dur} noFadeIn={first}>{children}</SceneFade>
    </Sequence>
  );
};
const SceneFade: React.FC<{dur: number; noFadeIn?: boolean; children: React.ReactNode}> = ({dur, noFadeIn, children}) => {
  const f = useCurrentFrame();
  const o = noFadeIn ? interpolate(f, [dur - XF, dur], [1, 0], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'}) : fadeInOut(f, dur, XF, XF);
  return <AbsoluteFill style={{opacity: o}}>{children}</AbsoluteFill>;
};

// 1. 冒頭：0秒目から「結婚式場で、マルシェ!?」＋入場無料 → 特別な日を彩る結婚式場が
const HOOK = 52; // 冒頭の見出しを出しておくフレーム数（約1.7秒）
const S1: React.FC<{dur: number}> = ({dur}) => {
  const f = useCurrentFrame();
  const hookOut = interpolate(f, [HOOK - 10, HOOK + 4], [1, 0], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'});
  const hookScale = interpolate(f, [0, HOOK], [1.06, 1.0], {extrapolateRight: 'clamp', easing: ease});
  return (
    <AbsoluteFill>
      <Photo src="c2.jpg" dur={dur} from={1.1} to={1.0} panY={-20} />
      <AbsoluteFill style={{background: 'linear-gradient(180deg, rgba(30,16,6,0.25) 0%, rgba(30,16,6,0.62) 14%, rgba(30,16,6,0.55) 34%, rgba(30,16,6,0) 52%, rgba(30,16,6,0) 62%, rgba(30,16,6,0.55) 100%)'}} />
      <AbsoluteFill style={{background: 'rgba(26,14,6,0.45)', opacity: hookOut}} />
      {/* 見出し（0フレーム目から表示） */}
      <AbsoluteFill style={{alignItems: 'center', justifyContent: 'center', top: -120, opacity: hookOut, transform: `scale(${hookScale})`}}>
        <div style={{fontFamily: SERIF_EN, fontSize: 32, letterSpacing: '0.3em', marginRight: '-0.3em', color: GOLD_LIGHT, textShadow}}>LA LA CHANCE BELAMI</div>
        <div style={{height: 40}} />
        <div style={{...jpBody, fontSize: 84, fontWeight: 700, letterSpacing: '0.08em'}}>結婚式場で、</div>
        <div style={{height: 6}} />
        <div style={{fontFamily: MINCHO, fontWeight: 700, fontSize: 150, letterSpacing: '0.02em', ...goldText}}>マルシェ<span style={{letterSpacing: '-0.08em'}}>!?</span></div>
        <div style={{height: 40}} />
        <div style={{
          fontFamily: MINCHO, fontWeight: 700, fontSize: 44, letterSpacing: '0.14em', color: BROWN,
          padding: '14px 44px 14px 52px', borderRadius: 999, background: `linear-gradient(180deg, ${GOLD_LIGHT}, ${GOLD})`,
          boxShadow: '0 6px 24px rgba(0,0,0,0.35)',
        }}>12.13 SUN ・ 入場無料</div>
      </AbsoluteFill>
      {/* 続き：特別な日を彩る結婚式場が */}
      <AbsoluteFill style={{alignItems: 'center', top: 300}}>
        <FadeUp delay={HOOK + 2}><div style={{fontFamily: SERIF_EN, fontSize: 34, letterSpacing: '0.3em', marginRight: '-0.3em', color: GOLD_LIGHT, textShadow}}>LA LA CHANCE BELAMI</div></FadeUp>
        <div style={{height: 26}} />
        <FadeUp delay={HOOK + 6}><Divider width={420} /></FadeUp>
        <div style={{height: 40}} />
        <RevealText text="特別な日を彩る" delay={HOOK + 10} style={{...jpBody, fontSize: 64, letterSpacing: '0.12em'}} />
        <div style={{height: 18}} />
        <RevealText text="結婚式場が" delay={HOOK + 24} style={{...jpBody, fontSize: 64, letterSpacing: '0.12em'}} />
      </AbsoluteFill>
    </AbsoluteFill>
  );
};

// 2. 会場：みんなのマルシェに
const S2: React.FC<{dur: number}> = ({dur}) => (
  <AbsoluteFill>
    <Photo src="c1.jpg" dur={dur} from={1.0} to={1.1} />
    <AbsoluteFill style={{background: 'radial-gradient(ellipse at 50% 38%, rgba(30,16,6,0.72) 0%, rgba(30,16,6,0.35) 38%, rgba(30,16,6,0.08) 65%)'}} />
    <AbsoluteFill style={{alignItems: 'center', top: 560}}>
      <FadeUp delay={4}><div style={{fontFamily: ITALIC_EN, fontStyle: 'italic', fontSize: 56, ...goldText}}>Open to everyone</div></FadeUp>
      <div style={{height: 36}} />
      <RevealText text="この冬、" delay={12} style={{...jpBody, fontSize: 66, letterSpacing: '0.12em'}} />
      <div style={{height: 18}} />
      <RevealText text="みんなのマルシェに。" delay={24} style={{...jpBody, fontSize: 66, letterSpacing: '0.12em'}} />
    </AbsoluteFill>
  </AbsoluteFill>
);

// 3. タイトル：結婚式場で初開催 ララマルシェ
const S3: React.FC<{dur: number}> = ({dur}) => {
  const f = useCurrentFrame();
  const glow = interpolate(f, [10, 40], [0, 1], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'});
  return (
    <AbsoluteFill>
      <Photo src="woodhall.jpg" dur={dur} from={1.08} to={1.16} blur={3} dim={0.42} />
      <Bokeh count={22} />
      <Garland y={40} sag={170} delay={2} />
      <AbsoluteFill style={{alignItems: 'center', justifyContent: 'center', top: -40}}>
        <FadeUp delay={6}>
          <div style={{
            fontFamily: MINCHO, fontWeight: 700, fontSize: 38, letterSpacing: '0.18em', color: BROWN,
            padding: '14px 40px 14px 48px', borderRadius: 999, background: `linear-gradient(180deg, ${GOLD_LIGHT}, ${GOLD})`,
            boxShadow: '0 6px 24px rgba(0,0,0,0.35)',
          }}>結婚式場で初開催</div>
        </FadeUp>
        <div style={{height: 54}} />
        <FadeUp delay={14}><div style={{fontFamily: SERIF_EN, fontSize: 40, letterSpacing: '0.42em', marginRight: '-0.42em', ...goldText}}>LALA MARCHE</div></FadeUp>
        <div style={{height: 20}} />
        <div style={{position: 'relative'}}>
          <div style={{position: 'absolute', inset: -60, background: 'radial-gradient(ellipse, rgba(255,205,130,0.35), transparent 65%)', opacity: glow}} />
          <RevealText text="ララマルシェ" delay={18} stagger={3} gold style={{fontFamily: MINCHO, fontWeight: 700, fontSize: 142, letterSpacing: '0.04em'}} />
        </div>
        <div style={{height: 34}} />
        <FadeUp delay={40}><Divider width={560} /></FadeUp>
        <div style={{height: 34}} />
        <FadeUp delay={48}><div style={{...jpBody, fontSize: 44, letterSpacing: '0.1em'}}>〜つながる想い、ひろがる笑顔。〜</div></FadeUp>
        <div style={{height: 44}} />
        <FadeUp delay={58}>
          <div style={{
            fontFamily: MINCHO, fontWeight: 700, fontSize: 50, letterSpacing: '0.3em', color: CREAM,
            border: `2px solid ${GOLD}`, padding: '12px 40px 12px 56px', background: 'rgba(42,26,15,0.6)',
          }}>入場無料</div>
        </FadeUp>
      </AbsoluteFill>
      <GoldFrame />
    </AbsoluteFill>
  );
};

// 4. 楽しみ方：体験・ステージ・グルメ（企画書の3つのブース）
const BOOTHS = [
  {photo: 'c6.jpg', from: 1.02, to: 1.1, offsetY: 0, en: 'EXPERIENCE', jp: '体験', sub: 'チャペルでブーケづくり\nフォトスポットも'},
  {photo: 'c5_stage_v2.jpg', from: 1.02, to: 1.1, offsetY: 0, en: 'STAGE', jp: 'ステージ', sub: 'ダンスなどの\nステージ発表'},
  {photo: 'c3.jpg', from: 1.02, to: 1.1, offsetY: 0, en: 'GOURMET', jp: 'グルメ', sub: 'ほっとひと息\nおいしいひととき'},
];
// 写真の切り替えより先に文字を消し、次の文字と重ならないようにする
const BoothTextFade: React.FC<{len: number; last: boolean; children: React.ReactNode}> = ({len, last, children}) => {
  const f = useCurrentFrame();
  const o = last ? 1 : interpolate(f, [len - XF - 8, len - XF + 2], [1, 0], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'});
  return <AbsoluteFill style={{opacity: o}}>{children}</AbsoluteFill>;
};
const S4: React.FC<{dur: number}> = ({dur}) => {
  // このシーンは n4a 開始の0.25秒前 − XF から始まる
  const s0 = sec(L.n4a.start - 0.25) - XF;
  const starts = [0, sec(L.n4b.start - 0.25) - s0 - XF / 2, sec(L.n4c.start - 0.25) - s0 - XF / 2];
  return (
    <AbsoluteFill>
      {BOOTHS.map((b, i) => {
        const from = starts[i];
        const len = i === 2 ? dur - from : starts[i + 1] - from + XF;
        return (
          <Sequence key={b.en} from={from} durationInFrames={len}>
            <SceneFade dur={len} noFadeIn={i === 0}>
              <Photo src={b.photo} dur={len} from={b.from} to={b.to} offsetY={b.offsetY} />
              <AbsoluteFill style={{background: 'linear-gradient(180deg, rgba(30,16,6,0.1) 25%, rgba(30,16,6,0.72) 50%, rgba(30,16,6,0.72) 72%, rgba(30,16,6,0.25) 90%)'}} />
              <BoothTextFade len={len} last={i === 2}>
              <AbsoluteFill style={{alignItems: 'center', top: 760}}>
                <FadeUp delay={i === 0 ? XF : 6}>
                  <div style={{fontFamily: SERIF_EN, fontSize: 30, letterSpacing: '0.34em', marginRight: '-0.34em', color: GOLD_LIGHT, textShadow}}>
                    {`0${i + 1}  /  ${b.en}`}
                  </div>
                </FadeUp>
                <div style={{height: 14}} />
                <RevealText text={b.jp} delay={i === 0 ? XF + 2 : 8} stagger={3} gold style={{fontFamily: MINCHO, fontWeight: 700, fontSize: 132}} />
                <div style={{height: 18}} />
                <FadeUp delay={i === 0 ? XF + 10 : 16}>
                  <div style={{...jpBody, fontSize: 46, lineHeight: 1.55, letterSpacing: '0.06em', whiteSpace: 'pre-line'}}>{b.sub}</div>
                </FadeUp>
              </AbsoluteFill>
              </BoothTextFade>
            </SceneFade>
          </Sequence>
        );
      })}
    </AbsoluteFill>
  );
};

// 5. 開催情報：12.13 SUN 11:00 START 入場無料
const S5: React.FC<{dur: number}> = ({dur}) => (
  <AbsoluteFill>
    <Photo src="c7.jpg" dur={dur} from={1.1} to={1.02} blur={3} dim={0.5} />
    <Bokeh count={18} />
    <Garland y={40} sag={170} />
    <AbsoluteFill style={{alignItems: 'center', justifyContent: 'center', top: -30}}>
      <FadeUp delay={4}><div style={{fontFamily: SERIF_EN, fontSize: 34, letterSpacing: '0.3em', marginRight: '-0.3em', color: GOLD_LIGHT, textShadow}}>2026</div></FadeUp>
      <div style={{display: 'flex', alignItems: 'center', gap: 26, marginTop: 6}}>
        <RevealText text="12.13" delay={8} stagger={3} gold style={{fontFamily: SERIF_EN, fontSize: 210, lineHeight: 1}} />
        <FadeUp delay={22}>
          <div style={{fontFamily: SERIF_EN, fontSize: 46, lineHeight: 1.05, display: 'flex', flexDirection: 'column', alignItems: 'center', ...goldText}}>
            <span>S</span><span>U</span><span>N</span>
          </div>
        </FadeUp>
      </div>
      <div style={{height: 26}} />
      <FadeUp delay={30}><Divider width={600} /></FadeUp>
      <div style={{height: 30}} />
      <FadeUp delay={36}><div style={{fontFamily: SERIF_EN, fontSize: 68, letterSpacing: '0.06em', color: CREAM, textShadow}}>11:00 START</div></FadeUp>
      <div style={{height: 40}} />
      <FadeUp delay={48}>
        <div style={{
          fontFamily: MINCHO, fontWeight: 700, fontSize: 52, letterSpacing: '0.3em', paddingLeft: '0.3em', color: CREAM,
          border: `2px solid ${GOLD}`, padding: '12px 40px 12px 56px', background: 'rgba(42,26,15,0.55)',
        }}>入場無料</div>
      </FadeUp>
      <div style={{height: 52}} />
      <FadeUp delay={58}><div style={{fontFamily: SERIF_EN, fontSize: 34, letterSpacing: '0.16em', color: GOLD_LIGHT, textShadow}}>at LA LA CHANCE BELAMI</div></FadeUp>
      <div style={{height: 12}} />
      <FadeUp delay={64}><div style={{...jpBody, fontSize: 36, letterSpacing: '0.2em'}}>ララシャンス ベルアミー（福井市高柳）</div></FadeUp>
    </AbsoluteFill>
    <GoldFrame />
  </AbsoluteFill>
);

// 6. お誘い：はじめてのララマルシェ、ぜひ遊びに来てください
const S6: React.FC<{dur: number}> = ({dur}) => (
  <AbsoluteFill>
    <Photo src="c4.jpg" dur={dur} from={1.0} to={1.1} />
    <AbsoluteFill style={{background: 'radial-gradient(ellipse at 50% 45%, rgba(30,16,6,0.6) 0%, rgba(30,16,6,0.15) 65%)'}} />
    <AbsoluteFill style={{alignItems: 'center', top: 600}}>
      <FadeUp delay={4}><div style={{fontFamily: ITALIC_EN, fontStyle: 'italic', fontSize: 60, ...goldText}}>Welcome</div></FadeUp>
      <div style={{height: 30}} />
      <RevealText text="はじめての、ララマルシェ。" delay={10} style={{...jpBody, fontSize: 62, letterSpacing: '0.06em'}} />
      <div style={{height: 20}} />
      <RevealText text="ぜひ遊びに来てください" delay={32} style={{...jpBody, fontSize: 62, letterSpacing: '0.06em'}} />
    </AbsoluteFill>
  </AbsoluteFill>
);

// 7. エンドカード：Instagramをフォローしてお待ちください
const InstaIcon: React.FC<{size?: number}> = ({size = 64}) => (
  <svg width={size} height={size} viewBox="0 0 64 64" fill="none" stroke={GOLD_LIGHT} strokeWidth={4}>
    <rect x={6} y={6} width={52} height={52} rx={15} /><circle cx={32} cy={32} r={12} /><circle cx={47} cy={17} r={2.5} fill={GOLD_LIGHT} stroke="none" />
  </svg>
);
const S7: React.FC<{dur: number}> = ({dur}) => (
  <AbsoluteFill>
    <Photo src="c7.jpg" dur={dur} from={1.15} to={1.08} blur={6} dim={0.6} />
    <Bokeh count={24} />
    <Garland y={40} sag={170} />
    <AbsoluteFill style={{alignItems: 'center', justifyContent: 'center', top: -60}}>
      <FadeUp delay={2}><div style={{fontFamily: SERIF_EN, fontSize: 34, letterSpacing: '0.42em', marginRight: '-0.42em', ...goldText}}>LALA MARCHE</div></FadeUp>
      <div style={{height: 14}} />
      <FadeUp delay={6}><div style={{fontFamily: MINCHO, fontWeight: 700, fontSize: 96, ...goldText}}>ララマルシェ</div></FadeUp>
      <div style={{height: 22}} />
      <FadeUp delay={10}><div style={{fontFamily: SERIF_EN, fontSize: 36, letterSpacing: '0.1em', color: CREAM, textShadow}}>2026.12.13 SUN 11:00 START</div></FadeUp>
      <div style={{height: 10}} />
      <FadeUp delay={12}><div style={{...jpBody, fontSize: 34, letterSpacing: '0.12em'}}>入場無料 ／ ララシャンス ベルアミー</div></FadeUp>
      <div style={{height: 46}} />
      <FadeUp delay={18}><Divider width={600} /></FadeUp>
      <div style={{height: 46}} />
      <FadeUp delay={24}><div style={{...jpBody, fontSize: 44, letterSpacing: '0.06em', lineHeight: 1.6}}>イベントの詳細は<br />Instagramで随時お知らせします</div></FadeUp>
      <div style={{height: 40}} />
      <FadeUp delay={34}>
        <div style={{display: 'flex', alignItems: 'center', gap: 20, padding: '20px 40px', border: `1.5px solid ${GOLD}`, background: 'rgba(42,26,15,0.5)'}}>
          <InstaIcon size={58} />
          <div style={{fontFamily: MINCHO, fontWeight: 500, fontSize: 40, letterSpacing: '0.03em', color: CREAM}}>@lalachance_belami_fukui_</div>
        </div>
      </FadeUp>
      <div style={{height: 40}} />
      <RevealText text="フォローしてお待ちください" delay={44} gold style={{fontFamily: MINCHO, fontWeight: 700, fontSize: 54, letterSpacing: '0.08em'}} />
    </AbsoluteFill>
    <GoldFrame />
  </AbsoluteFill>
);

// ===== 字幕（ナレーション版のみ） =====
const splitCaption = (text: string) => text.split(/(?<=。)/).map((s) => s.trim()).filter(Boolean);
const Captions: React.FC = () => {
  const frame = useCurrentFrame();
  const t = frame / FPS;
  let current: string | null = null; let local = 0; let segDur = 1;
  for (const l of timeline.lines) {
    const parts = splitCaption(l.text);
    const total = parts.reduce((a, p) => a + p.length, 0);
    let s = l.start;
    for (const p of parts) {
      const d = (l.dur * p.length) / total;
      if (t >= s - 0.05 && t < s + d + (p === parts[parts.length - 1] ? 0.25 : 0)) { current = p; local = t - s; segDur = d; }
      s += d;
    }
  }
  if (!current) return null;
  const o = interpolate(local, [-0.05, 0.12, segDur + 0.05, segDur + 0.25], [0, 1, 1, 0], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'});
  return (
    <AbsoluteFill style={{justifyContent: 'flex-end', alignItems: 'center', paddingBottom: 430}}>
      <div style={{
        opacity: o, maxWidth: 860, padding: '14px 30px', borderRadius: 14, background: 'rgba(28,16,8,0.62)',
        fontFamily: MINCHO, fontWeight: 700, fontSize: 40, lineHeight: 1.5, color: '#fffaf0', textAlign: 'center',
        wordBreak: 'keep-all', overflowWrap: 'anywhere',
      }}>{current}</div>
    </AbsoluteFill>
  );
};

// ===== 本体 =====
export const LalaMarche: React.FC<{narration: boolean}> = ({narration}) => {
  useFonts();
  const {durationInFrames} = useVideoConfig();
  // シーン境界はナレーションの開始位置に合わせる
  const b = [0, sec(L.n2.start - 0.25), sec(L.n3.start - 0.25), sec(L.n4a.start - 0.25), sec(L.n5.start - 0.25), sec(L.n6.start - 0.25), sec(L.n7.start - 0.25), durationInFrames];
  const scenes = [S1, S2, S3, S4, S5, S6, S7];
  return (
    <AbsoluteFill style={{background: BROWN}}>
      {scenes.map((S, i) => (
        <Scene key={i} first={i === 0} from={Math.max(0, b[i] - (i ? XF : 0))} to={b[i + 1]}>
          <S dur={b[i + 1] - b[i] + XF * 2} />
        </Scene>
      ))}
      <Snow count={60} opacity={0.75} />
      {narration && <Captions />}
      {narration && timeline.lines.map((l) => (
        <Sequence key={l.id} from={sec(l.start)} durationInFrames={sec(l.dur) + 10}>
          <Audio src={staticFile(`lalamarche/${l.id}.wav`)} />
        </Sequence>
      ))}
    </AbsoluteFill>
  );
};
