# 17. Brand Design System v2

Built on the **existing** identity (see `04`). Nothing here replaces the logo.

## Evidence-based identity elements
| Element | Evidence |
|---|---|
| Logo A (digital): glitter-purple 3D "KC" + gold script "Customs" on near-black | YouTube avatar |
| Logo B (physical): purple "KC" + **lime-green** "customs" | Studio neon sign, storefront, video thumbnails |
| Tagline **"Beyond the Expectations"** | Storefront fascia, graffiti wall, painted into customer work (Ij2xuOjz4qI) |
| "KC STYLE" / #Kcstyle | Video titles, founder's jersey |
| Studio: purple walls, wall of helmets, wall of painted panels, checkered floor, graffiti | New Chromepet studio Shorts (Aug–Oct 2026) |

## Colour tokens
| Token | HEX | Use |
|---|---|---|
| `--ink` | #0B0D11 | Page background (deeper than v1 so photos glow) |
| `--surface` | #12171D | Logo background colour; alternate sections |
| `--surface-2` | #1A1F27 | Raised panels |
| `--violet` | #813D8A | Brand purple (logo flake mid-tone) |
| `--violet-deep` | #58326D | Shadows, gradients |
| `--violet-glow` | #B177C1 | Purple text on dark (passes contrast) |
| `--gold` | #B7885C | Logo script. Hairlines, numbers |
| `--gold-light` | #D9B07F | Gold text on dark, accent italics |
| `--lime` | #B8F23C | From signage. **One accent only**: "open now" dot, active indicators |
| `--text` | #EEEAF2 | Body |
| `--muted` | #9C98A6 | Secondary text (≈7:1 on --ink) |
| `--wa` | #25D366 | WhatsApp floating button only (recognisability) |

Rules: dark base. Purple carries brand; gold is for detail, never large fills; lime appears at most once per screen. Bike photography supplies the rest of the colour.

## Typography
| Role | Font | Why |
|---|---|---|
| Display | **Anton** (uppercase, tight) | Echoes the heavy condensed captions in KC's videos |
| Accent | **Instrument Serif Italic** in gold | Gives premium editorial contrast and nods to the gold script "Customs" without copying it |
| Body / UI | **Inter** 400/500/600 | Legible on small screens |
| Spec labels | Inter, uppercase, 0.18em tracking, tabular numbers | "Spec-sheet" metadata (model, year, views) |

Scale: `clamp()` fluid sizes. Display 3–9.5rem, H2 2.4–5.5rem, body 1–1.06rem, labels 0.72rem.

## Layout
- **Vertical-first.** All of KC's best media is 9:16, so the core module is a tall "panel" (like the painted panels on the studio wall), not a 16:9 card.
- 12-column fluid grid, 16 px gutters on mobile, max content width 1320 px. Full-bleed sections for imagery.
- Asymmetric editorial compositions. Section numbers (01–10) in gold.

## Image treatment
- Real KC frames only. Slight darkening gradient for legibility, no colour filters that change paint colour.
- Never show the Hayabusa render as completed work.
- Crops remove burned-in captions and prices.

## Components
Nav + overlay menu · Hero triptych · Statement with word reveal · Fact strip · Craft index (list + sticky stage) · Project rail (pinned horizontal) · Sticky process story · Three-step hydro sequence · Model spreads · Workshop mosaic · Community strip · Academy split · Founder portrait · Visit/contact block · Video dialog · Floating WhatsApp.

## Voice
Direct, proud, plain English, with the founder's own phrases quoted and attributed. No invented superlatives ("best in Chennai", "No. 1"). Owner claims ("Best in class", "Beyond the Expectations") are used as **his** words.
