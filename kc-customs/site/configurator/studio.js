/* KC design studio controller (ES module, no dependencies). */
import { MODELS, COLORS, FINISHES, GRAPHICS, ARTWORK, PLACEMENTS, HYDRO, PARTS, PART_SOURCES, RIMS, MODS, DEFAULTS, STOCK } from './catalogue.js';
import { renderBike } from './render.js';
import { VIEWS } from './bikes.js';
import { createStore, refOf, decode, shareUrl, listSaved, saveDesign, removeSaved } from './store.js';
import { summaryRows, whatsappText, whatsappUrl, exportPNG, colorName } from './exporter.js';

const $ = (s, c = document) => c.querySelector(s);
const $$ = (s, c = document) => [...c.querySelectorAll(s)];
const reduce = matchMedia('(prefers-reduced-motion: reduce)').matches;
const byId = (list, id) => list.find((x) => x.id === id);
const yt = (id) => `https://www.youtube.com/shorts/${id}`;
const srcLink = (id) => id ? `<span class="src">Seen in <a class="link" href="${yt(id)}" target="_blank" rel="noopener">this KC video ↗</a></span>` : '';

const STEPS = [
  { k: 'paint', name: 'Paint' }, { k: 'graphics', name: 'Graphics' }, { k: 'airbrush', name: 'Airbrush' },
  { k: 'hydro', name: 'Hydro dip' }, { k: 'parts', name: 'Parts' }, { k: 'extras', name: 'Extras' }, { k: 'review', name: 'Review' },
];

const ui = { step: 0, view: VIEWS.full.slice(), compare: false, split: 50, typing: false };
let store;

/* ---------------- toast ---------------- */
let tt;
function toast(msg) { const t = $('#toast'); t.textContent = msg; t.classList.add('on'); clearTimeout(tt); tt = setTimeout(() => t.classList.remove('on'), 2200); }

/* ---------------- picker ---------------- */
function renderPicker() {
  $('#models').innerHTML = MODELS.map((m) => {
    const cfg = { ...DEFAULTS(m.id) };
    return `<button type="button" class="model" data-model="${m.id}" aria-label="Design a ${m.name}">
      <div class="model-art">${renderBike(cfg, { uid: 'pk' + m.id })}</div>
      <div class="model-t"><strong>${m.name.replace('Yamaha ', '')}</strong><span>${m.blurb}</span><span class="model-go">Select →</span></div></button>`;
  }).join('');
  $$('.model').forEach((b) => b.addEventListener('click', () => openStudio(DEFAULTS(b.dataset.model))));
  const saved = listSaved();
  const box = $('#saved');
  box.hidden = !saved.length;
  $('.saved-list', box).innerHTML = saved.map((d) => `<span class="saved-item">${d.ref}<button type="button" class="open" data-ref="${d.ref}">Open</button><button type="button" data-del="${d.ref}" aria-label="Delete ${d.ref}">✕</button></span>`).join('');
  $$('[data-ref]', box).forEach((b) => b.addEventListener('click', () => { const d = listSaved().find((x) => x.ref === b.dataset.ref); if (d) openStudio(decode(btoaSafe(d.cfg)) || d.cfg); }));
  $$('[data-del]', box).forEach((b) => b.addEventListener('click', () => { removeSaved(b.dataset.del); renderPicker(); }));
}
const btoaSafe = (cfg) => btoa(unescape(encodeURIComponent(JSON.stringify(cfg)))).replace(/\+/g, '-').replace(/\//g, '_').replace(/=+$/, '');

function showPicker() {
  $('#studio').hidden = true; $('#picker').hidden = false;
  history.replaceState(null, '', location.pathname);
  renderPicker(); scrollTo(0, 0);
}

/* ---------------- panels ---------------- */
const radio = (key, val, inner, cls = 'opt') => `<button type="button" class="${cls}" role="radio" data-set="${key}" data-val="${val}">${inner}</button>`;

function panelHTML(k, cfg) {
  const m = byId(MODELS, cfg.model);
  switch (k) {
    case 'paint': return `
      <div class="grp"><span class="label">Base colour</span><div class="swatches" role="radiogroup" aria-label="Base colour">
        ${COLORS.map((c) => radio('color', c.hex, '', 'sw').replace('class="sw"', `class="sw" style="background:${c.hex}" title="${c.name}" aria-label="${c.name}"`)).join('')}
        <label class="sw sw-custom" title="Any colour"><input type="color" data-color="color" value="${cfg.color}" aria-label="Pick any base colour"></label>
      </div><p class="sw-name" data-name="color"></p></div>
      <div class="grp"><span class="label">Finish</span><div class="opts" role="radiogroup" aria-label="Finish">
        ${FINISHES.map((f) => radio('finish', f.id, `<strong>${f.name}</strong><small>${f.note}</small>`)).join('')}
      </div><p class="hint" style="margin-top:8px">Matte and metallic aren't shown in KC's videos, so ask KC about them.</p></div>
      <div class="grp"><span class="label">Accent colour (graphics &amp; accent parts)</span><div class="swatches" role="radiogroup" aria-label="Accent colour">
        ${COLORS.map((c) => radio('accent', c.hex, '', 'sw').replace('class="sw"', `class="sw" style="background:${c.hex}" title="${c.name}" aria-label="${c.name}"`)).join('')}
        <label class="sw sw-custom" title="Any colour"><input type="color" data-color="accent" value="${cfg.accent}" aria-label="Pick any accent colour"></label>
      </div><p class="sw-name" data-name="accent"></p></div>`;
    case 'graphics': return `
      <div class="grp"><span class="label">Tank &amp; side-panel graphics</span><div class="opts" role="radiogroup" aria-label="Graphics">
        ${GRAPHICS.map((g) => radio('graphic', g.id, `<strong>${g.name}</strong><small>${g.note}</small>`)).join('')}
      </div></div>
      <div class="grp" data-show="lettering"><span class="label">Your text</span><input type="text" data-text="text" maxlength="14" placeholder="e.g. RED ROCKET" value="${(cfg.text || '').replace(/"/g, '')}"></div>
      <p class="hint">Graphics use your accent colour. KC hand-paints and stickers them to your design.</p>`;
    case 'airbrush': return `
      <div class="grp"><span class="label">Artwork style</span><p class="hint">Thumbnails are past KC artwork. Your piece is painted fresh.</p><div class="opts" role="radiogroup" aria-label="Artwork">
        ${ARTWORK.map((a) => radio('art', a.id, `${a.tex ? `<img src="configurator/textures/${a.tex}.webp" alt="" loading="lazy">` : '<span class="opt-none">Paint only</span>'}<span class="opt-t"><strong>${a.name}</strong></span>`, 'opt has-img')).join('')}
      </div></div>
      <div class="grp"><span class="label">Placement</span><div class="seg" role="radiogroup" aria-label="Placement">
        ${PLACEMENTS.map((p) => radio('place', p.id, p.name, '')).join('')}
      </div></div>`;
    case 'hydro': return `
      <div class="grp"><span class="label">Hydro dip pattern</span><div class="opts" role="radiogroup" aria-label="Hydro pattern">
        ${HYDRO.map((h) => radio('hydro', h.id, `${h.tex ? `<img src="configurator/textures/${h.tex}.webp" alt="" loading="lazy">` : '<span class="opt-none carbon"></span>'}<span class="opt-t"><strong>${h.name}</strong></span>`, 'opt has-img')).join('')}
      </div></div>
      <div class="grp"><span class="label">Dip these parts</span><div class="checks">
        ${PARTS.filter((p) => !(p.needs && !m[p.needs])).map((p) => `<label class="check"><input type="checkbox" data-hydro-part="${p.id}"> <span>${p.name}</span></label>`).join('')}
      </div></div>`;
    case 'parts': return `
      <p class="hint" style="margin-top:14px">Choose what each component gets.</p>
      ${PARTS.filter((p) => !(p.needs && !m[p.needs])).map((p) => `<div class="part-row"><span class="label">${p.name}</span><div class="seg seg-sm" role="radiogroup" aria-label="${p.name}">
        ${PART_SOURCES.map((s) => `<button type="button" role="radio" data-part="${p.id}" data-src="${s.id}">${s.name}</button>`).join('')}</div></div>`).join('')}
      <div class="grp"><span class="label">Rims</span><div class="seg" role="radiogroup" aria-label="Rims">${RIMS.map((r) => radio('rims', r.id, r.name, '')).join('')}</div></div>`;
    case 'extras': return `
      <div class="grp"><span class="label">Modifications for the ${m.short}</span><p class="hint">These aren't drawn in the preview. They're added to your request.</p><div class="checks">
        ${MODS.filter((x) => x.models.includes(m.id)).map((x) => `<label class="check"><input type="checkbox" data-mod="${x.id}"> <span>${x.name}<br>${srcLink(x.src)}</span></label>`).join('')}
      </div></div>
      <div class="grp"><span class="label">Your preferences</span><textarea data-text="note" maxlength="300" placeholder="Theme, inspiration, deadline, anything KC should know…">${cfg.note || ''}</textarea></div>`;
    case 'review': return '';
  }
  return '';
}

function sync(cfg) {
  const p = $('#panel');
  $$('[data-set]', p).forEach((el) => {
    const on = String(cfg[el.dataset.set]).toLowerCase() === String(el.dataset.val).toLowerCase();
    el.setAttribute('aria-checked', String(on)); if (el.closest('.seg')) el.classList.toggle('is-on', on);
  });
  $$('[data-part]', p).forEach((el) => { const on = (cfg.parts[el.dataset.part] || 'stock') === el.dataset.src; el.classList.toggle('is-on', on); el.setAttribute('aria-checked', String(on)); });
  $$('[data-hydro-part]', p).forEach((el) => { el.checked = cfg.parts[el.dataset.hydroPart] === 'hydro'; });
  $$('[data-mod]', p).forEach((el) => { el.checked = cfg.mods.includes(el.dataset.mod); });
  $$('[data-name]', p).forEach((el) => { el.textContent = colorName(cfg[el.dataset.name]); });
  $$('[data-color]', p).forEach((el) => { el.value = cfg[el.dataset.color]; });
  const show = $('[data-show]', p); if (show) show.hidden = cfg.graphic !== show.dataset.show;
}

function setStep(i) {
  ui.step = Math.max(0, Math.min(STEPS.length - 1, i));
  const k = STEPS[ui.step].k, cfg = store.get();
  $$('.st-steps button').forEach((b, n) => { b.setAttribute('aria-selected', String(n === ui.step)); b.tabIndex = n === ui.step ? 0 : -1; });
  $('#panel').innerHTML = panelHTML(k, cfg);
  $('#studio').classList.toggle('on-review', k === 'review');
  $('.st-stepcount').textContent = `Step ${ui.step + 1} / ${STEPS.length}`;
  $('[data-step="-1"]').disabled = ui.step === 0;
  const next = $('[data-step="1"]');
  next.textContent = ui.step === STEPS.length - 1 ? 'Request →' : 'Next →';
  sync(cfg);
}

/* ---------------- preview ---------------- */
function applyView() {
  $$('#stage svg').forEach((s) => s.setAttribute('viewBox', ui.view.map((n) => n.toFixed(1)).join(' ')));
}
function renderPreview(cfg) {
  $('#layer-custom').innerHTML = renderBike(cfg, { uid: 'c' });
  if (ui.compare) $('#layer-stock').innerHTML = renderBike(STOCK(cfg.model), { uid: 's' });
  applyView();
}
function setCompare(on) {
  ui.compare = on;
  $('[data-act="compare"]').setAttribute('aria-pressed', String(on));
  $('#layer-stock').hidden = !on; $('#cmp').hidden = !on;
  if (on) { $('#layer-stock').innerHTML = renderBike(STOCK(store.get().model), { uid: 's' }); applySplit(); applyView(); }
}
function applySplit() {
  $('#layer-stock').style.clipPath = `inset(0 ${100 - ui.split}% 0 0)`;
  $('#cmp').style.setProperty('--split', ui.split + '%');
}
function zoom(f, cx = .5, cy = .5) {
  const [x, y, w, h] = ui.view;
  const nw = Math.max(180, Math.min(1000, w / f)), nh = nw * (h / w);
  ui.view = [x + (w - nw) * cx, y + (h - nh) * cy, nw, nh]; applyView();
}
function setView(name) {
  ui.view = VIEWS[name].slice(); applyView();
  $$('[data-view]').forEach((b) => b.classList.toggle('is-on', b.dataset.view === name));
}

/* ---------------- summary ---------------- */
function renderSummary(cfg) {
  const m = byId(MODELS, cfg.model), ref = refOf(cfg);
  $('.sum-model').textContent = m.name;
  $('.sum-ref').textContent = ref;
  $('.sum-list').innerHTML = summaryRows(cfg).filter((r) => r[0] !== 'Motorcycle').map(([k, v, step]) =>
    `<div><dt>${k}</dt><dd><button type="button" data-goto="${step}">${String(v).replace(/</g, '&lt;')}</button></dd></div>`).join('');
  $('.studio-crumb span').textContent = `${m.short} · ${ref}`;
}

/* ---------------- studio ---------------- */
function openStudio(cfg) {
  $('#picker').hidden = true; $('#studio').hidden = false;
  ui.view = VIEWS.full.slice(); setCompare(false);
  store.replace(cfg);
  setStep(0); setView('full'); scrollTo(0, 0);
}

function onChange(cfg, h) {
  renderPreview(cfg); renderSummary(cfg); if (!ui.typing) sync(cfg);
  $('[data-act="undo"]').disabled = !h.canUndo; $('[data-act="redo"]').disabled = !h.canRedo;
  history.replaceState(null, '', '#c=' + btoaSafe(cfg));
}

function bind() {
  const studio = $('#studio');
  $('.st-steps').innerHTML = STEPS.map((s, i) => `<button type="button" role="tab" data-k="${s.k}"><b>${String(i + 1).padStart(2, '0')}</b>${s.name}</button>`).join('');
  $$('.st-steps button').forEach((b, i) => b.addEventListener('click', () => setStep(i)));
  $$('[data-step]').forEach((b) => b.addEventListener('click', () => {
    if (+b.dataset.step > 0 && ui.step === STEPS.length - 1) return openRequest();
    setStep(ui.step + (+b.dataset.step));
    $('.st-left').scrollIntoView({ block: 'start', behavior: reduce ? 'auto' : 'smooth' });
  }));

  const panel = $('#panel');
  panel.addEventListener('click', (e) => {
    const s = e.target.closest('[data-set]');
    if (s) { store.set({ [s.dataset.set]: s.dataset.val }); return; }
    const p = e.target.closest('[data-part]');
    if (p) store.set({ parts: { [p.dataset.part]: p.dataset.src } });
  });
  panel.addEventListener('change', (e) => {
    const t = e.target;
    if (t.dataset.hydroPart) store.set({ parts: { [t.dataset.hydroPart]: t.checked ? 'hydro' : (t.dataset.hydroPart === 'tank' || t.dataset.hydroPart === 'side' || t.dataset.hydroPart === 'cowl' ? 'main' : 'stock') } });
    if (t.dataset.mod) { const mods = new Set(store.get().mods); t.checked ? mods.add(t.dataset.mod) : mods.delete(t.dataset.mod); store.set({ mods: [...mods] }); }
    if (t.dataset.color) store.set({ [t.dataset.color]: t.value });
  });
  let typeT;
  panel.addEventListener('input', (e) => {
    const t = e.target;
    if (t.dataset.color) { ui.typing = true; store.set({ [t.dataset.color]: t.value }); ui.typing = false; return; }
    if (!t.dataset.text) return;
    clearTimeout(typeT);
    typeT = setTimeout(() => { ui.typing = true; store.set({ [t.dataset.text]: t.value.trim() }); ui.typing = false; }, 250);
  });

  $$('[data-view]').forEach((b) => b.addEventListener('click', () => setView(b.dataset.view)));
  $$('[data-zoom]').forEach((b) => b.addEventListener('click', () => zoom(+b.dataset.zoom > 0 ? 1.25 : 0.8)));
  document.addEventListener('click', (e) => {
    const a = e.target.closest('[data-act]'); if (!a) return;
    const act = a.dataset.act, cfg = store.get();
    if (act === 'undo') store.undo();
    else if (act === 'redo') store.redo();
    else if (act === 'reset') { store.reset(); setView('full'); toast('Reset to the starting design'); }
    else if (act === 'compare') setCompare(!ui.compare);
    else if (act === 'save') { const r = saveDesign(cfg); toast(r ? 'Saved in this browser · ' + r : 'Could not save in this browser'); }
    else if (act === 'share') shareLink(cfg);
    else if (act === 'image') downloadImage(cfg);
    else if (act === 'share-image') shareImage(cfg);
    else if (act === 'request') openRequest();
    else if (act === 'send') sendRequest();
    else if (act === 'change') showPicker();
  });
  $('.sum-list').addEventListener('click', (e) => {
    const g = e.target.closest('[data-goto]'); if (!g) return;
    const k = g.dataset.goto; if (k === 'bike') return showPicker();
    setStep(STEPS.findIndex((s) => s.k === k));
  });
  $('#cmp input').addEventListener('input', (e) => { ui.split = +e.target.value; applySplit(); });

  // pan + wheel zoom on the stage
  const stage = $('#stage'); let pan = null;
  stage.addEventListener('pointerdown', (e) => { if (e.target.closest('.cmp input')) return; pan = { x: e.clientX, y: e.clientY, v: ui.view.slice() }; stage.setPointerCapture(e.pointerId); stage.classList.add('panning'); });
  stage.addEventListener('pointermove', (e) => {
    if (!pan) return;
    const k = pan.v[2] / stage.clientWidth;
    ui.view = [pan.v[0] - (e.clientX - pan.x) * k, pan.v[1] - (e.clientY - pan.y) * k, pan.v[2], pan.v[3]]; applyView();
  });
  const end = () => { pan = null; stage.classList.remove('panning'); };
  stage.addEventListener('pointerup', end); stage.addEventListener('pointercancel', end);
  stage.addEventListener('wheel', (e) => {
    if (!matchMedia('(min-width:1100px)').matches) return;
    e.preventDefault(); const r = stage.getBoundingClientRect();
    zoom(e.deltaY < 0 ? 1.12 : 0.89, (e.clientX - r.left) / r.width, (e.clientY - r.top) / r.height);
  }, { passive: false });
  document.addEventListener('keydown', (e) => {
    if (studio.hidden || e.target.matches('input, textarea')) return;
    if ((e.ctrlKey || e.metaKey) && e.key.toLowerCase() === 'z') { e.preventDefault(); e.shiftKey ? store.redo() : store.undo(); }
  });

  // request dialog
  const dlg = $('#req');
  $('[data-close]', dlg).addEventListener('click', () => dlg.close());
  dlg.addEventListener('click', (e) => { if (e.target === dlg) dlg.close(); });
  const ack = $('input[name=ack]', dlg), send = $('[data-act="send"]', dlg);
  ack.addEventListener('change', () => { send.disabled = !ack.checked; });
}

/* ---------------- share / export / request ---------------- */
async function shareLink(cfg) {
  const url = shareUrl(cfg);
  try {
    if (navigator.share) { await navigator.share({ title: 'My KC Customs build ' + refOf(cfg), url }); return; }
    await navigator.clipboard.writeText(url); toast('Design link copied');
  } catch (e) { if (e && e.name !== 'AbortError') { prompt('Copy your design link:', url); } }
}
async function downloadImage(cfg) {
  try {
    const ref = refOf(cfg), blob = await exportPNG(cfg, ref);
    const a = document.createElement('a'); a.href = URL.createObjectURL(blob); a.download = ref + '.png';
    document.body.appendChild(a); a.click(); a.remove(); setTimeout(() => URL.revokeObjectURL(a.href), 4000);
    toast('Image saved · ' + ref + '.png');
  } catch (e) { toast('Could not create the image'); }
}
async function shareImage(cfg) {
  try {
    const ref = refOf(cfg), blob = await exportPNG(cfg, ref);
    const file = new File([blob], ref + '.png', { type: 'image/png' });
    await navigator.share({ files: [file], title: 'KC Customs build ' + ref, text: 'My KC Customs concept build ' + ref });
  } catch (e) { if (e && e.name !== 'AbortError') toast('Sharing is not available here'); }
}
function openRequest() {
  const cfg = store.get(), dlg = $('#req');
  $('#req-prev').innerHTML = renderBike(cfg, { uid: 'r' });
  $('.req-ref', dlg).textContent = byId(MODELS, cfg.model).name + ' · ' + refOf(cfg);
  const can = !!(navigator.canShare && navigator.canShare({ files: [new File([''], 'x.png', { type: 'image/png' })] }));
  $('[data-act="share-image"]', dlg).hidden = !can;
  $('[data-act="send"]', dlg).disabled = !$('input[name=ack]', dlg).checked;
  dlg.showModal();
}
function sendRequest() {
  const dlg = $('#req'); if (!$('input[name=ack]', dlg).checked) return;
  const cfg = store.get();
  const text = whatsappText(cfg, refOf(cfg), shareUrl(cfg), $('input[name=name]', dlg).value.trim());
  window.open(whatsappUrl(text), '_blank', 'noopener');
}

/* ---------------- boot ---------------- */
store = createStore(DEFAULTS('rxz'), onChange);
bind();
const hash = new URLSearchParams(location.hash.slice(1)).get('c');
const qBike = new URLSearchParams(location.search).get('bike');
const fromHash = hash && decode(hash);
if (fromHash) openStudio(fromHash);
else if (qBike && MODELS.some((m) => m.id === qBike)) openStudio(DEFAULTS(qBike));
else showPicker();
