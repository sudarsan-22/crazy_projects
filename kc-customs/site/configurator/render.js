/* Preview renderer: builds an SVG string for a configuration. Pure function → easy to export. */
import { geometry } from './bikes.js';
import { HYDRO, ARTWORK, RIMS } from './catalogue.js';

const TEX = (name) => `configurator/textures/${name}.webp`;

function hexToRgb(h) { const n = parseInt(h.slice(1), 16); return [(n >> 16) & 255, (n >> 8) & 255, n & 255]; }
function rgbToHex([r, g, b]) { return '#' + [r, g, b].map((v) => Math.max(0, Math.min(255, Math.round(v))).toString(16).padStart(2, '0')).join(''); }
function mix(a, b, t) { const A = hexToRgb(a), B = hexToRgb(b); return rgbToHex(A.map((v, i) => v + (B[i] - v) * t)); }
const lighten = (c, t) => mix(c, '#ffffff', t);
const darken = (c, t) => mix(c, '#000000', t);

/* Gradient stops per finish. Chrome uses banded stops for a mirror look. */
function stops(c, finish) {
  switch (finish) {
    case 'candy': return [[0, lighten(c, .38)], [.35, c], [.75, darken(c, .45)], [1, darken(c, .7)]];
    case 'chrome': return [[0, lighten(c, .75)], [.22, lighten(c, .15)], [.42, darken(c, .55)], [.55, lighten(c, .5)], [.78, c], [1, darken(c, .65)]];
    case 'pearl': return [[0, lighten(c, .6)], [.4, lighten(c, .12)], [.7, mix(c, '#d8c8ff', .18)], [1, darken(c, .25)]];
    default: return [[0, lighten(c, .22)], [.5, c], [1, darken(c, .35)]];
  }
}
const grad = (id, c, finish) => `<linearGradient id="${id}" x1="0" y1="0" x2="0.25" y2="1">${stops(c, finish).map(([o, s]) => `<stop offset="${o}" stop-color="${s}"/>`).join('')}</linearGradient>`;

/* Graphics drawn in bike coordinates, then clipped to tank / side panel. */
function graphicMarkup(kind, accent, main, text) {
  const a = accent, a2 = lighten(accent, .35), d = darken(main, .55);
  switch (kind) {
    case 'stripes': return `<g opacity=".95"><path d="M600,150 L626,150 L566,290 L540,290 Z" fill="${a}"/><path d="M640,150 L654,150 L594,290 L580,290 Z" fill="${a2}"/><path d="M420,240 L438,240 L398,340 L380,340 Z" fill="${a}"/><path d="M448,240 L458,240 L418,340 L408,340 Z" fill="${a2}"/></g>`;
    case 'angular': return `<g><path d="M720,190 L560,236 L640,250 L520,262 L720,250 Z" fill="${a}" opacity=".95"/><path d="M700,206 L590,232 L660,236 Z" fill="${a2}"/><path d="M520,180 L600,176 L540,214 Z" fill="${d}" opacity=".6"/><path d="M500,268 L320,256 L420,286 L300,292 L470,318 Z" fill="${a}" opacity=".92"/><path d="M480,280 L380,276 L430,296 Z" fill="${a2}"/></g>`;
    case 'splash': return `<g><circle cx="610" cy="214" r="34" fill="${a}" opacity=".9"/><circle cx="650" cy="232" r="18" fill="${a2}"/><circle cx="566" cy="238" r="14" fill="${lighten(main, .5)}" opacity=".7"/><path d="M540,200 C580,180 610,204 640,190 C670,176 690,196 706,206 L700,226 C670,214 650,236 616,230 C584,226 566,246 534,236 Z" fill="${a2}" opacity=".55"/><circle cx="420" cy="292" r="22" fill="${a}" opacity=".9"/><circle cx="452" cy="306" r="10" fill="${a2}"/><path d="M340,280 C380,266 400,300 440,286 L470,300 C430,318 390,300 350,310 Z" fill="${a2}" opacity=".55"/></g>`;
    case 'flames': return `<g><path d="M716,206 C690,200 676,216 650,206 C664,222 640,226 618,214 C630,232 600,240 580,226 C590,246 556,252 536,238 C548,256 520,260 504,250 L520,262 C600,266 660,260 708,246 Z" fill="${a}"/><path d="M712,214 C692,212 680,224 660,218 C668,232 646,236 630,228 C636,242 610,246 596,238 C640,254 690,248 708,238 Z" fill="${a2}"/><path d="M490,282 C470,276 460,290 440,282 C450,298 426,300 410,292 C418,306 392,310 378,302 L384,318 C430,322 470,316 486,304 Z" fill="${a}"/></g>`;
    case 'lettering': {
      const t = (text || 'KC STYLE').replace(/[<>&"]/g, '').slice(0, 14);
      return `<text x="604" y="236" text-anchor="middle" font-family="Anton, Impact, sans-serif" font-size="${t.length > 9 ? 26 : 34}" fill="${a}" stroke="${darken(a, .6)}" stroke-width="1.2" letter-spacing="1" transform="rotate(-6 604 236)">${t.toUpperCase()}</text><text x="414" y="300" text-anchor="middle" font-family="Anton, Impact, sans-serif" font-size="20" fill="${a}" transform="rotate(-4 414 300)">${t.toUpperCase()}</text>`;
    }
    default: return '';
  }
}

function carbonPattern(id) {
  return `<pattern id="${id}" width="14" height="14" patternUnits="userSpaceOnUse" patternTransform="rotate(35)"><rect width="14" height="14" fill="#1b1c20"/><rect width="7" height="7" fill="#2c2e34"/><rect x="7" y="7" width="7" height="7" fill="#2c2e34"/><rect width="14" height="1" fill="#3a3d44" opacity=".5"/></pattern>`;
}

/**
 * @param {object} cfg configuration
 * @param {object} opt { uid, texBase, showLabels }
 */
export function renderBike(cfg, opt = {}) {
  const g = geometry(cfg.model);
  const u = opt.uid || 'b';
  const texBase = opt.texBase || '';
  const T = (n) => texBase + TEX(n);
  const main = cfg.color, accent = cfg.accent;
  const hydro = HYDRO.find((h) => h.id === cfg.hydro) || HYDRO[0];
  const rim = RIMS.find((r) => r.id === cfg.rims) || RIMS[0];
  const rimHex = rim.id === 'main' ? main : rim.hex;
  const art = ARTWORK.find((a) => a.id === cfg.art);
  const STOCK_PART = { frontGuard: 'url(#' + u + 'chrome)', rearGuard: 'url(#' + u + 'chrome)', engine: '#9aa0a8', tank: '#15161A', side: '#15161A', cowl: '#15161A' };

  const fillFor = (part) => {
    const src = (cfg.parts || {})[part] || 'stock';
    if (src === 'main') return `url(#${u}main)`;
    if (src === 'accent') return `url(#${u}accent)`;
    if (src === 'hydro') return `url(#${u}hydro)`;
    return STOCK_PART[part];
  };

  const defs = [
    grad(u + 'main', main, cfg.finish),
    grad(u + 'accent', accent, cfg.finish),
    `<linearGradient id="${u}chrome" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#f4f6f8"/><stop offset=".45" stop-color="#9aa1aa"/><stop offset=".6" stop-color="#e3e7ec"/><stop offset="1" stop-color="#5d636b"/></linearGradient>`,
    `<linearGradient id="${u}tyre" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#2a2b30"/><stop offset="1" stop-color="#0c0c0e"/></linearGradient>`,
    `<radialGradient id="${u}lamp" cx=".4" cy=".35" r=".7"><stop offset="0" stop-color="#ffffff"/><stop offset=".5" stop-color="#cfe3ff"/><stop offset="1" stop-color="#5e7aa6"/></radialGradient>`,
    `<radialGradient id="${u}spec" cx=".35" cy=".25" r=".6"><stop offset="0" stop-color="#fff" stop-opacity=".75"/><stop offset="1" stop-color="#fff" stop-opacity="0"/></radialGradient>`,
    `<clipPath id="${u}clipTank"><path d="${g.tank}"/></clipPath>`,
    `<clipPath id="${u}clipSide"><path d="${g.side}"/></clipPath>`,
    `<clipPath id="${u}clipBody"><path d="${g.tank}"/><path d="${g.side}"/></clipPath>`,
    hydro.tex ? `<pattern id="${u}hydro" width="150" height="150" patternUnits="userSpaceOnUse"><image href="${T(hydro.tex)}" width="150" height="150" preserveAspectRatio="xMidYMid slice"/></pattern>` : carbonPattern(u + 'hydro'),
  ];

  const wheel = (cx, cy, disc) => {
    const spokes = Array.from({ length: 18 }, (_, i) => {
      const a = (i / 18) * Math.PI * 2; return `<line x1="${cx + Math.cos(a) * 16}" y1="${cy + Math.sin(a) * 16}" x2="${cx + Math.cos(a + .35) * 86}" y2="${cy + Math.sin(a + .35) * 86}"/>`;
    }).join('');
    return `<g class="wheel"><circle cx="${cx}" cy="${cy}" r="${g.tire - 11}" fill="none" stroke="url(#${u}tyre)" stroke-width="24"/>
      <circle cx="${cx}" cy="${cy}" r="${g.tire - 11}" fill="none" stroke="#3a3c42" stroke-width="1.5" stroke-dasharray="3 7"/>
      <circle cx="${cx}" cy="${cy}" r="88" fill="none" stroke="${rimHex}" stroke-width="7"/>
      <g stroke="#b9bec6" stroke-width="1.6" opacity=".85">${spokes}</g>
      ${disc ? `<circle cx="${cx}" cy="${cy}" r="50" fill="none" stroke="#8d939b" stroke-width="10"/><circle cx="${cx}" cy="${cy}" r="50" fill="none" stroke="#5a5f66" stroke-width="10" stroke-dasharray="2 9"/><rect x="${cx + 34}" y="${cy - 62}" width="20" height="38" rx="6" fill="#c0262c"/>` : ''}
      <circle cx="${cx}" cy="${cy}" r="18" fill="url(#${u}chrome)"/><circle cx="${cx}" cy="${cy}" r="6" fill="#333"/></g>`;
  };

  const artLayer = art && art.tex
    ? `<g clip-path="url(#${u}${cfg.place === 'tank' ? 'clipTank' : 'clipSide'})"><image href="${T(art.tex)}" ${cfg.place === 'tank' ? 'x="560" y="176" width="130" height="90"' : 'x="330" y="250" width="160" height="80"'} preserveAspectRatio="xMidYMid slice" opacity=".95"/></g>` : '';

  const headlight = g.headlight.type === 'round'
    ? `<circle cx="${g.headlight.cx}" cy="${g.headlight.cy}" r="${g.headlight.r}" fill="url(#${u}chrome)"/><circle cx="${g.headlight.cx + 4}" cy="${g.headlight.cy}" r="${g.headlight.r - 8}" fill="url(#${u}lamp)"/>`
    : `<path d="${g.cowl}" fill="${fillFor('cowl')}" stroke="#0b0c0f" stroke-width="2" data-part="cowl"/><path d="${g.cowl}" fill="url(#${u}spec)" opacity=".5"/><rect x="${g.headlight.x}" y="${g.headlight.y}" width="${g.headlight.w}" height="${g.headlight.h}" rx="7" fill="url(#${u}lamp)"/>`;

  const [sx, sy, sw, sh] = g.shadow;
  return `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1000 600" class="bike-svg" role="img" aria-label="Concept illustration of a customised ${cfg.model.toUpperCase()}">
  <defs>${defs.join('')}</defs>
  <ellipse cx="${sx}" cy="${sy}" rx="${sw}" ry="${sh}" fill="#000" opacity=".55"/>
  <path d="${g.silencer}" fill="url(#${u}chrome)"/>
  <path d="${g.rearGuard}" fill="${fillFor('rearGuard')}" stroke="#0b0c0f" stroke-width="2" data-part="rearGuard"/>
  <rect x="${g.tailLight[0]}" y="${g.tailLight[1]}" width="${g.tailLight[2]}" height="${g.tailLight[3]}" rx="4" fill="#d7262d"/>
  ${wheel(g.rearAxle[0], g.rearAxle[1], false)}
  <path d="${g.swingarm}" fill="#24262b"/>
  <path d="${g.chainGuard}" fill="#15161a"/>
  <line x1="${g.shock[0][0]}" y1="${g.shock[0][1]}" x2="${g.shock[1][0]}" y2="${g.shock[1][1]}" stroke="#d1a43a" stroke-width="12" stroke-linecap="round" stroke-dasharray="4 3"/>
  <path d="${g.frame}" fill="none" stroke="#1b1d22" stroke-width="11" stroke-linecap="round"/>
  <path d="${g.engineBlock}" fill="#2a2d33" stroke="#111" stroke-width="2"/>
  <path d="${g.cylinder}" fill="#3a3e45"/>
  <g stroke="#61666e" stroke-width="3">${[0, 1, 2, 3, 4, 5].map((i) => `<line x1="${560 + i * 2}" y1="${276 + i * 12}" x2="${618 - i * 2}" y2="${296 + i * 12}"/>`).join('')}</g>
  <path d="${g.engine}" fill="${fillFor('engine')}" stroke="#111" stroke-width="2" data-part="engine"/>
  <path d="${g.engine}" fill="url(#${u}spec)" opacity=".45"/>
  <path d="${g.exhaust}" fill="url(#${u}chrome)" stroke="#4a4f56" stroke-width="1.5"/>
  <path d="${g.side}" fill="${fillFor('side')}" stroke="#0b0c0f" stroke-width="2" data-part="side"/>
  <path d="${g.seat}" fill="#141518" stroke="#000" stroke-width="2"/>
  <path d="${g.seat}" fill="none" stroke="#2d2f35" stroke-width="1" stroke-dasharray="6 6" transform="translate(0,4)"/>
  <path d="${g.tank}" fill="${fillFor('tank')}" stroke="#0b0c0f" stroke-width="2" data-part="tank"/>
  <g clip-path="url(#${u}clipBody)">${graphicMarkup(cfg.graphic, accent, main, cfg.text)}</g>
  ${artLayer}
  <path d="${g.tank}" fill="url(#${u}spec)" opacity="${cfg.finish === 'chrome' || cfg.finish === 'candy' ? .7 : .45}"/>
  <path d="${g.side}" fill="url(#${u}spec)" opacity=".3"/>
  <path d="${g.fork2}" stroke="#8e949c" stroke-width="14" stroke-linecap="round"/>
  <path d="${g.fork}" stroke="url(#${u}chrome)" stroke-width="16" stroke-linecap="round"/>
  ${wheel(g.frontAxle[0], g.frontAxle[1], g.frontDisc)}
  <path d="${g.frontGuard}" fill="${fillFor('frontGuard')}" stroke="#0b0c0f" stroke-width="2" data-part="frontGuard"/>
  <path d="${g.bar}" fill="none" stroke="#111" stroke-width="8" stroke-linecap="round"/>
  <circle cx="${g.gauge[0]}" cy="${g.gauge[1]}" r="${g.gauge[2]}" fill="#0f1013" stroke="#c9cdd3" stroke-width="3"/>
  ${headlight}
  <path d="${g.footpeg}" stroke="#111" stroke-width="7" stroke-linecap="round"/>
</svg>`;
}
