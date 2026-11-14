# 36 — Reel-Engine Upgrade Plan (Stage 2, awaiting approval)

> **Status: PROPOSAL. Nothing implemented.** Created 2026-11-08 from the audit and benchmarks in [35](35-github-editing-skills-comparison.md).
> Principles: **improve, don't rebuild.** Additive milestones (U1–U8) on top of doc 34's M0–M7. `tools/reel_render.py` (v0) keeps working. Every change ships with tests. CPU fallback always. No new agents. No new Python packages (everything below uses FFmpeg + numpy/soundfile already in the engine venv). Previous productions and deliverables are untouched.

---

## 1. What changes and why (one line each)

| ID | Change | Fixes (evidence) | Source adapted | Effort |
|---|---|---|---|---|
| **U1** | **Fast HDR prep:** scale/reframe to 1080×1920 in 10-bit *before* tone-mapping | 2.1× faster prep, SSIM 0.9977 vs current 🧪 (35 §7 A6) | ours | S |
| **U2** | **NVENC encode path** with auto-detect + CPU fallback | 3.3× faster final at equal SSIM 🧪. Lossless intermediates | ours (benchmarked settings) | S |
| **U3** | **Audio seam fades + J/L cuts** (`audio_lead`) + frame-grid quantisation | CLAUDE.md gap 5. Clicks at joins. Abrupt butt cuts | agamm `_edl_audio_windows`, `_edl_achain`, `_edl_quantize` (MIT) | M |
| **U4** | **Motion quality:** smooth zoom/punch (no 2-px stepping), shake ≤ 10 Hz | Stair-stepping on slow push-ins. 12.9 Hz shake aliasing (35 §6) | agamm `_edl_vchain` idea (MIT); sunithvs rule (Apache) | S |
| **U5** | **QC v2:** rhythm report, reading time/chars per line, A/V sync vs source, frame count, grade consistency + noise, text-over-subject, SFX repetition/duplicates, limited-range assert | CLAUDE.md gap 4. P002 C6/C7/C8/C9 | agamm `edl_report`; sunithvs `verify.py`; saucetech signalstats QA | M |
| **U6** | **Audio intelligence:** beat tempo prior, `reel snap` (beats/silence) with a move report, SFX library QA + variant rotation, denoise-latency compensation | Half-tempo errors. P002 C9. Doc 24 §7 latency | agamm `beats`, `snap_edl`; saucetech `qa_sfx.py`; sunithvs `latency()` | M |
| **U7** | **Iteration speed:** `reel stills` (render chosen frames through the real graph) + `reel report` (pacing, no render) | Each review currently needs a ~2 min full render | Melvynx idea; agamm `--report --dry-run` | S |
| **U8** | **Deliverables:** Trial-Reel hook variants, editor kit (stems + FCP7 XML for Resolve), brand fonts via `fontsdir`, HALD-LUT grades, cover title text, score generator as an engine module | KB 02 §5 testing. CLAUDE.md gaps 2/6/7 | sunithvs `variants`, `xmeml.py` (Apache); agamm `grade_gen_lut` (MIT) | M–L |

Effort: S ≈ half a day, M ≈ 1 day, L ≈ 2 days of agent work including tests.

**Recommended approval order:** U1 → U2 → U3 → U4 → U5 → U7 → U6 → U8. The first four are the biggest quality and speed gains with the lowest risk.

---

## 2. Detailed design per milestone

### U1 · Fast HDR prep (CPU)
- **Where:**
  - `tools/reel_render.py`: per-segment chain order (HDR branch only).
  - `engine/reelengine/edl/compile.py` `prep_segment` (ramp/track prep).
- **Change:** for HDR sources:

  ```
  trim → setpts → [reframe crop] → fps → scale/crop to 1080×1920 (format=yuv420p10le, lanczos) → tone-map (zscale…mobius) → grade → …
  ```

  The current order is `tone-map@4K → … → scale`. Tracked crops keep their x-expression (evaluated before the scale). Zoom stays after the fit.
- **Guard:** an EDL key `"prep_order": "fast"` (the default for new EDLs). `"legacy"` reproduces the old order exactly, which keeps v0 EDLs byte-identical when requested.
- **Tests:**
  - (a) Synthetic HLG fixture (10-bit, `arib-std-b67` tagged): new vs legacy SSIM ≥ 0.995.
  - (b) Wall-time ratio ≤ 0.7 on a 4K fixture.
  - (c) The old v0 EDL regression hash is unchanged with `legacy`.
- **Risk:** scaling in the non-linear HLG domain softens fine highlight edges very slightly (measured PSNR 54 dB = invisible). Accepted.

### U2 · NVENC with CPU fallback
- **Where:** new `engine/reelengine/hw.py` (detection + encoder argument builder). Used by `tools/reel_render.py` through an env/EDL switch, and by `deliver.py`.
- **Detection (cached per session):** `nvidia-smi` present **and** a 1-frame `h264_nvenc` test encode succeeds → `gpu=true`. Otherwise CPU.
- **Final encode (GPU):**

  ```
  -c:v h264_nvenc -preset p7 -tune hq -rc vbr -cq 24 -b:v 0 -maxrate 40M -bufsize 80M
  -spatial-aq 1 -temporal-aq 1 -rc-lookahead 32 -bf 3 -b_ref_mode middle -profile:v high -pix_fmt yuv420p
  ```

  **`maxrate` is mandatory: without it CQ is ignored** 🧪.
- **Intermediates (GPU):** `h264_nvenc -preset p7 -tune lossless`. CPU: x264 veryfast CRF 8 (current).
- **Drafts:** `h264_nvenc -preset p4 -cq 28 -maxrate 20M`.
- **CPU fallback:** the exact current settings (x264 slow CRF 17). Forced by `REEL_ENCODER=cpu` or `"encoder": "cpu"` in the EDL.
- **Concurrency:** at most 1 NVENC session per render + 1 analysis job. Peak VRAM measured at ~380 MB per encode 🧪.
- **QC addition:** record the encoder used in `production.json`. The quality gate is unchanged (spec + loudness + visual).
- **Tests:**
  - (a) With the GPU: output spec-valid, SSIM vs the CPU render ≥ 0.97 on a fixture.
  - (b) With `REEL_ENCODER=cpu`: byte-identical to today's settings.
  - (c) Simulated no-GPU (PATH without nvidia-smi): falls back with a log line, no failure.
- **Not doing:** NVDEC, libplacebo, `scale_cuda`. They were slower or changed the look 🧪 (35 §7). Re-evaluate only if a fully GPU-resident pipeline is proposed later.

### U3 · Seam fades, J/L cuts, quantisation
- **Where:** `edl/schema.py` (`audio_lead: float = 0` per segment, `seam_fade_ms: int = 15` global), `edl/resolve.py` (audio windows), `tools/reel_render.py` (audio chain built from audio windows: separate video and audio concat chains, as in agamm).
- **Rules** (adapted from agamm, MIT, credited):
  - Clip *i* audio = `[in_i − lead_i, out_i − lead_{i+1}]` in source time. The leads telescope, so totals match.
  - Lead on segment 0 is ignored with a warning. Error if a lead reaches before the source start, or leaves < 0.05 s of audio.
  - All cut points and leads are rounded to the frame grid.
  - A `afade` of 15 ms at every internal seam where natural audio is kept.
  - Segments with `audio: mute`, ramps or speed ≠ 1 can't carry a lead (validation error with a readable message).
- **Partial mute:** `mute_ranges: [[a, b]]` per segment (local seconds), implemented as volume automation (`volume=enable='between(t,a,b)':volume=0` with 10 ms fades). Closes CLAUDE.md gap 5 "partial-segment mute" (needed for the S2 BGM switch).
- **Tests:**
  - (a) Audio-windows unit tests (J, L, guards) ported in our words from agamm's test design.
  - (b) A render with leads keeps total duration within 1 frame and audio = video length.
  - (c) No A/V drift on fractional cuts (click-track fixture: click positions within 1 ms of the plan).
  - (d) Seam click test: a sine fixture cut mid-phase has no sample step > threshold after fades.
  - (e) v0 EDLs (no new keys) render identically.

### U4 · Motion quality
- **Zoom/punch:** do zoom maths at **2× internal resolution** (scale to 2160×3840 → frame-evaluated scale → crop 2160×3840 → downscale to 1080×1920 with lanczos). The step is 0.5 px at output. **For 4K sources, apply it in the prep stage** (the source already has 2× pixels). Only segments with zoom/punch pay the cost.
- **Shake:** replace `sin(n*2.7)` with a **≤ 8 Hz** pseudo-random walk (two sines at 6.1/7.3 Hz on `t`, not `n`), amplitude decaying over `dur`. Optional `freq` key.
- **Tests:**
  - (a) Motion-smoothness metric: on a slow push fixture, the frame-to-frame scale delta via phase correlation of consecutive frames has CV < 0.3 (old method expected to fail, recorded as a before/after).
  - (b) Shake spectrum: dominant frequency of the frame offset series ≤ 10 Hz.
  - (c) Golden frames for punch/shake (hash tolerance via SSIM ≥ 0.99).

### U5 · QC v2 (engine), replacing the reviewer's manual script
New rows in `engine/reelengine/qc.py` (pass/warn/fail):

| Row | Rule | Severity |
|---|---|---|
| Rhythm | Shot-length CV ≥ 0.15. Last shot ≥ 0.8× mean (unless a planned button). Accelerating run reported | warn (reviewer decides) |
| Split edits | Report the count. Warn when 0 and natural audio is kept on ≥ 3 cuts | warn |
| Reading time | `max(1.0, 0.33×words + 0.5)` (cards ≥ 0.8 s). ≤ 2 lines, ≤ 42 chars/line. **Tamil words counted by whitespace tokens with a letter** (as in the reviewer script) | fail |
| Text over subject | Rendered text bbox ∩ subject bbox (from `analysis/<clip>/subject.json` + face boxes, mapped through the reframe) > 15% of the text area | fail (P002 C8) |
| SFX repetition | Same file within 10 s → warn. **Same file at the same time ±50 ms → fail (duplicate layer)** | warn/fail (P002 C9) |
| Frame count | `nb_read_frames == round(duration × fps) ± 1` | fail |
| A/V sync vs source | For segments with kept natural audio: FFT cross-correlation of output vs source (8 kHz mono, ≤ 12 s). \|lag\| ≤ 33 ms | fail |
| Grade consistency | Per-shot `signalstats` YAVG/UAVG/VAVG. Flag a cast (\|U−128\| or \|V−128\| > 6 on neutral-heavy shots), crushed blacks (YMIN ≈ 16 for > 5% of a shot), clipped whites, and shot-to-shot jumps within one scene (ΔYAVG > 25) | warn |
| Noise (dark shots) | Temporal noise estimate on shots with YAVG < 60 → suggest denoise | warn (P002 C7) |
| Colour range | `color_range` tv/unknown. Never `pc` | fail |

- The reviewer skill's manual Python block is replaced by `reel qc` output. The craft gates stay with the reviewer.
- **Tests:** deliberately broken EDLs, one per rule: monotone cut list, a 0.6 s 8-word caption, text on a face, duplicate SFX, a 50 ms audio offset, a pc-range file, a dark noisy fixture. Each must be caught. Clean fixtures must pass.

### U6 · Audio intelligence
- **Tempo prior:** in `analysis/music.py`'s librosa fallback (and `tools/audio_beats.py`), weight autocorrelation by a log-normal prior centred on 120 BPM (σ = 0.9 octave). Report `tempo_alt` (×2/÷2) so the editor can choose the metrical level. Beat This! stays primary.
- **`reel snap P### --to beats|silence [--tolerance 0.35]`:** moves cut points onto beats in the **output** timeline (requires markers or a reference) or onto silence edges in the source. Writes `build/edl.snapped.json` + a move report. **Never moves a cut that is a sync target** (`sync` events win).
- **SFX library QA** (`reel sfx-qa`): crest/flat/onset/peak checks on `assets/sfx/*`. Results go into `assets/sfx/sfx.json` (`qa` field).
- **Variant rotation:** generate 2–3 variants per SFX (pitch ±1–2 semitones via `asetrate`+`aresample`, slight EQ, length ±10%). The compiler auto-rotates when the same SFX repeats within 10 s. Variants are derived from our own synthetic files, so there's no licence issue.
- **Macro de-duplication:** S1/S3 macros skip their default SFX if an explicit SFX cue exists within 100 ms (P002 duplicate at 1.5 s).
- **Denoise latency:** when the voice chain (afftdn) is used, measure the delay vs raw (cross-correlation) and compensate with `adelay`/`atrim`. Reported in QC.
- **Tests:**
  - tempo on 90/128/145 BPM click fixtures (no half-tempo)
  - snap moves within tolerance and never moves a sync target
  - QA flags a synthetic buzz/multi-hit file
  - no identical SFX within 10 s after rotation
  - latency compensation leaves |lag| < 2 ms

### U7 · Iteration speed
- **`reel report P###`:** pacing table (bars, CV, leads, last-shot hold) + text timing + SFX list. No render (agamm's `edl --report` idea).
- **`reel stills P### --at 0,1.2,marker:D,seg4.start …`:** renders single frames through the *same* compiled graph (trimmed to ±1 frame around each time) at full quality → `build/stills_vN/`. Expected: seconds instead of a ~2 min render.
- **Skill change:** professional-editor iterates on report + stills, then renders once. The reviewer still reviews the full render.
- **Tests:** a still at time t matches the full render's frame at t (SSIM ≥ 0.99).

### U8 · Deliverables
- **Trial-Reel hook variants:** EDL `"variants": {"A": {...}, "B": {"segments_order": [...], "hook_text": "…"}}`. `reel deliver --variants` renders each, QC per variant, packages `FINAL_A.mp4`, `FINAL_B.mp4` + a note recommending which to run as a Trial Reel (KB 02 §5). Each variant passes the full gates.
- **Editor kit** (`reel kit P###`):
  - stems: natural, SFX, music(ref) WAVs + per-SFX files + `cues.csv`
  - SRT of on-screen text
  - **FCP7 XML** timeline (adapted from sunithvs `xmeml.py`, Apache-2.0, with a notice) that DaVinci Resolve imports
  - a self-check: stems sum to the mix within −60 dB
- **Brand fonts:** pass `fontsdir=assets/fonts` to the libass filter (closes CLAUDE.md gap 2). Text styles may then use Anton/Bebas/Montserrat/Poppins (OFL, already in `assets/fonts`).
- **Style sizes:** `sub` 50 → 58 px, `tag` 40 → 48 px (P002 C6; < 40 px unreadable per typography practice).
- **HALD-LUT grades:** `reel lut <grade>` bakes `cozy`, `cozy_lift`, `moviemode` and `reality` into `assets/luts/*.png`. Grades can be referenced as `"grade": "lut:cozy"` (`haldclut`). Same look, cheaper than chained filters, and identical in stills and renders.
- **Score generator:** promote P001/P002 `build/score*.py` into `engine/reelengine/score.py` (`reel score P### --bpm 100 --bars 10 --mood cute`), with a licence note auto-written to `licenses/` (closes gap 7 + the P002 reviewer note).
- **Cover title:** an optional title text on `cover.jpg` (3:4-safe check).
- **Tests:**
  - variants render and each passes QC
  - the XML parses and references existing files
  - stems sum check
  - the fontsdir glyph test renders Anton text (pixel bbox > 0)
  - a LUT grade vs chain grade gives SSIM ≥ 0.995
  - the score has its licence note

---

## 3. Skill updates (existing five only)

| Skill | Section changes |
|---|---|
| `footage-analyst` | §6 concepts: add our **8-point story check** (want, obstacle, stakes, expectation gap, change, cause→effect chain, specific moment, loop/payoff) + **spoiler check** (the hook frame must not reveal the payoff unless it's a deliberate result-first hook) + "middle re-hook" note. §4: dark-shot noise flag from signalstats. (Concept credit: iuliacodau storytelling ideas, rewritten; McKee/Olson/Dicks already in KB 05) |
| `audio-director` | §4: tempo alternatives (½×/2×) and snap plan. §5: SFX rotation + no duplicate layers. §6: denoise-latency compensation. §7: hand-off adds `audio_lead` plan per cut |
| `professional-editor` | §1 rhythm: J/L-cut rules (0.2–0.5 s within a thought, 0.5–1.0 s cutaways, none on hard breaks), seam fades default, "hold after a hit". §2: new keys (`audio_lead`, `mute_ranges`, `variants`, `grade: lut:*`). §3: `reel report` → `reel stills` → render once. Text placement must avoid the subject bbox. §3 dual deliverable via variants. Editor kit on request |
| `quality-reviewer` | Replace the manual Python block with `reel qc` QC v2 rows. Hard gates add frame count, A/V sync, colour range, text-over-subject. C4/C6/C8/C9 use the new measured rows |
| `reel-director` | §3: Trial-Reel variant decision (when the hook choice is genuinely uncertain). §7 delivery: mention the encoder (GPU/CPU), offer the editor kit. Preflight: `reel doctor` shows the GPU status |

CLAUDE.md: update "Engine status", "Known gaps" (close items 2, 4, 5, 6, 7) and "Verified technical standards" (encoder settings, colour range).

---

## 4. Test and regression strategy
- **Keep:** `engine/tests/run_tests.py` (10/12 currently pass; the 2 failures are test-side per CLAUDE.md, fixed first as **U0**) + `smoke.py`.
- **Add** `engine/tests/test_upgrade_u*.py` per milestone. All fixtures are synthetic (lavfi), generated at test time, plus one 10 s HLG excerpt read from P001 *read-only*.
- **Golden regression:**
  - before U1, record frame hashes of P001's and P002's last EDLs rendered with `REEL_ENCODER=cpu prep_order=legacy`
  - after every milestone, the legacy path must reproduce them; the new path must pass SSIM ≥ 0.99 vs golden where the look is meant to be unchanged
- **Performance log:** wall time and peak RAM/VRAM per stage written to doc 34 §6 after each milestone.
- **Preservation:**
  - no file under `productions/P00*/` or `output/` is modified
  - tests write to temp folders only
  - renders of existing productions for regression go to a temp copy

---

## 5. Performance and quality trade-offs (expected)

| Change | Speed | Quality | Risk |
|---|---|---|---|
| U1 reorder | prep ×2.1 faster 🧪 | SSIM 0.998 vs current 🧪 | very low |
| U2 NVENC final | encode ×3.3 faster 🧪, ~20% smaller files at equal SSIM 🧪 | Equal SSIM 🧪. Grain/very dark gradients may differ slightly → keep CPU as a QC fallback if banding is seen | low (auto-fallback) |
| U2 NVENC lossless intermediates | ≈ same speed, frees CPU | lossless (better than CRF 8) | disk: ~3× larger temp files (deleted after render) |
| U4 2× zoom | +cost only on zoomed segments (est. +20–40%) | removes stair-stepping | low |
| U5 QC v2 | +10–30 s per QC | catches P002-class issues automatically | false positives → warn level first |
| U7 stills | review rounds in seconds | identical frames | none |

**Est. total for a 24 s Reel from 4K HDR (P001-like):** today ≈ 2 min per final render. After U1+U2 ≈ 50–60 s (estimate from the measured stage ratios; verified at U2).

---

## 6. Licence and attribution actions (with implementation)
1. `engine/ATTRIBUTION.md`: one row per adapted function (our function → source repo/file → licence → change summary).
2. agamm/saucetech (MIT): include their copyright + MIT text in ATTRIBUTION.md.
3. sunithvs (Apache-2.0): add `assets/LICENSES/Apache-2.0.txt`. Modified files carry an "adapted from sunithvs/video-agent-skill `<file>`, Apache-2.0, modified" header.
4. iuliacodau: **no code or text reused.** A concept credit line in footage-analyst only.
5. No repository is copied into the project. Only individual functions are re-implemented and adapted.

---

## 7. Approval checklist (reply with what you approve)
- [ ] **U0** fix the 2 failing engine tests (test-side)
- [ ] **U1** fast HDR prep (CPU reorder)
- [ ] **U2** NVENC encode + CPU fallback
- [ ] **U3** seam fades + J/L cuts + partial mute + quantisation
- [ ] **U4** smooth zoom + shake ≤ 10 Hz
- [ ] **U5** QC v2
- [ ] **U6** audio intelligence (tempo prior, snap, SFX QA/rotation, latency)
- [ ] **U7** `reel report` + `reel stills`
- [ ] **U8** variants, editor kit, brand fonts, style sizes, LUT grades, score module, cover title
- [ ] Skill updates (§3) + CLAUDE.md update

**No package installs are needed for U0–U8** (FFmpeg 6.1 + the existing venv). Nothing will be published or uploaded anywhere.

**Related:** [35 Comparison](35-github-editing-skills-comparison.md) · [32 Architecture](32-automated-editing-architecture.md) · [34 Integration plan](34-tool-integration-plan.md)
