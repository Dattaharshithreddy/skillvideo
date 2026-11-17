import React from 'react';
import {AbsoluteFill, Audio, Img, OffthreadVideo, interpolate, spring, staticFile, useCurrentFrame, Easing} from 'remotion';
import T from './timing.json';
import LB from './labels.json';
const FONT = '"Noto Sans Telugu", Poppins, "DejaVu Sans", Arial, sans-serif';
const SERIF = '"Noto Serif Telugu", "Noto Sans Telugu", serif';
const FPS = 30, GOLD = '#FFC23D', CREAM = '#F6E7C6';
const clamp = {extrapolateLeft: 'clamp' as const, extrapolateRight: 'clamp' as const};
const ease = Easing.bezier(0.16, 1, 0.3, 1);
const goldText: React.CSSProperties = {background: 'linear-gradient(180deg, #FFF6C8 0%, #FFD35A 42%, #F09A1A 78%, #FFE08A 100%)', WebkitBackgroundClip: 'text',
  backgroundClip: 'text', color: 'transparent', filter: 'drop-shadow(0 4px 0 rgba(90,40,0,0.85)) drop-shadow(0 0 26px rgba(255,170,40,0.75))'};
const idx = (shot: string) => T.lines.findIndex((l) => l.shot === shot);
const span = (shot: string): [number, number] => { const i = idx(shot); return [T.starts[i] * FPS, (T.starts[i] + T.durs[i]) * FPS]; };
const useShot = (shot: string) => {
  const f = useCurrentFrame(); const i = idx(shot);
  const from = Math.round(T.starts[i] * FPS), dur = Math.round(T.durs[i] * FPS);
  return {f, t: f - from, dur, active: f >= from && f < from + dur};
};
const Pop: React.FC<{at: number; t: number; children: React.ReactNode; style?: React.CSSProperties}> = ({at, t, children, style}) => {
  const s = spring({frame: t - at, fps: FPS, config: {damping: 14, stiffness: 140}});
  return <div style={{...style, opacity: interpolate(t - at, [0, 6], [0, 1], clamp), transform: `${style?.transform || ''} translateY(${(1 - s) * 50}px) scale(${0.85 + 0.15 * s})`}}>{children}</div>;
};
const Fade: React.FC<{t: number; dur: number; children: React.ReactNode}> = ({t, dur, children}) => (
  <AbsoluteFill style={{opacity: interpolate(t, [0, 8, dur - 8, dur], [0, 1, 1, 0], clamp)}}>{children}</AbsoluteFill>
);
const Big: React.FC<{size: number; children: React.ReactNode}> = ({size, children}) => (
  <div style={{fontFamily: SERIF, fontSize: size, fontWeight: 900, lineHeight: 1.25, ...goldText}}>{children}</div>
);
const Sub: React.FC<{children: React.ReactNode; size?: number}> = ({children, size = 40}) => (
  <div style={{fontFamily: FONT, fontSize: size, fontWeight: 800, color: 'white', textShadow: '0 3px 14px rgba(40,15,0,0.95), 0 0 4px rgba(0,0,0,0.8)'}}>{children}</div>
);
// ---------- pins from the 3D scene ----------
const labRow = (shot: string, f: number): [string, number, number, number][] => {
  const fr = (LB as any).shots?.[shot]; if (!fr) return [];
  const ks = Object.keys(fr).map(Number).sort((a, b) => a - b); if (!ks.length) return [];
  let k = ks[0]; for (const x of ks) if (x <= f) k = x; return fr[String(k)] || [];
};
const pos = (shot: string, key: string, f: number) => { const r = labRow(shot, f).find((x) => x[0] === key); return r && r[3] ? {x: r[1] * 1080, y: r[2] * 1920} : null; };
const Icon: React.FC<{k: string; s?: number}> = ({k, s = 64}) => {
  const g = <defs><linearGradient id={'g' + k} x1="0" y1="0" x2="0" y2="1"><stop offset="0" stopColor="#FFF3B0" /><stop offset="0.5" stopColor="#FFC23D" /><stop offset="1" stopColor="#C77A10" /></linearGradient></defs>;
  const f = `url(#g${k})`;
  if (k === 'sword') return <svg width={s} height={s} viewBox="0 0 64 64">{g}<path d="M30 4 L34 4 L35 40 L29 40 Z" fill={f} /><rect x="20" y="40" width="24" height="5" rx="2" fill={f} /><rect x="29.5" y="45" width="5" height="12" fill="#8a4a10" /><circle cx="32" cy="59" r="3.5" fill={f} /></svg>;
  if (k === 'conch') return <svg width={s} height={s} viewBox="0 0 64 64">{g}<path d="M14 40 C10 22 30 6 46 14 C58 20 54 40 40 46 L22 56 C18 52 16 46 14 40 Z" fill={f} /><path d="M24 30 C28 22 38 20 44 26" stroke="#9a5a12" strokeWidth="3" fill="none" /><path d="M22 38 C28 32 40 32 46 36" stroke="#9a5a12" strokeWidth="3" fill="none" /></svg>;
  if (k === 'gem') return <svg width={s} height={s} viewBox="0 0 64 64">{g}<circle cx="32" cy="34" r="22" fill={f} /><path d="M32 18 L44 30 L32 50 L20 30 Z" fill="#E0233A" /><path d="M32 18 L38 30 L32 50 Z" fill="#FF5A6E" /></svg>;
  if (k === 'lotus') return <svg width={s} height={s} viewBox="0 0 64 64">{g}{[-50, -25, 0, 25, 50].map((a) => <path key={a} d="M32 52 C22 40 24 22 32 12 C40 22 42 40 32 52 Z" fill={a ? '#FF8FB0' : f} transform={`rotate(${a} 32 52)`} />)}</svg>;
  if (k === 'hill') return <svg width={s} height={s} viewBox="0 0 64 64">{g}<path d="M4 52 L22 22 L32 36 L42 18 L60 52 Z" fill={f} /></svg>;
  return <svg width={s} height={s} viewBox="0 0 64 64">{g}<path d="M10 52 L32 10 L54 52 Z" fill={f} /></svg>;
};
const PinCard: React.FC<{x: number; y: number; name: string; sub?: string; icon?: string; s: number; small?: boolean}> = ({x, y, name, sub, icon, s, small}) => {
  const px = Math.min(880, Math.max(200, x)), py = Math.min(1150, Math.max(460, y));
  return <div style={{position: 'absolute', left: px, top: py, transform: `translate(-50%, -100%) scale(${s * (small ? 0.72 : 1)})`, transformOrigin: '50% 100%', textAlign: 'center'}}>
    <div style={{display: 'inline-flex', alignItems: 'center', gap: 14, padding: '10px 26px 8px', borderRadius: 22, background: 'rgba(40,14,0,0.82)', border: '3px solid #FFC23D',
      boxShadow: '0 0 34px rgba(255,180,50,0.65)'}}>
      {icon && <Icon k={icon} s={small ? 50 : 70} />}
      <div style={{textAlign: 'left'}}>
        <div style={{fontFamily: SERIF, fontWeight: 900, fontSize: small ? 44 : 60, lineHeight: 1.2}}><span style={{...goldText, filter: undefined}}>{name}</span></div>
        {sub && <div style={{fontFamily: FONT, fontWeight: 800, fontSize: small ? 24 : 30, color: CREAM}}>{sub}</div>}
      </div>
    </div>
    <div style={{width: 4, height: 80, background: 'linear-gradient(180deg,#FFC23D,rgba(255,194,61,0.1))', margin: '0 auto'}} />
    <div style={{width: 18, height: 18, borderRadius: 9, background: '#FFE9A0', boxShadow: '0 0 20px #FFC23D', margin: '-6px auto 0'}} />
  </div>;
};
const Pin: React.FC<{shot: string; k: string; name: string; sub?: string; icon?: string; at?: number; small?: boolean}> = ({shot, k, name, sub, icon, at = 0.15, small}) => {
  const {f, t, active, dur} = useShot(shot); if (!active) return null;
  const a = Math.round(dur * at); if (t < a) return null; const p = pos(shot, k, f); if (!p) return null;
  const s = spring({frame: t - a, fps: FPS, config: {damping: 13, stiffness: 160}}) * interpolate(t, [dur - 8, dur], [1, 0], clamp);
  return <PinCard x={p.x} y={p.y} name={name} sub={sub} icon={icon} s={s} small={small} />;
};
// ---------- divine light ----------
const rnd = (n: number) => { const x = Math.sin(n * 127.1 + 311.7) * 43758.5453; return x - Math.floor(x); };
const GoldDust: React.FC<{o: number}> = ({o}) => {
  const f = useCurrentFrame();
  return <AbsoluteFill style={{mixBlendMode: 'screen', opacity: o}}>
    {Array.from({length: 50}).map((_, i) => {
      const sz = 6 + rnd(i) * 18, sp = 1.0 + rnd(i + 50) * 2.4;
      const y = 2000 - ((rnd(i + 9) * 2100 + f * sp) % 2100), x = rnd(i + 3) * 1080 + Math.sin(f / 40 + i) * 26;
      const tw = 0.35 + 0.65 * Math.abs(Math.sin(f / (9 + rnd(i + 7) * 14) + i));
      return <div key={i} style={{position: 'absolute', left: x, top: y, width: sz, height: sz, borderRadius: sz, opacity: tw,
        background: 'radial-gradient(circle, rgba(255,240,190,1) 0%, rgba(255,190,70,0.75) 45%, rgba(255,150,30,0) 72%)'}} />;
    })}
  </AbsoluteFill>;
};
const Rays: React.FC<{x: number; y: number; o: number; size?: number}> = ({x, y, o, size = 1}) => {
  const f = useCurrentFrame(); const R = 1700 * size;
  const mask = 'radial-gradient(circle, rgba(0,0,0,1) 0%, rgba(0,0,0,0.55) 22%, rgba(0,0,0,0) 62%)';
  const ray = (rot: number, period: number, a: number): React.CSSProperties => ({position: 'absolute', left: x - R, top: y - R, width: 2 * R, height: 2 * R, transform: `rotate(${rot}deg)`,
    background: `repeating-conic-gradient(from 0deg, rgba(255,214,120,0) 0deg, rgba(255,220,130,${a}) ${period * 0.16}deg, rgba(255,214,120,0) ${period * 0.42}deg, rgba(255,214,120,0) ${period}deg)`,
    WebkitMaskImage: mask, maskImage: mask, filter: 'blur(5px)'});
  return <AbsoluteFill style={{mixBlendMode: 'screen', opacity: o}}>
    <div style={ray(f * 0.22, 18, 0.5)} /><div style={ray(-f * 0.15 + 7, 29, 0.42)} />
    <div style={{position: 'absolute', left: x - 520 * size, top: y - 520 * size, width: 1040 * size, height: 1040 * size, opacity: 0.85 + 0.15 * Math.sin(f / 11),
      background: 'radial-gradient(circle, rgba(255,244,200,0.95) 0%, rgba(255,196,84,0.5) 13%, rgba(255,150,40,0.16) 34%, rgba(255,150,40,0) 60%)'}} />
  </AbsoluteFill>;
};
const DIV = ['hook', 'gods', 'finale'];
const Divine: React.FC = () => {
  const f = useCurrentFrame();
  for (const s of DIV) {
    const [a, b0] = span(s); const b = s === 'finale' ? T.end : b0; if (f < a || f >= b) continue;
    const t = f - a, dur = b - a; const env = interpolate(t, [0, 12, dur - 8, dur], [0, 1, 1, s === 'finale' ? 1 : 0], clamp);
    const p = pos(s, 'temple', f);
    return <AbsoluteFill>
      <AbsoluteFill style={{background: 'linear-gradient(180deg, rgba(255,150,40,0.38) 0%, rgba(255,170,60,0.1) 28%, rgba(0,0,0,0) 48%, rgba(50,14,0,0.45) 100%)', opacity: env}} />
      {p && <Rays x={p.x} y={p.y} o={env * (s === 'hook' ? 0.75 : 1)} size={s === 'finale' ? 1.1 : 0.7} />}
    </AbsoluteFill>;
  }
  return null;
};
// soft gold dust everywhere, warm vignette, tilt-shift bands
const Finish: React.FC = () => <>
  <GoldDust o={0.45} />
  <AbsoluteFill style={{background: 'linear-gradient(180deg, rgba(255,200,120,0.10) 0%, rgba(0,0,0,0) 18%, rgba(0,0,0,0) 82%, rgba(30,10,0,0.25) 100%)'}} />
  <AbsoluteFill style={{background: 'radial-gradient(ellipse at center, rgba(0,0,0,0) 55%, rgba(25,8,0,0.55) 100%)'}} />
</>;
const Dips: React.FC = () => {
  const f = useCurrentFrame(); let o = 0;
  for (let i = 1; i < T.starts.length; i++) o = Math.max(o, interpolate(f - Math.round(T.starts[i] * FPS), [-5, 0, 7], [0, 0.75, 0], clamp));
  return <AbsoluteFill style={{background: '#1a0b02', opacity: o}} />;
};
// ---------- captions ----------
type Ch = {words: string[]; s: number; e: number};

const CH: Ch[][] = T.lines.map((ln, i) => {
  const words = ln.text.split(' '); const w = words.map((x) => Math.max(x.replace(/[?.!,…]/g, '').length, 2));
  const total = w.reduce((a, b) => a + b, 0); const d = T.durs[i] - (i === T.lines.length - 1 ? 3.6 : 0.6);
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
      return <div style={{position: 'absolute', top: 1290, width: '100%', textAlign: 'center', fontFamily: FONT, fontWeight: 900, fontSize: 68,
        lineHeight: 1.3, color: 'white', transform: `scale(${sc})`, padding: '0 70px', textShadow: '0 5px 0 rgba(0,0,0,0.55), 0 0 24px rgba(0,0,0,0.7)',
        WebkitTextStroke: '3px rgba(0,0,0,0.8)', paintOrder: 'stroke fill'}}>
        {c.words.map((wd, n) => <span key={n} style={{color: k.includes(norm(wd)) ? GOLD : 'white'}}>{wd}{n < c.words.length - 1 ? ' ' : ''}</span>)}
      </div>;
    }
  }
  return null;
};
// ---------- story cards ----------
const Count: React.FC<{shot: string; to: number; at: number; label: string; top?: number; size?: number}> = ({shot, to, at, label, top = 250, size = 170}) => {
  const {t, active, dur} = useShot(shot); if (!active) return null; const a = Math.round(dur * at);
  const v = Math.round(to * interpolate(t, [a, a + 40], [0, 1], {...clamp, easing: ease}));
  return <Fade t={t} dur={dur}><Pop at={a} t={t} style={{position: 'absolute', width: '100%', top, textAlign: 'center'}}>
    <Big size={size}>{v.toLocaleString('en-IN')}</Big><Sub size={44}>{label}</Sub></Pop></Fade>;
};
const Hook: React.FC = () => {
  const {t, active, dur} = useShot('hook'); if (!active) return null;
  const x = interpolate(t, [dur * 0.38, dur * 0.48], [0, 1], clamp);
  return <Fade t={t} dur={dur}>
    <Pop at={4} t={t} style={{position: 'absolute', width: '100%', top: 230, textAlign: 'center'}}>
      <Sub size={46}>రోజుకి</Sub><Big size={150}>1,00,000</Big><Sub size={46}>భక్తులు</Sub>
    </Pop>
    <Pop at={Math.round(dur * 0.4)} t={t} style={{position: 'absolute', width: '100%', top: 640, textAlign: 'center'}}>
      <div style={{display: 'inline-block', padding: '12px 34px', borderRadius: 20, background: 'rgba(120,10,0,0.85)', border: '3px solid #FF6A4D', fontFamily: FONT,
        fontSize: 54, fontWeight: 900, color: 'white', transform: `rotate(${-4 * x}deg)`}}>ప్రైవేట్ హోటళ్ళు: 0</div>
    </Pop>
  </Fade>;
};
const Rename: React.FC = () => {
  const {t, active, dur} = useShot('rename'); if (!active) return null;
  const a = Math.round(dur * 0.12), b = Math.round(dur * 0.55);
  const strike = interpolate(t, [b - 20, b - 6], [0, 100], clamp);
  return <Fade t={t} dur={dur}>
    <Pop at={a} t={t} style={{position: 'absolute', width: '100%', top: 230, textAlign: 'center'}}>
      <Sub size={38}>దాతలు కట్టిన</Sub><Big size={120}>45</Big><Sub size={38}>అతిథి గృహాలు</Sub>
    </Pop>
    <Pop at={Math.round(dur * 0.3)} t={t} style={{position: 'absolute', width: '100%', top: 600, textAlign: 'center'}}>
      <div style={{position: 'relative', display: 'inline-block', fontFamily: FONT, fontSize: 46, fontWeight: 800, color: '#ddd', padding: '6px 20px', background: 'rgba(0,0,0,0.55)', borderRadius: 14}}>
        లక్ష్మీ VPR గెస్ట్ హౌస్
        <div style={{position: 'absolute', left: 10, top: '52%', height: 6, width: `${strike * 0.96}%`, background: '#FF3B30', borderRadius: 3}} />
      </div>
      {t > b && <Pop at={b} t={t} style={{marginTop: 18}}><Big size={84}>లక్ష్మీ భవన్</Big></Pop>}
    </Pop>
  </Fade>;
};
const Gods: React.FC = () => {
  const {t, active, dur} = useShot('gods'); if (!active) return null;
  const items: [string, string, number][] = [['శ్రీ పద్మావతి అతిథి గృహం', 'అమ్మవారి పేరు', 0.04], ['శ్రీ వేంకటేశ్వర అతిథి గృహం', 'స్వామివారి పేరు', 0.25], ['వరాహస్వామి అతిథి గృహం', 'ఆదివరాహ క్షేత్రం', 0.5]];
  return <Fade t={t} dur={dur}>
    <div style={{position: 'absolute', width: '100%', top: 210, textAlign: 'center'}}>
      {items.map(([n, s, at]) => t >= dur * at ? <Pop key={n} at={Math.round(dur * at)} t={t} style={{marginBottom: 22}}>
        <div style={{display: 'inline-block', padding: '10px 30px', borderRadius: 22, background: 'rgba(40,14,0,0.78)', border: '3px solid #FFC23D', boxShadow: '0 0 30px rgba(255,180,50,0.5)'}}>
          <div style={{fontFamily: SERIF, fontSize: 54, fontWeight: 900}}><span style={{...goldText, filter: undefined}}>{n}</span></div><Sub size={30}>{s}</Sub></div></Pop> : null)}
    </div>
  </Fade>;
};
const More: React.FC = () => {
  const {t, active, dur} = useShot('more'); if (!active) return null;
  const names = ['యాత్రి సదన్', 'రాంబగీచా', 'ఆళ్వార్ ట్యాంక్', 'గాయత్రి సదన్', 'హిల్ వ్యూ', 'మంగళ బావి', 'వ్యాలీ వ్యూ', 'శంకు మిట్ట'];
  return <Fade t={t} dur={dur}>
    <div style={{position: 'absolute', left: 60, right: 60, top: 220, display: 'flex', flexWrap: 'wrap', justifyContent: 'center', gap: 16}}>
      {names.map((n, i) => { const at = Math.round(dur * 0.07 * i); return t >= at ? <Pop key={n} at={at} t={t}>
        <div style={{padding: '8px 22px', borderRadius: 18, background: 'rgba(40,14,0,0.78)', border: '2px solid #FFC23D', fontFamily: SERIF, fontSize: 44, fontWeight: 900}}>
          <span style={{...goldText, filter: undefined}}>{n}</span></div></Pop> : null; })}
    </div>
  </Fade>;
};
const Om: React.FC<{size?: number}> = ({size = 40}) => <div style={{fontFamily: SERIF, fontSize: size, fontWeight: 800, letterSpacing: 2, ...goldText}}>ఓం నమో వేంకటేశాయ</div>;
const Finale: React.FC = () => {
  const f = useCurrentFrame(); const [a, b] = span('finale'); if (f < a) return null; const t = f - a;
  const endIn = b - 95; const e = interpolate(f, [endIn, endIn + 18], [0, 1], clamp); const mid = Math.round((b - a) * 0.45);
  return <AbsoluteFill>
    <AbsoluteFill style={{opacity: 1 - e}}>
      <Pop at={6} t={t} style={{position: 'absolute', width: '100%', top: 210, textAlign: 'center'}}><Om size={58} /></Pop>
      {t > mid && <Pop at={mid} t={t} style={{position: 'absolute', width: '100%', top: 330, textAlign: 'center'}}><Big size={120}>గోవిందా… గోవిందా!</Big></Pop>}
    </AbsoluteFill>
    <AbsoluteFill style={{opacity: e, background: 'radial-gradient(ellipse at center, rgba(42,22,8,0.92), rgba(20,8,2,0.97))', alignItems: 'center', justifyContent: 'center'}}>
      <Img src={staticFile('logo_wm.png')} style={{width: 420, height: 420, transform: `scale(${0.9 + 0.1 * e})`}} />
      <div style={{fontSize: 46, color: CREAM, fontWeight: 800, marginTop: 40, fontFamily: SERIF}}>మీరు ఏ అతిథి గృహంలో ఉన్నారు?</div>
      <div style={{fontSize: 36, color: GOLD, fontWeight: 700, marginTop: 14, fontFamily: FONT}}>Follow @charithracheppinakatha</div>
      <div style={{position: 'absolute', bottom: 60, width: '100%', textAlign: 'center', color: 'rgba(255,255,255,0.6)', fontSize: 19, padding: '0 60px', lineHeight: 1.4, fontFamily: 'DejaVu Sans, Arial'}}>
        Sources: TTD (tirumala.org, TTD board note, TTD press 2019 & 2025–26) · Rooms: approx. · Miniature: Blender; figures by Model Forge; buildings & trees Quaternius (CC0); HDRI Poly Haven (CC0)
      </div>
    </AbsoluteFill>
  </AbsoluteFill>;
};
const Logo: React.FC = () => {
  const f = useCurrentFrame(); const o = interpolate(f, [15, 30, T.end - 110, T.end - 95], [0, 0.6, 0.6, 0], clamp);
  return <Img src={staticFile('logo_wm.png')} style={{position: 'absolute', left: 40, top: 170, width: 110, height: 110, opacity: o}} />;
};
export const Main: React.FC<{bg: string; audio: string; preview: boolean}> = ({bg, audio, preview}) => (
  <AbsoluteFill style={{background: '#0b0805'}}>
    {preview ? <AbsoluteFill style={{background: 'linear-gradient(#4a3a26, #0b0805)'}} /> : <OffthreadVideo src={staticFile(bg)} muted />}
    {!preview && <Audio src={staticFile(audio)} />}
    <Divine /><Finish /><Dips />
    <Hook />
    <Count shot="count" to={7800} at={0.12} label="గదులు · కాటేజీలు · అతిథి గృహాలు · సత్రాలు" />
    <Rename />
    <Pin shot="rename" k="donor" name="దాతల అతిథి గృహం" at={0.05} small />
    <Pin shot="nandakam" k="nand" name="నందకం" sub="విష్ణువు ఖడ్గం · 340 గదులు" icon="sword" at={0.42} />
    <Pin shot="panchajanyam" k="panch" name="పాంచజన్యం" sub="దివ్య శంఖం · 386 గదులు" icon="conch" at={0.08} />
    <Pin shot="kausthubham" k="kaus" name="కౌస్తుభం" sub="స్వామి వక్షస్థలపు మణి" icon="gem" at={0.08} />
    <Pin shot="vakula" k="vakula" name="మాతృశ్రీ వకుళమాత" sub="270 గదులు · 1,400 మంది" icon="lotus" at={0.3} />
    <Pin shot="four" k="nand" name="నందకం" icon="sword" at={0.05} small />
    <Pin shot="four" k="panch" name="పాంచజన్యం" icon="conch" at={0.12} small />
    <Pin shot="four" k="kaus" name="కౌస్తుభం" icon="gem" at={0.19} small />
    <Pin shot="four" k="vakula" name="వకుళమాత" icon="lotus" at={0.26} small />
    <Count shot="four" to={1228} at={0.45} label="గదులు · నాలుగింటిలోనే" top={200} size={150} />
    <Pin shot="pac" k="pac" name="వేంకటాద్రి నిలయం" sub="PAC-5 · ఉచితం · 2,500 మంది" icon="hill" at={0.35} />
    <Gods />
    <Pin shot="hills" k="seshadri" name="శేషాద్రి నగర్" icon="hill" at={0.35} small />
    <Pin shot="hills" k="garudadri" name="గరుడాద్రి నగర్" icon="hill" at={0.5} small />
    <Pin shot="hills" k="anjanadri" name="అంజనాద్రి నగర్" icon="hill" at={0.65} small />
    <More /><Finale /><Captions /><Logo />
  </AbsoluteFill>
);
