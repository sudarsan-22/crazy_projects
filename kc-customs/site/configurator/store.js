/* Configuration manager: undo/redo history, save to this browser, share links, reference IDs. */
import { DEFAULTS, MODELS } from './catalogue.js';

export function createStore(initial, onChange) {
  let hist = [JSON.stringify(initial)], idx = 0;
  const get = () => JSON.parse(hist[idx]);
  const emit = () => onChange && onChange(get(), { canUndo: idx > 0, canRedo: idx < hist.length - 1 });
  return {
    get,
    set(patch) {
      const next = { ...get(), ...patch };
      if (patch.parts) next.parts = { ...get().parts, ...patch.parts };
      const s = JSON.stringify(next);
      if (s === hist[idx]) return;
      hist = hist.slice(0, idx + 1); hist.push(s); if (hist.length > 80) hist.shift(); idx = hist.length - 1; emit();
    },
    replace(cfg) { hist = [JSON.stringify(cfg)]; idx = 0; emit(); },
    undo() { if (idx > 0) { idx--; emit(); } },
    redo() { if (idx < hist.length - 1) { idx++; emit(); } },
    reset() { this.set(DEFAULTS(get().model)); },
    emit,
  };
}

/* Reference ID: stable short hash of the configuration (FNV-1a). */
export function refOf(cfg) {
  const s = JSON.stringify({ ...cfg, note: undefined });
  let h = 0x811c9dc5;
  for (let i = 0; i < s.length; i++) { h ^= s.charCodeAt(i); h = Math.imul(h, 0x01000193) >>> 0; }
  const m = MODELS.find((x) => x.id === cfg.model);
  return 'KC-' + (m ? m.short : 'BIKE').toUpperCase() + '-' + h.toString(36).toUpperCase().slice(0, 5).padStart(5, '0');
}

/* Share links: compact base64url JSON in the URL hash. */
const b64 = (s) => btoa(unescape(encodeURIComponent(s))).replace(/\+/g, '-').replace(/\//g, '_').replace(/=+$/, '');
const unb64 = (s) => decodeURIComponent(escape(atob(s.replace(/-/g, '+').replace(/_/g, '/'))));
export function encode(cfg) { return b64(JSON.stringify(cfg)); }
export function decode(str) {
  try {
    const c = JSON.parse(unb64(str));
    if (!c || !MODELS.some((m) => m.id === c.model)) return null;
    const d = DEFAULTS(c.model);
    return { ...d, ...c, parts: { ...d.parts, ...(c.parts || {}) }, mods: Array.isArray(c.mods) ? c.mods : [] };
  } catch (e) { return null; }
}
export function shareUrl(cfg) {
  const u = new URL(location.href); u.search = ''; u.hash = 'c=' + encode(cfg); return u.toString();
}

/* Saved designs live only in this browser (localStorage). Never required for the flow to work. */
const KEY = 'kc-designs';
export function listSaved() { try { return JSON.parse(localStorage.getItem(KEY) || '[]'); } catch (e) { return []; } }
export function saveDesign(cfg) {
  const ref = refOf(cfg);
  try {
    const list = listSaved().filter((d) => d.ref !== ref);
    list.unshift({ ref, cfg, ts: Date.now() });
    localStorage.setItem(KEY, JSON.stringify(list.slice(0, 8)));
    return ref;
  } catch (e) { return null; }
}
export function removeSaved(ref) { try { localStorage.setItem(KEY, JSON.stringify(listSaved().filter((d) => d.ref !== ref))); } catch (e) {} }
