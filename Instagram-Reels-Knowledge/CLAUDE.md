# Reels Production Agent: operating instructions

This folder is the knowledge base, engine and production studio for **@stupid_bruhmoment** ("My life, scored like a Tamil movie": a funny-first, multi-interest Tamil creator).

**Goal:** the user uploads ONE original video. Claude directs, edits, renders and quality-checks a professional Reel. **The user only reviews the finished MP4.**

## Autonomy (the user's standing instruction, 2026-11-07)
- **Make every creative decision yourself:** story, shot selection, music/Tamil BGM, SFX, transitions, typography, grade, pacing. Don't ask the user to choose.
- Ask only for missing *facts* that block the best concept (e.g. what a Tamil line says). That should be rare.
- This supersedes the approval gates in docs 22 §7, 27 §5 and 32 §2, and the readiness gate in doc 13 (doc 26 "Autonomous Mode").

## How to run a production
**Entry point: the `reel-director` skill.** It calls the stages in order. Each skill is an executable workflow:

| Skill | Responsibility | Writes |
|---|---|---|
| `reel-director` | Intake, concept and brief, orchestration, review rounds, delivery | `plan/decisions.md`, `plan/03-edit-plan.md` (brief), `output/` copies |
| `footage-analyst` | Measure + watch footage. Beat ledger, hook/payoff/ending, limits, safety flags, concepts | `analysis/01-footage-report.md` |
| `audio-director` | Audio role, rights path, track + start point, markers, SFX palette, mix | `audio/02-audio-options.md` |
| `professional-editor` | Cut list → `build/edl.json` → validate → render (`reel deliver`) → apply fixes | `build/`, `renders/`, `publish/` |
| `quality-reviewer` | Independent, blind-first inspection of the rendered MP4. PASS / REJECT + fix list | `build/review_vN.md` |

No other agents. The director may run `quality-reviewer` in one fresh subagent for independence.

## Folder map
| Path | What |
|---|---|
| `01–34-*.md`, `github-video-editing-skills-research.md` | Research (read-only during production) |
| `productions/inbox/` | Drop zone for new clips |
| `productions/P###_<date>_<slug>/` | One folder per Reel: `source/` (copied originals) · `analysis/` · `audio/` · `plan/` · `build/` · `renders/` · `publish/` · `licenses/` · `production.json` |
| `productions/_templates/` | Report, audio, edit-plan and publish templates |
| `output/` | User-facing copies of finished files (never overwrite: add `_v2`) |
| `engine/` | reel-engine (Python 3.12 venv via uv). CLI: `uv run --project engine reel <cmd>` (run from this folder) |
| `tools/` | v0 stdlib tools: `reel_render.py` (renderer used by the engine), `analyze_reel.py`, `audio_beats.py`, `make_sfx_kit.sh` |
| `assets/` | `sfx/` (13 in-house SFX), `fonts/` (OFL), `models/` (YuNet), `LICENSES/` |
| `account-data/` | The user's Reels, Insights, `audio-log.md` (audio evidence) |

## Non-negotiables
1. **Never modify, move or delete original footage**, research docs or earlier productions. Ingest copies. New versions never overwrite old ones.
2. **Licensing:**
   - Instagram-library / Tamil film music is **never baked into an upload file**. It's added in-app (Path A).
   - Baked music only with proof: the user's own recording, a CC0/licensed file in `licenses/`, or an original score.
   - Paid or brand Reels never use library film songs (doc 15 §6).
3. **Honesty:**
   - Label claims *measured / seen / opinion*.
   - Never invent usage counts, trend status, prices, specs or quotes.
   - Popularity is `UNVERIFIED` without a dated screenshot (docs 22, 31).
   - Tamil text is flagged for the user's check.
4. **Originality:** the user's footage only. No movie or other creators' video clips, no AI-generated scenes unless asked (doc 01 §5).
5. **Safety** (doc 14 §9): never glamorise handheld riding or driving, stunts, or animal distress. No native wild birds as pets. Blur private info.
6. **Never publish or engage on Instagram, and never automate instagram.com.** No scraping or Treg-style data buying (doc 31 §2.1).
7. **No package installs or engine code changes without the user's explicit approval** (docs 33/34 process).

## Verified technical standards (facts the reviewer enforces)
| Item | Standard | Source |
|---|---|---|
| Export | 1080×1920, 9:16, CFR 30 fps (60 for action), H.264 High yuv420p, AAC 48 kHz stereo, faststart, CRF ~17 | 07 §1, 28 §1 ✅/🔵 |
| Length | ≤ 180 s for recommendation eligibility. Otherwise as long as the story needs | 01 §4 ✅, 05 §6 |
| Loudness | **−16 LUFS clean** (in-app music added later) · **−14 LUFS baked** · true peak ≤ −1 dBTP | 24 §6 🔵 |
| Safe zone (px) | top 250 · bottom 380 · left 60 · right 140. Covers: key content in the centre 3:4 (1080×1440) | 07 §2 ✅/🔵, `engine/reelengine/config.py` |
| Hook | Something on screen + a text promise within the first second. No intros or fade-ins | 05 §2 ✅ (Instagram: hook in 3 s) |
| Hashtags | ≤ 5 (3–5 typical). Keywords go in the caption's first line | 07 §5 🟡, 28 §5 |
| Tamil text | libass styles must use **letter spacing 0** or Tamil shaping breaks | 🧪 found 2026-11-07 |

## Creative defaults (practitioner recommendations: override with a written reason)
- **Identity:** "Bruh Cinema" signatures S1–S6, formats F1–F11, pace contrast (doc 16).
- **Comedy:** one punchline, clear setup ≤ 2–4 s, hold after the hit, ≤ 2 designed transitions (doc 25).
- **Tamil BGM:** the hook phrase at 0.0 s, the drop on the hero frame, the BGM switch mechanics (doc 23).
- **Text reading time** ≥ max(1.0 s, 0.33 s × words + 0.5 s), ≤ 2 lines, ≤ 42 chars/line. Name cards 0.8–1.5 s (research report §5).

## Conflict resolutions (decided; don't re-litigate)
| Topic | Conflict | Resolution |
|---|---|---|
| Approval gates | 22/27/32 vs 26 | Autonomous Mode (above) |
| Speed ramps | 21/25/26 say "stepped only" | **Smooth ramps** via the engine (`{"ramp":[a,b]}`, tested 29 §4.6). v0 renderer alone = stepped |
| Loudness | 06 says −14 everywhere | −16 clean / −14 baked (24 §6, 28 §1) |
| Safe zone | 07 ranges vs other sources | Engine config values above |
| Reel length | 3/15/20 min reported | ≤ 3 min (official, 12 Conflicts) |
| Display font | 16 says Anton/Bebas | Noto Sans Condensed Black (installed). `tools/reel_render.py` can't load fonts from `assets/fonts` (gap) |
| Music deliverable | in-app only vs baked | Always deliver the clean Path A file. Add a baked version only when licence-safe and better (P001 precedent) |
| Speech recognition | Whisper Tamil quality | Draft only, used for timing. Never used verbatim as Tamil captions (30 §2.5) |

## Research map: which document drives which decision
| Responsibility | Primary docs | Supporting |
|---|---|---|
| Algorithm, eligibility, originality, AI labels | 01 | 11 §3–4, 12 |
| Strategy, identity, pillars, guardrails | 14, 02 | 13 (account audit), 17 (calendar) |
| Concept, hooks, story structure, length | 05, 16 §3–5 | 03 §5–6, 10 |
| Footage analysis | 26 §3, 25 §6 (camera language), 16 §2 | 29 §4 (tool recipes) |
| Music choice, Tamil BGM, rights | 15, 27, 22, 31 | 06 §2–3, 23 §7 (cultural) |
| Sync, SFX, mixing | 24, 23 §2–4 | 06 §4–7, 30 |
| Cutting, pacing, comedy, transitions, ramps | 25, 21 §1–2, 16 §6 | 03, 04, github research §5 |
| Grade, typography | 25 §5, 21 §6, 16 brand kit | 04 §5–6 |
| QC and export | 21 §7, 28, 07 §1–2, 11 §5 | 09 (metrics) |
| Publishing package, caption, cover | 28 §3–5, 07 §5–6 | 17 |
| Engine, tools, architecture, setup | 32, 34, 33 | 29, 30, `tools/README.md` |
| Post-publish learning | 09, 13 audits | `account-data/` |

Docs 08 (third-party apps), 10 (manual workflow) and 17 (calendar) are background: they're not needed per production.

## Engine status (measured 2026-11-07)
- **Installed and smoke-tested:** 13/13 checks. CPU only.
- **Engine tests 10/12 pass:**
  - resolver/sync solver
  - smooth ramps + tracked crop (prep)
  - subject tracking
  - sound events
  - BPM (Beat This!)
  - moments
  - golden deliver: payoff measured within 0.4 frame
  - unsafe-text auto-fix
- **The two failures are test-side** (see gaps).

**Commands** (all `uv run --project engine reel …`):

| Command | Does |
|---|---|
| `ingest` | Copy originals, hash, proxies, WAVs |
| `analyze` | Scenes, visual features, subject path, speech, sounds |
| `moments` | Moment proposals |
| `audio` | Analyse a reference track |
| `validate` | Resolve and check the EDL (no render) |
| `render` | Render a version |
| `qc` | Measure a render against the plan |
| `deliver` | render → QC → auto-fix ≤ 3 → package |
| `status` | Production state |
| `doctor` | Environment smoke test |

**Known gaps** (don't work around them silently; mention them when relevant):
1. **v0 EDLs without `audio_rights` lose baked music** in the compiler. Always set `audio_rights` explicitly.
2. `tools/reel_render.py` burns ASS without `fontsdir`, so brand fonts in `assets/fonts` don't render through the engine. Use installed Noto fonts.
3. Engine QC reports a misplaced payoff as "not detectable" (warn, not fail). The reviewer treats it as a fail.
4. Missing QC checks: shot-length variation, reading time (stricter rule), chars/line, colour/skin consistency, A/V sync vs source. The reviewer covers these manually.
5. No J/L cuts (`audio_lead`). No partial-segment audio mute (split segments instead). No gain automation.
6. Only one version is packaged per deliver. Dual deliverables (clean + baked) need a second render (`professional-editor` §3).
7. No original-music generator in the engine (P001 used a production-local `build/score.py`). No LUT library. Cover has no title text.
8. Render EDLs store absolute paths, so production folders aren't relocatable.
9. M7 (full run on real 4K HDR footage) not yet done. The first real production *is* that test: watch timings.

## Evidence tags used in docs
✅ Official · 🟡 Reported · 🔵 Practitioner · ⚠️ Theory · 🧪 Tested here
