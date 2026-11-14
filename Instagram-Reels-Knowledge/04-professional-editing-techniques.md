# 04 — Professional Editing Techniques

> Evidence tags: ✅ Official · 🟡 Reported · 🔵 Practitioner · ⚠️ Theory
> Last researched: 2026-11-07 · Prerequisite: [03 — Fundamentals](03-video-editing-fundamentals.md)
> Almost everything here is 🔵 practitioner craft. Instagram doesn't rank on technique; it ranks on whether people watch and share. Use technique to **serve the story**, not to show off.

---

## 1. Transitions

### Principle
🔵 The best transition is **motivated**: the movement, shape or sound in shot A *causes* the move into shot B. Unmotivated preset transitions (spins, page curls) look amateur.

### Transition library

| Transition | How to shoot | How to edit | Best for |
|---|---|---|---|
| **Whip pan** | End shot A with a fast pan (right). Start shot B with a fast pan in the same direction | Cut at the blurriest frames. Add directional blur (4–8 frames) and a *whoosh* SFX | Location changes, energy |
| **Match cut (shape/motion)** | Frame a similar shape or motion in both shots (a ball and the moon, a door closing and a laptop closing) | Align the shapes' positions frame-accurately. Hard cut | "Wow" storytelling beats |
| **Object / body wipe** | Something passes close to the lens (a hand, a pole, a person) | Mask along the edge of the wiping object, revealing shot B behind it | Seamless scene changes |
| **Mask / reveal transition** | A walk-through doorway, a pillar, a phone covering the lens | Keyframe a mask following the edge | Travel, outfit changes |
| **Cover-the-lens** | Hand or object covers the lens fully, then uncovers in a new scene | Cut on the fully covered frame | Easy and reliable, good on a phone |
| **Zoom transition** | Push in fast at the end of A, pull out at the start of B | Scale keyframes with easing plus motion blur. Or a "zoom-through" on a dark area | Fast-paced montages |
| **Spin / roll** | Rotate the camera during the move | Rotation keyframes plus blur. Match the direction | Energetic content (use sparingly) |
| **Jump/drop on the beat** | Action lands on the beat (a jump, a clap, a snap) | Cut exactly on the beat frame | Outfit changes, before/after |
| **Light leak / flash** | — | Overlay a light leak or white flash (2–6 frames, screen blend) | Mood shifts, vintage style |
| **Morph cut / smooth cut** | Same framing talking head | Premiere's Morph Cut, Resolve's Smooth Cut (AI interpolation) | Hiding jump cuts invisibly |
| **Sound-led (J-cut)** | — | Bring in shot B's audio 0.3–1 s early | Elegant, cinematic, invisible |

### Execution tips
- Keep transitions **under ~0.5 s** in short-form, unless the transition *is* the content.
- **Pair every visual transition with SFX** (whoosh, swish, hit) at the frame of change. See [06](06-audio-and-sound-design.md#4-sound-design-layering-sfx).
- **Motion blur** sells speed: add it after scale or position keyframes (built-in in Resolve and Premiere; plugins like ReelSmart Motion Blur).
- **Plan transitions while shooting.** You can't fake a whip pan you didn't film.

---

## 2. Cinematic camera movements

| Movement | Emotion / function | Phone tip |
|---|---|---|
| **Push-in (dolly in)** | Tension, focus, revelation | Walk forward slowly. Gimbal or "action mode" stabilisation |
| **Pull-out (dolly out)** | Reveal context, ending, isolation | Walk backward. Reveal the environment |
| **Orbit / arc** | Hero shot, product showcase | Circle the subject at a constant distance. A gimbal helps |
| **Parallax slide** | Depth, premium feel | Move sideways with an object in the foreground. Subject in the mid-ground |
| **Tilt reveal** | Reveal from feet to face, or ground to skyline | Slow, steady tilt |
| **Pedestal (vertical move)** | Rise above an obstacle into a reveal | Raise the phone from low to high |
| **Low-angle tracking** | Power, energy (walking shots) | Phone upside-down near the ground (flip in the edit) |
| **Top-down (flat lay)** | Tutorials, food, desk setups | Overhead arm or tripod |
| **Handheld** | Authenticity, energy, vlog | Intentional, not shaky. Light stabilisation in post |
| **Static locked-off** | Talking heads, timelapse, letting action breathe | Tripod |

### Faking movement in post
- 🔵 **Digital push-in:** Shoot 4K, scale from 100% to 110–115% over the shot with easing. Works best on static shots.
- 🔵 **Ken Burns on photos:** slow scale plus position drift.
- 🔵 **Camera shake:** add subtle shake on impacts (2–6 frames). Resolve's Camera Shake, a plugin, or keyframed position jitter.
- 🔵 **Stabilisation:** Warp Stabilizer (Premiere), Stabilizer (Resolve) or Gyroflow (gyro-data cameras). Over-stabilising causes "jelly" warping. Use crop-smooth mode.

---

## 3. Speed ramping & slow motion

### Shooting for slow motion (🔵)

| Capture fps | On a 30 fps timeline | On a 24 fps timeline |
|---|---|---|
| 60 fps | 50% (2× slower), clean | 40% |
| 120 fps | 25% (4× slower), clean | 20% |
| 240 fps | 12.5% (8× slower), clean | 10% |

- **Shutter for slow-mo:** 1/(2×capture fps), so 1/240 for 120 fps. More light is needed: shoot outdoors or add lights. Indoor 120 fps on a phone is often noisy.
- **Lock exposure and focus** (AE/AF lock) so they don't pulse mid-shot.
- Slower than your capture allows will **stutter**. Use **frame interpolation** (Resolve **Optical Flow / Speed Warp**, Premiere **Optical Flow**, Topaz Video AI, Twixtor). Interpolation artefacts appear around edges and fast-moving objects, so check them.

### Speed ramp technique (🔵)

A speed ramp goes fast, then slow, then fast (or the reverse) within one clip, for emphasis.

1. **Conform** high-fps footage so it plays at 100% real time on the timeline (or interpret it as 60 fps).
2. **Find the hero moment**: the impact, the jump, the reveal.
3. **Ramp:** before the moment, run at 150–300% speed. At the moment, drop to 20–50% (using the extra frames). After it, ramp back to 150–300%.
4. **Ease the ramp** with bezier/curve speed keyframes. Linear ramps feel mechanical. A ramp duration of 4–10 frames feels snappy, 10–20 frames feels smooth.
5. **Sync to music:** Put the slow section on a drop, a breath in the music, or a riser peak. Put the fast sections on build-ups.
6. **Add motion blur** in the fast sections, plus a **whoosh into the slow-mo** and an **impact** at the hero moment.

**Where:** Premiere (Time Remapping), Resolve (Retime Controls / Retime Curve), Final Cut (Retime / Speed Ramp), CapCut (Speed → Curve), Edits (speed tools).

---

## 4. Keyframing, masking, tracking & compositing

| Technique | Use | Tools |
|---|---|---|
| **Keyframes with easing** | Every animated property (position, scale, opacity). Always ease in and out | All editors. Learn the graph/curve editor |
| **Masking** | Reveal transitions, clone effects (you twice in a frame), text behind subject | Premiere masks, Resolve Power Windows, CapCut masks |
| **AI subject isolation** | "Text behind person" effect, background replacement, selective colour | Resolve Magic Mask, Premiere Object Mask, CapCut Remove BG, Edits cutouts |
| **Motion tracking** | Text or graphic sticks to a moving object. Blur faces or logos | Resolve tracker, Premiere mask tracking, After Effects, Mocha |
| **Green screen / chroma key** | Commentary over a screenshot or article | Resolve Delta Keyer / 3D Keyer, Premiere Ultra Key, Instagram green screen effect |
| **Picture-in-picture** | Face cam over screen recording | Rounded-corner frame, subtle drop shadow |
| **Freeze frame + cutout** | Pause the action and highlight a subject | Freeze, then mask the subject, then darken the background, then add a label |

**Signature effect example: "Text behind subject"**
1. Duplicate the clip on V2.
2. AI-mask the person on V2 (Magic Mask / Object Mask).
3. Put the title text on a track between V1 and V2.
4. The text now sits behind the person but in front of the background.

---

## 5. Colour correction and grading

### Correction first, then grade (🔵)

**Correction** makes footage technically right: neutral, balanced, matched. **Grading** creates the look and mood.

#### Use scopes, not your eyes
- **Waveform / luma parade:** exposure. Blacks around 0–5% (not crushed unless intended), highlights under 100% (no clipping), skin around 50–70%.
- **RGB parade:** white balance. Neutral greys show equal R, G and B.
- **Vectorscope with the skin-tone line:** skin hues fall near the skin-tone indicator line regardless of ethnicity (saturation varies, hue stays close).

#### Correction order (node or layer order)
1. **Input transform:** if shot in log (Apple Log, Samsung Log, S-Log3, etc.), convert to Rec.709 with the proper **colour space transform (CST)** or the manufacturer LUT.
2. **Exposure / contrast:** set black and white points.
3. **White balance:** neutralise with the colour temperature and tint, or eyedropper a neutral surface.
4. **Saturation:** moderate global saturation.
5. **Shot matching:** match all shots in a scene to a hero shot.

### Grading (creating a look)

| Look | Recipe (starting point) |
|---|---|
| **Clean / bright creator** | Lifted exposure, soft contrast, accurate warm skin, slightly boosted vibrance |
| **Teal & orange cinematic** | Push shadows toward teal and highlights or skin toward orange. Protect skin with a qualifier |
| **Moody / desaturated** | Lower saturation (−15 to −30%), crush blacks slightly, cool shadows, warm highlights |
| **Film emulation** | Film LUT or plugin (Dehancer, FilmConvert), soft highlight roll-off, grain at 5–15% |
| **Vintage / VHS / retro** | Faded blacks (lift), colour cast, grain, halation, slight chromatic aberration |

**Grading rules (🔵):**
- **Protect skin tones.** Viewers forgive an odd sky but not odd skin.
- **LUTs are a starting point, not a finish.** Apply them *after* correction (or as the CST), then reduce opacity or intensity to taste.
- **Consistency:** One signature look across your Reels supports brand recognition. Save it as a preset (Phase 3).
- **Check on a phone at medium brightness.** Most viewers watch there. Laptop screens lie.
- **Instagram compression** crushes subtle gradients (skies, dark scenes) into banding. Add light grain (2–5%) to reduce banding and avoid extreme dark grades.

### HDR vs SDR
- 🔵 / 🟡 iPhone and many Androids record **HDR (HLG / Dolby Vision)** by default. Instagram plays HDR on supported phones, but appearance varies, and mixing HDR and SDR clips causes brightness jumps.
- **Recommendation for edited Reels:** Grade and export **SDR Rec.709**, or turn off HDR capture for consistency, unless you're deliberately delivering HDR end-to-end.

---

## 6. Text animation & subtitles

### Subtitle styles (2026 short-form standards)

| Style | Description | Use |
|---|---|---|
| **Word-by-word highlight** | Active word changes colour or scales | Talking heads, high energy |
| **Phrase pop** | 2–5 words pop in with a scale bounce (90%→105%→100%) | Most versatile |
| **Karaoke fill** | Words fill with colour as spoken | Educational |
| **Minimal lower-centre** | Clean sans-serif, small, sentence case | Cinematic, premium |
| **Keyword emphasis** | Only key words in large type, sometimes with emoji | Hook and emphasis moments |

### Typography rules (🔵)
- **Fonts:** 1–2 fonts max. Bold geometric or grotesque sans for captions (for example Montserrat, Inter, Poppins, Gilroy, Proxima-style). A display or serif font for titles if it fits your brand.
- **Size:** Body captions around **55–75 px** cap height at 1080 wide. Hook titles **80–140 px**.
- **Contrast:** white or yellow with a black stroke (3–6 px) or a soft shadow. Or a text box (rounded rectangle, 70–90% opacity).
- **Placement:** Inside the safe zone. Captions around the **lower-middle third** (above the bottom UI), never under the right-side buttons.
- **Line length:** 3–6 words per line, 2 lines max.
- **Reading time:** Viewers need about **0.3 s per word, minimum 1 s per on-screen card**. Hook text must be readable inside 1–2 s.
- **Accuracy:** Fix auto-transcription errors. Typos hurt credibility.
- **Accessibility:** Burned-in captions plus Instagram auto-captions (toggleable). Avoid red/green-only colour coding.

### Kinetic text techniques
- **Scale bounce in:** 0→110→100% over 6–8 frames, with an overshoot ease.
- **Slide plus fade:** 20–40 px movement plus opacity over 4–6 frames.
- **Typewriter:** per-character reveal for "terminal" or story styles.
- **Masked reveal:** text rises from behind an invisible line.
- **Tracked text:** text pinned to a moving object (see section 4).
- **Emphasis hits:** a key word scales up with an SFX "pop" or "hit".

**Tools:** CapCut and Edits auto-captions with styles; Premiere Pro (Speech-to-Text plus **single-word social captions**, added in v26.3, June 2026 🟡 [Adobe](https://helpx.adobe.com/hk_en/premiere-pro/using/new-features.html)); Resolve (Studio auto subtitles plus Text+ animation); Submagic and similar AI caption tools (see [08](08-editing-tools-and-resources.md)).

---

## 7. Advanced retention-editing tricks (🔵)

| Trick | Description |
|---|---|
| **Visual hook stacking** | First frame contains motion, a face and text at once |
| **Progress cue** | "3 tips" counters, a step number on screen, or a subtle progress bar. Viewers stay to finish |
| **Zoom on emphasis** | Punch in 10–20% on key words |
| **Sound-effect accents** | A pop or whoosh on every text or graphic entrance (keep it subtle) |
| **Screen-shake on impact** | 2–4 frames on punchlines or reveals |
| **B-roll every claim** | Literal visuals for abstract statements |
| **Loop edit** | The last frame or line connects seamlessly to the first, so replays feel natural |
| **"Wait for it" timing** | Hold the payoff until the final 10–20% |
| **Colour or energy change at the midpoint** | Re-hooks viewers at the typical drop point |

---

## 8. Pro editing workflow summary

```
Organise → Select (stringout of best takes) → Rough cut (story only)
 → Fine cut (pacing, jump cuts, B-roll) → Lock picture
 → Sound (dialogue clean-up, music, SFX, mix)
 → Colour (correct → match → grade)
 → Graphics & captions
 → QC on phone → Export → Upload
```
Full SOP with checklists: [10 — Workflow](10-content-creation-workflow.md).

**Related:** [03 Fundamentals](03-video-editing-fundamentals.md) · [06 Audio](06-audio-and-sound-design.md) · [08 Tools](08-editing-tools-and-resources.md)
