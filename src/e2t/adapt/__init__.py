"""Platform adaptation: render writer briefs from CIR + templates."""

from __future__ import annotations

from pathlib import Path

from e2t.cir import CIR

PLATFORMS = ("wechat", "xiaohongshu", "zhihu", "weibo", "douyin")


def skill_templates_dir() -> Path:
    here = Path(__file__).resolve()
    repo = here.parents[3]
    return repo / "skill" / "everything2template" / "templates"


def load_template(platform: str) -> str:
    platform = platform.lower().strip()
    if platform not in PLATFORMS:
        raise ValueError(f"Unsupported platform: {platform}. Choose from {PLATFORMS}")
    path = skill_templates_dir() / f"{platform}.md"
    if not path.exists():
        raise FileNotFoundError(f"Missing template: {path}")
    return path.read_text(encoding="utf-8")


def build_writer_brief(
    cir: CIR,
    platform: str,
    *,
    mode: str = "rewrite",
    voice: str | None = None,
) -> str:
    template = load_template(platform)
    voice_block = ""
    if voice:
        try:
            from e2t.voices import load_voice

            voice_block = load_voice(voice).as_prompt_block()
        except Exception as exc:  # noqa: BLE001
            voice_block = f"(voice '{voice}' unavailable: {exc})"
    voice_line = voice_block or "Match the platform native voice; keep facts faithful to CIR."
    return "\n".join(
        [
            f"# Writer brief — {platform} / mode={mode}",
            "",
            "## Instructions",
            "1. Read the platform template rules carefully.",
            "2. Use ONLY facts present in the CIR brief (do not invent metrics, quotes, or affiliations).",
            "3. If a claim lacks evidence, mark it as 待核实 or omit it.",
            "4. Output the final article in the template's required structure.",
            "5. Voice profile / guidance:",
            voice_line,
            "",
            "## Platform template",
            template.strip(),
            "",
            "## CIR brief",
            cir.to_brief(),
            "",
            "## Required deliverables",
            "- Final article body (Markdown)",
            "- 3 alternative titles",
            "- Platform metadata block (tags/CTA/cover hints as required by template)",
            "- Risks / assumptions list (short)",
        ]
    )


def skeleton_article(cir: CIR, platform: str) -> str:
    """Backward-compatible alias — now produces full rewrite, not thin skeleton."""
    from e2t.rewrite import rewrite_article

    return rewrite_article(cir, platform, use_llm=False)
