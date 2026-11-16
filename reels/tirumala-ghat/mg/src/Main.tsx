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
// ---------- divine shots: light rays from the temple, gold dust, glow, hill names ----------
const SERIF = '"Noto Serif Telugu", "Noto Sans Telugu", serif';
const goldText: React.CSSProperties = {background: 'linear-gradient(180deg, #FFF6C8 0%, #FFD35A 42%, #F09A1A 78%, #FFE08A 100%)', WebkitBackgroundClip: 'text',
  backgroundClip: 'text', color: 'transparent', filter: 'drop-shadow(0 4px 0 rgba(90,40,0,0.85)) drop-shadow(0 0 26px rgba(255,170,40,0.75))'};
const DIV = ['hills', 'seven', 'govinda'];
const divSpan = (s: string): [number, number] => { const [a, b] = span(s); return [a, s === 'govinda' ? T.end : b]; };
const labRow = (shot: string, f: number): [string, number, number, number][] => {
  const fr = (LB as any).shots?.[shot]; if (!fr) return [];
  const ks = Object.keys(fr); const first = Number(ks[0]), last = Number(ks[ks.length - 1]);
  const k = Math.min(last, Math.max(first, f - ((f - first) % 2))); return fr[String(k)] || [];
};
const rnd = (n: number) => { const x = Math.sin(n * 127.1 + 311.7) * 43758.5453; return x - Math.floor(x); };
const Dust: React.FC<{o: number}> = ({o}) => {
  const f = useCurrentFrame();
  return <AbsoluteFill style={{mixBlendMode: 'screen', opacity: o}}>
    {Array.from({length: 54}).map((_, i) => {
      const sz = 6 + rnd(i) * 20, sp = 1.2 + rnd(i + 50) * 2.6;
      const y = 2000 - ((rnd(i + 9) * 2100 + f * sp) % 2100), x = rnd(i + 3) * 1080 + Math.sin(f / 40 + i) * 26;
      const tw = 0.35 + 0.65 * Math.abs(Math.sin(f / (9 + rnd(i + 7) * 14) + i));
      return <div key={i} style={{position: 'absolute', left: x, top: y, width: sz, height: sz, borderRadius: sz, opacity: tw,
        background: 'radial-gradient(circle, rgba(255,240,190,1) 0%, rgba(255,190,70,0.75) 45%, rgba(255,150,30,0) 72%)', filter: sz > 18 ? 'blur(2px)' : undefined}} />;
    })}
  </AbsoluteFill>;
};
const Rays: React.FC<{x: number; y: number; o: number; size?: number}> = ({x, y, o, size = 1}) => {
  const f = useCurrentFrame(); const R = 1700 * size;
  const mask = 'radial-gradient(circle, rgba(0,0,0,1) 0%, rgba(0,0,0,0.55) 22%, rgba(0,0,0,0) 62%)';
  const ray = (rot: number, period: number, a: number): React.CSSProperties => ({position: 'absolute', left: x - R, top: y - R, width: 2 * R, height: 2 * R, transform: `rotate(${rot}deg)`,
    background: `repeating-conic-gradient(from 0deg, rgba(255,214,120,0) 0deg, rgba(255,220,130,${a}) ${period * 0.16}deg, rgba(255,214,120,0) ${period * 0.42}deg, rgba(255,214,120,0) ${period}deg)`,
    WebkitMaskImage: mask, maskImage: mask, filter: 'blur(5px)'});
  const pulse = 0.85 + 0.15 * Math.sin(f / 11);
  return <AbsoluteFill style={{mixBlendMode: 'screen', opacity: o}}>
    <div style={ray(f * 0.22, 18, 0.5)} /><div style={ray(-f * 0.15 + 7, 29, 0.42)} />
    <div style={{position: 'absolute', left: x - 520 * size, top: y - 520 * size, width: 1040 * size, height: 1040 * size, opacity: pulse,
      background: 'radial-gradient(circle, rgba(255,244,200,0.95) 0%, rgba(255,196,84,0.5) 13%, rgba(255,150,40,0.16) 34%, rgba(255,150,40,0) 60%)'}} />
  </AbsoluteFill>;
};
const Divine: React.FC<{bg: string; preview: boolean}> = ({bg, preview}) => {
  const f = useCurrentFrame();
  for (const s of DIV) {
    const [a, b] = divSpan(s); if (f < a || f >= b) continue;
    const t = f - a, dur = b - a; const row = labRow(s, f); const tp = row[row.length - 1];
    const env = interpolate(t, [0, 10, dur - 8, dur], [0, 1, 1, s === 'govinda' ? 1 : 0], clamp);
    const near = s === 'govinda' ? 1 : s === 'hills' ? interpolate(t, [dur * 0.35, dur * 0.9], [0.35, 1], clamp) : interpolate(t, [dur * 0.72, dur * 0.95], [0, 1], clamp);
    return <AbsoluteFill>
      {!preview && <AbsoluteFill style={{mixBlendMode: 'screen', opacity: 0.42 * env}}>
        <OffthreadVideo src={staticFile(bg)} muted style={{filter: 'brightness(0.72) contrast(2.6) saturate(1.5) blur(22px)'}} /></AbsoluteFill>}
      <AbsoluteFill style={{background: 'linear-gradient(180deg, rgba(255,150,40,0.42) 0%, rgba(255,170,60,0.12) 26%, rgba(0,0,0,0) 45%, rgba(40,10,0,0.0) 70%, rgba(50,14,0,0.5) 100%)', opacity: env}} />
      {tp && tp[3] === 1 && <Rays x={tp[1] * 1080} y={tp[2] * 1920} o={env * near} size={s === 'govinda' ? 1.15 : 0.55 + 0.45 * near} />}
      <Dust o={env * 0.9} />
      <AbsoluteFill style={{background: 'radial-gradient(ellipse at 50% 45%, rgba(0,0,0,0) 52%, rgba(46,14,0,0.55) 100%)', opacity: env}} />
    </AbsoluteFill>;
  }
  return null;
};
const Om: React.FC<{size?: number}> = ({size = 40}) => (
  <div style={{fontFamily: SERIF, fontSize: size, fontWeight: 800, letterSpacing: 2, ...goldText}}>ఓం నమో వేంకటేశాయ</div>
);
const Hills: React.FC = () => {
  const {t, active, dur} = useShot('hills'); if (!active) return null;
  return <Fade t={t} dur={dur}>
    <Pop at={4} t={t} style={{position: 'absolute', width: '100%', top: 190, textAlign: 'center'}}>
      <Om size={44} />
      <div style={{fontFamily: SERIF, fontSize: 190, fontWeight: 900, lineHeight: 1.25, ...goldText}}>తిరుమల</div>
      <div style={{fontFamily: FONT, fontSize: 36, fontWeight: 800, color: 'white', letterSpacing: 3, textShadow: '0 3px 14px rgba(60,20,0,0.9)'}}>ఏడుకొండల వాడి కొండ</div>
    </Pop>
  </Fade>;
};
const Seven: React.FC = () => {
  const f = useCurrentFrame(); const {t, active, dur} = useShot('seven'); if (!active) return null;
  const row = labRow('seven', f); const NT: number[] = (T as any).name_t || [];
  let cur = -1; NT.forEach((x, i) => { if (t / dur >= x) cur = i; });
  const on = (k: number) => k <= cur;
  const HNAMES = ['శేషాద్రి', 'నీలాద్రి', 'గరుడాద్రి', 'అంజనాద్రి', 'వృషభాద్రి', 'నారాయణాద్రి', 'వేంకటాద్రి'];
  const src = cur === 6 ? row[row.length - 1] : (row.length === 7 ? row[cur] : null);
  const L: [string, number, number, number] | null = cur >= 0 ? [HNAMES[cur], src ? src[1] : 0.5, src ? src[2] : 0.4, src ? src[3] : 0] : null; const at = cur >= 0 ? Math.round(NT[cur] * dur) : 0;
  const s = spring({frame: t - at, fps: FPS, config: {damping: 13, stiffness: 160}});
  const vis = L ? L[3] === 1 : false;
  const px = L && vis ? Math.min(880, Math.max(200, L[1] * 1080)) : 540, py = L && vis ? Math.min(1120, Math.max(560, L[2] * 1920)) : 760;
  return <Fade t={t} dur={dur}>
    <Pop at={4} t={t} style={{position: 'absolute', width: '100%', top: 150, textAlign: 'center'}}>
      <div style={{fontFamily: SERIF, fontSize: 104, fontWeight: 900, lineHeight: 1.3, ...goldText}}>ఏడుకొండలు</div>
      <div style={{fontFamily: FONT, fontSize: 24, color: 'rgba(255,240,210,0.92)', textShadow: '0 2px 8px rgba(0,0,0,0.9)'}}>సంప్రదాయ పేర్లు · స్థానాలు సూచన కోసం</div>
    </Pop>
    <div style={{position: 'absolute', top: 372, width: '100%', display: 'flex', justifyContent: 'center', gap: 12}}>
      {Array.from({length: 7}).map((_, k) => <div key={k} style={{width: 46, height: 46, borderRadius: 23, fontFamily: FONT, fontWeight: 900, fontSize: 26, lineHeight: '46px', textAlign: 'center',
        color: on(k) ? '#3a1800' : 'rgba(255,255,255,0.7)', background: on(k) ? 'linear-gradient(180deg,#FFE9A0,#F3A52A)' : 'rgba(20,10,0,0.55)',
        border: '2px solid rgba(255,214,120,0.8)', boxShadow: k === cur ? '0 0 22px #FFC23D' : undefined}}>{k + 1}</div>)}
    </div>
    {L && <div style={{position: 'absolute', left: px, top: py, transform: `translate(-50%, -100%) scale(${s})`, transformOrigin: '50% 100%', textAlign: 'center'}}>
      <div style={{display: 'inline-block', padding: '10px 30px 6px', borderRadius: 20, background: 'rgba(40,14,0,0.8)', border: '3px solid #FFC23D', boxShadow: '0 0 34px rgba(255,180,50,0.7)',
        fontFamily: SERIF, fontWeight: 900, fontSize: 76, whiteSpace: 'nowrap'}}><span style={{...goldText, filter: undefined}}>{cur + 1}. {L[0]}</span></div>
      {vis && <div style={{width: 4, height: 70, background: 'linear-gradient(180deg,#FFC23D,rgba(255,194,61,0.1))', margin: '0 auto'}} />}
      {vis && <div style={{width: 18, height: 18, borderRadius: 9, background: '#FFE9A0', boxShadow: '0 0 20px #FFC23D', margin: '-6px auto 0'}} />}
    </div>}
  </Fade>;
};
const Govinda: React.FC = () => {
  const f = useCurrentFrame(); const [a] = divSpan('govinda'); if (f < a) return null; const t = f - a;
  const tail = Math.round(span('govinda')[1] - a);
  return <AbsoluteFill>
    <Pop at={4} t={t} style={{position: 'absolute', width: '100%', top: 200, textAlign: 'center'}}><Om size={62} /></Pop>
    <Pop at={tail - 6} t={t} style={{position: 'absolute', width: '100%', top: 1210, textAlign: 'center'}}>
      <div style={{fontFamily: SERIF, fontSize: 118, fontWeight: 900, lineHeight: 1.3, ...goldText}}>గోవిందా… గోవిందా!</div>
    </Pop>
  </AbsoluteFill>;
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
  if (f < from || f >= span('finale')[1]) return null; const t = f - from;
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
    <Divine bg={bg} preview={preview} />
    {!preview && <Audio src={staticFile(audio)} />}
    <Dips /><Hills /><Seven /><Govinda /><Open /><TwoRoads /><Track /><People /><Lay /><Straight /><Hairpins /><Traffic /><Second /><Rock /><Finale /><Stamp /><Captions /><Credits />
  </AbsoluteFill>
);
