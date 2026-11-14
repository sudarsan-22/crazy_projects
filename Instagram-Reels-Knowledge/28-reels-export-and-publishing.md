# 28 — Reels Export & Publishing

> **Phase 3** · Created 2026-11-07 · Builds on [07 — SEO & Optimization](07-instagram-seo-and-optimization.md) and [11 — Best Practices](11-best-practices-and-mistakes.md)
> Evidence tags: ✅ Official · 🟡 Reported · 🔵 Practitioner · 🧪 Tested here

---

## 1. Export settings by tool

### Master spec
| Setting | Value | Why |
|---|---|---|
| Resolution | **1080×1920** (9:16), no borders | ✅ Instagram's recommended vertical format ([07 §1](07-instagram-seo-and-optimization.md#1-video-specs-cheat-sheet)) |
| Codec / container | H.264 (High profile), MP4, yuv420p | 🔵 Most compatible. Minimal extra conversion |
| Frame rate | **Same as the timeline/source** (30, or 60 for action). Constant | 🔵 Never convert 30↔60 at export |
| Quality | x264 **CRF 16–18**, or ~15–20 Mbps VBR | 🔵 A clean master survives Instagram's re-encode |
| Audio | AAC, 48 kHz, 320 kb/s, stereo | 🔵 |
| Loudness | **≈ −16 LUFS** if you'll add Instagram library music in-app · **−14 LUFS** if music is baked in. True peak ≤ −1 dBTP | [24 §6](24-beat-sync-and-sound-design.md#6-mixing-levels) |
| Colour | SDR Rec.709 | [25 §5](25-cinematic-and-comedy-editing.md#5-colour-correction--cinematic-grading) |
| Length | ≤ 3:00 for recommendations | ✅ |

### ffmpeg (my renders) 🧪
```bash
ffmpeg -i <graph output> \
  -c:v libx264 -preset slow -crf 17 -profile:v high -pix_fmt yuv420p -r 30 \
  -movflags +faststart \
  -c:a aac -b:a 320k -ar 48000 \
  FINAL.mp4
```
(`-r` = the timeline fps. The full filter graph lives in the production's `build/render.sh`.)

HDR phone footage → SDR. 🧪 The chain runs correctly on a synthetic 10-bit HLG clip (output 8-bit Rec.709). **Visual accuracy will be checked on your first real HDR clip:**
```bash
-vf "zscale=t=linear:npl=100,format=gbrpf32le,zscale=p=bt709,tonemap=tonemap=hable:desat=0,zscale=t=bt709:m=bt709:r=tv,format=yuv420p"
```

### CapCut
Export → Resolution **1080p** · Frame rate **= source** (30 or 60) · Code rate **Higher** (or Recommended) · **Smart HDR off** · Format MP4.
Before exporting: make sure the **default ending (watermark) is off** ([21 §4](21-professional-reels-editing.md#4-capcut-quick-reference-mobile-desktop-is-similar)). Mute CapCut library music if you'll add Instagram audio.

### DaVinci Resolve (Deliver page)
Custom → Format **MP4** · Codec **H.264** (H.264 Main/High) · Resolution **1080×1920** · Frame rate **= timeline** · Quality **Restrict to 20,000 kb/s** · Encoding profile High · Audio **AAC 320 kb/s, 48 kHz** · Data levels Auto · Colour space tag Rec.709.

### Edits
Export at **1080p** (or 4K if the source is 4K; Instagram downscales), source frame rate. Edits can post straight to Instagram 🟡.

---

## 2. Verify, then transfer

1. **Measure** the export: `python3 -I tools/analyze_reel.py FINAL.mp4 publish/check` → all spec checks pass ([tools](tools/README.md))
2. **Phone check:** watch the full Reel on your phone (sound on, then muted)
3. **Transfer without compression:**
   - ✅ USB cable · Google Drive / OneDrive / Dropbox (download the original file) · Nearby/Quick Share · AirDrop (iPhone) · Telegram **as a file** (not as a video)
   - ❌ WhatsApp or Telegram as a *video* (recompressed) · screen recordings
4. Instagram: **Settings → Data usage and media quality → Upload at highest quality: ON** ✅ ([07 §1](07-instagram-seo-and-optimization.md#1-video-specs-cheat-sheet))

---

## 3. Adding Instagram library audio in-app

> This is how your Tamil film audio stays **licensed** and **linked to its audio page** ✅ ([15 §5](15-tamil-music-and-audio-strategy.md#licensed-audio-workflow-important)). UI details change often 🟡, so the steps are generic.

### Single track (Instagram app)
1. **+ → Reel** → select `FINAL.mp4` (the clean version) → Next
2. Tap **Audio / music** → search the approved audio by its **exact name** (from the publish package)
3. **Select the segment:** drag the track so the **stated start point** (e.g. 0:42.1) aligns with the start of your video
4. **Volume:** open audio controls → set **original audio** and **music** levels per the package (starting points in [24 §6.1](24-beat-sync-and-sound-design.md#61-when-library-music-is-added-in-app-the-default-workflow))
5. **Check the sync:** play back. The drop (D) must hit the hero frame. Nudge the segment until it does. Use the 2-frame sync flash if I included one (then post the version without it)

### Two tracks (BGM switch, multitrack)
6. After track A: **"Add to the mix"** → select track B → place it to start at the stated video time (after the silence gap) → trim A to end at the switch time 🟡 ([TechCrunch](https://techcrunch.com/2024/07/16/instagram-now-allows-users-to-add-multiple-audio-tracks-to-reels))
7. Re-check the switch timing on playback

### Edits app (alternative)
Import `FINAL.mp4` → add audio from the Instagram music library → align on the timeline (beat markers help) → adjust volumes → export or post to Instagram 🟡.

### Original audio
If the Reel uses **your own voice or sounds** as the main audio, it becomes "Original audio". Instagram lets creators rename their original audio 🟡. Name it after your series ("Bruh Moment #7 — stupid_bruhmoment") so it's searchable if others reuse it.

---

## 4. Cover

| Rule | Detail |
|---|---|
| Source size | 1080×1920. **Key content inside the centre 1080×1440 (3:4)**, because the grid crops to 3:4 ✅ |
| Content | The strongest frame: character freeze, the reveal moment, or a reaction face |
| Title | 3–5 words, display font, high contrast, the series tag (S4) |
| Consistency | The same template on every Reel ([16 §1](16-editing-identity-and-reel-formats.md#brand-kit-spec-build-in-phase-3)) |
| Production | I render the cover as `publish/cover.jpg` from a chosen frame + title text (ffmpeg), with a 3:4 safe-area check |
| Upload | In the Reel's **Edit cover** → **Add from camera roll** |

---

## 5. Caption, keywords & hashtags

### 5.1 Caption formula (your voice: Tanglish + English)
```
Line 1  Hook + keyword (searchable; works as the Google title)
        e.g. "R15 start aagala… mass entry wasted 😭 | Tamil comedy reel"
Line 2  One line of context or the joke's extension (don't explain the joke)
Line 3  CTA that fits: "Send this to your bike-crazy friend 🏍️" / "Part 2 venuma?"
Line 4  🎵 Audio credit (when useful): "BGM: <film> — <composer>"
Line 5  3–5 hashtags
```
- ✅ Keywords in the caption, not the comments ([07 §5](07-instagram-seo-and-optimization.md#5-captions-keywords--hashtags))
- ✅ Up to 2,200 characters, but the first line carries the most weight
- No engagement bait without a real reason ([11 §3](11-best-practices-and-mistakes.md#3-banned--harmful-growth-tactics--never-use))

### 5.2 Searchable keywords (choose per Reel)
| Pillar | Keyword candidates (English / Tanglish) |
|---|---|
| All | tamil comedy reel, tamil funny video, tamil bgm, bruh moment |
| P1 Bruh Moments | tamil relatable, tamil pov, funny moments tamil |
| P2 Pet Cast | funny rabbit, pet rabbit tamil, bunny comedy, pet birds, lovebirds / budgies (only your actual species) |
| P3 Builds | diy tamil, room setup, gadget review tamil, desk setup |
| P4 Roads | yamaha r15, r15 v4 (your version), hyundai verna, tamil ride, road trip tamil nadu |

### 5.3 Hashtags (🟡 max 5)
**Rule:** 1–2 topic + 1–2 audience or community + 0–1 series or brand ([07 §5](07-instagram-seo-and-optimization.md#5-captions-keywords--hashtags)). The candidates below are **descriptive, not claims about popularity**. Check what the tag pages actually show before relying on them.
| Pillar | Candidate set |
|---|---|
| P1 | #tamilcomedy #tamilreels #bruhmoment |
| P2 | #petrabbit #rabbitsofinstagram #tamilcomedy #petcast |
| P3 | #diyprojects #roomsetup #tamilreels |
| P4 | #yamahar15 #r15 #hyundaiverna #tamilreels |
| Series tag | #bruhmoment (if you adopt it consistently) |

### 5.4 Audio attribution
| Audio type | Attribution |
|---|---|
| Instagram library track | Automatic (shown on the Reel and linked). An optional caption credit is a courtesy |
| Multitrack mix | Shown as your mix 🟡. Credit both sources in the caption if helpful |
| Royalty-free music baked in | **Follow the licence.** Some (e.g. free tiers) *require* a credit line in the caption |
| Your original audio | Rename it (§3) |

---

## 6. Publish settings checklist

- [ ] Clean `FINAL.mp4` uploaded (not the sync-guide version)
- [ ] Library audio added: correct name, start point, volumes, sync checked
- [ ] Cover uploaded (3:4-safe)
- [ ] Caption: keyword line 1, one CTA, audio credit if useful, 3–5 hashtags
- [ ] **Auto-captions** ON (accessibility)
- [ ] Location (if relevant) · collaborators tagged (if any)
- [ ] **Trial Reel?** Decide per the testing plan ([02 §5](02-reels-growth-strategy.md#5-testing-system-trial-reels--iteration))
- [ ] AI label only if realistic AI-generated media is included ✅ (normally no)
- [ ] Paid partnership label if sponsored ✅. **Sponsored means no library film songs** ([15 §6](15-tamil-music-and-audio-strategy.md#6-licensing--legal-india-specific))
- [ ] Post or schedule 30–60 min before your audience's peak (Insights)

---

## 7. Final quality checklist (render + publish)

**Technical (measured):** 1080×1920 · constant fps = source · H.264 MP4 · ≤3:00 · loudness target met · TP ≤ −1 dBTP · no black or fade start · no watermark
**Editorial:** hook lands < 3 s · payoff on its planned frame · ≥3 signatures (S1–S6) · no unnecessary effects ([25 §7](25-cinematic-and-comedy-editing.md#7-over-editing-warning-signs-remove-if-you-see-these)) · text proofread (Tamil + English) · safe zones clear
**Audio:** licensed path confirmed · in-app sync checked on the phone · voice intelligible on the phone speaker
**Identity:** funny beat present · feels like you, not a generic influencer edit ([16 §8](16-editing-identity-and-reel-formats.md#8-identity-consistency-check-before-publishing))
**Safety:** pets unstressed · no handheld riding/driving footage · culturally safe audio ([23 §7](23-tamil-bgm-editing-guide.md#7-cultural--safety-notes-for-tamil-audio-content-))

---

## 8. After posting

| When | Action |
|---|---|
| First hour | Reply to comments. Pin a good one. Share to Story |
| 72 h | Insights screenshots → per-Reel audit ([26 §9](26-video-production-workflow.md#9-stage-7--after-posting)) |
| Day 7 | Final numbers → [13](13-my-instagram-account-analysis.md) + [audio-log](account-data/audio-log.md) |

Template: [productions/_templates/04-publish-package.md](productions/_templates/04-publish-package.md)

**Related:** [07](07-instagram-seo-and-optimization.md) · [26](26-video-production-workflow.md) · [11](11-best-practices-and-mistakes.md)
