# 12. Audit of Website v1 (before the redesign)

Date: 2026-11-06. Scope: `site/` (index.html, css/style.css, js/main.js, assets/img) and research docs 01–11.

## Architecture
- Static single page: one HTML file (~300 lines), one CSS file (~250 lines, tokens in `:root`), one JS file (~50 lines). No build step, no framework. Total weight ~1.5 MB (10 JPEG thumbnails).
- Fonts: Google Fonts (Anton + Inter), `display=swap`.
- JS features: WhatsApp prefilled links (`data-wa`), click-to-load YouTube (lite facade), IntersectionObserver reveal, footer year.
- SEO: title/description, OG tags, `LocalBusiness`-style JSON-LD (`AutoPartsStore`).

## What works (keep)
| Item | Why keep |
|---|---|
| No framework, static files | Fast, cheap hosting, easy to maintain. Nothing in the brief needs React/Next.js |
| WhatsApp-first conversion with prefilled messages | Matches how the business already sells (every YouTube title carries the number) |
| Click-to-load YouTube | Keeps YouTube's ~1 MB player off the initial load |
| Honest content policy (no fake prices, reviews or hours) | Required by the brief |
| Reduced-motion support, mobile-first CSS | Required by the brief |
| JSON-LD with address/phone/sameAs | Local SEO |

## Problems found
### Content (biggest gap)
1. Built from **12 of 262** public videos. It misses verified services and facts: **reverse painting** (the channel's most-viewed item, 2.4M views), helmet painting, engine-cover art, chrome/candy finishes, PU top coat + clear coat, RX135→RX King and 4→6-speed conversions, imported performance parts, ceramic coating, cars (VW Polo), sneakers, Malaysia community links, the **new Chromepet studio (opened 15 Aug 2026)**, and the academy's actual subjects (painting, airbrush, hydro dipping, stickering, reverse painting, designing).
2. The brand's own tagline **"Beyond the Expectations"** (studio sign, graffiti wall, painted into work) was not used. The hero line "Your bike. Your colours. Built by hand." was generic.
3. The "How it works" steps were written by us, not evidenced.

### Visual
4. Images are YouTube thumbnails at 480–1280 px, two of them letterboxed (black bars baked in) and one upscaled from 480×360.
5. One image (EdImonHW1JA) appears **three times**, another twice.
6. Repetitive card grids (services, videos, steps all use the same rounded card), which reads as a template.
7. Proof bar item "1 studio + training academy" is filler.

### Functional / accessibility
8. **Bug:** `.reveal` elements start at `opacity:0`. The `.no-js` fallback class is never set, so if JavaScript fails the content stays invisible.
9. **Mobile has no navigation**. The links are hidden below 720 px with no menu replacement.
10. No skip link. Video embeds replace the button without a way to close or go full-screen in a focused view.
11. Google Maps iframe loads for every visitor (third-party weight + tracking) even if they never look at it.
12. `og:image` is relative (needs an absolute URL once the domain exists). JSON-LD type `AutoPartsStore` is imprecise; `AutoBodyShop` fits better.

## Decision
Keep the static HTML/CSS/JS architecture and the working features (WhatsApp links, lite video, JSON-LD, reduced motion). Rebuild the content, layout and interaction layer from the expanded research. No framework or animation library is needed; see `19_ANIMATION_INTERACTION_SPEC.md` for why.
