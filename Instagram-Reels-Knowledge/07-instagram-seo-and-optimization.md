# 07 — Instagram SEO & Optimization

> Evidence tags: ✅ Official · 🟡 Reported · 🔵 Practitioner · ⚠️ Theory
> Last researched: 2026-11-07

---

## 1. Video specs cheat sheet

| Spec | Recommended | Tag / notes |
|---|---|---|
| **Aspect ratio** | **9:16** vertical, **no borders** | ✅ Instagram recommends high-res 9:16 with no borders |
| **Resolution** | **1080×1920** (minimum 720×1280) | 🔵 Universal consensus. 4K uploads are downscaled |
| **Container / codec** | **MP4, H.264** video, **AAC** audio | 🔵 MOV and HEVC upload but get converted. MP4/H.264 is the safest |
| **Frame rate** | **30 fps** standard. 24/25 for cinematic, **60 fps** for fast action. Accepted range ~23–60 | 🔵 Export at the timeline's native rate. Don't convert |
| **Bitrate** | **~10–20 Mbps VBR** for 1080p (sources range 5–15 Mbps) | 🔵 Instagram re-encodes everything. Higher than this gains little |
| **Audio** | AAC, 48 kHz, 128–320 kbps, stereo | 🔵 |
| **Colour** | SDR Rec.709 (or deliberate HDR) | 🔵 See [04](04-professional-editing-techniques.md#hdr-vs-sdr) |
| **Max file size** | ~4 GB | 🟡 |
| **Length — recommendation-eligible** | **≤ 3 minutes** | ✅ ([Creators blog](https://creators.instagram.com/blog/instagram-recommendations-eligibility-tips-creators)) |
| **Length — maximum** | 3 min in-app is standard. Longer uploads (reports of 15–20 min) rolling out | 🟡 Over 3 min reaches followers only |
| **Cover image** | 1080×1920 source. **Grid displays a 3:4 (1080×1440) centre crop** | ✅ Grid switched to 3:4 in Jan 2025 |

### ✅ Phone setting that matters
**Settings → Data usage and media quality → "Upload at highest quality" = ON.** Without it, Instagram may compress uploads harder on mobile data.

### 🔵 Upload hygiene
- Upload the **original export file**. Never upload a screen recording or a file re-downloaded from another app.
- Avoid uploading over weak connections. Use wi-fi.
- **No watermarks** (CapCut, TikTok or other editor end-cards) ✅.
- When cross-posting from TikTok or YouTube Shorts, export **clean** versions without platform watermarks.

---

## 2. Safe zones

🔵 Instagram overlays UI on top of Reels. Keep key content inside the safe area:

```
┌──────────────── 1080 px ────────────────┐
│  TOP ~250 px: username, audio, camera   │  ← avoid text/faces
├─────────────────────────────────────────┤
│                                         │
│                                   ~120px│  ← right edge: like/
│        SAFE ZONE (≈1080×1420,           │     comment/share/
│        content centred, keep text       │     remix buttons
│        ~60 px from left edge and        │
│        ~150 px from right edge)         │
│                                         │
├─────────────────────────────────────────┤
│  BOTTOM ~350–420 px: caption, handle,   │  ← avoid captions here
│  audio label, CTA buttons               │
└─────────────────────────────────────────┘
          1920 px tall total
```

- Also consider the **3:4 grid crop** (top and bottom ~240 px cut off on the profile grid). Keep cover text centred.
- 🔵 Make a **safe-zone overlay PNG** (Phase 3) and place it on the top track while editing. Disable it before export.

---

## 3. Instagram search: how it works

- ✅ **"Search results are matched by text"** ([Creators blog](https://creators.instagram.com/blog/instagram-recommendations-eligibility-tips-creators)). Instagram matches query text against **usernames, profile names, bios, captions, hashtags and locations**, then ranks by relevance and popularity.
- ✅ Instagram's guidance: **put keywords and hashtags in the caption, not the comments.**
- 🔵 Instagram's content understanding also uses visual and audio signals (✅ "visual understanding of frames" and audio are listed as signals). **Saying the keyword aloud and showing it as text** is cheap insurance.
- ✅ **Google and Bing indexing (since 10 July 2025):** Public posts from **professional accounts (18+)** can appear in Google search results, Images and video carousels. It's on by default and can be turned off in privacy settings ([Metricool](https://metricool.com/instagram-indexing-on-google/), [Search Engine World](https://www.searchengineworld.com/its-live-instagram-posts-are-ranking-and-showing-in-google-and-bing-seo-meets-social)). Your **caption's first line works like a page title** for Google.

---

## 4. Profile SEO

| Field | Optimisation |
|---|---|
| **Username (@handle)** | Short, memorable, ideally niche-related. Changing it often breaks recognition |
| **Name field** (separate from the username; searchable) | **Name + primary keyword**, for example "Priya · Video Editing Tips" ✅ Instagram advises a name related to your content |
| **Bio** (150 chars) | Who it's for, plus the promise, plus the keywords ✅ "add keywords to your bio" |
| **Category** (professional account) | The most accurate category |
| **Links** | Up to 5 bio links. Put the most important first |
| **Highlights** | Named with keywords ("Editing Tips", "Presets") |

---

## 5. Captions, keywords & hashtags

### Caption structure (🔵, built on ✅ text-matching)

```
Line 1:  Keyword-rich hook / title  (visible before "…more"; acts as Google title)
         e.g. "How to colour grade Reels on your phone (3 free steps)"
Line 2–5: Value summary / context / mini-tutorial / story
Line 6:  One CTA (save / send / comment / follow)
Line 7:  3–5 hashtags
```

- **Caption length limit:** 2,200 characters ✅. 🔵 Long, useful captions add search text and reading time, but the first line carries the most weight.
- **Keywords:** Use the words your audience **actually types in search**: "reels editing tutorial", "capcut transition", "colour grading phone". Use Instagram's search autocomplete to find them.
- **Natural language.** No keyword stuffing.

### Hashtags (2026 rules)
- 🟡 **Hard limit: 5 hashtags per post/Reel** (announced by @creators, 18 Dec 2025; applies to new posts and edits) ([Business Today](https://www.businesstoday.in/technology/news/story/no-more-hashtag-stuffing-instagram-limits-hashtag-usage-to-just-5-per-reel-and-post-507444-2025-12-19)).
- ✅ / 🟡 Mosseri: hashtags help Instagram **understand and categorise** content and help **search**, but **don't meaningfully increase reach**.
- 🔵 **Hashtag mix (3–5 total):**
  - 1–2 **topic-specific** (#reelsediting, #colorgrading)
  - 1–2 **audience or community** (#contentcreatortips)
  - 0–1 **branded** or series (#YourNameEdits)
- ❌ Avoid irrelevant or huge generic tags (#viral, #fyp, #explore). They add no topical signal.

### Other text surfaces
- **On-screen text:** 🔵 Reinforces the topic for viewers and possibly for content understanding.
- **Spoken keywords:** 🔵 Say the topic in the first sentence.
- **Auto-captions:** Turn them on for accessibility.
- **Location tag:** ✅ Searchable. Valuable for local businesses, travel and food.
- **Collaborators and tags:** ✅ Collab posts show on both profiles. Product tags and affiliate tags 🟡 (up to 30 products per video since April 2026).

---

## 6. Covers & thumbnails

Covers matter for the **profile grid** (follow conversion), **Explore grids** and **search results**. They matter less in the Reels feed, which autoplays.

🔵 **Cover design rules:**
- Design at 1080×1920 but keep everything important inside the **centre 1080×1440 (3:4)** area ✅.
- **3–6 word title** in large type (100+ px), high contrast.
- **Consistent template** (font, placement, colour) across Reels, so the grid looks like a channel.
- **A face with clear emotion** or the **result** (the "after") performs well for covers.
- Pick a cover frame from the video or upload a custom cover. Instagram lets you upload a separate image.
- 🔵 You can also add the cover as the **first frame** (0.1–0.3 s) so it carries over to platforms without custom covers. ⚠️ This may hurt the hook if it isn't visually strong.

---

## 7. Posting timing & frequency

### Timing
- ✅ Instagram has **no official best time**.
- 🟡 Large third-party studies disagree:
  - Buffer (2026, ~9.6M posts): top slots Thursday 9 am, Wednesday 12 pm, Wednesday 6 pm (local time), with evenings strong overall
  - Sprout Social, Later and RivalIQ each give different windows ([SocialPilot summary](https://www.socialpilot.co/insights/best-time-to-post-reels-on-instagram))
- 🔵 **Use your own data:** **Insights → Audience → Most active times.** Post about 30–60 minutes before your audience's peak so early testing happens while they're online.
- 🔵 Reels keep getting distributed for days to weeks ("Views over time" in Insights ✅). Timing affects the **first test**, not the whole lifetime.

### Frequency
- ✅ No official requirement. 🔵 **3–5 Reels per week** is a common sustainable target (🟡 Buffer guidance). Quality and consistency beat volume.
- ✅ Use **scheduling** (native scheduler, Meta Business Suite, or scheduling Trial Reels 🟡) to keep consistency.

---

## 8. Pre-publish optimisation checklist

- [ ] 1080×1920, H.264 MP4, correct fps, no watermark
- [ ] ≤3 min (if you want non-follower reach)
- [ ] "Upload at highest quality" is ON
- [ ] Key text and faces in the safe zone
- [ ] Cover: custom, 3:4-safe, matches the grid template
- [ ] Caption line 1 = keyword-rich hook
- [ ] 3–5 relevant hashtags in the caption
- [ ] Location, collaborators and product tags added if relevant
- [ ] Auto-captions ON
- [ ] Music added in-app or properly licensed
- [ ] Trial Reel? (decide per [02](02-reels-growth-strategy.md#5-testing-system-trial-reels--iteration))
- [ ] Posting time ≈ 30–60 min before audience peak

**Related:** [01 Algorithm](01-instagram-algorithm.md) · [04 Pro Techniques](04-professional-editing-techniques.md) · [09 Analytics](09-instagram-analytics.md)
