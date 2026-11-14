# 20. Asset Manifest & Asset Requests (v2)

Machine-readable list: `data/asset_manifest.json` (every web image → source video ID → source thumbnail → crop).

## What the site uses now
| Type | Count | Location | Source | Quality |
|---|---|---|---|---|
| Images (WebP, responsive) | 46 named assets, 96 files incl. sizes | `site/assets/media/` | KC Customs' own YouTube covers (Shorts 1080×1920, long videos 1280×720) and YouTube-generated frames (cropped to 405×720) | Covers: good. Frames: **soft** (405 px wide), used only at small sizes |
| Logo | 2 sizes | `site/assets/media/logo-*.webp` | YouTube channel avatar (800 px JPEG, `data/source/`) | Acceptable on screen; **not a master file** |
| Video | 0 files hosted | n/a | All playback is YouTube-nocookie embeds, loaded only when the visitor taps | Native YouTube quality |
| Fonts | 4 woff2 (~110 KB) | `site/assets/fonts/` | Google Fonts (Anton, Instrument Serif, Inter), SIL Open Font License | Self-hosted to avoid layout shift |

**Not hotlinked:** every image is a local copy. No image is loaded from YouTube's servers at page load.

**Permission:** these are KC Customs' own public images. Get written OK (WhatsApp is fine) from Chandu before launch. Two images show identifiable third parties: the helmet consultation (racer Alisha Abdullah) and students. Confirm that their appearance is fine.

## Video asset manifest
| Section | Video | Format | Thumbnail | Duration | Playback |
|---|---|---|---|---|---|
| Hero "Watch the studio" | zc8_EFEJ5ug | Short | i.ytimg.com/vi/zc8_EFEJ5ug/oardefault.jpg | 1:21 | Dialog, 9:16 |
| Statement | TZ5N0Spz064 | Short | …/oardefault.jpg | 1:28 | Dialog |
| Craft index | oWhoaVNHnH4, Ij2xuOjz4qI, -1SPsRunfLw, Glsa5eccRBI, EOkal7lTLC0, Ac0JbaZAokQ, SPijWcLsh2M, DW4hmWpu3SM | Shorts | …/oardefault.jpg | 0:20–1:40 | Dialog |
| Projects | vRxt4pK-0wA (12:58), oWhoaVNHnH4, ZNegxLjxVZA, kkQ9kdpLZDA, EQ3jW9j3Fb8, jvk2rxSIMs0, ht_Y0jp5r3g, s0RYTEwp5kk (1:30) | Mixed | maxres / oar | various | Dialog; hover cycles 3 local frames |
| Airbrush | tWAe6b1ONRU, Mo3HZt57J_U | Shorts | | 0:51, n/a | Dialog |
| Hydro | ojYErDs5dU0 | Short | | | Dialog |
| Builds | HcIpbg8CbIs (3:21), EdImonHW1JA, Glsa5eccRBI, Gg50_VpLoOk, hw1Uzh5Bh3E (8:48), X8-hUFeROlM (13:12) | Mixed | | | Dialog |
| Community | c2o0blpKsdw, 78TGCDZ-Pos, UNcfze8Nxag | Shorts | | | Dialog |
| Academy | 08qn45o5ux8 | Short | | 1:23 | Dialog |
| About | mzmCaIEJBUg | Video | | | Dialog (**content not reviewed**) |

There is **no muted autoplay background video**, because we have no original clip files. YouTube embeds can't be used as silent backgrounds without heavy scripts and branding. The hero uses three stills instead. Swap in a self-hosted MP4 when an original arrives (spec in `09`: ≤1.5 MB, 5–10 s, muted, `playsinline`, poster first).

## Assets to request from Chandu (priority order)
| # | Asset | Why | Replaces |
|---|---|---|---|
| 1 | **Original logo** (SVG or 2000 px PNG, transparent): both the gold-script and lime "customs" versions | Crisp logo, favicon, social image | `logo-*.webp` |
| 2 | **3–5 raw vertical clips** (5–15 s, no captions): reveal of a finished bike, spray gun on a tank, dipping | Real video hero and project hover previews | Hero stills, frame cycling |
| 3 | **High-res photos of finished bikes** (Red Rocket, Chrome Red RX King, Malaysian RXZ, Chetak, Polo, RX100, RX115) | Project rail and builds at full sharpness | Covers with burned-in logos |
| 4 | **Airbrush close-ups** (macro: candy flake, chrome, linework) | Airbrush story | 405 px frames |
| 5 | **Hydro dipping sequence** (film, activator, dip, rinse, clear) | Show the full process truthfully | 3 frames |
| 6 | **Workshop footage / stills** (prep, masking, booth) | Behind-the-craft mosaic | Frames with on-screen stickers |
| 7 | **Before/after pairs** of the same bike | Enables the before/after slider (not built: no matched pairs exist) | n/a |
| 8 | **Academy photos** (+ student consent) | Academy collage | Frames |
| 9 | **Founder portrait** (clean background) | About section | Video cover |
| 10 | **Customer photos + written testimonials** (with consent) | Testimonials section (not built: none exist) | n/a |

## Regenerating images
`scratchpad/scripts/build_assets.py` (kept in the session scratchpad) holds the crop list. It's simplest to rerun it with new source files, or to export new WebP files at 540/960 px (vertical) and 640/1280 px (16:9) under the same names.
