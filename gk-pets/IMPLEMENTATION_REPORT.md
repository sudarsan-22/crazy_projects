# G K Pets – Landing Page: Implementation Report (Phase 5: built from G K Pets' own material)

`site/` – plain HTML/CSS/JS, no build, opens directly from `site/index.html` (tested via file://).

## Why this version
The previous version used generic stock photos (macaw, koi, canaries) and read as a general website. Per the owner-side decision "build from what exists", all stock photography was **removed**. Everything on the page now comes from G K Pets' real information and materials.

## What is G K Pets-specific now
- **Real pack shots**: hand-feeding formula, aquarium fish food, bird cage, aquarium air pump, cropped from the owner's own poster (hero wall + "Imported packs, on the shelf"). Shown at roughly native size so they stay crisp.
- **Real brand elements**: the logo wordmark (header tab/footer), the Tamil name ஜிகே பெட்ஸ் set as typography (hero ghost text, footer, meta), navy and yellow from the poster.
- **Real catalogue**: 12-line index using the categories from the old G K Pets store (Hand-feeding formula, Pigeon products, Feeding cups, Bird food, Bird supplements, Bird toys, Cuttlebone & holders, Hand-feeding tools, Automatic feeders, Cages, Breeding boxes) plus Aquarium feeds & accessories (poster). Each line opens a prefilled WhatsApp enquiry; on desktop, hovering Hand-feeding formula / Cages / Aquarium feeds shows the matching real pack shot.
- **Wholesale enquiry slip**: a small form (business name, location, products, quantity) that builds the wholesale WhatsApp message. Nothing is stored or sent by the site.
- **Two real locations** (shop and warehouse/gowdown) presented as separate address blocks, with the phone number as a giant headline.

## Design system
Bricolage Grotesque (display) + Instrument Sans (body) + Noto Sans Tamil. Navy #2B2E58, ink #0D0F2B, yellow #EEE565, bone/white. Motion: page fade-in, headline mask reveal, scroll reveals, ticker, hover preview, button fill, full-screen mobile menu; all off under reduced-motion.

## Testing (headless Chromium: 1440, 768, 390, 430 px)
No horizontal overflow, no broken images, no console errors/failed requests. 47 links audited (all anchors / tel / wa.me / Google Maps; none missing). Wholesale (6) and retail (2) WhatsApp messages intact. Enquiry slip produces the correct prefilled message. Hover preview works. Mobile menu opens/navigates/closes; Call/WhatsApp dock fixed. Reduced motion verified. Not tested: real devices/Safari, Lighthouse, WhatsApp delivery. Map fallback appears only on timeout (browsers still fire iframe `load` on error pages).

## Image limitation (unchanged and important)
The only real product imagery is the poster's small tiles (~210–230 px wide, upscaled 2x with light sharpening). They look acceptable at the sizes used but will look soft on high-DPI screens and cannot be enlarged. **Replace with original product photography** (hand-feeding formula, fish food, cages, accessories, shop and warehouse). Drop-in: replace `site/assets/img/pack-*.webp` (keep names) or edit the `<figure class="pk">` blocks in `index.html`.
The shop/warehouse themselves have no photos on the page yet.
The poster, business card and old crops are in `gk-pets/source-assets/`, outside the deployed `site/`.

## Needs owner confirmation
1. WhatsApp number (page uses 9884555888; confirmed as phone, not as WhatsApp).
2. Shop address (No. 13 School Road) vs warehouse (No. 10 Kasthuri 1st St); which takes walk-ins; map pin uses the shop.
3. The three enquiry steps (send list → availability and pricing → confirm details) are generic; confirm.
4. Categories: "Aquarium feeds & accessories" (from poster tagline) and the old-store category names.
5. "Pack shots in our materials include NutriBird, Optimum and Taiyo": factual wording, no partnership claimed; owner to confirm naming.
6. Original logo files (header logo is a raster crop of the poster), og:image, social links, hours, second phone 9884 988 877 (unpublished).

## Phase 6 update: image-led, quieter typography
- Removed the oversized typography: the outlined "WHOLESALE" word, the giant footer Tamil mark, the hero ghost text; headline, catalogue, phone number and "why" lines are now much smaller.
- New **"Imported products, on our shelves"** section (Brands) directly after About: four studio-style product cards (NutriBird hand-feeding formula, Optimum & Taiyo aquarium fish food, aquarium air pumps, bird cages) with an Enquire link each. The catalogue index shows small pack thumbnails beside the matching lines.
- **Product images are still the owner's own poster tiles.** I did not take official brand pack shots from the brand sites or from retailers (myowngarden, indohobby, BigBasket etc.): those are copyrighted, no licence/terms allowing reuse were found (Versele's page shows none), and no free-licensed pack shots of NutriBird/Optimum/Taiyo exist on Wikimedia Commons.
- To upgrade to premium-quality packshots: get high-resolution images from the supplier/distributor or the brand (dealers are normally given them) or photograph the stock. Drop them in `site/assets/products/` (see README there) and point the `<img>` tags in the "Brands & products" section at them. Product cards are sized for ~1200 px square images.
- Re-tested after the change: 50 links, wholesale/retail messages, enquiry slip, hover preview, mobile menu at 390/430, reduced motion, no console errors.

## Phase 7 update: Instagram and WhatsApp catalogue
- Verified from the owner's Instagram bio (@gk_pets_kolathur): the WhatsApp Business catalogue "G K Pets" is on **+91 98849 88877**.
  - All WhatsApp links (wholesale, retail, per-category, enquiry slip, mobile dock) now go to 98849 88877.
  - Calls stay on 98845 55888.
  - Both numbers are shown in Contact.
- Added "Browse our full WhatsApp catalogue" links (wa.me/c/919884988877) in the hero, the Brands section, the catalogue section and the footer.
- Added an Instagram band (Follow, Watch reels), a footer Instagram link and `sameAs` in the structured data.
- Instagram posts and reels and the WhatsApp catalogue items need a login or the app, so no product content from them is on the page yet. Needed from the owner: original photos and videos of the posts and catalogue items, plus product names.
- Re-tested: 58 links all valid, enquiry slip uses the new number, menu, layout at 1440/768/390/430, reduced motion, no console errors.

## Phase 8: product showcase built from the real WhatsApp catalogue
**Source.** 11 screenshots of the owner's WhatsApp Business catalogue gave 53 real products with names, sizes and brands. Combined with 3 poster pack shots, the site now shows 56 products in 5 collections.
- Product data: `catalog/products.py`.
- Page generator: `catalog/build_site.py`. Run `python3 catalog/build_site.py` after editing the data. The site itself remains static HTML with no build step.

**Page structure**
- **Hero:** eight real catalogue packs (NutriBird A19, Orlux Lori, Opti-Breed, Petslife 15 kg, Okiko Head Power, Calci-Lux, Bio Digest+) float into a layered composition. They have staggered entrances, gentle bobbing, depth and pointer parallax. Below sits a row of the brands named in the catalogue.
- **Catalogue:** one wrapper whose background and text colours morph as each collection reaches mid-screen.
  1. **Bird nutrition:** on desktop, vertical scroll drives a horizontal product story pinned beside the collection title, with a progress bar. On tablet and mobile it becomes a swipe rail.
  2. **Aquarium:** split layout with staggered large plates.
  3. **Pigeon:** two oversized specimens.
  4. **Toys & accessories:** editorial groups with sticky labels (feeders and cups, cuttlebone, hand-feeding tools, cages and cage tools, toys and wear).
  5. **Small pets:** drag or swipe reel with previous/next buttons.
- Every product links to WhatsApp with its own prefilled enquiry.
- **Wholesale:** "Stock the whole range." over a tilted wall of all products moving in two directions, plus the enquiry slip. Retail is a secondary strip.
- **Palette:** neutral ink and white, with a distinct tone for each collection (forest, ocean, stone, paper, blush). Logo navy and yellow are used only as accents.

**Testing** (headless Chromium, 1440 / 768 / 390 / 430 px, also opened from file://)
- 101 links, all valid; 56 product enquiry links; 7 wholesale and 2 retail messages.
- No broken images, no horizontal overflow and no console errors.
- The pinned story works on desktop and falls back to a swipe rail on tablet and mobile.
- The reel buttons scroll, the mobile menu opens and closes, and the map loads.
- With reduced motion: no pinning, no floating, no moving wall, and all content is visible.

**Image quality: important.** The product images are WhatsApp catalogue thumbnails, about 122 px originals. They were upscaled 2× with light sharpening and are shown at 170 px or less. I removed the rounded-corner remnants. They are acceptable at the current sizes but soft on high-DPI screens. **Ask the owner for the original catalogue photos.** Drop each one in as `site/assets/products/<id>.webp`, using the `id` from `products.py`. Square images of 800–1200 px are ideal, and the layout will use them as they are.

**Not published:** catalogue prices (owner decision), "Best Wholesale Price", and "No cash on delivery".
