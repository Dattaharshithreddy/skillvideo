import React from 'react';
import {AbsoluteFill, Audio, OffthreadVideo, interpolate, spring, staticFile, useCurrentFrame, Easing} from 'remotion';
import T from './timing.json';
import LB from './labels.json';
const FONT = '"Noto Sans Telugu", Poppins, "DejaVu Sans", Arial, sans-serif';
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
      return <div style={{position: 'absolute', top: 1230, width: '100%', textAlign: 'center', fontFamily: FONT, fontWeight: 900, fontSize: 72,
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
// ---------- eras: 1944 shots look like old film; a wipe brings colour back ----------
const OLD = ['cart_track', 'people', 'lay_road', 'straight', 'hairpins', 'traffic'];
const span = (s: string) => { const i = idx(s); return [T.starts[i] * FPS, (T.starts[i] + T.durs[i]) * FPS]; };
const oldA = span('cart_track')[0], oldB = span('traffic')[1];
const sepiaClip = (f: number) => {            // % of the frame (from the left) shown in old-film style
  if (f < oldA - 1 || f > oldB + 20) return 0;
  if (f < oldA + 18) return interpolate(f, [oldA, oldA + 18], [0, 100], {...clamp, easing: ease});
  if (f <= oldB) return 100;
  return interpolate(f, [oldB, oldB + 20], [100, 0], {...clamp, easing: ease});
};
const Grain: React.FC = () => {
  const f = useCurrentFrame(); const seed = f % 7;
  return <AbsoluteFill style={{opacity: 0.22, mixBlendMode: 'overlay'}}>
    <svg width={1080} height={1920}><filter id={`g${seed}`}><feTurbulence type="fractalNoise" baseFrequency="0.9" numOctaves={2} seed={seed} /></filter>
      <rect width="100%" height="100%" filter={`url(#g${seed})`} /></svg></AbsoluteFill>;
};
const Era: React.FC<{bg: string; preview: boolean}> = ({bg, preview}) => {
  const f = useCurrentFrame(); const p = sepiaClip(f); if (p <= 0) return null;
  const flick = 0.93 + 0.07 * Math.sin(f * 1.7) * Math.sin(f * 0.37);
  return <AbsoluteFill style={{clipPath: `inset(0 ${100 - p}% 0 0)`}}>
    {preview ? <AbsoluteFill style={{background: 'rgba(120,90,50,0.45)'}} /> :
      <OffthreadVideo src={staticFile(bg)} muted style={{filter: `sepia(0.9) contrast(1.15) brightness(${flick})`}} />}
    <Grain />
    <AbsoluteFill style={{background: 'radial-gradient(ellipse at center, rgba(0,0,0,0) 50%, rgba(30,18,5,0.6) 100%)'}} />
    {p < 100 && <div style={{position: 'absolute', left: `${p}%`, top: 0, bottom: 0, width: 6, background: GOLD, boxShadow: `0 0 30px ${GOLD}`}} />}
  </AbsoluteFill>;
};
const Stamp: React.FC = () => {
  const f = useCurrentFrame();
  const eras: [string, string, string][] = [['cart_track', 'traffic', '1944'], ['second_road', 'rockfall', '1974'], ['open', 'two_roads', 'నేడు'], ['old_runs', 'finale', 'నేడు']];
  for (const [a, b, label] of eras) {
    const s = span(a)[0], e = span(b)[1];
    if (f >= s && f < e) {
      const o = interpolate(f, [s, s + 10, e - 8, e], [0, 1, 1, 0], clamp);
      return <div style={{position: 'absolute', right: 60, top: 150, opacity: o, fontFamily: FONT, fontWeight: 900, fontSize: 64, color: label === '1944' ? '#F3D9A4' : 'white',
        border: `4px solid ${label === '1944' ? '#F3D9A4' : 'white'}`, borderRadius: 14, padding: '4px 22px', transform: 'rotate(-4deg)', textShadow: '0 4px 16px rgba(0,0,0,0.7)'}}>{label}</div>;
    }
  }
  return null;
};
// ---------- seven hills labels (positions projected from the 3D camera) ----------
const Hills: React.FC = () => {
  const {t, active, dur} = useShot('hills'); if (!active) return null;
  const f = useCurrentFrame(); const fr = (LB as any).frames; const key = String(f - ((f - Number(Object.keys(fr)[0])) % 2));
  const row: [string, number, number, number][] = fr[key] || [];
  return <Fade t={t} dur={dur}>
    {row.map(([n, x, y, v], k) => {
      if (!v) return null; const at = Math.round(dur * 0.08 + k * dur * 0.06); const temple = k === row.length - 1;
      const o = interpolate(t, [at, at + 8], [0, 1], clamp);
      return <div key={n} style={{position: 'absolute', left: x * 1080, top: y * 1920, transform: 'translate(-50%, -100%)', opacity: o, fontFamily: FONT, textAlign: 'center'}}>
        <div style={{...card, padding: '6px 18px', fontSize: temple ? 40 : 32, fontWeight: 800, borderColor: temple ? GOLD : 'rgba(255,255,255,0.3)', color: temple ? GOLD : 'white'}}>{n}</div>
        <div style={{width: 3, height: 40, background: temple ? GOLD : 'white', margin: '0 auto', opacity: 0.85}} />
      </div>;
    })}
    <Pop at={6} t={t} style={{position: 'absolute', width: '100%', top: 210, textAlign: 'center', fontFamily: FONT}}>
      <div style={{fontSize: 64, fontWeight: 900, color: 'white', textShadow: '0 6px 30px rgba(0,0,0,0.7)'}}>ఏడుకొండలు</div>
      <div style={{fontSize: 24, color: 'rgba(255,255,255,0.8)'}}>పేర్లు సంప్రదాయం ప్రకారం · స్థానాలు సూచనప్రాయం</div>
    </Pop>
    <Pop at={Math.round(dur * 0.7)} t={t} style={{position: 'absolute', left: 60, right: 60, bottom: 760}}>
      <Tag c={GOLD} k="తిరుమల" v="శ్రీ వేంకటేశ్వర స్వామి ఆలయం" /></Pop>
  </Fade>;
};
const Open: React.FC = () => {
  const {t, active, dur} = useShot('open'); if (!active) return null;
  return <Fade t={t} dur={dur}><Pop at={6} t={t} style={{position: 'absolute', width: '100%', top: 250, textAlign: 'center', fontFamily: FONT}}>
    <div style={{fontSize: 34, letterSpacing: 4, color: GOLD, fontWeight: 800}}>ఎలా కట్టారు?</div>
    <div style={{fontSize: 92, fontWeight: 900, color: 'white', lineHeight: 1.1, textShadow: '0 6px 30px rgba(0,0,0,0.7)'}}>తిరుమల<br />ఘాట్ రోడ్డు</div>
  </Pop></Fade>;
};
const TwoRoads: React.FC = () => {
  const {t, active, dur} = useShot('two_roads'); if (!active) return null;
  return <Fade t={t} dur={dur}><div style={{position: 'absolute', left: 60, top: 260, width: 700}}>
    <Pop at={4} t={t}><Tag c={GREEN} k="1944 · మొదటి ఘాట్ రోడ్డు" v="ప్రతి వర్షాకాలం తట్టుకుంటుంది" /></Pop>
    <Pop at={Math.round(dur * 0.45)} t={t}><Tag c={ORANGE} k="1974 · రెండో ఘాట్ రోడ్డు" v="కొండచరియలు, మూసివేతలు" /></Pop>
  </div></Fade>;
};
const Track: React.FC = () => {
  const {t, active, dur} = useShot('cart_track'); if (!active) return null;
  return <Fade t={t} dur={dur}><Pop at={20} t={t} style={{position: 'absolute', left: 60, top: 260}}>
    <Tag c={GOLD} k="1944 కి ముందు" v="కాలిబాట, ఎడ్ల బండ్ల దారి" /></Pop></Fade>;
};
const People: React.FC = () => {
  const {t, active, dur} = useShot('people'); if (!active) return null;
  const P = [['ప్లాన్ ఘనత', 'సర్ ఎం. విశ్వేశ్వరయ్య', 'భారతరత్న ఇంజనీర్'], ['పనికి నాయకత్వం', 'ఎ. నాగేశ్వర అయ్యర్', 'ద హిందూ, 1944'],
    ['నిర్మాణం', 'గ్యానన్ డంకర్లీ & కో.', 'కాంట్రాక్టర్లు']];
  return <Fade t={t} dur={dur}><div style={{position: 'absolute', left: 60, right: 60, top: 240}}>
    {P.map(([k, v, s], n) => <Pop key={k} at={Math.round(dur * (0.02 + 0.3 * n))} t={t}><Tag c={GOLD} k={k} v={v} sub={s} /></Pop>)}
  </div></Fade>;
};
const Lay: React.FC = () => {
  const {t, active, dur} = useShot('lay_road'); if (!active) return null;
  return <Fade t={t} dur={dur}><Pop at={Math.round(dur * 0.4)} t={t} style={{position: 'absolute', left: 60, top: 260}}>
    <Tag c={GREEN} k="సూత్రం" v="పాత దారినే అనుసరించు" sub="పైవరకూ నెమ్మదైన వాలు" /></Pop></Fade>;
};
const Straight: React.FC = () => {
  const {t, active, dur} = useShot('straight'); if (!active) return null;
  return <Fade t={t} dur={dur}><div style={{position: 'absolute', left: 60, top: 250, width: 720}}>
    <Pop at={6} t={t}><Tag c={RED} k="నేరుగా పైకి" v="కొన్ని చోట్ల 60% పైగా వాలు" /></Pop>
    <Pop at={Math.round(dur * 0.5)} t={t}><Tag c={GREEN} k="పాత రోడ్డు" v="సగటు వాలు 3.4%" sub="635 మీ. ఎత్తు · సుమారు 18.5 కి.మీ." /></Pop>
  </div></Fade>;
};
const Hairpins: React.FC = () => {
  const {t, active, dur} = useShot('hairpins'); if (!active) return null;
  const n = Math.round(interpolate(t, [10, dur * 0.7], [0, 34], clamp));
  return <Fade t={t} dur={dur}><Pop at={4} t={t} style={{position: 'absolute', left: 60, top: 250}}>
    <div style={{...card, padding: '20px 32px', borderColor: GREEN}}>
      <div style={{fontSize: 26, fontWeight: 800, color: GREEN}}>మొదటి ఘాట్ రోడ్డు</div>
      <div style={{fontSize: 120, fontWeight: 900, lineHeight: 1}}>{n}</div>
      <div style={{fontSize: 40, fontWeight: 800}}>హెయిర్‌పిన్ మలుపులు</div>
      <div style={{fontSize: 22, opacity: 0.75}}>మ్యాప్ డేటా నుంచి లెక్కించినవి</div>
    </div></Pop></Fade>;
};
const Traffic: React.FC = () => {
  const {t, active, dur} = useShot('traffic'); if (!active) return null;
  return <Fade t={t} dur={dur}><Pop at={6} t={t} style={{position: 'absolute', left: 60, top: 260}}>
    <Tag c={GREEN} k="1944 – 1974" v="ఒకే రోడ్డు: ఎక్కడం, దిగడం" /></Pop></Fade>;
};
const Second: React.FC = () => {
  const {t, active, dur} = useShot('second_road'); if (!active) return null;
  return <Fade t={t} dur={dur}><div style={{position: 'absolute', left: 60, top: 250, width: 720}}>
    <Pop at={20} t={t}><Tag c={ORANGE} k="1974 · రెండో ఘాట్ రోడ్డు" v="3 హెయిర్‌పిన్లు మాత్రమే" sub="మరింత నేరుగా ఉండే దారి" /></Pop>
    <Pop at={Math.round(dur * 0.6)} t={t}><Tag c={RED} k="11 – 17 కి.మీ." v="రాతిని నిటారుగా తొలిచారు" /></Pop>
  </div></Fade>;
};
const Rock: React.FC = () => {
  const {t, active, dur} = useShot('rockfall'); if (!active) return null;
  return <Fade t={t} dur={dur}><Pop at={6} t={t} style={{position: 'absolute', left: 60, top: 260}}>
    <Tag c={RED} k="భారీ వర్షం" v="పగిలిన రాయి → బండరాళ్ళు" sub="మరమ్మత్తుల కోసం రోడ్డు మూసివేత" /></Pop></Fade>;
};
const Finale: React.FC = () => {
  const f = useCurrentFrame(); const i = idx('finale'); const from = Math.round(T.starts[i] * FPS);
  if (f < from) return null; const t = f - from;
  return <AbsoluteFill style={{fontFamily: FONT}}>
    <Pop at={Math.round(T.durs[i] * FPS * 0.5)} t={t} style={{position: 'absolute', width: '100%', top: 270, textAlign: 'center'}}>
      <div style={{fontSize: 80, fontWeight: 900, color: 'white', lineHeight: 1.15, textShadow: '0 6px 30px rgba(0,0,0,0.7)'}}>ప్రకృతితో<br /><span style={{color: GREEN}}>కలిసి</span></div>
    </Pop>
  </AbsoluteFill>;
};
const Credits: React.FC = () => (
  <div style={{position: 'absolute', bottom: 40, width: '100%', textAlign: 'center', color: 'rgba(255,255,255,0.8)', fontSize: 18, padding: '0 40px', lineHeight: 1.35,
    fontFamily: 'Poppins, "DejaVu Sans", Arial, sans-serif', textShadow: '0 2px 6px rgba(0,0,0,0.9)'}}>
    Imagery: Google, ©2026 Airbus, Maxar Technologies · Terrain: Copernicus DEM GLO-30 © DLR e.V. & Airbus, under COPERNICUS by the EU and ESA ·
    Roads: © OpenStreetMap contributors (ODbL)</div>
);
export const Main: React.FC<{bg: string; audio: string; preview: boolean}> = ({bg, audio, preview}) => (
  <AbsoluteFill style={{background: preview ? 'transparent' : '#0b1020'}}>
    {!preview && <OffthreadVideo src={staticFile(bg)} muted />}
    <Era bg={bg} preview={preview} />
    {!preview && <Audio src={staticFile(audio)} />}
    <Dips /><Hills /><Open /><TwoRoads /><Track /><People /><Lay /><Straight /><Hairpins /><Traffic /><Second /><Rock /><Finale /><Stamp /><Captions /><Credits />
  </AbsoluteFill>
);
