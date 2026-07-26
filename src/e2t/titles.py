"""Title variant generator — punchy but claim-safe; never mid-word truncate."""

from __future__ import annotations

import re


def _clip(text: str, n: int) -> str:
    s = (text or "").strip().lstrip("#").strip()
    s = re.sub(r"\s+", " ", s)
    if len(s) <= n:
        return s
    cut = s[:n]
    for sep in ("。", "！", "？", "；", "，", "、", " ", "|", "｜", "：", ":", "—", "-"):
        i = cut.rfind(sep)
        if i >= max(4, n / 3):
            return cut[:i].rstrip("，。；、 ：:|｜—-")
    return cut.rstrip("，。；、 ：:|｜—-") + "…"


def _theme(title: str, n: int = 18) -> str:
    s = (title or "未命名主题").strip().lstrip("#").strip()
    for sep in ("：", ":"):
        if sep in s:
            left, right = s.split(sep, 1)
            left, right = left.strip(), right.strip()
            if len(left) >= 8 and (
                right.startswith(("我用", "用", "基于", "借助"))
                or "Everything2template" in right
                or "e2t" in right.lower()
            ):
                return _clip(left, n)
            if 8 <= len(left) <= n:
                return left
    if 8 <= len(s) <= n:
        return s
    return _clip(s, n)


def title_variants(title: str, platform: str, *, summary: str = "") -> list[str]:
    base = (title or "未命名主题").strip().lstrip("#").strip()
    short = _theme(base, 18)
    tip = _clip(summary or short, 16)
    tip2 = _clip(summary or short, 12)
    platform = platform.lower()

    if platform == "wechat":
        # Lead with intact short theme; avoid "别再…：{残缺长标题}"
        return [
            f"别再同文换皮了：{_clip(short, 14)}" if len(short) > 8 else f"别再同文换皮了｜{_clip(base, 16)}",
            f"我劝你先改结构，再改语气｜{_clip(short, 12)}",
            f"{_clip(short, 16)}：多数人栽在这一步",
            f"从材料到流量：怎么把{_clip(short, 10)}写对",
            f"一篇讲透{_clip(short, 14)}（可直接套用）",
        ]
    if platform == "xiaohongshu":
        return [
            f"{_clip(short, 10)}｜别再换皮了✨",
            f"救命！{_clip(tip2, 10)}这样做才有阅读",
            f"收藏！{_clip(short, 8)}避坑清单",
            f"{_clip(short, 10)} 亲测结构法",
            f"创作者必看｜{_clip(tip2, 10)}",
        ]
    if platform == "zhihu":
        return [
            f"如何把「{_clip(short, 16)}」写成有流量还不假的内容？",
            f"关于{_clip(short, 14)}，为什么同文换皮一定扑街？",
            f"{_clip(short, 16)}：结论先行之后还缺什么？",
            f"有哪些可验证的做法，能让{_clip(tip2, 12)}更站得住？",
            f"做内容的人如何避免「正确但没人看」？以{_clip(short, 12)}为例",
        ]
    if platform == "weibo":
        return [
            f"【狠话】{_clip(short, 16)}",
            f"一句说清：{_clip(tip, 18)}",
            f"{_clip(short, 16)}，别再误解了",
            "换皮党看起来很勤奋，其实在浪费流量",
            f"{_clip(short, 14)}｜我的立场",
        ]
    if platform == "douyin":
        return [
            f"{_clip(short, 8)}别换皮",
            f"3秒：{_clip(tip2, 10)}",
            f"停！{_clip(short, 6)}这样写",
            f"{_clip(short, 8)}真相",
            f"今天拆{_clip(short, 6)}",
        ]
    return [base, f"{base}（详解）", f"关于{base}"]
