"""Generate Tecience brand + multi QR assets (portable; no machine abs paths).

Run from Everything2template repo root, or pass sibling roots via env:

  TECIENCE_SIBLING_ROOT=..  python scripts/gen_tecience_assets.py

By default, discovers sibling project dirs next to this repo.
"""

from __future__ import annotations

import os
from pathlib import Path

import qrcode
from PIL import Image, ImageDraw, ImageFont

HERE = Path(__file__).resolve().parent
THIS_REPO = HERE.parent
SIBLING_ROOT = Path(os.environ.get("TECIENCE_SIBLING_ROOT", THIS_REPO.parent)).resolve()

PROJECTS = [
    {
        "dirname": "Doctor_query_skill",
        "name": "Doctor_Query",
        "repo": "https://github.com/QinHsiu/Doctor_query_skill",
        "keyword": "DOCTOR",
    },
    {
        "dirname": "Paper_Rec_Skill",
        "name": "Paper_Rec",
        "repo": "https://github.com/QinHsiu/Paper_Rec_Skill",
        "keyword": "PAPER",
    },
    {
        "dirname": "Compass",
        "name": "Compass",
        "repo": "https://github.com/QinHsiu/Compass",
        "keyword": "COMPASS",
    },
    {
        "dirname": "Everything2template",
        "name": "Everything2template",
        "repo": "https://github.com/QinHsiu/Everything2template",
        "keyword": "E2T",
    },
]

ORG = "https://github.com/QinHsiu"
WECHAT_HINT = "微信公众号：Tecience\nWeChat OA: Tecience\n搜一搜关注 · Search & Follow"


def _font(size: int) -> ImageFont.ImageFont:
    windir = Path(os.environ.get("WINDIR", "C:/Windows"))
    candidates = [
        windir / "Fonts" / "msyh.ttc",
        windir / "Fonts" / "msyhbd.ttc",
        windir / "Fonts" / "simhei.ttf",
        windir / "Fonts" / "arial.ttf",
        Path("/System/Library/Fonts/PingFang.ttc"),
        Path("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"),
    ]
    for p in candidates:
        if p.exists():
            try:
                return ImageFont.truetype(str(p), size=size)
            except OSError:
                continue
    return ImageFont.load_default()


def make_qr(data: str, box_size: int = 8, border: int = 2) -> Image.Image:
    qr = qrcode.QRCode(
        version=None,
        error_correction=qrcode.constants.ERROR_CORRECT_M,
        box_size=box_size,
        border=border,
    )
    qr.add_data(data)
    qr.make(fit=True)
    return qr.make_image(fill_color="#0B3D2E", back_color="#FFFFFF").convert("RGB")


def labeled_qr(img: Image.Image, title: str, subtitle: str) -> Image.Image:
    pad_top, pad_bot, side = 52, 44, 16
    w, h = img.size
    canvas = Image.new("RGB", (w + side * 2, h + pad_top + pad_bot), "#F7FBF8")
    canvas.paste(img, (side, pad_top))
    draw = ImageDraw.Draw(canvas)
    ft = _font(22)
    fs = _font(16)
    tw = draw.textlength(title, font=ft)
    draw.text(((canvas.width - tw) / 2, 12), title, fill="#0B3D2E", font=ft)
    sw = draw.textlength(subtitle, font=fs)
    draw.text(
        ((canvas.width - sw) / 2, canvas.height - 32),
        subtitle,
        fill="#5C6B7A",
        font=fs,
    )
    draw.rectangle([4, 4, canvas.width - 5, canvas.height - 5], outline="#C4A35A", width=2)
    return canvas


def banner(project_name: str, keyword: str) -> Image.Image:
    w, h = 960, 200
    img = Image.new("RGB", (w, h), "#0F1F1A")
    draw = ImageDraw.Draw(img)
    draw.rectangle([0, 0, 12, h], fill="#C4A35A")
    draw.rectangle([0, h - 8, w, h], fill="#2F9E6E")
    f1, f2, f3 = _font(36), _font(20), _font(18)
    draw.text((36, 36), "Tecience", fill="#E8F5EE", font=f1)
    draw.text((36, 90), "开源项目来源 · Open Source from WeChat OA", fill="#9AADA2", font=f2)
    draw.text(
        (36, 140),
        f"{project_name}  ·  微信搜一搜 Tecience  ·  回复 {keyword}",
        fill="#C4A35A",
        font=f3,
    )
    return img


def write_assets_readme(out: Path, project: dict) -> None:
    out.write_text(
        f"""# Tecience assets

本目录为公众号 **Tecience** 来源标识与扫码图。

| 文件 | 用途 |
|------|------|
| `banner.png` | README 顶栏品牌条 |
| `qr-wechat-oa.png` | 微信公众号官方关注二维码（源图） |
| `qr-wechat.png` | 官方二维码 + 标题框（README 主展示） |
| `qr-repo.png` | 本仓库 GitHub |
| `qr-github.png` | GitHub @QinHsiu |

关键词回复建议：`{project["keyword"]}`
""",
        encoding="utf-8",
    )


def resolve_root(dirname: str) -> Path | None:
    if dirname == THIS_REPO.name:
        return THIS_REPO
    cand = SIBLING_ROOT / dirname
    return cand if cand.is_dir() else None


def main() -> None:
    for meta in PROJECTS:
        root = resolve_root(meta["dirname"])
        if root is None:
            print("skip missing", meta["dirname"], "under", SIBLING_ROOT)
            continue
        out = root / "docs" / "assets" / "tecience"
        out.mkdir(parents=True, exist_ok=True)
        banner(meta["name"], meta["keyword"]).save(out / "banner.png")
        # Prefer keeping official OA image if present; only regenerate companions
        labeled_qr(make_qr(meta["repo"]), "GitHub 本仓库", meta["repo"].rsplit("/", 1)[-1]).save(
            out / "qr-repo.png"
        )
        labeled_qr(make_qr(ORG), "GitHub @QinHsiu", "更多开源项目").save(out / "qr-github.png")
        if not (out / "qr-wechat-oa.png").exists():
            labeled_qr(
                make_qr(WECHAT_HINT),
                "Tecience 公众号",
                "微信搜一搜 · Tecience",
            ).save(out / "qr-wechat.png")
        write_assets_readme(out / "README.md", meta)
        print("wrote", out.relative_to(root) if root == THIS_REPO else out.name, "->", meta["dirname"])


if __name__ == "__main__":
    main()
