// Puru sample: 3 Blender miniature shots + Telugu motion-design labels pinned to tracked 3D points.
import React from 'react';
import {AbsoluteFill, OffthreadVideo, Sequence, interpolate, spring, staticFile, useCurrentFrame, Easing} from 'remotion';
import TR from './tracks.json';
const FONT = '"Noto Sans Telugu", Poppins, "DejaVu Sans", Arial, sans-serif';
const FPS = 30, SRC_FPS = 24, W = 1080, H = 1920, GOLD = '#FFC23D';
const clamp = {extrapolateLeft: 'clamp' as const, extrapolateRight: 'clamp' as const};
const ease = Easing.bezier(0.16, 1, 0.3, 1);
type Tracks = Record<string, Record<string, Record<string, number[]>>>;
const T = TR as unknown as Tracks;
export const SHOT_LEN = 150; // 5 s per shot
const pt = (shot: string, key: string, t: number) => {
  const tr = T[shot]; const n = Object.keys(tr).length;
  const f = Math.min(n, Math.max(1, Math.round((t * SRC_FPS) / FPS) + 1));
  const [x, y, z] = tr[String(f)][key]; return {x: x * W, y: y * H, vis: z > 0};
};
// palm-leaf name tag (channel style)
const Leaf: React.FC<{v: string; sub?: string; size?: number}> = ({v, sub, size = 50}) => (
  <div style={{display: 'inline-block', background: 'linear-gradient(#F2DAA2, #E2C07C)', borderRadius: '60px / 34px', padding: '12px 34px 14px',
    boxShadow: '0 6px 0 #A87A34, 0 14px 30px rgba(0,0,0,0.45)', fontFamily: FONT, color: '#3A1E0B', textAlign: 'center', whiteSpace: 'nowrap'}}>
    <div style={{fontSize: size, fontWeight: 900, lineHeight: 1.25}}>{v}</div>
    {sub && <div style={{fontSize: size * 0.56, fontWeight: 700, opacity: 0.8}}>{sub}</div>}
  </div>
);
// tag that follows a tracked point: dot on the subject, leader line up, label above
const Pin: React.FC<{shot: string; k: string; v: string; sub?: string; at: number; out?: number; lift?: number; dx?: number; size?: number}> =
  ({shot, k, v, sub, at, out = SHOT_LEN - 6, lift = 170, dx = 0, size}) => {
  const t = useCurrentFrame(); const p = pt(shot, k, t); if (!p.vis) return null;
  const s = spring({frame: t - at, fps: FPS, config: {damping: 14, stiffness: 150}});
  const o = interpolate(t, [at, at + 6, out - 8, out], [0, 1, 1, 0], clamp);
  const line = lift * interpolate(t - at, [0, 10], [0, 1], {...clamp, easing: ease});
  return <div style={{position: 'absolute', left: 0, top: 0, opacity: o}}>
    <div style={{position: 'absolute', left: p.x - 9, top: p.y - 9, width: 18, height: 18, borderRadius: 9, background: GOLD, boxShadow: '0 0 0 5px rgba(0,0,0,0.35)'}} />
    <div style={{position: 'absolute', left: p.x - 2, top: p.y - line, width: 4, height: line, background: 'linear-gradient(rgba(255,194,61,0.2), #FFC23D)'}} />
    <div style={{position: 'absolute', left: p.x + dx, top: p.y - lift, transform: `translate(-50%, -100%) scale(${0.6 + 0.4 * s})`, transformOrigin: '50% 100%'}}>
      <Leaf v={v} sub={sub} size={size} />
    </div>
  </div>;
};
// big title block (top of frame)
const Title: React.FC<{k?: string; v: string; at: number; top?: number}> = ({k, v, at, top = 230}) => {
  const t = useCurrentFrame(); const s = spring({frame: t - at, fps: FPS, config: {damping: 16, stiffness: 120}});
  const o = interpolate(t, [at, at + 8, SHOT_LEN - 10, SHOT_LEN - 2], [0, 1, 1, 0], clamp);
  return <div style={{position: 'absolute', top, width: '100%', textAlign: 'center', opacity: o, transform: `translateY(${(1 - s) * 40}px)`, fontFamily: FONT}}>
    {k && <div style={{display: 'inline-block', background: '#7A1A12', color: '#F6E7C6', fontSize: 38, fontWeight: 800, padding: '6px 26px', borderRadius: 12, marginBottom: 14}}>{k}</div>}
    <div style={{fontSize: 96, fontWeight: 900, color: 'white', lineHeight: 1.2, textShadow: '0 6px 0 rgba(0,0,0,0.55), 0 0 30px rgba(0,0,0,0.6)', WebkitTextStroke: '3px rgba(0,0,0,0.75)', paintOrder: 'stroke fill'}}>{v}</div>
  </div>;
};
// counting number chip
const Counter: React.FC<{to: number; label: string; at: number; top?: number}> = ({to, label, at, top = 260}) => {
  const t = useCurrentFrame(); const n = Math.round(to * interpolate(t, [at, at + 40], [0, 1], {...clamp, easing: ease}));
  const o = interpolate(t, [at, at + 6, SHOT_LEN - 10, SHOT_LEN - 2], [0, 1, 1, 0], clamp);
  return <div style={{position: 'absolute', top, width: '100%', textAlign: 'center', opacity: o, fontFamily: FONT}}>
    <div style={{fontSize: 150, fontWeight: 900, color: GOLD, lineHeight: 1, textShadow: '0 8px 0 rgba(0,0,0,0.5)', WebkitTextStroke: '4px rgba(0,0,0,0.7)', paintOrder: 'stroke fill'}}>{n}</div>
    <div style={{fontSize: 62, fontWeight: 900, color: 'white', textShadow: '0 5px 0 rgba(0,0,0,0.55)', WebkitTextStroke: '2px rgba(0,0,0,0.7)', paintOrder: 'stroke fill'}}>{label}</div>
  </div>;
};
const Shot: React.FC<{src: string; children?: React.ReactNode}> = ({src, children}) => {
  const t = useCurrentFrame(); const dip = interpolate(t, [0, 8, SHOT_LEN - 6, SHOT_LEN], [1, 0, 0, 0.9], clamp);
  return <AbsoluteFill style={{background: 'black'}}>
    <OffthreadVideo src={staticFile(src)} />
    {children}
    <AbsoluteFill style={{background: 'black', opacity: dip}} />
  </AbsoluteFill>;
};
export const Sample: React.FC = () => (
  <AbsoluteFill style={{background: 'black'}}>
    <Sequence durationInFrames={SHOT_LEN}>
      <Shot src="mini/clip_A.mp4">
        <Title k="క్రీ.పూ. 326" v="హైడాస్పెస్ యుద్ధం" at={8} />
        <Pin shot="A" k="greek" v="అలెగ్జాండర్ సైన్యం" at={40} lift={120} size={44} />
        <Pin shot="A" k="river" v="జీలం నది" at={58} lift={110} dx={120} size={44} />
        <Pin shot="A" k="indian" v="పురు సైన్యం" at={76} lift={130} size={44} />
      </Shot>
    </Sequence>
    <Sequence from={SHOT_LEN} durationInFrames={SHOT_LEN}>
      <Shot src="mini/clip_B.mp4">
        <Counter to={200} label="యుద్ధ ఏనుగులు" at={6} />
        <Pin shot="B" k="puru" v="పురు" sub="పౌరవ రాజు" at={84} lift={190} />
      </Shot>
    </Sequence>
    <Sequence from={SHOT_LEN * 2} durationInFrames={SHOT_LEN}>
      <Shot src="mini/clip_C.mp4">
        <Pin shot="C" k="alexander" v="అలెగ్జాండర్" sub="మాసిడోనియా రాజు" at={20} lift={210} />
        <Pin shot="C" k="horse" v="బుసెఫాలస్" sub="అలెగ్జాండర్ గుర్రం" at={50} lift={150} size={42} />
      </Shot>
    </Sequence>
  </AbsoluteFill>
);
