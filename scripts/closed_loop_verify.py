"""Verify Tecience commercial closed-loop readiness (product-side)."""

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


def _has(path: Path, *needles: str) -> bool:
    if not path.exists() or path.stat().st_size < 20:
        return False
    if not needles:
        return True
    text = path.read_text(encoding="utf-8")
    return all(n in text for n in needles)


def main() -> int:
    rows: list[dict] = []

    checks: list[tuple[str, bool, str]] = [
        (
            "funnel_doc",
            _has(ROOT / "docs" / "tecience_funnel.md", "Tecience", "E2T"),
            "docs/tecience_funnel.md",
        ),
        (
            "pay_doc",
            _has(ROOT / "docs" / "pay_tecience.md", "¥99", "已付"),
            "docs/pay_tecience.md",
        ),
        (
            "sales_tecience",
            _has(ROOT / "docs" / "sales.md", "Tecience", "E2T"),
            "docs/sales.md",
        ),
        (
            "landing_tecience",
            _has(ROOT / "docs" / "landing.html", "Tecience", "E2T"),
            "docs/landing.html",
        ),
        (
            "trial_cta",
            _has(ROOT / "src" / "e2t" / "web_static" / "index.html", "Tecience", "E2T"),
            "web_static/index.html",
        ),
        (
            "auto_reply",
            _has(ROOT / "content" / "publish" / "tecience" / "auto_reply.md", "E2T", "¥99"),
            "content/publish/tecience/auto_reply.md",
        ),
        (
            "launch_article",
            _has(
                ROOT / "content" / "publish" / "tecience" / "launch_wechat.md",
                "Tecience",
                "E2T",
            ),
            "content/publish/tecience/launch_wechat.md",
        ),
        (
            "source_brief",
            _has(ROOT / "content" / "publish" / "tecience" / "source_brief.md", "OpenAlex"),
            "content/publish/tecience/source_brief.md",
        ),
        (
            "ops_playbook",
            _has(ROOT / "content" / "publish" / "tecience" / "OPS.md", "发表", "关键词"),
            "content/publish/tecience/OPS.md",
        ),
        (
            "wechat_template_depth",
            _has(
                ROOT / "skill" / "everything2template" / "templates" / "wechat.md",
                "引子",
                "Tecience",
            ),
            "templates/wechat.md",
        ),
        (
            "xhs_template_depth",
            _has(
                ROOT / "skill" / "everything2template" / "templates" / "xiaohongshu.md",
                "共鸣",
                "收藏",
            ),
            "templates/xiaohongshu.md",
        ),
        (
            "ollama_provider",
            _has(ROOT / "src" / "e2t" / "rewrite_llm.py", "ollama"),
            "rewrite_llm.py ollama",
        ),
        (
            "pro_readme",
            _has(ROOT / "packaging" / "pro" / "README.md", "e2t"),
            "packaging/pro/README.md",
        ),
    ]

    for name, ok, path in checks:
        rows.append({"item": name, "ok": ok, "path": path})

    # launch wechat html export
    launch_md = ROOT / "content" / "publish" / "tecience" / "launch_wechat.md"
    launch_html = ROOT / "content" / "publish" / "tecience" / "launch_wechat.wechat.html"
    html_ok = False
    if launch_md.exists():
        try:
            from e2t.export import export_wechat_html

            export_wechat_html(
                launch_md.read_text(encoding="utf-8"),
                launch_html,
                title="一稿五发太累？我把保真改写做成了本地工具",
            )
            html_ok = launch_html.exists() and "Tecience" in launch_html.read_text(
                encoding="utf-8"
            )
        except Exception as exc:  # noqa: BLE001
            rows.append({"item": "launch_html_error", "ok": False, "path": str(exc)})
    rows.append({"item": "launch_html", "ok": html_ok, "path": _rel(launch_html)})
    # release zips
    build = subprocess.run(
        [sys.executable, str(ROOT / "scripts" / "build_release.py")],
        cwd=str(ROOT),
        capture_output=True,
        text=True,
        check=False,
    )
    pro_zips = list((ROOT / "releases").glob("everything2template-pro-*.zip"))
    rows.append({"item": "release_build", "ok": build.returncode == 0, "path": "build_release"})
    rows.append(
        {
            "item": "pro_zip",
            "ok": bool(pro_zips),
            "path": _rel(pro_zips[-1]) if pro_zips else "",
        }
    )

    # demo pipeline smoke
    demo = "examples/sample_inputs/demo_article.md"
    out_dir = ROOT / "content" / "exp" / "e2t-closed-loop-v3" / "demo_run"
    run = subprocess.run(
        [
            sys.executable,
            "-m",
            "e2t",
            "run",
            demo,
            "--out-dir",
            "content/exp/e2t-closed-loop-v3/demo_run",
            "--platforms",
            "wechat,xiaohongshu",
            "--no-pdf",
            "--no-llm",
        ],
        cwd=str(ROOT),
        capture_output=True,
        text=True,
        check=False,
    )
    draft = out_dir / "wechat" / "export" / "draft.md"
    draft_ok = run.returncode == 0 and draft.exists() and draft.stat().st_size > 200
    rows.append({"item": "pipeline_demo", "ok": draft_ok, "path": _rel(draft)})

    # tests
    tests = subprocess.run(
        [sys.executable, "-m", "pytest", "-q"],
        cwd=str(ROOT),
        capture_output=True,
        text=True,
        check=False,
    )
    rows.append({"item": "tests_pass", "ok": tests.returncode == 0, "path": "pytest"})

    # commercial score
    commercial = subprocess.run(
        [sys.executable, str(ROOT / "scripts" / "commercial_score.py")],
        cwd=str(ROOT),
        capture_output=True,
        text=True,
        check=False,
    )
    commercial_ok = False
    try:
        cpayload = json.loads(commercial.stdout)
        commercial_ok = bool(cpayload.get("commercializable"))
    except Exception:  # noqa: BLE001
        cpayload = {}
    rows.append({"item": "commercializable", "ok": commercial_ok, "path": "commercial_score"})

    score = round(sum(1 for r in rows if r["ok"]) / max(len(rows), 1), 3)
    # Product-side closed loop: packaging + Tecience funnel + publish assets.
    # Live WeChat publish / first payment is operator action (documented in OPS).
    closed = score >= 0.92 and all(
        next(r["ok"] for r in rows if r["item"] == i)
        for i in (
            "funnel_doc",
            "pay_doc",
            "sales_tecience",
            "launch_article",
            "launch_html",
            "auto_reply",
            "pro_zip",
            "pipeline_demo",
            "trial_cta",
        )
    )

    payload = {
        "closed_loop_score": score,
        "threshold": 0.92,
        "closed_loop_ready": closed,
        "pay_channel": "Tecience WeChat OA",
        "operator_remaining": [
            "在微信公众平台登录 Tecience，粘贴 launch_wechat.wechat.html 并发表",
            "配置关键词自动回复（content/publish/tecience/auto_reply.md）",
            "在 docs/pay_tecience.md 填入真实收款码（勿提交密钥到 git）",
        ],
        "checks": rows,
        "commercial_score": cpayload,
    }

    out = ROOT / "docs" / "closed_loop.json"
    out.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    exp = ROOT / "content" / "exp" / "e2t-closed-loop-v3" / "metrics" / "closed_loop.json"
    exp.parent.mkdir(parents=True, exist_ok=True)
    exp.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    return 0 if closed else 1


if __name__ == "__main__":
    raise SystemExit(main())
