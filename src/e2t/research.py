"""Optional web research enrichment for CIR (DDGS if installed)."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class ResearchHit:
    title: str
    url: str
    snippet: str = ""


@dataclass
class ResearchResult:
    query: str
    hits: list[ResearchHit] = field(default_factory=list)
    backend: str = "none"
    notes: list[str] = field(default_factory=list)

    def to_markdown(self) -> str:
        lines = [f"# Research: {self.query}", f"Backend: {self.backend}", ""]
        if self.notes:
            lines.extend(f"- {n}" for n in self.notes)
            lines.append("")
        for i, h in enumerate(self.hits, 1):
            lines.append(f"## {i}. {h.title}")
            lines.append(f"- URL: {h.url}")
            if h.snippet:
                lines.append(f"- Snippet: {h.snippet}")
            lines.append("")
        return "\n".join(lines).strip() + "\n"

    def to_dict(self) -> dict[str, Any]:
        return {
            "query": self.query,
            "backend": self.backend,
            "notes": self.notes,
            "hits": [h.__dict__ for h in self.hits],
        }


def research(query: str, *, max_results: int = 8, region: str = "zh-cn") -> ResearchResult:
    """Search the web. Uses ddgs when available; otherwise returns structured stub notes."""
    q = query.strip()
    if not q:
        return ResearchResult(query=q, notes=["Empty query"])

    try:
        from ddgs import DDGS  # type: ignore
    except ImportError:
        return ResearchResult(
            query=q,
            backend="none",
            notes=[
                "ddgs not installed — run: pip install ddgs",
                "Agent may use WebSearch instead and merge into CIR.meta['research']",
            ],
        )

    hits: list[ResearchHit] = []
    try:
        with DDGS() as ddgs:
            for row in ddgs.text(q, region=region, max_results=max_results):
                hits.append(
                    ResearchHit(
                        title=str(row.get("title") or ""),
                        url=str(row.get("href") or row.get("url") or ""),
                        snippet=str(row.get("body") or row.get("snippet") or ""),
                    )
                )
    except Exception as exc:  # noqa: BLE001
        return ResearchResult(query=q, backend="ddgs-error", notes=[str(exc)], hits=hits)

    return ResearchResult(query=q, backend="ddgs", hits=hits)
