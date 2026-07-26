"""Deterministic Chinese AI-flavor reduction (inspired by oh-my-writing humanizer-cn)."""

from __future__ import annotations

import re
from dataclasses import dataclass, field

# phrase -> safer replacement (keep meaning, cut pomp)
REPLACEMENTS: list[tuple[str, str]] = [
    ("综上所述", "总的来说"),
    ("总而言之", "总之"),
    ("值得注意的是", "有一点"),
    ("值得一提的是", "还有"),
    ("不言而喻", "很明显"),
    ("毋庸置疑", "可以确定"),
    ("显而易见", "很清楚"),
    ("与此同时", "同时"),
    ("鉴于此", "所以"),
    ("基于此", "所以"),
    ("有鉴于此", "所以"),
    ("从某种意义上说", "某种程度上"),
    ("就此而言", "就这点来说"),
    ("一言以蔽之", "简单说"),
    ("具有里程碑意义", "挺关键"),
    ("具有划时代意义", "影响不小"),
    ("开创了先河", "算是新做法"),
    ("树立了标杆", "成了参照"),
    ("奠定了基础", "先把底子打好了"),
    ("广受关注", "很多人在看"),
    ("引发热议", "讨论不少"),
    ("备受瞩目", "关注度高"),
    ("在业界引起强烈反响", "圈内讨论很多"),
    ("匠心独运", "设计用心"),
    ("精心打造", "认真做了"),
    ("倾力呈现", "重点做了"),
    ("重新定义", "换了一种做法"),
    ("开启新篇章", "进入下一阶段"),
    ("独树一帜", "风格比较特别"),
    ("赋能", "帮助"),
    ("助力", "帮到"),
    ("打造闭环", "把流程串起来"),
    ("未来可期", "后面还有空间"),
    ("砥砺前行", "继续推进"),
    ("前景广阔", "空间还在"),
    ("任重道远", "后面还有硬仗"),
    ("希望对您有所帮助", "如果有用就好"),
    ("如有需要请随时告知", "有问题直接说"),
    ("业内人士指出", "有人提到"),
    ("专家表示", "有人说"),
    ("有观点认为", "也有人觉得"),
    ("据了解", "目前看到的是"),
    ("据悉", "目前信息是"),
    ("多方消息显示", "几处信息都提到"),
    ("不仅是一次技术升级，更是一次理念革新", "这次主要是技术升级，也改了产品思路"),
    ("in conclusion", "overall"),
    ("it is important to note that", "note that"),
    ("delve into", "look at"),
    ("leverage", "use"),
    ("cutting-edge", "new"),
    ("seamlessly", "smoothly"),
]

DELETE_SOFT = [
    "在当今时代",
    "在这个日新月异的时代",
    "随着科技的不断发展",
    "让我们拭目以待",
]


@dataclass
class HumanizeResult:
    text: str
    replacements: list[str] = field(default_factory=list)
    removed: list[str] = field(default_factory=list)

    @property
    def changed(self) -> bool:
        return bool(self.replacements or self.removed)


def humanize(text: str) -> HumanizeResult:
    out = text
    reps: list[str] = []
    removed: list[str] = []
    for src, dst in REPLACEMENTS:
        if src in out:
            count = out.count(src)
            out = out.replace(src, dst)
            reps.append(f"{src}→{dst}×{count}")
    for phrase in DELETE_SOFT:
        if phrase in out:
            out = out.replace(phrase, "")
            removed.append(phrase)
    # collapse leftover double spaces / empty emphasis
    out = re.sub(r"[ \t]{2,}", " ", out)
    out = re.sub(r"\n{3,}", "\n\n", out)
    return HumanizeResult(text=out.strip() + ("\n" if text.endswith("\n") else ""), replacements=reps, removed=removed)
