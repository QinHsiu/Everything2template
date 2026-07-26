"""Shared convert pipeline used by CLI and web trial."""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

from e2t.adapt import PLATFORMS
from e2t.compliance import check_compliance
from e2t.export import export_markdown, export_wechat_html
from e2t.humanize import humanize
from e2t.images import build_image_plan
from e2t.ingest import ingest
from e2t.rewrite import rewrite_article
from e2t.rewrite_llm import llm_configured
from e2t.titles import title_variants
from e2t.validate import validate_article


PLATFORM_LABELS = {
    "wechat": "微信公众号",
    "xiaohongshu": "小红书",
    "zhihu": "知乎",
    "weibo": "微博",
    "douyin": "抖音口播",
}


def _quality_bonus(platform: str, draft: str) -> float:
    """Extra score for hook/length/substance (commercial effect)."""
    n = len(re.sub(r"\s+", "", draft))
    bonus = 0.0
    hooks = ["先说", "别再", "结论", "停一下", "立场", "钩子", "救命", "避坑"]
    if any(h in draft for h in hooks):
        bonus += 8
    if platform == "wechat" and n >= 900:
        bonus += 10
    if platform == "zhihu" and n >= 700:
        bonus += 8
    if platform == "xiaohongshu" and 180 <= n <= 1100:
        bonus += 8
    if "备选标题" in draft or "### 备选" in draft:
        bonus += 4
    return bonus


def convert_source(
    source: str,
    *,
    platforms: list[str] | None = None,
    hint: str | None = None,
    voice: str | None = None,
    out_dir: str | Path | None = None,
    do_humanize: bool = True,
    use_llm: bool = True,
) -> dict[str, Any]:
    selected = platforms or list(PLATFORMS)
    for p in selected:
        if p not in PLATFORMS:
            raise ValueError(f"Unsupported platform: {p}")

    cir = ingest(source, hint=hint)
    root = Path(out_dir) if out_dir else Path.cwd() / "content" / "runs" / "web" / cir.id
    root.mkdir(parents=True, exist_ok=True)
    cir.save(root / "cir.json")
    (root / "brief.md").write_text(cir.to_brief(), encoding="utf-8")

    outputs: list[dict[str, Any]] = []
    pass_count = 0
    quality_scores: list[float] = []
    for p in selected:
        pdir = root / p
        pdir.mkdir(parents=True, exist_ok=True)
        draft = rewrite_article(cir, p, use_llm=use_llm)
        if do_humanize:
            draft = humanize(draft).text
        (pdir / "draft.md").write_text(draft, encoding="utf-8")
        export_markdown(draft, pdir / "export" / "draft.md")
        html_path = None
        if p == "wechat":
            html_path = str(
                export_wechat_html(draft, pdir / "export" / "draft.wechat.html", title=cir.title)
            )
        titles = title_variants(cir.title, p, summary=cir.summary)
        (pdir / "titles.json").write_text(
            json.dumps(titles, ensure_ascii=False, indent=2), encoding="utf-8"
        )
        plan = build_image_plan(cir.title, cir.key_points, platform=p)
        (pdir / "image_plan.md").write_text(plan.to_markdown(), encoding="utf-8")
        v = validate_article(p, draft)
        c = check_compliance(draft, platform=p)
        q = min(100.0, v.score + _quality_bonus(p, draft))
        quality_scores.append(q)
        ok = v.ok and c.ok and q >= 65
        if ok:
            pass_count += 1
        outputs.append(
            {
                "platform": p,
                "label": PLATFORM_LABELS.get(p, p),
                "draft": draft,
                "titles": titles,
                "validate": {**v.to_dict(), "quality_score": q},
                "compliance": c.to_dict(),
                "ok": ok,
                "image_plan": plan.to_markdown(),
                "html_path": html_path,
                "draft_path": str(pdir / "draft.md"),
            }
        )

    n = max(len(outputs), 1)
    effect_score = round(sum(quality_scores) / n, 1) if quality_scores else 0.0
    gate = effect_score >= 72 and pass_count >= max(1, n // 2)
    verdict = (
        "达到可商业化写作效果：有钩子、有结构、信息来自原文，可再人工微调后发布"
        if gate
        else "未达商业化写作效果：内容偏弱或校验未过，请补充更完整原文，或配置 E2T_LLM_API_KEY 做 LLM 精修"
    )
    return {
        "cir": {
            "id": cir.id,
            "title": cir.title,
            "summary": cir.summary,
            "source_kind": cir.source_kind.value,
            "source_ref": cir.source_ref,
            "key_points": cir.key_points,
            "risks": cir.risks,
            "brief": cir.to_brief(max_chars=4000),
        },
        "out_dir": str(root),
        "platforms": outputs,
        "effect": {
            "score": effect_score,
            "pass_count": pass_count,
            "total": len(outputs),
            "verdict": verdict,
            "commercializable_hint": gate,
            "llm_enabled": llm_configured(),
            "mode": "llm+rules" if llm_configured() and use_llm else "rules-rewrite",
        },
        "voice": voice,
    }
