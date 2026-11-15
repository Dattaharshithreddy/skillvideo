import React, {createContext, useContext} from 'react';
import {AbsoluteFill, Audio, OffthreadVideo, interpolate, spring, staticFile, useCurrentFrame, useVideoConfig, Easing} from 'remotion';
import TP from './timing_public.json';
import TS from './timing_student.json';

export const FONT = 'Poppins, "DejaVu Sans", Arial, sans-serif';
export const FPS = 30;
export const ORANGE = '#FF8A1F';
export const RED = '#FF3B30';
export const GREEN = '#33D17A';
export const BLUE = '#4DA3FF';
export const GOLD = '#FFC23D';
export const CYAN = '#3FD8FF';
type Timing = {starts: number[]; durs: number[]; cuts: number[]; lines: {text: string; keywords: string[]}[]};
export const TIMINGS: Record<string, Timing> = {public: TP as Timing, student: TS as Timing};
export const TAIL = 150; // student cut: silent high-yield card at the end (frames)
const Ctx = createContext<Timing>(TP as Timing);
const useT = () => useContext(Ctx);
export const clamp = {extrapolateLeft: 'clamp' as const, extrapolateRight: 'clamp' as const};
const ease = Easing.bezier(0.16, 1, 0.3, 1);
export const card: React.CSSProperties = {
  background: 'rgba(8, 12, 22, 0.78)', borderRadius: 30, border: '2px solid rgba(255,255,255,0.14)',
  boxShadow: '0 20px 60px rgba(0,0,0,0.45)', color: 'white', fontFamily: FONT,
};

// ---------- helpers ----------
const useLocal = (i: number) => {
  const T = useT(); const f = useCurrentFrame();
  const from = Math.round(T.starts[i] * FPS), dur = Math.round(T.durs[i] * FPS);
  return {t: f - from, dur, active: f >= from && f < from + dur};
};
const useSpan = (i: number, j: number) => {
  const T = useT(); const f = useCurrentFrame();
  const from = Math.round(T.starts[i] * FPS), to = Math.round((T.starts[j] + T.durs[j]) * FPS);
  const split = Math.round(T.starts[j] * FPS) - from;
  return {t: f - from, dur: to - from, split, active: f >= from && f < to};
};
export const Pop: React.FC<{at: number; t: number; children: React.ReactNode; style?: React.CSSProperties; from?: 'left' | 'up' | 'scale'}> = ({at, t, children, style, from = 'scale'}) => {
  const {fps} = useVideoConfig();
  const s = spring({frame: t - at, fps, config: {damping: 14, stiffness: 160}});
  const tf = from === 'left' ? `translateX(${(1 - s) * -700}px)` : from === 'up' ? `translateY(${(1 - s) * 80}px)` : `scale(${0.6 + 0.4 * s})`;
  return <div style={{...style, opacity: interpolate(t - at, [0, 6], [0, 1], clamp), transform: tf}}>{children}</div>;
};
const Fade: React.FC<{t: number; dur: number; children: React.ReactNode}> = ({t, dur, children}) => (
  <AbsoluteFill style={{opacity: interpolate(t, [0, 8, dur - 6, dur], [0, 1, 1, 0], clamp)}}>{children}</AbsoluteFill>
);
const Panel: React.FC<{top?: number; children: React.ReactNode; color?: string; w?: number}> = ({top = 250, children, color, w = 960}) => (
  <div style={{position: 'absolute', left: (1080 - w) / 2, top, width: w, ...card, padding: '28px 34px', borderColor: color || 'rgba(255,255,255,0.14)'}}>{children}</div>
);
const Kicker: React.FC<{c?: string; children: React.ReactNode}> = ({c = ORANGE, children}) => (
  <div style={{fontSize: 30, letterSpacing: 5, fontWeight: 800, color: c, marginBottom: 6}}>{children}</div>
);

// ---------- captions ----------
type Chunk = {words: string[]; s: number; e: number};
const chunksFor = (T: Timing): Chunk[][] => T.lines.map((ln, i) => {
  const words = ln.text.split(' ');
  const w = words.map((x) => Math.max(x.replace(/[?.!,:]/g, '').length, 2));
  const total = w.reduce((a, b) => a + b, 0);
  const d = T.durs[i] - 0.45;
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
  const T = useT(); const f = useCurrentFrame(); const sec = f / FPS;
  const ALL = React.useMemo(() => chunksFor(T), [T]);
  for (let i = 0; i < ALL.length; i++) {
    for (const c of ALL[i]) {
      if (sec >= c.s && sec < c.e + (c === ALL[i][ALL[i].length - 1] ? 0.3 : 0)) {
        const k = T.lines[i].keywords.map((x) => x.toLowerCase().replace(/[?.!,:]/g, ''));
        const sc = interpolate(f - c.s * FPS, [0, 4], [0.82, 1], {...clamp, easing: ease});
        return (
          <div style={{position: 'absolute', top: 1220, width: '100%', textAlign: 'center', fontFamily: FONT, fontWeight: 900, fontSize: 88,
            lineHeight: 1.08, color: 'white', transform: `scale(${sc})`, padding: '0 70px',
            textShadow: '0 6px 0 rgba(0,0,0,0.55), 0 0 26px rgba(0,0,0,0.6)', WebkitTextStroke: '3px rgba(0,0,0,0.85)', paintOrder: 'stroke fill'}}>
            {c.words.map((wd, n) => (
              <span key={n} style={{color: k.includes(wd.toLowerCase().replace(/[?.!,:]/g, '')) ? ORANGE : 'white'}}>{wd}{n < c.words.length - 1 ? ' ' : ''}</span>
            ))}
          </div>
        );
      }
    }
  }
  return null;
};
// short dip to dark at every station cut
const Dips: React.FC = () => {
  const T = useT(); const f = useCurrentFrame();
  let o = 0;
  for (const c of T.cuts) o = Math.max(o, interpolate(f - c, [-4, 0, 6], [0, 0.85, 0], clamp));
  return <AbsoluteFill style={{background: '#02040a', opacity: o}} />;
};

// ---------- reusable visuals ----------
const Dot: React.FC<{x: number; y: number; r?: number; c?: string}> = ({x, y, r = 10, c = GOLD}) => (
  <circle cx={x} cy={y} r={r} fill={c} style={{filter: `drop-shadow(0 0 6px ${c})`}} />
);
// a cell with a door; open 0..1, rust 0..1, key 0..1 (key travel), inflow 0..1
const KeyDoor: React.FC<{t: number; open: number; rust: number; kp: number; label?: string; sub?: string}> = ({t, open, rust, kp, label, sub}) => {
  const doorCol = rust > 0.01 ? `rgb(${150 + 50 * rust},${110 - 40 * rust},${80 - 50 * rust})` : '#8fa8c8';
  const dots = Array.from({length: 9}, (_, i) => {
    const ph = ((t / 40 + i / 9) % 1);
    const inside = open > 0.6 && i % 2 === 0;
    const x = inside ? 520 + 240 * ph : 120 + (i % 3) * 70 + 10 * Math.sin(t / 9 + i);
    const y = inside ? 230 + 40 * Math.sin(i + t / 15) : 150 + Math.floor(i / 3) * 70 + 8 * Math.cos(t / 11 + i);
    return <Dot key={i} x={x} y={y} r={13} />;
  });
  return (
    <svg width={900} height={420} viewBox="0 0 900 420">
      <rect x={470} y={40} width={410} height={360} rx={60} fill="rgba(51,209,122,0.10)" stroke={open > 0.6 ? GREEN : 'rgba(255,255,255,0.4)'} strokeWidth={6} />
      <text x={675} y={95} textAnchor="middle" fill="white" fontSize={34} fontWeight={800} fontFamily={FONT}>CELL</text>
      <rect x={455} y={150} width={36} height={170} fill="#0b1020" />
      <g transform={`translate(455 ${150 - 150 * open})`}><rect width={36} height={170} rx={8} fill={doorCol} />
        {rust > 0.2 && [20, 70, 120].map((yy) => <circle key={yy} cx={18} cy={yy} r={9 * rust} fill="#7a3b12" />)}
        <circle cx={18} cy={85} r={9} fill="#0b1020" /></g>
      {dots}
      <g transform={`translate(${60 + 330 * kp} 330)`} opacity={kp > 0 ? 1 : 0}>
        <circle cx={0} cy={0} r={22} fill="none" stroke={CYAN} strokeWidth={9} />
        <rect x={20} y={-5} width={60} height={10} fill={CYAN} /><rect x={62} y={5} width={8} height={14} fill={CYAN} /><rect x={74} y={5} width={8} height={10} fill={CYAN} />
      </g>
      {label && <text x={240} y={60} textAnchor="middle" fill={GOLD} fontSize={34} fontWeight={800} fontFamily={FONT}>{label}</text>}
      {sub && <text x={675} y={370} textAnchor="middle" fill={open > 0.6 ? GREEN : rust > 0.3 ? ORANGE : 'white'} fontSize={36} fontWeight={900} fontFamily={FONT}>{sub}</text>}
    </svg>
  );
};
// a chain of steps lighting up one by one
const Chain: React.FC<{steps: string[]; lit: number; color?: string; cols?: number; bad?: number[]}> = ({steps, lit, color = CYAN, cols = 2, bad = []}) => (
  <div style={{display: 'grid', gridTemplateColumns: `repeat(${cols}, 1fr)`, gap: 14}}>
    {steps.map((s, i) => {
      const on = Math.max(0, Math.min(1, lit - i));
      const isBad = bad.includes(i);
      return (
        <div key={s} style={{padding: '14px 18px', borderRadius: 18, fontSize: 34, fontWeight: 800, lineHeight: 1.15,
          background: on ? (isBad ? 'rgba(255,59,48,0.22)' : 'rgba(63,216,255,0.16)') : 'rgba(255,255,255,0.05)',
          border: `3px solid ${on ? (isBad ? RED : color) : 'rgba(255,255,255,0.12)'}`, opacity: 0.35 + 0.65 * on,
          transform: `scale(${0.94 + 0.06 * on})`, color: 'white'}}>
          <span style={{color: isBad ? RED : color, marginRight: 10}}>{i + 1}</span>{s}{isBad && on > 0.5 ? '  ✕' : ''}
        </div>
      );
    })}
  </div>
);
// glucose meter bar 0..300 mg/dL
const Meter: React.FC<{v: number; marks: [number, string, string][]; title?: string}> = ({v, marks, title}) => {
  const x = (n: number) => 40 + (n / 300) * 820;
  const col = v >= 126 ? RED : v >= 100 ? ORANGE : GREEN;
  return (
    <svg width={900} height={230} viewBox="0 0 900 230">
      {title && <text x={450} y={40} textAnchor="middle" fill="white" fontSize={32} fontWeight={800} fontFamily={FONT}>{title}</text>}
      <rect x={40} y={90} width={820} height={34} rx={17} fill="rgba(255,255,255,0.12)" />
      <rect x={40} y={90} width={Math.max(0, x(v) - 40)} height={34} rx={17} fill={col} />
      {marks.map(([n, lab, c]) => (
        <g key={n}><line x1={x(n)} y1={76} x2={x(n)} y2={138} stroke={c} strokeWidth={5} />
          <text x={x(n)} y={178} textAnchor="middle" fill={c} fontSize={30} fontWeight={800} fontFamily={FONT}>{n}</text>
          <text x={x(n)} y={212} textAnchor="middle" fill="rgba(255,255,255,0.8)" fontSize={22} fontFamily={FONT}>{lab}</text></g>
      ))}
      <text x={x(v)} y={68} textAnchor="middle" fill={col} fontSize={40} fontWeight={900} fontFamily={FONT}>{Math.round(v)}</text>
    </svg>
  );
};
const Station: React.FC<{i: number; stop: string; name: string; color: string; sub: string}> = ({i, stop, name, color, sub}) => {
  const {t, active, dur} = useLocal(i);
  if (!active) return null;
  return (
    <Fade t={t} dur={dur}>
      <Pop at={4} t={t} from="left" style={{position: 'absolute', left: 60, top: 250}}>
        <div style={{...card, padding: '22px 36px', borderColor: color}}>
          <div style={{fontSize: 30, letterSpacing: 6, color, fontWeight: 800}}>{stop}</div>
          <div style={{fontSize: 80, fontWeight: 900, lineHeight: 1}}>{name}</div>
          <div style={{fontSize: 34, opacity: 0.85, marginTop: 6}}>{sub}</div>
        </div>
      </Pop>
    </Fade>
  );
};
const Big: React.FC<{i: number; k: string; title: string; c: string; sub?: string; at?: number; top?: number}> = ({i, k, title, c, sub, at = 0.15, top = 300}) => {
  const {t, active, dur} = useLocal(i);
  if (!active) return null;
  return (
    <Fade t={t} dur={dur}>
      <Pop at={Math.round(dur * at)} t={t} from="up" style={{position: 'absolute', width: '100%', top, textAlign: 'center'}}>
        <Panel w={880} color={c}><Kicker c={c}>{k}</Kicker><div style={{fontSize: 76, fontWeight: 900, lineHeight: 1.05}}>{title}</div>
          {sub && <div style={{fontSize: 36, opacity: 0.85, marginTop: 8}}>{sub}</div>}</Panel>
      </Pop>
    </Fade>
  );
};
const List: React.FC<{i: number; title: string; items: string[]; c: string; tick?: boolean; from?: number; to?: number; top?: number}> = ({i, title, items, c, tick, from = 0.08, to = 0.6, top = 250}) => {
  const {t, active, dur} = useLocal(i);
  if (!active) return null;
  return (
    <Fade t={t} dur={dur}>
      <Panel top={top} color={c}><Kicker c={c}>{title}</Kicker>
        {items.map((x, n) => {
          const s = spring({frame: t - Math.round(dur * (from + (to - from) * n / items.length)), fps: FPS, config: {damping: 14}});
          return <div key={x} style={{fontSize: 44, fontWeight: 800, margin: '10px 0', opacity: s, transform: `translateX(${(1 - s) * 60}px)`}}>
            <span style={{color: c}}>{tick ? '✓' : '•'}</span>&nbsp; {x}</div>;
        })}
      </Panel>
    </Fade>
  );
};
const Credit: React.FC = () => (
  <div style={{position: 'absolute', bottom: 70, width: '100%', textAlign: 'center', color: 'rgba(255,255,255,0.72)', fontSize: 22, padding: '0 60px', fontFamily: FONT}}>
    For learning only. Not medical advice. Don't change your medicines without your doctor.<br />
    3D anatomy: Z-Anatomy (CC BY-SA 4.0), based on BodyParts3D © DBCLS (CC BY-SA 2.1 JP).
  </div>
);

// =============== PUBLIC CUT ===============
const PIntro: React.FC = () => {
  const {t, active, dur} = useLocal(0);
  if (!active) return null;
  return (
    <AbsoluteFill>
      <Pop at={6} t={t} from="left" style={{position: 'absolute', left: 70, top: 280}}>
        <div style={{...card, padding: '24px 40px'}}>
          <div style={{fontSize: 30, letterSpacing: 6, color: ORANGE, fontWeight: 700}}>MEET</div>
          <div style={{fontSize: 78, fontWeight: 900, lineHeight: 1}}>Raju</div>
          <div style={{fontSize: 36, opacity: 0.85, marginTop: 6}}>3 plates of rice a day</div>
        </div>
      </Pop>
      <Pop at={dur - 60} t={t} style={{position: 'absolute', width: '100%', top: 720, textAlign: 'center'}}>
        <div style={{fontFamily: FONT, fontWeight: 900, fontSize: 104, color: 'white', textShadow: '0 8px 30px rgba(0,0,0,0.6)'}}>
          FOLLOW THE <span style={{color: GOLD}}>SUGAR</span></div>
      </Pop>
    </AbsoluteFill>
  );
};
const PDoor: React.FC<{i: number; mode: 'locked' | 'open' | 'rusty'}> = ({i, mode}) => {
  const {t, active, dur} = useLocal(i);
  if (!active) return null;
  const p = t / dur;
  const key = mode === 'open' ? interpolate(p, [0.05, 0.35], [0, 1], clamp) : mode === 'rusty' ? interpolate(p, [0.3, 0.7], [0, 0.85], clamp) : interpolate(p, [0.65, 0.9], [0, 0.5], clamp);
  const open = mode === 'open' ? interpolate(p, [0.35, 0.5], [0, 1], clamp) : 0;
  const rust = mode === 'rusty' ? interpolate(p, [0.1, 0.5], [0, 1], clamp) : 0;
  const sub = mode === 'open' ? (open > 0.6 ? 'ENERGY ⚡' : '') : mode === 'rusty' ? (rust > 0.5 ? 'RUSTY LOCKS' : '') : 'LOCKED';
  return (
    <Fade t={t} dur={dur}>
      <div style={{position: 'absolute', left: 60, top: mode === 'rusty' ? 400 : 260, ...card, padding: 10}}>
        {mode === 'rusty' && <div style={{fontSize: 34, fontWeight: 900, color: ORANGE, padding: '10px 24px'}}>YEARS LATER…</div>}
        <KeyDoor t={t} open={open} rust={rust} kp={key} label="GLUCOSE" sub={sub} />
      </div>
    </Fade>
  );
};
const PTired: React.FC = () => {
  const {t, active, dur} = useLocal(6);
  if (!active) return null;
  const v = interpolate(t / dur, [0, 0.45, 0.7, 1], [0.35, 1, 1, 0.15], clamp);
  return (
    <Fade t={t} dur={dur}>
      <Panel color={v > 0.5 ? ORANGE : RED}><Kicker c={ORANGE}>PANCREAS · INSULIN OUTPUT</Kicker>
        <div style={{height: 60, borderRadius: 30, background: 'rgba(255,255,255,0.1)', overflow: 'hidden'}}>
          <div style={{width: `${v * 100}%`, height: '100%', background: v > 0.5 ? ORANGE : RED, borderRadius: 30}} /></div>
        <div style={{fontSize: 64, fontWeight: 900, marginTop: 14, color: t / dur > 0.72 ? RED : 'white'}}>{t / dur > 0.72 ? 'TIRED' : 'MORE… AND MORE'}</div>
      </Panel>
    </Fade>
  );
};
const PSigns: React.FC = () => {
  const {t, active, dur} = useLocal(11);
  if (!active) return null;
  const split = Math.round(dur * 0.62);
  const items = ['Always thirsty', 'Peeing often', 'Tired', 'Blurry vision', "Wounds that won't heal"];
  return (
    <Fade t={t} dur={dur}>
      {t < split + 6 ? (
        <Panel color={ORANGE}><Kicker>WATCH FOR</Kicker>
          {items.map((x, n) => {
            const s = spring({frame: t - 8 - n * Math.round(split / 6), fps: FPS, config: {damping: 14}});
            return <div key={x} style={{fontSize: 46, fontWeight: 800, margin: '8px 0', opacity: s, transform: `translateX(${(1 - s) * 60}px)`}}><span style={{color: ORANGE}}>!</span>&nbsp; {x}</div>;
          })}
        </Panel>
      ) : (
        <Panel color={RED}><Kicker c={GOLD}>FASTING SUGAR (mg/dL)</Kicker>
          <Meter v={interpolate(t - split, [0, 25, 60, 90], [80, 95, 95, 140], clamp)} marks={[[100, 'normal below', GREEN], [126, 'diabetes', RED]]} />
        </Panel>
      )}
    </Fade>
  );
};
const PFix: React.FC = () => {
  const {t, active, dur} = useLocal(12);
  if (!active) return null;
  const items = ['Less rice', 'More vegetables & dal', 'Walk after every meal', 'Tablets as the doctor says'];
  const p = t / dur;
  return (
    <Fade t={t} dur={dur}>
      <Panel color={GREEN}><Kicker c={GREEN}>RAJU TAKES CHARGE</Kicker>
        {items.map((x, n) => {
          const s = spring({frame: t - 8 - n * Math.round(dur * 0.13), fps: FPS, config: {damping: 14}});
          return <div key={x} style={{fontSize: 46, fontWeight: 800, margin: '8px 0', opacity: s, transform: `translateX(${(1 - s) * 60}px)`}}><span style={{color: GREEN}}>✓</span>&nbsp; {x}</div>;
        })}
        {p > 0.68 && <Meter v={interpolate(p, [0.68, 0.95], [160, 95], clamp)} marks={[[100, 'normal', GREEN], [126, 'diabetes', RED]]} title="A few months later" />}
      </Panel>
    </Fade>
  );
};
const PEnd: React.FC = () => {
  const {t, active, dur} = useLocal(13);
  if (!active) return null;
  const a1 = Math.round(dur * 0.2), a2 = Math.round(dur * 0.38), a3 = Math.round(dur * 0.66);
  return (
    <AbsoluteFill style={{fontFamily: FONT}}>
      <AbsoluteFill style={{background: `rgba(4,6,12,${interpolate(t, [0, 15], [0, 0.6], clamp)})`}} />
      <Pop at={4} t={t} from="up" style={{position: 'absolute', width: '100%', top: 250, textAlign: 'center'}}>
        <div style={{fontSize: 96, fontWeight: 900, color: GOLD}}>100+ MILLION</div><div style={{fontSize: 40, fontWeight: 700, color: 'white'}}>Indians have diabetes</div>
      </Pop>
      <Pop at={a1} t={t} from="up" style={{position: 'absolute', width: '100%', top: 480, textAlign: 'center'}}>
        <div style={{fontSize: 46, letterSpacing: 4, fontWeight: 800, color: ORANGE}}>DON'T WAIT FOR SYMPTOMS</div>
      </Pop>
      <Pop at={a2} t={t} from="up" style={{position: 'absolute', width: '100%', top: 570, textAlign: 'center'}}>
        <div style={{fontSize: 40, fontWeight: 700, color: 'rgba(255,255,255,0.9)'}}>Above 35, or diabetes in your family?</div>
        <div style={{fontSize: 100, fontWeight: 900, color: 'white', lineHeight: 1.05}}>CHECK YOUR<br />SUGAR</div>
      </Pop>
      <Pop at={a3} t={t} from="up" style={{position: 'absolute', width: '100%', top: 900, textAlign: 'center'}}>
        <div style={{fontSize: 52, fontWeight: 900, color: GREEN}}>Save your eyes, kidneys, life</div>
      </Pop>
      <Credit />
    </AbsoluteFill>
  );
};
const PublicLayers: React.FC = () => (
  <>
    <PIntro />
    <Big i={1} k="INSIDE" title="RICE → GLUCOSE" c={GOLD} sub="soaks into the blood" top={260} />
    <PDoor i={2} mode="locked" />
    <Station i={3} stop="STOP 1" name="PANCREAS" color={CYAN} sub="makes the key: INSULIN" />
    <PDoor i={4} mode="open" />
    <PDoor i={5} mode="rusty" />
    <PTired />
    <Big i={7} k="SUGAR STUCK IN BLOOD" title="TYPE 2 DIABETES" c={RED} />
    <Station i={8} stop="STOP 2" name="EYES" color={ORANGE} sub="tiny vessels damaged" />
    <List i={9} title="STOP 3 · KIDNEYS & FEET" items={['Kidney filters wear out', 'Feet: nerves go numb', 'Small cut → big wound']} c={ORANGE} from={0.05} to={0.75} />
    <List i={10} title="ALSO" items={['Heart attack risk ↑', 'Stroke risk ↑', 'Early on: often NO symptoms']} c={RED} from={0.05} to={0.7} />
    <PSigns />
    <PFix />
    <PEnd />
  </>
);

// =============== STUDENT CUT ===============
const STitle: React.FC = () => {
  const {t, active, dur} = useLocal(0);
  if (!active) return null;
  const chips = ['Absorption', 'Secretion', 'Resistance', 'Complications'];
  return (
    <Fade t={t} dur={dur}>
      <Pop at={4} t={t} from="up" style={{position: 'absolute', width: '100%', top: 250, textAlign: 'center'}}>
        <div style={{fontSize: 34, letterSpacing: 8, color: CYAN, fontWeight: 800}}>DEEP DIVE · TYPE 2 DM</div>
        <div style={{fontSize: 100, fontWeight: 900, color: 'white', lineHeight: 1}}>FOLLOW THE <span style={{color: GOLD}}>SUGAR</span></div>
      </Pop>
      <div style={{position: 'absolute', top: 520, width: '100%', display: 'flex', flexWrap: 'wrap', justifyContent: 'center', gap: 16, padding: '0 60px'}}>
        {chips.map((c, n) => <Pop key={c} at={Math.round(dur * (0.25 + 0.12 * n))} t={t}><div style={{...card, padding: '12px 26px', fontSize: 38, fontWeight: 800, borderColor: CYAN}}>{c}</div></Pop>)}
      </div>
    </Fade>
  );
};
const SAbsorb: React.FC = () => {
  const {t, active, dur} = useLocal(1);
  if (!active) return null;
  const p = t / dur;
  const g = (i: number) => {
    const ph = (t / 50 + i / 5) % 1;
    return {x: 120 + ph * 680, y: 210 + 18 * Math.sin(i * 2 + t / 10)};
  };
  return (
    <Fade t={t} dur={dur}>
      <Panel color={GOLD}><Kicker c={GOLD}>SMALL INTESTINE · ENTEROCYTE</Kicker>
        <svg width={890} height={360} viewBox="0 0 890 360">
          <text x={70} y={40} fill="white" fontSize={26} fontFamily={FONT}>LUMEN</text>
          <text x={780} y={40} fill="white" fontSize={26} fontFamily={FONT} textAnchor="middle">BLOOD</text>
          <rect x={230} y={70} width={420} height={270} rx={40} fill="rgba(255,138,31,0.12)" stroke="rgba(255,255,255,0.4)" strokeWidth={4} />
          <rect x={215} y={160} width={30} height={100} rx={10} fill={p > 0.3 ? CYAN : '#556'} />
          <text x={230} y={300} textAnchor="middle" fill={CYAN} fontSize={30} fontWeight={800} fontFamily={FONT} opacity={p > 0.3 ? 1 : 0.3}>SGLT1</text>
          <text x={230} y={140} textAnchor="middle" fill="white" fontSize={24} fontFamily={FONT} opacity={p > 0.4 ? 1 : 0}>Na⁺ + glucose</text>
          <rect x={635} y={160} width={30} height={100} rx={10} fill={p > 0.65 ? GREEN : '#556'} />
          <text x={650} y={300} textAnchor="middle" fill={GREEN} fontSize={30} fontWeight={800} fontFamily={FONT} opacity={p > 0.65 ? 1 : 0.3}>GLUT2</text>
          {p > 0.3 && [0, 1, 2, 3, 4].map((i) => { const q = g(i); const lim = p > 0.65 ? 860 : 600; return q.x < lim ? <Dot key={i} x={q.x} y={q.y} r={12} /> : null; })}
          <text x={445} y={110} textAnchor="middle" fill="rgba(255,255,255,0.8)" fontSize={24} fontFamily={FONT}>starch → glucose</text>
        </svg>
      </Panel>
    </Fade>
  );
};
const SMeter: React.FC<{i: number; v: number; title: string}> = ({i, v, title}) => {
  const {t, active, dur} = useLocal(i);
  if (!active) return null;
  return (
    <Fade t={t} dur={dur}>
      <Panel color={GREEN}><Kicker c={GREEN}>{title}</Kicker>
        <Meter v={interpolate(t, [0, 30], [60, v], clamp)} marks={[[100, 'normal <100', GREEN], [126, 'diabetes ≥126', RED]]} />
      </Panel>
    </Fade>
  );
};
const BETA = ['Glucose enters via GLUT2', 'Glucokinase (sensor)', 'ATP ↑', 'K-ATP channels close', 'Membrane depolarises', 'Voltage-gated Ca²⁺ opens', 'Ca²⁺ influx', 'Insulin exocytosis'];
const SBeta: React.FC = () => {
  const {t, active, dur, split} = useSpan(3, 4);
  if (!active) return null;
  const lit = t < split ? interpolate(t, [Math.round(split * 0.3), split], [0, 2.4], clamp) : interpolate(t, [split, dur - 20], [2.4, 8], clamp);
  return (
    <Fade t={t} dur={dur}>
      <Panel color={CYAN} top={240}><Kicker c={CYAN}>β-CELL · INSULIN SECRETION</Kicker><Chain steps={BETA} lit={lit} /></Panel>
    </Fade>
  );
};
const INS = ['Insulin receptor (tyrosine kinase)', 'IRS phosphorylated', 'PI3K', 'Akt', 'GLUT4 → membrane', 'Glucose into muscle & fat'];
const SInsulin: React.FC<{i: number; resist?: boolean}> = ({i, resist}) => {
  const {t, active, dur} = useLocal(i);
  if (!active) return null;
  const lit = interpolate(t, [10, dur * 0.8], [0, 6], clamp);
  return (
    <Fade t={t} dur={dur}>
      <Panel color={resist ? RED : CYAN} top={240}><Kicker c={resist ? RED : CYAN}>{resist ? 'INSULIN RESISTANCE · POST-RECEPTOR' : 'INSULIN SIGNALLING'}</Kicker>
        <Chain steps={INS} lit={lit} cols={2} bad={resist ? [2, 3, 4] : []} color={CYAN} />
        {resist && t > dur * 0.7 && <div style={{fontSize: 42, fontWeight: 900, color: RED, marginTop: 16}}>Fewer GLUT4 → glucose stays in blood</div>}
      </Panel>
    </Fade>
  );
};
const SFat: React.FC = () => {
  const {t, active, dur} = useLocal(8);
  if (!active) return null;
  return (
    <Fade t={t} dur={dur}>
      <Panel color={ORANGE}><Kicker>VISCERAL FAT</Kicker>
        <Chain steps={['Free fatty acids ↑', 'Cytokines (TNF-α, IL-6)', 'Insulin resistance ↑']} lit={interpolate(t, [10, dur * 0.5], [0, 3], clamp)} cols={1} color={ORANGE} />
        {t > dur * 0.6 && <div style={{fontSize: 40, fontWeight: 800, marginTop: 16}}><span style={{color: ORANGE}}>Indians:</span> thin-fat phenotype, risk at lower BMI</div>}
      </Panel>
    </Fade>
  );
};
const SFailure: React.FC = () => {
  const {t, active, dur} = useLocal(9);
  if (!active) return null;
  const p = t / dur;
  const W = 820, H = 280;
  const ins = (x: number) => x < 0.45 ? 0.35 + 0.55 * (x / 0.45) : 0.9 - 0.6 * ((x - 0.45) / 0.55);
  const glu = (x: number) => x < 0.45 ? 0.3 + 0.05 * x : 0.32 + 0.6 * ((x - 0.45) / 0.55);
  const path = (fn: (x: number) => number) => Array.from({length: 41}, (_, k) => k / 40).filter((x) => x <= p * 1.15)
    .map((x, k) => `${k ? 'L' : 'M'}${40 + x * W} ${H - fn(x) * (H - 40)}`).join(' ');
  return (
    <Fade t={t} dur={dur}>
      <Panel color={ORANGE}><Kicker>OVER YEARS</Kicker>
        <svg width={890} height={330} viewBox="0 0 890 330">
          <line x1={40} y1={H} x2={870} y2={H} stroke="rgba(255,255,255,0.4)" strokeWidth={3} />
          <path d={path(ins)} stroke={CYAN} strokeWidth={8} fill="none" /><path d={path(glu)} stroke={GOLD} strokeWidth={8} fill="none" />
          <text x={60} y={30} fill={CYAN} fontSize={30} fontWeight={800} fontFamily={FONT}>Insulin</text>
          <text x={240} y={30} fill={GOLD} fontSize={30} fontWeight={800} fontFamily={FONT}>Glucose</text>
          <text x={40 + 0.22 * W} y={H + 36} textAnchor="middle" fill="white" fontSize={24} fontFamily={FONT}>hyperinsulinaemia</text>
          <text x={40 + 0.78 * W} y={H + 36} textAnchor="middle" fill={RED} fontSize={24} fontFamily={FONT}>β-cell exhaustion</text>
        </svg>
      </Panel>
    </Fade>
  );
};
const SRenal: React.FC = () => {
  const {t, active, dur} = useLocal(10);
  if (!active) return null;
  return (
    <Fade t={t} dur={dur}>
      <Panel color={BLUE}><Kicker c={BLUE}>RENAL THRESHOLD</Kicker>
        <Meter v={interpolate(t, [0, dur * 0.35], [120, 220], clamp)} marks={[[180, 'renal threshold', BLUE]]} />
        <Chain steps={['Glucosuria', 'Osmotic diuresis', 'Polyuria', 'Polydipsia']} lit={interpolate(t, [dur * 0.35, dur * 0.85], [0, 4], clamp)} cols={2} color={BLUE} />
      </Panel>
    </Fade>
  );
};
const SPath: React.FC = () => {
  const {t, active, dur} = useLocal(11);
  if (!active) return null;
  const P = [['AGEs', 'advanced glycation end products'], ['POLYOL', 'aldose reductase: glucose → sorbitol'], ['PKC', 'protein kinase C activation']];
  return (
    <Fade t={t} dur={dur}>
      <Panel color={RED}><Kicker c={RED}>CHRONIC HYPERGLYCAEMIA → VESSEL DAMAGE</Kicker>
        {P.map(([a, b], n) => (
          <Pop key={a} at={Math.round(dur * (0.2 + 0.25 * n))} t={t} from="left">
            <div style={{display: 'flex', alignItems: 'center', gap: 18, margin: '12px 0'}}>
              <div style={{fontSize: 46, fontWeight: 900, color: GOLD, minWidth: 220}}>{a}</div><div style={{fontSize: 34, fontWeight: 600}}>{b}</div></div>
          </Pop>
        ))}
      </Panel>
    </Fade>
  );
};
const SComp: React.FC = () => {
  const {t, active, dur} = useLocal(12);
  if (!active) return null;
  const col = (title: string, c: string, items: string[], at: number) => (
    <div style={{flex: 1}}><div style={{fontSize: 36, fontWeight: 900, color: c, marginBottom: 8}}>{title}</div>
      {items.map((x, n) => <Pop key={x} at={Math.round(dur * (at + 0.1 * n))} t={t} from="left"><div style={{fontSize: 38, fontWeight: 800, margin: '8px 0'}}>• {x}</div></Pop>)}</div>
  );
  return (
    <Fade t={t} dur={dur}>
      <Panel color={RED}><div style={{display: 'flex', gap: 30}}>
        {col('MICROVASCULAR', ORANGE, ['Retinopathy', 'Nephropathy', 'Neuropathy'], 0.05)}
        {col('MACROVASCULAR', RED, ['Atherosclerosis', 'MI', 'Stroke'], 0.5)}
      </div></Panel>
    </Fade>
  );
};
const Criteria: React.FC<{rows: [string, string, string][]; title: string; c: string; t: number; dur: number}> = ({rows, title, c, t, dur}) => (
  <Panel color={c}><Kicker c={c}>{title}</Kicker>
    {rows.map(([a, b, d], n) => (
      <Pop key={a} at={Math.round(dur * (0.06 + 0.16 * n))} t={t} from="left">
        <div style={{display: 'flex', justifyContent: 'space-between', alignItems: 'baseline', borderBottom: '1px solid rgba(255,255,255,0.12)', padding: '10px 0'}}>
          <div style={{fontSize: 36, fontWeight: 700}}>{a}</div><div style={{fontSize: 46, fontWeight: 900, color: c}}>{b}<span style={{fontSize: 24, color: 'rgba(255,255,255,0.7)'}}> {d}</span></div></div>
      </Pop>
    ))}
  </Panel>
);
const SDiag: React.FC = () => {
  const {t, active, dur} = useLocal(13);
  if (!active) return null;
  return (
    <Fade t={t} dur={dur}>
      <Criteria t={t} dur={dur} c={RED} title="DIAGNOSIS (any one, confirm)" rows={[['Fasting plasma glucose', '≥126', 'mg/dL'], ['HbA1c', '≥6.5', '%'], ['2-h OGTT (75 g)', '≥200', 'mg/dL'], ['Random + symptoms', '≥200', 'mg/dL']]} />
      {t > dur * 0.72 && <div style={{position: 'absolute', top: 900, width: '100%', textAlign: 'center'}}><div style={{...card, display: 'inline-block', padding: '14px 28px', fontSize: 36, fontWeight: 800}}>HbA1c ≈ 3 months <span style={{color: GOLD}}>(RBC life ~120 days)</span></div></div>}
    </Fade>
  );
};
const SPre: React.FC = () => {
  const {t, active, dur} = useLocal(14);
  if (!active) return null;
  return <Fade t={t} dur={dur}><Criteria t={t} dur={dur} c={ORANGE} title="PREDIABETES" rows={[['Fasting plasma glucose', '100–125', 'mg/dL'], ['HbA1c', '5.7–6.4', '%'], ['2-h OGTT', '140–199', 'mg/dL']]} /></Fade>;
};
const SMgmt: React.FC = () => {
  const {t, active, dur} = useLocal(15);
  if (!active) return null;
  return (
    <Fade t={t} dur={dur}>
      <Panel color={GREEN}><Kicker c={GREEN}>MANAGEMENT</Kicker>
        <Chain steps={['Lifestyle: diet, activity, weight', 'Metformin: usual first drug', 'CVD / CKD / HF → SGLT2i or GLP-1 RA']} lit={interpolate(t, [8, dur * 0.65], [0, 3], clamp)} cols={1} color={GREEN} />
      </Panel>
      {t > dur * 0.78 && <Pop at={Math.round(dur * 0.78)} t={t} from="up" style={{position: 'absolute', width: '100%', top: 860, textAlign: 'center'}}>
        <div style={{fontSize: 34, letterSpacing: 6, color: CYAN, fontWeight: 800}}>NEXT EPISODE</div><div style={{fontSize: 80, fontWeight: 900}}>METFORMIN, decoded</div></Pop>}
    </Fade>
  );
};
export const HighYield: React.FC<{scale?: number}> = ({scale = 1}) => {
  const rows: [string, string][] = [
    ['DEFECT', 'Insulin resistance (post-receptor PI3K–Akt) + progressive β-cell failure'],
    ['SECRETION', 'Glucose → GLUT2 → glucokinase → ATP↑ → K-ATP closes → depolarisation → Ca²⁺ in → insulin out'],
    ['ACTION', 'GLUT4 translocation (muscle, fat); ↓ hepatic glucose output'],
    ['RENAL THRESHOLD', '~180 mg/dL → glucosuria, osmotic diuresis'],
    ['DAMAGE', 'AGEs · polyol (aldose reductase → sorbitol) · PKC'],
    ['DIAGNOSIS', 'FPG ≥126 · HbA1c ≥6.5% · OGTT 2-h ≥200 · random ≥200 + symptoms'],
    ['MNEMONIC', 'Go And Keep Calcium In: Glucose, ATP, K⁺ shut, Ca²⁺, Insulin'],
  ];
  return (
    <div style={{...card, width: 980, padding: '30px 34px', borderColor: GOLD, transform: `scale(${scale})`, transformOrigin: 'top center'}}>
      <div style={{fontSize: 30, letterSpacing: 6, fontWeight: 800, color: GOLD}}>HIGH-YIELD · SCREENSHOT THIS</div>
      <div style={{fontSize: 56, fontWeight: 900, marginBottom: 10}}>Type 2 Diabetes</div>
      {rows.map(([a, b]) => (
        <div key={a} style={{display: 'flex', gap: 18, padding: '10px 0', borderTop: '1px solid rgba(255,255,255,0.12)'}}>
          <div style={{minWidth: 230, fontSize: 26, fontWeight: 800, color: CYAN, letterSpacing: 1}}>{a}</div>
          <div style={{fontSize: 30, fontWeight: 600, lineHeight: 1.25}}>{b}</div></div>
      ))}
    </div>
  );
};
const STail: React.FC = () => {
  const T = useT(); const f = useCurrentFrame();
  const end = Math.round((T.starts[T.starts.length - 1] + T.durs[T.durs.length - 1]) * FPS);
  if (f < end) return null;
  const t = f - end;
  return (
    <AbsoluteFill style={{background: `rgba(4,6,12,${interpolate(t, [0, 10], [0, 0.82], clamp)})`, fontFamily: FONT}}>
      <Pop at={2} t={t} from="up" style={{position: 'absolute', left: 50, top: 220}}><HighYield /></Pop>
      <Credit />
    </AbsoluteFill>
  );
};
const StudentLayers: React.FC = () => (
  <>
    <STitle /><SAbsorb /><SMeter i={2} v={88} title="NORMAL FASTING PLASMA GLUCOSE" /><SBeta />
    <SInsulin i={5} /><Big i={6} k="LIVER" title="↓ Gluconeogenesis ↓ Glycogenolysis" c={GREEN} sub="second way insulin lowers sugar" top={260} />
    <SInsulin i={7} resist /><SFat /><SFailure /><SRenal /><SPath /><SComp /><SDiag /><SPre /><SMgmt /><STail />
  </>
);

export const Main: React.FC<{cut: 'public' | 'student'; bg: string; audio: string; preview: boolean}> = ({cut, bg, audio, preview}) => (
  <Ctx.Provider value={TIMINGS[cut]}>
    <AbsoluteFill style={{background: '#0b1020'}}>
      {preview ? <AbsoluteFill style={{background: 'linear-gradient(#26304a, #0b1020)'}} /> : <OffthreadVideo src={staticFile(bg)} muted />}
      {!preview && <Audio src={staticFile(audio)} />}
      <Dips />
      {cut === 'public' ? <PublicLayers /> : <StudentLayers />}
      <Captions />
    </AbsoluteFill>
  </Ctx.Provider>
);
