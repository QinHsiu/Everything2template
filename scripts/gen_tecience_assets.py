"""Generate Tecience brand + multi QR assets for QinHsiu open-source READMEs."""

from __future__ import annotations

from pathlib import Path

import qrcode
from PIL import Image, ImageDraw, ImageFont

PROJECTS = [
    {
        "root": Path(r"D:\PycharmProjects\pythonProject\projects\Doctor_query_skill"),
        "name": "Doctor_Query",
        "repo": "https://github.com/QinHsiu/Doctor_query_skill",
        "keyword": "DOCTOR",
    },
    {
        "root": Path(r"D:\PycharmProjects\pythonProject\projects\Paper_Rec_Skill"),
        "name": "Paper_Rec",
        "repo": "https://github.com/QinHsiu/Paper_Rec_Skill",
        "keyword": "PAPER",
    },
    {
        "root": Path(r"D:\PycharmProjects\pythonProject\projects\Compass"),
        "name": "Compass",
        "repo": "https://github.com/QinHsiu/Compass",
        "keyword": "COMPASS",
    },
    {
        "root": Path(r"D:\PycharmProjects\pythonProject\projects\Everything2template"),
        "name": "Everything2template",
        "repo": "https://github.com/QinHsiu/Everything2template",
        "keyword": "E2T",
    },
]

ORG = "https://github.com/QinHsiu"
# Scannable hint: WeChat camera / other scanners show this text → user searches OA
WECHAT_HINT = "微信公众号：Tecience\nWeChat OA: Tecience\n搜一搜关注 · Search & Follow"


def _font(size: int) -> ImageFont.ImageFont:
    for name in (
        r"C:\Windows\Fonts\msyh.ttc",
        r"C:\Windows\Fonts\msyhbd.ttc",
        r"C:\Windows\Fonts\simhei.ttf",
        r"C:\Windows\Fonts\arial.ttf",
    ):
        p = Path(name)
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
    # title
    tw = draw.textlength(title, font=ft)
    draw.text(((canvas.width - tw) / 2, 12), title, fill="#0B3D2E", font=ft)
    sw = draw.textlength(subtitle, font=fs)
    draw.text(
        ((canvas.width - sw) / 2, canvas.height - 32),
        subtitle,
        fill="#5C6B7A",
        font=fs,
    )
    # thin frame
    draw.rectangle([4, 4, canvas.width - 5, canvas.height - 5], outline="#C4A35A", width=2)
    return canvas


def banner(project_name: str, keyword: str) -> Image.Image:
    w, h = 960, 200
    img = Image.new("RGB", (w, h), "#0F1F1A")
    draw = ImageDraw.Draw(img)
    # accent bar
    draw.rectangle([0, 0, 12, h], fill="#C4A35A")
    draw.rectangle([0, h - 8, w, h], fill="#2F9E6E")
    f1 = _font(36)
    f2 = _font(20)
    f3 = _font(18)
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
| `qr-wechat.png` | 扫码可见「Tecience」关注提示（请用微信搜一搜关注） |
| `qr-repo.png` | 本仓库 GitHub |
| `qr-github.png` | GitHub @QinHsiu |

若你已从微信公众平台导出**官方关注二维码**，请替换为 `qr-wechat-oa.png`，并在 README 表格中优先展示该图。

关键词回复建议：`{project["keyword"]}`
""",
        encoding="utf-8",
    )


def main() -> None:
    for p in PROJECTS:
        out = p["root"] / "docs" / "assets" / "tecience"
        out.mkdir(parents=True, exist_ok=True)

        banner(p["name"], p["keyword"]).save(out / "banner.png")
        labeled_qr(
            make_qr(WECHAT_HINT),
            "Tecience 公众号",
            "微信搜一搜 · Tecience",
        ).save(out / "qr-wechat.png")
        labeled_qr(make_qr(p["repo"]), "GitHub 本仓库", p["repo"].rsplit("/", 1)[-1]).save(
            out / "qr-repo.png"
        )
        labeled_qr(make_qr(ORG), "GitHub @QinHsiu", "更多开源项目").save(out / "qr-github.png")
        write_assets_readme(out / "README.md", p)
        print("wrote", out)


if __name__ == "__main__":
    main()
