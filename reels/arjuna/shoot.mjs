import puppeteer from 'puppeteer-core'; import http from 'node:http'; import fs from 'node:fs'; import path from 'node:path';
const types = { '.html': 'text/html', '.js': 'text/javascript', '.json': 'application/json', '.jpg': 'image/jpeg', '.png': 'image/png', '.bin': 'application/octet-stream', '.glb': 'model/gltf-binary', '.gltf': 'model/gltf+json', '.hdr': 'application/octet-stream' };
const srv = http.createServer((q, r) => { const f = path.join(process.cwd(), decodeURIComponent(q.url.split('?')[0])); if (!fs.existsSync(f)) { r.writeHead(404); return r.end(); } r.writeHead(200, { 'Content-Type': types[path.extname(f)] || 'application/octet-stream' }); fs.createReadStream(f).pipe(r); }).listen(8123);
const b = await puppeteer.launch({ executablePath: '/usr/bin/google-chrome', args: ['--no-sandbox', '--use-angle=swiftshader', '--enable-unsafe-swiftshader', '--ignore-gpu-blocklist'] });
for (const [page_, q, out] of JSON.parse(process.argv[2])) {
  const p = await b.newPage(); const [w, h] = [Number(new URLSearchParams(q).get('w') || 1080), Number(new URLSearchParams(q).get('h') || 1920)];
  await p.setViewport({ width: w, height: h }); p.on('console', (m) => console.log('pg', m.text())); p.on('pageerror', (e) => console.log('ERR', e.message));
  await p.goto(`http://localhost:8123/${page_}?${q}`); await p.waitForFunction('window.DONE', { timeout: 900000 });
  await (await p.$('canvas')).screenshot({ path: out }); console.log('saved', out); await p.close();
}
await b.close(); srv.close();
