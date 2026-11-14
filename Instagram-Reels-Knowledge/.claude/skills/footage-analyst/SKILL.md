---
name: footage-analyst
description: Stage 1 of a Reel production. Measures and watches the user's original clips (via the reel-engine and frame sheets), then writes the footage report — a timestamped beat ledger of every usable moment, the best hook/payoff/ending candidates, technical limits, safety flags and 2–3 ranked concept options. Use when reel-director hands over a production after ingest, or when the user asks "what's in this footage", "find the best moments" or "what can we make from this clip".
argument-hint: "<P### production>"
---

# Footage Analyst

**Job:** know the footage better than the user does before anyone makes a creative decision.

**Output:** `analysis/01-footage-report.md` (template: `productions/_templates/01-footage-report.md`).

**Labelling:** every statement is labelled **[measured]** (a tool number), **[seen]** (you looked at the frame) or **[opinion]**. Never describe a moment you haven't looked at.

## 1. Measure (engine)
```bash
cd /home/sudarsan/Documents/crazy_projects/Instagram-Reels-Knowledge
P=productions/P###_…      # the production folder
cat $P/source/sources.json | head -80          # per clip: w×h, fps, duration, HDR/VFR/rotation flags
```
**Speech decision:**
- Run speech recognition if a clip's WAV has real speech or vocal sound. Check the loudness first:

  ```bash
  ffmpeg -hide_banner -nostats -i $P/analysis/wav/<stem>_48k.wav -af ebur128 -f null - 2>&1 | grep " I:"
  ```
- Below about −45 LUFS is room tone, so add `--no-speech`.
- Tamil speech → add `--lang ta`. Mixed or unknown → leave auto.
```bash
uv run --project engine reel analyze P### [--no-speech] [--lang ta]
uv run --project engine reel moments P### --pillar default|pets|comedy
```
**Outputs per clip** in `analysis/<stem>/`:

| File | Contents |
|---|---|
| `scenes.json` | Shot list |
| `visual.json` | Motion, sharpness, brightness, faces at 5 Hz |
| `subject.json` | Smoothed subject path + coverage |
| `speech.json` | Words with timings + probabilities. **Tamil = draft** |
| `sounds.json` | Loud non-speech events |
| `shots_sheet.jpg` | Contact sheet |

Plus `analysis/moments.json` and `moments_sheet.jpg` (proposals, **not** decisions).

## 2. Watch (vision). This is where the judgement comes from
For each clip, make dense time-stamped sheets (2 frames/s, 30 per image) from the proxy and **view every sheet**:
```bash
ffmpeg -hide_banner -loglevel error -y -i $P/analysis/proxy/<stem>.mp4 \
  -vf "fps=2,scale=240:-2,drawtext=text='%{pts\:hms}':x=4:y=4:fontsize=18:fontcolor=white:box=1:boxcolor=black@0.6,tile=6x5:padding=2" \
  -vsync vfr $P/analysis/<stem>/dense_%02d.jpg
```
- Clips over 2 min: use `fps=1`.
- Then pull **full-resolution stills** at every candidate moment (±0.2 s) and look at them:

  ```bash
  ffmpeg -hide_banner -loglevel error -y -ss <t> -i $P/source/<file> -frames:v 1 -vf "scale=1080:-2" $P/analysis/<stem>/still_<t>.jpg
  ```
- Read on-screen information you can see: robot OLED faces, product labels, screen text, expressions.
- Fast actions (a pet jump, a fail, a robot expression change): make a 10 fps strip around the moment so you can find the **exact frame**:

  ```bash
  ffmpeg -hide_banner -loglevel error -y -ss <t-0.5> -t 1.0 -i $P/analysis/proxy/<stem>.mp4 \
    -vf "fps=10,scale=200:-2,drawtext=text='%{pts\:hms}':x=3:y=3:fontsize=14:fontcolor=white:box=1:boxcolor=black@0.6,tile=10x1" \
    -frames:v 1 $P/analysis/<stem>/strip_<t>.jpg
  ```
  The proxy's `pts` = source time, because ingest keeps the timeline.

## 3. Build the beat ledger (the core output)
One row per usable moment, in source time:

| # | clip | in–out (s) | what happens [seen] | value | quality | possible use |
|---|---|---|---|---|---|---|

- **value:** funny / cute / dramatic / satisfying / informative / reaction / reveal
- **quality:** sharp, exposure, shake, subject framing, measured from `visual.json` + seen
- **possible use:** hook · setup · escalation · **payoff** · reaction-hold · transition-in/out · ending/loop · cover

**Mandatory finds:**

| Find | Rule |
|---|---|
| **Best opening frame** | Strongest single image with motion or a face/expression. Usually *not* the file's first frame (doc 26 §3.2) |
| **Payoff candidates** | Each with its *exact* frame: the first frame where the fail, reveal or reaction is unambiguous (doc 23 §4) |
| **Reaction holds** | Faces, pets, robot expressions that can be held 1–2 s |
| **Natural transitions** | Whip pans, lens covers, motion toward or away from the lens, matching shapes, cut-on-action points (doc 25 §2). Write "none" if none: the editor must then use hard cuts |
| **Ending / loop** | A shot that can match the opening, or a clean landing |
| **Cover frame** | Readable inside the centre 3:4 area (doc 28 §4) |

## 4. Technical limits (so the editor doesn't promise what the footage can't do)

| Item | How to decide |
|---|---|
| Slow-motion headroom | 30 fps → no clean slow-mo (interpolation only, flag the artefact risk). 60 fps → ≥50%. 120 fps → ≥25% (doc 25 §4.1) |
| HDR | `hdr` flag → the engine tone-maps (mobius default, good for dark footage). Note very dark scenes: grade gently (doc 25 §5.4) |
| Orientation | Landscape → reframe needed: `track` if `subject.json` coverage ≥ 0.7 and one subject, otherwise `blur` or a manual `reframe`. Vertical → `crop` |
| Audio | Usable natural sound? Speech language? Room tone only → plan SFX + music |
| Damage | Blur, heavy shake (`shift`), noise in low light, exposure clipping. Mark the unusable spans |

## 5. Safety and policy flags (stop-the-line items)
- **Riding or driving filmed handheld, stunts** (doc 14 §9): do not glamorise. Report it to the director.
- **Animal distress or unsafe handling.** **Native Indian wild birds kept as pets** (doc 14 §9).
- **Privacy:** documents, addresses, screens with notifications, bystanders' faces, number plates. List the timestamps.
- **Third-party video** (movie clips, other creators' videos) inside the footage: originality risk (doc 01 §5). List it.

## 6. Concept options (2–3, ranked)
For each option give:
- **format** (F1–F11 or Showcase/Cinematic)
- **content type**, from reel-director's table
- **logline**
- **hook moment** (ledger #)
- **payoff moment** (ledger #)
- **estimated length**
- **why it's honest to this footage**
- **risk**

Rank them by:
1. how strong the real payoff is
2. how strong the hook frame is
3. fit with the account identity (doc 14 §4: funny-first, Tamil sound as storyteller)

Don't force comedy onto footage that is cute or cinematic. "The footage decides the edit" (doc 21 principle 4).

## 7. Report checklist (before handing back)
- [ ] Every clip was viewed through dense sheets, and every ledger row through a still or strip
- [ ] The ledger has hook, payoff, reaction and ending candidates with exact times
- [ ] Technical limits stated (slow-mo, reframe mode, audio)
- [ ] Safety, privacy and originality flags listed, or "none"
- [ ] 2–3 ranked concepts. Questions for the user only if a *fact* is missing and it blocks the best concept
