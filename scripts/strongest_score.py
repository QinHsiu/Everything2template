"""Open-source strongest gate — rewrite quality + parity + tests.

Target: commercializable *effect* while remaining fully open core.
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PLATFORMS = ["wechat", "xiaohongshu", "zhihu", "weibo", "douyin"]


def _rel(path: Path) -> str:
    try:
        return path.resolve().relative_to(ROOT.resolve()).as_posix()
    except ValueError:
        return path.name


def main() -> int:
    out_dir = ROOT / "content" / "exp" / "e2t-oss-strongest-v4" / "metrics" / "demo"
    out_dir.mkdir(parents=True, exist_ok=True)

    run = subprocess.run(
        [
            sys.executable,
            "-m",
            "e2t",
            "run",
            "examples/sample_inputs/demo_article.md",
            "--out-dir",
            "content/exp/e2t-oss-strongest-v4/metrics/demo",
            "--platforms",
            ",".join(PLATFORMS),
            "--no-pdf",
            "--no-llm",
        ],
        cwd=str(ROOT),
        capture_output=True,
        text=True,
        check=False,
    )

    from e2t.validate import FILLER_SPAM, validate_article

    platform_rows = []
    for p in PLATFORMS:
        draft = out_dir / p / "export" / "draft.md"
        if not draft.exists():
            draft = out_dir / p / "draft.md"
        text = draft.read_text(encoding="utf-8") if draft.exists() else ""
        vr = validate_article(p, text)
        spam = [s for s in FILLER_SPAM if s in text]
        h1 = ""
        for ln in text.splitlines():
            if ln.startswith("# "):
                h1 = ln[2:].strip()
                break
        platform_rows.append(
            {
                "platform": p,
                "ok": vr.ok and not spam and bool(text),
                "score": vr.score,
                "errors": vr.errors,
                "warnings": vr.warnings,
                "spam": spam,
                "h1": h1,
                "chars": len(text.replace(" ", "").replace("\n", "")),
                "path": _rel(draft) if draft.exists() else _rel(out_dir / p / "draft.md"),
            }
        )

    avg = round(
        sum(r["score"] for r in platform_rows) / max(len(platform_rows), 1), 2
    )
    all_ok = all(r["ok"] for r in platform_rows) and run.returncode == 0

    # competitive parity
    parity = subprocess.run(
        [sys.executable, str(ROOT / "scripts" / "competitive_parity.py")],
        cwd=str(ROOT),
        capture_output=True,
        text=True,
        check=False,
    )
    try:
        pp = json.loads(parity.stdout)
        parity_ok = float(pp.get("competitive_parity") or 0) >= 0.85
        parity_v = float(pp.get("competitive_parity") or 0)
    except Exception:  # noqa: BLE001
        parity_ok = False
        parity_v = 0.0
        pp = {}

    tests = subprocess.run(
        [sys.executable, "-m", "pytest", "-q"],
        cwd=str(ROOT),
        capture_output=True,
        text=True,
        check=False,
    )

    # Quality bar for "开源最强 / 可商用效果"
    quality_ok = avg >= 85 and all_ok
    strongest = quality_ok and parity_ok and tests.returncode == 0

    payload = {
        "strongest_ready": strongest,
        "quality_avg": avg,
        "quality_threshold": 85,
        "pipeline_ok": run.returncode == 0,
        "parity": parity_v,
        "parity_ok": parity_ok,
        "tests_ok": tests.returncode == 0,
        "platforms": platform_rows,
        "positioning": "Apache-2.0 open core — aim: best OSS multi-source→multi-platform adapter",
        "next_if_fail": [
            "Fix rewrite filler/truncation until validate errors empty",
            "Raise per-platform structure depth vs oh-my converters",
            "Keep ingest/export/MCP lead vs prompt-only packs",
        ],
    }

    out = ROOT / "docs" / "strongest_score.json"
    out.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    exp = ROOT / "content" / "exp" / "e2t-oss-strongest-v4" / "metrics" / "strongest_score.json"
    exp.parent.mkdir(parents=True, exist_ok=True)
    exp.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    return 0 if strongest else 1


if __name__ == "__main__":
    raise SystemExit(main())
