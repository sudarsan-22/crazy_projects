# 25 — Cinematic & Comedy Editing

> **Phase 3** · Created 2026-11-07 · Extends [04 — Professional Techniques](04-professional-editing-techniques.md) with production recipes for CapCut, DaVinci Resolve and ffmpeg
> Evidence tags: ✅ Official · 🟡 Reported · 🔵 Practitioner · ⚠️ Theory · 🧪 Tested here
> Your style: "Bruh Cinema". **Commit fully to the cinematic setup, then break it with comedy.** Both halves must be done well for the contrast to work.

---

## 1. Comedy timing toolkit

| Device | How it works | Edit execution | Typical timing (🔵) |
|---|---|---|---|
| **The beat (pause)** | A short silence before or after the punchline lets the brain catch up | Hold the shot. Cut the music or drop it to natural sound | 0.3–0.8 s |
| **Reaction hold** | The audience laughs at the *reaction* more than the event | Cut to the face or pet and **hold** longer than feels comfortable | 1–2 s |
| **Smash cut** | Abrupt cut from setup to contrasting reality | Hard cut + audio contrast (loud → quiet or epic → silly) | Instant |
| **Zoom punch** | Sudden push-in = "realisation" or emphasis | Scale 100→112–120% over 3–5 frames, hold, optional return | 3–5 frames in |
| **Freeze frame + caption** | Pauses time to comment on the moment | Freeze 0.8–1.5 s + text or name card + hit SFX | 0.8–1.5 s |
| **Record scratch** | Signals "wait, what?" | Scratch SFX on the switch frame + freeze or stop | 0.3–0.6 s |
| **Rule of three** | Two normal beats, the third breaks the pattern | Same framing or rhythm for beats 1–2, then subvert on 3 | — |
| **Callback** | Reuse an earlier joke (the rabbit's villain theme returns) | The same audio cue or framing as the earlier Reel or moment | — |
| **Deadpan** | No reaction is funnier than overacting | Static shot, neutral face, hold | 1–2 s |
| **Speed-up for absurdity** | 2–4× speed makes struggle look silly | Speed-up + comedic music or natural sound pitched up | — |
| **Screen shake** | Physical impact or shock | 2–4 frames of ±10–20 px jitter | 2–4 frames |
| **Ironic text** | Text contradicts the image ("Professional rider" over a stall) | Clean, confident text style. Let the image disprove it | Read time ≥1 s |

### Comedy rules
1. **Setup must be clear.** If viewers don't understand the expectation, the break isn't funny. Establish it within 2–4 s.
2. **One punchline per Reel** (plus an optional tag at the end). Stacking jokes dilutes them.
3. **Cut on the laugh, not after.** End or move on right after the payoff lands. Lingering kills energy. Exception: the reaction hold.
4. **Real beats fake.** Genuine fails and reactions from your footage beat staged ones. Look for them during footage analysis ([26 §3](26-video-production-workflow.md#3-stage-1--footage-analysis)).
5. **Don't explain the joke** in text or caption.

---

## 2. Cinematic transitions (recipes)

| Transition | Needs in footage | CapCut | Resolve | ffmpeg 🧪 |
|---|---|---|---|---|
| **Hard cut on beat** | — | Split on a beat marker | Blade on a marker | trim + concat |
| **Whip pan** | A fast pan at the end of A and the start of B (same direction) | Cut at the blurriest frames + "Blur" or "Swipe" transition ≤0.3 s + whoosh | Cut + Directional Blur (Fusion) or Transform blur | `xfade=transition=slideleft:duration=0.2` (approximation) + whoosh |
| **Match cut** | A similar shape or motion in both clips | Align by position/scale keyframes. Hard cut | Same. Use onion-skin-style overlay at 50% opacity to align | Precise trim. Scale/position via `scale`+`crop` |
| **Cover-the-lens** | A hand or object covers the lens fully | Cut on the fully covered frame | Same | Cut at the darkest frame |
| **Zoom-through** | Motion toward the lens or a dark area | Zoom transition ≤0.3 s | Dynamic Zoom + Cross Dissolve 4 frames | `xfade=transition=zoomin` 🧪 + scale ramp |
| **Flash cut** | — | White "Flash" transition, 2–3 frames | Dip to colour (white) 2–3 frames | `xfade=transition=fadewhite:duration=0.1` |
| **Light leak** | — | Overlay light-leak clip (Screen blend) | Light-leak clip, Composite: Screen | Requires a light-leak asset (royalty-free) |
| **Cross dissolve** | Emotional or romantic scenes only | Dissolve 8–12 frames | Cross Dissolve | `xfade=transition=fade:duration=0.35` 🧪 |
| **Beat-drop smash** | — | Hard cut exactly on D (drop) | Same | trim at the drop frame |

🧪 Tested 2026-11-07: `xfade` (slide), frame-evaluated scale + crop zoom, combined in one filter graph. Rendered correctly at 1080×1920 / 30 fps.

**Restraint rule:** ≤2 "designed" transitions per Reel. The rest are hard cuts. Designed transitions should mark **section changes** (setup → reality, location A → B).

---

## 3. Speed ramping (recipes)

### 3.1 Ramp shapes
| Shape | Profile | Use |
|---|---|---|
| **Hero ramp** | 100% → **25–40%** (hold the hero moment) → 100% | Bike or car reveal, a jump, a pet leap |
| **Montage ramp** | 200–300% → 50% on the hit → 200% | Travel or montage energy |
| **Bullet** | 100% → 10–20% at the peak → 100% | One dramatic freeze-like moment |
| **Flash in / out** | Fast in (300%) → normal, or normal → fast out | Entering or leaving a scene |

### 3.2 Execution rules (🔵)
- The **slow section needs high-fps source** (60/120 fps) or interpolation (§4)
- **Ease the transitions** with bezier curves over 4–10 frames (snappy) or 10–20 frames (smooth)
- **The slowest point = the beat or drop** ([24 §2](24-beat-sync-and-sound-design.md#2-sync-hierarchy-what-to-align-in-priority-order))
- Add **motion blur** to the fast sections, a whoosh *into* the slow-mo, and an impact *at* the hero frame
- **Audio:** ramps distort natural sound. Mute it or replace it with SFX during the ramp

### 3.3 Tool steps
| Tool | Steps |
|---|---|
| **CapCut** | Clip → Speed → **Curve** → "Hero" or "Montage" preset → Edit: drag the beat points so the dip lands on the beat marker → enable **Smooth slow-mo** if the slow section stutters |
| **Resolve** | Retime Controls → add speed points around the hero moment → set the middle segment to 25–40% → **Retime Curve** → bezier handles for easing → Retime Process: Optical Flow |
| **ffmpeg (me)** | Split into segments, apply `setpts` per segment, concat. **Limitation:** stepped speed changes, not true bezier curves. I approximate easing with 4–8 short segments of gradually changing speed. Fine for snappy ramps. For silky long ramps I'll give you CapCut or Resolve steps instead |

---

## 4. Slow motion & time remapping

### 4.1 Source frame rate determines quality
| Source fps | On a 30 fps timeline | Quality |
|---|---|---|
| 30 | 100% only. Slower needs interpolation | ⚠️ Interpolation artefacts |
| 60 | down to **50%** clean | ✅ |
| 120 | down to **25%** clean | ✅✅ |
| 240 | down to **12.5%** clean | ✅✅ (needs strong light) |

### 4.2 Methods when slower than the source allows
| Method | Quality | Where |
|---|---|---|
| Frame duplication | Stutter | Default in many apps. Avoid |
| Frame blending | Ghosting | Resolve "Frame Blend". OK for quick fixes |
| **Optical flow** | Good. Warping at edges and with fast motion | CapCut Smooth slow-mo · Resolve Optical Flow (free) · **ffmpeg `minterpolate`** 🧪 |
| **AI (Speed Warp, Topaz)** | Best | Resolve Studio · Topaz Video AI |

🧪 ffmpeg interpolation tested 2026-11-07:
```bash
# 30 fps source -> interpolate to 60 -> play at half speed on a 30 fps timeline
-vf "minterpolate=fps=60:mi_mode=mci:mc_mode=aobmc:vsbmc=1,setpts=2*PTS,fps=30"
# 60 fps source -> clean 50% slow-mo (no interpolation needed)
-vf "setpts=2*PTS,fps=30"
```
⚠️ `minterpolate` is slow (CPU) and can warp fast-moving edges (wheels, hands). I always review interpolated sections frame by frame and fall back to a shorter slow-mo if artefacts show.

### 4.3 Shooting for slow-mo (for future footage)
- Phone: Slo-mo mode (120/240 fps) or 60 fps video. **Bright light** is essential
- Shutter ≈ 1/(2×fps) when controllable (Blackmagic Camera app)
- Lock focus and exposure
- Shoot **longer than needed** (2–3 s before and after the action)

---

## 5. Colour correction & cinematic grading

### 5.1 Pipeline (always in this order)
1. **Normalise:** HDR → SDR if needed (iPhone HDR / HLG footage). Log → Rec.709 via the manufacturer LUT
2. **Correct:** exposure (black and white points), white balance, saturation baseline
3. **Match** shots in the same scene
4. **Look:** MovieMode or Reality (S5), applied consistently
5. **Finish:** grain (reduces banding after Instagram compression), vignette (subtle)

### 5.2 Your two signature looks (S5) — starting values

| Parameter | 🎬 **MovieMode** (dramatic setup) | 📱 **Reality** (after the switch) |
|---|---|---|
| Contrast | +8–12% | 0 to −5% (slightly flat) |
| Saturation | +5–10% (skin protected) | 0 to −10% |
| Shadows | Toward teal/blue | Neutral |
| Highlights / skin | Toward warm/orange | Neutral |
| Vignette | Subtle (darken edges ~15–20%) | None |
| Grain | Light (3–6%) | None |
| Optional | Slight warm bloom on highlights | Slightly cooler white balance (looks "everyday") |

**ffmpeg implementation 🧪** (tested chain; values tuned per footage):
```bash
# MovieMode
-vf "eq=contrast=1.08:saturation=1.08:gamma=0.97,colorbalance=rs=-0.05:bs=0.06:rh=0.06:bh=-0.04,vignette=PI/5,noise=alls=5:allf=t"
# Reality
-vf "eq=contrast=0.97:saturation=0.95,colortemperature=temperature=7000"
```
**CapCut:** Adjust → Contrast +10, Saturation +8, HSL (orange: saturation −5 to protect skin), Vignette +15, Grain +5. Save as a preset (Phase 3 kit).
**Resolve:** Node 1 correction → Node 2 look (Color Warper or Lift/Gain wheel tint: lift → teal, gain → warm) → Node 3 grain (Film Grain, Studio) or an overlay.
**LUTs:** `.cube` LUTs work in all three (ffmpeg: `lut3d=file.cube`). Apply **after** correction, at reduced strength.

### 5.3 Correction quick fixes (ffmpeg)
| Problem | Filter |
|---|---|
| Too dark / bright | `eq=brightness=0.04` or `eq=gamma=1.1` |
| Too blue / orange | `colortemperature=temperature=5500` (adjust) or `colorbalance` |
| Flat | `curves=preset=medium_contrast` |
| Over-saturated (phone) | `eq=saturation=0.9` |
| Banding in skies | `deband` + light `noise` |
| Shaky handheld | `vidstabdetect` → `vidstabtransform=smoothing=15` (two pass) |

### 5.4 Grading rules
- **Protect skin** (yours) and the **pets' natural colours.** Viewers notice orange skin or a green-tinted white rabbit instantly
- Grade with **scopes or measurements**, then confirm on a **phone at medium brightness**
- **Consistency within a Reel** beats a fancy look
- Low-light phone footage + heavy grade = noise and blocking after compression. **Grade gently** on dark footage

---

## 6. Cinematic camera language for your footage

| Shot | Meaning | Your use |
|---|---|---|
| Low angle, slow push-in | Power, hero | R15, Verna, the rabbit "hero/villain" entry |
| Eye-level with pets | Empathy, character | Pet Cast episodes |
| Extreme close-up | Detail, tension | DIY parts, villain eyes, clues |
| Wide static | Context, deadpan comedy | Fails, skits |
| POV (mount) | Immersion | Rides and drives (mounted only) |
| Over-the-shoulder | Story, perspective | You looking at the build or bike |
| Top-down | Process | DIY, gadget unboxing |

Digital camera moves in post (from a static 4K or 1080 shot): slow push-in 100→110% over the shot, a subtle drift (position keyframes), and zoom punches for comedy. ffmpeg uses frame-evaluated `scale` + `crop` 🧪. Avoid on 1080 sources beyond ~115% (softness).

---

## 7. Over-editing warning signs (remove if you see these)

- More than 2 designed transitions in a 15–30 s Reel
- A zoom on every cut
- SFX on every cut
- Slow-mo that isn't on a meaningful moment
- A grade that changes skin colour noticeably
- Text that repeats what's obvious on screen
- Effects that delay the payoff

**Related:** [04](04-professional-editing-techniques.md) · [21](21-professional-reels-editing.md) · [23](23-tamil-bgm-editing-guide.md) · [24](24-beat-sync-and-sound-design.md)
