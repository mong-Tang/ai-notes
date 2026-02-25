import html
import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DATA_FILE = ROOT / "data" / "youtube.json"
YOUTUBE_HTML = ROOT / "youtube.html"
INDEX_HTML = ROOT / "index.html"
DEFAULT_THUMB_DIR = "assets/img"


def update_block(content: str, start: str, end: str, inner: str) -> str:
    pattern = re.compile(rf"({re.escape(start)})(.*)({re.escape(end)})", re.S)
    if not pattern.search(content):
        raise ValueError(f"Markers not found: {start} / {end}")
    return pattern.sub(rf"\1\n{inner}\n      \3", content, count=1)


def normalize_videos(data: dict) -> list[dict]:
    def normalize_thumb_path(raw: str) -> str:
        value = str(raw).strip()
        if not value:
            value = "sample.jpg"
        if "/" not in value and "\\" not in value:
            value = f"{DEFAULT_THUMB_DIR}/{value}"
        filename = Path(value).name
        if "." not in filename:
            value = f"{value}.jpg"
        return value.replace("\\", "/")

    videos = data.get("videos", [])
    normalized: list[dict] = []
    for v in videos:
        if not v.get("title") or not v.get("url") or not v.get("thumb"):
            continue
        normalized.append(
            {
                "title": str(v["title"]).strip(),
                "url": str(v["url"]).strip(),
                "thumb": normalize_thumb_path(v["thumb"]),
                "date": str(v.get("date", "")).strip() or "-",
                "summary": str(v.get("summary", "")).strip(),
            }
        )
    normalized.sort(key=lambda x: x["date"], reverse=True)
    return normalized


def build_latest_cards(videos: list[dict], limit: int = 2) -> str:
    picks = videos[:limit]
    if not picks:
        return '<p class="subtitle">현재 공개된 영상이 없습니다. 준비되는 대로 업데이트합니다.</p>'

    cards: list[str] = []
    for idx, v in enumerate(picks, start=1):
        cards.append(
            "<article class=\"mini-card\">\n"
            f"  <a href=\"{html.escape(v['url'], quote=True)}\" target=\"_blank\" rel=\"noopener noreferrer\">\n"
            "    <span class=\"youtube-thumb-wrap\">\n"
            f"      <img class=\"youtube-thumb\" src=\"{html.escape(v['thumb'], quote=True)}\" alt=\"최신 영상 {idx} 썸네일\" />\n"
            "    </span>\n"
            "  </a>\n"
            f"  <p><a href=\"{html.escape(v['url'], quote=True)}\" target=\"_blank\" rel=\"noopener noreferrer\">{html.escape(v['title'])}</a></p>\n"
            f"  <p>{html.escape(v['summary'] or '요약 없음')}</p>\n"
            f"  <p>게시일: {html.escape(v['date'])}</p>\n"
            "</article>"
        )
    return "\n".join(cards)


def build_home_cards(videos: list[dict], limit: int = 2) -> str:
    picks = videos[:limit]
    if not picks:
        return '<p class="subtitle">현재 공개된 영상이 없습니다. 준비되는 대로 업데이트합니다.</p>'

    cards: list[str] = []
    for idx, v in enumerate(picks, start=1):
        cards.append(
            "<article class=\"mini-card\">\n"
            f"  <a href=\"{html.escape(v['url'], quote=True)}\" target=\"_blank\" rel=\"noopener noreferrer\">\n"
            "    <span class=\"youtube-thumb-wrap\">\n"
            f"      <img class=\"youtube-thumb\" src=\"{html.escape(v['thumb'], quote=True)}\" alt=\"영상 {idx} 썸네일\" />\n"
            "    </span>\n"
            "  </a>\n"
            f"  <p><a href=\"{html.escape(v['url'], quote=True)}\" target=\"_blank\" rel=\"noopener noreferrer\">{html.escape(v['title'])}</a></p>\n"
            "</article>"
        )
    return "\n".join(cards)


def build_archive_rows(videos: list[dict]) -> str:
    if not videos:
        return '<p class="subtitle">현재 공개된 영상이 없습니다. 준비되는 대로 업데이트합니다.</p>'

    rows: list[str] = []
    for v in videos:
        rows.append(
            "<div class=\"youtube-archive-row\">\n"
            f"  <span>{html.escape(v['date'])}</span>\n"
            f"  <span><a href=\"{html.escape(v['url'], quote=True)}\" target=\"_blank\" rel=\"noopener noreferrer\">{html.escape(v['title'])}</a></span>\n"
            f"  <span>{html.escape(v['summary'] or '-')}</span>\n"
            f"  <span><a href=\"{html.escape(v['url'], quote=True)}\" target=\"_blank\" rel=\"noopener noreferrer\">보기</a></span>\n"
            "</div>"
        )
    return "\n".join(rows)


def main() -> None:
    data = json.loads(DATA_FILE.read_text(encoding="utf-8"))
    videos = normalize_videos(data)

    latest_cards = build_latest_cards(videos, 2)
    home_cards = build_home_cards(videos, 2)
    archive_rows = build_archive_rows(videos)

    content = YOUTUBE_HTML.read_text(encoding="utf-8")
    content = update_block(
        content,
        "<!-- YOUTUBE_LATEST_CARDS_START -->",
        "<!-- YOUTUBE_LATEST_CARDS_END -->",
        latest_cards,
    )
    content = update_block(
        content,
        "<!-- YOUTUBE_ARCHIVE_ROWS_START -->",
        "<!-- YOUTUBE_ARCHIVE_ROWS_END -->",
        archive_rows,
    )
    YOUTUBE_HTML.write_text(content, encoding="utf-8")

    index_content = INDEX_HTML.read_text(encoding="utf-8")
    index_content = update_block(
        index_content,
        "<!-- HOME_YOUTUBE_CARDS_START -->",
        "<!-- HOME_YOUTUBE_CARDS_END -->",
        home_cards,
    )
    INDEX_HTML.write_text(index_content, encoding="utf-8")

    print("Updated youtube.html and index.html from data/youtube.json")


if __name__ == "__main__":
    main()
