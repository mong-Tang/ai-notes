# WORKFLOW

## 1) 글 작성
```powershell
python scripts/new_post.py posts_md/your-post-name
```

## 2) HTML 생성
```powershell
python scripts/generate_post.py posts_md/your-post-name.md
```

## 3) 로컬 확인
- `index.html` 최신글 반영 확인
- `posts/index.html` 목록 반영 확인
- 생성된 `posts/your-post-name.html` 본문 확인

메모
- 현재 `python scripts/generate_post.py posts_md/`(폴더 인자)는 미지원
