# 06 — Audio & Sound Design

> Evidence tags: ✅ Official · 🟡 Reported · 🔵 Practitioner · ⚠️ Theory
> Last researched: 2026-11-07

---

## 1. Why audio matters on Reels

- ✅ Instagram aims to show fewer **muted** Reels. Always include audio ([Help Center](https://help.instagram.com/1525585517644948)).
- ✅ **Going to the audio page** is one of the actions Instagram predicts. Audio that inspires others to create is a positive signal ([Ranking Explained](https://about.instagram.com/blog/announcements/instagram-ranking-explained)).
- 🔵 Viewers forgive soft video far more than bad audio. Echo, hiss, clipping or music drowning out speech all cause fast swipes.

---

## 2. Background music selection

### Choosing the track (🔵)

| Decision | Guidance |
|---|---|
| **Mood first** | Pick the emotion (hype, calm, nostalgic, suspense, funny) before the genre |
| **Tempo vs pacing** | Fast cuts suit 110–140 BPM. Calm or cinematic suits 60–90 BPM. Talking heads want low-intensity beds with no vocals |
| **Vocals vs instrumental** | **No lyrics under speech**: lyrics compete with your words. Lyrics are fine for montages |
| **Structure** | Find the **drop** or change and align your hero moment or reveal to it |
| **Start point** | Start the track at its most interesting part, not its intro. Trim to the hook of the song |
| **Signature sound** | A recurring audio motif (an intro sting, a transition sound) builds recognition for series |

### Trending vs original audio

| Option | Pros | Cons |
|---|---|---|
| **Trending audio** (Instagram library) | Rides an existing wave. Viewers may recognise it. Possible audio-page traffic | Not available for many business accounts. The trend fades fast. Can feel generic |
| **Original audio** (your voice, your sound) | Fully yours. Others can reuse it, crediting you ✅ (your Reel shows on the audio page) | No built-in trend momentum |
| **Library music** (licensed or royalty-free) | Safe, high quality, consistent brand | No trend effect |

🔵 **Trick:** Edit with your own licensed music for control, or add Instagram library audio **inside Instagram** at publish time (set the original audio low or muted where appropriate). Music added in-app is properly licensed and linked to the audio page; music baked into the file is not.

---

## 3. Licensing: what you can legally use

| Source | Personal / creator account | Business account / commercial | Tag |
|---|---|---|---|
| **Instagram music library (popular songs)** | Yes, within Instagram, for non-commercial use | **Restricted.** Many popular tracks are unavailable or not cleared for commercial use | ✅ Meta's music agreements cover personal, non-commercial use |
| **Meta Sound Collection** (Creator Studio / Meta Business Suite) | Yes | **Yes**, including ads. 14,000+ royalty-free tracks and SFX, **for use within Meta products** | ✅ / 🟡 ([Instagram Help](https://help.instagram.com/ipad-app/402084904469945)) |
| **Paid libraries** (Epidemic Sound, Artlist, Musicbed, Soundstripe) | Yes, per your plan | Yes, with a commercial or business plan | 🔵 Check the plan covers social and ads |
| **Free libraries** (YouTube Audio Library, Pixabay Music, Uppbeat free tier, Free Music Archive) | Usually, per each track's licence | Check each licence. Some require attribution or exclude commercial use | 🔵 |
| **Commercial songs from Spotify etc. baked into the file** | ❌ Copyright risk: muted audio, blocked Reel, takedown | ❌ | ✅ |

**Rules:**
- ⚠️ "Commercial use" means **what the content does**, not just the account type. A personal account promoting a business or a brand deal is commercial use 🟡.
- 🔵 **Keep licence proof** (download receipts or licence certificates) in each project folder (see [10](10-content-creation-workflow.md#6-ingest--organise)).
- 🔵 Branded content (paid partnerships) must use commercially cleared music.
- Music not cleared → Instagram may **mute the audio**, which is a recommendation negative ✅, or block the Reel in some regions.

---

## 4. Sound design: layering SFX

🔵 Sound design makes edits feel "expensive". Professional Reels layer four kinds of sound:

| Layer | Purpose | Examples |
|---|---|---|
| **Transitional SFX** | Sell the motion of cuts and transitions | Whoosh, swish, swoosh, reverse cymbal, riser, tape stop |
| **Impact SFX** | Emphasis on reveals, beats and punchlines | Boom, sub drop, hit, punch, camera shutter, bass drop |
| **UI / graphic SFX** | Text pops, emoji, highlights | Pop, click, tick, ding, keyboard type, notification |
| **Foley / ambience** | Realism and immersion | Footsteps, fabric, pouring, room tone, city, nature |

### SFX placement rules (🔵)
1. **Sync to the frame.** The SFX peak lands on the exact frame of the visual event (a whoosh peaks at the middle of the motion blur, an impact on the hit frame).
2. **Pre-roll risers.** Risers end on the reveal. Start them 0.5–2 s before.
3. **Less is more.** Not every cut needs a sound. Use SFX for **emphasis moments** (5–15 per minute is typical in high-energy edits, fewer in calm ones).
4. **Vary the sounds.** The same whoosh 20 times sounds cheap. Rotate 3–5 variants.
5. **Duck the music** briefly under big impacts so they punch through.
6. **Silence is a sound.** Cutting all audio for 0.3–0.5 s before a reveal creates huge impact.

### Starter SFX kit (build in Phase 3)
- 5 whooshes (short, medium, long, airy, heavy)
- 3 risers (2 s, 4 s, reverse)
- 4 impacts (sub boom, punch, cinematic hit, glitch)
- 6 UI sounds (pop, click, ding, swipe, type, camera shutter)
- 2 record scratches / tape stops (comedy)
- Room tones: quiet room, café, outdoors

Sources: [08 — Tools](08-editing-tools-and-resources.md#5-music--sound-effects-libraries).

---

## 5. Voice recording & processing

### Recording (🔵)
- **Mic:** a wireless lav (DJI Mic series, Rode Wireless series, Hollyland Lark, etc.) or a shotgun mic beats the phone's built-in mic. Keep the mic 15–25 cm from the mouth.
- **Room:** soft furnishings kill echo. Record in a closet or a carpeted room. Avoid bare walls.
- **Levels:** peaks around **−12 dBFS** when recording. Use 32-bit float recorders if available (no clipping).
- **Monitor** with headphones. Record 10 s of room tone at every location.

### Processing chain (in this order)
```
1. Noise reduction   (AI: Adobe Podcast Enhance, Resolve Voice Isolation, Premiere Enhance Speech, CapCut "Reduce noise") — 50–80%; 100% can sound robotic
2. High-pass filter  (80–100 Hz: removes rumble)
3. EQ                (cut mud 200–400 Hz if boomy; gentle boost 3–5 kHz for clarity; air 10–12 kHz)
4. De-esser          (tame 5–8 kHz sibilance)
5. Compressor        (ratio 3:1–4:1, 3–6 dB gain reduction, fast attack, medium release)
6. Limiter           (ceiling −1 dBTP)
```

---

## 6. Mixing levels for Reels

🔵 Instagram doesn't publish a loudness target. These are widely used social-media mixing standards:

| Element | Target |
|---|---|
| **Overall integrated loudness** | About **−14 LUFS** (common streaming and social target). Range −14 to −10 LUFS for punchy short-form |
| **True peak** | ≤ **−1 dBTP** (prevents distortion after Instagram's encoding) |
| **Dialogue** | The loudest, clearest element. Typically peaks around −6 to −3 dBFS after the limiter |
| **Music under speech** | **−18 to −25 dB below dialogue** (felt, not competing) |
| **Music alone (montage)** | Can sit near full level |
| **SFX** | Present but not startling. Impacts can briefly match dialogue level |

**Ducking:** Use auto-ducking (Premiere Essential Sound "Ducking", Resolve Fairlight sidechain or Auto-Duck, CapCut) or keyframe the music volume down under speech, with 0.2–0.5 s fades.

**Phone-speaker check (🔵):** Phones play through tiny speakers with little bass. Always test the final mix on a phone speaker **and** earbuds. Bass-only elements (sub drops) disappear on speakers, so layer a mid-frequency element on impacts.

---

## 7. Beat syncing

🔵 Workflow:
1. Place the music first. Mark the beats: Premiere markers (M key while playing), Resolve markers, CapCut **Auto Beat / Beats**, Edits beat markers.
2. Cut primary transitions on the **downbeats** (1 of each bar). Add accents on snares or claps.
3. Put the biggest visual moment on the **drop** or key change.
4. Don't sync *every* cut to *every* beat. Syncopation (some cuts off the beat) feels more natural.
5. Use speed ramps to fit an action precisely onto a beat (see [04](04-professional-editing-techniques.md#3-speed-ramping--slow-motion)).

---

## 8. Audio QC checklist

- [ ] Audio is present (not muted). Music is licensed for this use
- [ ] Dialogue is intelligible on a phone speaker
- [ ] No clipping. True peak ≤ −1 dBTP. Around −14 LUFS
- [ ] Music ducked under speech
- [ ] No clicks at cuts (audio fades of 2–4 frames)
- [ ] Room tone under jump cuts
- [ ] SFX synced to the frame and varied
- [ ] Licence proof saved in the project folder

**Related:** [04 Pro Techniques](04-professional-editing-techniques.md) · [08 Tools](08-editing-tools-and-resources.md)
