# 35 — GitHub Video-Editing Agents & Skills: Source-Level Comparison

> **Stage 1 (research and audit) · 2026-11-08 · nothing in the engine or skills was modified.**
> Method: the five repos were shallow-cloned into a scratch folder and **read, not executed**: every SKILL.md, every script, manifests and licence files. Our own engine (`engine/reelengine/*`, `tools/*`, `.claude/skills/*`, CLAUDE.md) and the P001/P002 reviews were audited. The GPU claims come from benchmarks on the user's real 4K HDR footage (§7).
> Builds on `github-video-editing-skills-research.md` (2026-11-07, survey level). This document goes to the **source level** and adds the two repos it didn't cover (iuliacodau, saucetech).
> Tags: ✅ verified in source · 🧪 measured here · 🟡 stated by the repo, not verified · ⚠️ concern

---

## 1. Summary

1. **None of the five repos can edit our footage better than our engine.** Four are built for talking heads, and one is knowledge-only. Our engine is already ahead on the hard problems (4K HLG tone-mapping, Tamil text shaping, in-app-audio sync planning, frame-exact sync solving, blind QC review).
2. **The real value is ~12 specific techniques** (§4), mostly from **agamm** (MIT, real code: J/L cuts, seam fades, frame quantisation, rhythm report, beat prior, snapping, HALD LUTs), **sunithvs** (Apache-2.0: A/V-sync and frame-count verification, denoise-latency compensation, stems/XML editor kit, Trial-Reel variants) and **saucetech** (MIT: measured grade QC, SFX library QA, seam fades, limited-range export).
3. **iuliacodau has no licence file**, so all rights are reserved. Its story diagnostic is excellent, but we may only reuse *ideas* in our own words, never its text.
4. **GPU:** NVENC is a real 3.3× win for the final encode at equal quality 🧪. NVDEC/libplacebo **slow down** our HDR pipeline on this laptop 🧪. The biggest speed win is a **CPU reorder** (scale before tone-map: 2.1× faster, visually identical 🧪).

---

## 2. Repository comparison

| | **agamm/video-agent** | **Melvynx/video-agent-skills** | **iuliacodau/video-editing-skills** | **saucetech/ai-video-editor** | **sunithvs/video-agent-skill** |
|---|---|---|---|---|---|
| Last commit (shallow clone) | 2026-07-28 | 2026-11-06 | 2026-11-01 | 2026-06-03 | 2026-10-16 |
| Licence (file) | **MIT** ✅ | **MIT** ✅ | **None.** No LICENSE, no licence field in plugin.json ⚠️ | **MIT** ✅ (fonts OFL) | **Apache-2.0** ✅ |
| Size | 12 skills + `video_agent.py` (2,100 lines) + 30 pytest tests | 13 skills, Node engine (~1 MB JS) | 8 skills (knowledge) + 1 helper script | 1 skill + 3 Python build scripts + SFX QA + HTML template | 2 skills + Python/Node scripts (~2,400 lines) |
| Implemented vs instructions | **Real code**: EDL renderer, J/L cuts, beats, snapping, tighten, reframe, LUT tools | Real code (motion-design engine), much of it browser-side | **Instructions only** (plus `transcribe.py`) | Real code: per-segment grade + voice chain, SFX mix, SFX QA. Relies on video-use + HyperFrames | Real code: assemble/tonemap, mix + measured SFX peaks, verify, stems + XML editor kit |
| Target footage | Any (talking heads, montage, trailer). Generic | Talking-head "paper" motion shorts | Planning and teaching (shoot, story, grade) | **Talking head**: kinetic word captions, glass cards | **Talking head**: morphing face layouts |
| Ubuntu | ⚠️ `VCODEC = "h264_videotoolbox"` and `mlx_whisper` are hard-coded (Mac). Needs patching to run | 🟡 Linux path documented (MediaPipe in Chrome) | ✅ (text) / ✅ script (faster-whisper) | 🟡 Needs Node + HyperFrames + video-use. ElevenLabs optional | ✅ README "macOS or Linux". FFmpeg zscale HDR path |
| Paid APIs | xAI Grok (optional VFX) | **Treg (buys other accounts' IG data)**, ElevenLabs dubbing, Codex images | none | ElevenLabs (optional SFX generation) | Stock APIs optional (keys) |
| Fit with our FFmpeg/Python engine | **High:** same paradigm (JSON EDL → FFmpeg) | Low (browser render) | Medium (craft rules for skills) | Medium (FFmpeg scripts are portable) | Medium-high (Python/FFmpeg scripts) |
| **Overall value to us** | **Highest (code + craft)** | Low (ideas: stills loop, hook variants, style measurement) | Medium (story diagnostic, ideas only) | Medium (grade QC, SFX QA, export rules) | Medium-high (verification, variants, editor kit) |

### Excluded on principle (CLAUDE.md non-negotiables 4 and 6)
- Melvynx `insta-audit`, `outliers`, and `steal`'s download path (Treg data purchase / downloading other creators' Reels via yt-dlp).
- agamm `grok-video-edit` (AI-modified footage, paid).
- saucetech and Melvynx ElevenLabs generation/dubbing (paid, and voice cloning).
- sunithvs `stock.py` and `fetch_x.py` (third-party media).

---

## 3. What each repo really contains (verified in source)

### agamm/video-agent (MIT)
| File / function | What it does | Quality |
|---|---|---|
| `video_agent.py: _edl_audio_windows` | **J/L cuts**: `audio_lead` per clip. Audio and video are separate concat chains. The leads *telescope*, so total audio = total video. Rejects leads that reach before the source start | ✅ Tested (`test_edl_audio_windows_split_edit`, `…_l_cut_and_guards`, `…_split_edit_keeps_duration`) |
| `_edl_achain` | ~15 ms `afade` in/out at every internal audio seam (removes clicks) | ✅ |
| `_edl_quantize` | Rounds every cut/lead to the frame grid, so audio and video can't drift on fractional cuts | ✅ (`test_edl_no_av_drift_on_fractional_cuts`) |
| `_edl_check_cutaway` | Cutaway picture length must equal the audio it covers (±1 frame) | ✅ |
| `_edl_vchain` (punch) | Slow push via `zoompan` on a **2× pre-scaled** frame, because zoompan on a 1× frame stair-steps (integer crop origin) | ✅ |
| `edl_report` | Shot-length bars, mean/median/range, **CV < 0.15 → monotone**, **no split edits**, **last shot < 0.8× mean** warnings | ✅ (`test_edl_report_flags_monotone_cut_list`) |
| `beats` | Spectral-flux onsets. Autocorrelation tempo with a **log-normal prior around 120 BPM** (fixes half-tempo lock). Sub-frame period interpolation. Circular-mean phase | ✅ (`test_beats_finds_the_tempo`) |
| `snap_edl` | Moves cuts to the nearest **beat (output timeline)** or **silence edge (source)** within a tolerance. Never drags distant cuts. Reports every move | ✅ (3 tests) |
| `tighten` | Shortens long pauses from the middle (keeps breaths) | ✅ Speech only |
| `grade_gen_lut` | Bakes any FFmpeg colour chain into a **HALD-CLUT PNG** (identity `haldclutsrc` through the chain) → fast, exact, reusable grade | ✅ (`test_grade_gen_and_apply`) |
| `reframe` | Crop with a focus bias, or pad with a blurred fill. **No tracking** by design | ✅ (we already have tracking) |
| Skills `cutting-rhythm`, `editor` | The best written cutting craft found: split-edit amounts (0.2–0.5 s conversational, 0.5–1.0 s cutaway), "hold after a hit", "accelerate to the climax", "never cut on the peak of a gesture", trailer structure hook → build → turn → climax → button | Instructions, MIT |

### sunithvs/video-agent-skill (Apache-2.0)
| File | What it does |
|---|---|
| `scripts/verify.py` | Final check: 1080×1920, **frame count = duration × fps (±1)**, −14 LUFS, true peak, **A/V sync vs the source audio by FFT cross-correlation (fails > 33 ms)** |
| `scripts/mix_audio.py` | Synthesised UI SFX **placed by measured envelope peak** (we already do this). **Denoise latency measured and removed** (afftdn ≈ 25 ms). One static gain + limiter master. **Stems** (voice/sfx/music + every SFX + `cues.csv`) that sum exactly to the mix |
| `scripts/xmeml.py` + `kit.py` | **FCP7 XML timeline** that Premiere and **DaVinci Resolve** import with every layer on its own track. Kit self-check: layers restacked vs master (PSNR ≥ 40 dB), stems summed vs mix |
| `scripts/assemble.py` | HDR tone-map via zscale (npl 203, hable), crop to 9:16, 30 fps |
| SKILL.md lessons | **Shakes under ~10 Hz** (faster aliases at 30 fps into jitter and doubled text) · 6 motion-blur sub-frames for graphics · **variants** (re-cut the same take with a different cold open for Trial Reels) · Indic native-script Whisper output is "often garbage", so use the translation pass for meaning |

### saucetech/ai-video-editor (MIT)
| File | What it does |
|---|---|
| `scripts/build_base_clip.py` | Per-segment extract with LUT + grade. **30 ms audio fades at every segment boundary.** Lossless `-c copy` concat with a fixed GOP. Voice chain (highpass 80, afftdn, EQ, de-ess) + two-pass loudnorm. **Freeze-fill** (`video_end`) keeps segment duration. Grade comment documents **measured QA**: `signalstats` YMIN/YAVG/YMAX, UAVG/VAVG ≈ 128 = neutral |
| `sfx/qa_sfx.py` | **SFX library QA without listening:** crest factor (dull), flat factor (buzz), onset count (multi-hit), peak (hot), silence |
| `scripts/build_sfx_mix.py` | Per-word tick + role hits, transient-trimmed samples (sample-accurate) |
| SKILL.md export rule | **Limited-range BT.709. Never tag `color_range=pc`** ("Instagram renders that with wrong levels"). Grade rule: deep blacks + S-curve + highlight recovery, no sharpening |

### iuliacodau/video-editing-skills (no licence)
- 8 knowledge skills: storytelling, scriptwriting, cinematography, color-grading, typography, color-palettes, captions, social-media-optimisation. Plus `captions/scripts/transcribe.py` (faster-whisper + VAD, SRT/VTT, `--max-words`).
- **Best idea:** an 8-point story check rated Strong/Thin/Missing: *want, obstacle, stakes, gap (expectation vs result), change, chain (but/therefore, not "and then"), specifics, loop + payoff*. Plus two gates: *one idea*, *viewer's interest not creator's pride*. Story shapes mapped to lengths (7–15 s = one ABT sentence. 15–30 s = hook, setup, attempt, turn, payoff).
- ⚠️ **No licence:** default copyright applies. **Reuse ideas only, rewritten, with a "concept credit"**, never copied text. (The underlying frameworks are published books, e.g. McKee, Cron, Olson's ABT, Dicks, which we already cite in doc 05.)

### Melvynx/video-agent-skills (MIT)
- Node + headless-Chrome engine for talking-head motion design. WebCodecs encode. Face framing via Apple Vision or MediaPipe.
- Transferable *ideas*:
  - **stills before renders** ("stills cost seconds, renders cost minutes")
  - **hook variants** (`hooks.mjs`: N different intros of one edit)
  - **style measurement**: hard cuts/s via `scdet`, a spectrogram for SFX on cuts, music level under voice, zoom count
  - the quality bar "the hook reads on the first frame"
- Code is not portable to our stack.

---

## 4. Best individual techniques (ranked by value to our Reels)

| # | Technique | Source (exact file) | Licence | Fixes which real problem | Our status |
|---|---|---|---|---|---|
| 1 | **J/L cuts with telescoping `audio_lead`** + frame quantisation | agamm `video_agent.py` `_edl_audio_windows`, `_edl_quantize` | MIT | CLAUDE.md gap 5. Butt cuts feel abrupt (research §5) | ❌ missing |
| 2 | **Seam fades (15–30 ms) at every audio join** | agamm `_edl_achain`; saucetech `build_base_clip.py` | MIT | Clicks at kept-natural-sound cuts | ❌ missing (`tools/reel_render.py` concats raw) |
| 3 | **Rhythm report** (CV, split edits, last-shot hold) inside engine QC | agamm `edl_report` | MIT | Gap 4. The reviewer computes it by hand | ⚠️ manual script in reviewer skill |
| 4 | **A/V-sync verification vs source** + frame-count check | sunithvs `verify.py` | Apache-2.0 | Gap 4 ("A/V sync vs source" missing) | ❌ missing |
| 5 | **Measured grade QC** (black/white points, cast, cross-shot consistency via `signalstats`) | saucetech `build_base_clip.py` comments + SKILL QA | MIT | Gap 4 ("colour/skin consistency"). P002 low-light noise | ❌ missing |
| 6 | **SFX library QA** (crest/flat/onsets/peak) | saucetech `sfx/qa_sfx.py` | MIT | Our 13 synthetic SFX were never QA'd. P002 C9 repetition | ❌ missing |
| 7 | **Beat-tempo prior + snap-to-beat/silence with move report** | agamm `beats`, `snap_edl` | MIT | Half-tempo errors (seen in our own tool tests). Hand-placed cuts | ⚠️ we have Beat This!/librosa + solver, no snapping |
| 8 | **Smooth zoom without stair-stepping** (do the zoom at 2× or source resolution) | agamm `_edl_vchain` | MIT | Our `scale=2*trunc(W*z/2)` + integer crop steps every few frames on slow push-ins (analysis, §6) | ⚠️ likely visible on slow zooms |
| 9 | **Shake ≤ 10 Hz** | sunithvs SKILL.md | Apache-2.0 | Our shake is `sin(n*2.7)` ≈ **12.9 Hz at 30 fps** → aliasing and jitter | ❌ |
| 10 | **Trial-Reel variants** (same edit, alternative cold opens) | sunithvs `variants()`; Melvynx `hooks.mjs` (idea) | Apache / MIT | KB 02 §5 testing system. P002 "hook spoils the payoff" | ❌ |
| 11 | **Editor kit: stems + FCP7 XML for DaVinci Resolve** | sunithvs `xmeml.py`, `mix_audio.py --stems` | Apache-2.0 | The user can fine-tune in Resolve/CapCut. Stems make the in-app music rebalance easy | ❌ |
| 12 | **HALD-LUT baked grades** | agamm `grade_gen_lut` | MIT | Consistent grade across segments. Faster than chained filters | ❌ |
| 13 | **Story diagnostic** (8 points + 2 gates) for non-speech footage | iuliacodau `storytelling` (ideas only) | **No licence**: ideas only | P002 hook spoiled the turn. Middle drift 8–13 s | ⚠️ partly in KB 05 |
| 14 | **Stills-before-render loop** | Melvynx short-editing (idea) | MIT | Faster review rounds. Full renders cost ~2 min | ❌ |
| 15 | **Limited-range BT.709 export guard** | saucetech SKILL §7 | MIT | Prevents the wrong-levels risk | ⚠️ implicit (yuv420p tv). Not asserted in QC |
| 16 | **Denoise-latency compensation** | sunithvs `mix_audio.py latency()` | Apache-2.0 | Doc 24 §7 voice chain uses afftdn (~25 ms delay) | ❌ |

---

## 5. Where our engine is already ahead (keep, don't replace)

| Capability | Ours | Theirs |
|---|---|---|
| iPhone 4K HLG → SDR | mobius tone-map chosen by side-by-side test (P001) 🧪 | sunithvs hable/npl 203. Others none |
| Sync | **Sync solver** (`resolve.solve_sync`: flex an edit so an event lands on a marker, exact) + measured payoff check | Snap only (agamm) |
| Reframing | Subject path (YuNet faces → motion centroid) + smoothed virtual camera | agamm manual focus. Others talking-head face only |
| Tamil text | libass + Noto Sans Tamil. Spacing-0 rule found by test | Nobody |
| In-app audio workflow | Path A/B/C rights model, never bakes film music | sunithvs mentions in-app audio. Nobody models rights |
| Review | Independent blind-first reviewer with hard and craft gates | sunithvs/Melvynx visual loops. No independent gate |
| Honesty rules | UNVERIFIED popularity, measured/seen/opinion labels | sunithvs "content honesty" |

---

## 6. Missing features in our engine (audit, with evidence)

| Gap | Evidence | Fix source |
|---|---|---|
| J/L cuts, partial mute, gain automation | CLAUDE.md gap 5 | agamm (#1) |
| Audio seam fades | `tools/reel_render.py` concat has no `afade` at joins | agamm/saucetech (#2) |
| QC: shot-length variation, reading time, chars/line | CLAUDE.md gap 4. Reviewer runs a manual script | agamm (#3) + our reviewer script |
| QC: A/V sync vs source, frame count | CLAUDE.md gap 4 | sunithvs (#4) |
| QC: colour/skin/grade consistency, noise | CLAUDE.md gap 4. P002 C7 low-light noise | saucetech (#5). GPU denoise (§7) |
| QC: text over the subject's face | P002 C8 ("MELTED." over the OLED face) | Ours: `subject.json` bbox vs text bbox (new) |
| SFX repetition and duplicates | P002 C9 (pop ×6, ding ×5, duplicate impact at 1.5 s from S1 macro + manual cue) | QC rule + dedupe in the compiler + saucetech QA (#6) |
| Small sub/tag text | P002 C6 (`sub` 50 px, `tag` 40 px) | Style sizes ≥ 54/48 px (iuliacodau ideas: < 40 px unreadable) |
| Zoom stair-stepping | `tools/reel_render.py` zoom = `scale=2*trunc(W*z/2)` + integer crop (2-px size steps; P001 ending pushed 86 px over 156 frames ≈ one step every ~3.6 frames) | agamm (#8). Measure in Stage 2 |
| Shake aliasing | Shake `sin(n*2.7)` per frame ≈ 12.9 Hz | sunithvs (#9) |
| Hook variants for Trial Reels | none | sunithvs/Melvynx (#10) |
| Editor hand-off (stems, XML) | none | sunithvs (#11) |
| Fonts from `assets/fonts` | CLAUDE.md gap 2 (no `fontsdir`) | libass `fontsdir=` option (ours) |
| Original music generator in the engine | CLAUDE.md gap 7 (P001/P002 used production-local scripts) | Ours (promote `score.py` to an engine module) |
| Stills preview | none (each review = full render ~2 min) | Melvynx idea (#14) |

---

## 7. GPU audit (measured 2026-11-08 on P001 `IMG_7191.MOV`, 10 s of 4K60 HEVC 10-bit HLG → 1080×1920 30 fps)

Hardware: RTX 3050 Laptop 4 GB (driver 580.178.04) + Intel Iris Xe iGPU (hybrid laptop). FFmpeg 6.1.1 (Ubuntu): `h264/hevc_nvenc`, `*_cuvid`, `scale_cuda`, `overlay_cuda`, `colorspace_cuda`, `bilateral_cuda`, **`libplacebo` (Vulkan)**, `tonemap_opencl`, `nlmeans_opencl/vulkan`, `xfade_opencl/vulkan`. **No CUDA tone-map filter.** **`av1_nvenc` produces no packets** (Ampere has no AV1 encoder) 🧪. **Vulkan device 0 = Intel iGPU, device 1 = RTX 3050** (FFmpeg defaults to the Intel one) 🧪.

### Decode + tone-map + fit (→ lossless FFV1, quality vs A1)
| Pipeline | Wall | Peak RAM | Peak VRAM | Quality vs current | Verdict |
|---|---|---|---|---|---|
| **A1 current:** CPU decode, zscale tone-map **at 4K**, then scale | 31.5 s | 2.2 GB | — | reference | baseline |
| A2 NVDEC (auto download) + same | 59.4 s | 2.1 GB | 0.9 GB | identical | ❌ **slower** (4K 10-bit frame download over PCIe) |
| A3 NVDEC + `scale_cuda` → tone-map at 1080p | 37.4 s | 1.1 GB | 1.1 GB | output failed comparison (orientation/format) | ❌ NVDEC saturated (100%) |
| A4 CPU decode + **libplacebo on RTX 3050** | 39.1 s | 2.1 GB | 0.7 GB | SSIM 0.943 (different tone curve) | ❌ slower, changes the look |
| A5 NVDEC + libplacebo | 58.3 s | 1.9 GB | 1.5 GB | SSIM 0.60 (**broken**) | ❌ |
| **A6 CPU: scale to 1080×1920 in 10-bit FIRST, tone-map at 1080p** | **14.9 s** | 1.9 GB | — | **SSIM 0.9977, PSNR 54 dB** (visually identical) | ✅ **2.1× faster, CPU only** |
| A7 Intel QSV decode | failed (exit 171) | — | — | — | ❌ |

### Encoders (identical lossless 1080×1920 input, quality vs lossless)
| Encoder | Wall | Mbps | SSIM | PSNR-Y | Verdict |
|---|---|---|---|---|---|
| **x264 slow CRF 17 (current final)** | 17.6 s | 11.9 | 0.9744 | 29.83 | baseline |
| h264_nvenc p7 hq, `-cq 19 -b:v 0` | 5.4 s | 16.5 | 0.9764 | 29.85 | ⚠️ **CQ ignored** (CQ 16 gave the same 16.5 Mbps) |
| **h264_nvenc p7 hq, VBR CQ 24 + maxrate 40M, spatial+temporal AQ, lookahead 32, B-frames** | **5.4 s** | **9.3** | **0.9747** | 29.84 | ✅ **= x264 quality, smaller, 3.3× faster** |
| h264_nvenc at x264's bitrate | 7.9 s | 13.2 | 0.9757 | 29.85 | ✅ |
| hevc_nvenc p7 | 6.0 s | 10.1 | 0.9756 | 29.85 | ✅ (Instagram accepts HEVC. H.264 stays the default) |
| x264 veryfast CRF 8 (current intermediate) | 7.9 s | 58 | 0.9946 | 51.1 | baseline intermediate |
| h264_nvenc **lossless** intermediate | 7.8 s | 167 | 1.0 | ∞ | ✅ truly lossless at the same speed. Frees the CPU |
| h264_nvenc constqp 20 | 17.1 s | — | — | — | ❌ slow |

Peak VRAM for any NVENC encode: **~380 MB**. A 4 GB card can safely run 1 encode + 1 decode.

### Where GPU acceleration fits without breaking effects
| Stage | Recommendation | Why |
|---|---|---|
| Segment prep (tone-map, reframe, grade) | **CPU, reordered** (scale → tone-map) | 2.1× faster 🧪. Our effects (zscale, eq, curves, colorbalance, ASS, zoom) are CPU filters. GPU round-trips cost more |
| Segment intermediates | `h264_nvenc` lossless, **CPU fallback** x264 CRF 8 | Lossless and offloads the CPU 🧪 |
| Final encode | `h264_nvenc` p7 VBR-CQ + maxrate (**must set maxrate**), **CPU fallback** x264 slow CRF 17 | 3.3× faster, equal SSIM 🧪 |
| Drafts and stills | NVENC p4 | Speed |
| Denoise for dark footage (P002 C7) | Candidate: `nlmeans_opencl` / `hqdn3d` (CPU). **To benchmark in Stage 2** | Unmeasured |
| HDR tone-map on GPU | ❌ Not now. libplacebo changes the look and was slower 🧪 | — |
| NVDEC | ❌ Not for HLG 10-bit 4K on this laptop 🧪 | Re-test only if the pipeline becomes fully GPU-resident |

**Memory:** the benchmark was OOM-killed once with ~5 GB of free RAM (Firefox and Tracker hold ~4 GB). The engine must keep **one heavy decoder at a time** (already the case since the P001 fix) and cap x264/FFmpeg threads when RAM is low.

---

## 8. Licence and attribution requirements

| Source | Licence | Reuse rule for us |
|---|---|---|
| agamm/video-agent | MIT, © 2026 Agam More | Adapt code/text freely. **Keep the MIT notice** in an `ATTRIBUTION.md` entry + a header comment naming the function adapted |
| saucetech/ai-video-editor | MIT, © 2026 saucetech | Same as MIT above |
| Melvynx/video-agent-skills | MIT, © 2026 Melvyn Malherbe | Ideas only planned. If code is adapted: MIT notice |
| sunithvs/video-agent-skill | Apache-2.0 | Adapting code requires: a **copy of the licence**, a **notice of changes** in modified files ("adapted from … , modified"), and keeping any NOTICE text (none found). No trademark use |
| iuliacodau/video-editing-skills | **No licence = all rights reserved** | **Ideas only, in our own words.** No copied text or tables. Optional courtesy credit ("concept inspired by") |
| Fonts in saucetech/sunithvs (Geist, Instrument Serif, Inter, Archivo) | OFL | Not needed (we use Noto + our OFL set) |

Planned: `engine/ATTRIBUTION.md` listing each adapted function → source file → licence, plus `assets/LICENSES/Apache-2.0.txt` if any sunithvs code is adapted.

---

## 9. Agents that should receive improvements (no new agents)

| Existing skill | Improvements |
|---|---|
| `footage-analyst` | Story diagnostic (8 points + 2 gates, our wording) on each concept. "Spoiler check": the hook must not reveal the payoff. Noise/low-light flag from `signalstats` |
| `audio-director` | Beat prior + snap reports. Split-edit plan (which cuts get `audio_lead`). SFX rotation plan (no repeat within 10 s). Denoise-latency note |
| `professional-editor` | `audio_lead` (J/L), seam fades default, `reel report` before rendering, stills preview loop, hook variants, subject-aware text placement, stems/XML on request |
| `quality-reviewer` | New engine QC rows replace the manual script: rhythm, reading time, A/V sync, frame count, grade consistency, text-over-subject, SFX repetition, limited-range |
| `reel-director` | Trial-Reel variant decision. Editor-kit offer. GPU/CPU encode note in delivery |

**Related:** [36 Upgrade plan](36-reel-engine-upgrade-plan.md) · [github-video-editing-skills-research.md](github-video-editing-skills-research.md) · [32](32-automated-editing-architecture.md) · [34](34-tool-integration-plan.md)
