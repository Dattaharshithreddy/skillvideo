// Indian attire + procedural poses for MakeHuman (mixamo rig) people.
// dhoti/pancha and saree skirts are skinned "hull wraps" built from the body's own rest-pose vertices.
import * as THREE from 'three';
import { GLTFLoader } from 'three/addons/loaders/GLTFLoader.js';
import * as SkeletonUtils from 'three/addons/utils/SkeletonUtils.js';
const gl = new GLTFLoader(); const cache = {};
const load = (p) => (cache[p] ??= gl.loadAsync(p));
const strip = (n) => n.replace(/_\d+$/, '').replace(/^mixamorig:?/, '');
const V = (x = 0, y = 0, z = 0) => new THREE.Vector3(x, y, z);

export function clothTex(base, border, border2, stripes = false, pleats = false) {
  const c = document.createElement('canvas'); c.width = 64; c.height = 512; const x = c.getContext('2d');
  x.fillStyle = base; x.fillRect(0, 0, 64, 512);
  if (stripes) for (let i = 0; i < 512; i += 6) { x.fillStyle = 'rgba(0,0,0,0.035)'; x.fillRect(0, i, 64, 2); }
  for (let i = 0; i < 4000; i++) { x.fillStyle = `rgba(${Math.random() < 0.5 ? '0,0,0' : '255,255,255'},0.04)`; x.fillRect(Math.random() * 64, Math.random() * 512, 1, 1); }
  if (pleats) for (let i = 0; i < 7; i++) { const px = 9 + i * 1.6; x.fillStyle = 'rgba(0,0,0,0.06)'; x.fillRect(px, 0, 0.6, 512); x.fillStyle = 'rgba(255,255,255,0.06)'; x.fillRect(px + 0.6, 0, 0.6, 512); }
  if (border) { x.fillStyle = border; x.fillRect(0, 512 - 46, 64, 34); if (border2) { x.fillStyle = border2; x.fillRect(0, 512 - 40, 64, 4); x.fillRect(0, 512 - 20, 64, 4); } }
  const t = new THREE.CanvasTexture(c); t.colorSpace = THREE.SRGBColorSpace; t.wrapS = THREE.RepeatWrapping; return t;
}
const plain = (col, rough = 0.85, sheen = 0) => new THREE.MeshPhysicalMaterial({ color: col, roughness: rough, sheen, sheenColor: new THREE.Color(col), side: THREE.DoubleSide });

export function restVerts(o) { // world-space rest positions of every skinned mesh vertex
  const pts = []; o.updateMatrixWorld(true);
  o.traverse((m) => { if (!m.isMesh || m.userData.wrap) return; const p = m.geometry.attributes.position; const v = V();
    for (let i = 0; i < p.count; i += 2) { m.getVertexPosition(i, v); pts.push(v.clone().applyMatrix4(m.matrixWorld)); } });
  return pts;
}
export function hullRing(pts, y0, y1, n, margin, center) { // support-function ring of points between heights
  const sel = pts.filter((p) => p.y >= y0 && p.y < y1 && (!center || Math.hypot(p.x - center.x, p.z - center.z) < 0.27)); const c = center || sel.reduce((a, p) => a.add(p), V()).multiplyScalar(1 / Math.max(1, sel.length));
  const ring = []; for (let k = 0; k < n; k++) { const a = (k / n) * Math.PI * 2, d = V(Math.cos(a), 0, Math.sin(a));
    let r = 0.05; for (const p of sel) r = Math.max(r, (p.x - c.x) * d.x + (p.z - c.z) * d.z); ring.push(r + margin); }
  return { c, ring };
}
export function boneMap(o) { const m = {}; o.traverse((b) => { if (b.isBone) m[strip(b.name)] = b; }); return m; }
const wpos = (b) => b.getWorldPosition(V());

// Builds a skinned wrap from waist (yTop) to hem (yBot). kind: 'dhoti' | 'saree'
export function wrap(o, B, target, kind, mat) {
  const pts = restVerts(o); const yTop = wpos(B.Hips).y + (kind === 'saree' ? 0.04 : 0.02);
  const yAnk = wpos(B.LeftFoot).y; const yBot = kind === 'saree' ? yAnk - 0.06 : yAnk + 0.02;
  const N = 40, H = 18; const pos = [], uv = [], si = [], sw = [], idx = [];
  const BI = target.skeleton.bones; const bi = (n) => BI.indexOf(B[n]);
  const hips = bi('Hips'), lu = bi('LeftUpLeg'), ll = bi('LeftLeg'), ru = bi('RightUpLeg'), rl = bi('RightLeg'), sp = bi('Spine');
  const cx = (wpos(B.LeftUpLeg).x + wpos(B.RightUpLeg).x) / 2, cz = (wpos(B.LeftUpLeg).z + wpos(B.RightUpLeg).z) / 2;
  const kneeY = wpos(B.LeftLeg).y; const lx = wpos(B.LeftUpLeg).x > cx ? 1 : -1; // which world-x side is the character's left
  let kneeRing = null;
  for (let h = 0; h <= H; h++) { const t = h / H; const y = THREE.MathUtils.lerp(yTop, yBot, t);
    const band = 0.06; const { ring } = hullRing(pts, Math.max(y - band, yBot), y + band, N, 0.02 + t * (kind === 'saree' ? 0.025 : 0.015), V(cx, 0, cz));
    if (y > kneeY - 0.05) kneeRing = ring.slice(); else if (kneeRing) for (let k = 0; k < N; k++) ring[k] = Math.min(ring[k], kneeRing[k] * (1 + (kind === 'saree' ? 0.18 : 0.08) * t));
    for (let k = 0; k <= N; k++) { const a = (k / N) * Math.PI * 2, r = ring[k % N];
      const x = cx + Math.cos(a) * r, z = cz + Math.sin(a) * r; pos.push(x, y, z); uv.push(k / N, 1 - t);
      const side = THREE.MathUtils.smoothstep((x - cx) * lx, -0.05, 0.05); // 1 = left leg
      const up = y > kneeY ? 1 : 0; const legW = THREE.MathUtils.smoothstep(t, 0.05, 0.45) * (kind === 'saree' ? 0.12 : 1);
      const hipW = 1 - legW; const L = up ? lu : ll, R = up ? ru : rl;
      si.push(hips, L, R, sp); sw.push(hipW, legW * side, legW * (1 - side), 0); } }
  for (let h = 0; h < H; h++) for (let k = 0; k < N; k++) { const a = h * (N + 1) + k, b = a + N + 1; idx.push(a, b, a + 1, b, b + 1, a + 1); }
    const g = new THREE.BufferGeometry(); const inv = target.matrixWorld.clone().invert(); const P = new Float32Array(pos);
  for (let i = 0; i < P.length; i += 3) { const v = V(P[i], P[i + 1], P[i + 2]).applyMatrix4(inv); P.set([v.x, v.y, v.z], i); }
  g.setAttribute('position', new THREE.BufferAttribute(P, 3)); g.setAttribute('uv', new THREE.Float32BufferAttribute(uv, 2));
  g.setAttribute('skinIndex', new THREE.Uint16BufferAttribute(si, 4)); g.setAttribute('skinWeight', new THREE.Float32BufferAttribute(sw, 4)); g.setIndex(idx); g.computeVertexNormals();
  const m = new THREE.SkinnedMesh(g, mat); m.castShadow = m.receiveShadow = true; m.frustumCulled = false; target.parent.add(m);
  m.position.copy(target.position); m.quaternion.copy(target.quaternion); m.scale.copy(target.scale); m.bind(target.skeleton, target.bindMatrix); return m;
}
// pallu: a ribbon from right hip, across the chest, over the left shoulder, down the back
export function pallu(o, B, target, mat) {
  const pts = restVerts(o); const L = wpos(B.LeftArm), R = wpos(B.RightArm), hip = wpos(B.Hips); const c = V((L.x + R.x) / 2, 0, (L.z + R.z) / 2);
  const lat = R.clone().sub(L).setY(0).normalize(); const fwd = V(0, 1, 0).cross(lat).normalize(); // forward
  const surf = (y, dir, off) => { const sel = pts.filter((p) => Math.abs(p.y - y) < 0.03 && Math.abs((p.x - c.x) * -dir.z + (p.z - c.z) * dir.x) < 0.06);
    let r = 0.1; for (const p of sel) r = Math.max(r, (p.x - c.x) * dir.x + (p.z - c.z) * dir.z); return V(c.x + dir.x * (r + off), y, c.z + dir.z * (r + off)); };
  const shY = L.y + 0.07; const path = [];
  const S = 16; for (let i = 0; i <= S; i++) { const s = i / S; const y = THREE.MathUtils.lerp(hip.y + 0.02, shY - 0.06, s);
    const dir = fwd.clone().multiplyScalar(1).add(lat.clone().multiplyScalar(THREE.MathUtils.lerp(0.55, -0.75, s))).normalize(); path.push(surf(y, dir, 0.012 + 0.008 * s)); }
  const top = L.clone().add(V(0, 0.09, 0)).add(lat.clone().multiplyScalar(0.03)); path.push(top);
  for (let i = 1; i <= 12; i++) { const s = i / 12; const y = THREE.MathUtils.lerp(shY - 0.04, hip.y - 0.22, s);
    const dir = fwd.clone().multiplyScalar(-1).add(lat.clone().multiplyScalar(-0.75 + 0.3 * s)).normalize(); path.push(surf(y, dir, 0.03 + 0.02 * s)); }
  const W = 0.17; const pos = [], uv = [], si = [], sw = [], idx = []; const BI = target.skeleton.bones;
  const sp2 = BI.indexOf(B.Spine2), sp = BI.indexOf(B.Spine), ls = BI.indexOf(B.LeftShoulder), hp = BI.indexOf(B.Hips);
  for (let i = 0; i < path.length; i++) { const p = path[i], q = path[Math.min(i + 1, path.length - 1)], p0 = path[Math.max(i - 1, 0)];
    const tan = q.clone().sub(p0).normalize(); const out = p.clone().sub(c).setY(0).normalize(); const side = tan.clone().cross(out).normalize();
    const w = W * (i < 17 ? 0.75 : 1);
    for (const s of [-0.5, 0.5]) { const v = p.clone().add(side.clone().multiplyScalar(s * w)); pos.push(v.x, v.y, v.z); uv.push(s + 0.5, i / path.length); }
    const yN = (p.y - hip.y) / (shY - hip.y); const top2 = Math.abs(i - 17) < 3 ? 1 : 0;
    for (let j = 0; j < 2; j++) { si.push(sp2, sp, ls, hp); sw.push(yN > 0.5 ? 0.8 - top2 * 0.4 : 0.3, yN > 0.5 ? 0.2 : 0.4, top2 * 0.4, yN > 0.5 ? 0 : 0.3); } }
  for (let i = 0; i < path.length - 1; i++) { const a = i * 2; idx.push(a, a + 2, a + 1, a + 1, a + 2, a + 3); }
  const g = new THREE.BufferGeometry(); const inv = target.matrixWorld.clone().invert(); const P = new Float32Array(pos);
  for (let i = 0; i < P.length; i += 3) { const v = V(P[i], P[i + 1], P[i + 2]).applyMatrix4(inv); P.set([v.x, v.y, v.z], i); }
  g.setAttribute('position', new THREE.BufferAttribute(P, 3)); g.setAttribute('uv', new THREE.Float32BufferAttribute(uv, 2));
  g.setAttribute('skinIndex', new THREE.Uint16BufferAttribute(si, 4)); g.setAttribute('skinWeight', new THREE.Float32BufferAttribute(sw, 4)); g.setIndex(idx); g.computeVertexNormals();
  const m = new THREE.SkinnedMesh(g, mat); m.castShadow = m.receiveShadow = true; m.frustumCulled = false; target.parent.add(m);
  m.position.copy(target.position); m.quaternion.copy(target.quaternion); m.scale.copy(target.scale); m.bind(target.skeleton, target.bindMatrix); return m;
}

// --- poses (aim bones at world directions in the body frame) ---
export function aim(bone, child, dir) {
  const a = wpos(bone), b = wpos(child); const cur = b.sub(a).normalize();
  const q = new THREE.Quaternion().setFromUnitVectors(cur, dir.clone().normalize());
  const w = q.multiply(bone.getWorldQuaternion(new THREE.Quaternion()));
  const pw = bone.parent.getWorldQuaternion(new THREE.Quaternion()).invert(); bone.quaternion.copy(pw.multiply(w)); bone.updateMatrixWorld(true);
}
export function pose(o, B, name, ph = 0) {
  o.updateMatrixWorld(true);
  const lat = wpos(B.RightUpLeg).sub(wpos(B.LeftUpLeg)).setY(0).normalize(); // toward character's right
  const F = V(0, 1, 0).cross(lat).normalize(), U = V(0, 1, 0), Rt = lat, Lf = lat.clone().negate();
  const d = (f, u, r) => F.clone().multiplyScalar(f).add(U.clone().multiplyScalar(u)).add(Rt.clone().multiplyScalar(r));
  const s = Math.sin(ph * Math.PI * 2), c2 = Math.cos(ph * Math.PI * 2);
  const leg = (sd, sw) => { const k = sd === 'L' ? -1 : 1; const side = sd === 'L' ? 'Left' : 'Right'; const back = Math.max(0, -sw);
    aim(B[side + 'UpLeg'], B[side + 'Leg'], d(0.42 * sw, -1, 0.02 * k)); aim(B[side + 'Leg'], B[side + 'Foot'], d(0.42 * sw - 0.55 * back - 0.15 * Math.max(0, sw), -1, 0.01 * k));
    if (B[side + 'ToeBase']) aim(B[side + 'Foot'], B[side + 'ToeBase'], d(1, -0.35 + 0.3 * back, 0)); };
  const arm = (sd, upper, fore, hand) => { const side = sd === 'L' ? 'Left' : 'Right'; aim(B[side + 'Arm'], B[side + 'ForeArm'], upper); aim(B[side + 'ForeArm'], B[side + 'Hand'], fore);
    const mid = B[side + 'HandMiddle1']; if (mid && hand) aim(B[side + 'Hand'], mid, hand); };
  if (name === 'walk') { leg('L', s); leg('R', -s);
    arm('L', d(-0.3 * s, -1, -0.1), d(-0.3 * s + 0.35, -1, -0.05), d(0.1, -1, 0)); arm('R', d(0.3 * s, -1, 0.1), d(0.3 * s + 0.35, -1, 0.05), d(0.1, -1, 0));
    B.Hips.position.y += 0; }
  else { leg('L', 0); leg('R', 0);
    if (name === 'namaskaram') { arm('L', d(0.35, -1, -0.12), d(0.55, 0.85, 1.05), d(0.25, 1, 0.1)); arm('R', d(0.35, -1, 0.12), d(0.55, 0.85, -1.05), d(0.25, 1, -0.1)); }
    else if (name === 'folded') { arm('L', d(0.2, -1, -0.2), d(0.6, 0.1, 0.8), null); arm('R', d(0.22, -1, 0.2), d(0.6, 0.15, -0.8), null); }
    else { arm('L', d(0.03, -1, -0.12), d(0.15, -1, -0.03), d(0.05, -1, 0)); arm('R', d(0.03, -1, 0.12), d(0.15, -1, 0.03), d(0.05, -1, 0)); } }
  aim(B.Spine, B.Spine1 || B.Spine2, d(0.05, 1, 0));
  o.updateMatrixWorld(true);
}

// --- outfits ---
const SHIRTS = ['#f4f1e8', '#ece4cf', '#dfe8f0', '#f2efe9', '#e9dcc0', '#cfdde6', '#f6f3ee'];
const SAREES = [['#c2185b', '#e8b33a', '#2e7d32'], ['#e0861a', '#a3141d', '#f2c14e'], ['#1f7a4a', '#e8b33a', '#a3141d'], ['#6a1b9a', '#e8b33a', '#f8d36a'],
  ['#d81b60', '#1b5e20', '#e8b33a'], ['#b71c1c', '#e8b33a', '#e8b33a'], ['#f9a825', '#b71c1c', '#c62828'], ['#0d47a1', '#e8b33a', '#b71c1c']];
export async function devotee(file, { female, seed = 0, poseName = 'stand', phase = 0, light = 0 } = {}) {
  const g = await load(file); const o = globalThis.NOCLONE ? g.scene : SkeletonUtils.clone(g.scene); let target = null;
  o.traverse((m) => { if (!m.isMesh) return; m.castShadow = m.receiveShadow = true; m.frustumCulled = false;
    if (m.isSkinnedMesh && !target) target = m; const mats = Array.isArray(m.material) ? m.material : [m.material];
    if (globalThis.NOMAT) return; m.material = mats.map((t0) => { const t = globalThis.INPLACE ? t0 : t0.clone(); const n = (t.name || '').toLowerCase();
      if (/eyebrow|short|long|bob|ponytail|braid|eyelash|hair|high-poly|low-poly|eye/.test(n)) { t.transparent = false; t.alphaTest = 0.5; } else { t.transparent = false; t.alphaTest = 0; t.opacity = 1; }
      t.depthWrite = true; if (!globalThis.NOTINT && /body|ears/.test(n) && t.color) t.color = new THREE.Color(1.3, 1.16, 1.06);
      if (/short|long|bob|ponytail|braid|hair/.test(n)) t.color = new THREE.Color(0.22, 0.19, 0.17);
      if (/suit/.test(n)) { const col = female ? SAREES[seed % SAREES.length][2] : SHIRTS[seed % SHIRTS.length]; t.map = null; t.normalMap = null; t.roughnessMap = null; t.metalnessMap = null; t.color = new THREE.Color(col); t.roughness = 0.92; t.metalness = 0; t.envMapIntensity = 0.6; }
      return t; });
    if (m.material.length === 1) m.material = m.material[0]; });
  o.updateMatrixWorld(true); const B = boneMap(o); if (globalThis.RAW) { o.traverse((m) => { if (m.isMesh && globalThis.HIDE && new RegExp(globalThis.HIDE).test(m.name)) m.visible = false; if (m.isMesh) console.log('mesh', m.name, (Array.isArray(m.material)?m.material:[m.material]).map(t=>t.name+':'+t.type+':'+(t.map?1:0)).join(' ')); }); return o; }
  if (!female) { wrap(o, B, target, 'dhoti', new THREE.MeshPhysicalMaterial({ map: clothTex(seed % 4 === 3 ? '#efe3c8' : '#f5f2ea', seed % 3 ? '#c99a2e' : '#9c1c1c', null, true, true), roughness: 0.9, side: THREE.DoubleSide })); }
  else { const [base, border, blouse] = SAREES[seed % SAREES.length]; const m = new THREE.MeshPhysicalMaterial({ map: clothTex(base, border, '#f3d27a', false, true), roughness: 0.55, sheen: 0.6, sheenColor: new THREE.Color(border), side: THREE.DoubleSide });
    wrap(o, B, target, 'saree', m); const pm = new THREE.MeshPhysicalMaterial({ map: clothTex(base, border, '#f3d27a'), roughness: 0.55, sheen: 0.6, sheenColor: new THREE.Color(border), side: THREE.DoubleSide }); pallu(o, B, target, pm); }
  if (light) { const lm = new THREE.MeshStandardMaterial({ color: 0xffd27a, emissive: 0xffa630, emissiveIntensity: light, metalness: 0.2, roughness: 0.55 });
    o.traverse((m) => { if (m.isMesh) { m.material = lm; m.castShadow = false; } if (m.isMesh && /eyebrow|high-poly|low-poly/i.test(m.name)) m.visible = false; }); }
  if (!globalThis.NOPOSE) pose(o, B, poseName, phase); if (globalThis.HIDEBODY) target.visible = false; return o;
}
