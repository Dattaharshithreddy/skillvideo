// Mahabharata costumes + action poses for MakeHuman (mixamo rig) characters.
// Everything procedural: silk dhoti (wrap), gold kavacha (torso hull wrap), kiritam crown, armlets, necklace, uttariya, bow, quiver.
import * as THREE from 'three';
import { GLTFLoader } from 'three/addons/loaders/GLTFLoader.js';
import * as SkeletonUtils from 'three/addons/utils/SkeletonUtils.js';
import { clothTex, restVerts, hullRing, boneMap, wrap, pallu, aim } from './attire.js';
const gl = new GLTFLoader(); const cache = {}; const load = (p) => (cache[p] ??= gl.loadAsync(p));
const V = (x = 0, y = 0, z = 0) => new THREE.Vector3(x, y, z); const wpos = (b) => b.getWorldPosition(V());

// ---------- materials ----------
let envTex = null; export const setEnv = (t) => { envTex = t; };
const goldM = (c = 0xffc54a, r = 0.28) => new THREE.MeshStandardMaterial({ color: c, metalness: 1, roughness: r });
function patternTex(base, line) { // scale-mail / brocade rows
  const c = document.createElement('canvas'); c.width = c.height = 256; const x = c.getContext('2d'); x.fillStyle = base; x.fillRect(0, 0, 256, 256);
  x.strokeStyle = line; x.lineWidth = 3; for (let r = 0; r < 9; r++) for (let k = -1; k < 9; k++) { const cx = k * 32 + (r % 2) * 16, cy = r * 30; x.beginPath(); x.arc(cx, cy, 16, 0, Math.PI); x.stroke(); }
  x.fillStyle = line; for (let k = 0; k < 9; k++) x.fillRect(0, k * 60 + 56, 256, 2);
  const t = new THREE.CanvasTexture(c); t.colorSpace = THREE.SRGBColorSpace; t.wrapS = t.wrapT = THREE.RepeatWrapping; return t;
}
const armorM = (kind = 'gold') => { const col = kind === 'bronze' ? 0x6e4a26 : kind === 'silver' ? 0xd8dde2 : 0xffc04a; const m = goldM(col, kind === 'bronze' ? 0.42 : 0.3);
  m.map = patternTex('#ffffff', kind === 'bronze' ? '#4a3018' : '#9a9ca0'); m.map.repeat.set(3, 2); m.bumpMap = m.map; m.bumpScale = 1.6; return m; };
function medallion(kind) { const g = new THREE.Group(); const c = kind === 'silver' ? 0xe8ecf0 : 0xffc54a;
  const d = new THREE.Mesh(new THREE.CylinderGeometry(0.075, 0.08, 0.018, 32), goldM(c, 0.25)); d.rotation.x = Math.PI / 2; g.add(d);
  for (let i = 0; i < 3; i++) { const r = new THREE.Mesh(new THREE.TorusGeometry(0.03 + i * 0.022, 0.0045, 6, 32), goldM(c, 0.2)); r.position.z = 0.011; g.add(r); }
  const gem = new THREE.Mesh(new THREE.SphereGeometry(0.016, 12, 10), new THREE.MeshPhysicalMaterial({ color: 0xc0102e, roughness: 0.05, emissive: 0x400010 })); gem.position.z = 0.015; g.add(gem); return g; }
const silk = (base, border) => new THREE.MeshPhysicalMaterial({ map: clothTex(base, border, '#f6d77a', false, true), roughness: 0.45, sheen: 0.8, sheenColor: new THREE.Color(border), side: THREE.DoubleSide });

// skinned torso hull (kavacha / blouse) between two heights, weighted to spine bones
function torsoWrap(o, B, target, y0, y1, mat, margin = 0.012) {
  const pts = restVerts(o); const BI = target.skeleton.bones; const bi = (n) => BI.indexOf(B[n]);
  const c0 = wpos(B.Spine1 || B.Spine); const N = 40, H = 16; const latv = wpos(B.RightUpLeg).sub(wpos(B.LeftUpLeg)).setY(0).normalize(), fv = V(0, 1, 0).cross(latv).normalize(); const pos = [], uv = [], si = [], sw = [], idx = [];
  const sp = [bi('Hips'), bi('Spine'), bi('Spine1') >= 0 ? bi('Spine1') : bi('Spine'), bi('Spine2')];
  for (let h = 0; h <= H; h++) { const t = h / H, y = THREE.MathUtils.lerp(y0, y1, t);
    const armY = wpos(B.LeftArm).y - 0.05, nkY = wpos(B.Neck).y; const cap = y < armY ? 0.165 : THREE.MathUtils.lerp(0.165, 0.075, Math.min(1, (y - armY) / Math.max(0.01, nkY - armY)));
    const { ring } = hullRing(pts.filter((p) => Math.abs((p.x - c0.x) * latv.x + (p.z - c0.z) * latv.z) < cap && Math.abs((p.x - c0.x) * fv.x + (p.z - c0.z) * fv.z) < 0.16), y - 0.025, y + 0.025, N, margin, V(c0.x, 0, c0.z));
    for (let k = 0; k <= N; k++) { const a = k / N * Math.PI * 2, r = ring[k % N]; pos.push(c0.x + Math.cos(a) * r, y, c0.z + Math.sin(a) * r); uv.push(k / N, t);
      const w = [Math.max(0, 1 - t * 3), Math.max(0, 1 - Math.abs(t - 0.3) * 3), Math.max(0, 1 - Math.abs(t - 0.6) * 3), Math.max(0, t * 2.2 - 1)]; const s = w.reduce((a2, b) => a2 + b, 0) || 1;
      si.push(...sp); sw.push(...w.map((x) => x / s)); } }
  for (let h = 0; h < H; h++) for (let k = 0; k < N; k++) { const a = h * (N + 1) + k, b = a + N + 1; idx.push(a, b, a + 1, b, b + 1, a + 1); }
  return skinned(target, pos, uv, si, sw, idx, mat);
}
function skinned(target, pos, uv, si, sw, idx, mat) {
  const g = new THREE.BufferGeometry(); const inv = target.matrixWorld.clone().invert(); const P = new Float32Array(pos);
  for (let i = 0; i < P.length; i += 3) { const v = V(P[i], P[i + 1], P[i + 2]).applyMatrix4(inv); P.set([v.x, v.y, v.z], i); }
  g.setAttribute('position', new THREE.BufferAttribute(P, 3)); g.setAttribute('uv', new THREE.Float32BufferAttribute(uv, 2));
  g.setAttribute('skinIndex', new THREE.Uint16BufferAttribute(si, 4)); g.setAttribute('skinWeight', new THREE.Float32BufferAttribute(sw, 4)); g.setIndex(idx); g.computeVertexNormals();
  const m = new THREE.SkinnedMesh(g, mat); m.castShadow = m.receiveShadow = true; m.frustumCulled = false; target.parent.add(m);
  m.position.copy(target.position); m.quaternion.copy(target.quaternion); m.scale.copy(target.scale); m.bind(target.skeleton, target.bindMatrix); return m;
}
// rigid prop parented to a bone, placed at a world position in rest pose
function attach(bone, obj, worldPos, worldQuat) {
  bone.updateMatrixWorld(true); const inv = bone.matrixWorld.clone().invert(); obj.position.copy(worldPos.clone().applyMatrix4(inv));
  const bq = bone.getWorldQuaternion(new THREE.Quaternion()).invert(); obj.quaternion.copy(bq.multiply(worldQuat || new THREE.Quaternion()));
  const ws = bone.getWorldScale(V()); obj.scale.set(1 / ws.x, 1 / ws.y, 1 / ws.z); bone.add(obj); obj.traverse((m) => { if (m.isMesh) { m.castShadow = true; m.frustumCulled = false; } }); return obj;
}
function headTop(o, B) { const pts = restVerts(o); const h = wpos(B.Head); let top = h.y; for (const p of pts) if (Math.hypot(p.x - h.x, p.z - h.z) < 0.09 && p.y > top) top = p.y; return V(h.x, top, h.z); }
function kiritam(scale = 1, tall = 0.24) { // tiered gold crown with jewels
  const g = new THREE.Group(); const prof = []; const H = tall;
  const pr = [[0.105, 0], [0.11, 0.02], [0.1, 0.035], [0.104, 0.05], [0.09, 0.09], [0.094, 0.1], [0.075, 0.14], [0.079, 0.15], [0.055, 0.19], [0.058, 0.2], [0.03, H - 0.02], [0.012, H], [0, H + 0.04]];
  for (const [r, y] of pr) prof.push(new THREE.Vector2(r * scale, y));
  const body = new THREE.Mesh(new THREE.LatheGeometry(prof, 32), armorM()); g.add(body);
  const gem = (col, y, r, a) => { const s = new THREE.Mesh(new THREE.SphereGeometry(0.012 * scale, 10, 8), new THREE.MeshPhysicalMaterial({ color: col, roughness: 0.05, transmission: 0.3, emissive: col, emissiveIntensity: 0.15 })); s.position.set(Math.sin(a) * r * scale, y, Math.cos(a) * r * scale); g.add(s); };
  for (let i = 0; i < 10; i++) gem(i % 2 ? 0xd0103a : 0x10a050, 0.025, 0.112, i / 10 * 6.283);
  gem(0xd0103a, 0.12, 0.085, 0); gem(0x1060d0, 0.17, 0.066, 0);
  // front crest plate
  const crest = new THREE.Mesh(new THREE.CircleGeometry(0.05 * scale, 20, 0, Math.PI), armorM()); crest.position.set(0, 0.06, 0.104 * scale); g.add(crest);
  return g;
}
function band(r, w = 0.025, mat = goldM()) { return new THREE.Mesh(new THREE.CylinderGeometry(r, r, w, 24, 1, true), Object.assign(mat, { side: THREE.DoubleSide })); }
function bow() { // recurved bow + string, local Y up, ~1.5 m
  const g = new THREE.Group(); const pts = []; for (let i = 0; i <= 24; i++) { const t = i / 24 * 2 - 1; pts.push(V(0, t * 0.75, -0.16 * (1 - t * t) + 0.05 * Math.pow(Math.abs(t), 6))); }
  const curve = new THREE.CatmullRomCurve3(pts); g.add(new THREE.Mesh(new THREE.TubeGeometry(curve, 48, 0.016, 8), new THREE.MeshStandardMaterial({ color: 0x5a3216, roughness: 0.5, metalness: 0.2 })));
  for (const y of [-0.06, 0.06]) { const b = band(0.022, 0.03); b.position.set(0, y, -0.16); g.add(b); }
  const s = new THREE.Mesh(new THREE.CylinderGeometry(0.002, 0.002, 1.52, 4), new THREE.MeshBasicMaterial({ color: 0xeeeeee })); s.position.set(0, 0, 0.05); g.add(s); g.userData.string = s; return g;
}
export function arrow() { const g = new THREE.Group(); const sh = new THREE.Mesh(new THREE.CylinderGeometry(0.005, 0.005, 0.8, 6), new THREE.MeshStandardMaterial({ color: 0xc89a58 })); sh.rotation.x = Math.PI / 2; g.add(sh);
  const tip = new THREE.Mesh(new THREE.ConeGeometry(0.014, 0.07, 8), goldM(0xdddddd, 0.2)); tip.rotation.x = Math.PI / 2; tip.position.z = 0.43; g.add(tip);
  for (let i = 0; i < 3; i++) { const f = new THREE.Mesh(new THREE.PlaneGeometry(0.03, 0.08), new THREE.MeshStandardMaterial({ color: 0xffffff, side: THREE.DoubleSide })); f.position.z = -0.36; f.rotation.set(Math.PI / 2, i * 2.09, 0); f.translateX(0.015); g.add(f); }
  return g; }


// ---------- dhoti, kaccha style: short wrap at the hips, each leg wrapped loosely to mid-calf, pleated front fall, gold belt and patka ----------
function legTube(o, B, target, side, y0, y1, mat, margin) {
  const pts = restVerts(o); const BI = target.skeleton.bones; const S = side; const up = B[S + 'UpLeg'], kn = B[S + 'Leg'], ft = B[S + 'Foot'];
  const pU = wpos(up), pK = wpos(kn), pF = wpos(ft); const iU = BI.indexOf(up), iK = BI.indexOf(kn), iH = BI.indexOf(B.Hips);
  const sideSign = Math.sign(pU.x - wpos(B.Hips).x) || 1; const N = 28, Hn = 14; const pos = [], uv = [], si = [], sw = [], idx = [];
  const axisAt = (y) => (y > pK.y ? pU.clone().lerp(pK, (pU.y - y) / (pU.y - pK.y)) : pK.clone().lerp(pF, (pK.y - y) / (pK.y - pF.y)));
  for (let h = 0; h <= Hn; h++) { const t = h / Hn, y = lerpN(y0, y1, t); const c = axisAt(y);
    const sel = pts.filter((p) => Math.abs(p.y - y) < 0.03 && Math.hypot(p.x - c.x, p.z - c.z) < 0.16 && Math.sign(p.x - wpos(B.Hips).x) === sideSign);
    for (let k = 0; k <= N; k++) { const a = k / N * Math.PI * 2, dx = Math.cos(a), dz = Math.sin(a); let r = 0.05; for (const p of sel) r = Math.max(r, (p.x - c.x) * dx + (p.z - c.z) * dz);
      const fold = 1 + 0.06 * Math.sin(a * 5 + h * 0.7);   // cloth folds
      r = (r + margin * (0.7 + 0.6 * t)) * fold; pos.push(c.x + dx * r, y, c.z + dz * r); uv.push(k / N, 1 - (0.35 + 0.65 * t));
      const wK = THREE.MathUtils.smoothstep(pK.y + 0.06 - y, 0, 0.12), wH = Math.max(0, 1 - t * 4) * 0.5; si.push(iH, iU, iK, iU); sw.push(wH, (1 - wK) * (1 - wH), wK * (1 - wH), 0); } }
  for (let h = 0; h < Hn; h++) for (let k = 0; k < N; k++) { const a = h * (N + 1) + k, b = a + N + 1; idx.push(a, b, a + 1, b, b + 1, a + 1); }
  return skinned(target, pos, uv, si, sw, idx, mat);
}
const lerpN = (a, b, t) => a + (b - a) * t;
function panel(o, B, target, y0, y1, w0, w1, mat, out = 0.02, bones = ['Hips']) { // flat cloth strip hanging at the front centre (pleats / patka)
  const pts = restVerts(o); const BI = target.skeleton.bones; const h = wpos(B.Hips); const lat = wpos(B.RightUpLeg).sub(wpos(B.LeftUpLeg)).setY(0).normalize(); const F = V(0, 1, 0).cross(lat).normalize();
  const pos = [], uv = [], si = [], sw = [], idx = []; const Hn = 12; let lastF = 0.12;
  for (let k = 0; k <= Hn; k++) { const t = k / Hn, y = lerpN(y0, y1, t), w = lerpN(w0, w1, t);
    let f = 0.05; for (const p of pts) if (Math.abs(p.y - y) < 0.03 && Math.abs(p.clone().sub(h).dot(lat)) < 0.12) f = Math.max(f, p.clone().sub(h).dot(F)); if (y < h.y - 0.25) f = Math.max(f, lastF * 0.96); lastF = f;
    for (const sx of [-1, 1]) { const v = h.clone().setY(y).add(F.clone().multiplyScalar(f + out)).add(lat.clone().multiplyScalar(sx * w / 2)); pos.push(v.x, v.y, v.z); uv.push((sx + 1) / 2, 1 - t); si.push(BI.indexOf(B[bones[0]]), 0, 0, 0); sw.push(1, 0, 0, 0); } }
  for (let k = 0; k < Hn; k++) { const a = k * 2; idx.push(a, a + 2, a + 1, a + 1, a + 2, a + 3); }
  const m = skinned(target, pos, uv, si, sw, idx, mat); m.material.side = THREE.DoubleSide; return m;
}
function pleatTex(base, border) { const c = document.createElement('canvas'); c.width = 128; c.height = 512; const x = c.getContext('2d'); x.fillStyle = base; x.fillRect(0, 0, 128, 512);
  for (let i = 0; i < 9; i++) { const g = x.createLinearGradient(i * 14, 0, i * 14 + 14, 0); g.addColorStop(0, 'rgba(0,0,0,0.28)'); g.addColorStop(0.5, 'rgba(255,255,255,0.12)'); g.addColorStop(1, 'rgba(0,0,0,0.05)'); x.fillStyle = g; x.fillRect(i * 14 + 1, 0, 14, 512); }
  x.fillStyle = border; x.fillRect(0, 470, 128, 30); x.fillStyle = '#f6d77a'; x.fillRect(0, 476, 128, 4); x.fillRect(0, 492, 128, 4);
  const t = new THREE.CanvasTexture(c); t.colorSpace = THREE.SRGBColorSpace; return t; }
export function dhotiKaccha(o, B, target, base, border) {
  const hy = wpos(B.Hips).y, ky = wpos(B.LeftLeg).y, fy = wpos(B.LeftFoot).y; const crotch = hy - 0.13;
  const silkM = () => new THREE.MeshPhysicalMaterial({ map: clothTex(base, border, '#f6d77a', false, false), roughness: 0.5, sheen: 0.8, sheenColor: new THREE.Color(border), side: THREE.DoubleSide });
  torsoWrap(o, B, target, crotch - 0.04, hy + 0.06, silkM(), 0.02);                            // short wrap around the hips
  for (const sd of ['Left', 'Right']) legTube(o, B, target, sd, crotch + 0.02, fy + (ky - fy) * 0.32, silkM(), 0.035);   // loose leg wraps to mid-calf
  panel(o, B, target, hy + 0.05, fy + (ky - fy) * 0.25, 0.16, 0.26, new THREE.MeshPhysicalMaterial({ map: pleatTex(base, border), roughness: 0.5, sheen: 0.8, sheenColor: new THREE.Color(border) }), 0.03);   // pleated front fall
  torsoWrap(o, B, target, hy + 0.04, hy + 0.09, goldM(0xffc54a, 0.25), 0.03);                // gold kamarbandh belt
  panel(o, B, target, hy + 0.05, hy - 0.32, 0.12, 0.09, new THREE.MeshPhysicalMaterial({ map: clothTex(border, '#f6d77a', null), roughness: 0.5, sheen: 0.6 }), 0.05);   // patka hanging from the belt
}

// ---------- poses (aim-based, rest-pose independent) ----------
export function epicPose(o, B, name, ph = 0) {
  o.updateMatrixWorld(true);
  const lat = wpos(B.RightUpLeg).sub(wpos(B.LeftUpLeg)).setY(0).normalize(); const F = V(0, 1, 0).cross(lat).normalize(), U = V(0, 1, 0), R = lat;
  const d = (f, u, r) => F.clone().multiplyScalar(f).add(U.clone().multiplyScalar(u)).add(R.clone().multiplyScalar(r));
  const arm = (sd, up, fo, hd) => { const s = sd === 'L' ? 'Left' : 'Right'; aim(B[s + 'Arm'], B[s + 'ForeArm'], up); aim(B[s + 'ForeArm'], B[s + 'Hand'], fo); if (hd && B[s + 'HandMiddle1']) aim(B[s + 'Hand'], B[s + 'HandMiddle1'], hd); };
  const leg = (sd, th, ca) => { const s = sd === 'L' ? 'Left' : 'Right'; aim(B[s + 'UpLeg'], B[s + 'Leg'], th); aim(B[s + 'Leg'], B[s + 'Foot'], ca); if (B[s + 'ToeBase']) aim(B[s + 'Foot'], B[s + 'ToeBase'], d(1, -0.3, 0)); };
  const stand = () => { leg('L', d(0, -1, -0.06), d(0, -1, -0.04)); leg('R', d(0, -1, 0.06), d(0, -1, 0.04)); };
  if (name === 'bowdraw') { // archer: body side-on, left arm straight to target (+R side = character's right... we aim to the LEFT side), right hand at cheek
    const T = d(0.05, 0.04, -1); leg('L', d(0.1, -1, -0.32), d(0.06, -1, -0.32)); leg('R', d(-0.05, -1, 0.3), d(-0.05, -1, 0.3));
    arm('L', T, T, T); arm('R', d(-0.25, 0.05, -0.6), d(0.2, 0.4, 1), d(0, 0.3, -1)); aim(B.Neck, B.Head, d(0, 1, 0)); if (B.Head) B.Head.rotateY(0.9); }
  else if (name === 'bowrest') { stand(); arm('L', d(0.15, -1, -0.15), d(0.5, -0.4, -0.1), d(0.2, 0.2, 0)); arm('R', d(0.05, -1, 0.12), d(0.15, -1, 0.05), d(0.05, -1, 0)); }
  else if (name === 'angry') { stand(); arm('L', d(0.15, -1, -0.15), d(0.5, -0.4, -0.1), d(0.2, 0.2, 0)); arm('R', d(0.9, 0.05, 0.2), d(1, 0.15, 0.05), d(1, 0, 0)); }
  else if (name === 'offer') { stand(); arm('L', d(0.6, -0.8, -0.1), d(1, 0.15, 0.15), d(1, 0, 0.1)); arm('R', d(0.6, -0.8, 0.1), d(1, 0.15, -0.15), d(1, 0, -0.1)); aim(B.Spine, B.Spine1 || B.Spine2, d(0.25, 1, 0)); }
  else if (name === 'namaskaram') { stand(); arm('L', d(0.35, -1, -0.12), d(0.55, 0.85, 1.05), d(0.25, 1, 0.1)); arm('R', d(0.35, -1, 0.12), d(0.55, 0.85, -1.05), d(0.25, 1, -0.1)); }
  else if (name === 'kneel') { leg('L', d(1, -0.15, -0.1), d(0, -1, 0)); leg('R', d(0.05, -1, 0.1), d(-1, -0.05, 0)); arm('L', d(0.3, -1, -0.1), d(0.6, -0.7, 0.2), null); arm('R', d(0.3, -1, 0.1), d(0.6, -0.7, -0.2), null);
    aim(B.Spine, B.Spine1 || B.Spine2, d(0.3, 1, 0)); B.Hips.position.y *= 0.62; }
  else if (name === 'fallen') { leg('L', d(-0.05, -1, -0.1), d(0.2, -1, -0.12)); leg('R', d(-0.1, -1, 0.15), d(0.25, -1, 0.1)); arm('L', d(0, 0.1, -1), d(0.3, 0.2, -1), null); arm('R', d(0.2, -1, 0.5), d(0.4, -0.6, 0.6), null); }
  else if (name === 'embrace') { stand(); arm('L', d(0.75, -0.35, -0.3), d(0.4, 0.1, 1), d(-0.2, 0, 1)); arm('R', d(0.75, -0.25, 0.3), d(0.4, 0.15, -1), d(-0.2, 0, -1)); }
  else if (name === 'raise') { stand(); arm('L', d(0.4, 0.9, -0.4), d(0.3, 1, -0.2), d(0, 1, 0)); arm('R', d(0.4, 0.9, 0.4), d(0.3, 1, 0.2), d(0, 1, 0)); }
  else { stand(); arm('L', d(0.03, -1, -0.12), d(0.15, -1, -0.03), d(0.05, -1, 0)); arm('R', d(0.03, -1, 0.12), d(0.15, -1, 0.03), d(0.05, -1, 0)); }
  o.updateMatrixWorld(true);
}

// ---------- characters ----------
const LOOK = {
  arjuna: { dhoti: ['#e9b927', '#9c1c1c'], armor: 'bronze', crown: 0.15, uttariya: '#c2185b', bow: true, quiver: true, mustache: '#1e1612', tilak: true },
  babhru: { dhoti: ['#8e1b2a', '#e8b33a'], armor: 'gold', crown: 0.13, uttariya: '#e8b33a', bow: true, quiver: true, tilak: true },
  bhishma: { dhoti: ['#f5f2ea', '#c99a2e'], armor: 'silver', crown: 0.2, crownKind: 'silver', tilak: true, uttariya: '#f5f2ea', hair: '#e8e6e0', bow: true, beard: '#f2f0ea' },
  shikhandi: { dhoti: ['#3b5f2a', '#e8b33a'], armor: 'bronze', tilak: true, crown: 0, uttariya: '#c27a1b', bow: true },
  kauravya: { dhoti: ['#0f4d5a', '#e8b33a'], armor: 'gold', crown: 0.24, uttariya: '#1fa38a', naga: true, tilak: true, mustache: '#2a221c' },
  soldier_a: { dhoti: ['#7a5a2e', '#3a2a14'], armor: 'bronze', crown: 0 }, soldier_b: { dhoti: ['#5a2e2e', '#2a1414'], armor: 'bronze', crown: 0 },
  ulupi: { saree: ['#0f7a6a', '#e8b33a'], blouse: '#e8b33a', crown: 0.1, naga: true },
  chitrangada: { saree: ['#a3141d', '#e8b33a'], blouse: '#e8b33a', crown: 0.12 },
  ganga: { saree: ['#e8f4ff', '#9ad0ff'], blouse: '#cfe8ff', crown: 0.1 },
};
export async function character(name, { poseName = 'stand', phase = 0, light = 0, file } = {}) {
  const L = LOOK[name] || LOOK.soldier_a; const g = await load(file || `cast/${name}.glb`); const o = SkeletonUtils.clone(g.scene); let target = null;
  o.traverse((m) => { if (!m.isMesh) return; m.castShadow = m.receiveShadow = true; m.frustumCulled = false; if (m.isSkinnedMesh && !target && /^base|body/i.test(m.name + '')) target = m;
    const mats = Array.isArray(m.material) ? m.material : [m.material];
    m.material = mats.map((t0) => { const t = t0.clone(); const n = (t.name || '').toLowerCase(); t.depthWrite = true;
      if (/eyebrow|short|long|bob|ponytail|braid|eyelash|hair/.test(n)) { t.transparent = false; t.alphaTest = 0.5; } else { t.transparent = false; t.alphaTest = 0; t.opacity = 1; }
      if (/body|ears/.test(n) && t.color) t.color = new THREE.Color(1.55, 1.36, 1.2);
      if (/short|long|bob|ponytail|braid|hair/.test(n)) { if (L.hair) { t.color = new THREE.Color(1, 1, 1); const m0 = t.map; if (m0 && m0.image) { const c = document.createElement('canvas'); c.width = m0.image.width; c.height = m0.image.height; const x = c.getContext('2d'); x.filter = 'grayscale(1) brightness(2.6) contrast(0.8)'; x.drawImage(m0.image, 0, 0); const nt = new THREE.CanvasTexture(c); nt.flipY = m0.flipY; nt.colorSpace = m0.colorSpace; nt.channel = m0.channel; t.map = nt; } } else t.color = new THREE.Color('#2a221c'); }
      if (/suit|blouse|dress|top/.test(n)) { t.map = null; t.normalMap = null; t.color = new THREE.Color(L.blouse || '#e8b33a'); t.roughness = 0.6; t.metalness = 0.2; }
      return t; }); if (m.material.length === 1) m.material = m.material[0]; });
  if (!target) o.traverse((m) => { if (m.isSkinnedMesh && !target) target = m; });
  o.updateMatrixWorld(true); const B = boneMap(o);
  const female = !!L.saree;
  if (!female) {
    dhotiKaccha(o, B, target, ...L.dhoti);
    if (L.armor) { const kind = L.armor === true ? 'gold' : L.armor; const hy = wpos(B.Hips).y, sy = wpos(B.LeftArm).y; torsoWrap(o, B, target, hy + 0.0, wpos(B.Neck).y - 0.015, armorM(kind), 0.014);
      const lat0 = wpos(B.RightUpLeg).sub(wpos(B.LeftUpLeg)).setY(0).normalize(); const F0 = V(0, 1, 0).cross(lat0).normalize();
      // chest medallion at the front surface of the kavacha
      const cpts = restVerts(o).filter((p) => Math.abs(p.y - (sy - 0.17)) < 0.03); let fz = -1e9; const sp2 = wpos(B.Spine2); for (const p of cpts) { const f = p.clone().sub(sp2).dot(F0); if (Math.abs(p.clone().sub(sp2).dot(lat0)) < 0.05) fz = Math.max(fz, f); }
      attach(B.Spine2, medallion(kind), sp2.clone().setY(sy - 0.17).add(F0.clone().multiplyScalar(fz + 0.022)), new THREE.Quaternion().setFromUnitVectors(V(0, 0, 1), F0));
      // shoulder plates (pauldrons) + leather bracers
      for (const sd of ['Left', 'Right']) { const sh = wpos(B[sd + 'Arm']); const pd = new THREE.Mesh(new THREE.SphereGeometry(0.075, 20, 12, 0, Math.PI * 2, 0, Math.PI * 0.45), armorM(kind)); pd.scale.set(1, 0.75, 1.1);
        const out = sh.clone().sub(sp2).setY(0).normalize(); attach(B[sd + 'Arm'], pd, sh.clone().add(V(0, -0.025, 0)).add(out.clone().multiplyScalar(-0.01)), new THREE.Quaternion().setFromUnitVectors(V(0, 1, 0), out.clone().multiplyScalar(0.9).add(V(0, 1, 0)).normalize()));
        const fa = wpos(B[sd + 'ForeArm']), hd = wpos(B[sd + 'Hand']); const br = new THREE.Mesh(new THREE.CylinderGeometry(0.043, 0.036, fa.distanceTo(hd) * 0.6, 16), new THREE.MeshStandardMaterial({ color: 0x3a2412, roughness: 0.7 }));
        attach(B[sd + 'ForeArm'], br, fa.clone().lerp(hd, 0.62), new THREE.Quaternion().setFromUnitVectors(V(0, 1, 0), hd.clone().sub(fa).normalize())); } }
    const neck = wpos(B.Neck); const nk = new THREE.Mesh(new THREE.TorusGeometry(0.085, 0.012, 8, 32), goldM()); nk.scale.set(1, 0.65, 1.0);
    attach(B.Spine2, nk, neck.clone().add(V(0, -0.05, 0.02)), new THREE.Quaternion().setFromEuler(new THREE.Euler(Math.PI / 2 + 0.4, 0, 0)));
  } else { wrap(o, B, target, 'saree', silk(...L.saree)); const hy = wpos(B.Hips).y, fy = wpos(B.LeftFoot).y; panel(o, B, target, hy + 0.03, fy - 0.04, 0.14, 0.34, new THREE.MeshPhysicalMaterial({ map: pleatTex(L.saree[0], L.saree[1]), roughness: 0.45, sheen: 0.8, sheenColor: new THREE.Color(L.saree[1]) }), 0.045); pallu(o, B, target, silk(...L.saree)); }
  // armlets + wrist bands
  for (const s of ['Left', 'Right']) { const a = wpos(B[s + 'Arm']).lerp(wpos(B[s + 'ForeArm']), 0.35), dir = wpos(B[s + 'ForeArm']).sub(wpos(B[s + 'Arm'])).normalize();
    attach(B[s + 'Arm'], band(0.048, 0.035), a, new THREE.Quaternion().setFromUnitVectors(V(0, 1, 0), dir));
    const w = wpos(B[s + 'Hand']).lerp(wpos(B[s + 'ForeArm']), 0.1), dw = wpos(B[s + 'Hand']).sub(wpos(B[s + 'ForeArm'])).normalize();
    attach(B[s + 'ForeArm'], band(0.036, 0.04), w, new THREE.Quaternion().setFromUnitVectors(V(0, 1, 0), dw)); }
  if (L.crown) { const top = headTop(o, B); const c = kiritam(female ? 0.8 : (L.crown < 0.18 ? 0.82 : 1), L.crown); if (L.crownKind === 'silver') c.traverse((m) => { if (m.isMesh && m.material.metalness === 1) { m.material = m.material.clone(); m.material.color.set(0xdfe4ea); } }); attach(B.Head, c, top.clone().add(V(0, -0.05, -0.01))); }
  if (L.naga) { const hood = new THREE.Group(); for (let i = 0; i < 5; i++) { const s = new THREE.Mesh(new THREE.SphereGeometry(0.05, 12, 10), new THREE.MeshStandardMaterial({ color: 0x0d5a48, roughness: 0.35, metalness: 0.4, emissive: 0x0a3a30, emissiveIntensity: 0.4 }));
      s.scale.set(0.7, 1.4, 0.4); s.position.set((i - 2) * 0.06, 0.1 - Math.abs(i - 2) * 0.03, -0.02); s.rotation.z = (i - 2) * -0.25; hood.add(s); }
    const top = headTop(o, B); attach(B.Head, hood, top.clone().add(V(0, -0.02, -0.08))); }
  if (L.beard) { const h = wpos(B.Head); const lat = wpos(B.RightUpLeg).sub(wpos(B.LeftUpLeg)).setY(0).normalize(); const F = V(0, 1, 0).cross(lat).normalize();
    const c = document.createElement('canvas'); c.width = 64; c.height = 256; const x = c.getContext('2d'); x.fillStyle = L.beard; x.fillRect(0, 0, 64, 256);
    for (let i = 0; i < 900; i++) { x.strokeStyle = `rgba(${Math.random() < 0.5 ? '0,0,0,0.12' : '255,255,255,0.25'})`; const px = Math.random() * 64; x.beginPath(); x.moveTo(px, Math.random() * 256); x.lineTo(px + (Math.random() - 0.5) * 4, Math.random() * 256); x.stroke(); }
    const t = new THREE.CanvasTexture(c); t.colorSpace = THREE.SRGBColorSpace;
    const prof = [[0.0, -0.2], [0.02, -0.19], [0.045, -0.15], [0.065, -0.09], [0.075, -0.03], [0.07, 0.0], [0.0, 0.01]].map(([r, y]) => new THREE.Vector2(r, y));
    const bd = new THREE.Mesh(new THREE.LatheGeometry(prof, 20), new THREE.MeshStandardMaterial({ map: t, roughness: 0.95 }));
    bd.scale.set(1.15, 1, 0.55); const p = h.clone().add(V(0, -0.0, 0)).add(F.clone().multiplyScalar(0.06)); attach(B.Head, bd, p, new THREE.Quaternion().setFromUnitVectors(V(0, 0, 1), F));
    const mu = new THREE.Mesh(new THREE.TorusGeometry(0.03, 0.009, 6, 16, Math.PI), bd.material); attach(B.Head, mu, h.clone().add(V(0, 0.035, 0)).add(F.clone().multiplyScalar(0.095)), new THREE.Quaternion().setFromUnitVectors(V(0, 0, 1), F)); }
  if (L.tilak || L.mustache) { const h = wpos(B.Head); const lat = wpos(B.RightUpLeg).sub(wpos(B.LeftUpLeg)).setY(0).normalize(); const F = V(0, 1, 0).cross(lat).normalize();
    const pts = restVerts(o).filter((p) => Math.abs(p.clone().sub(h).dot(lat)) < 0.012 && p.y > h.y - 0.05 && p.y < h.y + 0.16); const front = (y) => { let f = 0; for (const p of pts) if (Math.abs(p.y - y) < 0.012) f = Math.max(f, p.clone().sub(h).dot(F)); return f; };
    if (L.tilak) { const yy = h.y + 0.105; const tk = new THREE.Mesh(new THREE.PlaneGeometry(0.008, 0.03), new THREE.MeshStandardMaterial({ color: 0xb00020, roughness: 0.5, polygonOffset: true, polygonOffsetFactor: -4 }));
      attach(B.Head, tk, h.clone().setY(yy).add(F.clone().multiplyScalar(front(yy) + 0.004)), new THREE.Quaternion().setFromUnitVectors(V(0, 0, 1), F.clone().add(V(0, 0.35, 0)).normalize())); }
    if (L.mustache) { const yy = h.y + 0.012; const mm = new THREE.Mesh(new THREE.TorusGeometry(0.026, 0.005, 6, 16, Math.PI), new THREE.MeshStandardMaterial({ color: L.mustache, roughness: 0.9 }));
      attach(B.Head, mm, h.clone().setY(yy).add(F.clone().multiplyScalar(front(yy) + 0.002)), new THREE.Quaternion().setFromUnitVectors(V(0, 0, 1), F)); } }
  if (L.quiver) { const q = new THREE.Mesh(new THREE.CylinderGeometry(0.06, 0.05, 0.6, 14), new THREE.MeshStandardMaterial({ color: 0x6a2a12, roughness: 0.6 })); const sp = wpos(B.Spine2);
    for (let i = 0; i < 6; i++) { const a = arrow(); a.rotation.x = -Math.PI / 2; a.position.set((i % 3 - 1) * 0.02, 0.45, (Math.floor(i / 3) - 0.5) * 0.02); q.add(a); }
    attach(B.Spine2, q, sp.clone().add(V(0.08, 0.02, -0.17)), new THREE.Quaternion().setFromEuler(new THREE.Euler(0, 0, -0.35))); }
  if (light) { // divine light form: glowing rim (fresnel), translucent golden body, no surface detail
    const col = new THREE.Color(female ? 0xa8d8ff : 0xffc060);
    const lm = new THREE.MeshStandardMaterial({ color: col, transparent: true, opacity: 0.16 * light + 0.06, blending: THREE.AdditiveBlending, depthWrite: false, side: THREE.FrontSide });
    lm.onBeforeCompile = (sh) => { sh.fragmentShader = sh.fragmentShader.replace('#include <opaque_fragment>',
      'float fr = pow(1.0 - abs(dot(normalize(normal), normalize(vViewPosition))), 2.2); outgoingLight = diffuse * (0.6 + 3.2 * fr); diffuseColor.a = opacity * (0.35 + 2.6 * fr);\n#include <opaque_fragment>'); };
    o.traverse((m) => { if (m.isMesh) { m.material = lm; m.castShadow = false; m.receiveShadow = false; m.renderOrder = 2; } }); }
  epicPose(o, B, poseName, phase);
  if (L.bow && /bow/.test(poseName)) { const b = bow(); const h = wpos(B.LeftHand); B.LeftHand.updateMatrixWorld(true);
    const lat = wpos(B.RightUpLeg).sub(wpos(B.LeftUpLeg)).setY(0).normalize(); const F = V(0, 1, 0).cross(lat).normalize();
    const q = new THREE.Quaternion().setFromUnitVectors(V(0, 0, -1), lat.clone().negate()); if (poseName === 'bowrest') q.setFromUnitVectors(V(0, 0, -1), F.clone().negate());
    attach(B.LeftHand, b, h.clone().add(lat.clone().multiplyScalar(-0.04)), q);
    if (poseName === 'bowdraw') { const a = arrow(); const rh = wpos(B.RightHand); const dir = h.clone().sub(rh).normalize(); const aq = new THREE.Quaternion().setFromUnitVectors(V(0, 0, 1), dir);
      const ap = rh.clone().add(dir.clone().multiplyScalar(0.35)); o.add(a); a.position.copy(o.worldToLocal(ap)); a.quaternion.copy(aq); } }
  o.userData.B = B; return o;
}
