import time
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
POSTS_MD = ROOT / "posts_md"
GEN = ROOT / "scripts" / "post_generate.py"


def snapshot():
    files = []
    if POSTS_MD.exists():
        for p in POSTS_MD.glob("*.md"):
            try:
                stat = p.stat()
                files.append((p.name, stat.st_mtime, stat.st_size))
            except FileNotFoundError:
                continue
    return tuple(sorted(files))


def latest_md_path():
    md_files = list(POSTS_MD.glob("*.md"))
    if not md_files:
        return None
    md_files.sort(key=lambda p: p.stat().st_mtime, reverse=True)
    return md_files[0]


def run_generate(target: Path):
    print(f"[watch] change detected → generate from: {target.name}")
    subprocess.run(["python", str(GEN), str(target)], check=False)


def main():
    print("[watch] watching posts_md for changes...")
    prev = snapshot()
    while True:
        time.sleep(2)
        cur = snapshot()
        if cur != prev:
            target = latest_md_path()
            if target:
                run_generate(target)
            prev = cur


if __name__ == "__main__":
    main()
