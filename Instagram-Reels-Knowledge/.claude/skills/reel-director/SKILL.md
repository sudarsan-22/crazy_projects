---
name: reel-director
description: Entry point for producing an Instagram Reel from the user's original footage, fully autonomously. Use whenever the user uploads or names a video clip, drops files in productions/inbox/, says "make a reel", "edit this", "new reel", or asks to redo or revise an existing production (P###). Runs intake → footage-analyst → creative brief → audio-director → professional-editor → quality-reviewer → delivery, and makes every creative decision itself (story, shots, music, Tamil BGM, SFX, transitions, typography, grade, pacing). The user only reviews the finished MP4.
argument-hint: "<video file(s) | P### | 'inbox'> [optional one-line brief]"
---

# Reel Director

You own the whole production. The user reviews only the finished MP4, so **don't ask for creative choices** (CLAUDE.md "Autonomy"). Ask only for missing *facts* you can't get from the footage, and only when the Reel can't be made well without them (e.g. what a Tamil line says, if the joke depends on it).

Run from the KB root (`Instagram-Reels-Knowledge/`). All engine commands are `uv run --project engine reel …` (abbreviated `reel` below).

## 0. Preflight (once per session, ~1 min)
```bash
cd /home/sudarsan/Documents/crazy_projects/Instagram-Reels-Knowledge
uv run --project engine reel --help >/dev/null && ffmpeg -version | head -1
```
- If the engine fails to import, fall back to the v0 tools (`tools/reel_render.py`, `tools/analyze_reel.py`) for everything below, and say so in the delivery note.
- Run `reel doctor` only if something misbehaves.

## 1. Intake
- Files given or uploaded: `reel ingest <files…> --slug <short-topic>`
- Inbox: `reel ingest --inbox --slug <topic>`
- Existing production: `reel status P###`

This copies originals into `productions/P###_<date>_<slug>/source/` (never moved or modified), hashes them, builds proxies and WAVs, and flags HDR/VFR/rotation. **Never touch the user's originals or older productions' files.**

Record the user's brief (if any) verbatim at the top of `plan/decisions.md`.

## 2. Understand the footage → invoke `footage-analyst`
Wait for `analysis/01-footage-report.md`, which contains the beat ledger and 2–3 concept options. Don't make creative decisions before it exists.

## 3. Decide the concept (the creative brief)
Pick ONE concept and write the brief at the top of `plan/03-edit-plan.md` (template: `productions/_templates/03-edit-plan.md`):

| Field | Rule |
|---|---|
| Content type | One of the rows in the table below |
| Format | F1–F11 (doc 16 §3), or "Showcase" / "Cinematic" when no comedy format fits honestly |
| Logline | One sentence: *who/what* + *want/expectation* + *what actually happens* |
| Hook (0–3 s) | Visual + text + audio layer (doc 05 §2). Frame 1 = content, mid-action |
| Spine | Beats with target durations: hook → setup → escalation/build → payoff → button/loop |
| Punchline / payoff | ONE (doc 25 §1 rule 2). Name the exact source moment from the beat ledger |
| Ending | Loop to the hook, reaction hold, or verdict card. Never a fade-out to nothing |
| Target length | As long as the story needs. Defaults in the table below. Hard max 180 s |
| Language plan | Tanglish/English text by default. Tamil script only when it *is* the joke (flagged for the user's check) |

### Decision table by content type (defaults, which you may override with a written reason)
| Content | Story shape | Length | Pace | Grade | Music role (doc 15 §3) | Signatures |
|---|---|---|---|---|---|---|
| **DIY gadget / build** | Result-first hook → process (beat-synced, accelerating) → reveal on the drop → one funny final beat (F6/F5) | 15–30 s | Process fast (0.4–1 s shots), reveal held 1.5–2.5 s | Clean, slightly punchy. MovieMode only for the reveal | Training montage → mass/drop | S1 on the gadget, S4 tag |
| **Product showcase** | Problem/tease → hero reveal (low angle, push-in, slow-mo) → 3 feature beats (macro, one idea each) → verdict card (F5) | 15–25 s | Deliberate. Each feature 1.5–3 s. Hero hold ≥1.5 s | Clean, premium, protect true product colours | Stylish/mass BGM. Comedy only on the verdict | S1 name card, verdict card |
| **Cute robot** (e.g. Minimo) | Character intro → "personality" moments (expressions, reactions) → escalation → affectionate payoff → loop (F4 as a character) | 15–25 s | Medium. Hold on expressions ≥1 s | Warm "cozy" | Cute/romantic melody, light percussion | S1 character card |
| **Pets** | Character + mini plot (villain/hero) → twist. Real behaviour only (F4/F3) | 10–25 s | Patient setup, instant twist, reaction hold 1–2 s | Natural. **Protect fur/feather colours** | Villain/hero theme by character (15 §2.4) | S1, S3 on the twist |
| **Cinematic** (roads, scenery) | Establish → flow (motion-matched cuts on downbeats) → peak shot on the drop → loop to the opener (F8) | 12–30 s | Smooth 1.5–3 s shots | MovieMode | Nostalgic/mass | Minimal text (one line) |
| **Comedy** (bruh moments, skits, fails) | Setup → escalation → **switch** → reality → tag (F1/F2/F9) | 7–20 s | Slow, committed setup → instant switch → fast reality | MovieMode → Reality (S5) | Epic → switch → comedy/tragedy (23 §4) | S2, S3, S5 |
| **Lifestyle** (room, day, routine) | Relatable POV text → 3–5 quick beats → funny/relatable button (F9) | 8–20 s | Fast, varied holds | Natural/cozy | Trending-style or comedy | POV text, S4 |

**Hard rules** (CLAUDE.md "Non-negotiables"):
- Funny-first identity: every Reel needs one honest laugh, smile or "aww" beat, but **never fake one**.
- Pets and riding safety (doc 14 §9): if the footage shows unsafe riding or a distressed animal, don't glamorise it. Choose another concept or tell the user why.

## 4. Sound → invoke `audio-director`
Hand it the brief.

**Output:** `audio/02-audio-options.md`, which contains:
- the chosen path (A in-app / B Sound Collection / C baked)
- track(s), start point, roles, H/B/D/S/E markers (measured or planned)
- the SFX palette

## 5. Edit → invoke `professional-editor`
Hand it the brief and the audio plan.

**Output:** `build/edl.json` (edl/2), `plan/03-edit-plan.md` (completed), and renders from `reel deliver P###`.

## 6. Independent review → `quality-reviewer`
**Independence:**
- **Preferred:** launch ONE fresh general-purpose subagent with only this instruction: *"Follow `.claude/skills/quality-reviewer/SKILL.md` for production `<path>`, version `<N>`. Report the verdict file path."*
- **Otherwise:** run the skill yourself, following its blind-first protocol strictly.

Then act on the verdict:
- **REJECT** → give the numbered fix list to `professional-editor` → new version → review again.
- **At most 3 review rounds.** After round 3, deliver the best version that passes every *technical* gate, with remaining creative issues listed honestly.
- **Never deliver a version that fails a technical gate.**

## 7. Deliver
1. `reel package` runs inside `reel deliver`. Confirm that `publish/FINAL.mp4`, `publish/cover.jpg` and `publish/04-publish-package.md` exist and match the reviewed version.
2. Copy for the user (copy, never move):

   | Source | Copy to |
   |---|---|
   | `publish/FINAL.mp4` | `output/<Title>_FINAL.mp4` |
   | baked-music version (if any) | `output/<Title>_FINAL_with_music.mp4` |
   | `publish/cover.jpg` | `output/<Title>_cover.jpg` |
   | `publish/04-publish-package.md` | `output/<Title>_PUBLISH.md` |

   **Check before copying: if a file already exists at that name in `output/`, add `_v2`. Never overwrite.**
3. Append a dated entry to `plan/decisions.md`: concept, why, the audio choice, review rounds, known compromises.
4. Final message to the user (short):

   | Section | Content |
   |---|---|
   | Header | What was made (1 line) |
   | Which file to post | Path |
   | Audio | Exact name + start point + volumes, or "baked in". Popularity **UNVERIFIED** unless screenshot evidence exists |
   | Edit summary | Time → what happens table, 5–8 rows |
   | Check before posting | Tamil text, any unmeasured sync, anything the reviewer flagged |
   | Ready to paste | Caption + ≤5 hashtags |

## Revisions requested by the user
- Treat the user's notes as the brief delta: edit `build/edl.json` → `reel deliver P###` (creates vN+1) → reviewer → deliver.
- Previous versions stay on disk.

## Time and cost discipline
- Use the draft-free `reel deliver` loop (it already stops on failures).
- Don't re-run analysis unless the sources change.
- Speech recognition on silent clips is wasted. The analyst decides `--no-speech`.
