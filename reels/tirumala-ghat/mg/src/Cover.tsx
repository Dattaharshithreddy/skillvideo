import React from 'react';
import {AbsoluteFill, Img, staticFile} from 'remotion';
import LB from './labels.json';
const SERIF = '"Noto Serif Telugu", "Noto Sans Telugu", serif', SANS = '"Noto Sans Telugu", Poppins, sans-serif';
const gold: React.CSSProperties = {background: 'linear-gradient(180deg, #FFF8D0 0%, #FFD35A 40%, #F09A1A 78%, #FFE08A 100%)', WebkitBackgroundClip: 'text', backgroundClip: 'text',
  color: 'transparent', filter: 'drop-shadow(0 6px 0 rgba(80,30,0,0.95)) drop-shadow(0 0 34px rgba(255,170,40,0.85))'};
export const Cover: React.FC = () => {
  const g = (LB as any).shots?.govinda || {}; const ks = Object.keys(g); const row = ks.length ? g[ks[ks.length - 1]] : []; const tp = row.length ? row[row.length - 1] : ['', 0.5, 0.45, 1];
  const x = tp[1] * 1080, y = 710 + tp[2] * 1920, R = 1500;
  const mask = 'radial-gradient(circle, rgba(0,0,0,1) 0%, rgba(0,0,0,0.5) 24%, rgba(0,0,0,0) 62%)';
  return <AbsoluteFill style={{background: '#1a0a00'}}>
    <Img src={staticFile('cover_bg.jpg')} style={{position: 'absolute', top: 520, left: 0, width: 1080, height: 1920, filter: 'saturate(1.4) contrast(1.1) brightness(0.92)'}} />
    <AbsoluteFill style={{mixBlendMode: 'screen'}}>
      <div style={{position: 'absolute', left: x - R, top: y - R, width: 2 * R, height: 2 * R, background: 'repeating-conic-gradient(from 4deg, rgba(255,214,120,0) 0deg, rgba(255,224,140,0.6) 3deg, rgba(255,214,120,0) 8deg, rgba(255,214,120,0) 20deg)',
        WebkitMaskImage: mask, maskImage: mask, filter: 'blur(5px)'}} />
      <div style={{position: 'absolute', left: x - 560, top: y - 560, width: 1120, height: 1120, background: 'radial-gradient(circle, rgba(255,244,200,0.9) 0%, rgba(255,196,84,0.45) 14%, rgba(255,150,40,0.14) 36%, rgba(255,150,40,0) 60%)'}} />
    </AbsoluteFill>
    <AbsoluteFill style={{background: 'linear-gradient(180deg, rgba(70,20,0,1) 0%, rgba(110,38,0,1) 27%, rgba(120,45,0,0.75) 40%, rgba(60,20,0,0.1) 54%, rgba(0,0,0,0) 62%, rgba(20,6,0,0.35) 80%, rgba(20,6,0,0.95) 100%)'}} />
    <div style={{position: 'absolute', top: 285, width: '100%', textAlign: 'center'}}>
      <div style={{fontFamily: SERIF, fontSize: 46, fontWeight: 800, letterSpacing: 2, ...gold}}>ఓం నమో వేంకటేశాయ</div>
      <div style={{fontFamily: SERIF, fontSize: 250, fontWeight: 900, lineHeight: 1.22, marginTop: -8, ...gold}}>తిరుమల</div>
      <div style={{fontFamily: SANS, fontSize: 132, fontWeight: 900, color: 'white', lineHeight: 1.1, marginTop: -18, WebkitTextStroke: '5px rgba(40,12,0,0.95)', paintOrder: 'stroke fill', textShadow: '0 8px 0 rgba(40,12,0,0.9)'}}>ఘాట్ రోడ్డు</div>
    </div>
    <div style={{position: 'absolute', top: 850, width: '100%', textAlign: 'center'}}>
      <div style={{display: 'inline-block', transform: 'rotate(-3deg)', background: '#E0211B', border: '6px solid #FFD35A', borderRadius: 26, padding: '14px 44px 6px', boxShadow: '0 14px 40px rgba(0,0,0,0.6)',
        fontFamily: SANS, fontWeight: 900, fontSize: 92, color: 'white', lineHeight: 1.2}}>80 ఏళ్ళ <span style={{color: '#FFE36B'}}>రహస్యం!</span></div>
      <div style={{position: 'absolute', top: 870, width: '100%', fontFamily: SANS, fontWeight: 900, fontSize: 66, color: 'white', textShadow: '0 4px 14px rgba(0,0,0,0.95)', WebkitTextStroke: '3px rgba(30,8,0,0.9)', paintOrder: 'stroke fill'}}><span style={{color: '#FFD35A'}}>1944</span> లో ఎలా కట్టారు?</div>
    </div>
  </AbsoluteFill>;
};
