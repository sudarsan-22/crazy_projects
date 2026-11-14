# 23. Feature: Design Your Dream Bike

Date: 2026-11-06. Page: `site/design.html`. Code: `site/configurator/`. Homepage entry: section 04 of `site/index.html`.

## 1. Research: verified option catalogue
Built from the 262-video inventory (`13`) plus visual checks of covers and frames (`16`). Every option in `configurator/catalogue.js` carries its source video.

| Category | Options offered | Evidence |
|---|---|---|
| Models | RX100, RXZ, RX115 | HcIpbg8CbIs, D46gpxd8nA4 · vRxt4pK-0wA, ZNegxLjxVZA · X8-hUFeROlM, P08bwaDRwRc |
| Finish | Gloss (PU top coat + clear), Candy, Chrome, Pearl | tWAe6b1ONRU · cq1YADod7Z8 · oWhoaVNHnH4 · cq1YADod7Z8 |
| Base colours | Chrome Red, Candy Red, Candy Blue, KC Purple, Lime, Racing Yellow, Pearl White, Hot Pink, Gold, Gloss Black, **plus any colour** (custom paint) | Each colour is tied to a KC build in the catalogue |
| Graphics | Clean, Twin stripes (decal style), KC layers, Colour splash, Flames, Lettering | R-jAihOHzc0 (6-speed decals), X8-hUFeROlM, HcIpbg8CbIs, FJHeepFVawY, q9GEdi3sdlY; stickering classes |
| Airbrush artwork | Deity panel (Murugan), Deity panel (Kali), Skull & flames, Cartoon badge, Caricature, Script lettering. Placement: side panels or tank | ZNegxLjxVZA, 66u_MtxUcVE, FJHeepFVawY, biiIjij08T4, DW4hmWpu3SM, q9GEdi3sdlY (thumbnails are crops of those frames) |
| Hydro dip | Carbon look, Skulls, Roses & skulls, Sugar skull, Sticker bomb | cq1YADod7Z8 (carbon hydro dip), GnQmHIi4ZOE, gFQ1GW-Y46s, J6uavvancpw |
| Components | Fuel tank, side panels, front mudguard, rear mudguard/tail, headlight cowl (RXZ/RX115), engine cover. Each: main / accent / hydro / stock | Full-bike paint videos. Engine covers Ac0JbaZAokQ, sP3-uZ3z7qQ |
| Rims | Stock chrome, Gold, Pink, Match main colour | X8-hUFeROlM, kkQ9kdpLZDA, d4Amxf5w4BE (wheel painting) |
| Modifications (enquiry only, not drawn) | Full restoration (all), imported performance/CNC parts (all), imported exhaust (RX100, RXZ), 4→6-speed (RXZ), Malaysian-style (RXZ), RX King-style conversion (RX100) | EOkal7lTLC0, MCiFikHUXT0, TTO78NUK2AU, Glsa5eccRBI, ZNegxLjxVZA, EQ3jW9j3Fb8 |

**Deliberately excluded:** matte and metallic (no KC evidence; the UI says "ask KC"). Prices (none approved). Models without builds on the channel (RX King, RX135 and Aerox point to WhatsApp instead).

## 2. Preview engine: 2D vs 3D
| | 2D layered SVG (chosen) | 3D (Three.js + GLB) |
|---|---|---|
| Needs | Vector side-view per model with separate part paths | A licensed, accurate GLB of each model with separate meshes per part |
| Asset availability | Drawn for this project | **None available.** No KC 3D models exist. A random downloaded model would break "no random motorcycle images" and licensing |
| Colour/finish/pattern accuracy | Per-part gradients (gloss/candy/chrome/pearl), real KC texture patterns, clip-masked graphics and artwork | Good if a model existed |
| Weight / mobile | ~30 KB JS + ~200 KB textures, instant on phones | Three.js ~600 KB+, model several MB, GPU-heavy |
| Honesty | Labelled "concept illustration · not to scale" | Would need to be accurate to justify itself |

**Decision: 2D layered SVG.** Genuine 3D isn't possible without a real model, and faking it with a static image is ruled out. The renderer is modular, so a 3D view could replace `render.js` later if KC commissions GLB models. **Limitation:** the bikes are stylised illustrations, not photographs. Shapes are simplified.

## 3. Interaction flow
1. **Picker**: 3 large live-rendered model cards with name, one-line description and Select, plus saved designs from this browser.
2. **Workspace**:
   - **Desktop (≥1100 px), three panels.** Left: categories and options. Centre: preview with views (Full / Tank / Side / Wheels), zoom ± and wheel zoom, drag-to-pan, compare (stock vs yours slider), undo/redo (also Ctrl+Z / Ctrl+Shift+Z) and reset. Right: summary (each row jumps to its category), reference ID, Save, Share link, Image and **Request this build**.
   - **Mobile**: a sticky preview on top, one category per step (Paint → Graphics → Airbrush → Hydro dip → Parts → Extras → Review) with Back/Next, and the summary on the Review step.
3. **Request this build** dialog:
   - Preview, reference and optional name.
   - A required checkbox: "I understand this is a concept preview…".
   - **Send on WhatsApp** to +91 96771 84462 with the full summary and a design link.
   - Download image (PNG). **Share image** uses the Web Share API with the file, where supported, so the picture can go straight into WhatsApp on phones.

Configuration reference: `KC-<MODEL>-<5 chars>` (hash of the configuration). Share links carry the whole configuration in the URL hash, so they need no server. The page also restores from its own URL.

## 4. Architecture (adapted, no framework)
```
site/design.html                  page shell (picker, workspace, request dialog)
site/configurator/
  catalogue.js     data: models, colours, finishes, graphics, artwork, hydro, parts, rims, mods (+ sources)
  bikes.js         SVG geometry per model + camera views   ← add a model here
  render.js        pure renderer: config → SVG (gradients, patterns, clips)
  store.js         configuration manager: undo/redo, refs, share URLs, saved designs
  exporter.js      summary rows, WhatsApp text, PNG export (inlines textures → canvas)
  studio.js        UI controller (picker, panels, preview, summary, request)
  studio.css       studio styles (reuses site tokens)
  textures/        10 real KC texture/artwork crops (WebP)
```
To add a model: add an entry to `MODELS` (catalogue), its paths to `bikes.js`, and model ids to any `MODS` it supports.

## 5. Tests (headless Chromium, final run)
- **Desktop 1440×900:**
  - Picker shows 3 cards. RXZ opens the studio.
  - Paint, graphics with lettering, artwork, hydro on the front mudguard, parts and rims, and mods (5 RXZ-specific shown) all applied. The configuration was verified from the URL state.
  - Undo/redo restore the note. Compare slider, tank view and zoom work.
  - Save stores the design in localStorage. The shared link reopens the same reference (KC-RXZ-P3UQZ).
  - PNG export produces a 1600×1240 image (~630 KB).
  - The send button stays disabled until the checkbox is ticked. The WhatsApp URL is `wa.me/919677184462?text=…` with every summary field and the disclaimer.
- **Mobile 390×844:** all 7 steps render with **0 elements spilling past the viewport** (fixed during testing). The review step shows the summary, and Next on the last step opens the request dialog.
- **Homepage:** 3 entry cards render live bikes and link to `design.html?bike=…`.
- 0 console errors.

Issues found and fixed:
1. Mobile grid column grew to its content (cut-off preview and options). Fixed with `minmax(0,1fr)` and wrapping controls.
2. Exported image text overlapped the bike.
3. Default accents showed as "Custom #hex" (they now use palette colours).
4. The sticky mobile preview was see-through at the bottom.

**Not tested:** real iOS/Android share sheets, Safari/Firefox, WhatsApp receiving the message, and opening share links on a deployed domain (they use the current URL, so they work once hosted).

## 6. Questions for Chandu
- Approve the option list. Are matte or metallic finishes offered? Any graphics or artwork styles to add or remove?
- Can we publish starting prices per option? (Currently none.)
- Real side-view photos of RX100/RXZ/RX115 builds against a plain wall would let us trace more accurate illustrations.
- Which models next (RX King, RX135, Aerox 155)?
