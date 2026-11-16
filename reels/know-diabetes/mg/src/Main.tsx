import React from 'react';
import {AbsoluteFill, Audio, OffthreadVideo, interpolate, spring, staticFile, useCurrentFrame, Easing} from 'remotion';
import T from './timing.json';

const FONT = 'Poppins, "DejaVu Sans", Arial, sans-serif';
const FPS = 30, ORANGE = '#FF8A1F', RED = '#FF4B3E', GREEN = '#33D17A', GOLD = '#FFC23D', CYAN = '#3FD8FF', MINT = '#9FF0C9';
const clamp = {extrapolateLeft: 'clamp' as const, extrapolateRight: 'clamp' as const};
const ease = Easing.bezier(0.16, 1, 0.3, 1);
const card: React.CSSProperties = {background: 'rgba(8, 12, 22, 0.80)', borderRadius: 30, border: '2px solid rgba(255,255,255,0.14)',
  boxShadow: '0 20px 60px rgba(0,0,0,0.45)', color: 'white', fontFamily: FONT};
const span = (i: number, j = i) => [Math.round(T.starts[i] * FPS), Math.round((T.starts[j] + T.durs[j]) * FPS)];
const Pop: React.FC<{at: number; t: number; children: React.ReactNode; style?: React.CSSProperties}> = ({at, t, children, style}) => {
  const s = spring({frame: t - at, fps: FPS, config: {damping: 14, stiffness: 160}});
  return <div style={{...style, opacity: interpolate(t - at, [0, 6], [0, 1], clamp), transform: `translateY(${(1 - s) * 60}px) scale(${0.85 + 0.15 * s})`}}>{children}</div>;
};
// a layer that lives for lines i..j, fading in and out
const Seg: React.FC<{i: number; j?: number; hold?: boolean; children: (t: number, dur: number) => React.ReactNode}> = ({i, j = i, hold, children}) => {
  const f = useCurrentFrame(); const [a, b0] = span(i, j); const b = hold ? T.end : b0;
  if (f < a || f >= b) return null; const t = f - a, dur = b - a;
  return <AbsoluteFill style={{opacity: interpolate(t, [0, 8, dur - 6, dur], [0, 1, 1, hold ? 1 : 0], clamp)}}>{children(t, dur)}</AbsoluteFill>;
};
const Panel: React.FC<{top?: number; color?: string; children: React.ReactNode}> = ({top = 240, color, children}) => (
  <div style={{position: 'absolute', left: 60, top, width: 960, ...card, padding: '28px 36px', borderColor: color || 'rgba(255,255,255,0.14)'}}>{children}</div>
);
const Kicker: React.FC<{c?: string; children: React.ReactNode}> = ({c = ORANGE, children}) => (
  <div style={{fontSize: 30, letterSpacing: 5, fontWeight: 800, color: c, marginBottom: 8}}>{children}</div>
);
const Rows: React.FC<{t: number; dur: number; items: string[]; c: string; tick?: boolean; from?: number; to?: number; size?: number}> = ({t, dur, items, c, tick, from = 0.08, to = 0.6, size = 44}) => (
  <>{items.map((x, n) => {
    const s = spring({frame: t - Math.round(dur * (from + ((to - from) * n) / items.length)), fps: FPS, config: {damping: 14}});
    return <div key={x} style={{fontSize: size, fontWeight: 800, margin: '10px 0', opacity: s, transform: `translateX(${(1 - s) * 60}px)`}}>
      <span style={{color: c}}>{tick ? '✓' : '•'}</span>&nbsp; {x}</div>;
  })}</>
);

// ---------- captions ----------
type Chunk = {words: string[]; s: number; e: number};
const CH: Chunk[][] = T.lines.map((ln, i) => {
  const words = ln.text.split(' '); const w = words.map((x) => Math.max(x.replace(/[?.!,:]/g, '').length, 2));
  const total = w.reduce((a, b) => a + b, 0); const d = T.durs[i] - 0.45;
  const out: Chunk[] = []; let cur: string[] = []; let cw = 0; let tc = T.starts[i];
  words.forEach((wd, k) => {
    cur.push(wd); cw += w[k];
    if (cur.length === 3 || cur.join('').length >= 13 || /[?.!,:]$/.test(wd) || k === words.length - 1) {
      const e = tc + (d * cw) / total; out.push({words: cur, s: tc, e}); tc = e; cur = []; cw = 0;
    }
  });
  return out;
});
const Captions: React.FC = () => {
  const f = useCurrentFrame(); const sec = f / FPS;
  for (let i = 0; i < CH.length - 1; i++) for (const c of CH[i]) {          // the last line is shown by the end card
    if (sec >= c.s && sec < c.e + (c === CH[i][CH[i].length - 1] ? 0.3 : 0)) {
      const k = T.lines[i].keywords.map((x) => x.toLowerCase().replace(/[?.!,:]/g, ''));
      const sc = interpolate(f - c.s * FPS, [0, 4], [0.82, 1], {...clamp, easing: ease});
      return <div style={{position: 'absolute', top: 1230, width: '100%', textAlign: 'center', fontFamily: FONT, fontWeight: 900, fontSize: 84, lineHeight: 1.08,
        color: 'white', transform: `scale(${sc})`, padding: '0 70px', textShadow: '0 6px 0 rgba(0,0,0,0.55), 0 0 26px rgba(0,0,0,0.6)',
        WebkitTextStroke: '3px rgba(0,0,0,0.85)', paintOrder: 'stroke fill'}}>
        {c.words.map((wd, n) => <span key={n} style={{color: k.includes(wd.toLowerCase().replace(/[?.!,:]/g, '')) ? ORANGE : 'white'}}>{wd}{n < c.words.length - 1 ? ' ' : ''}</span>)}
      </div>;
    }
  }
  return null;
};
const Dips: React.FC = () => {
  const f = useCurrentFrame(); let o = 0;
  for (const c of T.cuts) o = Math.max(o, interpolate(f - c, [-4, 0, 6], [0, 0.85, 0], clamp));
  return <AbsoluteFill style={{background: '#02040a', opacity: o}} />;
};

// ---------- cards, one per line of the script ----------
const Hook: React.FC = () => <Seg i={0}>{(t, dur) => (
  <div style={{position: 'absolute', left: 60, top: 250, display: 'flex', flexDirection: 'column', gap: 16}}>
    {['Always thirsty', 'Always tired', 'Bathroom, again and again'].map((x, n) => (
      <Pop key={x} at={Math.round(dur * (0.04 + 0.22 * n))} t={t}><div style={{...card, display: 'inline-block', padding: '14px 28px', fontSize: 46, fontWeight: 800, borderColor: ORANGE}}>
        <span style={{color: ORANGE}}>?</span>&nbsp; {x}</div></Pop>))}
  </div>)}</Seg>;
const Title: React.FC = () => <Seg i={1}>{(t) => (
  <Pop at={2} t={t} style={{position: 'absolute', width: '100%', top: 330, textAlign: 'center', fontFamily: FONT}}>
    <div style={{fontSize: 150, fontWeight: 900, color: 'white', lineHeight: 1, textShadow: '0 8px 40px rgba(0,0,0,0.8)'}}>DIABETES</div>
    <div style={{fontSize: 52, fontWeight: 800, color: MINT, marginTop: 14, textShadow: '0 4px 20px rgba(0,0,0,0.8)'}}>The silent sugar problem</div>
  </Pop>)}</Seg>;
const Chain: React.FC = () => <Seg i={2}>{(t, dur) => {
  const steps = ['FOOD', 'DIGESTION', 'GLUCOSE', 'ENERGY']; const cols = [ORANGE, ORANGE, GOLD, GREEN];
  return <div style={{position: 'absolute', left: 60, right: 60, top: 250, display: 'flex', alignItems: 'center', justifyContent: 'space-between'}}>
    {steps.map((x, n) => <React.Fragment key={x}>
      <Pop at={Math.round(dur * (0.05 + 0.2 * n))} t={t}><div style={{...card, padding: '16px 18px', fontSize: 34, fontWeight: 900, borderColor: cols[n], color: cols[n]}}>{x}</div></Pop>
      {n < 3 && <Pop at={Math.round(dur * (0.15 + 0.2 * n))} t={t}><div style={{fontSize: 44, fontWeight: 900, color: 'white', fontFamily: FONT}}>→</div></Pop>}
    </React.Fragment>)}
  </div>;
}}</Seg>;
const Insulin: React.FC = () => <Seg i={3}>{(t, dur) => (
  <Pop at={Math.round(dur * 0.25)} t={t} style={{position: 'absolute', left: 60, top: 250}}>
    <div style={{...card, padding: '22px 34px', borderColor: CYAN}}>
      <Kicker c={CYAN}>INSULIN</Kicker>
      <div style={{fontSize: 46, fontWeight: 800, lineHeight: 1.2}}>A hormone from the pancreas</div>
      <div style={{fontSize: 36, fontWeight: 700, opacity: 0.9, marginTop: 6}}>It signals cells to let glucose in</div>
    </div></Pop>)}</Seg>;
const Types: React.FC = () => {
  const f = useCurrentFrame(); const R: [string, string, string][] = [['TYPE 1', 'Immune system destroys insulin-making cells', RED],
    ['TYPE 2', 'Cells stop responding to insulin', ORANGE], ['GESTATIONAL', 'Develops during pregnancy', CYAN]];
  return <Seg i={4} j={6}>{(t) => <Panel><Kicker c={GOLD}>TYPES OF DIABETES</Kicker>
    {R.map(([k, v, c], n) => {
      const a = span(4 + n)[0] - span(4)[0]; const on = f >= span(4 + n)[0] && f < span(4 + n)[1];
      const s = spring({frame: t - a - 3, fps: FPS, config: {damping: 14}});
      return <div key={k} style={{display: 'flex', alignItems: 'center', gap: 22, margin: '14px 0', opacity: s * (on ? 1 : 0.55), transform: `translateX(${(1 - s) * 60}px)`}}>
        <div style={{minWidth: 270, textAlign: 'center', padding: '8px 12px', borderRadius: 16, background: c, color: '#0b0f18', fontSize: 34, fontWeight: 900}}>{k}</div>
        <div style={{fontSize: 36, fontWeight: 800, lineHeight: 1.15}}>{v}</div></div>;
    })}</Panel>}</Seg>;
};
const Signs: React.FC = () => <Seg i={7}>{(t, dur) => <>
  <Panel color={ORANGE}><Kicker>WARNING SIGNS</Kicker>
    <div style={{display: 'grid', gridTemplateColumns: '1fr 1fr', columnGap: 20}}>
      <Rows t={t} dur={dur} c={ORANGE} size={38} to={0.5} items={['Increased thirst', 'Frequent urination', 'Increased hunger', 'Tiredness', 'Blurred vision', 'Slow wound healing']} /></div>
  </Panel>
  <Pop at={Math.round(dur * 0.66)} t={t} style={{position: 'absolute', left: 60, top: 640, width: 960}}>
    <div style={{...card, padding: '16px 30px', borderColor: RED, fontSize: 38, fontWeight: 800}}><span style={{color: RED}}>Type 2:</span> often no symptoms for years</div></Pop>
</>}</Seg>;
const Risk: React.FC = () => <Seg i={8}>{(t, dur) => <>
  <Panel color={GOLD}><Kicker c={GOLD}>WHAT RAISES THE RISK</Kicker>
    <div style={{display: 'grid', gridTemplateColumns: '1fr 1fr', columnGap: 20}}>
      <Rows t={t} dur={dur} c={GOLD} size={40} to={0.45} items={['Family history', 'Age', 'Inactivity', 'Excess weight']} /></div></Panel>
  <Pop at={Math.round(dur * 0.6)} t={t} style={{position: 'absolute', left: 60, top: 560, width: 960}}>
    <div style={{...card, padding: '16px 30px', borderColor: GREEN, fontSize: 38, fontWeight: 800}}><span style={{color: GREEN}}>Not</span> simply caused by eating sweets</div></Pop>
</>}</Seg>;
const Organs: React.FC = () => {
  const O: [string, string][] = [['HEART', 'Higher risk of heart disease'], ['KIDNEYS', 'Filters get damaged'], ['EYES', 'Tiny retinal vessels damaged'], ['NERVES & FEET', 'Numbness, wounds']];
  return <Seg i={9}>{(t, dur) => {
    const k = Math.min(3, Math.floor((t / dur) * 4)); const lt = t - Math.round((dur * k) / 4);
    return <>
      <div style={{position: 'absolute', top: 210, width: '100%', textAlign: 'center', fontFamily: FONT, fontSize: 34, fontWeight: 800, letterSpacing: 3, color: RED, textShadow: '0 3px 12px rgba(0,0,0,0.9)'}}>LONG-TERM HIGH BLOOD SUGAR</div>
      <Pop key={k} at={2} t={lt} style={{position: 'absolute', left: 60, top: 270}}>
        <div style={{...card, padding: '18px 32px', borderColor: RED}}><div style={{fontSize: 60, fontWeight: 900, color: RED}}>{O[k][0]}</div>
          <div style={{fontSize: 38, fontWeight: 700}}>{O[k][1]}</div></div></Pop></>;
  }}</Seg>;
};
const Tests: React.FC = () => {
  const R: [string, string, string][] = [['Fasting blood glucose', '≥126 mg/dL', 'after at least 8 hours without food'], ['2-hour glucose tolerance test', '≥200 mg/dL', 'after a 75 g glucose drink'],
    ['HbA1c', '≥6.5%', 'average over about 2–3 months']];
  return <Seg i={10}>{(t, dur) => <Panel top={215} color={GREEN}><Kicker c={GREEN}>DIAGNOSIS · NON-PREGNANT ADULTS</Kicker>
    {R.map(([k, v, s_], n) => {
      const s = spring({frame: t - Math.round(dur * (0.12 + 0.2 * n)), fps: FPS, config: {damping: 14}});
      return <div key={k} style={{display: 'flex', justifyContent: 'space-between', alignItems: 'center', padding: '12px 0', borderTop: n ? '1px solid rgba(255,255,255,0.15)' : undefined, opacity: s, transform: `translateY(${(1 - s) * 30}px)`}}>
        <div><div style={{fontSize: 36, fontWeight: 800}}>{k}</div><div style={{fontSize: 24, opacity: 0.75}}>{s_}</div></div>
        <div style={{fontSize: 56, fontWeight: 900, color: GREEN, whiteSpace: 'nowrap'}}>{v}</div></div>;
    })}
    <Pop at={Math.round(dur * 0.78)} t={t}><div style={{marginTop: 8, fontSize: 28, fontWeight: 700, color: GOLD}}>A doctor confirms it. One home reading is not a diagnosis.</div></Pop>
  </Panel>}</Seg>;
};
const Manage: React.FC = () => <Seg i={11}>{(t, dur) => <Panel color={GREEN}><Kicker c={GREEN}>DIABETES CAN BE MANAGED</Kicker>
  <Rows t={t} dur={dur} c={GREEN} tick from={0.2} to={0.85} items={['Eat balanced meals', 'Stay active', 'Check sugar as advised', 'Take medicines as prescribed']} /></Panel>}</Seg>;
const Prevent: React.FC = () => <Seg i={12}>{(t, dur) => <Panel color={CYAN}><Kicker c={CYAN}>CAN IT BE PREVENTED?</Kicker>
  <Pop at={4} t={t}><div style={{fontSize: 40, fontWeight: 800, margin: '10px 0'}}><span style={{color: RED}}>Type 1:</span> not by lifestyle changes</div></Pop>
  <Pop at={Math.round(dur * 0.45)} t={t}><div style={{fontSize: 40, fontWeight: 800, margin: '10px 0'}}><span style={{color: GREEN}}>Type 2:</span> risk can often be reduced</div></Pop>
</Panel>}</Seg>;
const End: React.FC = () => <Seg i={13} hold>{(t) => <>
  <AbsoluteFill style={{background: 'linear-gradient(180deg, rgba(4,20,16,0.55) 0%, rgba(4,20,16,0.25) 45%, rgba(4,20,16,0.85) 100%)'}} />
  <div style={{position: 'absolute', left: 70, right: 70, top: 300, ...card, background: 'rgba(14,42,34,0.92)', padding: '44px 30px', textAlign: 'center', borderColor: MINT}}>
    {[['KNOW DIABETES', 'white'], ['CONTROL DIABETES', MINT], ['LIVE A HEALTHIER LIFE', 'white']].map(([x, c], n) => (
      <Pop key={x} at={4 + n * 28} t={t}><div style={{fontSize: 68, fontWeight: 900, color: c, lineHeight: 1.35}}>{x}</div></Pop>))}
    <Pop at={96} t={t}><div style={{borderTop: '2px solid rgba(255,255,255,0.3)', marginTop: 22, paddingTop: 20, fontSize: 36, fontWeight: 700}}>Health awareness can save lives.</div></Pop>
  </div></>}</Seg>;
const Credit: React.FC = () => (
  <div style={{position: 'absolute', bottom: 70, width: '100%', textAlign: 'center', color: 'rgba(255,255,255,0.75)', fontSize: 22, padding: '0 60px', fontFamily: FONT, textShadow: '0 2px 6px rgba(0,0,0,0.9)'}}>
    For learning only. Not medical advice. Don't change your medicines without your doctor.<br />
    3D anatomy: Z-Anatomy (CC BY-SA 4.0), based on BodyParts3D © DBCLS (CC BY-SA 2.1 JP).</div>
);
export const Main: React.FC = () => (
  <AbsoluteFill style={{background: '#0b1020'}}>
    <OffthreadVideo src={staticFile('bg.mp4')} muted />
    <Audio src={staticFile('narration.wav')} />
    <Dips /><Hook /><Title /><Chain /><Insulin /><Types /><Signs /><Risk /><Organs /><Tests /><Manage /><Prevent /><End /><Captions /><Credit />
  </AbsoluteFill>
);
