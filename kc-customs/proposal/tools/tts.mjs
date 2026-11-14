import { MsEdgeTTS, OUTPUT_FORMAT } from 'msedge-tts';
import { writeFileSync, mkdirSync } from 'node:fs';
// usage: node tts.mjs <voice> <outfile.mp3> <text>
const [voice, out, ...t] = process.argv.slice(2);
const tts = new MsEdgeTTS();
await tts.setMetadata(voice, OUTPUT_FORMAT.AUDIO_24KHZ_96KBITRATE_MONO_MP3);
const { audioStream } = tts.toStream(t.join(' '));
const chunks = [];
await new Promise((res, rej) => { audioStream.on('data', (c) => chunks.push(c)); audioStream.on('end', res); audioStream.on('error', rej); });
writeFileSync(out, Buffer.concat(chunks));
console.log(out, Buffer.concat(chunks).length);
process.exit(0);
