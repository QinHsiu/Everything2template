"""Code file or project directory → CIR (structure + key files)."""

from __future__ import annotations

from pathlib import Path

from e2t.cir import CIR, Section, SourceKind
from e2t.ingest.draft import draft_cir_from_text
from e2t.paths import display_path

SKIP_DIRS = {
    ".git",
    ".hg",
    ".svn",
    ".venv",
    "venv",
    "node_modules",
    "__pycache__",
    ".mypy_cache",
    ".pytest_cache",
    "dist",
    "build",
    ".next",
    "target",
    "out",
}

PRIORITY_NAMES = {
    "readme.md",
    "readme.rst",
    "readme.txt",
    "pyproject.toml",
    "package.json",
    "cargo.toml",
    "go.mod",
    "skill.md",
    "license",
    "license.md",
}

CODE_EXTS = {
    ".py",
    ".js",
    ".ts",
    ".tsx",
    ".jsx",
    ".go",
    ".rs",
    ".java",
    ".md",
    ".toml",
    ".yml",
    ".yaml",
    ".json",
}


def _tree_lines(root: Path, *, max_entries: int = 120) -> list[str]:
    lines: list[str] = []
    count = 0
    for p in sorted(root.rglob("*")):
        if any(part in SKIP_DIRS for part in p.parts):
            continue
        rel = p.relative_to(root).as_posix()
        if p.is_dir():
            lines.append(f"{rel}/")
        else:
            lines.append(rel)
        count += 1
        if count >= max_entries:
            lines.append("…")
            break
    return lines


def _read_capped(path: Path, limit: int = 4000) -> str:
    try:
        data = path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return ""
    if len(data) > limit:
        return data[: limit - 20] + "\n…[truncated]"
    return data


def ingest_code_or_project(path: str | Path) -> CIR:
    path = Path(path)
    if path.is_file():
        code = _read_capped(path, 12000)
        cir = draft_cir_from_text(
            f"# File: {path.name}\n\n```\n{code}\n```",
            source_kind=SourceKind.code,
            source_ref=display_path(path),
            title=path.name,
        )
        cir.code_snippets = [{"lang": path.suffix.lstrip("."), "code": code[:3000]}]
        cir.audience = "developers / technical creators"
        cir.tone_hints = ["practical", "concrete", "show-don't-tell"]
        return cir

    root = path
    tree = _tree_lines(root)
    priority_files: list[Path] = []
    for p in root.rglob("*"):
        if not p.is_file():
            continue
        if any(part in SKIP_DIRS for part in p.parts):
            continue
        if p.name.lower() in PRIORITY_NAMES or p.suffix.lower() in CODE_EXTS:
            priority_files.append(p)
    # Prefer shallow + readme first
    priority_files.sort(
        key=lambda p: (
            0 if p.name.lower().startswith("readme") else 1,
            len(p.relative_to(root).parts),
            p.as_posix(),
        )
    )

    snippets: list[dict[str, str]] = []
    sections: list[Section] = [
        Section(
            heading="Project tree",
            body="\n".join(tree[:80]),
            bullets=tree[:20],
        )
    ]
    bodies: list[str] = [f"# Project: {root.name}", "", "## Tree", "```", *tree, "```", ""]
    for fp in priority_files[:12]:
        rel = fp.relative_to(root).as_posix()
        content = _read_capped(fp, 3500)
        if not content:
            continue
        snippets.append({"lang": fp.suffix.lstrip("."), "path": rel, "code": content[:2500]})
        sections.append(
            Section(heading=rel, body=content[:1500], bullets=[])
        )
        bodies.append(f"## {rel}\n\n```\n{content}\n```\n")

    text = "\n".join(bodies)
    cir = draft_cir_from_text(
        text,
        source_kind=SourceKind.project,
        source_ref=display_path(root),
        title=root.name,
    )
    cir.sections = sections[:14]
    cir.code_snippets = snippets[:8]
    cir.audience = "developers / builders / technical operators"
    cir.tone_hints = ["demo-driven", "problem→solution", "honest tradeoffs"]
    cir.key_points = [
        f"Project root: {root.name}",
        f"Indexed files: {len(priority_files)}",
        f"Tree entries: {len(tree)}",
        *cir.key_points[:5],
    ]
    cir.meta["file_count_indexed"] = len(priority_files)
    return cir
