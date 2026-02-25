import html
import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DATA_FILE = ROOT / "data" / "tools.json"
TOOLS_KO_HTML = ROOT / "tools.html"
TOOLS_EN_HTML = ROOT / "tools-en.html"
INDEX_KO_HTML = ROOT / "index.html"
INDEX_EN_HTML = ROOT / "index-en.html"
GITHUB = "https://github.com"


def detect_audience(tool: dict) -> str:
    if tool.get("audience") in ("user", "dev"):
        return tool["audience"]
    if tool.get("tag") and tool.get("asset"):
        return "user"
    if tool.get("path"):
        return "dev"
    return "dev"


def detect_type(tool: dict) -> str:
    if tool.get("type") in ("deploy", "script", "other"):
        return tool["type"]
    audience = detect_audience(tool)
    return "deploy" if audience == "user" else "script"


def primary_url(tool: dict) -> str:
    repo = tool["repo"]
    tool_type = detect_type(tool)
    if tool_type == "deploy" and tool.get("tag") and tool.get("asset"):
        return f"{GITHUB}/{repo}/releases/download/{tool['tag']}/{tool['asset']}"

    path = tool.get("path", "").strip("/")
    if path:
        return f"{GITHUB}/{repo}/tree/main/{path}"
    return f"{GITHUB}/{repo}"


def secondary_url(tool: dict) -> str | None:
    tool_type = detect_type(tool)
    if tool_type == "deploy":
        return f"{GITHUB}/{tool['repo']}/releases"
    return None


def primary_label(tool: dict, locale: str) -> str:
    tool_type = detect_type(tool)
    if locale == "ko":
        return tool.get("label_ko", "다운로드" if tool_type == "deploy" else "소스 보기")
    return tool.get("label_en", "Download" if tool_type == "deploy" else "View Source")


def secondary_label(locale: str) -> str:
    return "출처 보기" if locale == "ko" else "View Repository"


def status_text(tool: dict, locale: str) -> str:
    audience = detect_audience(tool)
    if locale == "ko":
        return tool.get("status_ko", "배포중" if audience == "user" else "개발중")
    return tool.get("status_en", "Released" if audience == "user" else "In development")


def type_label(tool: dict, locale: str) -> str:
    mapping = {
        "ko": {"deploy": "배포형", "script": "스크립트", "other": "기타"},
        "en": {"deploy": "Deploy", "script": "Script", "other": "Other"},
    }
    return mapping[locale][detect_type(tool)]


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


def build_list_row(tool: dict, locale: str) -> str:
    desc = tool.get(f"desc_{locale}") or tool.get("desc_ko", tool["name"])
    type_text = type_label(tool, locale)
    primary_href = primary_url(tool)
    secondary_href = secondary_url(tool)
    tool_type = detect_type(tool)
    row_href = secondary_href if tool_type == "deploy" and secondary_href else primary_href

    actions: list[str] = []
    if tool_type == "deploy":
        actions.append(
            f"<a href=\"{html.escape(primary_href, quote=True)}\" target=\"_blank\" rel=\"noopener noreferrer\">{html.escape(primary_label(tool, locale))}</a>"
        )
        if secondary_href:
            actions.append(
                f"<a href=\"{html.escape(secondary_href, quote=True)}\" target=\"_blank\" rel=\"noopener noreferrer\">{html.escape(secondary_label(locale))}</a>"
            )

    actions_html = " ".join(actions)
    return (
        "<li>\n"
        "  <div class=\"tool-reg-row\">\n"
        f"    <a class=\"tool-reg-overlay\" href=\"{html.escape(row_href, quote=True)}\" target=\"_blank\" rel=\"noopener noreferrer\" aria-label=\"{html.escape(tool['name'])}\"></a>\n"
        f"    <span class=\"tool-reg-title\">{html.escape(tool['name'])}</span>\n"
        f"    <span class=\"tool-reg-summary\">{html.escape(desc)}</span>\n"
        f"    <span class=\"tool-reg-type\">{html.escape(type_text)}</span>\n"
        f"    <span class=\"tool-reg-actions\">{actions_html}</span>\n"
        "  </div>\n"
        "</li>"
    )


def split_recent_tools(tools: list[dict], limit: int = 3) -> tuple[list[dict], list[dict]]:
    if limit <= 0:
        return [], list(reversed(tools))
    recent = list(reversed(tools[-limit:]))
    remaining = list(reversed(tools[:-limit]))
    return recent, remaining


def build_tools_sections(tools: list[dict], locale: str) -> str:
    recent_cards, remaining_tools = split_recent_tools(tools, limit=3)

    cards_html = "\n".join(build_card(t, locale) for t in recent_cards)
    list_html = "\n".join(build_list_row(t, locale) for t in remaining_tools)

    card_title = "신규 등록 (최신 3개)" if locale == "ko" else "Newly Added (Latest 3)"
    list_title = "등록 리스트" if locale == "ko" else "Registered List"
    header_name = "이름" if locale == "ko" else "Name"
    header_summary = "설명" if locale == "ko" else "Description"
    header_type = "타입" if locale == "ko" else "Type"
    header_link = "링크" if locale == "ko" else "Link"
    empty_text = "표시할 항목이 없습니다." if locale == "ko" else "No items to display."

    cards_inner = cards_html if cards_html else f'<p class="tool-empty">{empty_text}</p>'
    list_inner = list_html if list_html else f'<p class="tool-empty">{empty_text}</p>'

    cards_block = f"<h3 class=\"tools-subtitle\">{card_title}</h3>\n<div class=\"mini-grid\">\n{cards_inner}\n</div>"
    list_block = (
        "<div class=\"tool-list-section\">\n"
        f"  <h3 class=\"tools-subtitle\">{list_title}</h3>\n"
        f"  <div class=\"tool-reg-header\"><span>{header_name}</span><span>{header_summary}</span><span>{header_type}</span><span>{header_link}</span></div>\n"
        f"  <ul class=\"tool-reg-list\">\n{list_inner}\n</ul>\n"
        "</div>"
    )

    return f"{cards_block}\n{list_block}"


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


def select_recent_tools(tools: list[dict], limit: int = 3) -> list[dict]:
    recent, _ = split_recent_tools(tools, limit=limit)
    return recent


def build_home_highlight_cards(tools: list[dict], locale: str) -> str:
    return "\n".join(build_home_highlight_card(t, locale) for t in tools)


def main() -> None:
    data = json.loads(DATA_FILE.read_text(encoding="utf-8"))
    tools = data.get("tools", [])

    ko_sections = build_tools_sections(tools, "ko")
    en_sections = build_tools_sections(tools, "en")

    ko_html = TOOLS_KO_HTML.read_text(encoding="utf-8")
    ko_html = update_block(ko_html, "<!-- TOOLS_CARDS_KO_START -->", "<!-- TOOLS_CARDS_KO_END -->", ko_sections)
    TOOLS_KO_HTML.write_text(ko_html, encoding="utf-8")

    en_html = TOOLS_EN_HTML.read_text(encoding="utf-8")
    en_html = update_block(en_html, "<!-- TOOLS_CARDS_EN_START -->", "<!-- TOOLS_CARDS_EN_END -->", en_sections)
    TOOLS_EN_HTML.write_text(en_html, encoding="utf-8")

    recent_tools = select_recent_tools(tools, 3)
    home_cards_ko = build_home_highlight_cards(recent_tools, "ko")
    home_cards_en = build_home_highlight_cards(recent_tools, "en")

    index_ko_html = INDEX_KO_HTML.read_text(encoding="utf-8")
    index_ko_html = update_block(
        index_ko_html,
        "<!-- HOME_TOOLS_HIGHLIGHT_START -->",
        "<!-- HOME_TOOLS_HIGHLIGHT_END -->",
        home_cards_ko,
    )
    INDEX_KO_HTML.write_text(index_ko_html, encoding="utf-8")

    index_en_html = INDEX_EN_HTML.read_text(encoding="utf-8")
    index_en_html = update_block(
        index_en_html,
        "<!-- HOME_TOOLS_HIGHLIGHT_START -->",
        "<!-- HOME_TOOLS_HIGHLIGHT_END -->",
        home_cards_en,
    )
    INDEX_EN_HTML.write_text(index_en_html, encoding="utf-8")

    print("Updated tools.html, tools-en.html, index.html, and index-en.html from data/tools.json")


if __name__ == "__main__":
    main()
