# 21. Desktop, Tablet & Mobile Test Report (v2)

Date: 2026-11-06. Method: headless Chromium (Playwright's bundled build) driven over the Chrome DevTools Protocol by a small Node script. Served locally with `python3 -m http.server`. Screenshots reviewed by eye at every section.

## Viewports
| Run | Size | Result |
|---|---|---|
| Desktop | 1440×900 | ✅ |
| Tablet | 834×1112, touch | ✅ (after fix 4) |
| Mobile | 390×844 @2x, touch | ✅ (after fix 3) |
| Reduced motion | 390×844, `prefers-reduced-motion: reduce` | ✅ All content visible, no animation |
| JavaScript disabled | 1440×900 | ✅ All content visible. Craft rows expanded, rail scrolls natively |

## Functional checks (final run)
| Check | Result |
|---|---|
| Console errors / failed requests | 0 |
| Broken images | 0 |
| Horizontal page overflow | 0 px on all viewports |
| WhatsApp links (5) | All `wa.me/919677184462?text=…` with prefilled messages |
| Phone links | `tel:+919677184462` ×2 |
| Menu | Opens, `aria-expanded=true`, focus moves to the first link, Esc closes |
| Video dialog | Opens a YouTube-nocookie embed in the right aspect (9:16 Shorts / 16:9 videos), Esc closes, iframe removed on close (video stops) |
| Pinned project rail (≥1024 px) | Pins and translates with scroll (e.g. −1316 px at midpoint), progress bar fills |
| Mobile rail | Native swipe with scroll-snap. Progress bar follows (0.24 after a 700 px swipe) |
| Craft index | Desktop hover/focus swaps the sticky image. Mobile tap opens an accordion with inline image |
| Airbrush story | Active step and image change with scroll (desktop). Inline images (mobile) |
| Map | No Google request until "Load map". The iframe then loads |

## Performance (first visit, empty cache, local server)
| Metric | Desktop | Mobile |
|---|---|---|
| Initial transfer | ~390 KB | ~565 KB (3 hero images at 2× density) |
| LCP | ~1.3 s (includes the 1 s intro on first visit) | <0.1 s on repeat views |
| CLS | **0** (was 0.38 before fix 2) | 0 |
| JS | 13 KB, no libraries | same |

Local-server numbers flatter real networks. Re-test on the live domain with PageSpeed Insights.

## Issues found and fixed
1. **404**: `p-malaysian-rxz-960.webp` doesn't exist (source cover only 720 px). Srcset now points at the 720 px file.
2. **CLS 0.38**: the web font swap at ~660 ms moved the hero text and ticker. Fonts are now self-hosted and preloaded, and the hero waits for `document.fonts.ready` (max 1.2 s). CLS is now 0.
3. **Mobile nav**: the "KC Customs" wordmark wrapped and collided with the WhatsApp button below 520 px. It's hidden there now (the logo stays).
4. **Tablet rail**: cards were ~1,100 px tall. Card width is now capped by viewport height.
5. **Desktop rail**: card captions overlapped the progress bar. Cards are smaller and the bar has moved.
6. **Academy collage**: the right-hand images stretched the grid. They are now absolutely positioned inside their cells.
7. **Image quality**: the blurry RXZ action frame was replaced with a sharp 16:9 cover. Two mosaic frames with on-screen stickers were replaced.
8. **Overlay numbers** used `mix-blend-mode: difference`, which turned muddy on purple. They now use solid text with a shadow.
9. **v1 bug fixed**: content stayed invisible without JS. Reveal styles now only apply under `html.js`.

## Not tested
- Real devices (iOS Safari, low-end Android), Firefox, and real-network throttling.
- Screen-reader walkthrough (semantics were checked in code: landmarks, skip link, labelled buttons, `aria-expanded`, dialog labelling, alt text).
- YouTube playback inside the dialog. Headless Chromium loads the embed, but actual video playback was not verified.
