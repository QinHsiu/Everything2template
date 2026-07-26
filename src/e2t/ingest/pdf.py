"""PDF text extraction → CIR."""

from __future__ import annotations

from pathlib import Path

from pypdf import PdfReader

from e2t.cir import SourceKind
from e2t.ingest.draft import draft_cir_from_text
from e2t.paths import display_path


def ingest_pdf(path: str | Path, *, max_pages: int = 40):
    path = Path(path)
    reader = PdfReader(str(path))
    pages = reader.pages[:max_pages]
    chunks: list[str] = []
    for i, page in enumerate(pages, 1):
        t = (page.extract_text() or "").strip()
        if t:
            chunks.append(f"<!-- page {i} -->\n{t}")
    text = "\n\n".join(chunks).strip()
    ref = display_path(path)
    if not text:
        cir = draft_cir_from_text(
            "(empty PDF or scanned image-only PDF — OCR not enabled)",
            source_kind=SourceKind.pdf,
            source_ref=ref,
            title=path.stem,
        )
        cir.risks.append("PDF has no extractable text; consider OCR.")
        return cir
    cir = draft_cir_from_text(
        text,
        source_kind=SourceKind.pdf,
        source_ref=ref,
        title=path.stem,
    )
    cir.meta["pages"] = len(reader.pages)
    cir.meta["pages_read"] = len(pages)
    if len(reader.pages) > max_pages:
        cir.risks.append(f"Only first {max_pages} pages ingested.")
    return cir
