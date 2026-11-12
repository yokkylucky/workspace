import {useEffect, useMemo, useRef} from 'react';
import {AbsoluteFill, useCurrentFrame, useVideoConfig} from 'remotion';
import {ThreeCanvas} from '@remotion/three';
import gsap from 'gsap';

// GSAPのタイムラインは自動再生せず、Remotionの現在フレームで seek して決定的に描画する
const GsapTitle: React.FC = () => {
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();
  const root = useRef<HTMLDivElement>(null);
  const tl = useMemo(() => gsap.timeline({paused: true}), []);

  useEffect(() => {
    const chars = root.current!.querySelectorAll('span');
    tl.clear()
      .from(chars, {y: 80, opacity: 0, rotate: 12, stagger: 0.05, duration: 0.6, ease: 'back.out(2)'})
      .to(root.current, {letterSpacing: '0.08em', duration: 1, ease: 'power2.inOut'}, '+=0.3');
  }, [tl]);

  useEffect(() => { tl.seek(frame / fps); }, [frame, fps, tl]);

  return (
    <div ref={root} style={{fontFamily: 'sans-serif', fontWeight: 800, fontSize: 96, color: '#f5f1e8'}}>
      {'Video Studio'.split('').map((c, i) => <span key={i} style={{display: 'inline-block'}}>{c === ' ' ? ' ' : c}</span>)}
    </div>
  );
};

const Knot: React.FC = () => {
  const frame = useCurrentFrame();
  return (
    <mesh rotation={[frame * 0.02, frame * 0.03, 0]}>
      <torusKnotGeometry args={[1, 0.32, 160, 24]} />
      <meshStandardMaterial color="#e2603a" roughness={0.35} metalness={0.2} />
    </mesh>
  );
};

export const Demo: React.FC = () => {
  const {width, height} = useVideoConfig();
  return (
    <AbsoluteFill style={{background: '#14161c'}}>
      <ThreeCanvas width={width} height={height} camera={{position: [0, 0, 5]}}>
        <ambientLight intensity={0.4} />
        <directionalLight position={[3, 4, 5]} intensity={2} />
        <Knot />
      </ThreeCanvas>
      <AbsoluteFill style={{justifyContent: 'flex-end', alignItems: 'center', paddingBottom: 70}}>
        <GsapTitle />
      </AbsoluteFill>
    </AbsoluteFill>
  );
};
