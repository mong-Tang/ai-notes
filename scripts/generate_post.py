import re
import sys
from pathlib import Path
from datetime import datetime

ROOT = Path(__file__).resolve().parents[1]
POSTS_MD = ROOT / "posts_md"
POSTS_HTML = ROOT / "posts"
INDEX_HTML = ROOT / "index.html"
INDEX_EN_HTML = ROOT / "index-en.html"
POSTS_INDEX_HTML = POSTS_HTML / "index.html"

POST_TEMPLATE = """<!doctype html>
<html lang=\"ko\">
<head>
  <meta charset=\"utf-8\" />
  <meta name=\"viewport\" content=\"width=device-width, initial-scale=1\" />
  <title>{title}</title>
  <link rel=\"stylesheet\" href=\"../assets/css/style.css\" />
</head>
<body>
  <nav class=\"nav-bar\">
    <div class=\"nav-inner\">
      <div class=\"brand\">mongTang</div>
      <div class=\"nav-links\">
        <a href=\"../index.html\">홈</a>
        <a href=\"index.html\">글 목록</a>
        <a href=\"../contact.html\">문의</a>
        <a id=\"lang-toggle\" href=\"#\" aria-label=\"언어 전환\">🇺🇸</a>
      </div>
    </div>
  </nav>

  <main class=\"container\">
    <article class=\"doc\">
      <div class=\"doc-header\">
        <div class=\"doc-title\">{title}</div>
        <div class=\"doc-meta\">
          <div><span class=\"label\">등록일</span> {date}</div>
        </div>
      </div>
      <div class=\"doc-body\">
        {body}
      </div>
    </article>

    <section class=\"card\">
      <h2>댓글</h2>
      <div id=\"utterances\"></div>
    </section>
  </main>

  <footer class=\"site-footer\">
    <div class=\"footer-inner\">
      <p>© 2026 My Hobby</p>
    </div>
  </footer>

  <script src=\"../assets/js/main.js?v=20260223\"></script>
  <!-- Utterances 스크립트는 main.js에서 주입합니다. -->
</body>
</html>
"""

# 허용 키워드
# - note:
# - 요약:
# - note(요약):
NOTE_RE = re.compile(r"^\ufeff?\s*(?:note(?:\s*\(\s*요약\s*\))?|요약)\s*:", re.IGNORECASE)
# - body:
# - 본문:
# - body(본문):
BODY_RE = re.compile(r"^\ufeff?\s*(?:body(?:\s*\(\s*본문\s*\))?|본문)\s*:", re.IGNORECASE)
CODE_FENCE = re.compile(r"^```\s*$")


def md_to_html(md: str) -> str:
    lines = md.strip().splitlines()
    html_lines = []
    in_code = False
    code_lines = []

    for line in lines:
        if CODE_FENCE.match(line.strip()):
            if not in_code:
                in_code = True
                code_lines = []
            else:
                in_code = False
                code_text = "\n".join(code_lines)
                html_lines.append("<pre><code>" + escape_html(code_text) + "</code></pre>")
            continue

        if in_code:
            code_lines.append(line)
            continue

        if NOTE_RE.match(line) or BODY_RE.match(line):
            continue
        if line.startswith("# "):
            html_lines.append(f"<h2>{line[2:].strip()}</h2>")
        elif line.startswith("## "):
            html_lines.append(f"<h3>{line[3:].strip()}</h3>")
        elif line.strip() == "":
            html_lines.append("")
        else:
            html_lines.append(f"<p>{line.strip()}</p>")

    if in_code and code_lines:
        code_text = "\n".join(code_lines)
        html_lines.append("<pre><code>" + escape_html(code_text) + "</code></pre>")

    return "\n".join([l for l in html_lines if l != ""])


def escape_html(text: str) -> str:
    return (text.replace("&", "&amp;")
                .replace("<", "&lt;")
                .replace(">", "&gt;"))


def extract_note(md: str) -> str:
    for line in md.splitlines():
        if NOTE_RE.match(line):
            return NOTE_RE.sub("", line, count=1).strip()
    return ""


def format_date_from_mtime(p: Path) -> str:
    return datetime.fromtimestamp(p.stat().st_mtime).strftime("%Y-%m-%d")


def update_block(content: str, start: str, end: str, new_inner: str) -> str:
    pattern = re.compile(rf"({re.escape(start)})(.*)({re.escape(end)})", re.S)
    def repl(match):
        return match.group(1) + "\n" + new_inner + "\n" + match.group(3)
    if not pattern.search(content):
        raise ValueError(f"Markers not found: {start} / {end}")
    return pattern.sub(repl, content, count=1)


def clip_note(text: str, limit: int = 50) -> str:
    if len(text) <= limit:
        return text
    return text[:limit].rstrip() + "…"


def build_row(title: str, href: str, note: str, date: str) -> str:
    return (
        "<li>\n"
        "  <a class=\"post-row\" href=\"%s\">\n"
        "    <span class=\"post-title\">%s</span>\n"
        "    <span class=\"post-summary\">%s</span>\n"
        "    <span class=\"post-meta\">%s</span>\n"
        "  </a>\n"
        "</li>" % (href, title, note, date)
    )


def build_posts_list(items: list) -> str:
    return "\n".join([build_row(t, h, s, d) for t, h, s, d in items])


def build_latest_list(items: list) -> str:
    return "\n".join([build_row(t, h, s, d) for t, h, s, d in items])


def has_content(md_text: str) -> bool:
    lines = []
    in_code = False
    for line in md_text.splitlines():
        if CODE_FENCE.match(line.strip()):
            in_code = not in_code
            continue
        if NOTE_RE.match(line) or BODY_RE.match(line):
            continue
        if line.strip() == "":
            continue
        lines.append(line.strip())
    return len(lines) > 0


def main():
    if len(sys.argv) < 2:
        print("Usage: python scripts/generate_post.py posts_md/your-file-name.md")
        sys.exit(1)

    md_path = Path(sys.argv[1]).resolve()
    if not md_path.exists():
        raise FileNotFoundError(md_path)

    md = md_path.read_text(encoding="utf-8")
    note = extract_note(md)
    if not has_content(md) and note == "":
        print(f"Skip: {md_path.name} (no content)")
        return

    title = md_path.stem
    date = format_date_from_mtime(md_path)
    body_html = md_to_html(md)

    slug = md_path.stem
    out_html = POSTS_HTML / f"{slug}.html"

    out_html.write_text(
        POST_TEMPLATE.format(title=title, date=date, body=body_html),
        encoding="utf-8"
    )

    md_files = list(POSTS_MD.glob("*.md"))
    md_files.sort(key=lambda p: p.stat().st_mtime, reverse=True)

    posts_items = []
    latest_items = []
    for p in md_files:
        md_text = p.read_text(encoding="utf-8")
        t = p.stem
        d = format_date_from_mtime(p)
        n = clip_note(extract_note(md_text), 50)
        slug = p.stem
        posts_items.append((t, f"{slug}.html", n, d))
        latest_items.append((t, f"posts/{slug}.html", n, d))

    posts_block = build_posts_list(posts_items)
    posts_index = POSTS_INDEX_HTML.read_text(encoding="utf-8")
    posts_index = update_block(posts_index, "<!-- POSTS_LIST_START -->", "<!-- POSTS_LIST_END -->", posts_block)
    POSTS_INDEX_HTML.write_text(posts_index, encoding="utf-8")

    latest_items = latest_items[:3]
    latest_block = build_latest_list(latest_items)
    index_html = INDEX_HTML.read_text(encoding="utf-8")
    index_html = update_block(index_html, "<!-- POSTS_LATEST_START -->", "<!-- POSTS_LATEST_END -->", latest_block)
    INDEX_HTML.write_text(index_html, encoding="utf-8")

    if INDEX_EN_HTML.exists():
        index_en_html = INDEX_EN_HTML.read_text(encoding="utf-8")
        index_en_html = update_block(index_en_html, "<!-- POSTS_LATEST_START -->", "<!-- POSTS_LATEST_END -->", latest_block)
        INDEX_EN_HTML.write_text(index_en_html, encoding="utf-8")

    print(f"Generated: {out_html}")
    print("Updated posts/index.html and index.html (등록순)")


if __name__ == "__main__":
    main()
