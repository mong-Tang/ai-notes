// Utterances 삽입 (GitHub repo 설정 필요)
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

// 언어 토글(ko/en 파일 전환)
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
    toggle.textContent = '🇺🇸';
    if (isKo) {
      targetPath = path.replace(/-ko\.html$/i, '-en.html');
    } else if (/\.html$/i.test(path)) {
      targetPath = path.replace(/\.html$/i, '-en.html');
    }
  } else {
    toggle.textContent = '🇰🇷';
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

    // 정책(B): 영문 상세 페이지가 없으면 자동번역 임시 fallback 사용
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
      ? '영문 페이지 준비 중입니다.'
      : '한글 페이지 준비 중입니다.');
  });
})();
