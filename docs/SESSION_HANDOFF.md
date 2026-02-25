# SESSION_HANDOFF (세션 인수인계)

## ✅ 고정 체크리스트 (한/영 동시 반영)
- [ ] 한글 페이지 반영 확인
- [ ] 영문 페이지 동일 반영 확인

업데이트 기준: 2026-02-25

---

## 1) 현재 운영 구조 (입력/생성/출력)

### A. Lab(Post)
- 입력 원본: `posts_md/*.md`
- 생성 스크립트: `scripts/post_generate.py`
- 출력:
  - `posts/*.html`
  - `posts/labs.html` (Lab 목록)
  - `index.html`, `index-en.html` (최근 실험 블록)

### B. Tools
- 입력 원본: `data/tools.json`
- 등록 스크립트(대화형): `scripts/tool_add.py`
- 생성 스크립트: `scripts/tool_generate.py`
- 출력:
  - `tools.html`
  - `tools-en.html`
  - `index.html`, `index-en.html` (Tools 하이라이트)

### C. YouTube
- 입력 원본: `data/youtube.json`
- 등록 스크립트(대화형): `scripts/youtube_add.py`
- 생성 스크립트: `scripts/youtube_generate.py`
- 출력:
  - `youtube.html`
  - `index.html`, `index-en.html` (YouTube 카드)

---

## 2) 운영 규칙

1. 수동 편집은 데이터 파일 우선
   - Tools: `data/tools.json`
   - YouTube: `data/youtube.json`

2. 반영은 생성 스크립트로 수행
   - Tools: `python scripts/tool_generate.py`
   - YouTube: `python scripts/youtube_generate.py`

3. 한/영 동시 반영 확인 필수
   - `index.html` + `index-en.html`
   - `tools.html` + `tools-en.html`

4. 마커 블록 외 영역은 수동 수정 시 인코딩 주의

---

## 3) 빠른 실행 명령

```powershell
# Tools 반영
python scripts/tool_generate.py

# YouTube 반영
python scripts/youtube_generate.py

# 전체 프리셋(필요 시)
.\scripts\run.ps1 p2
```

---

## 4) 인코딩 가드레일

- 기본 저장 인코딩: UTF-8
- PowerShell 실행 시 UTF-8 강제는 `scripts/run.ps1`에 반영됨
- 한글이 깨지면 파일을 UTF-8로 다시 저장 후 생성 스크립트 재실행
