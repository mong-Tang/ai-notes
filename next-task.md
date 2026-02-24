# next-task.md

업데이트 일시: 2026-02-23
프로젝트: use_AI

## PROJECT_DIRECTION
- 이 프로젝트는 "내가 좋아서 하는" 취미 기록용 정적 블로그다.
- 목적: AI를 직접 써보며 가능한 범위/한계를 기록하고 축적한다.
- 운영 원칙:
  - 조회수보다 기록
  - 완성도보다 지속성
  - 재미 없으면 쉬고, 재미 있으면 진행

## PLAN (로드맵)
### Phase 1. 학습/실험 (현재)
- 주 1~2회 실험 글 작성
- 템플릿 기반 기록(목표/입력/결과/한계/다음 액션)

### Phase 2. 가능 범위 검증
- 주제별 판정표(가능/조건부 가능/어려움) 축적

### Phase 3. 자료 재사용
- 누적 글을 정리글/요약글로 재편집

### Phase 4. YouTube 확장
- 블로그 글 1개 → 3~5분 영상 스크립트 변환

## DONE_LOG (지금까지 완료)
- [x] 모바일 반응형 1차 안정화
  - 인덱스/포스트 모바일 가로 스크롤 해소
  - 목록 날짜 정렬 개선(모바일에서 아래줄 밀림 완화)
  - 모바일 메뉴 우측 정렬 유지
- [x] 포스트 생성 파서 확장
  - `note:`, `요약:`, `note(요약):` 인식
  - `body:`, `본문:`, `body(본문):` 인식
- [x] 템플릿 정비
  - `docs/POST_TEMPLATE.md` 실사용형으로 개정
  - `posts_md/ai-log-01~05.md` 템플릿 샘플 생성
- [x] 언어 토글 1차 적용
  - 메뉴에 국기 토글(🇺🇸/🇰🇷) 추가
  - `index.html` ↔ `index-en.html` 연결
  - `main.js`에 언어 전환 로직 추가

## RUNBOOK (실행 명령 모음)
### 1) 로컬 서버 실행 (필수)
```powershell
cd d:\my_Work\workspace\use_AI
python -m http.server 8000
```
접속: `http://127.0.0.1:8000/index.html`

### 2) 새 글 파일 만들기
```powershell
python scripts/new_post.py posts_md/my-post
```

### 3) 단일 글 HTML 생성
```powershell
python scripts/generate_post.py posts_md/my-post.md
```

### 4) 전체 글 일괄 생성
```powershell
Get-ChildItem posts_md\*.md | ForEach-Object { python scripts/generate_post.py $_.FullName }
```

### 5) 자동 감시 (선택)
```powershell
python scripts/watch_posts.py
```
- 주의: `watch_posts.py`는 생성 자동화 도구일 뿐, 웹 서버가 아님.

### 6) 접속 문제 트러블슈팅
```powershell
netstat -ano | findstr :8000
python -m http.server 5500
```

## NEXT_TASK (다음 작업)
- [ ] `contact.html` 이메일 실제값으로 교체
- [ ] `favicon.ico` 추가 및 `<head>` 링크 반영
- [ ] 댓글(utterances) `YOUR_GITHUB_ID/YOUR_REPO` 실제값 반영
- [x] 영문 상세 페이지(`*-en.html`) 운영 정책 확정
  - (A) 수동 작성
  - (B) 자동번역 임시 fallback (채택)
- [ ] 디자인 1차 미세조정(내일)
  - [ ] 타이포/간격 미세조정
  - [ ] 카드/목록 시각 밀도 조정
  - [ ] 색상 포인트 1차 정리

## BACKLOG (보류)
- 요약/본문 영문 전용 필드(`note_en`, `body_en`) 도입 여부
- YouTube용 고정 대본 템플릿 세분화

## QUICK_MEMO
- `python scripts/generate_post.py posts_md/` 는 폴더 인자 미지원
- 현재 구조는 정적 블로그: "내가 작성/생성/업로드", 방문자는 읽기만 함

## LESSONS_LEARNED
- 파트 분할은 접점/규칙 없이 진행하면 통합 단계에서 반드시 충돌한다.
- 책임 경계와 완료 기준(DoD)을 먼저 정해야 불필요한 갈등이 줄어든다.
- 수작업 취합은 누락/오류 위험이 크다. 반복 작업은 가능한 한 스크립트로 고정한다.
- 기억은 사라진다. 떠오른 순간 바로 기록해야 다음에 재사용할 수 있다.
- 취미 프로젝트는 "재미"가 우선이다. 피로도가 올라가면 범위를 줄이고 리듬을 유지한다.
