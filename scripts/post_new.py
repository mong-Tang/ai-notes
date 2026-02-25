import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
POSTS_MD = ROOT / "posts_md"

TEMPLATE = """note: 

body:
"""


def main():
    if len(sys.argv) < 2:
        print("Usage: python scripts/post_new.py posts_md/your-file-name")
        sys.exit(1)

    out_path = Path(sys.argv[1]).resolve()
    if out_path.suffix.lower() != ".md":
        out_path = out_path.with_suffix(".md")

    if out_path.exists():
        print(f"Error: file already exists: {out_path}")
        sys.exit(1)

    out_path.parent.mkdir(parents=True, exist_ok=True)
    content = TEMPLATE
    out_path.write_text(content, encoding="utf-8")
    print(f"Created: {out_path}")
    print("Tip: 작성 후 아래 명령으로 반영하세요.")
    print(f"  python scripts/post_generate.py {out_path}")


if __name__ == "__main__":
    main()
