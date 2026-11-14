# 03 — Video Editing Fundamentals for Reels

> Evidence tags: ✅ Official · 🟡 Reported · 🔵 Practitioner · ⚠️ Theory
> Last researched: 2026-11-07 · Next: [04 — Professional Techniques](04-professional-editing-techniques.md)

---

## 1. Think vertical from the start

| Principle | Detail |
|---|---|
| **Shoot 9:16 natively when possible** | ✅ Instagram recommends high-resolution 9:16 vertical with **no borders**. Letterboxed horizontal video is a recommendation negative |
| **If shooting horizontal (4K), plan the crop** | 🔵 A 4K (3840×2160) frame cropped to 9:16 gives ~1215×2160, which is still above 1080×1920. You can reframe and punch in during the edit |
| **Centre-weighted framing** | 🔵 UI overlays cover the top ~250 px and bottom ~350–420 px, plus the right edge (like/comment/share buttons). Keep faces and text in the centre safe zone (see [07](07-instagram-seo-and-optimization.md#2-safe-zones)) |
| **Eyes in the upper third** | 🔵 For talking heads, eye line at roughly 1/3 from the top. Leave headroom below the top UI |
| **Fill the frame** | 🔵 Phones are small. Use mid close-ups (chest up) for talking and close-ups for detail. Wide shots only as context beats |

---

## 2. Project / timeline settings

🔵 Set these **before** importing:

| Setting | Value | Why |
|---|---|---|
| Resolution | **1080×1920** (or 2160×3840 for a 4K master) | Matches delivery. Many editors cut at 4K and export 1080 for sharper downscaling |
| Frame rate | **Match your main footage**: 30 fps (most phone footage) or 24/25 fps (cinematic) | Mixed frame rates cause stutter. Pick one timeline rate |
| Colour space | **Rec.709 / SDR** for most work | Predictable look across phones. HDR is in [04](04-professional-editing-techniques.md#5-colour-correction-and-grading) |
| Audio | 48 kHz | Video standard |

**Frame-rate rules of thumb (🔵):**
- **24 fps:** cinematic motion blur. Good for moody storytelling and travel.
- **30 fps:** the default for talking heads, tutorials and phone-native content.
- **60 fps** footage on a 30 fps timeline gives **50% slow motion**. **120 fps** gives **25%** (see [04 — Speed](04-professional-editing-techniques.md#3-speed-ramping--slow-motion)).
- **Shutter:** about 2× the frame rate (the 180° rule), so 1/50 at 24/25 fps and 1/60 at 30 fps. Use ND filters outdoors on cameras. On phones, apps like Blackmagic Camera give manual control.

---

## 3. The grammar of cutting

### Cut types every Reel uses

| Cut | What it is | Use for |
|---|---|---|
| **Hard cut** | Instant change | The default. Keeps pace |
| **Jump cut** | Cut within the same shot to remove pauses | Talking heads. Remove every breath, "um" and pause 🔵 |
| **Punch-in / zoom cut** | Alternate between 100% and ~110–120% scale on the same shot | Hides jump cuts and adds emphasis. Very common in talking-head Reels |
| **J-cut** | The next clip's **audio** starts before its video | Smooth transitions, leading into a new scene |
| **L-cut** | The current audio continues over the next clip's video | B-roll over speech. Reaction shots |
| **Cut on action** | Cut mid-movement (a hand reaching, a turn) | Invisible continuity between angles |
| **Match cut** | Similar shape, motion or colour across two shots | "Wow" moments (details in [04](04-professional-editing-techniques.md#1-transitions)) |
| **Cutaway / B-roll insert** | Cut to illustrate what's being said | Visual proof. Hides edits |
| **Smash cut** | An abrupt cut to a contrasting scene or sound | Comedy, pattern interrupts |

### Cutting principles (🔵)

1. **Cut out everything that doesn't earn its place.** If removing a shot loses nothing, remove it.
2. **Enter late, leave early.** Start each clip after the setup and end it before the wind-down.
3. **Cut on the beat or on the word.** Edits feel deliberate when aligned to music beats or speech rhythm.
4. **Vary shot size.** Wide → medium → close keeps the eye working.
5. **Motivate every cut.** A new piece of information, a reaction, or movement.

---

## 4. A-roll, B-roll and layering

- **A-roll:** the main footage that carries the story (you talking, the main action).
- **B-roll:** supporting footage that shows what you say (product shots, screen recordings, process, environment).
- 🔵 **Rule:** **Never say what you could show.** Every claim gets a visual.
- 🔵 **Layer stack (top to bottom on the timeline):**

```
V6  Captions / subtitles
V5  Graphics, arrows, emojis, highlight boxes
V4  On-screen title text (hook, chapter labels)
V3  Overlays (screen recording, picture-in-picture, green-screen)
V2  B-roll
V1  A-roll (primary)
A1  Dialogue / voiceover
A2  Music
A3  SFX
A4  Ambience / room tone
```

---

## 5. Pacing for retention

🔵 Short-form pacing is faster than YouTube or film, but **rhythm beats raw speed**.

| Content type | Typical shot length | Notes |
|---|---|---|
| Talking-head tips | 1.5–3 s per visual change (cut, punch-in, B-roll or graphic) | Remove all pauses |
| Tutorials | One step per 2–4 s | Show the result of each step |
| Cinematic / travel | 0.5–2 s, cut to music | Beat-synced |
| Storytime | Varies. Slow down for the emotional beat | Contrast creates impact |
| Satisfying / process | Longer holds are OK if the motion is continuous | Speed-ramp the boring parts |

**Pattern interrupts** (🔵): about every 2–5 seconds, change *something*: angle, zoom, B-roll, text pop, SFX, colour, location, or graphic. The retention graph in Insights ✅ shows where people leave. Add an interrupt just before typical drop points.

**The "dead air" audit:** Watch your edit muted at 1.5× speed. Anywhere you get bored, cut. Then watch with sound at 1×. Anywhere the audio drags, tighten it.

---

## 6. Structure of a short edit

🔵 A reusable skeleton. Details in [05 — Hooks & Storytelling](05-hooks-and-storytelling.md).

```
0.0–3.0 s   HOOK        Visual + text + spoken hook. Strongest frame first.
3–8 s       CONTEXT     Why this matters / what they'll get. Open a loop.
8–(end-5) s BODY        Steps/story beats. Each beat = new visual. Escalate.
last 3–5 s  PAYOFF      Deliver the promise. Best reveal last.
final 1 s   LOOP / CTA  Ending that flows back to start, or one clear ask.
```

---

## 7. Basic audio in the edit

🔵 Bad audio gets more scrolls than bad video.

- Dialogue should be clearly intelligible over music. **Duck the music** 12–20 dB under speech.
- Remove background noise (most editors have AI noise reduction; see [08](08-editing-tools-and-resources.md)).
- Use **room tone or ambience** under jump cuts so the background doesn't "pop".
- Add a short **audio fade (2–4 frames)** on every cut to prevent clicks.
- Full guidance: [06 — Audio & Sound Design](06-audio-and-sound-design.md).

---

## 8. Captions and on-screen text basics

- ✅ Instagram notes many people watch with sound off. ✅ Muted Reels are a recommendation negative, so **always include audio**, but make the video understandable without it.
- 🔵 **Burned-in captions** (styled, word-by-word or phrase) or Instagram's **auto-captions** (viewer-toggleable). Many creators use both: styled burned-in text for key words, auto-captions for accessibility.
- 🔵 Readability: high-contrast text, a stroke or shadow, 2 lines max, 3–6 words per line, and inside the safe zone.
- ✅ Avoid **text covering most of the screen**. That's listed as a recommendation negative.
- Advanced styling: [04 — Text Animation](04-professional-editing-techniques.md#6-text-animation--subtitles).

---

## 9. Export basics

🔵 Export **H.264 MP4, 1080×1920, at the timeline's frame rate, ~10–20 Mbps VBR, AAC 320 kbps 48 kHz**. Instagram re-compresses everything. A clean, moderately high-bitrate source survives compression best. Full spec table: [07](07-instagram-seo-and-optimization.md#1-video-specs-cheat-sheet).

---

## 10. Fundamentals checklist

- [ ] Timeline 1080×1920, single frame rate
- [ ] First frame is the strongest frame (no black or fade-in)
- [ ] Every pause and filler word removed
- [ ] A visual change every 2–5 s
- [ ] Every claim has a visual (B-roll, screen, graphic)
- [ ] Faces and text inside the safe zone
- [ ] Music ducked under speech. No clicks at cuts
- [ ] Understandable on mute
- [ ] Ending loops or lands cleanly
- [ ] Exported per spec. No watermark

**Related:** [04 Pro Techniques](04-professional-editing-techniques.md) · [06 Audio](06-audio-and-sound-design.md) · [10 Workflow](10-content-creation-workflow.md)
