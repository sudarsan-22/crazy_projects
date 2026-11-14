"""Generate gk-pets/site/index.html from catalog/products.py.

Optional tooling only: the site itself is plain static HTML/CSS/JS with no build step.
Run:  python3 catalog/build_site.py   (from the gk-pets folder)
"""
import html
import os
import sys
from urllib.parse import quote

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from products import P  # noqa: E402

SITE = os.path.join(HERE, "..", "site")
WA_NUM = "919884988877"            # WhatsApp Business (catalogue) number – from the owner's Instagram bio
CALL = "+919884555888"
WA = f"https://wa.me/{WA_NUM}"
CAT = f"https://wa.me/c/{WA_NUM}"
IG = "https://www.instagram.com/gk_pets_kolathur/"
e = html.escape


def wa(text):
    return f"{WA}?text={quote(text, safe='')}"


WHOLESALE = wa("Hello G K Pets, I would like to make a wholesale enquiry.\n\nBusiness name:\nLocation:\nProducts required:\nApproximate quantity:")
RETAIL = wa("Hello G K Pets, I would like to ask about a product (retail enquiry).\n\nProduct:\nQuantity:")

prods = [dict(zip(("id", "thumb", "ch", "col", "brand", "name", "detail"), p)) for p in P]
by_id = {p["id"]: p for p in prods}


def full_name(p):
    return " ".join(x for x in (p["brand"], p["name"], p["detail"]) if x).replace(" · ", ", ")


def img(p, cls="", lazy=True):
    alt = e(" ".join(x for x in (p["brand"], p["name"], p["detail"]) if x))
    return (f'<img class="{cls}" src="assets/products/{p["id"]}.webp" width="228" height="228" alt="{alt}"'
            f'{" loading=\"lazy\"" if lazy else ""} decoding="async">')


def plate(p, i, extra="", lazy=True):
    brand = f'<span class="pl-brand">{e(p["brand"])}</span>' if p["brand"] else f'<span class="pl-brand">{e(p["col"])}</span>'
    detail = f'<span class="pl-detail">{e(p["detail"])}</span>' if p["detail"] else ""
    return (f'<a class="plate {extra}" href="{wa("Hello G K Pets, I would like to enquire about: " + full_name(p))}" '
            f'target="_blank" rel="noopener" style="--i:{i}">'
            f'<span class="pl-img">{img(p, lazy=lazy)}</span>'
            f'<span class="pl-meta"><span class="pl-n">{i:02d}</span>{brand}<span class="pl-name">{e(p["name"])}</span>{detail}'
            f'<span class="pl-go">Enquire <i aria-hidden="true">&#8599;</i></span></span></a>')


def poster_plate(file, w, name, col, i, extra=""):
    return (f'<a class="plate {extra}" href="{wa("Hello G K Pets, I would like to enquire about: " + name)}" target="_blank" rel="noopener" style="--i:{i}">'
            f'<span class="pl-img"><img class="wide" src="assets/img/{file}" width="{w}" alt="{e(name)}" loading="lazy" decoding="async"></span>'
            f'<span class="pl-meta"><span class="pl-n">{i:02d}</span><span class="pl-brand">{e(col)}</span><span class="pl-name">{e(name)}</span>'
            f'<span class="pl-go">Enquire <i aria-hidden="true">&#8599;</i></span></span></a>')


def chapter_items(ch):
    return [p for p in prods if p["ch"] == ch]


def cols_summary(items):
    seen = []
    for p in items:
        if p["col"] not in seen:
            seen.append(p["col"])
    return "".join(f'<li>{e(c)} <b>{sum(1 for p in items if p["col"] == c):02d}</b></li>' for c in seen)


# ---------- hero floating packs (real catalogue images) ----------
HERO = [  # id, x%, y%, width px, depth, delay, float duration, start rotation
    ("nutribird-a19-800g", 50, 46, 210, 1.0, .35, 6.0, -6),
    ("orlux-lori-3kg", 18, 24, 150, .7, .5, 7.0, 7),
    ("opti-breed", 82, 20, 140, .6, .62, 6.5, -5),
    ("petslife-hf-15kg", 16, 72, 160, .8, .74, 7.5, 6),
    ("okiko-head-power", 84, 70, 150, .75, .86, 6.8, -7),
    ("calci-lux", 62, 86, 110, .4, .98, 8.0, 5),
    ("bio-digest", 36, 8, 104, .35, 1.1, 8.5, -4),
    ("nutribird-a19-250g", 92, 46, 96, .3, 1.2, 9.0, 8),
]
hero_packs = "\n".join(
    f'<div class="hp{" far" if z < .5 else ""}" style="--x:{x}%;--y:{y}%;--w:{w}px;--z:{z};--d:{d}s;--f:{f}s;--r0:{r}deg;z-index:{int(z * 10)}">'
    f'<div class="hp-in">{img(by_id[i], lazy=False)}</div></div>'
    for i, x, y, w, z, d, f, r in HERO)

# ---------- chapters ----------
nut = chapter_items("nutrition")
nut_plates = "\n".join(plate(p, n, lazy=False) for n, p in enumerate(nut, 1))  # eager: slides in sideways

aq = chapter_items("aquarium")
aq_plates = (plate(aq[0], 1, "pl-lg")
             + poster_plate("pack-fish-food.webp", 422, "Aquarium fish food (Optimum, Taiyo)", "Fish food", 2, "pl-lg")
             + poster_plate("pack-air-pump.webp", 448, "Aquarium air pumps", "Accessories", 3, "pl-lg"))

pig = chapter_items("pigeon")
pig_plates = "\n".join(plate(p, n, "pl-xl") for n, p in enumerate(pig, 1))

acc = chapter_items("accessories")
groups = []
for c in ["Feeders & cups", "Cuttlebone", "Hand-feeding tools", "Cage tools", "Toys & wear"]:
    items = [p for p in acc if p["col"] == c]
    cells = []
    off = 1 if c == "Cage tools" else 0   # the poster cage photo leads the cage group
    if off:
        cells.append(poster_plate("pack-cage.webp", 422, "Bird cages", "Cages", 1, "pl-feat"))
    for n, p in enumerate(items):
        cells.append(plate(p, n + 1 + off, "pl-feat" if n == 0 and len(items) > 3 and not off else ""))
    title = "Cages & cage tools" if c == "Cage tools" else c
    groups.append(f'<div class="grp" data-reveal><div class="grp-h"><h3>{e(title)}</h3><span>{len(cells):02d}</span></div>'
                  f'<div class="grp-grid">{"".join(cells)}</div></div>')
acc_groups = "\n".join(groups)

sp = chapter_items("smallpets")
sp_plates = "\n".join(plate(p, n) for n, p in enumerate(sp, 1))

wall_items = [p for p in prods]
half = len(wall_items) // 2


def wall_row(items):
    # decorative (every product is listed with a name in the chapters above); duplicated for a seamless loop
    tiles = "".join(f'<span class="wt"><img src="assets/products/{p["id"]}.webp" width="228" height="228" alt="" decoding="async"></span>'
                    for p in items)
    return tiles + tiles


TOTAL = len(prods) + 3  # + poster pack shots (fish food, air pump, cage)

page = f'''<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>G K Pets – Imported Pet Products | Wholesale &amp; Retail, Chennai</title>
<meta name="description" content="G K Pets, Kolathur, Chennai: wholesale-first supplier of imported pet products – NutriBird and Petslife hand-feeding formula, bird feeds, supplements, feeders, cage tools, pigeon, aquarium and small-pet products. Retail welcome. WhatsApp 98849 88877.">
<meta name="theme-color" content="#0f1013">
<link rel="icon" href="assets/favicon.png" type="image/png">
<meta property="og:type" content="website">
<meta property="og:title" content="G K Pets – Imported Pet Products | Wholesale &amp; Retail">
<meta property="og:description" content="Wholesale-first supplier of imported pet products. Kolathur, Chennai.">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Bricolage+Grotesque:opsz,wght@12..96,400..800&family=Instrument+Sans:wght@400;500;600&display=swap" rel="stylesheet">
<link rel="stylesheet" href="css/styles.css">
<!-- Generated by catalog/build_site.py from catalog/products.py. Product images: owner's WhatsApp catalogue (low-res thumbnails, replace with originals).
     WhatsApp Business = +91 98849 88877 (owner's Instagram bio). Calls = +91 98845 55888. OWNER TO CONFIRM: shop/warehouse addresses, enquiry steps. -->
<script type="application/ld+json">
{{"@context":"https://schema.org","@type":"Store","name":"G K Pets","alternateName":"ஜிகே பெட்ஸ்","description":"Wholesale-first supplier of imported pet products. Retail available.","telephone":"+91 98845 55888","sameAs":["{IG}"],"address":{{"@type":"PostalAddress","streetAddress":"No. 13, School Road, Kolathur","addressLocality":"Chennai","addressRegion":"Tamil Nadu","postalCode":"600099","addressCountry":"IN"}}}}
</script>
</head>
<body>
<a class="skip" href="#main">Skip to content</a>

<header class="nav" id="top">
  <a class="logo-tab" href="#top" aria-label="G K Pets – home"><img src="assets/logo-wordmark.webp" width="837" height="254" alt="G K Pets"></a>
  <nav class="nav-links" aria-label="Main">
    <a href="#collection"><b>01</b>Collection</a><a href="#nutrition"><b>02</b>Bird nutrition</a><a href="#accessories"><b>03</b>Accessories</a><a href="#wholesale"><b>04</b>Wholesale</a><a href="#contact"><b>05</b>Visit</a>
  </nav>
  <a class="btn btn-y nav-cta" href="{WHOLESALE}" target="_blank" rel="noopener"><span>Wholesale Enquiry</span></a>
  <button class="burger" aria-expanded="false" aria-controls="sheet" aria-label="Open menu"><i></i><i></i></button>
</header>
<div class="sheet" id="sheet" aria-hidden="true">
  <nav aria-label="Mobile"><a href="#collection"><b>01</b>Collection</a><a href="#nutrition"><b>02</b>Bird nutrition</a><a href="#accessories"><b>03</b>Accessories</a><a href="#wholesale"><b>04</b>Wholesale</a><a href="#contact"><b>05</b>Visit</a></nav>
  <a class="btn btn-y" href="{WHOLESALE}" target="_blank" rel="noopener"><span>Wholesale Enquiry</span></a>
</div>

<main id="main">

<!-- HERO -->
<section class="hero" id="hero">
  <div class="h-copy">
    <p class="kicker rise" style="--d:.1s">G K Pets <span>/</span> Kolathur, Chennai</p>
    <h1 class="mega"><span class="ln"><span style="--d:.2s">Imported</span></span><span class="ln"><span style="--d:.3s">pet products,</span></span><span class="ln"><span style="--d:.4s"><em>supplied wholesale.</em></span></span></h1>
    <p class="lead rise" style="--d:.9s">Hand-feeding formula, feeds, supplements and accessories for birds, aquariums and small pets &ndash; supplied to pet shops, breeders and resellers. Retail welcome.</p>
    <div class="cta rise" style="--d:1.05s">
      <a class="btn btn-y" href="{WHOLESALE}" target="_blank" rel="noopener"><span>Wholesale Enquiry</span></a>
      <a class="btn btn-o" href="#collection"><span>Explore Products</span></a>
    </div>
    <a class="cat-link rise" style="--d:1.2s" href="{CAT}" target="_blank" rel="noopener"><span class="wa-dot" aria-hidden="true"></span>Browse our WhatsApp catalogue <i>&#8599;</i></a>
  </div>
  <div class="stage" id="stage" aria-label="Products from our catalogue">
{hero_packs}
  </div>
  <div class="brands-row rise" style="--d:1.4s">
    <span class="br-k">Brands in our catalogue</span>
    <span>Versele-Laga</span><span>NutriBird</span><span>Oropharma</span><span>Petslife</span><span>Okiko</span>
  </div>
</section>

<!-- COLLECTION INTRO -->
<section class="intro" id="collection">
  <div class="wrap intro-grid">
    <p class="idx" data-reveal>(01) The collection</p>
    <h2 class="intro-h" data-reveal>{TOTAL} products from our catalogue, in five collections. Wholesale first, retail welcome.</h2>
    <ol class="chap-index" data-reveal>
      <li><a href="#nutrition"><span>01</span>Bird nutrition<b>{len(nut):02d}</b></a></li>
      <li><a href="#aquarium"><span>02</span>Aquarium<b>{len(aq) + 2:02d}</b></a></li>
      <li><a href="#pigeon"><span>03</span>Pigeon<b>{len(pig):02d}</b></a></li>
      <li><a href="#accessories"><span>04</span>Toys &amp; accessories<b>{len(acc) + 1:02d}</b></a></li>
      <li><a href="#smallpets"><span>05</span>Small pets<b>{len(sp):02d}</b></a></li>
    </ol>
  </div>
</section>

<!-- CATALOGUE: one wrapper whose tone morphs between chapters -->
<div class="catalogue" id="catalogue" data-tone="nutrition">

  <section class="chapter pin" id="nutrition" data-tone="nutrition">
    <div class="pin-sticky">
      <div class="ch-head">
        <p class="ch-num">Collection 01</p>
        <h2 class="ch-title">Bird<br>nutrition</h2>
        <p class="ch-desc">{e("Hand-feeding formula, feeds, supplements and mineral blocks.")}</p>
        <ul class="ch-cols">{cols_summary(nut)}</ul>
        <div class="ch-progress" aria-hidden="true"><i></i></div>
      </div>
      <div class="track" tabindex="0" aria-label="Bird nutrition products (scrolls sideways)">
{nut_plates}
      </div>
    </div>
  </section>

  <section class="chapter split" id="aquarium" data-tone="aquarium">
    <div class="wrap split-grid">
      <div class="ch-head" data-reveal>
        <p class="ch-num">Collection 02</p>
        <h2 class="ch-title">Aquarium</h2>
        <p class="ch-desc">Fish foods and aquarium accessories.</p>
      </div>
      <div class="stagger">
{aq_plates}
      </div>
    </div>
  </section>

  <section class="chapter duo" id="pigeon" data-tone="pigeon">
    <div class="wrap duo-grid">
      <div class="ch-head" data-reveal>
        <p class="ch-num">Collection 03</p>
        <h2 class="ch-title">Pigeon</h2>
        <p class="ch-desc">Feeding and handling products for pigeon keepers.</p>
      </div>
{pig_plates}
    </div>
  </section>

  <section class="chapter editorial" id="accessories" data-tone="accessories">
    <div class="wrap">
      <div class="ch-head ed-head" data-reveal>
        <p class="ch-num">Collection 04</p>
        <h2 class="ch-title">Toys &amp; accessories</h2>
        <p class="ch-desc">Cuttlebone holders, feeders, hand-feeding tools, cages and cage tools, and toys. Breeding boxes on request.</p>
      </div>
{acc_groups}
    </div>
  </section>

  <section class="chapter reel" id="smallpets" data-tone="smallpets">
    <div class="wrap reel-head" data-reveal>
      <div class="ch-head">
        <p class="ch-num">Collection 05</p>
        <h2 class="ch-title">Small pets</h2>
        <p class="ch-desc">Hamster, rabbit and sugar glider cages, wheels and care.</p>
      </div>
      <div class="reel-nav"><button type="button" class="rn-btn" data-dir="-1" aria-label="Previous products">&#8592;</button><button type="button" class="rn-btn" data-dir="1" aria-label="Next products">&#8594;</button></div>
    </div>
    <div class="reel-track" tabindex="0" aria-label="Small pet products (scrolls sideways)">
{sp_plates}
    </div>
  </section>

</div>

<!-- WHOLESALE -->
<section class="wholesale" id="wholesale">
  <div class="wrap ws-top" data-reveal>
    <p class="idx light">Wholesale &mdash; our main business</p>
    <h2 class="ws-h">Stock the <em>whole range.</em></h2>
    <p class="ws-sub">Pet shops, breeders, resellers and distributors: send your product list and quantities on WhatsApp. Pricing and order terms are shared on enquiry.</p>
    <div class="cta">
      <a class="btn btn-y btn-l" href="{WHOLESALE}" target="_blank" rel="noopener"><span>Wholesale Enquiry</span></a>
      <a class="btn btn-o btn-l" href="{CAT}" target="_blank" rel="noopener"><span>Open WhatsApp catalogue &#8599;</span></a>
    </div>
  </div>
  <div class="wall" aria-hidden="true">
    <div class="wall-row">{wall_row(wall_items[:half])}</div>
    <div class="wall-row rev">{wall_row(wall_items[half:])}</div>
  </div>
  <div class="wrap ws-grid">
    <ol class="steps">
      <li data-reveal><b>01</b><span>Send your product list and quantities.</span></li>
      <li data-reveal><b>02</b><span>We reply with availability and pricing.</span></li>
      <li data-reveal><b>03</b><span>Confirm your order details with us directly.</span></li>
    </ol>
    <form class="slip" id="slip" data-reveal aria-label="Wholesale enquiry">
      <p class="slip-h">Wholesale enquiry <span>via WhatsApp</span></p>
      <label>Business name<input name="biz" autocomplete="organization" placeholder="Your shop or company"></label>
      <label>Location<input name="loc" autocomplete="address-level2" placeholder="City / area"></label>
      <label>Products required<textarea name="prod" rows="3" placeholder="e.g. NutriBird A19 800 g, feeder cups"></textarea></label>
      <label>Approximate quantity<input name="qty" placeholder="Optional"></label>
      <a class="btn btn-y btn-l" id="slip-go" href="{WHOLESALE}" target="_blank" rel="noopener"><span>Send on WhatsApp &#8599;</span></a>
      <p class="slip-n">Opens WhatsApp with your details filled in. Nothing is stored on this site.</p>
    </form>
  </div>
</section>
<section class="retail">
  <div class="wrap retail-in" data-reveal>
    <p><b>Retail</b> &mdash; buying in smaller quantities? Ask about product availability.</p>
    <div class="cta">
      <a class="btn btn-d" href="{RETAIL}" target="_blank" rel="noopener"><span>Retail Enquiry</span></a>
      <a class="btn btn-line" href="tel:{CALL}"><span>Call us</span></a>
    </div>
  </div>
</section>

<!-- VISIT / CONTACT -->
<section class="contact" id="contact">
  <div class="wrap">
    <p class="idx light" data-reveal>Visit &amp; contact</p>
    <div class="numbers" data-reveal>
      <a class="phone" href="tel:{CALL}"><small>Call</small>98845 55888</a>
      <a class="phone phone-wa" href="{WA}" target="_blank" rel="noopener"><small>WhatsApp</small>98849 88877</a>
    </div>
    <div class="cta" data-reveal>
      <a class="btn btn-y" href="{WHOLESALE}" target="_blank" rel="noopener"><span>Wholesale Enquiry</span></a>
      <a class="btn btn-o" href="{RETAIL}" target="_blank" rel="noopener"><span>Retail Enquiry</span></a>
      <a class="btn btn-o" href="{IG}" target="_blank" rel="noopener"><span>Instagram &#8599;</span></a>
    </div>
    <div class="places">
      <article class="place" data-reveal>
        <p class="place-k">Shop</p>
        <p class="place-a">No. 13, School Road,<br>Kolathur, Chennai &ndash; 600 099</p>
        <a href="https://www.google.com/maps/search/?api=1&amp;query=No.+13+School+Road+Kolathur+Chennai+600099" target="_blank" rel="noopener">Open in Google Maps &#8599;</a>
      </article>
      <article class="place" data-reveal>
        <p class="place-k">Warehouse (Gowdown)</p>
        <p class="place-a">No. 10, Kasthuri 1st Street, Kadappa Road,<br>Kolathur, Chennai &ndash; 600 099</p>
        <a href="https://www.google.com/maps/search/?api=1&amp;query=No.+10+Kasthuri+1st+Street+Kadappa+Road+Kolathur+Chennai+600099" target="_blank" rel="noopener">Open in Google Maps &#8599;</a>
      </article>
    </div>
    <div class="map" id="map" data-src="https://www.google.com/maps?q=No.+13+School+Road+Kolathur+Chennai+600099&amp;output=embed">
      <div class="map-state" id="map-state"><p>Shop location, Kolathur</p><button class="btn btn-y" id="map-load" type="button"><span>Load map</span></button></div>
    </div>
  </div>
</section>

</main>

<footer class="foot">
  <div class="wrap foot-grid">
    <div><img src="assets/logo-wordmark.webp" width="837" height="254" alt="G K Pets" class="foot-logo" loading="lazy"><p>Imported pet products &ndash; wholesale and retail. Kolathur, Chennai.</p></div>
    <nav aria-label="Footer"><a href="#collection">Collection</a><a href="#nutrition">Bird nutrition</a><a href="#accessories">Accessories</a><a href="#wholesale">Wholesale</a><a href="#contact">Visit</a></nav>
    <div class="foot-c"><a href="tel:{CALL}">Call 98845 55888</a><a href="{WA}" target="_blank" rel="noopener">WhatsApp 98849 88877</a><a href="{CAT}" target="_blank" rel="noopener">WhatsApp catalogue</a><a href="{IG}" target="_blank" rel="noopener">Instagram</a></div>
  </div>
  <p class="wrap legal">&copy; <span id="yr">2026</span> G K Pets. All rights reserved.</p>
</footer>

<div class="dock" role="group" aria-label="Quick contact">
  <a class="dock-call" href="tel:{CALL}">Call</a>
  <a class="dock-wa" href="{WHOLESALE}" target="_blank" rel="noopener">WhatsApp</a>
</div>

<script src="js/main.js" defer></script>
</body>
</html>
'''

with open(os.path.join(SITE, "index.html"), "w") as f:
    f.write(page)
print("wrote index.html:", len(prods), "catalogue products +3 poster packs")
