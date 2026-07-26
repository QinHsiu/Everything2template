"""Image planning + optional DuckDuckGo image fetch."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any
from urllib.request import Request, urlopen


@dataclass
class ImageSlot:
    role: str  # cover | step | compare | screenshot
    caption: str
    search_query: str
    path: str | None = None


@dataclass
class ImagePlan:
    slots: list[ImageSlot] = field(default_factory=list)

    def to_markdown(self) -> str:
        lines = ["# Image plan", ""]
        for i, s in enumerate(self.slots, 1):
            lines.append(f"## {i}. {s.role}")
            lines.append(f"- Caption: {s.caption}")
            lines.append(f"- Search: {s.search_query}")
            if s.path:
                lines.append(f"- File: {s.path}")
            lines.append("")
        return "\n".join(lines)

    def to_dict(self) -> dict[str, Any]:
        return {"slots": [s.__dict__ for s in self.slots]}


def build_image_plan(title: str, key_points: list[str], *, platform: str = "xiaohongshu") -> ImagePlan:
    slots = [
        ImageSlot(
            role="cover",
            caption=title[:24] or "封面大字",
            search_query=f"{title} 封面 简约",
        )
    ]
    for i, p in enumerate(key_points[:5], 1):
        slots.append(
            ImageSlot(
                role="step" if platform in {"xiaohongshu", "douyin"} else "section",
                caption=p[:40],
                search_query=p[:30],
            )
        )
    if platform == "wechat":
        slots.append(
            ImageSlot(role="cta", caption="文末互动引导配图", search_query="在看 分享 简约图标")
        )
    return ImagePlan(slots=slots)


def try_fetch_images(plan: ImagePlan, out_dir: str | Path, *, max_download: int = 3) -> ImagePlan:
    """Best-effort download via ddgs images. Never raises for missing deps."""
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    try:
        from ddgs import DDGS  # type: ignore
    except ImportError:
        return plan

    downloaded = 0
    try:
        with DDGS() as ddgs:
            for slot in plan.slots:
                if downloaded >= max_download:
                    break
                try:
                    results = list(ddgs.images(slot.search_query, max_results=1))
                except Exception:  # noqa: BLE001
                    continue
                if not results:
                    continue
                url = results[0].get("image") or results[0].get("url")
                if not url:
                    continue
                dest = out / f"{downloaded+1:02d}_{slot.role}.jpg"
                try:
                    req = Request(url, headers={"User-Agent": "Everything2template/0.3"})
                    with urlopen(req, timeout=15) as resp:  # noqa: S310
                        dest.write_bytes(resp.read())
                    slot.path = str(dest)
                    downloaded += 1
                except Exception:  # noqa: BLE001
                    continue
    except Exception:  # noqa: BLE001
        return plan
    return plan
