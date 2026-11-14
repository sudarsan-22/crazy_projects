// Record the full-site tour (music only). usage: node tour-record.mjs <music.wav> <outDir> <out.mp4>
import { spawn, execFileSync } from 'node:child_process';
import { writeFileSync, mkdirSync, readFileSync } from 'node:fs';
import { homedir } from 'node:os';
const [music, out, outFile, scenesFile = 'tour-scenes.json', bpm = '110', speed = '1'] = process.argv.slice(2);
const HERE = new URL('.', import.meta.url).pathname;
const scenes = JSON.parse(readFileSync(HERE + scenesFile, 'utf8'));
const BAR = 60 / +bpm * 4;
const frames = `${out}/frames`; mkdirSync(frames, { recursive: true });
const CHROME = homedir() + '/.cache/ms-playwright/chromium-1234/chrome-linux64/chrome';
const port = 9566;
const chrome = spawn(CHROME, ['--headless=new', '--no-sandbox', '--hide-scrollbars', '--mute-audio', `--remote-debugging-port=${port}`, `--user-data-dir=${out}/profile`, '--window-size=1920,1223', 'about:blank'], { stdio: 'ignore' });
const sleep = (ms) => new Promise((r) => setTimeout(r, ms));
let ws; for (let i = 0; i < 60; i++) { try { const l = await (await fetch(`http://127.0.0.1:${port}/json/list`)).json(); const p = l.find((t) => t.type === 'page'); if (p) { ws = new WebSocket(p.webSocketDebuggerUrl); break; } } catch {} await sleep(200); }
await new Promise((r) => ws.addEventListener('open', r));
let id = 0; const pend = new Map(); const shots = [];
ws.addEventListener('message', (m) => {
  const d = JSON.parse(m.data);
  if (d.id && pend.has(d.id)) { pend.get(d.id)(d); pend.delete(d.id); return; }
  if (d.method === 'Page.screencastFrame') {
    const f = `${frames}/f${String(shots.length).padStart(6, '0')}.jpg`;
    writeFileSync(f, Buffer.from(d.params.data, 'base64')); shots.push({ f, t: d.params.metadata.timestamp });
    ws.send(JSON.stringify({ id: ++id, method: 'Page.screencastFrameAck', params: { sessionId: d.params.sessionId } }));
  }
});
const send = (method, params = {}) => new Promise((r) => { const i = ++id; pend.set(i, r); ws.send(JSON.stringify({ id: i, method, params })); });
const ev = async (expression) => { const r = await send('Runtime.evaluate', { expression, awaitPromise: true, returnByValue: true }); if (r.result?.exceptionDetails) console.error('EVAL', JSON.stringify(r.result.exceptionDetails).slice(0, 400)); return r.result?.result?.value; };
await send('Page.enable'); await send('Runtime.enable');
await send('Emulation.setDeviceMetricsOverride', { width: 1920, height: 1080, deviceScaleFactor: 1, mobile: false });
await send('Page.navigate', { url: 'http://localhost:8000/_tour.html?speed=' + speed }); await sleep(2500);
await ev('setup()'); await sleep(800);
await send('Page.startScreencast', { format: 'jpeg', quality: 85, maxWidth: 1920, maxHeight: 1080, everyNthFrame: 1 });
await sleep(400);
const start = Date.now() / 1000; let bar = 0;
for (const s of scenes) {
  const t0 = start + bar * BAR, ms = Math.round(s.bars * BAR * 1000);
  const wait = (t0 - Date.now() / 1000) * 1000; if (wait > 0) await sleep(wait);
  const late = Math.round(Date.now() / 1000 * 1000 - t0 * 1000);
  await ev(`run(${JSON.stringify(s.act)}, ${JSON.stringify(s.en)}, ${JSON.stringify(s.ta)}, ${ms - Math.max(0, late)})`);
  console.log(s.act, 'late', late, 'ms');
  bar += s.bars;
}
const end = start + bar * BAR + 1.5; const w = (end - Date.now() / 1000) * 1000; if (w > 0) await sleep(w);
await send('Page.stopScreencast'); await sleep(400); ws.close(); chrome.kill();
// frames → video aligned to `start`
let list = 'ffconcat version 1.0\n';
const first = shots.findIndex((x) => x.t >= start); const S = shots.slice(Math.max(0, first - 1));
for (let i = 0; i < S.length; i++) { const t = i === 0 ? start : S[i].t; const d = i < S.length - 1 ? Math.max(0.001, S[i + 1].t - t) : Math.max(1, start + bar * BAR + 1.5 - t); list += `file '${S[i].f}'\nduration ${d.toFixed(4)}\n`; }
list += `file '${S[S.length - 1].f}'\n`;
writeFileSync(`${out}/frames.txt`, list);
const total = (bar * BAR + 1.5).toFixed(2);
execFileSync('ffmpeg', ['-y', '-v', 'error', '-f', 'concat', '-safe', '0', '-i', `${out}/frames.txt`, '-vf', 'fps=30,format=yuv420p', '-t', total, '-c:v', 'libx264', '-preset', 'medium', '-crf', '19', `${out}/video.mp4`], { stdio: 'inherit' });
execFileSync('ffmpeg', ['-y', '-v', 'error', '-i', `${out}/video.mp4`, '-i', music, '-map', '0:v', '-map', '1:a', '-af', `afade=t=out:st=${(+total - 2).toFixed(2)}:d=2`, '-t', total, '-c:v', 'copy', '-c:a', 'aac', '-b:a', '192k', '-movflags', '+faststart', outFile], { stdio: 'inherit' });
console.log('done', outFile, total + 's');
process.exit(0);
