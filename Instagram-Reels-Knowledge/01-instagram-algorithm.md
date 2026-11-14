# 01 — The Instagram Algorithm (Reels Focus)

> Evidence tags: ✅ Official · 🟡 Reported · 🔵 Practitioner · ⚠️ Theory (see [README](README.md#evidence-legend-used-in-every-document))
> Last researched: 2026-11-07

---

## 1. There is no single "algorithm"

✅ Instagram runs **separate ranking systems** for Feed, Stories, Reels, Explore and Search. Each one is tuned to how people use that surface. ([Instagram Ranking Explained](https://about.instagram.com/blog/announcements/instagram-ranking-explained))

| Surface | Mostly shows | What it optimises for |
|---|---|---|
| **Feed** | Accounts you follow, plus suggested posts | Relationships and interest. Recency matters |
| **Stories** | Accounts you follow | Closeness (DMs, profile visits, past story views) |
| **Reels tab** | **Mostly accounts you don't follow** | Entertainment and "worth my time" |
| **Explore** | Mostly accounts you don't follow | Popularity and interest match. "These signals matter much more in Explore than in Feed or Stories" |
| **Search** | Text-matched accounts, audio, hashtags, places | Text relevance plus popularity |

**Implication:** A Reel competes in the **Reels tab and Explore** against the best content from every creator in your topic, not just your followers' other options.

---

## 2. How Reels are ranked (the pipeline)

✅ Meta's system cards and Instagram's explainer describe the general shape. Exact weights are not published.

```
1. Candidate gathering  →  Find thousands of Reels a viewer might like
                           (topics they engage with, similar viewers, accounts
                            they interact with, trending/fresh content)
2. Signals/features     →  Gather info about the Reel, creator, viewer and context
3. Predictions          →  Predict probability of each action for THIS viewer
4. Scoring & ranking    →  Combine predictions into a score
5. Integrity & variety  →  Remove ineligible content; avoid too much from one
                           creator or topic in a row
```

### ✅ What Instagram predicts for Reels

Per Instagram's own explainer ([source](https://about.instagram.com/blog/announcements/instagram-ranking-explained)), the most important predictions are the likelihood that the viewer will:

1. **Reshare** the Reel
2. **Watch it all the way through**
3. **Like** it
4. **Go to the audio page** (a proxy for "inspired to create")

Instagram also surveys viewers on whether a Reel was **"worth their time or fun"** and tunes ranking with that feedback. Content that keeps people watching but feels like a cheap trick can still lose out.

### ✅ Input signals (in rough order of importance per Instagram)

1. **Your activity:** Reels you've liked, saved, reshared, commented on, watched through
2. **Your history with the poster:** past interactions, even if you don't follow them
3. **Information about the Reel:** audio track, visual understanding of the frames, popularity
4. **Information about the poster:** popularity signals such as follower count and engagement level

### 🟡 The "top three" signals (Mosseri, January 2025 and repeated in 2026)

Mosseri named **watch time, likes and sends** (DM shares) as the three most important signals. They aren't ranked against each other. Widely quoted framing:

- **Likes per reach** carry more weight for content shown to **followers**
- **Sends per reach** carry more weight for reaching **non-followers**
- **Watch time / average watch time** matter across the board

His suggested order of things for new creators to watch is **sends per reach → likes per reach → average watch time**. That advice is attributed to his June 2024 Colin & Samir interview ([summary](https://web.swipeinsight.app/posts/instagram-reveals-sends-per-reach-as-key-ranking-signal-8270)) and repeated in later coverage. Some blogs date a similar clip to October 2026, but I couldn't verify that date.

⚠️ Claims that "sends are weighted 3–5× more than likes" or "DMs beat watch time" are **not** official. No weights have been published.

### 🟡 Mosseri's 2026 ranking video series (September 2026)

In a multi-part series on his account ([coverage](https://kabo.sh/guides/instagram-ranking-2026), [another](https://www.parasocialmagazine.com/news/mosseri-names-four-instagram-ranking-principles-for-creators/)), Mosseri named these as things Instagram values beyond engagement:

- **Originality.** The original creator should get the distribution, not the reposter.
- **Recency.** Newer content is favoured. This is part of why Feed stays roughly chronological among followed accounts.
- **Breaking content.** Giving new and smaller creators a chance to break out.
- **Larger AI models.** Better content understanding, meaning more precise interest matching.

The series gave no weights and no guaranteed actions. Treat it as categories to understand, not a recipe.

---

## 3. How a Reel reaches non-followers

🟡 / ✅ As Instagram describes it, the general flow works like this:

```
Publish → small initial test audience (mix of followers + likely-interested non-followers)
       → if early viewers watch through, send, like, save → shown to larger, similar audiences
       → repeats in widening rings while performance holds
       → plateaus when engagement rate drops for the new audience ring
```

What drives the expansion:

| Lever | Why it works | How to pull it |
|---|---|---|
| **Clear topic** | Content understanding (the "larger AI models") matches you to the right interest cluster | One topic per Reel. Say the topic in speech, on-screen text and the caption |
| **Stranger-proof hook** | Non-followers have zero loyalty. Skip rate decides whether they stay | Hook makes sense with no context. No "as I said in my last video" |
| **Watch-through** | A core prediction | Tight edit, payoff at the end, loopable endings |
| **Sendability** | Sends per reach is the key non-follower signal | Content people DM to a specific person: "this is so you", useful, funny, relatable |
| **Originality** | Reposts are ineligible | Film it yourself, or transform it substantially |
| **Eligibility** | Ineligible content is never recommended | ≤3 min, no watermarks, Recommendation Guidelines compliant |

### ✅ Trial Reels

Trial Reels are shown **only to non-followers** first. If one performs well, you can share it to followers manually, or let it auto-share after **72 hours** based on performance. 🟡 Trial Reels gained **scheduling in February 2026** and are rolling out more widely ([coverage](https://socialbee.com/blog/instagram-updates/)). Mosseri recommended them in the 2026 series as the way to test without "spending" your follower audience.

**Use Trial Reels for:** testing two hooks on the same body, testing a new format or niche angle, and testing riskier creative without hurting follower engagement history.

### ✅ Viewer-side "Your Algorithm" control (December 2025)

Viewers can now see and edit the **topics** that shape their Reels recommendations ([TechCrunch](https://techcrunch.com/2025/12/10/instagrams-new-your-algorithm-tool-gives-you-more-control-over-the-reels-you-see)). It launched in the US first, with an English-language global rollout planned. **Implication:** Being clearly classifiable into a topic matters more now. Vague "random vlog" content is harder to match to a viewer who has picked topics explicitly.

---

## 4. Recommendation eligibility — the hard rules

✅ From the [Instagram Creators blog on recommendations](https://creators.instagram.com/blog/instagram-recommendations-eligibility-tips-creators) and the [Help Center](https://help.instagram.com/1525585517644948):

**To be recommended to non-followers, a Reel must:**
- Come from a **public** account
- Be **3 minutes or less**. Longer Reels can be posted, but only reach followers
- Follow the **Community Guidelines** (or it's removed) **and** the stricter **Recommendation Guidelines**

**Instagram aims to show fewer Reels that:**
- Are **muted, blurry or low resolution**
- Contain **borders, logos or watermarks** (for example a TikTok or CapCut watermark)
- Are **not original**: reposted from Instagram or aggregated
- Have **text covering most of the screen**
- Depict violence, promote regulated products (tobacco, vaping), or are sexually suggestive
- Come from accounts whose **profile photo or bio** violates the guidelines. This can make the whole account ineligible

**Account-level consequence:** Recent or repeated violations can make **your entire account ineligible** for recommendations for a period of time.

### ✅ Account Status — check it first when reach drops

**Settings → Account → Account Status** (professional accounts). It shows whether your content can be recommended, which posts are flagged, and lets you request a review. This is Instagram's official answer to "shadowbanning". Instagram says it does not intentionally hide content and **does not suppress content to sell ads** ([source](https://about.instagram.com/blog/announcements/instagram-ranking-explained)).

---

## 5. Originality rules (2024 → 2026)

| Date | Change | Tag |
|---|---|---|
| Feb 2021 | Reels with visible watermarks from other apps made "less discoverable" | ✅ |
| Apr 2024 | Ranking changed to favour original creators. Aggregators lose recommendations. When duplicates are found, the **original replaces the copy** in recommendations | ✅ ([Engadget](https://www.engadget.com/instagrams-algorithm-overhaul-will-reward-original-content-and-penalize-aggregators-130018977.html)) |
| 30 Apr 2026 | Anti-repost policy extended from Reels to **photos and carousels**. Accounts that **mostly** share others' work are ineligible for recommendations | ✅ ([TechCrunch](https://techcrunch.com/2026/04/30/instagram-restricts-reach-of-content-aggregators-in-new-crackdown/), [PetaPixel](https://petapixel.com/2026/04/30/new-instagram-policies-target-reposted-content/)) |

**What counts as original (per Instagram, April 2026):** content you **wholly created**, or content that **reflects your unique perspective**, including **substantially edited** third-party material with added commentary, humour, unique text or voiceover.

**What does NOT count:**
- Adding a border, watermark, subtitles or a credit alone
- Speed changes alone
- Screenshotting someone's post and tagging them
- "Minor edits"

**Safe ways to use others' content:** Instagram's **Remix** and **Collab** tools, sharing to your **Story**, reaction or commentary formats where *your* contribution is the point.

🟡 Some outlets report accounts regain eligibility **30 days** after their last unoriginal repost. That isn't consistently confirmed.

---

## 6. AI content and labeling (2024 → 2026)

- ✅ Posts with AI-generated or AI-modified content can carry an **"AI info"** label. It's applied by you, or automatically when industry-standard AI metadata is detected.
- 🟡 **May 2026:** Instagram tested an optional profile-level **"AI creator"** label ([Hypebeast](https://hypebeast.com/2026/5/instagram-tests-voluntary-ai-creator-label-on-profiles)).
- 🟡 **From 31 August 2026:** Profiles presenting **AI-generated people/personas** must carry an **"AI-generated profile"** label. Unlabeled detected profiles become **ineligible for recommendations** ([Unite.AI](https://www.unite.ai/instagram-renames-ai-creator-label-and-restricts-unlabeled-ai-generated-profiles/)). This targets AI personas, **not** normal use of AI editing tools such as captions, noise removal or upscaling.
- 🔵 **Practice:** Disclose realistic AI-generated visuals or voices. Normal AI-assisted editing doesn't need a label.

---

## 7. Common reasons for low reach — diagnostic table

Work top to bottom. The early rows are the most common causes.

| Symptom | Likely cause | Fix |
|---|---|---|
| Views ≈ near zero, no non-follower reach at all | **Ineligible**: Account Status flag, watermark, >3 min, guideline issue, private account | Check Account Status. Remove watermarks. Trim to ≤3 min. Appeal if wrong |
| High **skip rate** | Weak or slow hook, unclear first frame, logo intro, slow fade-in | Rework 0–3 s (see [05](05-hooks-and-storytelling.md)) |
| Low skip rate but **low avg watch time** | The middle sags, no open loop, payoff too early | Cut 20–40% of runtime. Add pattern interrupts. Move the payoff later |
| Good watch time, **low sends/shares** | Content is "fine" but not worth passing on | Make it more useful, relatable or specific to a type of person |
| Good reach, **few follows** | No reason to follow: random topic, weak profile | Series format. Consistent pillar. Clear bio promise (see [02](02-reels-growth-strategy.md)) |
| Reach mostly followers (>70%) | Content too insider-y, or a fallback because non-followers didn't engage | Stranger-proof hooks. Use Trial Reels |
| Sudden drop across all posts | Account-level eligibility issue, or a topic/format shift | Account Status. Compare against your previous format |
| Reels look soft or blocky | Low-quality upload setting, bad export, re-uploaded compressed file | Turn on "Upload at highest quality". Export settings in [07](07-instagram-seo-and-optimization.md) |
| Reposted content underperforming | Originality rules | Transform it, or stop reposting |

---

## 8. Myths vs. reality

| Claim | Verdict |
|---|---|
| "Instagram shadowbans you randomly" | ✅ Instagram says it doesn't intend to. Eligibility issues show in **Account Status**. Most "shadowbans" are just weak content or eligibility problems |
| "Hashtags boost reach" | ✅/🟡 Mosseri: hashtags help **categorise and search**, not reach. Capped at 5 since Dec 2025 |
| "Posting at the perfect minute is critical" | ⚠️ Overstated. Timing helps followers see it early, but Reels distribution runs for days or weeks (see "Views over time" in Insights) |
| "Ads boost organic reach" or "not buying ads suppresses you" | ✅ False. Instagram says it doesn't suppress content to encourage ad buying |
| "Saying 'TikTok' or 'link in bio' kills reach" | ⚠️ Unconfirmed. Meta has never stated this. Watermarks are the confirmed issue |
| "Engagement pods / comment groups help" | ⚠️ Inauthentic engagement violates the guidelines. It gives misleading signals from people who aren't your audience and can wreck targeting |
| "Delete and repost a flopped Reel" | ⚠️ Risky. Duplicate detection may treat it as unoriginal. Better: re-edit with a new hook, or run it as a Trial Reel |
| "Editing the caption after posting resets reach" | ⚠️ No evidence either way. Minor edits are generally fine |
| "Sends matter more than everything" | 🟡 Sends are one of the top three, and key for non-followers. No official ranking says they beat watch time |
| "Longer Reels are favoured now" | 🟡 Reels can be longer (reports of up to 20 min), but **only ≤3 min Reels are recommended to non-followers** ✅ |

---

## 9. Operating principles derived from the above

1. **Make it for the stranger.** Assume every viewer has never heard of you.
2. **Earn the first 3 seconds, then the last 3 seconds.** Hook and payoff decide watch-through.
3. **Design for a send.** Before filming, name the person a viewer would send this to.
4. **Stay eligible.** Original, no watermarks, ≤3 min, clean Account Status.
5. **One topic per Reel, and say it.** Help the classifier match you to the right audience.
6. **Test on non-followers** with Trial Reels before committing a format.
7. **Judge by ratios.** See [09 — Analytics](09-instagram-analytics.md).

**Related:** [02 Growth Strategy](02-reels-growth-strategy.md) · [05 Hooks](05-hooks-and-storytelling.md) · [09 Analytics](09-instagram-analytics.md) · [12 Sources](12-research-sources.md)
