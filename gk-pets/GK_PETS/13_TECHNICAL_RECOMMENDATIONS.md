# 13 – Technical Recommendations
- Audit existing gkpets.in (platform, hosting, domain registrar, analytics) from owner's network/access; it didn't resolve from the research environment, so check whether the domain is live.
- Likely stack: static/JAMstack site with JSON product data, WhatsApp click-to-chat links, Google Maps embed, schema.org LocalBusiness markup.
- Hosting on Netlify/Vercel/Cloudflare Pages; fast image optimisation (WebP).
- Defer payments/cart unless owner needs online sales; no returns policy already stated on current site.
- Not started: no code written.


## Phase 2 update
- Existing site is a DotPe hosted store; domain gkpets.in showed expiry 2024-08-29 and now fails DNS. First task: confirm domain ownership/renewal (registrar login, Tucows-registry .in) before any build, or risk losing the domain.
- Check GST/FSSAI/IEC only if owner wants to display them.
