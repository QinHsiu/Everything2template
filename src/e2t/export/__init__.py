"""Export helpers: Markdown + PDF + WeChat HTML."""

from __future__ import annotations

import re
from pathlib import Path

from e2t.export.wechat_html import export_wechat_html, markdown_to_wechat_html

__all__ = [
    "export_markdown",
    "export_pdf",
    "export_wechat_html",
    "markdown_to_wechat_html",
]


def export_markdown(text: str, path: str | Path) -> Path:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text.strip() + "\n", encoding="utf-8")
    return path


def _find_cjk_font() -> str | None:
    # Prefer TTF over TTC — fpdf2 is more reliable with single-font files.
    candidates = [
        "C:/Windows/Fonts/simhei.ttf",
        "C:/Windows/Fonts/msyh.ttf",
        "C:/Windows/Fonts/simkai.ttf",
        "C:/Windows/Fonts/msyh.ttc",
        "C:/Windows/Fonts/simsun.ttc",
        "/System/Library/Fonts/STHeiti Light.ttc",
        "/System/Library/Fonts/PingFang.ttc",
        "/usr/share/fonts/truetype/wqy/wqy-microhei.ttc",
        "/usr/share/fonts/truetype/noto/NotoSansCJK-Regular.ttc",
        "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc",
    ]
    for c in candidates:
        if Path(c).exists():
            return c
    return None


_EMOJI_RE = re.compile(
    "["
    "\U0001F300-\U0001F9FF"
    "\U00002600-\U000026FF"
    "\U00002700-\U000027BF"
    "\U0001FA00-\U0001FAFF"
    "\U0000FE00-\U0000FE0F"
    "]+",
    flags=re.UNICODE,
)


def _sanitize_for_pdf(text: str) -> str:
    text = _EMOJI_RE.sub("", text)
    text = text.replace("\u20e3", "")  # combining keycap
    # Replace fancy dashes / bullets that some fonts miss
    repl = {
        "—": "-",
        "–": "-",
        "｜": "|",
        "•": "-",
        "·": ".",
        "“": '"',
        "”": '"',
        "‘": "'",
        "’": "'",
        "\u200b": "",
        "1️⃣": "1.",
        "2️⃣": "2.",
        "3️⃣": "3.",
        "4️⃣": "4.",
        "5️⃣": "5.",
        "6️⃣": "6.",
    }
    for a, b in repl.items():
        text = text.replace(a, b)
    # Drop other non-BMP chars
    text = "".join(ch for ch in text if ord(ch) < 0x10000)
    return text


def _md_to_plain_blocks(md: str) -> list[tuple[str, str]]:
    blocks: list[tuple[str, str]] = []
    for raw in md.splitlines():
        line = raw.rstrip()
        if not line.strip():
            blocks.append(("gap", ""))
            continue
        if line.startswith("# "):
            blocks.append(("title", line[2:].strip()))
        elif line.startswith("## "):
            blocks.append(("h2", line[3:].strip()))
        elif line.startswith("### "):
            blocks.append(("h3", line[4:].strip()))
        elif re.match(r"^[-*•]\s+", line):
            blocks.append(("bullet", re.sub(r"^[-*•]\s+", "", line)))
        elif line.startswith(">"):
            blocks.append(("quote", line.lstrip("> ").strip()))
        else:
            blocks.append(("body", line))
    return blocks


def export_pdf(text: str, path: str | Path, *, title: str | None = None) -> Path:
    """Export UTF-8 (incl. CJK) article to PDF via fpdf2."""
    from fpdf import FPDF

    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    font = _find_cjk_font()
    if not font:
        raise RuntimeError(
            "No CJK font found for PDF export. Install Microsoft YaHei / SimHei / "
            "Noto Sans CJK. Markdown export still works."
        )

    text = _sanitize_for_pdf(text)
    title = _sanitize_for_pdf(title) if title else None

    pdf = FPDF(format="A4", unit="mm")
    pdf.set_auto_page_break(auto=True, margin=18)
    pdf.set_margins(18, 18, 18)
    pdf.add_page()
    pdf.add_font("CJK", "", font)
    pdf.add_font("CJK", "B", font)

    usable = pdf.epw  # effective page width

    def write_block(style: str, content: str) -> None:
        if style == "gap":
            pdf.ln(3)
            return
        content = content.strip()
        if not content:
            return
        if style == "title":
            pdf.set_font("CJK", "B", 16)
            pdf.multi_cell(usable, 9, content)
            pdf.ln(2)
        elif style == "h2":
            pdf.set_font("CJK", "B", 13)
            pdf.multi_cell(usable, 8, content)
            pdf.ln(1)
        elif style == "h3":
            pdf.set_font("CJK", "B", 11)
            pdf.multi_cell(usable, 7, content)
        elif style == "bullet":
            pdf.set_font("CJK", "", 11)
            pdf.multi_cell(usable, 7, f"- {content}")
        elif style == "quote":
            pdf.set_font("CJK", "", 10)
            pdf.multi_cell(usable, 6, f"| {content}")
        else:
            pdf.set_font("CJK", "", 11)
            pdf.multi_cell(usable, 7, content)

    if title:
        write_block("title", title)

    for style, content in _md_to_plain_blocks(text):
        write_block(style, content)

    pdf.output(str(path))
    return path
