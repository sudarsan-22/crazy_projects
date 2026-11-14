/* KC Customs v3: minimalist showroom interaction layer (no dependencies) */
(function () {
  'use strict';
  var PHONE = '919677184462';
  var doc = document.documentElement;
  var reduce = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  var $ = function (s, c) { return (c || document).querySelector(s); };
  var $$ = function (s, c) { return Array.prototype.slice.call((c || document).querySelectorAll(s)); };
  var wa = function (msg) { return 'https://wa.me/' + PHONE + '?text=' + encodeURIComponent(msg); };

  /* ---------- intro + hero start (waits for fonts → no layout shift) ---------- */
  var hero = $('.hero'), heroStarted = false;
  function startHero() {
    if (!hero || heroStarted) return;
    var go = function () { if (heroStarted) return; heroStarted = true; requestAnimationFrame(function () { hero.classList.add('go'); countUp(); }); };
    if (document.fonts && document.fonts.ready) { document.fonts.ready.then(go); setTimeout(go, 1200); } else { go(); }
  }
  if (doc.classList.contains('intro')) {
    try { sessionStorage.setItem('kc-intro', '1'); } catch (e) {}
    setTimeout(function () {
      doc.classList.add('intro-out'); startHero();
      setTimeout(function () { doc.classList.remove('intro', 'intro-out'); }, 700);
    }, 1050);
  } else { startHero(); }

  /* ---------- hero stats count-up ---------- */
  function countUp() {
    if (reduce) return;
    $$('.stats [data-count]').forEach(function (el) {
      var end = +el.getAttribute('data-count'), suf = el.getAttribute('data-suffix') || '', t0 = null;
      (function step(t) {
        if (!t0) t0 = t;
        var k = Math.min(1, (t - t0) / 1300);
        el.textContent = Math.round(end * (1 - Math.pow(1 - k, 3))) + suf;
        if (k < 1) requestAnimationFrame(step);
      })(performance.now());
    });
  }

  /* ---------- WhatsApp links ---------- */
  $$('[data-wa]').forEach(function (a) { a.href = wa(a.getAttribute('data-wa')); a.target = '_blank'; a.rel = 'noopener'; });

  /* ---------- nav + menu ---------- */
  var nav = $('.nav'), menu = $('#menu'), menuBtn = $('.menu-btn'), menuLabel = $('.menu-btn-t');
  function setMenu(open) {
    menu.classList.toggle('open', open);
    menu.setAttribute('aria-hidden', String(!open));
    menuBtn.setAttribute('aria-expanded', String(open));
    menuLabel.textContent = open ? 'Close' : 'Menu';
    document.body.classList.toggle('menu-open', open);
    $$('a', menu).forEach(function (a) { a.setAttribute('tabindex', open ? '0' : '-1'); });
    if (open) { var f = $('a', menu); if (f) setTimeout(function () { f.focus(); }, 120); }
  }
  if (menu && menuBtn) {
    $$('a', menu).forEach(function (a) { a.setAttribute('tabindex', '-1'); a.addEventListener('click', function () { setMenu(false); }); });
    menuBtn.addEventListener('click', function () { setMenu(!menu.classList.contains('open')); });
    document.addEventListener('keydown', function (e) { if (e.key === 'Escape' && menu.classList.contains('open')) { setMenu(false); menuBtn.focus(); } });
  }

  /* ---------- reveal ---------- */
  var rv = $$('.sec h2, .tile, .bc, .bc-more, .st, .ac-strip figure, .about-img, .dz-preview, .fam-row, .visit-in');
  rv.forEach(function (el) { el.classList.add('rv'); });
  if ('IntersectionObserver' in window && !reduce) {
    var io = new IntersectionObserver(function (es) {
      es.forEach(function (e) { if (e.isIntersecting) { e.target.classList.add('in'); io.unobserve(e.target); } });
    }, { threshold: 0.08, rootMargin: '0px 400px -4% 400px' });
    rv.forEach(function (el) { io.observe(el); });
  } else { rv.forEach(function (el) { el.classList.add('in'); }); }

  /* ---------- horizontal tracks: arrows, drag, progress ---------- */
  function setupTrack(track) {
    var id = track.id, bar = id ? $('.bar[data-for="' + id + '"] span') : null;
    var ctrl = id ? $('.rail-ctrl[data-for="' + id + '"]') : null;
    function update() {
      var max = track.scrollWidth - track.clientWidth;
      var p = max > 0 ? track.scrollLeft / max : 1;
      if (bar) bar.parentNode.style.setProperty('--p', Math.max(0.08, p).toFixed(3));
      if (ctrl) {
        $$('.arr', ctrl).forEach(function (b) {
          var d = +b.getAttribute('data-dir');
          b.disabled = d < 0 ? track.scrollLeft < 4 : track.scrollLeft > max - 4;
        });
      }
    }
    track.addEventListener('scroll', function () { requestAnimationFrame(update); }, { passive: true });
    window.addEventListener('resize', update);
    if (ctrl) $$('.arr', ctrl).forEach(function (b) {
      b.addEventListener('click', function () {
        track.scrollBy({ left: +b.getAttribute('data-dir') * track.clientWidth * 0.8, behavior: reduce ? 'auto' : 'smooth' });
      });
    });
    // mouse drag (desktop); touch uses native scrolling
    var down = false, moved = false, sx = 0, sl = 0;
    track.addEventListener('pointerdown', function (e) {
      if (e.pointerType !== 'mouse' || e.button !== 0) return;
      down = true; moved = false; sx = e.clientX; sl = track.scrollLeft;
    });
    window.addEventListener('pointermove', function (e) {
      if (!down) return;
      var dx = e.clientX - sx;
      if (!moved && Math.abs(dx) > 6) { moved = true; track.classList.add('dragging'); }
      if (moved) track.scrollLeft = sl - dx;
    });
    window.addEventListener('pointerup', function () {
      if (!down) return; down = false;
      if (moved) setTimeout(function () { track.classList.remove('dragging'); }, 0);
    });
    track.addEventListener('click', function (e) { if (moved) { e.preventDefault(); e.stopPropagation(); moved = false; } }, true);
    track.addEventListener('keydown', function (e) {
      if (e.target !== track) return;
      if (e.key === 'ArrowRight' || e.key === 'ArrowLeft') { e.preventDefault(); track.scrollBy({ left: (e.key === 'ArrowRight' ? 1 : -1) * 320, behavior: reduce ? 'auto' : 'smooth' }); }
    });
    update();
    return update;
  }
  var updaters = {};
  $$('.track').forEach(function (t) { var u = setupTrack(t); if (t.id) updaters[t.id] = u; });

  /* ---------- build filters ---------- */
  var bTrack = $('#builds-track');
  $$('.filters .chip').forEach(function (c) {
    c.addEventListener('click', function () {
      var f = c.getAttribute('data-filter');
      $$('.filters .chip').forEach(function (x) { var on = x === c; x.classList.toggle('is-on', on); x.setAttribute('aria-pressed', String(on)); });
      $$('.bc', bTrack).forEach(function (b) {
        var show = f === 'all' || b.getAttribute('data-tags').split(' ').indexOf(f) > -1;
        b.classList.toggle('is-hidden', !show);
        if (show) b.classList.add('in');
      });
      bTrack.scrollTo({ left: 0 });
      if (updaters['builds-track']) updaters['builds-track']();
    });
  });

  /* ---------- hover frame previews on build cards ---------- */
  $$('.bc-media[data-frames]').forEach(function (btn) {
    if (reduce) return;
    var names = btn.getAttribute('data-frames').split(','), frames = null, timer = null, k = -1;
    btn.addEventListener('mouseenter', function () {
      if (!window.matchMedia('(hover: hover)').matches) return;
      if (!frames) frames = names.map(function (n) {
        var im = new Image(); im.src = 'assets/media/' + n + '.webp'; im.alt = ''; im.className = 'pc-frame'; im.decoding = 'async';
        btn.insertBefore(im, btn.querySelector('.bc-cap')); return im;
      });
      timer = setInterval(function () { if (k >= 0) frames[k].classList.remove('on'); k = (k + 1) % frames.length; frames[k].classList.add('on'); }, 750);
    });
    btn.addEventListener('mouseleave', function () { clearInterval(timer); if (frames) frames.forEach(function (f) { f.classList.remove('on'); }); k = -1; });
  });

  /* ---------- process tabs ---------- */
  var tabs = $$('.tabs [role="tab"]');
  function selectTab(t) {
    tabs.forEach(function (x) {
      var on = x === t;
      x.classList.toggle('is-on', on); x.setAttribute('aria-selected', String(on)); x.tabIndex = on ? 0 : -1;
      var p = document.getElementById(x.getAttribute('aria-controls'));
      p.classList.toggle('is-on', on);
      if (on) { $$('.rv', p).forEach(function (el) { el.classList.add('in'); }); var tr = $('.track', p); if (tr) tr.scrollLeft = 0; }
    });
  }
  tabs.forEach(function (t, i) {
    t.addEventListener('click', function () { selectTab(t); });
    t.addEventListener('keydown', function (e) {
      if (e.key !== 'ArrowRight' && e.key !== 'ArrowLeft') return;
      var n = tabs[(i + (e.key === 'ArrowRight' ? 1 : tabs.length - 1)) % tabs.length]; selectTab(n); n.focus();
    });
  });

  /* ---------- design-your-bike configurator ---------- */
  var form = $('.dz-form');
  if (form) {
    var imgs = $$('.dz-img'), sum = $('.dz-sum');
    var val = function (n) { var r = form.querySelector('input[name="' + n + '"]:checked'); return r ? r.value : ''; };
    var refresh = function () {
      var bike = val('bike'), work = val('work'), fin = val('finish');
      sum.textContent = [bike === 'another bike or car' ? 'Your ride' : bike, work, fin.replace(' (your call)', '')].join(' · ');
      var k = (form.querySelector('input[name="work"]:checked') || {}).getAttribute ? form.querySelector('input[name="work"]:checked').getAttribute('data-k') : 'airbrush';
      imgs.forEach(function (im) {
        var on = im.getAttribute('data-k') === k;
        if (on && im.getAttribute('data-src')) { im.src = im.getAttribute('data-src'); im.removeAttribute('data-src'); }
        im.classList.toggle('is-on', on);
      });
    };
    form.addEventListener('change', refresh);
    form.addEventListener('submit', function (e) {
      e.preventDefault();
      var idea = form.idea.value.trim();
      var msg = 'Hi KC Customs, I want to design my bike.\n• Bike: ' + val('bike') + '\n• Work: ' + val('work') + '\n• Finish: ' + val('finish') + (idea ? '\n• Idea: ' + idea : '') + '\nI can send photos.';
      window.open(wa(msg), '_blank', 'noopener');
    });
    refresh();
  }

  /* ---------- scroll: nav state + hero parallax ---------- */
  var heroImgs = $$('.hp img'), desk = window.matchMedia('(min-width: 900px)'), ticking = false;
  function frame() {
    ticking = false;
    var y = window.scrollY;
    if (nav) nav.classList.toggle('solid', y > 40);
    if (!reduce && desk.matches && y < window.innerHeight * 1.2) heroImgs.forEach(function (im, i) { im.style.setProperty('--py', (y * [0.06, 0.12, 0.03][i]).toFixed(1) + 'px'); });
  }
  window.addEventListener('scroll', function () { if (!ticking) { ticking = true; requestAnimationFrame(frame); } }, { passive: true });
  frame();

  /* ---------- video dialog ---------- */
  var dlg = $('.vd'), dFrame = $('.vd-frame'), dTitle = $('.vd-title'), dYt = $('.vd-yt'), lastFocus = null;
  var ytUrl = function (id, f) { return (f === 'short' ? 'https://www.youtube.com/shorts/' : 'https://www.youtube.com/watch?v=') + id; };
  function openVideo(id, format, title) {
    if (!dlg || typeof dlg.showModal !== 'function') { window.open(ytUrl(id, format), '_blank', 'noopener'); return; }
    lastFocus = document.activeElement;
    dFrame.className = 'vd-frame ' + (format === 'short' ? 'is-short' : 'is-video');
    var f = document.createElement('iframe');
    f.src = 'https://www.youtube-nocookie.com/embed/' + id + '?autoplay=1&rel=0&playsinline=1&modestbranding=1';
    f.title = title || 'KC Customs video'; f.allow = 'autoplay; encrypted-media; picture-in-picture; fullscreen'; f.allowFullscreen = true;
    dFrame.innerHTML = ''; dFrame.appendChild(f);
    dTitle.textContent = title || ''; dYt.href = ytUrl(id, format);
    dlg.showModal(); document.body.classList.add('menu-open'); $('.vd-close', dlg).focus();
  }
  if (dlg) {
    dlg.addEventListener('close', function () { dFrame.innerHTML = ''; document.body.classList.remove('menu-open'); if (lastFocus && lastFocus.focus) lastFocus.focus(); });
    $('.vd-close', dlg).addEventListener('click', function () { dlg.close(); });
    dlg.addEventListener('click', function (e) { if (e.target === dlg) dlg.close(); });
  }
  document.addEventListener('click', function (e) {
    var t = e.target.closest('[data-video]');
    if (!t) return;
    e.preventDefault();
    openVideo(t.getAttribute('data-video'), t.getAttribute('data-format'), t.getAttribute('data-title'));
  });

  /* ---------- map: load on request ---------- */
  var map = $('.map');
  if (map) $('.map-btn', map).addEventListener('click', function () {
    var f = document.createElement('iframe');
    f.src = map.getAttribute('data-map'); f.title = 'KC Customs location on Google Maps'; f.loading = 'lazy'; f.referrerPolicy = 'no-referrer-when-downgrade';
    map.innerHTML = ''; map.appendChild(f); map.classList.add('loaded');
  });

  var yr = $('#yr'); if (yr) yr.textContent = new Date().getFullYear();
})();
