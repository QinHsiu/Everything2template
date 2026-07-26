"""Publish-quality rewrite from CIR — hooks, structure, facts-only, no filler spam."""

from __future__ import annotations

import re
from typing import Iterable

from e2t.cir import CIR, Section
from e2t.humanize import humanize
from e2t.titles import title_variants


def _clean(text: str) -> str:
    text = re.sub(r"^#+\s*", "", text.strip())
    text = re.sub(r"[ \t]+", " ", text)
    return text.strip()


def _theme_title(title: str, n: int = 28) -> str:
    """Prefer the semantic left side; drop trailing「：我用 …」product clauses."""
    s = _clean(title)
    for sep in ("：", ":"):
        if sep in s:
            left, right = s.split(sep, 1)
            left, right = left.strip(), right.strip()
            if len(left) >= 8 and (
                right.startswith(("我用", "用", "基于", "借助")) or "Everything2template" in right
            ):
                return _clip(left, n, ellipsis=False)
            if len(left) >= 8 and len(left) <= n:
                return left
    return _clip(s, n, ellipsis=False)


def _clip(text: str, n: int, *, ellipsis: bool = True) -> str:
    s = _clean(text)
    if len(s) <= n:
        # strip dangling function words
        s = re.sub(r"(：我用|：用|我用)$", "", s).rstrip("：:，、 ")
        return s
    cut = s[:n]
    for sep in ("。", "！", "？", "；", "，", "、", " ", "|", "｜", "：", ":"):
        i = cut.rfind(sep)
        if i >= max(6, n / 3):
            out = cut[:i].rstrip("，。；、 ：:|｜-")
            out = re.sub(r"(：我用|我用)$", "", out)
            return out
    out = cut.rstrip("，。；、 ：:|｜-")
    out = re.sub(r"(：我用|我用)$", "", out)
    return out + ("…" if ellipsis else "")


def _sentences(text: str, limit: int = 12) -> list[str]:
    raw = re.split(r"(?<=[。！？!?\n])\s*", text)
    out: list[str] = []
    for s in raw:
        s = _clean(s)
        if len(s) < 8 or s.startswith("```"):
            continue
        out.append(s)
        if len(out) >= limit:
            break
    return out


def _dedupe(items: Iterable[str], *, min_len: int = 4) -> list[str]:
    seen: set[str] = set()
    out: list[str] = []
    for raw in items:
        p = _clean(raw)
        if len(p) < min_len:
            continue
        key = re.sub(r"\s+", "", p)
        if key in seen:
            continue
        seen.add(key)
        out.append(p)
    return out


def _material(cir: CIR) -> dict:
    title = _clean(cir.title) or "这个话题"
    summary = _clean(cir.summary) or ""
    points = [_clean(p) for p in cir.key_points if _clean(p)]
    sections: list[Section] = list(cir.sections or [])
    bodies: list[str] = []
    for s in sections:
        if s.body:
            bodies.append(_clean(s.body)[:600])
        for b in s.bullets:
            if _clean(b):
                points.append(_clean(b))
    points = _dedupe(points)[:10]
    excerpt_sents = _sentences(cir.raw_excerpt or summary, 16)
    if not summary and excerpt_sents:
        summary = excerpt_sents[0]
    if not points:
        points = excerpt_sents[:6] or [f"围绕「{_clip(title, 24)}」整理可执行判断"]
    return {
        "title": title,
        "summary": summary,
        "points": points,
        "sections": sections,
        "bodies": bodies,
        "excerpt_sents": excerpt_sents,
        "tags": cir.tags or [],
        "audience": cir.audience or "创作者与知识工作者",
    }


def _nearest_evidence(point: str, bodies: list[str], excerpt: list[str], idx: int) -> str:
    tokens = [t for t in re.findall(r"[\u4e00-\u9fff]{2,}|[A-Za-z]{3,}", point) if len(t) >= 2]
    for b in bodies:
        if any(t in b for t in tokens[:4]):
            return _clip(b, 140, ellipsis=False)
    if excerpt:
        return _clip(excerpt[min(idx, len(excerpt) - 1)], 140, ellipsis=False)
    return ""


def _expand_point(point: str, bodies: list[str], excerpt: list[str], idx: int) -> str:
    """Expand a bullet into 1–2 readable sentences — no stock CTA spam."""
    lead = point.rstrip("。.;；")
    evidence = _nearest_evidence(point, bodies, excerpt, idx)
    if evidence and evidence not in lead and lead not in evidence:
        return f"{lead}。补充细节：{evidence.rstrip('。')}。"
    return f"{lead}。"


def _hook_wechat(m: dict) -> str:
    pain = _clip(m["points"][0] if m["points"] else m["summary"], 42)
    core = _theme_title(m["title"], 28)
    return (
        f"先说一句得罪人的话：大多数人不是不会写，而是同一份材料要在不同平台「再说一遍」，"
        f"最后写成了同文换皮。\n\n"
        f"这篇围绕「{core}」。真正费时间的往往是适配，不是灵感。"
        + (f"最典型的卡点是：{pain}。" if pain else "")
    )


def _hook_xhs(m: dict) -> str:
    return (
        f"先说结论：{_clip(m['summary'] or m['title'], 70)}\n\n"
        f"别再把公众号长文直接粘到小红书了——会被划走。"
    )


def _hook_zhihu(m: dict) -> str:
    return (
        f"**先说结论：** {_clip(m['summary'] or ('关于「' + m['title'] + '」，关键是结构重建而不是换皮。'), 120)}\n\n"
        f"下面按「现象 → 原因 → 可验证做法 → 边界」展开；不编造数据，只整理源材料里站得住的点。"
    )


def _format_section_body(heading: str, body: str, bullets: list[str], m: dict, idx: int) -> str:
    bullets = _dedupe(bullets)
    body = (body or "").strip()

    if body:
        paras = [p.strip() for p in re.split(r"\n\s*\n", body) if p.strip()]
        if len(paras) == 1 and re.search(r"(?m)^([-*•]|\d+[\.、])\s+", body):
            lines = [ln.strip() for ln in body.splitlines() if ln.strip()]
            items: list[str] = []
            for ln in lines:
                item = re.sub(r"^([-*•]|\d+[\.、])\s*", "", ln).strip()
                if item:
                    items.append(item)
            items = _dedupe(items)
            if items:
                out = [f"关于「{heading}」，源材料里最硬的几条是："]
                for it in items[:6]:
                    out.append(f"\n\n- **{it}**")
                closer = (
                    "先改结构，再纠结措辞。"
                    if idx % 2
                    else "写下一篇时，先挑一条今天就能改的落地。"
                )
                out.append(f"\n\n{closer}")
                return "".join(out)
        chunks = [_clean(re.sub(r"\s+", " ", p)) for p in paras[:5]]
        text = "\n\n".join(c for c in chunks if c)
        # Prefer any real body over falling back to unrelated key_points
        if len(text) >= 12:
            if bullets:
                extra = "\n".join(f"- {b}" for b in bullets[:4] if b not in text)
                if extra:
                    text = f"{text}\n\n还可以记住：\n{extra}"
            return text

    if bullets:
        parts = [f"「{heading}」可以拆成下面几条（均来自源材料）："]
        for i, b in enumerate(bullets[:6]):
            ev = _nearest_evidence(b, m["bodies"], m["excerpt_sents"], idx + i)
            if ev and ev != b and b not in ev:
                parts.append(f"\n\n**{b}**\n\n{ev}")
            else:
                parts.append(f"\n\n**{b}**")
        return "".join(parts)

    point = m["points"][idx] if idx < len(m["points"]) else heading
    return _expand_point(point, m["bodies"], m["excerpt_sents"], idx)


def _action_steps(m: dict) -> list[str]:
    catalog = [
        ("材料", "先选定一种输入（网页 / PDF / 代码），跑通一次完整转换"),
        ("平台", "只选一个目标平台，按该平台结构重写，不要同时换皮三份"),
        ("CIR", "先看 CIR / 要点是否保真，再谈钩子与标题"),
        ("门禁", "导出前过一遍 validate：套话、长度、CTA"),
        ("导出", "需要交付时导出 Markdown 或公众号 HTML，而不是只留在对话框"),
    ]
    steps: list[str] = []
    blob = " ".join(m["points"] + [m["summary"], m["title"]])
    for key, step in catalog:
        if key in blob or not steps:
            steps.append(step)
        if len(steps) >= 4:
            break
    while len(steps) < 3:
        for _, step in catalog:
            if step not in steps:
                steps.append(step)
            if len(steps) >= 3:
                break
    return _dedupe(steps)[:4]


def rewrite_wechat(cir: CIR) -> str:
    m = _material(cir)
    titles = title_variants(m["title"], "wechat", summary=m["summary"])
    abstract = _clip(m["summary"] or m["title"], 54, ellipsis=False)
    sections_out: list[str] = []
    heads: list[tuple[str, str, list[str]]] = []
    for i, s in enumerate(m["sections"][:6]):
        heads.append((s.heading or f"要点 {i+1}", s.body or "", list(s.bullets or [])))
    if not heads:
        for i, p in enumerate(m["points"][:5]):
            heads.append((_clip(p, 24, ellipsis=False) or f"要点 {i+1}", p, []))

    used_bodies: set[str] = set()
    for i, (h, body, bullets) in enumerate(heads):
        h = _clean(h) or f"要点 {i+1}"
        block = _format_section_body(h, body, bullets, m, i)
        key = re.sub(r"\s+", "", block)[:80]
        if key in used_bodies and i > 0:
            continue
        used_bodies.add(key)
        sections_out.append(
            f"## {h}\n\n{block}\n\n<!-- 配图：与「{_clip(h, 12, ellipsis=False)}」相关的示意图或截图 -->\n"
        )

    actions = "\n".join(f"- {s}" for s in _action_steps(m))
    core = _theme_title(m["title"], 28)
    return humanize(
        "\n".join(
            [
                f"# {titles[0]}",
                "",
                f"> 摘要：{abstract}",
                "",
                _hook_wechat(m),
                "",
                *sections_out,
                "## 你可以怎么用",
                "",
                "别追求一次写完美。按这个顺序更稳：",
                "",
                actions,
                "",
                "## 小结",
                "",
                f"关于「{core}」，记住三句话：信息要正确、结构要平台原生、结尾要有一个明确动作。"
                f"流量不是喊出来的，是读者愿意停下来、转发出去换来的。",
                "",
                "---",
                "",
                "如果这篇帮你省掉一轮「换皮重写」，点个「在看」。你也可以把原文主题丢过来，按同一套结构再拆一版。",
                "",
                "### 备选标题",
                *[f"{i}. {t}" for i, t in enumerate(titles[:5], 1)],
                "",
                "### 元数据",
                f"- 封面建议：大字「{_clip(m['title'], 12, ellipsis=False)}」+ 冲突感对比图",
                f"- 标签：{', '.join(m['tags'][:5]) or '内容创作, 效率, 方法论'}",
                f"- 受众：{m['audience']}",
            ]
        )
    ).text


def rewrite_xiaohongshu(cir: CIR) -> str:
    m = _material(cir)
    titles = title_variants(m["title"], "xiaohongshu", summary=m["summary"])
    steps: list[str] = []
    for i, p in enumerate(m["points"][:5], 1):
        detail = ""
        if i - 1 < len(m["excerpt_sents"]):
            cand = m["excerpt_sents"][i - 1]
            if cand != p and p not in cand:
                detail = _clip(cand, 40, ellipsis=False)
        line = f"{i}️⃣ {_clip(p, 36, ellipsis=False)}"
        if detail:
            line += f"\n   · {detail}"
        steps.append(line)
        steps.append("")
    tags = m["tags"][:3] or ["干货分享", "效率工具", "创作者"]
    tag_line = " ".join(f"#{t.replace('#', '')}" for t in tags + ["一稿多发", "写作技巧"])
    return humanize(
        "\n".join(
            [
                _clip(titles[0], 20, ellipsis=False),
                "",
                _hook_xhs(m),
                "",
                "我踩过的坑：同一篇长文三平台乱贴，阅读和互动都会很难看。",
                "",
                *steps,
                "避坑：不要编经历、不要绝对化承诺；不确定就写「待核实」。",
                "",
                "你们最想看我拆哪种原文？（PDF / 项目 README / 网页）评论区扣👇",
                "",
                tag_line,
                "",
                "### 备选标题",
                *[f"- {t}" for t in titles[:5]],
                "",
                "### 配图建议",
                "1. 封面：大字标题 + 强对比色",
                "2-6. 每一步一张卡片（关键词超大字）",
            ]
        )
    ).text


def rewrite_zhihu(cir: CIR) -> str:
    m = _material(cir)
    titles = title_variants(m["title"], "zhihu", summary=m["summary"])
    body_parts: list[str] = []
    for i, p in enumerate(m["points"][:6], 1):
        expanded = _expand_point(p, m["bodies"], m["excerpt_sents"], i)
        body_parts.append(f"## {i}. {_clip(p, 40, ellipsis=False)}\n\n{expanded}\n")
        if i == min(3, len(m["points"])):
            body_parts.append(
                "## 边界条件\n\n"
                "以上判断只在「源材料可支撑」的范围内成立。缺数据的地方不会硬编；"
                "如果你有反例，欢迎直接贴出来，结论可以更新。\n"
            )
    return humanize(
        "\n".join(
            [
                f"# {titles[0]}",
                "",
                _hook_zhihu(m),
                "",
                *body_parts,
                "## 总结",
                "",
                f"回到「{_theme_title(m['title'], 28)}」：先保证信息正确，再谈钩子与传播。"
                f"平台流量喜欢「结论清楚 + 细节可验证 + 态度真诚」，而不是空喊方法论。",
                "",
                "欢迎补充反例与你的实操路径。",
                "",
                "### 备选标题",
                *[f"{i}. {t}" for i, t in enumerate(titles[:5], 1)],
                "",
                "### 元数据",
                f"- 话题：{', '.join(m['tags'][:5]) or '内容创作, 方法论, 效率'}",
                "- 形式：文章",
            ]
        )
    ).text


def rewrite_weibo(cir: CIR) -> str:
    m = _material(cir)
    titles = title_variants(m["title"], "weibo", summary=m["summary"])
    p1 = m["points"][0] if m["points"] else m["summary"]
    p2 = m["points"][1] if len(m["points"]) > 1 else ""
    tags = " ".join(f"#{t}" for t in (m["tags"][:3] or ["内容创作", "效率", "写作"]))
    return humanize(
        "\n".join(
            [
                f"【{_clip(titles[0], 28, ellipsis=False)}】",
                "",
                f"立场：{_clip(m['summary'] or p1, 90, ellipsis=False)}",
                "",
                f"为何值得吵一句：{_clip(p1, 80, ellipsis=False)}",
                (f"\n补充：{_clip(p2, 70, ellipsis=False)}" if p2 else ""),
                "",
                "别做同文换皮。平台不同，结构就该不同。",
                "",
                tags,
                "",
                "### 备选标题",
                *[f"- {t}" for t in titles[:4]],
            ]
        )
    ).text


def rewrite_douyin(cir: CIR) -> str:
    m = _material(cir)
    titles = title_variants(m["title"], "douyin", summary=m["summary"])
    lines = [
        f"【封面文案】{_clip(titles[0], 12, ellipsis=False)}",
        "",
        f"【0–3s 钩子】停一下：{_clip(m['summary'] or m['title'], 36, ellipsis=False)}",
        "",
    ]
    spoken = m["excerpt_sents"][:4] or m["points"][:4]
    for i, s in enumerate(spoken[:4], 1):
        oral = _clip(s.replace("##", "").replace("#", ""), 42, ellipsis=False)
        lines.append(f"【镜头{i}】画面：大字「{_clip(oral, 10, ellipsis=False)}」 / 口播：{oral}")
        lines.append("")
    lines.extend(
        [
            "【结尾 CTA】有用就关注；评论你最想改写的原文类型",
            "",
            "【BGM 建议】轻快无歌词",
            f"【字幕】高亮：{'、'.join(_clip(x, 8, ellipsis=False) for x in m['points'][:3])}",
            "",
            "### 备选封面",
            *[f"- {t}" for t in titles[:4]],
        ]
    )
    return humanize("\n".join(lines)).text


def rewrite_article(cir: CIR, platform: str, *, use_llm: bool = True) -> str:
    """Main entry: rich rewrite; optional LLM polish when configured."""
    platform = platform.lower().strip()
    writers = {
        "wechat": rewrite_wechat,
        "xiaohongshu": rewrite_xiaohongshu,
        "zhihu": rewrite_zhihu,
        "weibo": rewrite_weibo,
        "douyin": rewrite_douyin,
    }
    if platform not in writers:
        raise ValueError(f"Unsupported platform: {platform}")
    draft = writers[platform](cir)
    if use_llm:
        try:
            from e2t.rewrite_llm import maybe_llm_polish

            polished = maybe_llm_polish(cir, platform, draft)
            if polished:
                return humanize(polished).text
        except Exception:  # noqa: BLE001
            pass
    return draft


# Back-compat alias used by older callers
skeleton_article = rewrite_article
