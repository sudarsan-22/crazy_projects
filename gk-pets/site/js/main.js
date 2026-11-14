(function () {
  'use strict';
  var d = document, root = d.documentElement, win = window;
  var reduce = win.matchMedia('(prefers-reduced-motion: reduce)').matches;
  var finePointer = win.matchMedia('(hover: hover) and (pointer: fine)').matches;

  /* ---------- Navigation ---------- */
  var nav = d.querySelector('.nav'), burger = d.querySelector('.burger'), sheet = d.getElementById('sheet');
  function onNav() { nav.classList.toggle('solid', win.scrollY > 40); }
  onNav(); win.addEventListener('scroll', onNav, { passive: true });
  function setMenu(open) {
    d.body.classList.toggle('menu-open', open); d.body.classList.toggle('lock', open);
    burger.setAttribute('aria-expanded', open); burger.setAttribute('aria-label', open ? 'Close menu' : 'Open menu');
    sheet.setAttribute('aria-hidden', !open);
  }
  burger.addEventListener('click', function () { setMenu(!d.body.classList.contains('menu-open')); });
  sheet.querySelectorAll('a').forEach(function (a) { a.addEventListener('click', function () { setMenu(false); }); });
  d.addEventListener('keydown', function (e) { if (e.key === 'Escape') setMenu(false); });

  /* ---------- Scroll reveals ---------- */
  if (!reduce && 'IntersectionObserver' in win) {
    root.classList.add('rv');
    var io = new IntersectionObserver(function (es) {
      es.forEach(function (e) { if (e.isIntersecting) { e.target.classList.add('in'); io.unobserve(e.target); } });
    }, { rootMargin: '0px 0px -8% 0px', threshold: 0.05 });
    d.querySelectorAll('[data-reveal], .grp-grid .plate, .stagger .plate, .duo-grid .plate, .reel-track .plate').forEach(function (el) { io.observe(el); });
  }

  /* ---------- Catalogue tone: background morphs as each collection reaches mid-screen ---------- */
  var cat = d.getElementById('catalogue');
  if (cat && 'IntersectionObserver' in win) {
    var tio = new IntersectionObserver(function (es) {
      es.forEach(function (e) { if (e.isIntersecting) cat.setAttribute('data-tone', e.target.getAttribute('data-tone')); });
    }, { rootMargin: '-50% 0px -50% 0px' });
    cat.querySelectorAll('.chapter[data-tone]').forEach(function (s) { tio.observe(s); });
  }

  /* ---------- Hero: pointer parallax on the floating packs ---------- */
  var stage = d.getElementById('stage');
  if (stage && finePointer && !reduce) {
    var hero = d.getElementById('hero'), pending = 0, mx = 0, my = 0;
    hero.addEventListener('mousemove', function (e) {
      var r = hero.getBoundingClientRect();
      mx = ((e.clientX - r.left) / r.width - 0.5) * 2; my = ((e.clientY - r.top) / r.height - 0.5) * 2;
      if (!pending) pending = requestAnimationFrame(function () {
        stage.style.setProperty('--mx', mx.toFixed(3)); stage.style.setProperty('--my', my.toFixed(3)); pending = 0;
      });
    });
    hero.addEventListener('mouseleave', function () { stage.style.setProperty('--mx', 0); stage.style.setProperty('--my', 0); });
  }

  /* ---------- Collection 01: vertical scroll drives a horizontal product story (desktop only) ---------- */
  var pin = d.querySelector('.pin'), mqPin = win.matchMedia('(min-width: 1101px)');
  var track = pin && pin.querySelector('.track'), bar = pin && pin.querySelector('.ch-progress i');
  var plates = track ? [].slice.call(track.querySelectorAll('.plate')) : [], dist = 0, ticking = false;
  function layoutPin() {
    if (!pin) return;
    var on = mqPin.matches && !reduce;
    root.classList.toggle('pinned', on);
    if (!on) { pin.style.height = ''; track.style.transform = ''; plates.forEach(function (p) { p.style.opacity = ''; }); return; }
    track.style.transform = 'translate3d(0,0,0)';
    dist = Math.max(0, track.scrollWidth - track.clientWidth);
    pin.style.height = (win.innerHeight + dist) + 'px';
    runPin();
  }
  function runPin() {
    ticking = false;
    if (!root.classList.contains('pinned')) return;
    var r = pin.getBoundingClientRect(), p = Math.min(1, Math.max(0, -r.top / (dist || 1)));
    track.style.transform = 'translate3d(' + (-p * dist).toFixed(1) + 'px,0,0)';
    if (bar) bar.style.transform = 'scaleX(' + p.toFixed(3) + ')';
    var vw = win.innerWidth;
    plates.forEach(function (pl) {          // plates fade in from the right edge
      var b = pl.getBoundingClientRect(), t = (vw - b.left) / (vw * 0.25);
      pl.style.opacity = Math.min(1, Math.max(0.15, t)).toFixed(2);
    });
  }
  if (pin) {
    win.addEventListener('scroll', function () { if (!ticking) { ticking = true; requestAnimationFrame(runPin); } }, { passive: true });
    win.addEventListener('resize', layoutPin);
    win.addEventListener('load', layoutPin);
    if (mqPin.addEventListener) mqPin.addEventListener('change', layoutPin);
    layoutPin();
  }

  /* ---------- Collection 05: reel buttons + drag to scroll ---------- */
  var reel = d.querySelector('.reel-track');
  if (reel) {
    d.querySelectorAll('.rn-btn').forEach(function (b) {
      b.addEventListener('click', function () {
        reel.scrollBy({ left: Number(b.getAttribute('data-dir')) * reel.clientWidth * 0.8, behavior: reduce ? 'auto' : 'smooth' });
      });
    });
    if (finePointer) {
      var down = false, sx = 0, sl = 0, moved = false;
      reel.addEventListener('pointerdown', function (e) { if (e.button !== 0) return; down = true; moved = false; sx = e.clientX; sl = reel.scrollLeft; });
      win.addEventListener('pointermove', function (e) {
        if (!down) return;
        var dx = e.clientX - sx;
        if (Math.abs(dx) > 5) { moved = true; reel.classList.add('drag'); }
        if (moved) reel.scrollLeft = sl - dx;
      });
      win.addEventListener('pointerup', function () { down = false; reel.classList.remove('drag'); });
      reel.addEventListener('click', function (e) { if (moved) { e.preventDefault(); moved = false; } }, true);
    }
  }

  /* ---------- Wholesale enquiry slip -> prefilled WhatsApp (nothing stored or sent by this site) ---------- */
  var slip = d.getElementById('slip'), go = d.getElementById('slip-go');
  if (slip && go) {
    var build = function () {
      var f = slip.elements, v = function (n) { return (f[n].value || '').trim(); };
      var t = 'Hello G K Pets, I would like to make a wholesale enquiry.\n\nBusiness name: ' + v('biz') +
        '\nLocation: ' + v('loc') + '\nProducts required: ' + v('prod') + '\nApproximate quantity: ' + v('qty');
      go.href = 'https://wa.me/919884988877?text=' + encodeURIComponent(t);
    };
    slip.addEventListener('input', build);
    slip.addEventListener('submit', function (e) { e.preventDefault(); build(); win.open(go.href, '_blank', 'noopener'); });
  }

  /* ---------- Map on demand, with loading + failure states ---------- */
  var map = d.getElementById('map'), state = d.getElementById('map-state'), load = d.getElementById('map-load');
  function fail() {
    state.innerHTML = '<p>The map could not be loaded.</p><a class="btn btn-y" target="_blank" rel="noopener" href="https://www.google.com/maps/search/?api=1&query=No.+13+School+Road+Kolathur+Chennai+600099"><span>Open in Google Maps</span></a>';
    state.hidden = false;
  }
  if (load) load.addEventListener('click', function () {
    state.innerHTML = '<p>Loading map…</p>';
    var f = d.createElement('iframe'), done = false;
    f.title = 'Map showing the G K Pets shop in Kolathur, Chennai';
    f.loading = 'lazy'; f.referrerPolicy = 'no-referrer-when-downgrade'; f.src = map.dataset.src;
    f.addEventListener('load', function () { done = true; state.hidden = true; });
    f.addEventListener('error', fail);
    map.appendChild(f);
    setTimeout(function () { if (!done) fail(); }, 10000);
  });

  var y = d.getElementById('yr'); if (y) y.textContent = new Date().getFullYear();
})();
