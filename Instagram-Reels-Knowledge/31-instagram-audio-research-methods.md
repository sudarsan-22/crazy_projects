# 31 — Instagram Audio Research Methods (Official Sources, APIs, Publishing Integration)

> **Phase 3b · Technical infrastructure** · Created 2026-11-07 · Research only. No accounts, apps or API keys have been created
> Evidence tags: ✅ Official (Meta / Google developer docs, Instagram's own posts) · 🟡 Reported · 🔵 Practitioner · ⚠️ Theory · 🧪 Tested here
> **Builds on [22 — Instagram Audio Discovery](22-instagram-audio-discovery.md)**, which already defines the evidence standard, the trend-lifecycle stages and the **screenshot protocol**. This document adds: (1) a ranked map of *official* data sources, including the new **Instagram Audio API**; (2) per-category research methods; (3) a machine-readable audio record for the editing engine; (4) how the chosen audio gets into the published Reel.
> **Rules carried over:** no unauthorised scraping, no invented counts, and no "trending" without dated evidence ([22 §4](22-instagram-audio-discovery.md#4-evidence-standard-for-audio-claims)).

---

## 1. Key findings (what changed since doc 22)

| # | Finding | Tag |
|---|---|---|
| 1 | **An official Instagram Audio API exists (launched 1 June 2026).** `GET /ig_audio?audio_type=music\|original_sound` searches audio. **With no `search_query` it returns trending audio.** `GET /{ig_audio_id}` returns metadata. A Reel can be published with `audio_configuration: {audio_id, audio_volume, video_volume}` ([Audio API docs](https://developers.facebook.com/docs/instagram-platform/content-publishing/audio-api/), [changelog](https://developers.facebook.com/documentation/instagram-platform/changelog)) | ✅ |
| 2 | **But it only covers audio "authorized for third party use":** original sounds from Reels and **royalty-free Meta Sound Collection music**. The changelog describes music as Sound Collection. **Tamil film songs and label music from the in-app library aren't available through it** | ✅ |
| 3 | The Audio API returns **no usage counts**, **no trend direction**, **no region parameter** and **no start-offset parameter** for attaching audio. It says the selection "may differ from the native Instagram app" | ✅ (absence in docs) |
| 4 | Audio results include a **temporary `download_url`** (expires after about 1.5 days, may be null). That gives a **legitimate local reference copy** for beat analysis of API-available audio | ✅ |
| 5 | Your own Reels now expose **`media_audio_type`** (`MUSIC` / `ORIGINAL_SOUND`), and since 30 July 2026 `media_url` is **omitted** for videos with licensed or library audio | ✅ |
| 6 | **We found no official endpoint** for: audio usage counts, the in-app Trending leaderboard, or "list public Reels that use audio X". Those stay **in-app only**, gathered through your screenshots ([22 §5](22-instagram-audio-discovery.md#5-screenshot-protocol-what-to-send-me)) | ✅ (absence in docs) |
| 7 | **Meta Content Library / API** is for vetted researchers (institution review, secure research environment), so it's **not a creator tool** | ✅ ([Meta Transparency](https://transparency.meta.com/researchtools/meta-content-library/)) |
| 8 | Third-party "Instagram music / Reels-by-audio APIs" (Apify actors, ScrapeCreators, SociaVault and similar) describe themselves as scrapers of Instagram pages, so **they're excluded** under your no-scraping rule and Instagram's Terms on automated collection | ✅ policy / 🟡 vendor self-descriptions |

---

## 2. Source hierarchy (use the highest source available)

| Rank | Source | Access method | What it can prove | Who operates it |
|---|---|---|---|---|
| **1** | **Instagram app** (audio pages, ↗ arrow, Trending leaderboard, Professional dashboard, Edits Inspiration) | **You, manually**. Screenshots go to `account-data/audio/` | Usage count, trending flag, top Reels, recency | You → Claude logs them |
| **2** | **Instagram Audio API** (Graph API, Facebook Login) | Official API call from a Meta developer app **you own** | Trending *API-eligible* audio (original sounds + Sound Collection), metadata, preview file | Claude, via a script, after you set up the app ([§6](#6-instagram-audio-api-setup-optional-not-yet-approved)) |
| **3** | **Instagram Graph API: your own media and insights** | Official API | Which audio *type* your Reels used, and how they performed (`media_audio_type`, views, skip rate, reposts) | Claude (Phase 5 analytics loop) |
| **4** | **YouTube Data API v3** (official, free API key) | `videos.list?chart=mostPopular&regionCode=IN&videoCategoryId=10` (1 quota unit, 10,000/day by default) and `search.list` (100 units) | What's popular in **music in India** right now: a *leading indicator* for Tamil songs. Since 21 July 2025 `mostPopular` draws from YouTube's music, movie and gaming charts, after the Trending page was retired ✅ ([guide](https://developers.google.com/youtube/v3/guides/implementation/videos), [revision history](https://developers.google.com/youtube/v3/revision_history)) | Claude, via a script, once you create a Google Cloud API key |
| **5** | **Public web (official pages)**: Wikipedia film release lists (MediaWiki API), label YouTube channels, film-release news, @creators posts | Web search and fetch, MediaWiki API | Release dates, film or composer attribution, upcoming spikes | Claude |
| **6** | Curated playlists and trend newsletters (Spotify editorial and user playlists, Buffer, Later, Metricool) | Public pages | **Candidates only.** Streaming popularity ≠ Instagram trend ([22 §3.2](22-instagram-audio-discovery.md#32-leading-indicators-outside-instagram)) | Claude |
| ❌ | Scraper APIs, browser automation on instagram.com, spoofed user agents, logged-in session reuse | — | — | **Never** |

**Spotify note (✅):** since 27 November 2024, *new* Spotify Web API apps can't read algorithmic or Spotify-editorial playlists, audio features or recommendations. Spotify Charts has no public API. Spotify is therefore a **manual, human-viewed** signal only.

### 2.1 Browser-based research policy
| Allowed | Not allowed |
|---|---|
| You browse Instagram or Edits normally and take screenshots | Claude driving a browser on instagram.com to scroll audio pages, count Reels or collect data, even in your logged-in browser. That's automated collection, which Instagram's Terms prohibit without permission, and you've asked for no bots |
| Claude browsing **public non-Meta pages** (news, Wikipedia, YouTube, label sites) | Logged-out fetching of Reel or audio pages with a fake crawler user agent (already refused and logged, [13 §A0](13-my-instagram-account-analysis.md#a0-data-access-log)) |
| Claude reading the screenshots you save (vision), then logging the numbers **with the screenshot filename as evidence** | Estimating a count from a screenshot where the number isn't legible. Record it as `UNVERIFIED` instead |

---

## 3. Methods by research question

| Question | Primary (official) method | Secondary signals | Output / evidence level |
|---|---|---|---|
| **Trending Tamil audio** | You: Trending leaderboard + audio-picker searches ([22 §3.1](22-instagram-audio-discovery.md#31-search-terms-for-instagrams-audio-picker-)) → screenshots of audio pages. Re-check 2–3 days later for direction | YouTube `mostPopular` (IN, Music) filtered to Tamil titles or `defaultAudioLanguage=ta` · new Tamil film releases (MediaWiki) · Spotify Tamil playlists (manual) | Trend stage per [22 §4.1](22-instagram-audio-discovery.md#41-trend-lifecycle-classification-rules-no-invented-thresholds). Usage count **only** from screenshots |
| **Trending English audio** | Same in-app routine. Audio API trending call for *original sounds and Sound Collection* (if set up) | Buffer / Later / Metricool weekly lists (US-centric) · YouTube `mostPopular` IN | Same |
| **Popular Tamil movie BGM** | Audio-picker searches (`<film> bgm`, `mass bgm`, composer names) → audio page screenshots | Film release calendar · label channels (official uploads) · YouTube `search.list` for `<film> BGM` from **official label channels** | Evergreen vs new-release tag. Composer and film attribution from a reliable source |
| **Comedy dialogues** | Audio-picker searches (`vadivelu`, `goundamani`, `<film> comedy`) → audio pages. Most are **original sounds** uploaded by other users | Audio API `audio_type=original_sound&search_query=vadivelu` (if set up) returns API-eligible original sounds with uploader `ig_username` | ⚠️ An original sound that *contains* a film dialogue doesn't mean it's cleared. **Prefer acting the line yourself** ([15 §6](15-tamil-music-and-audio-strategy.md#practical-rules)) |
| **Emerging trends** | Two dated screenshots → velocity ([22 §4.1](22-instagram-audio-discovery.md#41-trend-lifecycle-classification-rules-no-invented-thresholds)) · Audio API trending list snapshots stored **daily with timestamps** (new entries = emerging, within the API pool only) | YouTube chart entries in their first week · trailer releases | 🌱 Emerging only with ≥ 2 dated observations |
| **Audio usage counts** | **Audio page screenshot only.** No official API exposes counts | — | The number exactly as shown ("12.4K reels"), with date and filename |
| **Public Reels using an audio** | Audio page screenshot (top 6–9 Reels with view counts) | Hashtag Search API (`top_media`/`recent_media`, limit 30 unique hashtags per 7 days) gives Reels **by hashtag, not by audio**, so it's a weak proxy | Examples are only "verified" if visible in your screenshot |

---

## 4. The audio record (machine-readable, used by the engine)

Doc 22 keeps the human log in [account-data/audio-log.md](account-data/audio-log.md). The engine reads the same facts as JSON (`audio_candidates.json`, one per job, see [32](32-automated-editing-architecture.md)):

```json
{
  "audio_key": "aud_2026-11-12_mass_bgm_x",
  "title": "…", "artist_or_film": "…", "composer": "…",
  "role": "mass_hero_entry",
  "rights_path": "in_app_library",
  "ig_audio_id": null,
  "observations": [
    {"captured_at": "2026-11-12", "source": "screenshot",
     "evidence": "account-data/audio/AUDIO_massx_2026-11-12.png",
     "usage_count_text": "12.4K reels", "trending_arrow": true}
  ],
  "trend_stage": "rising",
  "stage_basis": "2 dated counts (11-12, 11-14)",
  "reference_audio": {"path": "jobs/<id>/04_audio/ref.wav", "origin": "screen_recording_by_user", "use": "timing_only"},
  "analysis": {"bpm": 128.0, "markers": {"H": 0.0, "D": 7.52, "E": 15.0}},
  "in_app_start": "0:41.3",
  "approved_by_user": false
}
```
`rights_path` must be one of: `in_app_library` (added in-app only, never baked in) · `sound_collection` (royalty-free from Meta, can be baked in for Meta platforms) · `original_sound_api` · `own_recording` · `licensed_file` (licence proof in `licenses/`). Rules: any field without evidence stays `null`. `trend_stage` without two dated observations is `"unknown"`.

---

## 5. Getting the chosen audio into the published Reel

The rendered MP4 and the licensed audio meet at **publish time**. Which path applies depends on `rights_path`:

### Path A: Instagram library music (Tamil film songs, label tracks). **The default for your style**
1. **Reference copy for timing only (optional, [26](26-video-production-workflow.md#two-honest-limits-that-remain-and-the-best-feasible-alternative)):** you screen-record the audio playing in Instagram or Edits (as [24 §4](24-beat-sync-and-sound-design.md#4-syncing-to-audio-youll-add-in-app) specifies), or provide your own lawfully obtained copy. The engine analyses it ([30 §3](30-audio-analysis-tool-comparison.md#3-how-each-task-is-automated)) and **never puts it in an upload file**. Without a reference, cuts follow the track structure Claude planned, and you nudge the start in-app.
2. Claude picks the **in-app start point** (Autonomous Mode), e.g. `0:41.3`. The video's 0.0 s = that point.
3. Engine outputs: `final_clean.mp4` (no music, ≈ −16 LUFS) · `sync_guide.mp4` (review only) · `publish_sheet.md` with the song, start time, the **sync check** ("the drop should land on the name-card freeze at 7.52 s / frame 226"), suggested volume sliders, caption, ≤ 5 hashtags and cover frame.
4. You publish **in Instagram or Edits**: add the song from the library, set the start, check the sync check frame, and adjust original vs music volume.
5. 🟡 **Edits is preferred over the Instagram composer** for this step, because it shows the waveform and beat markers, so nudging the start point is more precise.
6. Licence reminder: library film songs are for **non-commercial personal Reels**. For any paid or brand Reel, use Path B or C ([15 §6](15-tamil-music-and-audio-strategy.md#6-licensing--legal-india-specific)).

### Path B: Sound Collection or original sounds via the Audio API (optional, needs [§6](#6-instagram-audio-api-setup-optional-not-yet-approved))
1. The engine searches `/ig_audio` → candidates → Claude selects one with [27](27-audio-matching-framework.md) scoring (or you choose, in plan-first mode).
2. It downloads the preview from `download_url` (temporary) → beat analysis → cuts.
3. Either **bake it in** (Sound Collection only, −14 LUFS) or **attach it at publish**:
   - `POST /{ig-user-id}/media` with `media_type=REELS`, `video_url` (must be **publicly reachable** at request time), `audio_configuration={"audio_id":…, "audio_volume":…, "video_volume":…}`
   - then `POST /{ig-user-id}/media_publish`
4. ⚠️ **No start-offset parameter is documented**, and the docs say previews with attached audio aren't supported ("The Reel will be published as configured"). The first API publish must be a **Trial Reel** (`trial_params`, ✅ since Dec 2025) to confirm where the audio starts before trusting beat sync.
5. API publishing counts against **100 API-published posts per 24 hours** ✅. That's irrelevant at your volume, but it's an official limit.

### Path C: Baked-in audio (own recordings, licensed files, Sound Collection downloads)
Mixed in the render at −14 LUFS / −1 dBTP, with licence proof in `licenses/`. Upload normally. Note: baked-in audio becomes an **original sound** on Instagram, so it won't link to an existing song's audio page.

### Account-type note
🟡 Business accounts are widely reported to get a **restricted music library** compared with Creator accounts. Keep @stupid_bruhmoment as a **Creator** account (already a to-do in [13](13-my-instagram-account-analysis.md)). The Audio API needs a **Business or Creator account connected to a Facebook Page** ✅.

---

## 6. Instagram Audio API setup (optional, not yet approved)

**Not required for Path A.** Only worth doing if you want automated trend snapshots of original sounds and Sound Collection, or API publishing.

| Requirement | Detail | Tag |
|---|---|---|
| Login type | **Instagram API with Facebook Login** (or Unified Login). *Not* available with Instagram Login | ✅ |
| Account | Instagram Business or Creator account **connected to a Facebook Page** | ✅ |
| Permissions | `instagram_basic`, `instagram_content_publish` (+ `pages_read_engagement` for Facebook Login publishing) | ✅ |
| Developer app | A Meta developer app you own. In development mode, permissions generally work for users who have a role on the app, so App Review is likely unnecessary for your own account | 🟡 (verify during setup) |
| Token storage | Long-lived user token in a local `.env` (git-ignored, `chmod 600`). Never pasted into documents | 🔵 |
| Cost | Free | ✅ |

**Decision for you (later):** set this up in Phase 4 only if Path B audio or trend snapshots prove useful. Path A works without it.

---

## 7. What we cannot do (by design)
- Read Instagram usage counts, the Trending leaderboard or audio-page Reel lists automatically. They're **screenshot only**.
- Attach Tamil film songs from the Instagram library via any API. That's **in-app only**.
- Download library songs from Instagram, YouTube or Spotify to bake into exports.
- Give region-specific (India or Tamil) trending data from any official API. The Audio API documents no region parameter.

**Related:** [22 Audio discovery](22-instagram-audio-discovery.md) · [15 Licensing](15-tamil-music-and-audio-strategy.md#6-licensing--legal-india-specific) · [24 Sync to in-app audio](24-beat-sync-and-sound-design.md#4-syncing-to-audio-youll-add-in-app) · [32 Architecture](32-automated-editing-architecture.md)
