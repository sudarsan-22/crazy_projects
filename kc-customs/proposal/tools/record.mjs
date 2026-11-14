// Record the presenter page with Chrome's screencast and build an MP4 with per-scene voice-over.
// usage: node record.mjs <lang en|ta> <outDir>
import { spawn, execFileSync } from 'node:child_process';
import { writeFileSync, mkdirSync, readFileSync } from 'node:fs';
import { homedir } from 'node:os';

const [lang, out] = process.argv.slice(2);
const HERE = new URL('.', import.meta.url).pathname;
const script = JSON.parse(readFileSync('/home/sudarsan/Documents/crazy_projects/kc-customs/proposal/script.json', 'utf8'));
const frames = `${out}/frames`; mkdirSync(frames, { recursive: true });
const dur = (f) => parseFloat(execFileSync('ffprobe', ['-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0', f]).toString());

const CHROME = homedir() + '/.cache/ms-playwright/chromium-1234/chrome-linux64/chrome';
const port = 9555;
const chrome = spawn(CHROME, ['--headless=new', '--no-sandbox', '--hide-scrollbars', '--autoplay-policy=no-user-gesture-required', `--remote-debugging-port=${port}`, `--user-data-dir=${out}/profile`, '--window-size=1920,1223', 'about:blank'], { stdio: 'ignore' });
const sleep = (ms) => new Promise((r) => setTimeout(r, ms));
let ws; for (let i = 0; i < 60; i++) { try { const l = await (await fetch(`http://127.0.0.1:${port}/json/list`)).json(); const p = l.find((t) => t.type === 'page'); if (p) { ws = new WebSocket(p.webSocketDebuggerUrl); break; } } catch {} await sleep(200); }
await new Promise((r) => ws.addEventListener('open', r));
let id = 0; const pend = new Map(); const shots = [];
ws.addEventListener('message', (m) => {
  const d = JSON.parse(m.data);
  if (d.id && pend.has(d.id)) { pend.get(d.id)(d); pend.delete(d.id); return; }
  if (d.method === 'Page.screencastFrame') {
    const n = shots.length; const f = `${frames}/f${String(n).padStart(6, '0')}.jpg`;
    writeFileSync(f, Buffer.from(d.params.data, 'base64')); shots.push({ f, t: d.params.metadata.timestamp });
    ws.send(JSON.stringify({ id: ++id, method: 'Page.screencastFrameAck', params: { sessionId: d.params.sessionId } }));
  }
  if (d.method === 'Runtime.exceptionThrown') console.error('EXC', JSON.stringify(d.params.exceptionDetails).slice(0, 400));
});
const send = (method, params = {}) => new Promise((r) => { const i = ++id; pend.set(i, r); ws.send(JSON.stringify({ id: i, method, params })); });
const ev = async (expression) => { const r = await send('Runtime.evaluate', { expression, awaitPromise: true, returnByValue: true }); if (r.result?.exceptionDetails) console.error('EVAL', JSON.stringify(r.result.exceptionDetails).slice(0, 300)); return r.result?.result?.value; };

await send('Page.enable'); await send('Runtime.enable');
await send('Emulation.setDeviceMetricsOverride', { width: 1920, height: 1080, deviceScaleFactor: 1, mobile: false });
await send('Page.navigate', { url: 'http://localhost:8000/_presenter.html' }); await sleep(2500);
await ev(`setup(${JSON.stringify(lang)})`); await sleep(1500);
await send('Page.startScreencast', { format: 'jpeg', quality: 85, maxWidth: 1920, maxHeight: 1080, everyNthFrame: 1 });
await sleep(600);
const marks = [];
for (const s of script) {
  const a = `${HERE}audio/${s.id}-${lang}.mp3`;
  const ms = Math.round((dur(a) + 0.7) * 1000);
  const t0 = Date.now() / 1000; marks.push({ id: s.id, t0, a, ms });
  await ev(`run(${JSON.stringify(s.act)}, ${JSON.stringify(s['cap_' + lang])}, ${ms}, ${JSON.stringify(lang)})`);
  const left = ms - (Date.now() / 1000 - t0) * 1000; if (left > 0) await sleep(left);
  console.log(s.id, 'planned', ms, 'actual', Math.round((Date.now() / 1000 - t0) * 1000));
}
await sleep(1200);
await send('Page.stopScreencast'); await sleep(500);
ws.close(); chrome.kill();

// ---- write frame list + marks, then assemble
const T0 = shots[0].t;
let list = 'ffconcat version 1.0\n';
for (let i = 0; i < shots.length; i++) {
  const d = i < shots.length - 1 ? Math.max(0.001, shots[i + 1].t - shots[i].t) : 1.2;
  list += `file '${shots[i].f}'\nduration ${d.toFixed(4)}\n`;
}
list += `file '${shots[shots.length - 1].f}'\n`;
writeFileSync(`${out}/frames.txt`, list);
writeFileSync(`${out}/marks.json`, JSON.stringify(marks.map((m) => ({ id: m.id, a: m.a, off: Math.max(0, Math.round((m.t0 - T0) * 1000) + 250) }))));
execFileSync('node', [HERE + 'assemble.mjs', lang, out], { stdio: 'inherit' });
process.exit(0);
