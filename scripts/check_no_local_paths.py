"""Quick check: no machine-local absolute paths in tracked text artifacts."""

from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SKIP = {".git", ".venv", "venv", "__pycache__", "releases", "competitors", "content/runs"}
SUFFIX = {".md", ".json", ".html", ".yml", ".yaml", ".toml", ".txt", ".example"}

BAD = re.compile(
    r"PycharmProjects|/Users/\w+/|httpissues|(?<![A-Za-z])[A-Za-z]:\\(?:Users|PycharmProjects)\\",
    re.I,
)


def main() -> int:
    bad: list[str] = []
    for path in ROOT.rglob("*"):
        if not path.is_file():
            continue
        if any(p in SKIP for p in path.parts):
            continue
        if "content" in path.parts and "runs" in path.parts:
            continue
        if path.suffix.lower() not in SUFFIX:
            continue
        text = path.read_text(encoding="utf-8", errors="ignore")
        if BAD.search(text):
            bad.append(path.relative_to(ROOT).as_posix())
    if bad:
        print("FAIL")
        for b in bad:
            print(b)
        return 1
    print("OK no local absolute paths in docs/metrics")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
