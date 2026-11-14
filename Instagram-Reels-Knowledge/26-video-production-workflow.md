# 26 — Video Production Workflow (Operating Procedure)

> **Phase 3** · Created 2026-11-07
> **This is the procedure I follow for every clip you upload.** It implements your pipeline: **Analyse → Research audio → Compare → Recommend → ✋ Approve → Plan → ✋ Approve → Edit → Review → ✋ Approve → Prepare for publishing.**
> Evidence tags: ✅ Official · 🟡 Reported · 🔵 Practitioner · 🧪 Tested here

---

## ⚡ AUTONOMOUS MODE: the default since 2026-11-07

**Your instruction (2026-11-07):** you upload the original clip, I make every creative and technical decision, and you review only the finished Reel. **Gates 1–3 below are skipped.** I don't ask you to pick music, transitions, scene order or effects.

```
ANALYSE → RESEARCH → SELECT AUDIO → CREATIVE DIRECTION → EDIT → RENDER → QUALITY CHECK → DELIVER
```

| Stage | What I do (no waiting) | Tool |
|---|---|---|
| Analyse | Measure + review frames (whole clip at 0.5 s sampling + shot frames), write the footage report | `analyze_reel.py` |
| Research | Web research for candidate audio + the audio log + evergreen Tamil options, scored with [27](27-audio-matching-framework.md) | WebSearch / audio log |
| Select audio | **I pick the final audio myself** and record why | [27 §5](27-audio-matching-framework.md#5-the-five-category-winners--one-recommendation) |
| Creative direction | Write an EDL (edit decision list): hook, order, cuts, speed, zooms, transitions, SFX, text, grade, ending | `build/edl.json` + `build/text.ass` |
| Edit + render | One high-quality render from your originals | `tools/reel_render.py` 🧪 |
| Quality check | Measure the render + review its frames against the 10-point QC. **Fix and re-render before delivering** | `analyze_reel.py` |
| Deliver | Finished MP4 + audio name/source/reference + creative explanation + caption + hashtags + cover | `publish/` |

### Drop zone
Put clips in **`productions/inbox/`** (any filename), or upload them here. I create `productions/P###_…/`, **copy** the clip into `source/`, and never touch the original.

### Two honest limits that remain (and the best feasible alternative)
| Limit | Why | What I do instead |
|---|---|---|
| **Live Instagram audio data** (usage counts, ↗, top Reels) | Instagram audio pages require a login and block automated access ([22 §1](22-instagram-audio-discovery.md#1-what-i-can-and-cannot-see-access-reality)) | I select on fit, cultural recognisability and public evidence. Every delivery states clearly which popularity fields are **unverified**. Your audio-page screenshots, when you happen to send them, go into the [audio log](account-data/audio-log.md) and improve later picks |
| **Embedding Tamil film audio in the MP4** | I can't legally obtain the track file, and baking copyrighted audio into the export loses Instagram's licence and audio-page link ([15 §6](15-tamil-music-and-audio-strategy.md#6-licensing--legal-india-specific)) | **FINAL.mp4 is fully edited** (cuts, speed, grade, text, SFX, natural sound at −16 LUFS), timed to the chosen track's structure. **One step in the app:** add the named track at the stated start point (≈30 s). If you ever drop a reference recording of the audio (e.g. a screen recording of the audio page) into the inbox, I sync cuts to its measured beats frame-exactly. Optional, never required |

---

## 0. Ground rules

1. ~~No editing before approval.~~ **Superseded by Autonomous Mode** (above). The approval gates in §4–§7 apply only if you ask for a "plan first" production.
2. **Your footage only.** No AI-generated scenes or replacement footage unless you explicitly ask.
3. **Honesty about rendering.** I say exactly what I rendered and how. If an effect is impossible here, I use the best feasible alternative and say so.
4. **No invented audio data.** Usage counts and trend status come only from dated evidence ([22 §4](22-instagram-audio-discovery.md#4-evidence-standard-for-audio-claims)).
5. **Quality first.** Originals are never modified. One final encode from source.
6. ~~Production readiness gate~~ **Lifted by your 2026-11-07 instruction**: clips are produced on arrival. The account audit ([13](13-my-instagram-account-analysis.md)) keeps running in parallel and feeds back into decisions.

---

## 1. What I can render here (capability check, 2026-11-07)

| Capability | Status | Notes |
|---|---|---|
| Cut, trim, reorder, concatenate | ✅ 🧪 | Frame-accurate |
| Speed up / slow down / reverse | ✅ 🧪 | `setpts` / `atempo` |
| Slow-mo from 60/120 fps | ✅ 🧪 | Clean |
| Interpolated slow-mo from 30 fps | ✅ 🧪 | `minterpolate`. Slow render, check artefacts |
| Speed ramps | ⚠️ 🧪 | Stepped approximation of curves ([25 §3.3](25-cinematic-and-comedy-editing.md#33-tool-steps)): a sequence of short segments at changing speeds |
| **Full EDL render** (all of the below in one pass) | ✅ 🧪 | [tools/reel_render.py](tools/README.md#reel_renderpy--render-a-finished-reel-from-an-edl): segments, speed, fit (crop/blur), grades, zoom, punches, shakes, freeze, xfade, ASS text, SFX, optional music + ducking, two-pass loudness |
| **SFX kit** | ✅ 🧪 | 13 original synthesised sounds in `assets/sfx/` (whooshes, impacts, sub drop, punch, pop, click, ding, riser, scratch-stop, tape-stop, shutter). No licensing issues |
| **Display font for name cards** | ✅ 🧪 | Installed **Noto Sans Condensed Black** (heavy condensed). No download needed |
| Zoom punch / digital push-in | ✅ 🧪 | Frame-evaluated scale + crop |
| Transitions (fade, slide, wipe, zoom, flash) | ✅ 🧪 | `xfade` |
| Freeze frame + name card | ✅ | `tpad` clone + ASS text |
| Colour correction & grade (incl. `.cube` LUTs) | ✅ 🧪 | MovieMode / Reality presets ([25 §5.2](25-cinematic-and-comedy-editing.md#52-your-two-signature-looks-s5--starting-values)) |
| HDR (iPhone HLG/Dolby Vision) → SDR | ✅ (`zscale` + `tonemap` available) | Standard recipe. Verified on your first HDR clip before use |
| Stabilisation | ✅ | `vidstab` two-pass |
| Animated text & subtitles, **Tamil script** | ✅ 🧪 | ASS + Noto Sans Tamil. Display fonts (Anton / Bebas Neue / Montserrat, OFL) **downloaded only with your OK** |
| SFX placement & mixing, ducking, loudness | ✅ 🧪 | Needs SFX files: yours, royalty-free (licence kept), or simple ones synthesised with ffmpeg (original, basic quality) |
| Beat/tempo analysis of a reference audio | ✅ 🧪 | [tools/audio_beats.py](tools/README.md) |
| Measuring the final render | ✅ 🧪 | [tools/analyze_reel.py](tools/README.md) |
| **Adding Instagram library audio** | ❌ | You add it in-app with my exact timings ([28 §3](28-reels-export-and-publishing.md#3-adding-instagram-library-audio-in-app)) |
| AI masks / background removal / object tracking | ❌ | CapCut or Resolve instructions instead |
| Transcribing Tamil speech | ❌ | You give me the words, or we install a transcription tool (your call) |
| Identifying a song by listening | ❌ | Audio names come from you or the Instagram audio page |
| Watching video in real time | ❌ | I analyse measurements plus extracted frames and frame strips |

---

## 2. Stage 0 — Intake (you)

**Create a production** by uploading clips to `productions/P###_YYYY-MM-DD_slug/source/` (I'll create the folder if you just upload).
Tell me in one message (any of these you know):
- What happened / what you want it to be (or "you decide")
- Pillar guess (Bruh Moment / Pet Cast / Builds / Roads)
- Any audio you already have in mind
- Anything that must or mustn't appear

### Folder structure
```
productions/P001_2026-11-20_r15-wont-start/
├── source/        original clips — never modified
├── analysis/      measurements, frames, 01-footage-report.md
├── audio/         reference copies (timing only, never uploaded), 02-audio-options.md, screenshots
├── plan/          03-edit-plan.md
├── build/         generated render script, .ass text files, SFX used
├── renders/       v1_syncguide.mp4, v1_clean.mp4, v2_…
├── publish/       FINAL.mp4, cover.jpg, 04-publish-package.md
└── licenses/      proof for any music/SFX/fonts used
```
Templates: [productions/_templates/](productions/_templates/)

---

## 3. Stage 1 — Footage analysis

**Goal:** understand the footage before any creative decision. Output: `analysis/01-footage-report.md` ([template](productions/_templates/01-footage-report.md)).

### 3.1 Automatic measurements (per clip)
`tools/analyze_reel.py` → duration, resolution, fps (and whether it's variable), HDR flag, audio presence and loudness, detected shot changes, plus frames: opening frames, one frame per shot, transition strips.
Extra frame sampling: **every 0.5 s** contact sheet for short clips, so I can see the whole action.

### 3.2 What I identify (your Part 3 list)
| Item | How |
|---|---|
| What's happening · main subject & action | Frame review + your description |
| Mood & atmosphere | Light, colour, setting, pace, natural sound |
| **Interesting moments** (timestamps) | Peaks of action, expressions, pet reactions, fails, reveals |
| **Best opening frame** | Strongest single image (motion, face, clarity) within the clip. Often *not* frame 1 of the file |
| **Potential comedy moments** | Fails, awkward pauses, unexpected pet behaviour, reaction faces, contrast opportunities |
| **Best ending** | A clean landing, a loop point, or the reaction hold |
| **Natural transition opportunities** | Whip movements, lens covers, matching shapes, motion toward or away from the lens, cuts on action |
| Technical notes | Shake, exposure issues, focus, noise, HDR, VFR, usable slow-mo range |
| **Concept options** | 2–3 ways this footage could become a Reel (mapped to formats F1–F11 in [16](16-editing-identity-and-reel-formats.md#3-reel-format-library)) |
| Questions for you | Anything I can't tell from frames (what was said, context) |

**I stop here and share the report.** No audio or editing decisions are final yet.

---

## 4. Stage 2 — Audio research & matching

Per [22 §7](22-instagram-audio-discovery.md#7-per-clip-audio-research-when-you-upload-footage) and [27](27-audio-matching-framework.md):
1. Decide the **audio roles** the footage supports (hero, villain, comedy dialogue, nostalgia…)
2. Gather ≥5 candidates (audio log + evergreen classics + web research + English option)
3. Score them with the matching framework. Popularity is scored **only with evidence**
4. Send you a **verification list** of audio pages to screenshot (counts, ↗, top Reels)
5. Finalise the comparison, give the 5 category winners and **one recommendation**, plus a **sync map** (which video moment hits which audio moment)

Output: `audio/02-audio-options.md`.

### ✋ GATE 1 — you approve the audio (or pick another, or ask for more options)

---

## 5. Stage 3 — Edit plan

Output: `plan/03-edit-plan.md` ([template](productions/_templates/03-edit-plan.md)). Contents:
- **Concept & format** (one line + F-number), intent (Entertain/Feel/Teach), target length
- **Audio:** approved track, in-app start point, markers H/B/D/S/E with times ([24 §3](24-beat-sync-and-sound-design.md#3-marking-the-audio-before-cutting))
- **Timeline table:** every segment with **source clip + in/out timecodes**, output time range, speed, transition, zoom or move, SFX, text (exact words), grade, and sync point
- **Signatures used** (S1–S6, at least 3) and **effects deliberately not used** (to keep it clean)
- **Render path:** `ffmpeg (me)` / `CapCut steps (you)` / `Resolve steps (you)` / hybrid, with the reason
- **Deliverables list**

### ✋ GATE 2 — you approve the plan (or request changes)

---

## 6. Stage 4 — Production

### Path A: I render with ffmpeg (default when the plan allows)
1. Generate `build/render.sh` (the full, readable command) + `.ass` text files
2. **Single-pass render from the originals.** Quality settings in [28 §1](28-reels-export-and-publishing.md#1-export-settings-by-tool)
3. Deliver **two versions:**
   - `vN_syncguide.mp4`: includes the reference audio so you can judge timing (**for review only, never upload**)
   - `vN_clean.mp4`: natural sound + SFX only, at about −16 LUFS, ready for in-app music
4. If the music is licensed or royalty-free (not Instagram library), a single `vN_final.mp4` with music baked in at −14 LUFS

### Path B: you edit in CapCut or Resolve with my instructions
- A numbered **step list** with exact timecodes, speed values, keyframe values, transition names and durations, text, and the grade settings from [21 §4–5](21-professional-reels-editing.md#4-capcut-quick-reference-mobile-desktop-is-similar) and [25](25-cinematic-and-comedy-editing.md)
- You export → I measure and review the export (Stage 5)

### Path C: hybrid
I render everything ffmpeg does well. You add the specific effects that need CapCut or Resolve (an AI mask, a smooth bezier ramp) on top of my render, then export.

### Technical rules
| Rule | Why |
|---|---|
| Convert variable frame rate (phone) to constant at the timeline fps | Prevents audio drift and stutter |
| Respect rotation metadata | Phone clips are often stored rotated |
| HDR source → tone-map to SDR Rec.709 (unless delivering HDR on purpose) | Consistent look on all phones ([04](04-professional-editing-techniques.md#hdr-vs-sdr)) |
| One encode: CRF 16–18, preset slow, high profile, yuv420p, faststart | Survives Instagram's re-encode best |
| Never upscale low-res source beyond 1080×1920 | Upscaling adds no detail |

---

## 7. Stage 5 — Review

**Me:**
- Run `analyze_reel.py` on the render: specs, loudness, cuts, black frames, safe zone, cut-to-beat sync
- Frame review: hook frames, safe-zone overlays, transition strips
- Check against the plan (every timeline row) and the quality bar ([21 §7](21-professional-reels-editing.md#7-professional-quality-bar-what-done-means))
- A short **review note**: what matches the plan, what deviates, known compromises

**You:** watch `syncguide` on your **phone**, with sound and muted. Send revision notes ("move the freeze 3 frames later", "text too small").
→ Revisions produce `v2`, `v3`… Each version is kept. Nothing is overwritten.

### ✋ GATE 3 — you approve the final cut

---

## 8. Stage 6 — Publishing package

Per [28](28-reels-export-and-publishing.md): `publish/FINAL.mp4` + cover + caption (Tanglish/English) + 3–5 hashtags + keywords + **in-app audio instructions** (track, start point, volumes) + audio attribution + Trial Reel recommendation + final QC checklist. Output: `publish/04-publish-package.md`.

## 9. Stage 7 — After posting

At **72 h** and **day 7**, send Insights screenshots → I add a per-Reel audit ([13-reel-audits](13-reel-audits/_TEMPLATE.md)), compare the prediction with the result ([13 §C5](13-my-instagram-account-analysis.md#c5-calibration-log-my-predictions-vs-actual-performance)), and log what the audio delivered in [audio-log](account-data/audio-log.md).

---

## 10. Turnaround expectations

| Stage | Typical exchange |
|---|---|
| Footage analysis | 1 message from me after upload |
| Audio options | 1 message + your screenshots + 1 final comparison |
| Edit plan | 1 message (+ revisions) |
| Render | Minutes for simple edits. Interpolated slow-mo or stabilisation take longer (CPU only, no GPU on this machine) |
| Review loop | Usually 1–3 versions |

**Related:** [21](21-professional-reels-editing.md) · [27](27-audio-matching-framework.md) · [28](28-reels-export-and-publishing.md)
