import React from 'react';
import {AbsoluteFill, Audio, OffthreadVideo, interpolate, spring, staticFile, useCurrentFrame, useVideoConfig, Easing} from 'remotion';
import timing from './timing.json';

const FONT = 'Poppins, "DejaVu Sans", Arial, sans-serif';

const FPS = 30;
const ORANGE = '#FF8A1F';
const RED = '#FF3B30';
const GREEN = '#33D17A';
const BLUE = '#4DA3FF';
const L = (i: number) => ({from: Math.round(timing.starts[i] * FPS), dur: Math.round(timing.durs[i] * FPS)});
const clamp = {extrapolateLeft: 'clamp' as const, extrapolateRight: 'clamp' as const};
const ease = Easing.bezier(0.16, 1, 0.3, 1);

const card: React.CSSProperties = {
  background: 'rgba(8, 12, 22, 0.74)', borderRadius: 30, border: '2px solid rgba(255,255,255,0.14)',
  backdropFilter: 'blur(10px)', boxShadow: '0 20px 60px rgba(0,0,0,0.45)', color: 'white', fontFamily: FONT,
};

// ---------- helpers ----------
const useLocal = (i: number) => {
  const f = useCurrentFrame();
  const {from, dur} = L(i);
  return {t: f - from, dur, active: f >= from && f < from + dur};
};
const Pop: React.FC<{at: number; t: number; children: React.ReactNode; style?: React.CSSProperties; from?: 'left' | 'up' | 'scale'}> = ({at, t, children, style, from = 'scale'}) => {
  const {fps} = useVideoConfig();
  const s = spring({frame: t - at, fps, config: {damping: 14, stiffness: 160}});
  const tf = from === 'left' ? `translateX(${(1 - s) * -700}px)` : from === 'up' ? `translateY(${(1 - s) * 80}px)` : `scale(${0.6 + 0.4 * s})`;
  return <div style={{...style, opacity: interpolate(t - at, [0, 6], [0, 1], clamp), transform: tf}}>{children}</div>;
};

// ---------- captions ----------
type Chunk = {words: string[]; s: number; e: number};
const chunks = (i: number): Chunk[] => {
  const words = timing.lines[i].text.split(' ');
  const w = words.map((x) => Math.max(x.replace(/[?.!,]/g, '').length, 2));
  const total = w.reduce((a, b) => a + b, 0);
  const d = timing.durs[i] - 0.35;
  const out: Chunk[] = [];
  let cur: string[] = []; let cw = 0; let tcur = timing.starts[i];
  words.forEach((wd, k) => {
    cur.push(wd); cw += w[k];
    const len = cur.join('').length;
    if (cur.length === 3 || len >= 13 || /[?.!,]$/.test(wd) || k === words.length - 1) {
      const e = tcur + (d * cw) / total;
      out.push({words: cur, s: tcur, e}); tcur = e; cur = []; cw = 0;
    }
  });
  return out;
};
const ALL = timing.lines.map((_, i) => chunks(i));
const Captions: React.FC = () => {
  const f = useCurrentFrame();
  const sec = f / FPS;
  for (let i = 0; i < ALL.length; i++) {
    for (const c of ALL[i]) {
      if (sec >= c.s && sec < c.e + (c === ALL[i][ALL[i].length - 1] ? 0.3 : 0)) {
        const k = timing.lines[i].keywords.map((x) => x.toLowerCase().replace(/[?.!,]/g, ''));
        const t = f - c.s * FPS;
        const sc = interpolate(t, [0, 4], [0.82, 1], {...clamp, easing: ease});
        return (
          <div style={{position: 'absolute', top: 1180, width: '100%', textAlign: 'center', fontFamily: FONT, fontWeight: 900, fontSize: 96,
            lineHeight: 1.08, color: 'white', transform: `scale(${sc})`, padding: '0 70px',
            textShadow: '0 6px 0 rgba(0,0,0,0.55), 0 0 26px rgba(0,0,0,0.6)', WebkitTextStroke: '3px rgba(0,0,0,0.85)', paintOrder: 'stroke fill'}}>
            {c.words.map((wd, n) => (
              <span key={n} style={{color: k.includes(wd.toLowerCase().replace(/[?.!,]/g, '')) ? ORANGE : 'white'}}>{wd}{n < c.words.length - 1 ? ' ' : ''}</span>
            ))}
          </div>
        );
      }
    }
  }
  return null;
};

// ---------- flash transitions ----------
const Flash: React.FC = () => {
  const f = useCurrentFrame();
  const cuts = [L(1).from, L(7).from];
  let o = 0;
  for (const c of cuts) o = Math.max(o, interpolate(f - c, [-3, 0, 10], [0, 1, 0], clamp));
  return <AbsoluteFill style={{background: 'white', opacity: o}} />;
};

// ---------- line 0: intro ----------
const Intro: React.FC = () => {
  const {t, active, dur} = useLocal(0);
  if (!active) return null;
  const chips = ['Pickle', 'Papad', 'Chips'];
  return (
    <AbsoluteFill>
      <Pop at={6} t={t} from="left" style={{position: 'absolute', left: 70, top: 300}}>
        <div style={{...card, padding: '26px 40px'}}>
          <div style={{fontSize: 30, letterSpacing: 6, color: ORANGE, fontWeight: 700}}>MEET</div>
          <div style={{fontSize: 74, fontWeight: 900, lineHeight: 1}}>Raju garu</div>
          <div style={{fontSize: 34, opacity: 0.85, marginTop: 6}}>68 · loves extra salt</div>
        </div>
      </Pop>
      <div style={{position: 'absolute', left: 70, top: 560, display: 'flex', gap: 18}}>
        {chips.map((c, n) => (
          <Pop key={c} at={50 + n * 14} t={t}>
            <div style={{...card, padding: '14px 28px', fontSize: 40, fontWeight: 800, borderColor: ORANGE}}>+ {c}</div>
          </Pop>
        ))}
      </div>
      <Pop at={dur - 55} t={t} style={{position: 'absolute', width: '100%', top: 760, textAlign: 'center'}}>
        <div style={{fontFamily: FONT, fontWeight: 900, fontSize: 104, color: 'white', textShadow: '0 8px 30px rgba(0,0,0,0.6)'}}>
          FOLLOW THE <span style={{color: ORANGE}}>SALT</span>
        </div>
      </Pop>
    </AbsoluteFill>
  );
};

// ---------- journey HUD (lines 1-6) ----------
const Journey: React.FC = () => {
  const f = useCurrentFrame();
  const a = L(1).from, b = L(6).from + L(6).dur;
  if (f < a || f >= b) return null;
  const k = [L(1).from, L(3).from, L(4).from, L(5).from, L(6).from, b].map((x) => x);
  const prog = interpolate(f, [k[0], k[1], k[1] + 20, k[2], k[2] + 20, k[4], k[4] + 20, k[5]], [0, 0.0, 0.0, 0.5, 0.5, 0.5, 1.0, 1.0], clamp);
  const p2 = f < k[1] ? interpolate(f, [k[0], k[1]], [-0.12, 0], clamp) : prog;
  const fadeIn = interpolate(f - a, [0, 15], [0, 1], clamp);
  const nodes = ['HEART', 'KIDNEYS', 'BRAIN'];
  const W = 820, x0 = 130;
  // pressure gauge 0..1
  const beat = Math.max(0, Math.sin((f / FPS) * Math.PI * 2 * 1.2)) ** 3;
  const base = interpolate(f, [L(1).from, L(2).from + L(2).dur, L(5).from, L(5).from + L(5).dur], [0.3, 0.86, 0.86, 0.94], clamp);
  const pr = Math.min(1, base + 0.05 * beat);
  const ang = -90 + 180 * pr;
  const gcol = pr > 0.75 ? RED : pr > 0.5 ? ORANGE : GREEN;
  return (
    <AbsoluteFill style={{opacity: fadeIn, fontFamily: FONT}}>
      <div style={{position: 'absolute', left: 50, top: 70, width: 980, height: 150, ...card, borderRadius: 40}} />
      <div style={{position: 'absolute', left: x0, top: 132, width: W, height: 8, background: 'rgba(255,255,255,0.18)', borderRadius: 4}} />
      <div style={{position: 'absolute', left: x0, top: 132, width: W * Math.max(0, p2), height: 8, background: ORANGE, borderRadius: 4}} />
      {nodes.map((n, i) => {
        const pos = i / 2;
        const reached = p2 >= pos - 0.001;
        return (
          <div key={n} style={{position: 'absolute', left: x0 + W * pos - 26, top: 110}}>
            <div style={{width: 52, height: 52, borderRadius: 26, background: reached ? ORANGE : 'rgba(255,255,255,0.15)', border: '4px solid white',
              boxShadow: reached ? `0 0 26px ${ORANGE}` : 'none'}} />
            <div style={{position: 'absolute', top: 60, left: -60, width: 172, textAlign: 'center', color: 'white', fontWeight: 800, fontSize: 26, letterSpacing: 2}}>{n}</div>
          </div>
        );
      })}
      <div style={{position: 'absolute', left: x0 + W * Math.max(0, p2) - 18, top: 118, width: 36, height: 36, borderRadius: 18, background: 'white',
        boxShadow: '0 0 20px white', opacity: p2 < 0 ? 0 : 1}} />
      {/* gauge */}
      <div style={{position: 'absolute', right: 50, top: 250, width: 280, height: 196, ...card, borderRadius: 28}}>
        <svg width={280} height={160} style={{position: 'absolute', top: 34}}>
          <path d="M 40 140 A 100 100 0 0 1 240 140" stroke="rgba(255,255,255,0.18)" strokeWidth={22} fill="none" strokeLinecap="round" />
          <path d="M 40 140 A 100 100 0 0 1 240 140" stroke={gcol} strokeWidth={22} fill="none" strokeLinecap="round"
            strokeDasharray={`${Math.PI * 100 * pr} 999`} />
          <g transform={`rotate(${ang} 140 140)`}><line x1={140} y1={140} x2={140} y2={58} stroke="white" strokeWidth={8} strokeLinecap="round" /></g>
          <circle cx={140} cy={140} r={12} fill="white" />
        </svg>
        <div style={{position: 'absolute', top: 10, width: '100%', textAlign: 'center', color: 'white', fontWeight: 800, fontSize: 24, letterSpacing: 4}}>PRESSURE</div>
      </div>
    </AbsoluteFill>
  );
};

const Station: React.FC<{i: number; stop: string; name: string; color: string; sub: string}> = ({i, stop, name, color, sub}) => {
  const {t, active, dur} = useLocal(i);
  if (!active) return null;
  const out = interpolate(t, [dur - 10, dur], [1, 0], clamp);
  return (
    <Pop at={4} t={t} from="left" style={{position: 'absolute', left: 50, top: 260, opacity: out}}>
      <div style={{...card, padding: '22px 36px', borderLeft: `12px solid ${color}`}}>
        <div style={{fontSize: 30, fontWeight: 700, letterSpacing: 6, color}}>{stop}</div>
        <div style={{fontSize: 82, fontWeight: 900, lineHeight: 1}}>{name}</div>
        <div style={{fontSize: 32, opacity: 0.85, marginTop: 6}}>{sub}</div>
      </div>
    </Pop>
  );
};

const SaltWater: React.FC = () => {
  const {t, active} = useLocal(1);
  if (!active) return null;
  return (
    <Pop at={45} t={t} from="left" style={{position: 'absolute', left: 50, top: 260}}>
      <div style={{...card, padding: '22px 34px', display: 'flex', alignItems: 'center', gap: 22, fontSize: 52, fontWeight: 900}}>
        <span>SALT</span><span style={{color: ORANGE}}>+</span><span style={{color: BLUE}}>WATER</span>
      </div>
    </Pop>
  );
};
const Push: React.FC = () => {
  const {t, active} = useLocal(2);
  if (!active) return null;
  const s = 1 + 0.06 * Math.max(0, Math.sin((t / FPS) * Math.PI * 2 * 1.2)) ** 3;
  return (
    <Pop at={20} t={t} from="left" style={{position: 'absolute', left: 50, top: 260}}>
      <div style={{...card, padding: '22px 34px', fontSize: 50, fontWeight: 900, transform: `scale(${s})`}}>
        MORE WATER = <span style={{color: RED}}>MORE PUSH</span>
      </div>
    </Pop>
  );
};
const Years: React.FC = () => {
  const {t, active, dur} = useLocal(5);
  if (!active) return null;
  const y = Math.round(interpolate(t, [10, dur - 20], [1, 10], clamp));
  return (
    <Pop at={4} t={t} from="left" style={{position: 'absolute', left: 50, top: 260}}>
      <div style={{...card, padding: '22px 36px', width: 470}}>
        <div style={{fontSize: 30, fontWeight: 700, letterSpacing: 6, color: ORANGE}}>YEAR AFTER YEAR</div>
        <div style={{fontSize: 92, fontWeight: 900, lineHeight: 1}}>YEAR {y}</div>
        <div style={{height: 12, background: 'rgba(255,255,255,0.15)', borderRadius: 6, marginTop: 14}}>
          <div style={{height: 12, width: `${y * 10}%`, background: ORANGE, borderRadius: 6}} />
        </div>
        <div style={{fontSize: 30, marginTop: 10, opacity: 0.85}}>tubes turn hard & narrow</div>
      </div>
    </Pop>
  );
};
const Stroke: React.FC = () => {
  const {t, active, dur} = useLocal(6);
  if (!active) return null;
  const at = Math.round(dur * 0.45);
  if (t < at) return null;
  const pulse = 0.5 + 0.5 * Math.sin(((t - at) / FPS) * Math.PI * 4);
  return (
    <AbsoluteFill>
      <AbsoluteFill style={{boxShadow: `inset 0 0 ${180 + 80 * pulse}px rgba(255,30,20,${0.55 + 0.25 * pulse})`}} />
      <Pop at={at} t={t} style={{position: 'absolute', right: 50, top: 470}}>
        <div style={{...card, background: RED, borderColor: 'white', padding: '14px 34px', fontSize: 64, fontWeight: 900, letterSpacing: 6}}>STROKE</div>
      </Pop>
    </AbsoluteFill>
  );
};

// ---------- line 7: silent killer ----------
const Silent: React.FC = () => {
  const {t, active, dur} = useLocal(7);
  if (!active) return null;
  const txt = 'No pain. No warning.';
  const n = Math.floor(interpolate(t, [Math.round(dur * 0.25), Math.round(dur * 0.55)], [0, txt.length], clamp));
  const stampAt = Math.round(dur * 0.66);
  const s = spring({frame: t - stampAt, fps: FPS, config: {damping: 9, stiffness: 200}});
  return (
    <AbsoluteFill style={{fontFamily: FONT}}>
      <div style={{position: 'absolute', left: 70, top: 300, fontSize: 70, fontWeight: 800, color: 'white', textShadow: '0 6px 24px rgba(0,0,0,0.7)'}}>
        {txt.slice(0, n)}<span style={{opacity: n < txt.length && t % 20 < 10 ? 1 : 0}}>|</span>
      </div>
      {t >= stampAt && (
        <div style={{position: 'absolute', left: 90, top: 440, transform: `rotate(-7deg) scale(${2.2 - 1.2 * s})`, opacity: Math.min(1, s * 1.5),
          border: `8px solid ${RED}`, borderRadius: 18, padding: '10px 30px', color: RED, fontWeight: 900, fontSize: 84, letterSpacing: 4,
          background: 'rgba(255,255,255,0.88)'}}>THE SILENT KILLER</div>
      )}
    </AbsoluteFill>
  );
};

// ---------- BP readout (lines 8 and 11) ----------
const BP: React.FC<{i: number; fromV: [number, number]; toV: [number, number]; label: string; color: string; note: string}> = ({i, fromV, toV, label, color, note}) => {
  const {t, active, dur} = useLocal(i);
  if (!active) return null;
  const k = interpolate(t, [8, Math.min(dur - 10, 60)], [0, 1], {...clamp, easing: ease});
  const sys = Math.round(fromV[0] + (toV[0] - fromV[0]) * k), dia = Math.round(fromV[1] + (toV[1] - fromV[1]) * k);
  return (
    <Pop at={2} t={t} from="up" style={{position: 'absolute', left: 140, top: 260}}>
      <div style={{...card, width: 800, padding: '30px 40px', textAlign: 'center'}}>
        <div style={{fontSize: 30, letterSpacing: 6, fontWeight: 700, opacity: 0.8}}>BLOOD PRESSURE</div>
        <div style={{fontSize: 170, fontWeight: 900, lineHeight: 1.05, color}}>{sys}<span style={{color: 'white', opacity: 0.6}}>/</span>{dia}</div>
        <div style={{display: 'inline-block', marginTop: 8, background: color, color: '#081018', fontWeight: 900, fontSize: 46, padding: '6px 30px', borderRadius: 40,
          opacity: k > 0.95 ? 1 : 0}}>{label}</div>
        <div style={{fontSize: 28, opacity: 0.75, marginTop: 14}}>{note}</div>
      </div>
    </Pop>
  );
};

// ---------- lines 9-10: checklist ----------
const ITEMS: [number, number, string][] = [
  [9, 0.2, 'Less salt: max 1 tsp a day'], [9, 0.68, 'More fruits & vegetables'],
  [10, 0.05, 'Walk every day'], [10, 0.3, 'No smoking, no alcohol'], [10, 0.62, 'Tablets as the doctor says'],
];
const Checklist: React.FC = () => {
  const f = useCurrentFrame();
  const a = L(9).from, b = L(10).from + L(10).dur;
  if (f < a || f >= b) return null;
  return (
    <AbsoluteFill style={{fontFamily: FONT}}>
      <div style={{position: 'absolute', left: 60, top: 240, width: 960, ...card, padding: '26px 36px'}}>
        <div style={{fontSize: 30, letterSpacing: 6, fontWeight: 700, color: GREEN, marginBottom: 10}}>RAJU GARU'S NEW HABITS</div>
        {ITEMS.map(([li, x, txt], n) => {
          const at = L(li).from + Math.round(L(li).dur * x);
          const s = spring({frame: f - at, fps: FPS, config: {damping: 14}});
          if (f < at) return null;
          return (
            <div key={n} style={{display: 'flex', alignItems: 'center', gap: 22, fontSize: 46, fontWeight: 800, margin: '10px 0', opacity: s,
              transform: `translateX(${(1 - s) * 60}px)`}}>
              <div style={{width: 54, height: 54, borderRadius: 27, background: GREEN, display: 'flex', alignItems: 'center', justifyContent: 'center',
                transform: `scale(${s})`}}>
                <svg width={34} height={34} viewBox="0 0 24 24"><path d="M4 12.5l5 5L20 6.5" stroke="#081018" strokeWidth={3.6} fill="none" strokeLinecap="round" strokeLinejoin="round" /></svg>
              </div>
              {txt}
            </div>
          );
        })}
      </div>
    </AbsoluteFill>
  );
};

// ---------- line 12: end card ----------
const End: React.FC = () => {
  const {t, active} = useLocal(12);
  if (!active) return null;
  const dim = interpolate(t, [0, 20], [0, 0.55], clamp);
  return (
    <AbsoluteFill style={{fontFamily: FONT}}>
      <AbsoluteFill style={{background: `rgba(4,6,12,${dim})`}} />
      <Pop at={6} t={t} from="up" style={{position: 'absolute', width: '100%', top: 360, textAlign: 'center'}}>
        <div style={{fontSize: 108, fontWeight: 900, color: 'white', lineHeight: 1.05}}>SILENT<br />PROBLEM.</div>
      </Pop>
      <Pop at={30} t={t} from="up" style={{position: 'absolute', width: '100%', top: 620, textAlign: 'center'}}>
        <div style={{fontSize: 108, fontWeight: 900, color: GREEN, lineHeight: 1.05}}>SIMPLE<br />CHECK.</div>
      </Pop>
      <Pop at={60} t={t} style={{position: 'absolute', width: '100%', top: 900, textAlign: 'center'}}>
        <div style={{display: 'inline-block', ...card, padding: '16px 36px', fontSize: 42, fontWeight: 800}}>Check your BP regularly</div>
      </Pop>
      <div style={{position: 'absolute', bottom: 70, width: '100%', textAlign: 'center', color: 'rgba(255,255,255,0.7)', fontSize: 22, padding: '0 60px'}}>
        3D anatomy: Z-Anatomy (CC BY-SA 4.0), based on BodyParts3D © DBCLS (CC BY-SA 2.1 JP). General awareness, not medical advice.
      </div>
    </AbsoluteFill>
  );
};

export const Main: React.FC<{bg: string; audio: string; preview: boolean}> = ({bg, audio, preview}) => {
  return (
    <AbsoluteFill style={{background: '#0b1020'}}>
      {preview ? <AbsoluteFill style={{background: 'linear-gradient(#26304a, #0b1020)'}} /> : <OffthreadVideo src={staticFile(bg)} muted />}
      {!preview && <Audio src={staticFile(audio)} />}
      <Intro />
      <Journey />
      <SaltWater />
      <Push />
      <Station i={3} stop="STOP 1" name="HEART" color={RED} sub="pumps harder, every beat" />
      <Station i={4} stop="STOP 2" name="KIDNEYS" color={BLUE} sub="can't keep up with the salt" />
      <Years />
      <Station i={6} stop="STOP 3" name="BRAIN" color={ORANGE} sub="weak, narrow tubes" />
      <Stroke />
      <Silent />
      <BP i={8} fromV={[0, 0]} toV={[150, 95]} label="TOO HIGH" color={RED} note="Normal: below 120/80" />
      <Checklist />
      <BP i={11} fromV={[150, 95]} toV={[120, 80]} label="MUCH BETTER" color={GREEN} note="A few months later" />
      <End />
      <Captions />
      <Flash />
    </AbsoluteFill>
  );
};
