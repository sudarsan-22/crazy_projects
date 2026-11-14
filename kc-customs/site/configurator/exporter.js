/* Preview image export (PNG) and WhatsApp summary text. */
import { renderBike } from './render.js';
import { MODELS, COLORS, FINISHES, GRAPHICS, ARTWORK, PLACEMENTS, HYDRO, PARTS, PART_SOURCES, RIMS, MODS, PHONE } from './catalogue.js';

const byId = (list, id) => list.find((x) => x.id === id);
export function colorName(hex) { const c = COLORS.find((x) => x.hex.toLowerCase() === String(hex).toLowerCase()); return c ? c.name : 'Custom ' + String(hex).toUpperCase(); }

/* Human-readable summary rows (used by the panel, the image and WhatsApp). */
export function summaryRows(cfg) {
  const m = byId(MODELS, cfg.model);
  const g = byId(GRAPHICS, cfg.graphic);
  const a = byId(ARTWORK, cfg.art);
  const usesHydro = Object.values(cfg.parts || {}).includes('hydro');
  const parts = PARTS.filter((p) => !(p.needs && !m[p.needs]))
    .map((p) => p.name + ': ' + byId(PART_SOURCES, cfg.parts[p.id] || 'stock').name).join(', ');
  const rows = [
    ['Motorcycle', m.name, 'bike'],
    ['Base colour', colorName(cfg.color) + ' · ' + byId(FINISHES, cfg.finish).name, 'paint'],
    ['Accent colour', colorName(cfg.accent), 'paint'],
    ['Graphics', g.name + (cfg.graphic === 'lettering' && cfg.text ? ' "' + cfg.text + '"' : ''), 'graphics'],
    ['Airbrush artwork', a.id === 'none' ? 'None' : a.name + ' on ' + byId(PLACEMENTS, cfg.place).name.toLowerCase(), 'airbrush'],
    ['Hydro dip', usesHydro ? byId(HYDRO, cfg.hydro).name : 'None', 'hydro'],
    ['Components', parts, 'parts'],
    ['Rims', byId(RIMS, cfg.rims).name, 'parts'],
    ['Modifications', (cfg.mods || []).map((id) => (byId(MODS, id) || {}).name).filter(Boolean).join(', ') || 'None', 'extras'],
  ];
  if (cfg.note) rows.push(['Preferences', cfg.note, 'extras']);
  return rows;
}

export function whatsappText(cfg, ref, link, name) {
  const lines = ['Hi KC Customs, I designed a bike on your website and would like to request this build.', '', 'Ref: ' + ref];
  if (name) lines.push('Name: ' + name);
  summaryRows(cfg).forEach(([k, v]) => lines.push(k + ': ' + v));
  lines.push('', 'Design link: ' + link, '', 'I understand this is a concept preview. Final design, feasibility and price to be confirmed by KC Customs.');
  return lines.join('\n');
}
export const whatsappUrl = (text) => 'https://wa.me/' + PHONE + '?text=' + encodeURIComponent(text);

/* Inline textures as data URIs so the SVG can be drawn onto a canvas. */
async function inlineImages(svg) {
  const urls = [...new Set([...svg.matchAll(/href="([^"]+\.webp)"/g)].map((m) => m[1]))];
  for (const u of urls) {
    const blob = await (await fetch(u)).blob();
    const data = await new Promise((r) => { const fr = new FileReader(); fr.onload = () => r(fr.result); fr.readAsDataURL(blob); });
    svg = svg.split('href="' + u + '"').join('href="' + data + '"');
  }
  return svg;
}

export async function exportPNG(cfg, ref) {
  const W = 1600, H = 1240;
  const svg = await inlineImages(renderBike(cfg, { uid: 'ex' }));
  const img = new Image();
  const url = URL.createObjectURL(new Blob([svg], { type: 'image/svg+xml' }));
  await new Promise((res, rej) => { img.onload = res; img.onerror = rej; img.src = url; });
  const c = document.createElement('canvas'); c.width = W; c.height = H;
  const x = c.getContext('2d');
  const bg = x.createLinearGradient(0, 0, 0, H); bg.addColorStop(0, '#171c24'); bg.addColorStop(1, '#0B0D11');
  x.fillStyle = bg; x.fillRect(0, 0, W, H);
  x.drawImage(img, 150, 150, 1300, 780);
  URL.revokeObjectURL(url);
  x.fillStyle = '#D9B07F'; x.font = '600 22px Inter, sans-serif'; x.fillText('KC CUSTOMS · DESIGN YOUR DREAM BIKE', 60, 70);
  x.fillStyle = '#EEEAF2'; x.font = '400 64px Anton, Impact, sans-serif'; x.fillText(byId(MODELS, cfg.model).name.toUpperCase(), 60, 140);
  x.textAlign = 'right'; x.fillStyle = '#B177C1'; x.font = '600 26px Inter, sans-serif'; x.fillText(ref, W - 60, 70); x.textAlign = 'left';
  const rows = summaryRows(cfg).filter((r) => r[0] !== 'Motorcycle' && r[0] !== 'Components');
  x.font = '500 21px Inter, sans-serif';
  rows.slice(0, 8).forEach(([k, v], i) => {
    const col = i % 2, row = Math.floor(i / 2), px = 60 + col * 760, py = 990 + row * 46;
    x.fillStyle = '#9C98A6'; x.fillText(k.toUpperCase(), px, py);
    x.fillStyle = '#EEEAF2'; x.fillText(String(v).slice(0, 44), px + 270, py);
  });
  x.fillStyle = '#9C98A6'; x.font = '400 19px Inter, sans-serif';
  x.fillText('Concept preview, not to scale. Final design, feasibility and price are confirmed by KC Customs · WhatsApp +91 96771 84462', 60, H - 40);
  return await new Promise((r) => c.toBlob(r, 'image/png'));
}
