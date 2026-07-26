"""Commercial readiness score for v0 productization loop."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def _rel(path: Path) -> str:
    try:
        return path.resolve().relative_to(ROOT.resolve()).as_posix()
    except ValueError:
        return path.name


PRODUCT_CHECKS = [
    ("README.md", ROOT / "README.md"),
    ("LICENSE", ROOT / "LICENSE"),
    ("pyproject.toml", ROOT / "pyproject.toml"),
    ("SKILL.md", ROOT / "skill" / "everything2template" / "SKILL.md"),
    ("wechat template", ROOT / "skill" / "everything2template" / "templates" / "wechat.md"),
    ("xhs template", ROOT / "skill" / "everything2template" / "templates" / "xiaohongshu.md"),
    ("zhihu template", ROOT / "skill" / "everything2template" / "templates" / "zhihu.md"),
    ("weibo template", ROOT / "skill" / "everything2template" / "templates" / "weibo.md"),
    ("douyin template", ROOT / "skill" / "everything2template" / "templates" / "douyin.md"),
    ("humanize", ROOT / "src" / "e2t" / "humanize.py"),
    ("wechat_html", ROOT / "src" / "e2t" / "export" / "wechat_html.py"),
    ("mcp_server", ROOT / "src" / "e2t" / "mcp_server.py"),
    ("competitive doc", ROOT / "docs" / "competitive.md"),
    ("gtm doc", ROOT / "docs" / "gtm.md"),
    ("demo input", ROOT / "examples" / "sample_inputs" / "demo_article.md"),
    ("cli module", ROOT / "src" / "e2t" / "cli.py"),
    ("tests", ROOT / "tests" / "test_pipeline.py"),
]

GTM_CHECKS = [
    ("landing_md", ROOT / "docs" / "landing.md"),
    ("landing_html", ROOT / "docs" / "landing.html"),
    ("changelog", ROOT / "CHANGELOG.md"),
    ("support", ROOT / "SUPPORT.md"),
    ("waitlist_issue_template", ROOT / ".github" / "ISSUE_TEMPLATE" / "pro-waitlist.yml"),
    ("design_partners_log", ROOT / "docs" / "design_partners.md"),
    ("polished_samples", ROOT / "examples" / "sample_outputs" / "polished" / "wechat.md"),
    ("demo_script", ROOT / "docs" / "demo_script.md"),
]


def _ok(path: Path) -> bool:
    return path.exists() and path.stat().st_size > 20


def _parity() -> dict:
    script = ROOT / "scripts" / "competitive_parity.py"
    proc = subprocess.run(
        [sys.executable, str(script)],
        cwd=str(ROOT),
        capture_output=True,
        text=True,
        check=False,
    )
    return json.loads(proc.stdout)


def main() -> int:
    product_rows = [
        {"item": name, "ok": _ok(path), "path": _rel(path)} for name, path in PRODUCT_CHECKS
    ]
    gtm_rows = [
        {"item": name, "ok": _ok(path), "path": _rel(path)} for name, path in GTM_CHECKS
    ]
    product_score = round(100 * sum(1 for r in product_rows if r["ok"]) / len(product_rows), 1)
    gtm_score = round(100 * sum(1 for r in gtm_rows if r["ok"]) / len(gtm_rows), 1)
    parity = _parity()
    parity_score = float(parity.get("competitive_parity", 0))

    commercializable = (
        product_score >= 90 and gtm_score >= 75 and parity_score >= 0.85
    )
    payload = {
        "product_score": product_score,
        "product_ready_for_pro_core": product_score >= 90,
        "gtm_score": gtm_score,
        "competitive_parity": parity_score,
        "commercializable": commercializable,
        "growth_kpis_manual": {
            "stripe_or_gumroad_live": False,
            "waitlist_count": 0,
            "design_partners_active": 0,
            "target_waitlist": 50,
            "target_design_partners": 3,
        },
        "next_actions": [
            "Publish docs/landing.html or equivalent public page",
            "Open Pro waitlist via GitHub issue template",
            "Recruit 3 design partners; log in docs/design_partners.md",
            "Record demo from docs/demo_script.md",
            "Connect Stripe/Gumroad when waitlist converts",
        ],
        "product_checks": product_rows,
        "gtm_checks": gtm_rows,
        "parity": parity,
    }
    out = ROOT / "docs" / "commercial_score.json"
    out.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    exp_metrics = (
        ROOT / "content" / "exp" / "e2t-oss-loop-v1" / "metrics" / "summary.json"
    )
    exp_metrics.parent.mkdir(parents=True, exist_ok=True)
    exp_metrics.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    return 0 if commercializable else 1


if __name__ == "__main__":
    raise SystemExit(main())
