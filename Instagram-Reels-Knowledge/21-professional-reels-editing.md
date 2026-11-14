# 21 — Professional Reels Editing (Phase 3 Master Reference)

> **Phase 3 · Production system** · Created 2026-11-07
> Evidence tags: ✅ Official · 🟡 Reported · 🔵 Practitioner · ⚠️ Theory · 🧪 **Tested here** (rendered on this machine on 2026-11-07)
> Foundations live in [03](03-video-editing-fundamentals.md), [04](04-professional-editing-techniques.md), [05](05-hooks-and-storytelling.md) and [06](06-audio-and-sound-design.md). This document is the **production-level** layer: which technique to use when, and exactly how to do it in **CapCut, DaVinci Resolve, Edits, and ffmpeg (my local renderer)**.

### Phase 3 document map
| Doc | Covers |
|---|---|
| **21** (this) | Editing principles, technique catalogue, tool capabilities, tool how-tos |
| [22](22-instagram-audio-discovery.md) | Finding and verifying Instagram audio (trending, Tamil, English) |
| [23](23-tamil-bgm-editing-guide.md) | Editing *to* Tamil BGM, songs and dialogue |
| [24](24-beat-sync-and-sound-design.md) | Beat maths, sync technique, SFX layering, mixing |
| [25](25-cinematic-and-comedy-editing.md) | Comedy timing, cinematic transitions, speed ramps, slow-mo, grading |
| [26](26-video-production-workflow.md) | The **operating procedure** for every clip you send me (analysis → approval → render) |
| [27](27-audio-matching-framework.md) | Scoring and recommending audio for a specific clip |
| [28](28-reels-export-and-publishing.md) | Export settings, in-app audio, cover, caption, final QC |

---

## 1. Five principles of professional Reels editing

1. **Every edit serves one of four jobs:** hook, clarity, rhythm or payoff. An effect that does none of these is removed. (You asked for no unnecessary effects. This principle enforces that.)
2. **Audio leads, picture follows.** In music-led Reels, the audio structure (beats, drop, dialogue) is the skeleton, and cuts hang on it ([24](24-beat-sync-and-sound-design.md)).
3. **Contrast creates impact.** Slow vs fast, loud vs silent, cinematic vs raw. Your "Bruh Cinema" identity is built on this ([16 §1](16-editing-identity-and-reel-formats.md#1-the-editing-identity-bruh-cinema)).
4. **The footage decides the edit.** Analyse first: what's actually funny or beautiful in the clip ([26 §3](26-video-production-workflow.md#3-stage-1--footage-analysis)). Don't force a template onto footage that doesn't support it.
5. **Preserve quality.** Work from original files, render once at the end, and match the source frame rate ([28](28-reels-export-and-publishing.md)).

---

## 2. Technique catalogue: when to use, when NOT to

| Technique | Use when | Don't use when | Deep dive |
|---|---|---|---|
| **Hard cut on beat** | Music-led montage, energy | Dialogue mid-sentence | [24](24-beat-sync-and-sound-design.md) |
| **Jump cut / punch-in** | Talking, reactions, removing dead time | Cinematic slow scenes | [03 §3](03-video-editing-fundamentals.md#3-the-grammar-of-cutting) |
| **J/L cut** | Dialogue leads into the next scene | Beat-synced montage | [03 §3](03-video-editing-fundamentals.md#3-the-grammar-of-cutting) |
| **Match cut** | Similar shape or motion exists in two clips | Forced, with no real match in the footage | [25 §2](25-cinematic-and-comedy-editing.md#2-cinematic-transitions-recipes) |
| **Whip / swipe transition** | A camera whip was **filmed** | Static footage (fake whips look cheap) | [25 §2](25-cinematic-and-comedy-editing.md#2-cinematic-transitions-recipes) |
| **Speed ramp** | One hero action (jump, kick-start, reveal) | Every clip. Ramps lose impact when overused | [25 §3](25-cinematic-and-comedy-editing.md#3-speed-ramping-recipes) |
| **Slow motion** | Emotional or hero beat, 60/120 fps source | 30 fps source without interpolation (stutter) | [25 §4](25-cinematic-and-comedy-editing.md#4-slow-motion--time-remapping) |
| **Freeze frame + name card** | Character intro ("Bruh Cinema" S1) | More than 1–2 per Reel | [23 §3](23-tamil-bgm-editing-guide.md#3-recipe-cards-by-audio-role) |
| **Zoom punch** | Emphasis word, realisation, punchline | Constant zooming (motion sickness) | [25 §1](25-cinematic-and-comedy-editing.md#1-comedy-timing-toolkit) |
| **BGM switch / record scratch** | The expectation-vs-reality moment | No clear "expectation" set up first | [23 §4](23-tamil-bgm-editing-guide.md#4-the-bgm-switch-step-by-step) |
| **Screen shake** | Impact, shock, bass hit | Calm or emotional scenes | [25 §1](25-cinematic-and-comedy-editing.md#1-comedy-timing-toolkit) |
| **Colour grade shift** | MovieMode → Reality switch | Random filter changes between shots | [25 §5](25-cinematic-and-comedy-editing.md#5-colour-correction--cinematic-grading) |
| **Animated captions** | Speech, dialogue translation, punch words | Captions repeating what's already obvious on screen | [21 §6](#6-text--subtitle-production-standard) |
| **SFX** | Transitions, text pops, impacts, comedy beats | Under every cut ("SFX soup") | [24 §5](24-beat-sync-and-sound-design.md#5-sound-design-layering) |

---

## 3. Tool capability matrix (Nov 2026)

| Capability | **CapCut** (mobile/desktop) | **Edits** (Instagram) | **DaVinci Resolve** (free / Studio) | **ffmpeg here** (my renderer) |
|---|---|---|---|---|
| Vertical 9:16 project | ✅ | ✅ | ✅ Resolve 20+ auto-rearranges UI for vertical timelines 🟡 ([ProVideo Coalition](https://www.provideocoalition.com/davinci-resolve-20-released/)) | ✅ 🧪 |
| **Instagram library audio** (licensed, linked to the audio page) | ❌ Own library. Not licensed for Instagram distribution in general 🔵 | ✅ 🟡 | ❌ | ❌ **I add none.** You add it in-app ([28 §3](28-reels-export-and-publishing.md#3-adding-instagram-library-audio-in-app)) |
| Beat markers | ✅ Beats → Auto generate | ✅ beat markers 🟡 | ✅ **AI Detect Music Beats** (Resolve 20+) 🟡 · manual markers (M) | ✅ energy-onset detection (approximate) 🧪 |
| Speed curves / ramps | ✅ Speed → Curve (presets + custom) | ✅ basic | ✅ Retime curve (bezier) | ⚠️ stepped segments only (no true bezier) 🧪 |
| Smooth slow-mo (interpolation) | ✅ "Smooth slow-mo" / optical flow (may need Pro) | Limited | ✅ Optical Flow (free) · **Speed Warp** (Studio) | ✅ `minterpolate` motion-compensated (slow to render) 🧪 |
| Keyframes / zoom | ✅ | ✅ basic | ✅ | ✅ zoom via frame-evaluated scale + crop 🧪 |
| Transitions | ✅ many presets | ✅ | ✅ + Fusion | ✅ `xfade` (fade, slide, wipe, zoom, etc.) 🧪 |
| Masks / AI subject cutout | ✅ Remove BG, masks | ✅ cutouts | ✅ Magic Mask (Studio) · Power Windows (free) | ❌ no AI segmentation installed |
| Motion tracking | ✅ basic | ❌ | ✅ | ❌ (not practical) |
| Colour grading | ✅ Adjust, HSL, curves, LUT | ✅ filters | ✅✅ industry best | ✅ `eq`, `curves`, `colorbalance`, `lut3d` (.cube LUTs), vignette, grain 🧪 |
| Stabilisation | ✅ | ❌ | ✅ | ✅ `vidstab` (two-pass) |
| Auto captions | ✅ (Tamil support varies, so check) | ✅ (🟡 bilingual in 15 languages) | ✅ AI Animated Subtitles (Resolve 20) 🟡 ([NewsShooter](https://www.newsshooter.com/2025/05/27/davinci-resolve-20-final-release/)) | ❌ no transcription installed. ✅ **animated styled text** via ASS subtitles, **including Tamil script** (Noto Sans Tamil) 🧪 |
| Audio ducking / loudness | ✅ basic | ✅ basic | ✅ Fairlight (pro) | ✅ `sidechaincompress` + `loudnorm` to −14 LUFS 🧪 |
| Export control | Good (resolution, fps, bitrate presets) | Good (up to 4K) | Full | Full (x264 CRF, profile, fps) 🧪 |
| Watermark risk | ⚠️ Disable the default ending | None | None | None |

**How we'll split the work** (details in [26](26-video-production-workflow.md)):
- **I render** whatever ffmpeg does well: cuts, speed, simple ramps, zooms, transitions, grade, styled text, SFX mix, export. Everything is from your original footage.
- **You finish in-app:** add the **Instagram library audio** (licensing plus audio-page linking) in Edits or Instagram, using my sync instructions.
- **For effects beyond ffmpeg** (AI masks, tracking, bezier ramps), I give you a **frame-exact CapCut or Resolve timeline** instead. I won't pretend to render what I can't.

---

## 4. CapCut quick reference (mobile; desktop is similar)

| Task | Steps |
|---|---|
| Project ratio | Ratio → **9:16** |
| Remove the end watermark | Settings (gear) → **turn off "Add default ending"**, or delete the ending clip |
| Speed ramp | Select clip → Speed → **Curve** → presets (Montage, Hero, Bullet, Jump Cut, Flash In/Out) or **Custom** (drag beat points) |
| Smooth slow-mo | Speed → Normal (e.g. 0.3×) → enable **Smooth slow-mo** (rendering takes longer; feature tier may vary) |
| Beat markers | Select the audio → **Beats** → Auto generate. Then cut on the markers |
| Zoom punch | Select clip → keyframe at frame A (scale 100%) → keyframe 4–6 frames later (scale 115%) → (optional) back to 100% |
| Freeze frame | Select clip at the playhead → **Freeze** → adds a 3 s still (trim it to 0.8–1.5 s) |
| Text animation | Text → Add → Animation → In (Pop, Bounce, Typewriter) · Out · Loop. Keep In ≤ 0.3 s |
| Auto captions | Text → Auto captions → choose the language → style → **proofread every line** |
| Colour | Adjust → Brightness / Contrast / Saturation / HSL / Curves · Filters at ≤ 50% intensity |
| SFX | Audio → Sound effects (or import your own kit) |
| Export | 1080p · frame rate = source (30 or 60) · bitrate "Higher" · **Smart HDR off** (export SDR) ([28 §1](28-reels-export-and-publishing.md#1-export-settings-by-tool)) |
| ⚠️ Audio | Use CapCut music only as a **timing guide**. Export with the music muted, then add the Instagram library audio in-app |

---

## 5. DaVinci Resolve quick reference (free unless noted)

| Task | Steps |
|---|---|
| Vertical project | File → Project Settings → Master Settings → timeline resolution **1080×1920** (custom), frame rate = source. Or create a vertical timeline in Resolve 20+ |
| Beat markers | Resolve 20+: **AI Detect Music Beats** places markers on beats; clips snap to them 🟡 (check the edition) · Manual: play audio, press **M** on each beat |
| Speed ramp | Right-click clip → **Retime Controls** (Ctrl/Cmd+R) → add speed points → right-click → **Retime Curve** → bezier the frame curve |
| Smooth slow-mo | Inspector → Retime & Scaling → Retime Process: **Optical Flow** (free) · Motion Estimation: **Speed Warp** (Studio) |
| Zoom punch | Inspector → Transform → Zoom keyframes, or the **Dynamic Zoom** checkbox (ease in/out) |
| Freeze frame | Right-click → **Freeze Frame**. Add a Text+ name card on top |
| Text | Effects → Titles → **Text+** (animate with keyframes) · Resolve 20 **AI Animated Subtitles** for speech 🟡 |
| Colour | Color page: node 1 = correction (lift/gamma/gain, WB) → node 2 = grade (look) → node 3 = LUT / film grain. Use scopes (waveform, vectorscope) |
| Audio | Fairlight: EQ, compressor, **Dialogue Leveler**, **Voice Isolation** (Studio) · Ducking via sidechain or keyframes |
| Export | Deliver page → H.264 MP4, 1080×1920, source fps, quality restricted to ~20 Mb/s, audio AAC 320 kb/s ([28 §1](28-reels-export-and-publishing.md#1-export-settings-by-tool)) |
| 🟡 MCP (Resolve 21.1) | Reports say AI tools can control Resolve through MCP ([Motion Media](https://www.motionmedia.com/mm-blog/davinci-resolve-21-1-update-new-features)). **Resolve isn't installed on this machine.** If you install it, we can explore this later |

---

## 6. Text & subtitle production standard

| Element | Standard (from [16 §1](16-editing-identity-and-reel-formats.md#brand-kit-spec-build-in-phase-3)) | ffmpeg implementation 🧪 |
|---|---|---|
| Captions (speech/dialogue) | Bold sans, white + black outline 5 px, lower-middle (above the bottom UI), ≤2 lines, 3–6 words/line | ASS style: `Fontsize 70–80`, `Outline 5`, `Alignment 2`, `MarginV ≈ 520–600` |
| Tamil script text | **Noto Sans Tamil** (installed). Tested rendering correctly 🧪 | `Fontname=Noto Sans Tamil` |
| Name cards / titles | Heavy condensed display font, yellow `#FFC400`, slide-in 6 frames + hit SFX | ASS `\move` + `\t` transforms. Display fonts (Anton / Bebas Neue, OFL licence) **need downloading with your OK** |
| Pop-in animation | Scale 60→110→100% over ~7 frames | `{\fscx60\fscy60\t(0,120,\fscx110\fscy110)\t(120,200,\fscx100\fscy100)}` 🧪 |
| Translation subtitles | For Tamil dialogue: English (or Tanglish) translation, smaller, below the main text | Second ASS style |
| Safe zone | Nothing in the top 250 px, the bottom ~380 px or the right 140 px | Verified with the overlay from [tools/](tools/README.md) |

---

## 7. Professional quality bar (what "done" means)

- [ ] Opening frame chosen deliberately (not just the clip's first frame)
- [ ] Every cut motivated (beat, action, dialogue, reaction)
- [ ] Hero moment lands exactly on the planned audio point (±1 frame)
- [ ] No effect without a job (§1.1)
- [ ] Consistent grade. Skin and natural colours believable
- [ ] Text readable on a phone, in the safe zone, proofread (Tamil and English)
- [ ] Natural sound and SFX balanced. Leave room for the in-app music
- [ ] Exported per [28](28-reels-export-and-publishing.md), measured with [tools/analyze_reel.py](tools/README.md)
- [ ] Original footage only. No AI-generated scenes unless you ask

**Related:** [26 Production workflow](26-video-production-workflow.md) · [16 Editing identity](16-editing-identity-and-reel-formats.md)
