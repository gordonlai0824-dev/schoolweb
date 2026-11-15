/* 基道小學網站 — 前台互動 */
(function () {
  'use strict';
  var $ = function (s, r) { return (r || document).querySelector(s); };
  var $$ = function (s, r) { return Array.prototype.slice.call((r || document).querySelectorAll(s)); };
  var mobile = function () { return window.matchMedia('(max-width: 1000px)').matches; };

  /* ---------- 主選單 ---------- */
  var toggle = $('.nav-toggle'), nav = $('#main-nav');
  if (toggle && nav) {
    toggle.addEventListener('click', function () {
      // 選單由頁首下方開始，覆蓋整個畫面
      nav.style.top = Math.max(0, document.querySelector('.site-header').getBoundingClientRect().bottom) + 'px';
      var open = nav.classList.toggle('open');
      toggle.setAttribute('aria-expanded', open);
      toggle.setAttribute('aria-label', open ? '關閉選單' : '開啟選單');
      document.body.classList.toggle('nav-open', open);
    });
    $$('.nav-item > button.nav-link', nav).forEach(function (btn) {
      btn.addEventListener('click', function () {
        var item = btn.parentElement, open = !item.classList.contains('open');
        $$('.nav-item.open', nav).forEach(function (i) {
          if (i !== item) { i.classList.remove('open'); $('button', i).setAttribute('aria-expanded', 'false'); }
        });
        item.classList.toggle('open', open);
        btn.setAttribute('aria-expanded', open);
      });
    });
    // 點選選單連結後關閉手機選單
    $$('.dropdown a, a.nav-link', nav).forEach(function (a) {
      a.addEventListener('click', function () {
        nav.classList.remove('open'); document.body.classList.remove('nav-open');
        toggle.setAttribute('aria-expanded', 'false');
        $$('.nav-item.open', nav).forEach(function (i) { i.classList.remove('open'); });
      });
    });
    document.addEventListener('click', function (e) {
      if (!mobile() && !nav.contains(e.target)) {
        $$('.nav-item.open', nav).forEach(function (i) { i.classList.remove('open'); $('button', i).setAttribute('aria-expanded', 'false'); });
      }
    });
    document.addEventListener('keydown', function (e) {
      if (e.key !== 'Escape') return;
      var openItem = $('.nav-item.open', nav);
      if (openItem) { openItem.classList.remove('open'); var b = $('button', openItem); b.setAttribute('aria-expanded', 'false'); b.focus(); }
      else if (nav.classList.contains('open')) { toggle.click(); toggle.focus(); }
    });
  }

  /* ---------- 字體大小 ---------- */
  var root = document.documentElement;
  var fsBtns = $$('.fs-btn');
  function setFs(cls) {
    root.classList.remove('fs-lg', 'fs-xl');
    if (cls) root.classList.add(cls);
    fsBtns.forEach(function (b) { b.setAttribute('aria-pressed', b.dataset.fs === cls); });
    try { cls ? localStorage.setItem('kt-fs', cls) : localStorage.removeItem('kt-fs'); } catch (e) {}
  }
  fsBtns.forEach(function (b) { b.addEventListener('click', function () { setFs(b.dataset.fs); }); });
  setFs(root.classList.contains('fs-xl') ? 'fs-xl' : root.classList.contains('fs-lg') ? 'fs-lg' : '');

  /* ---------- 分頁標籤 ---------- */
  $$('[role="tablist"]').forEach(function (list) {
    var tabs = $$('[role="tab"]', list);
    function select(tab, focus) {
      tabs.forEach(function (t) {
        var on = t === tab;
        t.setAttribute('aria-selected', on);
        t.tabIndex = on ? 0 : -1;
        var panel = document.getElementById(t.getAttribute('aria-controls'));
        if (panel) panel.hidden = !on;
      });
      if (focus) tab.focus();
    }
    tabs.forEach(function (t, i) {
      t.addEventListener('click', function () { select(t); });
      t.addEventListener('keydown', function (e) {
        var n = e.key === 'ArrowRight' ? 1 : e.key === 'ArrowLeft' ? -1 : 0;
        if (n) { e.preventDefault(); select(tabs[(i + n + tabs.length) % tabs.length], true); }
      });
    });
  });

  /* ---------- 學生成就篩選 ---------- */
  $$('[data-filter-group]').forEach(function (group) {
    var target = group.parentElement.querySelector('[data-filter-target]');
    var empty = group.parentElement.querySelector('.filter-empty');
    var yearSel = $('[data-filter-year]', group);
    var cat = '';
    function apply() {
      var year = yearSel ? yearSel.value : '', shown = 0;
      $$('[data-cat]', target).forEach(function (el) {
        var ok = (!cat || el.dataset.cat === cat) && (!year || el.dataset.year === year);
        el.classList.toggle('is-hidden', !ok);
        if (ok) shown++;
      });
      if (empty) empty.hidden = shown > 0;
    }
    $$('button[data-filter]', group).forEach(function (b) {
      b.addEventListener('click', function () {
        cat = b.dataset.filter;
        $$('button[data-filter]', group).forEach(function (x) { x.setAttribute('aria-pressed', x === b); });
        apply();
      });
    });
    if (yearSel) yearSel.addEventListener('change', apply);
  });

  /* ---------- 內頁側欄：目前位置 ---------- */
  var subLinks = $$('.subnav a');
  if (subLinks.length && 'IntersectionObserver' in window) {
    var map = {};
    subLinks.forEach(function (a) { map[a.getAttribute('href').slice(1)] = a; });
    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (en) {
        if (en.isIntersecting && map[en.target.id]) {
          subLinks.forEach(function (a) { a.classList.remove('active'); });
          map[en.target.id].classList.add('active');
          if (mobile()) map[en.target.id].scrollIntoView({ block: 'nearest', inline: 'center' });
        }
      });
    }, { rootMargin: '-30% 0px -60% 0px' });
    $$('.page-content > section[id]').forEach(function (s) { io.observe(s); });
  }

  /* ---------- 進場動畫 ---------- */
  var reveals = $$('.reveal');
  if ('IntersectionObserver' in window) {
    var ro = new IntersectionObserver(function (entries) {
      entries.forEach(function (en) { if (en.isIntersecting) { en.target.classList.add('in'); ro.unobserve(en.target); } });
    }, { rootMargin: '0px 0px -8% 0px' });
    reveals.forEach(function (el) { ro.observe(el); });
  } else { reveals.forEach(function (el) { el.classList.add('in'); }); }

  /* ---------- 返回頁首 ---------- */
  var top = $('.back-top');
  if (top) {
    window.addEventListener('scroll', function () { top.classList.toggle('show', window.scrollY > 600); }, { passive: true });
    top.addEventListener('click', function () { window.scrollTo({ top: 0 }); var m = $('#main'); if (m) m.focus({ preventScroll: true }); });
  }

  /* ---------- 影片彈窗 ---------- */
  $$('[data-video]').forEach(function (btn) {
    btn.addEventListener('click', function () {
      var dlg = document.createElement('dialog');
      dlg.className = 'video-dialog';
      dlg.setAttribute('aria-label', '影片');
      dlg.innerHTML = '<button type="button" class="vd-close" aria-label="關閉影片">×</button>' +
        '<div class="vd-frame"><iframe allow="autoplay; encrypted-media; picture-in-picture" allowfullscreen title="影片"></iframe></div>';
      var src = btn.dataset.video;
      $('iframe', dlg).src = src + (src.indexOf('?') > -1 ? '&' : '?') + 'autoplay=1';
      document.body.appendChild(dlg);
      dlg.addEventListener('close', function () { dlg.remove(); btn.focus(); });
      $('.vd-close', dlg).addEventListener('click', function () { dlg.close(); });
      dlg.addEventListener('click', function (e) { if (e.target === dlg) dlg.close(); });
      dlg.showModal();
    });
  });
})();
