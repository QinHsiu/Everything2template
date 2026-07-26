# Writer brief — wechat / mode=rewrite

## Instructions
1. Read the platform template rules carefully.
2. Use ONLY facts present in the CIR brief (do not invent metrics, quotes, or affiliations).
3. If a claim lacks evidence, mark it as 待核实 or omit it.
4. Output the final article in the template's required structure.
5. Voice profile / guidance:
Voice profile: Tech Builder (tech_builder)
Persona: 务实的构建者：先演示，再讲原理，诚实说局限
Do:
- 给可复现步骤
- 用具体数字（仅来自源）
- 对比取舍
Don't:
- 假装测评过未出现的产品
- 绝对化承诺
- 空泛励志
CTA overrides:
- wechat: 如果这篇对你有用，点个在看，我继续拆可落地的方法。
- xiaohongshu: 你们还想看我拆哪个工具？评论区扣1
- zhihu: 欢迎贴反例；有更好的做法我会更新到文首。
Banned phrases: 赋能, 闭环, 颠覆式

## Platform template
# 微信公众号模板 / WeChat

## 目标

写出适合手机阅读、可直接进编辑器的公众号长文草稿（推荐 1200–2800 字）。

## 结构（必须）

```text
# 主标题（≤30 字，前 15 字抓人）
> 摘要（分享卡片，≤54 字）

开篇钩子 1–2 段（场景 / 冲突 / 反常识）

## 小标题 1
段落（每段 3–5 行）

## 小标题 2
…

## 小结
行动建议 1–3 条

---
互动引导（在看 / 关注）
```

## 标题公式（选一）

1. 数字 + 痛点 + 方法：`3 个方法，解决…`
2. 对比：`A 和 B 的差距，只在这一点`
3. 疑问：`为什么 …？答案有点反直觉`
4. 身份 + 悬念：`做了 N 年 …，我劝你…`

另给 3 个备选标题。

## 文风

- 口语书面化：像朋友讲清楚一件事，不是汇报材料
- 短段落；关键句可加粗（Markdown `**`）
- 少用空泛词：赋能、闭环、抓手、底层逻辑（除非源文本身在讲这些）
- 每约 300–500 字暗示一处配图位：`<!-- 配图：... -->`

## 排版提示（给运营）

- 正文字号约 15px，行距 1.75–2
- 封面图建议 900×383
- 文末 CTA：在看 > 转发 > 关注（按目标选一个主 CTA）

## format vs rewrite

- `format`：保留原论证顺序，只切段、加小标题、补摘要与 CTA
- `rewrite`：可重排结构，强化钩子与小节行动，但不得新增事实

## CIR brief
# demo_article
Source: markdown | examples\sample_inputs\demo_article.md

## Summary
# 把任何材料变成可发布内容：我用 Everything2template 做了一稿三发

## Key points
- 创作者最耗时间的不是「写」，而是「同一件事用三种平台语言再说一遍」。
- 公众号要有钩子和小节；小红书要关键词前置和步骤感；知乎要结论先行和边界条件。手动改三遍，质量还容易塌成「换皮粘贴」。
- ## 问题
- - 源材料形态太多：网页、PDF、文档、代码、整个项目
- ## 方法
- 1. 先把材料摄入成 CIR（Canonical Intermediate Representation）
- ## 结果

## Sections
### 把任何材料变成可发布内容：我用 Everything2template 做了一稿三发
创作者最耗时间的不是「写」，而是「同一件事用三种平台语言再说一遍」。

公众号要有钩子和小节；小红书要关键词前置和步骤感；知乎要结论先行和边界条件。手动改三遍，质量还容易塌成「换皮粘贴」。
### 问题
- 源材料形态太多：网页、PDF、文档、代码、整个项目
- 平台语风差异大，模板套用不等于平台原生
- 导出经常卡在「只能复制文本」，不便存档或对外交付
- 源材料形态太多：网页、PDF、文档、代码、整个项目
- 平台语风差异大，模板套用不等于平台原生
- 导出经常卡在「只能复制文本」，不便存档或对外交付
### 方法
1. 先把材料摄入成 CIR（Canonical Intermediate Representation）
2. 再按平台模板重写结构（不是同文换皮）
3. 用质量门禁检查套话、长度、CTA
4. 导出 Markdown / PDF
### 结果
你得到的是三份可继续精修的平台草稿 + 可交付文件，而不是一个「通用长文」。
### 边界
自动发布到平台后台、账号矩阵运营不属于本工具的默认范围；它专注「写对」与「导出」。

## Risks / caveats
- Heuristic CIR — agent should refine before publishing.

## Required deliverables
- Final article body (Markdown)
- 3 alternative titles
- Platform metadata block (tags/CTA/cover hints as required by template)
- Risks / assumptions list (short)