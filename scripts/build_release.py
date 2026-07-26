"""Build Hobby + Pro release zips for Gumroad delivery."""

from __future__ import annotations

import zipfile
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "releases"
VERSION = "0.3.0"


HOBBY_GLOBS = [
    "README.md",
    "LICENSE",
    "CHANGELOG.md",
    "SUPPORT.md",
    "pyproject.toml",
    "requirements.txt",
    "docs/sales.md",
    "docs/INSTALL.md",
    "docs/landing.html",
    "docs/demo_script.md",
    "skill/**",
    "src/**",
    "tests/**",
    "examples/sample_inputs/**",
    "examples/sample_outputs/polished/**",
    "examples/case_study/**",
    "scripts/install.ps1",
    "scripts/install.sh",
    "scripts/commercial_score.py",
    "scripts/competitive_parity.py",
    "scripts/profit_ready.py",
    ".claude-plugin/plugin.json",
]


def _add_tree(z: zipfile.ZipFile, base: Path, arc_prefix: str) -> None:
    if base.is_file():
        z.write(base, arc_prefix.replace("\\", "/"))
        return
    for p in base.rglob("*"):
        if p.is_file() and ".git" not in p.parts and "__pycache__" not in p.parts:
            rel = p.relative_to(base)
            z.write(p, f"{arc_prefix}/{rel.as_posix()}")


def _expand(pattern: str) -> list[Path]:
    return [p for p in ROOT.glob(pattern) if p.exists()]


def build() -> dict:
    OUT.mkdir(parents=True, exist_ok=True)
    stamp = date.today().isoformat()
    hobby = OUT / f"everything2template-hobby-{VERSION}-{stamp}.zip"
    pro = OUT / f"everything2template-pro-{VERSION}-{stamp}.zip"

    with zipfile.ZipFile(hobby, "w", zipfile.ZIP_DEFLATED) as z:
        for pat in HOBBY_GLOBS:
            for path in _expand(pat):
                if path.is_dir():
                    for f in path.rglob("*"):
                        if f.is_file() and "__pycache__" not in f.parts:
                            z.write(f, f"everything2template/{f.relative_to(ROOT).as_posix()}")
                else:
                    z.write(path, f"everything2template/{path.relative_to(ROOT).as_posix()}")

    with zipfile.ZipFile(pro, "w", zipfile.ZIP_DEFLATED) as z:
        pro_root = ROOT / "packaging" / "pro"
        for f in pro_root.rglob("*"):
            if f.is_file():
                z.write(f, f"e2t-pro/{f.relative_to(pro_root).as_posix()}")
        # include sales page for buyers
        z.write(ROOT / "docs" / "sales.md", "e2t-pro/sales.md")

    return {"hobby": str(hobby), "pro": str(pro), "version": VERSION}


if __name__ == "__main__":
    import json

    print(json.dumps(build(), indent=2))
