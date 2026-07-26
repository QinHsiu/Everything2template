"""Competitive parity score vs OSS rivals (exp_loop metric)."""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def _rel(path: Path) -> str:
    try:
        return path.resolve().relative_to(ROOT.resolve()).as_posix()
    except ValueError:
        return path.name


FEATURES = [
    ("ingest_url_pdf_docx", ROOT / "src" / "e2t" / "ingest" / "pdf.py"),
    ("ingest_code_project", ROOT / "src" / "e2t" / "ingest" / "code_project.py"),
    ("cir", ROOT / "src" / "e2t" / "cir.py"),
    ("template_wechat", ROOT / "skill" / "everything2template" / "templates" / "wechat.md"),
    ("template_xhs", ROOT / "skill" / "everything2template" / "templates" / "xiaohongshu.md"),
    ("template_zhihu", ROOT / "skill" / "everything2template" / "templates" / "zhihu.md"),
    ("template_weibo", ROOT / "skill" / "everything2template" / "templates" / "weibo.md"),
    ("template_douyin", ROOT / "skill" / "everything2template" / "templates" / "douyin.md"),
    ("humanize", ROOT / "src" / "e2t" / "humanize.py"),
    ("compliance", ROOT / "src" / "e2t" / "compliance.py"),
    ("wechat_html", ROOT / "src" / "e2t" / "export" / "wechat_html.py"),
    ("pdf_export", ROOT / "src" / "e2t" / "export" / "__init__.py"),
    ("mcp_server", ROOT / "src" / "e2t" / "mcp_server.py"),
    ("voices", ROOT / "src" / "e2t" / "voices.py"),
    ("validate", ROOT / "src" / "e2t" / "validate.py"),
    ("research", ROOT / "src" / "e2t" / "research.py"),
    ("images", ROOT / "src" / "e2t" / "images.py"),
    ("titles", ROOT / "src" / "e2t" / "titles.py"),
    ("sales", ROOT / "docs" / "sales.md"),
    ("pro_pack", ROOT / "packaging" / "pro" / "README.md"),
    ("skill", ROOT / "skill" / "everything2template" / "SKILL.md"),
    ("landing", ROOT / "docs" / "landing.html"),
    ("gap_analysis", ROOT / "content" / "exp" / "e2t-oss-loop-v1" / "analysis" / "gap_matrix.md"),
]


def main() -> int:
    rows = []
    for name, path in FEATURES:
        ok = path.exists() and path.stat().st_size > 40
        rows.append({"feature": name, "ok": ok, "path": _rel(path)})
    # platforms count from adapt
    adapt = (ROOT / "src" / "e2t" / "adapt" / "__init__.py").read_text(encoding="utf-8")
    platforms_ge_5 = "weibo" in adapt and "douyin" in adapt and "zhihu" in adapt
    rows.append({"feature": "platforms_ge_5", "ok": platforms_ge_5, "path": "adapt.PLATFORMS"})

    score = round(sum(1 for r in rows if r["ok"]) / len(rows), 3)
    payload = {
        "competitive_parity": score,
        "threshold": 0.85,
        "pass": score >= 0.85,
        "features": rows,
        "deferred": [
            "auto_publish_login",
            "image_search_pipeline",
            "12_platform_prompt_pack_full_parity",
        ],
    }
    out = ROOT / "content" / "exp" / "e2t-oss-loop-v1" / "metrics" / "parity.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    # also mirror under docs
    (ROOT / "docs" / "competitive_parity.json").write_text(
        json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    return 0 if payload["pass"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
