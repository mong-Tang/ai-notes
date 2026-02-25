import html
import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DATA_FILE = ROOT / "data" / "tools.json"
TOOLS_KO_HTML = ROOT / "tools.html"
TOOLS_EN_HTML = ROOT / "tools-en.html"
INDEX_KO_HTML = ROOT / "index.html"
GITHUB = "https://github.com"


def detect_audience(tool: dict) -> str:
    if tool.get("audience") in ("user", "dev"):
        return tool["audience"]
    if tool.get("tag") and tool.get("asset"):
        return "user"
    if tool.get("path"):
        return "dev"
    raise ValueError(f"Tool '{tool.get('name', 'unknown')}' missing fields for audience detection")


def primary_url(tool: dict) -> str:
    repo = tool["repo"]
    audience = detect_audience(tool)
    if audience == "user":
        return f"{GITHUB}/{repo}/releases/download/{tool['tag']}/{tool['asset']}"
    return f"{GITHUB}/{repo}/tree/main/{tool['path'].strip('/')}"


def secondary_url(tool: dict) -> str | None:
    if detect_audience(tool) == "user":
        return f"{GITHUB}/{tool['repo']}/releases"
    return None


def primary_label(tool: dict, locale: str) -> str:
    audience = detect_audience(tool)
    if locale == "ko":
        return tool.get("label_ko", "다운로드" if audience == "user" else "소스 보기")
    return tool.get("label_en", "Download" if audience == "user" else "View Source")


def secondary_label(locale: str) -> str:
    return "출처 보기" if locale == "ko" else "View Repository"


def status_text(tool: dict, locale: str) -> str:
    audience = detect_audience(tool)
    if locale == "ko":
        return tool.get("status_ko", "배포중" if audience == "user" else "개발중")
    return tool.get("status_en", "Released" if audience == "user" else "In development")


def build_links(primary_href: str, primary_text: str, secondary_href: str | None, secondary_text: str) -> str:
    links = [
        f"<a href=\"{html.escape(primary_href, quote=True)}\" target=\"_blank\" rel=\"noopener noreferrer\">{html.escape(primary_text)}</a>"
    ]
    if secondary_href:
        links.append(
            f"<a href=\"{html.escape(secondary_href, quote=True)}\" target=\"_blank\" rel=\"noopener noreferrer\">{html.escape(secondary_text)}</a>"
        )
    return "  <div class=\"tool-links\">" + " ".join(links) + "</div>\n"


def build_card(tool: dict, locale: str) -> str:
    desc = tool.get(f"desc_{locale}") or tool.get("desc_ko", tool["name"])
    status_label = "상태" if locale == "ko" else "Status"
    return (
        "<article class=\"mini-card\">\n"
        f"  <h3>{html.escape(tool['name'])}</h3>\n"
        f"  <p>{html.escape(desc)}</p>\n"
        f"  <p><strong>{status_label}:</strong> {html.escape(status_text(tool, locale))}</p>\n"
        + build_links(
            primary_url(tool),
            primary_label(tool, locale),
            secondary_url(tool),
            secondary_label(locale),
        )
        + "</article>"
    )


def build_home_highlight_card(tool: dict, locale: str) -> str:
    desc = tool.get(f"desc_{locale}") or tool.get("desc_ko", tool["name"])
    return (
        "<article class=\"mini-card\">\n"
        f"  <h3>{html.escape(tool['name'])}</h3>\n"
        f"  <p>{html.escape(desc)}</p>\n"
        + build_links(
            primary_url(tool),
            primary_label(tool, locale),
            secondary_url(tool),
            secondary_label(locale),
        )
        + "</article>"
    )


def update_block(content: str, start: str, end: str, inner: str) -> str:
    pattern = re.compile(rf"({re.escape(start)})(.*)({re.escape(end)})", re.S)
    if not pattern.search(content):
        raise ValueError(f"Markers not found: {start} / {end}")
    return pattern.sub(rf"\1\n{inner}\n        \3", content, count=1)


def build_cards(tools: list[dict], locale: str) -> str:
    return "\n".join(build_card(t, locale) for t in tools)


def select_recent_tools(tools: list[dict], limit: int = 3) -> list[dict]:
    if limit <= 0:
        return []
    return list(reversed(tools[-limit:]))


def build_home_highlight_cards(tools: list[dict], locale: str) -> str:
    return "\n".join(build_home_highlight_card(t, locale) for t in tools)


def main() -> None:
    data = json.loads(DATA_FILE.read_text(encoding="utf-8"))
    tools = data.get("tools", [])

    ko_cards = build_cards(tools, "ko")
    en_cards = build_cards(tools, "en")

    ko_html = TOOLS_KO_HTML.read_text(encoding="utf-8")
    ko_html = update_block(ko_html, "<!-- TOOLS_CARDS_KO_START -->", "<!-- TOOLS_CARDS_KO_END -->", ko_cards)
    TOOLS_KO_HTML.write_text(ko_html, encoding="utf-8")

    en_html = TOOLS_EN_HTML.read_text(encoding="utf-8")
    en_html = update_block(en_html, "<!-- TOOLS_CARDS_EN_START -->", "<!-- TOOLS_CARDS_EN_END -->", en_cards)
    TOOLS_EN_HTML.write_text(en_html, encoding="utf-8")

    recent_tools = select_recent_tools(tools, 3)
    home_cards = build_home_highlight_cards(recent_tools, "ko")

    index_ko_html = INDEX_KO_HTML.read_text(encoding="utf-8")
    index_ko_html = update_block(
        index_ko_html,
        "<!-- HOME_TOOLS_HIGHLIGHT_START -->",
        "<!-- HOME_TOOLS_HIGHLIGHT_END -->",
        home_cards,
    )
    INDEX_KO_HTML.write_text(index_ko_html, encoding="utf-8")

    print("Updated tools.html, tools-en.html, and index.html from data/tools.json")


if __name__ == "__main__":
    main()
