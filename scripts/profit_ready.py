"""Profit-ready gate — stricter than commercializable scaffolding."""

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


CHECKS = [
    ("sales_page", ROOT / "docs" / "sales.md"),
    ("sales_has_price", ROOT / "docs" / "sales.md"),  # content check below
    ("case_study", ROOT / "examples" / "case_study" / "README.md"),
    ("claude_plugin", ROOT / ".claude-plugin" / "plugin.json"),
    ("install_ps1", ROOT / "scripts" / "install.ps1"),
    ("install_sh", ROOT / "scripts" / "install.sh"),
    ("pro_voice", ROOT / "packaging" / "pro" / "voices" / "pro_operator.json"),
    ("pro_template", ROOT / "packaging" / "pro" / "templates" / "wechat_pro.md"),
    ("pro_readme", ROOT / "packaging" / "pro" / "README.md"),
    ("build_release", ROOT / "scripts" / "build_release.py"),
    ("research_module", ROOT / "src" / "e2t" / "research.py"),
    ("images_module", ROOT / "src" / "e2t" / "images.py"),
    ("titles_module", ROOT / "src" / "e2t" / "titles.py"),
    ("converter_depth", ROOT / "skill" / "everything2template" / "references" / "converter-depth.md"),
    ("landing", ROOT / "docs" / "landing.html"),
    ("gumroad_listing", ROOT / "docs" / "gumroad_listing.md"),
]


def _ok_file(path: Path) -> bool:
    return path.exists() and path.stat().st_size > 40


def main() -> int:
    rows = []
    for name, path in CHECKS:
        if name == "sales_has_price":
            text = path.read_text(encoding="utf-8") if path.exists() else ""
            ok = ("¥99" in text or "$19" in text) and "Gumroad" in text
        else:
            ok = _ok_file(path)
        rows.append({"item": name, "ok": ok, "path": _rel(path)})

    # release zips must build
    build = subprocess.run(
        [sys.executable, str(ROOT / "scripts" / "build_release.py")],
        cwd=str(ROOT),
        capture_output=True,
        text=True,
        check=False,
    )
    zips_ok = build.returncode == 0
    hobby_zips = list((ROOT / "releases").glob("everything2template-hobby-*.zip"))
    pro_zips = list((ROOT / "releases").glob("everything2template-pro-*.zip"))
    rows.append({"item": "release_build", "ok": zips_ok, "path": "scripts/build_release.py"})
    rows.append(
        {
            "item": "hobby_zip",
            "ok": bool(hobby_zips),
            "path": _rel(hobby_zips[-1]) if hobby_zips else "",
        }
    )
    rows.append(
        {
            "item": "pro_zip",
            "ok": bool(pro_zips),
            "path": _rel(pro_zips[-1]) if pro_zips else "",
        }
    )

    # commercial + parity
    commercial = subprocess.run(
        [sys.executable, str(ROOT / "scripts" / "commercial_score.py")],
        cwd=str(ROOT),
        capture_output=True,
        text=True,
        check=False,
    )
    try:
        cpayload = json.loads(commercial.stdout)
        commercial_ok = bool(cpayload.get("commercializable"))
        parity = float(cpayload.get("competitive_parity") or 0)
    except Exception:  # noqa: BLE001
        commercial_ok = False
        parity = 0.0
        cpayload = {"error": commercial.stderr[-500:]}

    rows.append({"item": "commercializable", "ok": commercial_ok, "path": "commercial_score"})
    rows.append({"item": "parity_ge_085", "ok": parity >= 0.85, "path": f"parity={parity}"})

    # tests
    tests = subprocess.run(
        [sys.executable, "-m", "pytest", "-q"],
        cwd=str(ROOT),
        capture_output=True,
        text=True,
        check=False,
    )
    rows.append({"item": "tests_pass", "ok": tests.returncode == 0, "path": "pytest"})

    score = round(sum(1 for r in rows if r["ok"]) / len(rows), 3)
    # Live Gumroad URL still optional — product can be listed manually.
    # profit_ready requires packaging completeness >= 0.90
    payload = {
        "profit_ready_score": score,
        "threshold": 0.9,
        "profit_ready": score >= 0.9,
        "commercializable": commercial_ok,
        "competitive_parity": parity,
        "checkout_live": False,
        "note": "Checkout URL is operational step; packaging+offer must be complete first.",
        "checks": rows,
        "exhausted_plans": [
            "SaaS web UI (out of skill wedge)",
            "Auto-publish with cookies (account risk)",
        ],
        "remaining_for_revenue": [
            "Create Gumroad products and paste real checkout URLs into docs/sales.md + landing.html",
            "Upload hobby/pro zips from releases/",
            "Post launch thread + demo from docs/demo_script.md",
            "Close 3 design-partner interviews",
        ],
    }
    out = ROOT / "docs" / "profit_ready.json"
    out.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    exp = ROOT / "content" / "exp" / "e2t-profit-loop-v2" / "metrics" / "profit_ready.json"
    exp.parent.mkdir(parents=True, exist_ok=True)
    exp.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    return 0 if payload["profit_ready"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
