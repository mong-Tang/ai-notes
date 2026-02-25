function resolvePreferredLang() {
  var params = new URLSearchParams(window.location.search);
  var queryLang = (params.get('lang') || '').toLowerCase();
  if (queryLang === 'ko' || queryLang === 'en') return queryLang;

  var path = window.location.pathname;
  if (/-en\.html$/i.test(path)) return 'en';
  if (/-ko\.html$/i.test(path)) return 'ko';

  return (document.documentElement.lang || '').toLowerCase().startsWith('en') ? 'en' : 'ko';
}

// Shared navigation injection (no frames)
(function initSharedNav() {
  var mount = document.getElementById('site-nav');
  if (!mount) return;

  var base = mount.getAttribute('data-base') || '.';
  var isEn = resolvePreferredLang() === 'en';
  var langQuery = isEn ? '?lang=en' : '';
  var homePath = isEn ? 'index-en.html' : 'index.html';
  var aboutPath = isEn ? 'about-en.html' : 'about.html';
  var toolsPath = isEn ? 'tools-en.html' : 'tools.html';
  var youtubePath = 'youtube.html' + langQuery;
  var labPath = 'posts/labs.html' + langQuery;
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
          '<a href="' + href(labPath) + '" data-nav-key="lab">' + labels.lab + '</a>' +
          '<a href="' + href(toolsPath) + '" data-nav-key="tools">' + labels.tools + '</a>' +
          '<a href="' + href(youtubePath) + '" data-nav-key="youtube">' + labels.youtube + '</a>' +
          '<a href="' + href(aboutPath) + '" data-nav-key="about">' + labels.about + '</a>' +
          '<a id="lang-toggle" href="#" aria-label="' + labels.toggle + '">' + labels.flag + '</a>' +
        '</div>' +
      '</div>' +
    '</nav>';

  var path = window.location.pathname;
  var navKey = 'home';
  if (/\/posts\/labs\.html$/i.test(path) || /\/posts\/.+\.html$/i.test(path)) {
    navKey = 'lab';
  } else if (/\/tools(?:-en)?\.html$/i.test(path)) {
    navKey = 'tools';
  } else if (/\/youtube(?:-en)?\.html$/i.test(path)) {
    navKey = 'youtube';
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
  var currentLang = resolvePreferredLang();
  var runtimeI18n = document.documentElement.getAttribute('data-i18n-runtime') === 'true';

  // i18n 페이지(labs/youtube): 같은 페이지에서 ?lang 전환
  if (runtimeI18n) {
    var nextLang = currentLang === 'en' ? 'ko' : 'en';
    toggle.textContent = currentLang === 'en' ? '\uD83C\uDDF0\uD83C\uDDF7' : '\uD83C\uDDFA\uD83C\uDDF8';

    var runtimeUrl = new URL(window.location.href);
    runtimeUrl.searchParams.set('lang', nextLang);
    toggle.href = runtimeUrl.pathname + runtimeUrl.search + runtimeUrl.hash;

    toggle.addEventListener('click', function (e) {
      e.preventDefault();
      window.location.href = runtimeUrl.pathname + runtimeUrl.search + runtimeUrl.hash;
    });
    return;
  }

  // 분리 페이지(index/about/tools): -en.html <-> .html 전환
  toggle.textContent = currentLang === 'en' ? '\uD83C\uDDF0\uD83C\uDDF7' : '\uD83C\uDDFA\uD83C\uDDF8';

  var targetPath = path;
  if (/-en\.html$/i.test(path)) {
    targetPath = path.replace(/-en\.html$/i, '.html');
  } else if (/\.html$/i.test(path)) {
    targetPath = path.replace(/\.html$/i, '-en.html');
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
      window.location.href = targetPath + window.location.search + window.location.hash;
      return;
    }
    alert(currentLang === 'ko'
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

// YouTube 아카이브: 행 클릭 시 "보기" 링크로 이동
(function initYoutubeArchiveRowClick() {
  var rows = document.querySelectorAll('.youtube-archive-row');
  if (!rows.length) return;

  rows.forEach(function (row) {
    var viewLink = row.querySelector('span:last-child a');
    if (!viewLink) return;

    row.setAttribute('role', 'link');
    row.setAttribute('tabindex', '0');

    row.addEventListener('click', function (e) {
      if (e.target && e.target.closest('a')) return;
      viewLink.click();
    });

    row.addEventListener('keydown', function (e) {
      if (e.key !== 'Enter' && e.key !== ' ') return;
      e.preventDefault();
      viewLink.click();
    });
  });
})();

// 페이지 문구 i18n 치환 (파일럿: data-i18n-runtime=true 페이지)
(function initPageI18n() {
  if (document.documentElement.getAttribute('data-i18n-runtime') !== 'true') return;

  var lang = resolvePreferredLang();
  document.documentElement.lang = lang;

  var base = /\/posts\//i.test(window.location.pathname) ? '..' : '.';
  var file = base + '/data/i18n/' + lang + '.json';
  var fallback = base + '/data/i18n/ko.json';

  function applyDict(dict) {
    var nodes = document.querySelectorAll('[data-i18n]');
    nodes.forEach(function (el) {
      var key = el.getAttribute('data-i18n');
      if (!key) return;
      if (Object.prototype.hasOwnProperty.call(dict, key)) {
        el.textContent = dict[key];
      }
    });
  }

  fetch(file, { cache: 'no-store' })
    .then(function (res) {
      if (!res.ok) throw new Error('i18n not found');
      return res.json();
    })
    .then(applyDict)
    .catch(function () {
      if (file === fallback) return;
      fetch(fallback, { cache: 'no-store' })
        .then(function (res) { return res.ok ? res.json() : {}; })
        .then(applyDict)
        .catch(function () {});
    });
})();

// YouTube 채널 버튼: 준비중 안내
(function initYoutubeChannelNotice() {
  var link = document.getElementById('youtube-channel-link');
  var notice = document.getElementById('youtube-channel-notice');
  if (!link || !notice) return;

  var hideTimer = null;

  link.addEventListener('click', function (e) {
    e.preventDefault();
    notice.hidden = false;
    if (hideTimer) clearTimeout(hideTimer);
    hideTimer = setTimeout(function () {
      notice.hidden = true;
    }, 3000);
  });
})();
