# Interactive publish script for ai-notes
# Usage:
#   powershell -ExecutionPolicy Bypass -File scripts/publish_post_interactive.ps1

$post = Read-Host "포스트 파일명 입력 (예: no-summary-detail-check, .md 생략 가능)"
if ([string]::IsNullOrWhiteSpace($post)) {
  Write-Host "파일명이 비어있습니다."
  exit 1
}

$md = if ($post.EndsWith('.md')) { $post } else { "$post.md" }
$base = [System.IO.Path]::GetFileNameWithoutExtension($md)
$mdPath = "posts_md/$md"
$htmlPath = "posts/$base.html"

if (!(Test-Path $mdPath)) {
  Write-Host "파일 없음: $mdPath"
  exit 1
}

python scripts/post_generate.py $mdPath
if ($LASTEXITCODE -ne 0) {
  Write-Host "HTML 생성 명령이 실패했습니다."
  exit 1
}

if (!(Test-Path $htmlPath)) {
  Write-Host "HTML 생성 실패: $htmlPath"
  exit 1
}

$msg = Read-Host "커밋 메시지 입력 (엔터 시 기본값 사용)"
if ([string]::IsNullOrWhiteSpace($msg)) {
  $msg = "add $base post"
}

# index-en.html은 현재 생성 대상이 아니라 제외
# 필요 시 수동으로 포함 가능

git add $mdPath $htmlPath posts/labs.html index.html
if ($LASTEXITCODE -ne 0) {
  Write-Host "git add 실패"
  exit 1
}

git commit -m $msg
if ($LASTEXITCODE -ne 0) {
  Write-Host "커밋할 변경이 없거나 git commit 실패"
  exit 1
}

git push
if ($LASTEXITCODE -ne 0) {
  Write-Host "git push 실패"
  exit 1
}

Write-Host "완료: $base"
