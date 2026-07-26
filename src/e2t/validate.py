"""Platform quality gates for draft articles."""

from __future__ import annotations

import re
from collections import Counter
from dataclasses import dataclass, field

AI_FLAVOR = [
    "综上所述",
    "值得注意的是",
    "在当今时代",
    "赋能",
    "助力",
    "打造闭环",
    "全方位",
    "深度剖析",
    "本文将从以下几个方面",
    "as an ai",
    "delve into",
    "in conclusion",
    "it is important to note",
]

# Engine self-spam — marks template-quality failure vs OSS peers
FILLER_SPAM = [
    "先抓重点——",
    "不是口号，是一组能执行的约束",
    "落到动作上，就是别只收藏",
    "原文里其实已经点到了",
    "写的时候按这条约束执行，比写完再硬改语气更省时间",
]


@dataclass
class CheckResult:
    platform: str
    ok: bool
    score: float
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "platform": self.platform,
            "ok": self.ok,
            "score": self.score,
            "errors": self.errors,
            "warnings": self.warnings,
        }


def _count_chars(text: str) -> int:
    return len(re.sub(r"\s+", "", text))


def _h1(text: str) -> str:
    m = re.search(r"^#\s+(.+)$", text, re.M)
    return (m.group(1).strip() if m else "").strip()


def validate_article(platform: str, text: str) -> CheckResult:
    platform = platform.lower().strip()
    errors: list[str] = []
    warnings: list[str] = []
    score = 100.0
    n = _count_chars(text)

    if n < 80:
        errors.append("正文过短，无法作为可发布草稿")
        score -= 40

    lower = text.lower()
    hits = [p for p in AI_FLAVOR if p.lower() in lower or p in text]
    if hits:
        warnings.append(f"疑似 AI 套话：{', '.join(hits[:5])}")
        score -= 5 * min(len(hits), 4)

    spam_hits = [p for p in FILLER_SPAM if p in text]
    if spam_hits:
        errors.append(f"模板套话复读：{', '.join(spam_hits[:3])}")
        score -= 25

    h1 = _h1(text)
    if h1:
        if h1.endswith(("：", ":", "｜", "|", "、", "，", "的", "了", "与", "和", "我用")):
            errors.append(f"标题疑似截断或不完整：{h1[:40]}")
            score -= 20
        if len(h1) >= 12 and ("：我用" in h1 or h1.endswith("我用")):
            errors.append(f"标题疑似截断：{h1[:40]}")
            score -= 15
        if "围绕「" in text and "：我用」" in text:
            errors.append("正文主题截断（：我用）")
            score -= 15

    paras = [
        re.sub(r"\s+", "", p)[:40]
        for p in re.split(r"\n\s*\n", text)
        if len(p.strip()) > 40
    ]
    dup = [k for k, v in Counter(paras).items() if v >= 2 and k]
    if len(dup) >= 2:
        warnings.append(f"存在重复段落指纹 ×{len(dup)}")
        score -= 8 * min(len(dup), 3)

    if platform == "wechat":
        if n < 600:
            warnings.append("公众号建议 ≥800 汉字（骨架稿可再扩写）")
            score -= 10
        if n > 6000:
            warnings.append("公众号过长，建议拆分或精简到 1500–3500 字")
            score -= 5
        if not re.search(r"^#\s+\S+", text, re.M):
            errors.append("缺少一级标题 (# 标题)")
            score -= 15
        if "在看" not in text and "关注" not in text:
            warnings.append("缺少文末互动/关注引导")
            score -= 5
        paras_raw = [p for p in re.split(r"\n\s*\n", text) if p.strip()]
        long_paras = [p for p in paras_raw if len(p) > 220]
        if len(long_paras) >= 3:
            warnings.append("存在过多超长段落，不利手机阅读")
            score -= 5

    elif platform == "xiaohongshu":
        if n > 1200:
            warnings.append("小红书正文偏长，建议压到 300–800 字并拆图")
            score -= 8
        if n < 120:
            warnings.append("小红书正文偏短")
            score -= 8
        first_line = next((ln.strip() for ln in text.splitlines() if ln.strip()), "")
        if len(first_line) > 24:
            warnings.append("首行标题建议 ≤20 字（信息流截断）")
            score -= 5
        if "#" not in text:
            warnings.append("缺少话题标签 #")
            score -= 5
        if not re.search(r"[✨🔥✅💡📌💕💬🙌👇]", text):
            warnings.append("可适量增加表情以提升信息流点击（勿堆砌）")
            score -= 3

    elif platform == "zhihu":
        if n < 500:
            warnings.append("知乎文章建议 ≥800 字并给出明确结论")
            score -= 10
        if "结论" not in text and "先说" not in text:
            warnings.append("建议开篇给出结论")
            score -= 5
        if not re.search(r"^##\s+\S+", text, re.M):
            warnings.append("建议使用二级标题分节")
            score -= 5

    elif platform == "weibo":
        if n > 500:
            warnings.append("微博主贴建议压到 180–300 字，长文可转长图")
            score -= 8
        if n < 40:
            errors.append("微博正文过短")
            score -= 20
        if "#" not in text:
            warnings.append("建议加 1–3 个话题标签")
            score -= 5

    elif platform == "douyin":
        if "钩子" not in text and "0–3" not in text and "0-3" not in text:
            warnings.append("建议标注 0–3 秒钩子")
            score -= 8
        if "口播" not in text and "镜头" not in text:
            warnings.append("建议按镜头/口播结构书写")
            score -= 8
        if n < 60:
            warnings.append("口播稿偏短")
            score -= 5
    else:
        errors.append(f"未知平台: {platform}")
        score -= 50

    score = max(0.0, min(100.0, score))
    ok = len(errors) == 0 and score >= 60
    return CheckResult(platform=platform, ok=ok, score=score, errors=errors, warnings=warnings)
