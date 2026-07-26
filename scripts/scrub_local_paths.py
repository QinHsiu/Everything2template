"""Strip machine-local absolute paths from docs/metrics artifacts.

Never rewrites package source (src/, tests/) or http(s) URLs.
"""

from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

SKIP_DIRS = {
    ".git",
    ".venv",
    "venv",
    "__pycache__",
    "node_modules",
    "releases",
    ".pytest_cache",
    "competitors",
    "src",
    "tests",
}

TEXT_SUFFIX = {".md", ".json", ".txt", ".yml", ".yaml", ".toml", ".html", ".example"}

# Require drive letter NOT preceded by another letter (avoids matching https:)
WIN_ABS = re.compile(
    r"(?<![A-Za-z])[A-Za-z]:[\\/]+(?:Users|PycharmProjects|home)[^\n\"']*?"
    r"[\\/]+Everything2template[\\/]+",
    re.I,
)
WIN_ABS_ESC = re.compile(
    r"(?<![A-Za-z])[A-Za-z]:\\\\(?:Users|PycharmProjects|home)[^\"\n]*?"
    r"\\\\Everything2template\\\\",
    re.I,
)
UNIX_ABS = re.compile(r"/(?:Users|home)/[^\s\"']*?/Everything2template/", re.I)
LEADING_BS = re.compile(r'(["\'])\\+(src|docs|skill|examples|content|packaging|scripts)/?')


def scrub(text: str, *, is_json: bool = False) -> str:
    out = WIN_ABS.sub("", text)
    out = WIN_ABS_ESC.sub("", out)
    out = UNIX_ABS.sub("", out)
    out = LEADING_BS.sub(r"\1\2/", out)
    if is_json:
        # normalize remaining Windows separators inside JSON string values only lightly
        out = re.sub(r'(?<!https:)(?<!http:)\\\\', "/", out)
    return out


def main() -> int:
    changed = 0
    for path in ROOT.rglob("*"):
        if not path.is_file():
            continue
        if any(part in SKIP_DIRS for part in path.parts):
            continue
        if path.suffix.lower() not in TEXT_SUFFIX:
            continue
        if path.resolve() == Path(__file__).resolve():
            continue
        try:
            raw = path.read_text(encoding="utf-8")
        except (UnicodeDecodeError, OSError):
            continue
        new = scrub(raw, is_json=path.suffix.lower() == ".json")
        if new != raw:
            path.write_text(new, encoding="utf-8")
            changed += 1
            print("scrubbed", path.relative_to(ROOT).as_posix())
    print(f"done files_changed={changed}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
