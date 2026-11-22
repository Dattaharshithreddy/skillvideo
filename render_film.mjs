// node render_film.mjs film.json W H FPS K N outdir  -> renders frames i where i % N == K (strided so every slice gets a mix of shots)
import puppeteer from 'puppeteer-core'; import http from 'node:http'; import fs from 'node:fs'; import path from 'node:path';
const [film, W, H, FPS, K, N, out] = [JSON.parse(fs.readFileSync(process.argv[2])), +process.argv[3], +process.argv[4], +process.argv[5], +process.argv[6], +process.argv[7], process.argv[8]];
fs.mkdirSync(out, { recursive: true });
const types = { '.html': 'text/html', '.js': 'text/javascript', '.json': 'application/json', '.jpg': 'image/jpeg', '.png': 'image/png', '.bin': 'application/octet-stream', '.glb': 'model/gltf-binary', '.gltf': 'model/gltf+json', '.hdr': 'application/octet-stream' };
const port = 8200 + K; const srv = http.createServer((q, r) => { const f = path.join(process.cwd(), decodeURIComponent(q.url.split('?')[0])); if (!fs.existsSync(f)) { r.writeHead(404); return r.end(); } r.writeHead(200, { 'Content-Type': types[path.extname(f)] || 'application/octet-stream' }); fs.createReadStream(f).pipe(r); }).listen(port);
const b = await puppeteer.launch({ executablePath: process.env.CHROME || '/usr/bin/google-chrome', args: ['--no-sandbox', '--use-angle=swiftshader', '--enable-unsafe-swiftshader', '--ignore-gpu-blocklist'] });
const total = Math.round(film.duration * FPS); let n = 0; const t0 = Date.now();
for (let i = K; i < total; i += N) {
  const fn = `${out}/f${String(i).padStart(5, '0')}.png`; if (fs.existsSync(fn)) continue;
  const tau = i / FPS; const sh = film.shots.find((s) => tau >= s.s && tau < s.e) || film.shots.at(-1);
  const q = `${sh.q}&w=${W}&h=${H}&t=${(tau - sh.s).toFixed(4)}&dur=${(sh.e - sh.s).toFixed(3)}`;
  const p = await b.newPage(); await p.setViewport({ width: W, height: H }); p.on('pageerror', (e) => console.log('ERR', sh.page, e.message));
  try { await p.goto(`http://localhost:${port}/${sh.page}?${q}`); await p.waitForFunction('window.DONE', { timeout: 120000 }); await (await p.$('canvas')).screenshot({ path: fn }); n++; }
  catch (e) { console.log('FAIL', i, sh.page, e.message); }
  await p.close();
  if (n % 25 === 0) console.log(`slice ${K}/${N}: ${n} frames, ${((Date.now() - t0) / n / 1000).toFixed(1)} s/frame`);
}
await b.close(); srv.close(); console.log('SLICE_DONE', K, n);
