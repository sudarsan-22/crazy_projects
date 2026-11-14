// Original instrumental for the KC Customs showcase video (synthesised from scratch → no licensing issues).
// 110 BPM, A minor, Am–F–C–G. usage: node music.mjs <out.wav> [bars=75]
import { writeFileSync } from 'node:fs';
const out = process.argv[2] || 'music.wav';
const BARS = +(process.argv[3] || 75);
const BPM = +(process.argv[4] || 110);
const SECT = process.argv[5] ? JSON.parse(process.argv[5]) : null;
const SR = 44100, BEAT = 60 / BPM, BAR = BEAT * 4;
const N = Math.ceil((BARS * BAR + 3) * SR);
const L = new Float32Array(N), R = new Float32Array(N);
const midi = (m) => 440 * Math.pow(2, (m - 69) / 12);
let seed = 7; const rnd = () => (seed = (seed * 16807) % 2147483647) / 2147483647 * 2 - 1;

// sections (bar indices)
const S = SECT || { intro: [0, 8], build: [8, 16], mainA: [16, 40], brk: [40, 48], mainB: [48, 69], outro: [69, BARS] };
const inS = (b, k) => b >= S[k][0] && b < S[k][1];
const CH = [[57, 60, 64], [53, 57, 60], [48, 52, 55], [55, 59, 62]]; // Am F C G (root position)
const ROOT = [45, 41, 36, 43];

// sidechain envelope (driven by kick hits)
const duck = new Float32Array(N).fill(1);
function addDuck(t0) { const s = Math.floor(t0 * SR); for (let i = 0; i < SR * 0.3 && s + i < N; i++) { const k = i / (SR * 0.3); duck[s + i] = Math.min(duck[s + i], 0.35 + 0.65 * k * k); } }

function addBuf(t0, buf, gl, gr) { const s = Math.floor(t0 * SR); for (let i = 0; i < buf.length && s + i < N; i++) { L[s + i] += buf[i] * gl; R[s + i] += buf[i] * gr; } }

// ---------- instruments ----------
function kick() { const n = SR * 0.45, b = new Float32Array(n); let ph = 0; for (let i = 0; i < n; i++) { const t = i / SR; const f = 45 + 110 * Math.exp(-t * 28); ph += 2 * Math.PI * f / SR; b[i] = Math.sin(ph) * Math.exp(-t * 7) + (i < 200 ? rnd() * 0.3 * (1 - i / 200) : 0); } return b; }
function clap() { const n = SR * 0.25, b = new Float32Array(n); let lp = 0, prev = 0; for (let i = 0; i < n; i++) { const t = i / SR; const env = (t < .01 ? 1 : 0) + (t > .012 && t < .022 ? .8 : 0) + (t > .024 ? Math.exp(-(t - .024) * 22) : 0); const x = rnd(); lp += 0.35 * (x - lp); const hp = lp - prev; prev = lp; b[i] = hp * env * 1.6; } return b; }
function hat(open) { const n = SR * (open ? 0.18 : 0.05), b = new Float32Array(n); let lp = 0; for (let i = 0; i < n; i++) { const t = i / SR; const x = rnd(); lp += 0.6 * (x - lp); b[i] = (x - lp) * Math.exp(-t * (open ? 18 : 70)); } return b; }
function saw(ph) { return 2 * (ph - Math.floor(ph + 0.5)); }
function pluck(f, dur, bright) { const n = Math.floor(SR * dur), b = new Float32Array(n); let ph = 0, ph2 = 0, lp = 0; for (let i = 0; i < n; i++) { const t = i / SR; ph += f / SR; ph2 += f * 1.004 / SR; const x = saw(ph) * .6 + saw(ph2) * .4; const cut = 0.04 + bright * Math.exp(-t * 9); lp += cut * (x - lp); b[i] = lp * Math.exp(-t * 6) * Math.min(1, t * 400); } return b; }
function padNote(f, dur, cutoff) { const n = Math.floor(SR * dur), bl = new Float32Array(n), br = new Float32Array(n); const det = [-0.012, -0.004, 0.005, 0.011]; const ph = det.map(() => Math.random()); let lpl = 0, lpr = 0; for (let i = 0; i < n; i++) { const t = i / SR; let xl = 0, xr = 0; det.forEach((d, k) => { ph[k] += f * (1 + d) / SR; const v = saw(ph[k]); if (k % 2) xr += v; else xl += v; }); lpl += cutoff * (xl - lpl); lpr += cutoff * (xr - lpr); const env = Math.min(1, t / 0.6) * Math.min(1, (dur - t) / 0.5); bl[i] = lpl * env; br[i] = lpr * env; } return [bl, br]; }
function bassNote(f, dur) { const n = Math.floor(SR * dur), b = new Float32Array(n); let ph = 0, lp = 0; for (let i = 0; i < n; i++) { const t = i / SR; ph += f / SR; const x = Math.sin(2 * Math.PI * ph) * .8 + saw(ph) * .35; lp += 0.08 * (x - lp); b[i] = lp * Math.min(1, t * 200) * Math.exp(-t * 3.5); } return b; }
function leadNote(f, dur) { const n = Math.floor(SR * dur), b = new Float32Array(n); let ph = 0, lp = 0; for (let i = 0; i < n; i++) { const t = i / SR; const vib = 1 + 0.004 * Math.sin(2 * Math.PI * 5.5 * t) * Math.min(1, t * 3); ph += f * vib / SR; const sq = (ph % 1) < 0.5 ? 1 : -1; const x = sq * .5 + saw(ph) * .5; lp += 0.12 * (x - lp); b[i] = lp * Math.min(1, t * 60) * Math.min(1, (dur - t) * 20) * 0.9; } return b; }
function riser(dur) { const n = Math.floor(SR * dur), b = new Float32Array(n); let lp = 0; for (let i = 0; i < n; i++) { const k = i / n; const x = rnd(); lp += (0.02 + 0.5 * k * k) * (x - lp); b[i] = (x - lp) * k * k * 0.9; } return b; }
function impact() { const n = SR * 2.5, b = new Float32Array(n); let ph = 0; for (let i = 0; i < n; i++) { const t = i / SR; ph += (40 + 60 * Math.exp(-t * 6)) / SR; b[i] = Math.sin(2 * Math.PI * ph) * Math.exp(-t * 1.6) * 0.9 + rnd() * Math.exp(-t * 8) * 0.25; } return b; }

const K = kick(), CL = clap(), HC = hat(false), HO = hat(true);
const padL = [], padR = [];
const melody = [[76, 0, 1], [74, 1, .5], [72, 1.5, .5], [71, 2, 1], [72, 3, 1], [69, 4, 1.5], [72, 5.5, .5], [74, 6, 1], [76, 7, 1], [77, 8, 1.5], [76, 9.5, .5], [74, 10, 2], [74, 12, 1], [72, 13, .5], [71, 13.5, .5], [74, 14, 2]]; // 4 bars in beats

for (let b = 0; b < BARS; b++) {
  const t = b * BAR, c = b % 4;
  const full = inS(b, 'mainA') || inS(b, 'mainB');
  // pad
  const cutoff = inS(b, 'intro') ? 0.01 + 0.004 * b * 8 / Math.max(1, S.intro[1]) : inS(b, 'brk') ? 0.02 : 0.035;
  const pg = inS(b, 'outro') ? 0.09 * (1 - (b - S.outro[0]) / (BARS - S.outro[0])) : 0.09;
  CH[c].forEach((m) => { const [bl, br] = padNote(midi(m), BAR + 0.4, cutoff); addBuf(t, bl, pg, pg * .6); addBuf(t, br, pg * .6, pg); });
  // arp (16ths)
  if (!inS(b, 'outro') || b < S.outro[0] + 2) {
    const notes = [...CH[c].map((m) => m + 12), CH[c][1] + 24, CH[c][0] + 24];
    for (let s = 0; s < 16; s++) {
      const m = notes[[0, 1, 2, 3, 2, 1, 4, 2][s % 8]];
      const g = (inS(b, 'intro') ? 0.04 + 0.006 * b : 0.085) * (s % 4 === 0 ? 1.15 : 1);
      const pan = s % 2 ? [0.55, 1] : [1, 0.55];
      addBuf(t + s * BEAT / 4, pluck(midi(m), 0.3, inS(b, 'brk') ? 0.2 : 0.45), g * pan[0], g * pan[1]);
    }
  }
  // drums
  if (inS(b, 'build') || full) {
    for (let q = 0; q < 4; q++) {
      if (inS(b, 'build') && q % 2 && b < S.build[1] - 2) continue;
      addBuf(t + q * BEAT, K, 0.9, 0.9); addDuck(t + q * BEAT);
    }
    for (let e = 0; e < 8; e++) addBuf(t + e * BEAT / 2 + (e % 2 ? 0 : BEAT / 4 * 0), e % 2 ? HO : HC, e % 2 ? 0.12 : 0.09, e % 2 ? 0.09 : 0.12);
    if (full || b >= S.build[1] - 4) { addBuf(t + BEAT, CL, 0.45, 0.45); addBuf(t + 3 * BEAT, CL, 0.45, 0.45); }
    if (full) for (let s = 0; s < 16; s += 2) addBuf(t + s * BEAT / 4 + BEAT / 8, HC, 0.05, 0.06);
  }
  // bass (offbeat 8ths)
  if (inS(b, 'build') && b >= S.build[1] - 4 || full) for (let e = 0; e < 8; e++) { const off = e * BEAT / 2 + BEAT / 4; addBuf(t + off, bassNote(midi(ROOT[c]), BEAT / 2), 0.38, 0.38); }
  // lead
  if (inS(b, 'mainB')) { const phase = (b - S.mainB[0]) % 4; melody.filter((n) => Math.floor(n[1] / 4) === phase).forEach(([m, st, d]) => addBuf(t + (st % 4) * BEAT, leadNote(midi(m), d * BEAT), 0.11, 0.09)); }
  // risers & impacts
  if (b === S.mainA[0] - 2 || b === S.mainB[0] - 2) addBuf(t, riser(BAR * 2), 0.22, 0.22);
  if (b === S.mainA[0] || b === S.mainB[0] || b === S.outro[0]) addBuf(t, impact(), 0.5, 0.5);
}
// final chord hit
addBuf(BARS * BAR - BAR, impact(), 0.45, 0.45);

// sidechain on everything except drums is approximated by ducking the whole mix lightly + pads strongly
for (let i = 0; i < N; i++) { const d = 0.55 + 0.45 * duck[i]; L[i] *= d; R[i] *= d; }
// normalise + soft clip
let pk = 0; for (let i = 0; i < N; i++) pk = Math.max(pk, Math.abs(L[i]), Math.abs(R[i]));
const g = 0.9 / pk;
const pcm = Buffer.alloc(44 + N * 4);
pcm.write('RIFF', 0); pcm.writeUInt32LE(36 + N * 4, 4); pcm.write('WAVEfmt ', 8); pcm.writeUInt32LE(16, 16); pcm.writeUInt16LE(1, 20); pcm.writeUInt16LE(2, 22); pcm.writeUInt32LE(SR, 24); pcm.writeUInt32LE(SR * 4, 28); pcm.writeUInt16LE(4, 32); pcm.writeUInt16LE(16, 34); pcm.write('data', 36); pcm.writeUInt32LE(N * 4, 40);
for (let i = 0; i < N; i++) { const l = Math.tanh(L[i] * g * 1.1), r = Math.tanh(R[i] * g * 1.1); pcm.writeInt16LE(Math.round(l * 32000), 44 + i * 4); pcm.writeInt16LE(Math.round(r * 32000), 46 + i * 4); }
writeFileSync(out, pcm);
console.log(out, (N / SR).toFixed(1) + 's', 'bar', BAR.toFixed(3) + 's');
