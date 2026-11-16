import React from 'react';
import {AbsoluteFill, Audio, Img, OffthreadVideo, interpolate, spring, staticFile, useCurrentFrame, Easing} from 'remotion';
import T from './timing.json';
const FONT = '"Noto Sans Telugu", Poppins, "DejaVu Sans", Arial, sans-serif';
const SERIF = '"Noto Serif Telugu", "Noto Sans Telugu", serif';
const FPS = 30, GOLD = '#FFC23D', CREAM = '#F6E7C6', BLOOD = '#E0483A', ORANGE = '#FFA41F', GREEN = '#7BE08A';
const clamp = {extrapolateLeft: 'clamp' as const, extrapolateRight: 'clamp' as const};
const ease = Easing.bezier(0.16, 1, 0.3, 1);
const idx = (shot: string) => T.lines.findIndex((l) => l.shot === shot);
const span = (shot: string) => { const i = idx(shot); return [T.starts[i] * FPS, (T.starts[i] + T.durs[i]) * FPS]; };
const useShot = (shot: string) => {
  const f = useCurrentFrame(); const i = idx(shot);
  const from = Math.round(T.starts[i] * FPS), dur = Math.round(T.durs[i] * FPS);
  return {t: f - from, dur, active: f >= from && f < from + dur};
};
const Pop: React.FC<{at: number; t: number; children: React.ReactNode; style?: React.CSSProperties}> = ({at, t, children, style}) => {
  const s = spring({frame: t - at, fps: FPS, config: {damping: 15, stiffness: 140}});
  return <div style={{...style, opacity: interpolate(t - at, [0, 6], [0, 1], clamp), transform: `translateY(${(1 - s) * 50}px)`}}>{children}</div>;
};
const Fade: React.FC<{t: number; dur: number; children: React.ReactNode}> = ({t, dur, children}) => (
  <AbsoluteFill style={{opacity: interpolate(t, [0, 8, dur - 8, dur], [0, 1, 1, 0], clamp)}}>{children}</AbsoluteFill>
);
// palm-leaf label, matching the channel logo
const Leaf: React.FC<{k?: string; v: string; sub?: string; c?: string}> = ({k, v, sub, c = '#3A1E0B'}) => (
  <div style={{display: 'inline-block', background: 'linear-gradient(#F2DAA2, #E2C07C)', borderRadius: '60px / 34px', padding: '18px 46px 20px',
    boxShadow: '0 8px 0 #A87A34, 0 18px 40px rgba(0,0,0,0.45)', fontFamily: FONT, color: c, textAlign: 'center', marginBottom: 22}}>
    {k && <div style={{fontSize: 30, fontWeight: 800, opacity: 0.75, letterSpacing: 1}}>{k}</div>}
    <div style={{fontSize: 56, fontWeight: 900, lineHeight: 1.25}}>{v}</div>
    {sub && <div style={{fontSize: 30, fontWeight: 700, opacity: 0.8}}>{sub}</div>}
  </div>
);
const TopLeaf: React.FC<{shot: string; at: number; k?: string; v: string; sub?: string; top?: number}> = ({shot, at, k, v, sub, top = 300}) => {
  const {t, active, dur} = useShot(shot); if (!active) return null;
  return <Fade t={t} dur={dur}><Pop at={Math.round(dur * at)} t={t} style={{position: 'absolute', width: '100%', top, textAlign: 'center'}}>
    <Leaf k={k} v={v} sub={sub} /></Pop></Fade>;
};
// ---------- captions (Telugu, 2-3 words at a time) ----------
type Ch = {words: string[]; s: number; e: number};
const CH: Ch[][] = T.lines.map((ln, i) => {
  const words = ln.text.split(' '); const w = words.map((x) => Math.max(x.replace(/[?.!,…]/g, '').length, 2));
  const total = w.reduce((a, b) => a + b, 0); const d = T.durs[i] - (i === T.lines.length - 1 ? 3.6 : 0.7);
  const out: Ch[] = []; let cur: string[] = []; let cw = 0; let tc = T.starts[i] + 0.05;
  words.forEach((wd, k) => {
    cur.push(wd); cw += w[k];
    if (cur.length === 3 || cur.join('').length >= 16 || /[?.!,…]$/.test(wd) || k === words.length - 1) {
      const e = tc + (d * cw) / total; out.push({words: cur, s: tc, e}); tc = e; cur = []; cw = 0;
    }
  });
  return out;
});
const norm = (x: string) => x.replace(/[?.!,…]/g, '');
const Captions: React.FC = () => {
  const f = useCurrentFrame(); const sec = f / FPS;
  for (let i = 0; i < CH.length; i++) for (const c of CH[i]) {
    if (sec >= c.s && sec < c.e) {
      const k = T.lines[i].keywords.map(norm);
      const sc = interpolate(f - c.s * FPS, [0, 4], [0.86, 1], {...clamp, easing: ease});
      return <div style={{position: 'absolute', top: 1250, width: '100%', textAlign: 'center', fontFamily: FONT, fontWeight: 900, fontSize: 70,
        lineHeight: 1.3, color: 'white', transform: `scale(${sc})`, padding: '0 70px', textShadow: '0 5px 0 rgba(0,0,0,0.55), 0 0 24px rgba(0,0,0,0.7)',
        WebkitTextStroke: '3px rgba(0,0,0,0.8)', paintOrder: 'stroke fill'}}>
        {c.words.map((wd, n) => <span key={n} style={{color: k.includes(norm(wd)) ? GOLD : 'white'}}>{wd}{n < c.words.length - 1 ? ' ' : ''}</span>)}
      </div>;
    }
  }
  return null;
};
const Dips: React.FC = () => {
  const f = useCurrentFrame(); let o = 0;
  for (let i = 1; i < T.starts.length; i++) o = Math.max(o, interpolate(f - Math.round(T.starts[i] * FPS), [-5, 0, 7], [0, 0.85, 0], clamp));
  return <AbsoluteFill style={{background: '#050403', opacity: o}} />;
};
// ---------- weather, dust, miniature finish ----------
const rnd = (n: number) => { const x = Math.sin(n * 127.1) * 43758.5453; return x - Math.floor(x); };
const Rain: React.FC = () => {
  const f = useCurrentFrame(); const [a, b] = span('storm');
  if (f < a - 20 || f > b + 8) return null;
  const k = interpolate(f, [a - 20, a, b - 10, b + 8], [0, 1, 1, 0], clamp);
  const drops = Array.from({length: 170}, (_, n) => {
    const x = rnd(n) * 1300 - 110, sp = 60 + rnd(n + 9) * 40, y = ((f * sp + rnd(n + 3) * 2200) % 2200) - 200;
    return <line key={n} x1={x} y1={y} x2={x - 12} y2={y + 55} stroke="rgba(205,220,255,0.42)" strokeWidth={2.2} />;
  });
  const L = [0.06, 0.3, 0.33, 0.52, 0.8].map((q) => a + (b - a) * q);
  const flash = Math.max(...L.map((l) => interpolate(f - l, [-1, 0, 2, 3, 7], [0, 0.7, 0.15, 0.45, 0], clamp)));
  return <AbsoluteFill style={{opacity: k}}><svg width={1080} height={1920}>{drops}</svg><AbsoluteFill style={{background: '#dfe8ff', opacity: flash}} /></AbsoluteFill>;
};
const Dust: React.FC = () => {
  const f = useCurrentFrame(); const [a, b] = span('battle');
  if (f < a || f > b) return null;
  const k = interpolate(f, [a, a + 40, b - 15, b], [0, 1, 1, 0], clamp);
  return <AbsoluteFill style={{opacity: k * 0.45, background: 'linear-gradient(to top, rgba(175,135,85,0.8), rgba(175,135,85,0) 60%)'}} />;
};
// tilt-shift finish: soft bands top and bottom, warm vignette
const Mini: React.FC = () => <>
  <AbsoluteFill style={{background: 'radial-gradient(ellipse at center, rgba(0,0,0,0) 55%, rgba(10,5,0,0.55) 100%)'}} />
</>;
const Logo: React.FC = () => {
  const f = useCurrentFrame(); const o = interpolate(f, [15, 30, T.end - 110, T.end - 95], [0, 0.6, 0.6, 0], clamp);
  return <Img src={staticFile('logo_wm.png')} style={{position: 'absolute', left: 40, top: 170, width: 110, height: 110, opacity: o}} />;
};
// ---------- story overlays ----------
const Open: React.FC = () => {
  const {t, active, dur} = useShot('open'); if (!active) return null;
  return <Fade t={t} dur={dur}>
    <Pop at={8} t={t} style={{position: 'absolute', width: '100%', top: 250, textAlign: 'center', fontFamily: SERIF}}>
      <div style={{fontSize: 40, color: GOLD, fontWeight: 800, letterSpacing: 2, textShadow: '0 4px 18px rgba(0,0,0,0.9)'}}>క్రీ.పూ. 326 · జీలం నది యుద్ధం</div>
      <div style={{fontSize: 118, fontWeight: 900, color: 'white', lineHeight: 1.15, textShadow: '0 6px 30px rgba(0,0,0,0.85)'}}>పురు<br /><span style={{fontSize: 64, color: GOLD}}>vs</span><br />అలెగ్జాండర్</div>
    </Pop>
  </Fade>;
};
const King: React.FC = () => {
  const {t, active, dur} = useShot('king'); if (!active) return null;
  return <Fade t={t} dur={dur}><Pop at={Math.round(dur * 0.66)} t={t} style={{position: 'absolute', left: 60, right: 60, top: 280, textAlign: 'center'}}>
    <div style={{display: 'inline-block', background: 'linear-gradient(#F2DAA2, #E2C07C)', borderRadius: '70px / 40px', padding: '30px 44px',
      boxShadow: '0 10px 0 #A87A34, 0 20px 50px rgba(0,0,0,0.5)', fontFamily: SERIF, color: '#3A1E0B'}}>
      <div style={{fontSize: 34, fontWeight: 800, opacity: 0.75}}>పురు</div>
      <div style={{fontSize: 64, fontWeight: 900, lineHeight: 1.3}}>“ఒక రాజు, ఇంకో రాజుని<br />ఎలా చూస్తాడో… అలా.”</div>
      <div style={{fontSize: 24, fontWeight: 700, opacity: 0.7, marginTop: 6}}>Arrian, Anabasis 5.19</div>
    </div></Pop></Fade>;
};
const Finale: React.FC = () => {
  const f = useCurrentFrame(); const [a, b] = span('legacy'); if (f < a) return null; const t = f - a;
  const endIn = b - 105; const e = interpolate(f, [endIn, endIn + 18], [0, 1], clamp);
  return <AbsoluteFill style={{fontFamily: SERIF}}>
    <Pop at={Math.round((b - a) * 0.3)} t={t} style={{position: 'absolute', width: '100%', top: 270, textAlign: 'center', opacity: 1 - e}}>
      <div style={{fontSize: 40, color: GOLD, fontWeight: 800, textShadow: '0 4px 18px rgba(0,0,0,0.9)'}}>పురుషోత్తముడు</div>
      <div style={{fontSize: 150, fontWeight: 900, color: 'white', lineHeight: 1.1, textShadow: '0 6px 30px rgba(0,0,0,0.85)'}}>రాజు</div>
    </Pop>
    <AbsoluteFill style={{opacity: e, background: 'radial-gradient(ellipse at center, rgba(42,22,8,0.92), rgba(20,8,2,0.97))', alignItems: 'center', justifyContent: 'center'}}>
      <Img src={staticFile('logo_wm.png')} style={{width: 420, height: 420, transform: `scale(${0.9 + 0.1 * e})`}} />
      <div style={{fontSize: 46, color: CREAM, fontWeight: 800, marginTop: 40}}>మీ ఊరి చరిత్ర కూడా చెప్పాలా?</div>
      <div style={{fontSize: 36, color: GOLD, fontWeight: 700, marginTop: 14, fontFamily: FONT}}>Follow @charithracheppinakatha</div>
      <div style={{position: 'absolute', bottom: 60, width: '100%', textAlign: 'center', color: 'rgba(255,255,255,0.6)', fontSize: 19, padding: '0 60px', lineHeight: 1.4, fontFamily: 'DejaVu Sans, Arial'}}>
        Sources: Arrian, Anabasis 5; Curtius 8.13–14; Plutarch, Alexander 60; Diodorus 19.14 · Miniature figures: Quaternius (CC0), elephant by syncopika (OpenGameArt, CC0) · HDRI: Poly Haven (CC0)
      </div>
    </AbsoluteFill>
  </AbsoluteFill>;
};
export const Main: React.FC<{bg: string; audio: string; preview: boolean}> = ({bg, audio, preview}) => (
  <AbsoluteFill style={{background: '#0b0805'}}>
    {preview ? <AbsoluteFill style={{background: 'linear-gradient(#4a3a26, #0b0805)'}} /> : <OffthreadVideo src={staticFile(bg)} muted />}
    {!preview && <Audio src={staticFile(audio)} />}
    <Rain /><Dust /><Mini /><Dips />
    <Open />
    <TopLeaf shot="demand" at={0.55} k="పురు జవాబు" v="ఆయుధాలతో కలుద్దాం!" />
    <TopLeaf shot="ambhi" at={0.3} k="మొదటి ద్రోహం" v="తక్షశిల రాజు అంభి" />
    <TopLeaf shot="river" at={0.08} k="జీలం నది" v="గ్రీకులు: హైడాస్పీస్" sub="ఏనుగులు: 85–200 (గ్రీకు లెక్కలు)" />
    <TopLeaf shot="feint" at={0.1} k="రాత్రి రాత్రీ" v="దొంగ దాడులు" />
    <TopLeaf shot="storm" at={0.62} k="తెల్లవారి చూస్తే" v="నది మధ్యలో దీవి!" />
    <TopLeaf shot="son" at={0.4} k="పురు కొడుకు" v="బురదలో రథాలు" />
    <TopLeaf shot="battle" at={0.35} k="ఏనుగులు vs" v="5–6 మీటర్ల బల్లాలు" sub="మాసిడోనియన్ సరిస్సా" />
    <King />
    <TopLeaf shot="return" at={0.12} k="అలెగ్జాండర్" v="రాజ్యం తిరిగిచ్చాడు" sub="ఇంకా పెద్దది చేసి" />
    <TopLeaf shot="murder" at={0.5} k="మూడో ద్రోహం" v="సేనాని యూడెమస్" />
    <Finale /><Captions /><Logo />
  </AbsoluteFill>
);
