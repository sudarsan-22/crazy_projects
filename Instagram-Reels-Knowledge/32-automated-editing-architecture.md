# 32 — Automated Editing Architecture (v0 tools → v1 "reel-engine")

> **Phase 3b · Technical infrastructure** · Created 2026-11-07 · **Design document. No new code written yet** (build order in [34](34-tool-integration-plan.md#3-build-milestones))
> Evidence tags: ✅ Official · 🟡 Reported · 🔵 Practitioner · ⚠️ Theory · 🧪 Tested here
> This is the software design behind [26 — Video Production Workflow](26-video-production-workflow.md), which runs in **Autonomous Mode** by default: you upload footage, Claude makes every creative and technical decision, and you review the finished Reel. It **extends the working v0 tools** rather than replacing them, using the stack chosen in [29](29-video-processing-tool-comparison.md) and [30](30-audio-analysis-tool-comparison.md) and the audio rules in [31](31-instagram-audio-research-methods.md).

---

## 1. Starting point: v0 already works

| v0 component (stdlib Python + FFmpeg) | Does | Gap that v1 closes |
|---|---|---|
| [tools/analyze_reel.py](tools/README.md) 🧪 | Specs, loudness, cuts (`scdet`), black frames, hook frames, safe-zone overlays, contact sheet, cut strips | No pass/fail rules against a plan. No speech, subject or motion features |
| [tools/audio_beats.py](tools/README.md) 🧪 | Tempo, beat grid (±18 ms on clicks), hits, drop | No downbeats or phrases. A fixed grid breaks on tempo changes |
| [tools/reel_render.py](tools/README.md#reel_renderpy--render-a-finished-reel-from-an-edl) 🧪 | **EDL → one-pass render**: segments, speed, crop/blur fit, grades, zoom, punches, shakes, freeze, `xfade`, ASS text, SFX, music + ducking, two-pass loudness, HDR tone-map | Static crop focus (`focus_x`). **Stepped** ramps. No schema validation. No marker-based sync. Times are written by hand |
| `assets/sfx/` (13 synthesised SFX, `tools/make_sfx_kit.sh`) 🧪 | Licence-free SFX | No `peak_offset` metadata, so peak alignment is manual |
| `productions/P###_…/` + `_templates/` | Folder convention and report templates | No machine-readable state |
| Claude Code + doc 26 SOP | Autonomous decisions, QC by frame review | The QC → fix loop is manual and judgement-only |

**v1 principle: additive.** Every v0 script keeps working without the venv. v1 adds an analysis layer, a validated and versioned EDL, a sync resolver, automated QC and a correction loop.

---

## 2. Design principles

1. **Claude decides, code executes.** Scripts measure and render. Creative choices are written by Claude into the **EDL** with reasons in `plan/decisions.md`, never hidden inside heuristics.
2. **Autonomous by default ([26](26-video-production-workflow.md#-autonomous-mode-the-default-since-2026-11-07)).** No approval waits. You review the finished Reel. "Plan-first" mode (doc 26 Gates 1–3) stays available on request.
3. **Everything is a file** in the production folder. Any step can be inspected, re-run or diffed.
4. **One encode from the originals** for the final ([26 §6](26-video-production-workflow.md#6-stage-4--production) technical rules). Drafts may use cached *lossless* intermediates.
5. **Honest outputs.** *Measured*, *opinion* and *unverified* labels. **Tamil-script text is flagged** in the delivery note for your check before posting, because ASR and Claude's Tamil spelling can be wrong ([23 §6](23-tamil-bgm-editing-guide.md#6-subtitles-for-tamil-audio), [30 §2.5](30-audio-analysis-tool-comparison.md#25-whisper-family--selected-faster-whisper)).
6. **Adapters.** One module per external tool, each with a fixed JSON output.
7. **Never publishes, never engages.** Delivery ends at `publish/`. You post.

---

## 3. System overview (autonomous loop)

```
 productions/inbox/clip.mp4
        │
        ▼
 INGEST ─► ANALYSE ───────────────► PROPOSE MOMENTS ─► AUDIO (select + markers)
 probe,    scenes (PySceneDetect)    scored windows      doc 27 scoring, ref audio optional,
 VFR/HDR   visual (PyAV+OpenCV)      + thumbnails        Beat This!/librosa → H B D S A E
 copy      subject path (YuNet)                                  │
           speech (faster-whisper)                               ▼
           sounds (peaks, YAMNet)              CLAUDE writes build/edl.json  (creative direction)
                                                                 │
                                   ┌──────── VALIDATE + RESOLVE (markers → frames, sync, safe zone)
                                   ▼
                               RENDER (reel_render core, FFmpeg) ─► QC (measure + rules + evidence images)
                                   ▲                                   │
                                   └──── Claude revises edl vN+1 ◄─────┘  (≤ 3 rounds)
                                                                       │ pass
                                                                       ▼
                                          DELIVER publish/FINAL.mp4 + 04-publish-package.md → YOU review & post
```

---

## 4. Code and folder layout

The KB folder is already the project root (it holds `tools/`, `assets/` and `productions/`), so v1 lives **inside it** in a self-contained `engine/` folder:

```
Instagram-Reels-Knowledge/
├── tools/                      # v0 scripts. Stay stdlib, stay runnable
├── assets/  sfx/ (+ sfx.json sidecars, v1) · fonts/ (optional brand fonts) · models/ (YuNet) · luts/ · LICENSES/
├── productions/P###_…/         # one folder per Reel (doc 26)
└── engine/                     # NEW (after approval)
    ├── pyproject.toml  uv.lock  .venv/          # doc 33
    ├── CLAUDE.md                                 # operating rules: autonomous mode, honesty labels, never bake library audio, never publish
    ├── reelengine/
    │   ├── cli.py              # `reel <command> <production>`
    │   ├── config.py           # canvas, loudness, safe zones, brand styles ← KB docs (34 §2)
    │   ├── state.py            # production.json (stages, versions, tool versions, timings)
    │   ├── ingest.py           # copy from inbox, hash, probe, proxy (540×960 CFR SDR), 48 kHz WAV
    │   ├── analysis/  scenes.py · visual.py · subject.py · speech.py · sounds.py · music.py
    │   ├── moments.py          # proposals (not decisions)
    │   ├── edl/  schema.py (pydantic, edl/1 + edl/2) · resolve.py · validate.py · macros.py · otio_export.py
    │   ├── render/  (wraps then absorbs tools/reel_render.py: smooth ramps, track fit, text items, draft cache)
    │   ├── qc/  checks.py · evidence.py (reuses analyze_reel.py) · compare.py
    │   └── package.py          # publish/04-publish-package.md from the template
    └── tests/  fixtures/ (synthetic clips with known cuts, beats, loudness) · golden/ (per-macro renders)
```

**Stage outputs mapped onto doc 26's production folder:**

| Folder | v0 content | v1 adds |
|---|---|---|
| `source/` | Copied originals (never modified) | `sources.json` (sha256, probe summary) |
| `analysis/` | analyze_reel metrics, frames, `01-footage-report.md` | `proxy_*.mp4`, `scenes.json`, `visual.json`, `subject_*.json`, `speech.json`, `sounds.json`, `moments.json`, `moments_sheet.jpg` |
| `audio/` | Reference copies (timing only), `02-audio-options.md` | `audio_candidates.json` ([31 §4](31-instagram-audio-research-methods.md#4-the-audio-record-machine-readable-used-by-the-engine)), `music.json`, `beats_plot.png` |
| `plan/` | `03-edit-plan.md` | `decisions.md` (finding → choice → reason, per version) |
| `build/` | `edl.json`, `text.ass` | `edl.vN.json` history, `edl.resolved.vN.json`, `graph_vN.txt`, `render_vN.log`, `qc_vN.json`, `qc_vN/` evidence images |
| `renders/` | `vN_syncguide.mp4`, `vN_clean.mp4` | `vN_draft.mp4` (540×960) |
| `publish/` | `FINAL.mp4`, cover, `04-publish-package.md` | — |
| *(root)* | — | `production.json` (state machine) |

---

## 5. Stage contracts

| # | Command (v1) | Reads → writes | Tools |
|---|---|---|---|
| 1 | `reel ingest <inbox-file\|P###>` | inbox → `source/`, `sources.json`, proxy, WAV | ffprobe, FFmpeg |
| 2 | `reel analyze P###` | proxy, WAV → `analysis/*.json` + contact sheets | PySceneDetect, PyAV, OpenCV/YuNet, faster-whisper (+VAD), [YAMNet] |
| 3 | `reel moments P###` | analysis → `moments.json`, `moments_sheet.jpg` | NumPy |
| 4 | `reel audio P### [--ref file --start 41.3 --rights in_app_library]` | candidates + optional reference → `music.json`, markers | Beat This!, librosa (fallback: audio_beats.py) |
| 5 | *Claude writes* `build/edl.json` (+ `plan/03-edit-plan.md`, `decisions.md`) | everything above | — |
| 6 | `reel validate P###` | EDL → resolved EDL or readable errors + required shifts | pydantic |
| 7 | `reel render P### [--draft]` | resolved EDL → `renders/vN_*.mp4`, `graph_vN.txt` | FFmpeg |
| 8 | `reel qc P###` | render + resolved EDL → `qc_vN.json` + evidence images | ffprobe, FFmpeg detectors, OpenCV, analyze_reel.py |
| 9 | *Claude revises* → `edl.v(N+1).json` | QC findings | — (§9 loop) |
| 10 | `reel package P###` | final EDL + audio record → `publish/` | — |
| — | `reel run P###` | stages 1–4, then pauses for Claude to write the EDL | — |
| — | `reel doctor` | environment check ([33 §8](33-environment-setup-guide.md#8-verification-smoke-test)) | — |

### 5.1 Moment proposals (inputs to Claude, not decisions)
Each 0.5 s window: `score = Σ wᵢ·featureᵢ − penalties`, with weights per pillar in `config.py`.
- **Features:** non-speech loudness spikes (laughs, shouts, rabbit thumps, engine revs), speech plus transcript words, motion-energy peaks, face presence, face size or a turn to camera, scene starts.
- **Penalties:** blur (Laplacian variance), bad exposure, heavy shake, subject leaving the crop.
- **Output:** the top ~12 windows with timestamps, reasons and thumbnail strips. Claude chooses and writes *why*. A high score isn't evidence that a moment is funny.

---

## 6. The EDL contract (backward-compatible extension of v0)

`edl/1` = today's reel_render.py format (see the [tools/reel_render.py](tools/reel_render.py) docstring). Every v1 key is optional, so **v0 EDLs stay valid**.

| New in `edl/2` | Meaning |
|---|---|
| `"schema": "edl/2"` | Version tag |
| `"speed": {"ramp": [from, to]}` | **Smooth** closed-form ramp ([29 §4.6](29-video-processing-tool-comparison.md#46-speed-ramp--smooth-not-stepped)). A plain number keeps v0 behaviour |
| `"fit": "track"` + `"track": "<subject_*.json>"` | Crop follows the smoothed subject path ([29 §4.3](29-video-processing-tool-comparison.md#43-916-vertical-conversion)) instead of a fixed `focus_x` |
| `"markers"` | `{"H":…, "D":…, "S":…, "E":…}` in video seconds (video 0.0 = in-app audio start point) |
| `"sync"` | Constraints like `{"event": "seg2.freeze_start", "marker": "D", "flex": "seg1.in"}`. The validator reports or applies the shift at `flex` |
| `"components"` | Signature macros S1–S6 (§6.2) |
| `"text"` | Text items (style, content, timing, `needs_check` for Tamil). The engine generates the ASS, and a hand-written `"ass"` file still works |
| `"sfx[].at": "marker:D"`, `"align": "peak"` | Peak-aligned SFX using `peak_offset_ms` from `sfx.json` ([30 §3.8](30-audio-analysis-tool-comparison.md#38-sound-effect-placement)) |
| `"audio_rights"` | `in_app_library` / `sound_collection` / `own_recording` / `licensed_file` ([31 §4](31-instagram-audio-research-methods.md#4-the-audio-record-machine-readable-used-by-the-engine)) |

### 6.1 Example (`edl/2`)
```json
{
  "schema": "edl/2", "fps": 30, "width": 1080, "height": 1920, "crf": 17,
  "loudness_lufs": -16, "audio_rights": "in_app_library",
  "output": "../renders/v2_clean.mp4",
  "markers": {"H": 0.0, "D": 7.52, "S": 11.80, "E": 15.0},
  "segments": [
    {"id": "seg1", "src": "../source/S1.mp4", "in": 9.613, "out": 15.10, "speed": 1.0,
     "fit": "track", "track": "../analysis/subject_S1.json", "grade": "moviemode", "audio": "keep"},
    {"id": "seg2", "src": "../source/S1.mp4", "in": 15.10, "out": 16.20, "speed": {"ramp": [1.0, 0.25]},
     "fit": "track", "track": "../analysis/subject_S1.json", "grade": "moviemode", "audio": "mute",
     "freeze_end": 1.2},
    {"id": "seg3", "src": "../source/S2.mp4", "in": 3.00, "out": 9.28, "speed": 1.0,
     "fit": "crop", "focus_x": 0.5, "grade": "reality", "audio": "keep"}
  ],
  "sync": [{"event": "seg2.freeze_start", "marker": "D", "flex": "seg1.in"},
           {"event": "end", "marker": "E", "flex": "seg3.out"}],
  "components": [
    {"macro": "S1_name_card", "at": "seg2.freeze_start", "dur": 1.2, "text": "RABBIT — THE VILLAIN"},
    {"macro": "S3_bruh_sting", "at": "marker:S"},
    {"macro": "S4_episode_tag", "text": "PET CAST #03"}
  ],
  "text": [{"style": "caption_ta", "text": "என்ன டா இது?", "start": 12.6, "end": 14.0, "needs_check": true}],
  "sfx": [{"file": "assets/sfx/impact_hit.wav", "at": "marker:D", "align": "peak", "gain_db": -3}]
}
```
**How it resolves:** seg1 plays 5.487 s. The seg2 ramp turns 1.1 s of source into 1.1 / (−0.75) · ln 0.25 = 2.033 s, so the freeze starts at **7.520 s = D** ✅ and holds to 8.72 s. seg3 plays 6.28 s, so the Reel ends at **15.00 s = E** ✅. The bruh sting fires at S = 11.80 s inside seg3.

### 6.2 Signatures as macros (from [16 §1](16-editing-identity-and-reel-formats.md)). They expand into v0 primitives
| Macro | Expands to |
|---|---|
| `S1_name_card` | `freeze_end` + display-font ASS card (`#FFC400`, slide-in about 6 frames) + impact SFX on the hit |
| `S2_bgm_switch` | Planned 0.3–0.5 s silence before S ([15 §2.2](15-tamil-music-and-audio-strategy.md#22-the-bgm-switch-expectation--reality)) + grade switch + optional `scratch_stop.wav` |
| `S3_bruh_sting` | `punches` (6–8 frames) + `shakes` + brief desaturation + the bruh SFX |
| `S4_episode_tag` | Small corner label, inside the safe zone, for the whole Reel |
| `S5_two_tone` | `moviemode` → `reality` grade at S |
| `S6_captions` | Caption style from [21 §6](21-professional-reels-editing.md#6-text--subtitle-production-standard) |

### 6.3 Validation (`reel validate`)
- Schema. Files and fonts exist. `in < out ≤ source duration`. Total ≤ 180 s (recommendation eligibility, [01](01-instagram-algorithm.md)) and within the format's target.
- `xfade` durations shorter than both neighbours. Offsets computed by the resolver.
- **Sync:** every constraint within ±1 frame after frame quantisation (`round(t·fps)/fps`). Otherwise apply or report the shift at `flex`.
- **Text:** layout inside the [07 §2](07-instagram-seo-and-optimization.md#2-safe-zones) safe zone. Minimum on-screen time (configurable reading-pace rule 🔵).
- **Rights:** if `audio_rights == in_app_library`, only `syncguide` outputs may contain the reference audio.
- **Ramps and slow-mo:** source fps is high enough for the slowest speed, otherwise `interpolate` is required and flagged for an artefact check.

---

## 7. Renderer

- **Core = reel_render.py's single-pass graph** (already tested 🧪). v1 adds:
  - the closed-form ramp in `setpts` 🧪
  - the `crop` x(t) path from `subject_*.json` 🧪
  - macro expansion
  - generated ASS from `text` items
  - `graph_vN.txt` saved for every render
- **Outputs:** `vN_draft` (540×960, fast), `vN_clean` (≈ −16 LUFS, no library music), `vN_syncguide` (review only, never uploaded), `vN_final` (only when music may be baked in, −14 LUFS). Encode settings per [28 §1](28-reels-export-and-publishing.md#1-export-settings-by-tool) and [29 §4.10](29-video-processing-tool-comparison.md#410-rendering-presets).
- **Draft cache (optional, only if drafts get slow):** per-segment FFV1 lossless intermediates keyed by sha256 (source hash + segment JSON + engine version). **The final always re-renders in one pass from the originals.**

---

## 8. QC checks

`reel qc` measures the **rendered file** and writes `qc_vN.json` with `pass / warn / fail` per rule.

| Area | Rule | Measured with | Severity |
|---|---|---|---|
| Spec | 1080×1920, planned CFR fps, H.264 High, yuv420p, AAC 48 kHz stereo, faststart | ffprobe | fail |
| Duration | Resolved EDL duration ±1 frame. ≤ 180 s | ffprobe | fail |
| Loudness | Integrated within ±1 LU of target (−16 clean / −14 baked). True peak ≤ −1.0 dBTP | `ebur128`, pyloudnorm | fail → **auto-fix** |
| Black / freeze | No `blackdetect` hits. `freezedetect` only inside planned freezes | FFmpeg detectors | fail / warn |
| Silence | No unplanned gap > 0.6 s. The planned pre-switch silence is present | `silencedetect` | warn |
| Hook | First frame not black. Audio starts ≤ 0.1 s. Visual change or text in the first second ([05](05-hooks-and-storytelling.md)) | analyze_reel.py | warn |
| **Sync** | Measured cut and freeze times vs markers: **D within ±1 frame**, downbeat cuts within ±2 frames | `scdet` on the render vs the resolved EDL | fail (D) / warn |
| **Text safe zone** | Text layer rendered alone on a transparent canvas → OpenCV alpha bounding box per item, inside the safe zone | FFmpeg + OpenCV | fail |
| **Rights** | `clean`/`FINAL` audio doesn't correlate with the reference music | NumPy cross-correlation | fail |
| Reframe | Subject centre inside the crop for ≥ 95% of tracked frames | subject path vs crop path | warn |
| Pacing | Shot lengths and cuts per 10 s vs the format's target ([16](16-editing-identity-and-reel-formats.md)) | EDL + `scdet` | info |
| Tamil text | Every `needs_check` item listed in the delivery note | EDL | info (for you) |

**Evidence images for Claude** (Claude reviews images and can't *watch* video): the contact sheet, hook frames with the safe-zone overlay, 7-frame strips at each cut, frames from ramped and interpolated spans (smearing), caption frames, and a **sync plot** (music energy + beat and downbeat ticks + markers + *measured* cut lines).

---

## 9. Correction loop (autonomous)

```
qc_vN.json → each finding is
  AUTO    loudness, spec, sync off by ≤2 frames with a declared flex → engine fixes → re-render
  CLAUDE  text in an unsafe area, subject cut off, ramp smear, dead air, flat pacing
          → edl.v(N+1).json + decisions.md entry ("finding → change → reason")
  REPORT  anything still subjective after 3 rounds, or anything only playback can judge
          (comedic timing, lip-sync feel) → listed in the delivery note as "check this"
```
At most **3 automatic rounds** per delivery. Drafts first, the final only after the draft passes. Every version stays on disk. Your feedback after delivery starts the next version, as in doc 26 §7.

---

## 10. How Claude operates it

| Aspect | Design |
|---|---|
| Runtime | **Claude Code** in the KB folder runs `uv run --project engine reel …`, reads JSON, views evidence images and writes EDLs. **No API key or subscription** |
| Rules | `engine/CLAUDE.md` + doc 26: autonomous by default, honesty labels, Tamil text flagged, library audio never baked in, never publishes, asks before installing anything new |
| Optional later | A project skill `/edit-reel` that walks the SOP. A headless Claude Agent SDK runner for batch analysis of the inbox |
| State | `production.json`: `ingested → analyzed → audio_selected → planned → rendered(vN) ⇄ qc(vN) → delivered → posted (you) → audited (72 h / day 7, doc 26 §9)` with timestamps, tool versions and wall times (they feed the [34 §6](34-tool-integration-plan.md#6-performance-log) performance log) |

## 11. Robustness and tests
- `subprocess` with argument lists and timeouts. stderr goes to `render_vN.log`, and the last 30 lines are surfaced on failure.
- Inputs are normalised (fps, SAR, pixel format, 48 kHz) before `concat`/`xfade`.
- Synthetic fixtures with known cuts, beats, black frames and loudness (the method that validated analyze_reel.py and audio_beats.py 🧪). A golden render per macro. Every v0 EDL in `productions/` re-renders identically after each renderer change.

## 12. Extending
- **Format** (F1–F11) = an EDL template with slots, macros and pacing targets.
- **Signature** = a macro + a golden test.
- **Analysis tool** = a new adapter writing a new JSON file. Nothing downstream changes until a scorer or QC rule reads it.

**Related:** [26 SOP](26-video-production-workflow.md) · [29](29-video-processing-tool-comparison.md) · [30](30-audio-analysis-tool-comparison.md) · [31](31-instagram-audio-research-methods.md) · [33 Setup](33-environment-setup-guide.md) · [34 Integration plan](34-tool-integration-plan.md)
