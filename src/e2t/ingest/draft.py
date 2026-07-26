"""Shared draft CIR helpers (no package circular imports)."""

from __future__ import annotations

import re
from pathlib import Path

from e2t.cir import CIR, Claim, Section, SourceKind
from e2t.paths import display_path


def heuristic_title(text: str, fallback: str) -> str:
    for line in text.splitlines():
        s = line.strip()
        if not s:
            continue
        if s.startswith("#"):
            return s.lstrip("#").strip()[:80]
        if len(s) >= 8:
            return s[:80]
    return fallback


def split_paragraphs(text: str) -> list[str]:
    chunks = re.split(r"\n\s*\n", text.strip())
    return [c.strip() for c in chunks if c.strip()]


def draft_cir_from_text(
    text: str,
    *,
    source_kind: SourceKind,
    source_ref: str,
    title: str | None = None,
) -> CIR:
    source_ref = display_path(source_ref)
    paras = split_paragraphs(text)
    # Prefer first non-heading paragraph as summary
    summary = ""
    for p in paras:
        line = p.split("\n", 1)[0].strip()
        if line.startswith("#"):
            continue
        if line.startswith("-") or line.startswith("*") or re.match(r"^\d+\.", line):
            continue
        summary = line[:400]
        break
    if not summary and paras:
        summary = paras[0].lstrip("# ").strip()[:400]

    sections: list[Section] = []
    key_points: list[str] = []
    # Prefer H2/H3 as sections; H1 is usually the document title
    md_secs = re.split(r"(?m)^#{2,3}\s+", text)
    if len(md_secs) > 1:
        for block in md_secs[1:10]:
            lines = block.strip().splitlines()
            if not lines:
                continue
            heading = lines[0].strip()[:80]
            body_lines = lines[1:]
            body = "\n".join(body_lines).strip()[:2200]
            bullets = [
                ln.lstrip("-*• ").strip()
                for ln in body_lines
                if ln.strip().startswith(("-", "*", "•"))
                or re.match(r"^\d+[\.、]\s*", ln.strip())
            ]
            bullets = [re.sub(r"^\d+[\.、]\s*", "", b).strip() for b in bullets if b.strip()]
            bullets = bullets[:10]
            sections.append(Section(heading=heading, body=body, bullets=bullets))
            if bullets:
                key_points.extend(bullets[:4])
            elif body:
                first = body.split("\n", 1)[0].strip()[:160]
                if first:
                    key_points.append(first)
    else:
        for i, p in enumerate(paras[:8], 1):
            if p.startswith("#"):
                continue
            sections.append(Section(heading=f"要点 {i}", body=p[:1500], bullets=[]))
            key_points.append(p.split("\n", 1)[0].strip()[:160])

    # Also harvest list items globally
    for ln in text.splitlines():
        s = ln.strip()
        if s.startswith(("-", "*", "•")) or re.match(r"^\d+[\.、]\s+\S", s):
            item = re.sub(r"^([-*•]|\d+[\.、])\s*", "", s).strip()
            if item and item not in key_points:
                key_points.append(item[:160])

    # de-dupe
    seen: set[str] = set()
    uniq: list[str] = []
    for kp in key_points:
        if not kp or kp in seen:
            continue
        seen.add(kp)
        uniq.append(kp)
    key_points = uniq[:12]

    claims = [
        Claim(text=kp, evidence=source_ref, confidence=0.6) for kp in key_points[:6]
    ]
    resolved_title = title or heuristic_title(text, Path(source_ref).stem or "untitled")
    return CIR(
        source_kind=source_kind,
        source_ref=source_ref,
        title=resolved_title,
        summary=summary,
        key_points=key_points,
        claims=claims,
        sections=sections,
        raw_excerpt=text[:12000],
        tags=[],
        risks=["CIR 由规则抽取；发布前请核对事实。"],
        tone_hints=["hook-first", "concrete", "traffic-aware", "no-fabricated-facts"],
    )
