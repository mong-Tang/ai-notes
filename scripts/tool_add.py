import json
import subprocess
import sys
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


ROOT = Path(__file__).resolve().parents[1]
TOOLS_JSON = ROOT / "data" / "tools.json"
GENERATE_SCRIPT = ROOT / "scripts" / "tool_generate.py"


def ask(prompt: str, default: str | None = None, required: bool = False) -> str:
    while True:
        suffix = f" [{default}]" if default else ""
        value = input(f"{prompt}{suffix}: ").strip()
        if not value and default is not None:
            return default
        if value:
            return value
        if not required:
            return ""
        print("값이 필요합니다. 다시 입력해 주세요.")


def ask_choice(prompt: str, choices: tuple[str, ...], default: str) -> str:
    allowed = "/".join(choices)
    while True:
        value = ask(f"{prompt} ({allowed})", default=default, required=True).lower()
        if value in choices:
            return value
        print(f"허용값: {allowed}")


def ask_yes_no(prompt: str, default_yes: bool = True) -> bool:
    default = "y" if default_yes else "n"
    while True:
        v = ask(f"{prompt} (y/n)", default=default).lower()
        if v in ("y", "yes"):
            return True
        if v in ("n", "no"):
            return False
        print("y 또는 n으로 입력해 주세요.")


def github_get_json(url: str) -> dict | None:
    req = Request(
        url,
        headers={
            "Accept": "application/vnd.github+json",
            "User-Agent": "ai-notes-add-tool-script",
        },
    )
    try:
        with urlopen(req, timeout=10) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except (HTTPError, URLError, TimeoutError, json.JSONDecodeError):
        return None


def repo_exists(repo: str) -> bool:
    return github_get_json(f"https://api.github.com/repos/{repo}") is not None


def fetch_latest_release(repo: str) -> tuple[str, list[str]] | None:
    payload = github_get_json(f"https://api.github.com/repos/{repo}/releases/latest")
    if not payload:
        return None
    tag = payload.get("tag_name")
    assets = [a.get("name", "") for a in payload.get("assets", []) if a.get("name")]
    if not tag:
        return None
    return tag, assets


def fetch_release_assets_by_tag(repo: str, tag: str) -> list[str] | None:
    payload = github_get_json(f"https://api.github.com/repos/{repo}/releases/tags/{tag}")
    if not payload:
        return None
    return [a.get("name", "") for a in payload.get("assets", []) if a.get("name")]


def github_path_exists(repo: str, path: str) -> bool:
    path = path.strip("/")
    if not path:
        return False
    payload = github_get_json(f"https://api.github.com/repos/{repo}/contents/{path}?ref=main")
    return payload is not None


def pick_asset_from_list(assets: list[str]) -> str:
    if not assets:
        return ask("asset 파일명", required=True)

    print("\n발견된 asset 목록:")
    for i, a in enumerate(assets, start=1):
        print(f"  {i}. {a}")

    if ask_yes_no("목록에서 번호로 선택할까요?", default_yes=True):
        while True:
            idx = ask("번호 입력", default="1")
            if idx.isdigit() and 1 <= int(idx) <= len(assets):
                return assets[int(idx) - 1]
            print("올바른 번호를 입력해 주세요.")
    return ask("asset 파일명 직접 입력", required=True)


def load_json() -> dict:
    if not TOOLS_JSON.exists():
        return {"tools": []}
    return json.loads(TOOLS_JSON.read_text(encoding="utf-8"))


def save_json(data: dict) -> None:
    TOOLS_JSON.parent.mkdir(parents=True, exist_ok=True)
    TOOLS_JSON.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def upsert_tool(tools: list[dict], entry: dict) -> tuple[list[dict], str]:
    for i, t in enumerate(tools):
        if t.get("name", "").strip().lower() == entry["name"].strip().lower():
            tools[i] = entry
            return tools, "updated"
    tools.append(entry)
    return tools, "added"


def prompt_repo(name: str) -> str:
    while True:
        repo = ask("GitHub repo", default=f"mong-Tang/{name}", required=True)
        if repo_exists(repo):
            return repo
        print(f"repo를 찾을 수 없습니다: {repo}")
        if not ask_yes_no("다시 입력할까요?", default_yes=True):
            raise SystemExit("작업을 중단했습니다.")


def prompt_user_release(repo: str) -> tuple[str, str]:
    tag = ""
    asset = ""

    if ask_yes_no("최신 release 정보를 자동 조회할까요?", default_yes=True):
        latest = fetch_latest_release(repo)
        if latest:
            tag, assets = latest
            print(f"\n최신 tag: {tag}")
            asset = pick_asset_from_list(assets)
        else:
            print("자동 조회 실패. 수동 입력으로 진행합니다.")

    while True:
        if not tag:
            tag = ask("release tag (예: v0.1.0)", required=True)
        if not asset:
            asset = ask("asset 파일명", required=True)

        assets = fetch_release_assets_by_tag(repo, tag)
        if assets is None:
            print(f"tag를 찾을 수 없습니다: {tag}")
        elif asset not in assets:
            print(f"asset을 찾을 수 없습니다: {asset}")
            if assets:
                print("현재 tag의 asset 목록:")
                for a in assets:
                    print(f" - {a}")
        else:
            return tag, asset

        if not ask_yes_no("tag/asset을 다시 입력할까요?", default_yes=True):
            raise SystemExit("작업을 중단했습니다.")
        tag = ""
        asset = ""


def prompt_dev_path(repo: str) -> str:
    while True:
        path = ask("소스 path (예: scripts/post_new.py)", required=True).strip("/")
        if github_path_exists(repo, path):
            return path
        print(f"path를 찾을 수 없습니다: {path}")
        if not ask_yes_no("path를 다시 입력할까요?", default_yes=True):
            raise SystemExit("작업을 중단했습니다.")


def infer_default_type(audience: str) -> str:
    return "deploy" if audience == "user" else "script"


def main() -> None:
    print("=== Tool 등록 도우미 ===")
    print("입력 후 tools.json 저장 + tools 페이지 자동 생성까지 진행합니다.\n")

    data = load_json()
    tools = data.get("tools", [])

    name = ask("툴 이름(name)", required=True)
    repo = prompt_repo(name)

    audience = ask_choice("대상 audience", ("user", "dev"), default="user")
    tool_type = ask_choice("타입 type", ("deploy", "script", "other"), default=infer_default_type(audience))

    desc_ko = ask("한글 설명(desc_ko)", required=True)
    desc_en = ask("영문 설명(desc_en, 비우면 desc_ko 사용)", default="")

    entry = {
        "name": name,
        "repo": repo,
        "audience": "user" if tool_type == "deploy" else "dev",
        "type": tool_type,
        "desc_ko": desc_ko,
    }
    if desc_en:
        entry["desc_en"] = desc_en

    if tool_type == "deploy":
        tag, asset = prompt_user_release(repo)
        entry["tag"] = tag
        entry["asset"] = asset
    else:
        entry["path"] = prompt_dev_path(repo)

    if ask_yes_no("상태(status)/버튼(label)을 직접 지정할까요?", default_yes=False):
        for key in ("status_ko", "status_en", "label_ko", "label_en"):
            v = ask(key, default="")
            if v:
                entry[key] = v

    tools, mode = upsert_tool(tools, entry)
    data["tools"] = tools
    save_json(data)
    print(f"\nJSON {mode}: {name}")

    print("tools/index 페이지 생성 중...")
    subprocess.run([sys.executable, str(GENERATE_SCRIPT)], check=True, cwd=str(ROOT))
    print("완료되었습니다.")


if __name__ == "__main__":
    main()
