// KC Customs website proposal deck (pptxgenjs, structured: theme + layouts + sections)
const pptxgen = require('pptxgenjs');
const { applyTheme } = require('/home/sudarsan/.claude/skills/synced/924a4c77-edd8-408c-97b3-245dcd24dfcd_849415e9-0fb9-4ed7-874d-d992a6eb102b/pptx/scripts/apply_theme.js');
const IMG = '/tmp/claude-1000/-home-sudarsan-Documents-crazy-projects/b2288fb5-b8d7-4c5b-a308-196a3c544618/scratchpad/deck/img/';
const OUT = '/home/sudarsan/Documents/crazy_projects/kc-customs/proposal/KC-Customs-Website-Proposal.pptx';

const THEME = {
  name: 'KC Customs', headFontFace: 'Arial', bodyFontFace: 'Calibri',
  colors: { dk1: '0B0D11', lt1: 'FFFFFF', dk2: '12171D', lt2: 'EEEAF2', accent1: '813D8A', accent2: 'D9B07F', accent3: 'B177C1', accent4: 'B8F23C', accent5: '25D366', accent6: '9C98A6', hlink: 'D9B07F', folHlink: 'B177C1' },
};
const pres = new pptxgen();
pres.layout = 'LAYOUT_WIDE'; // 13.33 x 7.5
pres.theme = { headFontFace: THEME.headFontFace, bodyFontFace: THEME.bodyFontFace };
pres.title = 'KC Customs: Website Proposal';
pres.company = 'KC Customs';
const C = pres.SchemeColor;
const BG = '0B0D11', PANEL = '1A1F27';

pres.defineSlideMaster({
  title: 'KC_COVER', background: { color: BG },
  objects: [{ placeholder: { options: { name: 'title', type: 'title', x: 0.7, y: 2.2, w: 7.2, h: 2.2, fontSize: 54, bold: true, color: C.background2, valign: 'top', align: 'left', margin: 0 }, text: '' } }],
});
pres.defineSlideMaster({
  title: 'KC_TITLE_ONLY', background: { color: BG },
  objects: [
    { placeholder: { options: { name: 'title', type: 'title', x: 0.7, y: 0.45, w: 11.9, h: 0.9, fontSize: 36, bold: true, color: C.background2, valign: 'middle', align: 'left', margin: 0 }, text: '' } },
    { text: { text: 'KC CUSTOMS · WEBSITE PROPOSAL', options: { x: 0.7, y: 6.95, w: 5, h: 0.3, fontSize: 10, color: C.accent6, charSpacing: 2, margin: 0 } } },
  ],
  slideNumber: { x: 12.2, y: 6.95, w: 0.5, h: 0.3, fontSize: 10, color: C.accent6, align: 'right' },
});

const T = (s, text, o) => s.addText(text, { isTextBox: true, margin: 0, fontFace: THEME.bodyFontFace, color: C.background2, ...o });
const label = (s, text, x, y, w = 6) => T(s, text.toUpperCase(), { x, y, w, h: 0.3, fontSize: 11, bold: true, color: C.accent2, charSpacing: 2 });
const panel = (s, x, y, w, h, name) => s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x, y, w, h, rectRadius: 0.08, fill: { color: PANEL }, line: { color: '2A303A', width: 0.75 }, objectName: name });
const img = (s, file, x, y, w, h, name, type = 'cover') => s.addImage({ path: IMG + file, x, y, w, h, sizing: { type, w, h }, altText: name, objectName: name });
const title = (s, runs) => s.addText(runs, { placeholder: 'title' });
const accent = (t) => ({ text: t, options: { italic: true, color: C.accent2, fontFace: 'Cambria', bold: false } });

// ---------- 1 COVER ----------
pres.addSection({ title: 'Opening' });
let s = pres.addSlide({ masterName: 'KC_COVER', sectionTitle: 'Opening' });
s.addImage({ path: IMG + 'logo-400.png', x: 0.7, y: 0.7, w: 1.1, h: 1.1, altText: 'KC Customs logo', objectName: 'logo' });
label(s, 'Website proposal · Chromepet, Chennai · November 2026', 0.7, 1.95, 7.5);
title(s, [{ text: 'A website for ' }, accent('KC Customs')]);
T(s, 'Beyond the Expectations, now online. A digital showroom built from your own work.', { x: 0.7, y: 4.6, w: 6.6, h: 0.9, fontSize: 20, color: C.background2 });
T(s, 'Live demo · full website tour video', { x: 0.7, y: 6.2, w: 6.5, h: 0.4, fontSize: 14, color: C.accent6 });
img(s, 'sig.jpg', 8.4, 0, 4.93, 7.5, 'hero image');
s.addNotes('Thank Chandu for his time. This is a proposal for a website built entirely from KC Customs\' own videos and photos. We will show the live site, the walkthrough video, and what we need to go live.');

// ---------- 2 OPPORTUNITY ----------
pres.addSection({ title: 'Why a website' });
s = pres.addSlide({ masterName: 'KC_TITLE_ONLY', sectionTitle: 'Why a website' });
title(s, [{ text: 'A huge audience with ' }, accent('no home base')]);
[['84K', 'Instagram followers'], ['48K', 'YouTube subscribers'], ['17M+', 'YouTube views'], ['0', 'websites']].forEach(([n, l], i) => {
  const x = 0.7 + i * 3.0;
  panel(s, x, 1.8, 2.75, 2.4, 'stat ' + l);
  T(s, n, { x: x + 0.3, y: 2.05, w: 2.2, h: 1.2, fontSize: 60, bold: true, fontFace: THEME.headFontFace, color: i === 3 ? C.accent2 : C.accent3 });
  T(s, l, { x: x + 0.3, y: 3.35, w: 2.2, h: 0.5, fontSize: 16, color: C.accent6 });
});
T(s, [
  { text: 'People already search for KC. ', options: { bold: true } },
  { text: 'A search like "airbrush painting Chennai" or "RX100 restoration Chennai" has no KC page to land on. Every enquiry depends on someone finding your Instagram first.' },
], { x: 0.7, y: 4.7, w: 11.6, h: 1.2, fontSize: 18 });
s.addNotes('All numbers are from the public profiles in November 2026: 84.4K Instagram followers, 48.1K YouTube subscribers, 17.5M views across 262 public videos. There is no website and no Google listing that we could find.');

// ---------- 3 RESEARCH ----------
s = pres.addSlide({ masterName: 'KC_TITLE_ONLY', sectionTitle: 'Why a website' });
title(s, [{ text: 'We studied all ' }, accent('262 of your videos')]);
const services = ['Custom airbrush & chrome paint', 'Reverse painting', 'Hydro dipping', 'RX King & RXZ conversions', 'Restoration (RXZ, Chetak)', 'Engine-cover art', 'Helmets', 'Cars & sneakers', 'Painting academy'];
services.forEach((t, i) => {
  const col = i % 2, row = Math.floor(i / 2), x = 0.7 + col * 3.55, y = 1.75 + row * 0.82;
  panel(s, x, y, 3.35, 0.64, 'service ' + t);
  T(s, t, { x: x + 0.25, y: y + 0.12, w: 3.0, h: 0.4, fontSize: 15 });
});
T(s, 'Every service, project and fact on the site comes from your own titles, descriptions and footage. Nothing is invented.', { x: 0.7, y: 6.0, w: 6.9, h: 0.7, fontSize: 14, color: C.accent6 });
img(s, 'redrocket.jpg', 8.2, 1.6, 2.15, 3.82, 'Red Rocket RXZ');
img(s, 'hydro.jpg', 10.5, 1.6, 2.15, 3.82, 'hydro dipped panel');
T(s, 'Project Red Rocket · hydro dip, from your videos', { x: 8.2, y: 5.55, w: 4.45, h: 0.35, fontSize: 12, color: C.accent6 });
s.addNotes('The research covered 44 long videos and 218 Shorts. Highlights: reverse painting is the most-watched item at 2.4 million views; the academy teaches painting, airbrush, hydro dipping, stickering, reverse painting and designing; the new Chromepet studio opened in August 2026.');

// ---------- 4 BRAND ----------
s = pres.addSlide({ masterName: 'KC_TITLE_ONLY', sectionTitle: 'Why a website' });
title(s, [{ text: 'Your brand, ' }, accent('kept exactly')]);
s.addImage({ path: IMG + 'logo-400.png', x: 0.7, y: 1.8, w: 2.2, h: 2.2, altText: 'KC Customs logo', objectName: 'logo large' });
[['813D8A', 'KC Purple'], ['D9B07F', 'Script Gold'], ['12171D', 'Night Black'], ['B8F23C', 'Signage Lime']].forEach(([hex, n], i) => {
  const x = 3.2 + i * 1.3;
  s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x, y: 1.8, w: 1.1, h: 1.1, rectRadius: 0.1, fill: { color: hex }, line: { color: '3A3F48', width: 0.75 }, objectName: 'swatch ' + n });
  T(s, n, { x, y: 3.0, w: 1.25, h: 0.3, fontSize: 12, color: C.accent6 });
});
T(s, '"Beyond the Expectations"', { x: 0.7, y: 4.4, w: 7, h: 0.7, fontSize: 30, italic: true, fontFace: 'Cambria', color: C.accent2 });
T(s, 'Your own tagline from the storefront and the studio wall is the headline of the site. The logo is untouched, and the colours are sampled from it.', { x: 0.7, y: 5.15, w: 7, h: 1.0, fontSize: 16 });
img(s, 'store.jpg', 8.6, 1.6, 4.05, 4.3, 'Chromepet storefront');
s.addNotes('We did not redesign the logo. Colours were sampled from the logo and the studio signage. The tagline Beyond the Expectations appears on the storefront and graffiti wall, so it leads the website.');

// ---------- 5 THE SITE ----------
pres.addSection({ title: 'The website' });
s = pres.addSlide({ masterName: 'KC_TITLE_ONLY', sectionTitle: 'The website' });
title(s, [{ text: 'A digital showroom in ' }, accent('8 sections')]);
img(s, 'hero.jpg', 0.7, 1.65, 7.6, 4.275, 'homepage hero screenshot');
['Hero: your tagline + studio photos', 'Signature crafts', 'Featured builds', 'Process: airbrush · hydro · studio', 'Design your dream bike', 'Academy', 'Chandu\'s story', 'Visit Chromepet + WhatsApp'].forEach((t, i) => {
  const y = 1.65 + i * 0.54;
  T(s, String(i + 1).padStart(2, '0'), { x: 8.75, y, w: 0.55, h: 0.4, fontSize: 14, bold: true, color: C.accent2 });
  T(s, t, { x: 9.3, y, w: 3.4, h: 0.4, fontSize: 15 });
});
T(s, 'Big visuals, little text. WhatsApp is one tap away on every screen.', { x: 0.7, y: 6.15, w: 7.6, h: 0.4, fontSize: 14, color: C.accent6 });
s.addNotes('Walk through the live site. The page is about seven screens long on desktop, with large images and short text. Every project opens the original KC video.');

// ---------- 6 WORK IS THE HERO ----------
s = pres.addSlide({ masterName: 'KC_TITLE_ONLY', sectionTitle: 'The website' });
title(s, [{ text: 'Your work is ' }, accent('the hero')]);
img(s, 'crafts.jpg', 0.7, 1.65, 5.85, 3.29, 'crafts section screenshot');
img(s, 'builds.jpg', 6.8, 1.65, 5.85, 3.29, 'builds section screenshot');
[['9 signature crafts', 'Each tile plays your own video'], ['12 featured builds', 'Filter by RX King, RXZ, RX100/115, restoration'], ['Layer by layer', 'Airbrush, hydro dip and studio-floor tabs']].forEach(([h, b], i) => {
  const x = 0.7 + i * 4.05;
  T(s, h, { x, y: 5.25, w: 3.8, h: 0.45, fontSize: 20, bold: true, fontFace: THEME.headFontFace });
  T(s, b, { x, y: 5.75, w: 3.8, h: 0.6, fontSize: 15, color: C.accent6 });
});
s.addNotes('Red Rocket, Chrome Red, the Malaysian RXZ, Project Evergreen, the Chetak and the Polo art car all appear with their real videos. Hovering a build previews frames from its video.');

// ---------- 7 CONFIGURATOR ----------
pres.addSection({ title: 'Design your dream bike' });
s = pres.addSlide({ masterName: 'KC_TITLE_ONLY', sectionTitle: 'Design your dream bike' });
title(s, [{ text: 'Design your ' }, accent('dream bike')]);
img(s, 'studio.jpg', 0.7, 1.65, 7.6, 4.275, 'design studio screenshot');
[['Pick an RX', 'RX100, RXZ or RX115'], ['Customise', 'Candy, chrome, pearl · graphics · airbrush art · hydro patterns'], ['Compare & save', 'Stock vs custom slider · save · share link · image'], ['Request', 'The build goes to your WhatsApp']].forEach(([h, b], i) => {
  const y = 1.65 + i * 1.1;
  s.addShape(pres.shapes.OVAL, { x: 8.7, y, w: 0.55, h: 0.55, fill: { color: '813D8A' }, line: { color: '813D8A' }, objectName: 'step ' + (i + 1) });
  T(s, String(i + 1), { x: 8.7, y: y + 0.08, w: 0.55, h: 0.4, fontSize: 16, bold: true, align: 'center', color: C.background2 });
  T(s, h, { x: 9.45, y: y - 0.02, w: 3.3, h: 0.4, fontSize: 18, bold: true, fontFace: THEME.headFontFace });
  T(s, b, { x: 9.45, y: y + 0.38, w: 3.3, h: 0.6, fontSize: 14, color: C.accent6 });
});
T(s, 'Every option comes from a KC video. Previews are labelled as concept illustrations.', { x: 0.7, y: 6.15, w: 7.6, h: 0.4, fontSize: 14, color: C.accent6 });
s.addNotes('This is the feature people will remember. Options are limited to what KC has shown in videos: no matte or metallic, because we found no example. It is a 2D illustration, not a 3D model; a 3D version would need proper 3D models of each bike.');

// ---------- 8 ENQUIRIES ----------
s = pres.addSlide({ masterName: 'KC_TITLE_ONLY', sectionTitle: 'Design your dream bike' });
title(s, [{ text: 'Enquiries arrive ' }, accent('ready')]);
img(s, 'request.jpg', 0.7, 1.65, 7.6, 4.275, 'request dialog and WhatsApp message');
['Reference number for every design', 'Bike, colours, finish, art, hydro, parts and mods', 'A link that reopens the exact design', 'Customer confirms it is a concept', 'No prices shown until you approve them'].forEach((t, i) => {
  const y = 1.75 + i * 0.82;
  panel(s, 8.7, y, 3.95, 0.66, 'benefit ' + i);
  T(s, t, { x: 8.95, y: y + 0.13, w: 3.6, h: 0.42, fontSize: 15 });
});
s.addNotes('Instead of "price?" messages, KC receives a complete brief with a reference like KC-RXZ-5HONV. Customers can also download or share an image of their design.');

// ---------- 9 MOBILE ----------
pres.addSection({ title: 'Quality' });
s = pres.addSlide({ masterName: 'KC_TITLE_ONLY', sectionTitle: 'Quality' });
title(s, [{ text: 'Built for ' }, accent('phones first')]);
['phone-m01-hero.jpg', 'phone-m03-builds.jpg', 'phone-m02-step2.jpg'].forEach((f, i) => {
  const x = 0.9 + i * 2.6;
  s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x: x - 0.08, y: 1.57, w: 2.31, h: 4.86, rectRadius: 0.2, fill: { color: '050608' }, line: { color: '2A2D33', width: 1 }, objectName: 'phone frame ' + i });
  img(s, f, x, 1.65, 2.15, 4.7, 'phone screenshot ' + (i + 1));
});
T(s, 'Most of your audience arrives from Instagram on a phone.', { x: 8.9, y: 1.9, w: 3.8, h: 1.0, fontSize: 22, bold: true, fontFace: THEME.headFontFace });
['Swipe galleries instead of long pages', 'Sticky preview while designing', 'WhatsApp button always in reach', 'Tested at 390 px phone width'].forEach((t, i) => {
  T(s, t, { x: 8.9, y: 3.3 + i * 0.6, w: 3.8, h: 0.45, fontSize: 15, color: C.accent6, bullet: true });
});
s.addNotes('The mobile layout is designed separately: horizontal swipe galleries, a full-screen menu, and a step-by-step design studio.');

// ---------- 10 FAST & HONEST ----------
s = pres.addSlide({ masterName: 'KC_TITLE_ONLY', sectionTitle: 'Quality' });
title(s, [{ text: 'Fast, honest ' }, accent('and accessible')]);
[['565 KB', 'first load on a phone'], ['0', 'layout shift (CLS)'], ['0', 'errors in testing']].forEach(([n, l], i) => {
  const x = 0.7 + i * 2.55;
  panel(s, x, 1.8, 2.35, 2.1, 'metric ' + l);
  T(s, n, { x: x + 0.25, y: 2.0, w: 1.95, h: 0.9, fontSize: 34, bold: true, fontFace: THEME.headFontFace, color: C.accent3 });
  T(s, l, { x: x + 0.25, y: 3.0, w: 1.95, h: 0.6, fontSize: 14, color: C.accent6 });
});
T(s, 'What we will not do', { x: 8.6, y: 1.8, w: 4, h: 0.45, fontSize: 20, bold: true, fontFace: THEME.headFontFace });
['No fake reviews or testimonials', 'No invented prices or offers', 'No stock photos, only KC media', 'No services you have not shown'].forEach((t, i) => {
  T(s, t, { x: 8.6, y: 2.4 + i * 0.55, w: 4, h: 0.45, fontSize: 15, bullet: true });
});
T(s, 'Plain HTML, CSS and JavaScript, no heavy frameworks. Works with reduced-motion settings and screen readers, and still shows content if JavaScript is off.', { x: 0.7, y: 4.4, w: 7.4, h: 1.0, fontSize: 15, color: C.accent6 });
s.addNotes('Numbers come from headless Chrome tests on desktop, tablet and phone. Still to do before launch: testing on real iPhone and Android devices and in Safari.');

// ---------- 11 WHAT WE NEED ----------
pres.addSection({ title: 'Next steps' });
s = pres.addSlide({ masterName: 'KC_TITLE_ONLY', sectionTitle: 'Next steps' });
title(s, [{ text: 'What we need ' }, accent('from you')]);
[['Logo files', 'Original logo (PNG or SVG), both versions'], ['Original photos & clips', 'Finished bikes, close-ups, 5–15 s raw videos'], ['Permission', 'OK to use your YouTube and Instagram media'], ['Price policy', 'Show starting prices, or quote on WhatsApp only'], ['Academy details', 'Duration, fees, batch dates you want public'], ['Domain name', 'e.g. a .in domain you own']].forEach(([h, b], i) => {
  const col = i % 3, row = Math.floor(i / 3), x = 0.7 + col * 4.05, y = 1.8 + row * 2.2;
  panel(s, x, y, 3.8, 1.9, 'need ' + h);
  T(s, String(i + 1).padStart(2, '0'), { x: x + 0.3, y: y + 0.25, w: 1, h: 0.35, fontSize: 13, bold: true, color: C.accent2 });
  T(s, h, { x: x + 0.3, y: y + 0.65, w: 3.3, h: 0.45, fontSize: 20, bold: true, fontFace: THEME.headFontFace });
  T(s, b, { x: x + 0.3, y: y + 1.15, w: 3.3, h: 0.6, fontSize: 14, color: C.accent6 });
});
s.addNotes('The site works today with images taken from KC\'s YouTube. Original files will make it sharper, and KC\'s written OK is needed before launch. Students and clients shown in videos may need to agree too.');

// ---------- 12 NEXT STEPS ----------
s = pres.addSlide({ masterName: 'KC_COVER', sectionTitle: 'Next steps' });
s.addImage({ path: IMG + 'logo-400.png', x: 0.7, y: 0.7, w: 1.1, h: 1.1, altText: 'KC Customs logo', objectName: 'logo end' });
title(s, [{ text: 'Ready to go ' }, accent('live')]);
['Review the demo and share feedback', 'Send logo, photos and permission', 'Final polish and real-phone testing', 'Launch on your domain'].forEach((t, i) => {
  const x = 0.7 + i * 3.05;
  s.addShape(pres.shapes.OVAL, { x, y: 4.45, w: 0.6, h: 0.6, fill: { color: '813D8A' }, line: { color: '813D8A' }, objectName: 'next ' + (i + 1) });
  T(s, String(i + 1), { x, y: 4.55, w: 0.6, h: 0.4, fontSize: 18, bold: true, align: 'center' });
  T(s, t, { x, y: 5.25, w: 2.7, h: 0.8, fontSize: 16 });
});
T(s, 'Beyond the Expectations', { x: 0.7, y: 6.35, w: 6, h: 0.5, fontSize: 22, italic: true, fontFace: 'Cambria', color: C.accent2 });
s.addNotes('Close by agreeing the first step: feedback on the demo and the asset list. Share the website tour video with Chandu after the meeting.');

pres.writeFile({ fileName: OUT }).then(async () => { await applyTheme(OUT, THEME); console.log('written', OUT); });
