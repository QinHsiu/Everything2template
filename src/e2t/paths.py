"""Portable path helpers — never persist machine-local absolute paths."""

from __future__ import annotations

from pathlib import Path


def repo_root() -> Path | None:
    """Locate package repo root (directory containing pyproject.toml)."""
    here = Path(__file__).resolve()
    for parent in here.parents:
        if (parent / "pyproject.toml").exists() and (parent / "src" / "e2t").exists():
            return parent
    return None


def display_path(path: str | Path, *, base: Path | None = None) -> str:
    """Return a portable path string (repo-/cwd-relative, posix).

    Prefers paths relative to ``base``, then cwd, then repo root, then ``~/…``.
    Falls back to the filename only (never a drive-letter absolute path).
    """
    raw = str(path).strip()
    if not raw or raw in {"inline", "-"}:
        return raw or "inline"
    if raw.startswith(("http://", "https://", "file:")):
        return raw

    p = Path(raw).expanduser()
    try:
        p = p.resolve()
    except OSError:
        p = Path(raw)

    candidates: list[Path] = []
    if base is not None:
        try:
            candidates.append(base.resolve())
        except OSError:
            candidates.append(base)
    try:
        candidates.append(Path.cwd().resolve())
    except OSError:
        pass
    root = repo_root()
    if root is not None:
        candidates.append(root)

    for b in candidates:
        try:
            return p.relative_to(b).as_posix()
        except ValueError:
            continue

    try:
        home = Path.home().resolve()
        return ("~/" + p.relative_to(home).as_posix()).replace("\\", "/")
    except ValueError:
        pass

    return p.name


def rel_to_repo(path: Path | str) -> str:
    """Path relative to repo root when possible; else ``display_path``."""
    root = repo_root()
    return display_path(path, base=root)
