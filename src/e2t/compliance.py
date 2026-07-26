"""Lightweight compliance lexicon for CN social drafts."""

from __future__ import annotations

from dataclasses import dataclass, field

# Absolute / medical / financial hype — flag, do not auto-delete facts
BANNED_OR_RISKY = [
    "国家级",
    "世界级",
    "最高级",
    "第一",
    "唯一",
    "首个",
    "100%",
    "彻底根治",
    "包治百病",
    "稳赚不赔",
    "保本保收益",
    "内幕消息",
    "限时免费领取",
    "点击领取红包",
]


@dataclass
class ComplianceResult:
    ok: bool
    hits: list[str] = field(default_factory=list)
    notes: list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {"ok": self.ok, "hits": self.hits, "notes": self.notes}


def check_compliance(text: str, *, platform: str | None = None) -> ComplianceResult:
    hits = [w for w in BANNED_OR_RISKY if w in text]
    notes: list[str] = []
    if platform == "xiaohongshu" and "最牛" in text:
        hits.append("最牛")
    if hits:
        notes.append("疑似绝对化/营销敏感词，发布前请人工确认或改写。")
    return ComplianceResult(ok=len(hits) == 0, hits=hits, notes=notes)
