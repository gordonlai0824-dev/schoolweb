/* 網站後台 — 互動功能及簡易富文本編輯器 */
(function () {
  'use strict';
  var $ = function (s, r) { return (r || document).querySelector(s); };
  var $$ = function (s, r) { return Array.prototype.slice.call((r || document).querySelectorAll(s)); };
  var CSRF = ($('meta[name="csrf-token"]') || {}).content || '';

  /* 手機側欄 */
  var st = $('.side-toggle'), side = $('#side');
  if (st && side) st.addEventListener('click', function () {
    var open = side.classList.toggle('open'); st.setAttribute('aria-expanded', open);
  });

  /* 刪除確認 */
  $$('form[data-confirm]').forEach(function (f) {
    f.addEventListener('submit', function (e) { if (!window.confirm(f.dataset.confirm)) e.preventDefault(); });
  });

  /* 未儲存提示 */
  $$('form[data-dirty-check]').forEach(function (f) {
    var dirty = false;
    f.addEventListener('input', function () { dirty = true; });
    f.addEventListener('change', function () { dirty = true; });
    f.addEventListener('submit', function () { dirty = false; });
    window.addEventListener('beforeunload', function (e) { if (dirty) { e.preventDefault(); e.returnValue = ''; } });
    f._markDirty = function () { dirty = true; };
  });

  /* 網站設定分頁 */
  var tabs = $$('.stab');
  tabs.forEach(function (t) {
    t.addEventListener('click', function () {
      tabs.forEach(function (x) { x.setAttribute('aria-selected', x === t); });
      $$('[data-panel]').forEach(function (p) { p.hidden = p.dataset.panel !== t.dataset.tab; });
      var inp = $('[data-tab-input]'); if (inp) inp.value = t.dataset.tab;
    });
  });

  /* 相片預覽 */
  $$('input[type=file][data-preview]').forEach(function (inp) {
    inp.addEventListener('change', function () {
      var old = inp.parentElement.querySelector('.thumb.new'); if (old) old.remove();
      if (inp.files && inp.files[0]) {
        if (inp.files[0].size > 25 * 1024 * 1024) { alert('檔案超過 25MB，請先壓縮相片。'); inp.value = ''; return; }
        var img = document.createElement('img'); img.className = 'thumb new'; img.alt = '預覽';
        img.src = URL.createObjectURL(inp.files[0]); img.style.marginTop = '8px';
        inp.after(img);
      }
    });
  });

  /* ---------------- 富文本編輯器 ---------------- */
  var ALLOWED = { P: 1, BR: 1, B: 1, STRONG: 1, I: 1, EM: 1, U: 1, UL: 1, OL: 1, LI: 1, A: 1, H2: 1, H3: 1, H4: 1,
    TABLE: 1, THEAD: 1, TBODY: 1, TR: 1, TH: 1, TD: 1, BLOCKQUOTE: 1 };

  // 由 Word／網頁貼上時，只保留基本格式
  function cleanPasted(html) {
    var doc = new DOMParser().parseFromString(html, 'text/html');
    function walk(node) {
      Array.prototype.slice.call(node.childNodes).forEach(function (n) {
        if (n.nodeType === 8) { n.remove(); return; }
        if (n.nodeType !== 1) return;
        walk(n);
        if (/^(SCRIPT|STYLE|META|LINK|O:P|XML)$/i.test(n.nodeName)) { n.remove(); return; }
        if (!ALLOWED[n.nodeName]) {
          var tag = /^(DIV|SECTION|ARTICLE|H1)$/.test(n.nodeName) ? 'p' : null;
          if (tag) { var p = document.createElement(tag); while (n.firstChild) p.appendChild(n.firstChild); n.replaceWith(p); }
          else { while (n.firstChild) n.parentNode.insertBefore(n.firstChild, n); n.remove(); }
          return;
        }
        var href = n.getAttribute('href');
        Array.prototype.slice.call(n.attributes).forEach(function (a) { n.removeAttribute(a.name); });
        if (n.nodeName === 'A' && href && /^(https?:|\/|mailto:|#)/.test(href)) n.setAttribute('href', href);
      });
    }
    walk(doc.body);
    return doc.body.innerHTML;
  }

  var SNIPPETS = {
    callout: '<div class="callout"><strong>重點標題</strong><p>在此輸入重點內容。</p></div><p></p>',
    gpor: '<div class="gpor"><div><span class="k">目標</span><p>…</p></div><div><span class="k">過程</span><p>…</p></div>' +
          '<div><span class="k">成果</span><p>…</p></div><div><span class="k">反思</span><p>學生的話…</p></div></div><p></p>',
    cards: '<div class="grid grid-3"><div class="card"><h3>標題一</h3><p>內容</p></div><div class="card"><h3>標題二</h3><p>內容</p></div>' +
           '<div class="card"><h3>標題三</h3><p>內容</p></div></div><p></p>',
    checklist: '<ul class="check-list"><li>重點一</li><li>重點二</li><li>重點三</li></ul><p></p>',
    table: '<div class="table-wrap"><table><thead><tr><th>標題</th><th>標題</th></tr></thead><tbody><tr><td>內容</td><td>內容</td></tr><tr><td>內容</td><td>內容</td></tr></tbody></table></div><p></p>'
  };

  function uploadImage(file, cb) {
    var fd = new FormData(); fd.append('file', file);
    fetch('/admin/upload', { method: 'POST', body: fd, headers: { 'X-CSRF-Token': CSRF }, credentials: 'same-origin' })
      .then(function (r) { return r.json(); })
      .then(function (j) { if (j.url) cb(j.url); else alert(j.error || '上載失敗'); })
      .catch(function () { alert('上載失敗，請稍後再試。'); });
  }

  $$('[data-rte]').forEach(function (wrap) {
    var ta = $('textarea', wrap), form = wrap.closest('form');
    var area = document.createElement('div');
    area.className = 'rte-area'; area.contentEditable = 'true';
    area.setAttribute('role', 'textbox'); area.setAttribute('aria-multiline', 'true');
    area.setAttribute('aria-label', (document.querySelector('label[for="' + ta.id + '"]') || {}).textContent || '內容');
    area.innerHTML = ta.value;
    var bar = document.createElement('div'); bar.className = 'rte-bar'; bar.setAttribute('role', 'toolbar');
    var B = [
      ['p', '段落', '內文'], ['h2', '大標題', 'H2'], ['h3', '小標題', 'H3'], '|',
      ['bold', '粗體', '<b>B</b>'], ['italic', '斜體', '<i>I</i>'], ['underline', '底線', '<u>U</u>'], '|',
      ['ul', '項目清單', '• 清單'], ['ol', '編號清單', '1. 清單'], ['quote', '引言', '❝'], '|',
      ['link', '加入連結', '連結'], ['unlink', '移除連結', '移除連結'], ['image', '插入相片', '相片'], ['video', '插入 YouTube 影片', '影片'], '|',
      ['s-callout', '插入重點框', '+重點框'], ['s-cards', '插入三欄卡片', '+卡片'], ['s-checklist', '插入剔號清單', '+剔號清單'],
      ['s-gpor', '插入「目標・過程・成果・反思」', '+成果四格'], ['s-table', '插入表格', '+表格'], '|',
      ['undo', '復原', '↶'], ['redo', '重做', '↷'], ['clear', '清除格式', '清除格式'], ['source', '切換 HTML 原始碼', '&lt;/&gt;']
    ];
    B.forEach(function (b) {
      if (b === '|') { var s = document.createElement('span'); s.className = 'sep'; bar.appendChild(s); return; }
      var btn = document.createElement('button'); btn.type = 'button'; btn.dataset.cmd = b[0];
      btn.title = b[1]; btn.setAttribute('aria-label', b[1]); btn.innerHTML = b[2];
      bar.appendChild(btn);
    });
    var fileInp = document.createElement('input'); fileInp.type = 'file'; fileInp.accept = 'image/*'; fileInp.hidden = true;
    wrap.insertBefore(bar, ta); wrap.insertBefore(area, ta); wrap.appendChild(fileInp);
    ta.hidden = true;
    var sourceMode = false, saved = null;

    function sync() { if (!sourceMode) ta.value = area.innerHTML; if (form && form._markDirty) form._markDirty(); }
    function keepSel() { var s = window.getSelection(); if (s.rangeCount && area.contains(s.anchorNode)) saved = s.getRangeAt(0); }
    function restoreSel() { area.focus(); if (saved) { var s = window.getSelection(); s.removeAllRanges(); s.addRange(saved); } }
    function insert(html) { restoreSel(); document.execCommand('insertHTML', false, html); sync(); }

    area.addEventListener('input', sync);
    area.addEventListener('keyup', keepSel); area.addEventListener('mouseup', keepSel); area.addEventListener('blur', keepSel);
    area.addEventListener('paste', function (e) {
      var cd = e.clipboardData; if (!cd) return;
      var img = Array.prototype.find.call(cd.files || [], function (f) { return /^image\//.test(f.type); });
      e.preventDefault();
      if (img) { uploadImage(img, function (url) { insert('<img src="' + url + '" alt="">'); }); return; }
      var html = cd.getData('text/html');
      if (html) document.execCommand('insertHTML', false, cleanPasted(html));
      else document.execCommand('insertText', false, cd.getData('text/plain'));
      sync();
    });
    fileInp.addEventListener('change', function () {
      if (!fileInp.files[0]) return;
      uploadImage(fileInp.files[0], function (url) {
        var alt = prompt('相片說明（供視障人士使用的替代文字）：', '') || '';
        insert('<img src="' + url + '" alt="' + alt.replace(/"/g, '&quot;') + '">');
      });
      fileInp.value = '';
    });

    bar.addEventListener('mousedown', function (e) { if (e.target.closest('button')) e.preventDefault(); });
    bar.addEventListener('click', function (e) {
      var btn = e.target.closest('button'); if (!btn) return;
      var c = btn.dataset.cmd;
      if (c === 'source') {
        sourceMode = !sourceMode; btn.classList.toggle('on', sourceMode);
        if (sourceMode) { ta.value = area.innerHTML; ta.hidden = false; area.hidden = true; ta.focus(); }
        else { area.innerHTML = ta.value; ta.hidden = true; area.hidden = false; area.focus(); }
        $$('button', bar).forEach(function (b) { if (b !== btn) b.disabled = sourceMode; });
        return;
      }
      restoreSel();
      if (c === 'p' || c === 'h2' || c === 'h3') document.execCommand('formatBlock', false, c.toUpperCase());
      else if (c === 'quote') document.execCommand('formatBlock', false, 'BLOCKQUOTE');
      else if (c === 'ul') document.execCommand('insertUnorderedList');
      else if (c === 'ol') document.execCommand('insertOrderedList');
      else if (c === 'link') {
        var url = prompt('連結網址（例：https://… 或 /parents#p1）：', 'https://');
        if (url && /^(https?:\/\/|\/|#|mailto:|tel:)/.test(url)) {
          if (window.getSelection().isCollapsed) insert('<a href="' + url + '">' + url + '</a>');
          else document.execCommand('createLink', false, url);
        } else if (url) alert('連結須以 https:// 或 / 開頭。');
      }
      else if (c === 'unlink') document.execCommand('unlink');
      else if (c === 'image') fileInp.click();
      else if (c === 'video') {
        var v = prompt('YouTube 影片網址：', '');
        var m = v && v.match(/(?:youtu\.be\/|v=|embed\/|shorts\/)([\w-]{11})/);
        if (m) insert('<iframe src="https://www.youtube-nocookie.com/embed/' + m[1] + '" title="影片" allowfullscreen loading="lazy"></iframe><p></p>');
        else if (v) alert('未能辨認 YouTube 網址。');
      }
      else if (c.indexOf('s-') === 0) insert(SNIPPETS[c.slice(2)]);
      else if (c === 'clear') document.execCommand('removeFormat');
      else document.execCommand(c);
      sync();
    });
    if (form) form.addEventListener('submit', function () { if (!sourceMode) ta.value = area.innerHTML; });
  });
})();
