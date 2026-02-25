# scripts 사용 안내

이 문서는 `scripts/` 폴더의 스크립트를 **언제/어떻게 쓰는지** 빠르게 찾기 위한 안내서입니다.

---

## 1) `post_new.py`

- 목적: 새 실험 글 마크다운(`posts_md/*.md`) 초안 파일 생성
- 언제 사용:
  - 새 Lab 글을 시작할 때
- 필요 MD 파일:
  - 생성 대상: `posts_md/새글이름.md`
- 실행 예시:
  ```powershell
  python scripts/post_new.py posts_md/my-new-post
  ```
- 결과:
  - `posts_md/my-new-post.md` 생성

---

## 2) `post_generate.py`

- 목적: 마크다운 글을 HTML로 생성하고 목록 갱신
- 언제 사용:
  - 글 내용을 수정한 뒤 반영할 때
- 필요 MD 파일:
  - 입력 원본: `posts_md/*.md`
- 실행 예시:
  ```powershell
  python scripts/post_generate.py posts_md/my-new-post.md
  ```
- 자동 갱신 대상:
  - `posts/*.html` (해당 글)
  - `posts/labs.html` (Lab 목록)
  - `index.html` (홈 최근 글)

---

## 3) `tool_add.py`

- 목적: Tool 정보를 대화형으로 입력하고 `data/tools.json`에 저장
- 언제 사용:
  - 새 Tool 카드를 추가하거나 수정할 때
- 필요 MD 파일:
  - 없음 (입력은 대화형, 저장은 `data/tools.json`)
- 실행 예시:
  ```powershell
  python scripts/tool_add.py
  ```
- 자동 실행:
  - 내부에서 `tool_generate.py`를 호출해 페이지 갱신

---

## 4) `tool_generate.py`

- 목적: `data/tools.json` 기준으로 Tool 페이지/홈 하이라이트 재생성
- 언제 사용:
  - `data/tools.json`을 직접 수정한 뒤 반영할 때
- 필요 MD 파일:
  - 없음 (입력 원본은 `data/tools.json`)
- 실행 예시:
  ```powershell
  python scripts/tool_generate.py
  ```
- 자동 갱신 대상:
  - `tools.html`
  - `tools-en.html`
  - `index.html` (Tools 하이라이트)

---

## 5) `youtube_add.py`

- 목적: YouTube 영상 항목을 대화형으로 등록
- 언제 사용:
  - 새 영상을 등록할 때
- 필요 MD 파일:
  - 없음 (입력은 대화형, 저장은 `data/youtube.json`)
- 실행 예시:
  ```powershell
  python scripts/youtube_add.py
  ```
- 입력 규칙:
  - 썸네일은 파일명만 입력해도 자동 보정
  - 예: `sample.jpg` 입력 시 `assets/img/sample.jpg`로 저장
- 자동 실행:
  - 내부에서 `youtube_generate.py`를 호출해 페이지 갱신

---

## 6) `youtube_generate.py`

- 목적: `data/youtube.json` 기준으로 YouTube 페이지/홈 영상 섹션 갱신
- 언제 사용:
  - `data/youtube.json`을 직접 수정한 뒤 반영할 때
- 필요 MD 파일:
  - 없음 (입력 원본은 `data/youtube.json`)
- 실행 예시:
  ```powershell
  python scripts/youtube_generate.py
  ```
- 자동 갱신 대상:
  - `youtube.html`
  - `index.html` (홈 YouTube 카드)

---

## 7) `watch_posts.py`

- 목적: 포스트 마크다운 변경을 감시해 자동 생성 보조
- 언제 사용:
  - 글을 자주 수정하면서 반복 생성이 귀찮을 때
- 필요 MD 파일:
  - 입력 원본: `posts_md/*.md`
- 실행 예시:
  ```powershell
  python scripts/watch_posts.py
  ```
- 주의:
  - 웹 서버가 아니라 **감시/생성 보조 도구**

---

## 8) `publish_post_interactive.ps1`

- 목적: 단일 포스트 생성 후 Git add/commit/push를 대화형으로 수행
- 언제 사용:
  - 글 1건을 바로 배포까지 올릴 때
- 필요 MD 파일:
  - 입력 원본: `posts_md/글이름.md`
- 실행 예시:
  ```powershell
  powershell -ExecutionPolicy Bypass -File scripts/publish_post_interactive.ps1
  ```
- 주의:
  - Git 커밋/푸시까지 진행하므로 실행 전 변경 파일 확인 필요

---

## 9) `run.ps1`

- 목적: 여러 작업을 프리셋으로 묶어 실행
- 언제 사용:
  - 여러 생성 작업을 한 번에 돌릴 때
- 필요 MD 파일:
  - `p1` 포함 시: `posts_md/*.md`
  - `p2`, `p3`만 사용 시: MD 직접 입력은 보통 없음
- 실행 예시:
  ```powershell
  powershell -NoProfile -ExecutionPolicy Bypass -File scripts/run.ps1 p12
  ```
- 프리셋:
  - `p1`: post 생성
  - `p2`: tool 생성
  - `p3`: weekly(있으면 실행)
  - `all`, `p12`, `p13`, `p23` 조합 지원
- 주의:
  - 로컬 보조 스크립트이므로 필요할 때만 사용

---

## 추천 최소 운영 루틴 (헷갈릴 때)

1. 포스트 작업:
   - 새 글: `post_new.py`
   - 반영: `post_generate.py`
2. Tool 작업:
   - 등록: `tool_add.py` (또는 json 직접 수정 후 `tool_generate.py`)
3. YouTube 작업:
   - 등록: `youtube_add.py` (가장 간단)
4. 마지막:
   - `git status --short` 확인 후 커밋/푸시

---

## MD 파일 빠른 찾기 (요약)

- Lab 글 작성/수정:
  - `posts_md/*.md`
  - 관련 스크립트: `post_new.py`, `post_generate.py`, `watch_posts.py`, `publish_post_interactive.ps1`

- 문서/운영 메모 수정:
  - `next-task.md`, `docs/*.md`, `scripts/doc.md`
  - 관련 스크립트: 직접 연동 없음(참고 문서용)

- Tool/YouTube 등록:
  - MD가 아니라 JSON 사용
  - `data/tools.json`, `data/youtube.json`
