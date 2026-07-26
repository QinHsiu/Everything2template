"""WeChat Official Account paste-friendly HTML (inline CSS)."""

from __future__ import annotations

import html
import re
from pathlib import Path


def _inline(text: str) -> str:
    pieces: list[str] = []
    pos = 0
    for m in re.finditer(r"\*\*(.+?)\*\*", text):
        pieces.append(html.escape(text[pos : m.start()]))
        pieces.append(f"<strong>{html.escape(m.group(1))}</strong>")
        pos = m.end()
    pieces.append(html.escape(text[pos:]))
    return "".join(pieces)


def _p(inner: str) -> str:
    return (
        f'<p style="margin:0 0 1em;font-size:15px;line-height:1.75;color:#3f3f3f;'
        f'letter-spacing:0.5px;">{inner}</p>'
    )


def _h(text: str, level: int) -> str:
    sizes = {1: 20, 2: 17, 3: 16}
    return (
        f'<h{level} style="font-size:{sizes.get(level, 16)}px;font-weight:700;'
        f'margin:1.1em 0 0.5em;color:#1a1a1a;line-height:1.4;">'
        f"{html.escape(text)}</h{level}>"
    )


def markdown_to_wechat_html(md: str, *, title: str | None = None) -> str:
    """Minimal MD→WeChat HTML suitable for pasting into the official editor."""
    parts: list[str] = []
    if title:
        parts.append(_h(title, 1))
    para: list[str] = []

    def flush() -> None:
        nonlocal para
        if not para:
            return
        parts.append(_p(_inline(" ".join(para))))
        para = []

    in_code = False
    for raw in md.splitlines():
        line = raw.rstrip()
        if line.startswith("```"):
            in_code = not in_code
            flush()
            continue
        if in_code:
            parts.append(
                f'<p style="margin:0;font-family:Consolas,monospace;font-size:13px;'
                f'background:#f6f8fa;">{html.escape(line)}</p>'
            )
            continue
        if not line.strip():
            flush()
            continue
        if line.startswith("### "):
            flush()
            parts.append(_h(line[4:].strip(), 3))
        elif line.startswith("## "):
            flush()
            parts.append(_h(line[3:].strip(), 2))
        elif line.startswith("# "):
            flush()
            parts.append(_h(line[2:].strip(), 1))
        elif line.startswith(">"):
            flush()
            parts.append(
                '<blockquote style="margin:0 0 1em;padding:0.6em 1em;'
                'border-left:4px solid #07c160;background:#f7f7f7;color:#666;font-size:14px;">'
                f"{_inline(line.lstrip('> ').strip())}</blockquote>"
            )
        elif re.match(r"^[-*]\s+", line):
            flush()
            parts.append(_p("• " + _inline(re.sub(r"^[-*]\s+", "", line))))
        else:
            para.append(line)
    flush()
    body = "\n".join(parts)
    return (
        '<section style="max-width:677px;margin:0 auto;padding:0 12px;'
        "font-family:-apple-system,BlinkMacSystemFont,'PingFang SC','Helvetica Neue',sans-serif;\">"
        f"\n{body}\n</section>\n"
    )


def export_wechat_html(md: str, path: str | Path, *, title: str | None = None) -> Path:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(markdown_to_wechat_html(md, title=title), encoding="utf-8")
    return path
