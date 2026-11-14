// usage: node assemble.mjs <lang> <outDir>   (needs <outDir>/frames.txt and <outDir>/marks.json)
import { execFileSync } from 'node:child_process'; import { readFileSync } from 'node:fs';
const [lang, out] = process.argv.slice(2);
const marks = JSON.parse(readFileSync(`${out}/marks.json`, 'utf8'));
const run = (a) => execFileSync('ffmpeg', ['-y', '-v', 'error', ...a], { stdio: 'inherit' });
run(['-f', 'concat', '-safe', '0', '-i', `${out}/frames.txt`, '-vf', 'fps=30,format=yuv420p', '-c:v', 'libx264', '-preset', 'medium', '-crf', '20', `${out}/video.mp4`]);
const vdur = parseFloat(execFileSync('ffprobe', ['-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0', `${out}/video.mp4`]).toString());
const inputs = [], f = [];
marks.forEach((m, i) => { inputs.push('-i', m.a); f.push(`[${i}:a]adelay=${m.off}|${m.off}[a${i}]`); });
run([...inputs, '-filter_complex', f.join(';') + ';' + marks.map((_, i) => `[a${i}]`).join('') + `amix=inputs=${marks.length}:normalize=0,apad=whole_dur=${vdur.toFixed(2)},loudnorm=I=-16:TP=-1.5[a]`, '-map', '[a]', '-t', vdur.toFixed(2), '-c:a', 'aac', '-b:a', '160k', `${out}/audio.m4a`]);
const file = `${out}/kc-customs-website-proposal-${lang}.mp4`;
run(['-i', `${out}/video.mp4`, '-i', `${out}/audio.m4a`, '-map', '0:v', '-map', '1:a', '-c', 'copy', '-movflags', '+faststart', file]);
console.log(file, vdur.toFixed(1) + 's');
