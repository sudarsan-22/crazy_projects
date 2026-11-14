---
name: audio-director
description: Stage 2 of a Reel production. Chooses the Reel's sound — Tamil/English music or BGM role, the rights path (Instagram in-app library vs baked-in), the exact track start point and sync markers (H/B/D/S/E), the SFX palette and mix targets — without inventing popularity data. Use when reel-director hands over a creative brief, or when the user asks which song/BGM to use, how to sync to it, or about SFX/mix for a production.
argument-hint: "<P### production>"
---

# Audio Director

**Output:** `audio/02-audio-options.md` (template: `productions/_templates/02-audio-options.md`), plus the `markers` and `audio_rights` fields that the editor puts into the EDL.

**Craft sources:** doc 15 (why Tamil sound tells the joke), 23 (BGM anatomy, BGM switch), 24 (sync and mix), 27 (scoring). **Rules:** doc 22/31 (evidence), 15 §6 (licensing).

## 1. Pick the audio ROLE before any song (doc 15 §3)
The role comes from the brief's content type and payoff:

| Brief | Role |
|---|---|
| Trivial thing treated as epic | Mass hero entry |
| Pet or object as antagonist | Villain theme |
| Fail or loss | Tragedy / sad violin |
| Reaction, reality check | Comedy track or comedian dialogue |
| Cute robot, affection, "aww" | Romantic / cute melody |
| Build process | Training montage → drop |
| Roads, scenery | Nostalgic melody, or mass BGM for bikes |
| Product reveal | Stylish/mass BGM (licensed only if it's a brand deal) |

**Comedy switch** (F1/F2): two roles, A (epic/romantic) and B (comedy/tragedy). Follow doc 23 §4.

## 2. Choose the rights path (decide first; it changes everything)

| Path | When | Deliverable |
|---|---|---|
| **A: in-app library (default for Tamil film songs and BGM)** | Personal, non-paid Reels | `FINAL.mp4` with natural sound + SFX only, **≈ −16 LUFS**. You state the track, the **start point** and volumes. The user adds it in Instagram or Edits (doc 28 §3). Two tracks for a switch: multitrack (doc 23 §4) |
| **C: baked in** | Licence-safe music exists: the user's own recording, a CC0/licensed file with proof in `licenses/`, or an **original score** | `FINAL_with_music.mp4` at −14 LUFS, beat-exact |
| B: Sound Collection via API | Only after the user sets up the Meta app (doc 31 §6). **Not available now** | — |

- **Brand or paid Reel → never library film songs** (doc 15 §6, Zee v. Nykaa). Use Path C with licensed music only.
- **Default deliverable:** Path A clean file. *Additionally* deliver Path C when you can do it licence-safely and it makes the edit better. P001 did both: an in-app Tamil song **and** an original score version (`productions/P001_*/build/score.py`, additive synthesis, no samples).
- An original score is appropriate for cute, music-box or minimal percussive styles. Don't attempt "mass BGM" or film-style scores by synthesis. They'll sound cheap.

## 3. Select the track (Path A) without fake data
1. **Candidates (≥3):**
   - evergreen Tamil classics for the role (doc 15 §2.5 composer shorthand)
   - recent Tamil film songs (web research, release dates)
   - `account-data/audio-log.md` entries
   - one English alternative
2. **Gates** (doc 27 §3), all must pass:
   - availability is plausible for a Creator account
   - not a paid Reel
   - **cultural safety:** no caste/religion/political mockery, no fan-war bait, no devotional music for comedy (doc 23 §7)
   - **footage fit:** the track's key moment can land on a real ledger moment
3. **Score fit** (doc 27 §4):
   - Relevance ×3, Tamil appeal ×2, comedy/emotion ×3, sync feasibility ×3, longevity ×1 → **Fit score /60**
   - **Popularity is `?` unless a dated audio-page screenshot exists** in `account-data/audio/`. Never estimate it.
   - Never write "trending" without that evidence.
4. **Pick ONE** (and one English runner-up). In `02-audio-options.md` record:

   | Field | Notes |
   |---|---|
   | exact song name | — |
   | film / composer | with a source link |
   | role and why it fits a specific ledger moment | — |
   | usage count | `UNVERIFIED` unless evidence |
   | trend status | `unknown` unless evidence |
   | licensing note | — |

## 4. Structure and sync markers (video 0.0 s = audio start point)

| Situation | Method | Label |
|---|---|---|
| **Reference audio available** (the user's screen recording of the audio page, or a lawful copy) in `audio/` | `uv run --project engine reel audio P### --ref audio/<file> --start <track_seconds> --dur <reel_length+2> --name "<song>" --role <role>`. View `audio/beats_plot.png`. Write `music.json` markers H, B, D, E (+ S for switch) into the brief. Timing only: it never enters `FINAL.mp4` (QC checks correlation) | **measured** |
| **No reference** (common) | Choose the start point by the song's known structure: the hook phrase at 0.0 s (doc 23 §2). Plan cuts on the *visual* rhythm. Put the payoff on a moment the user can nudge to in-app | **planned, not measured.** Say so in the package |
| **Path C / original score** | You control the tempo. Pick a BPM so key moments fall on beats (frames per beat, doc 24 §1). The score's bar grid *is* the marker set | **exact** |

**Sync hierarchy** (doc 24 §2): drop/hit → hero frame. Phrase starts → section changes. Downbeats → main cuts. Accents → text pops or punches. Never cut on every beat for the whole Reel.

## 5. SFX palette (from `assets/sfx/`, all synthesised in-house, licence-free)

| File | Use |
|---|---|
| `whoosh_short` / `whoosh_airy` / `whoosh_long` | Designed transitions, fast moves (peak mid-blur) |
| `riser_2s` | Into a reveal or drop (**align end**) |
| `impact_hit`, `sub_drop` | Name card, hero frame, drop (**align peak**). Sub only on the drop |
| `punch` | Zoom punch / S3 bruh sting |
| `pop`, `click`, `ding` | Text pops, UI-style moments, robot screens |
| `scratch_stop`, `tape_stop` | BGM switch (doc 23 §4) |
| `shutter` | Freeze frame / photo moment |

**Density** (doc 24 §5.2, 25 §7):
- High energy: about 5–15 per minute. Calm or cinematic: 0–4.
- Never one on every cut.
- Rotate variants, no identical SFX within 10 s.
- Leave mid-low room when in-app music will be added.

**Pets:** add sound in the edit, never by startling the animal (doc 14 §9).

## 6. Natural sound and voice

| Natural sound | Handling |
|---|---|
| Room tone only (≤ −45 LUFS) | Mute (`"audio": "mute"`) and carry the Reel with SFX + music. P001 lesson |
| Good natural sound (pets, engine, reactions) | **Keep it.** It's authenticity (doc 24 §5.1) |
| Speech | Keep. Music must sit under it (−18 to −25 dB below dialogue). The voice chain is in doc 24 §7 |

**Mix targets:**
- Clean: −16 LUFS. Baked: −14 LUFS. True peak ≤ −1 dBTP (doc 24 §6).
- The engine normalises these automatically. You choose the *relative* levels (SFX `gain_db`, typically −16 to −6).

## 7. Hand-off to the editor (put these in `02-audio-options.md`)

| # | Item |
|---|---|
| 1 | `audio_rights` value for the EDL (`in_app_library` / `own_recording` / `licensed_file`) |
| 2 | Track name(s), start point(s), suggested volumes (original/music %), switch timing if multitrack |
| 3 | Markers (H, B, D, S, E) in video seconds, each labelled measured / planned / exact |
| 4 | SFX cue list: `{file, at (time or marker:X or segN.event), align, gain_db}` |
| 5 | Which segments keep natural audio |
| 6 | Caption audio credit line (optional) |
