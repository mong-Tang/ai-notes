// Shared navigation injection (no frames)
(function initSharedNav() {
  var mount = document.getElementById('site-nav');
  if (!mount) return;

  var base = mount.getAttribute('data-base') || '.';
  var isEn = (document.documentElement.lang || '').toLowerCase().startsWith('en');
  var homePath = isEn ? 'index-en.html' : 'index.html';
  var aboutPath = isEn ? 'about-en.html' : 'about.html';
  var toolsPath = isEn ? 'tools-en.html' : 'tools.html';
  var labels = isEn
    ? { home: 'Home', lab: 'Lab', tools: 'Tools', youtube: 'YouTube', about: 'About', toggle: 'Language toggle', flag: '\uD83C\uDDF0\uD83C\uDDF7' }
    : { home: 'Home', lab: 'Lab', tools: 'Tools', youtube: 'YouTube', about: 'About', toggle: '\uC5B8\uC5B4 \uC804\uD658', flag: '\uD83C\uDDFA\uD83C\uDDF8' };

  function href(path) {
    return base + '/' + path;
  }

  mount.outerHTML =
    '<nav class="nav-bar">' +
      '<div class="nav-inner">' +
        '<div class="brand">mongTang</div>' +
        '<div class="nav-links">' +
          '<a href="' + href(homePath) + '" data-nav-key="home">' + labels.home + '</a>' +
          '<a href="' + href('posts/index.html') + '" data-nav-key="lab">' + labels.lab + '</a>' +
          '<a href="' + href(toolsPath) + '" data-nav-key="tools">' + labels.tools + '</a>' +
          '<a href="' + href(homePath + '#youtube') + '" data-nav-key="youtube">' + labels.youtube + '</a>' +
          '<a href="' + href(aboutPath) + '" data-nav-key="about">' + labels.about + '</a>' +
          '<a id="lang-toggle" href="#" aria-label="' + labels.toggle + '">' + labels.flag + '</a>' +
        '</div>' +
      '</div>' +
    '</nav>';

  var path = window.location.pathname;
  var navKey = 'home';
  if (/\/posts\/index\.html$/i.test(path) || /\/posts\/.+\.html$/i.test(path)) {
    navKey = 'lab';
  } else if (/\/tools(?:-en)?\.html$/i.test(path)) {
    navKey = 'tools';
  } else if (/\/about(?:-en)?\.html$/i.test(path) || /\/contact(?:-en)?\.html$/i.test(path)) {
    navKey = 'about';
  }

  var active = document.querySelector('.nav-links a[data-nav-key="' + navKey + '"]');
  if (active) active.classList.add('active');
})();

// Utterances ??
(function initUtterances(){
  var container = document.getElementById('utterances');
  if (!container) return;

  var s = document.createElement('script');
  s.src = 'https://utteranc.es/client.js';
  s.setAttribute('repo', 'mong-Tang/ai-notes');
  s.setAttribute('issue-term', 'pathname');
  s.setAttribute('theme', 'github-light');
  s.crossOrigin = 'anonymous';
  s.async = true;
  container.appendChild(s);
})();

// ?? ??(ko/en ?? ??)
(function initLangToggle() {
  var toggle = document.getElementById('lang-toggle');
  if (!toggle) return;

  var path = window.location.pathname;
  var isEn = /-en\.html$/i.test(path);
  var isKo = /-ko\.html$/i.test(path);
  var current = isEn ? 'en' : 'ko';

  var targetPath = path;
  var fallbackPath = null;

  if (current === 'ko') {
    toggle.textContent = '\uD83C\uDDFA\uD83C\uDDF8';
    if (isKo) {
      targetPath = path.replace(/-ko\.html$/i, '-en.html');
    } else if (/\.html$/i.test(path)) {
      targetPath = path.replace(/\.html$/i, '-en.html');
    }
  } else {
    toggle.textContent = '\uD83C\uDDF0\uD83C\uDDF7';
    targetPath = path.replace(/-en\.html$/i, '-ko.html');
    fallbackPath = path.replace(/-en\.html$/i, '.html');
  }

  toggle.href = targetPath + window.location.search + window.location.hash;

  async function exists(url) {
    try {
      var res = await fetch(url, { method: 'HEAD', cache: 'no-store' });
      return res.ok;
    } catch (e) {
      return false;
    }
  }

  toggle.addEventListener('click', async function (e) {
    e.preventDefault();

    if (await exists(targetPath)) {
      window.location.href = targetPath;
      return;
    }

    // ??(B): ?? ?? ???? ??? ???? ?? fallback ??
    if (current === 'ko' && /^https?:/i.test(window.location.href)) {
      var translated = 'https://translate.google.com/translate?sl=ko&tl=en&u='
        + encodeURIComponent(window.location.href);
      window.location.href = translated;
      return;
    }

    if (fallbackPath && await exists(fallbackPath)) {
      window.location.href = fallbackPath;
      return;
    }

    alert(current === 'ko'
      ? '\uC601\uBB38 \uD398\uC774\uC9C0 \uC900\uBE44 \uC911\uC785\uB2C8\uB2E4.'
      : '\uD55C\uAE00 \uD398\uC774\uC9C0 \uC900\uBE44 \uC911\uC785\uB2C8\uB2E4.');
  });
})();

// ???? ??? ?? ??? ?? ??? ??
(function initPostSummaryBridge() {
  var STORAGE_KEY = 'postSummaryMapV1';

  function readMap() {
    try {
      return JSON.parse(localStorage.getItem(STORAGE_KEY) || '{}') || {};
    } catch (e) {
      return {};
    }
  }

  function writeMap(map) {
    try {
      localStorage.setItem(STORAGE_KEY, JSON.stringify(map));
    } catch (e) {}
  }

  function clip50(text) {
    if (!text) return '';
    return text.length > 50 ? text.slice(0, 50) + '...' : text;
  }

  // ?? ?? ? ?? ??
  var rows = document.querySelectorAll('.post-row');
  if (rows.length) {
    rows.forEach(function (row) {
      row.addEventListener('click', function () {
        var href = row.getAttribute('href');
        var summaryEl = row.querySelector('.post-summary');
        if (!href || !summaryEl) return;

        var summary = (summaryEl.textContent || '').trim();
        if (!summary) return;

        var targetPath = new URL(href, window.location.href).pathname;
        var map = readMap();
        map[targetPath] = summary;
        writeMap(map);
      });
    });
  }

  // ???? ?? ? ??
  var doc = document.querySelector('article.doc');
  if (!doc) return;

  var map = readMap();
  var currentPath = window.location.pathname;
  var summaryText = map[currentPath] || '';
  var body = summaryText ? clip50(summaryText) : '(?? ??)';

  var bridge = document.createElement('div');
  bridge.className = 'doc-summary-bridge';

  var labelEl = document.createElement('span');
  labelEl.className = 'label';
  labelEl.textContent = '?? : ';

  var textEl = document.createElement('span');
  textEl.className = 'text';
  textEl.textContent = body;

  bridge.appendChild(labelEl);
  bridge.appendChild(textEl);

  doc.parentNode.insertBefore(bridge, doc);
})();
