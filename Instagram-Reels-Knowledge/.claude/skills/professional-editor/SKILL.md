---
name: professional-editor
description: Stage 3 of a Reel production. Turns the creative brief, beat ledger and audio plan into a frame-exact edit — writes build/edl.json (edl/2) with shot selection, order, timing, speed ramps, reframing, transitions, typography, colour grade, SFX and sync constraints — then renders and self-checks it with the reel-engine (`reel validate` / `reel deliver`). Also applies the quality-reviewer's fix lists. Use when reel-director hands over a brief + audio plan, or when a review returns REJECT.
argument-hint: "<P### production> [fix list from review]"
---

# Professional Editor

**Output:** `build/edl.json`, the completed `plan/03-edit-plan.md`, a `plan/decisions.md` entry, and rendered versions.

**Principle:** every element has one job (hook, clarity, rhythm or payoff). Anything without a job is removed (doc 21 §1).

## 1. Write the cut list on paper first (in `03-edit-plan.md` §3)
From the brief's spine and the ledger, one row per segment:

| # | out time | source clip @ in–out | speed | why this shot (job) | transition in | text | SFX | grade | sync |
|---|---|---|---|---|---|---|---|---|---|

### Selection rules
- **Hook (0–1 s):** the ledger's best opening frame, mid-action. Text hook ≤ 8 words on screen from frame 1 (≤ 0.1 s). No intro, logo or fade-in (doc 05 §2).
- **Setup:** only as long as needed to make the expectation clear (≤ 2–4 s for comedy, doc 25 §1). Cut every frame that repeats information.
- **Payoff:** the ledger's exact payoff frame. **Hold after the hit:** ≥ 0.6 s before the next cut (1–2 s for a reaction hold).
- **Ending:** loop back to the hook image, a reaction hold, or a verdict/end card. The final shot is never the shortest one.

### Rhythm rules
These are what separates professional from "AI-edited". Sources: doc 16 §6, doc 25, github-video-editing-skills-research.md §5.
- **Vary shot lengths.** If every shot is within ±15% of the same length, it's monotone. Re-plan.
- **Accelerate into the climax** (e.g. 2.0 → 1.6 → 1.2 → 0.8 s), then **hold** the payoff.
- The contrast in pace *is* the comedy: a committed slow setup, then an instant switch.
- Cut on action (a movement in progress hides the cut). Never cut on the *peak* of a gesture.
- Cut 0–1 frame before a beat for a perceived on-beat cut (doc 24 §2). Use `early_frames` in `sync`.
- **One punchline per Reel** (+ optional tag). Don't explain the joke in text.

### Transitions
- Hard cuts by default.
- **≤ 2 designed transitions per Reel**, and only at section changes (doc 25 §2).
- Whip/slide only where the footage has a real whip. Dissolves only for emotional or romantic beats.
- Zoom punches for emphasis, never on every cut (doc 25 §7).

### Speed

| Situation | Rule |
|---|---|
| Source fps limits | Doc 25 §4.1. On 30 fps sources keep speed ≥ 1.0 unless `interpolate: true` (then the reviewer must check smearing) |
| **Hero ramp** (doc 25 §3.1) | Three segments of the same clip: `{"ramp": [1.0, 0.35]}` → constant `0.35` hold on the hero moment → `{"ramp": [0.35, 1.0]}` |
| Montage ramp | Mirror it: `[2.5, 0.5]` → `[0.5, 2.5]` |
| Ramp audio | Ramp segments are automatically muted. Cover them with SFX/music (whoosh *into* the slow part, impact *at* the hero frame) |

### Reframing (vertical 1080×1920)

| Source | `fit` |
|---|---|
| Vertical source | `"fit": "crop"` (+ `focus_x/y` to place the subject) |
| Landscape, one moving subject, coverage ≥ 0.7 | `"fit": "track"`. Subject path from analysis (smooth ramps and tracking are pre-rendered losslessly) |
| Landscape, whole frame matters | `"fit": "blur"` |
| Punch into a region of 4K | `"reframe": [x, y, scale]` (fractions, applied before scaling). Don't push 1080p sources beyond ~115% |

### Typography (doc 21 §6, safe zone = CLAUDE.md)
- **Styles:** `hook` (upper third), `caption` (lower middle), `caption_ta` (auto for Tamil script), `card` (yellow name card), `sub`, `tag` (series, top-left), `bruh` (red stamp).
- **Animations:** `pop` (default), `slide_in`, `stamp`, `fade`, `none`.
- **Reading time:** ≥ max(1.0 s, 0.33 s × words + 0.5 s), except stamps and tags. ≤ 2 lines, ≤ 42 characters per line.
- Highlight ONE punch word (`"punch": "word"`). Text never repeats what's obvious on screen.
- Tamil script only when it is the joke. It's set `needs_check` automatically and flagged to the user.

### Colour (doc 25 §5)
- **Grades:** `moviemode` (dramatic setup), `reality` (after the switch), `cozy` (warm: robots, cute, home), `none`, or a raw FFmpeg chain (`eq`, `colorbalance`, `curves`, `lut3d`).
- HDR is tone-mapped automatically (`"tonemap": "mobius"` default; `"hable"` for more contrast on bright footage).
- **Consistency within a scene** beats a fancy look. Protect skin, fur, feathers and product colours. Grade dark footage gently.

### Signatures (doc 16 §1). Use ≥ 3 per Reel only where they serve the story; never forced
`components`:
- `S1_name_card` `{at, dur, text, sub?}`
- `S3_bruh_sting` `{at, text?:"" to disable}`
- `S4_episode_tag` `{text}`
- `S5_two_tone` `{at, before, after}` (overrides all segment grades)
- `S2_bgm_switch` `{at, silence}`. **Note:** S2 adds the scratch SFX + grade switch but does **not** silence natural audio. Split the segment and set `"audio": "mute"` on the 0.3–0.5 s before the switch.

## 2. Write `build/edl.json` (edl/2)
Start from `engine/tests/example_edl2.json` (a verified, working example). Rules:

| Topic | Rule |
|---|---|
| `src` paths | Relative to `build/`, e.g. `"../source/IMG_7191.MOV"` |
| Segments | Every segment gets an `id` and a `note` (its job) |
| `markers` | From the audio plan. Video 0.0 s = audio start point |
| `sync` | `{"event": "seg4.freeze_start" or "seg5.start" or "end", "marker": "D", "flex": "seg3.in"}`. The engine solves `flex` exactly. Flex an edge that *can* move (`in`, `out`, `freeze_end`, constant `speed`) |
| `sfx` | `{"file": "assets/sfx/impact_hit.wav", "at": "marker:D", "align": "peak", "gain_db": -6}` |
| `audio_rights` | From the audio plan |
| `reference_audio` | `{"file": "../audio/<ref>", "start": 0}`. Only when a reference exists. Produces a `syncguide` render (never uploaded) |
| Baked music (Path C) | `"music": {"file": "../audio/<score>.wav", "start": 0, "gain_db": -3, "duck": true}` + `audio_rights: "own_recording"` / `"licensed_file"` |
| `cover_at` | Event/time of the cover frame |
| `caption` | `{title, text, hashtags (≤5), keywords, trial, audio: {name, start, volume, sync_note, credit, evidence}}`. Hashtags: 1–2 topic + 1–2 community + 0–1 series (doc 28 §5) |

## 3. Validate, render, self-check
```bash
uv run --project engine reel validate P###     # resolved timeline, sync solutions, macros, text, PROBLEMS
uv run --project engine reel deliver P###      # render → engine QC → auto-fix (loudness, unsafe text) ≤3 rounds → publish/
```

**Fix every `PROBLEM`** and any `NOT SOLVED` sync before rendering.

If `deliver` stops with "needs an EDL change", read `build/qc_vN_clean.md`, fix the EDL, and run `deliver` again.

**Self-check before review:** look at these evidence images yourself (don't hand obviously broken work to the reviewer):
- `build/qc_vN_clean/analyze/contact_sheet.jpg`
- the hook frames
- `text/*.jpg`

### Dual deliverable (Path A + Path C), when the audio plan asks for both
1. Copy `build/edl.json` → `build/edl_music.json`.
2. Set `audio_rights` + `music` in the copy.
3. Run:

   ```bash
   uv run --project engine reel render P### build/edl_music.json --variants final
   uv run --project engine reel qc P### --variant final
   ```
4. The director copies that render to `output/…_FINAL_with_music.mp4` (the engine packages only one version).

## 4. Applying a review fix list
- Map every numbered fix to a concrete EDL change.
- Record each one in `plan/decisions.md` as "fix # → change → why".
- Change only what the fix requires. Re-render with `reel deliver P###` (new version; old versions stay).

## 5. Fallback (engine unavailable)
Write an edl/1 file (the format in the `tools/reel_render.py` docstring) and run:

```bash
python3 -I tools/reel_render.py build/edl_v0.json
python3 -I tools/analyze_reel.py <out.mp4> build/qc_v0/
```

This loses: smooth ramps (use stepped speed segments), tracking, macros, sync solving, generated text (write ASS by hand like `productions/P001_*/build/text.ass`), and engine QC.
