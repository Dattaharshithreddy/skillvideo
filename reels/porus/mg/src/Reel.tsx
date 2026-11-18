// Puru vs Alexander: Telugu motion-design layer over the Blender miniature, in the style of the Tirumala reel
// (gold serif titles, dark cards, gold name pins that follow the 3D figures, bold captions with gold keywords, dips between shots).
import React from 'react';
import {AbsoluteFill, Audio, Img, OffthreadVideo, interpolate, spring, staticFile, useCurrentFrame, Easing} from 'remotion';
import {loadFont} from '@remotion/fonts';
import T from './timing.json';
import LB from './labels.json';

loadFont({family: 'Noto Sans Telugu', url: staticFile('fonts/sans-800.woff2'), weight: '800'});
loadFont({family: 'Noto Sans Telugu', url: staticFile('fonts/sans-900.woff2'), weight: '900'});
loadFont({family: 'Noto Serif Telugu', url: staticFile('fonts/serif-800.woff2'), weight: '800'});
loadFont({family: 'Noto Serif Telugu', url: staticFile('fonts/serif-900.woff2'), weight: '900'});

const FPS = 30;
const FONT = '"Noto Sans Telugu", Poppins, sans-serif';
const SERIF = '"Noto Serif Telugu", "Noto Sans Telugu", serif';
const GOLD = '#FFC23D', RED = '#FF4A3D', BLUE = '#6EC6FF';
const clamp = {extrapolateLeft: 'clamp' as const, extrapolateRight: 'clamp' as const};
const ease = Easing.bezier(0.16, 1, 0.3, 1);
// envelope 0 -> 1 -> 1 -> 0 that stays valid for very short shots
const env = (t: number, dur: number, a = 8, b = 6, end = 0) => {
  const p1 = Math.min(a, dur * 0.3), p2 = Math.max(p1 + 0.01, dur - Math.min(b, dur * 0.3)), p3 = Math.max(p2 + 0.01, dur);
  return interpolate(t, [0, p1, p2, p3], [0, 1, 1, end], clamp);
};
const goldText: React.CSSProperties = {background: 'linear-gradient(180deg, #FFF6C8 0%, #FFD35A 42%, #F09A1A 78%, #FFE08A 100%)', WebkitBackgroundClip: 'text',
  backgroundClip: 'text', color: 'transparent', filter: 'drop-shadow(0 4px 0 rgba(90,40,0,0.85)) drop-shadow(0 0 22px rgba(255,170,40,0.6))'};
const card: React.CSSProperties = {background: 'rgba(8,8,14,0.74)', borderRadius: 26, border: '2px solid rgba(255,214,120,0.55)',
  boxShadow: '0 18px 50px rgba(0,0,0,0.5)', color: 'white', fontFamily: FONT};

type Line = {shot: string; text: string; keywords: string[]};
const LINES = T.lines as Line[];
const idx = (shot: string) => LINES.findIndex((l) => l.shot === shot);
const from = (i: number) => (T.nf as number[]).slice(0, i).reduce((a, b) => a + b, 0);
const useShot = (shot: string) => {
  const f = useCurrentFrame(); const i = idx(shot); const a = from(i), dur = (T.nf as number[])[i];
  return {t: f - a, dur, active: i >= 0 && f >= a && f < a + dur};
};
const Pop: React.FC<{at: number; t: number; children: React.ReactNode; style?: React.CSSProperties}> = ({at, t, children, style}) => {
  const s = spring({frame: t - at, fps: FPS, config: {damping: 15, stiffness: 150}});
  return <div style={{...style, opacity: interpolate(t - at, [0, 6], [0, 1], clamp), transform: `translateY(${(1 - s) * 60}px)`}}>{children}</div>;
};
const Fade: React.FC<{t: number; dur: number; children: React.ReactNode; out?: boolean}> = ({t, dur, children, out = true}) => (
  <AbsoluteFill style={{opacity: env(t, dur, 8, 6, out ? 0 : 1)}}>{children}</AbsoluteFill>
);
const Tag: React.FC<{c?: string; k: string; v: string; sub?: string}> = ({c = GOLD, k, v, sub}) => (
  <div style={{...card, padding: '16px 28px', borderColor: c, display: 'inline-block'}}>
    <div style={{fontSize: 28, letterSpacing: 2, fontWeight: 800, color: c}}>{k}</div>
    <div style={{fontSize: 56, fontWeight: 900, lineHeight: 1.12}}>{v}</div>
    {sub && <div style={{fontSize: 28, opacity: 0.85, marginTop: 4}}>{sub}</div>}
  </div>
);

// ---------- pins that follow tracked 3D points ----------
const track = (shot: string, key: string, t: number): [number, number, number] | null => {
  const s = (LB as any)[shot]; if (!s) return null;
  const f = Math.max(1, t + 1); const k = String(f - ((f - 1) % 2));
  const fr = s[k] || s[String(f)]; if (!fr || !fr[key]) return null; return fr[key];
};
const Pin: React.FC<{shot: string; k: string; label: string; sub?: string; at: number; t: number; c?: string; up?: number; until?: number}> = ({shot, k, label, sub, at, t, c = GOLD, up = 120, until = 1e9}) => {
  const p = track(shot, k, t); if (!p || !p[2] || t > until) return null;
  const s = spring({frame: t - at, fps: FPS, config: {damping: 13, stiffness: 160}}); if (t < at) return null;
  const x = Math.min(900, Math.max(180, p[0] * 1080)), y = Math.min(1160, Math.max(380, p[1] * 1920));
  return <div style={{position: 'absolute', left: x, top: y, transform: `translate(-50%, -100%) scale(${s})`, transformOrigin: '50% 100%', textAlign: 'center'}}>
    <div style={{display: 'inline-block', padding: '8px 26px 6px', borderRadius: 18, background: 'rgba(30,12,0,0.82)', border: `3px solid ${c}`,
      boxShadow: `0 0 30px ${c}88`, fontFamily: SERIF, fontWeight: 900, fontSize: 54, whiteSpace: 'nowrap', color: 'white'}}>
      <span style={c === GOLD ? {...goldText, filter: undefined} : {color: c}}>{label}</span>
      {sub && <div style={{fontFamily: FONT, fontSize: 26, fontWeight: 800, color: 'rgba(255,240,210,0.9)'}}>{sub}</div>}
    </div>
    <div style={{width: 4, height: up, background: `linear-gradient(180deg, ${c}, ${c}22)`, margin: '0 auto'}} />
    <div style={{width: 16, height: 16, borderRadius: 8, background: '#FFE9A0', boxShadow: `0 0 18px ${c}`, margin: '-6px auto 0'}} />
  </div>;
};

// ---------- captions (word groups inside exact sentence times when available) ----------
type Ch = {words: string[]; s: number; e: number; line: number};
const groupWords = (words: string[], a: number, b: number, line: number): Ch[] => {
  const w = words.map((x) => Math.max(x.replace(/[?.!,…]/g, '').length, 2)); const total = w.reduce((p, q) => p + q, 0);
  const out: Ch[] = []; let cur: string[] = []; let cw = 0; let tc = a;
  words.forEach((wd, k) => {
    cur.push(wd); cw += w[k];
    if (cur.length === 3 || cur.join('').length >= 14 || /[?.!,…]$/.test(wd) || k === words.length - 1) {
      const e = tc + ((b - a) * cw) / total; out.push({words: cur, s: tc, e, line}); tc = e; cur = []; cw = 0;
    }
  });
  return out;
};
const SENTS = (T as any).sentences as {para: number; start: number; end: number; text: string}[];
const CH: Ch[] = (SENTS && SENTS.length)
  ? SENTS.flatMap((s) => groupWords(s.text.replace('క్రీస్తు పూర్వం మూడు వందల ఇరవై ఆరు.', 'క్రీస్తు పూర్వం 326.').replace('క్రీస్తు పూర్వం… మూడొందల ఇరవై ఆరు.', 'క్రీస్తు పూర్వం 326.').split(' ').filter(Boolean), s.start, s.end, s.para))
  : LINES.flatMap((l, i) => groupWords(l.text.split(' '), T.starts[i] + 0.15, T.starts[i] + T.durs[i] - 0.5, i));
const Captions: React.FC = () => {
  const f = useCurrentFrame(); const sec = f / FPS;
  const c = CH.find((x) => sec >= x.s && sec < x.e); if (!c) return null;
  const k = LINES[c.line].keywords.map((x) => x.replace(/[?.!,…]/g, ''));
  const sc = interpolate(f - c.s * FPS, [0, 4], [0.84, 1], {...clamp, easing: ease});
  return <div style={{position: 'absolute', top: 1240, width: '100%', textAlign: 'center', fontFamily: FONT, fontWeight: 900, fontSize: 70, lineHeight: 1.12,
    color: 'white', transform: `scale(${sc})`, padding: '0 70px', textShadow: '0 6px 0 rgba(0,0,0,0.55), 0 0 26px rgba(0,0,0,0.6)',
    WebkitTextStroke: '3px rgba(0,0,0,0.85)', paintOrder: 'stroke fill'}}>
    {c.words.map((wd, n) => <span key={n} style={{color: k.includes(wd.replace(/[?.!,…]/g, '')) ? GOLD : 'white'}}>{wd}{n < c.words.length - 1 ? ' ' : ''}</span>)}
  </div>;
};
const Dips: React.FC = () => {
  const f = useCurrentFrame(); let o = 0;
  for (let i = 1; i < LINES.length; i++) o = Math.max(o, interpolate(f - from(i), [-4, 0, 6], [0, 0.85, 0], clamp));
  return <AbsoluteFill style={{background: '#03050a', opacity: o}} />;
};
const Vignette: React.FC = () => <AbsoluteFill style={{background: 'radial-gradient(ellipse at 50% 46%, rgba(0,0,0,0) 55%, rgba(10,4,0,0.55) 100%)'}} />;

// ---------- weather and mood ----------
const rnd = (n: number) => { const x = Math.sin(n * 127.1 + 311.7) * 43758.5453; return x - Math.floor(x); };
const Rain: React.FC = () => {
  const {t, active, dur} = useShot('storm'); if (!active) return null;
  const o = env(t, dur, 10, 6);
  return <AbsoluteFill style={{opacity: o * 0.75}}>
    {Array.from({length: 140}).map((_, i) => {
      const sp = 70 + rnd(i) * 50, len = 60 + rnd(i + 3) * 90; const x = (rnd(i + 7) * 1300 - 110 + t * 9) % 1300 - 110;
      const y = ((rnd(i + 11) * 2200 + t * sp) % 2200) - 200;
      return <div key={i} style={{position: 'absolute', left: x, top: y, width: 2.4, height: len, transform: 'rotate(14deg)',
        background: 'linear-gradient(180deg, rgba(200,220,255,0), rgba(200,220,255,0.75))'}} />;
    })}
    <AbsoluteFill style={{background: 'linear-gradient(180deg, rgba(10,20,40,0.35), rgba(0,0,0,0.1))'}} />
  </AbsoluteFill>;
};
const NightTint: React.FC = () => {
  const a = useShot('feint'), b = useShot('storm'), m = useShot('murder');
  const s = a.active ? a : b.active ? b : m.active ? m : null; if (!s) return null;
  const o = env(s.t, s.dur);
  return <AbsoluteFill style={{opacity: o, background: m.active ? 'radial-gradient(ellipse at 55% 45%, rgba(0,0,0,0) 30%, rgba(0,0,0,0.75) 100%)'
    : 'radial-gradient(ellipse at 50% 45%, rgba(0,0,0,0) 45%, rgba(0,8,30,0.6) 100%)'}} />;
};
const Embers: React.FC<{o: number}> = ({o}) => {
  const f = useCurrentFrame();
  return <AbsoluteFill style={{mixBlendMode: 'screen', opacity: o}}>
    {Array.from({length: 40}).map((_, i) => {
      const sz = 5 + rnd(i) * 14, sp = 1.2 + rnd(i + 50) * 2.4;
      const y = 2000 - ((rnd(i + 9) * 2100 + f * sp) % 2100), x = rnd(i + 3) * 1080 + Math.sin(f / 40 + i) * 26;
      return <div key={i} style={{position: 'absolute', left: x, top: y, width: sz, height: sz, borderRadius: sz, opacity: 0.4 + 0.6 * Math.abs(Math.sin(f / 13 + i)),
        background: 'radial-gradient(circle, rgba(255,240,190,1) 0%, rgba(255,190,70,0.75) 45%, rgba(255,150,30,0) 72%)'}} />;
    })}
  </AbsoluteFill>;
};

// ---------- the twelve shots ----------
const Open: React.FC = () => {
  const {t, active, dur} = useShot('open'); if (!active) return null;
  const tO = interpolate(t, [dur * 0.36, dur * 0.42 + 1], [1, 0], clamp);
  return <Fade t={t} dur={dur}>
    <AbsoluteFill style={{opacity: tO}}><Pop at={6} t={t} style={{position: 'absolute', width: '100%', top: 170, textAlign: 'center'}}>
      <div style={{display: 'inline-block', fontFamily: FONT, fontWeight: 900, fontSize: 40, color: '#3a1800', background: 'linear-gradient(180deg,#FFE9A0,#F3A52A)',
        borderRadius: 40, padding: '4px 30px', marginBottom: 10}}>క్రీ.పూ. 326</div>
      <div style={{fontFamily: SERIF, fontSize: 132, fontWeight: 900, lineHeight: 1.25, ...goldText}}>పురు</div>
      <div style={{fontFamily: SERIF, fontSize: 56, fontWeight: 900, color: 'white', textShadow: '0 4px 18px rgba(0,0,0,0.8)'}}>vs అలెగ్జాండర్</div>
      <div style={{fontFamily: FONT, fontSize: 34, fontWeight: 800, color: 'rgba(255,240,210,0.95)', marginTop: 6, textShadow: '0 3px 12px rgba(0,0,0,0.9)'}}>హైడాస్పెస్ (జీలం) యుద్ధం</div>
    </Pop></AbsoluteFill>
    <Pin shot="open" k="greek" label="అలెగ్జాండర్ సైన్యం" at={Math.round(dur * 0.45)} t={t} c={BLUE} up={70} />
    <Pin shot="open" k="indian" label="పురు సైన్యం" at={Math.round(dur * 0.62)} t={t} up={70} />
    <Pin shot="open" k="river" label="జీలం నది" at={Math.round(dur * 0.78)} t={t} c={BLUE} up={50} />
  </Fade>;
};
const Demand: React.FC = () => {
  const {t, active, dur} = useShot('demand'); if (!active) return null;
  return <Fade t={t} dur={dur}>
    <Pin shot="demand" k="messenger" label="అలెగ్జాండర్ దూత" at={8} t={t} c={BLUE} up={90} until={Math.round(dur * 0.55)} />
    {t < dur * 0.55 && <Pop at={Math.round(dur * 0.12)} t={t} style={{position: 'absolute', left: 70, top: 220}}><Tag c={BLUE} k="అలెగ్జాండర్ కబురు" v="కప్పం కట్టు!" sub="లొంగిపో" /></Pop>}
    <Pop at={Math.round(dur * 0.56)} t={t} style={{position: 'absolute', left: 70, top: 220}}><Tag c={RED} k="పురు జవాబు" v="సరిహద్దులో కలుద్దాం" sub="…ఆయుధాలతో!" /></Pop>
  </Fade>;
};
const Ambhi: React.FC = () => {
  const {t, active, dur} = useShot('ambhi'); if (!active) return null;
  return <Fade t={t} dur={dur}>
    <Pin shot="ambhi" k="fort" label="తక్షశిల" at={8} t={t} up={80} until={Math.round(dur * 0.52)} />
    <Pin shot="ambhi" k="ambhi" label="రాజు అంభి సైన్యం" at={Math.round(dur * 0.35)} t={t} c={RED} up={70} />
    <Pop at={Math.round(dur * 0.55)} t={t} style={{position: 'absolute', left: 70, top: 250}}><Tag c={RED} k="పొరుగు రాజు" v="ద్రోహం" sub="అలెగ్జాండర్‌కి కోట తలుపులు" /></Pop>
  </Fade>;
};
const River: React.FC = () => {
  const {t, active, dur} = useShot('river'); if (!active) return null;
  const n = Math.round(interpolate(t, [dur * 0.36, dur * 0.62 + 1], [1, 200], {...clamp, easing: ease}));
  return <Fade t={t} dur={dur}>
    <Pin shot="river" k="river" label="జీలం నది" sub="వరదలో ఉప్పొంగి" at={8} t={t} c={BLUE} up={60} />
    {t > dur * 0.36 && <Pop at={Math.round(dur * 0.36)} t={t} style={{position: 'absolute', left: 70, top: 250}}>
      <div style={{...card, padding: '18px 30px'}}>
        <div style={{fontSize: 130, fontWeight: 900, lineHeight: 1, ...goldText, fontFamily: FONT}}>{n}</div>
        <div style={{fontSize: 46, fontWeight: 900}}>యుద్ధ ఏనుగులు</div>
      </div></Pop>}
    <Pop at={Math.round(dur * 0.75)} t={t} style={{position: 'absolute', right: 70, top: 620}}><Tag c={RED} k="గ్రీకు గుర్రాలు" v="బెదిరిపోతాయి" /></Pop>
  </Fade>;
};
const Feint: React.FC = () => {
  const {t, active, dur} = useShot('feint'); if (!active) return null;
  return <Fade t={t} dur={dur}>
    <Pop at={8} t={t} style={{position: 'absolute', width: '100%', top: 200, textAlign: 'center'}}>
      <div style={{fontFamily: SERIF, fontSize: 104, fontWeight: 900, ...goldText}}>రాత్రి ఎత్తుగడ</div></Pop>
    <Pin shot="feint" k="torches" label="కాగడాలు, అరుపులు" at={Math.round(dur * 0.25)} t={t} c={'#FF9A3D'} up={80} />
    <Pop at={Math.round(dur * 0.62)} t={t} style={{position: 'absolute', left: 70, top: 470}}><Tag c={'#FF9A3D'} k="పురు సైన్యం" v="ప్రతిసారీ సిద్ధం…" sub="చివరికి అలసిపోయింది" /></Pop>
  </Fade>;
};
const Storm: React.FC = () => {
  const {t, active, dur} = useShot('storm'); if (!active) return null;
  return <Fade t={t} dur={dur}>
    <Pop at={8} t={t} style={{position: 'absolute', width: '100%', top: 200, textAlign: 'center'}}>
      <div style={{fontFamily: SERIF, fontSize: 108, fontWeight: 900, color: 'white', textShadow: '0 0 30px rgba(140,180,255,0.9)'}}>తుఫాను రాత్రి</div></Pop>
    <Pin shot="storm" k="crossing" label="రహస్యంగా నది దాటారు" at={Math.round(dur * 0.3)} t={t} c={BLUE} up={90} />
    <Pop at={Math.round(dur * 0.66)} t={t} style={{position: 'absolute', left: 70, top: 470}}><Tag c={BLUE} k="తెల్లవారి చూస్తే" v="అది ఒక దీవి!" sub="ఛాతీ లోతు నీళ్లలో మళ్ళీ" /></Pop>
  </Fade>;
};
const Son: React.FC = () => {
  const {t, active, dur} = useShot('son'); if (!active) return null;
  return <Fade t={t} dur={dur}>
    <Pin shot="son" k="prince" label="పురు కొడుకు" at={8} t={t} up={90} />
    <Pin shot="son" k="mud" label="రథాలు బురదలో" at={Math.round(dur * 0.35)} t={t} c={'#C98A4B'} up={50} />
  </Fade>;
};
const Battle: React.FC = () => {
  const {t, active, dur} = useShot('battle'); if (!active) return null;
  return <Fade t={t} dur={dur}>
    <Pin shot="battle" k="elephants" label="పురు ఏనుగులు" at={10} t={t} up={80} />
    <Pin shot="battle" k="phalanx" label="మాసిడోనియన్ బల్లాలు" sub="సరిస్సా · 5-6 మీటర్లు" at={Math.round(dur * 0.32)} t={t} c={BLUE} up={70} />
    <Pop at={Math.round(dur * 0.78)} t={t} style={{position: 'absolute', width: '100%', top: 220, textAlign: 'center'}}>
      <div style={{...card, display: 'inline-block', padding: '14px 34px', borderColor: RED}}>
        <div style={{fontSize: 30, color: RED, fontWeight: 800}}>అలెగ్జాండర్ జీవితంలోనే</div>
        <div style={{fontSize: 58, fontWeight: 900}}>అత్యంత కఠినమైన యుద్ధం</div></div></Pop>
  </Fade>;
};
const King: React.FC = () => {
  const {t, active, dur} = useShot('king'); if (!active) return null;
  return <Fade t={t} dur={dur}>
    <Pin shot="king" k="puru" label="పురు" at={8} t={t} up={60} until={Math.round(dur * 0.4)} />
    <Pin shot="king" k="alexander" label="అలెగ్జాండర్" at={Math.round(dur * 0.22)} t={t} c={BLUE} up={150} until={Math.round(dur * 0.4)} />
    <Pop at={Math.round(dur * 0.42)} t={t} style={{position: 'absolute', left: 70, right: 70, top: 230}}>
      <div style={{...card, padding: '14px 28px', borderColor: BLUE}}><div style={{fontSize: 28, color: BLUE, fontWeight: 800}}>అలెగ్జాండర్</div>
        <div style={{fontSize: 46, fontWeight: 900}}>“నిన్ను ఎలా చూడాలి?”</div></div></Pop>
    <Pop at={Math.round(dur * 0.62)} t={t} style={{position: 'absolute', left: 70, right: 70, top: 440}}>
      <div style={{...card, padding: '18px 28px', borderColor: GOLD}}><div style={{fontSize: 28, color: GOLD, fontWeight: 800}}>పురు</div>
        <div style={{fontFamily: SERIF, fontSize: 52, fontWeight: 900, lineHeight: 1.3, ...goldText}}>“ఒక రాజు ఇంకో రాజుని ఎలా చూస్తాడో… అలా.”</div></div></Pop>
  </Fade>;
};
const Return: React.FC = () => {
  const {t, active, dur} = useShot('return'); if (!active) return null;
  return <Fade t={t} dur={dur}>
    <Embers o={interpolate(t, [0, Math.min(20, dur * 0.25), Math.max(Math.min(20, dur * 0.25) + 1, dur * 0.5)], [0, 0.9, 0.5], clamp)} />
    <Pop at={10} t={t} style={{position: 'absolute', width: '100%', top: 210, textAlign: 'center'}}>
      <div style={{fontFamily: SERIF, fontSize: 92, fontWeight: 900, lineHeight: 1.3, ...goldText}}>రాజ్యం తిరిగి పురుకే</div>
      <div style={{fontFamily: FONT, fontSize: 36, fontWeight: 800, color: 'white', textShadow: '0 3px 12px rgba(0,0,0,0.9)'}}>…ఇంకా పెద్దదిగా</div></Pop>
    <Pop at={Math.round(dur * 0.58)} t={t} style={{position: 'absolute', left: 70, top: 520}}><Tag c={BLUE} k="బియాస్ నది దగ్గర" v="గ్రీకు సైన్యం ఆగిపోయింది" /></Pop>
  </Fade>;
};
const Murder: React.FC = () => {
  const {t, active, dur} = useShot('murder'); if (!active) return null;
  return <Fade t={t} dur={dur}>
    <Pin shot="murder" k="eudemus" label="యూడెమస్" sub="అలెగ్జాండర్ సేనాని" at={Math.round(dur * 0.25)} t={t} c={RED} up={90} />
    <Pop at={Math.round(dur * 0.6)} t={t} style={{position: 'absolute', width: '100%', top: 230, textAlign: 'center'}}>
      <div style={{display: 'inline-block', fontFamily: FONT, fontWeight: 900, fontSize: 56, color: RED, border: `4px solid ${RED}`, borderRadius: 16, padding: '4px 26px',
        transform: 'rotate(-3deg)', background: 'rgba(0,0,0,0.6)'}}>మోసంతో హత్య</div></Pop>
  </Fade>;
};
const Legacy: React.FC = () => {
  const {t, active, dur} = useShot('legacy'); if (!active) return null;
  return <AbsoluteFill style={{opacity: interpolate(t, [0, 8], [0, 1], clamp)}}>
    <Embers o={0.7} />
    <Pin shot="legacy" k="statue" label="పురు" at={8} t={t} up={60} />
    <Pop at={Math.round(dur * 0.45)} t={t} style={{position: 'absolute', width: '100%', top: 230, textAlign: 'center'}}>
      <div style={{fontFamily: SERIF, fontSize: 150, fontWeight: 900, lineHeight: 1.25, ...goldText}}>రాజు.</div></Pop>
    <Pop at={Math.round(dur * 0.72)} t={t} style={{position: 'absolute', width: '100%', top: 1520, textAlign: 'center'}}>
      <Img src={staticFile('logo.png')} style={{width: 150, height: 150, objectFit: 'contain'}} />
      <div style={{fontFamily: SERIF, fontSize: 44, fontWeight: 900, ...goldText}}>చరిత్ర చెప్పిన కథ</div></Pop>
  </AbsoluteFill>;
};
const Watermark: React.FC = () => {
  const f = useCurrentFrame(); const i = idx('legacy'); if (f >= from(i) + (T.nf as number[])[i] * 0.7) return null;
  return <Img src={staticFile('logo.png')} style={{position: 'absolute', right: 34, top: 60, width: 96, height: 96, objectFit: 'contain', opacity: 0.85}} />;
};

export const Reel: React.FC<{bg: string; audio: string; music: string; preview: boolean}> = ({bg, audio, music, preview}) => (
  <AbsoluteFill style={{background: preview ? 'transparent' : '#0b1020'}}>
    {!preview && <OffthreadVideo src={staticFile(bg)} muted />}
    <NightTint /><Rain /><Vignette />
    {!preview && audio && <Audio src={staticFile(audio)} />}
    {!preview && music && <Audio src={staticFile(music)} volume={0.22} />}
    <Dips />
    <Open /><Demand /><Ambhi /><River /><Feint /><Storm /><Son /><Battle /><King /><Return /><Murder /><Legacy />
    <Captions /><Watermark />
  </AbsoluteFill>
);
