import React from 'react';
import {AbsoluteFill, Img, staticFile} from 'remotion';
import {FONT, ORANGE, RED, GREEN, BLUE, GOLD, CYAN, card, HighYield} from './Main';

const Frame: React.FC<{n: number; total: number; deck: string; img?: string; children: React.ReactNode}> = ({n, total, deck, img, children}) => (
  <AbsoluteFill style={{background: 'linear-gradient(160deg, #0d1426, #05070e)', fontFamily: FONT, color: 'white'}}>
    {img && <Img src={staticFile(img)} style={{position: 'absolute', width: '100%', height: '100%', objectFit: 'cover', opacity: 0.38}} />}
    <AbsoluteFill style={{padding: '70px 64px'}}>{children}</AbsoluteFill>
    <div style={{position: 'absolute', bottom: 34, left: 64, right: 64, display: 'flex', justifyContent: 'space-between', fontSize: 24, opacity: 0.75}}>
      <span>{deck}</span><span>{n} / {total}</span></div>
  </AbsoluteFill>
);
const H: React.FC<{k: string; c?: string; children: React.ReactNode}> = ({k, c = ORANGE, children}) => (
  <div style={{marginBottom: 26}}><div style={{fontSize: 30, letterSpacing: 6, fontWeight: 800, color: c}}>{k}</div>
    <div style={{fontSize: 68, fontWeight: 900, lineHeight: 1.05}}>{children}</div></div>
);
const Row: React.FC<{a: string; b: string; c?: string}> = ({a, b, c = CYAN}) => (
  <div style={{display: 'flex', gap: 22, padding: '16px 0', borderTop: '1px solid rgba(255,255,255,0.14)'}}>
    <div style={{minWidth: 300, fontSize: 32, fontWeight: 800, color: c}}>{a}</div><div style={{fontSize: 34, lineHeight: 1.3}}>{b}</div></div>
);
const Steps: React.FC<{items: string[]; c?: string}> = ({items, c = CYAN}) => (
  <div>{items.map((x, i) => (
    <div key={x} style={{display: 'flex', gap: 18, alignItems: 'center', margin: '12px 0'}}>
      <div style={{width: 56, height: 56, borderRadius: 28, background: c, color: '#081018', fontWeight: 900, fontSize: 30, display: 'flex', alignItems: 'center', justifyContent: 'center'}}>{i + 1}</div>
      <div style={{fontSize: 38, fontWeight: 700}}>{x}</div></div>))}</div>
);
const Box: React.FC<{c?: string; children: React.ReactNode}> = ({c = 'rgba(255,255,255,0.14)', children}) => (
  <div style={{...card, padding: '24px 30px', borderColor: c, marginTop: 20}}>{children}</div>
);
const MCQ: React.FC<{q: string; o: string[]; a: number; why: string; n: number}> = ({q, o, a, why, n}) => (
  <div style={{marginBottom: 22}}>
    <div style={{fontSize: 30, fontWeight: 800}}>Q{n}. {q}</div>
    <div style={{fontSize: 27, margin: '6px 0'}}>{o.map((x, i) => <span key={x} style={{marginRight: 22, color: i === a ? GREEN : 'rgba(255,255,255,0.85)', fontWeight: i === a ? 900 : 500}}>{'abcd'[i]}) {x}</span>)}</div>
    <div style={{fontSize: 24, opacity: 0.8}}>✓ {why}</div></div>
);

const STU = 'Follow the Sugar | Deep Dive';
const PUB = 'Follow the Sugar';
export const STUDENT_SLIDES: React.FC[] = [
  () => <Frame n={1} total={10} deck={STU} img="stills/pancreas.jpg">
    <div style={{marginTop: 300}}><div style={{fontSize: 34, letterSpacing: 8, color: CYAN, fontWeight: 800}}>DEEP DIVE · TYPE 2 DM</div>
      <div style={{fontSize: 120, fontWeight: 900, lineHeight: 1}}>FOLLOW THE <span style={{color: GOLD}}>SUGAR</span></div>
      <div style={{fontSize: 40, marginTop: 20, opacity: 0.9}}>Absorption · Secretion · Resistance · Complications · Diagnosis</div>
      <div style={{fontSize: 34, marginTop: 40, color: GOLD, fontWeight: 800}}>Swipe → save for exams</div></div></Frame>,
  () => <Frame n={2} total={10} deck={STU} img="stills/gut.jpg"><H k="1 · ABSORPTION" c={GOLD}>Starch → glucose → blood</H>
    <Row a="Apical (lumen)" b="SGLT1: Na⁺–glucose co-transport (secondary active)" /><Row a="Basolateral" b="GLUT2: facilitated diffusion into blood" />
    <Row a="Route" b="Portal vein → liver → systemic circulation" /><Box c={GREEN}><div style={{fontSize: 34}}>Normal fasting plasma glucose: <b style={{color: GREEN}}>&lt;100 mg/dL</b></div></Box></Frame>,
  () => <Frame n={3} total={10} deck={STU} img="stills/pancreas.jpg"><H k="2 · β-CELL SECRETION" c={CYAN}>How insulin is released</H>
    <Steps items={['Glucose enters via GLUT2', 'Glucokinase phosphorylates (glucose sensor)', 'ATP/ADP ratio ↑', 'K-ATP channels close', 'Membrane depolarises', 'Voltage-gated Ca²⁺ channels open', 'Ca²⁺ influx → insulin exocytosis']} />
    <Box c={GOLD}><div style={{fontSize: 32}}><b style={{color: GOLD}}>Mnemonic:</b> Go And Keep Calcium In<br />Glucose · ATP · K⁺ shut · Ca²⁺ · Insulin</div></Box></Frame>,
  () => <Frame n={4} total={10} deck={STU} img="stills/muscle.jpg"><H k="3 · INSULIN ACTION" c={CYAN}>Receptor to GLUT4</H>
    <Steps items={['Insulin receptor (tyrosine kinase) autophosphorylates', 'IRS proteins phosphorylated', 'PI3K → Akt', 'GLUT4 vesicles fuse with membrane', 'Glucose uptake: skeletal muscle & adipose']} />
    <Box c={GREEN}><div style={{fontSize: 32}}><b style={{color: GREEN}}>Liver:</b> ↓ gluconeogenesis, ↓ glycogenolysis, ↑ glycogen synthesis</div></Box></Frame>,
  () => <Frame n={5} total={10} deck={STU} img="stills/fat.jpg"><H k="4 · PATHOPHYSIOLOGY" c={RED}>Type 2 DM in two hits</H>
    <Row a="Insulin resistance" b="Post-receptor defect: weak PI3K–Akt → fewer GLUT4 at surface" c={RED} />
    <Row a="Visceral fat" b="FFAs + cytokines (TNF-α, IL-6) worsen resistance" c={ORANGE} />
    <Row a="Compensation" b="Hyperinsulinaemia keeps glucose normal for years" c={CYAN} />
    <Row a="β-cell failure" b="Glucotoxicity + lipotoxicity → relative insulin deficiency → hyperglycaemia" c={RED} />
    <Box c={ORANGE}><div style={{fontSize: 30}}>Indians: <b>thin-fat phenotype</b>, risk at lower BMI</div></Box></Frame>,
  () => <Frame n={6} total={10} deck={STU} img="stills/kidney.jpg"><H k="5 · KIDNEY & SYMPTOMS" c={BLUE}>Why the 3 P's</H>
    <Row a="Renal threshold" b="~180 mg/dL: PCT glucose transporters (SGLT2, SGLT1) saturate → glucosuria" c={BLUE} />
    <Row a="Polyuria" b="Osmotic diuresis: glucose drags water" c={BLUE} />
    <Row a="Polydipsia" b="Water loss → thirst" c={BLUE} />
    <Row a="Polyphagia" b="Cells starved of glucose despite high blood levels" c={BLUE} /></Frame>,
  () => <Frame n={7} total={10} deck={STU} img="stills/eye.jpg"><H k="6 · COMPLICATIONS" c={RED}>How sugar damages vessels</H>
    <Row a="AGEs" b="Advanced glycation end products cross-link proteins" c={GOLD} />
    <Row a="Polyol" b="Aldose reductase: glucose → sorbitol (osmotic damage; nerves, lens)" c={GOLD} />
    <Row a="PKC" b="Protein kinase C activation → vascular dysfunction" c={GOLD} />
    <Box c={RED}><div style={{fontSize: 32}}><b style={{color: ORANGE}}>Micro:</b> retinopathy · nephropathy · neuropathy<br /><b style={{color: RED}}>Macro:</b> atherosclerosis → MI · stroke · PAD</div></Box></Frame>,
  () => <Frame n={8} total={10} deck={STU}><H k="7 · DIAGNOSIS (ADA 2026)" c={RED}>Numbers to remember</H>
    <Row a="Fasting glucose" b="≥126 mg/dL  (prediabetes 100–125)" c={RED} /><Row a="HbA1c" b="≥6.5%  (prediabetes 5.7–6.4)" c={RED} />
    <Row a="2-h OGTT (75 g)" b="≥200 mg/dL  (prediabetes 140–199)" c={RED} /><Row a="Random" b="≥200 mg/dL + classic symptoms" c={RED} />
    <Box c={GOLD}><div style={{fontSize: 30}}>Without clear hyperglycaemia, confirm with a repeat or second test. HbA1c ≈ last ~3 months (RBC life ~120 days).</div></Box></Frame>,
  () => <Frame n={9} total={10} deck={STU} img="stills/room_healthy.jpg"><H k="8 · MANAGEMENT" c={GREEN}>Big picture</H>
    <Steps c={GREEN} items={['Lifestyle: diet, activity, weight loss', 'Metformin: usual first drug', 'With ASCVD, heart failure or CKD: SGLT2 inhibitor or GLP-1 RA with proven organ protection', 'Add-ons by need: DPP-4i, SU, TZD, insulin']} />
    <Box c={CYAN}><div style={{fontSize: 34, fontWeight: 800}}>Next episode: <span style={{color: CYAN}}>Metformin, decoded</span></div></Box></Frame>,
  () => <Frame n={10} total={10} deck={STU}><H k="9 · TEST YOURSELF" c={GOLD}>3 exam MCQs</H>
    <MCQ n={1} q="Insulin release is triggered by closure of:" o={['Na⁺ channels', 'ATP-sensitive K⁺ channels', 'GLUT4', 'Cl⁻ channels']} a={1} why="ATP closes K-ATP → depolarisation → Ca²⁺ influx → exocytosis." />
    <MCQ n={2} q="Insulin increases glucose uptake in skeletal muscle mainly by:" o={['SGLT1', 'GLUT4 translocation', 'Glucokinase', 'GLUT2']} a={1} why="PI3K–Akt moves GLUT4 vesicles to the membrane." />
    <MCQ n={3} q="Sorbitol buildup in diabetic neuropathy is due to:" o={['Hexokinase', 'Aldose reductase', 'G-6-phosphatase', 'PKC']} a={1} why="Polyol pathway: aldose reductase converts glucose to sorbitol." /></Frame>,
];
export const PUBLIC_SLIDES: React.FC[] = [
  () => <Frame n={1} total={5} deck={PUB} img="stills/body_wide.jpg">
    <div style={{marginTop: 360}}><div style={{fontSize: 120, fontWeight: 900, lineHeight: 1}}>FOLLOW THE <span style={{color: GOLD}}>SUGAR</span></div>
      <div style={{fontSize: 44, marginTop: 20}}>What rice does inside your body, and how diabetes starts</div></div></Frame>,
  () => <Frame n={2} total={5} deck={PUB} img="stills/muscle.jpg"><H k="HOW IT WORKS" c={CYAN}>Sugar needs a key</H>
    <Steps items={['Rice turns into sugar (glucose) in your blood', 'The pancreas makes the key: insulin', 'Insulin unlocks your cells: sugar goes in → energy', 'Years of extra rice, sweets, belly fat, no exercise → locks get rusty', 'Sugar stays in the blood → type 2 diabetes']} /></Frame>,
  () => <Frame n={3} total={5} deck={PUB}><H k="WARNING SIGNS" c={ORANGE}>Often NO symptoms early</H>
    <Steps c={ORANGE} items={['Always thirsty', 'Peeing often', 'Feeling tired', 'Blurry vision', "Wounds that won't heal"]} />
    <Box c={RED}><div style={{fontSize: 34}}>Untreated, it damages eyes, kidneys, feet nerves, and raises heart attack & stroke risk.</div></Box></Frame>,
  () => <Frame n={4} total={5} deck={PUB}><H k="KNOW YOUR NUMBER" c={GOLD}>Fasting blood sugar</H>
    <Row a="Normal" b="below 100 mg/dL" c={GREEN} /><Row a="Prediabetes" b="100 – 125 mg/dL" c={ORANGE} /><Row a="Diabetes" b="126 mg/dL or more" c={RED} />
    <Box c={GOLD}><div style={{fontSize: 34}}>Above 35, overweight, or diabetes in the family? <b>Get tested.</b> Your doctor confirms the diagnosis.</div></Box></Frame>,
  () => <Frame n={5} total={5} deck={PUB} img="stills/room_healthy.jpg"><H k="WHAT HELPS" c={GREEN}>Take charge</H>
    <Steps c={GREEN} items={['Less rice and sweets, more vegetables & dal', 'Walk after every meal', 'Keep a healthy weight', 'Take tablets exactly as your doctor says', 'Check sugar regularly']} />
    <Box><div style={{fontSize: 26, opacity: 0.85}}>For awareness only. Not medical advice. Don't change your medicines without your doctor.</div></Box></Frame>,
];
export const Slide: React.FC<{deck: 'student' | 'public'; idx: number}> = ({deck, idx}) => {
  const S = (deck === 'student' ? STUDENT_SLIDES : PUBLIC_SLIDES)[idx];
  return <S />;
};
export const HighYieldSlide: React.FC = () => (
  <AbsoluteFill style={{background: 'linear-gradient(160deg, #0d1426, #05070e)', alignItems: 'center', paddingTop: 80}}><HighYield /></AbsoluteFill>
);
