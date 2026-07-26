"""Source ingestion: URL / PDF / DOCX / MD / text / code / project → CIR draft."""

from __future__ import annotations

import re
from pathlib import Path

from e2t.cir import CIR, SourceKind
from e2t.ingest.code_project import ingest_code_or_project
from e2t.ingest.docx_md import ingest_docx, ingest_markdown, ingest_text_file
from e2t.ingest.draft import draft_cir_from_text
from e2t.ingest.pdf import ingest_pdf
from e2t.ingest.url import ingest_url

CODE_EXTS = {
    ".py",
    ".js",
    ".ts",
    ".tsx",
    ".jsx",
    ".go",
    ".rs",
    ".java",
    ".kt",
    ".c",
    ".cpp",
    ".h",
    ".cs",
    ".rb",
    ".php",
    ".swift",
    ".scala",
    ".sh",
    ".sql",
}


def ingest(source: str, *, hint: str | None = None) -> CIR:
    """Auto-detect source type and ingest into a draft CIR."""
    s = source.strip()
    kind = (hint or "").lower().strip() or None

    if kind == "url" or (kind is None and re.match(r"^https?://", s, re.I)):
        return ingest_url(s)

    path = Path(s)
    if path.exists():
        if path.is_dir() or kind in {"project", "code"}:
            return ingest_code_or_project(path)
        suf = path.suffix.lower()
        if kind == "pdf" or suf == ".pdf":
            return ingest_pdf(path)
        if kind == "docx" or suf in {".docx"}:
            return ingest_docx(path)
        if kind in {"markdown", "md"} or suf in {".md", ".markdown"}:
            return ingest_markdown(path)
        if kind == "code" or suf in CODE_EXTS:
            return ingest_code_or_project(path)
        if kind == "text" or suf in {".txt", ".rst", ".log"}:
            return ingest_text_file(path)
        return ingest_text_file(path)

    return draft_cir_from_text(
        s, source_kind=SourceKind.text, source_ref="inline", title=None
    )
