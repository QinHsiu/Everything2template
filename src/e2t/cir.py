"""Canonical Intermediate Representation — extract once, adapt many times."""

from __future__ import annotations

from datetime import datetime, timezone
from enum import Enum
from pathlib import Path
from typing import Any
from uuid import uuid4

from pydantic import BaseModel, Field

from e2t.paths import display_path


class SourceKind(str, Enum):
    url = "url"
    pdf = "pdf"
    docx = "docx"
    markdown = "markdown"
    text = "text"
    code = "code"
    project = "project"
    mixed = "mixed"


class Claim(BaseModel):
    text: str
    evidence: str | None = None
    confidence: float = Field(default=0.7, ge=0.0, le=1.0)


class Section(BaseModel):
    heading: str
    body: str
    bullets: list[str] = Field(default_factory=list)


class CIR(BaseModel):
    """Canonical Intermediate Representation."""

    id: str = Field(default_factory=lambda: uuid4().hex[:12])
    created_at: str = Field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )
    source_kind: SourceKind
    source_ref: str
    title: str = ""
    summary: str = ""
    audience: str = ""
    tone_hints: list[str] = Field(default_factory=list)
    key_points: list[str] = Field(default_factory=list)
    claims: list[Claim] = Field(default_factory=list)
    sections: list[Section] = Field(default_factory=list)
    quotes: list[str] = Field(default_factory=list)
    code_snippets: list[dict[str, str]] = Field(default_factory=list)
    tags: list[str] = Field(default_factory=list)
    risks: list[str] = Field(default_factory=list)
    raw_excerpt: str = ""
    meta: dict[str, Any] = Field(default_factory=dict)

    def to_brief(self, max_chars: int = 6000) -> str:
        ref = display_path(self.source_ref)
        parts: list[str] = [
            f"# {self.title or '(untitled)'}",
            f"Source: {self.source_kind.value} | {ref}",
            "",
            "## Summary",
            self.summary or "(none)",
            "",
            "## Key points",
        ]
        parts.extend(f"- {p}" for p in self.key_points[:20])
        if self.sections:
            parts.append("")
            parts.append("## Sections")
            for s in self.sections[:12]:
                parts.append(f"### {s.heading}")
                parts.append(s.body[:800])
                for b in s.bullets[:8]:
                    parts.append(f"- {b}")
        if self.code_snippets:
            parts.append("")
            parts.append("## Code snippets")
            for snip in self.code_snippets[:5]:
                lang = snip.get("lang", "")
                parts.append(f"```{lang}")
                parts.append(snip.get("code", "")[:1200])
                parts.append("```")
        if self.risks:
            parts.append("")
            parts.append("## Risks / caveats")
            parts.extend(f"- {r}" for r in self.risks)
        text = "\n".join(parts).strip()
        if len(text) > max_chars:
            return text[: max_chars - 20] + "\n\n…[truncated]"
        return text

    def save(self, path: str | Path) -> Path:
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(self.model_dump_json(indent=2), encoding="utf-8")
        return path

    @classmethod
    def load(cls, path: str | Path) -> "CIR":
        return cls.model_validate_json(Path(path).read_text(encoding="utf-8"))
