# 22. Minimalist Redesign (v3): what changed and why

Date: 2026-11-06. Goal: less text, fewer sections, bigger visuals. v2 is backed up in the session scratchpad (`index.v2.html`, `style.v2.css`, `main.v2.js`).

## Section audit
| v2 section | v3 decision |
|---|---|
| Hero + crafts ticker | Hero kept, shorter line. Ticker removed (duplicated the crafts). Stats moved into the hero |
| Statement quote + facts strip | Merged: stats → hero, quote → About |
| Craft index (9 rows + paragraphs + sticky stage) | **01 Signature crafts**: 9 tall image tiles, name only, tap to watch |
| Projects rail (8, pinned scroll) + Two-stroke builds (4 spreads) | **02 Featured builds**: one gallery of 12 builds with model filters (All · RX King · RXZ · RX100/RX115 · Restoration & beyond). Pinned scroll removed (it added ~3 screens) |
| Airbrush story + Hydro dipping + Behind-the-craft mosaic | **03 Layer by layer**: 3 tabs (Airbrush · Hydro dip · Studio floor), each a horizontal strip with 2–4-word captions |
| (new) | **04 Design your bike**: pick ride / work / finish (+ optional idea) → preview swaps to matching KC work → opens WhatsApp with the build summary. A website feature, not a new service |
| Academy | **05 Academy**: subject chips, one proof line, two CTAs |
| About + community strip | **06 Chandu**: two-sentence story, quote, three community thumbnails |
| Visit + footer | **07 Visit**: full-bleed storefront, WhatsApp/Call, address, map on request. Slim footer |

## Result
| Viewport | v2 length | v3 length | Change |
|---|---|---|---|
| Desktop 1440×900 | 21,388 px (23.8 screens) | 6,533 px (7.3 screens) | **−69%** |
| Mobile 390×844 | 16,874 px (20.0 screens) | 6,943 px (8.2 screens) | **−59%** |

Sections: 11 → 8 (hero + 7). Every verified project, craft, process image and fact from v2 is still on the page. Long-form detail lives in `16_PROJECT_LIBRARY.md`.

## Text kept (all sourced)
Tagline "Beyond the Expectations"; stats (17M+ views, 84K, 48K, studio 2026); Red Rocket (first bike, ₹2.7L+ parts); Malaysian RXZ (Murugan panel); Maharashtra client; PU top coat & clear coat; hydro parts (Aerox, KTM 390, RXZ, Dio); academy subjects, students from Bengaluru/Tiruppur, KC Syndicate ceremony; founder story (RXZ 2014, Pallavaram → Chromepet Aug 2026, caricature artist, natural bodybuilder, men's physique athlete); two founder quotes; address and phone.

## Interaction changes
- Shared horizontal **track** component: native swipe on touch, mouse drag, arrow buttons (hover devices ≥900 px), keyboard arrows, progress bar.
- Build filters, ARIA tabs (arrow-key navigation), configurator built on native radio inputs (keyboard/screen-reader friendly).
- Kept: intro logo reveal, hero triptych + parallax, hover frame previews, video dialog, click-to-load map, WhatsApp prefills, reduced motion, no-JS fallback.
- Desktop shows inline nav links (≥1100 px). Mobile uses the full-screen menu.

## Test results (headless Chromium, final run)
Desktop 1440×900, tablet 834×1112, mobile 390×844 @2x, reduced motion, JS disabled.
- 0 console errors, 0 broken images, 0 px horizontal overflow, CLS 0 on all viewports.
- Arrows scroll the builds rail. The RX King filter shows 5 of 12. Hydro tab selects correctly.
- Configurator produced: "Hi KC Customs, I want to design my bike. • Bike: RX King • Work: Hydro dipping • Finish: Chrome • Idea: Purple skulls. I can send photos."
- Menu focus and Esc, video dialog open and Esc, map load all pass.
- Fixed during testing: build cards too tall at 900 px height, configurator preview too tall on tablet, hero label colliding with headline on phones.

Not tested: real iOS/Android devices, Safari/Firefox, YouTube playback itself.
