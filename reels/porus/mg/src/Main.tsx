import React from 'react';
import {AbsoluteFill, Audio, OffthreadVideo, interpolate, spring, staticFile, useCurrentFrame, Easing} from 'remotion';
import T from './timing.json';
const FONT = 'Poppins, "DejaVu Sans", Arial, sans-serif';
const FPS = 30, GREEN = '#4DFF8A', ORANGE = '#FFA41F', RED = '#FF3B30', GOLD = '#FFC23D', BLOOD = '#D93A2B';
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
// ---------- weather & mood ----------
const rnd = (n: number) => { const x = Math.sin(n * 127.1) * 43758.5453; return x - Math.floor(x); };
const Rain: React.FC = () => {
  const f = useCurrentFrame(); const i = idx('storm'), j = idx('feint');
  const a = T.starts[i] * FPS, b = (T.starts[i] + T.durs[i]) * FPS, a2 = (T.starts[j] + T.durs[j] * 0.85) * FPS;
  if (f < a2 || f > b + 10) return null;
  const k = interpolate(f, [a2, a, b - 10, b + 10], [0.2, 1, 1, 0], clamp);
  const drops = Array.from({length: 150}, (_, n) => {
    const x = rnd(n) * 1300 - 110, sp = 70 + rnd(n + 9) * 40, y = ((f * sp + rnd(n + 3) * 2200) % 2200) - 200;
    return <line key={n} x1={x} y1={y} x2={x - 14} y2={y + 60} stroke="rgba(200,215,255,0.45)" strokeWidth={2} />;
  });
  // lightning: same frames as the sun spikes in build.py (see build.py lit)
  const L = [0.12, 0.38, 0.41, 0.7, 0.88].map((q) => T.starts[i] * FPS + T.durs[i] * FPS * q);
  const flash = Math.max(...L.map((l) => interpolate(f - l, [-1, 0, 2, 3, 7], [0, 0.85, 0.2, 0.6, 0], clamp)));
  return <AbsoluteFill style={{opacity: k}}>
    <svg width={1080} height={1920}>{drops}</svg>
    <AbsoluteFill style={{background: '#dfe8ff', opacity: flash}} />
  </AbsoluteFill>;
};
const Dust: React.FC = () => {
  const f = useCurrentFrame(); const i = idx('battle'); const a = T.starts[i] * FPS, b = a + T.durs[i] * FPS;
  if (f < a || f > b) return null;
  const k = interpolate(f, [a, a + 40, b - 15, b], [0, 1, 1, 0], clamp);
  return <AbsoluteFill style={{opacity: k * 0.55, background: 'linear-gradient(to top, rgba(170,130,80,0.75), rgba(170,130,80,0) 55%)'}} />;
};
const Vignette: React.FC = () => <AbsoluteFill style={{background: 'radial-gradient(ellipse at center, rgba(0,0,0,0) 55%, rgba(0,0,0,0.55) 100%)'}} />;
// ---------- shot overlays ----------
const Open: React.FC = () => {
  const {t, active, dur} = useShot('open'); if (!active) return null;
  return <Fade t={t} dur={dur}>
    <Pop at={6} t={t} style={{position: 'absolute', width: '100%', top: 220, textAlign: 'center', fontFamily: FONT}}>
      <div style={{fontSize: 34, letterSpacing: 10, color: GOLD, fontWeight: 800}}>326 BC · BATTLE OF THE HYDASPES</div>
      <div style={{fontSize: 108, fontWeight: 900, color: 'white', lineHeight: 1, textShadow: '0 6px 30px rgba(0,0,0,0.8)'}}>ALEXANDER<br /><span style={{fontSize: 60, color: GOLD}}>vs</span><br />PORUS</div>
    </Pop>
  </Fade>;
};
const Ambhi: React.FC = () => {
  const {t, active, dur} = useShot('ambhi'); if (!active) return null;
  return <Fade t={t} dur={dur}><Pop at={Math.round(dur * 0.25)} t={t} style={{position: 'absolute', left: 60, top: 230}}>
    <Tag c={BLOOD} k="BETRAYAL 1" v="Ambhi, king of Taxila" sub="opened his gates to Alexander" /></Pop></Fade>;
};
const River: React.FC = () => {
  const {t, active, dur} = useShot('river'); if (!active) return null;
  return <Fade t={t} dur={dur}><div style={{position: 'absolute', left: 60, top: 230, width: 720}}>
    <Pop at={6} t={t}><Tag c={GOLD} k="THE RIVER" v="Jhelum" sub="the Greeks called it Hydaspes" /></Pop>
    <Pop at={Math.round(dur * 0.42)} t={t}><Tag c={ORANGE} k="PORUS'S ARMY" v="200 war elephants" sub="Arrian's count" /></Pop>
  </div></Fade>;
};
const Feint: React.FC = () => {
  const {t, active, dur} = useShot('feint'); if (!active) return null;
  return <Fade t={t} dur={dur}><Pop at={6} t={t} style={{position: 'absolute', left: 60, top: 240}}>
    <Tag c={GOLD} k="NIGHT AFTER NIGHT" v="Fake attacks" sub="until Porus's army stopped reacting" /></Pop></Fade>;
};
const Storm: React.FC = () => {
  const {t, active, dur} = useShot('storm'); if (!active) return null;
  return <Fade t={t} dur={dur}><Pop at={Math.round(dur * 0.55)} t={t} style={{position: 'absolute', left: 60, top: 240}}>
    <Tag c={GOLD} k="BETRAYAL 2 · DECEPTION" v="Crossed upstream in a storm" /></Pop></Fade>;
};
const Battle: React.FC = () => {
  const {t, active, dur} = useShot('battle'); if (!active) return null;
  return <Fade t={t} dur={dur}><Pop at={Math.round(dur * 0.55)} t={t} style={{position: 'absolute', left: 60, top: 240}}>
    <Tag c={ORANGE} k="ELEPHANTS vs PIKES" v="Sarissa: about 5–6 m long" /></Pop></Fade>;
};
const King: React.FC = () => {
  const {t, active, dur} = useShot('king'); if (!active) return null;
  return <Fade t={t} dur={dur}><Pop at={Math.round(dur * 0.66)} t={t} style={{position: 'absolute', left: 70, right: 70, top: 260, textAlign: 'center', fontFamily: FONT}}>
    <div style={{...card, padding: '34px 36px', borderColor: GOLD}}>
      <div style={{fontSize: 30, letterSpacing: 6, color: GOLD, fontWeight: 800}}>PORUS</div>
      <div style={{fontSize: 72, fontWeight: 900, lineHeight: 1.1}}>“As a king<br />treats a king.”</div>
      <div style={{fontSize: 24, opacity: 0.75, marginTop: 10}}>as recorded by Plutarch & Arrian</div>
    </div></Pop></Fade>;
};
const Return: React.FC = () => {
  const {t, active, dur} = useShot('return'); if (!active) return null;
  return <Fade t={t} dur={dur}><div style={{position: 'absolute', left: 60, top: 230, width: 720}}>
    <Pop at={6} t={t}><Tag c={GREEN} k="ALEXANDER" v="Gave his kingdom back" sub="and made it larger" /></Pop>
    <Pop at={Math.round(dur * 0.55)} t={t}><Tag c={ORANGE} k="AT THE BEAS RIVER" v="His army refused to go on" /></Pop>
  </div></Fade>;
};
const Murder: React.FC = () => {
  const {t, active, dur} = useShot('murder'); if (!active) return null;
  return <Fade t={t} dur={dur}><Pop at={Math.round(dur * 0.45)} t={t} style={{position: 'absolute', left: 60, top: 240}}>
    <Tag c={BLOOD} k="BETRAYAL 3" v="Eudemus" sub="had Porus killed, after 323 BC" /></Pop></Fade>;
};
const Finale: React.FC = () => {
  const f = useCurrentFrame(); const i = idx('legacy'); const from = Math.round(T.starts[i] * FPS);
  if (f < from) return null; const t = f - from;
  return <AbsoluteFill style={{fontFamily: FONT}}>
    <Pop at={Math.round(T.durs[i] * FPS * 0.62)} t={t} style={{position: 'absolute', width: '100%', top: 250, textAlign: 'center'}}>
      <div style={{fontSize: 34, letterSpacing: 10, color: GOLD, fontWeight: 800}}>PURUSHOTTAM</div>
      <div style={{fontSize: 130, fontWeight: 900, color: 'white', lineHeight: 1, textShadow: '0 6px 30px rgba(0,0,0,0.8)'}}>A KING</div>
    </Pop>
    <div style={{position: 'absolute', bottom: 50, width: '100%', textAlign: 'center', color: 'rgba(255,255,255,0.72)', fontSize: 19, padding: '0 50px', lineHeight: 1.4}}>
      Sources: Arrian, Anabasis 5; Plutarch, Life of Alexander 60; Diodorus 19.14 · 3D figures: Quaternius (CC0), elephant by syncopika (OpenGameArt, CC0) ·
      Terrain: Copernicus DEM GLO-30 © DLR e.V. & Airbus, under COPERNICUS by the EU and ESA · Imagery: modified Copernicus Sentinel data 2026 · River: © OpenStreetMap contributors (ODbL)</div>
  </AbsoluteFill>;
};
export const Main: React.FC<{bg: string; audio: string; preview: boolean}> = ({bg, audio, preview}) => (
  <AbsoluteFill style={{background: '#0b1020'}}>
    {preview ? <AbsoluteFill style={{background: 'linear-gradient(#26304a, #0b1020)'}} /> : <OffthreadVideo src={staticFile(bg)} muted />}
    {!preview && <Audio src={staticFile(audio)} />}
    <Rain /><Dust /><Vignette /><Dips /><Open /><Ambhi /><River /><Feint /><Storm /><Battle /><King /><Return /><Murder /><Finale /><Captions />
  </AbsoluteFill>
);
