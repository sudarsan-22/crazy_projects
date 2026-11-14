# GitHub Research: Video-Editing Skills & Tools for Claude Code

> **Researched:** 2026-11-07. **Research only: nothing installed, nothing executed, no project files changed** (this report is the only new file).
> **Method:** 16 repositories were shallow-cloned into a scratch folder and read directly: every SKILL.md frontmatter, the key SKILL.md bodies, manifests (`pyproject.toml`, `package.json`, `requirements.txt`), licence files, and the main scripts. Stars, forks and dates come from the GitHub API on the research date. Licence statements were checked against the licence *files* (GitHub's own detection was wrong or missing for 4 repos). Repo search covered "claude skill video editing", Remotion, HyperFrames, Motion Canvas, beat sync, shot detection, highlight detection and video quality assessment.
> **Context:** your footage is real camera footage (DIY gadgets, cute robots like Minimo Bear, pets, bikes, Tamil comedy), not talking heads or code-drawn explainers. That turns out to be the key filter.

---

## 1. Bottom line

1. **No repository edits your kind of footage well out of the box.** Almost the whole ecosystem targets either **talking-head** creators (cut silences, captions, face layouts) or **code-generated motion graphics** (SaaS launch promos, explainers). None handles comedy timing on pet or gadget footage, Tamil captions, or syncing to Instagram in-app audio.
2. **The valuable part is the *craft knowledge* in a few skills, not their engines.** The best editing intelligence is in agamm's `cutting-rhythm` and `editor`, herk-edit-kit's `short-form-edit`, kmilo93sd's `editing-videos` review checklist, and HyperFrames' `motion-doctrine` and `cut-the-curve`. All are MIT or Apache, so they can be adapted.
3. **Of the four repos you named, only sunithvs/video-agent-skill runs on Ubuntu as-is**, and it's a talking-head engine. agamm's CLI is **macOS-only** as written. Melvynx and imtamiliniyan are talking-head or faceless-explainer pipelines with cloud dependencies.
4. **Keep the reel-engine (FFmpeg + libass, local, CPU) as the renderer.** Add the craft rules as a Claude Code project skill plus new QC checks. Optionally add **HyperFrames** (Apache-2.0, Linux `.deb`, Node 22 already present) only as a motion-graphics overlay layer.
5. **Excluded on principle:**
   - Treg-based skills (they buy other accounts' Instagram data, which breaks your no-scraping rule)
   - fan-video pipelines that download third-party footage
   - DOVER (non-commercial licence)

---

## 2. The four repositories you named

| | **Melvynx/video-agent-skills** | **agamm/video-agent** | **imtamiliniyan/claude-video-skills** | **sunithvs/video-agent-skill** |
|---|---|---|---|---|
| Link | https://github.com/Melvynx/video-agent-skills | https://github.com/agamm/video-agent | https://github.com/imtamiliniyan/claude-video-skills | https://github.com/sunithvs/video-agent-skill |
| Licence (file) | MIT | MIT | MIT | Apache-2.0 |
| ★ / forks · created → last push | 122 / 29 · 2026-10-09 → 11-06 | 13 / 2 · 06-05 → 07-29 | 8 / 5 · 07-26 → 07-26 (**single drop**) | 3 / 1 · 10-16 → 10-16 (**single drop**) |
| Skills (SKILL.md verified) | 13 | 12 (+ `video_agent.py` CLI, 2,100 lines, 375-line test file) | 5 (two are 820–871 lines) | 2 (+ ~2,400 lines of scripts) |
| Engine | Node + headless Chrome (HTML frames) + FFmpeg | Python CLI on PyAV + FFmpeg. Remotion optional | **Remotion** (React) for every frame. FFmpeg only cuts | HTML page `seek(t)` → Playwright screenshots → FFmpeg |
| Transcription | whisper.cpp or ElevenLabs | **mlx-whisper (Apple Silicon only)** | **AssemblyAI or OpenAI (cloud keys)**. WhisperX commented out | **faster-whisper (local)** |
| Ubuntu status | ✅ Linux path documented (MediaPipe-in-Chrome replaces the macOS `.swift` vision helpers) | ❌ `VCODEC = "h264_videotoolbox"` and `import mlx_whisper` are hard-coded. Needs patching | ⚠️ Setup guide is macOS-only, pins Python 3.11 | ✅ README: "macOS or Linux". FFmpeg zscale for iPhone HDR |
| Built for | Talking-head "paper-style" motion shorts, B-roll library, clips from long videos, publishing | Any genre from raw footage (montage, doc, trailer, vlog…) via an auditable JSON EDL | Talking-head shorts + faceless "paper-reel" explainers | Talking-head reels with morphing face layouts, kinetic text, synced UI SFX |
| Best transferable idea | `steal`: *measure* a reference style with FFmpeg instead of eyeballing it | **`cutting-rhythm` + `editor`**: the clearest written editing craft found (§6) | Narrative-shape picker in `reel-script` (reveal, before/after, showdown…) | `verify.py` (frame count, LUFS, TP, A/V sync by cross-correlation) and **SFX placed on their measured peaks** in `mix_audio.py` |
| Red flags | `insta-audit` (competitor mode), `outliers` and `steal` fetch other accounts' Reels through **Treg** (paid, ~$0.001/call) | Grok VFX skill needs a paid xAI key (optional) | Cloud transcription by default. No maintenance history | One push, 3 stars. Talking-head only |
| **Fit for your Reels** | Low (talking-head) | **Medium: craft yes, code no** | Low | Low–medium (only if you start talking-head Reels) |

---

## 3. Alternatives found (verified)

| Repo | ★ · licence (file) · last push | What it really is (from its files) | Fit |
|---|---|---|---|
| **[heygen-com/hyperframes](https://github.com/heygen-com/hyperframes)** | 80.4k · **Apache-2.0** · 2026-11-07 | HTML/CSS/GSAP → deterministic MP4. Claude Code plugin (`claude plugin install hyperframes@hyperframes`). Linux `.deb`. ~450 registry blocks. 28 SKILL.md, including **`motion-doctrine`** (the "vector law" for seams) and **`cut-the-curve`** (zoom-through, inverse zoom, rack-focus blur-cut…) | **High as an overlay layer** (name cards, kinetic type, end cards). Not a footage editor |
| **[nateherkai/herk-edit-kit](https://github.com/nateherkai/herk-edit-kit)** | 2.6k · **MIT** + a use-permission file allowing personal or commercial videos (that's why GitHub shows NOASSERTION) · 10-14 | HyperFrames-based kit. 15 skills. **`short-form-edit`** (339 lines) is the best *storytelling* skill found: open-loop ledger, 3 alternative openings, first 3 s as a separate edit, muted test, object callbacks, "never manufacture retention scores" | **High (craft)** |
| **[kmilo93sd/agent-video-editor](https://github.com/kmilo93sd/agent-video-editor)** | 7 · MIT · 10-04 | One "editing judgment" skill with measured review checklist (text ≥ max(1.5 s, words×0.33+0.5 s), captions ≤42 chars/line, ≤20 chars/s), **CC0 SFX/music library with per-source licence review**, a 59-meme catalog that ships **no media** (Content-ID risk + how to make an original version) | **High (QC + comedy-meme safety)** |
| **[kajisho5/ffmpeg-skill](https://github.com/kajisho5/ffmpeg-skill)** | 4.7k · MIT · 11-07 | One FFmpeg skill + 13 unrelated dev-process skills. 42 stdlib-Python tools + MCP server, `--dry-run --json` contract, `check.py --platform`, `look.py` contact sheets, tests and benchmarks (~65k lines) | Medium: reference toolbox. Overlaps our engine |
| **[remotion-dev/skills](https://github.com/remotion-dev/skills)** | 6.5k · *no licence file* (Remotion's own licence: free for individuals and companies ≤3 people) · 11-05 | Official Remotion skills (13): create, render, captions, markup best practices | Medium: alternative to HyperFrames for graphics |
| **[digitalsamba/claude-code-video-toolkit](https://github.com/digitalsamba/claude-code-video-toolkit)** | 2.5k · MIT · 11-06 | Explainer production: Remotion, ElevenLabs, RunPod, LTX-2, ACE-Step music generation, moviepy | Low (generative/explainer) |
| **[calesthio/OpenMontage](https://github.com/calesthio/OpenMontage)** | 78k · **AGPL-3.0** · 11-03 | 13 pipeline YAMLs, 140 SKILL.md. Stock/generated-media productions (Pexels, Archive.org, Kling via fal.ai…). `cinematic` "works best with supplied footage" | Low–medium: ideas only (staged checkpoints). Heavy, AGPL |
| [Vincentwei1021/video-shotcraft](https://github.com/Vincentwei1021/video-shotcraft) | 17.6k · Apache-2.0 · 10-30 | Cinematic promos **from web pages/front-end projects** (Remotion, page captures) | Low: software products, not physical gadgets |
| [lemomo-ai/lemo-opuscar](https://github.com/lemomo-ai/lemo-opuscar) | 13.3k · MIT · 11-07 | 66 film *styles* rendered entirely in code (no footage) | Low |
| [guigulaoshi/music-video-director-skill](https://github.com/guigulaoshi/music-video-director-skill) | 69 · MIT · 09-25 | Music + clips → beat-synced MV (librosa, PySceneDetect, openai-whisper, ffmpeg-python). Tests included. **But:** the file is lowercase `skill.md` (Claude Code expects `SKILL.md`), its workflow downloads third-party anime/film footage from Bilibili/YouTube, and setup **appends to your shell rc** | Low (ideas: "song-first scene selection", novelty-based section detection) |
| [iart-ai/motion-skills](https://github.com/iart-ai/motion-skills) | 1.3k · MIT | An **index** of skill packs in other repos (0 SKILL.md in this repo) | — |
| [zhuyansen/awesome-claude-video-skills](https://github.com/zhuyansen/awesome-claude-video-skills) | 1.7k · CC0 | Curated list. ~40 relevant-looking entries scanned by name and description (not each cloned). Dominated by motion-graphics/SaaS promo skills | Discovery only |

### Specialist tools (non-skill)
| Need | Tool | Licence (file) | Verdict |
|---|---|---|---|
| Shot boundaries (better than content thresholds on fast handheld) | [soCzech/TransNetV2](https://github.com/soCzech/TransNetV2) | MIT. Last push 2023 | Optional upgrade to PySceneDetect. Unmaintained |
| Moment / highlight retrieval from text queries | [line/lighthouse](https://github.com/line/lighthouse) | Apache-2.0. Active | Optional research item ("find the moment the rabbit jumps") |
| Perceptual quality (encode damage, needs a reference) | [Netflix/vmaf](https://github.com/Netflix/vmaf) | BSD-2-Clause-Patent | Fine licence, but **not in your Ubuntu FFmpeg build** and it measures compression, not creativity |
| No-reference UGC quality (aesthetic/technical) | [VQAssessment/DOVER](https://github.com/VQAssessment/DOVER) | **S-Lab License, non-commercial** | ❌ Excluded (blocks brand-deal use) |
| Motion graphics in TypeScript | [motion-canvas/motion-canvas](https://github.com/motion-canvas/motion-canvas) | MIT. Last push 2026-07 | No agent-skill repo under the motion-canvas org (4 repos checked). HyperFrames/Remotion are better served |

---

## 4. Fit for your content types

| Content | What helps (and from where) | What nobody provides |
|---|---|---|
| **DIY gadgets / product showcase** (real objects) | herk `premium-motion-and-footage` guidance (restrained type, real object depth, soft shadows). HyperFrames blocks for spec callouts and end cards. agamm "trailer" recipe (hook → build → turn → climax → button) | Physical-product shot grammar (hero rotation, macro detail, before/after build) from *your* footage. Write it ourselves (KB 25) |
| **Cute robots** (Minimo Bear) | HyperFrames for overlays/UI-style cards. herk "object callback" (plant the object in the hook, pay it off at the end) | Robot "character" timing and OLED-face beat matching. KB 16 S1 name card + 23 role BGMs cover it |
| **Cinematic** | HyperFrames `motion-doctrine`/`cut-the-curve` (vector-matched seams, rack-focus blur-cut). agamm documentary recipe (L-cuts, held endings) | Grading/LUT intelligence on real footage. Our MovieMode/Reality grades stay |
| **Comedy Reels** | agamm "hold after a hit / widen the pause after a punchline". kmilo93sd meme catalog (Content-ID risk + "make your own version"). herk muted-first-3-s test | Comedy timing on *non-speech* footage (pet/gadget fails), BGM-switch mechanics, Tamil captions. Our KB 15/23/25 + engine are ahead here |

---

## 5. Why basic automated editing looks poor (evidence from the repos and our own tests)

| Failure | Why it happens | Fix (source) |
|---|---|---|
| **Accurate but lifeless cuts** | Sound and picture cut on the same frame ("butt cuts") | Split edits: `audio_lead` ±0.2–1.0 s (J/L cuts) (agamm `cutting-rhythm`) |
| **Monotone pacing** | Uniform shot lengths, uniform pause tightening | Vary holds, shorten shots toward the climax, *hold after a hit*, widen pauses after punchlines (agamm). Measure shot-length variation in QC |
| **Slideshow transitions** | Each scene animated in isolation, mismatched motion across seams | Vector law: same axis, direction and speed across a cut, cut mid-motion (HyperFrames `motion-doctrine`) |
| **Weak hooks** | Hook treated as part of the timeline, logo/greeting first | Edit the first 3 s separately, build 3 alternative openings, must work muted (herk). Hook frame at t=0 (sunithvs) |
| **Metric-chasing / invented claims** | Agents optimise numbers they can't measure | "Never manufacture retention scores" (herk). "Don't invent numbers" (sunithvs). Same as KB 13/22 rules |
| **SFX feel late** | SFX placed by file start, not by transient | Place by *measured peak* (sunithvs `mix_audio.py`). Already in our engine 🧪 |
| **Captions/text broken** | Letter spacing breaks complex-script shaping. Text outside the UI-safe zone | Found in our own QC on 2026-11-07: libass needs `Spacing 0` for Tamil 🧪. Safe-zone bbox checks |
| **"Verified" by looking at JSON** | No visual review loop | Contact sheets, stills at every entrance and cut, 2–3 review rounds (sunithvs step 7, ffmpeg-skill `look.py`, our QC evidence) |
| **The edit doesn't fit the footage** | Template forced onto material | Read the footage first, pick a treatment, then compose (agamm `editor` Step 1–2). Our KB 21 principle 4 |

**The core lesson:** quality comes from *editorial rules + a measured review loop*, not from a bigger rendering engine. Every strong repo pairs explicit craft rules with a verify step.

---

## 6. Recommendation for Ubuntu + Claude Code

**Keep the stack you approved, and add knowledge rather than another engine.**

| Layer | Choice | Why |
|---|---|---|
| Footage edit + render + QC | **reel-engine** (FFmpeg/libass, PyAV/OpenCV, faster-whisper, Beat This!) | Only option built for real footage, Tamil text, in-app audio sync and local CPU. Already passes its own tests |
| Editing intelligence | A new **project skill (`/edit-reel`)** that adapts, with attribution: agamm `cutting-rhythm` + `editor` (MIT), herk `short-form-edit` storytelling rules (MIT + permission), kmilo93sd review-checklist thresholds (MIT), HyperFrames seam vector law (Apache-2.0) | Craft rules transfer. Their engines don't fit your footage |
| New engine features suggested by the research | `audio_lead` (J/L cuts) in the EDL. QC rules for shot-length variation, "hold after hit", text duration `max(1.5 s, words×0.33+0.5 s)`, captions ≤42 chars/line | Directly fixes the §5 failure modes |
| Sound | Keep our 13 synthesised SFX. **Optionally** import kmilo93sd's CC0 SFX/music library (licences reviewed per source) | More variety, zero licence risk |
| Motion graphics (optional, later) | **HyperFrames** CLI + skills, rendered as transparent overlays and composited by FFmpeg | Apache-2.0, Linux `.deb`, Node 22 already in `~/.local/bin`, strongest agent skills. Remotion is the fallback (free for individuals) |
| Reference toolbox (optional) | kajisho5/ffmpeg-skill | Good dry-run/contract patterns. Don't install alongside the engine unless needed |
| Talking-head Reels (only if you start making them) | sunithvs/video-agent-skill | Linux-ready, faster-whisper, Apache-2.0 |

**Do not use:**
- agamm's CLI on Ubuntu without patching
- Melvynx `insta-audit`/`outliers`/`steal` (Treg data purchase)
- imtamiliniyan (cloud keys, macOS, no maintenance)
- music-video-director (third-party footage, shell-rc edits)
- OpenMontage (AGPL, generative-first)
- DOVER (non-commercial)

### Proposed next steps (each needs your OK, nothing done yet)
1. Write `/edit-reel` (project skill) from the §6 sources, with licence attributions, cross-linked to KB 21–28.
2. Add `audio_lead` + the new QC rules to the engine and its tests. Then resume milestones M5–M7 (paused mid-M5).
3. Optional: evaluate HyperFrames in an isolated folder for name cards and end cards (installs Node packages, so it needs its own approval).

**Related:** [32 Architecture](32-automated-editing-architecture.md) · [34 Integration plan](34-tool-integration-plan.md) · [21 Professional editing](21-professional-reels-editing.md) · [25 Cinematic & comedy](25-cinematic-and-comedy-editing.md)
