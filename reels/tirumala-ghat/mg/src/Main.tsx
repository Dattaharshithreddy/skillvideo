import React from 'react';
import {AbsoluteFill, Audio, OffthreadVideo, interpolate, spring, staticFile, useCurrentFrame, Easing} from 'remotion';
import T from './timing.json';
const FONT = 'Poppins, "DejaVu Sans", Arial, sans-serif';
const FPS = 30, GREEN = '#4DFF8A', ORANGE = '#FFA41F', RED = '#FF3B30', GOLD = '#FFC23D';
const clamp = {extrapolateLeft: 'clamp' as const, extrapolateRight: 'clamp' as const};
const ease = Easing.bezier(0.16, 1, 0.3, 1);
const card: React.CSSProperties = {background: 'rgba(6,10,18,0.72)', borderRadius: 28, border: '2px solid rgba(255,255,255,0.14)',
  boxShadow: '0 18px 50px rgba(0,0,0,0.45)', color: 'white', fontFamily: FONT};
const idx = (shot: string) => T.lines.findIndex((l) => l.shot === shot);
const useShot = (shot: string) => {
  const f = useCurrentFrame(); const i = idx(shot);
  const from = Math.round(T.starts[i] * FPS), dur = Math.round(T.durs[i] * FPS);
  return {t: f - from, dur, active: f >= from && f < from + dur};
};
const Pop: React.FC<{at: number; t: number; children: React.ReactNode; style?: React.CSSProperties}> = ({at, t, children, style}) => {
  const s = spring({frame: t - at, fps: FPS, config: {damping: 15, stiffness: 150}});
  return <div style={{...style, opacity: interpolate(t - at, [0, 6], [0, 1], clamp), transform: `translateY(${(1 - s) * 60}px)`}}>{children}</div>;
};
const Fade: React.FC<{t: number; dur: number; children: React.ReactNode}> = ({t, dur, children}) => (
  <AbsoluteFill style={{opacity: interpolate(t, [0, 8, dur - 6, dur], [0, 1, 1, 0], clamp)}}>{children}</AbsoluteFill>
);
const Tag: React.FC<{c: string; k: string; v: string; sub?: string}> = ({c, k, v, sub}) => (
  <div style={{...card, padding: '18px 28px', borderColor: c, marginBottom: 16}}>
    <div style={{fontSize: 26, letterSpacing: 4, fontWeight: 800, color: c}}>{k}</div>
    <div style={{fontSize: 52, fontWeight: 900, lineHeight: 1.05}}>{v}</div>
    {sub && <div style={{fontSize: 28, opacity: 0.85, marginTop: 4}}>{sub}</div>}
  </div>
);
// ---------- captions ----------
type Ch = {words: string[]; s: number; e: number};
const CH: Ch[][] = T.lines.map((ln, i) => {
  const words = ln.text.split(' '); const w = words.map((x) => Math.max(x.replace(/[?.!,]/g, '').length, 2));
  const total = w.reduce((a, b) => a + b, 0); const d = T.durs[i] - 0.4;
  const out: Ch[] = []; let cur: string[] = []; let cw = 0; let tc = T.starts[i];
  words.forEach((wd, k) => {
    cur.push(wd); cw += w[k];
    if (cur.length === 3 || cur.join('').length >= 13 || /[?.!,]$/.test(wd) || k === words.length - 1) {
      const e = tc + (d * cw) / total; out.push({words: cur, s: tc, e}); tc = e; cur = []; cw = 0;
    }
  });
  return out;
});
const Captions: React.FC = () => {
  const f = useCurrentFrame(); const sec = f / FPS;
  for (let i = 0; i < CH.length; i++) for (const c of CH[i]) {
    if (sec >= c.s && sec < c.e + (c === CH[i][CH[i].length - 1] ? 0.3 : 0)) {
      const k = T.lines[i].keywords.map((x) => x.toLowerCase().replace(/[?.!,]/g, ''));
      const sc = interpolate(f - c.s * FPS, [0, 4], [0.84, 1], {...clamp, easing: ease});
      return <div style={{position: 'absolute', top: 1230, width: '100%', textAlign: 'center', fontFamily: FONT, fontWeight: 900, fontSize: 86,
        lineHeight: 1.08, color: 'white', transform: `scale(${sc})`, padding: '0 70px', textShadow: '0 6px 0 rgba(0,0,0,0.55), 0 0 26px rgba(0,0,0,0.6)',
        WebkitTextStroke: '3px rgba(0,0,0,0.85)', paintOrder: 'stroke fill'}}>
        {c.words.map((wd, n) => <span key={n} style={{color: k.includes(wd.toLowerCase().replace(/[?.!,]/g, '')) ? GOLD : 'white'}}>{wd}{n < c.words.length - 1 ? ' ' : ''}</span>)}
      </div>;
    }
  }
  return null;
};
const Dips: React.FC = () => {
  const f = useCurrentFrame(); let o = 0;
  for (let i = 1; i < T.starts.length; i++) o = Math.max(o, interpolate(f - Math.round(T.starts[i] * FPS), [-4, 0, 6], [0, 0.8, 0], clamp));
  return <AbsoluteFill style={{background: '#03050a', opacity: o}} />;
};
// ---------- shot overlays ----------
const Open: React.FC = () => {
  const {t, active, dur} = useShot('open'); if (!active) return null;
  return <Fade t={t} dur={dur}>
    <Pop at={6} t={t} style={{position: 'absolute', width: '100%', top: 230, textAlign: 'center', fontFamily: FONT}}>
      <div style={{fontSize: 32, letterSpacing: 8, color: GOLD, fontWeight: 800}}>HOW IT WAS BUILT</div>
      <div style={{fontSize: 96, fontWeight: 900, color: 'white', lineHeight: 1, textShadow: '0 6px 30px rgba(0,0,0,0.7)'}}>TIRUMALA<br />GHAT ROAD</div>
    </Pop>
  </Fade>;
};
const TwoRoads: React.FC = () => {
  const {t, active, dur} = useShot('two_roads'); if (!active) return null;
  return <Fade t={t} dur={dur}><div style={{position: 'absolute', left: 60, top: 230, width: 620}}>
    <Pop at={4} t={t}><Tag c={GREEN} k="1944 · FIRST GHAT ROAD" v="Survives every monsoon" /></Pop>
    <Pop at={Math.round(dur * 0.45)} t={t}><Tag c={ORANGE} k="1974 · SECOND GHAT ROAD" v="Landslides, closures" /></Pop>
  </div></Fade>;
};
const Track: React.FC = () => {
  const {t, active, dur} = useShot('cart_track'); if (!active) return null;
  return <Fade t={t} dur={dur}><Pop at={6} t={t} style={{position: 'absolute', left: 60, top: 240}}>
    <Tag c={GOLD} k="BEFORE 1944" v="Foot path & bullock-cart track" /></Pop></Fade>;
};
const People: React.FC = () => {
  const {t, active, dur} = useShot('people'); if (!active) return null;
  const P = [['PLAN CREDITED TO', 'Sir M. Visvesvaraya', 'Bharat Ratna engineer'], ['ENGINEER IN CHARGE', 'A. Nageswara Iyer', 'The Hindu, 1944'],
    ['BUILT BY', 'Gannon Dunkerley & Co.', 'contractors']];
  return <Fade t={t} dur={dur}><div style={{position: 'absolute', left: 60, right: 60, top: 220}}>
    {P.map(([k, v, s], n) => <Pop key={k} at={Math.round(dur * (0.02 + 0.3 * n))} t={t}><Tag c={GOLD} k={k} v={v} sub={s} /></Pop>)}
  </div></Fade>;
};
const Lay: React.FC = () => {
  const {t, active, dur} = useShot('lay_road'); if (!active) return null;
  return <Fade t={t} dur={dur}><Pop at={Math.round(dur * 0.4)} t={t} style={{position: 'absolute', left: 60, top: 240}}>
    <Tag c={GREEN} k="THE RULE" v="Follow the old track" sub="gentle slope all the way" /></Pop></Fade>;
};
const Straight: React.FC = () => {
  const {t, active, dur} = useShot('straight'); if (!active) return null;
  return <Fade t={t} dur={dur}><div style={{position: 'absolute', left: 60, top: 230, width: 700}}>
    <Pop at={6} t={t}><Tag c={RED} k="STRAIGHT UP" v="Stretches over 60% steep" /></Pop>
    <Pop at={Math.round(dur * 0.5)} t={t}><Tag c={GREEN} k="OLD ROAD" v="Average slope 3.4%" sub="635 m climb · ~18.5 km" /></Pop>
  </div></Fade>;
};
const Hairpins: React.FC = () => {
  const {t, active, dur} = useShot('hairpins'); if (!active) return null;
  const n = Math.round(interpolate(t, [10, dur * 0.7], [0, 34], clamp));
  return <Fade t={t} dur={dur}><Pop at={4} t={t} style={{position: 'absolute', left: 60, top: 230}}>
    <div style={{...card, padding: '20px 32px', borderColor: GREEN}}>
      <div style={{fontSize: 26, letterSpacing: 4, fontWeight: 800, color: GREEN}}>FIRST GHAT ROAD</div>
      <div style={{fontSize: 120, fontWeight: 900, lineHeight: 1}}>{n}</div>
      <div style={{fontSize: 40, fontWeight: 800}}>hairpin bends</div>
      <div style={{fontSize: 24, opacity: 0.75}}>measured from map data</div>
    </div></Pop></Fade>;
};
const Traffic: React.FC = () => {
  const {t, active, dur} = useShot('traffic'); if (!active) return null;
  return <Fade t={t} dur={dur}><Pop at={6} t={t} style={{position: 'absolute', left: 60, top: 240}}>
    <Tag c={GREEN} k="1944 – 1974" v="One road, up AND down" /></Pop></Fade>;
};
const Second: React.FC = () => {
  const {t, active, dur} = useShot('second_road'); if (!active) return null;
  return <Fade t={t} dur={dur}><div style={{position: 'absolute', left: 60, top: 230, width: 700}}>
    <Pop at={6} t={t}><Tag c={ORANGE} k="1974 · SECOND GHAT ROAD" v="Only 3 hairpins" sub="a more direct line" /></Pop>
    <Pop at={Math.round(dur * 0.6)} t={t}><Tag c={RED} k="KM 11 – 17" v="Cut steeply through rock" /></Pop>
  </div></Fade>;
};
const Rock: React.FC = () => {
  const {t, active, dur} = useShot('rockfall'); if (!active) return null;
  return <Fade t={t} dur={dur}><Pop at={6} t={t} style={{position: 'absolute', left: 60, top: 240}}>
    <Tag c={RED} k="HEAVY RAIN" v="Fractured rock → boulders" sub="road closed for repairs" /></Pop></Fade>;
};
const Finale: React.FC = () => {
  const f = useCurrentFrame(); const i = idx('finale'); const from = Math.round(T.starts[i] * FPS);
  if (f < from) return null; const t = f - from;
  return <AbsoluteFill style={{fontFamily: FONT}}>
    <Pop at={Math.round(T.durs[i] * FPS * 0.5)} t={t} style={{position: 'absolute', width: '100%', top: 260, textAlign: 'center'}}>
      <div style={{fontSize: 84, fontWeight: 900, color: 'white', lineHeight: 1.05, textShadow: '0 6px 30px rgba(0,0,0,0.7)'}}>WORK WITH<br /><span style={{color: GREEN}}>NATURE</span></div>
    </Pop>
    <div style={{position: 'absolute', bottom: 60, width: '100%', textAlign: 'center', color: 'rgba(255,255,255,0.75)', fontSize: 20, padding: '0 50px', lineHeight: 1.4}}>
      Terrain: Copernicus DEM GLO-30 © DLR e.V. 2010-2014 & Airbus 2014-2018, provided under COPERNICUS by the EU and ESA ·
      Imagery: contains modified Copernicus Sentinel data 2026 · Roads: © OpenStreetMap contributors (ODbL)</div>
  </AbsoluteFill>;
};
export const Main: React.FC<{bg: string; audio: string; preview: boolean}> = ({bg, audio, preview}) => (
  <AbsoluteFill style={{background: '#0b1020'}}>
    {preview ? <AbsoluteFill style={{background: 'linear-gradient(#26304a, #0b1020)'}} /> : <OffthreadVideo src={staticFile(bg)} muted />}
    {!preview && <Audio src={staticFile(audio)} />}
    <Dips /><Open /><TwoRoads /><Track /><People /><Lay /><Straight /><Hairpins /><Traffic /><Second /><Rock /><Finale /><Captions />
  </AbsoluteFill>
);
