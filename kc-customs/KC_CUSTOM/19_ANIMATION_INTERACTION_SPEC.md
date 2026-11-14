# 19. Animation & Interaction Specification

## Technology decision
**Vanilla JS + CSS. No GSAP, no smooth-scroll library.**
- Every effect below is a transform/opacity/clip-path change driven by `IntersectionObserver` or one `requestAnimationFrame` scroll loop. That's about 300 lines of JS.
- GSAP + ScrollTrigger would add ~70 KB and a dependency for effects we can do natively.
- Native scrolling is kept (no scroll-jacking). The pinned rail uses `position: sticky`.

## Motion tokens
| Token | Value |
|---|---|
| `--ease-out` | cubic-bezier(.16,1,.3,1) |
| `--ease-io` | cubic-bezier(.65,0,.35,1) |
| Durations | 180 ms (UI), 600 ms (reveals), 900–1200 ms (hero panels) |
| Stagger | 80–120 ms |

## Interactions
| Where | Behaviour | Trigger | Reduced motion |
|---|---|---|---|
| Loader | Logo scales 0.94→1 with a purple light sweep, overlay fades out (~0.9 s). First visit per session only. Content is in the DOM underneath | load | Skipped |
| Nav | Transparent → solid after 40 px. "Menu" opens a full-screen overlay with numbered links; Esc closes; focus moves in and back | scroll / click | Instant |
| Hero | Three panels reveal with `clip-path: inset()` staggered. Slight parallax per panel (−6%…+6%) while scrolling past. Mobile: one panel, crossfading through the three images every 5 s | load / scroll | Static first image |
| Text reveals | Lines rise 24 px + fade | IO 15% | Visible immediately |
| Statement | Each word goes from 18% → 100% opacity as the section passes through the viewport | rAF scroll progress | Full opacity |
| Fact strip | Numbers count up once | IO | Final numbers |
| Craft index | Hover/focus/tap on a row swaps the sticky image (clip reveal + scale 1.06→1) | pointer / focus / IO on mobile | Instant swap |
| Project rail | Desktop ≥ 1024 px: section height = track overflow; inner sticky; `translateX` follows scroll progress; progress bar. Mobile: native horizontal scroll with `scroll-snap` | rAF | Native scroll on all sizes |
| Project cards | Hover cycles 3 real video frames every 700 ms; image scales 1.04 | pointer | No cycling |
| Airbrush story | Desktop: sticky image stage; active step set by IO (rootMargin −45%); image clip-wipes to the next | IO | Instant swap |
| Hydro sequence | Panels reveal left→right with clip-path | IO | Visible |
| Mosaic | Tiles reveal staggered | IO | Visible |
| Video dialog | `<dialog>` with YouTube-nocookie iframe (9:16 for Shorts, 16:9 for videos), loaded only on open, removed on close. Esc / backdrop / close button. Native YouTube controls and full-screen | click | Same |
| Map | Click-to-load iframe (no Google request until asked) | click | Same |
| Buttons | Background fill slides in, arrow nudges 4 px | hover/focus | Colour change only |

## Performance rules
- Animate only `transform`, `opacity`, `clip-path`.
- The scroll loop runs only while the hero, statement or rail is on screen (IO-gated), and reads layout once per frame.
- `content-visibility: auto` on long lower sections.
- No custom cursor (it would not help usability).
