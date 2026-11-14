# 24 — Beat Sync & Sound Design

> **Phase 3** · Created 2026-11-07 · Extends [06 — Audio & Sound Design](06-audio-and-sound-design.md)
> Evidence tags: ✅ Official · 🟡 Reported · 🔵 Practitioner · ⚠️ Theory · 🧪 Tested here

---

## 1. Beat maths (frames per beat)

`frames per beat = 60 ÷ BPM × fps`

| BPM | Feel | @ 24 fps | @ 30 fps | @ 60 fps | 1 bar (4 beats) @ 30 fps |
|---|---|---|---|---|---|
| 70 | Slow melody, emotional | 20.6 | 25.7 | 51.4 | 3.43 s |
| 80 | Ballad, nostalgic | 18.0 | 22.5 | 45.0 | 3.00 s |
| 90 | Mid groove | 16.0 | 20.0 | 40.0 | 2.67 s |
| 100 | Mid | 14.4 | 18.0 | 36.0 | 2.40 s |
| 110 | Upbeat | 13.1 | 16.4 | 32.7 | 2.18 s |
| 120 | Dance / pop | 12.0 | 15.0 | 30.0 | 2.00 s |
| 128 | EDM / mass | 11.3 | 14.1 | 28.1 | 1.88 s |
| 140 | Fast / hype | 10.3 | 12.9 | 25.7 | 1.71 s |
| 150 | Very fast | 9.6 | 12.0 | 24.0 | 1.60 s |
| 160 | Very fast | 9.0 | 11.3 | 22.5 | 1.50 s |

**Reading it:** at 120 BPM and 30 fps, a beat is every 15 frames. A cut **every beat** is very fast (0.5 s shots). **Every 2 beats** (1 s) is energetic. **Every bar** (2 s) is calm. Non-integer values (e.g. 14.1) mean the beat drifts across frames, so **snap each cut to the nearest marker**, not to a fixed frame count.

---

## 2. Sync hierarchy (what to align, in priority order)

| Priority | Audio event | Picture event |
|---|---|---|
| 1 | **Drop / biggest hit** | Hero frame, reveal, freeze + name card, BGM switch |
| 2 | **Phrase starts** (every 4 or 8 bars) | Scene or section changes |
| 3 | **Downbeats** (beat 1 of a bar) | Main cuts |
| 4 | **Accents** (snare, clap, vocal hits) | Action hits, text pops, zoom punches |
| 5 | Off-beats | Optional syncopated cuts for variety |
| — | **Dialogue syllables** | Lip-sync, reaction cuts ([23 §5](23-tamil-bgm-editing-guide.md#5-dialogue-lip-sync--dub-technique)) |

🔵 **Don't cut on every beat for the whole Reel.** Vary density: sparse in the setup, dense in the build, a hard sync on the drop. Contrast in cut density reads as rhythm. Uniform density reads as a slideshow.

🔵 **Cut 1–2 frames before the beat.** Many editors place cuts 1–2 frames *early*, so the cut is perceived *on* the beat (visual processing lags slightly behind audio). Test both on your phone.

🔵 **Action on the beat, not the cut.** For movement (a kick, a jump, a head turn), the beat should hit the **peak of the action**, which may be mid-shot rather than at a cut.

---

## 3. Marking the audio before cutting

| Tool | How to get beat and hit markers |
|---|---|
| **tools/audio_beats.py** (me) 🧪 | Gives the BPM, beat grid (seconds + frame numbers), strongest hits and the candidate drop from a local reference copy ([tools/README](tools/README.md#audio_beatspy--tempo-beat-grid-hits-and-drop-for-sync-planning)). Beat grid tested to within 18 ms. Confirm by ear |
| CapCut | Select the audio → **Beats** → Auto generate. Add manual beats by tapping while playing |
| DaVinci Resolve 20+ | **AI Detect Music Beats** places markers automatically 🟡 ([ProVideo Coalition](https://www.provideocoalition.com/davinci-resolve-20-released/)) · or press **M** on each beat during playback |
| Instagram / Edits | Align clips to the audio waveform in the editor. Edits reportedly has beat markers 🟡 |
| Manual (always valid) | Play the track, tap along, and mark the 4–6 points that matter: start of the hook phrase, build start, drop, switch, end |

**Marker naming convention** (used in every edit plan, see [26](26-video-production-workflow.md)):
`H` = hook phrase start · `B` = build start · `D` = drop · `S` = switch · `A1…An` = accents · `E` = ending / loop point

---

## 4. Syncing to audio you'll add in-app

Library audio is added **in Instagram or Edits after export** ([28 §3](28-reels-export-and-publishing.md#3-adding-instagram-library-audio-in-app)). So the sync must survive that hand-off:

1. **Get a reference copy** of the exact audio segment (screen-record the Instagram audio page or Reel playing, or use your own copy) → I analyse it with `audio_beats.py`
2. **Define the in-app start point:** "Start the audio at **0:14.2** of the track" (the time the hook phrase begins in the full song)
3. I cut the video to the reference's markers, with **the video's 0.0 s = the audio's start point**
4. I export a **sync-guide version** (with the reference audio, for your review only) and a **clean version** (natural sound + SFX only, no film audio)
5. You add the library audio in-app, set the start at the stated point, and check that the drop hits the hero frame. Instagram's segment picker is coarse, so **nudge until the drop lands**. The export includes a **visual sync flash** option (a 2-frame marker you can remove) if alignment is hard

---

## 5. Sound design layering

### 5.1 Layer stack for a Bruh-Cinema Reel
```
L1  Natural sound (your voice, pets, engine, room)     → authenticity; keep it, don't mute it
L2  SFX: transitions (whoosh/swish/riser)               → sells motion
L3  SFX: impacts (hit/boom/punch) + "bruh" sting (S3)   → emphasis / comedy beats
L4  SFX: UI (pop/click/ding) for text and graphics      → subtle
L5  Music: added in-app (library) OR licensed/royalty-free baked in
```

### 5.2 SFX placement rules
| Rule | Detail |
|---|---|
| Frame-accurate | The **peak** of the SFX lands on the visual event (a whoosh peaks mid-blur, an impact on the hit frame) |
| Pre-roll risers | A riser **ends** on the reveal. It starts 0.5–2 s earlier |
| Density | High-energy edits: ~5–15 SFX per minute. Calm or cinematic: a few, or none |
| Variety | Rotate 3–5 variants per type. Repeating the identical whoosh sounds cheap |
| Silence | 0.2–0.5 s of near-silence before the big reveal or switch is the strongest "SFX" you have |
| Don't fight the music | When library music will be added, keep SFX in the mid-highs (whooshes, pops). Keep heavy sub-booms only on the drop |

### 5.3 Your signature sounds (to build in the Phase 3 kit)
| Signature | Spec |
|---|---|
| **"Bruh" sting (S3)** | ≤0.6 s. Your own recorded voice ("bruh") or a distinctive royalty-free sound. Normalised and consistent every time |
| **Name-card hit (S1)** | Short cinematic impact (sub + transient), ~0.4–0.8 s |
| **Record scratch** | For the BGM switch. Royalty-free version only |
| **Whoosh set** | Short (≤0.3 s), medium (0.5 s), airy, heavy |
| Sources | Royalty-free libraries ([08 §5](08-editing-tools-and-resources.md#5-music--sound-effects-libraries)), or record your own (best for originality). Keep licence proof in `licenses/` |

---

## 6. Mixing levels

### 6.1 When library music is added in-app (the default workflow)
| Element in my export | Target | Why |
|---|---|---|
| Overall export loudness | **≈ −16 LUFS integrated** (slightly under −14) | Leaves headroom. The in-app music adds energy on top |
| True peak | ≤ −1 dBTP | Prevents distortion after Instagram's encoding |
| Dialogue / your voice | The clearest element. Normalised so it's intelligible over music | You'll balance with Instagram's volume sliders |
| SFX | Present, not startling. Impacts can briefly reach dialogue level | |

In-app: Instagram's editor has separate volume controls for the **original audio** and the **added music**. 🔵 Starting point: music around 60–80%, original 80–100% when speech matters. Music up and original down for pure montage. Check on a phone speaker.

### 6.2 When everything is baked into the export (licensed or royalty-free music only)
| Element | Target |
|---|---|
| Integrated loudness | **−14 LUFS** (range −14 to −10 for punchy short-form) ([06 §6](06-audio-and-sound-design.md#6-mixing-levels-for-reels)) |
| True peak | ≤ −1 dBTP |
| Music under speech | Ducked 12–20 dB (sidechain) |

### 6.3 ffmpeg mixing recipes 🧪 (tested 2026-11-07)
```bash
# Duck music under voice (sidechain) + mix + loudness-normalise to -14 LUFS / -1 dBTP
ffmpeg -i music.wav -i voice.wav -filter_complex \
 "[1:a]asplit=2[vsc][vmix];[0:a][vsc]sidechaincompress=threshold=0.03:ratio=8:attack=20:release=300[duck];\
  [duck][vmix]amix=inputs=2:normalize=0,loudnorm=I=-14:TP=-1.0:LRA=11[a]" -map "[a]" -ar 48000 mix.wav

# Place an SFX at 3.20 s (adelay in ms, both channels) and mix with the natural sound
ffmpeg -i natural.wav -i whoosh.wav -filter_complex \
 "[1:a]adelay=3200|3200,volume=0.8[s];[0:a][s]amix=inputs=2:normalize=0[a]" -map "[a]" out.wav
```
For final deliverables I use **two-pass loudnorm** (measure, then apply) for accurate targets.

---

## 7. Voice clean-up chain (your speech in Reels)

From [06 §5](06-audio-and-sound-design.md#5-voice-recording--processing), available locally in ffmpeg:
| Step | ffmpeg filter | Notes |
|---|---|---|
| Noise reduction | `afftdn` / `anlmdn` (classic) · `arnndn` (needs an RNNoise model file) | 50–80% strength. Avoid a robotic sound |
| Rumble removal | `highpass=f=90` | |
| Clarity EQ | `equalizer=f=300:t=q:w=1:g=-3, equalizer=f=4000:t=q:w=1:g=2` | Adjust by ear |
| De-ess | `deesser` | |
| Compression | `acompressor=threshold=-20dB:ratio=3:attack=10:release=150` | |
| Loudness | `loudnorm` (two-pass) | |

If you edit in CapCut or Resolve: CapCut's "Reduce noise" and "Enhance voice", or Resolve's Voice Isolation (Studio) / Dialogue Leveler.

---

## 8. Beat-sync & sound checklist

- [ ] Markers H, B, D, (S), E identified and noted in the edit plan
- [ ] Hero frame on D within ±1 frame
- [ ] Cut density varies (sparse → dense → hit)
- [ ] SFX peaks on visual events. Variants rotated. Silence before the big moment
- [ ] Export loudness ≈ −16 LUFS (in-app music) or −14 LUFS (baked music), TP ≤ −1
- [ ] In-app audio start point and volume levels written down for you
- [ ] Checked on a phone speaker

**Related:** [23 Tamil BGM](23-tamil-bgm-editing-guide.md) · [25 Cinematic & comedy](25-cinematic-and-comedy-editing.md) · [28 Export](28-reels-export-and-publishing.md)
