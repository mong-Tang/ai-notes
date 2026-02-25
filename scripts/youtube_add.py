import json
import subprocess
import sys
from datetime import datetime
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DATA_FILE = ROOT / "data" / "youtube.json"
GENERATE_SCRIPT = ROOT / "scripts" / "youtube_generate.py"
DEFAULT_THUMB_DIR = "assets/img"


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


def load_data() -> dict:
    if not DATA_FILE.exists():
        return {"videos": []}
    return json.loads(DATA_FILE.read_text(encoding="utf-8"))


def save_data(data: dict) -> None:
    DATA_FILE.parent.mkdir(parents=True, exist_ok=True)
    DATA_FILE.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def normalize_thumb_path(raw: str) -> str:
    value = raw.strip()
    if not value:
        value = "sample.jpg"

    # 경로 구분자가 없으면 assets/img 고정 경로로 보정
    if "/" not in value and "\\" not in value:
        value = f"{DEFAULT_THUMB_DIR}/{value}"

    # 확장자가 없으면 jpg 자동 보정
    filename = Path(value).name
    if "." not in filename:
        value = f"{value}.jpg"

    return value.replace("\\", "/")


def main() -> None:
    print("=== YouTube 영상 등록 도우미 ===")

    today = datetime.now().strftime("%Y-%m-%d")
    title = ask("제목", required=True)
    url = ask("영상 URL", required=True)
    thumb_input = ask("썸네일 경로(파일명만 입력 가능)", default="sample.jpg", required=True)
    thumb = normalize_thumb_path(thumb_input)
    date = ask("등록일자(YYYY-MM-DD)", default=today, required=True)
    summary = ask("1줄 요약", default="")

    data = load_data()
    videos = data.get("videos", [])
    videos.append(
        {
            "title": title,
            "url": url,
            "thumb": thumb,
            "date": date,
            "summary": summary,
        }
    )
    data["videos"] = videos
    save_data(data)

    subprocess.run([sys.executable, str(GENERATE_SCRIPT)], check=True, cwd=str(ROOT))
    print("완료: data/youtube.json 저장 + youtube.html 갱신")


if __name__ == "__main__":
    main()
