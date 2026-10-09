/* Woodward Sports Network — preview site */
(function () {
  'use strict';
  var d = document, root = d.documentElement;
  var RM = root.classList.contains('rm');
  var $ = function (s, c) { return (c || d).querySelector(s); };
  var $$ = function (s, c) { return Array.prototype.slice.call((c || d).querySelectorAll(s)); };

  /* ---------- header, progress, parallax ---------- */
  var hdr = $('[data-hdr]'), tabs = $('.tabs'), wall = $('.wall'), phone = $('.phone'), marquee = $('.loud__marquee');
  var bar = d.createElement('div'); bar.className = 'progress'; d.body.appendChild(bar);
  var lastY = scrollY, ticking = false;
  function onScroll() {
    var y = scrollY, max = d.documentElement.scrollHeight - innerHeight;
    hdr.classList.toggle('is-solid', y > 20);
    if (!d.body.classList.contains('menu-open')) hdr.classList.toggle('is-hidden', y > 420 && y > lastY + 2);
    if (y < lastY - 2) hdr.classList.remove('is-hidden');
    bar.style.setProperty('--sp', max > 0 ? (y / max).toFixed(4) : 0);
    if (!RM) {
      if (wall && y < innerHeight * 1.2) wall.style.transform = 'translateY(' + (y * 0.35).toFixed(1) + 'px)';
      if (phone) { var r = phone.getBoundingClientRect(); if (r.bottom > 0 && r.top < innerHeight) phone.style.setProperty('--py', ((r.top + r.height / 2 - innerHeight / 2) * -0.08).toFixed(1) + 'px'); }
      if (marquee) { var m = marquee.getBoundingClientRect(); if (m.bottom > 0 && m.top < innerHeight) marquee.style.setProperty('--mx', ((m.top - innerHeight) * 0.35).toFixed(1) + 'px'); }
    }
    lastY = y; ticking = false;
  }
  addEventListener('scroll', function () { if (!ticking) { ticking = true; requestAnimationFrame(onScroll); } }, { passive: true });
  onScroll();

  /* ---------- menu ---------- */
  var burger = $('[data-burger]'), menu = $('[data-menu]');
  function setMenu(open) {
    burger.setAttribute('aria-expanded', open);
    burger.setAttribute('aria-label', open ? 'Close menu' : 'Open menu');
    d.body.classList.toggle('menu-open', open);
    d.body.style.overflow = open ? 'hidden' : '';
    if (open) { menu.hidden = false; hdr.classList.remove('is-hidden'); hdr.classList.add('is-solid'); requestAnimationFrame(function () { menu.classList.add('is-open'); }); }
    else { menu.classList.remove('is-open'); menu.hidden = true; onScroll(); }
  }
  burger.addEventListener('click', function () { setMenu(burger.getAttribute('aria-expanded') !== 'true'); });
  $$('a', menu).forEach(function (a) { a.addEventListener('click', function () { setMenu(false); }); });
  d.addEventListener('keydown', function (e) { if (e.key === 'Escape' && d.body.classList.contains('menu-open')) { setMenu(false); burger.focus(); } });

  /* ---------- live schedule (America/Detroit) ---------- */
  var SCHED = window.WSN_SCHEDULE || [];
  var fmt = new Intl.DateTimeFormat('en-US', { timeZone: 'America/Detroit', weekday: 'short', hour: 'numeric', minute: 'numeric', second: 'numeric', hourCycle: 'h23' });
  var DAYS = { Sun: 0, Mon: 1, Tue: 2, Wed: 3, Thu: 4, Fri: 5, Sat: 6 };
  function detroitNow() {
    var p = {}; fmt.formatToParts(new Date()).forEach(function (x) { p[x.type] = x.value; });
    return { day: DAYS[p.weekday], h: +p.hour % 24, m: +p.minute, s: +p.second };
  }
  function hm(sec) {
    var h = Math.floor(sec / 3600), m = Math.floor(sec % 3600 / 60), s = sec % 60;
    return h ? h + 'h ' + (m < 10 ? '0' : '') + m + 'm' : m + 'm ' + (s < 10 ? '0' : '') + s + 's';
  }
  function clock(t) {
    var h = t.h % 12 || 12;
    return h + ':' + (t.m < 10 ? '0' : '') + t.m + ' ' + (t.h < 12 ? 'AM' : 'PM') + ' ET';
  }
  function hourLabel(h) { return (h % 12 || 12) + (h < 12 ? ' AM' : ' PM'); }
  var oa = $('[data-onair]'), pill = $('[data-pill]'), pillText = $('[data-pill-text]');
  var nowLine = $('.tl__now');
  function live() {
    var t = detroitNow(), secs = t.h * 3600 + t.m * 60 + t.s, wk = t.day >= 1 && t.day <= 5;
    var cur = null, next = null, nextLabel = '';
    if (wk) {
      SCHED.forEach(function (s) { if (secs >= s.start * 3600 && secs < s.end * 3600) cur = s; });
      if (!cur) for (var i = 0; i < SCHED.length; i++) if (secs < SCHED[i].start * 3600) { next = SCHED[i]; break; }
    }
    if (!cur && !next) {
      next = SCHED[0];
      var add = t.day === 5 ? 3 : t.day === 6 ? 2 : 1;
      if (!wk && t.day === 0) add = 1;
      nextLabel = (add === 1 && t.day !== 0 && t.day !== 6 ? 'Tomorrow ' : 'Monday ') + hourLabel(next.start) + ' ET';
      if (t.day === 0 || t.day === 6 || t.day === 5) nextLabel = 'Monday ' + hourLabel(next.start) + ' ET';
    }
    oa.classList.toggle('is-off', !cur);
    pill.classList.toggle('is-off', !cur);
    $('[data-oa-clock]', oa).textContent = clock(t);
    if (cur) {
      var len = (cur.end - cur.start) * 3600, done = secs - cur.start * 3600;
      $('[data-oa-state]', oa).lastChild.textContent = 'On air now';
      $('[data-oa-show]', oa).textContent = cur.name;
      $('[data-oa-hosts]', oa).textContent = cur.hosts;
      $('[data-oa-bar]', oa).parentNode.style.setProperty('--p', (done / len * 100).toFixed(2) + '%');
      $('[data-oa-bar]', oa).style.width = (done / len * 100).toFixed(2) + '%';
      $('[data-oa-count]', oa).textContent = 'Live until ' + hourLabel(cur.end) + ' ET · ' + hm(len - done) + ' left';
      pillText.textContent = 'Live now';
    } else {
      $('[data-oa-state]', oa).lastChild.textContent = 'Off air · Up next';
      $('[data-oa-show]', oa).textContent = next.name;
      $('[data-oa-hosts]', oa).textContent = next.hosts;
      $('[data-oa-bar]', oa).style.width = '0%';
      $('[data-oa-count]', oa).textContent = nextLabel ? nextLabel : 'Starts in ' + hm(next.start * 3600 - secs) + ' · ' + hourLabel(next.start) + ' ET';
      pillText.textContent = 'Watch';
    }
    $$('[data-show]').forEach(function (el) {
      var slug = el.getAttribute('data-show');
      el.classList.toggle('is-live', !!cur && cur.slug === slug);
      el.classList.toggle('is-next', !cur && next && next.slug === slug && !el.classList.contains('tl__block'));
      var st = $('[data-state]', el);
      if (st) st.textContent = cur && cur.slug === slug ? 'Live now' : (!cur && next && next.slug === slug ? 'Up next' : '');
    });
    if (nowLine) {
      var inDay = wk && secs >= 8 * 3600 && secs < 19 * 3600;
      nowLine.hidden = !inDay;
      if (inDay) nowLine.style.setProperty('--p', ((secs - 8 * 3600) / (11 * 3600) * 100).toFixed(2) + '%');
    }
  }
  if (oa && SCHED.length) { live(); setInterval(live, 1000); }
  var tl = $('[data-tl]');
  if (tl && nowLine && !nowLine.hidden && tl.scrollWidth > tl.clientWidth) tl.scrollLeft = nowLine.offsetLeft - tl.clientWidth * 0.45;

  /* ---------- reveal ---------- */
  var rv = $$('.rv');
  if ('IntersectionObserver' in window && !RM) {
    var io = new IntersectionObserver(function (es) {
      es.forEach(function (e) { if (e.isIntersecting) { e.target.classList.add('in'); io.unobserve(e.target); } });
    }, { rootMargin: '0px 0px -8% 0px', threshold: 0.08 });
    rv.forEach(function (el) { io.observe(el); });
  } else rv.forEach(function (el) { el.classList.add('in'); });

  /* ---------- hero counters ---------- */
  if (!RM) $$('[data-count]').forEach(function (el) {
    var to = +el.getAttribute('data-count'), suf = el.getAttribute('data-suffix') || '', t0 = null;
    el.textContent = '0' + suf;
    setTimeout(function () {
      requestAnimationFrame(function step(ts) {
        if (!t0) t0 = ts;
        var k = Math.min(1, (ts - t0) / 1600), e = 1 - Math.pow(1 - k, 4);
        el.textContent = Math.round(to * e) + suf;
        if (k < 1) requestAnimationFrame(step);
      });
    }, 1150);
  });

  /* ---------- story filter ---------- */
  var chips = $$('.chip'), stories = $$('.story'), empty = $('.stories__empty');
  function filter(key) {
    chips.forEach(function (c) { var on = c.getAttribute('data-filter') === key; c.classList.toggle('is-on', on); c.setAttribute('aria-pressed', on); });
    var n = 0;
    stories.forEach(function (s) {
      var show = key === 'all' || (' ' + s.getAttribute('data-teams') + ' ').indexOf(' ' + key + ' ') > -1;
      s.classList.toggle('is-hide', !show);
      s.classList.remove('is-pop');
      if (show) { s.style.setProperty('--n', n++); s.classList.add('in'); void s.offsetWidth; s.classList.add('is-pop'); }
    });
    if (empty) empty.hidden = n > 0;
  }
  chips.forEach(function (c) { c.addEventListener('click', function () { filter(c.getAttribute('data-filter')); }); });
  $$('.team[data-filter]').forEach(function (t) { t.addEventListener('click', function () { filter(t.getAttribute('data-filter')); }); });

  /* ---------- video player ---------- */
  var dlg = $('[data-player]'), frame = $('[data-player-frame]');
  function openVideo(id, title) {
    frame.innerHTML = '<iframe src="https://www.youtube-nocookie.com/embed/' + id + '?autoplay=1&rel=0&playsinline=1" title="' + (title || 'Video').replace(/"/g, '&quot;') + '" allow="autoplay; encrypted-media; picture-in-picture; fullscreen" allowfullscreen></iframe>';
    if (dlg.showModal) dlg.showModal(); else dlg.setAttribute('open', '');
    d.body.style.overflow = 'hidden';
  }
  function closeVideo() { if (dlg.open) dlg.close(); }
  dlg.addEventListener('close', function () { frame.innerHTML = ''; d.body.style.overflow = ''; });
  dlg.addEventListener('click', function (e) { if (e.target === dlg) closeVideo(); });
  $('[data-player-close]').addEventListener('click', closeVideo);
  $$('[data-yt]').forEach(function (b) { b.addEventListener('click', function () { openVideo(b.getAttribute('data-yt'), b.getAttribute('data-title')); }); });

  /* ---------- drag-to-scroll rails (mouse only) ---------- */
  $$('[data-rail]').forEach(function (r) {
    var down = false, sx = 0, sl = 0, moved = false;
    r.addEventListener('pointerdown', function (e) { if (e.pointerType !== 'mouse') return; down = true; moved = false; sx = e.clientX; sl = r.scrollLeft; });
    addEventListener('pointermove', function (e) {
      if (!down) return;
      var dx = e.clientX - sx;
      if (Math.abs(dx) > 5) { moved = true; r.classList.add('is-drag'); }
      if (moved) r.scrollLeft = sl - dx;
    });
    addEventListener('pointerup', function () { if (!down) return; down = false; setTimeout(function () { r.classList.remove('is-drag'); }, 0); });
    r.addEventListener('click', function (e) { if (moved) { e.preventDefault(); e.stopPropagation(); moved = false; } }, true);
  });

  /* ---------- active section → nav + tabs ---------- */
  var links = $$('.hdr__nav a, .tabs a');
  var secs = $$('main section[id]');
  if ('IntersectionObserver' in window) {
    var so = new IntersectionObserver(function (es) {
      es.forEach(function (e) {
        if (!e.isIntersecting) return;
        var id = e.target.id;
        links.forEach(function (a) { a.classList.toggle('is-on', a.getAttribute('href') === '#' + id); });
      });
    }, { rootMargin: '-45% 0px -50% 0px' });
    secs.forEach(function (s) { so.observe(s); });
  }

  /* ---------- magnetic buttons (fine pointers) ---------- */
  if (!RM && matchMedia('(hover: hover) and (pointer: fine)').matches) {
    $$('.btn--lg, .feature__play').forEach(function (b) {
      b.addEventListener('pointermove', function (e) {
        var r = b.getBoundingClientRect(), x = (e.clientX - r.left - r.width / 2) * 0.18, y = (e.clientY - r.top - r.height / 2) * 0.25;
        b.style.translate = x.toFixed(1) + 'px ' + y.toFixed(1) + 'px';
      });
      b.addEventListener('pointerleave', function () { b.style.translate = ''; });
    });
  }
})();
