# SESSION_HANDOFF (재시작용 인수인계)

업데이트 기준: 2026-02-25

---

## 1) 현재 운영 구조 (입력/생성/출력)

### A. Lab(Post)
- 입력 원본: `posts_md/*.md`
- 생성 스크립트: `scripts/post_generate.py`
- 출력:
  - `posts/*.html`
  - `posts/labs.html` (Lab 목록)
  - `index.html` (최근 실험 목록 블록)

### B. Tools
- 입력 원본: `data/tools.json`
- 등록 스크립트(대화형): `scripts/tool_add.py`
- 생성 스크립트: `scripts/tool_generate.py`
- 출력:
  - `tools.html`
  - `tools-en.html`
  - `index.html` (Tools 하이라이트 블록)

### C. YouTube
- 입력 원본: `data/youtube.json`
- 등록 스크립트(대화형): `scripts/youtube_add.py`
- 생성 스크립트: `scripts/youtube_generate.py`
- 출력:
  - `youtube.html`
  - `index.html` (홈 YouTube 카드 블록)

---

## 2) 파일명/경로 변경 사항 (중요)

- Lab 목록 파일명 변경:
  - `posts/index.html` -> `posts/labs.html`
- 스크립트 리네임 완료:
  - `generate_post.py` -> `post_generate.py`
  - `generate_tools.py` -> `tool_generate.py`
  - `add_tool.py` -> `tool_add.py`
  - `new_post.py` -> `post_new.py`

참조 파일/문서/데이터의 경로 문자열은 함께 동기화한 상태.

---

## 3) 자동/수동 편집 구분

### 자동 갱신 구간 (스크립트가 덮어씀)
- `index.html`
  - `<!-- POSTS_LATEST_START --> ... <!-- POSTS_LATEST_END -->`
  - `<!-- HOME_TOOLS_HIGHLIGHT_START --> ... <!-- HOME_TOOLS_HIGHLIGHT_END -->`
  - `<!-- HOME_YOUTUBE_CARDS_START --> ... <!-- HOME_YOUTUBE_CARDS_END -->`

- `youtube.html`
  - `<!-- YOUTUBE_LATEST_CARDS_START --> ... <!-- YOUTUBE_LATEST_CARDS_END -->`
  - `<!-- YOUTUBE_ARCHIVE_ROWS_START --> ... <!-- YOUTUBE_ARCHIVE_ROWS_END -->`

### 수동 편집 구간
- `youtube.html`
  - `<!-- YOUTUBE_IN_PROGRESS_START --> ... <!-- YOUTUBE_IN_PROGRESS_END -->`
  - `<!-- YOUTUBE_ROADMAP_START --> ... <!-- YOUTUBE_ROADMAP_END -->`

※ 수동 문구는 메모장 순수 텍스트 기준으로 관리.

---

## 4) YouTube 썸네일 규칙 (현재)

- 기본 위치: `assets/img/`
- `youtube_add.py` 입력 보정:
  - `sample.jpg` -> `assets/img/sample.jpg`
  - `sample` -> `assets/img/sample.jpg`
  - `assets/img/sample` -> `assets/img/sample.jpg`

`youtube_generate.py`에도 썸네일 경로 보정 로직이 있어, 누락 시 자동 보정됨.

---

## 5) 모바일 네비게이션 상태

- 이슈: 모바일에서 상단 메뉴 우측(`US`) 잘림 문제
- 조치: 모바일 CSS(`@media max-width: 768px`)에서
  - `.nav-links` 스크롤/우측 여백 보정
  - `.brand` 크기 축소
  - `max-width` 제거(텍스트 잘림 완화)
- 현재 상태: 390px 기준 `US`까지 보이는 상태 확인됨.

---

## 6) 핵심 실행 명령 (최소)

```powershell
# 새 글 md 생성
python scripts/post_new.py posts_md/my-post

# 글 반영
python scripts/post_generate.py posts_md/my-post.md

# Tool 등록(대화형 + 자동 생성)
python scripts/tool_add.py

# Tool 생성만
python scripts/tool_generate.py

# YouTube 등록(대화형 + 자동 생성)
python scripts/youtube_add.py

# YouTube 생성만
python scripts/youtube_generate.py
```

---

## 7) 재시작 시 우선 체크 순서

1. `git status --short`로 현재 변경 상태 확인  
2. 작업 대상 구분:
   - 글 / 툴 / 유튜브
3. 원본만 수정:
   - Post: `posts_md/*.md`
   - Tool: `data/tools.json`(또는 `tool_add.py`)
   - YouTube: `data/youtube.json`(또는 `youtube_add.py`)
4. 생성 스크립트 실행  
5. 결과 페이지 확인 후 커밋/푸시

---

## 8) 현재 사용자 선호/원칙 (중요)

- 설명은 한국어, 모호한 표현보다 명확한 범위 표현 선호
- `지금 세션 기준` 표현 선호
- 작업은 최소 단위/최소 리스크 선호
- 자동화는 좋지만 과복잡화는 지양
- 수동 작업 부담이 크므로 입력 지점 최소화 지향

